"""Fusion Add-in proxy routes.

Bloco B8 — Etapa 1 (temporary):
  GET  /api/fusion/status
  POST /api/fusion/execute   — receives a CadPlan body and forwards to Add-in
  GET  /api/fusion/jobs/{job_id}
"""

from fastapi import APIRouter, Depends, Body
from app.api.deps import fusion_client_dep
from app.integrations.fusion_client import FusionClient
from app.core.errors import ApiError

router = APIRouter(prefix="/fusion", tags=["fusion"])


@router.get("/status")
async def fusion_status(client: FusionClient = Depends(fusion_client_dep)):
    online = await client.ping()
    if not online:
        return {"online": False}
    return {"online": True}


@router.post("/execute")
async def fusion_execute(
    plan: dict = Body(...),
    client: FusionClient = Depends(fusion_client_dep),
):
    """Temporary Etapa 1 route: receives a raw CadPlan dict and forwards to Add-in."""
    try:
        job_id = await client.execute(plan)
    except ApiError:
        raise
    return {"job_id": job_id}


@router.get("/jobs/{job_id}")
async def fusion_job_status(
    job_id: str,
    client: FusionClient = Depends(fusion_client_dep),
):
    result = await client.get_job(job_id)
    return result
