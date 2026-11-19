"""Core Protocols (interfaces) for Phase 1 and Phase 2 modules.

Phase 2 (electronics) will add PcbAnalyzer, KicadExporter, EasyedaExporter here.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class Analyzer(Protocol):
    """Produces an AnalysisResult from one or more images."""

    def analyze(self, project_id: str, image_ids: list[str], hints: dict | None = None) -> Any:
        ...


@runtime_checkable
class PlanCompiler(Protocol):
    """Compiles an AnalysisResult into a CadPlan."""

    def compile(self, analysis: Any, options: dict | None = None) -> Any:
        ...


@runtime_checkable
class Exporter(Protocol):
    """Exports a plan to an external format or tool."""

    def export(self, plan: Any, **kwargs: Any) -> Any:
        ...
