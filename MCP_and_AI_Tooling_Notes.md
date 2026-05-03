# MCP and AI Tooling Notes

**Scope:** Reference notes on MCP servers, AI model categories, and how both map onto Brad's current project portfolio (FMCW baseband PCB, KiCad workflow, homebrew val bench). Captured April 2026.

**Audience:** Brad, and future-Brad six months from now who has forgotten why he agreed to any of this.

---

## 1. What an MCP server actually is

The single most important thing to get right up front: **an MCP server does not run AI.**

MCP (Model Context Protocol) is a standard protocol for exposing "tools" (functions, really) to an LLM client. An MCP server is a plain program (Python, Node, Go, whatever) that speaks this protocol and offers a menu of callable tools. The LLM lives wherever the client lives (Claude Desktop, Cowork, Cursor, etc.). The MCP is a dumb pipe that lets the LLM push buttons on software it otherwise could not reach.

Round trip, in order:

1. User asks Claude to do something ("run DRC on the FMCW board")
2. Claude picks the right MCP tool and sends a structured call (`run_drc(project_path)`)
3. The MCP server receives the call, does the real work (talks to KiCad via its IPC API)
4. Results come back to Claude as structured data
5. Claude reasons about the results and talks to the user

No neural-network inference happens inside the MCP server. The "intelligence" is the LLM; the MCP is just a wrapper around whatever the real tool is.

A useful mental model: MCP is to LLMs what a driver is to an operating system. It lets the general-purpose thing talk to the specific thing.

---

## 2. AI model categorization by compute tier

This is where a lot of confusion lives, so the cleanest cut is by what hardware the model fits on. Four tiers cover the whole landscape.

### Tier 1: Microcontroller class (TinyML)

Runs on Cortex-M parts or similar. Few hundred KB of flash, int8 quantized. Frameworks: TensorFlow Lite Micro, ExecuTorch, CMSIS-NN.

Typical jobs: keyword spotting ("hey" wake word), accelerometer anomaly classification, MEMS-mic leak or bearing-fault detection. A Pi Zero 2 W can run these entirely in software with no accelerator.

### Tier 2: Edge accelerator class

This is where the AI HAT+ (Hailo-8L, ~13 TOPS) sits. Similar hardware: Google Coral (Edge TPU), Intel Movidius, Jetson Nano/Orin. Models range from tens to low hundreds of megabytes, compiled to the accelerator's own instruction set.

Typical models:

- **YOLO family** — object detection, bounding boxes on images
- **MobileNet / EfficientNet** — image classification
- **Whisper-tiny** (39M params) — offline speech-to-text
- **PoseNet, DeepLabV3-Mobile** — pose estimation, segmentation
- **1D CNNs and autoencoders** — time-series classification and anomaly detection

No chat-capable LLM fits here. Even the smallest useful language models are too big.

### Tier 3: Prosumer GPU / Apple Silicon class

RTX 4090, M3 Max laptops, Framework Desktop. Runs 7B-13B quantized LLMs (Llama 3 8B, Qwen 2.5 7B, Mistral 7B), Stable Diffusion, Segment Anything (SAM), larger Whisper variants. Useful assistants live here, but nowhere near frontier.

### Tier 4: Datacenter class

A100/H100 clusters, trillions of parameters across many GPUs. Frontier LLMs like Claude, GPT, Gemini. Only reachable through a cloud API.

### Task-type axis

Orthogonal to compute tier, models are almost always purpose-built for one job: vision, audio, time-series, language, multimodal, control/RL. Frontier LLMs look general because they are trained on everything and scaled up. A 50 MB edge model is almost always narrowly specialized.

---

## 3. kicad-mcp-pro (KiCad EDA integration)

### What it is

Open-source (MIT) Python MCP server that wraps KiCad's IPC API and `kicad-cli` to expose EDA operations as MCP tools. Actively maintained (last commit 2026-04-18). Installs via `uvx kicad-mcp-pro` or `pip install kicad-mcp-pro`.

**Repo:** https://github.com/oaslananka/kicad-mcp-pro

### Capability groups (verbatim from the README)

- **PCB tools** for board inspection, tracks, vias, footprints, text, shapes, outline editing, and zone refill
- **Schematic tools** for symbols, wires, labels, buses, no-connect markers, property updates, annotation, netlist-aware auto-layout, hop-over display control, and IPC reload
- **Library tools** for symbol search, footprint search, datasheet lookup, footprint assignment, and custom symbol generation
- **Validation tools** for DRC, ERC, DFM, courtyard issues, silk overlaps, and schematic-versus-PCB footprint checks
- **Export tools** for Gerber, drill, BOM, PDF, netlist, STEP, render, pick-and-place, IPC-2581, SVG, and DXF
- **Signal integrity tools** for impedance synthesis, differential skew checks, stackup planning, via-stub review, and decoupling heuristics
- **Power integrity tools** for voltage-drop estimation, copper current checks, plane generation, and thermal via guidance
- **EMC tools** for plane coverage, return-path review, via stitching, diff-pair symmetry, and bundled compliance sweeps
- **Simulation tools** for SPICE operating-point, AC, transient, DC sweep, and loop-stability checks

