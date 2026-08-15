"""UludagFormula - pipeline configuration (single source of truth).

Milestone 0B.

This module is the ONLY place in the UludagFormula Blender pipeline where the
following are defined:

  * unit system and scale conventions
  * axis / handedness conventions
  * bone names and bone hierarchy
  * collection names
  * object / mesh / material / file naming patterns
  * vehicle design dimensions
  * validation tolerances and budgets
  * FBX export settings

No other script may hardcode any of the above.

IMPORTANT: this module deliberately does NOT import ``bpy``. It contains no
scene operations. It is importable by a plain CPython interpreter so that its
internal consistency can be checked without running Blender.

Honesty note: nothing in this file has been executed inside Blender. The
numbers below are UludagFormula design values chosen for this project. They are
not measurements, and they are not regulations of any real motorsport series.
"""

from __future__ import annotations

import hashlib
import json
import os

# ---------------------------------------------------------------------------
# 0. Identity and versioning
# ---------------------------------------------------------------------------

PROJECT_NAME = "UludagFormula"
ASSET_PREFIX = "AF_"
SCRIPT_PREFIX = "af_"

#: Version of the pipeline contract. Bump when any convention below changes in
#: a way that invalidates previously exported assets.
#: 0B.1.1: wheel MESH objects renamed AF_Wheel_* -> AF_WheelMesh_* (D-079).
#: Bone names are unchanged; previously exported FBX files carry colliding
#: node names and must be re-exported.
#: 0B.1.2: apply_scale_options FBX_SCALE_ALL -> FBX_SCALE_UNITS (D-083).
#: FBX_SCALE_ALL baked the m->cm x100 unit factor into the armature OBJECT
#: node transform, which Unreal Interchange folds into the skeleton root's
#: reference-pose scale (observed as Scale (100,100,100) on
#: AF_Armature_Proto, OPEN-080-A). FBX_SCALE_UNITS carries the conversion in
#: FBX unit metadata instead, so bones import at scale (1,1,1). Previously
#: exported FBX files carry the baked x100 and must be re-exported.
#: 0B.1.3: apply_scale_options FBX_SCALE_UNITS -> FBX_SCALE_NONE (D-089).
#: FBX_SCALE_UNITS keeps vertex/bone numbers in metres and carries the m->cm
#: factor only in FBX unit metadata; the legacy UE FBX importer (active per
#: D-084) ignores that metadata unless "Convert Scene Unit" is checked
#: (default OFF), so the whole vehicle imported at 1/100 size (M5.3 FAIL,
#: bounds X = 5.60 cm instead of 560). FBX_SCALE_NONE applies the unit
#: conversion directly to the exported vertex/bone data, so numbers arrive
#: in cm without relying on importer metadata handling and without baking a
#: node-level x100 (the OPEN-080-A failure mode). Previously exported FBX
#: files carry metre-sized data and must be re-exported.
#: 0B.1.4: export-time cm bake in af_export.py (D-090). FBX_SCALE_NONE alone
#: still produced a root-bone scale of (100,100,100) in UE: the scene data is
#: authored in metres, so the exporter's m->cm x100 unit factor was folded by
#: the legacy importer into the skeleton root's reference pose (bounds were
#: correct at 560, only the root scale was dirty). af_export.py now bakes the
#: x100 into mesh/armature DATA (and object locations) right before export,
#: compensates scene.unit_settings.scale_length to 0.01 so the exporter's
#: effective unit factor becomes 1.0, and unbakes in a finally block so the
#: scene is restored even on failure. Exporter options stay FBX_SCALE_NONE;
#: no fourth apply_scale_options experiment (2nd-FAIL rule, D-087 policy).
PIPELINE_VERSION = "0B.1.4"

#: The Blender version this pipeline targets. Checked at runtime by
#: af_validate.py; a mismatch is reported, never silently accepted.
TARGET_BLENDER_VERSION = (5, 2)

#: The Unreal Engine version this pipeline exports for. Informational on the
#: Blender side; recorded in every report.
TARGET_UNREAL_VERSION = "5.8"

#: Tokens that must never appear in any name produced by this pipeline.
PROHIBITED_NAME_TOKENS = ("F1", "f1", "FIA", "fia")


# ---------------------------------------------------------------------------
# 1. Units and axes  (Documentation/BLENDER_PIPELINE_DESIGN.md section 2)
# ---------------------------------------------------------------------------

#: Blender unit system. 1 Blender unit == 1 metre. Never changed to compensate
#: for a size error.
BLENDER_UNIT_SYSTEM = "METRIC"
BLENDER_LENGTH_UNIT = "METERS"
BLENDER_SCALE_LENGTH = 1.0

#: Authoring convention inside Blender:
#:   +X = vehicle forward
#:   +Y = vehicle LEFT
#:   +Z = up
#: Z = 0 is the tyre contact plane at design ride height.
BLENDER_FORWARD_AXIS = "+X"
BLENDER_LEFT_AXIS = "+Y"
BLENDER_UP_AXIS = "+Z"

