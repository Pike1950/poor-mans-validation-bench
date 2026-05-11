"""Phase 0 end-to-end verification milestone.

Per SDD §13.1, Phase 0 closes when a single test exercises the full data path
end-to-end against BOTH the simulator and a real Pico 2 W:

1. Open `sim/placeholder/responses.yaml` via pyvisa-sim, send `*IDN?`, confirm
   the placeholder responds.
2. Open one of the chassis-connected Pico 2 W instruments via pyvisa-py over
   USB-TMC, send `*IDN?`, confirm a chip-ID-derived response.
3. Write both records to InfluxDB through `pmvb.influx.write_measurement` with
   the SDD §10.2 tag taxonomy.
4. Query InfluxDB back through `pmvb.influx.query_run` and confirm both
   records are present.
5. Render a Jinja2 + Matplotlib HTML report through `pmvb.reports.render`
   covering both records.

Run with the pmvb venv activated::

    pytest tests/test_phase0_e2e.py -v

Requires:
- InfluxDB 2.x running on localhost with token at /etc/pmvb/influx.token
- At least one Pico 2 W flashed with `pmvb_usbtmc_stub` connected to the hub
- udev rules from `tools/udev/99-pmvb-usbtmc.rules` installed so the bench user
  can claim the USB device via libusb

When this passes, Phase 0 is officially complete and Phase 1 begins.
"""

from __future__ import annotations

import re
import time
import uuid
from pathlib import Path

import pyvisa
import pytest

from pmvb.influx import query_run, write_measurement
from pmvb.reports.render import write_report

PMVB_VID = 0xCAFE
PMVB_PID = 0x4001
SIM_YAML = Path(__file__).resolve().parent.parent / "sim" / "placeholder" / "responses.yaml"

RESOURCE_RE = re.compile(
    r"^USB\d*::(0x[0-9A-Fa-f]+|\d+)::(0x[0-9A-Fa-f]+|\d+)::([^:]+)(?:::\d+)?::INSTR$"
)


def _is_pmvb_resource(resource: str) -> bool:
    m = RESOURCE_RE.match(resource)
    if not m:
        return False
    try:
        vid = int(m.group(1), 0)
        pid = int(m.group(2), 0)
    except ValueError:
        return False
    return vid == PMVB_VID and pid == PMVB_PID


@pytest.fixture(scope="module")
def e2e_run_id() -> str:
    """Unique run identifier shared across all records this test writes."""
    return f"phase0-e2e-{uuid.uuid4().hex[:8]}"


@pytest.mark.sim
@pytest.mark.hardware
def test_phase0_milestone(e2e_run_id: str, tmp_path: Path) -> None:
    """Phase 0 closing milestone: sim + real Pico -> InfluxDB -> report."""

    # ---- Part 1: pyvisa-sim placeholder ----
    assert SIM_YAML.exists(), f"sim schema missing at {SIM_YAML}"
    sim_rm = pyvisa.ResourceManager(f"{SIM_YAML.as_posix()}@sim")
    sim_resources = list(sim_rm.list_resources())
    assert sim_resources, "pyvisa-sim returned no resources from the placeholder schema"

    sim_inst = sim_rm.open_resource(sim_resources[0])
    sim_inst.timeout = 2000
    sim_idn = sim_inst.query("*IDN?").strip()
    sim_inst.close()
    assert sim_idn.startswith("PMVB"), f"unexpected sim IDN: {sim_idn!r}"

    write_measurement(
        measurement="phase0_e2e",
        instrument="sim-placeholder",
        channel=0,
        dut="phase0-bringup-dut",
        run_id=e2e_run_id,
        measurement_type="idn_response",
        value=1.0,
        extra_fields={"idn_string": sim_idn, "source": "pyvisa-sim"},
    )

    # ---- Part 2: real Pico 2 W over pyvisa-py USB-TMC ----
    real_rm = pyvisa.ResourceManager("@py")
    pmvb_resources = [r for r in real_rm.list_resources() if _is_pmvb_resource(r)]
    assert pmvb_resources, (
        "No PMVB Pico 2 W USB-TMC instruments discovered by pyvisa-py. "
        "Confirm at least one Pico is flashed with pmvb_usbtmc_stub and "
        "udev rules from tools/udev/99-pmvb-usbtmc.rules are installed."
    )

    pico_resource = pmvb_resources[0]
    pico_inst = real_rm.open_resource(pico_resource)
    pico_inst.timeout = 2000
    pico_idn = pico_inst.query("*IDN?").strip()
    pico_inst.close()
    assert pico_idn.startswith("PMVB"), f"unexpected Pico IDN: {pico_idn!r}"

    # Extract the chip-ID serial from the IDN response so we can tag the
    # InfluxDB record with the actual hardware identity (per SDD §10.1).
    parts = pico_idn.split(",")
    assert len(parts) >= 3, f"malformed IDN response: {pico_idn!r}"
    pico_serial = parts[2].strip()
    assert pico_serial and len(pico_serial) == 16, (
        f"expected 16-hex-char chip ID in IDN, got {pico_serial!r}"
    )

    write_measurement(
        measurement="phase0_e2e",
        instrument=f"pico-{pico_serial}",
        channel=0,
        dut="phase0-bringup-dut",
        run_id=e2e_run_id,
        measurement_type="idn_response",
        value=1.0,
        extra_fields={"idn_string": pico_idn, "source": "pyvisa-py-usbtmc"},
    )

    # ---- Part 3: query both back from InfluxDB ----
    # Tiny wait for write durability (the writes are SYNCHRONOUS but tag
    # indexing is async; give InfluxDB a moment).
    time.sleep(0.5)
    records = query_run(e2e_run_id)
    assert records, f"InfluxDB returned no records for run_id={e2e_run_id}"

    instruments = {r["instrument"] for r in records if r.get("instrument")}
    assert "sim-placeholder" in instruments, (
        f"sim record missing from InfluxDB. Got instruments: {instruments}"
    )
    pico_instruments = {i for i in instruments if i.startswith("pico-")}
    assert pico_instruments, (
        f"Pico record missing from InfluxDB. Got instruments: {instruments}"
    )

    # ---- Part 4: render Jinja2 report ----
    report_path = tmp_path / f"phase0_e2e_{e2e_run_id}.html"
    write_report(e2e_run_id, report_path)
    assert report_path.exists(), f"report not written to {report_path}"
    assert report_path.stat().st_size > 0, "report file is empty"

    content = report_path.read_text()
    assert e2e_run_id in content, "report does not reference the run_id"
    assert "sim-placeholder" in content, "report does not reference the sim record"
    assert any(serial in content for serial in pico_instruments), (
        "report does not reference any Pico record"
    )

    # ---- Summary printed for the human running pytest -v ----
    print()
    print(f"  Phase 0 verification milestone PASS")
    print(f"  run_id:                {e2e_run_id}")
    print(f"  sim IDN:               {sim_idn}")
    print(f"  pico IDN:              {pico_idn}")
    print(f"  pico resource:         {pico_resource}")
    print(f"  InfluxDB records:      {len(records)}")
    print(f"  Report written:        {report_path} ({report_path.stat().st_size} bytes)")
