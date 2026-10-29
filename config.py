"""Configuration settings for the Multi-Agent Research Assistant powered by Sarvam AI."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root if it exists
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    load_dotenv()

class Config:
    """Central configuration for agents and Sarvam AI connection."""
    
    # Sarvam AI API Key
    SARVAM_API_KEY: str = os.getenv("SARVAM_API_KEY", "").strip()
    
    # Model name - 'sarvam-105b' is recommended for comprehensive reasoning
    SARVAM_MODEL: str = os.getenv("SARVAM_MODEL", "sarvam-105b").strip()
    
    # API Base URL
    SARVAM_BASE_URL: str = os.getenv("SARVAM_BASE_URL", "https://api.sarvam.ai/v1").rstrip("/")
    
    # Temperature for reasoning & creativity
    SARVAM_TEMPERATURE: float = float(os.getenv("SARVAM_TEMPERATURE", "0.2"))
    
    # Max tokens per agent turn
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "2048"))
    
    # Request timeout in seconds
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "60"))
    
    # Demo/simulation mode when API key is not yet set
    DEMO_MODE: bool = os.getenv("DEMO_MODE", "false").lower() in ("true", "1", "yes")

    @classmethod
    def has_api_key(cls) -> bool:
        """Check if an API key is set and not a placeholder."""
        return bool(
            cls.SARVAM_API_KEY
            and cls.SARVAM_API_KEY.lower() not in ("your_sarvam_api_key_here", "none", "")
        )
