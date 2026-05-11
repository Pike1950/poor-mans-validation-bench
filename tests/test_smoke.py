"""Phase 0 import-smoke tests.

These tests do nothing more than verify the orchestration stack is importable.
Running them is the first sanity check after `pip install -e .` on a fresh Pi.
A pass means: the venv resolved all declared dependencies, no version pin is
broken on this platform, and `pmvb` itself imports.

These are NOT the Phase 0 verification end-to-end test (that lives at
tests/test_phase0_e2e.py, authored in task #12).
"""

import pytest


@pytest.mark.sim
def test_pmvb_package_imports():
    """The pmvb package itself imports and exposes a version string."""
    import pmvb
    assert pmvb.__version__


@pytest.mark.sim
def test_pyvisa_stack_imports():
    """PyVISA + pyvisa-py (USB-TMC backend) + pyvisa-sim are importable."""
    import pyvisa
    import pyvisa_py  # noqa: F401
    import pyvisa_sim  # noqa: F401
    assert pyvisa.__version__


@pytest.mark.sim
def test_usb_stack_imports():
    """pyusb + pyserial are importable."""
    import usb.core  # noqa: F401
    import serial  # noqa: F401


@pytest.mark.sim
def test_test_runner_imports():
    """pytest itself is in the venv (obviously true if this runs, but explicit)."""
    import pytest as _pytest
    assert _pytest.__version__


@pytest.mark.sim
def test_influxdb_client_imports():
    """influxdb-client (works against InfluxDB 2.x natively) is importable."""
    import influxdb_client
    from influxdb_client.client.write_api import SYNCHRONOUS  # noqa: F401
    assert influxdb_client.__version__


@pytest.mark.sim
def test_report_stack_imports():
    """Jinja2 + Matplotlib for report generation."""
    import jinja2
    import matplotlib  # noqa: F401
    assert jinja2.__version__


@pytest.mark.sim
def test_mcp_imports():
    """The MCP server framework (FastMCP path)."""
    import mcp  # noqa: F401
    from mcp.server.fastmcp import FastMCP  # noqa: F401


@pytest.mark.sim
def test_anthropic_sdk_imports():
    """The Anthropic Claude SDK (used by orchestrator code calling out to Claude)."""
    import anthropic
    assert anthropic.__version__