#: Unreal convention: 1 uu == 1 cm, +X forward, +Y RIGHT, +Z up, left-handed.
#: The handedness difference is a Y-axis sign flip and nothing else.
UNREAL_FORWARD_AXIS = "+X"
UNREAL_RIGHT_AXIS = "+Y"
UNREAL_UP_AXIS = "+Z"
UNREAL_HANDEDNESS = "left"
BLENDER_HANDEDNESS = "right"

#: The single documented metre -> centimetre factor. Used ONLY when emitting
#: values intended for Unreal. All maths inside the scripts stays in metres.
CM_PER_UNIT = 100.0


def metres_to_cm(value_m):
    """Convert a metre value to the centimetre value quoted to Unreal."""
    return float(value_m) * CM_PER_UNIT


def blender_point_to_unreal_cm(point_m):
    """Map a Blender-space point in metres to an Unreal-space point in cm.

    The mapping is explicit, not vague::

        Unreal.X =  Blender.X * 100      forward stays forward
        Unreal.Y = -Blender.Y * 100      handedness flip: left -> right
        Unreal.Z =  Blender.Z * 100      up stays up

    Stated once here so it can be checked numerically without Blender.
    """
    x, y, z = (float(c) for c in point_m)
    return (x * CM_PER_UNIT, -y * CM_PER_UNIT, z * CM_PER_UNIT)


# ---------------------------------------------------------------------------
# 2. Collections owned by the pipeline
# ---------------------------------------------------------------------------

COLLECTION_SOURCE = "AF_Source"
COLLECTION_GENERATED = "AF_Generated"
COLLECTION_BODY = "AF_Body"
COLLECTION_WHEELS = "AF_Wheels"
COLLECTION_SUSPENSION = "AF_Suspension"
COLLECTION_COLLISION = "AF_Collision"
COLLECTION_LOD = "AF_LOD"
COLLECTION_RIG = "AF_Rig"
COLLECTION_EXPORT = "AF_Export"

#: Child collections nested under AF_Generated.
GENERATED_CHILDREN = (
    COLLECTION_BODY,
    COLLECTION_WHEELS,
    COLLECTION_SUSPENSION,
    COLLECTION_COLLISION,
    COLLECTION_LOD,
)

#: Full owned set. The pipeline must never delete anything outside this set.
OWNED_COLLECTIONS = (
    COLLECTION_SOURCE,
    COLLECTION_GENERATED,
) + GENERATED_CHILDREN + (
    COLLECTION_RIG,
    COLLECTION_EXPORT,
)

#: Top-level collections cleared before each generation run.
#: AF_Source is deliberately NOT cleared - it may hold hand-authored input.
CLEARABLE_COLLECTIONS = (
    COLLECTION_GENERATED,
    COLLECTION_RIG,
    COLLECTION_EXPORT,
)


# ---------------------------------------------------------------------------
# 3. Bones  (mirrored on the Unreal side by UAFBoneNameMap)
# ---------------------------------------------------------------------------

CORNERS = ("FL", "FR", "RL", "RR")

BONE_ROOT = "AF_Root"
BONE_CHASSIS = "AF_Chassis"
BONE_STEERING = "AF_Steering"

BONE_WHEELS = tuple("AF_Wheel_%s" % c for c in CORNERS)
BONE_SUSPENSIONS = tuple("AF_Suspension_%s" % c for c in CORNERS)

#: The exact, ordered, complete bone list. Eleven bones. No leaf bones.
BONE_ORDER = (
    BONE_ROOT,
    BONE_CHASSIS,
    BONE_STEERING,
    "AF_Suspension_FL",
    "AF_Wheel_FL",
    "AF_Suspension_FR",
    "AF_Wheel_FR",
    "AF_Suspension_RL",
    "AF_Wheel_RL",
    "AF_Suspension_RR",
    "AF_Wheel_RR",
)

#: Parent map. ``None`` means the bone is the armature root.
BONE_PARENTS = {
    BONE_ROOT: None,
    BONE_CHASSIS: BONE_ROOT,
    BONE_STEERING: BONE_CHASSIS,
    "AF_Suspension_FL": BONE_CHASSIS,
    "AF_Suspension_FR": BONE_CHASSIS,
    "AF_Suspension_RL": BONE_CHASSIS,
    "AF_Suspension_RR": BONE_CHASSIS,
    "AF_Wheel_FL": "AF_Suspension_FL",
    "AF_Wheel_FR": "AF_Suspension_FR",
    "AF_Wheel_RL": "AF_Suspension_RL",
    "AF_Wheel_RR": "AF_Suspension_RR",
}

#: Bone axis convention requested of the FBX exporter, set explicitly so bone
#: orientation is reproducible instead of exporter-default.
BONE_PRIMARY_AXIS = "Y"
BONE_SECONDARY_AXIS = "X"

#: Length of each generated bone, in metres. Bones are built along +X so bone
#: direction is deterministic and matches the vehicle forward axis.
BONE_LENGTH_M = 0.20
BONE_ROLL_RAD = 0.0

