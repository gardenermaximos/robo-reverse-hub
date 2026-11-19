"""test_validate.py — Tests for the Add-in validator (no adsk required)."""

import sys
import os

# Allow importing from the RCJBridge package without adsk
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from RCJBridge.validate import validate_plan


def _base_plan():
    return {
        "schema_version": "1.0.0",
        "units": "mm",
        "constraints": {"max_enclosing_diameter_mm": 220.0},
        "commands": [
            {"id": "c001", "op": "create_sketch",
             "args": {"sketch_id": "sk_out", "plane": {"base": "XY", "offset_mm": 0.0}}},
            {"id": "c002", "op": "draw_circle",
             "args": {"sketch_id": "sk_out", "center": [0, 0], "diameter_mm": 215.0}},
            {"id": "c003", "op": "extrude",
             "args": {"sketch_id": "sk_out", "operation": "new_body", "distance_mm": 3.0}},
        ],
    }


def test_valid_plan():
    errors, warnings = validate_plan(_base_plan())
    assert errors == []


def test_duplicate_ids():
    plan = _base_plan()
    plan["commands"].append(
        {"id": "c001", "op": "create_sketch",
         "args": {"sketch_id": "sk_other", "plane": {"base": "XY", "offset_mm": 5.0}}}
    )
    errors, _ = validate_plan(plan)
    assert any("duplicate" in e.lower() for e in errors)


def test_unknown_op():
    plan = _base_plan()
    plan["commands"].append(
        {"id": "c099", "op": "fly_to_moon", "args": {}}
    )
    errors, _ = validate_plan(plan)
    assert any("fly_to_moon" in e for e in errors)


def test_unimplemented_op_is_warning():
    plan = _base_plan()
    plan["commands"].append(
        {"id": "c099", "op": "standoff",
         "args": {"center": [0, 0], "z_from_mm": 3.0, "height_mm": 15.0,
                  "outer_shape": "hex", "across_flats_mm": 5.0,
                  "thread": "M3", "body_name": "std_01"}}
    )
    errors, warnings = validate_plan(plan)
    assert not any("standoff" in e for e in errors)
    assert any("standoff" in w for w in warnings)


def test_wrong_units():
    plan = _base_plan()
    plan["units"] = "cm"
    errors, _ = validate_plan(plan)
    assert any("units" in e.lower() for e in errors)
