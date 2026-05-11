"""PMVB report renderer.

The standard pipeline:

1. Caller provides a run_id.
2. `render_run()` queries InfluxDB for all records tagged with that run_id.
3. Records are grouped by (instrument, channel, measurement_type).
4. Matplotlib renders one chart per group, base64-embedded into the HTML.
5. Jinja2 renders the report HTML against the template.
6. `write_report()` writes to disk.

Phase 0 ships a single template (`basic_report.html.j2`). Per-module phases
may add specialized templates (e.g., `audio_analyzer_report.html.j2` for the
1E + 2E recipe).
"""

from __future__ import annotations

import base64
import io
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless backend; no display required on the Pi

import matplotlib.pyplot as plt  # noqa: E402
from jinja2 import Environment, FileSystemLoader, select_autoescape  # noqa: E402

from pmvb.influx import query_run  # noqa: E402

TEMPLATE_DIR = Path(__file__).parent / "templates"


def _jinja_env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=select_autoescape(["html", "xml"]),
    )


def _plot_to_data_uri(records: list[dict], title: str = "") -> str:
    """Render a value-vs-time Matplotlib plot, return as a base64 PNG data URI.

    Empty `records` returns an empty string; the template renders an empty
    chart slot rather than failing.
    """
    if not records:
        return ""
    times = [r["time"] for r in records]
    values = [r["value"] for r in records]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(times, values, marker="o", linestyle="-")
    ax.set_xlabel("time")
    ax.set_ylabel("value")
    if title:
        ax.set_title(title)
    ax.grid(True, alpha=0.3)
    fig.autofmt_xdate()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=100, bbox_inches="tight")
    plt.close(fig)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def render_run(run_id: str, template: str = "basic_report.html.j2") -> str:
    """Render an HTML report for a given run_id. Returns the HTML as a string."""
    records = query_run(run_id)

    # Group records by (instrument, channel, measurement_type)
    grouped: dict[tuple, list[dict]] = {}
    for r in records:
        key = (r.get("instrument"), r.get("channel"), r.get("measurement_type"))
        grouped.setdefault(key, []).append(r)

    charts = []
    for (instrument, channel, mtype), recs in grouped.items():
        title = f"{instrument} ch{channel} {mtype}"
        charts.append({
            "title": title,
            "instrument": instrument,
            "channel": channel,
            "measurement_type": mtype,
            "count": len(recs),
            "data_uri": _plot_to_data_uri(recs, title),
            "records": recs,
        })

    env = _jinja_env()
    tpl = env.get_template(template)
    return tpl.render(
        run_id=run_id,
        record_count=len(records),
        chart_count=len(charts),
        charts=charts,
    )


def write_report(run_id: str, output_path: str | Path) -> Path:
    """Render to HTML and write to disk. Returns the output path."""
    path = Path(output_path)
    path.write_text(render_run(run_id))
    return path
