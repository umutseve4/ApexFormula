"""ApexFormula - deterministic placeholder vehicle generation.

Milestone 0B.

Builds the blocked-out ApexFormula prototype vehicle from the design values in
``af_pipeline_config``. Nothing here is final art: this is a proportion-correct
placeholder whose purpose is to exercise the whole Blender -> Unreal pipeline
with measurable, checkable geometry.

What it creates, all inside AF_Generated:
  * AF_Body_Proto      - one merged body mesh (nose, monocoque, cockpit,
                         sidepods, front wing, rear wing, halo)
  * AF_Wheel_FL/FR/RL/RR - cylindrical tyre proxies, correctly placed
  * AF_Susp_FL/FR/RL/RR  - simple arm proxies from pickup to wheel centre
  * UCX_AF_Body_Proto_01..05 - convex collision boxes
  * LOD meshes for the body, driven by LOD_RATIOS

Determinism: the mesh is built from explicit vertex lists and config values.
The same config always produces the same vertices in the same order.

Design envelope (D-040): the halo arc height is solved from
``overall_height_m`` rather than being a fixed multiple of ``halo_radius_m``,
so the tallest point of the vehicle can never breach the design envelope.
``check_design_envelope`` re-measures the whole vehicle in pure Python before
Blender is touched, so an envelope regression fails fast and locally instead
of surfacing later as a validate-stage failure.

Face winding (D-047): every face produced here is wound counter-clockwise as
seen from outside the solid, so the outward normal follows the right-hand
rule and the signed volume of any closed block is positive. Tools/
af_mesh_quality.py check C6 enforces this. Inward winding is not a cosmetic
detail: it inverts lighting, hides surfaces under backface culling, and
travels through the FBX into Unreal.

Usage
-----
    blender --background --python af_vehicle_generate.py

Exit codes: 0 success, 2 Blender API unavailable, 3 generation failed.
"""

from __future__ import annotations

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import af_pipeline_config as cfg  # noqa: E402

try:
    import bpy
except ImportError:  # pragma: no cover
    bpy = None


EXIT_OK = 0
EXIT_NO_BPY = 2
EXIT_FAILED = 3


# ---------------------------------------------------------------------------
# Halo geometry (D-040)
# ---------------------------------------------------------------------------
#
# The halo is the tallest structure on the vehicle, so its vertical extent is
# derived from the design envelope instead of being an independent constant.
# Previously the arc height was ``halo_radius_m * 0.55``, which placed the top
# surface at 0.97415 m against an ``overall_height_m`` of 0.950 m - a 0.02415 m
# breach, well outside TOLERANCE["length_m"] (0.010 m).

HALO_SEGMENTS = 12
HALO_APEX_CLEARANCE_M = 0.010


def halo_segment_thetas():
    """Return the fixed half-ring angles used to place the halo segments."""
    return tuple(math.pi * i / (HALO_SEGMENTS - 1) for i in range(HALO_SEGMENTS))


def halo_max_sin():
    """Return the largest ``sin(theta)`` actually hit by the segment set.

    With an even segment count no segment lands exactly on the apex, so the
    real peak is slightly below 1.0. Using the sampled maximum keeps the
    solved arc height exact rather than conservative.
    """
    return max(math.sin(theta) for theta in halo_segment_thetas())


def halo_base_z_m():
    """Return the Z the halo ring is built up from: the top of the chassis."""
    return cfg.DESIGN["ride_height_m"] + cfg.DESIGN["chassis_top_m"]


def halo_arc_height_m():
    """Return the halo arc height solved from the design envelope.

    Solved so the top surface of the highest halo segment lands exactly
    ``HALO_APEX_CLEARANCE_M`` below ``overall_height_m``. Never taller than
    ``halo_radius_m``, so a generous envelope cannot inflate the halo into a
    shape the radius does not describe.
    """
    headroom = (cfg.DESIGN["overall_height_m"]
                - HALO_APEX_CLEARANCE_M
                - halo_base_z_m()
                - cfg.DESIGN["halo_thickness_m"] / 2.0)
    solved = headroom / (0.5 + halo_max_sin())
    return min(solved, cfg.DESIGN["halo_radius_m"])


