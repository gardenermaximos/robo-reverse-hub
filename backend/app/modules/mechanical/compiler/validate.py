"""Minimal CadPlan validator (Bloco C6).

Checks:
- Envelope ≤ max_enclosing_diameter_mm for draw_circle outline ops
- Unique command IDs
- Known ops
- sketch_id forward references in draw_* / extrude
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


def validate_plan(plan: dict[str, Any]) -> tuple[list[str], list[str]]:
    """Return (errors, warnings) for a raw CadPlan dict."""
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(plan, dict):
        errors.append("Plan must be a JSON object")
        return errors, warnings

    # Schema version
    if plan.get("schema_version") != "1.0.0":
        warnings.append(f"schema_version is {plan.get('schema_version')!r}; expected '1.0.0'")

    # Units
    if plan.get("units") != "mm":
        errors.append(f"units must be 'mm', got {plan.get('units')!r}")

    max_diam = plan.get("constraints", {}).get("max_enclosing_diameter_mm", 220.0)
    max_radius = max_diam / 2.0

    commands = plan.get("commands")
    if not isinstance(commands, list):
        errors.append("'commands' must be a list")
        return errors, warnings

    seen_ids: set[str] = set()
    sketch_ids: set[str] = set()
    plane_ids: set[str] = set()

    for cmd in commands:
        if not isinstance(cmd, dict):
            errors.append("Each command must be a JSON object")
            continue

        cid = cmd.get("id", "<no id>")
        op = cmd.get("op", "<no op>")
        args = cmd.get("args", {})

        # Unique IDs
        if cid in seen_ids:
            errors.append(f"Duplicate command id: {cid!r}")
        seen_ids.add(cid)

        # Known ops
        if op not in KNOWN_OPS:
            errors.append(f"Command {cid}: unknown op {op!r}")
            continue

        # args must be a dict
        if not isinstance(args, dict):
            errors.append(f"Command {cid}: 'args' must be a JSON object")
            continue

        # Track sketch / plane creation
        if op == "create_sketch":
            sid = args.get("sketch_id")
            if not sid:
                errors.append(f"Command {cid}: create_sketch missing 'sketch_id'")
            else:
                sketch_ids.add(sid)
            # Validate plane_id reference
            plane = args.get("plane", {})
            if isinstance(plane, dict) and plane.get("plane_id"):
                if plane["plane_id"] not in plane_ids:
                    errors.append(
                        f"Command {cid}: plane_id {plane['plane_id']!r} used before creation"
                    )

        elif op == "create_plane_offset":
            pid = args.get("plane_id")
            if not pid:
                errors.append(f"Command {cid}: create_plane_offset missing 'plane_id'")
            else:
                plane_ids.add(pid)

        elif op in ("draw_circle", "draw_rect", "draw_slot", "draw_polygon"):
            sid = args.get("sketch_id")
            if sid and sid not in sketch_ids:
                errors.append(
                    f"Command {cid}: sketch_id {sid!r} used before creation"
                )

            # Envelope check for draw_circle
            if op == "draw_circle":
                center = args.get("center", [0, 0])
                diam = args.get("diameter_mm", 0)
                if isinstance(center, (list, tuple)) and len(center) == 2:
                    dist = math.sqrt(center[0] ** 2 + center[1] ** 2)
                    if dist + diam / 2 > max_radius:
                        errors.append(
                            f"Command {cid}: circle extends beyond envelope "
                            f"({dist + diam/2:.1f} mm > {max_radius:.1f} mm radius)"
                        )

        elif op == "extrude":
            sid = args.get("sketch_id")
            if sid and sid not in sketch_ids:
                errors.append(
                    f"Command {cid}: sketch_id {sid!r} used before creation"
                )

        elif op == "standoff":
            warnings.append(
                f"Command {cid}: op 'standoff' not yet implemented in this Add-in version"
            )

    return errors, warnings
