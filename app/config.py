from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "Student Pulse AI"
    TAGLINE: str = "Evidence → Insight → Action"
    API_V1_PREFIX: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "sqlite:///./student_pulse.db"
    
    # Auth & Security
    AUTH_SECRET: str = "student-pulse-ai-prototype-secret-2026-safe"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 180
    
    # Explainable AI integration
    AI_ENABLED: bool = False
    AI_PROVIDER_API_KEY: str = ""
    AI_MODEL_NAME: str = "gemini-1.5-flash"
    
    # Paths
    BASE_DIR: Path = BASE_DIR
    DATA_DIR: Path = BASE_DIR / "data"
    
    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:3000"
    ]
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
