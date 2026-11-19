"""Application configuration via pydantic-settings (reads .env)."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    fusion_url: str = Field(default="http://127.0.0.1:8765")
    fusion_token: str = Field(default="troque-este-token")
    data_dir: str = Field(default="./data")
    enable_electronics: bool = Field(default=False)
    gemini_api_key: str = Field(default="")
    gemini_model: str = Field(default="")


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
