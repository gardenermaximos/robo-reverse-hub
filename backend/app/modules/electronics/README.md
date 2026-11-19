# Fase 2 — Electronics Module (not implemented)

This module will implement PCB analysis and EDA export for Phase 2.

Planned components:
- `PcbAnalyzer` — photo → PCB components, pins, IR sensors (implements `core.interfaces.Analyzer`)
- `KicadExporter` — `EdaPlan` → KiCad `.kicad_sch` S-expressions (implements `core.interfaces.Exporter`)
- `EasyedaExporter` — `EdaPlan` → EasyEDA JSON format (implements `core.interfaces.Exporter`)

**Do not implement until Etapa 7+.**
Only add stubs/Protocols in `interfaces.py` to keep the architecture extensible.
