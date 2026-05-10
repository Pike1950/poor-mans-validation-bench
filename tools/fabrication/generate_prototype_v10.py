"""
PMVB prototype fabrication file generator (v10 geometry).

Outputs three files for the JLCPCB prototype quote + Tinkercad import:
  - module_body_v10.stl   : single module body (FDM PLA via JLCPCB; Tinkercad)
  - chassis_v10.dxf       : 6 nested acrylic panels (laser cut via JLCPCB)
  - chassis_v10.stl       : assembled chassis (Tinkercad import only)

All dimensions in mm. Constants at top — edit and re-run to regenerate.

Author: Brad Ward + Claude
Date: 2026-05-09
"""

from pathlib import Path
import ezdxf
import numpy as np
import trimesh
from shapely.geometry import Polygon

# ---------------------------------------------------------------
# v10 design constants (JLCPCB-FDM-compliant)
# ---------------------------------------------------------------

# Module geometry
MODULE_OUTER_W      = 16.3   # X: total module width including lip
MODULE_OUTER_L      = 125.0  # Y: module length (front-to-back)
MODULE_OUTER_H      = 86.0   # Z: total module height including top + bottom lips
SHELL_T             = 6.0    # Z: top and bottom shell thickness
RIGHT_WALL_T        = 2.0    # X: right wall thickness (FDM rule: >=2.0 at this area)
LIP_W               = 1.5    # X: lip width (FDM rule: >=1.5 protrusion minimum)
LIP_H               = 3.0    # Z: lip vertical extent (above shell or below shell)

# Derived module dims
MODULE_BODY_H       = MODULE_OUTER_H - 2 * LIP_H   # 80 mm body height
CAVITY_W            = MODULE_OUTER_W - RIGHT_WALL_T  # 14.3 mm
CAVITY_H            = MODULE_BODY_H - 2 * SHELL_T    # 68 mm

# Chassis geometry
CHASSIS_W           = 435.0  # widened from 420 to clear front-left standoff vs TX300 (2026-05-10)
CHASSIS_D           = 238.0
CHASSIS_H           = 92.0   # bumped from 90 to fit lip-and-groove stack
PANEL_T             = 3.0    # acrylic thickness for chassis panels
SLOT_PITCH          = 22.5
N_SLOTS             = 14
GROOVE_W            = LIP_W + 0.5  # 2.0 mm = 1.5 lip + 0.5 sliding clearance
GROOVE_DEPTH        = LIP_H        # full plate thickness, through-cut
SLOT_GROOVE_LEN     = 125.0        # along Y, matches module length

# First module slot starts X mm in from left wall.
# TX300 zone occupies x = 0 to 86 mm (left side of chassis); 4 mm air gap;
# module slot zone starts at x = 90 mm and extends 309 mm rightward.
TX300_LEFT_CLEAR    = 10.0   # standoff (5 mm hex at x=5) plus 2.5 mm clearance
TX300_ZONE_W        = 86.0   # left-side width reserved for TX300
TX300_GAP           = 4.0    # air gap between TX300 zone and first module slot
SLOT_X0             = TX300_LEFT_CLEAR + TX300_ZONE_W + TX300_GAP   # 100 mm

# Layout offsets for nested DXF panels (panel-to-panel gap)
DXF_GAP             = 10.0

OUT_DIR = Path(__file__).parent / "out"
OUT_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------
# Module body STL
# ---------------------------------------------------------------

