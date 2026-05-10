# Poor Man's Validation Bench

A modular SCPI instrument platform that mirrors NI PXIe rack-and-module test architecture at hobbyist budget. A Raspberry Pi 5 acts as the orchestration head running PyVISA, pytest, InfluxDB, and Grafana. Hot-swappable instrument modules attach over USB or Ethernet and present as independent SCPI-addressable instruments. Every module is also exposed through a Model Context Protocol (MCP) tool surface for agent-orchestrated bench sessions.

## Documentation

### Canonical reference

- **[System Design Document](https://pike1950.github.io/poor-mans-validation-bench/docs/system-design/System_Design_Document.html)** — full v1.0 SDD covering architecture, module catalog, specifications, software stack, build phases, and verification strategy. Rendered via GitHub Pages.

### Chassis design

- **[Chassis Architecture and Power Distribution](https://pike1950.github.io/poor-mans-validation-bench/docs/chassis/Chassis_Architecture_and_Power_Distribution.html)** — open-frame acrylic blade-style chassis (laser-cut from SendCutSend, 435 × 238 × 92 mm) housing the Silverstone TX300 PSU as an analog-rail backbone, the GeeekPi D-1188 ATX breakout, the Sabrent HB-BU10 USB 3.0 hub, and 14 module slots at 22.5 mm pitch. Covers mechanical architecture, electrical architecture (4-rail back-wall harness with Phoenix MC 1,5/4 module interconnect, per-rail fuse panel, banana-jack diagnostic test points), USB-TMC backplane, BOM with Digi-Key and Amazon cross-references, bring-up procedure, and safety protocols.

### Per-module design

- **[Module 1E: Function Generator / AWG](https://pike1950.github.io/poor-mans-validation-bench/docs/modules/Module_1E_Design_Document.html)** — theory of operation, functional block diagram, Pico-to-DAC-to-op-amp pin assignments, four sample applications (single-tone sine, swept-sine THD, multitone IMD, white noise), calibration procedure, bring-up checklist, and BOM with Mouser and Digi-Key cross-references.

## Module Catalog

Every module is built on a Pico 2 W bridge presenting as a USB-TMC instrument over the chassis powered USB hub. Tier 2 modules add a Tang Primer 25K FPGA the Pico masters over SPI. Tier 3 modules (deferred) replace the Tang Primer 25K with a larger FPGA platform and add a Pi Zero 2 W streaming sidecar for sustained-capture data paths beyond USB-TMC's 12 Mbps.

| ID | Tier | Function | Status |
|----|------|----------|--------|
| 1A | 1 | Digital I/O Controller | Planned (v1.0) |
| 1B | 1 | Voltage Measurement Unit | Planned (v1.0) |
| 1C | 1 | USB HID Protocol Analyzer | Planned (v1.0) |
| 1D | 1 | Source-Measure Unit Lite | Planned (v1.0) |
| 1E | 1 | Function Generator / AWG | Planned (v1.0) |
| 1F | 1 | High-Voltage Differential Probe | Planned (v1.1) |
| 1G | 1 | IR Capture and Transmit | Planned (v1.1) |
| 1H | 1 | Multi-Function DMM | Planned (v1.0) |
| 2A | 2 | Logic Analyzer | Planned (v1.0) |
| 2B | 2 | Protocol Exerciser / Analyzer | Planned (v1.0) |
| 2C | 2 | Frequency Counter | Planned (v1.0) |
| 2D | 2 | Ethernet MAC and Network Analyzer | Planned (v1.0) |
| 2E | 2 | Mixed-Signal Digitizer / Oscilloscope | Planned (v1.0) |
| 3A | 3 | USB 2.0 Protocol Analyzer | Deferred |
| 3B | 3 | HDMI Sideband Analyzer | Deferred |
| 3C | 3 | USB-C CC Analyzer | Deferred |

## Architecture at a Glance

Two control planes per module: a VISA/SCPI plane for headless test sequencing (pytest, vendor-portable, deterministic) and an MCP plane that exposes the same instrument surface as LLM-callable tools for agent-orchestrated bench sessions. Both planes consume the same per-module YAML command schema; firmware parsers and PyVISA-sim simulation backends are generated mechanically from the YAML.

Every module is built around a Pico 2 W running the SCPI parser in bare-metal C and presenting as a USB-TMC instrument. Tier 1 modules add an analog or digital front end appropriate to the function. Tier 2 modules add a Sipeed Tang Primer 25K FPGA where the instrument logic lives; the Pico bridges to the FPGA over SPI at approximately 30 MHz. Tier 3 modules (deferred) replace the Tang Primer 25K with a larger FPGA (Tang Mega 138K Pro or Alinx AX7325B) for high-speed interface analysis and add a Pi Zero 2 W streaming sidecar for sustained-capture data paths beyond USB-TMC's 12 Mbps. Persistent state for Tier 1 and Tier 2 modules lives in the Pico's onboard 4 MB flash; bench-level admin services run on the Pi 5 orchestration head.

See section 4 of the [System Design Document](https://pike1950.github.io/poor-mans-validation-bench/docs/system-design/System_Design_Document.html#functional-block-diagram) for the full architecture diagram.

## Status

Phase-by-phase build progress. Top-level structure mirrors [SDD section 13](https://pike1950.github.io/poor-mans-validation-bench/docs/system-design/System_Design_Document.html#build-phases-and-investment-roadmap). Items are sized for single-session work units. Per-module work follows a standard template: design doc → BOM → PCB → assembly → firmware → bring-up → calibration → service. Status legend: `[ ]` not started · `[~]` in progress · `[x]` complete · `[!]` blocked.

### Phase 0 — Orchestration + Chassis Power

Phase 0 brings up the orchestration head and chassis power subsystem to the point where a simulator-backed end-to-end test exercises the full SCPI → InfluxDB → Grafana → report pipeline.

**Architectural decisions (settled)**

- [x] System Design Document v1.0 published
- [x] Chassis LAN switch dropped from v1.0 baseline (moved to Phase 4)
- [x] TFX (TX300) is analog-rail backbone, not chassis-wide power
- [x] Pi 5, Sabrent hub, Picos run from independent external supplies
- [x] Pi 5 ↔ USB hub link is USB 3.0
- [x] Chassis envelope: 435 × 238 × 92 mm in 3 mm cast acrylic from SendCutSend
- [x] Chassis topology v1.0: open-frame card cage (4 panels: floor, bottom groove plate, top groove plate, ceiling) held by 4 M3 corner standoffs. Side walls + rear wall + front panel deferred to v1.1 pending thermal review.
- [x] Module form factor v10 (JLCPCB-FDM-compliant): 16.3 × 125 × 86 mm outer, 6 mm shells, 2 mm right wall, 1.5 × 3 × 125 mm rail lips at top-right and bottom-right edges, 14.3 × 125 × 68 mm cavity
- [x] Chassis groove: 2 mm wide × 3 mm deep × 125 mm long, at 22.5 mm slot pitch starting at x = 100 mm (leftmost 10 mm reserved for M3 corner standoff clearance + 86 mm TX300 zone + 4 mm air gap). 0.5 mm sliding clearance.
- [x] Module fabrication path: FDM PLA via US service for prototype (Baysinger's AM); FDM PETG via JLCPCB for the production batch of 14 once v10 fit validates
- [x] Module Design Document Schema authored (local tooling)

**Chassis sourcing (verified BOM, ~$280)**

- [x] GeeekPi D-1188 ATX breakout — Amazon B08MC389FQ ($13)
- [ ] Sabrent HB-BU10 USB 3.0 hub — Amazon B0797NZFYP ($47)
- [ ] Phoenix MC 1,5/4 connector kit — Digi-Key 277-1208-ND + 277-1163-ND, ×14 pairs (~$170)
- [ ] Fuse panel hardware — Eaton BK/HTB-22M-R holders ×3 + Bel BK1/GMC cartridges (5 A / 3 A / 0.5 A) (~$25)
- [ ] Pomona 3760 banana jacks ×4, color-coded (~$20)
- [ ] VCC 5102H LED indicators ×3 (red 5 V, red 12 V, green 12 V) ($6)
- [ ] Hookup wire kit (14 AWG harness colors + 22 AWG signal assortment, ~$25)
- [ ] M3 hardware: 4× M3 × 80 mm hex aluminum standoffs + bag of M3 × 10 mm button head cap screws (~$15 from Amazon / McMaster)
- [ ] USB-C-to-USB-A short cables ×14, ~150 mm (~$30)
- [x] Heat-shrink tubing on hand (ElectroBits)
- [x] TX300 PSU on hand

**Chassis fabrication + assembly**

Iterative build strategy: prototype-first. Order one chassis acrylic set (4 panels) plus one PLA module body, slide-test the v10 lip-and-groove fit, then commit to the JLCPCB batch order for the remaining 13 module bodies and proceed with the full chassis assembly + harness build-out. Module 1E is still the first module to fully populate (analog complexity shakes out harness, USB, and faceplate clearances better than simpler modules); Pi 5 software-stack work runs in parallel.

- [x] Tinkercad reference design committed (chassis + module + slot grooves + vent grid)
- [x] Parametric DXF + STL generator authored (`tools/fabrication/generate_prototype_v10.py`) using ezdxf + trimesh
- [x] v10 module STL generated (`module_body_v10.stl`, 44 triangles, watertight, 42.6 cm³)
- [x] Chassis DXFs generated with M3 corner clearance holes: `panel_solid_plate.dxf` (qty 2 for floor + ceiling), `panel_groove_plate.dxf` (qty 2 for bottom + top divider, with 14 module slot cutouts each)
- [x] Exploded-view assembly diagram + STL generated (`chassis_assembly_exploded.png`, `chassis_assembly_exploded.stl`)
- [x] v10 prototype module ordered from Baysinger's AM (Texas, USA) via Craftcloud — order #465257381764, $24.77 express, ETA May 14-19
- [ ] Order chassis acrylic from SendCutSend (~$135 for 4 panels in 3 mm blue cast acrylic at the widened 435 × 238 × 92 mm envelope, free US shipping)
- [ ] Order M3 hardware (4× M3 × 80 mm hex standoffs + M3 × 10 mm cap screws, ~$15)
- [ ] Receive prototype module and chassis panels; verify dimensions
- [ ] Slide-fit test: insert module body into one chassis slot, verify lip-and-groove engagement with 0.5 mm sliding clearance
- [ ] Iterate v10 design if slide-fit fails (edit constants in generator script, regenerate, re-order)
- [ ] If slide-fit passes: order JLCPCB batch of 14 module bodies in PETG (~$84)
- [ ] Frame assembly: stack floor + bottom groove plate + 4 corner standoffs + top groove plate + ceiling, clamp with 8 M3 × 10 mm screws
- [ ] Mount TX300 inside the open-frame chassis (IEC inlet at front, fan up)
- [ ] Mount GeeekPi D-1188 on TX300 rear top + connect 24-pin ATX
- [ ] Mount Sabrent HB-BU10 to floor, rear-center
- [ ] Build per-rail fuse panel + wire to GeeekPi outputs
- [ ] Build 4-wire back-wall harness (303 mm × 14 AWG, color-coded) — initially only tap slot 1 for Module 1E shakedown
- [ ] Single-slot shakedown: install Module 1E in slot 1, verify Phoenix mate + USB cable run + harness tap routing
- [ ] After single-slot shakedown passes, tap remaining 13 harness positions
- [ ] Install + wire front-panel diagnostic strip (banana jacks ×4 + LED indicators ×3) on a separate small acrylic strip mounted to the chassis floor (front-panel proper deferred to v1.1)
- [ ] **Deferred to v1.1:** chassis side walls, rear wall, front panel, ventilation geometry, module-specific faceplate cutouts. Walls + vents must be co-designed because closing the chassis re-introduces TX300 cooling constraints.

**Chassis bring-up**

- [ ] Visual + continuity tests, mains disconnected
- [ ] Mains-only AC test (TX300 in standby)
- [ ] DC at no load (rail voltages at fuse outputs, front-panel LEDs, banana-jack test points all verified)
- [ ] Back-wall harness rail voltages verified at every Phoenix plug position

**Pi 5 hardware**

- [x] Pi 5 16 GB price verified at Microcenter ($305)
- [x] Pi 5 16 GB + 27 W USB-C charger + active cooler on hand
- [x] microSD (32 GB) + M.2 HAT+ + 512 GB NVMe SSD on hand
- [x] Pi 5 assembled (heatsink + M.2 HAT+ + NVMe)

**Pi 5 software stack**

- [ ] Raspberry Pi OS 64-bit install + headless config (hostname, network, SSH)
- [ ] Migrate boot to NVMe SSD
- [ ] Python 3.11+ + PyVISA / pyvisa-py + USB-TMC udev permissions
- [ ] InfluxDB 1.8 (install + service + PMVB tag schema)
- [ ] Grafana (install + InfluxDB datasource + placeholder bench dashboard)
- [ ] Jinja2 + Matplotlib + report template skeleton
- [ ] MCP gateway scaffolding (Anthropic Python SDK)

**Phase 0 verification milestone (per SDD §13.1)**

- [ ] Pi 5 boots from NVMe, reaches bench network, hub enumerates as USB 3.0
- [ ] PyVISA-sim end-to-end: pytest queries `*IDN?` against simulator → InfluxDB write → Grafana panel renders → Jinja2 report references the record

**Phase 0 documentation**

- [x] Chassis Architecture and Power Distribution doc
- [x] SDD §11.5 Power Architecture
- [ ] Phase 0 bring-up record (date, observed rail voltages, blockers)

### Phase 1 — Tier 1 Core (1A, 1B, 1D, 1E)

Four foundational Tier 1 modules using the chassis from Phase 0. Each follows the per-module template.

- [ ] **Module 1A — Digital I/O Controller**: design doc · BOM · PCB · assembly · firmware · bring-up · calibration · service
- [ ] **Module 1B — Voltage Measurement Unit**: design doc · BOM · PCB · assembly · firmware · bring-up · calibration · service (front-end: ADS1115 + instrumentation amp on ±12 V rails)
- [ ] **Module 1D — Source-Measure Unit Lite**: design doc · BOM · PCB · assembly · firmware · bring-up · calibration · service (front-end: DAC + force/sense op-amp loop on ±12 V rails)
- **Module 1E — Function Generator / AWG**:
  - [x] Design doc v1.1
  - [x] Functional figures (system context, AD9742 datasheet embed, typical app)
  - [x] BOM verified at Digi-Key + Microcenter ($53)
  - [ ] BOM ordered
  - [ ] PCB design (KiCad: AD9742 + AD8056 + reconstruction filter + 3× Coto 9007 reeds + Pico)
  - [ ] PCB fab + assembly
  - [ ] Firmware (SCPI YAML for sine/square/triangle/ramp/noise/multitone/ARB/sweep + PIO+DMA streaming at 30-50 MSPS)
  - [ ] Bring-up checklist (visual → power → DC → swept sine → THD → spectral purity → impedance switch)
  - [ ] Calibration (DC offset, gain, frequency, filter passband flatness)
  - [ ] Module enters service

**Phase 1 system tests**

- [ ] Audio analyzer recipe partial (1E stimulus + 1B integration; full recipe blocked on Module 2E in Phase 2.5)
- [ ] Phase 1 verification milestone per SDD §13.2

### Phase 1.5 — HID Module + Tier 2 Bridge Bring-Up

- [ ] **Module 1C — USB HID Protocol Analyzer**: design doc · BOM · PCB · assembly · firmware · bring-up · service (architecture: dual-Pico bridge)
- [ ] **Tier 2 bridge stack (Tang Primer 25K + Pico)**: bridge module PCB · fab + assembly · Tang Primer placeholder HDL · Pico bridge firmware · `*IDN?` through bridge returns placeholder string · Phase 1.5 verification milestone per SDD §13.3

### Phase 1.7 — Module 1H DMM

- [ ] **Module 1H — Multi-Function DMM**: design doc · BOM · PCB · assembly · firmware · bring-up · per-range calibration · service (front-end: ADS1256 24-bit ADC + relay-switched multi-range network on ±12 V rails)
- [ ] Phase 1.7 verification milestone per SDD §13.3.5: 9 V battery, 1 kΩ ±1 % reference, 1 kHz sine from 1E all read within stated module accuracy

### Phase 2 — Tier 2 Core (2A, 2B, 2C, 2D)

Four primary Tier 2 modules using the bridge stack from Phase 1.5. Each adds Tang Primer 25K HDL alongside the Pico bridge firmware (synthesis on shared FPGA per project rule).

- [ ] **Module 2A — Logic Analyzer**: design doc · BOM · PCB · assembly · HDL (capture + buffer + SPI register IF) · firmware · bring-up · service
- [ ] **Module 2B — Protocol Exerciser / Analyzer**: design doc · BOM · PCB · assembly · HDL (protocol bit-banger + decoder) · firmware · bring-up · service
- [ ] **Module 2C — Frequency Counter**: design doc · BOM · PCB · assembly · HDL (count state machine) · firmware · bring-up · TCXO calibration via GPSDO · service
- [ ] **Module 2D — Ethernet MAC and Network Analyzer**: design doc · BOM · PCB · assembly · HDL (MAC frame analyzer) · firmware · bring-up · service

**Phase 2 verification milestone (SDD §13.4)**

- [ ] All Tier 2 modules enumerate and respond to `*IDN?`
- [ ] Trigger bus tested (2A capturing on 1E sync edge)
- [ ] InfluxDB receives capture records from each Tier 2 module

### Phase 2.5 — Module 2E Digitizer

- [ ] **Module 2E — Mixed-Signal Digitizer / Oscilloscope**: design doc · BOM · PCB · assembly · HDL (ADC capture + trigger logic) · firmware · bring-up · calibration (offset, gain, bandwidth) · service (front-end: high-speed multi-channel ADC + analog conditioning on ±5 V or ±12 V rails)

**Phase 2.5 system tests (SDD §13.5)**

- [ ] Audio analyzer recipe full: 1E sweep stimulus + 2E capture + Pi 5 FFT (THD/SFDR/IMD) → InfluxDB → Grafana → report
- [ ] Firestick boot capture: 5 V rail transient via 2E

### Phase 3 — v1.1 Tier 1 (1F, 1G)

- [ ] **Module 1F — High-Voltage Differential Probe**: design doc · HV safety review · BOM · PCB · assembly · firmware · bring-up (low-V → ramp to ±300 V) · calibration · service (front-end: AD8421 instrumentation amp + 100:1 attenuator on ±12 V rails). Document v1.2 fully-isolated variant as future enhancement.
- [ ] **Module 1G — IR Capture and Transmit**: design doc · BOM · PCB · assembly · firmware (NEC, RC5, Sony SIRC encode/decode) · bring-up · service

**Phase 3 verification milestone**

- [ ] Full v1.0 + v1.1 catalog enumerates correctly
- [ ] Cross-module integration recipe (e.g., 1F captures HV transient triggered by 1E AWG sync)

### Phase 4 — Tier 3 (Deferred)

Gated on a future FPGA-upgrade decision. Not on the v1.0 + v1.1 critical path.

- [ ] FPGA selection: Tang Mega 138K Pro vs AX7325B
- [ ] Pi Zero 2 W streaming sidecar architecture
- [ ] Chassis LAN switch re-evaluation
- [ ] Tier 3 modules: 3A (USB 2.0 protocol analyzer), 3B (HDMI sideband), 3C (USB-C CC analyzer)

### Cross-Cutting

Continuous work that spans phases.

**Documentation**

- [x] System Design Document v1.0
- [x] Chassis Architecture and Power Distribution doc
- [x] Module 1E Design Document v1.1
- [x] PMVB figure legend (Figure 4-0)
- [x] Figure 4-1 (top-level system block, TikZ)
- [x] Chassis block diagram (TikZ, wi