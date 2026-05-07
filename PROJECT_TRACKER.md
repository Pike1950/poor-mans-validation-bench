# PMVB Project Tracker

This file is the persistent task list for the Poor Man's Validation Bench. It tracks every step from current state through full v1.0 + v1.1 buildout (and notes the deferred Tier 3 / Phase 4 work). Top-level structure mirrors the build phases defined in the [SDD section 13](docs/system-design/System_Design_Document.html#build-phases-and-investment-roadmap); within each phase, sub-tasks are grouped by area (hardware sourcing, mechanical assembly, firmware, software, test, documentation).

**Status legend:**

- `[ ]` not started
- `[~]` in progress
- `[x]` complete
- `[!]` blocked (note in line what unblocks it)

**Conventions:**

- Items are intentionally fine-grained — most are single-session work units.
- When a task completes, update the status and (where useful) cite the commit hash that landed it.
- New tasks discovered mid-build should be added under the appropriate phase / area immediately.
- "Cross-Cutting" at the bottom holds work that doesn't bind to a single phase (firmware infrastructure, documentation maintenance, bench tooling).

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

---

## Phase 0 — Orchestration + Chassis Power

Phase 0 brings up the orchestration head (Pi 5 + software stack) and the chassis power subsystem to the point where a simulator-backed end-to-end test can write to InfluxDB, render a Grafana panel, and generate a Jinja2 report.

### Architectural decisions (mostly settled)

- [x] System Design Document v1.0 published (see [SDD](docs/system-design/System_Design_Document.html))
- [x] Drop chassis LAN switch from v1.0 baseline (move to Phase 4)
- [x] TFX (TX300) is analog-rail backbone, not chassis-wide power
- [x] Pi 5 from own 27 W USB-C charger; Sabrent hub from own brick
- [x] Pi 5 ↔ USB hub link is USB 3.0
- [x] Chassis architecture: open-frame acrylic blade case, laser-cut from SendCutSend
- [x] Module form factor locked: 16.5 × 125 × 86 mm body, C-shape cross-section, 22.5 mm slot pitch, 21.5 mm component-stack budget, PCB-against-right-wall convention
- [x] Module Design Document Schema authored

### Chassis hardware sourcing (verified BOM)

- [x] Silverstone TX300 PSU on hand
- [ ] GeeekPi D-1188 ATX breakout — Amazon B08MC389FQ, $13
- [ ] Sabrent HB-BU10 USB 3.0 hub — Amazon B0797NZFYP, $47
- [ ] Phoenix Contact MC 1,5/4-G-3,81 PCB headers (qty 14) — Digi-Key 277-1208-ND, $3.51 each
- [ ] Phoenix Contact MC 1,5/4-ST-3,81 cable plugs (qty 14) — Digi-Key 277-1163-ND, $8.73 each
- [ ] Eaton BK/HTB-22M-R panel-mount fuse holders (qty 3) — Digi-Key 283-3041-ND, $4.20 each
- [ ] Bel BK1/GMC slow-blow fuses 5×20 mm (5 A, 3 A, 0.5 A, ~5 each rating) — Digi-Key
- [ ] Pomona 3760 banana jacks (red, yellow, blue, black) — Digi-Key 501-1041-ND family, ~$5 each × 4
- [ ] VCC 5102H1-5V LED indicator (+5 V OK, red) — Digi-Key L10021-ND, $1.92
- [ ] VCC 5102H1-12V LED indicator (+12 V OK, red) — Digi-Key 5102H1-12V-ND, $1.92
- [ ] VCC 5102H5-12V LED indicator (−12 V OK, green) — Digi-Key 5102H5-12V-ND, $1.92
- [ ] 14 AWG stranded hookup wire (red, yellow, blue, black; ~1.5 m each) — Mouser Alpha 3050 series
- [ ] 22 AWG stranded hookup wire (assorted colors, ~30 m total) — Mouser
- [ ] M3 corner standoffs 12 mm (qty 16) — Amazon or Mouser
- [ ] M3 × 6 mm screws (qty ~32) — Amazon or Mouser
- [ ] M3 × 12 mm screws (qty 8) — Amazon or Mouser
- [ ] USB-C-to-USB-A short cables, ~150 mm (qty 14) — Amazon
- [x] Heat-shrink tubing assortment (ElectroBits Thin Wall, on hand)

