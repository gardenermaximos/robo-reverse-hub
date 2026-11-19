"""test_api_smoke.py — Smoke tests for health, plan/validate and fusion/execute endpoints.

FusionClient is mocked so these tests run without the Add-in.
"""

import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.fixture
def mock_fusion_online():
    with patch(
        "app.integrations.fusion_client.FusionClient.ping",
        new_callable=AsyncMock,
        return_value=True,
    ):
        yield


@pytest.fixture
def mock_fusion_offline():
    with patch(
        "app.integrations.fusion_client.FusionClient.ping",
        new_callable=AsyncMock,
        return_value=False,
    ):
        yield


@pytest.fixture
def mock_fusion_execute():
    with patch(
        "app.integrations.fusion_client.FusionClient.execute",
        new_callable=AsyncMock,
        return_value="job_abc123",
    ):
        yield


@pytest.mark.asyncio
async def test_health_fusion_offline(mock_fusion_offline):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["fusion"]["online"] is False


@pytest.mark.asyncio
async def test_health_fusion_online(mock_fusion_online):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["fusion"]["online"] is True


@pytest.mark.asyncio
async def test_plan_validate_valid():
    plan = {
        "schema_version": "1.0.0",
        "units": "mm",
        "constraints": {"max_enclosing_diameter_mm": 220.0},
        "commands": [
            {"id": "c001", "op": "create_sketch",
             "args": {"sketch_id": "sk_out", "plane": {"base": "XY", "offset_mm": 0.0}}},
            {"id": "c002", "op": "draw_circle",
             "args": {"sketch_id": "sk_out", "center": [0, 0], "diameter_mm": 215.0}},
        ],
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.post("/api/plan/validate", json=plan)
    assert r.status_code == 200
    assert r.json()["ok"] is True


@pytest.mark.asyncio
async def test_plan_validate_oversized():
    plan = {
        "schema_version": "1.0.0",
        "units": "mm",
        "constraints": {"max_enclosing_diameter_mm": 220.0},
        "commands": [
            {"id": "c001", "op": "create_sketch",
             "args": {"sketch_id": "sk_out", "plane": {"base": "XY", "offset_mm": 0.0}}},
            {"id": "c002", "op": "draw_circle",
             "args": {"sketch_id": "sk_out", "center": [0, 0], "diameter_mm": 230.0}},
        ],
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.post("/api/plan/validate", json=plan)
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is False
    assert len(body["errors"]) > 0


@pytest.mark.asyncio
async def test_fusion_execute_mocked(mock_fusion_execute):
    import json
    from pathlib import Path

    plan_path = (
        Path(__file__).parent.parent.parent
        / "schemas" / "examples" / "smoke_disc_4holes.cadplan.json"
    )
    plan = json.loads(plan_path.read_text(encoding="utf-8"))

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.post("/api/fusion/execute", json=plan)
    assert r.status_code == 200
    assert r.json()["job_id"] == "job_abc123"
