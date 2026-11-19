"""AnalysisResult schema — output of the perception stage.

Source of truth: Section 5.2 of ARCHITECTURE.md.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

from .common import Vec2, ViewKind


CalibrationMethod = Literal[
    "outer_diameter", "reference_component", "fastener_head", "manual_two_points"
]

FeatureKind = Literal[
    "outline", "wheel_cutout", "hole", "standoff", "nut", "motor_mount", "other"
]

FeatureSource = Literal["gemini", "opencv", "gemini+opencv", "user"]


class CalibrationReference(BaseModel):
    model_config = {"extra": "forbid"}
    kind: str
    value_mm: float


class Calibration(BaseModel):
    model_config = {"extra": "forbid"}
    image_id: str
    view: ViewKind
    method: CalibrationMethod
    mm_per_px: float = Field(gt=0)
    origin_px: Vec2
    forward_axis_deg: float = 90.0
    reference: CalibrationReference | None = None
    residual_pct: float | None = None


class Layer(BaseModel):
    model_config = {"extra": "forbid"}
    index: int = Field(ge=0)
    name: str
    z_bottom_mm: float
    thickness_mm: float = Field(gt=0)
    source_image_ids: list[str] = []
    confidence: float = Field(ge=0.0, le=1.0)


class Feature(BaseModel):
    model_config = {"extra": "forbid"}
    id: str
    kind: FeatureKind
    layer_index: int | None = None
    layer_range: list[int] | None = None  # [from_layer_idx, to_layer_idx]
    center_mm: Vec2
    center_px: Vec2 | None = None
    params: dict[str, Any] = {}
    confidence: float = Field(ge=0.0, le=1.0)
    source: FeatureSource = "gemini"
    needs_review: bool = False

    @model_validator(mode="after")
    def validate_params_by_kind(self) -> "Feature":
        """Validate required params fields by feature kind."""
        required: dict[str, list[str]] = {
            "outline": [],  # either diameter_mm or polygon_mm — checked loosely
            "wheel_cutout": ["width_mm", "length_mm", "rotation_deg"],
            "hole": [],  # either thread or diameter_mm
            "standoff": ["thread", "outer_shape", "height_mm"],
            "nut": ["thread", "pocket"],
            "motor_mount": ["catalog_id"],
            "other": [],
        }
        for field in required.get(self.kind, []):
            if field not in self.params:
                raise ValueError(
                    f"Feature {self.id!r} kind={self.kind!r} missing required param {field!r}"
                )
        return self


class RobotInfo(BaseModel):
    model_config = {"extra": "forbid"}
    outer_diameter_mm: float = Field(gt=0)


class AnalysisResult(BaseModel):
    model_config = {"extra": "forbid"}

    schema_version: str = "1.0.0"
    project_id: str
    calibrations: list[Calibration] = []
    robot: RobotInfo | None = None
    layers: list[Layer] = []
    features: list[Feature] = []
    warnings: list[str] = []
