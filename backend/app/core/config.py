from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database - MongoDB Atlas
    MONGODB_URL: str = "mongodb+srv://koasare009:%40Kwabenya1234@cluster0.hri9oup.mongodb.net/health?retryWrites=true&w=majority&appName=Cluster0"
    
    # JWT
    SECRET_KEY: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.superSecretKey_93f8a2b1c4e84b9e8d7f3c2a1f6d9a7b.randomSignaturePart"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # AI Models - No API keys needed
    MODEL_CACHE_DIR: str = "./models"
    USE_GPU: bool = False
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = True
    
    # Search and fallback settings
    ENABLE_WEB_SEARCH: bool = True
    MAX_SEARCH_RESULTS: int = 5
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
