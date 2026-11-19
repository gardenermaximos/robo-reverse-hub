"""units.py — millimetre to centimetre conversion.

Conversion ONLY happens here. All CadPlan values are in mm.
Fusion 360 internal API uses centimetres.
"""


def mm_to_cm(value_mm: float) -> float:
    """Convert mm to cm for the Fusion 360 API."""
    return value_mm / 10.0
