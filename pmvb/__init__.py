"""Poor Man's Validation Bench — orchestration layer.

The `pmvb` package contains the Python-side orchestration code: PyVISA fixtures
for pytest, InfluxDB write/read helpers, the MCP gateway, the Jinja2 report
generator, and any module-agnostic glue.

Per-module SCPI YAML command tables live at `modules/<id>/commands.yaml` in the
repo root, not inside this package. PyVISA-sim YAML schemas (generated from the
per-module commands.yaml) live at `sim/<id>/responses.yaml`.
"""

__version__ = "0.1.0"