def halo_apex_z_m():
    """Return the Z of the topmost halo surface, including segment thickness."""
    return (halo_base_z_m()
            + halo_arc_height_m() * (0.5 + halo_max_sin())
            + cfg.DESIGN["halo_thickness_m"] / 2.0)


# ---------------------------------------------------------------------------
# Pure geometry helpers - no bpy, unit-testable outside Blender
# ---------------------------------------------------------------------------

def box_mesh(centre, half_extent):
    """Return ``(verts, faces)`` for an axis-aligned box.

    Vertex order is fixed so the output is deterministic.

    Faces are wound counter-clockwise seen from outside the box (D-047), so
    every outward normal follows the right-hand rule and the signed volume is
    positive. The comment on each face names the outward direction.
    """
    cx, cy, cz = centre
    hx, hy, hz = half_extent
    verts = [
        (cx - hx, cy - hy, cz - hz),
        (cx + hx, cy - hy, cz - hz),
        (cx + hx, cy + hy, cz - hz),
        (cx - hx, cy + hy, cz - hz),
        (cx - hx, cy - hy, cz + hz),
        (cx + hx, cy - hy, cz + hz),
        (cx + hx, cy + hy, cz + hz),
        (cx - hx, cy + hy, cz + hz),
    ]
    faces = [
        (3, 2, 1, 0),  # bottom, outward -Z
        (5, 6, 7, 4),  # top,    outward +Z
        (1, 5, 4, 0),  # outward -Y
        (2, 6, 5, 1),  # outward +X
        (3, 7, 6, 2),  # outward +Y
        (0, 4, 7, 3),  # outward -X
    ]
    return verts, faces


def cylinder_mesh(centre, radius, width, segments, axis="Y"):
    """Return ``(verts, faces)`` for a closed cylinder.

    ``axis`` is the cylinder's spin axis. Wheels spin about Y in the
    ApexFormula convention (+Y is vehicle left).

    Side quads and both cap fans are wound so their normals point away from
    the cylinder body (D-047): the sides face radially outward, the -offset
    cap faces along the negative axis and the +offset cap along the positive
    axis. The signed volume of the result is positive.
    """
    if segments < 3:
        raise ValueError("a cylinder needs at least 3 segments")

    cx, cy, cz = centre
    half = width * 0.5
    verts = []

    for side_index, offset in enumerate((-half, +half)):
        for i in range(segments):
            theta = 2.0 * math.pi * i / segments
            a = radius * math.cos(theta)
            b = radius * math.sin(theta)
            if axis == "Y":
                verts.append((cx + a, cy + offset, cz + b))
            elif axis == "X":
                verts.append((cx + offset, cy + a, cz + b))
            else:
                verts.append((cx + a, cy + b, cz + offset))
        del side_index

    faces = []
    for i in range(segments):
        nxt = (i + 1) % segments
        faces.append((segments + i, segments + nxt, nxt, i))

    # Cap fans, using a centre vertex per side so caps stay planar n-gons free.
    left_centre = len(verts)
    verts.append((cx, cy - half, cz) if axis == "Y" else
                 ((cx - half, cy, cz) if axis == "X" else (cx, cy, cz - half)))
    right_centre = len(verts)
    verts.append((cx, cy + half, cz) if axis == "Y" else
                 ((cx + half, cy, cz) if axis == "X" else (cx, cy, cz + half)))

    for i in range(segments):
        nxt = (i + 1) % segments
        faces.append((left_centre, i, nxt))
        faces.append((right_centre, segments + nxt, segments + i))

    return verts, faces


def merge_meshes(parts):
    """Merge ``[(verts, faces), ...]`` into one ``(verts, faces)`` pair."""
    all_verts = []
    all_faces = []
    for verts, faces in parts:
        offset = len(all_verts)
        all_verts.extend(verts)
        all_faces.extend(tuple(index + offset for index in face) for face in faces)
    return all_verts, all_faces