Scope profiles select a subset at startup: `full`, `minimal`, `schematic_only`, `pcb_only`, `manufacturing`, `high_speed`, `power`, `simulation`, `analysis`, `agent_full`.

### KiCad 9 caveat

The project is described by the author as "KiCad 10.x-first runtime with best-effort 9.x support." KiCad-10-only features that will not work on a KiCad 9 project: graphical DRC, design variants, time-domain tuning, 3D PDF export. Core schematic, PCB, DRC, ERC, SI, PI, EMC, and export tools all work on KiCad 9.

For the FMCW baseband board (KiCad 9, mixed-signal, SPI focus) the loss is small. The `high_speed`, `power`, and `analysis` profiles are the most relevant.

### Install / wire-up

Claude Desktop (or any client with `mcpServers` config):

```json
{
  "mcpServers": {
    "kicad": {
      "command": "uvx",
      "args": ["kicad-mcp-pro"],
      "env": {
        "KICAD_MCP_PROJECT_DIR": "C:\\Users\\BradW\\Documents\\Claude\\Projects\\FMCW-Baseband-PCB"
      }
    }
  }
}
```

KiCad must be running with the IPC API enabled for the live tools (anything beyond `kicad-cli`-based export/validation). Transport defaults to stdio; HTTP mode is available via `--transport http` if you want to run the server on a different machine.

### Project-specific fit

What this would automate or assist on the FMCW project:

- Zero-error ERC and DRC enforcement as a first-class part of the design loop (matches the existing project rule)
- Controlled-impedance trace checks for SPI and the signal chain (matches the mixed-signal design rule)
- AGND/DGND ferrite-bead split validation via EMC return-path tools
- Decoupling placement heuristics for PGA113, ADS8881, REF5025
- SPICE loop-stability sweeps on the REF5025 buffer before layout commits
- Automated BOM and pick-and-place generation at export time

---

## 4. SamacSys / Component Search Engine

### What it is (and what it is not)

Free component library service from SamacSys (Supplyframe). Provides verified schematic symbols, PCB footprints, and 3D STEP models for millions of parts, with direct import into KiCad via the Library Loader helper application.

**Not an MCP.** This is a human-facing tool that populates your KiCad libraries. It complements kicad-mcp-pro but does not overlap.

**Landing page:** https://componentsearchengine.com/learn-more
**KiCad integration instructions:** https://www.samacsys.com/kicad/kicad-library-loader-instructions/

### Workflow

1. Install Library Loader (free, standalone desktop app)
2. Configure it to point at a dedicated KiCad library path (see namespace note below)
3. Search for a part on componentsearchengine.com, click download
4. Library Loader monitors the download folder and auto-imports the symbol + footprint + 3D model into the configured KiCad library
5. Part is now available in KiCad's library browser

If a part isn't in the database, you can submit a free 48-hour part request or build it yourself with the web Build Wizard.

### One caveat: namespace cleanly

SamacSys symbols and footprints follow their own naming and layer conventions. Mixing them freely into KiCad's built-in libraries gets messy at BOM-generation and DFM-review time. Set up a project-specific library path (or a dedicated `SamacSys/` library) so their parts stay namespaced separately.

### Project-specific fit

Pre-commit sanity check: verify that the three reference parts called out in the project instructions (PGA113, ADS8881, REF5025) all have verified models on CSE before committing to Library Loader as the primary source. If any are missing or low-quality, file the free part request rather than building by hand.

---

## 5. Val bench + MCP architecture vision

This is the part worth keeping in the overall-project docs, not just the FMCW folder. The homebrew val bench ("Poor Man's PXI") is where MCP really earns its keep across projects.

### Why MCP fits a distributed val bench

The val bench architecture is already distributed: multiple Pi Zero 2 W nodes, each paired with a Sipeed Tang FPGA and a front-end analog/digital IC set, each FPGA running an "instrument personality" (scope, AWG, DMM, logic analyzer, pattern gen). The natural abstraction is one MCP server per node, exposing that node's capabilities as tools. Claude orchestrates across nodes via the LAN.

### Tier-2 model use cases (AI HAT+ node)

The Pi 5 + AI HAT+ is a Tier-2 accelerator, so the useful models are narrow and purpose-built. Validation work is full of exactly these kinds of problems:

