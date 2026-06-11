# Module 1E Parts Checklist

One-time prep before schematic capture. Goal: end up with a project-local
KiCad library that holds every custom symbol + footprint + 3D model the
Module 1E board needs. Generic passives (R, C, L, ferrite bead) and a few
common discretes come from KiCad's standard libraries and skip this list.

Source for the custom parts: Component Search Engine
(<https://componentsearchengine.com>), Library Loader output configured for
KiCad. Each bundle is a `.kicad_sym` + `.pretty/` footprint dir + `.step`.

## Project library layout

Create this directory tree under the KiCad project root once:

```
hardware/modules/1E/kicad/
  module_1e.kicad_pro
  module_1e.kicad_sch
  module_1e.kicad_pcb
  lib/
    PMVB_1E/
      symbols/         <- .kicad_sym files dropped here
      footprints.pretty/  <- .kicad_mod files dropped here
      3dmodels/        <- .step files dropped here
```

Add the library to the KiCad project (steps in `Module_1E_KiCad_Build_Guide.md`,
section "Library setup"). Use **project-local scope**, not global, so the
library travels with the repo.

---

## Custom parts to fetch from Component Search Engine

Five custom parts. For each: open the CSE URL, pick the KiCad output, run
Library Loader (or download the zip), unpack the three files into the
matching subfolder of `lib/PMVB_1E/`.

### 1. AD9742ARUZ - 12-bit 210 MSPS DAC, 28-lead TSSOP

- **Manufacturer:** Analog Devices
- **MPN:** `AD9742ARUZ`
- **CSE:** <https://componentsearchengine.com/part-view/AD9742ARUZ/Analog%20Devices>
- **Fetch:** symbol + footprint (TSSOP-28) + 3D STEP.
- **Notes:** Pinout is the verified one from D5 of the design package. Pin 23
  RESERVED must remain unconnected (do not stub to GND in the schematic).
  Pin 25 MODE is a data-format strap (DCOM for straight binary), not a
  parallel/serial select.

### 2. AD8056ARZ - dual 1400 V/us op-amp, SOIC-8

- **Manufacturer:** Analog Devices
- **MPN:** `AD8056ARZ`
- **CSE:** <https://componentsearchengine.com/part-view/AD8056ARZ/Analog%20Devices>
- **Fetch:** symbol + footprint (SOIC-8) + 3D STEP.
- **Notes:** Channel A is the live signal path. Channel B is unused: tie +INB
  to GND, tie -INB to OUTB to terminate it as a unity follower (per design
  package, OpAmp sheet).

### 3. Raspberry Pi Pico 2 W - 40-pin RP2350 module

- **Manufacturer:** Raspberry Pi
- **MPN:** `SC1633` (also listed as "Raspberry Pi Pico 2 W")
- **CSE:** <https://componentsearchengine.com/part-view/SC1633/Raspberry%20Pi>
  (if CSE doesn't have it, SnapEDA or the official Raspberry Pi KiCad
  library at <https://github.com/raspberrypi/hardware-design-guide> is the
  fallback)
- **Fetch:** symbol + footprint (40-pin, 2x20 castellated + THT, 2.54 mm
  pitch, 17.78 mm row pitch) + 3D STEP.
- **Notes:** On Module 1E, VBUS (pin 40) and VSYS (pin 39) are left
  unconnected on the PCB; the Pico is powered through its own micro-USB
  cable. 3V3_OUT (pin 36) feeds the DAC supply island.

### 4. Coto 9007-05-01 - SPST-NO reed relay, 5 V coil

- **Manufacturer:** Coto Technology
- **MPN:** `9007-05-01`
- **CSE:** <https://componentsearchengine.com/part-view/9007-05-01/Coto%20Technology>
- **Fetch:** symbol + footprint + 3D STEP.
- **Notes:** Three instances (K1, K2, K3) for the 50 ohm / high-Z / 10 kohm
  impedance switch. Verify the four pin positions (two coil, two contact)
  against the Coto datasheet after import.

### 5. Phoenix Contact MC 1,5/5-G-3,81 right-angle pluggable PCB header (1803303)

- **Manufacturer:** Phoenix Contact
- **MPN:** `1803303` (MC 1,5/5-G-3,81). RESOLVED per D6: the 5-position
  right-angle header (TME spec table "angled 90 deg", 5 pins, 8 A), now
  carrying +3.3 V on pin 5 in addition to +5 V / +12 V / -12 V / GND. Same
  "MC = right-angle" naming as the 4-pin; the straight variant is MCV.
- **Distributor:** Digi-Key 277-1209-ND, ~$1.84 single-qty, in stock. Mates
  with the harness plug MC 1,5/5-ST-3,81 (1803604, Digi-Key 277-1164-ND).
- **CSE:** <https://componentsearchengine.com/part-view/1803303/Phoenix%20Contact>
- **Fetch:** symbol + footprint (right-angle, 3.81 mm pitch, 5-pos) + 3D STEP.
- **Notes:** mounts on the rear edge beside the USB for rearward blind-mate on
  insertion. 8 A / 160 V. Start the schematic with the generic 5-position
  MC 1,5 symbol as a placeholder; lock the 1803303 footprint before layout.

### Optional: Coilcraft 0805 chip wirewound inductors (filter L)

- **Manufacturer:** Coilcraft
- **Values:** 0.22 uH (L1/L5, 4 off) and 0.68 uH (L3, 2 off) per the D2
  synthesis. Confirm the exact P/N for each value on the Coilcraft 0805
  family page or at Digi-Key.
- **Fetch:** optional. The generic KiCad `L_0805_2012Metric` footprint is
  physically compatible with the six filter inductors (L1 through L6). Fetch
  the Coilcraft models only if you want exact pad geometry + 3D + a tidier
  BOM export.

---

## Parts from KiCad standard libraries (no fetch needed)

For these, set the symbol field to the standard library reference and the
footprint field to the standard library footprint listed below. They install
with KiCad and need no CSE step.

| Quantity | Part | KiCad symbol | KiCad footprint |
|----------|------|--------------|-----------------|
| 12 | Resistor 0805 (1 % or 0.1 %) | `Device:R` | `Resistor_SMD:R_0805_2012Metric` |
| 9  | Capacitor 0603 (0.1 uF X7R) | `Device:C` | `Capacitor_SMD:C_0603_1608Metric` |
| 4  | Capacitor 0805 (10 uF X5R bulk) | `Device:C` | `Capacitor_SMD:C_0805_2012Metric` |
| 4  | Capacitor 0603 (820 pF C0G filter) | `Device:C` | `Capacitor_SMD:C_0603_1608Metric` |
| 4  | Inductor 0805 (0.22 uH filter L1/L5) | `Device:L` | `Inductor_SMD:L_0805_2012Metric` |
| 2  | Inductor 0805 (0.68 uH filter L3) | `Device:L` | `Inductor_SMD:L_0805_2012Metric` |
| 2  | Ferrite bead 0805 (~600 ohm @ 100 MHz) | `Device:FerriteBead` | `Inductor_SMD:L_0805_2012Metric` |
| 3  | 2N3904 NPN BJT (relay driver) | `Transistor_BJT:2N3904` | `Package_TO_SOT_THT:TO-92_Inline` |
| 3  | 1N4148 small-signal diode (flyback) | `Diode:1N4148` | `Diode_THT:D_DO-35_SOD27_P7.62mm_Horizontal` |
| 1  | 1x2 pin header (BNC wire-out, J2) | `Connector_Generic:Conn_01x02` | `Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical` |
| 1  | 1x3 pin header (trigger bus, J3) | `Connector_Generic:Conn_01x03` | `Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical` |

The BNC front-panel jack itself (Amphenol RF 031-5538) is panel-mounted and
wired off-board to J2; it does not get a PCB footprint.

---

## After fetch: verification

Once the five CSE bundles are in `lib/PMVB_1E/`, before placing them on the
schematic:

1. Open each symbol in the KiCad Symbol Editor. Compare pin numbers and
   names against the datasheet. Especially AD9742 (D5 in the design package
   lists every pin) and the Phoenix header pin order
   (1 = +5V, 2 = +12V, 3 = -12V, 4 = GND per the chassis harness).
2. Open each footprint in the KiCad Footprint Editor. Sanity-check the pad
   pitch against the datasheet mechanical drawing.
3. Confirm the 3D STEP loads in the 3D viewer when the footprint is placed
   on the PCB.

If any of those checks fail, fall back to drawing the symbol or footprint
by hand in KiCad rather than trusting a bad CSE bundle - the AD9742 in
particular is worth verifying since it has been wrong in our own design doc.