def body_parts():
    """Return the list of ``(verts, faces)`` blocks making up the body.

    Every position is derived from ``cfg.DESIGN``; nothing is hardcoded here.
    """
    d = cfg.DESIGN
    front_axle = cfg.FRONT_AXLE_X_M
    rear_axle = cfg.REAR_AXLE_X_M
    nose_tip_x = front_axle + (d["overall_length_m"] / 2.0 - front_axle)

    parts = []

    # Monocoque: spans from just behind the front axle back towards the rear.
    mono_front = front_axle - 0.30
    mono_rear = rear_axle + 0.40
    mono_len = mono_front - mono_rear
    parts.append(box_mesh(
        ((mono_front + mono_rear) / 2.0, 0.0, d["ride_height_m"] + d["chassis_top_m"] / 2.0),
        (mono_len / 2.0, d["cockpit_width_m"] / 2.0, d["chassis_top_m"] / 2.0)))

    # Cockpit surround, sitting on top of the monocoque.
    cockpit_centre_x = mono_front - d["cockpit_length_m"] / 2.0
    parts.append(box_mesh(
        (cockpit_centre_x, 0.0, d["ride_height_m"] + d["chassis_top_m"] + 0.06),
        (d["cockpit_length_m"] / 2.0, d["cockpit_width_m"] / 2.0 * 0.85, 0.06)))

    # Nose cone, tapering forward from the monocoque towards the wing.
    nose_rear_x = mono_front
    nose_front_x = nose_rear_x + d["nose_length_m"]
    parts.append(box_mesh(
        ((nose_front_x + nose_rear_x) / 2.0, 0.0,
         d["ride_height_m"] + d["nose_height_m"] / 2.0 + 0.10),
        (d["nose_length_m"] / 2.0, d["nose_width_m"] / 2.0, d["nose_height_m"] / 2.0)))

    # Front wing at the very front of the vehicle.
    parts.append(box_mesh(
        (nose_tip_x - d["front_wing_chord_m"] / 2.0, 0.0,
         d["ride_height_m"] + d["front_wing_thickness_m"] / 2.0),
        (d["front_wing_chord_m"] / 2.0, d["front_wing_span_m"] / 2.0,
         d["front_wing_thickness_m"] / 2.0)))

    # Sidepods, mirrored about Y = 0.
    sidepod_centre_x = (mono_front + mono_rear) / 2.0 - 0.10
    sidepod_y = d["cockpit_width_m"] / 2.0 + d["sidepod_width_m"] / 2.0
    for y_sign in (1.0, -1.0):
        parts.append(box_mesh(
            (sidepod_centre_x, y_sign * sidepod_y,
             d["ride_height_m"] + d["sidepod_height_m"] / 2.0),
            (d["sidepod_length_m"] / 2.0, d["sidepod_width_m"] / 2.0,
             d["sidepod_height_m"] / 2.0)))

    # Rear structure / engine cover.
    parts.append(box_mesh(
        (rear_axle + 0.10, 0.0, d["ride_height_m"] + d["chassis_top_m"] / 2.0 + 0.05),
        (0.70, d["cockpit_width_m"] / 2.0 * 0.80, d["chassis_top_m"] / 2.0 + 0.05)))

    # Rear wing plane plus two endplates.
    rear_wing_x = -d["overall_length_m"] / 2.0 + d["rear_wing_chord_m"] / 2.0
    parts.append(box_mesh(
        (rear_wing_x, 0.0, d["rear_wing_height_m"]),
        (d["rear_wing_chord_m"] / 2.0, d["rear_wing_span_m"] / 2.0,
         d["rear_wing_thickness_m"] / 2.0)))
    for y_sign in (1.0, -1.0):
        parts.append(box_mesh(
            (rear_wing_x, y_sign * d["rear_wing_span_m"] / 2.0,
             d["rear_wing_height_m"] - 0.12),
            (d["rear_wing_chord_m"] / 2.0, 0.02, 0.16)))

    # Halo: a thin ring approximated by segments around the cockpit opening.
    # The arc height is solved from the design envelope (D-040), so the apex
    # cannot breach overall_height_m no matter how the envelope is retuned.
    halo_centre_x = cockpit_centre_x - 0.10
    halo_base_z = halo_base_z_m()
    halo_arc = halo_arc_height_m()
    for theta in halo_segment_thetas():  # half ring, over the top
        y = d["halo_radius_m"] * math.cos(theta)
        z = halo_arc * math.sin(theta)
        parts.append(box_mesh(
            (halo_centre_x, y, halo_base_z + halo_arc * 0.5 + z),
            (d["halo_thickness_m"] / 2.0, d["halo_thickness_m"] / 2.0,
             d["halo_thickness_m"] / 2.0)))

    return parts