- **Waveform classification.** Small 1D CNN trained on your own labeled scope captures: `clean`, `ringing`, `overshoot`, `oscillation`, `noise-limited`. Sub-millisecond inference. MCP tool: `classify_trace(samples) -> {class, confidence}`.
- **Anomaly detection on ADC data.** Autoencoder trained on known-good captures. Reconstruction error spikes when something changes. Tool: `score_anomaly(samples) -> float`.
- **SPI / logic timing violation detection.** Same pattern on logic-analyzer captures.
- **DUT vision inspection.** Small YOLO model trained on your own boards. Tool: `inspect_dut(image) -> {dut_id, missing_parts, solder_issues}`.
- **Offline voice control.** Whisper-tiny on the Pi 5 for hands-free bench commands ("start sweep," "capture channel one," "save as run 47").

Every one of these becomes an MCP tool. From the LLM's perspective there is no neural net, just a function call.

### Node sketches

Rough tool surface per node type. Treat these as stubs to flesh out, not as final APIs.

```
scope-01         (Pi Zero 2W + Tang + analog front-end)
  arm(trigger_cfg)
  capture(duration_ms, rate_sps, channels) -> trace_id
  download(trace_id) -> samples or file path

awg-01           (Pi Zero 2W + Tang + DAC)
  set_waveform(type, freq, amp, offset)
  upload_arbitrary(samples)
  start() / stop()

dmm-01           (Pi Zero 2W + Tang + precision ADC)
  measure_dc() / measure_ac() / measure_resistance() / measure_continuity()

logic-01         (Pi Zero 2W + Tang)
  configure(pins, rate, depth)
  arm(trigger_cfg)
  decode_spi(trace_id) -> transactions

ml-01            (Pi 5 + AI HAT+)
  classify_trace(samples) -> {class, confidence}
  score_anomaly(samples) -> float
  inspect_dut(image) -> {...}
```

Example orchestration for "characterize PGA113 noise floor":

1. `awg-01.set_waveform(sine, 1 kHz, 100 mVpp)`
2. `scope-01.arm(rising, CH1, 0 V)`
3. `scope-01.capture(1000 ms, 1 Msps, [CH1])`
4. Pull samples, compute FFT and noise density
5. Optionally `ml-01.score_anomaly(samples)` against a known-good baseline

All of that is addressable from a single conversation with Claude.

### Gotchas worth knowing up front

- **Timing-critical sync does not go through MCP.** Two instruments that must trigger within nanoseconds of each other need a shared FPGA sync line. MCP only arms them; the FPGAs handle the actual sync.
- **Big data does not travel inline.** A million-sample scope capture is a few megabytes. Return a file path or an ID and let a separate tool fetch the payload on demand. Do not base64-encode megabytes into the response body.
- **One node, one job.** MCP tools are request/response and single-threaded per call. Do not try to run the scope and the AWG off the same Pi Zero 2 W unless the MCP server is careful about concurrency.
- **HTTP transport on the LAN needs auth.** The kicad-mcp-pro README warns about this too. At minimum use a shared token; ideally run on a management VLAN.
- **Pi Zero 2 W is small** (512 MB RAM, quad A53). Fine for MCP server + serial/SPI/UART bridge. Do not expect heavy DSP to fit there. Push DSP to the FPGA or the Pi 5.

---

## 6. Suggested sequencing

Ordered from cheap to expensive, so the early steps de-risk the later ones.

1. **Verify components on CSE** before committing Library Loader as the primary source. Search PGA113, ADS8881, REF5025. If any are missing, file free 48h requests.
2. **Install kicad-mcp-pro** with the config above. Run a read-only exercise first: have it parse the (future) FMCW schematic and return the hierarchy. No writes, no risk.
3. **Stand up a scope-01 stub MCP server** on one Pi Zero 2 W with fake data to feel the end-to-end round trip before wiring any real analog. This is a no-hardware-risk way to validate the architecture.
4. **Add kicad-mcp-pro write tools into the design loop** (DRC, ERC, SI checks) once comfortable with read-only behavior.
5. **Replace the scope-01 stub with real Tang FPGA bridge** once the protocol is working.
6. **Add ml-01 (AI HAT+ node) last,** once there are enough labeled captures from real bench runs to train the waveform classifier or anomaly autoencoder.

---

## 7. Open questions to revisit later

- Do the FMCW baseband's DFT hooks need any specific MCP-facing tooling (e.g., a dedicated "read-out DFT chain via SPI" tool on scope-01 or logic-01)?
- Is there value in an MCP that wraps the SystemVerilog toolchain (Verilator build + TB run) so design-loop iterations on the SPI controller RTL stay inside one conversation? This would parallel the kicad-mcp-pro model.
- Does the AI HAT+ node justify itself on FMCW alone, or does it need a second project (e.g., the RISC CPU val bench) to earn the setup cost?
