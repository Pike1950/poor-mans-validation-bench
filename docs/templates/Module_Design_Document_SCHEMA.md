# PMVB Module Design Document Schema

This file codifies the structure that a PMVB module design document must follow.
Module 1E is the proven reference implementation. Every other module document
(1A–1H, 2A–2E, future Tier 3) should use the same skeleton so a reader can find
the same information in the same place across modules.

The schema has two parts:

1. **Section structure** — the eleven canonical sections, what each one is for,
   and what to skip.
2. **Fillable template** — a copy-paste-able markdown skeleton with placeholders
   matching the conventions established in Module 1E.

A module document that follows the schema is also expected to follow the
project conventions on figures, BOM sourcing, SCPI tables, and calibration
procedure formatting. Those are summarized at the end of this file.

---

## 1. Section structure

Every module design document has the same eleven sections, in this order:

1. **Theory of Operation** — what the module does, the signal chain, and the
   load-bearing design choices behind the active topology. Describe what *is*
   used; do not enumerate alternatives that were considered and rejected. If a
   non-obvious choice has a reason worth recording (a part picked over an
   obvious alternative because of package, slew, supply, or cost), state the
   reason once in a "Why X" subsection.
2. **Functional Block Diagram** — link to the TikZ-rendered SVG under
   `docs/figures/modules/`. Caption with a one-line summary. Do not duplicate
   the diagram inline as ASCII or Mermaid; the SVG is the source of truth.
3. **Schematic Notes** — high-level commentary on the analog/digital front
   end. Each subsection covers one functional block (e.g. DAC output stage,
   reconstruction filter, op-amp gain network, impedance switching,
   decoupling). The full schematic lives in KiCad; this section explains the
   *intent* behind the schematic, not the schematic itself.
4. **Pin Assignments** — every Pico/FPGA pin used by the module, organized by
   functional purpose (data bus, control, power, trigger I/O). One subsection
   per logical group. Use a consistent table format: `| Pico GPIO | Signal |
   Direction | Purpose |`.
5. **Specifications** — table that mirrors the SDD spec table for this module
   exactly. The two tables must agree; keep them in sync when either is
   edited.
6. **Sample Applications** — at least three numbered worked examples showing
   how a user invokes the module via SCPI to accomplish a real measurement.
   Each example is self-contained: SCPI commands, expected behavior, and a
   note on what the user does next with the data. Pair examples with other
   modules where the recipe spans the bench.
7. **Bill of Materials** — table with columns: `Item | Manufacturer Part |
   Source | Source PN | Qty | Unit Price | Notes`. Prices follow the project
   sourcing rule: Mouser > Digi-Key > Microcenter > Amazon, with the part
   number cited. Items pending direct verification are explicitly marked.
   Module total at the bottom.
8. **Calibration Procedure** — numbered steps a user runs after assembly to
   bring the module within its specified accuracy. One subsection per
   calibration target (DC offset, gain, frequency, filter response, etc.).
   Reference the SCPI commands the user invokes.
9. **Bring-Up Checklist** — ordered list of first-power-on checks. From visual
   inspection through the first end-to-end SCPI exchange. The reader should
   be able to follow this in one sitting on the bench.
10. **Known Issues and Future Work** — populate as the module is built. Keep
    issues factual (what was observed and the workaround); keep future work
    bounded (specific enhancement, not vague aspiration).
11. **References** — datasheets, app notes, the parent SDD section, and any
    external standards the module implements.

---

## 2. Front matter

Every module document opens with the same six metadata fields, on lines 1–9:

```markdown
# Module {ID}: {Module name}

## Module Design Document

**Version:** {x.y} ({Month Year}, {short note on this revision})
**Module ID:** {ID, e.g. 1E}
**Tier:** {1, 2, or 3}
**Status:** {In Design | In Build | Bring-Up | Operational | Deprecated}
**Parent SDD section:** {x.y.z} of the [PMVB System Design Document](../system-design/System_Design_Document.html#{anchor})
```

Followed by a horizontal rule and the Table of Contents. The TOC links to
every numbered section AND every named subsection. Use lowercase, dash-
separated anchor slugs that pandoc will generate.

---

## 3. Conventions

### Figures

- TikZ source lives in `docs/figures/modules/{module_id}_{name}.tex`.
- Compiled to PDF via `pdflatex`, then to SVG via `pdftocairo -svg`. Both
  artifacts are committed.
- The Module document references the SVG with a relative path:
  `../figures/modules/{module_id}_{name}.svg`. Do not link the PDF.
- All TikZ figures load `pmvb-figures.sty` for the house style (FMCW dark
  palette, edge styles, helper macros). See `docs/figures/STYLE_GUIDE.md`.
