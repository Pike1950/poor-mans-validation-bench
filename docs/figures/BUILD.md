# Building TikZ Figures

This directory contains LaTeX/TikZ source for every figure in the PMVB design
documents. Each `.tex` file is a `standalone`-class document that produces one
figure as a tightly-cropped PDF, which is then converted to SVG for embedding
in the SDD HTML and the per-module / chassis design docs.

## One-time setup (Windows)

1. Install **MiKTeX** from <https://miktex.org/download>. Pick the "Install missing packages on the fly" option (yes, automatically). About 200 MB initial.
2. Install **`pdftocairo`** for PDF -> SVG conversion. It comes with **Poppler**:
   - Easiest: `winget install oschwartz10612.Poppler` (or download the Windows binaries from <https://github.com/oschwartz10612/poppler-windows/releases>).
   - Add `<poppler>\Library\bin` to your PATH so `pdftocairo` resolves on the command line.
3. Optional: install **latexmk** if MiKTeX did not include it (`mpm --install=latexmk`). latexmk is what we wrap so the build re-runs LaTeX the right number of times automatically.

Verify in PowerShell:

```powershell
pdflatex --version
latexmk --version
pdftocairo -v
```

All three should print version info.

## Repository layout

```
docs/figures/
├── style/
│   └── pmvb-figures.sty           house style sheet (load in every .tex)
├── system-design/                 Figures referenced from SDD HTML
│   ├── fig_4_1_top_level.tex / .svg
│   ├── fig_11_1_power_tree.tex / .svg
│   └── ...
├── modules/                       Figures for per-module design docs
│   ├── 1e_system_context.tex / .svg
│   ├── 1e_mcp4922_internal.tex / .svg
│   ├── 1e_typical_app.tex / .svg
│   └── ...
└── chassis/                       Figures for chassis design docs
    └── ...
```

Every `.tex` file should be paired with the `.svg` it produces. Both are
checked into the repo: `.tex` for reproducibility / review, `.svg` so GitHub
Pages can render the docs without running LaTeX on the build server.

## Building one figure

From PowerShell, in `docs/figures/modules/`:

```powershell
pdflatex -interaction=nonstopmode 1e_system_context.tex
pdftocairo -svg 1e_system_context.pdf 1e_system_context.svg
```

The first run may pause to install LaTeX packages on the fly (TikZ,
circuitikz, standalone, etc.). Just click "Install" each time MiKTeX
prompts. After the first build, subsequent builds are silent.

## Building everything

A PowerShell helper lives at `docs/figures/build-all.ps1`:

```powershell
cd docs\figures
.\build-all.ps1
```

This re-renders every `.tex` under `docs/figures/` and produces an `.svg`
next to each. Stale PDF intermediates get cleaned at the end.

## House style at a glance

The style sheet `pmvb-figures.sty` defines:

- A dark-mode color palette matching the FMCW SDD HTML theme (override with
  `\pmvbLightMode` for portfolio PDFs).
- Node styles: `pmvb subsystem`, `pmvb ic`, `pmvb internal`, `pmvb pin`,
  `pmvb connector`, `pmvb annotation`, `pmvb group`.
- Edge styles encoding signal type: `pmvb digital`, `pmvb analog`,
  `pmvb power`, `pmvb control`, `pmvb bus`, `pmvb optional`, plus
  bidirectional variants.
- Helper macros: `\pmvblabel`, `\pmvbsubsystem`, `\pmvbic`.

When you write a new figure, the structure is always:

```latex
\documentclass[border=8pt]{standalone}

\makeatletter
\def\input@path{{../style/}}
\makeatother

\usepackage{pmvb-figures}

\begin{document}
\begin{tikzpicture}[pmvb figure]
  % nodes here
  % edges here
\end{tikzpicture}
\end{document}
```

The first TikZ figure you author always feels like wrestling. By the third or
fourth, the patterns settle in and you stop fighting positioning.

## Embedding figures in design docs

In a Markdown source file (e.g. `docs/modules/Module_1E_Design_Document.md`):

```markdown
![Figure 1E-1: Module 1E system context](../figures/modules/1e_system_context.svg)
```

In raw HTML (e.g. inline in `System_Design_Document.html`):

```html
<img src="../figures/modules/1e_system_context.svg"
     alt="Figure 1E-1: Module 1E system context"
     style="max-width: 100%;">
```

Always embed by `.svg` reference, never copy the SVG content inline (keeps the
HTML source readable and lets the figure update without touching the doc).

## Common errors

- **`! LaTeX Error: File 'pmvb-figures.sty' not found`** — the `\input@path`
  hack in the figure source assumes the `.tex` is inside one of the per-doc
  subdirectories (modules/, system-design/, chassis/) and the `.sty` is one
  level up in `style/`. If you put a figure somewhere else, adjust the path.
- **`Missing \endcsname inserted`** in a circuitikz block — usually a
  mismatched `}` in a node label. Check the node spec on the line LaTeX
  pointed at.
- **PDF renders fine, SVG looks blocky/missing fonts** — `pdftocairo -svg`
  embeds fonts. If a system font isn't available, install it system-wide or
  switch to a TeX-bundled font (Latin Modern is the default and ships with
  MiKTeX).
- **Long compile** the first time — MiKTeX is downloading TikZ + circuitikz
  on demand. After the first build it's cached.
