"""Common types shared across all schemas.

All coordinates are in millimetres unless the field name ends with _px.
"""

from __future__ import annotations

from typing import Literal

# [x_mm, y_mm] relative to robot centre; _px variant when field ends with _px
Vec2 = tuple[float, float]

ViewKind = Literal["top", "side", "bottom", "iso"]

Units = Literal["mm"]
