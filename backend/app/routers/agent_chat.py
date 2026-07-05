"""
HR <-> agent chat API.

Dispatch logic, in order:
0. If the message is a system-wide question ("how many candidates are in the
   system", "how many on round 2") it isn't about any one candidate - answer it
   straight from a DB count/aggregate (never left to the LLM to estimate) and
   return immediately, regardless of whether anyone happens to be pending.
1. Otherwise, find every candidate currently awaiting SOME action (round1
   yes/no, a datetime reply, or a free-text command) - not just "whichever is
   most recent," which used to silently ignore any other candidate in flight.
2. If exactly one is pending, the message applies to them directly - no need
   to name them (keeps the common case simple: just reply "yes").
3. If more than one is pending, the message must identify who it's about,
   either by "#<id>" or by fuzzy-matching a name anywhere in the message. If
   that fails or is ambiguous, ask HR to clarify (listing name + id + role so
   even same-named candidates can be told apart by id).
4. Once a candidate is resolved, what the message means depends on THEIR
   specific pending interrupt type: round1_confirmation -> yes/no,
   schedule_datetime -> a date/time (+ optional link), freetext_command ->
   parse_hr_command for advance/reject.
"""
import json
import logging
import random
import re
from datetime import datetime, timedelta

import pytz
from dateutil import parser as dateutil_parser
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from rapidfuzz import process, fuzz
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from app.core.limiter import limiter
from app.models.models import Candidate, ChatMessage
from app.routers.candidates_standalone import get_db
from app.services.ai_service import AIService
from app.services.command_parser import HISTORY_TURNS, parse_hr_command
from app.services.hiring_graph import get_pending_interrupt, resume_thread
from app.services.interviewer_calendar_registry import assign_interviewer

PENDING_STATUSES = ["awaiting_round1_confirmation", "awaiting_datetime_input", "awaiting_freetext_command"]

NAME_MATCH_THRESHOLD = 65  # rapidfuzz score (0-100) below which we don't consider it a match
NAME_MATCH_MARGIN = 10     # if the top two matches are within this margin, treat as ambiguous

logger = logging.getLogger(__name__)
router = APIRouter()

INDIA_TZ = pytz.timezone("Asia/Kolkata")

YES_WORDS = {"yes", "y", "yeah", "yep", "sure", "ok", "okay", "go ahead", "please", "confirm"}
NO_WORDS = {"no", "n", "nope", "nah", "not now", "skip", "cancel"}

URL_RE = re.compile(r"https?://\S+")
ID_RE = re.compile(r"#\s*(\d+)")
STATS_TRIGGER_RE = re.compile(
    r"\bhow many\b|\bhow much\b|\bcount\b|\btotal\b|\boverview\b|\bstatistics\b|\bstats\b|\bbreakdown\b",
    re.IGNORECASE,
)
LIST_TRIGGER_RE = re.compile(r"\bwho\b|\bwhich\b|\blist\b|\bshow me\b", re.IGNORECASE)
LOOKUP_TRIGGER_RE = re.compile(
    r"which round|what round|on which round|which stage|what stage|what.?s the status|current status",
    re.IGNORECASE,
)
ROUND_NUMBER_RE = re.compile(r"round\s*([0-3])\b", re.IGNORECASE)
TIME_COMPONENT_RE = re.compile(r"\d{1,2}(:\d{2})?\s*(am|pm)\b|\b\d{1,2}:\d{2}\b", re.IGNORECASE)

WEEKDAY_NAMES = {
    "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
    "friday": 4, "saturday": 5, "sunday": 6,
}
BUSINESS_START_HOUR = 9
BUSINESS_END_HOUR = 17
SLOT_COUNT = 4


class ChatMessageIn(BaseModel):
    message: str


def _parse_yes_no(text: str):
    normalized = text.strip().lower()
    if any(normalized == w or normalized.startswith(w + " ") for w in YES_WORDS):
        return True
    if any(normalized == w or normalized.startswith(w + " ") for w in NO_WORDS):
        return False
    return None


def _parse_datetime_and_link(text: str):
    """Best-effort: pull a URL out as the meet link, parse whatever's left as a datetime."""
    link_match = URL_RE.search(text)
    meet_link = link_match.group(0) if link_match else None
    remaining = URL_RE.sub("", text).strip(" ,")

    try:
        parsed = dateutil_parser.parse(remaining, fuzzy=True)
    except (ValueError, OverflowError):
        return None

    if parsed.tzinfo is None:
        parsed = INDIA_TZ.localize(parsed)
    return {"datetime": parsed.isoformat(), "meet_link": meet_link}


