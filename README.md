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
- [x] GeeekPi D-1188 mounted to chassis ceiling via 4× M2.5 × 5 mm standoffs (rotated 90° so terminal blocks face chassis front, status LEDs face rear). Mounting holes at (110.1, 161.6), (162.9, 161.6), (110.1, 225.4), (162.9, 225.4) on both ceiling and top groove plate
- [x] Sabrent HB-BU10 actual dimensions verified: 144.8 × 48.3 × 23.9 mm. Positioned at X = 102.6..247.4, Y = 175.4..223.7, Z = 6..29.9 (rear-center on chassis floor)
- [x] Back-wall harness taps: Wago 221-413 lever-nut connectors for v1.0 (one per rail per module). Custom 4-rail distribution PCB deferred to v1.1+ once layout is verified
- [x] Module Design Document Schema authored (local tooling)

**Chassis sourcing**

Detailed rationale (gauge sizing, standoff stacking, fastener stack-up, Wago vs PCB tradeoff) lives in the [chassis architecture doc](https://pike1950.github.io/poor-mans-validation-bench/docs/chassis/Chassis_Architecture_and_Power_Distribution.html). This tracker is part + source + qty + price only.

- [x] GeeekPi D-1188 ATX breakout — Amazon B08MC389FQ ($13)
- [x] Sabrent HB-BU10 USB 3.0 hub — Amazon B0797NZFYP ($47)
- [x] Phoenix MC 1,5/4 connector pairs ×2 — Digi-Key 277-1208-ND + 277-1163-ND ($11.40)
- [x] Eaton BK/HTB-22M-R fuse holders ×3 + Bel BK1/GMC cartridges ×2 each (5 A / 3 A / 500 mA, in-service + spare) — Digi-Key 283-3041-ND + 283-BK1/GMC-{5,3,500}-R-ND ($28.79)
- Pomona 3760 banana jacks ×4 — *deferred to v1.1 diagnostic strip*; open-frame chassis gives direct access to fuse-panel terminals for DMM spot-checks
- [x] 12 AWG silicone wire kit, 6 colors × 5 ft — Fermerry, Amazon B089CJ65SC ($20.29)
- [x] 14 AWG silicone wire kit, 6 colors × 10 ft — Fermerry, Amazon ($20.96)
- [x] M3 standoff/screw/nut kit, 320 pc — Csdtylh, Amazon B06Y5TJXY1 ($14.98)
- [x] M2.5 standoff/screw/nut kit, 160 pc — HVAZI, Amazon B01L06CUJG ($11.99)
- [x] Blue 243 threadlocker, 50 mL — ESKONKE, Amazon B0CHM5QS3N ($9.99)
- [x] Wago 221-413 lever-nuts ×10 — Digi-Key 2946-221-413-ND ($6.45)
- [ ] USB-C-to-USB-A cables ×14, ~150 mm — Amazon (~$30)
- [x] 22 AWG signal wire on hand
- [x] LEDs for diagnostic strip on hand
- [x] Heat-shrink tubing on hand (ElectroBits)
- [x] Silverstone SST-TX300 TFX PSU — Amazon ($99.99), on hand

**Chassis fabrication + assembly**

Prototype-first iterative build: order chassis acrylic + one PLA module, slide-test the v10 lip-and-groove fit, then commit the JLCPCB batch order for 13 more modules and proceed with full assembly + harness. Module 1E is the first module to fully populate; Pi 5 software-stack work runs in parallel.

*Design tooling and fabrication files (complete)*

- [x] Tinkercad reference design + parametric DXF/STL generator (`tools/fabrication/generate_prototype_v10.py`, ezdxf + trimesh) producing `panel_solid_plate.dxf`, `panel_groove_plate.dxf`, `module_body_v10.stl`, `chassis_v10.stl`, `chassis_v10_assembled.stl`, `chassis_assembly_exploded.{stl,png}`

*Orders placed*

- [x] v10 prototype module — Baysinger's AM, $24.77, ETA May 14-19
- [x] Chassis acrylic — SendCutSend, $142.57
- [x] Amazon order (hardware + wire + threadlocker), $78.21, ETA May 12
- [x] Digi-Key order (Phoenix + fuse panel + Wago), $62.19, placed 2026-05-10

*Receive + slide-fit validation*

- [ ] Receive prototype module + chassis panels; verify dimensions match v10 spec
- [ ] Slide-fit test: insert one module into one slot, verify 0.5 mm sliding clearance on the lip-and-groove engagement
- [ ] If fail: edit generator-script constants, regenerate, re-order. If pass: order JLCPCB batch of 14 module bodies in PETG (~$84)

*Frame + component install*

- [ ] Build 4× M3 corner standoff stacks (per chassis doc §7.1)
- [ ] Acrylic frame stack assembly (per chassis doc §7.1)
- [ ] Install TX300, GeeekPi (ceiling-mounted), Sabrent (per chassis doc §3.3-3.5)
- [ ] Run 24-pin ATX cable TX300 → GeeekPi
- [ ] Build per-rail fuse panel + wire to GeeekPi outputs

*Harness + module shakedown*

- [ ] Build 4-wire back-wall harness (~330 mm × 14 AWG, color-coded). Tap slot 1 only for Module 1E shakedown via 4× Wago 221-413 (one per rail)
- [ ] Single-slot shakedown: install Module 1E, verify Phoenix mate + USB cable run + harness tap
- [ ] On pass: add Wago taps at remaining 13 slots (52 more Wagos, total 56)
- [ ] Install front-panel diagnostic strip (×4 banana jacks + ×3 LED indicators) on a small acrylic strip on the chassis floor

*Deferred to v1.1:* chassis side walls, rear wall, front panel, ventilation geometry, module-specific faceplate cutouts, custom 4-rail distribution PCB. Walls + vents must be co-designed because closing the chassis re-introduces TX300 cooling constraints.

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

- [x] Raspberry Pi OS Full 64-bit install + headless config (Wi-Fi, SSH key-only auth, Raspberry Pi Connect enabled)
- [x] Boot migration to NVMe SSD (NVMe-first via EEPROM `BOOT_ORDER`, SD card retained as fallback)
- [x] Bootstrap Python project (`pyproject.toml` + `pmvb/` package + `.venv` on Pi)
- [x] InfluxDB 2.x install + service + `pmvb` org + `measurements` bucket + SDD §10.2 tag schema (Flux)
- [x] Grafana 10+ install + InfluxDB datasource (Pi 5 reference build runs Grafana 13)
- [x] Jinja2 + Matplotlib report template skeleton (`pmvb/reports/`)
- [x] MCP gateway scaffolding (`pmvb/mcp_gateway/server.py`, FastMCP + `anthropic` SDK)
- [x] PyVISA-sim placeholder schema (`sim/placeholder/responses.yaml`) for Phase 0 sim path
- [x] pytest fixtures (`pmvb/fixtures.py`, `run_id` / `dut` / `record`) per SDD §10.3
- [x] InfluxDB I/O helpers (`pmvb/influx.py`) enforcing the SDD §10.2 tag taxonomy

**Pico firmware bring-up (hot-plug verification)**

Pulled forward from Phase 1: a throwaway probe firmware on every Pico so the Phase 0 verification can exercise the real USB-TMC path, not just the simulator. The stub is not the eventual per-module SCPI firmware; it just enumerates and answers `*IDN?` so we can prove the hot-plug-by-serial architecture works.

- [ ] Pico SDK + TinyUSB cross-compile environment on the Pi 5 (`arm-none-eabi-gcc`, `pico-sdk` at `/opt/pico-sdk`, `PICO_SDK_PATH` set)
- [ ] Minimal USB-TMC stub firmware at `firmware/pmvb_usbtmc_stub/`: responds to `*IDN?` with chip-ID-derived serial number
- [ ] Flash all 5 Picos with the stub `.uf2`
- [ ] udev rules: plugdev access to USB-TMC class devices + stable `/dev/usbtmc-by-serial/{chip_id}` symlinks + suppress BOOTSEL automount
- [ ] Hot-plug verification: same Pico across different Sabrent hub ports preserves serial-based identity in pyvisa-py enumeration

**Phase 0 verification milestone (per SDD §13.1)**

- [x] Pi 5 boots from NVMe, reaches bench network, Sabrent hub enumerates as USB 3.0
- [ ] End-to-end pytest: real Pico over pyvisa-py USB-TMC + pyvisa-sim placeholder, both write to InfluxDB tagged appropriately, Grafana panel renders both, Jinja2 report queries InfluxDB and outputs HTML+PDF referencing both records
- [ ] Hot-plug-by-serial verified across at least 3 port-swap permutations

**Phase 0 documentation**

- [x] Chassis Architecture and Power Distribution doc
- [x] SDD §11.5 Power Architecture
- [ ] Rewrite `docs/setup/Phase_0_Orchestration_Setup.md` from actual procedure (replaces the stale 2024-era version)

### Phase 1 — Tier 1 Core (1A, 1B, 1D, 1E)

Four foundational Tier 1 modules using the chassis from Phase 0. Each follows the per-module template.

- **Module 1A — Digital I/O Controller**:
  - [ ] Design doc
  - [ ] Block diagram
  - [ ] BOM verified at Digi-Key + Mouser
  - [ ] BOM ordered
  - [ ] PCB design (KiCad: Pico + level shifters + I/O protection)
  - [ ] PCB fab + assembly
  - [ ] Firmware (SCPI YAML for read/write/pulse, configurable per-pin direction)
  - [ ] Bring-up
  - [ ] Module enters service
- **Module 1B — Voltage Measurement Unit** (front-end: ADS1115 + instrumentation amp on ±12 V rails):
  - [ ] Design doc
  - [ ] Functional figures (system context + front-end schematic)
  - [ ] BOM verified at Digi-Key + Mouser
  - [ ] BOM ordered
  - [ ] PCB design (KiCad: ADS1115 + instrumentation amp + ±12 V analog supplies)
  - [ ] PCB fab + assembly
  - [ ] Firmware (SCPI YAML for voltage measurement, range selection, averaging)
  - [ ] Bring-up
  - [ ] Calibration (offset, gain across ranges)
  - [ ] Module enters service
- **Module 1D — Source-Measure Unit Lite** (front-end: DAC + force/sense op-amp loop on ±12 V rails):
  - [ ] Design doc
  - [ ] Functional figures
  - [ ] BOM verified at Digi-Key + Mouser
  - [ ] BOM ordered
  - [ ] PCB design (KiCad: 12-bit DAC + force/sense op-amp loop + ±12 V analog supplies)
  - [ ] PCB fab + assembly
  - [ ] Firmware (SCPI YAML for V-source/I-measure, sweep, IV-curve)
  - [ ] Bring-up
  - [ ] Calibration (V-source, I-measure across ranges)
  - [ ] Module enters service
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

- **Module 1C — USB HID Protocol Analyzer** (architecture: dual-Pico bridge):
  - [ ] Design doc
  - [ ] Block diagram
  - [ ] BOM verified at Digi-Key + Mouser
  - [ ] BOM ordered
  - [ ] PCB design (KiCad: dual Pico, USB-host on capture Pico, USB-device on target side)
  - [ ] PCB fab + assembly
  - [ ] Firmware (SCPI YAML for HID enumeration, capture, parse)
  - [ ] Bring-up
  - [ ] Module enters service
- **Tier 2 bridge stack (Tang Primer 25K + Pico)**:
  - [ ] Bridge module PCB design
  - [ ] PCB fab + assembly
  - [ ] Tang Primer placeholder HDL (verify Pico ↔ FPGA SPI link)
  - [ ] Pico bridge firmware (SCPI YAML pass-through skeleton)
  - [ ] `*IDN?` through bridge returns placeholder string
  - [ ] Phase 1.5 verification milestone per SDD §13.3

### Phase 1.7 — Module 1H DMM

- **Module 1H — Multi-Function DMM** (front-end: ADS1256 24-bit ADC + relay-switched multi-range network on ±12 V rails):
  - [ ] Design doc
  - [ ] Functional figures
  - [ ] BOM verified at Digi-Key + Mouser
  - [ ] BOM ordered
  - [ ] PCB design (KiCad: ADS1256 + relay-switched multi-range network + ±12 V analog supplies)
  - [ ] PCB fab + assembly
  - [ ] Firmware (SCPI YAML for DC V/I/R, AC V, continuity, frequency)
  - [ ] Bring-up
  - [ ] Per-range calibration
  - [ ] Module enters service
- [ ] Phase 1.7 verification milestone per SDD §13.3.5: 9 V battery, 1 kΩ ±1 % reference, 1 kHz sine from 1E all read within stated module accuracy

### Phase 2 — Tier 2 Core (2A, 2B, 2C, 2D)

Four primary Tier 2 modules using the bridge stack from Phase 1.5. Each adds Tang Primer 25K HDL alongside the Pico bridge firmware (synthesis on shared FPGA per project rule).

- **Module 2A — Logic Analyzer**:
  - [ ] Design doc
  - [ ] Functional figures
  - [ ] BOM verified at Digi-Key + Mouser
  - [ ] BOM ordered
  - [ ] PCB design (KiCad: probe inputs + level shifters + Tang Primer 25K)
  - [ ] PCB fab + assembly
  - [ ] HDL (sample capture FSM + sample buffer + SPI register interface)
  - [ ] Pico bridge firmware (SCPI YAML for capture/trigger/decode)
  - [ ] Bring-up
  - [ ] Module enters service
- **Module 2B — Protocol Exerciser / Analyzer**:
  - [ ] Design doc
  - [ ] Functional figures
  - [ ] BOM verified at Digi-Key + Mouser
  - [ ] BOM ordered
  - [ ] PCB design (KiCad: protocol I/O + level shifters + Tang Primer 25K)
  - [ ] PCB fab + assembly
  - [ ] HDL (protocol bit-banger + decoder)
  - [ ] Pico bridge firmware
  - [ ] Bring-up
  - [ ] Module enters service
- **Module 2C — Frequency Counter**:
  - [ ] Design doc
  - [ ] Functional figures
  - [ ] BOM verified at Digi-Key + Mouser
  - [ ] BOM ordered
  - [ ] PCB design (KiCad: input conditioning + TCXO + Tang Primer 25K)
  - [ ] PCB fab + assembly
  - [ ] HDL (count state machine, gate timing)
  - [ ] Pico bridge firmware
  - [ ] Bring-up
  - [ ] TCXO calibration via GPSDO
  - [ ] Module enters service
- **Module 2D — Ethernet MAC and Network Analyzer**:
  - [ ] Design doc
  - [ ] Functional figures
  - [ ] BOM verified at Digi-Key + Mouser
  - [ ] BOM ordered
  - [ ] PCB design (KiCad: PHY + magnetics + Tang Primer 25K)
  - [ ] PCB fab + assembly
  - [ ] HDL (MAC frame analyzer + buffer)
  - [ ] Pico bridge firmware
  - [ ] Bring-up
  - [ ] Module enters service

**Phase 2 verification milestone (SDD §13.4)**

- [ ] All Tier 2 modules enumerate and respond to `*IDN?`
- [ ] Trigger bus tested (2A capturing on 1E sync edge)
- [ ] InfluxDB receives capture records from each Tier 2 module

### Phase 2.5 — Module 2E Digitizer

- **Module 2E — Mixed-Signal Digitizer / Oscilloscope** (front-end: high-speed multi-channel ADC + analog conditioning on ±5 V or ±12 V rails):
  - [ ] Design doc
  - [ ] Functional figures
  - [ ] BOM verified at Digi-Key + Mouser
  - [ ] BOM ordered
  - [ ] PCB design (KiCad: high-speed ADC + analog conditioning + Tang Primer 25K)
  - [ ] PCB fab + assembly
  - [ ] HDL (ADC capture + trigger logic + sample buffer)
  - [ ] Pico bridge firmware (SCPI YAML for capture/trigger/FFT readback)
  - [ ] Bring-up
  - [ ] Calibration (offset, gain, bandwidth)
  - [ ] Module enters service

**Phase 2.5 system tests (SDD §13.5)**

- [ ] Audio analyzer recipe full: 1E sweep stimulus + 2E capture + Pi 5 FFT (THD/SFDR/IMD) → InfluxDB → Grafana → report
- [ ] Firestick boot capture: 5 V rail transient via 2E

### Phase 3 — v1.1 Tier 1 (1F, 1G)

- **Module 1F — High-Voltage Differential Probe** (front-end: AD8421 instrumentation amp + 100:1 attenuator on ±12 V rails; v1.2 fully-isolated variant noted as future enhancement):
  - [ ] Design doc
  - [ ] HV safety review
  - [ ] Functional figures
  - [ ] BOM verified at Digi-Key + Mouser
  - [ ] BOM ordered
  - [ ] PCB design (KiCad: AD8421 + 100:1 attenuator + ±12 V analog supplies)
  - [ ] PCB fab + assembly
  - [ ] Firmware (SCPI YAML for HV differential measurement)
  - [ ] Bring-up (low-V validation → ramp to ±300 V)
  - [ ] Calibration
  - [ ] Module enters service
- **Module 1G — IR Capture and Transmit**:
  - [ ] Design doc
  - [ ] Block diagram
  - [ ] BOM verified at Digi-Key + Mouser
  - [ ] BOM ordered
  - [ ] PCB design (KiCad: IR LED + photodiode + Pico)
  - [ ] PCB fab + assembly
  - [ ] Firmware (SCPI YAML, NEC / RC5 / Sony SIRC encode/decode)
  - [ ] Bring-up
  - [ ] Module enters service

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
- [x] Chassis block diagram (TikZ, with analog/digital module split)
- [x] Module 1E figures (functional block, AD9742 datasheet embed, typical app)
- [x] Module Design Document Schema (local tooling, gitignored)
- [ ] Per-module design docs for 1A, 1B, 1C, 1D, 1F, 1G, 1H, 2A-2E (authored as each module enters Phase 1+)

**Tooling**

- [x] TikZ figure pipeline with `pmvb-figures.sty` (FMCW dark theme)
- [x] Pandoc-rendered HTML for SDD and chassis arch doc, served via GitHub Pages
- [x] Parametric DXF + STL generator for chassis fabrication (`tools/fabrication/`)
- [ ] KiCad project template + symbol/footprint library for per-module PCBs
- [ ] Pico SDK build environment (CMake + arm-none-eabi-gcc) for firmware development
- [ ] Tang Primer 25K HDL toolchain (Gowin EDA + open-source flow as backup)

**Test infrastructure**

- [x] pytest harness with parametric fixtures keyed off module catalog (Phase 0 scaffolding in `pmvb/fixtures.py`; per-module parametrization added as modules come online)
- [ ] PyVISA-sim YAML schemas (one per module, generated mechanically from `modules/<id>/commands.yaml`; Phase 0 placeholder at `sim/placeholder/responses.yaml`)
- [x] InfluxDB tag schema spec (instrument, channel, dut, run_id, measurement_type) enforced in `pmvb/influx.py`
- [x] Jinja2 + Matplotlib report templates (`pmvb/reports/templates/basic_report.html.j2`; specialized templates added per-recipe)
- [x] MCP gateway scaffolding (`pmvb/mcp_gateway/server.py`, FastMCP + Anthropic Python SDK; per-module tool surface added as modules come online)

**Workflow**

- [x] GitHub repository published at github.com/Pike1950/poor-mans-validation-bench
- [x] GitHub Pages deployment for SDD + chassis arch doc
- [ ] Per-module branch + PR workflow once Phase 1 module work begins
- [ ] CI for SCPI YAML schema validation + Pandoc HTML re-rendering on doc changes