### Chassis mechanical fabrication

- [x] Tinkercad reference design committed (chassis envelope, module envelope, slot grooves, vent grid)
- [ ] Generate DXF for SendCutSend from Tinkercad / Inkscape
- [ ] Front-panel module-faceplate cutouts deferred until module designs converge (revisit after Modules 1A/1B/1D/1E faceplate I/O committed)
- [ ] Order acrylic frame from SendCutSend (~$40-80 + shipping)
- [ ] Receive acrylic cuts and verify dimensions match DXF
- [ ] Order standoffs/screws hardware kit from Amazon

### Chassis assembly

- [ ] Frame assembly: corner standoffs + side walls + base plate + top plate
- [ ] Mount TX300 to floor plate (4× M3 standoffs, IEC inlet facing front)
- [ ] Mount GeeekPi D-1188 on top of TX300 rear (4× M3 × 6 mm)
- [ ] Connect TX300 24-pin ATX cable to GeeekPi 24-pin input
- [ ] Mount Sabrent HB-BU10 to floor plate at rear-center (VHB-tape standoffs + M3)
- [ ] Build per-rail fuse panel (perfboard or terminal-block strip, 3 × Eaton holders + cartridges)
- [ ] Wire GeeekPi outputs through fuse panel to back-wall harness origin
- [ ] Build 4-wire back-wall harness (303 mm × 14 AWG, color-coded, ~22.5 mm tap intervals)
- [ ] Install Pomona banana jacks in front-panel strip (4 holes, 4 jacks, color-coded)
- [ ] Wire banana jacks to post-fuse rails
- [ ] Install VCC LED indicators in front-panel strip (3 holes, 3 LEDs)
- [ ] Wire LEDs to post-fuse rails

### Chassis bring-up

