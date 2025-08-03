"""
OAuth2 Configuration and Helper Functions for Google Calendar Integration
Handles different authentication scenarios and environment configurations
"""
import os
import json
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class OAuth2Config:
    """
    OAuth2 configuration manager for Google Calendar API
    """
    
    # Google Calendar API OAuth2 scopes
    CALENDAR_SCOPES = [
        'https://www.googleapis.com/auth/calendar',           # Full calendar access
        'https://www.googleapis.com/auth/calendar.events',    # Event management
        'https://www.googleapis.com/auth/calendar.readonly'   # Read-only access
    ]
    
    # Additional scopes for user information
    USER_INFO_SCOPES = [
        'https://www.googleapis.com/auth/userinfo.email',     # User email
        'https://www.googleapis.com/auth/userinfo.profile'    # User profile
    ]
    
    # Combined scopes for comprehensive access
    ALL_SCOPES = CALENDAR_SCOPES + USER_INFO_SCOPES
    
    def __init__(self, config_file: str = "oauth2_config.json"):
        """
        Initialize OAuth2 configuration
        
        Args:
            config_file: Path to configuration file
        """
        self.config_file = Path(config_file)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """
        Load OAuth2 configuration from file or environment
        
        Returns:
            Configuration dictionary
        """
        default_config = {
            "credentials_file": os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json"),
            "token_directory": os.getenv("GOOGLE_TOKEN_DIR", "tokens"),
            "redirect_uris": [
                "http://localhost:8080",
                "http://localhost:8000", 
                "http://127.0.0.1:8080",
                "http://127.0.0.1:8000"
            ],
            "scopes": self.CALENDAR_SCOPES,
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "project_settings": {
                "timeout_seconds": 300,
                "max_retry_attempts": 3,
                "auto_refresh": True,
                "store_refresh_token": True
            }
        }
        
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    file_config = json.load(f)
                default_config.update(file_config)
                logger.info(f"Loaded OAuth2 config from {self.config_file}")
            else:
                logger.info("Using default OAuth2 configuration")
                
        except Exception as e:
            logger.warning(f"Error loading config file: {e}, using defaults")
        
        return default_config
    
    def save_config(self) -> bool:
        """
        Save current configuration to file
        
        Returns:
            bool: True if saved successfully
        """
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            logger.info(f"Saved OAuth2 config to {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            return False
    
    def get_credentials_file(self) -> str:
        """Get path to credentials file"""
        return self.config["credentials_file"]
    
    def get_token_directory(self) -> str:
        """Get token storage directory"""
        return self.config["token_directory"]
    
    def get_scopes(self, include_user_info: bool = False) -> List[str]:
        """
        Get OAuth2 scopes
        
        Args:
            include_user_info: Include user info scopes
            
        Returns:
            List of scope URLs
        """
        scopes = self.config.get("scopes", self.CALENDAR_SCOPES)
        
        if include_user_info:
            scopes = list(set(scopes + self.USER_INFO_SCOPES))
        
        return scopes
    
    def get_redirect_uris(self) -> List[str]:
        """Get allowed redirect URIs"""
        return self.config.get("redirect_uris", [])
    
    def validate_credentials_file(self) -> Tuple[bool, str]:
        """
        Validate the credentials file exists and is properly formatted
        
        Returns:
            Tuple of (is_valid, message)
        """
        try:
            creds_file = Path(self.get_credentials_file())
            
            if not creds_file.exists():
                return False, f"Credentials file not found: {creds_file}"
            
            with open(creds_file, 'r') as f:
                creds_data = json.load(f)
            
            # Check for required fields
            required_fields = ["client_id", "client_secret", "auth_uri", "token_uri"]
            
            if "web" in creds_data:
                client_data = creds_data["web"]
            elif "installed" in creds_data:
                client_data = creds_data["installed"]
            else:
                return False, "Invalid credentials file format - missing 'web' or 'installed' section"
            
            missing_fields = [field for field in required_fields if field not in client_data]
            
            if missing_fields:
                return False, f"Missing required fields in credentials: {missing_fields}"
            
            return True, "Credentials file is valid"
            
        except json.JSONDecodeError:
            return False, "Credentials file contains invalid JSON"
        except Exception as e:
            return False, f"Error validating credentials file: {e}"
    
    def setup_token_directory(self) -> bool:
        """
        Create token directory if it doesn't exist
        
        Returns:
            bool: True if directory exists or was created
        """
        try:
            token_dir = Path(self.get_token_directory())
            token_dir.mkdir(exist_ok=True, parents=True)
            
            # Create .gitignore to prevent token files from being committed
            gitignore_path = token_dir / ".gitignore"
            if not gitignore_path.exists():
                with open(gitignore_path, 'w') as f:
                    f.write("# Ignore all token files\n*.json\n*.pickle\n")
            
            logger.info(f"Token directory ready: {token_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting up token directory: {e}")
            return False
    
    def get_oauth_urls(self) -> Dict[str, str]:
        """
        Get OAuth2 URLs from configuration
        
        Returns:
            Dictionary with auth and token URLs
        """
        return {
            "auth_uri": self.config.get("auth_uri", "https://accounts.google.com/o/oauth2/auth"),
            "token_uri": self.config.get("token_uri", "https://oauth2.googleapis.com/token"),
            "revoke_uri": "https://oauth2.googleapis.com/revoke"
        }


class OAuth2Validator:
    """
    Validation utilities for OAuth2 flow
    """
    
    @staticmethod
    def validate_token_data(token_data: Dict) -> Tuple[bool, List[str]]:
        """
        Validate token data structure
        
        Args:
            token_data: Token data dictionary
            
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        required_fields = ["token", "refresh_token", "token_uri", "client_id", "client_secret"]
        
        for field in required_fields:
            if field not in token_data:
                issues.append(f"Missing required field: {field}")
        
        # Check token expiry
        if "expiry" in token_data:
            try:
                expiry = datetime.fromisoformat(token_data["expiry"].replace("Z", "+00:00"))
                if expiry < datetime.now().astimezone():
                    issues.append("Token has expired")
            except Exception:
                issues.append("Invalid expiry date format")
        
        # Check scopes
        if "scopes" in token_data:
            if not isinstance(token_data["scopes"], list):
                issues.append("Scopes should be a list")
        
        return len(issues) == 0, issues
    
    @staticmethod
    def validate_scopes(requested_scopes: List[str], granted_scopes: List[str]) -> Tuple[bool, List[str]]:
        """
        Validate that granted scopes cover requested scopes
        
        Args:
            requested_scopes: Scopes that were requested
            granted_scopes: Scopes that were granted
            
        Returns:
            Tuple of (all_granted, missing_scopes)
        """
        missing_scopes = [scope for scope in requested_scopes if scope not in granted_scopes]
        return len(missing_scopes) == 0, missing_scopes
    
    @staticmethod
    def estimate_token_validity(token_data: Dict) -> Optional[timedelta]:
        """
        Estimate how long a token will remain valid
        
        Args:
            token_data: Token data dictionary
            
        Returns:
            Time remaining until expiry or None if cannot determine
        """
        try:
            if "expiry" not in token_data:
                return None
            
            expiry = datetime.fromisoformat(token_data["expiry"].replace("Z", "+00:00"))
            now = datetime.now().astimezone()
            
            if expiry > now:
                return expiry - now
            else:
                return timedelta(0)  # Already expired
                
        except Exception:
            return None


# Environment-specific configurations
DEVELOPMENT_CONFIG = {
    "auth_mode": "local_server",
    "port_range": [8080, 8081, 8082, 8000, 8001],
    "auto_open_browser": True,
    "prompt_consent": True
}

PRODUCTION_CONFIG = {
    "auth_mode": "console",
    "auto_open_browser": False,
    "prompt_consent": False,
    "secure_storage": True
}

TESTING_CONFIG = {
    "auth_mode": "mock",
    "use_service_account": False,
    "mock_user_email": "test@example.com"
}

def get_environment_config(env: str = None) -> Dict:
    """
    Get configuration for specific environment
    
    Args:
        env: Environment name (development, production, testing)
        
    Returns:
        Environment-specific configuration
    """
    env = env or os.getenv("ENVIRONMENT", "development").lower()
    
    configs = {
        "development": DEVELOPMENT_CONFIG,
        "production": PRODUCTION_CONFIG,
        "testing": TESTING_CONFIG
    }
    
    return configs.get(env, DEVELOPMENT_CONFIG)

# Example usage and setup validation
if __name__ == "__main__":
    # Initialize OAuth2 config
    config = OAuth2Config()
    
    # Validate setup
    print("OAuth2 Configuration Validation")
    print("=" * 40)
    
    # Check credentials file
    valid, message = config.validate_credentials_file()
    print(f"Credentials file: {'✅' if valid else '❌'} {message}")
    
    # Setup token directory
    token_setup = config.setup_token_directory()
    print(f"Token directory: {'✅' if token_setup else '❌'} Setup")
    
    # Show configuration
    print(f"\nCredentials file: {config.get_credentials_file()}")
    print(f"Token directory: {config.get_token_directory()}")
    print(f"Scopes: {len(config.get_scopes())} configured")
    print(f"Redirect URIs: {len(config.get_redirect_uris())} configured")
    
    # Environment info
    env_config = get_environment_config()
    print(f"\nEnvironment: {os.getenv('ENVIRONMENT', 'development')}")
    print(f"Auth mode: {env_config.get('auth_mode', 'unknown')}")
