"""executor.py — Executes a CadPlan on the Fusion 360 main thread."""

import adsk.core
import adsk.fusion

from .ops import extrude, plane, sketch

OPS = {
    "create_plane_offset": plane.create_plane_offset,
    "create_sketch": sketch.create_sketch,
    "draw_circle": sketch.draw_circle,
    "extrude": extrude.extrude,
}


class Ctx:
    def __init__(self, design):
        self.design = design
        self.root = design.rootComponent
        self.planes = {}   # plane_id -> ConstructionPlane
        self.sketches = {}  # sketch_id -> Sketch
        self.bodies = {}   # body_name -> BRepBody


def execute_plan(plan: dict) -> list:
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    if design is None:
        raise RuntimeError("E_FUSION_NO_DESIGN: open a design in Fusion 360")

    ctx = Ctx(design)
    stop_on_error = plan.get("options", {}).get("stop_on_error", True)
    results = []

    for cmd in plan["commands"]:
        cid, op = cmd["id"], cmd["op"]
        try:
            fn = OPS.get(op)
            if fn is None:
                raise NotImplementedError(f"op '{op}' not yet implemented")
            info = fn(ctx, cmd["args"]) or {}
            results.append({"command_id": cid, "status": "ok", "info": info})
        except Exception as e:
            results.append({"command_id": cid, "status": "error", "error": str(e)})
            if stop_on_error:
                break

    return results
