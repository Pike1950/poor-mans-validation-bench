"""Chassis STL builder: composes panels and groove plates from solid boxes.
   No boolean operations (avoids manifold3d edge cases that produced
   internal-void cutouts instead of through-holes)."""

import trimesh


def make_chassis_stl(CHASSIS_W, CHASSIS_D, CHASSIS_H, PANEL_T,
                     N_SLOTS, SLOT_X0, SLOT_PITCH, MODULE_OUTER_W,
                     LIP_W, GROOVE_W, SLOT_GROOVE_LEN):
    """v1.0 open-frame chassis: 4 panels (floor, bottom groove plate, top groove
    plate, ceiling), no walls, held by external M3 corner standoffs."""
    parts = []

    # Floor: solid 420 x 238 x 3 mm
    floor = trimesh.creation.box(extents=[CHASSIS_W, CHASSIS_D, PANEL_T])
    floor.apply_translation([CHASSIS_W / 2, CHASSIS_D / 2, PANEL_T / 2])
    parts.append(floor)

    # Bottom groove plate at Z = 3..6
    parts.extend(make_groove_plate_strips(
        z_bottom=PANEL_T,
        CHASSIS_W=CHASSIS_W, CHASSIS_D=CHASSIS_D, PANEL_T=PANEL_T,
        N_SLOTS=N_SLOTS, SLOT_X0=SLOT_X0, SLOT_PITCH=SLOT_PITCH,
        MODULE_OUTER_W=MODULE_OUTER_W, LIP_W=LIP_W,
        GROOVE_W=GROOVE_W, SLOT_GROOVE_LEN=SLOT_GROOVE_LEN,
    ))

    # Top groove plate at Z = CHASSIS_H - 2*PANEL_T = 86..89
    parts.extend(make_groove_plate_strips(
        z_bottom=CHASSIS_H - 2 * PANEL_T,
        CHASSIS_W=CHASSIS_W, CHASSIS_D=CHASSIS_D, PANEL_T=PANEL_T,
        N_SLOTS=N_SLOTS, SLOT_X0=SLOT_X0, SLOT_PITCH=SLOT_PITCH,
        MODULE_OUTER_W=MODULE_OUTER_W, LIP_W=LIP_W,
        GROOVE_W=GROOVE_W, SLOT_GROOVE_LEN=SLOT_GROOVE_LEN,
    ))

    # Ceiling: solid 420 x 238 x 3 mm
    ceiling = trimesh.creation.box(extents=[CHASSIS_W, CHASSIS_D, PANEL_T])
    ceiling.apply_translation([CHASSIS_W / 2, CHASSIS_D / 2, CHASSIS_H - PANEL_T / 2])
    parts.append(ceiling)

    return trimesh.util.concatenate(parts)


def make_groove_plate_strips(z_bottom, *, CHASSIS_W, CHASSIS_D, PANEL_T,
                              N_SLOTS, SLOT_X0, SLOT_PITCH,
                              MODULE_OUTER_W, LIP_W,
                              GROOVE_W, SLOT_GROOVE_LEN):
    """Build a groove plate as a list of solid box strips.
       The plate is 420 x 238 x 3 mm. 14 module-slot cutouts run from Y=0 to
       Y=SLOT_GROOVE_LEN (125 mm), at X positions determined by the slot pitch.
       The back portion of the plate (Y > SLOT_GROOVE_LEN) is fully solid."""
    parts = []

    # Compute the X positions of each groove cutout
    cutouts_x = []  # list of (x0, x1) for each of the 14 cutouts
    for i in range(N_SLOTS):
        slot_left_x = SLOT_X0 + i * SLOT_PITCH
        lip_left_x = slot_left_x + MODULE_OUTER_W - LIP_W
        groove_x0 = lip_left_x - (GROOVE_W - LIP_W) / 2
        cutouts_x.append((groove_x0, groove_x0 + GROOVE_W))

    # 1. Back strip (Y = SLOT_GROOVE_LEN to CHASSIS_D, full width, no cutouts)
    if CHASSIS_D > SLOT_GROOVE_LEN:
        h = CHASSIS_D - SLOT_GROOVE_LEN
        b = trimesh.creation.box(extents=[CHASSIS_W, h, PANEL_T])
        b.apply_translation([CHASSIS_W / 2,
                             SLOT_GROOVE_LEN + h / 2,
                             z_bottom + PANEL_T / 2])
        parts.append(b)

    # 2. Strips between cutouts (Y = 0 to SLOT_GROOVE_LEN)
    cur_x = 0.0
    for x0, x1 in cutouts_x:
        # Solid strip from cur_x to x0
        if x0 > cur_x:
            w = x0 - cur_x
            b = trimesh.creation.box(extents=[w, SLOT_GROOVE_LEN, PANEL_T])
            b.apply_translation([cur_x + w / 2,
                                 SLOT_GROOVE_LEN / 2,
                                 z_bottom + PANEL_T / 2])
            parts.append(b)
        cur_x = x1
    # Final strip from last cutout right edge to CHASSIS_W
    if cur_x < CHASSIS_W:
        w = CHASSIS_W - cur_x
        b = trimesh.creation.box(extents=[w, SLOT_GROOVE_LEN, PANEL_T])
        b.apply_translation([cur_x + w / 2,
                             SLOT_GROOVE_LEN / 2,
                             z_bottom + PANEL_T / 2])
        parts.append(b)

    return parts
