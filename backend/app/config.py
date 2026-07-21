from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./channelbridge.db"
    jwt_secret: str = "local-development-only-change-me"
    storage_path: Path = Path("./storage")
    max_upload_bytes: int = 10 * 1024 * 1024
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

