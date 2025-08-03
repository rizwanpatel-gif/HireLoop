# Interview Scheduling System

A comprehensive interview scheduling system that combines AI-powered candidate analysis, smart interviewer matching, and automated Google Calendar integration.

## 🌟 Key Features

### ✅ Complete Interview Workflow
- **Candidate Management**: Create and manage candidate profiles with comprehensive data
- **AI Analysis**: Automated candidate evaluation using advanced AI models
- **Smart Matching**: AI-powered interviewer matching based on skills and experience
- **Interview Scheduling**: Automated scheduling with calendar integration
- **Google Calendar**: Automatic calendar event creation with Google Meet links
- **Email Notifications**: Automated interview invitations and reminders

### 🤖 AI-Powered Intelligence
- **Candidate Analysis**: Comprehensive AI evaluation of skills, experience, and fit
- **Interviewer Matching**: Smart algorithm to find the best interviewer matches
- **Confidence Scoring**: AI confidence levels for matching and recommendations
- **Focus Areas**: AI-recommended interview focus areas and preparation materials

### 📅 Calendar Integration
- **Google Calendar**: Seamless integration with Google Calendar
- **Google Meet**: Automatic video conference link generation
- **Email Invitations**: Automated calendar invites to all participants
- **Smart Reminders**: Multiple reminder notifications (24h, 30min, 10min before)

### 🛡️ Production Ready
- **Database Integration**: PostgreSQL with comprehensive data models
- **Background Processing**: Asynchronous task processing for scalability
- **Error Handling**: Graceful error recovery and retry mechanisms
- **API Documentation**: Comprehensive REST API with OpenAPI documentation

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd interview-scheduling-system

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration
```

### 2. Database Setup

```bash
# Create PostgreSQL database
createdb interview_db

# Run database migrations
python database_setup.py
```

### 3. Configuration

Create a `.env` file with the following configuration:

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost/interview_db

# AI Service Configuration
OPENROUTER_API_KEY=your-openrouter-api-key
AI_MODEL=anthropic/claude-3-haiku

# Google Calendar Configuration
GOOGLE_CREDENTIALS_FILE=credentials.json
GOOGLE_TOKEN_DIR=tokens

# Application Configuration
LOG_LEVEL=INFO
MAX_CONCURRENT_ANALYSES=10
```

### 4. Google Calendar Setup

1. **Create Google Cloud Project**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable Google Calendar API

2. **Create OAuth2 Credentials**:
   - Go to "Credentials" in Google Cloud Console
   - Create "OAuth 2.0 Client IDs" for desktop application
   - Download the JSON file as `credentials.json`

3. **Configure OAuth Scopes**:
   - The application requires these scopes:
     - `https://www.googleapis.com/auth/calendar`
     - `https://www.googleapis.com/auth/calendar.events`

### 5. Start the System

```bash
# Start the API server
python candidate_management_api.py

# The API will be available at:
# - Main API: http://localhost:8000
# - Documentation: http://localhost:8000/docs
# - Interview Scheduling: http://localhost:8000/api/schedule-interview/
```

## 🎯 Core API Endpoints

### Interview Scheduling

