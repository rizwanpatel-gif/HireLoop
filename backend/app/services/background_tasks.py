"""
Background Task Functions for Candidate Management System
========================================================

This module contains all background task functions for:
- AI candidate analysis
- Resume processing
- Interviewer matching
- Email notifications
- Data cleanup and maintenance

Each task is designed to be fault-tolerant and includes comprehensive error handling.
"""

import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from pathlib import Path
import json
import traceback

from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine

# Import database models and services
from candidate_management_api import (
    CandidateDB, AnalysisTaskDB, Base, AnalysisStatus, CandidateStatus,
    SessionLocal, DATABASE_URL
)
from ai_service import AIService, CandidateProfile, CandidateSkill, SkillLevel
from smart_matching_algorithm import SmartMatchingAlgorithm, create_sample_interviewer_profiles

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create separate engine for background tasks to avoid connection conflicts
bg_engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
BackgroundSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=bg_engine)


class BackgroundTaskManager:
    """
    Manager class for handling background tasks with error tracking and retry logic
    """
    
    def __init__(self):
        self.active_tasks = {}
        self.task_history = []
        self.max_retries = 3
        self.retry_delay = 5  # seconds
    
    def register_task(self, task_id: str, task_type: str, candidate_id: str):
        """Register a new background task"""
        self.active_tasks[task_id] = {
            'type': task_type,
            'candidate_id': candidate_id,
            'started_at': datetime.utcnow(),
            'retries': 0,
            'status': 'running'
        }
    
    def complete_task(self, task_id: str, success: bool = True, error: str = None):
        """Mark a task as completed"""
        if task_id in self.active_tasks:
            task_info = self.active_tasks.pop(task_id)
            task_info['completed_at'] = datetime.utcnow()
            task_info['success'] = success
            task_info['error'] = error
            self.task_history.append(task_info)
    
    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """Get status of a specific task"""
        if task_id in self.active_tasks:
            return self.active_tasks[task_id]
        
        # Check history
        for task in self.task_history:
            if task.get('task_id') == task_id:
                return task
        
        return None


# Global task manager instance
task_manager = BackgroundTaskManager()


