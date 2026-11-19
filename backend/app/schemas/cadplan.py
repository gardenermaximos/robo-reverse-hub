"""CadPlan schema — the central contract between backend, UI, and Add-in.

Source of truth: Section 5.3 of ARCHITECTURE.md.
JSON Schema is GENERATED from this file via scripts/export_schemas.py.
Never edit schemas/*.schema.json by hand.
"""

from __future__ import annotations

import re
from typing import Annotated, Any, Literal, Union

from pydantic import BaseModel, Field, field_validator, model_validator

from .common import Vec2, Units


# ─────────────────────────── Command argument models ─────────────────────────

class PlaneSpec(BaseModel):
    """Inline plane spec: either {base, offset_mm} or {plane_id}."""

    model_config = {"extra": "forbid"}

    base: Literal["XY"] | None = None
    offset_mm: float | None = None
    plane_id: str | None = None


class NewComponentArgs(BaseModel):
    model_config = {"extra": "forbid"}
    name: str


class CreatePlaneOffsetArgs(BaseModel):
    model_config = {"extra": "forbid"}
    plane_id: str
    base: Literal["XY"] = "XY"
    offset_mm: float


class CreateSketchArgs(BaseModel):
    model_config = {"extra": "forbid"}
    sketch_id: str
    plane: PlaneSpec
    name: str = ""


class DrawCircleArgs(BaseModel):
    model_config = {"extra": "forbid"}
    sketch_id: str
    center: Vec2
    diameter_mm: float = Field(gt=0)


class DrawRectArgs(BaseModel):
    model_config = {"extra": "forbid"}
    sketch_id: str
    center: Vec2
    width_mm: float = Field(gt=0)
    height_mm: float = Field(gt=0)
    corner_radius_mm: float = 0.0
    rotation_deg: float = 0.0


class DrawSlotArgs(BaseModel):
    model_config = {"extra": "forbid"}
    sketch_id: str
    center: Vec2
    length_mm: float = Field(gt=0)
    width_mm: float = Field(gt=0)
    rotation_deg: float = 0.0


class DrawPolygonArgs(BaseModel):
    model_config = {"extra": "forbid"}
    sketch_id: str
    center: Vec2
    sides: int = Field(ge=3)
    across_flats_mm: float = Field(gt=0)
    rotation_deg: float = 0.0


class ExtrudeArgs(BaseModel):
    model_config = {"extra": "forbid"}
    sketch_id: str
    operation: Literal["new_body", "join", "cut"]
    distance_mm: float = Field(gt=0)
    direction: Literal["positive", "negative", "symmetric"] = "positive"
    body_name: str | None = None
    target_body: str | None = None
    through_all: bool = False


class HoleArgs(BaseModel):
    model_config = {"extra": "forbid"}
    plane: PlaneSpec
    points: list[Vec2]
    thread: Literal["M2", "M2.5", "M3"] | None = None
    diameter_mm: float | None = None
    fit: Literal["clearance", "tap"] = "clearance"
    depth_mm: float = Field(gt=0)
    target_body: str | None = None
    countersink: bool = False

    @model_validator(mode="after")
    def thread_or_diameter(self) -> "HoleArgs":
        if self.thread is None and self.diameter_mm is None:
            raise ValueError("Either 'thread' or 'diameter_mm' must be specified")
        return self


class StandoffArgs(BaseModel):
    model_config = {"extra": "forbid"}
    center: Vec2
    z_from_mm: float
    height_mm: float = Field(gt=0)
    outer_shape: Literal["hex", "round"]
    across_flats_mm: float | None = None
    diameter_mm: float | None = None
    thread: Literal["M2", "M2.5", "M3"]
    body_name: str


# ─────────────────────────── Discriminated Command Union ─────────────────────

_CMD_ID_PATTERN = re.compile(r"^c\d{3,}$")


class _CmdBase(BaseModel):
    model_config = {"extra": "forbid"}
    id: str = Field(pattern=r"^c\d{3,}$")
    label: str = ""
    source_feature_ids: list[str] = []


class NewComponentCmd(_CmdBase):
    op: Literal["new_component"]
    args: NewComponentArgs


class CreatePlaneOffsetCmd(_CmdBase):
    op: Literal["create_plane_offset"]
    args: CreatePlaneOffsetArgs


