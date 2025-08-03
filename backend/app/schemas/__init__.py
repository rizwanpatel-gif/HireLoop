"""
Schema initialization file
"""

from .candidate import (
    CandidateCreate,
    CandidateUpdate, 
    CandidateResponse,
    CandidateDetailResponse,
    CandidateListResponse,
    InterviewCreate,
    InterviewUpdate,
    InterviewResponse,
    InterviewScheduleRequest,
    InterviewConfirmationResponse,
    DashboardStats,
    DashboardResponse,
    ErrorResponse,
    SuccessResponse,
    CandidateStatus,
    InterviewStatus,
    InterviewType
)

__all__ = [
    "CandidateCreate",
    "CandidateUpdate",
    "CandidateResponse", 
    "CandidateDetailResponse",
    "CandidateListResponse",
    "InterviewCreate",
    "InterviewUpdate",
    "InterviewResponse",
    "InterviewScheduleRequest", 
    "InterviewConfirmationResponse",
    "DashboardStats",
    "DashboardResponse",
    "ErrorResponse",
    "SuccessResponse",
    "CandidateStatus",
    "InterviewStatus",
    "InterviewType"
]
