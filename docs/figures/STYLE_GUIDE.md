# PMVB Figure Style Guide

This guide documents the conventions for authoring figures in PMVB design documents. Following it produces visually consistent diagrams across the System Design Document, the chassis design doc, and every per-module design doc.

If you're new to authoring a figure for PMVB, read this guide once, then use the existing Module 1E figures (`docs/figures/modules/1e_*.tex`) as worked examples.

The decoder for what each color and shape means is the [Figure Legend](system-design/00_legend.svg). Embed it in any document where readers will encounter their first PMVB figure.

---

## Scope

This guide covers the four diagram categories that render through TikZ:

1. **System block diagrams** — top-level architecture, multi-module recipes, power trees
2. **Functional block diagrams** — per-module signal-chain decomposition
3. **Schematics** — typical-application circuits with component-level detail
4. **Mechanical / power topology** — chassis layout, rail trees, AC/DC zoning

The other two diagram categories used in PMVB docs are **out of scope** for this guide:

- **Sequence diagrams** (Mermaid `sequenceDiagram`) render in their native style
- **Timing diagrams** (WaveDrom) render in their native style

These were intentionally left in their default rendering because (a) they're already legible, (b) Mermaid and WaveDrom are battle-tested in their own ecosystems, and (c) there's diminishing return in retheming them.

---

## Toolchain

Every TikZ figure is a standalone `.tex` file under `docs/figures/`, compiled to PDF and converted to SVG. The `.svg` is what design docs embed.

**Required tools:**

- **MiKTeX** (Windows) for `pdflatex`. Install missing packages on the fly.
- **Poppler** for `pdftocairo`. Install via `winget install oschwartz10612.Poppler`.

**Per-figure compile:**

```powershell
cd docs\figures\modules
pdflatex -interaction=nonstopmode my_figure.tex
pdftocairo -svg my_figure.pdf my_figure.svg
```

**Build everything at once:**

```powershell
cd docs\figures
.\build-all.ps1
```

---

## Repository layout

```
docs/figures/
├── BUILD.md                      Build instructions
├── STYLE_GUIDE.md                This document
├── build-all.ps1                 Bulk render script
├── style/
│   └── pmvb-figures.sty          House style sheet (load in every .tex)
├── system-design/                Figures for the SDD
│   ├── 00_legend.tex / .svg      The decoder ring (referenced from §4)
│   ├── fig_4_1_top_level.tex / .svg
│   └── ...
├── modules/                      Figures for per-module design docs
│   ├── 1e_system_context.tex / .svg
│   ├── 1e_typical_app.tex / .svg
│   └── ...
├── modules/external/             Third-party reference images (datasheet
│   └── *.png                       figures, official manufacturer SVGs)
└── chassis/                      Figures for chassis design docs
    └── ...
```

Both `.tex` source and rendered `.svg` are committed. Source for reproducibility and review; SVG so GitHub Pages can render the docs without a LaTeX server.

---

## Color palette

Defined in `pmvb-figures.sty`. Hexes match the SDD HTML's FMCW dark theme.

| Color name | Hex | Used for |
|---|---|---|
| `pmvbBg` | `#0d1117` | Page background |
| `pmvbFg` | `#e6edf3` | Default text and circuit lines |
| `pmvbMuted` | `#94a3b8` | Annotations, secondary labels |
| `pmvbBlue` | `#3b82f6` | Subsystem borders, digital signal lines |
| `pmvbBlueFill` | `#1f2937` | Subsystem fill |
| `pmvbGreen` | `#10b981` | IC borders |
| `pmvbGreenFill` | `#1e293b` | IC fill |
| `pmvbAmber` | `#f59e0b` | Analog signal lines |
| `pmvbRed` | `#ef4444` | Power rail labels (e.g., +3.3V) |
| `pmvbViolet` | `#a78bfa` | Control / strobe signal lines |

There is also a `pmvbLightMode` macro that switches the palette to a white background for printed portfolio PDFs. Default is dark mode; override per-figure with `\pmvbLightMode` after the `\input{pmvb-figures.sty}` line.

---

## Node (box) styles

