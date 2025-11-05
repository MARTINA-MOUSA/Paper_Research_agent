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

# Log if API key is loaded (don't show the key itself)
if settings.GEMINI_API_KEY:
    from loguru import logger
    logger.info(f" GEMINI_API_KEY loaded from .env (length: {len(settings.GEMINI_API_KEY)} chars)")
else:
    from loguru import logger
    logger.warning(" GEMINI_API_KEY not found in .env file!")

