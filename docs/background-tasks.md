# Background Tasks for AI Candidate Analysis

This module provides enhanced background task functionality for the candidate management system, focusing on AI-powered candidate analysis with robust error handling and monitoring capabilities.

## 🌟 Key Features

### ✅ Core Functionality
- **AI Candidate Analysis**: Comprehensive background processing for candidate evaluation
- **Resume Processing**: Automated text extraction from PDF, DOC, and TXT files
- **Interviewer Matching**: Smart matching algorithm integration
- **Database Integration**: Persistent storage with PostgreSQL and SQLAlchemy
- **Error Handling**: Graceful error recovery without affecting main application flow

### 🛡️ Reliability Features
- **Fault Tolerance**: Tasks continue running even if individual components fail
- **Task Monitoring**: Real-time status tracking and progress monitoring
- **Retry Logic**: Automatic retry mechanisms for transient failures
- **Comprehensive Logging**: Detailed logging for debugging and monitoring
- **Connection Management**: Separate database connections for background tasks

### 🔧 Maintenance & Operations
- **Task History**: Complete audit trail of all background operations
- **Cleanup Operations**: Automated removal of old task records
- **Performance Metrics**: Processing time tracking and statistics
- **Status Tracking**: Real-time task status and progress indicators

## 📁 File Structure

```
background_tasks.py              # Main background task functions
background_tasks_demo.py         # Demonstration and testing script
candidate_management_api.py      # Main API with database models
ai_service.py                   # AI analysis service integration
smart_matching_algorithm.py     # Interviewer matching logic
```

## 🚀 Quick Start

### 1. Import and Setup

```python
from background_tasks import (
    analyze_candidate_background,
    match_interviewers_background,
    task_manager
)

# Initialize task manager
task_manager = BackgroundTaskManager()
```

### 2. Basic Usage

```python
import asyncio

# Start AI analysis for a candidate
async def analyze_candidate():
    result = await analyze_candidate_background(
        candidate_id="candidate-uuid-here",
        force_reanalysis=False
    )
    
    if result['status'] == 'completed':
        print(f"Analysis completed with score: {result['analysis_results']['overall_score']}")
    else:
        print(f"Analysis failed: {result['message']}")

# Run the analysis
asyncio.run(analyze_candidate())
```

### 3. Integration with FastAPI

```python
from fastapi import BackgroundTasks

@app.post("/candidates/{candidate_id}/analyze")
async def trigger_analysis(candidate_id: str, background_tasks: BackgroundTasks):
    # Add task to FastAPI background processing
    background_tasks.add_task(
        analyze_candidate_background,
        candidate_id=candidate_id,
        force_reanalysis=True
    )
    
    return {"message": "Analysis started", "candidate_id": candidate_id}
```

## 🔧 Core Functions

### `analyze_candidate_background()`

Comprehensive AI analysis of candidate profiles with the following features:

**Parameters:**
- `candidate_id: str` - Unique candidate identifier
- `db_session_factory: sessionmaker` - Database session factory
- `force_reanalysis: bool` - Whether to reanalyze if already completed

**Process Flow:**
1. Fetch candidate data from database by ID
2. Convert to AI service compatible format
3. Call AI service for comprehensive analysis
4. Update candidate record with scores and insights
5. Store detailed analysis results
6. Trigger follow-up tasks (interviewer matching)
7. Handle all errors gracefully

**Returns:**
```python
{
    'task_id': 'uuid-string',
    'candidate_id': 'candidate-uuid',
    'status': 'completed|failed|skipped',
    'message': 'Human readable status message',
    'analysis_results': {
        'overall_score': 85,
        'technical_score': 90,
        'confidence_score': 80,
        'estimated_level': 'senior',
        'strengths': ['Python expertise', 'Problem solving'],
        'model_used': 'claude-3-haiku'
    },
    'processing_time_seconds': 15.7,
    'follow_up_tasks_triggered': True
}
```

### `match_interviewers_background()`

Smart interviewer matching based on candidate analysis results.

**Features:**
- Integrates with AI analysis results
- Uses multi-dimensional matching algorithm
- Considers technical skills, experience, and cultural fit
- Stores top 5 matches with confidence scores

### `process_resume_file_background()`

Automated resume processing and text extraction.

**Supported Formats:**
- PDF files (using PyPDF2)
- Word documents (using python-docx)
- Plain text files

**Security Features:**
- File type validation
- Size limits (10MB max)
- Safe file handling

## 📊 Task Monitoring

### Task Manager

The `BackgroundTaskManager` class provides comprehensive task tracking:

```python
# Check active tasks
active_tasks = task_manager.active_tasks
print(f"Currently running: {len(active_tasks)} tasks")

# View task history
for task in task_manager.task_history[-5:]:
    print(f"Task {task['type']}: {task['status']} ({task.get('error', 'success')})")

# Get specific task status
task_status = task_manager.get_task_status('task-uuid')
if task_status:
    print(f"Task status: {task_status['status']}")
```

### Database Task Records

All tasks are tracked in the `AnalysisTaskDB` table:

