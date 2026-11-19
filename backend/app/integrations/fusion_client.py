"""FusionClient — httpx-based client for the RCJBridge Add-in HTTP server."""

from __future__ import annotations

import httpx

from app.core.errors import ApiError


class FusionClient:
    def __init__(self, base_url: str, token: str) -> None:
        self._base_url = base_url.rstrip("/")
        self._headers = {"X-RCJ-Token": token, "Content-Type": "application/json"}

    async def ping(self) -> bool:
        """Returns True if the Add-in is reachable, False otherwise (never raises)."""
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                r = await client.get(f"{self._base_url}/health", headers=self._headers)
                return r.status_code == 200
        except Exception:
            return False

    async def validate(self, plan: dict) -> dict:
        """Calls POST /validate on the Add-in."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.post(
                    f"{self._base_url}/validate", json=plan, headers=self._headers
                )
                r.raise_for_status()
                return r.json()
        except httpx.ConnectError:
            raise ApiError(ApiError.E_FUSION_OFFLINE, "Add-in offline")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise ApiError(ApiError.E_FUSION_AUTH, "Invalid token")
            raise ApiError(ApiError.E_FUSION_OFFLINE, str(e))

    async def execute(self, plan: dict) -> str:
        """Calls POST /execute on the Add-in. Returns job_id."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                r = await client.post(
                    f"{self._base_url}/execute", json=plan, headers=self._headers
                )
                if r.status_code == 401:
                    raise ApiError(ApiError.E_FUSION_AUTH, "Invalid token")
                r.raise_for_status()
                return r.json()["job_id"]
        except ApiError:
            raise
        except httpx.ConnectError:
            raise ApiError(ApiError.E_FUSION_OFFLINE, "Add-in offline")
        except Exception as e:
            raise ApiError(ApiError.E_FUSION_OFFLINE, str(e))

    async def get_job(self, job_id: str) -> dict:
        """Calls GET /jobs/{job_id} on the Add-in."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.get(
                    f"{self._base_url}/jobs/{job_id}", headers=self._headers
                )
                if r.status_code == 401:
                    raise ApiError(ApiError.E_FUSION_AUTH, "Invalid token")
                r.raise_for_status()
                return r.json()
        except ApiError:
            raise
        except httpx.ConnectError:
            raise ApiError(ApiError.E_FUSION_OFFLINE, "Add-in offline")
        except Exception as e:
            raise ApiError(ApiError.E_FUSION_OFFLINE, str(e))
