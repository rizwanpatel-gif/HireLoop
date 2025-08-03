# Phase 6: Background Processing Implementation
## Complete FastAPI BackgroundTasks Integration

### Overview
This phase implements a comprehensive background processing system using FastAPI BackgroundTasks that handles:
- ✅ AI candidate analysis without blocking API responses
- ✅ Google Calendar event creation asynchronously  
- ✅ Email notifications after successful scheduling
- ✅ Graceful failure handling with retry logic
- ✅ Complete logging of all background task activities

### Architecture Components

#### 1. Enhanced Background Tasks (`backend/app/services/background_tasks.py`)
**New Features Added:**
- FastAPI BackgroundTasks integration functions
- Async processing with email notifications
- Calendar event creation with notifications
- Comprehensive error handling and retry logic
- Task status tracking and management

**Key Functions:**
```python
# Main integration functions
async def schedule_candidate_analysis(background_tasks, candidate_id, hiring_team_emails)
async def schedule_interview_creation(background_tasks, candidate_id, interviewer_emails, interview_datetime)
async def schedule_email_notification(background_tasks, email_type, recipient_emails, email_data)

# Background processing functions  
async def process_candidate_analysis_with_notifications(candidate_id, task_id, hiring_team_emails)
async def create_calendar_event_with_notifications(candidate_id, task_id, interviewer_emails, interview_datetime)
async def send_notification_email(task_id, email_type, recipient_emails, email_data)
```

#### 2. Email Service (`backend/app/services/email_service.py`)
**Features:**
- Async email sending with SMTP support
- Retry logic with exponential backoff
- Template system for different email types
- HTML and text content support
- Attachment handling
- Built-in email templates for interviews and analysis

**Key Classes:**
```python
class EmailService:
    async def send_email_async(to_emails, subject, html_content, text_content, attachments)
    async def send_interview_scheduled_notification(interviewer_emails, candidate_name, ...)
    async def send_analysis_complete_notification(hiring_team_emails, candidate_name, ai_score, ...)
```

#### 3. API Routes (`backend/app/api/background_routes.py`)
**Endpoints:**
- `POST /api/v1/background/analyze-candidate` - Schedule AI analysis
- `POST /api/v1/background/schedule-interview` - Schedule interview with calendar
- `POST /api/v1/background/send-notification` - Send email notifications
- `GET /api/v1/background/task-status/{task_id}` - Check task status
- `GET /api/v1/background/active-tasks` - View active tasks overview
- `GET /api/v1/background/health` - Health check
- `GET /api/v1/background/examples` - Usage examples

### Usage Examples

#### 1. Schedule Candidate Analysis with Notifications
```python
# API Call
POST /api/v1/background/analyze-candidate
{
    "candidate_id": "candidate_123",
    "hiring_team_emails": ["hr@company.com", "manager@company.com"],
    "force_reanalysis": false
}

# Response (Immediate)
{
    "message": "Candidate analysis scheduled successfully",
    "task_info": {
        "task_id": "uuid-task-id",
        "status": "scheduled",
        "candidate_id": "candidate_123",
        "scheduled_at": "2024-01-01T12:00:00",
        "notification_emails": 2
    },
    "status": "processing",
    "estimated_completion": "2-5 minutes"
}
```

**Background Process:**
1. FastAPI immediately returns 202 Accepted
2. Background task processes AI analysis
3. Email notifications sent to hiring team when complete
4. All activities logged for debugging

#### 2. Schedule Interview with Calendar Integration
```python
# API Call
POST /api/v1/background/schedule-interview
{
    "candidate_id": "candidate_123",
    "interviewer_emails": ["interviewer1@company.com", "interviewer2@company.com"],
    "interview_datetime": "2024-01-15T14:00:00",
    "duration_minutes": 60,
    "position": "Software Engineer",
    "meeting_details": {
        "location": "Conference Room A",
        "video_link": "https://meet.google.com/abc-def-ghi"
    }
}

# Response (Immediate)
{
    "message": "Interview creation scheduled successfully",
    "task_info": {
        "task_id": "uuid-task-id",
        "status": "scheduled",
        "candidate_id": "candidate_123",
        "interview_datetime": "2024-01-15T14:00:00",
        "scheduled_at": "2024-01-01T12:00:00",
        "interviewers": 2
    },
    "status": "processing",
    "estimated_completion": "1-3 minutes"
}
```

**Background Process:**
1. FastAPI immediately returns 202 Accepted
2. Background task creates Google Calendar event
3. Email notifications sent to all interviewers
4. Meeting links and details distributed
5. All activities logged for debugging

#### 3. Check Task Status
```python
# API Call
GET /api/v1/background/task-status/uuid-task-id

# Response
{
    "task_id": "uuid-task-id",
    "status": "completed",
    "created_at": "2024-01-01T12:00:00",
    "completed_at": "2024-01-01T12:03:30",
    "success": true,
    "error": null
}
```

### Error Handling & Retry Logic