def _has_explicit_time(text: str) -> bool:
    """Whether the message names an actual time ('2pm', '14:00') vs. just a date -
    a clicked slot button sends a full ISO datetime, which always matches this."""
    return bool(TIME_COMPONENT_RE.search(text))


def _resolve_rough_date(text: str, now: datetime = None):
    """
    Parse a date-only reference: 'July 15', 'tomorrow', 'Monday', etc.
    - Weekday names resolve to their next occurrence (today's name means next week).
    - A bare date like 'July 15' defaults to the current year (dateutil's
      `default=` fills in whatever isn't specified) - if that lands in the past,
      roll forward a year rather than schedule an interview last year.
    - Interviews only happen Mon-Fri, so a resolved weekend date rolls forward
      to the next business day.
    Returns a date object, or None if nothing date-like was found.
    """
    now = now or datetime.now(INDIA_TZ)
    today = now.date()
    lower = text.strip().lower()
    words = re.findall(r"[a-z]+", lower)

    def _mentions(word: str) -> bool:
        # typo-tolerant: catches 'tommorow', 'mondey', etc., not just exact spelling
        return any(fuzz.ratio(w, word) >= 80 for w in words)

    resolved = None
    if _mentions("today"):
        resolved = today
    elif _mentions("tomorrow"):
        resolved = today + timedelta(days=1)
    else:
        for name, weekday in WEEKDAY_NAMES.items():
            if _mentions(name):
                days_ahead = (weekday - today.weekday()) % 7
                days_ahead = days_ahead or 7  # naming today's own weekday means next week
                resolved = today + timedelta(days=days_ahead)
                break

    if resolved is None:
        try:
            parsed = dateutil_parser.parse(text, fuzzy=True, default=now)
        except (ValueError, OverflowError):
            return None
        resolved = parsed.date()
        if resolved < today:
            resolved = resolved.replace(year=resolved.year + 1)

    while resolved.weekday() >= 5:  # Saturday/Sunday - roll to the next business day
        resolved += timedelta(days=1)

    return resolved


def _generate_random_slots(resolved_date, count: int = SLOT_COUNT) -> list:
    """count random, distinct half-hour business-hours slots on the given date -
    a placeholder for real calendar availability, which isn't wired up yet."""
    possible_times = [
        (hour, minute)
        for hour in range(BUSINESS_START_HOUR, BUSINESS_END_HOUR)
        for minute in (0, 30)
    ]
    chosen = sorted(random.sample(possible_times, min(count, len(possible_times))))

    slots = []
    for hour, minute in chosen:
        dt = INDIA_TZ.localize(datetime(resolved_date.year, resolved_date.month, resolved_date.day, hour, minute))
        slots.append({"iso": dt.isoformat(), "label": dt.strftime("%I:%M %p").lstrip("0")})
    return slots


def _recent_history(db: Session, exclude_last_id: int) -> list:
    """Last few chat turns, oldest first, for giving the command parser multi-turn context."""
    rows = (
        db.query(ChatMessage)
        .filter(ChatMessage.id != exclude_last_id)
        .order_by(ChatMessage.id.desc())
        .limit(HISTORY_TURNS)
        .all()
    )
    rows.reverse()
    return [{"role": m.role, "content": m.content} for m in rows]


def _find_candidate_in_message(message: str, candidates: list) -> tuple:
    """
    Resolve which of several pending candidates a message is about.
    Returns (matched_candidate_or_None, clarification_message_or_None).
    Tries an explicit "#<id>" reference first (works even when two candidates
    share a name), then falls back to fuzzy-matching a name anywhere in the message.
    """
    id_match = ID_RE.search(message)
    if id_match:
        cid = int(id_match.group(1))
        for c in candidates:
            if c.id == cid:
                return c, None

    choices = {c.id: c.name for c in candidates}
    matches = process.extract(message, choices, scorer=fuzz.partial_ratio, limit=2)

    if not matches or matches[0][1] < NAME_MATCH_THRESHOLD:
        return None, None

    if len(matches) > 1 and (matches[0][1] - matches[1][1]) < NAME_MATCH_MARGIN:
        return None, _list_candidates(candidates, "That could match more than one candidate")

    matched_id = matches[0][2]
    return next(c for c in candidates if c.id == matched_id), None


def _list_candidates(candidates: list, lead_in: str) -> str:
    listed = ", ".join(f"{c.name} (#{c.id}, {c.position})" for c in candidates)
    return f"{lead_in}: {listed}. Reply with the name or #id."


