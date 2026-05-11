#!/usr/bin/env python3
"""Hot-plug-by-serial verification helper.

Enumerates every USB-TMC instrument currently attached to the chassis hub, sends
`*IDN?` to each one, and prints a compact table. Run this before and after
physically moving a Pico between hub ports; the serial number column should
match across runs even if the kernel-assigned /dev/usbtmcN renumbers.

Usage::

    python tools/hot_plug_verify.py

Closes the Phase 0 hot-plug verification milestone when three port-swap
permutations all show the same serial-to-IDN mapping.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pyvisa
import yaml

NICKNAMES_FILE = Path(__file__).parent / "pico_nicknames.yaml"


PMVB_VID = 0xCAFE
PMVB_PID = 0x4001
# pyvisa-py emits either hex-with-prefix (USB::0xCAFE::0x4001::SERIAL::INSTR)
# or decimal-no-prefix with interface number (USB0::51966::16385::SERIAL::0::INSTR).
# Match both; convert to int with base=0 for unified comparison.
RESOURCE_PATTERN = re.compile(
    r"^USB\d*::"
    r"(0x[0-9A-Fa-f]+|\d+)::"
    r"(0x[0-9A-Fa-f]+|\d+)::"
    r"([^:]+)"
    r"(?:::\d+)?"
    r"::INSTR$"
)


def parse_resource(resource: str) -> tuple[int, int, str] | None:
    """Extract (vid, pid, serial) from a PyVISA USB resource string.
    Returns ints for VID/PID so the caller compares against 0xCAFE / 0x4001
    regardless of whether pyvisa-py formatted the resource string as hex or
    decimal."""
    m = RESOURCE_PATTERN.match(resource)
    if not m:
        return None
    try:
        vid = int(m.group(1), 0)
        pid = int(m.group(2), 0)
    except ValueError:
        return None
    return vid, pid, m.group(3)


def read_serial_symlinks() -> dict[str, str]:
    """Return {serial: /dev/usbtmcN target} for everything under
    /dev/usbtmc-by-serial/."""
    by_serial = Path("/dev/usbtmc-by-serial")
    if not by_serial.is_dir():
        return {}
    result: dict[str, str] = {}
    for link in sorted(by_serial.iterdir()):
        try:
            target = link.resolve()
            result[link.name] = str(target)
        except OSError:
            continue
    return result


def read_nicknames() -> dict[str, str]:
    """Load the {serial: nickname} registry from tools/pico_nicknames.yaml."""
    if not NICKNAMES_FILE.exists():
        return {}
    try:
        with NICKNAMES_FILE.open() as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict):
            return {}
        return {str(k): str(v) for k, v in data.items()}
    except (yaml.YAMLError, OSError):
        return {}


def main() -> int:
    print("=" * 78)
    print("PMVB hot-plug-by-serial verification")
    print("=" * 78)

    rm = pyvisa.ResourceManager("@py")
    resources = list(rm.list_resources())

    pmvb_resources = []
    for r in resources:
        parsed = parse_resource(r)
        if parsed is None:
            continue
        vid, pid, serial = parsed
        if vid == PMVB_VID and pid == PMVB_PID:
            pmvb_resources.append((r, serial))

    if not pmvb_resources:
        print("\nNo PMVB USB-TMC instruments found via pyvisa-py.")
        print("Resources returned by ResourceManager.list_resources():")
        for r in resources:
            print(f"  {r}")
        return 1

    symlinks = read_serial_symlinks()
    nicknames = read_nicknames()

    print(f"\nFound {len(pmvb_resources)} PMVB USB-TMC instrument(s).\n")

    fmt = "{:<10}  {:<18}  {:<46}  {:<16}  {}"
    print(fmt.format("NICKNAME", "SERIAL (chip ID)", "PYVISA RESOURCE STRING", "DEV NODE", "*IDN? RESPONSE"))
    print("-" * 130)

    # Sort by nickname (which is more stable for human review than sorting by serial)
    def sort_key(entry: tuple[str, str]) -> tuple[str, str]:
        _, serial = entry
        nick = nicknames.get(serial, f"zzz-{serial}")  # unknowns sort last
        return (nick, serial)

    for resource, serial in sorted(pmvb_resources, key=sort_key):
        dev_node = symlinks.get(serial, "(no symlink)")
        nick = nicknames.get(serial, "(unnamed)")
        try:
            inst = rm.open_resource(resource)
            inst.timeout = 2000
            idn = inst.query("*IDN?").strip()
            inst.close()
        except Exception as exc:
            idn = f"ERROR: {exc}"
        print(fmt.format(nick, serial, resource, Path(dev_node).name, idn))

    print()
    print("To verify the hot-plug-by-serial architecture, run this script,")
    print("physically move one Pico to a different chassis hub port, and run")
    print("the script again. The SERIAL column and *IDN? RESPONSE column must")
    print("be identical across runs. The DEV NODE column may change if the")
    print("kernel renumbers /dev/usbtmcN; that is fine and expected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