def suspension_arm_parts(corner):
    """Return the box blocks for one suspension corner."""
    pickup = cfg.suspension_pickup_m(corner)
    hub = cfg.wheel_centre_m(corner)

    centre = tuple((p + h) / 2.0 for p, h in zip(pickup, hub))
    span = tuple(abs(h - p) for p, h in zip(pickup, hub))
    half = (max(span[0] / 2.0, 0.030),
            max(span[1] / 2.0, 0.030),
            max(span[2] / 2.0, 0.030))
    return [box_mesh(centre, half)]


# ---------------------------------------------------------------------------
# Pre-flight design envelope check (D-040) - pure Python, no bpy
# ---------------------------------------------------------------------------

def measured_bounds_m():
    """Return ``(min_xyz, max_xyz, size_xyz)`` over body, wheels and arms.

    Mirrors exactly what af_validate.py check 17 measures in Blender: the
    render meshes that ship, excluding LOD copies (which are duplicates of the
    body) and excluding UCX collision hulls.
    """
    verts = []
    for part_verts, _faces in body_parts():
        verts.extend(part_verts)

    for corner in cfg.CORNERS:
        wheel_verts, _faces = cylinder_mesh(
            cfg.wheel_centre_m(corner),
            cfg.wheel_radius_m(corner),
            cfg.wheel_width_m(corner),
            cfg.DESIGN["wheel_segments"],
            axis="Y")
        verts.extend(wheel_verts)
        for arm_verts, _arm_faces in suspension_arm_parts(corner):
            verts.extend(arm_verts)

    if not verts:
        raise RuntimeError("no geometry produced - cannot measure bounds")

    minimum = tuple(min(v[axis] for v in verts) for axis in range(3))
    maximum = tuple(max(v[axis] for v in verts) for axis in range(3))
    size = tuple(maximum[axis] - minimum[axis] for axis in range(3))
    return minimum, maximum, size


def check_design_envelope():
    """Return ``(ok, problems)`` for the measured-vs-design bounding box.

    Runs before Blender is touched so an envelope regression is caught at the
    top of the pipeline rather than four stages later. Being smaller than the
    envelope is fine; being larger than it by more than the length tolerance
    is not - that is the exact rule af_validate.py check 17 applies.
    """
    problems = []
    tol = cfg.TOLERANCE["length_m"]

    try:
        _minimum, _maximum, size = measured_bounds_m()
    except Exception as exc:  # noqa: BLE001
        return False, ["could not measure geometry: %s: %s"
                       % (type(exc).__name__, exc)]

    design = (cfg.DESIGN["overall_length_m"],
              cfg.DESIGN["overall_width_m"],
              cfg.DESIGN["overall_height_m"])
    for axis, label in enumerate(("length (X)", "width (Y)", "height (Z)")):
        delta = size[axis] - design[axis]
        if delta > tol:
            problems.append(
                "%s: measured %.5f m exceeds design %.3f m by %.5f m "
                "(tolerance %.3f m)" % (label, size[axis], design[axis],
                                        delta, tol))

    apex = halo_apex_z_m()
    if apex > cfg.DESIGN["overall_height_m"]:
        problems.append(
            "halo apex: %.5f m exceeds overall height %.3f m"
            % (apex, cfg.DESIGN["overall_height_m"]))

    if halo_arc_height_m() <= 0.0:
        problems.append(
            "halo arc height solved to %.5f m - the design envelope leaves no "
            "headroom above chassis_top_m" % halo_arc_height_m())

    return (not problems), problems