def make_module_body() -> trimesh.Trimesh:
    """
    Build the module body as a 2D cross-section extruded along Y.

    Cross-section (XZ plane, looking down +Y), outer envelope 16.3 × 86 mm
    plus 1.5 × 3 mm lips at top-right and bottom-right going +Z and -Z
    respectively. Going clockwise from bottom-left:
    """
    # Body proper sits Z=3 to Z=83 (80 mm tall)
    # Bottom lip: Z=0 to Z=3, X=14.8 to X=16.3 (right side of bottom shell)
    # Top lip: Z=83 to Z=86, X=14.8 to X=16.3
    # Cavity: X=0 to X=14.3, Z=9 to Z=77 (i.e. inside shells)

    body_z0 = LIP_H               # bottom of body proper (above bottom lip)
    body_z1 = LIP_H + MODULE_BODY_H  # top of body proper
    cavity_z0 = body_z0 + SHELL_T
    cavity_z1 = body_z1 - SHELL_T
    cavity_x1 = MODULE_OUTER_W - RIGHT_WALL_T  # right edge of cavity
    lip_x0 = MODULE_OUTER_W - LIP_W            # left edge of lip
    lip_x1 = MODULE_OUTER_W                    # right edge of lip

    # Trace clockwise from bottom-left of bottom lip
    pts = [
        (lip_x0,    0),                # left edge of bottom lip, going up
        (lip_x0,    body_z0),          # body's bottom-right area
        (0,         body_z0),          # along bottom of body to left edge
        (0,         body_z0 + SHELL_T),# up the inside-left of bottom shell
        # ^^^ wait, body bottom outline goes ALONG bottom of body proper
        # Let me redo this more carefully below.
    ]

    # Restart with explicit coordinates, clockwise:
    pts = [
        # Bottom lip outline (clockwise from bottom-left)
        (lip_x0,        0),
        (lip_x1,        0),
        # Up right side: through bottom lip, body, top lip
        (lip_x1,        MODULE_OUTER_H),
        # Top lip top edge going left
        (lip_x0,        MODULE_OUTER_H),
        # Top lip left edge going down to body top
        (lip_x0,        body_z1),
        # Body top going left to left edge
        (0,             body_z1),
        # Left edge of top shell going down to cavity ceiling
        (0,             cavity_z1),
        # Cavity ceiling going right
        (cavity_x1,     cavity_z1),
        # Cavity right wall going down (this is the LEFT face of right wall)
        (cavity_x1,     cavity_z0),
        # Cavity floor going left
        (0,             cavity_z0),
        # Left edge of bottom shell going down to body bottom
        (0,             body_z0),
        # Body bottom going right back to bottom lip
        (lip_x0,        body_z0),
        # Down the left edge of bottom lip back to start
        (lip_x0,        0),
    ]

    poly = Polygon(pts)
    if not poly.is_valid:
        raise ValueError(f"Cross-section polygon invalid: {poly}")

    # Extrude along Y by MODULE_OUTER_L (125 mm)
    mesh = trimesh.creation.extrude_polygon(poly, height=MODULE_OUTER_L)
    # extrude_polygon extrudes along Z by default; rotate so extrusion is along Y
    mesh.apply_transform(trimesh.transformations.rotation_matrix(
        angle=-np.pi / 2, direction=[1, 0, 0], point=[0, 0, 0]
    ))
    # Translate so bbox min is at origin (rotation puts Z negative)
    mesh.apply_translation([-mesh.bounds[0, 0], -mesh.bounds[0, 1], -mesh.bounds[0, 2]])
    return mesh


# ---------------------------------------------------------------
# Chassis DXF (6 panels nested)
# ---------------------------------------------------------------

def add_rect(msp, x, y, w, h):
    """Add a closed rectangular polyline at (x,y) with width w, height h."""
    pts = [(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)]
    msp.add_lwpolyline(pts, close=True)


def add_groove_plate(msp, ox, oy):
    """
    Add a chassis groove plate (top OR bottom) at offset (ox, oy).
    Outer rectangle is CHASSIS_W × CHASSIS_D. 14 rectangular through-cuts
    for module lips, GROOVE_W wide × SLOT_GROOVE_LEN long, at the rear of
    the slot (modules slide in from front, rear-anchored grooves keep the
    cut span equal to the module length).
    """
    # Outer perimeter
    add_rect(msp, ox, oy, CHASSIS_W, CHASSIS_D)

    # Modules slide in +Y from front (Y=0 in chassis frame), so groove
    # cuts run from Y=0 to Y=SLOT_GROOVE_LEN.
    groove_y0 = oy
    groove_y1 = oy + SLOT_GROOVE_LEN

    # Lip is at top-right corner of module: X position is at module's right
    # edge = SLOT_X0 + i*SLOT_PITCH + MODULE_OUTER_W - LIP_W
    # We want the groove centered on the lip with 0.25 mm clearance on
    # each side (total 0.5 mm clearance).
    for i in range(N_SLOTS):
        slot_left_x = ox + SLOT_X0 + i * SLOT_PITCH
        lip_left_x = slot_left_x + MODULE_OUTER_W - LIP_W
        # Groove is GROOVE_W wide centered on lip
        groove_x0 = lip_left_x - (GROOVE_W - LIP_W) / 2
        # Add the groove cutout as a closed rectangle (through-cut)
        pts = [
            (groove_x0,           groove_y0),
            (groove_x0 + GROOVE_W, groove_y0),
            (groove_x0 + GROOVE_W, groove_y1),
            (groove_x0,           groove_y1),
            (groove_x0,           groove_y0),
        ]
        msp.add_lwpolyline(pts, close=True)


