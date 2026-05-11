"""Pytest fixtures for PMVB test orchestration.

Implements the SDD §10.3 fixture pattern:

- `run_id`     a UUID identifying every measurement from the current pytest run
- `dut`        the DUT under test (overridable via env or parametrization)
- `record`     a callable that writes a measurement to InfluxDB tagged with
               run_id + dut, so test code does not have to re-pass those each
               time

Tests reference these fixtures by name. Phase 1+ adds a `module` fixture that
returns a PyVISA resource (live or simulated), plus calibration fixtures.
"""

from __future__ import annotations

import os
import uuid
from collections.abc import Callable
from typing import Any

import pytest

from pmvb.influx import write_measurement


@pytest.fixture(scope="session")
def run_id() -> str:
    """A UUID tagging every measurement in the current pytest run.

    Override via the `PMVB_RUN_ID` env var to coordinate a multi-pytest run
    (e.g., one shell-level run_id covering several pytest invocations).
    """
    return os.environ.get("PMVB_RUN_ID", f"run-{uuid.uuid4().hex[:12]}")


@pytest.fixture
def dut() -> str:
    """The DUT under test. Override per-test by parametrizing or by env."""
    return os.environ.get("PMVB_DUT", "unspecified")


@pytest.fixture
def record(run_id: str, dut: str) -> Callable[..., None]:
    """Returns a function that writes one measurement to InfluxDB.

    The returned callable closes over run_id and dut, so test code only has to
    pass the instrument/channel/measurement_type/value::

        def test_voltage(record):
            record(instrument="1B", channel=0,
                   measurement_type="voltage_dc", value=2.483)
    """
    def _record(
        *,
        instrument: str,
        channel: str | int,
        measurement_type: str,
        value: float,
        measurement: str = "measurement",
        extra_fields: dict[str, Any] | None = None,
    ) -> None:
        write_measurement(
            measurement=measurement,
            instrument=instrument,
            channel=channel,
            dut=dut,
            run_id=run_id,
            measurement_type=measurement_type,
            value=value,
            extra_fields=extra_fields,
        )
    return _record
