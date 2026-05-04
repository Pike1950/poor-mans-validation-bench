# Poor Man's Validation Bench

A modular SCPI instrument platform that mirrors NI PXIe rack-and-module test architecture at hobbyist budget. A Raspberry Pi 5 acts as the orchestration head running PyVISA, pytest, InfluxDB, and Grafana. Hot-swappable instrument modules attach over USB or Ethernet and present as independent SCPI-addressable instruments. Every module is also exposed through a Model Context Protocol (MCP) tool surface for agent-orchestrated bench sessions.

## Documentation

### Canonical reference

- **[System Design Document](https://pike1950.github.io/poor-mans-validation-bench/docs/system-design/System_Design_Document.html)** — full v1.0 SDD covering architecture, module catalog, specifications, software stack, build phases, and verification strategy. Rendered via GitHub Pages.

### Chassis design

- **[Chassis Power Distribution Design](https://pike1950.github.io/poor-mans-validation-bench/docs/chassis/Chassis_Power_Distribution_Design.html)** — single-enclosure Hammond 1411P design built around the Silverstone TX300 PSU. Covers theory of operation, mechanical fabrication for novice builders (IEC inlet cutout, fan grille, cable grommet), lid interlock topology, BOM with Mouser and Digi-Key cross-references, bring-up procedure, and safety protocols.

### Per-module design

- **[Module 1E: Function Generator / AWG](https://pike1950.github.io/poor-mans-validation-bench/docs/modules/Module_1E_Design_Document.html)** — theory of operation, functional block diagram, Pico-to-DAC-to-op-amp pin assignments, four sample applications (single-tone sine, swept-sine THD, multitone IMD, white noise), calibration procedure, bring-up checklist, and BOM with Mouser and Digi-Key cross-references.

## Module Catalog

Every module pairs a Pico 2 W bridge (USB-TMC primary instrument transport) with a Pi Zero 2 W admin sidecar (LAN access for storage, ssh, and module-level config). Tier 2 modules add a Tang Primer 25K FPGA; Tier 3 modules use a larger FPGA platform.

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

Every module includes a Pico 2 W (USB-TMC bridge) and a Pi Zero 2 W (admin sidecar). Tier 1 modules add an analog or digital front end appropriate to the function; the Pico runs the SCPI parser in firmware and the Pi Zero handles per-module Linux storage, ssh debug access, and configuration files. Tier 2 modules additionally include a Sipeed Tang Primer 25K FPGA where the instrument logic lives; the Pico bridges to the FPGA over SPI. Tier 3 modules replace the Tang Primer 25K with a larger FPGA (Tang Mega 138K Pro or Alinx AX7325B) for high-speed interface analysis.

See section 4 of the [System Design Document](https://pike1950.github.io/poor-mans-validation-bench/docs/system-design/System_Design_Document.html#functional-block-diagram) for the full architecture diagram.

## Status

This repository is currently a design document. Hardware implementation has not started. See [section 13 of the SDD](https://pike1950.github.io/poor-mans-validation-bench/docs/system-design/System_Design_Document.html#build-phases-and-investment-roadmap) for the build phases and investment roadmap.

## License

[MIT License](LICENSE) — see file for full text.

## Author

Bradley Ward
