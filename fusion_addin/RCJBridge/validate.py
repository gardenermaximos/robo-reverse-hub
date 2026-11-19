"""validate.py — Manual CadPlan validation for the Add-in (no external libs).

Must NOT import adsk at module level so pytest can run this outside Fusion.
"""

from __future__ import annotations

import math
from typing import Any

KNOWN_OPS = {
    "new_component",
    "create_plane_offset",
    "create_sketch",
    "draw_circle",
    "draw_rect",
    "draw_slot",
    "draw_polygon",
    "extrude",
    "hole",
    "standoff",
}

# Ops supported in this Add-in version (Etapa 1)
IMPLEMENTED_OPS = {
    "create_plane_offset",
    "create_sketch",
    "draw_circle",
    "extrude",
}


def validate_plan(plan: dict[str, Any]) -> tuple[list[str], list[str]]:
    """Return (errors, warnings)."""
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(plan, dict):
        errors.append("Plan must be a JSON object")
        return errors, warnings

    if plan.get("schema_version") != "1.0.0":
        warnings.append(f"schema_version={plan.get('schema_version')!r}; expected '1.0.0'")

    if plan.get("units") != "mm":
        errors.append(f"units must be 'mm', got {plan.get('units')!r}")

    commands = plan.get("commands")
    if not isinstance(commands, list):
        errors.append("'commands' must be a list")
        return errors, warnings

    seen_ids: set[str] = set()
    sketch_ids: set[str] = set()
    plane_ids: set[str] = set()
    max_diam = plan.get("constraints", {}).get("max_enclosing_diameter_mm", 220.0)

    for cmd in commands:
        if not isinstance(cmd, dict):
            errors.append("Each command must be a JSON object")
            continue

        cid = cmd.get("id", "<no id>")
        op = cmd.get("op", "<no op>")
        args = cmd.get("args") or {}

        # Unique IDs
        if cid in seen_ids:
            errors.append(f"Duplicate command id: {cid!r}")
        seen_ids.add(cid)

        # Required fields
        if not isinstance(args, dict):
            errors.append(f"Command {cid}: 'args' must be a JSON object")
            continue

        # Known op
        if op not in KNOWN_OPS:
            errors.append(f"Command {cid}: unknown op {op!r}")
            continue

        # Warn for unimplemented ops
        if op not in IMPLEMENTED_OPS:
            warnings.append(
                f"Command {cid}: op {op!r} not yet implemented in this Add-in version"
            )

        # Numeric/finite checks
        for key in ("distance_mm", "diameter_mm", "offset_mm", "height_mm"):
            if key in args:
                v = args[key]
                if not isinstance(v, (int, float)) or not math.isfinite(v) or v <= 0:
                    errors.append(f"Command {cid}: {key}={v!r} must be finite and > 0")

        # Track created sketches and planes
        if op == "create_sketch":
            sid = args.get("sketch_id")
            if not sid:
                errors.append(f"Command {cid}: missing sketch_id")
            else:
                sketch_ids.add(sid)

        elif op == "create_plane_offset":
            pid = args.get("plane_id")
            if not pid:
                errors.append(f"Command {cid}: missing plane_id")
            else:
                plane_ids.add(pid)

        elif op in ("draw_circle", "draw_rect", "draw_slot", "draw_polygon"):
            sid = args.get("sketch_id")
            if sid and sid not in sketch_ids:
                errors.append(f"Command {cid}: sketch_id {sid!r} used before creation")

        elif op == "extrude":
            sid = args.get("sketch_id")
            if sid and sid not in sketch_ids:
                errors.append(f"Command {cid}: sketch_id {sid!r} used before creation")

    return errors, warnings