- Mermaid block diagrams stay native (the SDD Mermaid blocks render through
  the doc's Mermaid runtime). Reserve TikZ for figures that need precise
  geometry, op-amp triangles, or pin-level detail.

### BOM sourcing

Quote prices only from these sources, in this priority order:

1. Mouser
2. Digi-Key
3. Microcenter
4. Amazon

Cite the part number used to look up the price. Date the quote (the BOM
section's "verified Month Year" line at the bottom). Items where the price
could not be retrieved at audit time are flagged "(verify direct)" rather
than estimated. Never speculate.

### SCPI command tables

Each module's SCPI command set is documented inline in its sample-applications
section AND in the parent SDD section. Both lists must agree. The canonical
command-set definition is the YAML file under `firmware/scpi/{module_id}.yaml`
(per the project instructions); the markdown tables are derived references.

### Spec table parity with the SDD

Section 5 (Specifications) of the module document duplicates the SDD spec
table for the module verbatim. When either is edited, update both. The SDD
table is canonical for cross-module summaries; the module-doc table exists
so a reader inside the module document does not have to leave to find specs.

### "Describe what is used"

Per the project rule: do not enumerate alternatives that were considered and
rejected, do not include change-log narration ("we previously tried X but..."),
do not include framing about deferred parts unless directly relevant to the
current section. Describe the current state of the module. If a non-obvious
choice is worth recording, state the reason once and move on.

### Mechanical form factor

Every module is a vertical "blade" that slots into the PMVB chassis. The
chassis (acrylic, laser-cut from SendCutSend, 420 × 238 × 90 mm overall)
holds 14 module slots at 22.5 mm pitch alongside the TX300 PSU, the GeeekPi
D-1188 ATX breakout, the Sabrent HB-BU10 USB hub, and a 4-rail back-wall
power harness. Every module PCB must conform to the following standard
envelope so it physically fits a slot, mates with the back-wall harness,
and connects to the USB hub in the same way as every other module:

**Module body envelope (mandatory):**

- **Outer width (X, slot-pitch direction):** 16.5 mm including the 1 mm rail
  lip. The 22.5 mm slot pitch leaves a 6 mm air gap between adjacent module
  bodies, which the chassis allocates to module components and assembly
  clearance per the convention below.
- **PCB depth (Y, front-to-back):** 125 mm. The front edge sits at the
  chassis front face; the rear edge sits 8 mm forward of the back-wall
  power harness, leaving a 35 mm cable-management gap.
- **PCB height (Z, vertical):** 80 mm of usable PCB. The 86 mm total module
  height (3 mm bottom rail lip + 80 mm body + 3 mm top rail lip) engages
  the chassis floor and ceiling card guides.
- **Module body shell:** 5 mm acrylic top/bottom shell walls, 1 mm right
  wall (with the 1 mm × 3 mm rail lips at the top-right and bottom-right
  corners), open left face. The cavity is 14.5 mm wide internally
  (x = −7.5 to +7), 70 mm tall (z = 11 to 81), 125 mm deep.

**PCB mounting and component-stack convention (mandatory):**

The module's host PCB mounts vertically against the cavity's **right wall**
(x = +7), with components extending leftward through the cavity and into
the 6 mm inter-module gap. This convention has three consequences:

- **Component-stack budget per module: 21.5 mm.** From the right wall (PCB
  surface at x = +7) leftward to the adjacent module's right wall
  exterior (x_neighbor + 8 = x_this − 14.5). The 1 mm lip on the adjacent
  module is above and below the cavity z-range and doesn't reduce the
  middle-cavity budget.
- **Pico 2 W mounting flexibility:** both direct-solder (~6.2 mm stack,
  recommended for 14-slot v1.0+v1.1 buildout) and female-header-mounted
  (~14.2 mm stack, swappable Pico) fit comfortably within the 21.5 mm
  budget. Direct-solder is preferred for layout density; headers are
  acceptable when Pico-swap convenience is worth the 7-mm-of-headroom
  trade-off.
- **No component placement on the back face of the host PCB.** The PCB's
  back face presses against the cavity right wall (x = +8 to +9 lip
  region); components on that face would crash into the wall. All
  components live on the cavity-facing (left) face of the PCB.

**Connector placements (mandatory):**

The host PCB sits vertically (PCB plane parallel to the chassis YZ plane,
PCB normal pointing in the X direction toward the cavity interior). The
PCB has four edges in this orientation: front (low Y, faces the chassis
front panel), rear (high Y, faces the back-wall harness), top (high Z),
bottom (low Z).

- **Pico USB-C connector:** on the **rear edge** of the host PCB, pointing
  rearward (+Y direction). The Pico 2 W is mounted with its long axis
  running along the Y direction, near the rear half of the PCB, so its
  natural USB-C connector position lands at the rear edge with the
  connector protruding ~3 mm past the PCB outline. A short USB-C-to-USB-A
  cable runs straight rearward from this connector to the Sabrent HB-BU10
  mounted at the chassis rear. All modules use the same Z offset for the
  USB-C connector so cables run in parallel.
- **Phoenix MC 1,5/4-G (1803293):** on the **top edge near the rear corner**
  of the host PCB, oriented so the four pins face upward (+Z direction).
  The mating cable plug from the chassis 4-rail back-wall harness drops
  down onto this header from above. Pin assignment, left to right viewed
  from outside the module looking in: +5 V, +12 V, −12 V, GND. The same
  pin order is used on every module's header for consistency.
- **Faceplate connectors:** on the **front edge** of the PCB. Module-specific
  I/O (BNC, banana jacks, banana binding posts, switches, indicator LEDs,
  trim pots) must fit within ~17 mm horizontal × 80 mm vertical of front
  face real estate. For module designs that legitimately need more
  faceplate real estate than 17 mm allows (e.g., a multi-range DMM with
  many input terminals), consider a "double-wide" 2-slot variant that
  consumes 45 mm of chassis pitch — this is the only acceptable deviation
  from the standard 1-slot envelope, and must be declared explicitly in
  the module's design doc.

**Mounting holes (mandatory):**

- **Four M3 holes** through the host PCB, one near each corner in the YZ
  plane. With the PCB filling the cavity (~120 × 75 mm of usable PCB
  area inside the 125 × 80 mm cavity), the recommended hole positions
  are 5 mm inset from each edge: (Y, Z) = (5, 5), (5, 75), (120, 5),
  (120, 75) measured from the front-bottom corner of the PCB. Holes
  are M3 clearance (3.2 mm diameter) with no copper exposure within a
  6 mm radius.
- The module body (acrylic shell) carries matching M3 mounting features
  (integrated standoff bosses or glued-in M3 nuts) on the inside face
  of the right wall so the host PCB can be screwed down with M3 × 4 mm
  pan-head screws. Mounting hardware is part of the module design, not
  the chassis design.

**Faceplate I/O layout for module-specific connectors:**

Each module's design doc should include a brief subsection in section 3
(Schematic Notes) or as part of section 4 (Pin Assignments) describing
the faceplate's I/O layout: which connectors, at what vertical position
on the 17 × 80 mm front face. A simple ASCII or diagram-style layout is
sufficient — this is not a full mechanical drawing, but it lets the
chassis builder verify front-panel cutouts are at the right positions.

---

## 4. Fillable template

Copy this skeleton into `docs/modules/Module_{ID}_Design_Document.md` and
populate. Strip the `{...}` placeholders as you fill them in.

```markdown
# Module {ID}: {Module name}

## Module Design Document

**Version:** {x.y} ({Month Year})
**Module ID:** {ID}
**Tier:** {1, 2, or 3}
**Status:** In Design
**Parent SDD section:** {x.y.z} of the [PMVB System Design Document](../system-design/System_Design_Document.html#{anchor})

---

## Table of Contents

- [1. Theory of Operation](#theory-of-operation)
  - [{first subsection}](#{first-subsection})
- [2. Functional Block Diagram](#functional-block-diagram)
- [3. Schematic Notes](#schematic-notes)
  - [{first analog/digital block}](#{first-analog-digital-block})
- [4. Pin Assignments](#pin-assignments)
  - [{first pin group}](#{first-pin-group})
- [5. Specifications](#specifications)
- [6. Sample Applications](#sample-applications)
  - [6.1 {first application}](#first-application)
- [7. Bill of Materials](#bill-of-materials)
- [8. Calibration Procedure](#calibration-procedure)
  - [8.1 {first cal target}](#first-cal-target)
- [9. Bring-Up Checklist](#bring-up-checklist)
- [10. Known Issues and Future Work](#known-issues-and-future-work)
- [11. References](#references)

---

## 1. Theory of Operation

{One paragraph: what the module does, the signal chain at a high level, and
the headline specs in one sentence. Mention every active part by manufacturer
and part number on first use.}

### {first subsection — typically the signal chain}

{Describe the signal flow from input to output (or stimulus to DUT). Cite the
specific parts and the role each plays. Include any sample-rate / bandwidth /
slew-rate analysis that proves the topology meets the headline specs.}

### Why {non-obvious-choice}

{Optional. Use only when a part choice is non-obvious and the reason is
worth recording. State the reason once: package, slew, supply, cost, or a
fundamental architectural constraint. Do not list alternatives that were
rejected.}

## 2. Functional Block Diagram

![Module {ID} functional block diagram](../figures/modules/{module_id}_block.svg)

*Figure {ID}-1: Module {ID} functional block diagram. {One-line caption.}*

## 3. Schematic Notes

The full schematic lives in `kicad/Module_{ID}/`. The notes below explain the
intent behind each functional block.

### {first block, e.g. DAC output stage}

{Prose describing the block's role, key component values, and any non-obvious
design choices. Reference the relevant pins or nets from the KiCad schematic.}

### {second block}

{...}

## 4. Pin Assignments

### {first pin group, e.g. Pico parallel data + clock to {DAC}}

| Pico GPIO | Signal | Direction | Purpose                  |
|-----------|--------|-----------|--------------------------|
| GP0       | DB0    | OUT       | DAC data bit 0 (LSB)     |
| ...       | ...    | ...       | ...                      |

### {second pin group, e.g. Power}

{...}

## 5. Specifications

This table mirrors SDD Table {x-y}. Keep both in sync.

| Parameter        | Value                              |
|------------------|------------------------------------|
| {param 1}        | {value 1}                          |
| ...              | ...                                |

## 6. Sample Applications

### 6.1 {first application name}

{One-paragraph description of the application: what the user is measuring or
generating, and why this module is appropriate.}

```python
# SCPI sequence
{module}.write('...')
{module}.write('...')
data = {module}.query('...')
```

{Note on what the user does with the result.}

### 6.2 {second application name}

{...}

## 7. Bill of Materials

| Item | Manufacturer Part | Source | Source PN | Qty | Unit Price | Notes |
|------|-------------------|--------|-----------|----:|-----------:|-------|
| {item} | {MPN}           | {source} | {SPN}   |  1  | $X.XX      | {notes} |
| ...    | ...             | ...      | ...     | ... | ...        | ... |
| **Module BOM total ({Month Year}, {sources})** | | | | | **~$XX** | {scope notes} |

Items marked "(verify direct)" are commodity passives whose prices were not
extracted at audit time; total impact is bounded under $XX.

## 8. Calibration Procedure

After module assembly, calibrate against {reference instruments} using the
following procedure.

### 8.1 {first calibration target}

1. Configure: `{SCPI commands}`.
2. {Action.}
3. {Measurement.}
4. {Adjustment or store-to-flash step.}

### 8.2 {second calibration target}

{...}

## 9. Bring-Up Checklist

In order, on first power-up:

1. **Visual inspection.** {What to check before applying power.}
2. **Power-on without DUT.** {Expected current draw at idle.}
3. **{MCU/FPGA} boots.** {How you know.}
4. **{First end-to-end test.}**
5. **{Subsequent functional tests, in increasing scope.}**
6. **Calibration.** {Run section 8 procedures.}
7. **PyVISA-sim parity check.** {Same SCPI sequence against sim backend.}

## 10. Known Issues and Future Work

(Populate as the module is built.)

- {Specific observed issue or known bound.}
- {Bounded future enhancement; not vague aspiration.}

## 11. References

- [{Datasheet 1}]({URL})
- [{App note}]({URL})
- [PMVB System Design Document, section {x.y.z}](../system-design/System_Design_Document.html#{anchor})
```

---

## 5. Authoring checklist

Before declaring a module document done:

- [ ] All eleven sections present, in order.
- [ ] Front matter (Version, Module ID, Tier, Status, Parent SDD section) populated.
- [ ] Table of Contents links resolve to every section and named subsection.
- [ ] Functional block diagram exists as TikZ source AND committed SVG.
- [ ] Specifications table matches the SDD table verbatim.
- [ ] BOM prices cite source and part number; verified items dated; unverified items flagged.
- [ ] Sample applications include real SCPI sequences, not pseudocode.
- [ ] Calibration procedure references SCPI commands the firmware exposes.
- [ ] Bring-up checklist runs in physical order (visual → power → boot → SCPI).
- [ ] No description of rejected alternatives, no change-log narration in body text.
- [ ] References include the parent SDD section anchor.
- [ ] PCB layout fits the standard 17 × 125 × 80 mm form factor with USB on the right edge, Phoenix MC 1,5/4-G on the top-rear corner facing rearward, faceplate on the front edge, and four M3 mounting holes at standard corner positions. Double-wide (45 mm pitch) variants explicitly declared if used.
- [ ] Faceplate I/O layout subsection present (which connectors at which vertical positions on the 17 × 80 mm front face).
- [ ] HTML rendered via pandoc and visually checked: TOC links, figures embed, tables format cleanly.