#: Bones that receive vertex weights. AF_Root and AF_Steering are control
#: bones; they carry no deforming geometry in the placeholder vehicle.
DEFORM_BONES = (BONE_CHASSIS,) + BONE_SUSPENSIONS + BONE_WHEELS


# ---------------------------------------------------------------------------
# 4. Vehicle design dimensions (UludagFormula design values, metres)
# ---------------------------------------------------------------------------
# ORIGINAL UludagFormula design values chosen for this project. NOT quoted from,
# derived from, or claimed to comply with any real motorsport regulation.

VEHICLE_VARIANT = "Proto"

DESIGN = {
    # Longitudinal
    "wheelbase_m": 3.600,
    "overall_length_m": 5.600,
    # Lateral
    "track_front_m": 1.600,
    "track_rear_m": 1.540,
    "overall_width_m": 2.000,
    # Vertical
    "overall_height_m": 0.950,
    "ride_height_m": 0.045,
    "chassis_top_m": 0.560,
    # Wheels
    "wheel_radius_front_m": 0.360,
    "wheel_radius_rear_m": 0.380,
    "wheel_width_front_m": 0.310,
    "wheel_width_rear_m": 0.400,
    "wheel_segments": 24,
    # Bodywork block proportions used by the placeholder generator
    "nose_length_m": 1.150,
    "nose_width_m": 0.300,
    "nose_height_m": 0.180,
    "cockpit_length_m": 1.500,
    "cockpit_width_m": 0.720,
    "cockpit_height_m": 0.560,
    "sidepod_length_m": 1.400,
    "sidepod_width_m": 0.420,
    "sidepod_height_m": 0.400,
    "front_wing_span_m": 1.900,
    "front_wing_chord_m": 0.420,
    "front_wing_thickness_m": 0.060,
    "rear_wing_span_m": 1.000,
    "rear_wing_chord_m": 0.450,
    "rear_wing_thickness_m": 0.070,
    "rear_wing_height_m": 0.820,
    "halo_radius_m": 0.420,
    "halo_thickness_m": 0.050,
    # Steering column visual reference point
    "steering_wheel_x_m": 0.150,
    "steering_wheel_z_m": 0.620,
    # Suspension pickup height above the contact plane
    "suspension_pickup_z_m": 0.320,
}

#: The wheelbase is centred about X = 0: front axle at +wheelbase/2, rear axle
#: at -wheelbase/2. Every other longitudinal position derives from these.
FRONT_AXLE_X_M = DESIGN["wheelbase_m"] * 0.5
REAR_AXLE_X_M = -DESIGN["wheelbase_m"] * 0.5


def corner_sign(corner):
    """Return ``(x_sign, y_sign)`` for a corner code.

    x_sign: +1 front, -1 rear.  y_sign: +1 LEFT (Blender +Y), -1 right.
    """
    if corner not in CORNERS:
        raise ValueError("unknown corner code: %r" % (corner,))
    x_sign = 1.0 if corner[0] == "F" else -1.0
    y_sign = 1.0 if corner[1] == "L" else -1.0
    return x_sign, y_sign


def wheel_radius_m(corner):
    return (DESIGN["wheel_radius_front_m"] if corner[0] == "F"
            else DESIGN["wheel_radius_rear_m"])


def wheel_width_m(corner):
    return (DESIGN["wheel_width_front_m"] if corner[0] == "F"
            else DESIGN["wheel_width_rear_m"])


def track_m(corner):
    return DESIGN["track_front_m"] if corner[0] == "F" else DESIGN["track_rear_m"]


def wheel_centre_m(corner):
    """Design wheel-centre position in Blender metres for a corner code."""
    x_sign, y_sign = corner_sign(corner)
    axle_x = FRONT_AXLE_X_M if x_sign > 0 else REAR_AXLE_X_M
    return (axle_x, y_sign * track_m(corner) * 0.5, wheel_radius_m(corner))


def suspension_pickup_m(corner):
    """Design suspension pickup position (inboard end) in Blender metres."""
    cx, cy, _cz = wheel_centre_m(corner)
    return (cx, cy * 0.25, DESIGN["suspension_pickup_z_m"])


def steering_pivot_m():
    """Design steering-bone origin in Blender metres."""
    return (DESIGN["steering_wheel_x_m"], 0.0, DESIGN["steering_wheel_z_m"])


def chassis_origin_m():
    """Design chassis-bone origin in Blender metres."""
    return (0.0, 0.0, DESIGN["chassis_top_m"] * 0.5)


# ---------------------------------------------------------------------------
# 5. Naming patterns
# ---------------------------------------------------------------------------
# D-079: mesh OBJECT names must never equal BONE names. The FBX node namespace
# is flat; when a wheel mesh was named AF_Wheel_FL (same as its bone), Unreal's
# importer deduplicated by renaming the BONE to AF_Wheel_FL1, silently breaking
# the bone-name contract with UAFBoneNameMap. Hence AF_WheelMesh_{corner}.
# self_check() now enforces bone/object name disjointness.

