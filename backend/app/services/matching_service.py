"""
RAG-based resume <-> job-description matching.

Each job role's JD is chunked and embedded into its own local Chroma collection
(no external vector DB / API key needed). A candidate's resume is chunked, and
each resume chunk retrieves the most relevant JD chunks; the union of retrieved
JD chunks is handed to AIService.score_resume_match for the actual scoring call.
"""
import hashlib
import logging
import os
from dataclasses import dataclass, field
from typing import List

import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.models.models import JobRole
from app.services.ai_service import AIService

logger = logging.getLogger(__name__)

CHROMA_STORE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "chroma_store")

_chroma_client = None


def get_chroma_client() -> "chromadb.ClientAPI":
    """Module-level singleton so collections persist across calls within a process."""
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = chromadb.PersistentClient(path=CHROMA_STORE_PATH)
    return _chroma_client


@dataclass
class MatchResult:
    score: float
    matched_requirements: List[str] = field(default_factory=list)
    missing_requirements: List[str] = field(default_factory=list)
    rationale: str = ""
    retrieved_jd_chunks: List[str] = field(default_factory=list)
    estimated_experience_years: float = 0.0
    extracted_skills: List[str] = field(default_factory=list)


def chunk_text(text: str, chunk_size: int = 800, chunk_overlap: int = 100) -> List[str]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = [c.strip() for c in splitter.split_text(text or "") if c.strip()]
    return chunks or ([text.strip()] if text and text.strip() else [])


def _jd_collection_name(job_role: JobRole) -> str:
    jd_hash = hashlib.md5(job_role.jd_text.encode("utf-8")).hexdigest()[:8]
    return f"jd_role_{job_role.id}_{jd_hash}"


def get_or_build_jd_collection(job_role: JobRole, chroma_client=None):
    """
    One Chroma collection per (job_role, jd_text) pair. The hash suffix means
    editing a role's JD transparently gets a fresh collection built next call —
    stale collections from a previous JD version are simply orphaned, which is
    fine at demo scale (no explicit cache invalidation needed).
    """
    client = chroma_client or get_chroma_client()
    name = _jd_collection_name(job_role)
    collection = client.get_or_create_collection(name=name)

    if collection.count() == 0:
        jd_chunks = chunk_text(job_role.jd_text)
        if jd_chunks:
            collection.upsert(
                ids=[f"chunk-{i}" for i in range(len(jd_chunks))],
                documents=jd_chunks,
            )
            logger.info(f"Built JD collection '{name}' with {len(jd_chunks)} chunks for role '{job_role.title}'")

    return collection


def score_resume_against_role(
    resume_text: str,
    job_role: JobRole,
    ai_service: AIService,
    chroma_client=None,
) -> MatchResult:
    """
    Chunk the resume, retrieve the most relevant JD chunks for each resume chunk,
    then ask the LLM to score the resume against ONLY those retrieved requirement
    excerpts (this is the RAG step — retrieval happens before the scoring call).
    """
    collection = get_or_build_jd_collection(job_role, chroma_client)

    resume_chunks = chunk_text(resume_text)
    if not resume_chunks:
        logger.warning(f"Empty resume text for role '{job_role.title}' — scoring as 0")
        return MatchResult(score=0.0, rationale="No resume text provided.")

    retrieved: List[str] = []
    seen = set()
    for chunk in resume_chunks:
        try:
            result = collection.query(query_texts=[chunk], n_results=4)
        except Exception as e:
            logger.error(f"Chroma query failed: {e}")
            continue
        for doc in (result.get("documents") or [[]])[0]:
            if doc not in seen:
                seen.add(doc)
                retrieved.append(doc)

    if not retrieved:
        logger.warning(f"No JD chunks retrieved for role '{job_role.title}' — falling back to full JD text")
        retrieved = chunk_text(job_role.jd_text)

    ai_result = ai_service.score_resume_match(resume_text, job_role.title, retrieved)

    if ai_result is None:
        logger.error(f"AI scoring failed for role '{job_role.title}' — defaulting to score 0")
        return MatchResult(score=0.0, rationale="AI scoring failed.", retrieved_jd_chunks=retrieved)

    return MatchResult(
        score=ai_result.get("match_score", 0.0),
        matched_requirements=ai_result.get("matched_requirements", []),
        missing_requirements=ai_result.get("missing_requirements", []),
        rationale=ai_result.get("rationale", ""),
        retrieved_jd_chunks=retrieved,
        estimated_experience_years=ai_result.get("estimated_experience_years", 0.0),
        extracted_skills=ai_result.get("extracted_skills", []),
    )
