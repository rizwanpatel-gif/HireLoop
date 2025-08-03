"""
OAuth2 Setup and Credential Management for Google Calendar Integration
Provides utilities for setting up OAuth2, managing tokens, and troubleshooting authentication
"""
import os
import json
import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Import our OAuth2 configuration
from oauth2_config import OAuth2Config, OAuth2Validator, get_environment_config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('oauth2_setup.log')
    ]
)
logger = logging.getLogger(__name__)

class OAuth2SetupManager:
    """
    Comprehensive OAuth2 setup and management utility
    """
    
    def __init__(self):
        """Initialize the setup manager"""
        self.config = OAuth2Config()
        self.validator = OAuth2Validator()
    
    def check_environment(self) -> Dict[str, bool]:
        """
        Check the current environment setup for OAuth2
        
        Returns:
            Dictionary with environment check results
        """
        checks = {}
        
        # Check Python version
        checks['python_version'] = sys.version_info >= (3, 7)
        
        # Check required packages
        required_packages = [
            'google-auth',
            'google-auth-oauthlib', 
            'google-auth-httplib2',
            'google-api-python-client'
        ]
        
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
                checks[f'package_{package}'] = True
            except ImportError:
                checks[f'package_{package}'] = False
        
        # Check credentials file
        valid_creds, _ = self.config.validate_credentials_file()
        checks['credentials_file'] = valid_creds
        
        # Check token directory
        checks['token_directory'] = self.config.setup_token_directory()
        
        # Check environment variables
        checks['env_vars'] = all([
            os.getenv('GOOGLE_CREDENTIALS_FILE') or Path('credentials.json').exists(),
            True  # Token directory will be created if needed
        ])
        
        return checks
    
    def install_requirements(self) -> bool:
        """
        Install required packages for OAuth2
        
        Returns:
            bool: True if installation successful
        """
        try:
            logger.info("Installing required packages...")
            
            packages = [
                'google-auth>=2.0.0',
                'google-auth-oauthlib>=1.0.0',
                'google-auth-httplib2>=0.1.0',
                'google-api-python-client>=2.0.0',
                'pytz>=2021.1'
            ]
            
            import subprocess
            
            for package in packages:
                logger.info(f"Installing {package}...")
                result = subprocess.run([
                    sys.executable, '-m', 'pip', 'install', package
                ], capture_output=True, text=True)
                
                if result.returncode != 0:
                    logger.error(f"Failed to install {package}: {result.stderr}")
                    return False
                else:
                    logger.info(f"✅ Installed {package}")
            
            logger.info("✅ All packages installed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error installing packages: {e}")
            return False
    
    def setup_credentials_file(self, source_path: str = None) -> bool:
        """
        Set up the credentials file from Google Cloud Console
        
        Args:
            source_path: Path to downloaded credentials file
            
        Returns:
            bool: True if setup successful
        """
        try:
            target_path = Path(self.config.get_credentials_file())
            
            if source_path:
                source = Path(source_path)
                if not source.exists():
                    logger.error(f"Source credentials file not found: {source}")
                    return False
                
                # Copy and validate
                import shutil
                shutil.copy2(source, target_path)
                logger.info(f"Copied credentials from {source} to {target_path}")
            
            # Validate the credentials file
            valid, message = self.config.validate_credentials_file()
            
            if valid:
                logger.info("✅ Credentials file is valid")
                return True
            else:
                logger.error(f"❌ Credentials file validation failed: {message}")
                return False
                
        except Exception as e:
            logger.error(f"Error setting up credentials file: {e}")
            return False
    
    def list_stored_tokens(self) -> List[Dict]:
        """
        List all stored authentication tokens
        
        Returns:
            List of token information dictionaries
        """
        try:
            token_dir = Path(self.config.get_token_directory())
            
            if not token_dir.exists():
                return []
            
            tokens = []
            
            for token_file in token_dir.glob("token_*.json"):
                try:
                    with open(token_file, 'r') as f:
                        token_data = json.load(f)
                    
                    # Extract information
                    token_info = {
                        'file': token_file.name,
                        'user_email': token_data.get('user_email', 'unknown'),
                        'created_at': token_data.get('created_at', 'unknown'),
                        'last_refreshed': token_data.get('last_refreshed', 'unknown'),
                        'valid': False,
                        'expires_in': None,
                        'scopes': []
                    }
                    
                    # Validate token
                    if 'credentials' in token_data:
                        creds = token_data['credentials']
                        valid, issues = self.validator.validate_token_data(creds)
                        token_info['valid'] = valid
                        token_info['issues'] = issues
                        token_info['scopes'] = creds.get('scopes', [])
                        
                        # Check expiry
                        validity = self.validator.estimate_token_validity(creds)
                        if validity:
                            token_info['expires_in'] = str(validity)
                    
                    tokens.append(token_info)
                    
                except Exception as e:
                    logger.warning(f"Error reading token file {token_file}: {e}")
            
            return tokens
            
        except Exception as e:
            logger.error(f"Error listing tokens: {e}")
            return []
    
    def cleanup_expired_tokens(self) -> int:
        """
        Remove expired and invalid tokens
        
        Returns:
            Number of tokens removed
        """
        try:
            tokens = self.list_stored_tokens()
            removed_count = 0
            token_dir = Path(self.config.get_token_directory())
            
            for token_info in tokens:
                if not token_info['valid'] or token_info['expires_in'] == '0:00:00':
                    token_file = token_dir / token_info['file']
                    
                    try:
                        token_file.unlink()
                        logger.info(f"Removed expired token: {token_info['file']}")
                        removed_count += 1
                    except Exception as e:
                        logger.warning(f"Failed to remove {token_info['file']}: {e}")
            
            logger.info(f"✅ Cleaned up {removed_count} expired tokens")
            return removed_count
            
        except Exception as e:
            logger.error(f"Error cleaning up tokens: {e}")
            return 0
    
    def test_oauth_flow(self, user_email: str) -> bool:
        """
        Test the OAuth2 flow for a specific user
        
        Args:
            user_email: User's email address
            
        Returns:
            bool: True if test successful
        """
        try:
            logger.info(f"Testing OAuth2 flow for {user_email}")
            
            # Import and test the calendar service
            from google_calendar_service import GoogleCalendarService
            
            # Initialize service
            calendar_service = GoogleCalendarService()
            
            # Test authentication
            success = calendar_service.authenticate(user_email)
            
            if success:
                # Test basic API call
                user_info = calendar_service.get_user_info()
                
                if user_info:
                    logger.info("✅ OAuth2 flow test successful")
                    logger.info(f"   User: {user_info.get('email')}")
                    logger.info(f"   Calendar: {user_info.get('calendar_summary')}")
                    logger.info(f"   Timezone: {user_info.get('timezone')}")
                    return True
                else:
                    logger.error("❌ Failed to get user info")
                    return False
            else:
                logger.error("❌ OAuth2 authentication failed")
                return False
                
        except Exception as e:
            logger.error(f"Error testing OAuth2 flow: {e}")
            return False
    
    def generate_setup_report(self) -> str:
        """
        Generate a comprehensive setup report
        
        Returns:
            Formatted setup report string
        """
        report = []
        report.append("=" * 60)
        report.append("Google Calendar OAuth2 Setup Report")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Environment checks
        report.append("Environment Checks:")
        report.append("-" * 20)
        checks = self.check_environment()
        
        for check, result in checks.items():
            status = "✅" if result else "❌"
            report.append(f"{status} {check.replace('_', ' ').title()}")
        
        report.append("")
        
        # Configuration info
        report.append("Configuration:")
        report.append("-" * 15)
        report.append(f"Credentials file: {self.config.get_credentials_file()}")
        report.append(f"Token directory: {self.config.get_token_directory()}")
        report.append(f"Scopes configured: {len(self.config.get_scopes())}")
        
        # Scopes detail
        report.append("\nConfigured Scopes:")
        for scope in self.config.get_scopes():
            report.append(f"  • {scope}")
        
        report.append("")
        
        # Token information
        report.append("Stored Tokens:")
        report.append("-" * 15)
        tokens = self.list_stored_tokens()
        
        if tokens:
            for token in tokens:
                status = "✅" if token['valid'] else "❌"
                report.append(f"{status} {token['user_email']} ({token['file']})")
                if token['expires_in']:
                    report.append(f"   Expires in: {token['expires_in']}")
                if 'issues' in token and token['issues']:
                    for issue in token['issues']:
                        report.append(f"   Issue: {issue}")
        else:
            report.append("No stored tokens found")
        
        report.append("")
        
        # Environment config
        env_config = get_environment_config()
        report.append("Environment Configuration:")
        report.append("-" * 25)
        for key, value in env_config.items():
            report.append(f"{key}: {value}")
        
        return "\n".join(report)


