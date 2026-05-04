# Phase 0: Orchestration Layer Setup

Step-by-step bring-up for the Raspberry Pi 5 16 GB orchestration head, the M.2 HAT+ with SSD, the powered USB hub and gigabit LAN switch, the Silverstone TX300 chassis PSU, and the Python software stack (PyVISA, pytest, InfluxDB 2.7, Grafana 10, MCP gateway scaffolding).

## Prerequisites

- Raspberry Pi 5 16 GB
- Raspberry Pi M.2 HAT+
- 512 GB NVMe SSD (M.2 2230 or 2242 form factor; M.2 2280 also works with the longer-board variant of the HAT+)
- 32 GB microSD card (boot, until SSD-boot is configured)
- Active cooler or heatsink for the Pi 5
- Powered USB hub (4 to 8 ports, 5 V at 2.4 A per port, 12 V barrel input preferred)
- Gigabit LAN switch (5 to 8 port, unmanaged is fine)
- Silverstone TX300 PSU (300 W TFX, 80+ Bronze)
- ATX 24-pin breakout board or terminal block
- USB-C power breakout boards (one per Pi to be powered from the +5 V rail)
- Cabling: USB-A to USB-C for hub uplink, Cat 6 patch cables, 5 V distribution wire (16 AWG recommended)

Verify the TX300 outputs by powering it on with a paperclip jumper between PS_ON# (green) and any GND (black) on the 24-pin connector. Measure +5 V and +12 V rails with a DMM before connecting to anything else.

## Step 1: Pi 5 OS install

1. Download Raspberry Pi Imager for your workstation and write **Raspberry Pi OS Bookworm 64-bit** to the 32 GB microSD card. Use the imager's pre-configured options to set:
   - Hostname: `pmvb-head` (or your preference)
   - Username: `bradw` (or your preference)
   - SSH enabled
   - Wi-Fi credentials if you want initial access via Wi-Fi
   - Locale and timezone
2. Insert the microSD into the Pi 5, attach the active cooler / heatsink, connect the Pi to wired Ethernet (preferred; LAN switch port), and apply 5 V power via the TX300 +5 V rail and a USB-C breakout.
3. From your workstation, `ssh bradw@pmvb-head.local` (or use the IP address).
4. Once logged in, run:
   ```bash
   sudo apt update && sudo apt full-upgrade -y
   sudo apt install -y git python3-venv python3-pip build-essential libusb-1.0-0-dev libgpiod-dev
   sudo reboot
   ```

## Step 2: M.2 HAT+ and SSD installation

