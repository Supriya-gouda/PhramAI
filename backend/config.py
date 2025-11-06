"""Configuration management for PharmAI."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Config:
    """Application configuration."""
    
    # Hugging Face Configuration
    HF_TOKEN = os.getenv("HF_TOKEN", "")
    MODEL_NAME = os.getenv("MODEL_NAME", "ibm-granite/granite-3.2-2b-instruct")
    DEVICE = os.getenv("DEVICE", "auto")
    
    # Google Cloud TTS
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
    
    # API Configuration
    BACKEND_HOST = os.getenv("BACKEND_HOST", "0.0.0.0")
    BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8000"))
    
    # Frontend Configuration
    FRONTEND_PORT = int(os.getenv("FRONTEND_PORT", "8501"))
    
    # Data paths
    PROJECT_ROOT = Path(__file__).parent.parent
    DATA_DIR = PROJECT_ROOT / "backend" / "data"
    RAW_DATA_DIR = DATA_DIR / "raw"
    PROCESSED_DATA_DIR = DATA_DIR / "processed"
    
    @classmethod
    def validate(cls):
        """Validate configuration."""
        issues = []
        
        if not cls.HF_TOKEN:
            issues.append("⚠️ HF_TOKEN not set. Granite model may not work without authentication.")
        
        if not cls.PROCESSED_DATA_DIR.exists():
            issues.append(f"⚠️ Processed data directory not found: {cls.PROCESSED_DATA_DIR}")
        
        return issues


# Create global config instance
config = Config()