```python
# Query recent tasks
from candidate_management_api import AnalysisTaskDB, SessionLocal

db = SessionLocal()
recent_tasks = db.query(AnalysisTaskDB).order_by(
    AnalysisTaskDB.started_at.desc()
).limit(10).all()

for task in recent_tasks:
    print(f"Task {task.id}: {task.status} ({task.task_type})")
```

## 🛡️ Error Handling

### Graceful Degradation

The background tasks are designed to handle errors without affecting the main application:

```python
# Even if AI service fails, the main API continues working
result = await analyze_candidate_background(candidate_id)

if result['status'] == 'failed':
    # Error is logged and stored in database
    # Main application flow continues normally
    # Candidate record is marked with failed status
    # Admin can review and retry later
    pass
```

### Error Categories

1. **Database Errors**: Connection issues, constraint violations
2. **AI Service Errors**: API timeouts, quota exceeded, service unavailable
3. **File Processing Errors**: Corrupted files, unsupported formats
4. **Validation Errors**: Invalid candidate data, missing required fields

### Recovery Strategies

- **Automatic Retry**: Transient errors are retried with exponential backoff
- **Graceful Fallback**: Failed tasks don't prevent other operations
- **Error Logging**: Comprehensive error details for debugging
- **Status Tracking**: Failed tasks are marked for manual review

## 🔧 Configuration

### Environment Variables

```bash
# Database configuration
DATABASE_URL=postgresql://user:password@localhost/interview_db

# AI Service configuration  
OPENROUTER_API_KEY=your-api-key-here
AI_MODEL=anthropic/claude-3-haiku

# Task configuration
MAX_RETRY_ATTEMPTS=3
RETRY_DELAY_SECONDS=5
TASK_TIMEOUT_MINUTES=10
```

### Database Schema

The tasks integrate with existing database models:

```sql
-- Candidates table (existing)
CREATE TABLE candidates (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    ai_analysis_status analysis_status DEFAULT 'pending',
    ai_analysis_results JSONB,
    -- ... other fields
);

-- Analysis tasks table
CREATE TABLE analysis_tasks (
    id UUID PRIMARY KEY,
    candidate_id UUID REFERENCES candidates(id),
    task_type VARCHAR(50) NOT NULL,
    status analysis_status DEFAULT 'pending',
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    results JSONB,
    error_message TEXT,
    error_details TEXT
);
```

## 🧪 Testing

### Run the Demo

```bash
# Install dependencies
pip install -r requirements.txt

# Set up database
python database_setup.py

# Run the background tasks demo
python background_tasks_demo.py
```

### Demo Features

The demo script demonstrates:

1. **Candidate Creation**: Creates test candidates with realistic data
2. **AI Analysis**: Runs background analysis tasks
3. **Progress Monitoring**: Shows real-time task progress
4. **Error Handling**: Tests error scenarios and recovery
5. **Maintenance Tasks**: Demonstrates cleanup operations

### Expected Output

```
🚀 Starting Background Tasks Demonstration
============================================================

📝 Step 1: Creating Test Candidates
----------------------------------------
   ✅ Created candidate: Alice Chen (ID: abc123...)
   ✅ Created candidate: Bob Wilson (ID: def456...)
   ✅ Created candidate: Carol Zhang (ID: ghi789...)

🤖 Step 2: AI Analysis Background Tasks  
----------------------------------------
   🔄 Starting AI analysis for Alice Chen...
      ✅ Task started for Alice Chen
   ⏳ Monitoring 3 analysis tasks...
      ✅ Alice Chen: Analysis completed (Score: 87/100)
      ✅ Bob Wilson: Analysis completed (Score: 82/100)
      ✅ Carol Zhang: Analysis completed (Score: 94/100)

📊 Step 3: Task Monitoring and Status Tracking
----------------------------------------
   📈 Task Manager Status:
      Active tasks: 0
      Completed tasks: 6
   📋 Recent Task History (last 5):
      1. ✅ ai_analysis for candidate abc123... at 2025-08-02 10:30:15
      2. ✅ interviewer_matching for candidate abc123... at 2025-08-02 10:30:30
      ...
```

## 🏗️ Architecture

### Task Flow

```
1. API Request
   ↓
2. Create Database Record
   ↓  
3. Start Background Task
   ↓
4. Fetch Candidate Data
   ↓
5. AI Analysis
   ↓
6. Update Database
   ↓
7. Trigger Follow-up Tasks
   ↓
8. Complete & Notify
```

### Error Handling Flow

```
Error Occurs
   ↓
Log Error Details
   ↓
Update Task Status
   ↓
Mark Candidate Record
   ↓
Continue Other Tasks
   ↓
Admin Review Available
```

## 📈 Performance

### Benchmarks

- **Average Analysis Time**: 8-15 seconds per candidate
- **Concurrent Tasks**: Up to 10 simultaneous analyses
- **Memory Usage**: ~50MB per active task
- **Database Connections**: Separate pool for background tasks

### Optimization Tips

