"""ExecutionReport schema — response from the Fusion 360 Add-in.

Source of truth: Section 5.4 of ARCHITECTURE.md.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class CommandResult(BaseModel):
    model_config = {"extra": "forbid"}
    command_id: str | None
    status: Literal["ok", "error"]
    info: dict[str, Any] = {}
    error: str | None = None


class FusionInfo(BaseModel):
    model_config = {"extra": "forbid"}
    document: str | None = None
    version: str | None = None


class ExecutionReport(BaseModel):
    model_config = {"extra": "forbid"}
    job_id: str
    status: Literal["queued", "running", "done", "failed"]
    started_at: float | None = None
    finished_at: float | None = None
    results: list[CommandResult] = []
    fusion: FusionInfo | None = None
