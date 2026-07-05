"""
Multi-account Google Calendar access for the interviewer roster.

GoogleCalendarService (calendar_service.py) is single-session-at-a-time: one
instance authenticates as one Google account and all its calendar/Meet calls act
on that account's 'primary' calendar. TokenManager already stores tokens keyed
by a hash of the account email, so it already supports multiple accounts - it's
just never been exercised with more than one at a time. This registry is a thin
cache of GoogleCalendarService instances, one per interviewer email, so the rest
of the app can schedule on a specific interviewer's calendar by email.
"""
import logging
from typing import Dict, Optional

from sqlalchemy.orm import Session

from app.models.models import User, UserRole
from app.services.calendar_service import GoogleCalendarService

logger = logging.getLogger(__name__)


class InterviewerCalendarRegistry:
    def __init__(self):
        self._services: Dict[str, GoogleCalendarService] = {}

    def get_service(self, interviewer_email: str) -> GoogleCalendarService:
        if interviewer_email not in self._services:
            svc = GoogleCalendarService()
            if not svc.authenticate(interviewer_email):
                raise RuntimeError(
                    f"No valid Google Calendar token for interviewer '{interviewer_email}'. "
                    f"Run: python scripts/authorize_interviewer.py {interviewer_email}"
                )
            self._services[interviewer_email] = svc
            logger.info(f"Authenticated calendar service for interviewer '{interviewer_email}'")
        return self._services[interviewer_email]


# Module-level singleton - GoogleCalendarService instances are reused across
# requests within a process rather than re-authenticating every call.
_registry = InterviewerCalendarRegistry()


def get_registry() -> InterviewerCalendarRegistry:
    return _registry


def assign_interviewer(db: Session, candidate_experience_years: float) -> Optional[User]:
    """
    Pick the interviewer whose experience_years exceeds the candidate's by the
    smallest margin (closest fit, least-overqualified). Falls back to the most
    senior interviewer on the roster if nobody strictly qualifies (e.g. the
    candidate is more senior than every interviewer).
    """
    candidate_experience_years = candidate_experience_years or 0

    qualifying = (
        db.query(User)
        .filter(User.role == UserRole.INTERVIEWER, User.experience_years > candidate_experience_years)
        .order_by(User.experience_years.asc())
        .first()
    )
    if qualifying:
        return qualifying

    fallback = (
        db.query(User)
        .filter(User.role == UserRole.INTERVIEWER, User.experience_years.isnot(None))
        .order_by(User.experience_years.desc())
        .first()
    )
    if fallback:
        logger.warning(
            f"No interviewer strictly more experienced than candidate ({candidate_experience_years} yrs) - "
            f"falling back to most senior interviewer '{fallback.email}' ({fallback.experience_years} yrs)"
        )
    return fallback
