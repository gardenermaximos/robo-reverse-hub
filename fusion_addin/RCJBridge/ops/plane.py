"""ops/plane.py — create_plane_offset operation."""

import adsk.core
from ..units import mm_to_cm


def create_plane_offset(ctx, a: dict):
    planes = ctx.root.constructionPlanes
    inp = planes.createInput()
    inp.setByOffset(
        ctx.root.xYConstructionPlane,
        adsk.core.ValueInput.createByReal(mm_to_cm(a["offset_mm"])),
    )
    p = planes.add(inp)
    ctx.planes[a["plane_id"]] = p
    return {"plane_id": a["plane_id"]}
