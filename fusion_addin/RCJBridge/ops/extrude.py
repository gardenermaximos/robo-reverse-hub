"""ops/extrude.py — extrude operation."""

import adsk.core
import adsk.fusion
from ..units import mm_to_cm

_OPS = {
    "new_body": adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
    "join": adsk.fusion.FeatureOperations.JoinFeatureOperation,
    "cut": adsk.fusion.FeatureOperations.CutFeatureOperation,
}


def extrude(ctx, a: dict):
    sk = ctx.sketches[a["sketch_id"]]
    if sk.profiles.count == 0:
        raise RuntimeError(f"No profiles found in sketch '{sk.name}'")

    profiles = adsk.core.ObjectCollection.create()
    for p in sk.profiles:
        profiles.add(p)

    feats = ctx.root.features.extrudeFeatures
    inp = feats.createInput(profiles, _OPS[a["operation"]])

    dist = mm_to_cm(a["distance_mm"])
    direction = a.get("direction", "positive")
    if direction == "symmetric":
        inp.setDistanceExtent(True, adsk.core.ValueInput.createByReal(dist))
    else:
        signed = dist if direction == "positive" else -dist
        inp.setDistanceExtent(False, adsk.core.ValueInput.createByReal(signed))

    target = a.get("target_body")
    if a["operation"] == "cut" and target:
        body = ctx.bodies.get(target)
        if body is None:
            raise RuntimeError(f"target_body '{target}' not found")
        # Note: if participantBodies doesn't accept a plain list, use ObjectCollection
        # and document the fix in docs/fusion-api-notes.md
        inp.participantBodies = [body]

    feat = feats.add(inp)
    name = a.get("body_name")
    if a["operation"] == "new_body" and name:
        body = feat.bodies.item(0)
        body.name = name
        ctx.bodies[name] = body
    return {"feature": feat.name}
