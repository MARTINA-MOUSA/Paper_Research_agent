import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    # API Keys
    GEMINI_API_KEY: str = ""
    
    # Database
    DATABASE_URL: str = "sqlite:///./app.db"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4
    
    # CORS
    CORS_ORIGINS: str = "*"
    
    # File handling
    MAX_FILE_SIZE: int = 10485760  # 10MB default
    UPLOAD_DIR: str = "uploads"
    OUTPUT_DIR: str = "outputs"
    MAX_PDF_PAGES: int = 12
    # Arabic dialect preference for script generation
    ARABIC_DIALECT: str = "MSA"  # options: MSA, EGYPTIAN

    # TTS Providers
    TTS_PROVIDER: str = "gtts"  # options: gtts, azure, elevenlabs
    # Azure Speech
    AZURE_SPEECH_KEY: str = ""
    AZURE_SPEECH_REGION: str = ""
    AZURE_SPEECH_VOICE: str = "ar-EG-SalmaNeural"  # or ar-EG-ShakirNeural
    # ElevenLabs
    ELEVENLABS_API_KEY: str = ""
    ELEVENLABS_VOICE_ID: str = ""  # Set a voice ID supporting Arabic
    
    # Processing limits
    MAX_TEXT_LENGTH: int = 50000
    MAX_SECTIONS: int = 20
    
    # Gemini
    GEMINI_MODEL: str = "gemini-2.5-flash"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Convert CORS_ORIGINS string to list"""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

# Load settings - will read from .env file automatically
settings = Settings()

# Log if API key is set (don't show the key itself)
from loguru import logger
logger.info(f" GEMINI_API_KEY present: {'Yes' if bool(settings.GEMINI_API_KEY) else 'No'}")

