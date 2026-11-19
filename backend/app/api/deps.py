"""FastAPI dependency helpers."""

from app.config import Settings, get_settings
from app.integrations.fusion_client import FusionClient


def settings_dep() -> Settings:
    return get_settings()


def fusion_client_dep() -> FusionClient:
    s = get_settings()
    return FusionClient(base_url=s.fusion_url, token=s.fusion_token)
