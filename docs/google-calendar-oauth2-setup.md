# Google Calendar OAuth2 Setup Guide

This guide provides comprehensive instructions for setting up OAuth2 authentication for Google Calendar API integration in your interview scheduling system.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Google Cloud Console Setup](#google-cloud-console-setup)
3. [OAuth2 Configuration](#oauth2-configuration)
4. [Environment Setup](#environment-setup)
5. [Testing Authentication](#testing-authentication)
6. [Troubleshooting](#troubleshooting)
7. [Production Deployment](#production-deployment)

## Prerequisites

### Required Python Packages

Install the required packages using the setup script:

```bash
python oauth2_setup.py --install
```

Or manually install:

```bash
pip install google-auth>=2.0.0
pip install google-auth-oauthlib>=1.0.0
pip install google-auth-httplib2>=0.1.0
pip install google-api-python-client>=2.0.0
pip install pytz>=2021.1
```

### Python Version

- Python 3.7 or higher is required
- Recommended: Python 3.8+

## Google Cloud Console Setup

### 1. Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Enter project name: `interview-scheduling-system`
4. Click "Create"

### 2. Enable Google Calendar API

1. In the Google Cloud Console, go to "APIs & Services" → "Library"
2. Search for "Google Calendar API"
3. Click on it and click "Enable"
4. Wait for the API to be enabled

### 3. Configure OAuth Consent Screen

1. Go to "APIs & Services" → "OAuth consent screen"
2. Choose "External" (for testing) or "Internal" (for organization use)
3. Fill in the required information:
   - **App name**: Interview Scheduling System
   - **User support email**: Your email
   - **Developer contact email**: Your email
4. Add scopes:
   - `https://www.googleapis.com/auth/calendar`
   - `https://www.googleapis.com/auth/calendar.events`
   - `https://www.googleapis.com/auth/calendar.readonly`
5. Add test users (for development):
   - Add your email and any other test users
6. Save and continue

### 4. Create OAuth2 Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. Choose "Desktop application" (for development) or "Web application" (for production)
4. Name: `Interview Scheduling OAuth Client`
5. For web application, add authorized redirect URIs:
   - `http://localhost:8080`
   - `http://localhost:8000`
   - `http://127.0.0.1:8080`
   - `http://127.0.0.1:8000`
6. Click "Create"
7. Download the JSON file and save it as `credentials.json` in your project directory

## OAuth2 Configuration

### 1. Environment Variables (Optional)

Create a `.env` file in your project directory:

```env
# Google Calendar OAuth2 Configuration
GOOGLE_CREDENTIALS_FILE=credentials.json
GOOGLE_TOKEN_DIR=tokens
ENVIRONMENT=development

# Application Settings
API_HOST=localhost
API_PORT=8000
```

### 2. Verify Setup

Run the environment check:

```bash
python oauth2_setup.py --report
```

This will generate a comprehensive report showing:
- Environment status
- Package installations
- Configuration details
- Token information

## Environment Setup

### 1. Project Structure

Ensure your project has this structure:

```
interview-scheduling-system/
├── credentials.json          # OAuth2 credentials from Google Cloud
├── oauth2_config.py         # OAuth2 configuration management
├── oauth2_setup.py          # Setup and management utilities
├── google_calendar_service.py  # Enhanced calendar service
├── tokens/                  # Directory for user tokens (auto-created)
│   ├── .gitignore          # Prevents tokens from being committed
│   └── token_*.json        # User-specific token files
├── api.py                  # Your FastAPI application
└── requirements.txt        # Python dependencies
```

### 2. Setup Token Directory

The token directory will be created automatically, but you can set it up manually:

```bash
python oauth2_setup.py --list-tokens
```

### 3. Verify Credentials File

```bash
python oauth2_setup.py
```

This will check if your credentials file is valid and properly formatted.

## Testing Authentication

### 1. Test OAuth Flow

Test the authentication flow for a specific user:

```bash
python oauth2_setup.py --test your-email@gmail.com
```

This will:
1. Start the OAuth2 flow
2. Open your browser for consent
3. Save the token for future use
4. Test a basic Calendar API call

### 2. Manual Testing

You can also test directly in Python:

```python
from google_calendar_service import GoogleCalendarService

# Initialize service
calendar_service = GoogleCalendarService()

# Authenticate (will open browser for consent)
success = calendar_service.authenticate("your-email@gmail.com")

if success:
    print("✅ Authentication successful!")
    
    # Get user info
    user_info = calendar_service.get_user_info()
    print(f"User: {user_info['email']}")
    print(f"Calendar: {user_info['calendar_summary']}")
    
    # Test availability check
    from datetime import datetime, timedelta
    
    start_date = datetime.now()
    end_date = start_date + timedelta(days=1)
    
    availability = calendar_service.get_availability(
        user_info['email'], start_date, end_date
    )
    
    print(f"Busy periods: {len(availability['busy'])}")
else:
    print("❌ Authentication failed!")
```

### 3. Token Management

List stored tokens:

```bash
python oauth2_setup.py --list-tokens
```

Clean up expired tokens:

```bash
python oauth2_setup.py --cleanup
```

## Advanced OAuth2 Features

### 1. User-Specific Token Storage

The enhanced OAuth2 implementation stores tokens per user:

```python
# Each user gets their own token file
tokens/
├── token_a1b2c3d4e5f6.json  # User 1 tokens (hashed email)
├── token_f6e5d4c3b2a1.json  # User 2 tokens (hashed email)
└── .gitignore
```

### 2. Automatic Token Refresh

Tokens are automatically refreshed when they expire:

```python
# The service handles refresh automatically
calendar_service = GoogleCalendarService()
success = calendar_service.authenticate("user@email.com")

# If token is expired but refresh token exists, it will refresh automatically
if calendar_service.is_authenticated("user@email.com"):
    print("Token is valid (refreshed if needed)")
```

### 3. Credential Validation

The system validates credentials before use:

```python
from oauth2_config import OAuth2Config

config = OAuth2Config()
valid, message = config.validate_credentials_file()

if not valid:
    print(f"Credentials issue: {message}")
```

## Integration with FastAPI

### 1. Authentication Endpoint

Add OAuth2 endpoints to your FastAPI application:

```python
from fastapi import FastAPI, HTTPException
from google_calendar_service import GoogleCalendarService

app = FastAPI()
calendar_service = GoogleCalendarService()

@app.post("/api/auth/google")
async def authenticate_google(user_email: str):
    """Initiate Google Calendar authentication"""
    try:
        success = calendar_service.authenticate(user_email)
        
        if success:
            user_info = calendar_service.get_user_info()
            return {
                "success": True,
                "user_info": user_info,
                "message": "Authentication successful"
            }
        else:
            raise HTTPException(
                status_code=400,
                detail="Authentication failed"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Authentication error: {str(e)}"
        )

@app.get("/api/auth/status/{user_email}")
async def check_auth_status(user_email: str):
    """Check if user is authenticated"""
    is_authenticated = calendar_service.is_authenticated(user_email)
    
    return {
        "authenticated": is_authenticated,
        "user_email": user_email
    }

@app.delete("/api/auth/revoke/{user_email}")
async def revoke_auth(user_email: str):
    """Revoke user authentication"""
    success = calendar_service.revoke_credentials(user_email)
    
    return {
        "success": success,
        "message": "Credentials revoked" if success else "Failed to revoke"
    }
```

### 2. Middleware for Authentication

Add middleware to check authentication:

```python
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

class CalendarAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, calendar_service):
        super().__init__(app)
        self.calendar_service = calendar_service
    
    async def dispatch(self, request: Request, call_next):
        # Check if calendar endpoints require authentication
        if request.url.path.startswith("/api/calendar/"):
            user_email = request.headers.get("X-User-Email")
            
            if not user_email:
                raise HTTPException(401, "User email required")
            
            if not self.calendar_service.is_authenticated(user_email):
                raise HTTPException(401, "Calendar authentication required")
        
        response = await call_next(request)
        return response

# Add to your FastAPI app
app.add_middleware(CalendarAuthMiddleware, calendar_service=calendar_service)
```

## Troubleshooting

### Common Issues

1. **"Credentials file not found"**
   - Ensure `credentials.json` is in the project directory
   - Check the `GOOGLE_CREDENTIALS_FILE` environment variable

2. **"Invalid credentials file format"**
   - Re-download credentials from Google Cloud Console
   - Ensure the file is valid JSON

3. **"Permission denied" error**
   - Check OAuth consent screen configuration
   - Ensure required scopes are configured
   - Add test users if using external consent screen

4. **"Token has expired"**
   - Run `python oauth2_setup.py --cleanup` to remove expired tokens
   - Re-authenticate with `python oauth2_setup.py --test <email>`

5. **"Refresh token missing"**
   - This happens if consent was not given properly
   - Delete the token file and re-authenticate
   - Ensure `prompt=consent` is used in OAuth flow

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Test with verbose output
calendar_service = GoogleCalendarService()
success = calendar_service.authenticate("user@email.com")
```

### Validation Tools

Use the built-in validation tools:

```bash
# Check environment
python oauth2_setup.py

# Generate detailed report
python oauth2_setup.py --report

# Validate specific token
python -c "
from oauth2_setup import OAuth2SetupManager
manager = OAuth2SetupManager()
tokens = manager.list_stored_tokens()
print(tokens)
"
```

## Production Deployment

### 1. Environment Configuration

For production, update your configuration:

```python
# oauth2_config.py - Production settings
PRODUCTION_CONFIG = {
    "auth_mode": "web",  # Use web flow instead of local server
    "auto_open_browser": False,
    "prompt_consent": False,
    "secure_storage": True,
    "redirect_uri": "https://your-domain.com/auth/callback"
}
```

### 2. Web-based OAuth Flow

For web applications, implement the web OAuth flow:

```python
from google_auth_oauthlib.flow import Flow

def create_auth_url(user_email: str) -> str:
    """Create authorization URL for web OAuth flow"""
    flow = Flow.from_client_secrets_file(
        'credentials.json',
        scopes=SCOPES,
        redirect_uri='https://your-domain.com/auth/callback'
    )
    
    auth_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        login_hint=user_email,
        prompt='consent'
    )
    
    # Store state for validation
    return auth_url

def handle_callback(authorization_code: str, state: str) -> bool:
    """Handle OAuth callback"""
    flow = Flow.from_client_secrets_file(
        'credentials.json',
        scopes=SCOPES,
        redirect_uri='https://your-domain.com/auth/callback'
    )
    
    flow.fetch_token(code=authorization_code)
    credentials = flow.credentials
    
    # Save credentials for user
    return save_user_credentials(credentials, user_email)
```

### 3. Security Considerations

1. **Secure Token Storage**
   - Use encrypted storage for production
   - Implement proper access controls
   - Regular token rotation

2. **Environment Variables**
   - Use environment variables for sensitive configuration
   - Never commit credentials to version control

3. **HTTPS**
   - Always use HTTPS in production
   - Update redirect URIs to use HTTPS

4. **Rate Limiting**
   - Implement rate limiting for OAuth endpoints
   - Monitor API usage and quotas

### 4. Monitoring and Logging

Set up proper monitoring:

```python
import logging
from datetime import datetime

# Configure production logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('oauth2.log'),
        logging.StreamHandler()
    ]
)

# Log OAuth events
def log_oauth_event(event: str, user_email: str, success: bool):
    logger.info(f"OAuth Event: {event} - User: {user_email} - Success: {success}")
```

## Example Usage in Interview Scheduling

Here's how to integrate OAuth2 with your interview scheduling system:

```python
from google_calendar_service import GoogleCalendarService
from datetime import datetime, timedelta

# Initialize calendar service
calendar_service = GoogleCalendarService()

async def schedule_interview(interview_data: dict):
    """Schedule interview with Google Calendar integration"""
    
    # Get interviewer and candidate emails
    interviewer_email = interview_data['interviewer_email']
    candidate_email = interview_data['candidate_email']
    
    # Ensure interviewer is authenticated
    if not calendar_service.is_authenticated(interviewer_email):
        auth_success = calendar_service.authenticate(interviewer_email)
        if not auth_success:
            raise Exception("Interviewer calendar authentication required")
    
    # Check availability
    start_time = interview_data['scheduled_time']
    end_time = start_time + timedelta(minutes=interview_data['duration'])
    
    availability = calendar_service.get_availability(
        interviewer_email, start_time, end_time
    )
    
    if availability['busy']:
        raise Exception("Interviewer is not available at the requested time")
    
    # Create calendar event
    event_id = calendar_service.create_interview_event(
        interview_data=interview_data,
        candidate_email=candidate_email,
        interviewer_email=interviewer_email
    )
    
    if event_id:
        # Update interview record with event ID
        interview_data['google_event_id'] = event_id
        return event_id
    else:
        raise Exception("Failed to create calendar event")
```

## Support and Resources

- **Google Calendar API Documentation**: [https://developers.google.com/calendar](https://developers.google.com/calendar)
- **OAuth2 Documentation**: [https://developers.google.com/identity/protocols/oauth2](https://developers.google.com/identity/protocols/oauth2)
- **Google Cloud Console**: [https://console.cloud.google.com/](https://console.cloud.google.com/)

For additional help, check the logs in `oauth2_setup.log` or run the diagnostic report:

```bash
python oauth2_setup.py --report > oauth2_diagnostic.txt
```
