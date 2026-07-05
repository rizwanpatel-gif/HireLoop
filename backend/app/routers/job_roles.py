"""
Job roles API - backs the role dropdown on the candidate intake form. Each role
carries the JD text that resumes get RAG-matched against (matching_service.py).
"""
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.models.models import JobRole
from app.routers.candidates_standalone import get_db

logger = logging.getLogger(__name__)
router = APIRouter()


class JobRoleCreate(BaseModel):
    title: str
    department: Optional[str] = None
    jd_text: str


class JobRoleResponse(BaseModel):
    id: int
    title: str
    department: Optional[str] = None
    jd_text: str
    is_active: int

    class Config:
        from_attributes = True


@router.get("/", response_model=List[JobRoleResponse])
async def list_job_roles(db: Session = Depends(get_db)):
    return db.query(JobRole).filter(JobRole.is_active == 1).order_by(JobRole.title.asc()).all()


@router.post("/", response_model=JobRoleResponse)
async def create_job_role(role_data: JobRoleCreate, db: Session = Depends(get_db)):
    existing = db.query(JobRole).filter(JobRole.title == role_data.title).first()
    if existing:
        raise HTTPException(status_code=400, detail="A job role with this title already exists")

    role = JobRole(
        title=role_data.title,
        department=role_data.department,
        jd_text=role_data.jd_text,
        is_active=1,
    )
    db.add(role)
    db.commit()
    db.refresh(role)
    logger.info(f"➕ Created job role '{role.title}' (id={role.id})")
    return role
