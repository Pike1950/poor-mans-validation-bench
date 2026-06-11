# Module 1E KiCad Build Guide

Step-by-step setup for the KiCad project, then the hierarchical sheet
specification you wire from. Targets KiCad 9 (KiCad 8 paths are identical for
all the menus used here). Pre-requisite: the five custom parts from
`Module_1E_Parts_Checklist.md` have been fetched and dropped into
`hardware/modules/1E/kicad/lib/PMVB_1E/`.

## 1. Create the project

1. **File - New Project**, set the project name to `module_1e` and the
   location to `hardware/modules/1E/kicad/`. KiCad creates
   `module_1e.kicad_pro`, `module_1e.kicad_sch`, and `module_1e.kicad_pcb`.
2. Open `module_1e.kicad_sch` (root). **File - Page Settings**, fill in:
   - **Title:** Module 1E - Function Generator / AWG
   - **Company:** PMVB
   - **Rev:** v0.1
   - **Date:** today's date
   - **Comment 1:** SDD section 7.5.5; design package
     `Module_1E_PCB_Design_Package.md`
   - **Comment 2:** designer Brad Ward
3. Save.

## 2. Library setup

In eeschema: **Preferences - Manage Symbol Libraries**. Switch to the
**Project Specific Libraries** tab and add:

| Nickname | Library Path |
|----------|--------------|
| PMVB_1E | `${KIPRJMOD}/lib/PMVB_1E/symbols/pmvb_1e.kicad_sym` |

Adjust the filename if the CSE Library Loader produced a different one;
combine multiple per-part `.kicad_sym` files into a single project library
or add each individually. Project-specific scope is correct here so the
library moves with the repo, not the workstation.

In pcbnew: **Preferences - Manage Footprint Libraries**, same idea:

| Nickname | Library Path |
|----------|--------------|
| PMVB_1E | `${KIPRJMOD}/lib/PMVB_1E/footprints.pretty` |

3D models from CSE land in `lib/PMVB_1E/3dmodels/`; the footprints' 3D
references should already point there if the Library Loader configured paths
correctly.

## 3. Import the board outline

In pcbnew, on a fresh empty board:

1. **File - Import - Graphics**, pick
   `../../library/module_pcb_outline.dxf`.
2. **Layer:** Edge.Cuts. **Placement:** at origin, scale 1:1.
3. Click OK. The 120 x 62 mm outline, the four M2.5 mounting-hole circles,
   and the placement-zone annotations come in. Move the
   `User.Comments`/`User.Drawings` items to whichever layer you find easiest
   to ignore during routing.
4. Save. Re-import any time the outline generator is regenerated.

## 4. Netclasses and DRC

In pcbnew: **File - Board Setup - Net Classes**. Set defaults and add the
classes from section 8 of the design package:

| Netclass | Track width | Clearance | Notes |
|----------|-------------|-----------|-------|
| Default | 0.25 mm | 0.2 mm | everything not otherwise assigned |
| Power_12V | 0.8 mm | 0.25 mm | +12V, -12V (op-amp rails) |
| Power_5V | 0.6 mm | 0.2 mm | +5V (relay coils) |
| Power_3V3 | 0.5 mm | 0.2 mm | +3V3, AVDD, DVDD |
| Analog | 0.3 mm | 0.25 mm | IOUTA, IOUTB, FILT_A, FILT_B, OPAMP_IN+/-, OPAMP_OUT, BNC_CENTER |
| DataBus | 0.25 mm | 0.2 mm | DB0..DB11, DAC_CLK |

Assign nets to classes after the schematic is captured and netlist imported
(eeschema **Tools - Edit Symbol Fields** or pcbnew **Net Inspector**).

Under **Board Setup - Design Rules - Constraints**: minimum clearance
0.20 mm, minimum track width 0.20 mm. Relax if your chosen fab needs more.

## 5. Create the hierarchical sheets