async def analyze_candidate_background(
    candidate_id: str, 
    db_session_factory: sessionmaker = BackgroundSessionLocal,
    force_reanalysis: bool = False
) -> Dict[str, Any]:
    """
    Enhanced background task for AI candidate analysis
    
    Features:
    - Fetches candidate data from database by ID
    - Calls AI service to analyze candidate profile  
    - Updates candidate record with AI score and insights
    - Handles errors gracefully without affecting main flow
    - Includes retry logic and detailed logging
    - Triggers follow-up tasks (interviewer matching)
    
    Args:
        candidate_id: Unique identifier for the candidate
        db_session_factory: Database session factory
        force_reanalysis: Whether to force re-analysis if already completed
        
    Returns:
        Dict containing task results and status information
    """
    task_id = str(uuid.uuid4())
    db = None
    analysis_task = None
    candidate_db = None
    
    # Register task with manager
    task_manager.register_task(task_id, 'ai_analysis', candidate_id)
    
    try:
        logger.info(f"🤖 Starting enhanced AI analysis for candidate {candidate_id}")
        logger.info(f"   Task ID: {task_id}")
        logger.info(f"   Force reanalysis: {force_reanalysis}")
        
        # Create database session
        db = db_session_factory()
        
        # Create analysis task record for tracking
        analysis_task = AnalysisTaskDB(
            id=task_id,
            candidate_id=candidate_id,
            task_type="ai_analysis",
            status=AnalysisStatus.IN_PROGRESS,
            started_at=datetime.utcnow(),
            metadata={
                'force_reanalysis': force_reanalysis,
                'version': '2.0'
            }
        )
        db.add(analysis_task)
        db.flush()  # Get the ID without committing
        
        # Fetch candidate data from database
        candidate_db = db.query(CandidateDB).filter(CandidateDB.id == candidate_id).first()
        
        if not candidate_db:
            raise ValueError(f"Candidate with ID {candidate_id} not found in database")
        
        logger.info(f"   Found candidate: {candidate_db.name} ({candidate_db.email})")
        logger.info(f"   Position: {candidate_db.position}")
        logger.info(f"   Current status: {candidate_db.status}")
        
        # Check if analysis already exists and not forcing reanalysis
        if (not force_reanalysis and 
            candidate_db.ai_analysis_status == AnalysisStatus.COMPLETED and
            candidate_db.ai_analysis_results):
            
            logger.info("   Analysis already completed, skipping (use force_reanalysis=True to override)")
            
            analysis_task.status = AnalysisStatus.COMPLETED
            analysis_task.completed_at = datetime.utcnow()
            analysis_task.results = candidate_db.ai_analysis_results
            analysis_task.notes = "Skipped - analysis already completed"
            
            db.commit()
            
            task_manager.complete_task(task_id, success=True)
            
            return {
                'task_id': task_id,
                'candidate_id': candidate_id,
                'status': 'skipped',
                'message': 'Analysis already completed',
                'existing_results': candidate_db.ai_analysis_results
            }
        
        # Update candidate status to indicate analysis in progress
        candidate_db.ai_analysis_status = AnalysisStatus.IN_PROGRESS
        candidate_db.status = CandidateStatus.ANALYZING
        candidate_db.updated_at = datetime.utcnow()
        db.commit()
        
        logger.info("   Converting candidate data to AI service format...")
        
        # Convert database skills to AI service format
        skills = []
        skills_data = candidate_db.skills or []
        
        for skill_data in skills_data:
            try:
                skill = CandidateSkill(
                    name=skill_data.get('name', ''),
                    level=SkillLevel(skill_data.get('level', 'beginner')),
                    years_experience=float(skill_data.get('years_experience', 0)),
                    projects_count=int(skill_data.get('projects_count', 0)),
                    certifications=skill_data.get('certifications', [])
                )
                skills.append(skill)
            except Exception as skill_error:
                logger.warning(f"   ⚠️ Error processing skill {skill_data}: {skill_error}")
                continue
        
        # Create comprehensive candidate profile for AI analysis
        candidate_profile = CandidateProfile(
            name=candidate_db.name,
            email=candidate_db.email,
            position=candidate_db.position,
            experience_years=float(candidate_db.experience_years or 0),
            skills=skills,
            education=candidate_db.education or "",
            previous_companies=candidate_db.previous_companies or [],
            github_url=candidate_db.github_url or "",
            linkedin_url=candidate_db.linkedin_url or "",
            portfolio_url=candidate_db.portfolio_url or "",
            cover_letter=candidate_db.cover_letter or "",
            resume_text=candidate_db.resume_text or "",
            preferred_salary=float(candidate_db.preferred_salary or 0),
            availability=candidate_db.availability or "",
            phone=candidate_db.phone or "",
            location=candidate_db.location or ""
        )
        
        logger.info(f"   Profile prepared with {len(skills)} skills")
        logger.info(f"   Resume text length: {len(candidate_profile.resume_text)} characters")
        
        # Initialize AI service and perform analysis
        logger.info("   🧠 Calling AI service for candidate analysis...")
        ai_service = AIService()
        
        # Run AI analysis in thread to avoid blocking
        analysis = await asyncio.to_thread(ai_service.analyze_candidate, candidate_profile)
        
        if not analysis:
            raise RuntimeError("AI analysis returned no results - service may be unavailable")
        
        logger.info("   ✅ AI analysis completed successfully")
        logger.info(f"   Overall Score: {analysis.overall_score}/100")
        logger.info(f"   Technical Score: {analysis.technical_score}/100")
        logger.info(f"   Confidence Score: {analysis.confidence_score}/100")
        logger.info(f"   Estimated Level: {analysis.estimated_level}")
        
        # Extract and store analysis results with error handling
        try:
            # Update candidate record with AI scores and insights
            candidate_db.ai_analysis_status = AnalysisStatus.COMPLETED
            candidate_db.status = CandidateStatus.ANALYZED
            candidate_db.ai_overall_score = float(analysis.overall_score)
            candidate_db.ai_technical_score = float(analysis.technical_score)
            candidate_db.ai_experience_score = float(getattr(analysis, 'experience_score', 0))
            candidate_db.ai_cultural_fit_score = float(getattr(analysis, 'cultural_fit_score', 0))
            candidate_db.ai_confidence_score = float(analysis.confidence_score)
            candidate_db.ai_model_used = getattr(ai_service, 'model', 'claude-3-haiku')
            candidate_db.analyzed_at = datetime.utcnow()
            candidate_db.updated_at = datetime.utcnow()
            
            # Create comprehensive analysis results dictionary
            analysis_results = {
                "analysis_version": "2.0",
                "analyzed_at": datetime.utcnow().isoformat(),
                "model_used": getattr(ai_service, 'model', 'claude-3-haiku'),
                "overall_score": analysis.overall_score,
                "technical_score": analysis.technical_score,
                "confidence_score": analysis.confidence_score,
                "estimated_level": analysis.estimated_level,
                "strengths": analysis.strengths,
                "areas_for_improvement": getattr(analysis, 'areas_for_improvement', []),
                
                # Additional detailed scores
                "experience_score": getattr(analysis, 'experience_score', 0),
                "cultural_fit_score": getattr(analysis, 'cultural_fit_score', 0),
                
                # Detailed analysis components
                "competency_scores": _safe_extract_dict(getattr(analysis, 'competency_scores', {})),
                "technical_skills": _safe_extract_dict(getattr(analysis, 'technical_skills', {})),
                "experience_analysis": _safe_extract_dict(getattr(analysis, 'experience_analysis', {})),
                "interview_strategy": _safe_extract_dict(getattr(analysis, 'interview_strategy', {})),
                "hiring_recommendation": _safe_extract_dict(getattr(analysis, 'hiring_recommendation', {})),
                
                # Metadata
                "processing_time_seconds": (datetime.utcnow() - analysis_task.started_at).total_seconds(),
                "skills_analyzed": len(skills),
                "resume_text_length": len(candidate_profile.resume_text)
            }
            
            # Store analysis results in candidate record
            candidate_db.ai_analysis_results = analysis_results
            
            # Update analysis task record
            analysis_task.status = AnalysisStatus.COMPLETED
            analysis_task.completed_at = datetime.utcnow()
            analysis_task.results = analysis_results
            analysis_task.notes = f"Analysis completed successfully with overall score {analysis.overall_score}/100"
            
            # Commit all changes
            db.commit()
            
            logger.info("   💾 Analysis results saved to database")
            
        except Exception as storage_error:
            logger.error(f"   ❌ Error storing analysis results: {storage_error}")
            raise RuntimeError(f"Failed to store analysis results: {storage_error}")
        
        # Mark task as completed in manager
        task_manager.complete_task(task_id, success=True)
        
        # Trigger follow-up tasks
        try:
            logger.info("   🔄 Triggering follow-up interviewer matching...")
            await asyncio.create_task(
                match_interviewers_background(candidate_id, db_session_factory)
            )
        except Exception as followup_error:
            logger.warning(f"   ⚠️ Follow-up task failed (non-critical): {followup_error}")
        
        # Return success result
        result = {
            'task_id': task_id,
            'candidate_id': candidate_id,
            'status': 'completed',
            'message': 'AI analysis completed successfully',
            'analysis_results': {
                'overall_score': analysis.overall_score,
                'technical_score': analysis.technical_score,
                'confidence_score': analysis.confidence_score,
                'estimated_level': analysis.estimated_level,
                'strengths': analysis.strengths[:3],  # Top 3 strengths
                'model_used': getattr(ai_service, 'model', 'claude-3-haiku')
            },
            'processing_time_seconds': (datetime.utcnow() - analysis_task.started_at).total_seconds(),
            'follow_up_tasks_triggered': True
        }
        
        logger.info(f"🎉 AI analysis task completed successfully for candidate {candidate_id}")
        return result
        
    except Exception as e:
        error_message = str(e)
        error_details = traceback.format_exc()
        
        logger.error(f"❌ AI analysis task failed for candidate {candidate_id}")
        logger.error(f"   Error: {error_message}")
        logger.error(f"   Details: {error_details}")
        
        # Update failure status in database
        try:
            if db and candidate_db:
                candidate_db.ai_analysis_status = AnalysisStatus.FAILED
                candidate_db.status = CandidateStatus.SUBMITTED  # Reset to submitted
                candidate_db.updated_at = datetime.utcnow()
            
            if db and analysis_task:
                analysis_task.status = AnalysisStatus.FAILED
                analysis_task.error_message = error_message
                analysis_task.error_details = error_details
                analysis_task.completed_at = datetime.utcnow()
            
            if db:
                db.commit()
                
        except Exception as db_error:
            logger.error(f"   Additional error updating failure status: {db_error}")
        
        # Mark task as failed in manager
        task_manager.complete_task(task_id, success=False, error=error_message)
        
        # Return error result (don't raise to avoid affecting main flow)
        return {
            'task_id': task_id,
            'candidate_id': candidate_id,
            'status': 'failed',
            'message': f'AI analysis failed: {error_message}',
            'error': error_message,
            'error_details': error_details
        }
        
    finally:
        # Always close database connection
        if db:
            try:
                db.close()
            except Exception as close_error:
                logger.error(f"Error closing database connection: {close_error}")


