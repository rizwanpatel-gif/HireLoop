"""
Google Calendar Configuration and Setup
"""
import os
from typing import Dict, Any

# Google Calendar API Configuration
GOOGLE_CALENDAR_CONFIG = {
    # OAuth2 Settings
    'oauth': {
        'scopes': [
            'https://www.googleapis.com/auth/calendar',
            'https://www.googleapis.com/auth/calendar.events'
        ],
        'redirect_uri': 'http://localhost:8080/oauth2callback',
        'access_type': 'offline',
        'prompt': 'consent'
    },
    
    # Calendar Settings
    'calendar': {
        'timezone': 'Asia/Kolkata',
        'working_hours': {
            'start': 9,   # 9 AM
            'end': 18,    # 6 PM
        },
        'working_days': [0, 1, 2, 3, 4],  # Monday to Friday
        'default_duration': 60,  # minutes
        'buffer_time': 15,       # minutes between meetings
    },
    
    # Event Settings
    'event': {
        'reminders': [
            {'method': 'email', 'minutes': 24 * 60},  # 1 day before
            {'method': 'popup', 'minutes': 30},       # 30 minutes before
        ],
        'conference_solution': 'hangoutsMeet',  # Google Meet integration
        'guest_permissions': {
            'can_modify': False,
            'can_invite_others': False,
            'can_see_other_guests': True
        },
        'visibility': 'private',
        'transparency': 'opaque'  # Show as busy
    }
}

# Environment variables for Google Calendar
REQUIRED_ENV_VARS = [
    'GOOGLE_CREDENTIALS_FILE',  # Path to credentials.json
    'GOOGLE_TOKEN_FILE',        # Path to store tokens
]

OPTIONAL_ENV_VARS = [
    'GOOGLE_CALENDAR_ID',       # Specific calendar ID (default: 'primary')
    'GOOGLE_ADMIN_EMAIL',       # Admin email for service account
    'GOOGLE_TIMEZONE',          # Override default timezone
]

def get_google_credentials_path() -> str:
    """Get the path to Google credentials file"""
    return os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')

def get_google_token_path() -> str:
    """Get the path to Google token file"""
    return os.getenv('GOOGLE_TOKEN_FILE', 'token.json')

def get_calendar_timezone() -> str:
    """Get the configured timezone"""
    return os.getenv('GOOGLE_TIMEZONE', GOOGLE_CALENDAR_CONFIG['calendar']['timezone'])

def validate_google_calendar_config() -> Dict[str, Any]:
    """
    Validate Google Calendar configuration
    
    Returns:
        Dict containing validation results
    """
    validation_result = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'config': {}
    }
    
    # Check for credentials file
    credentials_path = get_google_credentials_path()
    if not os.path.exists(credentials_path):
        validation_result['valid'] = False
        validation_result['errors'].append(
            f"Google credentials file not found: {credentials_path}"
        )
    else:
        validation_result['config']['credentials_file'] = credentials_path
    
    # Check token file path (create directory if needed)
    token_path = get_google_token_path()
    token_dir = os.path.dirname(token_path)
    if token_dir and not os.path.exists(token_dir):
        try:
            os.makedirs(token_dir, exist_ok=True)
            validation_result['warnings'].append(
                f"Created directory for token file: {token_dir}"
            )
        except Exception as e:
            validation_result['errors'].append(
                f"Cannot create token directory {token_dir}: {e}"
            )
    
    validation_result['config']['token_file'] = token_path
    validation_result['config']['timezone'] = get_calendar_timezone()
    
    # Check environment variables
    missing_env_vars = []
    for var in REQUIRED_ENV_VARS:
        if not os.getenv(var):
            missing_env_vars.append(var)
    
    if missing_env_vars:
        validation_result['warnings'].append(
            f"Missing optional environment variables: {missing_env_vars}"
        )
    
    return validation_result

# Google Calendar API quotas and limits
API_LIMITS = {
    'requests_per_day': 1000000,
    'requests_per_100_seconds': 100,
    'requests_per_100_seconds_per_user': 50,
    'events_per_request': 2500,
    'calendar_list_max_results': 250,
    'events_list_max_results': 2500
}

# Error codes and their meanings
GOOGLE_API_ERROR_CODES = {
    400: "Bad Request - Invalid request format",
    401: "Unauthorized - Invalid credentials",
    403: "Forbidden - Insufficient permissions or quota exceeded",
    404: "Not Found - Calendar or event not found",
    409: "Conflict - Resource conflict (e.g., duplicate event)",
    429: "Too Many Requests - Rate limit exceeded",
    500: "Internal Server Error - Google server error",
    503: "Service Unavailable - Google service temporarily unavailable"
}

def get_error_message(status_code: int) -> str:
    """Get human-readable error message for Google API error codes"""
    return GOOGLE_API_ERROR_CODES.get(status_code, f"Unknown error (HTTP {status_code})")

# Sample credentials.json structure for documentation
SAMPLE_CREDENTIALS_STRUCTURE = {
    "installed": {
        "client_id": "your-client-id.googleusercontent.com",
        "project_id": "your-project-id",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": "your-client-secret",
        "redirect_uris": ["http://localhost"]
    }
}
