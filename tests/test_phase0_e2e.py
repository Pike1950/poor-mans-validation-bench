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

import pytest
import pyvisa
import yaml

from pmvb.influx import query_run, write_measurement
from pmvb.reports.render import write_report

PMVB_VID = 0xCAFE
PMVB_PID = 0x4001
SIM_YAML = Path(__file__).resolve().parent.parent / "sim" / "placeholder" / "responses.yaml"
NICKNAMES_FILE = Path(__file__).resolve().parent.parent / "tools" / "pico_nicknames.yaml"

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


def _parse_pmvb_resource(resource: str) -> str | None:
    """Return the serial from a PMVB USB-TMC resource string, or None."""
    m = RESOURCE_RE.match(resource)
    if not m:
        return None
    try:
        vid = int(m.group(1), 0)
        pid = int(m.group(2), 0)
    except ValueError:
        return None
    if vid != PMVB_VID or pid != PMVB_PID:
        return None
    return m.group(3)


def _load_pico_inventory() -> list[tuple[str, str]]:
    """Return [(serial, nickname), ...] from tools/pico_nicknames.yaml.

    Natural-sorted by the integer in the nickname so "Pico #10" follows
    "Pico #9" instead of landing between "#1" and "#2"."""
    if not NICKNAMES_FILE.exists():
        return []
    with NICKNAMES_FILE.open() as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        return []

    def sort_key(item: tuple[str, str]) -> tuple[int, str]:
        _, nick = item
        m = re.search(r"\d+", nick)
        return (int(m.group()) if m else 10**9, nick)

    return sorted(((str(k), str(v)) for k, v in data.items()), key=sort_key)


def _pytest_id(serial: str, nickname: str) -> str:
    """Build a shell-friendly pytest parametrize ID from nickname + serial."""
    clean = nickname.replace(" ", "_").replace("#", "")
    return f"{clean}-{serial[:8]}"


PICO_INVENTORY: list[tuple[str, str]] = _load_pico_inventory()


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


# ---------------------------------------------------------------------------
# Parametric inventory exercise: ping every Pico in tools/pico_nicknames.yaml
#
# The milestone above proves the orchestration plumbing works against ONE
# Pico. This parametric test proves every chip ID in the nickname registry
# is present, responds to *IDN?, and reports back its own chip ID. A failure
# in any single Pico isolates to that pytest test ID, so it is obvious which
# board went missing or drifted from the registry.
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def inventory_run_id() -> str:
    """Single run_id shared across all parametric inventory pings, so the
    round-trip query at the end can pull them all back as one batch."""
    return f"phase0-inventory-{uuid.uuid4().hex[:8]}"


@pytest.fixture(scope="module")
def pmvb_resource_map() -> dict[str, str]:
    """Discover every PMVB USB-TMC resource currently attached, keyed by
    chip-ID serial. Done once per pytest module run so we are not hitting
    pyvisa-py's enumeration path 10+ times."""
    rm = pyvisa.ResourceManager("@py")
    resource_map: dict[str, str] = {}
    for resource in rm.list_resources():
        serial = _parse_pmvb_resource(resource)
        if serial is not None:
            resource_map[serial] = resource
    return resource_map


@pytest.mark.hardware
@pytest.mark.parametrize(
    "serial,nickname",
    PICO_INVENTORY,
    ids=[_pytest_id(serial, nick) for serial, nick in PICO_INVENTORY],
)
def test_pico_inventory_ping(
    serial: str,
    nickname: str,
    pmvb_resource_map: dict[str, str],
    inventory_run_id: str,
) -> None:
    """Ping one Pico from the nickname registry and write to InfluxDB.

    Asserts:
    - The chip ID is discoverable by pyvisa-py (i.e. enumerates as USB-TMC).
    - *IDN? responds and the response starts with the PMVB vendor field.
    - The IDN response's serial field equals the registry chip ID (catches
      YAML-drift-from-hardware, mis-flashed firmware, and physical swaps
      that were not tracked in pico_nicknames.yaml).
    """
    if not PICO_INVENTORY:
        pytest.skip("tools/pico_nicknames.yaml is empty or missing")

    assert serial in pmvb_resource_map, (
        f"{nickname} (chip ID {serial}) not discovered by pyvisa-py. "
        f"Discovered chip IDs: {sorted(pmvb_resource_map.keys())}. "
        f"Either the Pico is unplugged, not flashed with pmvb_usbtmc_stub, "
        f"or the registry has drifted from the bench inventory."
    )
    resource = pmvb_resource_map[serial]

    rm = pyvisa.ResourceManager("@py")
    inst = rm.open_resource(resource)
    inst.timeout = 2000
    try:
        idn = inst.query("*IDN?").strip()
    finally:
        inst.close()

    assert idn.startswith("PMVB"), f"{nickname}: unexpected IDN {idn!r}"
    parts = idn.split(",")
    assert len(parts) >= 3, f"{nickname}: malformed IDN {idn!r}"
    reported_serial = parts[2].strip()
    assert reported_serial == serial, (
        f"{nickname}: IDN reports chip ID {reported_serial!r} but registry "
        f"expects {serial!r}. Either the YAML drifted from hardware, the "
        f"firmware is reporting a static serial, or two Picos got swapped."
    )

    write_measurement(
        measurement="phase0_inventory",
        instrument=f"pico-{serial}",
        channel=0,
        dut="phase0-bringup-dut",
        run_id=inventory_run_id,
        measurement_type="idn_response",
        value=1.0,
        extra_fields={
            "idn_string": idn,
            "nickname": nickname,
            "resource": resource,
            "source": "pyvisa-py-usbtmc",
        },
    )


@pytest.mark.hardware
def test_pico_inventory_round_trip(
    pmvb_resource_map: dict[str, str],
    inventory_run_id: str,
) -> None:
    """After every parametric ping has run, confirm all of them landed in
    InfluxDB under the shared inventory_run_id.

    This runs last in the file by virtue of pytest's in-file collection
    order. If a parametric ping failed earlier, the corresponding record is
    missing here and this test fails too, giving the human running pytest -v
    a single 'inventory round-trip' line to look at alongside the per-Pico
    details."""
    if not PICO_INVENTORY:
        pytest.skip("tools/pico_nicknames.yaml is empty or missing")

    # Same write-then-query lag tolerance the milestone test uses.
    time.sleep(0.5)
    records = query_run(inventory_run_id)
    assert records, (
        f"InfluxDB returned no records for inventory_run_id={inventory_run_id}. "
        f"Did every parametric ping skip or error out?"
    )

    instruments = {r["instrument"] for r in records if r.get("instrument")}
    expected = {f"pico-{serial}" for serial, _ in PICO_INVENTORY}
    missing = expected - instruments
    assert not missing, (
        f"InfluxDB missing inventory records for: {sorted(missing)}. "
        f"Found instruments: {sorted(instruments)}."
    )

    # ---- Summary printed for the human running pytest -v ----
    print()
    print(f"  Phase 0 inventory round-trip PASS")
    print(f"  inventory_run_id:      {inventory_run_id}")
    print(f"  Picos in registry:     {len(PICO_INVENTORY)}")
    print(f"  Picos enumerated:      {len(pmvb_resource_map)}")
    print(f"  InfluxDB records:      {len(records)}")
    for serial, nickname in PICO_INVENTORY:
        marker = "OK" if f"pico-{serial}" in instruments else "MISS"
        print(f"    [{marker:>4}] {nickname:<10} {serial}")
