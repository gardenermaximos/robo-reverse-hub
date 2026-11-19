"""API error codes, model and global FastAPI exception handler."""

from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse


class ApiError(Exception):
    """Structured application error with a code, message and optional details."""

    # Error codes (Section 5.5 of ARCHITECTURE.md)
    E_SCHEMA = "E_SCHEMA"
    E_CALIB_MISSING = "E_CALIB_MISSING"
    E_CALIB_CONFLICT = "E_CALIB_CONFLICT"
    E_ENVELOPE = "E_ENVELOPE"
    E_LLM = "E_LLM"
    E_FUSION_OFFLINE = "E_FUSION_OFFLINE"
    E_FUSION_AUTH = "E_FUSION_AUTH"
    E_FUSION_NO_DESIGN = "E_FUSION_NO_DESIGN"
    E_CMD_FAILED = "E_CMD_FAILED"

    _HTTP_STATUS: dict[str, int] = {
        E_SCHEMA: 422,
        E_CALIB_MISSING: 400,
        E_CALIB_CONFLICT: 409,
        E_ENVELOPE: 422,
        E_LLM: 502,
        E_FUSION_OFFLINE: 503,
        E_FUSION_AUTH: 403,
        E_FUSION_NO_DESIGN: 409,
        E_CMD_FAILED: 422,
    }

    def __init__(self, code: str, message: str, details: dict | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}

    @property
    def http_status(self) -> int:
        return self._HTTP_STATUS.get(self.code, 500)


async def api_error_handler(request: Request, exc: ApiError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.http_status,
        content={"error": {"code": exc.code, "message": exc.message, "details": exc.details}},
    )