| Style | Visual | When to use |
|---|---|---|
| `pmvb subsystem` | Blue border, dark blue fill, rounded corners | Top-level physical units: a board, a piece of bench equipment, a whole module envelope |
| `pmvb ic` | Green border, dark green fill | A single IC or discrete hardware part |
| `pmvb internal` | Off-white border, dark fill | A functional sub-block inside an IC's internal block diagram |
| `pmvb pin` | Small box-with-X glyph | An IC die-boundary pin pad (datasheet redraws) |
| `pmvb connector` | Circle, dark fill, off-white border | A physical input or output port (BNC, banana jack) |
| `pmvb annotation` | No border, gray italic, `align=center` | Multi-line muted annotation blocks |
| `pmvb group` | Dashed muted border, rounded | Visual grouping box around a set of related elements |

**Rule of thumb:** if you can hold the thing in your hand, it's a subsystem. If it's a chip on a PCB, it's an IC. If it's only nameable in the datasheet's block diagram, it's an internal block.

---

## Edge (wire) styles

| Style | Visual | Encodes |
|---|---|---|
| `pmvb digital` | Blue solid arrow | Single-bit digital signal |
| `pmvb digital bi` | Blue solid double arrow | Bidirectional digital link (host ↔ peripheral) |
| `pmvb bus` | Thick blue double-line arrow | Multi-bit parallel bus or aggregated link. Add `node[pmvb bus width]{$\times N$}` mid-path to overlay an "×N" width annotation. |
| `pmvb analog` | Amber solid arrow | Continuous-voltage analog signal |
| `pmvb analog bi` | Amber solid double arrow | Bidirectional analog (rare; mostly for ports) |
| `pmvb power` | Red solid (no arrow) | DC power rail |
| `pmvb control` | Violet dashed arrow | Synchronous control or strobe |
| `pmvb optional` | Gray dashed arrow | Optional / future / conditional connection |

**Power rail convention:** power lines do *not* have arrow heads. Power is a passive distribution, not a directional signal. If you need to show "+3.3V flows here", terminate the line at the chip's V_DD pin and add a red text label at the rail entry point. Use a ground glyph (`\node[ground]`) to indicate ground connections.

**Control vs digital:** if the signal carries data, it's digital (blue). If it's a one-shot edge that latches or arms something (LDAC, SHDN, trigger), it's control (violet dashed).

---

## Text styles

| Style | Visual | When to use |
|---|---|---|
| Bold sans-serif (`\textbf`) | Off-white bold | Subsystem and IC titles |
| Regular sans-serif (`\sffamily`) | Off-white regular | Pin labels inside chip bodies |
| `\pmvblabel{...}` | Gray italic, `\scriptsize` | Wire annotations: bus names, voltage ranges, frequencies |
| Red text | `pmvbRed` color | Power rail labels |
| `pmvb annotation` node style | Gray italic, multi-line | Side-of-figure explanatory blocks |

**Multi-line text:** `\\` only works inside a node when the node has `align=center` (or `align=left`). The `pmvb annotation` style sets this automatically. For inline multi-line wire labels, set `align=center` in the node options yourself.

---

## Helper macros

Defined in `pmvb-figures.sty`:

- `\pmvblabel{text}` — single-line gray italic annotation, the standard wire label
- `\pmvbsubsystem{name}{title}{detail}` — places a subsystem node with a two-line label
- `\pmvbic{name}{title}{detail}` — same idea for an IC
- `\opamptri{name}{coord}{dir}` — draws an op-amp triangle. `dir` is `1` for apex-right or `-1` for apex-left (mirrored). Defines coordinates `<name>_p`, `<name>_n`, `<name>_out` for wiring. The `coord` argument MUST include parens (e.g., `(0.6, -0.5)` or `($(m1e.center) + (4mm, 0)$)`).

For **bus-width annotations** there's no helper macro — TikZ's path parser doesn't expand macros mid-path reliably. Use the node-in-path syntax inline:

```latex
\draw[pmvb bus] (A) -- node[pmvb bus width]{$\times 16$} (B);
```

Renders as "×16" overlaid on the bus line in white bold, with a dark fill that masks the underlying double-line.

---

## Diagram-specific patterns

### System block diagrams

- Lay subsystems out left-to-right or top-down following the dominant signal flow
- Allow at least 24mm of horizontal gap between subsystems so wire labels fit cleanly
- Stack multi-line wire labels using `align=center` and `\\` rather than cramming everything on one line
- Embed the relevant module's internal stages (Pico, IC, op-amp) inside its subsystem box at this level — readers reaching this figure don't yet know the module's topology
- Place the figure caption *below* any annotations (trigger bus notes, etc.) so it's the last thing the reader sees

### Functional block diagrams