async def match_interviewers_background(
    candidate_id: str,
    db_session_factory: sessionmaker = BackgroundSessionLocal
) -> Dict[str, Any]:
    """
    Background task to find and match suitable interviewers for a candidate
    
    Args:
        candidate_id: Unique identifier for the candidate
        db_session_factory: Database session factory
        
    Returns:
        Dict containing matching results
    """
    task_id = str(uuid.uuid4())
    db = None
    
    try:
        logger.info(f"👥 Starting interviewer matching for candidate {candidate_id}")
        
        db = db_session_factory()
        
        # Get candidate with analysis results
        candidate_db = db.query(CandidateDB).filter(CandidateDB.id == candidate_id).first()
        
        if not candidate_db:
            raise ValueError(f"Candidate {candidate_id} not found")
        
        if not candidate_db.ai_analysis_results:
            logger.warning("   No AI analysis results found, skipping interviewer matching")
            return {'status': 'skipped', 'reason': 'No AI analysis results'}
        
        # Initialize matching algorithm
        matching_algo = SmartMatchingAlgorithm()
        interviewer_profiles = create_sample_interviewer_profiles()
        
        # Convert candidate to matching format
        candidate_skills = []
        for skill_data in candidate_db.skills or []:
            candidate_skills.append({
                'name': skill_data.get('name', ''),
                'level': skill_data.get('level', 'beginner'),
                'years_experience': skill_data.get('years_experience', 0)
            })
        
        candidate_data = {
            'name': candidate_db.name,
            'position': candidate_db.position,
            'skills': candidate_skills,
            'experience_years': candidate_db.experience_years,
            'ai_analysis': candidate_db.ai_analysis_results
        }
        
        # Find matches
        matches = matching_algo.find_best_matches(candidate_data, interviewer_profiles)
        
        # Store matching results
        matching_results = {
            'matched_at': datetime.utcnow().isoformat(),
            'total_interviewers_considered': len(interviewer_profiles),
            'matches_found': len(matches),
            'top_matches': matches[:5]  # Store top 5 matches
        }
        
        candidate_db.interviewer_matches = matching_results
        candidate_db.updated_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"✅ Found {len(matches)} interviewer matches for candidate {candidate_id}")
        
        return {
            'task_id': task_id,
            'candidate_id': candidate_id,
            'status': 'completed',
            'matches_found': len(matches),
            'top_match_score': matches[0]['match_score'] if matches else 0
        }
        
    except Exception as e:
        logger.error(f"❌ Interviewer matching failed for candidate {candidate_id}: {e}")
        return {
            'task_id': task_id,
            'candidate_id': candidate_id,
            'status': 'failed',
            'error': str(e)
        }
        
    finally:
        if db:
            db.close()


