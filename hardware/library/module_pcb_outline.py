"""
module_pcb_outline.py - Standardized PMVB module host-PCB outline + floorplan.

All 14 module PCBs share ONE outer outline and ONE set of fixed connector
positions, so modules are mechanically interchangeable in the chassis and a
future 4-rail distribution backplane can mate every slot at the 22.5 mm pitch.
Module 1E is the first board to instantiate this template.

Generates (into output_dir, default = this file's directory):
  module_pcb_outline.dxf     - import to KiCad Edge.Cuts to start any module board
  module_pcb_floorplan.png   - annotated placement reference

Run:  python3 module_pcb_outline.py [output_dir]

PCB-local coordinate frame (mm):
  X = chassis depth    0 = front edge (faceplate end)   120 = rear edge
  Y = chassis height   0 = bottom edge                   62 = top edge
The PCB mounts vertically against the module-body cavity right wall; all
components sit on the cavity-facing (left) copper. J1 Phoenix (5-position) sits
at the rear edge beside the USB for rearward blind-mate on insertion. Outline
size and PCB mounting are a proposal to co-design with the v10 module-body STL
- see the design package.
"""

import os
import sys

# --- board outline -----------------------------------------------------
BOARD_W = 120.0          # X, chassis depth
BOARD_H = 62.0           # Y, chassis height
MOUNT_INSET = 4.0
MOUNT_DIA = 2.7          # M2.5 clearance
MOUNTS = [(MOUNT_INSET, MOUNT_INSET),
          (BOARD_W - MOUNT_INSET, MOUNT_INSET),
          (MOUNT_INSET, BOARD_H - MOUNT_INSET),
          (BOARD_W - MOUNT_INSET, BOARD_H - MOUNT_INSET)]

# --- connector / block placement zones  (x0, y0, x1, y1, label) --------
ZONES = [
    (100.0, 34.0, 120.0, 54.0, "J1 Phoenix MC1,5/5\n(power, rear-edge blind-mate, +X)"),
    (62.0,  5.0, 113.0, 26.0, "U1 Pico 2 W\n(USB -> rear edge)"),
    (40.0, 30.0,  58.0, 48.0, "U2 AD9742 DAC\n+ recon filter"),
    (20.0, 30.0,  39.0, 50.0, "U3 AD8056\n+ gain network"),
    (16.0,  6.0,  39.0, 27.0, "K1-3 reed relays\n+ output Z network"),
    ( 3.0, 26.0,  13.0, 36.0, "J2 BNC out\n(-> faceplate)"),
    ( 3.0, 44.0,  13.0, 53.0, "J3 trigger bus"),
]
PARTITION_X = 59.0       # rear of this line = digital; front = analog

OUT_NAME_DXF = "module_pcb_outline.dxf"
OUT_NAME_PNG = "module_pcb_floorplan.png"


def build_dxf(path):
    import ezdxf
    doc = ezdxf.new("R2010")
    doc.layers.add("Edge.Cuts", color=7)
    doc.layers.add("User.Comments", color=4)
    doc.layers.add("User.Drawings", color=3)
    msp = doc.modelspace()

    # board outline + mounting holes -> Edge.Cuts
    msp.add_lwpolyline(
        [(0, 0), (BOARD_W, 0), (BOARD_W, BOARD_H), (0, BOARD_H)],
        close=True, dxfattribs={"layer": "Edge.Cuts"})
    for (x, y) in MOUNTS:
        msp.add_circle((x, y), MOUNT_DIA / 2.0, dxfattribs={"layer": "Edge.Cuts"})

    # placement zones -> User.Comments
    for (x0, y0, x1, y1, label) in ZONES:
        msp.add_lwpolyline([(x0, y0), (x1, y0), (x1, y1), (x0, y1)],
                           close=True, dxfattribs={"layer": "User.Comments"})
        msp.add_text(label.replace("\n", " / "),
                     dxfattribs={"layer": "User.Comments", "height": 1.6}
                     ).set_placement((x0 + 0.6, y1 - 2.2))

    # analog / digital partition + notes -> User.Drawings
    msp.add_line((PARTITION_X, 0), (PARTITION_X, BOARD_H),
                 dxfattribs={"layer": "User.Drawings"})
    for txt, pos in [
        ("PMVB module host-PCB outline (shared template)", (2, BOARD_H + 4)),
        ("DIGITAL (rear)", (PARTITION_X + 4, 44)),
        ("ANALOG (front)", (42, 16)),
        ("front edge -> faceplate / BNC", (2, -5)),
    ]:
        msp.add_text(txt, dxfattribs={"layer": "User.Drawings", "height": 2.0}
                     ).set_placement(pos)
    doc.saveas(path)


def build_png(path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle, Circle

    fig, ax = plt.subplots(figsize=(11, 6.5))
    ax.add_patch(Rectangle((0, 0), BOARD_W, BOARD_H, fill=False, lw=2.2,
                           edgecolor="#1a1a2e"))
    for (x, y) in MOUNTS:
        ax.add_patch(Circle((x, y), MOUNT_DIA / 2.0, fill=False, lw=1.4,
                            edgecolor="#1a1a2e"))
    ax.axvline(PARTITION_X, color="#888", ls="--", lw=1.0)
    for (x0, y0, x1, y1, label) in ZONES:
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=True,
                               facecolor="#cfe3ff", edgecolor="#0f3460", lw=1.3))
        ax.text((x0 + x1) / 2, (y0 + y1) / 2, label, ha="center", va="center",
                fontsize=8)
    ax.text(PARTITION_X + 4, 44, "DIGITAL (rear)", fontsize=8,
            style="italic", color="#555")
    ax.text(42, 16, "ANALOG (front)", fontsize=8, style="italic",
            color="#555")
    ax.text(2, -7, "front edge -> faceplate / BNC      signal flow: rear -> front",
            fontsize=8, color="#555")
    ax.set_xlim(-8, BOARD_W + 8)
    ax.set_ylim(-12, BOARD_H + 10)
    ax.set_aspect("equal")
    ax.set_xlabel("X  (chassis depth, mm)")
    ax.set_ylabel("Y  (chassis height, mm)")
    ax.set_title("PMVB module host-PCB floorplan  (%g x %g mm, shared template)"
                 % (BOARD_W, BOARD_H))
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


if __name__ == "__main__":
    out_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(
        os.path.abspath(__file__))
    dxf_path = os.path.join(out_dir, OUT_NAME_DXF)
    png_path = os.path.join(out_dir, OUT_NAME_PNG)
    build_dxf(dxf_path)
    build_png(png_path)
    print("Wrote %s" % dxf_path)
    print("Wrote %s" % png_path)
    print("Board: %g x %g mm, 4x M2.5 mounts, %d placement zones"
          % (BOARD_W, BOARD_H, len(ZONES)))
