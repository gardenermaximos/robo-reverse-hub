"""Module registry — registers Analyzer/PlanCompiler/Exporter implementations.

Modules guarded by ENABLE_ELECTRONICS are only registered when that flag is true.
"""

from __future__ import annotations

from typing import Any


class ModuleRegistry:
    """Simple registry of named module instances."""

    def __init__(self) -> None:
        self._modules: dict[str, Any] = {}

    def register(self, name: str, instance: Any) -> None:
        self._modules[name] = instance

    def get(self, name: str) -> Any | None:
        return self._modules.get(name)

    def all(self) -> dict[str, Any]:
        return dict(self._modules)


# Singleton registry used throughout the application
registry = ModuleRegistry()


def setup_registry(enable_electronics: bool = False) -> None:
    """Register built-in modules; electronics modules are gated by feature flag."""
    # Mechanical modules registered in app/main.py after imports are ready.
    # Electronics modules: not registered unless ENABLE_ELECTRONICS=true.
    if enable_electronics:
        # Phase 2 — not implemented yet
        pass
