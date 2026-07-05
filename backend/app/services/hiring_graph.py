"""
LangGraph orchestration for the post-insert, human-in-the-loop part of the hiring
workflow. Pre-insert RAG scoring (matching_service.py) happens before this graph
is ever invoked - it has no human-in-the-loop step so it doesn't need one.

Each candidate gets its own graph "thread" (thread_id = f"candidate-{id}"),
checkpointed to a local sqlite file so the graph can genuinely pause - across
HTTP requests, potentially days apart - waiting for HR to reply in the chat UI.

Nodes are re-executed from the top on resume (LangGraph semantics, verified
against the installed version): anything before an interrupt() call must be
side-effect-free. All DB/email work happens strictly after interrupt() resolves.
"""
import logging
import sqlite3
import threading
from datetime import datetime
from typing import Optional, TypedDict

import pytz
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from app.core.database import SessionLocal
from app.models.models import Candidate, Interview, InterviewStatus, InterviewType
from app.services.candidate_lifecycle import reject_and_delete_candidate
from app.services.email_service import EmailService
from app.services.interviewer_calendar_registry import assign_interviewer

logger = logging.getLogger(__name__)

INDIA_TZ = pytz.timezone("Asia/Kolkata")
ROUND_NAMES = {1: "First", 2: "Second", 3: "Final"}
MAX_ROUNDS = 3


class HiringState(TypedDict, total=False):
    candidate_id: int
    round_number: int
    reply_text: str
    scheduled_datetime_input: Optional[str]
    meet_link_input: Optional[str]
    last_command: Optional[dict]


def _parse_ist_datetime(text: str) -> datetime:
    """Parse a datetime-local-style string ('2026-07-10T14:00' or with a space) as IST."""
    cleaned = text.strip().replace(' ', 'T', 1) if 'T' not in text and ' ' in text else text.strip()
    naive = datetime.fromisoformat(cleaned)
    return naive if naive.tzinfo else INDIA_TZ.localize(naive)


def ask_round1(state: HiringState) -> Command:
    candidate_id = state["candidate_id"]
    db = SessionLocal()
    try:
        candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
        question = (
            f"{candidate.name} scored {candidate.ai_overall_score}/100 for {candidate.position}. "
            f"Send the Round 1 interview invite? (yes/no)"
        )
    finally:
        db.close()

    approved = interrupt({"type": "round1_confirmation", "candidate_id": candidate_id, "question": question})

    # Persist a status marker so the chat dispatcher can find "which candidate is
    # mid-conversation" via a plain DB query, without needing to inspect graph state.
    db = SessionLocal()
    try:
        candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
        candidate.status = "awaiting_datetime_input" if approved else "awaiting_freetext_command"
        db.commit()
    finally:
        db.close()

    if approved:
        return Command(
            goto="ask_datetime",
            update={"reply_text": "What date & time should Round 1 be? (e.g. 2026-07-10 2:00 PM). You can add a meeting link too."},
        )
    # Declined for now, not rejected - candidate stays in the DB and HR can still
    # act on them later via a free-text command ("schedule round 1", "reject them").
    return Command(
        goto="await_freetext",
        update={"reply_text": "OK, no Round 1 invite sent yet. Let me know when you want to schedule it, or if you'd like to reject them."},
    )


def ask_datetime(state: HiringState) -> Command:
    candidate_id = state["candidate_id"]
    round_number = state["round_number"]

    reply = interrupt({"type": "schedule_datetime", "candidate_id": candidate_id, "round_number": round_number})
    # reply is expected to be a dict: {"datetime": "...", "meet_link": "..." (optional)}

    return Command(
        goto="schedule_round",
        update={"scheduled_datetime_input": reply.get("datetime"), "meet_link_input": reply.get("meet_link")},
    )


def schedule_round(state: dict) -> Command:
    candidate_id = state["candidate_id"]
    round_number = state["round_number"]
    scheduled_datetime = state.get("scheduled_datetime_input")
    meet_link = state.get("meet_link_input")

    db = SessionLocal()
    try:
        candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
        if not candidate:
            return Command(goto=END, update={"reply_text": "Candidate no longer exists."})

        interviewer = assign_interviewer(db, candidate.experience_years)
        if not interviewer:
            return Command(goto=END, update={"reply_text": "No interviewers configured on the roster."})

        interview_dt = _parse_ist_datetime(scheduled_datetime)

        candidate.current_round = round_number
        candidate.interview_datetime = interview_dt
        candidate.status = "scheduled"

        interview = Interview(
            candidate_id=candidate.id,
            interviewer_id=interviewer.id,
            scheduled_time=interview_dt,
            type=InterviewType.TECHNICAL,
            status=InterviewStatus.SCHEDULED,
            notes=meet_link or None,
        )
        db.add(interview)
        db.commit()

        round_name = ROUND_NAMES.get(round_number, f"Round {round_number}")
        display_link = meet_link or "Your interviewer will share the call link with you directly."

        email_service = EmailService()
        email_sent = None
        if email_service.enabled:
            import asyncio
            email_sent = asyncio.run(email_service.send_round_advancement_email(
                candidate_email=candidate.email,
                candidate_name=candidate.name,
                round_number=round_number,
                round_name=round_name,
                interview_datetime=interview_dt,
                meet_link=display_link,
                position=candidate.position,
            ))

        reply_text = (
            f"Scheduled {candidate.name}'s {round_name} round with {interviewer.name} "
            f"on {interview_dt.strftime('%A, %B %d at %I:%M %p IST')}. "
            f"Email sent: {'yes' if email_sent else 'no'}."
        )
        logger.info(f"✅ {reply_text}")

        if round_number >= MAX_ROUNDS:
            candidate.status = "completed"
            db.commit()
            return Command(goto="complete", update={"reply_text": reply_text})

        candidate.status = "awaiting_freetext_command"
        db.commit()
        return Command(goto="await_freetext", update={"reply_text": reply_text})
    finally:
        db.close()


