# Module 1E - KiCad project

This folder holds the KiCad project for Module 1E (Function Generator / AWG).
The KiCad files themselves (`module_1e.kicad_pro` / `.kicad_sch` / `.kicad_pcb`
and the five sub-sheets) are created and edited in the KiCad GUI, not authored
by hand. The step-by-step is `../Module_1E_KiCad_Build_Guide.md`.

## Build order

1. Read `../Module_1E_PCB_Design_Package.md` (engineering decisions D1-D7).
2. Fetch the five custom parts per `../Module_1E_Parts_Checklist.md` into
   `lib/PMVB_1E/` (`symbols/`, `footprints.pretty/`, `3dmodels/`).
3. Follow `../Module_1E_KiCad_Build_Guide.md`: File > New Project here as
   `module_1e`; set the title block; add the project library; import the shared
   outline `hardware/library/module_pcb_outline.dxf` onto Edge.Cuts; set
   netclasses; place the five hierarchical sheets; capture per build-guide
   section 7.

## Folder layout (this dir, after KiCad New Project)

    kicad/
      module_1e.kicad_pro / .kicad_sch / .kicad_pcb   <- KiCad creates these
      Pico / DAC / OpAmp / OutputSwitch / Trigger .kicad_sch   <- 5 sub-sheets
      lib/PMVB_1E/
        symbols/            *.kicad_sym  (from CSE)
        footprints.pretty/  *.kicad_mod  (from CSE)
        3dmodels/           *.step       (from CSE)

## Quick reference - the values easy to get wrong

Pulled here so you do not have to flip between docs while capturing. If any of
this drifts, the design package / design doc win.

- **Power connector J1** (rear edge, rearward blind-mate): Phoenix
  MC 1,5/5-G-3,81, order 1803303. Pins 1-5 = +5V, +12V, -12V, GND, +3.3V.
- **+3.3V source:** J1 pin 5 (chassis rail) -> FB1/FB2 -> AVDD/DVDD. The Pico
  3V3_OUT is NOT used; leave it unconnected.
- **AD9742 gotchas:** pin 23 RESERVED = leave floating (do not stub to GND);
  pin 25 MODE -> DCOM/GND (straight binary); IOUTA = pin 22, IOUTB = pin 21.
- **Op-amp gain net:** R_in1/R_in2 (R4/R5) = 1k; R_fb/R_ref (R6/R7) = 20k ->
  gain 20 (+/-10V).
- **Reconstruction filter (per leg, x2):** series L 0.22 / 0.68 / 0.22 uH;
  shunt C 820 pF (singly-terminated 5th-order Butterworth).
- **Output-Z relays:** K1 -> R8 (50R) / K2 -> direct (high-Z) / K3 -> R10 (10k).
- **Netclasses:** Power_12V 0.8mm, Power_5V 0.6mm, Power_3V3 0.5mm,
  Analog 0.3mm, DataBus 0.25mm, Default 0.25mm. Min clearance 0.20mm.

## What is committed vs ignored

Committed: `*.kicad_pro` / `*.kicad_sch` / `*.kicad_pcb`, the project library
tables (`sym-lib-table`, `fp-lib-table`), and everything under `lib/PMVB_1E/`.
Ignored (see repo `.gitignore`): KiCad backups, autosave, caches, lock files,
and the per-workstation `*.kicad_prl`.