def _last_addressed_candidate(db: Session, pending_candidates: list):
    """
    If the most recent assistant message was a question directed at one specific
    candidate (its candidate_id is set) and that candidate is still pending, a
    reply that doesn't name anyone else is almost certainly answering THAT
    question - e.g. the assistant just asked "...send Harish's Round 1 invite?
    (yes/no)" and HR says "yes". Without this, a bare "yes" among multiple
    pending candidates would force HR to re-specify the name for no reason.
    """
    pending_ids = {c.id for c in pending_candidates}
    last_assistant = (
        db.query(ChatMessage)
        .filter(ChatMessage.role == "assistant", ChatMessage.candidate_id.isnot(None))
        .order_by(ChatMessage.id.desc())
        .first()
    )
    if last_assistant and last_assistant.candidate_id in pending_ids:
        return next(c for c in pending_candidates if c.id == last_assistant.candidate_id)
    return None


def _extract_round_number(message: str):
    m = ROUND_NUMBER_RE.search(message)
    if m:
        return int(m.group(1))
    lower = message.lower()
    if re.search(r"\b(first|1st)\b", lower):
        return 1
    if re.search(r"\b(second|2nd)\b", lower):
        return 2
    if re.search(r"\b(third|3rd|final)\b", lower):
        return 3
    return None


def _try_answer_query(message: str, db: Session):
    """
    System-wide questions aren't about any one candidate, so they're tried
    before the pending-candidate dispatch and answered straight from the DB
    (never left to the LLM to estimate/hallucinate names or counts). Returns
    the reply text, or None if the message isn't one of these query types.
    """
    if STATS_TRIGGER_RE.search(message):
        return _format_stats_reply(_compute_stats(db))

    if LIST_TRIGGER_RE.search(message):
        round_number = _extract_round_number(message)
        if round_number is not None:
            return _format_round_list(db, round_number)

    if LOOKUP_TRIGGER_RE.search(message):
        looked_up = _lookup_candidate_status(message, db)
        if looked_up:
            return looked_up

    return None


def _format_round_list(db: Session, round_number: int) -> str:
    candidates = db.query(Candidate).filter(Candidate.current_round == round_number).all()
    if not candidates:
        return f"No candidates are currently on round {round_number}."
    listed = ", ".join(f"{c.name} (#{c.id}, {c.position})" for c in candidates)
    return f"Candidates on round {round_number}: {listed}."


def _lookup_candidate_status(message: str, db: Session):
    """Fuzzy-match a name anywhere in the message against ALL candidates (not just
    ones awaiting action - someone could ask about anyone already scheduled)."""
    all_candidates = db.query(Candidate).all()
    if not all_candidates:
        return None

    choices = {c.id: c.name for c in all_candidates}
    matches = process.extract(message, choices, scorer=fuzz.partial_ratio, limit=2)
    if not matches or matches[0][1] < NAME_MATCH_THRESHOLD:
        return None

    if len(matches) > 1 and (matches[0][1] - matches[1][1]) < NAME_MATCH_MARGIN:
        top = [next(c for c in all_candidates if c.id == m[2]) for m in matches]
        return _list_candidates(top, "That could match more than one candidate")

    matched = next(c for c in all_candidates if c.id == matches[0][2])
    round_desc = "not yet scheduled for an interview" if not matched.current_round else f"on round {matched.current_round}"
    return f"{matched.name} (#{matched.id}, {matched.position}) is {round_desc}. Status: {matched.status}."


def _compute_stats(db: Session) -> dict:
    """Real counts straight from the DB - deliberately not left to the LLM to
    estimate, since it's bad at exact counting and this needs to be accurate."""
    total = db.query(Candidate).count()
    round_counts = {r: db.query(Candidate).filter(Candidate.current_round == r).count() for r in (0, 1, 2, 3)}
    completed = db.query(Candidate).filter(Candidate.status == "completed").count()
    awaiting_action = db.query(Candidate).filter(Candidate.status.in_(PENDING_STATUSES)).count()
    return {
        "total": total,
        "round_counts": round_counts,
        "completed": completed,
        "awaiting_action": awaiting_action,
    }


def _format_stats_reply(stats: dict) -> str:
    rc = stats["round_counts"]
    return (
        f"There are {stats['total']} candidates in the system right now.\n"
        f"- Not yet scheduled: {rc.get(0, 0)}\n"
        f"- Round 1: {rc.get(1, 0)}\n"
        f"- Round 2: {rc.get(2, 0)}\n"
        f"- Round 3: {rc.get(3, 0)}\n"
        f"- Completed: {stats['completed']}\n"
        f"- Awaiting your action: {stats['awaiting_action']}"
    )


@router.get("/history")
async def get_history(db: Session = Depends(get_db)):
    messages = db.query(ChatMessage).order_by(ChatMessage.created_at.asc()).all()
    result = []
    for m in messages:
        metadata = None
        if m.metadata_json:
            try:
                metadata = json.loads(m.metadata_json)
            except (TypeError, ValueError):
                metadata = None
        result.append({
            "id": m.id,
            "role": m.role,
            "content": m.content,
            "candidate_id": m.candidate_id,
            "created_at": m.created_at,
            "metadata": metadata,
        })
    return result