On the root sheet `module_1e.kicad_sch`, drop five hierarchical sheet
symbols: **Place - Add Hierarchical Sheet** (shortcut `S`), one per
functional block. Filenames and recommended sheet sizes:

| Sheet symbol | Filename | Approx size |
|--------------|----------|-------------|
| Pico | `Pico.kicad_sch` | medium |
| DAC | `DAC.kicad_sch` | large (most components) |
| OpAmp | `OpAmp.kicad_sch` | medium |
| OutputSwitch | `OutputSwitch.kicad_sch` | medium |
| Trigger | `Trigger.kicad_sch` | small |

Double-click each sheet symbol to descend into it. Inside each sub-sheet,
place hierarchical labels (**Place - Add Hierarchical Label**, shortcut `H`)
that match the per-sheet contracts in section 7 below. Back on the root,
those labels appear as sheet pins on the sheet symbol; wire them to the
inter-sheet nets and to the Phoenix-driven power flags.

Use **Place - Add Power Symbol** for `+5V`, `+12V`, `-12V`, `+3V3`, `GND`
inside every sheet that uses them. Power symbols are auto-global, no
hierarchical-label declaration needed for them.

---

## 6. Root sheet contents

The root sheet `module_1e.kicad_sch` carries the project metadata, the
power input, and the sheet symbols. Concrete contents:

- **J1** Phoenix MC 1,5/4 right-angle header (placeholder symbol from
  `Connector_Phoenix_MC` until D6 P/N is fetched).
  - Pin 1 -> `+5V` power flag.
  - Pin 2 -> `+12V` power flag.
  - Pin 3 -> `-12V` power flag.
  - Pin 4 -> `GND` power flag.
- Five hierarchical sheet symbols (Pico, DAC, OpAmp, OutputSwitch, Trigger).
- No other components. All sub-sheet signals enter and exit via sheet pins.

---

## 7. Sub-sheet specifications