def make_chassis_dxf() -> Path:
    doc = ezdxf.new(dxfversion="R2010")
    msp = doc.modelspace()

    # Layout 6 panels in a row left-to-right (DXF units = mm)
    # Panel 1: Bottom solid panel (CHASSIS_W × CHASSIS_D)
    x_cursor = 0
    add_rect(msp, x_cursor, 0, CHASSIS_W, CHASSIS_D)
    x_cursor += CHASSIS_W + DXF_GAP

    # Panel 2: Bottom groove plate
    add_groove_plate(msp, x_cursor, 0)
    x_cursor += CHASSIS_W + DXF_GAP

    # Panel 3: Top groove plate
    add_groove_plate(msp, x_cursor, 0)
    x_cursor += CHASSIS_W + DXF_GAP

    # Panel 4: Top solid panel
    add_rect(msp, x_cursor, 0, CHASSIS_W, CHASSIS_D)
    x_cursor += CHASSIS_W + DXF_GAP

    # Panel 5: Left side wall (CHASSIS_D × CHASSIS_H)
    add_rect(msp, x_cursor, 0, CHASSIS_D, CHASSIS_H)
    x_cursor += CHASSIS_D + DXF_GAP

    # Panel 6: Right side wall
    add_rect(msp, x_cursor, 0, CHASSIS_D, CHASSIS_H)

    out_path = OUT_DIR / "chassis_v10.dxf"
    doc.saveas(out_path)
    return out_path


# ---------------------------------------------------------------
# Chassis assembled STL (for Tinkercad)
# Uses boolean operations from _chassis_stl_v2 for a single coherent mesh.
# ---------------------------------------------------------------

import sys as _sys
_sys.path.insert(0, str(Path(__file__).parent))
from _chassis_stl_v2 import make_chassis_stl as _make_chassis_stl


def make_chassis_stl():
    return _make_chassis_stl(
        CHASSIS_W=CHASSIS_W, CHASSIS_D=CHASSIS_D, CHASSIS_H=CHASSIS_H,
        PANEL_T=PANEL_T,
        N_SLOTS=N_SLOTS, SLOT_X0=SLOT_X0, SLOT_PITCH=SLOT_PITCH,
        MODULE_OUTER_W=MODULE_OUTER_W, LIP_W=LIP_W,
        GROOVE_W=GROOVE_W, SLOT_GROOVE_LEN=SLOT_GROOVE_LEN,
    )


# ---------------------------------------------------------------
# Main
# ---------------------------------------------------------------

if __name__ == "__main__":
    print("PMVB v10 prototype generator")
    print(f"Output dir: {OUT_DIR}")

    # Module body STL
    module_mesh = make_module_body()
    module_path = OUT_DIR / "module_body_v10.stl"
    module_mesh.export(module_path)
    print(f"  {module_path.name}: {module_path.stat().st_size / 1024:.1f} KB, "
          f"bbox = {module_mesh.bounds}")

    # Chassis DXF
    chassis_dxf = make_chassis_dxf()
    print(f"  {chassis_dxf.name}: {chassis_dxf.stat().st_size / 1024:.1f} KB")

    # Chassis assembled STL
    chassis_mesh = make_chassis_stl()
    chassis_path = OUT_DIR / "chassis_v10.stl"
    chassis_mesh.export(chassis_path)
    print(f"  {chassis_path.name}: {chassis_path.stat().st_size / 1024:.1f} KB, "
          f"bbox = {chassis_mesh.bounds}")

    print()
    print("Geometry summary (v10):")
    print(f"  Module: {MODULE_OUTER_W} × {MODULE_OUTER_L} × {MODULE_OUTER_H} mm")
    print(f"  Lip:    {LIP_W} × {LIP_H} mm × {MODULE_OUTER_L} mm")
    print(f"  Cavity: {CAVITY_W} × {MODULE_OUTER_L} × {CAVITY_H} mm")
 