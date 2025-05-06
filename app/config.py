# config.py: Environment variables and configuration
from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    GOOGLE_MAPS_API_KEY: str
    OPENWEATHER_API_KEY: str
    GEMINI_API_KEY: str
    DATABASE_URL: str = "sqlite:///./agriculture.db"  # Default to SQLite for simplicity

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Initialize settings object after the class definition
settings = Settings()