**POST /api/schedule-interview/**
```json
{
  "candidate_id": "uuid-string",
  "preferred_time": "2024-08-15T14:00:00",
  "duration_minutes": 90,
  "interview_type": "technical",
  "interview_round": 1,
  "is_remote": true,
  "additional_attendees": ["hr@company.com"],
  "notes": "Technical interview for Senior Developer position"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Interview successfully scheduled with John Smith for Friday, August 15 at 2:00 PM",
  "interview": {
    "interview_id": "interview-uuid",
    "candidate_name": "Sarah Chen",
    "interviewer_name": "John Smith",
    "interviewer_email": "john.smith@company.com",
    "scheduled_time": "2024-08-15T14:00:00",
    "ai_match_score": 92.5,
    "ai_match_confidence": 0.85,
    "google_meet_link": "https://meet.google.com/abc-defg-hij",
    "ai_recommended_focus_areas": ["Python expertise", "System design"],
    "preparation_materials": [...]
  },
  "calendar_details": {
    "event_creation_status": "in_progress",
    "attendees": ["sarah.chen@demo.com", "john.smith@company.com"],
    "google_meet_enabled": true
  },
  "next_steps": [
    "📧 Calendar invitations will be sent to all participants",
    "🎥 Google Meet link will be generated and shared",
    "⏰ Interview scheduled for Friday, August 15, 2024 at 02:00 PM"
  ]
}
```

### Candidate Management

**POST /api/candidates/**
```bash
curl -X POST "http://localhost:8000/api/candidates/" \
  -F "name=Sarah Chen" \
  -F "email=sarah.chen@demo.com" \
  -F "position=Senior Full Stack Developer" \
  -F "experience_years=6.0" \
  -F "skills=[{\"name\":\"Python\",\"level\":\"expert\",\"years_experience\":6.0}]" \
  -F "resume_file=@resume.pdf"
```

**GET /api/candidates/**
```bash
curl "http://localhost:8000/api/candidates/?status=analyzed&min_score=80"
```

### Interview Management

**GET /api/interviews/**
```bash
curl "http://localhost:8000/api/interviews/?status=scheduled&from_date=2024-08-01"
```

**GET /api/interviews/{interview_id}/status**
```bash
curl "http://localhost:8000/api/interviews/interview-uuid/status"
```

## 🔄 Complete Workflow

### 1. Candidate Creation
```python
import requests

# Create candidate with comprehensive data
candidate_data = {
    "name": "Sarah Chen",
    "email": "sarah.chen@demo.com",
    "position": "Senior Full Stack Developer",
    "experience_years": 6.0,
    "skills": json.dumps([
        {"name": "Python", "level": "expert", "years_experience": 6.0},
        {"name": "React", "level": "advanced", "years_experience": 4.0}
    ])
}

response = requests.post("http://localhost:8000/api/candidates/", data=candidate_data)
candidate_id = response.json()["candidate_id"]
```

### 2. Wait for AI Analysis
```python
import time

# Wait for AI analysis to complete
while True:
    response = requests.get(f"http://localhost:8000/api/candidates/{candidate_id}/analysis")
    analysis = response.json()
    
    if analysis["status"] == "completed":
        print(f"Analysis completed! Score: {analysis['overall_score']}/100")
        break
    
    time.sleep(5)  # Check every 5 seconds
```

### 3. Schedule Interview
```python
from datetime import datetime, timedelta

# Schedule interview for next week
interview_time = datetime.now() + timedelta(days=7)
interview_time = interview_time.replace(hour=14, minute=0, second=0, microsecond=0)

interview_request = {
    "candidate_id": candidate_id,
    "preferred_time": interview_time.isoformat(),
    "duration_minutes": 90,
    "interview_type": "technical",
    "interview_round": 1,
    "is_remote": True,
    "notes": "Technical interview for Senior Developer position"
}

response = requests.post(
    "http://localhost:8000/api/schedule-interview/",
    json=interview_request
)

interview_result = response.json()
print(f"Interview scheduled with {interview_result['interview']['interviewer_name']}")
print(f"Google Meet: {interview_result['interview']['google_meet_link']}")
```

## 🧪 Demo and Testing

### Run the Complete Demo

```bash
# Start the API server (in one terminal)
python candidate_management_api.py

# Run the comprehensive demo (in another terminal)
python interview_scheduling_demo.py
```

### Demo Features

The demo script demonstrates:

1. **API Health Check**: Verifies the system is running
2. **Candidate Creation**: Creates 3 realistic test candidates
3. **AI Analysis**: Waits for AI analysis completion
4. **Interview Scheduling**: Schedules interviews with AI matching
5. **Calendar Integration**: Shows Google Calendar event creation
6. **Status Monitoring**: Tracks interview and calendar status
7. **Results Summary**: Displays comprehensive results

### Expected Demo Output

```
🚀 Interview Scheduling System Demo
============================================================

🔍 Step 1: Checking API Health
----------------------------------------
   ✅ API is running and accessible
   📖 Documentation: http://localhost:8000/docs

📝 Step 2: Creating Test Candidates
----------------------------------------
   ✅ Created: Sarah Chen (ID: a1b2c3d4...)
   ✅ Created: Michael Rodriguez (ID: e5f6g7h8...)
   ✅ Created: Emily Johnson (ID: i9j0k1l2...)

🤖 Step 3: Waiting for AI Analysis Completion
----------------------------------------
   ✅ Sarah Chen: Analysis completed (Score: 87/100)
   ✅ Michael Rodriguez: Analysis completed (Score: 82/100)
   ✅ Emily Johnson: Analysis completed (Score: 79/100)

🗓️ Step 4: Scheduling Interviews
----------------------------------------
   🔄 Scheduling interview for Sarah Chen...
      Position: Senior Full Stack Developer
      Time: Friday, August 15 at 02:00 PM
      Type: Technical
      ✅ Interview scheduled successfully!
      👨‍💼 Interviewer: John Smith
      📊 AI Match Score: 92.5/100
      🎯 Confidence: 0.85

📊 Step 5: Monitoring Interview Status
----------------------------------------
   ✅ Sarah Chen: Calendar event created
      🎥 Google Meet link generated
      📧 Email invitations sent

📋 Step 6: Final Results Summary
============================================================

👥 CANDIDATES CREATED:
   ✅ Analyzed Sarah Chen (Senior Full Stack Developer)
   ✅ Analyzed Michael Rodriguez (DevOps Engineer)
   ✅ Analyzed Emily Johnson (Frontend Developer)

🗓️ INTERVIEWS SCHEDULED:
   📅 Calendar Created
      👤 Candidate: Sarah Chen
      👨‍💼 Interviewer: John Smith
      📊 Match Score: 92.5/100
      🕒 Time: 08/15 02:00 PM
      🎯 Type: Technical
      🎥 Google Meet: Ready
```

## 🏗️ Architecture

### System Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Candidate     │    │   AI Analysis   │    │   Interview     │
│   Management    │───▶│   Service       │───▶│   Scheduling    │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Database      │    │   Background    │    │   Google        │
│   PostgreSQL    │    │   Tasks         │    │   Calendar      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Database Schema

**Candidates Table:**
- Personal information (name, email, phone, location)
- Skills and experience data
- AI analysis results and scores
- Application status and timestamps

**Interviews Table:**
- Interview scheduling information
- Participant details (candidate, interviewer)
- AI matching scores and confidence levels
- Calendar integration data (event ID, Google Meet link)
- Interview status and feedback

**Analysis Tasks Table:**
- Background task tracking
- Task status and error handling
- Execution timing and results

### AI Integration Flow

```
1. Candidate Created
   ↓
2. Background AI Analysis Triggered
   ↓
3. OpenRouter API Call (Claude-3-Haiku)
   ↓
4. Analysis Results Stored
   ↓
5. Interviewer Matching Algorithm
   ↓
6. Interview Scheduling Ready
```

### Calendar Integration Flow

```
1. Interview Scheduled
   ↓
2. Google Calendar Authentication
   ↓
3. Calendar Event Creation
   ↓
4. Google Meet Link Generation
   ↓
5. Email Invitations Sent
   ↓
6. Automatic Reminders Set
```

## 🔧 Configuration Options

### Environment Variables

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost/interview_db
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# AI Service Configuration
OPENROUTER_API_KEY=your-api-key
AI_MODEL=anthropic/claude-3-haiku
AI_MAX_TOKENS=4000
AI_TEMPERATURE=0.1

# Google Calendar Configuration
GOOGLE_CREDENTIALS_FILE=credentials.json
GOOGLE_TOKEN_DIR=tokens
GOOGLE_SCOPES=calendar,calendar.events

# Background Tasks Configuration
MAX_CONCURRENT_TASKS=10
TASK_TIMEOUT_MINUTES=10
RETRY_ATTEMPTS=3
RETRY_DELAY_SECONDS=5

# Application Configuration
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=["http://localhost:3000"]

# File Upload Configuration
MAX_FILE_SIZE_MB=10
ALLOWED_FILE_TYPES=pdf,doc,docx,txt
UPLOAD_DIRECTORY=uploads/resumes
```

### Interview Types

The system supports multiple interview types:

- **technical**: Technical skills assessment
- **hr**: HR and behavioral interview
- **cultural**: Cultural fit assessment
- **final**: Final round interview
- **phone_screen**: Initial phone screening
- **coding**: Live coding session
- **system_design**: System design interview

### Interviewer Matching Algorithm

The AI-powered matching considers:

1. **Technical Skills Match**: Alignment between candidate skills and interviewer expertise
2. **Experience Level**: Matching experience levels appropriately
3. **Interview Type**: Specialized interviewers for different interview types
4. **Calendar Availability**: Real-time calendar checking
5. **Previous Performance**: Historical interviewer effectiveness
6. **Company Preferences**: Custom matching rules and preferences

## 📊 Monitoring and Analytics

### Health Checks

```bash
# Check API health
curl http://localhost:8000/health

# Check database connectivity
curl http://localhost:8000/health/database

# Check AI service status
curl http://localhost:8000/health/ai-service

# Check background tasks
curl http://localhost:8000/health/background-tasks
```

### Metrics and Analytics

The system provides comprehensive metrics:

- **Candidate Metrics**: Application rates, analysis completion times
- **Interview Metrics**: Scheduling success rates, calendar event creation
- **AI Performance**: Analysis accuracy, matching effectiveness
- **System Performance**: API response times, background task processing

### Logging

Comprehensive logging is implemented:

```python
# Application logs
logger.info("Candidate created successfully")
logger.warning("AI analysis taking longer than expected")
logger.error("Calendar event creation failed")

# Performance logs
logger.info(f"AI analysis completed in {duration:.2f} seconds")
logger.info(f"Interview scheduled with match score {score:.1f}")

# Security logs  
logger.info(f"OAuth authentication successful for {user_email}")
logger.warning(f"Invalid file upload attempt: {filename}")
```

## 🚀 Production Deployment

### Docker Configuration

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "candidate_management_api.py"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/interview_db
    depends_on:
      - db
      - redis

  db:
    image: postgres:14
    environment:
      - POSTGRES_DB=interview_db
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7
    
volumes:
  postgres_data:
```

### Kubernetes Deployment

**deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: interview-scheduling-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: interview-scheduling-api
  template:
    metadata:
      labels:
        app: interview-scheduling-api
    spec:
      containers:
      - name: api
        image: interview-scheduling:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: database-url
```

### Load Balancing and Scaling

- **Horizontal Scaling**: Multiple API instances behind load balancer
- **Database Scaling**: Read replicas for improved performance
- **Background Tasks**: Dedicated worker nodes for task processing
- **Caching**: Redis for caching AI analysis results and interviewer data

### Security Considerations

1. **Authentication**: OAuth2 for Google Calendar integration
2. **Authorization**: Role-based access control for API endpoints
3. **Data Encryption**: TLS/SSL for data in transit, encryption for sensitive data
4. **Input Validation**: Comprehensive validation for all user inputs
5. **File Security**: Virus scanning and type validation for uploads
6. **Rate Limiting**: API rate limiting to prevent abuse

## 🤝 Contributing

### Development Setup

```bash
# Clone repository
git clone <repository-url>
cd interview-scheduling-system

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Run linting
flake8 .
black .
mypy .
```

### Testing

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/api/

# Run with coverage
pytest --cov=. --cov-report=html
```

### Code Quality

- **Linting**: Black, Flake8, isort
- **Type Checking**: MyPy for static type analysis
- **Testing**: Pytest with comprehensive test coverage
- **Documentation**: Docstrings and API documentation

## 📞 Support

### Troubleshooting

**Common Issues:**

1. **API Not Starting**:
   ```bash
   # Check if port 8000 is in use
   lsof -i :8000
   
   # Check database connection
   psql -h localhost -U user -d interview_db
   ```

2. **AI Analysis Failing**:
   ```bash
   # Check API key
   echo $OPENROUTER_API_KEY
   
   # Test API connection
   curl -H "Authorization: Bearer $OPENROUTER_API_KEY" \
        https://openrouter.ai/api/v1/models
   ```

3. **Google Calendar Issues**:
   ```bash
   # Check credentials file
   ls -la credentials.json
   
   # Verify OAuth scopes
   cat credentials.json | jq '.web.redirect_uris'
   ```

### Getting Help

- **Documentation**: Comprehensive API docs at `/docs`
- **Logs**: Check application logs for detailed error information
- **GitHub Issues**: Report bugs and feature requests
- **Community**: Join our developer community for support

---

*This interview scheduling system provides a complete solution for modern technical hiring, combining AI intelligence with seamless calendar integration for an optimal interview experience.*
