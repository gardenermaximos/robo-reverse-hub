"""Project file storage — reads/writes JSON files under data/projects/<id>/."""

from __future__ import annotations

import json
import os
from pathlib import Path

from app.config import get_settings


def _projects_root() -> Path:
    return Path(get_settings().data_dir) / "projects"


def _project_dir(project_id: str) -> Path:
    return _projects_root() / project_id


def project_exists(project_id: str) -> bool:
    return (_project_dir(project_id) / "project.json").exists()


def save_json(project_id: str, filename: str, data: dict) -> None:
    d = _project_dir(project_id)
    d.mkdir(parents=True, exist_ok=True)
    (d / filename).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def load_json(project_id: str, filename: str) -> dict | None:
    p = _project_dir(project_id) / filename
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def images_dir(project_id: str) -> Path:
    d = _project_dir(project_id) / "images"
    d.mkdir(parents=True, exist_ok=True)
    return d
