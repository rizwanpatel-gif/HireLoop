# Phase 4: Candidate Management API 📋

Complete candidate management system with database integration, background AI analysis, and smart interviewer matching.

## 🌟 Features

### Core Functionality
- **Candidate Creation**: Form-based submission with file uploads
- **Background Processing**: Asynchronous AI analysis tasks
- **Database Integration**: PostgreSQL with SQLAlchemy ORM
- **File Management**: Resume upload and text extraction
- **Status Tracking**: Real-time progress monitoring
- **Smart Matching**: AI-powered interviewer recommendations

### API Endpoints
- `POST /api/candidates/` - Create new candidate
- `GET /api/candidates/` - List candidates with filtering
- `GET /api/candidates/{id}` - Get candidate details
- `GET /api/candidates/{id}/analysis` - Get AI analysis results
- `POST /api/candidates/{id}/reanalyze` - Trigger re-analysis
- `GET /api/analysis-tasks/{id}` - Check task status

## 🚀 Quick Start

### 1. Database Setup
```sql
-- Create PostgreSQL database
CREATE DATABASE interview_db;
CREATE USER interview_user WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE interview_db TO interview_user;
```

### 2. Environment Configuration
```bash
# Database connection
export DATABASE_URL="postgresql://interview_user:password@localhost/interview_db"

# AI service
export OPENROUTER_API_KEY="your_openrouter_api_key"

# File upload directory
export UPLOAD_DIR="uploads/resumes"
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Start API Server
```bash
python candidate_management_api.py
```

### 5. Run Demo
```bash
python candidate_management_demo.py
```

## 📊 Database Schema

### Candidates Table
```sql
CREATE TABLE candidates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    position VARCHAR(255) NOT NULL,
    experience_years FLOAT NOT NULL,
    phone VARCHAR(50),
    location VARCHAR(255),
    
    -- Resume and portfolio
    resume_file_path VARCHAR(500),
    resume_text TEXT,
    portfolio_url VARCHAR(500),
    github_url VARCHAR(500),
    linkedin_url VARCHAR(500),
    
    -- Skills and experience (JSON)
    skills JSON,
    education TEXT,
    previous_companies JSON,
    
    -- Application details
    cover_letter TEXT,
    preferred_salary FLOAT,
    availability VARCHAR(255),
    remote_preference VARCHAR(50),
    
    -- Status tracking
    status VARCHAR(50) DEFAULT 'submitted',
    source VARCHAR(100),
    
    -- AI Analysis Results
    ai_analysis_status VARCHAR(50) DEFAULT 'pending',
    ai_overall_score FLOAT,
    ai_technical_score FLOAT,
    ai_experience_score FLOAT,
    ai_cultural_fit_score FLOAT,
    ai_analysis_results JSON,
    ai_model_used VARCHAR(100),
    ai_confidence_score FLOAT,
    
    -- Matching and scheduling
    matched_interviewers JSON,
    interview_scheduled BOOLEAN DEFAULT FALSE,
    interview_datetime TIMESTAMP,
    interview_type VARCHAR(50),
    
    -- Notes and metadata
    recruiter_notes TEXT,
    red_flags JSON,
    tags JSON,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    analyzed_at TIMESTAMP
);
```

### Analysis Tasks Table
```sql
CREATE TABLE analysis_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id UUID NOT NULL REFERENCES candidates(id),
    status VARCHAR(50) DEFAULT 'pending',
    task_type VARCHAR(50),
    priority INTEGER DEFAULT 1,
    
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    
    results JSON,
    cost_estimate FLOAT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## 🔌 API Usage Examples

### Create Candidate with Form Data
```python
import requests

# Prepare candidate data
form_data = {
    'name': 'John Doe',
    'email': 'john.doe@email.com',
    'position': 'Senior Python Developer',
    'experience_years': 5.0,
    'skills': json.dumps([
        {"name": "Python", "level": "advanced", "years_experience": 5, "projects_count": 10},
        {"name": "Django", "level": "intermediate", "years_experience": 3, "projects_count": 6}
    ]),
    'phone': '+1-555-0123',
    'location': 'San Francisco, CA',
    'education': 'B.S. Computer Science',
    'previous_companies': json.dumps(['Google', 'Facebook']),
    'cover_letter': 'Experienced Python developer...',
    'preferred_salary': 150000,
    'availability': 'Available immediately',
    'remote_preference': 'hybrid'
}

# Optional file upload
files = {
    'resume_file': ('resume.pdf', open('path/to/resume.pdf', 'rb'), 'application/pdf')
}

# Create candidate
response = requests.post(
    'http://localhost:8000/api/candidates/',
    data=form_data,
    files=files
)

result = response.json()
print(f"Candidate ID: {result['candidate_id']}")
print(f"Analysis Task ID: {result['analysis_task_id']}")
```