- Source the diagram from the IC's datasheet block diagram where one exists
- Either redraw it in the house style (when datasheet allows fair-use redraw) or embed the datasheet figure with attribution: `Source: <datasheet ID>, page X. <Manufacturer> Inc. Used under fair-use citation.`
- Embedded datasheet images live under `docs/figures/modules/external/` so they're public-facing (not in the gitignored `Reference Photos/`)
- For redraws, use `pmvb internal` boxes for functional stages, `pmvb pin` for die-boundary pads, `\opamptri` for amplifiers

### Schematics

- Use the `circuitikz` environment (`\begin{circuitikz}` not `\begin{tikzpicture}`) so you have access to capacitor, resistor, op-amp, and ground primitives
- Place pin labels INSIDE the chip body (anchor=east on the right edge, anchor=west on the left edge) — this is standard schematic convention and avoids label collision with arrow labels
- Bypass network: place caps with their ground glyphs in CLEAR FREE SPACE above the chip, not inside the chip body. Use `\fill[pmvbFg] (junction) circle (0.5mm)` to draw junction dots where wires meet
- Op-amp feedback wires: route the vertical-up segment OUTSIDE the triangle's footprint (apex.x + 5mm or so), then meet the output wire at a junction dot. Never let the feedback wire intersect the triangle body
- Power rails: red text label at the top, plain (non-arrow) circuit wire down to the chip's V_DD pin, V_DD pin labeled inside the chip

### Mechanical / power topology

- These are addressed under the chassis design doc, not yet exercised in module figures
- When you reach for one, see `docs/chassis/Chassis_Architecture_and_Power_Distribution.md` for current diagram conventions; the TikZ port is a future task

---

## File naming

- Module figures: `<id>_<purpose>.tex` (e.g., `1e_system_context.tex`, `1e_typical_app.tex`, `2a_logic_capture_state.tex`)
- SDD figures: `fig_<section>_<index>_<short_name>.tex` (e.g., `fig_4_1_top_level.tex`, `fig_11_1_power_tree.tex`)
- Legend / utility: prefix with `00_` so it sorts to the top
- One figure per `.tex` file; do not bundle multiple figures into one source file

---

## Embedding figures in design docs

In Markdown source:

```markdown
![Figure 1E-1: Module 1E system context](../figures/modules/1e_system_context.svg)
```

In raw HTML (SDD):

```html
<p><strong>Figure 1E-1: Module 1E system context</strong></p>
<img src="../figures/modules/1e_system_context.svg"
     alt="Module 1E system context"
     style="max-width: 100%; display: block; margin: 0 auto;">
```

Always embed by `.svg` reference, never copy SVG content inline. Keeps the doc source readable and lets the figure update without touching the doc.

---

## Caption conventions

The caption is part of the figure source, rendered at the bottom of the SVG. Format:

```latex
\node[font=\sffamily\scriptsize\bfseries, text=pmvbFg,
      below=Nmm of <last_element>]
  {Figure <id>: <one-sentence description>.};
```

Caption text patterns:

- System block: `Figure X-N: <module/system> in the <context> (system block diagram).`
- Functional block: `Figure X-N: <IC name> internal functional block diagram (redrawn from <datasheet ID>).`
- Schematic: `Figure X-N: <module> typical application schematic (<signal flow summary>).`
- Power tree: `Figure X-N: Chassis Power Tree (<scope>).`

If the figure embeds a third-party image, add a second muted line beneath the caption:

```latex
\node[font=\sffamily\scriptsize\itshape, text=pmvbMuted, below=1mm of caption]
  {Source: <doc ID>, page X. <Manufacturer>. Used under fair-use citation.};
```

---

## References & Conventions

The conventions documented in this guide are not invented; they're an intentional compose of established practices from several lineages. Citing them anchors the guide in industry practice and tells anyone authoring a new figure where to look for deeper guidance.

### Schematic symbols

We follow **IEEE 315** (and its predecessor **ANSI Y32.2-1975**) for graphical symbols in electrical and electronics diagrams: op-amp triangles, resistor zig-zags, capacitor parallel lines, ground glyphs, transistor symbols. The `circuitikz` package is built around these conventions, so we conform by construction.

For international equivalence, the same symbol set is also covered by **IEC 60617**. Circuitikz supports either US-style (`american` package option, our default) or European-style (`european`) symbol rendering; we use the American resistor (zig-zag) and conventional triangle for op-amps.

