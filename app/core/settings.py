# app/core/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    SECRET_KEY: str = "dev-change-me"
    STAFF_SECRET_KEY: str = "dev-change-me-staff"
    DATABASE_URL: str = "sqlite:///./driver.sqlite3"

    # pydantic v2-style config
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()
