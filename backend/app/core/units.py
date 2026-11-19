"""Unit conversion utilities (backend side — for display only).

The contract is always in mm. Conversion to cm happens ONLY inside
the Fusion Add-in (fusion_addin/RCJBridge/units.py).
"""


def mm_to_cm(value_mm: float) -> float:
    """Convert millimetres to centimetres (for reference only — do NOT use in backend logic)."""
    return value_mm / 10.0


def cm_to_mm(value_cm: float) -> float:
    return value_cm * 10.0
