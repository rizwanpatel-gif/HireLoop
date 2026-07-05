"""
Configuration settings for HireLoop Interview Management System
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Application Settings
    app_name: str = "HireLoop Interview Management System"
    debug: bool = False
    
    # Database Settings
    database_url: str = "sqlite:///./hireloop.db"
    
    # Google Calendar API Settings
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/auth/callback"
    
    # OpenAI API Settings
    openai_api_key: str = ""
    
    # Email Settings
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    email_username: str = ""
    email_password: str = ""
    
    # Security Settings
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Business Logic Settings
    interview_duration_minutes: int = 60
    business_hours_start: int = 9  # 9 AM
    business_hours_end: int = 18   # 6 PM
    
    class Config:
        env_file = ".env"

settings = Settings()