# ---------------------------------------------------------------------------
# Blender-side construction
# ---------------------------------------------------------------------------

def _collection(name):
    coll = bpy.data.collections.get(name)
    if coll is None:
        raise RuntimeError(
            "collection %r is missing - run af_scene_setup.py first" % (name,))
    return coll


def create_object(name, verts, faces, collection_name):
    """Create a mesh object with an identity transform.

    All geometry is authored in world space, so object transforms stay at
    identity and nothing needs applying later.
    """
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata([tuple(v) for v in verts], [], [tuple(f) for f in faces])
    mesh.validate(verbose=False)
    mesh.update()

    if not mesh.uv_layers:
        mesh.uv_layers.new(name=cfg.UV_MAP_NAME)
    else:
        mesh.uv_layers[0].name = cfg.UV_MAP_NAME

    obj = bpy.data.objects.new(name, mesh)
    obj.location = (0.0, 0.0, 0.0)
    obj.rotation_euler = (0.0, 0.0, 0.0)
    obj.scale = (1.0, 1.0, 1.0)

    _collection(collection_name).objects.link(obj)
    return obj


def generate_body():
    verts, faces = merge_meshes(body_parts())
    return create_object(cfg.body_name(), verts, faces, cfg.COLLECTION_BODY)


def generate_wheels():
    created = []
    for corner in cfg.CORNERS:
        verts, faces = cylinder_mesh(
            cfg.wheel_centre_m(corner),
            cfg.wheel_radius_m(corner),
            cfg.wheel_width_m(corner),
            cfg.DESIGN["wheel_segments"],
            axis="Y")
        created.append(create_object(
            cfg.wheel_name(corner), verts, faces, cfg.COLLECTION_WHEELS))
    return created


def generate_suspension():
    created = []
    for corner in cfg.CORNERS:
        verts, faces = merge_meshes(suspension_arm_parts(corner))
        created.append(create_object(
            cfg.suspension_name(corner), verts, faces, cfg.COLLECTION_SUSPENSION))
    return created


def generate_collision():
    """Create UCX_<render mesh>_NN convex boxes.

    The UCX target name must match the render mesh name exactly, otherwise
    Unreal will not associate the hull with the mesh on import.
    """
    created = []
    target_mesh = cfg.body_name()
    for _target, index, centre, half in cfg.COLLISION_PIECES:
        name = cfg.collision_name(target_mesh, index)
        verts, faces = box_mesh(centre, half)
        obj = create_object(name, verts, faces, cfg.COLLECTION_COLLISION)
        obj.display_type = "WIRE"
        created.append(obj)
    return created


def generate_lods(body_obj):
    """Duplicate the body per LOD level and attach a decimate modifier.

    The modifier is left unapplied here; af_export.py applies modifiers via
    the exporter's ``use_mesh_modifiers`` option so the source stays editable.
    """
    created = []
    for level in cfg.LOD_LEVELS:
        name = cfg.lod_name(cfg.body_name(), level)
        mesh_copy = body_obj.data.copy()
        mesh_copy.name = name
        obj = bpy.data.objects.new(name, mesh_copy)
        obj.location = (0.0, 0.0, 0.0)
        obj.rotation_euler = (0.0, 0.0, 0.0)
        obj.scale = (1.0, 1.0, 1.0)

        modifier = obj.modifiers.new(name=cfg.MODIFIER_DECIMATE,
                                     type="DECIMATE")
        modifier.decimate_type = "COLLAPSE"
        modifier.ratio = cfg.LOD_RATIOS[level]

        _collection(cfg.COLLECTION_LOD).objects.link(obj)
        created.append(obj)
    return created