NAME_BODY = "AF_Body_{variant}"
NAME_WHEEL = "AF_WheelMesh_{corner}"
NAME_SUSPENSION = "AF_Susp_{corner}"
NAME_COLLISION = "UCX_{target}_{index:02d}"
NAME_LOD = "{base}_LOD{level}"
NAME_ARMATURE = "AF_Armature_{variant}"
NAME_MATERIAL = "AF_M_{purpose}"
NAME_EXPORT_FBX = "AF_Vehicle_{variant}.fbx"
NAME_EXPORT_GLB = "AF_Vehicle_{variant}.glb"
NAME_REPORT_JSON = "af_report_{subject}.json"
NAME_REPORT_TEXT = "af_report_{subject}.txt"

UV_MAP_NAME = "AF_UV0"

# Prefixes derived from the templates above so that consumers can *recognise*
# our assets without re-typing a literal. Deriving them here means the prefix
# can never drift away from the name template it belongs to.
MATERIAL_NAME_PREFIX = NAME_MATERIAL.split("{", 1)[0]
COLLISION_NAME_PREFIX = NAME_COLLISION.split("{", 1)[0]

# Modifier names. Blender identifies modifiers by name, so these are asset
# names too and belong in the config with everything else.
MODIFIER_DECIMATE = "AF_Decimate"
MODIFIER_ARMATURE = "AF_Armature"


def body_name(variant=VEHICLE_VARIANT):
    return NAME_BODY.format(variant=variant)


def armature_name(variant=VEHICLE_VARIANT):
    return NAME_ARMATURE.format(variant=variant)


def wheel_name(corner):
    return NAME_WHEEL.format(corner=corner)


def suspension_name(corner):
    return NAME_SUSPENSION.format(corner=corner)


def collision_name(target, index):
    """UCX_<render mesh name>_NN, the convention Unreal's importer looks for."""
    return NAME_COLLISION.format(target=target, index=index)


def lod_name(base, level):
    return NAME_LOD.format(base=base, level=level)


def material_name(purpose):
    return NAME_MATERIAL.format(purpose=purpose)


def export_fbx_name(variant=VEHICLE_VARIANT):
    return NAME_EXPORT_FBX.format(variant=variant)


def export_glb_name(variant=VEHICLE_VARIANT):
    return NAME_EXPORT_GLB.format(variant=variant)


def all_wheel_names():
    return tuple(wheel_name(c) for c in CORNERS)


def all_suspension_names():
    return tuple(suspension_name(c) for c in CORNERS)


# ---------------------------------------------------------------------------
# 6. Materials (placeholder slots only - Unreal owns final shading)
# ---------------------------------------------------------------------------

#: Ordered material slot purposes. Slot ORDER is part of the contract with
#: Unreal; af_validate.py checks it.
MATERIAL_SLOTS_BODY = ("Bodywork", "Detail", "Cockpit")
MATERIAL_SLOTS_WHEEL = ("Tyre", "Rim")
MATERIAL_SLOTS_SUSPENSION = ("Detail",)

#: Placeholder base colours (linear RGBA). Visual aid only; never final art.
MATERIAL_PLACEHOLDER_COLOURS = {
    "Bodywork": (0.055, 0.090, 0.180, 1.0),
    "Detail": (0.500, 0.500, 0.520, 1.0),
    "Cockpit": (0.030, 0.030, 0.035, 1.0),
    "Tyre": (0.018, 0.018, 0.020, 1.0),
    "Rim": (0.700, 0.700, 0.720, 1.0),
}

MATERIAL_ROUGHNESS = {
    "Bodywork": 0.35,
    "Detail": 0.55,
    "Cockpit": 0.80,
    "Tyre": 0.90,
    "Rim": 0.30,
}

MATERIAL_METALLIC = {
    "Bodywork": 0.0,
    "Detail": 0.6,
    "Cockpit": 0.0,
    "Tyre": 0.0,
    "Rim": 1.0,
}


def all_material_purposes():
    seen = []
    for group in (MATERIAL_SLOTS_BODY, MATERIAL_SLOTS_WHEEL, MATERIAL_SLOTS_SUSPENSION):
        for purpose in group:
            if purpose not in seen:
                seen.append(purpose)
    return tuple(seen)


# ---------------------------------------------------------------------------
# 7. Collision and LOD
# ---------------------------------------------------------------------------

#: Convex hull pieces authored for the body. Each entry is
#: (target, index, centre_m, half_extent_m) in Blender space.
COLLISION_PIECES = (
    ("Body", 1, (0.35, 0.00, 0.30), (1.30, 0.45, 0.30)),    # monocoque
    ("Body", 2, (2.10, 0.00, 0.14), (0.60, 0.18, 0.11)),    # nose
    ("Body", 3, (0.10, 0.62, 0.28), (0.70, 0.21, 0.20)),    # sidepod left
    ("Body", 4, (0.10, -0.62, 0.28), (0.70, 0.21, 0.20)),   # sidepod right
    ("Body", 5, (-1.85, 0.00, 0.32), (0.75, 0.35, 0.28)),   # rear structure
)

LOD_LEVELS = (1, 2, 3)
LOD_RATIOS = {1: 0.60, 2: 0.35, 3: 0.18}