### List Candidates with Filtering
```python
# Get all candidates
response = requests.get('http://localhost:8000/api/candidates/')
candidates = response.json()

# Filter by status
response = requests.get('http://localhost:8000/api/candidates/', params={
    'status': 'analyzed',
    'page': 1,
    'page_size': 10
})

# Filter by experience and score
response = requests.get('http://localhost:8000/api/candidates/', params={
    'min_experience': 5.0,
    'min_score': 80.0,
    'position': 'Python'
})

# Search candidates
response = requests.get('http://localhost:8000/api/candidates/', params={
    'search': 'john python'
})
```

### Monitor Analysis Progress
```python
import time

candidate_id = "550e8400-e29b-41d4-a716-446655440000"

# Check candidate status
while True:
    response = requests.get(f'http://localhost:8000/api/candidates/{candidate_id}')
    candidate = response.json()
    
    status = candidate['ai_analysis_status']
    if status == 'completed':
        print(f"Analysis complete! Score: {candidate['ai_overall_score']}/100")
        break
    elif status == 'failed':
        print("Analysis failed")
        break
    else:
        print(f"Status: {status}")
        time.sleep(5)
```

### Get Detailed Analysis Results
```python
# Get AI analysis results
response = requests.get(f'http://localhost:8000/api/candidates/{candidate_id}/analysis')
analysis = response.json()

if analysis['status'] == 'completed':
    results = analysis['analysis_results']
    
    print(f"Overall Score: {results['overall_score']}/100")
    print(f"Technical Score: {results['technical_score']}/100")
    print(f"Estimated Level: {results['estimated_level']}")
    print(f"Strengths: {', '.join(results['strengths'])}")
    
    # Competency breakdown
    competency = results.get('competency_scores', {})
    for skill, score in competency.items():
        print(f"{skill}: {score}/100")
    
    # Interviewer matches
    matches = analysis.get('matched_interviewers', [])
    for match in matches:
        print(f"Interviewer: {match['interviewer_name']} ({match['overall_score']}/100)")
```

## 📁 File Upload Handling

### Supported File Types
- **PDF**: `.pdf` (requires PyPDF2)
- **Word**: `.doc`, `.docx` (requires python-docx)
- **Text**: `.txt`

### File Validation
```python
# Maximum file size: 10MB
MAX_FILE_SIZE = 10 * 1024 * 1024

# Allowed extensions
ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx", ".txt"}

def validate_file(file: UploadFile) -> None:
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file selected")
    
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="File type not allowed")
    
    if file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large")
```

### Text Extraction
```python
def extract_text_from_resume(file_path: str) -> str:
    file_ext = Path(file_path).suffix.lower()
    
    if file_ext == '.txt':
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    elif file_ext == '.pdf':
        import PyPDF2
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
    
    elif file_ext in ['.doc', '.docx']:
        import python_docx
        doc = python_docx.Document(file_path)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])
    
    return ""
```

## ⚙️ Background Processing

### Analysis Workflow
```python
async def process_candidate_analysis(candidate_id: str):
    """
    1. Get candidate from database
    2. Convert to AI service format
    3. Perform AI analysis
    4. Store results in database
    5. Trigger interviewer matching
    6. Update candidate status
    """
    
    # Step 1: Database retrieval
    candidate_db = db.query(CandidateDB).filter(CandidateDB.id == candidate_id).first()
    
    # Step 2: Format conversion
    candidate_profile = CandidateProfile(
        name=candidate_db.name,
        email=candidate_db.email,
        # ... other fields
    )
    
    # Step 3: AI analysis
    ai_service = AIService()
    analysis = await asyncio.to_thread(ai_service.analyze_candidate, candidate_profile)
    
    # Step 4: Store results
    candidate_db.ai_analysis_results = analysis_dict
    candidate_db.ai_analysis_status = AnalysisStatus.COMPLETED
    db.commit()
    
    # Step 5: Trigger matching
    await process_interviewer_matching(candidate_id)
```

