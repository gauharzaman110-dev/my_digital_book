from pydantic_settings import SettingsConfigDict, BaseSettings
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    gemini_api_key: str
    qdrant_url: str
    qdrant_api_key: str
    database_url: str
    debug: bool = False
    session_expiry_hours: int = 24  # Default session expiry time


settings = Settings()