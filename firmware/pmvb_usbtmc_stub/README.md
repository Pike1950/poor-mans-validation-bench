# PMVB USB-TMC Stub Firmware

Phase 0 throwaway probe firmware for the Pico 2 W. Makes a bare Pico enumerate as a USB-TMC instrument with a chip-ID-derived serial number, so the bench can validate the [SDD §10.1 hot-plug-by-serial architecture](../../docs/system-design/System_Design_Document.html) without any module front-end attached.

This firmware is **not** the per-module SCPI parser. Each instrument module ships its own firmware in its own Phase, generated mechanically from the module's `commands.yaml` schema.

## What it does

Enumerates as a USB-TMC class device (USB488 subclass) with:

- **VID / PID:** `0xCafe` / `0x4001` (TinyUSB community-reserved test VID; PMVB-specific PID)
- **Manufacturer string:** `PMVB`
- **Product string:** `PMVB Pico 2 W USB-TMC Stub`
- **iSerialNumber:** the Pico 2 W's unique 64-bit chip ID, formatted as 16 hex chars

Supported SCPI commands:

| Command | Behavior |
|---------|----------|
| `*IDN?` | Returns `PMVB,Pico 2 W,<chip_id_hex>,1.0.0\n` |
| `*RST` | Silent acknowledgment |
| `*CLS` | Silent acknowledgment (clear status) |
| `*OPC?` | Returns `1\n` |
| `:SYST:BOOTSEL` | PMVB extension: reboots into BOOTSEL mode for hot re-flashing without the physical button |

Anything else is silently dropped.

## Build

Requires the Pico SDK installed at `/opt/pico-sdk` with `PICO_SDK_PATH` exported, and the arm-none-eabi toolchain (`gcc-arm-none-eabi`, `libnewlib-arm-none-eabi`, `libstdc++-arm-none-eabi-newlib`). See [`docs/setup/Phase_0_Orchestration_Setup.html`](../../docs/setup/Phase_0_Orchestration_Setup.html) section G.

From the repo root on the orchestration host:

```bash
cd firmware/pmvb_usbtmc_stub
mkdir -p build && cd build
cmake .. -G Ninja -DPICO_BOARD=pico2_w
ninja
```

Output: `build/pmvb_usbtmc_stub.uf2` (the firmware image to drag-drop onto each Pico in BOOTSEL mode).

## Flash

1. Hold the BOOTSEL button on the Pico and plug it into the chassis hub (or apply power while holding BOOTSEL).
2. The Pico enumerates as a mass-storage volume named `RP2350` at e.g. `/media/<user>/RP2350`.
3. Copy `pmvb_usbtmc_stub.uf2` onto that volume:
   ```bash
   cp build/pmvb_usbtmc_stub.uf2 /media/<user>/RP2350/
   ```
4. The Pico auto-reboots and re-enumerates as a USB-TMC instrument.

After the first flash, subsequent re-flashes can use the `:SYST:BOOTSEL` SCPI command instead of the physical button:

```python
import pyvisa
rm = pyvisa.ResourceManager('@py')
inst = rm.open_resource('USB::0xCafe::0x4001::<chip_id>::INSTR')
inst.write(':SYST:BOOTSEL')   # Pico reboots into BOOTSEL; copy new .uf2; done
```

## Verify enumeration

After flashing, on the orchestration host:

```bash
lsusb -v 2>/dev/null | grep -A2 "iSerial"
```

Each flashed Pico should show its own 16-hex-char serial. PyVISA resource discovery will key off this field; hot-plugging a Pico across different chassis hub ports preserves its logical identity.

## Files

- `CMakeLists.txt` - Pico SDK CMake build
- `tusb_config.h` - TinyUSB configuration (USB-TMC + USB488 subclass enabled)
- `usb_descriptors.c` - Device, configuration, and string descriptors
- `usbtmc_handlers.c` - USB-TMC class callbacks + SCPI command dispatch
- `main.c` - TinyUSB init and main loop
