# Chassis Architecture and Power Distribution Design Document

## v1.0 (May 2026)

Companion to the [PMVB System Design Document section 11](../system-design/System_Design_Document.html#power-architecture). This document defines the mechanical and electrical design of the PMVB chassis: an open-frame acrylic blade enclosure (laser-cut from SendCutSend) housing the Silverstone SST-TX300 PSU as an analog-rail backbone, a GeeekPi D-1188 ATX breakout, a Sabrent HB-BU10 USB 3.0 hub as the chassis-internal USB-TMC backplane, and 14 module slots arranged as parallel vertical blades.

**Architecture in one paragraph.** The chassis is the integrated mechanical-and-power subsystem that holds the entire bench instrument fabric in a single ~16.5" × 9.4" × 3.5" enclosure. The TX300 PSU supplies analog ±12 V and +5 V *only* to instrument modules that need clean bipolar or higher-current rails (Module 1B VMU, Module 1D SMU Lite, Module 1E AWG, Module 1F HV diff probe, Module 1G current probe, Module 1H DMM, Module 2B precision DAQ, Module 2E digitizer); it does **not** power the Pi 5, the USB hub, or chassis-side Picos, each of which has its own external supply (Pi 5 uses its 27 W USB-C charger, the Sabrent hub runs from its own wall brick, and module Picos draw 5 V from USB downstream power). Modules are vertical blades (16.5 × 125 × 86 mm body) that slot into the chassis at 22.5 mm pitch, plug into a 4-rail back-wall power harness via Phoenix Contact MC 1,5/4 connectors, and present USB to the Sabrent hub for SCPI command and measurement-data transport.

<img src="../figures/chassis/photos/pmvb_chassis_populated.png" alt="" style="max-width: 900px; width: 100%; display: block; margin: 1.5rem auto;">

*Figure 1: PMVB chassis fully populated with 14 module blades. The TX300 PSU sits at the left end with its IEC C14 inlet exposed through the front-panel cutout. The vent grid on the chassis top exhausts hot air from the TX300's internal fan. Module faceplate cutouts in the front panel are deferred until module-specific I/O designs converge.*

---

## Table of Contents

- [1. Design Philosophy](#design-philosophy)
- [2. Functional Block Diagram](#functional-block-diagram)
- [3. Mechanical Architecture](#mechanical-architecture)
  - [3.1 Outer Envelope and Form Factor](#outer-envelope-and-form-factor)
  - [3.2 Acrylic Frame and Cuts](#acrylic-frame-and-cuts)
  - [3.3 TX300 PSU Mounting](#tx300-psu-mounting)
  - [3.4 GeeekPi D-1188 Mounting](#geeekpi-d-1188-mounting)
  - [3.5 Sabrent HB-BU10 USB Hub Mounting](#sabrent-hb-bu10-usb-hub-mounting)
  - [3.6 Module Slot Geometry and Form Factor](#module-slot-geometry-and-form-factor)
  - [3.7 Front-Panel Strip and Module Faceplate Region](#front-panel-strip-and-module-faceplate-region)
  - [3.8 TX300 Fan Ventilation](#tx300-fan-ventilation)
- [4. Electrical Architecture](#electrical-architecture)
  - [4.1 Rail Sources from the TX300](#rail-sources-from-the-tx300)
  - [4.2 GeeekPi D-1188 ATX Breakout](#geeekpi-d-1188-atx-breakout)
  - [4.3 Per-Rail Fuse Panel](#per-rail-fuse-panel)
  - [4.4 4-Wire Back-Wall Harness](#4-wire-back-wall-harness)
  - [4.5 Per-Module Phoenix Pigtail](#per-module-phoenix-pigtail)
  - [4.6 Banana-Jack Diagnostic Test Points](#banana-jack-diagnostic-test-points)
  - [4.7 Front-Panel Indicator LEDs](#front-panel-indicator-leds)
- [5. USB-TMC Backplane](#usb-tmc-backplane)
- [6. Bill of Materials](#bill-of-materials)
- [7. Bring-Up Procedure](#bring-up-procedure)
- [8. Safety Procedures](#safety-procedures)
- [9. Future Enhancements](#future-enhancements)
- [10. References](#references)

---

## 1. Design Philosophy

The chassis is an integrated single-enclosure subsystem that consolidates the analog supply backbone, the USB-TMC backplane, and the module bay into one bench-friendly footprint. Three architectural decisions drive the design:

1. **The TX300 PSU is the *analog-rail backbone*, not the chassis-wide power source.** Its ±12 V and +5 V outputs feed only the instrument modules that need clean bipolar or higher-current rails. Bench infrastructure (Pi 5, USB hub, the Picos at the chassis level) runs from external supplies. This decoupling means the chassis interior is exclusively SELV (safety extra low voltage) once mains is contained inside the TX300's certified case, and the chassis itself does not need to be a safety boundary.

2. **Modules are vertical blades in a card-cage-style bay.** Each module is a 17 × 125 × 80 mm PCB that slides into a slot at 22.5 mm pitch, plugs into a back-wall power harness, connects USB to the Sabrent hub, and presents its module-specific I/O at the front face. This pattern follows the spirit of NI PXI / Eurocard subracks at hobbyist scale, with a custom laser-cut acrylic frame replacing the cost-prohibitive professional subrack hardware.

3. **The chassis is open-frame acrylic.** The TX300's certified IEC inlet handles AC safety; the acrylic frame is purely mechanical containment and does not need to be earth-bonded. Open construction makes the architecture self-documenting (you can see what's inside), simplifies cooling (TX300 fan exhausts through a 6 × 12 grid of vent holes in the chassis top), and keeps fabrication cost under $100 for the entire enclosure.

---

## 2. Functional Block Diagram

<img src="../figures/chassis/chassis_block_diagram.svg" alt="" style="max-width: 800px; width: 100%; display: block; margin: 1.5rem auto;">

*Figure 7: Chassis architecture as two parallel fabrics. The analog power fabric (right column, red edges) runs from the TX300 IEC inlet through the TX300 PSU, GeeekPi D-1188 ATX breakout, per-rail fuse panel, and 4-wire back-wall harness to the module bay. The USB-TMC control fabric (left and center columns, blue edges) runs from the Raspberry Pi 5 (external, not in chassis) over USB 3.0 to the Sabrent HB-BU10 USB hub (chassis backplane), then fans out as USB-A to all 13 populated module slots. Three external supplies (Pi 5 charger and Sabrent hub brick shown dashed; TX300 IEC inlet shown solid because it terminates inside the chassis) feed the three top-level subsystems independently. Front-panel diagnostic strip (banana jacks + LEDs) is documented separately in §3.7 and §4.6/4.7.*

---

## 3. Mechanical Architecture

### 3.1 Outer Envelope and Form Factor

The chassis is a **420 × 238 × 90 mm** rectangular enclosure (~16.5" × 9.4" × 3.5"). Material is 4 mm clear acrylic throughout, laser-cut from SendCutSend with the parts list described in [section 3.2](#acrylic-frame-and-cuts). The bench footprint is comparable to a 1U–2U rack-mount instrument; the low profile (3.5" tall) keeps the entire fabric at one bench level rather than stacking towers.

<img src="../figures/chassis/photos/pmvb_chassis_empty.png" alt="" style="max-width: 900px; width: 100%; display: block; margin: 1.5rem auto;">

*Figure 2: Empty chassis viewed from front-3/4. The dark rectangle on the left of the front panel is the TX300 IEC inlet cutout. The 14 module slot bays are visible across the lower front, each with a card-guide groove cut into the floor for the module's bottom rail lip. The vent grid on the chassis top (over the TX300 footprint) exhausts hot air from the TX300's internal fan.*

The Tinkercad reference design (committed 2026-05-07) defines the exact internal coordinate system used throughout this document: X is the long axis (chassis length, slot-pitch direction), Y is the depth axis (front to back), Z is the vertical axis (floor to ceiling). The origin is at the chassis center on the floor, with X spanning −210 to +210 (length 420), Y spanning −116 to +120 (depth 236, the −116 face is the front), and Z spanning 0 to 90.

### 3.2 Acrylic Frame and Cuts

The frame is six laser-cut pieces of 4 mm clear acrylic plus internal card guides. Cuts are produced from a single DXF file uploaded to SendCutSend.

| Piece | Dimensions (mm) | Cuts/features |
|---|---|---|
| Floor plate | 420 × 238 | 4 corner mounting holes; 14 lip-engagement grooves at 22.5 mm pitch (each ~1 mm wide × 3 mm deep × 125 mm long, running front-to-back along the Y axis), accepting the bottom rail lip on each module body |
| Top plate | 420 × 238 | 4 corner mounting holes; matching 14 lip-engagement grooves at 22.5 mm pitch on the underside (mirror of the floor pattern); ~6 × 12 grid of 5–6 mm round vent holes positioned over the TX300 footprint (X = −230 to −150, Y = −110 to +20) |
| Left side | 90 × 238 | 4 corner mounting holes; optional venting slots if convection alone is insufficient |
| Right side | 90 × 238 | 4 corner mounting holes |
| Back | 420 × 90 | Cutouts for: Sabrent USB hub uplink port and DC barrel jack at the hub's X position; 4-wire harness pass-through if the harness is fed from outside the back wall |
| Front | 420 × 90 | TX300 IEC C14 inlet cutout (35 × 28 mm rectangle at left end, X ≈ −230 to −195); 4 × 6 mm holes for Pomona banana jacks at the front-panel strip; 3 × 6 mm holes for VCC LED indicators; **14 module-faceplate cutouts (deferred — see note below)** |

**Note on front-panel module cutouts:** the per-module faceplate cutouts in the front panel are intentionally deferred. Each module's faceplate cutout shape and position depends on that module's specific I/O layout (which connectors at which vertical positions on the 17 mm wide × 80 mm tall faceplate area), and that I/O layout is part of each module's design doc. The chassis front panel will be cut after enough modules have committed faceplate I/O specs to make the cuts non-iterative. The chassis is designed so the front panel is the *only* piece that needs re-cutting when faceplate decisions change; all other pieces remain stable.

Frame is assembled with **M3 corner standoffs** (12 mm tall for the spacing between top and floor plates plus the 90 mm side panels, and the side panels mount via M3 screws into the standoff threads). Total hardware: 16 corner standoffs, ~32 M3 × 6 mm screws, 4 M3 × 12 mm screws for component mounting (TX300, GeeekPi, USB hub).

The lip-engagement grooves in the floor and ceiling form the card guides for module insertion. Each module's body has a 1 mm × 3 mm rail lip running along the bottom-right and top-right corners (the right side of each module body); these lips slide into the matching chassis grooves as the module is inserted from the front. The grooves stop short of the front edge of the floor/ceiling plate by ~3 mm so the module front-panel feature plays cleanly through the (eventually-cut) front-panel module-faceplate opening.

### 3.3 TX300 PSU Mounting

The TX300 sits at the **left end of the chassis floor**, X = −230 to −144 (86 mm wide), Y = −118 to +60 (178 mm deep), Z = 6 to 72 (66 mm tall). Orientation: the TX300's IEC C14 inlet faces the chassis **front** (Y = −118 face) so the AC cord plugs in from the front; the TX300's 24-pin ATX output cable exits from the chassis **back** (Y = +60 face) and terminates at the GeeekPi D-1188 mounted on top of the rear portion of the TX300; the 80 mm fan exhausts upward through the top vent grille (Z = 72 top face). The PSU mounts to the floor plate via four M3 standoffs threaded into the TX300's existing M3 mounting holes (standard TFX form factor pattern).

<img src="../figures/chassis/photos/PMVBChassis4.png" alt="" style="max-width: 550px; width: 100%; display: block; margin: 1.5rem auto;">

*Figure 3: Cutaway view of the TX300 PSU (gray) and the GeeekPi D-1188 ATX breakout (red, on top of the TX300's rear ~20 mm) inside the chassis. The TX300's full top surface from the front edge to ~20 mm forward of the rear is left exposed for the fan to exhaust upward through the chassis top vent grid.*

Internal AC routing is contained entirely within the TX300's certified enclosure; no external mains wiring exits the PSU body. The IEC inlet is exposed through a 35 × 28 mm rectangular cutout in the **front** panel at the TX300 IEC inlet position (occupying the leftmost ~90 mm of the front-panel face, separate from the diagnostic strip and module faceplate region).

### 3.4 GeeekPi D-1188 Mounting

The GeeekPi D-1188 ATX breakout sits **on top of the TX300** at the rear ~20 mm of the TX300's footprint, X = −213 to −143 (70 mm), Y = +41 to +100 (59 mm), Z = 73 to 83 (10 mm tall). The 70 × 59 mm breakout PCB mounts via four M3 × 6 mm standoffs that thread into the TX300's top-face mounting holes (or, alternatively, glue down with thermal-grade epoxy if those holes are unavailable on a particular TX300 SKU).

This positioning gives the breakout's screw terminals a short, direct cable run to the back-wall harness, while leaving the front ~80 mm of the TX300 top exposed for the fan exhaust to pass through the vent grille above.

<img src="../figures/chassis/photos/PMVBChassis2.png" alt="" style="max-width: 550px; width: 100%; display: block; margin: 1.5rem auto;">

*Figure 4: View of the chassis interior with the TX300 (left, gray), GeeekPi D-1188 (red, on top of the TX300 rear), and 14 module blades slotted into the bay. The GeeekPi sits at the back portion of the TX300 top so its screw terminals are positioned directly above the back-wall harness rails.*

### 3.5 Sabrent HB-BU10 USB Hub Mounting

The Sabrent HB-BU10 sits at the **rear-center of the chassis floor**, X = −136 to −26 (110 mm), Y = +24 to +74 (50 mm), Z = 6 to 36 (30 mm tall). The hub mounts to the floor plate via two M3 × 6 mm screws threaded into adhesive-backed standoffs (the hub doesn't have factory mounting holes; we attach standoffs with VHB tape to the hub bottom, then bolt those down).

The hub's USB-A downstream ports face **forward** (toward Y = −116) so each downstream port can run a short USB-C-to-USB-A cable rearward to the corresponding module's rear-edge Pico USB-C connector. With the modules' Pico USB-C connectors sitting at the rear edge of each module PCB (Y = +8) and the hub at Y = +24, the cable run is ~16 mm direct-line, easily handled by a 75–150 mm pre-built cable. The hub's uplink (Type-B, micro-B, or USB-C depending on the specific HB-BU10 revision) and DC barrel input pass out the back panel through cutouts.

### 3.6 Module Slot Geometry and Form Factor

The module bay occupies the right ~3/4 of the chassis floor: **14 slots at 22.5 mm pitch**, X centers at −132, −110, −87, −64, −42, −20, +3, +26, +48, +70, +93, +116, +138, +160.

<img src="../figures/chassis/photos/PMVBModule3.png" alt="" style="max-width: 350px; width: 100%; display: block; margin: 1.5rem auto;">

*Figure 5: Side profile of a single module body. The C-shape cross-section is clearly visible: closed top and bottom shells, closed right wall, open left face. The two extensions at the top-right and bottom-right corners are the 1 mm × 3 mm rail lips that engage the chassis floor and ceiling grooves as the module slides in from the front. The host PCB mounts vertically against the cavity right wall and components extend leftward through the cavity and into the inter-module gap, giving 21.5 mm of stack budget per slot.*

**Module body envelope.** Each module body is **16.5 × 125 × 86 mm** with a C-shape cross-section:

- 5 mm thick acrylic top and bottom shells running the full 125 mm depth.
- 1 mm thick right wall (closed) connecting top and bottom shells.
- 1 mm × 3 mm rail lips at the top-right and bottom-right corners, extending the full 125 mm depth, that engage the chassis floor and ceiling grooves.
- **Open left face** — the module's left side has no shell. This is intentional and structural: it widens the effective component-stack budget per slot from 13 mm (a fully closed cavity) to 21.5 mm (cavity plus the 6 mm inter-module gap shared with the adjacent module's open face).

Each module's body sits at Y = −116 (front edge, flush with the chassis front panel) to Y = +8 (rear edge, 35 mm forward of the back-wall harness to leave room for Phoenix plug body and cable strain relief), Z = 0 (3 mm bottom rail lip engages the chassis floor groove from Z = 0 to Z = 4) to Z = 90 (3 mm top rail lip engages the chassis ceiling groove from Z = 86 to Z = 90).

**Internal cavity** is 14.5 × 125 × 70 mm (X = −7.5 to +7, Y = full 125 mm depth, Z = 11 to 81 between the 5 mm top and bottom shells).

**Component stack budget per module: 21.5 mm.** Because every module's left face is open and every module follows the same orientation (lip-on-the-right), components on each module's PCB can extend leftward from the module's own cavity right wall (x = +7) all the way to the adjacent module's right wall outer edge (x = neighbor + 8 = this − 14.5 mm). The 1 mm rail lip on the adjacent module is above and below the cavity Z range and does not reduce the middle-cavity X budget. This is why we can fit headered Pico stacks (14.2 mm) and direct-soldered Pico stacks (6.2 mm) plus analog circuitry on the same side of the host PCB.

**Module mount convention (mandatory across all modules):** each module's host PCB is mounted vertically against the cavity right wall (PCB plane parallel to the chassis YZ plane, PCB normal pointing leftward into the cavity). All components are placed on the cavity-facing (left-pointing) face of the PCB. No components on the back face of the PCB (which is pressed against the right wall). This convention is what makes the 21.5 mm stack budget achievable — without it, adjacent modules could collide in the inter-module gap.

**Connector positions on the host PCB:**

- **Pico USB-C:** rear edge of the PCB, pointing rearward (+Y direction). The Pico 2 W is mounted near the rear half of the PCB with its long axis running along Y so its USB-C connector lands on the rear PCB edge. A short USB-C-to-USB-A cable runs straight rearward to one of the Sabrent HB-BU10's downstream ports.
- **Phoenix MC 1,5/4-G (1803293):** top edge near the rear corner, pointing upward (+Z direction). When the module is fully seated, the chassis's per-slot Phoenix MC 1,5/4-ST plug from the back-wall harness drops down onto this header from above (the harness wires run at Z ≈ 76, just 5 mm above the top edge of the module body's top shell at Z = 86 minus 5 mm shell = effectively at the top of the cavity).
- **Faceplate connectors:** front edge, fitting within ~17 mm wide × 80 mm tall front-face real estate per slot.

### 3.7 Front-Panel Strip and Module Faceplate Region

The front panel of the chassis is divided into two horizontal regions:

**Lower strip (chassis-level diagnostics):** ~50 mm tall, runs the full 420 mm width of the chassis along the bottom of the front panel. This strip carries:

- **4 banana jacks** (Pomona 3760 series, color-coded red/yellow/blue/black for +5 V, +12 V, −12 V, GND) at the leftmost ~80 mm of the strip. These are diagnostic test points: a user can clip a DMM directly onto a rail without disconnecting any module.
- **3 VCC 5102H LED indicators** (5 V variant for +5 V OK, 12 V variant for +12 V OK, optional second 12 V variant for −12 V OK) at the next ~50 mm of the strip. These give at-a-glance rail status visible from across the bench.
- The remaining ~290 mm of the strip is unused and provides surface area for future expansion (e.g., chassis-level oscillator reference, additional test points, or a chassis name/version label).

**Upper region (module faceplate openings — DEFERRED):** The upper ~40 mm of the front panel will eventually carry 14 cutouts at 22.5 mm pitch, each ~17 mm wide × 40 mm tall, exposing the front edge of each module's PCB and its faceplate-mounted I/O (BNC, banana jacks, switches, etc.).

**These cutouts are deliberately not specified in the v1 chassis fabrication.** Each module's faceplate I/O depends on that specific module's design, and committing to cutouts before module designs are stable would force re-fabrication of the front panel each time a module's faceplate I/O changes. The chassis is designed with the front panel as a discrete piece so it can be re-cut independently of the rest of the enclosure when module designs converge.

For the initial fabrication, the chassis front panel will be cut with **only the lower diagnostic strip** (banana jacks + LED indicators). Module-faceplate cutouts will be added in a second front-panel revision once enough modules have committed faceplate I/O specs (probably after Module 1A, 1B, 1D, 1E are designed in detail).

The module body design accommodates this deferral cleanly: with the front panel either uncut or cut for only the diagnostic strip, modules still slide into the chassis along the floor/ceiling card guide grooves, mate with the back-wall harness, and connect to the USB hub. They just don't have a front-panel cutout exposing their faceplate I/O until the front panel is re-cut. For prototyping, modules can be operated with the front of the chassis open or with a dummy panel.

### 3.8 TX300 Fan Ventilation

The TX300's 80 mm fan exhausts upward (Z = +72 face, the top of the PSU). The chassis top plate has a **6 × 12 grid of 5–6 mm round vent holes** positioned in the X = −230 to −150, Y = −110 to +20 region (above the TX300 fan area, clear of the GeeekPi D-1188 footprint at the rear).

Total open area of the vent grille is approximately 1,400–2,000 mm² (depending on hole diameter), or roughly 30–40% of the TX300's 80 mm fan inlet area (~5,000 mm²). This is sufficient for the TX300 running at ≤30% of its 300 W rating (typical PMVB load is well under 50 W on the analog rails) but may be increased if measured air temperature inside the chassis rises above ambient by more than ~10 °C under sustained load. The vent pattern can be densified by re-cutting the top plate without affecting any other piece of the enclosure.

---

## 4. Electrical Architecture

### 4.1 Rail Sources from the TX300

The TX300 provides the standard ATX rails at its 24-pin output: +3.3 V, +5 V, +12 V, −12 V, +5 V Standby, GND. PMVB uses only +5 V, +12 V, −12 V, and GND from this set; +3.3 V and +5 V Standby are not routed forward of the GeeekPi breakout. Per-rail current capacity (per the TX300 datasheet): +5 V at 14 A, +12 V at 22 A, −12 V at 0.3 A. The −12 V rail's 0.3 A budget bounds how many op-amps can be powered simultaneously across all modules; current planning expects worst-case ~150 mA combined across all v1.0 + v1.1 op-amp modules, comfortably within budget.

### 4.2 GeeekPi D-1188 ATX Breakout

The GeeekPi D-1188 (Amazon B08MC389FQ, ~$13) takes the TX300's 24-pin ATX cable as input and exposes each rail on a screw terminal. Features used:

- **PS_ON# slide switch** on the breakout PCB. This is the master enable for the TX300's main rails. With the switch off, only +5 V Standby is alive (which we don't use externally); with the switch on, all rails come up. There is no chassis-level master toggle; the GeeekPi's onboard switch is accessed through the open frame.
- **Per-rail status LEDs** on the breakout PCB. These show +5 V Standby, +3.3 V, +5 V, +12 V, −12 V, PS_ON, and PWROK status. The chassis also has separate front-panel LED indicators (section 4.7) for at-a-glance visibility, but the breakout's onboard LEDs are useful for diagnosing PSU faults during bring-up.
- **Screw terminals** for +5 V, +12 V, −12 V, GND. From these, short hookup wires (16 AWG for +5 V and +12 V; 20 AWG is sufficient for −12 V) carry the rails to the per-rail fuse panel.

### 4.3 Per-Rail Fuse Panel

Each rail passes through a panel-mount glass-cartridge fuse before reaching the back-wall harness. Fuses provide a fast-failure path independent of the breakout's onboard polyfuses (which reset themselves and don't visibly indicate a fault). The fuse panel is a small section of perfboard or terminal-block strip mounted to the chassis floor near the GeeekPi.

| Rail | Fuse rating | Fuse holder | Fuse cartridge |
|---|---|---|---|
| +5 V | 5 A slow-blow | Eaton BK/HTB-22M-R | Bel BK1/GMC-5-R |
| +12 V | 3 A slow-blow | Eaton BK/HTB-22M-R | Bel BK1/GMC-3-R |
| −12 V | 500 mA slow-blow | Eaton BK/HTB-22M-R | Bel BK1/GMC-500MA-R (or equivalent) |

A blown fuse is visible through the holder cap and replaceable without disassembly; the holder accepts standard 5 × 20 mm cartridges.

### 4.4 4-Wire Back-Wall Harness

After the fuse panel, each rail (+5 V, +12 V, −12 V, GND) runs as a 14 AWG stranded wire along the upper-rear region of the chassis interior, at approximately Z = 76 (10 mm below the chassis ceiling) and Y = 14 to 34 (35 mm forward of the back wall). The four wires run parallel along the X axis, ~303 mm long, spanning from just past the GeeekPi's screw terminals (X ≈ −142) to past the rightmost module slot (X ≈ +161).

<img src="../figures/chassis/photos/PMVBChassis3.png" alt="" style="max-width: 550px; width: 100%; display: block; margin: 1.5rem auto;">

*Figure 6: View of the chassis from above-rear, showing the 4-wire back-wall harness (orange) running parallel across the upper-rear region of the chassis interior. The four wires originate at the GeeekPi D-1188 (red, far right, on top of the TX300) and run leftward across the entire module bay, with one Phoenix MC 1,5/4 plug per slot tapping into the rails at each module's X position. The translucent module bodies show the slot pitch and the open-left-face geometry that gives each module access to the harness.*

At each module slot's X position, the harness terminates at a Phoenix MC 1,5/4-ST plug (Phoenix 1803594, Digi-Key 277-1163-ND, ~$8.73 each). The four wires are screwed into the plug's terminals in fixed order: pin 1 = +5 V (red wire), pin 2 = +12 V (yellow), pin 3 = −12 V (blue), pin 4 = GND (black). Wire colors follow lab convention.

The plug clips downward onto the module's PCB-mounted Phoenix MC 1,5/4-G header (Phoenix 1803293, Digi-Key 277-1208-ND, ~$3.51 each), which sits on the top edge near the rear corner of the host PCB with its pins facing upward (+Z direction). With the harness wires at Z ≈ 76 and the module top edge at Z ≈ 80–86, the plug-to-header mating runs perpendicular to the PCB plane, making module insertion and removal a vertical-down + horizontal-back motion. Plug body height is ~12 mm; cable strain relief adds another ~10 mm of Z consumption above the harness wire position, both well within the chassis ceiling clearance.

### 4.5 Per-Module Phoenix Pigtail

Each populated slot uses one Phoenix MC 1,5/4-ST plug terminating a short pigtail of 4 stranded wires (~30 mm long) tapping into the back-wall harness. The taps are made by stripping a 5 mm window in each of the four harness wires at the slot's X position and soldering on the four pigtail wires (or by using inline IDC splicers if soldering inside the chassis is impractical). Heat-shrink tubing covers each tap (using the ElectroBits Thin Wall Heat Shrink Tubing on hand).

Empty slots (no module installed) have no Phoenix plug — the harness wires pass through unbroken. When a new module is added, the user makes 4 splice taps at the slot's X position using the same procedure.

### 4.6 Banana-Jack Diagnostic Test Points

Four 4 mm panel-mount banana jacks (Pomona 3760 series) are installed in the front-panel strip at the leftmost ~80 mm. Color mapping (verified against Digi-Key 2026-05-07):

| Color | Pomona P/N | Digi-Key | Rail |
|---|---|---|---|
| Black | 3760-0 | 501-1041-ND family | GND |
| Red | 3760-2 | 501-1041-ND family | +5 V |
| Yellow | 3760-4 | 501-1041-ND family | +12 V |
| Blue | 3760-6 | 501-1041-ND family | −12 V |

(Note: the Pomona 3760 color suffix mapping is opposite to what's intuitive — `3760-0` is **black**, not red. Verified by Digi-Key catalog lookup.)

Each jack ties to its rail via a short 22 AWG wire from the fuse panel output (after the fuse, before the harness). With the panel jacks fed post-fuse, a fault that blows a fuse will also remove voltage from the test-point jack, providing a cross-check on which rail failed.

### 4.7 Front-Panel Indicator LEDs

Three panel-mount LED indicators (VCC 5102H series, integrated current-limiting resistor for the rated voltage) sit in the front-panel strip just to the right of the banana jacks:

| Indicator | LED | VCC P/N | Digi-Key | Wired to |
|---|---|---|---|---|
| +5 V OK | Red, 5 V | 5102H1-5V | L10021-ND | +5 V rail (post-fuse) |
| +12 V OK | Red, 12 V | 5102H1-12V | 5102H1-12V-ND | +12 V rail (post-fuse) |
| −12 V OK | Green, 12 V | 5102H5-12V | 5102H5-12V-ND | −12 V rail (post-fuse, with current direction handled by the LED's polarity) |

A blown rail fuse causes the corresponding LED to extinguish, giving a visible at-a-glance fault indicator. The LEDs are wired post-fuse so they reflect the rail state actually delivered to the modules.

---

## 5. USB-TMC Backplane

The Sabrent HB-BU10 USB 3.0 hub serves as the chassis-internal USB-TMC backplane. It is **not on the chassis BOM as a power consumer** of the TX300 — the hub runs from its own 60 W external wall brick, reaching the back panel through a barrel-jack cutout — but it is bolted into the chassis for mechanical integration.

Each populated module's Pico 2 W presents a USB-C peripheral interface on the module's right edge. A short USB-C-to-USB-A cable (~150 mm typical) runs from the module's right-edge connector to one of the Sabrent's 10 downstream ports. From the hub's uplink port, a single USB 3.0 cable runs out the back panel to the Pi 5 host on the bench.

Per-port switches and per-port LEDs on the HB-BU10 are operationally useful: a misbehaving Pico can be power-cycled by toggling its hub port without affecting any other module, and the per-port LED quickly identifies which port a SCPI device-discovery query enumerated. The hub's 0.9 A per-port current (USB 3.0 spec minimum) is well above the Pico 2 W's ~80 mA peak draw.

The hub's 10 ports support the v1.0 + v1.1 module count (13 modules) with one port to spare for development gear (a bench USB-TMC scope or a debug Pico). If port count becomes a constraint in a future revision, the hub can be replaced with a higher-port variant (Sabrent HB-B7C3 or similar) without changing any other chassis component.

---

## 6. Bill of Materials

Verified against current sourcing as of 2026-05-07. Sourcing priority: Mouser → Digi-Key → Microcenter → Amazon. The TX300 PSU is on hand from prior projects ($0); replacement cost ~$50–$70 if buying new.

| Item | Manufacturer P/N | Source | Source P/N | Qty | Unit Price | Notes |
|---|---|---|---|---:|---:|---|
| **Power supply and breakout** | | | | | | |
| Silverstone TX300 TFX PSU (300 W) | Silverstone SST-TX300 | n/a | n/a | 1 | $0 | On hand |
| GeeekPi D-1188 ATX 24-pin breakout | GeeekPi D-1188 | Amazon | B08MC389FQ | 1 | $13 | All rails incl. −12 V; per-rail status LEDs; PS_ON# slide switch; verified 2026-05-07 |
| **Per-rail fuse panel** | | | | | | |
| Panel-mount fuse holder, 5×20 mm cartridge | Eaton BK/HTB-22M-R | Digi-Key | 283-3041-ND | 3 | $4.20 | One per active rail (+5 V, +12 V, −12 V) |
| Slow-blow glass fuse 5×20 mm 5 A 125 V | Bel BK1/GMC-5-R | Digi-Key | (search direct) | 5 | $1.75 | +5 V rail; pack with spares |
| Slow-blow glass fuse 5×20 mm 3 A 125 V | Bel BK1/GMC-3-R | Digi-Key | (search direct) | 5 | $1.75 | +12 V rail; pack with spares |
| Slow-blow glass fuse 5×20 mm 0.5 A 125 V | Bel BK1/GMC-500MA-R | Digi-Key | (search direct) | 5 | $1.75 | −12 V rail; pack with spares |
| **Module power interconnect** | | | | | | |
| Phoenix MC 1,5/4-G-3,81 PCB header (chassis-side) | Phoenix Contact 1803293 | Digi-Key | 277-1208-ND | 14 | $3.51 | One per module slot, mounted on per-module PCB |
| Phoenix MC 1,5/4-ST-3,81 cable plug (back-wall harness) | Phoenix Contact 1803594 | Digi-Key | 277-1163-ND | 14 | $8.73 | One per active slot; tapped into back-wall harness |
| Hookup wire 14 AWG stranded, red/yellow/blue/black | Alpha 3050 series | Mouser | 602-3050-* | 1.5 m each color | $5/color | 4-rail back-wall harness, ~330 mm × 4 colors |
| Hookup wire 22 AWG stranded, assorted colors | Alpha 3050 series | Mouser | 602-3050-* | 30 m total | $20 | LED wiring, banana-jack wiring, pigtails |
| **Front-panel diagnostic features** | | | | | | |
| Banana jack panel-mount, 4 mm | Pomona 3760-0 (black) | Digi-Key | 501-1041-ND | 1 | $5 | GND test point |
| Banana jack panel-mount, 4 mm | Pomona 3760-2 (red) | Digi-Key | 501-1041-ND | 1 | $5 | +5 V test point |
| Banana jack panel-mount, 4 mm | Pomona 3760-4 (yellow) | Digi-Key | 501-1041-ND | 1 | $5 | +12 V test point |
| Banana jack panel-mount, 4 mm | Pomona 3760-6 (blue) | Digi-Key | 501-1041-ND | 1 | $5 | −12 V test point |
| LED panel indicator, red, 5 V | VCC 5102H1-5V | Digi-Key | L10021-ND | 1 | $1.92 | +5 V OK |
| LED panel indicator, red, 12 V | VCC 5102H1-12V | Digi-Key | 5102H1-12V-ND | 1 | $1.92 | +12 V OK |
| LED panel indicator, green, 12 V | VCC 5102H5-12V | Digi-Key | 5102H5-12V-ND | 1 | $1.92 | −12 V OK |
| **USB-TMC backplane** | | | | | | |
| Sabrent HB-BU10 USB 3.0 hub, 10-port, self-powered | Sabrent HB-BU10 | Amazon | B0797NZFYP | 1 | $47 | Verified 2026-05-07; uses own 60 W brick, not chassis PSU |
| USB-C to USB-A cable, 150 mm | Generic | Amazon | (any) | 14 | $2 | Per-module cable from Pico 2 W USB-C to hub USB-A |
| **Mechanical (acrylic frame, hardware)** | | | | | | |
| Custom laser-cut acrylic frame, 4 mm clear | n/a | SendCutSend | (custom DXF upload) | 1 set | $40–80 | 6 pieces: floor, top, left, right, back, front. Quote varies with exact DXF. |
| M3 corner standoffs, 12 mm | Generic | Amazon or Mouser | (assorted) | 16 | $0.50 | Frame assembly |
| M3 × 6 mm screws | Generic | Amazon or Mouser | (assorted) | 32 | $0.10 | Frame and component mounting |
| M3 × 12 mm screws | Generic | Amazon or Mouser | (assorted) | 8 | $0.10 | TX300, GeeekPi, hub mounting |
| **On hand (no purchase)** | | | | | | |
| ElectroBits Thin Wall Heat Shrink Tubing, assorted | ElectroBits | n/a | n/a | 1 set | $0 | On hand; covers harness taps and solder joints |
| **Subtotal** | | | | | | |
| Required (no front-panel test points or LEDs) | | | | | **~$235** | Floor with TX300, breakout, fuse panel, harness, hub, modules connected |
| With front-panel banana jacks and LEDs | | | | | **~$260** | Adds diagnostic visibility |

The chassis BOM is exclusive of the per-module BOMs, which are documented in each module's design doc.

---

## 7. Bring-Up Procedure

In order on first power-up, before any module is installed:

### 7.1 Mechanical assembly verification

1. **Visual inspection of the frame.** Confirm all six acrylic pieces are flat, free of cracks, and match the DXF dimensions. Confirm the floor card-guide grooves are at 22.5 mm pitch and span the full module-bay X range, the matching grooves are present on the underside of the top plate, the top-plate vent grille is in the right place, and the front-panel diagnostic strip cutouts (banana jacks + LEDs) are at the right positions. The 14 module-faceplate cutouts in the front panel are deferred — verify the front panel is otherwise solid above the diagnostic strip in the v1 fabrication.
2. **Dry-fit the frame** without electrical components. Verify all M3 screws thread fully; verify the front and back panels seat flush; verify no internal feature (standoff, screw head) blocks the module slot envelope.

### 7.2 Electrical bring-up, no modules

3. **Mount the TX300** to the floor plate. Verify the IEC inlet aligns with the front-panel cutout (left end of the front panel) and the 24-pin ATX output cable exits toward the back of the chassis where the GeeekPi will mount.
4. **Mount the GeeekPi D-1188** to the TX300's top face. Connect the TX300's 24-pin ATX cable to the breakout's 24-pin input.
5. **Wire the per-rail fuse panel.** From the breakout's screw terminals, run +5 V, +12 V, and −12 V through their respective fuse holders (5 A, 3 A, 0.5 A) to short stub wires. Leave the stub wires unconnected for now.
6. **Verify continuity (mains disconnected)**: with the IEC cord unplugged, confirm no short between any two rails or between any rail and the GeeekPi's metal housing. Use a DMM at the breakout's screw terminals.
7. **Plug the IEC cord** into the front-panel cutout. Switch the GeeekPi's PS_ON# slide switch ON.
8. **Verify rail voltages** at the post-fuse stub wires: +5 V should read 4.95 to 5.05 V, +12 V should read 11.85 to 12.15 V, −12 V should read −11.7 to −12.3 V.
9. **Verify the front-panel LEDs light** (+5 V OK red, +12 V OK red, −12 V OK green). Verify the GeeekPi's onboard rail-status LEDs are also lit.
10. **Verify the banana-jack test points** read the correct rail voltage with a DMM.

### 7.3 Back-wall harness bring-up

11. **Wire the back-wall harness.** Run 4 × 14 AWG wires from the post-fuse rails along the chassis upper-rear region. Solder a Phoenix MC 1,5/4-ST plug at each module slot's X position (or wire only one or two for initial bring-up).
12. **Verify harness voltage** at each Phoenix plug: clip a DMM across pins 1-4 and 2-4 (or use a banana-tipped probe through the plug from the back); confirm +5 V, +12 V, −12 V are present at each plug.
13. **Switch PS_ON# OFF** and verify all rails fall to ~0 V within 5 seconds (TX300's bulk-cap discharge time is bounded by its internal bleed resistors).

### 7.4 USB hub bring-up

14. **Mount the Sabrent HB-BU10** to the floor plate at the rear-center position. Connect its DC barrel jack to the Sabrent's 60 W wall brick (external, runs out the back panel through a barrel cutout). Connect its uplink USB cable to the Pi 5.
15. **Verify the hub enumerates.** Run `lsusb` on the Pi 5 and confirm the Sabrent appears as a USB 3.0 hub device.
16. **Verify per-port switches and LEDs.** Toggle each of the 10 per-port switches OFF and ON; confirm the LED for that port follows.

### 7.5 First-module bring-up

17. **Install one module** into the leftmost slot (slot 1). Connect its USB-C cable to hub port 1. Connect the slot-1 Phoenix plug to the module's top-rear header.
18. **Switch PS_ON# ON** and verify the module's Pico boots (heartbeat LED on the Pico).
19. **Run `lsusb`** on the Pi 5 and confirm the module appears as a USB-TMC device.
20. **Run a smoke-test SCPI sequence** against the module (`*IDN?` query) and confirm a valid response.

### 7.6 Full population

21. **Repeat steps 17–20** for each module as it is built and bring-up tested. Each module follows the same procedure.

---

## 8. Safety Procedures

### 8.1 Daily operation

Power up: confirm the TX300's IEC cord is plugged in. Switch the GeeekPi's PS_ON# slide switch ON. Front-panel LEDs should illuminate.

Power down: switch PS_ON# OFF. The +5 V Standby rail remains alive but is not used by anything in the chassis. For complete disconnect, unplug the IEC cord.

### 8.2 Working inside the chassis

The DC zone (everything downstream of the GeeekPi) is SELV under all operating conditions and is touch-safe. The AC zone (TX300's primary side, IEC inlet) is contained inside the TX300's certified enclosure; mains never leaves the PSU body.

To work inside the chassis (e.g., adding a module, replacing a fuse, debugging a harness tap):

1. Switch PS_ON# OFF.
2. Unplug the IEC cord from the back panel (positive disconnect — never trust just the slide switch for safety).
3. Wait 10 seconds for the TX300's bulk capacitors to discharge through their internal bleed resistors.
4. With a DMM, verify zero voltage on all rails at the post-fuse test points before touching any wire.
5. Perform the work.
6. Reverse the procedure: re-seat all components, plug the IEC cord, switch PS_ON# ON, re-verify rail voltages.

### 8.3 Shared work / lockout-tagout

If anyone other than the operator is working in the chassis (e.g., a friend helping debug a module):

1. Unplug the IEC cord from the wall outlet.
2. Hang a tag on the cord saying "DO NOT PLUG IN — under maintenance."
3. Open the chassis as in section 8.2.
4. Verify zero voltage with a DMM before touching any conductor.

This is overkill for solo hobbyist work but matches industry practice and is worth practicing.

---

## 9. Future Enhancements

- **Active cooling** via a small 40 mm muffin fan mounted on a side panel if the TX300 fan plus convective vent prove insufficient under sustained load. The chassis frame can be re-cut with a 40 mm fan grille without affecting any other piece.
- **Per-module fuses** in addition to per-rail fuses, providing slot-level fault isolation. The Phoenix MC 1,5/4-ST plug at each slot can be replaced with a 4-position fused plug (Phoenix MSTBVA series) at additional cost, ~$8 per slot.
- **Higher-port USB hub** if the v2.0 module roadmap exceeds the Sabrent HB-BU10's 10 ports. The hub is a drop-in swap; no chassis modifications required.
- **Galvanically isolated module variants** for HV-input modules (Module 1F HV diff probe v1.2). The module's input would use a flyback isolated DC-DC converter and digital isolators, drawing only +5 V from the harness; the −12 V and +12 V rails would not be used by that module.
- **Larger-current rail variants** for high-current SMU upgrades. The TX300's +12 V rail at 22 A is plenty for the planned analog modules; higher-current applications would need a different PSU class (e.g., a Mean Well RD-65A), which would be a separate chassis design.
- **Per-rail current monitoring** via INA226 or similar I²C current-sense ICs in line with each rail at the GeeekPi outputs. Adds ~$10 in parts and gives telemetry into Pico-driven monitoring during measurement runs.
- **DIN-rail or rack-mount adaptation** for users who want to integrate the chassis into a larger 19" rack or a DIN-rail-style instrument bay. The acrylic frame can be replaced with a different cut without changing any electrical content.

---

## 10. References

- [PMVB System Design Document section 11 (Power Architecture)](../system-design/System_Design_Document.html#power-architecture) — high-level architecture context.
- [PMVB System Design Document section 4.1 (Top-Level Architecture)](../system-design/System_Design_Document.html#top-level-architecture) — chassis position in the wider system.
- [Silverstone SST-TX300 manual](https://www.silverstonetek.com/en/product/info/power-supply/TX300/) — TX300 PSU electrical and mechanical specs.
- [GeeekPi D-1188 product page](https://www.amazon.com/dp/B08MC389FQ) — ATX 24-pin breakout reference.
- [Sabrent HB-BU10 product page](https://www.amazon.com/dp/B0797NZFYP) — USB 3.0 hub reference.
- [Phoenix Contact MC 1,5/4 series datasheet](https://www.phoenixcontact.com/en-us/products/pcb-plug-mc-15-4-st-381-1803594) — module power interconnect.
- [SendCutSend acrylic laser-cutting service](https://sendcutsend.com/materials/acrylic/) — chassis fabrication.