def generate_all():
    body = generate_body()
    wheels = generate_wheels()
    suspension = generate_suspension()
    collision = generate_collision()
    lods = generate_lods(body)

    return {
        "body": body.name,
        "body_polygons": len(body.data.polygons),
        "body_vertices": len(body.data.vertices),
        "wheels": [o.name for o in wheels],
        "wheel_polygons": {o.name: len(o.data.polygons) for o in wheels},
        "suspension": [o.name for o in suspension],
        "collision": [o.name for o in collision],
        "lods": [o.name for o in lods],
        "lod_ratios": {o.name: o.modifiers[cfg.MODIFIER_DECIMATE].ratio
                       for o in lods},
        "config_hash": cfg.config_hash(),
    }


def print_summary(summary):
    d = cfg.DESIGN
    _minimum, _maximum, size = measured_bounds_m()
    print("")
    print("af_vehicle_generate summary")
    print("  body            : %s (%d polys, %d verts)" % (
        summary["body"], summary["body_polygons"], summary["body_vertices"]))
    print("  wheels          : %s" % ", ".join(summary["wheels"]))
    print("  suspension      : %s" % ", ".join(summary["suspension"]))
    print("  collision hulls : %s" % ", ".join(summary["collision"]))
    print("  LODs            : %s" % ", ".join(
        "%s@%.2f" % (n, r) for n, r in summary["lod_ratios"].items()))
    print("")
    print("  design values used (ApexFormula design values, not regulations):")
    print("    wheelbase     : %.3f m  (%.1f cm)" % (
        d["wheelbase_m"], cfg.metres_to_cm(d["wheelbase_m"])))
    print("    overall length: %.3f m  (%.1f cm)" % (
        d["overall_length_m"], cfg.metres_to_cm(d["overall_length_m"])))
    print("    overall width : %.3f m  (%.1f cm)" % (
        d["overall_width_m"], cfg.metres_to_cm(d["overall_width_m"])))
    print("    track front   : %.3f m  (%.1f cm)" % (
        d["track_front_m"], cfg.metres_to_cm(d["track_front_m"])))
    print("    track rear    : %.3f m  (%.1f cm)" % (
        d["track_rear_m"], cfg.metres_to_cm(d["track_rear_m"])))
    print("")
    print("  measured bounding box vs design envelope (D-040):")
    print("    length (X)    : %.4f m  of %.3f m" % (
        size[0], d["overall_length_m"]))
    print("    width  (Y)    : %.4f m  of %.3f m" % (
        size[1], d["overall_width_m"]))
    print("    height (Z)    : %.4f m  of %.3f m" % (
        size[2], d["overall_height_m"]))
    print("    halo apex     : %.4f m  (arc %.4f m, clearance %.3f m)" % (
        halo_apex_z_m(), halo_arc_height_m(), HALO_APEX_CLEARANCE_M))
    print("  config hash     : %s" % summary["config_hash"][:16])


def main():
    print(cfg.describe())

    ok, problems = cfg.self_check()
    if not ok:
        print("")
        print("config self-check FAILED - refusing to generate geometry:")
        for problem in problems:
            print("  - %s" % problem)
        return EXIT_FAILED

    ok, problems = check_design_envelope()
    if not ok:
        print("")
        print("design envelope check FAILED - refusing to generate geometry:")
        for problem in problems:
            print("  - %s" % problem)
        return EXIT_FAILED

    if bpy is None:
        print("")
        print("bpy is unavailable: this script must be run inside Blender, e.g.")
        print("  blender --background --python af_vehicle_generate.py")
        return EXIT_NO_BPY

    try:
        summary = generate_all()
    except Exception as exc:  # noqa: BLE001
        print("")
        print("af_vehicle_generate FAILED: %s: %s" % (type(exc).__name__, exc))
        return EXIT_FAILED

    print_summary(summary)
    print("")
    print("af_vehicle_generate: OK")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