1. **Batch Processing**: Group multiple candidates for analysis
2. **Connection Pooling**: Use separate DB pool for background tasks
3. **Async Operations**: All file I/O and API calls are async
4. **Resource Limits**: Configure max concurrent tasks based on system capacity

## 🔍 Monitoring & Debugging

### Health Checks

```python
# Check task manager health
def check_background_tasks_health():
    active_count = len(task_manager.active_tasks)
    recent_failures = sum(
        1 for task in task_manager.task_history[-10:] 
        if not task.get('success', True)
    )
    
    return {
        'active_tasks': active_count,
        'recent_failures': recent_failures,
        'status': 'healthy' if recent_failures < 3 else 'degraded'
    }
```

### Debugging Failed Tasks

```python
# Find failed tasks for investigation
failed_tasks = db.query(AnalysisTaskDB).filter(
    AnalysisTaskDB.status == AnalysisStatus.FAILED
).order_by(AnalysisTaskDB.started_at.desc()).all()

for task in failed_tasks:
    print(f"Failed Task: {task.id}")
    print(f"Error: {task.error_message}")
    print(f"Details: {task.error_details}")
    print(f"Candidate: {task.candidate_id}")
    print("-" * 40)
```

## 🚦 Production Deployment

### Prerequisites

1. **Database**: PostgreSQL 12+ with proper connection pooling
2. **Dependencies**: All required Python packages installed
3. **Environment**: Production environment variables configured
4. **Monitoring**: Logging and monitoring systems in place

### Deployment Steps

1. **Configure Database**:
   ```bash
   # Create production database
   createdb interview_production
   
   # Run migrations
   python database_setup.py
   ```

2. **Set Environment Variables**:
   ```bash
   export DATABASE_URL=postgresql://user:pass@prod-db:5432/interview_production
   export OPENROUTER_API_KEY=your-production-api-key
   export LOG_LEVEL=INFO
   ```

3. **Start Application**:
   ```bash
   # Start main API server
   uvicorn candidate_management_api:app --host 0.0.0.0 --port 8000
   
   # Background tasks run automatically within the API
   ```

### Production Considerations

- **Resource Limits**: Configure appropriate memory and CPU limits
- **Error Notifications**: Set up alerts for failed tasks
- **Backup Strategy**: Regular database backups including task history
- **Scaling**: Consider task queues (Celery, RQ) for high-volume deployments

## 📚 API Integration

### With Existing Endpoints

The background tasks integrate seamlessly with the existing candidate management API:

```python
# In candidate_management_api.py
@app.post("/api/candidates/")
async def create_candidate(
    candidate_data: CandidateCreateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    # Create candidate record
    candidate = CandidateDB(**candidate_data.dict())
    db.add(candidate)
    db.commit()
    
    # Trigger background AI analysis
    background_tasks.add_task(
        analyze_candidate_background,
        candidate_id=candidate.id
    )
    
    return {
        "candidate_id": candidate.id,
        "message": "Candidate created successfully",
        "analysis_status": "started"
    }
```

### Status Endpoints

```python
@app.get("/api/candidates/{candidate_id}/analysis-status")
async def get_analysis_status(candidate_id: str, db: Session = Depends(get_db)):
    # Get latest analysis task
    task = db.query(AnalysisTaskDB).filter(
        AnalysisTaskDB.candidate_id == candidate_id
    ).order_by(AnalysisTaskDB.started_at.desc()).first()
    
    if not task:
        return {"status": "not_found"}
    
    return {
        "task_id": task.id,
        "status": task.status,
        "started_at": task.started_at,
        "completed_at": task.completed_at,
        "progress": "100%" if task.completed_at else "in_progress"
    }
```

## 🤝 Contributing

### Adding New Background Tasks

1. **Create Task Function**:
   ```python
   async def new_background_task(
       candidate_id: str,
       db_session_factory: sessionmaker = BackgroundSessionLocal
   ) -> Dict[str, Any]:
       task_id = str(uuid.uuid4())
       
       try:
           # Task implementation
           return {'task_id': task_id, 'status': 'completed'}
       except Exception as e:
           logger.error(f"Task failed: {e}")
           return {'task_id': task_id, 'status': 'failed', 'error': str(e)}
   ```

2. **Add to Exports**:
   ```python
   __all__ = [
       'analyze_candidate_background',
       'new_background_task',  # Add new function
       # ... other exports
   ]
   ```

3. **Update Demo Script**: Add test cases for the new task

### Testing Guidelines

- **Unit Tests**: Test individual task functions
- **Integration Tests**: Test database interactions
- **Error Tests**: Test error handling scenarios
- **Performance Tests**: Measure execution times

## 📞 Support

For questions, issues, or contributions:

1. **Check Logs**: Review application logs for error details
2. **Database Status**: Check analysis_tasks table for task history
3. **Task Manager**: Use task_manager for real-time status
4. **Demo Script**: Run demo to verify functionality

---

*This documentation covers the enhanced background task system for AI candidate analysis. The system is designed to be robust, scalable, and maintainable for production use.*