#: Triangle budgets per object. Exceeding a budget is a validation failure,
#: not a warning.
FACE_BUDGET = {
    "body": 60000,
    "wheel": 6000,
    "suspension": 2000,
    "collision": 200,
}


# ---------------------------------------------------------------------------
# 8. Validation tolerances
# ---------------------------------------------------------------------------

TOLERANCE = {
    "length_m": 0.010,          # linear dimension tolerance
    "wheel_centre_m": 0.005,    # wheel centre placement tolerance
    "contact_plane_m": 0.002,   # how close min-Z of a wheel must be to Z=0
    "transform_epsilon": 1.0e-5,
    "max_weights_per_vertex": 4,
}

#: Maximum convex-hull pieces Unreal will be asked to accept for one mesh.
MAX_COLLISION_PIECES = 16


# ---------------------------------------------------------------------------
# 9. FBX export settings
# ---------------------------------------------------------------------------
# Expressed as data. af_export.py filters these against the exporter's ACTUAL
# signature at runtime rather than assuming every key exists in Blender 5.2
# LTS. Unknown keys are reported in the export report, never silently dropped.
#
# D-089: apply_scale_options MUST be FBX_SCALE_NONE. History of this setting:
#   * FBX_SCALE_ALL (pre-D-083) baked the m->cm x100 unit factor into the
#     armature OBJECT node transform; UE folded that into the skeleton root,
#     producing reference-pose Scale (100,100,100) (OPEN-080-A).
#   * FBX_SCALE_UNITS (D-083) fixed the root scale but carried the m->cm
#     conversion only in FBX unit METADATA. The legacy UE FBX importer
#     (active per D-084) ignores that metadata unless "Convert Scene Unit"
#     is enabled (default OFF), so every linear dimension imported at 1/100
#     (M5.3 acceptance FAIL: bounds X = 5.60 cm instead of 560).
#   * FBX_SCALE_NONE (D-089) applies the unit conversion directly to the
#     exported vertex/bone DATA: numbers arrive in cm, no node-level x100,
#     no reliance on importer metadata handling. This is the only option
#     that satisfies both constraints at once.

FBX_EXPORT_SETTINGS = {
    "use_selection": True,
    "use_visible": False,
    "object_types": {"ARMATURE", "MESH"},
    "axis_forward": "X",
    "axis_up": "Z",
    "apply_scale_options": "FBX_SCALE_NONE",
    "global_scale": 1.0,
    "apply_unit_scale": True,
    "use_space_transform": True,
    "bake_space_transform": False,
    "use_mesh_modifiers": True,
    "mesh_smooth_type": "FACE",
    "use_tspace": True,
    "use_mesh_edges": False,
    "use_custom_props": False,
    "add_leaf_bones": False,
    "primary_bone_axis": BONE_PRIMARY_AXIS,
    "secondary_bone_axis": BONE_SECONDARY_AXIS,
    "armature_nodetype": "NULL",
    "use_armature_deform_only": False,
    "bake_anim": False,
    "path_mode": "COPY",
    "embed_textures": False,
}

#: GLB is a preview-only convenience path. Disabled by default; never the
#: authoritative export.
GLB_EXPORT_ENABLED = False
GLB_EXPORT_SETTINGS = {
    "export_format": "GLB",
    "export_yup": True,
    "export_apply": True,
    "export_animations": False,
    "export_skins": True,
}


# ---------------------------------------------------------------------------
# 10. Paths (project-relative, never absolute machine paths)
# ---------------------------------------------------------------------------

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
PIPELINE_ROOT = os.path.dirname(SCRIPTS_DIR)
REPO_ROOT = os.path.dirname(PIPELINE_ROOT)

DIR_SOURCE = os.path.join(PIPELINE_ROOT, "source")
DIR_GENERATED = os.path.join(PIPELINE_ROOT, "generated")
DIR_EXPORTS = os.path.join(PIPELINE_ROOT, "exports")
DIR_REPORTS = os.path.join(PIPELINE_ROOT, "reports")
DIR_LOCAL = os.path.join(PIPELINE_ROOT, "local")

MANAGED_DIRS = (DIR_SOURCE, DIR_GENERATED, DIR_EXPORTS, DIR_REPORTS, DIR_LOCAL)


def ensure_dirs():
    """Create the managed directories if absent. Never deletes anything."""
    created = []
    for path in MANAGED_DIRS:
        if not os.path.isdir(path):
            os.makedirs(path, exist_ok=True)
            created.append(path)
    return created


def report_path(subject, extension="json"):
    """Deterministic report path. No timestamp, so reruns overwrite cleanly
    and diffs in Git show what actually changed."""
    pattern = NAME_REPORT_JSON if extension == "json" else NAME_REPORT_TEXT
    return os.path.join(DIR_REPORTS, pattern.format(subject=subject))


def export_fbx_path(variant=VEHICLE_VARIANT):
    return os.path.join(DIR_EXPORTS, export_fbx_name(variant))