@router.delete("/history")
async def clear_history(db: Session = Depends(get_db)):
    """Clear the visible chat log for a fresh conversation. Doesn't touch candidate
    pipeline state (status/graph threads) - purely a display reset."""
    db.query(ChatMessage).delete()
    db.commit()
    return {"cleared": True}


@router.post("/message")
@limiter.limit("20/minute")
async def post_message(request: Request, body: ChatMessageIn, db: Session = Depends(get_db)):
    hr_message = ChatMessage(role="hr", content=body.message)
    db.add(hr_message)
    db.commit()
    db.refresh(hr_message)

    query_reply = _try_answer_query(body.message, db)
    if query_reply:
        db.add(ChatMessage(role="assistant", content=query_reply, candidate_id=None))
        db.commit()
        return {"reply": query_reply}

    pending_candidates = (
        db.query(Candidate)
        .filter(Candidate.status.in_(PENDING_STATUSES))
        .order_by(Candidate.id.asc())
        .all()
    )

    candidate = None
    reply_text = "There's no candidate currently awaiting action."
    reply_metadata = None

    if len(pending_candidates) == 1:
        candidate = pending_candidates[0]
    elif len(pending_candidates) > 1:
        candidate, clarification = _find_candidate_in_message(body.message, pending_candidates)
        if candidate is None and clarification is None:
            # No name/id mentioned at all - default to whoever the last question
            # was actually addressed to, rather than forcing HR to name them.
            candidate = _last_addressed_candidate(db, pending_candidates)
        if candidate is None:
            reply_text = clarification or _list_candidates(pending_candidates, "Multiple candidates are awaiting action")

    if candidate:
        pending = await run_in_threadpool(get_pending_interrupt, candidate.id)
        interrupt_type = pending.get("type") if pending else None

        if interrupt_type == "round1_confirmation":
            approved = _parse_yes_no(body.message)
            if approved is None:
                reply_text = "Sorry, please reply yes or no."
            else:
                result = await run_in_threadpool(resume_thread, candidate.id, approved)
                reply_text = result.get("reply_text", "Done.")

        elif interrupt_type == "schedule_datetime":
            if _has_explicit_time(body.message):
                # A full date+time (typed directly, or a clicked slot button
                # sending back its exact ISO datetime) books immediately.
                parsed = _parse_datetime_and_link(body.message)
                if parsed is None:
                    reply_text = "Sorry, I couldn't understand that date/time. Try something like '2026-07-10 2:00 PM'."
                else:
                    result = await run_in_threadpool(resume_thread, candidate.id, parsed)
                    reply_text = result.get("reply_text", "Done.")
            else:
                # Just a date ('July 15', 'tomorrow', 'Monday') - offer a few
                # random business-hours slots to click instead of requiring an
                # exact time. Placeholder until real calendar availability is
                # wired in - same interrupt/resume path either way.
                resolved_date = _resolve_rough_date(body.message)
                if resolved_date is None:
                    reply_text = "Sorry, I couldn't understand that date. Try 'July 15', 'tomorrow', or a day like 'Monday'."
                else:
                    slots = _generate_random_slots(resolved_date)
                    interviewer = assign_interviewer(db, candidate.experience_years)
                    matched_with = f" with {interviewer.name}" if interviewer else ""
                    day_label = resolved_date.strftime('%A, %B %d')
                    reply_text = (
                        f"{candidate.name}'s interview{matched_with} is matched for {day_label}. "
                        f"Pick a time slot:"
                    )
                    reply_metadata = {"type": "slot_options", "slots": slots}

        else:
            # freetext_command (or a defensive fallback if no interrupt is found)
            ai_service = AIService()
            history = _recent_history(db, exclude_last_id=hr_message.id)
            hr_command = await run_in_threadpool(parse_hr_command, body.message, ai_service, history)

            if hr_command.action == "unknown":
                reply_text = "Sorry, I couldn't tell what you'd like to do. Try 'schedule round 2', 'reschedule this candidate', or 'reject them'."
            else:
                result = await run_in_threadpool(
                    resume_thread,
                    candidate.id,
                    {"action": hr_command.action, "round_number": hr_command.round_number},
                )
                reply_text = result.get("reply_text", "Done.")

    db.add(ChatMessage(
        role="assistant",
        content=reply_text,
        candidate_id=candidate.id if candidate else None,
        metadata_json=json.dumps(reply_metadata) if reply_metadata else None,
    ))
    db.commit()

    return {"reply": reply_text, "metadata": reply_metadata}
