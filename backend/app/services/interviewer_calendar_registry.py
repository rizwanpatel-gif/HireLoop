"""
Interviewer assignment for the hiring pipeline.

Calendar/Meet integration was dropped (too slow/fragile to set up multi-account
OAuth for a student demo) - this module only picks which interviewer a
candidate should be assigned to based on experience level.
"""
import logging
from typing import Optional

from sqlalchemy.orm import Session

from app.models.models import User, UserRole

logger = logging.getLogger(__name__)


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
