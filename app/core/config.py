"""Application configuration settings"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application
    app_name: str = "OOO Consolidator"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = True
    secret_key: str
    timezone: str = "UTC"

    # Slack
    slack_bot_token: Optional[str] = None
    slack_user_token: Optional[str] = None
    slack_user_id: Optional[str] = None

    # Google
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    google_redirect_uri: str = "http://localhost:8000/oauth/google/callback"

    # Gmail
    email_address: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