- [ ] Visual + continuity tests with mains disconnected
- [ ] Mains-only AC test (TX300 in standby, fan does not spin, no DC at outputs)
- [ ] DC at no load (toggle PS_ON# via GeeekPi, verify rail voltages at fuse outputs)
- [ ] Verify all 3 front-panel LEDs illuminate
- [ ] Verify all 4 banana-jack test points read correct rail voltages
- [ ] Verify back-wall harness rail voltages at every Phoenix plug position

### Pi 5 hardware

- [x] Raspberry Pi 5 16 GB price verified at Microcenter ($305)
- [x] Order / receive Pi 5 16 GB
- [x] Order Pi 5 official 27 W USB-C charger ($15)
- [x] Order active cooler / heatsink ($5)
- [x] Order 32 GB microSD card ($8)
- [x] Order Raspberry Pi M.2 HAT+ ($12)
- [x] Order 512 GB NVMe SSD M.2 2230 or 2242 ($40)
- [x] Assemble Pi 5: install heatsink, M.2 HAT+, NVMe SSD

### Pi 5 software stack (Raspberry Pi OS 64-bit)

- [ ] Flash Raspberry Pi OS 64-bit (Bookworm or current) to microSD
- [ ] Initial boot: hostname, locale, network, SSH enable
- [ ] Wired Ethernet to bench network confirmed
- [ ] Boot from NVMe SSD (rpi-clone or `raspi-config` to migrate)
- [ ] System update (`apt update && apt upgrade`)
- [ ] Python 3.11+ environment (`python3 --version`, `venv` or `pipx`)
- [ ] PyVISA install (`pip install pyvisa pyvisa-py`)
- [ ] USB-TMC kernel/permissions: `usbtmc` udev rule for non-root access
- [ ] Pytest install (`pip install pytest`)
- [ ] InfluxDB 1.8 install + service running
- [ ] InfluxDB PMVB schema: bench-name + measurement-type + run-id + DUT-id tags
- [ ] Grafana install (apt or Docker) + admin password set + InfluxDB datasource configured
- [ ] Grafana placeholder dashboard ("PMVB Bench Status")
- [ ] Jinja2 install (`pip install jinja2 matplotlib`)
- [ ] Report-template skeleton (HTML + PDF rendering of an InfluxDB query)
- [ ] MCP gateway scaffolding (Anthropic MCP Python SDK, basic SCPI tool surface stub)

### Phase 0 verification milestone (per SDD §13.1)

- [ ] Pi 5 boots from NVMe and reaches the bench network
- [ ] Pi 5 USB hub (Sabrent) shows up via `lsusb` with USB 3.0 enumeration confirmed
- [ ] PyVISA-sim test: instantiate a placeholder backend, query `*IDN?`, return placeholder response
- [ ] InfluxDB write: pytest writes a measurement record, query confirms it landed
- [ ] Grafana panel renders the InfluxDB record live
- [ ] Jinja2 report generator produces a sample HTML/PDF report from the InfluxDB record
- [ ] End-to-end: pytest test calls `*IDN?` → writes result to InfluxDB → Grafana shows it → report references it

### Phase 0 documentation

- [x] [Chassis Architecture and Power Distribution doc](docs/chassis/Chassis_Architecture_and_Power_Distribution.html)
- [x] [SDD §11.5 Power Architecture](docs/system-design/System_Design_Document.html#power-architecture) updated with new power tree
- [ ] Pi 5 setup notes (gitignored — host-specific paths/credentials)
- [ ] Phase 0 bring-up record (date, observed rail voltages, blocked-on items)

---

## Phase 1 — Tier 1 Core (1A, 1B, 1D, 1E)

Phase 1 builds the four foundational Tier 1 modules using the chassis from Phase 0. Each module follows the same per-module work breakdown.

### Module 1A — Digital I/O Controller

- [ ] Design doc per [Module Design Document Schema](docs/templates/Module_Design_Document_SCHEMA.md)
  - [ ] §1 Theory of Operation
  - [ ] §2 Functional Block Diagram (TikZ)
  - [ ] §3 Schematic Notes
  - [ ] §4 Pin Assignments
  - [ ] §5 Specifications (mirror SDD spec table)
  - [ ] §6 Sample Applications (≥3)
  - [ ] §7 BOM (Mouser/Digi-Key verified)
  - [ ] §8 Calibration Procedure (if applicable)
  - [ ] §9 Bring-Up Checklist
  - [ ] §10 Known Issues (populate as built)
  - [ ] §11 References
- [ ] BOM ordered (Mouser/Digi-Key)
- [ ] PCB schematic captured in KiCad
- [ ] PCB layout per form factor (17 × 125 × 80 mm + lips, M3 mounting holes, USB on right edge, Phoenix on top-rear corner)
- [ ] PCB DRC + Gerber export
- [ ] PCB fab order (JLCPCB or PCBWay)
- [ ] Component assembly
- [ ] Firmware: SCPI YAML schema
- [ ] Firmware: SCPI parser + USB-TMC + GPIO command handlers
- [ ] Firmware build + flash to Pico 2 W
- [ ] Bring-up: power on, USB enumeration, `*IDN?` smoke test
- [ ] Bring-up: full functional test sweep per module checklist
- [ ] Calibration (if applicable) + record stored
- [ ] PyVISA-sim parity verified
- [ ] Module enters service

### Module 1B — Voltage Measurement Unit

- [ ] Design doc per Module Design Document Schema (same 11 sections)
- [ ] BOM ordered
- [ ] PCB schematic + layout
- [ ] PCB fab order
- [ ] Component assembly (Pico + ADS1115 + instrumentation amp + ±12 V analog rails)
- [ ] Firmware: SCPI YAML + parser + voltage-measurement command handlers
- [ ] Firmware build + flash
- [ ] Bring-up checklist
- [ ] Calibration (DC offset, gain, linearity)
- [ ] PyVISA-sim parity
- [ ] Module enters service

### Module 1D — Source-Measure Unit Lite

- [ ] Design doc per Module Design Document Schema
- [ ] BOM ordered
- [ ] PCB schematic + layout
- [ ] PCB fab order
- [ ] Component assembly (Pico + DAC + force/sense op-amps + ±12 V rails)
- [ ] Firmware: SCPI YAML + parser + force/measure command handlers
- [ ] Firmware build + flash
- [ ] Bring-up checklist
- [ ] Calibration (force voltage, sense voltage, sense current)
- [ ] PyVISA-sim parity
- [ ] Module enters service

### Module 1E — Function Generator / AWG

- [x] Design doc v1.1 published — [Module 1E Design Document](docs/modules/Module_1E_Design_Document.html)
- [x] BOM verified at Digi-Key + Microcenter ($53 module total, 2026-05-07)
- [x] Functional figures published (system context, AD9742 internal, typical app)
- [ ] BOM ordered
- [ ] PCB schematic captured in KiCad (AD9742 + AD8056 + reconstruction filter + reed relay SP3T)
- [ ] PCB layout per form factor
- [ ] PCB DRC + Gerber export
- [ ] PCB fab order (JLCPCB)
- [ ] Component assembly (Pico + AD9742 TSSOP + AD8056 SOIC + 3× Coto 9007 reeds + filter passives)
- [ ] Firmware: SCPI YAML schema (sine, square, triangle, ramp, noise, multitone, ARB, sweep)
- [ ] Firmware: PIO + DMA waveform streaming at 30–50 MSPS
- [ ] Firmware: SCPI parser + USB-TMC + waveform command handlers
- [ ] Firmware build + flash
- [ ] Bring-up: visual inspection, power-on without DUT, midscale DC test, full-scale DC test
- [ ] Bring-up: sine sweep tests at 1 kHz, 1 MHz, 10 MHz
- [ ] Bring-up: frequency response sweep + THD audio band + spectral purity HF band
- [ ] Bring-up: impedance switch test (50 Ω / 600 Ω / 10 kΩ verification)
- [ ] Calibration (DC offset, gain, frequency, filter passband flatness)
- [ ] PyVISA-sim parity
- [ ] Module enters service

### Phase 1 system tests

- [ ] Audio analyzer recipe (partial: 1E stimulus + 1B slow integration to confirm DC offset of Bravo Audio Ocean DUT)
- [ ] Phase 1 verification milestone per SDD §13.2

---

## Phase 1.5 — HID Module + Tier 2 Bridge Bring-Up

Phase 1.5 adds Module 1C (USB HID Analyzer) and stands up the Tier 2 bridge architecture without yet implementing any Tier 2 instrument logic.

### Module 1C — USB HID Protocol Analyzer

- [ ] Design doc per Module Design Document Schema
- [ ] BOM ordered (dual-Pico architecture)
- [ ] PCB schematic + layout
- [ ] PCB fab order
- [ ] Component assembly
- [ ] Firmware: dual-Pico bridge + HID protocol decode
- [ ] Firmware build + flash
- [ ] Bring-up
- [ ] Module enters service

### Tier 2 bridge stack (Tang Primer 25K + Pico)

- [ ] Tang Primer 25K FPGA on hand confirmed
- [ ] Bridge module PCB design (Pico master + SPI 30 MHz to Tang Primer + USB-TMC pass-through)
- [ ] Bridge module PCB fab + assembly
- [ ] Tang Primer placeholder HDL (returns hardcoded register values over SPI)
- [ ] Pico bridge firmware (USB-TMC client, SPI master, register-read pass-through)
- [ ] `*IDN?` query through the bridge returns placeholder string
- [ ] Phase 1.5 verification milestone per SDD §13.3

---

## Phase 1.7 — Module 1H DMM

Phase 1.7 adds the Multi-Function DMM. Separated from Phase 1 because 1H requires custom relay-switched analog front-end work and per-range calibration that need more bring-up time.

### Module 1H — Multi-Function DMM

- [ ] Design doc per Module Design Document Schema
- [ ] BOM ordered (Pico + ADS1256 24-bit ADC + relay-switched range network + ±12 V rails)
- [ ] PCB schematic + layout (multi-range DC voltage, AC voltage, resistance, current — relay range switching)
- [ ] PCB fab order
- [ ] Component assembly
- [ ] Firmware: SCPI YAML (range commands, function selection, autorange)
- [ ] Firmware: ADS1256 driver + range relay driver + measurement loop
- [ ] Firmware build + flash
- [ ] Bring-up checklist
- [ ] Per-range calibration (DC voltage ranges, resistance ranges, current ranges)
- [ ] Phase 1.7 verification milestone per SDD §13.3.5: 9 V battery, 1 kΩ ±1 % reference, 1 kHz sine from 1E all read within stated module accuracy

---

## Phase 2 — Tier 2 Core (2A, 2B, 2C, 2D)

Phase 2 adds the four primary Tier 2 modules using the bridge stack from Phase 1.5. Each module includes Tang Primer 25K HDL alongside the Pico bridge firmware.

### Module 2A — Logic Analyzer

- [ ] Design doc per Module Design Document Schema
- [ ] BOM ordered
- [ ] PCB schematic + layout (Pico + Tang Primer + level-shifted digital inputs + RAM if needed)
- [ ] PCB fab order
- [ ] Component assembly
- [ ] HDL: capture state machine + sample buffer (Verilog, synthesized via shared Tang Primer per project rule)
- [ ] HDL: SPI register interface
- [ ] Firmware: bridge + capture command handlers + buffer transfer
- [ ] Firmware build + flash
- [ ] Bring-up checklist
- [ ] Module enters service

### Module 2B — Protocol Exerciser / Analyzer

- [ ] Design doc per Module Design Document Schema
- [ ] BOM ordered
- [ ] PCB schematic + layout
- [ ] PCB fab order
- [ ] Component assembly
- [ ] HDL: protocol bit-banger + decoder
- [ ] Firmware: bridge + protocol command handlers
- [ ] Bring-up checklist
- [ ] Module enters service

### Module 2C — Frequency Counter

- [ ] Design doc per Module Design Document Schema
- [ ] BOM ordered (TCXO reference, level-shifted input)
- [ ] PCB schematic + layout
- [ ] PCB fab order
- [ ] Component assembly
- [ ] HDL: frequency-count state machine
- [ ] Firmware: bridge + count command handlers
- [ ] Bring-up + TCXO calibration via GPSDO
- [ ] Module enters service

### Module 2D — Ethernet MAC and Network Analyzer

- [ ] Design doc per Module Design Document Schema
- [ ] BOM ordered
- [ ] PCB schematic + layout (Pico + Tang Primer + Ethernet PHY)
- [ ] PCB fab order
- [ ] Component assembly
- [ ] HDL: MAC frame analyzer
- [ ] Firmware: bridge + frame capture command handlers
- [ ] Bring-up checklist
- [ ] Module enters service

### Phase 2 verification milestone (SDD §13.4)

- [ ] All 4 Tier 2 modules enumerate and respond to `*IDN?`
- [ ] Trigger bus tested with Module 2A capturing on a Module 1E AWG sync edge
- [ ] InfluxDB receives capture records from each Tier 2 module

---

## Phase 2.5 — Module 2E Digitizer

Phase 2.5 adds Module 2E (Mixed-Signal Digitizer / Oscilloscope) which enables the headline audio-analyzer recipe and consumer-electronics rail-capture workflows.

### Module 2E — Mixed-Signal Digitizer / Oscilloscope

- [ ] Design doc per Module Design Document Schema
- [ ] ADC selection (high-speed multi-channel; e.g., AD9226 or similar)
- [ ] BOM ordered
- [ ] PCB schematic + layout (Pico + Tang Primer + ADC + analog front-end with ±5 V or ±12 V rails)
- [ ] PCB fab order
- [ ] Component assembly
- [ ] HDL: ADC sample state machine + capture buffer + trigger logic
- [ ] HDL: trigger bus interface (sync to Module 1E AWG, Module 2A logic edges)
- [ ] Firmware: bridge + capture/trigger command handlers + sample-stream transfer
- [ ] Bring-up checklist
- [ ] Calibration (offset, gain, bandwidth)
- [ ] Module enters service

### Phase 2.5 system tests

- [ ] Audio analyzer recipe full: 1E (swept sine stimulus) + 2E (capture) + Pi 5 FFT (THD, SFDR, IMD) → InfluxDB → Grafana → report
- [ ] Firestick boot capture: 5 V rail transient measurement using 2E
- [ ] Phase 2.5 verification milestone per SDD §13.5

---

## Phase 3 — v1.1 Tier 1 (1F, 1G)

Phase 3 adds the v1.1 expansion modules to fill out the Tier 1 catalog.

### Module 1F — High-Voltage Differential Probe

- [ ] Design doc per Module Design Document Schema
- [ ] BOM ordered (Pico + AD8421 instrumentation amp + 100:1 attenuator network + ±12 V rails)
- [ ] HV safety review (insulated banana jacks, creepage and clearance, no operator access to high-voltage nodes)
- [ ] PCB schematic + layout
- [ ] PCB fab order
- [ ] Component assembly
- [ ] Firmware: bridge + HV measurement command handlers
- [ ] Bring-up checklist (start with low-voltage tests, ramp to ±300 V differential)
- [ ] Calibration (gain ratio, offset, common-mode rejection)
- [ ] Module enters service
- [ ] Document v1.2 fully-isolated variant as future enhancement (optical signal isolation + transformer-isolated DC-DC for front-end)

### Module 1G — IR Capture and Transmit

- [ ] Design doc per Module Design Document Schema
- [ ] BOM ordered (Pico + IR receiver + IR LED + drive transistor)
- [ ] PCB schematic + layout
- [ ] PCB fab order
- [ ] Component assembly
- [ ] Firmware: bridge + IR encode/decode command handlers (NEC, RC5, Sony SIRC protocols)
- [ ] Bring-up checklist
- [ ] Module enters service

### Phase 3 verification milestone

- [ ] Full v1.0 + v1.1 module catalog enumerates correctly
- [ ] Cross-module integration recipe (e.g., 1F captures HV transient triggered by 1E AWG sync)

---

## Phase 4 — Tier 3 (Deferred)

Phase 4 is gated on a future decision to upgrade FPGA capability and add streaming sidecars. Not on the v1.0 + v1.1 critical path.

### Architecture decisions

- [ ] FPGA choice: Tang Mega 138K Pro vs AX7325B vs other
- [ ] Pi Zero 2 W streaming sidecar architecture for sub-USB-TMC throughput modules
- [ ] Chassis LAN switch decision (re-evaluate vs Tier 3 streaming requirements)

### Tier 3 modules (3A — USB 2.0 Protocol Analyzer, 3B — HDMI Sideband, 3C — USB-C CC Analyzer)

- [ ] Per-module design docs + BOM + PCB + firmware + bring-up (deferred)

---

## Cross-Cutting

Work that spans phases and runs continuously rather than as a phase milestone.

### Documentation maintenance

- [x] System Design Document v1.0 — [SDD](docs/system-design/System_Design_Document.html)
- [x] Chassis Architecture and Power Distribution doc — [chassis arch](docs/chassis/Chassis_Architecture_and_Power_Distribution.html)
- [x] Module 1E Design Document v1.1
- [x] Module Design Document Schema (template + form-factor convention)
- [x] PMVB figure style guide
- [x] PMVB figure legend
- [x] Figure 4-1 (top-level system block, TikZ)
- [x] Chassis block diagram (TikZ, with analog/digital module split)
- [x] Module 1E figures (system context, AD9742 datasheet embed, typical application)
- [ ] Module 1A figures (functional block + any module-specific)
- [ ] Module 1B figures
- [ ] Module 1D figures
- [ ] Module 1F figures
- [ ] Module 1G figures
- [ ] Module 1H figures
- [ ] Module 1C figures
- [ ] Module 2A figures
- [ ] Module 2B figures
- [ ] Module 2C figures
- [ ] Module 2D figures
- [ ] Module 2E figures
- [ ] Front-panel cutout DXF (chassis re-cut once module faceplate I/O converges)
- [ ] SDD revisions as architecture evolves (track in revision history section)

### Firmware infrastructure

- [ ] SCPI YAML schema specification (canonical command-set definition format)
- [ ] YAML → C parser code generator (one shared codegen pipeline for all modules)
- [ ] YAML → PyVISA-sim backend generator (same source feeds simulator and firmware)
- [ ] TinyUSB integration recipe for Pico 2 W (USB-TMC class implementation)
- [ ] Common module firmware template (per-module customizes only command handlers + YAML)
- [ ] Pico build pipeline (CMake + RP2350 SDK, single-command build per module)
- [ ] Calibration record format (YAML in Pico flash, sync to InfluxDB)
- [ ] Firmware version reporting via `*IDN?` (module ID, firmware hash, build date)

### Verification infrastructure

- [ ] pytest fixtures for module discovery (PyVISA `ResourceManager` listing → per-module fixture)
- [ ] InfluxDB schema for measurement records (tag taxonomy: `bench`, `module_id`, `run_id`, `dut_id`, `measurement_type`)
- [ ] Calibration record schema and sync flow
- [ ] System test recipe catalog (audio analyzer, power sequencing, Firestick boot capture, etc.)
- [ ] CI for firmware + software (GitHub Actions on push: build firmware, run pytest with simulator backend) — optional
- [ ] PyVISA-sim CI integration (every module's YAML must round-trip through the simulator before being merged)

### Bench infrastructure

- [x] Fluke 87V calibrated DMM (on hand — confirm cal currency periodically)
- [ ] GPSDO 10 MHz reference for Module 2C frequency calibration (Leo Bodnar mini, ~$35-50)
- [ ] Bench oscilloscope for live verification during module bring-up
- [ ] Calibrated voltage reference (e.g., LM399-based or commercial precision reference)
- [ ] Variable AC supply for HV testing (when Module 1F is built)
- [ ] Soldering equipment audit: iron, hot air, flux, solder paste, tweezers, ESD wrist strap
- [ ] ESD-safe workstation setup (mat + wrist strap + grounded outlet)

### Build / sourcing logistics

- [ ] Inventory tracking spreadsheet (parts on hand, parts ordered, parts incoming)
- [ ] Sourcing aggregator: consolidate Mouser/Digi-Key orders before ordering to minimize shipping
- [ ] Receive-and-verify checklist for each order (count parts, check labels, verify part numbers)

### Project tooling

- [x] [Module Design Document Schema](docs/templates/Module_Design_Document_SCHEMA.md) (gitignored — local tooling only)
- [x] `docs/figures/build-all.ps1` — TikZ figure batch build
- [x] `docs/chassis/build-html.ps1` — chassis arch markdown→HTML render (requires pandoc)
- [ ] Install pandoc on Windows for local HTML rendering (or accept render-via-sandbox workflow)
- [ ] Project tracker review cadence (monthly? at each phase milestone?)

---

## Notes

This tracker is intentionally optimistic about the per-module work breakdown — the actual time per module varies a lot. Module 1E (analog, complex) probably takes 3–5x longer per work-step than Module 1A (digital, simple). Adjust expectations during execution.

Phase boundaries are dependency-driven, not calendar-driven: Phase 1 needs Phase 0 to land, Phase 2 needs Phase 1.5's bridge stack, etc. Calendar pace is set by build cadence and life context.