### Task Status Tracking
```python
class AnalysisStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

# Track task progress
analysis_task = AnalysisTaskDB(
    candidate_id=candidate_id,
    task_type="analysis",
    status=AnalysisStatus.IN_PROGRESS,
    started_at=datetime.utcnow()
)
```

## 🎯 Smart Interviewer Matching

### Matching Process
```python
async def process_interviewer_matching(candidate_id: str):
    """
    1. Get candidate analysis results
    2. Initialize smart matching algorithm
    3. Find best interviewer matches
    4. Store match recommendations
    5. Update candidate status
    """
    
    # Initialize smart matcher
    smart_matcher = SmartMatchingAlgorithm(ai_service, calendar_service)
    interviewer_profiles = create_sample_interviewer_profiles()
    
    # Find matches
    matches = await smart_matcher.find_best_matches(
        candidate=candidate_profile,
        interviewer_profiles=interviewer_profiles,
        interview_date_range=(start_date, end_date),
        required_interview_type=InterviewType.TECHNICAL,
        max_results=5
    )
    
    # Store matches
    match_data = []
    for match in matches:
        match_data.append({
            "interviewer_name": match.interviewer_profile.interviewer.name,
            "overall_score": round(match.overall_match_score, 1),
            "confidence": match.confidence_level.value,
            "available_slots": len(match.available_slots),
            "match_reasons": match.match_reasons
        })
    
    candidate_db.matched_interviewers = match_data
```

## 📊 Candidate Status Flow

```
SUBMITTED → ANALYZING → ANALYZED → SCHEDULED → INTERVIEWED → HIRED/REJECTED
    ↓           ↓           ↓           ↓            ↓
 Form Data   AI Analysis  Matching   Calendar    Interview
 Received    Running      Complete   Booking     Complete
```

### Status Definitions
- **SUBMITTED**: Initial application received
- **ANALYZING**: AI analysis in progress
- **ANALYZED**: Analysis complete, ready for review
- **SCHEDULED**: Interview scheduled
- **INTERVIEWED**: Interview completed
- **HIRED**: Offer extended/accepted
- **REJECTED**: Application declined

## 🔍 Advanced Filtering & Search

### Available Filters
```python
# Experience range
min_experience=5.0
max_experience=10.0

# AI scores
min_score=80.0

# Status filtering
status="analyzed"

# Position search
position="Python Developer"

# Text search (name, email, position)
search="john python senior"

# Pagination
page=1
page_size=20
```

### Complex Query Example
```python
# Find senior Python developers with high scores
response = requests.get('http://localhost:8000/api/candidates/', params={
    'position': 'Python',
    'min_experience': 5.0,
    'min_score': 85.0,
    'status': 'analyzed',
    'page': 1,
    'page_size': 10
})
```

## 🛡️ Error Handling & Validation

### Input Validation
```python
class CandidateCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr = Field(...)
    experience_years: float = Field(..., ge=0, le=50)
    skills: List[SkillRequest] = Field(..., min_items=1)
    
    @validator('skills')
    def validate_skills(cls, v):
        for skill in v:
            if not skill.name or not skill.level:
                raise ValueError("Each skill must have name and level")
        return v
```

### Error Responses
```python
# Validation error
{
    "detail": [
        {
            "loc": ["skills", 0, "level"],
            "msg": "Level must be one of: beginner, intermediate, advanced, expert",
            "type": "value_error"
        }
    ]
}

# Business logic error
{
    "detail": "Candidate with email john@example.com already exists"
}

# System error
{
    "detail": "Failed to create candidate: Database connection error"
}
```

## 🔒 Security Considerations

### Data Protection
- Email uniqueness validation
- File type and size restrictions
- SQL injection prevention via ORM
- Input sanitization and validation

### File Security
```python
# Secure file handling
def save_resume_file(file: UploadFile, candidate_id: str) -> str:
    # Validate file type and size
    validate_file(file)
    
    # Generate secure filename
    file_ext = Path(file.filename).suffix.lower()
    filename = f"{candidate_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{file_ext}"
    
    # Save to secure directory
    file_path = UPLOAD_DIR / filename
    with open(file_path, "wb") as buffer:
        content = file.file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large")
        buffer.write(content)
    
    return str(file_path)
```

