# Replacement chassis STL builder using boolean operations (manifold3d backend).
# Replaces make_chassis_stl() and build_groove_plate_mesh() in generate_prototype_v10.py.

import trimesh

def make_chassis_stl(CHASSIS_W, CHASSIS_D, CHASSIS_H, PANEL_T,
                     N_SLOTS, SLOT_X0, SLOT_PITCH, MODULE_OUTER_W,
                     LIP_W, GROOVE_W, SLOT_GROOVE_LEN):
    """
    Single coherent chassis mesh:
      - 5 walls (floor, ceiling, left, right, rear; front is OPEN for module insertion)
      - bottom groove plate at Z = 3..6 with 14 through-cuts
      - top groove plate at Z = 86..89 with 14 through-cuts
    Module slot pattern offset rightward by SLOT_X0 to leave TX300 zone clear.
    """
    # Outer envelope
    outer = trimesh.creation.box(extents=[CHASSIS_W, CHASSIS_D, CHASSIS_H])
    outer.apply_translation([CHASSIS_W / 2, CHASSIS_D / 2, CHASSIS_H / 2])

    # Inner cavity that includes the front face (front wall removed)
    # Y extent: from below front face (negative Y) to inside-rear (CHASSIS_D - PANEL_T)
    cavity_w = CHASSIS_W - 2 * PANEL_T
    cavity_d = CHASSIS_D - PANEL_T + 1.0   # +1 mm to clear front face cleanly
    cavity_h = CHASSIS_H - 2 * PANEL_T
    cavity = trimesh.creation.box(extents=[cavity_w, cavity_d, cavity_h])
    cavity.apply_translation([
        CHASSIS_W / 2,
        (cavity_d / 2) - 0.5,            # offset toward Y=0 so front is open
        CHASSIS_H / 2,
    ])
    chassis = outer.difference(cavity)

    # Bottom and top groove plates
    bot_plate = make_groove_plate_with_holes(
        z_bottom=PANEL_T,
        CHASSIS_W=CHASSIS_W, CHASSIS_D=CHASSIS_D, PANEL_T=PANEL_T,
        N_SLOTS=N_SLOTS, SLOT_X0=SLOT_X0, SLOT_PITCH=SLOT_PITCH,
        MODULE_OUTER_W=MODULE_OUTER_W, LIP_W=LIP_W,
        GROOVE_W=GROOVE_W, SLOT_GROOVE_LEN=SLOT_GROOVE_LEN,
    )
    top_plate = make_groove_plate_with_holes(
        z_bottom=CHASSIS_H - 2 * PANEL_T,
        CHASSIS_W=CHASSIS_W, CHASSIS_D=CHASSIS_D, PANEL_T=PANEL_T,
        N_SLOTS=N_SLOTS, SLOT_X0=SLOT_X0, SLOT_PITCH=SLOT_PITCH,
        MODULE_OUTER_W=MODULE_OUTER_W, LIP_W=LIP_W,
        GROOVE_W=GROOVE_W, SLOT_GROOVE_LEN=SLOT_GROOVE_LEN,
    )
    chassis = chassis.union(bot_plate)
    chassis = chassis.union(top_plate)

    return chassis


def make_groove_plate_with_holes(z_bottom, *,
                                  CHASSIS_W, CHASSIS_D, PANEL_T,
                                  N_SLOTS, SLOT_X0, SLOT_PITCH,
                                  MODULE_OUTER_W, LIP_W,
                                  GROOVE_W, SLOT_GROOVE_LEN):
    """
    Build a single groove-plate mesh: solid plate that fills the chassis cavity
    in X and Y, sized PANEL_T thick, with 14 rectangular through-cuts where
    module lips engage. Through-cuts run from the front of the chassis
    (Y = PANEL_T) for SLOT_GROOVE_LEN mm rearward (Y = PANEL_T + 125 mm).
    """
    plate_w = CHASSIS_W - 2 * PANEL_T
    plate_d = CHASSIS_D - 2 * PANEL_T
    plate = trimesh.creation.box(extents=[plate_w, plate_d, PANEL_T])
    plate.apply_translation([
        CHASSIS_W / 2,
        CHASSIS_D / 2,
        z_bottom + PANEL_T / 2,
    ])

    # Build all 14 cutout boxes, union them, then subtract once
    cutouts = []
    for i in range(N_SLOTS):
        slot_left_x = SLOT_X0 + i * SLOT_PITCH
        lip_left_x = slot_left_x + MODULE_OUTER_W - LIP_W
        groove_x0 = lip_left_x - (GROOVE_W - LIP_W) / 2
        cutout = trimesh.creation.box(
            extents=[GROOVE_W, SLOT_GROOVE_LEN, PANEL_T + 0.2]
        )
        cutout.apply_translation([
            groove_x0 + GROOVE_W / 2,
            PANEL_T + SLOT_GROOVE_LEN / 2,
            z_bottom + PANEL_T / 2,
        ])
        cutouts.append(cutout)

    cuts_union = cutouts[0]
    for c in cutouts[1:]:
        cuts_union = cuts_union.union(c)

    return plate.difference(cuts_union)
