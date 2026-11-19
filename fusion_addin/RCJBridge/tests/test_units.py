"""test_units.py — Tests for the mm_to_cm conversion."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from RCJBridge.units import mm_to_cm


def test_mm_to_cm_basic():
    assert mm_to_cm(10.0) == 1.0


def test_mm_to_cm_215():
    # 215 mm = 21.5 cm
    assert abs(mm_to_cm(215.0) - 21.5) < 1e-9


def test_mm_to_cm_zero():
    assert mm_to_cm(0.0) == 0.0


def test_mm_to_cm_fractional():
    assert abs(mm_to_cm(3.2) - 0.32) < 1e-9