def export_glb_path(variant=VEHICLE_VARIANT):
    return os.path.join(DIR_EXPORTS, export_glb_name(variant))


# ---------------------------------------------------------------------------
# 11. Effective-config hash (recorded in every report)
# ---------------------------------------------------------------------------

def effective_config():
    """Return the JSON-serialisable subset of config that affects output."""
    return {
        "pipeline_version": PIPELINE_VERSION,
        "target_blender_version": list(TARGET_BLENDER_VERSION),
        "target_unreal_version": TARGET_UNREAL_VERSION,
        "units": {
            "blender_unit_system": BLENDER_UNIT_SYSTEM,
            "blender_length_unit": BLENDER_LENGTH_UNIT,
            "blender_scale_length": BLENDER_SCALE_LENGTH,
            "cm_per_unit": CM_PER_UNIT,
            "blender_forward": BLENDER_FORWARD_AXIS,
            "blender_left": BLENDER_LEFT_AXIS,
            "blender_up": BLENDER_UP_AXIS,
            "unreal_forward": UNREAL_FORWARD_AXIS,
            "unreal_right": UNREAL_RIGHT_AXIS,
            "unreal_up": UNREAL_UP_AXIS,
            "blender_handedness": BLENDER_HANDEDNESS,
            "unreal_handedness": UNREAL_HANDEDNESS,
        },
        "bones": {
            "order": list(BONE_ORDER),
            "parents": dict(BONE_PARENTS),
            "deform": list(DEFORM_BONES),
            "primary_axis": BONE_PRIMARY_AXIS,
            "secondary_axis": BONE_SECONDARY_AXIS,
            "length_m": BONE_LENGTH_M,
            "roll_rad": BONE_ROLL_RAD,
        },
        "design": dict(DESIGN),
        "variant": VEHICLE_VARIANT,
        "collections": list(OWNED_COLLECTIONS),
        # D-079: naming templates are part of the output contract (node names
        # inside the FBX), so they participate in the config hash.
        "naming": {
            "body": NAME_BODY,
            "wheel": NAME_WHEEL,
            "suspension": NAME_SUSPENSION,
            "collision": NAME_COLLISION,
            "lod": NAME_LOD,
            "armature": NAME_ARMATURE,
            "material": NAME_MATERIAL,
            "uv_map": UV_MAP_NAME,
        },
        "materials": {
            "body": list(MATERIAL_SLOTS_BODY),
            "wheel": list(MATERIAL_SLOTS_WHEEL),
            "suspension": list(MATERIAL_SLOTS_SUSPENSION),
        },
        "collision_pieces": [
            {"target": t, "index": i, "centre_m": list(c), "half_extent_m": list(h)}
            for (t, i, c, h) in COLLISION_PIECES
        ],
        "lod_ratios": {str(k): v for k, v in LOD_RATIOS.items()},
        "face_budget": dict(FACE_BUDGET),
        "tolerance": dict(TOLERANCE),
        "fbx": {k: (sorted(v) if isinstance(v, set) else v)
                for k, v in FBX_EXPORT_SETTINGS.items()},
        "glb_enabled": GLB_EXPORT_ENABLED,
    }


