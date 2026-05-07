# Poor Man's Validation Bench

A modular SCPI instrument platform that mirrors NI PXIe rack-and-module test architecture at hobbyist budget. A Raspberry Pi 5 acts as the orchestration head running PyVISA, pytest, InfluxDB, and Grafana. Hot-swappable instrument modules attach over USB or Ethernet and present as independent SCPI-addressable instruments. Every module is also exposed through a Model Context Protocol (MCP) tool surface for agent-orchestrated bench sessions.

## Project Status

**Current focus:** Phase 0 — orchestration + chassis power. Chassis architecture, module mechanical form factor, and Module 1E v1.1 design are committed. Next milestones: chassis fabrication (SendCutSend DXF, parts ordering, frame assembly) and Pi 5 software stack stand-up.

| Phase | Scope | Status |
|---|---|---|
| **Phase 0** | Orchestration head + chassis power | Architecture and BOM committed; fabrication and software stack pending |
| Phase 1 | Tier 1 core (1A, 1B, 1D, 1E) | Module 1E design + figures done; 1A / 1B / 1D design docs pending |
| Phase 1.5 | HID module (1C) + Tier 2 bridge stack | Pending |
| Phase 1.7 | Module 1H DMM | Pending |
| Phase 2 | Tier 2 core (2A, 2B, 2C, 2D) | Pending |
| Phase 2.5 | Module 2E digitizer | Pending |
| Phase 3 | v1.1 Tier 1 (1F, 1G) | Pending |
| Phase 4 | Tier 3 modules + chassis LAN switch | Deferred |
| Cross-cutting | Documentation, firmware infrastructure, verification, bench tooling | Continuous |

**Recently landed (most recent first):**

- TikZ chassis block diagram with analog/digital module split (commit `65156ab`)
- Chassis Architecture and Power Distribution doc with embedded Tinkercad photos (commit `eb9949b`–`65156ab`)
- Module 1E v1.1 redesign (AD9742 + AD8056, DC–10 MHz) including figures and SDD §7.5.5 update (commit `bbded04`–`70544f3`)
- USB 3.0 architecture decision (Sabrent HB-BU10) with Figure 4-1 / 1E-1 label updates (commit `00b9fb4`)
- TFX-as-analog-backbone architecture pivot, deprecated chassis power doc replaced (commit `00b9fb4`)
- Module Design Document Schema with mechanical form factor convention

See **[PROJECT_TRACKER.md](PROJECT_TRACKER.md)** for the granular phase-by-phase, per-module task breakdown (~250 line items across 8 phases plus cross-cutting work). Update cadence: tracker checkboxes flip as commits land; this README's status table refreshes at phase milestones.

## Documentation

### Canonical reference

- **[System Design Document](https://pike1950.github.io/poor-mans-validation-bench/docs/system-design/System_Design_Document.html)** — full v1.0 SDD covering architecture, module catalog, specifications, software stack, build phases, and verification strategy. Rendered via GitHub Pages.

### Chassis design

- **[Chassis Architecture and Power Distribution](https://pike1950.github.io/poor-mans-validation-bench/docs/chassis/Chassis_Architecture_and_Power_Distribution.html)** — open-frame acrylic blade-style chassis (laser-cut from SendCutSend, 420 × 238 × 90 mm) housing the Silverstone TX300 PSU as an analog-rail backbone, the GeeekPi D-1188 ATX breakout, the Sabrent HB-BU10 USB 3.0 hub, and 14 module slots at 22.5 mm pitch. Covers mechanical architecture, electrical architecture (4-rail back-wall harness with Phoenix MC 1,5/4 module interconnect, per-rail fuse panel, banana-jack diagnostic test points), USB-TMC backplane, BOM with Digi-Key and Amazon cross-references, bring-up procedure, and safety protocols.

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

This repository is currently a design document. Hardware implementation has not started. See [section 13 of the SDD](https://pike1950.github.io/poor-mans-validation-bench/docs/system-design/System_Design_Document.html#build-phases-and-investment-roadmap) for the build phases and investment roadmap.

## License

[MIT License](LICENSE) — see file for full text.

## Author

Bradley Ward