For each sheet: the symbols that live on it, the hierarchical labels it
imports and exports (direction is from the sheet's perspective), the power
nets it uses, and any wiring notes you have to honor.

### 7.1 Pico (`Pico.kicad_sch`)

- **Symbols:** U1 (Raspberry Pi Pico 2 W); C15 0.1 uF X7R 0603 close to
  Pico 3V3_OUT pin as local bypass.
- **Hierarchical labels OUT** (Pico drives them):
  `DB0`, `DB1`, ..., `DB11`, `DAC_CLK`,
  `RELAY_50`, `RELAY_HIZ`, `RELAY_10K`,
  `SYNC_OUT`, `+3V3` (passive).
- **Hierarchical labels IN** (Pico receives):
  `TRIG_IN`.
- **Power:** `GND` on all eight Pico GND pins (3, 8, 13, 18, 23, 28, 33, 38).
- **Notes:**
  - VBUS (pin 40), VSYS (pin 39), 3V3_EN (pin 37), ADC_VREF (pin 35), RUN
    (pin 30), and GP18..GP28 unused on this module - leave unconnected or
    place "no-connect" flags.
  - Pin mapping for signals (from the design doc section 4):
    GP0..GP11 = DB0..DB11, GP12 = DAC_CLK, GP13 = RELAY_50,
    GP14 = RELAY_HIZ, GP15 = RELAY_10K, GP16 = SYNC_OUT, GP17 = TRIG_IN.
  - Pico is USB-powered; the module PCB does not feed it. Only the
    Pico's `3V3_OUT` (pin 36) exits the Pico sheet to feed the DAC supply
    island.

### 7.2 DAC (`DAC.kicad_sch`)

- **Symbols:** U2 (AD9742); FB1, FB2 (ferrite beads to AVDD, DVDD);
  R1 (1.91 k 0.1 % FSADJ); R2, R3 (25 ohm 0.1 % IOUTA/IOUTB terminations);
  C1 (0.1 uF REFIO); C6, C7 (0.1 uF AVDD, DVDD bypass);
  C8 (10 uF X5R 0805 bulk at +3V3 entry);
  C16, C17 (second 0.1 uF AVDD, DVDD bypass);
  L1, L3 (0.22 uH filter A outer series), L2 (0.68 uH filter A mid series); L4, L6 (0.22 uH filter B outer series), L5 (0.68 uH filter B mid series);
  C2, C3 (820 pF C0G filter A shunt); C4, C5 (820 pF C0G filter B shunt).
- **Hierarchical labels IN:** `DB0`..`DB11`, `DAC_CLK`, `+3V3` (passive).
- **Hierarchical labels OUT:** `FILT_A`, `FILT_B`.
- **Power:** `GND`, `+3V3` -> local FB1/FB2 -> `AVDD`/`DVDD` (local nets,
  do not export).
- **Notes:**
  - **Pin 23 RESERVED:** leave unconnected. Per the AD9742 datasheet
    Rev. C, do not stub to GND or to a supply.
  - **Pin 25 MODE -> GND (= DCOM):** selects straight-binary input format.
    Firmware must emit straight-binary sample codes (D5).
  - **Pin 15 SLEEP -> GND:** keeps the DAC out of power-down. Has an
    internal pull-down; tying low is explicit.
  - **Pin 16 REFLO -> GND:** uses the internal 1.2 V reference.
  - **Reconstruction filter (D2):** two independent 5th-order L-C-L-C-L
    ladders, one per leg. Topology and values are placeholders pending a
    real filter-synthesis pass; the wiring contract is fixed.
    - Leg A: IOUTA -> L1 -> n1A -> C2 to GND, L2 -> n2A -> C3 to GND,
      L3 -> FILT_A.
    - Leg B: IOUTB -> L4 -> n1B -> C4 to GND, L5 -> n2B -> C5 to GND,
      L6 -> FILT_B.
  - **25 ohm terminations:** R2 from IOUTA to GND, R3 from IOUTB to GND;
    place them physically adjacent to the DAC pins.

### 7.3 OpAmp (`OpAmp.kicad_sch`)

- **Symbols:** U3 (AD8056); R4, R5 (1 k 1 % input resistors);
  R6 (20 k 1 % feedback); R7 (20 k 1 % balance);
  C9, C10 (0.1 uF V+, V- bypass); C11, C12 (10 uF X5R bulk on each rail).
- **Hierarchical labels IN:** `FILT_A`, `FILT_B`.
- **Hierarchical labels OUT:** `OPAMP_OUT`.
- **Power:** `+12V`, `-12V`, `GND`.
- **Notes:**
  - **Channel A is the live path.** Standard difference-amp wiring:
    FILT_A through R4 (1 k) to +INA (pin 3); R7 (20 k) from +INA to GND;
    FILT_B through R5 (1 k) to -INA (pin 2); R6 (20 k) feedback from -INA
    to OUTA (pin 1). Differential gain = 20 (D1).
  - **Channel B is unused.** Terminate cleanly:
    +INB (pin 5) -> GND, -INB (pin 6) -> OUTB (pin 7).
    Leaving high-speed op-amp inputs floating is the usual oscillation trap.
  - **V+ pin 8 -> +12V; V- pin 4 -> -12V.**

### 7.4 OutputSwitch (`OutputSwitch.kicad_sch`)

- **Symbols:** K1, K2, K3 (Coto 9007-05-01); Q1, Q2, Q3 (2N3904);
  D1, D2, D3 (1N4148); R8 (50 ohm 1 %), R10 (10 k 1 %) series
  (K2's branch has no series resistor; R9 is intentionally not used);
  R11, R12, R13 (1 k base resistors);
  J2 (1x2 pin header, BNC wire-out); C13 (0.1 uF +5V bypass);
  C14 (10 uF X5R +5V bulk).
- **Hierarchical labels IN:** `OPAMP_OUT`, `RELAY_50`, `RELAY_HIZ`,
  `RELAY_10K`.
- **Hierarchical labels OUT:** none. The output reaches the panel BNC via
  J2, which is a wired connection off-board.
- **Power:** `+5V`, `GND`.
- **Notes:**
  - **Three relay branches with identical coil/drive sides; contact side
    differs by mode.** Coil and drive are the same for K1, K2, K3:
    - Coil side: `+5V` -> COIL1; COIL2 -> Q.collector. D anode at COIL2,
      D cathode at `+5V` (flyback across the coil).
    - Drive side: Q.emitter -> GND; Q.base -> base resistor (1 k) ->
      hierarchical label `RELAY_50` / `RELAY_HIZ` / `RELAY_10K`.
    - Contact side, per branch:
      - K1 (50 ohm back-term): OPAMP_OUT -> K1.SW1; K1.SW2 -> R8 (50 ohm)
        -> J2 pin 1.
      - K2 (high-Z source): OPAMP_OUT -> K2.SW1; K2.SW2 -> J2 pin 1
        **directly, no series resistor**.
      - K3 (10 kohm bias): OPAMP_OUT -> K3.SW1; K3.SW2 -> R10 (10 k)
        -> J2 pin 1.
  - **J2 pin 2 -> GND.** This is the BNC shield wire-out.
  - **Firmware enforces one relay energized at a time.** No hardware
    interlock; trust the Pico SCPI parser.

### 7.5 Trigger (`Trigger.kicad_sch`)

- **Symbols:** J3 (1x3 pin header).
- **Hierarchical labels IN:** `SYNC_OUT` (from Pico, to drive J3 pin 1).
- **Hierarchical labels OUT:** `TRIG_IN` (J3 pin 3 back to Pico).
- **Power:** `GND` (J3 pin 2).
- **Notes:** Chassis trigger-bus connector standard is not yet defined.
  This is a placeholder 3-pin 0.1 inch header. Will likely need to be
  re-locked across modules (like the Phoenix) once the bus is specified.

---

## 8. Wire-up and finish

1. Place power flags inside each sheet for the rails it uses.
2. Place hierarchical labels per the contracts in section 7. Inside a
   sheet, every label with the same name is the same net; on the root,
   they become sheet pins.
3. **ERC** in eeschema (`Inspect - Electrical Rules Checker`). Expect
   warnings about unconnected Pico GPIO pins (place "no-connect" flags on
   intentionally unused ones). Real errors should be zero.
4. **Annotate** (`Tools - Annotate Schematic`).
5. **Update PCB from Schematic** (`Tools - Update PCB from Schematic`).
   The 53 components from the BOM should land on the board.
6. Assign netclasses to nets in pcbnew (`Net Inspector`).
7. Place per the floorplan (`library/module_pcb_floorplan.png`), route,
   pour the L2 ground plane and the L3 power pours per section 7 of the
   design package.
8. **DRC** in pcbnew, fix until clean.

## 9. Verification checklist before fab

- Title block populated on every sheet.
- All five CSE-fetched symbols have manufacturer P/N in the value field.
- AD9742 pin 23 left floating (no track, no GND stub).
- AD9742 pin 25 (MODE) hard-tied to GND.
- AD8056 channel B inputs terminated (+INB to GND, -INB to OUTB).
- Phoenix header pin order matches chassis harness (1=+5V, 2=+12V,
  3=-12V, 4=GND).
- Mounting hole positions match the v10 module-body STL (co-design check
  with the chassis fabrication tooling).
- ERC clean, DRC clean.
- 3D viewer shows no collisions between Pico USB connector and the rear
  PCB edge, or between the Phoenix header and the top-rear M2.5 mounting
  hardware.

When all of section 9 passes, the board is ready for fab quote (JLCPCB,
Oshpark, PCBWay, etc.).
