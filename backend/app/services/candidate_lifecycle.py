"""
Shared candidate lifecycle actions used by both the REST DELETE endpoint and the
LangGraph reject-and-delete node, so the email+delete behavior lives in one place.
"""
import logging

from sqlalchemy.orm import Session

from app.models.models import Candidate
from app.services.email_service import EmailService

logger = logging.getLogger(__name__)


async def reject_and_delete_candidate(candidate_id: int, db: Session, reason: str = None) -> dict:
    """Send the standard rejection email, then permanently delete the candidate row."""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise ValueError(f"Candidate {candidate_id} not found")

    candidate_name = candidate.name
    candidate_email = candidate.email
    candidate_position = candidate.position

    logger.info(f"🗑️ Rejecting and deleting candidate: {candidate_name} ({candidate_email})")

    email_sent = False
    try:
        email_service = EmailService()
        if email_service.enabled:
            email_sent = await email_service.send_rejection_email(
                to_email=candidate_email,
                candidate_name=candidate_name,
                position=candidate_position,
                reason=reason,
            )
        else:
            logger.warning("⚠️ Email service not configured - skipping rejection email")
    except Exception as e:
        logger.error(f"❌ Error sending rejection email: {e}")

    db.delete(candidate)
    db.commit()

    logger.info(f"✅ Deleted candidate: {candidate_name} ({candidate_email})")

    return {
        "id": candidate_id,
        "name": candidate_name,
        "email": candidate_email,
        "rejection_email_sent": email_sent,
    }