class CreateSketchCmd(_CmdBase):
    op: Literal["create_sketch"]
    args: CreateSketchArgs


class DrawCircleCmd(_CmdBase):
    op: Literal["draw_circle"]
    args: DrawCircleArgs


class DrawRectCmd(_CmdBase):
    op: Literal["draw_rect"]
    args: DrawRectArgs


class DrawSlotCmd(_CmdBase):
    op: Literal["draw_slot"]
    args: DrawSlotArgs


class DrawPolygonCmd(_CmdBase):
    op: Literal["draw_polygon"]
    args: DrawPolygonArgs


class ExtrudeCmd(_CmdBase):
    op: Literal["extrude"]
    args: ExtrudeArgs


class HoleCmd(_CmdBase):
    op: Literal["hole"]
    args: HoleArgs


class StandoffCmd(_CmdBase):
    op: Literal["standoff"]
    args: StandoffArgs


AnyCommand = Annotated[
    Union[
        NewComponentCmd,
        CreatePlaneOffsetCmd,
        CreateSketchCmd,
        DrawCircleCmd,
        DrawRectCmd,
        DrawSlotCmd,
        DrawPolygonCmd,
        ExtrudeCmd,
        HoleCmd,
        StandoffCmd,
    ],
    Field(discriminator="op"),
]


# ─────────────────────────── Top-level CadPlan ───────────────────────────────

class CoordinateSystem(BaseModel):
    model_config = {"extra": "forbid"}
    origin: Literal["robot_center"] = "robot_center"
    x: Literal["right"] = "right"
    y: Literal["forward"] = "forward"
    z: Literal["up"] = "up"
    angle: Literal["ccw_deg_from_+x"] = "ccw_deg_from_+x"


class Constraints(BaseModel):
    model_config = {"extra": "forbid"}
    max_enclosing_diameter_mm: float = 220.0


class PlanOptions(BaseModel):
    model_config = {"extra": "forbid"}
    stop_on_error: bool = True
    group_timeline: bool = True
    dry_run: bool = False


class ProjectInfo(BaseModel):
    model_config = {"extra": "forbid"}
    id: str
    name: str
    created_at: str  # ISO 8601


class CadPlan(BaseModel):
    model_config = {"extra": "forbid"}

    schema_version: str = "1.0.0"
    project: ProjectInfo
    units: Units = "mm"
    coordinate_system: CoordinateSystem = Field(default_factory=CoordinateSystem)
    constraints: Constraints = Field(default_factory=Constraints)
    options: PlanOptions = Field(default_factory=PlanOptions)
    commands: list[AnyCommand]

    @model_validator(mode="after")
    def validate_command_consistency(self) -> "CadPlan":
        ids: set[str] = set()
        sketch_ids: set[str] = set()
        plane_ids: set[str] = set()
        errors: list[str] = []

        for cmd in self.commands:
            # Unique IDs
            if cmd.id in ids:
                errors.append(f"Duplicate command id: {cmd.id!r}")
            ids.add(cmd.id)

            if cmd.op == "create_sketch":
                sketch_ids.add(cmd.args.sketch_id)
                # Register plane_id if used
                if cmd.args.plane.plane_id:
                    if cmd.args.plane.plane_id not in plane_ids:
                        errors.append(
                            f"Command {cmd.id}: plane_id {cmd.args.plane.plane_id!r} "
                            f"used before creation"
                        )

            elif cmd.op == "create_plane_offset":
                plane_ids.add(cmd.args.plane_id)

            elif cmd.op in ("draw_circle", "draw_rect", "draw_slot", "draw_polygon"):
                if cmd.args.sketch_id not in sketch_ids:  # type: ignore[union-attr]
                    errors.append(
                        f"Command {cmd.id}: sketch_id {cmd.args.sketch_id!r} "  # type: ignore[union-attr]
                        f"used before creation"
                    )

            elif cmd.op == "extrude":
                if cmd.args.sketch_id not in sketch_ids:
                    errors.append(
                        f"Command {cmd.id}: sketch_id {cmd.args.sketch_id!r} used before creation"
                    )

        if errors:
            raise ValueError("; ".join(errors))
        return self
