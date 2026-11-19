"""fastener_table.py — Standard fastener dimensions (ISO 273 / DIN 912).

Values based on the catalog in Section 14 of ARCHITECTURE.md.
Verify against your actual hardware batch before use.
"""

# Clearance (through-hole) diameters in mm — ISO 273 fine series
CLEARANCE: dict[str, float] = {
    "M2": 2.2,
    "M2.5": 2.7,
    "M3": 3.2,
}

# Tap (threaded-hole) drill diameters in mm
TAP: dict[str, float] = {
    "M2": 1.6,
    "M2.5": 2.05,
    "M3": 2.5,
}

# Cap screw head (Ø × height) in mm
CAP_HEAD: dict[str, tuple[float, float]] = {
    "M2": (3.8, 2.0),
    "M2.5": (4.5, 2.5),
    "M3": (5.5, 3.0),
}

# Hex nut (across-flats × thickness) in mm
HEX_NUT: dict[str, tuple[float, float]] = {
    "M2": (4.0, 1.6),
    "M2.5": (5.0, 2.0),
    "M3": (5.5, 2.4),
}


def clearance_diameter(thread: str) -> float:
    if thread not in CLEARANCE:
        raise ValueError(f"Unknown thread size: {thread!r}. Known: {list(CLEARANCE)}")
    return CLEARANCE[thread]


def tap_diameter(thread: str) -> float:
    if thread not in TAP:
        raise ValueError(f"Unknown thread size: {thread!r}. Known: {list(TAP)}")
    return TAP[thread]
