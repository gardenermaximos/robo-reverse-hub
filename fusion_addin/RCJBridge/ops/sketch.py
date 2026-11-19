"""ops/sketch.py — create_sketch and draw_circle operations."""

import adsk.core
from ..units import mm_to_cm


def _resolve_plane(ctx, plane_spec: dict):
    if "plane_id" in plane_spec:
        return ctx.planes[plane_spec["plane_id"]]
    offset = plane_spec.get("offset_mm", 0.0)
    if offset == 0:
        return ctx.root.xYConstructionPlane
    planes = ctx.root.constructionPlanes
    inp = planes.createInput()
    inp.setByOffset(
        ctx.root.xYConstructionPlane,
        adsk.core.ValueInput.createByReal(mm_to_cm(offset)),
    )
    return planes.add(inp)


def create_sketch(ctx, a: dict):
    sk = ctx.root.sketches.add(_resolve_plane(ctx, a["plane"]))
    if a.get("name"):
        sk.name = a["name"]
    ctx.sketches[a["sketch_id"]] = sk
    return {"sketch": sk.name}


def draw_circle(ctx, a: dict):
    sk = ctx.sketches[a["sketch_id"]]
    x, y = a["center"]
    center = adsk.core.Point3D.create(mm_to_cm(x), mm_to_cm(y), 0)
    sk.sketchCurves.sketchCircles.addByCenterRadius(
        center, mm_to_cm(a["diameter_mm"]) / 2.0
    )
    return {}