async def process_resume_file_background(
    candidate_id: str,
    file_path: str,
    db_session_factory: sessionmaker = BackgroundSessionLocal
) -> Dict[str, Any]:
    """
    Background task to process uploaded resume file and extract text
    
    Args:
        candidate_id: Unique identifier for the candidate
        file_path: Path to the uploaded resume file
        db_session_factory: Database session factory
        
    Returns:
        Dict containing processing results
    """
    task_id = str(uuid.uuid4())
    db = None
    
    try:
        logger.info(f"📄 Processing resume file for candidate {candidate_id}")
        logger.info(f"   File path: {file_path}")
        
        db = db_session_factory()
        
        # Get candidate
        candidate_db = db.query(CandidateDB).filter(CandidateDB.id == candidate_id).first()
        if not candidate_db:
            raise ValueError(f"Candidate {candidate_id} not found")
        
        # Extract text from file based on extension
        file_path_obj = Path(file_path)
        file_extension = file_path_obj.suffix.lower()
        
        extracted_text = ""
        
        if file_extension == '.pdf':
            extracted_text = await _extract_pdf_text(file_path)
        elif file_extension in ['.doc', '.docx']:
            extracted_text = await _extract_word_text(file_path)
        elif file_extension == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                extracted_text = f.read()
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
        
        # Update candidate with extracted text
        candidate_db.resume_text = extracted_text
        candidate_db.resume_file_path = str(file_path)
        candidate_db.updated_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"✅ Resume processed successfully for candidate {candidate_id}")
        logger.info(f"   Extracted {len(extracted_text)} characters")
        
        return {
            'task_id': task_id,
            'candidate_id': candidate_id,
            'status': 'completed',
            'extracted_text_length': len(extracted_text),
            'file_type': file_extension
        }
        
    except Exception as e:
        logger.error(f"❌ Resume processing failed for candidate {candidate_id}: {e}")
        return {
            'task_id': task_id,
            'candidate_id': candidate_id,
            'status': 'failed',
            'error': str(e)
        }
        
    finally:
        if db:
            db.close()


