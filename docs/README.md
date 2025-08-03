# RHero Interview Management System

A comprehensive interview scheduling and candidate management platform built with FastAPI, featuring AI-powered candidate analysis and smart scheduling.

## Features

- **Smart Interview Scheduling**: Automatic scheduling with availability checking
- **Calendar Integration**: Google Calendar integration for seamless scheduling
- **AI-Powered Analysis**: Intelligent candidate evaluation and matching
- **Interview Dashboard**: Comprehensive dashboard with analytics
- **OAuth2 Authentication**: Secure authentication system
- **Email Notifications**: Automated notifications for all stakeholders
- **Background Tasks**: Asynchronous task processing

## Project Structure

```
RHero/
├── backend/                    # FastAPI backend application
│   ├── app/                   # Main application package
│   │   ├── core/             # Core configuration and database
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── crud/             # Database operations
│   │   ├── services/         # Business logic services
│   │   ├── routers/          # API route handlers
│   │   └── tests/            # Test files
│   ├── scripts/              # Utility scripts
│   ├── requirements.txt      # Python dependencies
│   ├── main.py              # FastAPI application entry point
│   └── Dockerfile           # Docker configuration
├── frontend/                  # React frontend (future)
├── docs/                     # Documentation
├── scripts/                  # Project scripts
└── docker-compose.yml       # Docker Compose configuration
```

## Quick Start

### 1. Clone and Setup

```bash
cd backend
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy `.env.example` to `.env` and configure your settings:

```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

### 3. Run the Application

```bash
# Development server
python main.py

# Or with uvicorn directly
uvicorn main:app --reload
```

### 4. Access the Application

- API Documentation: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

## Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build manually
cd backend
docker build -t rhero-backend .
docker run -p 8000:8000 rhero-backend
```

## API Endpoints

### Candidates
- `GET /api/candidates/` - List all candidates
- `POST /api/candidates/` - Create new candidate
- `GET /api/candidates/{id}` - Get specific candidate
- `GET /api/availability/{interviewer_id}` - Check interviewer availability

### Interviews
- `GET /api/interviews/` - List all interviews
- `POST /api/interviews/` - Schedule new interview
- `POST /api/interviews/automatic-schedule` - Automatic scheduling
- `PUT /api/interviews/{id}/status` - Update interview status

### Dashboard
- `GET /api/dashboard/overview` - Dashboard overview
- `GET /api/dashboard/interviews` - Interview analytics
- `GET /api/dashboard/filters` - Available filters

## Configuration

### Required API Keys

1. **Google Calendar API**:
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Enable Calendar API
   - Create OAuth2 credentials
   - Add credentials to `.env`

2. **OpenAI API**:
   - Get API key from [OpenAI Dashboard](https://platform.openai.com)
   - Add to `.env` file

3. **Email Configuration**:
   - Configure SMTP settings for notifications
   - Use app passwords for Gmail

## Development

### Running Tests

```bash
cd backend
python -m pytest app/tests/
```

### Adding New Features

1. **Models**: Add to `app/models/`
2. **Schemas**: Add to `app/schemas/`
3. **Services**: Add business logic to `app/services/`
4. **Routes**: Add API endpoints to `app/routers/`
5. **Tests**: Add tests to `app/tests/`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.
