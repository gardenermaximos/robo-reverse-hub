"""test_validate.py — Unit tests for the backend plan validator."""

import pytest

from app.modules.mechanical.compiler.validate import validate_plan


def _base_plan(**overrides):
    plan = {
        "schema_version": "1.0.0",
        "units": "mm",
        "constraints": {"max_enclosing_diameter_mm": 220.0},
        "commands": [
            {"id": "c001", "op": "create_sketch",
             "args": {"sketch_id": "sk_outline", "plane": {"base": "XY", "offset_mm": 0.0}}},
            {"id": "c002", "op": "draw_circle",
             "args": {"sketch_id": "sk_outline", "center": [0, 0], "diameter_mm": 215.0}},
            {"id": "c003", "op": "extrude",
             "args": {"sketch_id": "sk_outline", "operation": "new_body", "distance_mm": 3.0}},
        ],
    }
    plan.update(overrides)
    return plan


def test_valid_plan_has_no_errors():
    errors, warnings = validate_plan(_base_plan())
    assert errors == []


def test_rejects_oversized_disc():
    plan = _base_plan()
    plan["commands"][1]["args"]["diameter_mm"] = 230.0
    errors, _ = validate_plan(plan)
    assert any("envelope" in e.lower() or "230" in e for e in errors)


def test_rejects_duplicate_ids():
    plan = _base_plan()
    plan["commands"].append({
        "id": "c001",  # duplicate!
        "op": "create_sketch",
        "args": {"sketch_id": "sk_other", "plane": {"base": "XY", "offset_mm": 5.0}},
    })
    errors, _ = validate_plan(plan)
    assert any("duplicate" in e.lower() for e in errors)


def test_rejects_extrude_with_unknown_sketch():
    plan = {
        "schema_version": "1.0.0",
        "units": "mm",
        "constraints": {"max_enclosing_diameter_mm": 220.0},
        "commands": [
            {"id": "c001", "op": "extrude",
             "args": {"sketch_id": "sk_nonexistent", "operation": "new_body", "distance_mm": 3.0}},
        ],
    }
    errors, _ = validate_plan(plan)
    assert any("sk_nonexistent" in e for e in errors)


def test_rejects_draw_with_unknown_sketch():
    plan = {
        "schema_version": "1.0.0",
        "units": "mm",
        "constraints": {"max_enclosing_diameter_mm": 220.0},
        "commands": [
            {"id": "c001", "op": "draw_circle",
             "args": {"sketch_id": "sk_ghost", "center": [0, 0], "diameter_mm": 10.0}},
        ],
    }
    errors, _ = validate_plan(plan)
    assert any("sk_ghost" in e for e in errors)


def test_wrong_units():
    plan = _base_plan()
    plan["units"] = "cm"
    errors, _ = validate_plan(plan)
    assert any("units" in e.lower() for e in errors)
