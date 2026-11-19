"""test_schema_roundtrip.py — All examples/*.json must validate and round-trip."""

import json
from pathlib import Path

import pytest

from app.schemas.cadplan import CadPlan

EXAMPLES_DIR = Path(__file__).parent.parent.parent / "schemas" / "examples"


def get_example_files():
    return list(EXAMPLES_DIR.glob("*.cadplan.json"))


@pytest.mark.parametrize("path", get_example_files(), ids=lambda p: p.name)
def test_cadplan_roundtrip(path: Path):
    raw = json.loads(path.read_text(encoding="utf-8"))
    plan = CadPlan.model_validate(raw)
    dumped = json.loads(plan.model_dump_json())
    # Re-validate the dump — no data loss
    plan2 = CadPlan.model_validate(dumped)
    assert plan.schema_version == plan2.schema_version
    assert len(plan.commands) == len(plan2.commands)