**Op-amp orientation:** we draw op-amps with the non-inverting input (+) on top and the inverting input (−) on the bottom. This matches the dominant US production-schematic convention used in TI, Linear Technology, and Maxim/Analog Devices application notes. The opposite orientation (+ on bottom) is equally valid and appears in some textbooks (Razavi, Sedra-Smith) and in the Microchip MCP4922 datasheet block diagram. We chose + on top deliberately for consistency with the production-schematic style.

### Hierarchical decomposition

Our three-tier document hierarchy (SDD → per-module design doc → IC datasheet) follows the methodological pattern in **IEC 61082** (Preparation of documents used in electrotechnology). Each level abstracts one tier coarser than the next; readers can drop into any level and find self-contained context, with cross-references to neighbors.

### Documentation modes

We use the **Diataxis framework** (https://diataxis.fr/, by Daniele Procida) to classify which kind of document we're authoring. Diataxis splits technical documentation into four modes, each serving a different reader need:

| Diataxis mode | Reader need | PMVB example |
|---|---|---|
| Reference | Authoritative, comprehensive, look-up-friendly | System Design Document; future SCPI command tables |
| Explanation | Why decisions were made; how a topology works | Per-module design docs (e.g., Module 1E doc) |
| Tutorial | Step-by-step bring-up walkthrough | Phase 0 orchestration setup (gitignored, local-only) |
| How-to guide | Recipe for a specific outcome | Future runbooks (e.g., "characterize a tube amp") |

Before authoring a new document, decide which Diataxis mode it serves. Mixing modes in one document is a common pitfall and is the usual cause of "I can't find the right thing in this doc."

### Instrument architecture vocabulary

The system block diagrams use **PXIe rack-and-module decomposition** vocabulary (chassis, slot, controller, module, backplane, trigger bus) intentionally. This inheritance is from **NI PXI Express specifications** and **NI TestStand reference architecture**. Anyone with NI PXI / TestStand background reads the SDD's section 4 and immediately recognizes the structure; readers without that background can pick up the vocabulary from any NI primer.

### Module-level functional block diagrams

The per-module block diagram conventions — single-IC functional decomposition, signal-flow arrows annotated with engineering values (sample rate, bit width, voltage range), pin labels inside the chip body — are taken from **TI application notes** (MSP430 family guide, Precision Labs reference designs) and **Microchip datasheet typical-application schematics**. These conventions are well-established in industry analog/mixed-signal documentation and translate directly to our use case.

### Visual design

Where we have judgment calls about visual density and emphasis, we follow **Edward Tufte's data-ink principle** (from *The Visual Display of Quantitative Information*): minimize non-essential ink and let semantic color carry meaning. Specific applications in PMVB figures:

- Color is reserved for signal-type encoding (digital blue, analog amber, power red, control violet). Not used for decoration.
- Border style encodes box type (subsystem, IC, internal block). Not used for decoration.
- Annotations are gray italic so they recede behind the structural content.
- Captions are below-figure and italic so the figure itself is the primary visual focus.

If a future figure needs a new color, the question to answer is "what semantic distinction does this color encode that the existing palette doesn't?" If there isn't a clean answer, reuse an existing color.

---

## When in doubt

- Open Module 1E's three figures (`1e_system_context.tex`, `1e_mcp4922_internal.tex`, `1e_typical_app.tex`). They exercise every convention this guide documents.
- Read the legend (`system-design/00_legend.svg`).
- Match the visual weight of the existing figures rather than inventing a new style.
- If you need a new node or edge style, add it to `pmvb-figures.sty` once and use it across all subsequent figures, rather than defining one-off colors per figure.

---

## Quick reference card

```
BOXES                          WIRES
─────                          ─────
pmvb subsystem  blue   border  pmvb digital     blue solid →
pmvb ic         green  border  pmvb bus         blue thick → (×N via mid-path node)
pmvb internal   white  border  pmvb analog      amber solid →
pmvb pin        small ⊠ glyph  pmvb power       red solid (no →)
pmvb connector  circle          pmvb control     violet dashed →
pmvb annotation gray italic     pmvb optional    gray dashed →

TEXT                           STRUCTURE
────                           ─────────
\textbf{...}      title        \input{../style/pmvb-figures.sty}
\pmvblabel{...}   wire label   \begin{tikzpicture}[pmvb figure]
red text          power label  \begin{circuitikz}[pmvb figure]   for schematics
align=center      multi-line   \opamptri{name}{(x,y)}{dir}       op-amp shorthand
```
