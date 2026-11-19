"""Plan validation route.

POST /api/plan/validate — validates a CadPlan without sending to Fusion.
"""

from fastapi import APIRouter, Body
from app.modules.mechanical.compiler.validate import validate_plan

router = APIRouter(prefix="/plan", tags=["plan"])


@router.post("/validate")
async def plan_validate(plan: dict = Body(...)):
    errors, warnings = validate_plan(plan)
    return {"ok": len(errors) == 0, "errors": errors, "warnings": warnings}