#### Retry Mechanisms
- **Email Service**: 3 retries with exponential backoff (2^attempt seconds)
- **Background Tasks**: Built-in retry logic in BackgroundTaskManager
- **Calendar Service**: Integrates with existing OAuth2 token refresh

#### Graceful Failure Handling
```python
# Example error handling
try:
    # Process background task
    result = await process_task()
    task_manager.complete_task(task_id, success=True)
except Exception as e:
    logger.error(f"Task failed: {str(e)}")
    task_manager.complete_task(task_id, success=False, error=str(e))
    # Optionally send failure notification
```

#### Comprehensive Logging
```python
# All activities are logged with structured format
logger.info(f"🚀 Scheduling candidate analysis for {candidate_id}")
logger.info(f"📅 Creating calendar event with notifications")
logger.info(f"📧 Sending notification email: {email_type}")
logger.info(f"✅ Analysis complete and notifications sent")
logger.error(f"❌ Task failed with error: {error_message}")
```

### Integration with Existing Systems

#### Frontend Integration
The frontend can now use the enhanced API service to trigger background processes:

```javascript
// Using the existing apiService.js
const analysisResult = await apiService.candidateAPI.scheduleAnalysis({
    candidate_id: candidateId,
    hiring_team_emails: ['hr@company.com'],
    force_reanalysis: false
});

// Check task status
const taskStatus = await apiService.systemAPI.getTaskStatus(analysisResult.task_info.task_id);
```

#### Database Integration
- Uses existing `BackgroundSessionLocal` for database operations
- Integrates with `CandidateDB`, `AnalysisTaskDB` models
- Maintains existing database structure and relationships

#### Service Integration
- **AI Service**: Enhanced analysis with notification triggers
- **Calendar Service**: Async event creation with existing OAuth2 system
- **Email Service**: New service with template system and retry logic

### Configuration Requirements

#### Environment Variables
```bash
# Email Service Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
FROM_EMAIL=noreply@yourcompany.com

# Existing calendar service OAuth2 settings remain the same
```

#### Dependencies
```bash
# Additional dependencies for Phase 6
pip install fastapi
pip install python-multipart
pip install pydantic
# Email service already uses built-in smtplib
```

### Monitoring & Debugging

#### Task Status Monitoring
```python
# Get overview of all background tasks
GET /api/v1/background/active-tasks

# Response includes:
{
    "summary": {
        "active_tasks": 3,
        "completed_tasks": 45,
        "successful_tasks": 42,
        "failed_tasks": 3,
        "success_rate": 93.3
    },
    "active_tasks": [...],
    "recent_completed": [...]
}
```

#### Logging Structure
- **🚀** Task scheduling
- **🔄** Task processing
- **📧** Email operations
- **📅** Calendar operations
- **✅** Success operations
- **❌** Error operations
- **🔍** Status checking
- **📊** Monitoring operations

### Performance Characteristics

#### Response Times
- **API Response**: Immediate (< 100ms) - Returns 202 Accepted
- **AI Analysis**: 2-5 minutes background processing
- **Calendar Creation**: 1-3 minutes background processing
- **Email Notifications**: 30 seconds background processing

#### Scalability
- Non-blocking API responses
- Parallel background task processing
- Independent email and calendar operations
- Built-in retry and error recovery

### Testing Strategy

#### Unit Testing
```python
# Test background task scheduling
async def test_schedule_candidate_analysis():
    background_tasks = BackgroundTasks()
    result = await schedule_candidate_analysis(
        background_tasks, "test_candidate", ["test@example.com"]
    )
    assert result["status"] == "scheduled"
    assert "task_id" in result
```

#### Integration Testing
```python
# Test complete workflow
async def test_analysis_workflow():
    # 1. Schedule analysis
    # 2. Wait for completion
    # 3. Verify email sent
    # 4. Check task status
```

### Production Deployment

#### Process Management
- FastAPI BackgroundTasks runs in main application process
- No additional worker processes required
- Automatic task cleanup and memory management

#### Monitoring Integration
- Task status tracking via API endpoints
- Structured logging for external monitoring
- Health check endpoints for load balancers

### Next Steps & Extensions

#### Possible Enhancements
1. **Webhook Integration**: Add webhook notifications for task completion
2. **Task Queuing**: Implement Redis/Celery for heavy workloads
3. **Batch Processing**: Add bulk operation support
4. **Real-time Updates**: WebSocket notifications for frontend
5. **Advanced Scheduling**: Cron-like scheduling for recurring tasks

#### Scalability Considerations
- Current implementation suitable for moderate workloads (< 1000 tasks/hour)
- For high-volume scenarios, consider dedicated task queue systems
- Database connection pooling may need adjustment for heavy usage

---

## Summary

Phase 6 successfully implements a comprehensive background processing system that:

✅ **Processes AI candidate analysis without blocking API response**
✅ **Creates Google Calendar events asynchronously**  
✅ **Sends email notifications after successful scheduling**
✅ **Handles failures gracefully with retry logic**
✅ **Logs all background task activities for debugging**

The implementation provides immediate API responses while ensuring reliable background processing with comprehensive error handling, monitoring, and integration with existing systems.