def _safe_extract_dict(obj) -> Dict[str, Any]:
    """
    Safely extract dictionary from object that may have __dict__ attribute
    
    Args:
        obj: Object to extract dictionary from
        
    Returns:
        Dictionary representation of object
    """
    try:
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        elif isinstance(obj, dict):
            return obj
        else:
            return {}
    except Exception:
        return {}


async def _extract_pdf_text(file_path: str) -> str:
    """Extract text from PDF file"""
    try:
        import PyPDF2
        
        def extract_sync():
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        
        return await asyncio.to_thread(extract_sync)
        
    except ImportError:
        logger.error("PyPDF2 not installed for PDF processing")
        return ""
    except Exception as e:
        logger.error(f"Error extracting PDF text: {e}")
        return ""


async def _extract_word_text(file_path: str) -> str:
    """Extract text from Word document"""
    try:
        import docx
        
        def extract_sync():
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        
        return await asyncio.to_thread(extract_sync)
        
    except ImportError:
        logger.error("python-docx not installed for Word document processing")
        return ""
    except Exception as e:
        logger.error(f"Error extracting Word text: {e}")
        return ""


async def cleanup_old_tasks(
    days_old: int = 30,
    db_session_factory: sessionmaker = BackgroundSessionLocal
) -> Dict[str, Any]:
    """
    Background maintenance task to clean up old analysis tasks
    
    Args:
        days_old: Remove tasks older than this many days
        db_session_factory: Database session factory
        
    Returns:
        Dict containing cleanup results
    """
    db = None
    
    try:
        logger.info(f"🧹 Starting cleanup of analysis tasks older than {days_old} days")
        
        db = db_session_factory()
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        # Find old completed tasks
        old_tasks = db.query(AnalysisTaskDB).filter(
            AnalysisTaskDB.completed_at < cutoff_date,
            AnalysisTaskDB.status.in_([AnalysisStatus.COMPLETED, AnalysisStatus.FAILED])
        ).all()
        
        # Delete old tasks
        deleted_count = 0
        for task in old_tasks:
            db.delete(task)
            deleted_count += 1
        
        db.commit()
        
        logger.info(f"✅ Cleanup completed: removed {deleted_count} old tasks")
        
        return {
            'status': 'completed',
            'deleted_tasks': deleted_count,
            'cutoff_date': cutoff_date.isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Cleanup task failed: {e}")
        return {
            'status': 'failed',
            'error': str(e)
        }
        
    finally:
        if db:
            db.close()


# Export main functions
__all__ = [
    'analyze_candidate_background',
    'match_interviewers_background', 
    'process_resume_file_background',
    'cleanup_old_tasks',
    'task_manager',
    'BackgroundTaskManager'
]