1. Power the Pi 5 down. Disconnect 5 V.
2. Mount the M.2 HAT+ on the GPIO header per the [Raspberry Pi M.2 HAT+ install guide](https://www.raspberrypi.com/documentation/accessories/m2-hat-plus.html).
3. Install the NVMe SSD onto the HAT+ (check the screw post position matches the SSD form factor).
4. Reapply 5 V power. SSH back in.
5. Verify the SSD is detected:
   ```bash
   lsblk
   ```
   You should see an `nvme0n1` device. If not, add `dtparam=pciex1` to `/boot/firmware/config.txt` and reboot.
6. Format the SSD with ext4 and a single partition:
   ```bash
   sudo parted /dev/nvme0n1 -- mklabel gpt mkpart primary ext4 0% 100%
   sudo mkfs.ext4 /dev/nvme0n1p1
   ```
7. Create a mount point and persistent mount entry:
   ```bash
   sudo mkdir -p /mnt/pmvb-data
   echo "/dev/nvme0n1p1  /mnt/pmvb-data  ext4  defaults,noatime  0  2" | sudo tee -a /etc/fstab
   sudo mount -a
   sudo chown bradw:bradw /mnt/pmvb-data
   ```
8. Confirm the SSD is writable: `dd if=/dev/zero of=/mnt/pmvb-data/test.bin bs=1M count=100 oflag=direct` should report ~700 to 1500 MB/s on a typical SATA-class M.2 SSD; NVMe will be faster. Delete the test file.

(Booting from SSD instead of microSD is optional for v1.0; the microSD boots fine and the SSD serves as bulk data store. SSD boot configuration adds complexity and is not required.)

## Step 3: Python environment

```bash
cd ~
mkdir -p pmvb && cd pmvb
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install pyvisa pyvisa-py pyvisa-sim pytest numpy scipy matplotlib jinja2 influxdb-client pandas pyusb pyserial
echo "source ~/pmvb/venv/bin/activate" >> ~/.bashrc
```

Verify:
```bash
python -c "import pyvisa; print(pyvisa.__version__)"
python -c "import pytest; print(pytest.__version__)"
```

## Step 4: InfluxDB 2.7 installation

```bash
wget -qO- https://repos.influxdata.com/influxdata-archive_compat.key | sudo apt-key add -
echo "deb https://repos.influxdata.com/debian bookworm stable" | sudo tee /etc/apt/sources.list.d/influxdata.list
sudo apt update
sudo apt install -y influxdb2 influxdb2-cli
sudo systemctl enable --now influxdb
```

Configure on first run:
```bash
influx setup --username bradw --password '<choose>' --org pmvb --bucket measurements --retention 0 --force
```

Verify the InfluxDB web UI is accessible at `http://pmvb-head.local:8086/`.

Save the resulting API token (printed to stdout) somewhere safe; the Python InfluxDB client will need it.

## Step 5: Grafana 10 installation

```bash
sudo apt install -y software-properties-common
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
echo "deb https://packages.grafana.com/oss/deb stable main" | sudo tee /etc/apt/sources.list.d/grafana.list
sudo apt update
sudo apt install -y grafana
sudo systemctl enable --now grafana-server
```

Open `http://pmvb-head.local:3000/` in a browser. Default login `admin` / `admin`; change the password.

Add InfluxDB as a data source:
- Type: InfluxDB
- URL: `http://localhost:8086`
- Auth: Token (from step 4)
- Default bucket: `measurements`
- Organization: `pmvb`

## Step 6: MCP gateway scaffolding

The MCP gateway is a Python project that exposes per-module SCPI surfaces as MCP tools. The full implementation comes in Phase 1 alongside the first module; in Phase 0 we just create the project skeleton.

```bash
cd ~/pmvb
mkdir -p mcp-gateway/{servers,tools,tests}
cd mcp-gateway
pip install mcp
cat > main.py <<'EOF'
"""PMVB MCP Gateway entry point. Phase 0 stub."""
from mcp.server import FastMCP

app = FastMCP("pmvb")

@app.tool()
def health_check() -> str:
    """Return a heartbeat from the PMVB gateway."""
    return "pmvb gateway alive"

if __name__ == "__main__":
    app.run()
EOF
python main.py &
```

Verify the gateway starts without error. Stop with `kill %1`.

## Step 7: Build the chassis power distribution

The chassis power system involves AC mains-voltage components (TX300 PSU, IEC inlet, EMI filter network) that demand careful design and assembly. The full design, mechanical instructions, BOM, bring-up procedure, and safety protocols live in a dedicated document:

**[Chassis Power Distribution Design Document](../chassis/Chassis_Power_Distribution_Design.md)**

That document covers the split-enclosure topology (sealed AC compartment containing the TX300 + lid interlock; open DC distribution chassis with the ATX breakout, fuses, USB-C breakouts, and indicators), step-by-step mechanical fabrication for novice builders, a complete Mouser/Digi-Key BOM, and the safety procedures for opening the AC compartment after capacitor discharge.

Verify the bring-up checklist in section 7 of the chassis power design document passes before proceeding to step 8.

## Step 8: Verification

A representative simulator-backed test should pass end-to-end. Create `~/pmvb/test_phase0_smoke.py`:

```python
import pyvisa
import pytest

def test_pyvisa_simulator_smoke():
    """Smoke test: open a simulated instrument and round-trip an *IDN? query."""
    rm = pyvisa.ResourceManager('@sim')
    inst = rm.open_resource('ASRL1::INSTR')
    response = inst.query('*IDN?')
    assert 'INSTR' in response
    inst.close()

def test_influxdb_writable():
    """Smoke test: write a point to InfluxDB and read it back."""
    from influxdb_client import InfluxDBClient, Point
    from influxdb_client.client.write_api import SYNCHRONOUS
    client = InfluxDBClient(url='http://localhost:8086', token='<paste token>', org='pmvb')
    write_api = client.write_api(write_options=SYNCHRONOUS)
    write_api.write(bucket='measurements', record=Point('phase0_smoke').field('value', 1.0))
    query_api = client.query_api()
    result = query_api.query('from(bucket: "measurements") |> range(start: -1m)')
    assert any(r for r in result), 'No record returned from InfluxDB'
    client.close()
```

Run:
```bash
pytest test_phase0_smoke.py -v
```

Both tests should pass. If they do, Phase 0 is complete and you have:

- A Pi 5 16 GB orchestration head with M.2 SSD attached and ext4-mounted at `/mnt/pmvb-data`
- Python virtual env with PyVISA, PyVISA-py, PyVISA-sim, pytest, InfluxDB client, NumPy, SciPy, Matplotlib, Jinja2 installed
- InfluxDB 2.7 running with `pmvb` org and `measurements` bucket
- Grafana 10 running with InfluxDB as a data source
- MCP gateway stub running and reachable
- Powered USB hub and LAN switch wired to the chassis
- TX300 PSU supplying chassis 5 V and 12 V rails
- A passing smoke test that exercises PyVISA simulation and InfluxDB write/read

You are ready to start Phase 1 (Module 1E AWG bring-up).

## Troubleshooting

- **Pi 5 won't boot from SSD:** confirm `dtparam=pciex1` is in `/boot/firmware/config.txt`. Confirm the SSD is detected with `lsblk`. SSD boot is not required for Phase 0; microSD boot is fine.
- **InfluxDB web UI returns 404:** wait 30 seconds after `systemctl enable --now influxdb` for first-time setup; reload the page.
- **Grafana cannot reach InfluxDB:** verify the URL is `http://localhost:8086` (not `https`), the token is pasted correctly without trailing whitespace, and the organization name matches exactly (`pmvb`, not `PMVB`).
- **MCP gateway fails to start:** check the Python venv is activated and `mcp` package version is 1.0+.
- **TX300 does not turn on:** verify PS_ON# is tied to GND. Some PSUs also require a minimum load on the +5 V rail to start; if so, add a 10 Ω 5 W power resistor between +5 V and GND.
- **Pi 5 brownouts under load:** check the +5 V rail at the Pi's USB-C input under load; should be 4.9 V to 5.1 V. If it sags below 4.85 V, the wire is too long or thin; use 16 AWG or larger.
