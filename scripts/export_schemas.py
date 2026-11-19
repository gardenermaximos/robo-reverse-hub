"""export_schemas.py — Generate JSON Schemas from Pydantic models.

Usage (from project root):
    cd backend && uv run python ../scripts/export_schemas.py

Outputs:
    schemas/cadplan.schema.json
    schemas/analysis.schema.json
"""

import json
import sys
from pathlib import Path

# Allow running from project root or from backend/
root = Path(__file__).parent.parent
sys.path.insert(0, str(root / "backend"))

from app.schemas.cadplan import CadPlan
from app.schemas.analysis import AnalysisResult

schemas_dir = root / "schemas"
schemas_dir.mkdir(exist_ok=True)

for model, filename in [
    (CadPlan, "cadplan.schema.json"),
    (AnalysisResult, "analysis.schema.json"),
]:
    schema = model.model_json_schema()
    out = schemas_dir / filename
    out.write_text(json.dumps(schema, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Written: {out}")

print("Done.")
