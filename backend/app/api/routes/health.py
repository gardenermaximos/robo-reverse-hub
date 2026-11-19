"""GET /api/health — backend health check and Fusion Add-in connectivity."""

from fastapi import APIRouter, Depends
from app.api.deps import fusion_client_dep
from app.integrations.fusion_client import FusionClient

router = APIRouter(tags=["health"])


@router.get("/health")
async def health(client: FusionClient = Depends(fusion_client_dep)):
    online = await client.ping()
    return {"status": "ok", "version": "0.1.0", "fusion": {"online": online}}
