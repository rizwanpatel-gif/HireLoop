"""
Parses HR's free-text chat commands ("schedule round 2", "reject them") into a
structured action + round number. Candidate identification is NOT this module's
job - by the time this is called, the chat dispatcher has already resolved which
specific candidate the message is about (either because only one was pending, or
because the message named/ID'd one among several) - see agent_chat.py's
_find_candidate_in_message. This module only classifies intent.
"""
import json
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional

from app.services.ai_service import AIService

logger = logging.getLogger(__name__)

VALID_ACTIONS = {"advance_round", "reschedule", "reject", "unknown"}

HISTORY_TURNS = 6  # how many recent chat_messages rows to include as context


@dataclass
class HRCommand:
    action: str
    round_number: Optional[int]


def parse_hr_command(message: str, ai_service: AIService, history: Optional[List[Dict[str, str]]] = None) -> HRCommand:
    """
    message: HR's latest chat message, already known to be about one specific candidate.
    history: recent prior turns, oldest first, as [{"role": "hr"|"assistant", "content": ...}, ...].
    """
    system_prompt = """You extract a hiring action from a message an HR person sent about a specific candidate (which candidate is already known - you're only classifying what they want done).

RESPONSE FORMAT: Return ONLY valid JSON, no markdown, no extra text, in this exact shape:
{
    "action": "advance_round" | "reschedule" | "reject" | "unknown",
    "round_number": <integer 1-3, or null if not specified/not applicable>
}

Rules:
- "advance_round": HR wants to schedule/move the candidate to their NEXT interview round (e.g. "schedule their 2nd round", "move to round 3", "yes let's schedule it").
- "reschedule": HR wants to change the date/time of the candidate's CURRENT round - NOT move them forward a round (e.g. "reschedule the interview", "let's move the time for this candidate", "can we push the interview back").
- "reject": HR wants to reject/decline/remove the candidate (e.g. "reject them", "let them go", "we're not moving forward").
- "unknown": anything else, or if you genuinely can't tell what they want.
- If a round number isn't mentioned but the intent is clearly to advance, use round_number: null - the caller will figure out the next round from the candidate's current progress. For "reschedule", always use round_number: null - it always means the candidate's current round, not a specific number."""

    try:
        history_block = ""
        if history:
            lines = [f"{'HR' if h['role'] == 'hr' else 'Assistant'}: {h['content']}" for h in history[-HISTORY_TURNS:]]
            history_block = "RECENT CONVERSATION (oldest first):\n" + "\n".join(lines) + "\n\n"

        user_prompt = f"{history_block}HR's LATEST message: {message}"

        response = ai_service._make_api_call([{"role": "user", "content": user_prompt}], system_prompt, max_tokens=700)
        if not response:
            return HRCommand(action="unknown", round_number=None)

        response = response.strip()
        if response.startswith('```json'):
            response = response[7:-3]
        elif response.startswith('```'):
            response = response[3:-3]

        data = json.loads(response.strip())
        action = data.get("action") if data.get("action") in VALID_ACTIONS else "unknown"
        return HRCommand(action=action, round_number=data.get("round_number"))
    except Exception as e:
        logger.error(f"Failed to parse HR command '{message}': {e}")
        return HRCommand(action="unknown", round_number=None)