def await_freetext(state: HiringState) -> Command:
    candidate_id = state["candidate_id"]
    command = interrupt({"type": "freetext_command", "candidate_id": candidate_id})
    # command is expected to be a dict: {"action": "advance_round"|"reject", "round_number": int|None}
    return Command(goto="route_command", update={"last_command": command})


def route_command(state: HiringState) -> Command:
    candidate_id = state["candidate_id"]
    command = state.get("last_command") or {}
    action = command.get("action")

    if action == "reject":
        return Command(goto="reject_and_delete")

    if action in ("advance_round", "reschedule"):
        db = SessionLocal()
        try:
            candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
            current_round = candidate.current_round or 0
        finally:
            db.close()

        if action == "reschedule":
            # Same round they're already on, not the next one - just changing the time.
            if current_round < 1:
                return Command(
                    goto="await_freetext",
                    update={"reply_text": "They don't have an interview scheduled yet, so there's nothing to reschedule."},
                )
            target_round = current_round
            question = f"What's the new date & time for round {target_round}?"
        else:
            target_round = command.get("round_number") or (current_round + 1)
            if target_round <= current_round:
                return Command(
                    goto="await_freetext",
                    update={"reply_text": f"They're already at round {current_round}. Did you mean round {current_round + 1}?"},
                )
            if target_round > MAX_ROUNDS:
                return Command(goto="await_freetext", update={"reply_text": f"There's no round {target_round} - max is {MAX_ROUNDS}."})
            question = f"What date & time should round {target_round} be?"

        # Set the same status marker ask_round1 sets before its own ask_datetime
        # hop, so the chat dispatcher can find this candidate while it's waiting
        # on a datetime reply (this route can be entered for round 2/3, or a
        # reschedule of the current round, too).
        db = SessionLocal()
        try:
            candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
            candidate.status = "awaiting_datetime_input"
            db.commit()
        finally:
            db.close()

        return Command(goto="ask_datetime", update={"round_number": target_round, "reply_text": question})

    return Command(
        goto="await_freetext",
        update={"reply_text": "Sorry, I didn't catch an action - try something like 'schedule round 2', 'reschedule', or 'reject them'."},
    )


def reject_and_delete(state: HiringState) -> Command:
    candidate_id = state["candidate_id"]
    db = SessionLocal()
    try:
        import asyncio
        result = asyncio.run(reject_and_delete_candidate(candidate_id, db))
        reply_text = f"Rejected and removed {result['name']} from the system. Rejection email sent: {'yes' if result['rejection_email_sent'] else 'no'}."
        logger.info(f"✅ {reply_text}")
        return Command(goto=END, update={"reply_text": reply_text})
    except ValueError:
        return Command(goto=END, update={"reply_text": "That candidate no longer exists."})
    finally:
        db.close()


def complete(state: HiringState) -> Command:
    return Command(goto=END, update={"reply_text": state.get("reply_text", "All rounds complete.")})


def _build_graph():
    builder = StateGraph(HiringState)
    builder.add_node("ask_round1", ask_round1)
    builder.add_node("ask_datetime", ask_datetime)
    builder.add_node("schedule_round", schedule_round)
    builder.add_node("await_freetext", await_freetext)
    builder.add_node("route_command", route_command)
    builder.add_node("reject_and_delete", reject_and_delete)
    builder.add_node("complete", complete)
    builder.add_edge(START, "ask_round1")
    return builder


_checkpointer_conn = sqlite3.connect("langgraph_checkpoints.db", check_same_thread=False)
_checkpointer = SqliteSaver(_checkpointer_conn)
_graph = _build_graph().compile(checkpointer=_checkpointer)
_graph_lock = threading.Lock()


def get_graph():
    return _graph


def get_graph_lock():
    return _graph_lock


def thread_config(candidate_id: int) -> dict:
    return {"configurable": {"thread_id": f"candidate-{candidate_id}"}}


def start_round1_thread(candidate_id: int) -> dict:
    """Called right after a candidate is inserted - runs the graph to its first interrupt."""
    with _graph_lock:
        result = _graph.invoke({"candidate_id": candidate_id, "round_number": 1, "reply_text": ""}, config=thread_config(candidate_id))
    return result


def resume_thread(candidate_id: int, resume_value) -> dict:
    with _graph_lock:
        result = _graph.invoke(Command(resume=resume_value), config=thread_config(candidate_id))
    return result


def get_pending_interrupt(candidate_id: int) -> Optional[dict]:
    """What kind of input this candidate's thread is currently waiting on, if any."""
    with _graph_lock:
        snapshot = _graph.get_state(thread_config(candidate_id))
    if snapshot and snapshot.interrupts:
        return snapshot.interrupts[0].value
    return None