def main():
    """Main CLI interface for OAuth2 setup"""
    parser = argparse.ArgumentParser(description="Google Calendar OAuth2 Setup Manager")
    parser.add_argument('--install', action='store_true', help='Install required packages')
    parser.add_argument('--setup-credentials', type=str, help='Setup credentials from file path')
    parser.add_argument('--list-tokens', action='store_true', help='List stored tokens')
    parser.add_argument('--cleanup', action='store_true', help='Remove expired tokens')
    parser.add_argument('--test', type=str, help='Test OAuth flow for user email')
    parser.add_argument('--report', action='store_true', help='Generate setup report')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    manager = OAuth2SetupManager()
    
    try:
        if args.install:
            print("Installing required packages...")
            success = manager.install_requirements()
            sys.exit(0 if success else 1)
        
        elif args.setup_credentials:
            print(f"Setting up credentials from {args.setup_credentials}...")
            success = manager.setup_credentials_file(args.setup_credentials)
            sys.exit(0 if success else 1)
        
        elif args.list_tokens:
            print("Stored authentication tokens:")
            tokens = manager.list_stored_tokens()
            if tokens:
                for token in tokens:
                    status = "✅ Valid" if token['valid'] else "❌ Invalid"
                    print(f"  {status} - {token['user_email']} ({token['file']})")
                    if token['expires_in']:
                        print(f"    Expires in: {token['expires_in']}")
            else:
                print("  No tokens found")
        
        elif args.cleanup:
            print("Cleaning up expired tokens...")
            removed = manager.cleanup_expired_tokens()
            print(f"Removed {removed} expired tokens")
        
        elif args.test:
            print(f"Testing OAuth2 flow for {args.test}...")
            success = manager.test_oauth_flow(args.test)
            sys.exit(0 if success else 1)
        
        elif args.report:
            print(manager.generate_setup_report())
        
        else:
            # Default: show environment check
            print("Google Calendar OAuth2 Environment Check")
            print("=" * 40)
            
            checks = manager.check_environment()
            all_good = True
            
            for check, result in checks.items():
                status = "✅" if result else "❌"
                print(f"{status} {check.replace('_', ' ').title()}")
                if not result:
                    all_good = False
            
            print()
            if all_good:
                print("✅ Environment is ready for OAuth2!")
                print("Use --test <email> to test authentication")
            else:
                print("❌ Environment needs attention")
                print("Use --install to install missing packages")
                print("Use --setup-credentials <path> to setup credentials")
            
            print("\nFor more options, use --help")
    
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
