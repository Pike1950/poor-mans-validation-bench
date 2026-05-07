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
- [ ] HTML rendered via pandoc and visually checked: TOC links, figures embed, tables format cleanly.
