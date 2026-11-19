"""Fase 2 — Electronics interfaces (Phase 2 stubs only).

PcbAnalyzer, KicadExporter, EasyedaExporter will be defined here.
Do not implement until Etapa 7+.
"""

from __future__ import annotations

from typing import Any, Protocol


class PcbAnalyzer(Protocol):
    """Phase 2: Analyze a PCB photo → list of components, pads, IR sensors."""

    def analyze_pcb(self, project_id: str, image_ids: list[str]) -> Any:
        ...


class KicadExporter(Protocol):
    """Phase 2: Export an EdaPlan to KiCad .kicad_sch format."""

    def export_kicad(self, eda_plan: Any, output_path: str) -> None:
        ...


class EasyedaExporter(Protocol):
    """Phase 2: Export an EdaPlan to EasyEDA JSON format."""

    def export_easyeda(self, eda_plan: Any, output_path: str) -> None:
        ...