## 📈 Performance Optimization

### Database Indexing
```sql
-- Performance indexes
CREATE INDEX idx_candidates_email ON candidates(email);
CREATE INDEX idx_candidates_status ON candidates(status);
CREATE INDEX idx_candidates_position ON candidates(position);
CREATE INDEX idx_candidates_created_at ON candidates(created_at);
CREATE INDEX idx_candidates_ai_score ON candidates(ai_overall_score);
CREATE INDEX idx_analysis_tasks_candidate_id ON analysis_tasks(candidate_id);
CREATE INDEX idx_analysis_tasks_status ON analysis_tasks(status);
```

### Async Processing
```python
# Background task execution
background_tasks.add_task(process_candidate_analysis, candidate_id)

# Concurrent analysis support
async def process_candidate_analysis(candidate_id: str):
    analysis = await asyncio.to_thread(ai_service.analyze_candidate, candidate_profile)
```

### Pagination & Limiting
```python
# Efficient pagination
offset = (page - 1) * page_size
candidates = query.offset(offset).limit(page_size).all()

# Result size limits
max_results = min(requested_results, 100)  # Cap at 100 results
```

## 🧪 Testing

### Unit Tests
```python
def test_create_candidate():
    response = client.post("/api/candidates/", data=valid_candidate_data)
    assert response.status_code == 200
    assert "candidate_id" in response.json()

def test_invalid_email():
    data = {**valid_candidate_data, "email": "invalid-email"}
    response = client.post("/api/candidates/", data=data)
    assert response.status_code == 422

def test_duplicate_email():
    # Create first candidate
    client.post("/api/candidates/", data=valid_candidate_data)
    
    # Try to create duplicate
    response = client.post("/api/candidates/", data=valid_candidate_data)
    assert response.status_code == 409
```

### Integration Tests
```python
async def test_full_workflow():
    # Create candidate
    response = await client.post("/api/candidates/", data=candidate_data)
    candidate_id = response.json()["candidate_id"]
    
    # Wait for analysis
    await wait_for_analysis_completion(candidate_id)
    
    # Verify results
    response = await client.get(f"/api/candidates/{candidate_id}")
    assert response.json()["ai_analysis_status"] == "completed"
```

## 🚀 Production Deployment

### Docker Configuration
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "candidate_management_api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables
```bash
# Production settings
DATABASE_URL=postgresql://user:pass@db:5432/interview_db
OPENROUTER_API_KEY=your_production_key
UPLOAD_DIR=/app/uploads
MAX_FILE_SIZE=10485760
LOG_LEVEL=INFO

# Security
SECRET_KEY=your_secret_key
ALLOWED_HOSTS=your-domain.com
```

### Monitoring & Logging
```python
# Structured logging
logger.info(f"Candidate created", extra={
    "candidate_id": candidate_id,
    "position": position,
    "experience_years": experience_years,
    "skills_count": len(skills),
    "has_resume_file": bool(resume_file)
})

# Metrics tracking
metrics = {
    "candidates_created": len(created_candidates),
    "analysis_success_rate": success_rate,
    "average_processing_time": avg_time,
    "file_upload_rate": upload_rate
}
```

## 🔗 Integration Examples

### Frontend Integration
```javascript
// Create candidate with file upload
const formData = new FormData();
formData.append('name', 'John Doe');
formData.append('email', 'john@example.com');
formData.append('skills', JSON.stringify(skills));
formData.append('resume_file', fileInput.files[0]);

const response = await fetch('/api/candidates/', {
    method: 'POST',
    body: formData
});

const result = await response.json();
console.log('Candidate ID:', result.candidate_id);
```

### Webhook Integration
```python
# Notify external systems
async def notify_candidate_analyzed(candidate_id: str):
    webhook_url = os.getenv('CANDIDATE_WEBHOOK_URL')
    if webhook_url:
        payload = {
            "event": "candidate_analyzed",
            "candidate_id": candidate_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        await httpx.post(webhook_url, json=payload)
```

---

**Phase 4 Complete!** 🎉

Your interview scheduling system now has comprehensive candidate management with:
- Form-based candidate creation with file uploads
- Background AI analysis processing
- Database persistence and querying
- Smart interviewer matching
- Real-time status tracking
- Production-ready error handling and validation
