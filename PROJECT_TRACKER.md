# PMVB Project Tracker

This file is the persistent task list for the Poor Man's Validation Bench. Top-level structure mirrors the build phases defined in [SDD section 13](docs/system-design/System_Design_Document.html#build-phases-and-investment-roadmap); within each phase, tasks are grouped by area.

**Status legend:** `[ ]` not started · `[~]` in progress · `[x]` complete · `[!]` blocked

**Conventions:** items are sized for single-session work units. When an item completes, flip the checkbox and (where useful) cite the commit hash. New tasks discovered mid-build land under the appropriate phase immediately.

---

## Table of Contents

- [Phase 0 — Orchestration + Chassis Power](#phase-0--orchestration--chassis-power)
- [Phase 1 — Tier 1 Core (1A, 1B, 1D, 1E)](#phase-1--tier-1-core-1a-1b-1d-1e)
- [Phase 1.5 — HID Module + Tier 2 Bridge Bring-Up](#phase-15--hid-module--tier-2-bridge-bring-up)
- [Phase 1.7 — Module 1H DMM](#phase-17--module-1h-dmm)
- [Phase 2 — Tier 2 Core (2A, 2B, 2C, 2D)](#phase-2--tier-2-core-2a-2b-2c-2d)
- [Phase 2.5 — Module 2E Digitizer](#phase-25--module-2e-digitizer)
- [Phase 3 — v1.1 Tier 1 (1F, 1G)](#phase-3--v11-tier-1-1f-1g)
- [Phase 4 — Tier 3 (Deferred)](#phase-4--tier-3-deferred)
- [Cross-Cutting](#cross-cutting)

**Per-module work template** (used in every module subsection below):

1. Design doc per [Module Design Document Schema](docs/templates/Module_Design_Document_SCHEMA.md)
2. BOM verified at Mouser/Digi-Key + ordered
3. PCB design (KiCad schematic + layout + DRC + Gerbers)
4. PCB fab order + component assembly
5. Firmware (SCPI YAML + parser + USB-TMC + module handlers, flashed to Pico)
6. Bring-up checklist + (Tier 2) Tang Primer HDL
7. Calibration + module enters service

---

## Phase 0 — Orchestration + Chassis Power

Phase 0 brings up the orchestration head and chassis power subsystem to the point where a simulator-backed end-to-end test exercises the full SCPI → InfluxDB → Grafana → report pipeline.

### Architectural decisions (settled)

- [x] System Design Document v1.0 published
- [x] Chassis LAN switch dropped from v1.0 baseline (moved to Phase 4)
- [x] TFX (TX300) is analog-rail backbone, not chassis-wide power
- [x] Pi 5, Sabrent hub, Picos run from independent external supplies
- [x] Pi 5 ↔ USB hub link is USB 3.0
- [x] Chassis: open-frame acrylic blade case, laser-cut from SendCutSend
- [x] Module form factor: 16.5 × 125 × 86 mm body, C-shape, 22.5 mm slot pitch, PCB-against-right-wall convention
- [x] [Module Design Document Schema](docs/templates/Module_Design_Document_SCHEMA.md) authored

### Chassis sourcing (verified BOM, ~$280)

- [ ] GeeekPi D-1188 ATX breakout — Amazon B08MC389FQ ($13)
- [ ] Sabrent HB-BU10 USB 3.0 hub — Amazon B0797NZFYP ($47)
- [ ] Phoenix MC 1,5/4 connector kit — Digi-Key 277-1208-ND + 277-1163-ND, ×14 pairs (~$170)
- [ ] Fuse panel hardware — Eaton BK/HTB-22M-R holders ×3 + Bel BK1/GMC cartridges (5 A / 3 A / 0.5 A) (~$25)
- [ ] Pomona 3760 banana jacks ×4, color-coded (~$20)
- [ ] VCC 5102H LED indicators ×3 (red 5 V, red 12 V, green 12 V) ($6)
- [ ] Hookup wire kit (14 AWG harness colors + 22 AWG signal assortment, ~$25)
- [ ] M3 hardware kit (corner standoffs, screws qty ~50) (~$20)
- [ ] USB-C-to-USB-A short cables ×14, ~150 mm (~$30)
- [x] Heat-shrink tubing on hand (ElectroBits)
- [x] TX300 PSU on hand

### Chassis fabrication + assembly

- [x] Tinkercad reference design committed (chassis + module + slot grooves + vent grid)
- [ ] Generate SendCutSend DXF from Tinkercad / Inkscape; order acrylic frame (~$40-80)
- [ ] Front-panel module-faceplate cutouts (deferred until Modules 1A/1B/1D/1E faceplate I/O converges; chassis is designed so the front panel can be re-cut independently)
- [ ] Receive acrylic; verify dimensions match DXF
- [ ] Frame assembly (corner standoffs + side / top / bottom / front / back panels)
- [ ] Mount TX300 (IEC inlet to front, fan up, ATX cable to rear)
- [ ] Mount GeeekPi D-1188 on TX300 rear top + connect 24-pin ATX
- [ ] Mount Sabrent HB-BU10 to floor, rear-center
- [ ] Build per-rail fuse panel + wire to GeeekPi outputs
- [ ] Build 4-wire back-wall harness (303 mm × 14 AWG, color-coded)
- [ ] Install + wire front-panel banana jacks (×4) and LED indicators (×3)

### Chassis bring-up

- [ ] Visual + continuity tests, mains disconnected
- [ ] Mains-only AC test (TX300 in standby)
- [ ] DC at no load (rail voltages at fuse outputs, front-panel LEDs, banana-jack test points all verified)
- [ ] Back-wall harness rail voltages verified at every Phoenix plug position

### Pi 5 hardware

- [x] Pi 5 16 GB price verified at Microcenter ($305)
- [ ] Order Pi 5 16 GB + 27 W USB-C charger + active cooler ($325)
- [ ] Order microSD (32 GB) + M.2 HAT+ + 512 GB NVMe SSD ($60)
- [ ] Assemble Pi 5 (heatsink + M.2 HAT+ + NVMe)

### Pi 5 software stack

- [ ] Raspberry Pi OS 64-bit install + headless config (hostname, network, SSH)
- [ ] Migrate boot to NVMe SSD
- [ ] Python 3.11+ + PyVISA / pyvisa-py + USB-TMC udev permissions
- [ ] InfluxDB 1.8 (install + service + PMVB tag schema)
- [ ] Grafana (install + InfluxDB datasource + placeholder bench dashboard)
- [ ] Jinja2 + Matplotlib + report template skeleton
- [ ] MCP gateway scaffolding (Anthropic Python SDK)

### Phase 0 verification milestone (per SDD §13.1)

- [ ] Pi 5 boots from NVMe, reaches bench network, hub enumerates as USB 3.0
- [ ] PyVISA-sim end-to-end: pytest queries `*IDN?` against simulator → InfluxDB write → Grafana panel renders → Jinja2 report references the record

### Phase 0 documentation

- [x] [Chassis Architecture and Power Distribution doc](docs/chassis/Chassis_Architecture_and_Power_Distribution.html)
- [x] [SDD §11.5 Power Architecture](docs/system-design/System_Design_Document.html#power-architecture)
- [ ] Phase 0 bring-up record (date, observed rail voltages, blockers)

---

## Phase 1 — Tier 1 Core (1A, 1B, 1D, 1E)

Four foundational Tier 1 modules using the chassis from Phase 0. Each follows the per-module template above.

### Module 1A — Digital I/O Controller

- [ ] Design doc · BOM · PCB · assembly · firmware · bring-up · calibration · service

### Module 1B — Voltage Measurement Unit

- [ ] Design doc · BOM · PCB · assembly · firmware · bring-up · calibration · service
  - Front-end: ADS1115 + instrumentation amp on ±12 V rails

### Module 1D — Source-Measure Unit Lite

- [ ] Design doc · BOM · PCB · assembly · firmware · bring-up · calibration · service
  - Front-end: DAC + force/sense op-amp loop on ±12 V rails

### Module 1E — Function Generator / AWG

- [x] Design doc v1.1 — [Module 1E doc](docs/modules/Module_1E_Design_Document.html)
- [x] Functional figures (system context, AD9742 datasheet embed, typical app)
- [x] BOM verified at Digi-Key + Microcenter ($53)
- [ ] BOM ordered
- [ ] PCB design (KiCad: AD9742 + AD8056 + reconstruction filter + 3× Coto 9007 reeds + Pico)
- [ ] PCB fab + assembly
- [ ] Firmware (SCPI YAML for sine/square/triangle/ramp/noise/multitone/ARB/sweep + PIO+DMA streaming at 30-50 MSPS)
- [ ] Bring-up checklist (visual → power → DC → swept sine → THD → spectral purity → impedance switch)
- [ ] Calibration (DC offset, gain, frequency, filter passband flatness)
- [ ] Module enters service

### Phase 1 system tests

- [ ] Audio analyzer recipe partial (1E stimulus + 1B integration; full recipe blocked on Module 2E in Phase 2.5)
- [ ] Phase 1 verification milestone per SDD §13.2

---

## Phase 1.5 — HID Module + Tier 2 Bridge Bring-Up

### Module 1C — USB HID Protocol Analyzer

- [ ] Design doc · BOM · PCB · assembly · firmware · bring-up · service
  - Architecture: dual-Pico bridge

### Tier 2 bridge stack (Tang Primer 25K + Pico)

- [ ] Bridge module PCB (Pico master + SPI 30 MHz to Tang Primer + USB-TMC pass-through)
- [ ] PCB fab + assembly
- [ ] Tang Primer placeholder HDL + Pico bridge firmware
- [ ] `*IDN?` query through bridge returns placeholder string
- [ ] Phase 1.5 verification milestone per SDD §13.3

---

## Phase 1.7 — Module 1H DMM

### Module 1H — Multi-Function DMM

- [ ] Design doc · BOM · PCB · assembly · firmware · bring-up · per-range calibration · service
  - Front-end: ADS1256 24-bit ADC + relay-switched multi-range network on ±12 V rails
- [ ] Phase 1.7 verification milestone per SDD §13.3.5: 9 V battery, 1 kΩ ±1 % reference, 1 kHz sine from 1E all read within stated module accuracy

---

## Phase 2 — Tier 2 Core (2A, 2B, 2C, 2D)

Four primary Tier 2 modules using the bridge stack from Phase 1.5. Each adds Tang Primer 25K HDL alongside the Pico bridge firmware (synthesis on shared FPGA per project rule).

### Module 2A — Logic Analyzer

- [ ] Design doc · BOM · PCB · assembly · HDL (capture + buffer + SPI register IF) · firmware · bring-up · service

### Module 2B — Protocol Exerciser / Analyzer

- [ ] Design doc · BOM · PCB · assembly · HDL (protocol bit-banger + decoder) · firmware · bring-up · service

### Module 2C — Frequency Counter

- [ ] Design doc · BOM · PCB · assembly · HDL (count state machine) · firmware · bring-up · TCXO calibration via GPSDO · service

### Module 2D — Ethernet MAC and Network Analyzer

- [ ] Design doc · BOM · PCB · assembly · HDL (MAC frame analyzer) · firmware · bring-up · service

### Phase 2 verification milestone (SDD §13.4)

- [ ] All Tier 2 modules enumerate and respond to `*IDN?`
- [ ] Trigger bus tested (2A capturing on 1E sync edge)
- [ ] InfluxDB receives capture records from each Tier 2 module

---

## Phase 2.5 — Module 2E Digitizer

### Module 2E — Mixed-Signal Digitizer / Oscilloscope

- [ ] Design doc · BOM · PCB · assembly · HDL (ADC capture + trigger logic) · firmware · bring-up · calibration (offset, gain, bandwidth) · service
  - Front-end: high-speed multi-channel ADC + analog conditioning on ±5 V or ±12 V rails

### Phase 2.5 system tests (SDD §13.5)

- [ ] Audio analyzer recipe full: 1E sweep stimulus + 2E capture + Pi 5 FFT (THD/SFDR/IMD) → InfluxDB → Grafana → report
- [ ] Firestick boot capture: 5 V rail transient via 2E

---

## Phase 3 — v1.1 Tier 1 (1F, 1G)

### Module 1F — High-Voltage Differential Probe

- [ ] Design doc · HV safety review · BOM · PCB · assembly · firmware · bring-up (low-V → ramp to ±300 V) · calibration · service
  - Front-end: AD8421 instrumentation amp + 100:1 attenuator on ±12 V rails
- [ ] Document v1.2 fully-isolated variant as future enhancement

### Module 1G — IR Capture and Transmit

- [ ] Design doc · BOM · PCB · assembly · firmware (NEC, RC5, Sony SIRC encode/decode) · bring-up · service

### Phase 3 verification milestone

- [ ] Full v1.0 + v1.1 catalog enumerates correctly
- [ ] Cross-module integration recipe (e.g., 1F captures HV transient triggered by 1E AWG sync)

---

## Phase 4 — Tier 3 (Deferred)

Gated on a future FPGA-upgrade decision. Not on the v1.0 + v1.1 critical path.

- [ ] FPGA selection: Tang Mega 138K Pro vs AX7325B
- [ ] Pi Zero 2 W streaming sidecar architecture
- [ ] Chassis LAN switch re-evaluation
- [ ] Tier 3 modules: 3A (USB 2.0 protocol analyzer), 3B (HDMI sideband), 3C (USB-C CC analyzer)

---

## Cross-Cutting

Continuous work that spans phases.

### Documentation

- [x] System Design Document v1.0
- [x] Chassis Architecture and Power Distribution doc
- [x] Module 1E Design Document v1.1
- [x] Module Design Document Schema (form-factor convention)
- [x] PMVB figure style guide + figure legend
- [x] Figure 4-1 (top-level system block, TikZ)
- [x] Chassis block diagram (TikZ, with analog/digital module split)
- [x] Module 1E figures (×3)
- [ ] Per-module figures for 1A / 1B / 1C / 1D / 1F / 1G / 1H / 2A / 2B / 2C / 2D / 2E (one functional block diagram per module, more if module is complex)
- [ ] Front-panel cutout DXF (chassis re-cut once module faceplate I/O converges)
- [ ] SDD revision history maintained as architecture evolves

### Firmware infrastructure

- [ ] SCPI YAML schema specification (canonical command-set definition format)
- [ ] YAML → C parser + YAML → PyVISA-sim backend codegen pipeline (one source feeds firmware and simulator)
- [ ] TinyUSB / Pico 2 W USB-TMC integration recipe
- [ ] Common module firmware template + Pico build pipeline (CMake + RP2350 SDK)
- [ ] Calibration record format (YAML in Pico flash, sync to InfluxDB)
- [ ] Firmware version reporting via `*IDN?` (module ID + firmware hash + build date)

### Verification infrastructure

- [ ] pytest fixtures for module discovery (PyVISA `ResourceManager` listing → per-module fixture)
- [ ] InfluxDB schema + tag taxonomy (`bench`, `module_id`, `run_id`, `dut_id`, `measurement_type`)
- [ ] System test recipe catalog (audio analyzer, power sequencing, Firestick boot, etc.)
- [ ] Optional: GitHub Actions CI (firmware build + pytest with simulator backend)

### Bench infrastructure

- [x] Fluke 87V calibrated DMM on hand (confirm cal currency periodically)
- [ ] GPSDO 10 MHz reference (Leo Bodnar mini, ~$50) — needed for Module 2C
- [ ] Bench oscilloscope for live verification during module bring-up
- [ ] Calibrated voltage reference (LM399-based or commercial precision reference)
- [ ] Variable AC supply for HV testing (Module 1F)
- [ ] Soldering equipment audit (iron, hot air, flux, paste, tweezers, ESD wrist strap)
- [ ] ESD-safe workstation setup

### Build / sourcing logistics

- [ ] Inventory tracker (parts on hand / ordered / incoming)
- [ ] Sourcing aggregator (consolidate Mouser/Digi-Key orders to minimize shipping)
- [ ] Receive-and-verify checklist for each order

### Project tooling

- [x] [Module Design Document Schema](docs/templates/Module_Design_Document_SCHEMA.md) (gitignored, local-only)
- [x] `docs/figures/build-all.ps1` — TikZ figure batch build
- [x] `docs/chassis/build-html.ps1` — chassis arch markdown→HTML render (requires pandoc)
- [ ] Install pandoc on Windows for local HTML rendering (or accept render-via-sandbox workflow)

---

## Notes

Per-module time varies significantly: Module 1E (analog, complex topology) takes ~3-5× the work of Module 1A (digital, simple). Adjust expectations during execution.

Phase boundaries are dependency-driven, not calendar-driven: Phase 1 needs Phase 0, Phase 2 needs Phase 1.5's bridge, etc. Calendar pace is set by build cadence and life context.