def config_hash():
    """Stable SHA-256 of the effective configuration."""
    blob = json.dumps(effective_config(), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# 12. Self-consistency check (runs without Blender)
# ---------------------------------------------------------------------------

def self_check():
    """Validate the configuration's internal consistency.

    Returns ``(ok, problems)``. This is a pure-Python check: it proves the
    config is self-consistent. It does NOT prove Blender accepts it.
    """
    problems = []

    # --- bones -------------------------------------------------------------
    if len(BONE_ORDER) != 11:
        problems.append("BONE_ORDER must contain exactly 11 bones, found %d" % len(BONE_ORDER))
    if len(set(BONE_ORDER)) != len(BONE_ORDER):
        problems.append("BONE_ORDER contains duplicates")
    if set(BONE_ORDER) != set(BONE_PARENTS):
        problems.append("BONE_ORDER and BONE_PARENTS disagree")

    roots = [b for b, p in BONE_PARENTS.items() if p is None]
    if roots != [BONE_ROOT]:
        problems.append("expected exactly one root bone (%s), found %r" % (BONE_ROOT, roots))

    for bone, parent in BONE_PARENTS.items():
        if parent is None:
            continue
        if parent not in BONE_PARENTS:
            problems.append("bone %s has unknown parent %s" % (bone, parent))
        elif BONE_ORDER.index(parent) > BONE_ORDER.index(bone):
            problems.append("bone %s appears before its parent %s" % (bone, parent))

    for corner in CORNERS:
        wheel = "AF_Wheel_%s" % corner
        susp = "AF_Suspension_%s" % corner
        if BONE_PARENTS.get(wheel) != susp:
            problems.append("%s must be parented to %s" % (wheel, susp))
        if BONE_PARENTS.get(susp) != BONE_CHASSIS:
            problems.append("%s must be parented to %s" % (susp, BONE_CHASSIS))

    for bone in DEFORM_BONES:
        if bone not in BONE_PARENTS:
            problems.append("deform bone %s is not in the bone list" % bone)

    # --- bone vs object name collisions (D-079) -----------------------------
    # The FBX node namespace is flat. If a scene OBJECT shares a name with a
    # BONE, importers (Unreal Interchange included) deduplicate by renaming
    # one of them - observed as bone AF_Wheel_FL becoming AF_Wheel_FL1 in
    # Unreal, which silently breaks the UAFBoneNameMap contract.
    object_names = {body_name(), armature_name()}
    object_names.update(all_wheel_names())
    object_names.update(all_suspension_names())
    object_names.update(lod_name(body_name(), lvl) for lvl in LOD_LEVELS)
    object_names.update(collision_name(t, i) for (t, i, _c, _h) in COLLISION_PIECES)
    name_collisions = sorted(object_names & set(BONE_ORDER))
    if name_collisions:
        problems.append(
            "object names collide with bone names; FBX importers will rename "
            "bones on import: %s" % ", ".join(name_collisions))

    # --- prohibited tokens -------------------------------------------------
    names = list(BONE_ORDER) + list(OWNED_COLLECTIONS) + [
        body_name(), armature_name(), UV_MAP_NAME,
        export_fbx_name(), export_glb_name(),
    ]
    names += list(all_wheel_names())
    names += list(all_suspension_names())
    names += [material_name(p) for p in all_material_purposes()]
    names += [collision_name(t, i) for (t, i, _c, _h) in COLLISION_PIECES]
    for name in names:
        for token in PROHIBITED_NAME_TOKENS:
            if token in name:
                problems.append("prohibited token %r found in name %r" % (token, name))

    # --- geometry sanity ---------------------------------------------------
    if DESIGN["wheelbase_m"] >= DESIGN["overall_length_m"]:
        problems.append("wheelbase must be shorter than overall length")
    if DESIGN["track_front_m"] > DESIGN["overall_width_m"]:
        problems.append("front track must not exceed overall width")
    if DESIGN["track_rear_m"] > DESIGN["overall_width_m"]:
        problems.append("rear track must not exceed overall width")
    if DESIGN["front_wing_span_m"] > DESIGN["overall_width_m"]:
        problems.append("front wing span must not exceed overall width")
    if DESIGN["ride_height_m"] <= 0.0:
        problems.append("ride height must be positive")
    if DESIGN["chassis_top_m"] >= DESIGN["overall_height_m"]:
        problems.append("chassis top must be below overall height")
    if DESIGN["rear_wing_height_m"] > DESIGN["overall_height_m"]:
        problems.append("rear wing height must not exceed overall height")

    for corner in CORNERS:
        cx, cy, cz = wheel_centre_m(corner)
        radius = wheel_radius_m(corner)
        if abs(cz - radius) > 1.0e-9:
            problems.append(
                "wheel %s centre Z (%.4f) must equal its radius (%.4f) so the tyre "
                "touches Z=0" % (corner, cz, radius))
        if abs(abs(cx) - DESIGN["wheelbase_m"] / 2.0) > 1.0e-9:
            problems.append("wheel %s X position does not match half the wheelbase" % corner)
        if abs(abs(cy) * 2.0 - track_m(corner)) > 1.0e-9:
            problems.append("wheel %s Y position does not match the track width" % corner)
        half_width = wheel_width_m(corner) / 2.0
        if abs(cy) + half_width > DESIGN["overall_width_m"] / 2.0 + TOLERANCE["length_m"]:
            problems.append("wheel %s extends beyond the overall width" % corner)

    # Left and right corners must mirror exactly.
    for front_or_rear in ("F", "R"):
        left = wheel_centre_m(front_or_rear + "L")
        right = wheel_centre_m(front_or_rear + "R")
        if abs(left[0] - right[0]) > 1.0e-12 or abs(left[1] + right[1]) > 1.0e-12 \
                or abs(left[2] - right[2]) > 1.0e-12:
            problems.append("%s wheels are not mirrored about Y=0" % front_or_rear)

    # --- unit conversion ---------------------------------------------------
    if blender_point_to_unreal_cm((1.0, 2.0, 3.0)) != (100.0, -200.0, 300.0):
        problems.append("blender_point_to_unreal_cm does not implement the documented mapping")
    if metres_to_cm(1.0) != 100.0:
        problems.append("metres_to_cm does not implement CM_PER_UNIT")

    # --- LOD ---------------------------------------------------------------
    previous = 1.0
    for level in LOD_LEVELS:
        if level not in LOD_RATIOS:
            problems.append("LOD level %d has no ratio" % level)
            continue
        ratio = LOD_RATIOS[level]
        if not (0.0 < ratio < previous):
            problems.append("LOD%d ratio %.3f is not strictly between 0 and the "
                            "previous ratio %.3f" % (level, ratio, previous))
        previous = ratio

    # --- collision ---------------------------------------------------------
    if len(COLLISION_PIECES) > MAX_COLLISION_PIECES:
        problems.append("too many collision pieces (%d > %d)"
                        % (len(COLLISION_PIECES), MAX_COLLISION_PIECES))
    seen_indices = set()
    half_len = DESIGN["overall_length_m"] / 2.0
    half_wid = DESIGN["overall_width_m"] / 2.0
    for target, index, centre, half in COLLISION_PIECES:
        key = (target, index)
        if key in seen_indices:
            problems.append("duplicate collision piece %s_%02d" % (target, index))
        seen_indices.add(key)
        if abs(centre[0]) + half[0] > half_len + TOLERANCE["length_m"]:
            problems.append("collision piece %s_%02d exceeds the overall length" % (target, index))
        if abs(centre[1]) + half[1] > half_wid + TOLERANCE["length_m"]:
            problems.append("collision piece %s_%02d exceeds the overall width" % (target, index))
        if centre[2] - half[2] < -TOLERANCE["length_m"]:
            problems.append("collision piece %s_%02d dips below the contact plane"
                            % (target, index))
        if centre[2] + half[2] > DESIGN["overall_height_m"] + TOLERANCE["length_m"]:
            problems.append("collision piece %s_%02d exceeds the overall height" % (target, index))

    # --- collections -------------------------------------------------------
    for name in CLEARABLE_COLLECTIONS:
        if name not in OWNED_COLLECTIONS:
            problems.append("clearable collection %s is not in the owned set" % name)
    if COLLECTION_SOURCE in CLEARABLE_COLLECTIONS:
        problems.append("AF_Source must never be cleared automatically")

    # --- materials ---------------------------------------------------------
    for purpose in all_material_purposes():
        if purpose not in MATERIAL_PLACEHOLDER_COLOURS:
            problems.append("material purpose %s has no placeholder colour" % purpose)
        if purpose not in MATERIAL_ROUGHNESS:
            problems.append("material purpose %s has no roughness value" % purpose)
        if purpose not in MATERIAL_METALLIC:
            problems.append("material purpose %s has no metallic value" % purpose)

    # --- export settings ---------------------------------------------------
    if FBX_EXPORT_SETTINGS.get("add_leaf_bones") is not False:
        problems.append("add_leaf_bones must be False so the exported bone list matches "
                        "BONE_ORDER exactly")
    if FBX_EXPORT_SETTINGS.get("bake_space_transform") is not False:
        problems.append("bake_space_transform must be False")
    if FBX_EXPORT_SETTINGS.get("global_scale") != 1.0:
        problems.append("global_scale must stay 1.0; unit conversion is carried by "
                        "apply_scale_options, not by scene scale")
    if FBX_EXPORT_SETTINGS.get("apply_scale_options") != "FBX_SCALE_NONE":
        problems.append("apply_scale_options must be FBX_SCALE_NONE (D-089): "
                        "FBX_SCALE_ALL bakes x100 into the armature node "
                        "(root-bone scale 100,100,100, OPEN-080-A) and "
                        "FBX_SCALE_UNITS relies on unit metadata the legacy "
                        "UE importer ignores (100x shrink, M5.3 FAIL)")
    if FBX_EXPORT_SETTINGS.get("primary_bone_axis") != BONE_PRIMARY_AXIS:
        problems.append("FBX primary_bone_axis disagrees with BONE_PRIMARY_AXIS")
    if FBX_EXPORT_SETTINGS.get("secondary_bone_axis") != BONE_SECONDARY_AXIS:
        problems.append("FBX secondary_bone_axis disagrees with BONE_SECONDARY_AXIS")

    return (not problems), problems


def describe():
    """Human-readable summary printed by every script at start-up."""
    lines = [
        "%s pipeline config v%s" % (PROJECT_NAME, PIPELINE_VERSION),
        "  target Blender  : %d.%d LTS" % TARGET_BLENDER_VERSION,
        "  target Unreal   : %s" % TARGET_UNREAL_VERSION,
        "  Blender units   : 1 unit = 1 m, %s forward / %s left / %s up"
        % (BLENDER_FORWARD_AXIS, BLENDER_LEFT_AXIS, BLENDER_UP_AXIS),
        "  Unreal units    : 1 uu = 1 cm, %s forward / %s right / %s up"
        % (UNREAL_FORWARD_AXIS, UNREAL_RIGHT_AXIS, UNREAL_UP_AXIS),
        "  handedness      : Blender %s -> Unreal %s (Y sign flip only)"
        % (BLENDER_HANDEDNESS, UNREAL_HANDEDNESS),
        "  scale to Unreal : x%.1f" % CM_PER_UNIT,
        "  bones           : %d" % len(BONE_ORDER),
        "  variant         : %s" % VEHICLE_VARIANT,
        "  config hash     : %s" % config_hash()[:16],
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    import sys

    print(describe())
    ok, issues = self_check()
    if ok:
        print("")
        print("config self-check: PASS (%d bones, %d owned collections, %d collision pieces)"
              % (len(BONE_ORDER), len(OWNED_COLLECTIONS), len(COLLISION_PIECES)))
        sys.exit(0)
    print("")
    print("config self-check: FAIL (%d problems)" % len(issues))
    for issue in issues:
        print("  - %s" % issue)
    sys.exit(1)
