# PMVB Hardware

PCB design workspace for Poor Man's Validation Bench instrument modules.

Each module gets its own folder under `modules/<id>/`, holding the engineering
design package, a parts-fetch checklist for the custom parts that need
Component Search Engine downloads, a KiCad project build guide, and the KiCad
project files themselves (created in KiCad once the prep documents are read).

Schematic capture and board layout happen in KiCad's GUI. The Python in this
tree is small and one-purpose: it generates the shared module board outline
DXF that every module imports onto Edge.Cuts.

## Layout

```
hardware/
  README.md                       this file
  library/
    module_pcb_outline.py         generator for the shared module PCB outline
    module_pcb_outline.dxf        generated; import onto KiCad Edge.Cuts
    module_pcb_floorplan.png      annotated placement reference
  modules/
    1E/
      Module_1E_PCB_Design_Package.md   engineering decisions + design spec
      Module_1E_Parts_Checklist.md      Component Search Engine fetch list
      Module_1E_KiCad_Build_Guide.md    project setup + sheet specification
      kicad/                            KiCad project (created during build)
```

## Workflow for a module

1. **Read** the per-module design package. D1 through D6 (for 1E) are the
   engineering decisions baked into the spec. Push back on any you disagree
   with before they get into the schematic.
2. **Fetch** the custom symbols, footprints, and 3D models per the parts
   checklist. Source is Component Search Engine. Drop the files into the
   project library at `modules/<id>/kicad/lib/PMVB_<id>/`.
3. **Build the KiCad project** per the build guide: new project, title block,
   library import, board-outline DXF onto Edge.Cuts, netclasses configured,
   five hierarchical sheets scaffolded.
4. **Capture** each sub-sheet against the per-sheet contract in section 7 of
   the build guide. ERC, annotate, update PCB.
5. **Place and route** against the floorplan and stackup in the design
   package. DRC, run the verification checklist in the build guide section 9.

## Dependencies

Only the shared board-outline generator runs as code:

```
pip install ezdxf matplotlib
```

KiCad 8 or 9 is the actual design environment. Component Search Engine is a
web tool (no install).

## Status

Module 1E (Function Generator / AWG) is the first board through this workflow
and establishes the shared 120 x 62 mm board outline and the module-to-
backplane Phoenix interface spec that the other 13 modules inherit.
