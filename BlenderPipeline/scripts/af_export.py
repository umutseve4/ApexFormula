"""ApexFormula - FBX (and optional GLB) export.

Milestone 0B.

The export settings live in ``af_pipeline_config.FBX_EXPORT_SETTINGS`` as plain
data. This script does NOT assume every key exists in the installed Blender's
exporter. Blender's FBX exporter signature has changed across releases, and the
target here is Blender 5.2 LTS, so each key is filtered against the operator's
actual runtime properties. Keys the exporter does not recognise are reported as
DROPPED in the export report rather than silently ignored or blindly passed
(which would raise).

That filtering is the honest way to handle an option list that has been
designed but not yet verified against a running Blender.

Honesty note: this script has NOT been executed inside Blender, and no FBX has
been produced. Every export claim is "requires Blender execution"; correct
import into Unreal is additionally "requires Unreal Editor verification".

Usage
-----
    blender --background --python af_export.py

Exit codes: 0 success, 2 Blender API unavailable, 3 export failed.
"""

from __future__ import annotations

import datetime
import json
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

REPORT_SUBJECT = "export"


# ---------------------------------------------------------------------------
# Option filtering
# ---------------------------------------------------------------------------

def operator_property_names(operator):
    """Return the set of keyword names an operator actually accepts."""
    names = set()
    rna = getattr(operator, "get_rna_type", None)
    if rna is not None:
        try:
            for prop in operator.get_rna_type().properties:
                if prop.identifier != "rna_type":
                    names.add(prop.identifier)
        except Exception:  # noqa: BLE001 - fall through to the empty set
            pass
    return names


def filter_settings(settings, accepted):
    """Split ``settings`` into (accepted kwargs, dropped keys).

    If the accepted set could not be determined, everything is passed through
    and that fact is reported, so a failure is loud rather than mysterious.
    """
    if not accepted:
        return dict(settings), [], True
    kept = {k: v for k, v in settings.items() if k in accepted}
    dropped = sorted(k for k in settings if k not in accepted)
    return kept, dropped, False


# ---------------------------------------------------------------------------
# Selection
# ---------------------------------------------------------------------------

def export_object_names():
    """Names of everything that should be selected for export, in order."""
    names = [cfg.armature_name(), cfg.body_name()]
    names.extend(cfg.all_wheel_names())
    names.extend(cfg.all_suspension_names())
    names.extend(cfg.lod_name(cfg.body_name(), level) for level in cfg.LOD_LEVELS)
    names.extend(cfg.collision_name(cfg.body_name(), index)
                 for _t, index, _c, _h in cfg.COLLISION_PIECES)
    return names


def select_for_export():
    """Deselect everything, then select exactly the export set."""
    bpy.ops.object.select_all(action="DESELECT")

    selected = []
    missing = []
    for name in export_object_names():
        obj = bpy.data.objects.get(name)
        if obj is None:
            missing.append(name)
            continue
        obj.hide_set(False)
        obj.hide_viewport = False
        obj.select_set(True)
        selected.append(name)

    arm = bpy.data.objects.get(cfg.armature_name())
    if arm is not None:
        bpy.context.view_layer.objects.active = arm

    return selected, missing


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------

def export_fbx():
    cfg.ensure_dirs()
    path = cfg.export_fbx_path()

    accepted = operator_property_names(bpy.ops.export_scene.fbx)
    kwargs, dropped, unfiltered = filter_settings(cfg.FBX_EXPORT_SETTINGS, accepted)
    kwargs["filepath"] = path

    result = bpy.ops.export_scene.fbx(**kwargs)

    info = {
        "format": "FBX",
        "path": os.path.relpath(path, cfg.REPO_ROOT),
        "operator_result": list(result) if result else [],
        "settings_requested": sorted(cfg.FBX_EXPORT_SETTINGS),
        "settings_applied": sorted(k for k in kwargs if k != "filepath"),
        "settings_dropped_unknown_to_exporter": dropped,
        "settings_unfiltered_fallback": unfiltered,
        "exists": os.path.isfile(path),
        "size_bytes": os.path.getsize(path) if os.path.isfile(path) else 0,
    }
    return info


def export_glb():
    if not cfg.GLB_EXPORT_ENABLED:
        return {"format": "GLB", "skipped": True,
                "reason": "GLB_EXPORT_ENABLED is False; GLB is preview-only "
                          "and never the authoritative export (decision D-016)"}

    cfg.ensure_dirs()
    path = cfg.export_glb_path()

    accepted = operator_property_names(bpy.ops.export_scene.gltf)
    kwargs, dropped, unfiltered = filter_settings(cfg.GLB_EXPORT_SETTINGS, accepted)
    kwargs["filepath"] = path
    if "use_selection" in accepted:
        kwargs["use_selection"] = True

    result = bpy.ops.export_scene.gltf(**kwargs)

    return {
        "format": "GLB",
        "skipped": False,
        "path": os.path.relpath(path, cfg.REPO_ROOT),
        "operator_result": list(result) if result else [],
        "settings_dropped_unknown_to_exporter": dropped,
        "settings_unfiltered_fallback": unfiltered,
        "exists": os.path.isfile(path),
        "size_bytes": os.path.getsize(path) if os.path.isfile(path) else 0,
    }


def _bake_targets():
    """Objects plus their UNIQUE mesh/armature datablocks for the cm bake.

    Datablocks are deduplicated by name so shared meshes are transformed once.
    """
    objects = []
    meshes = {}
    armatures = {}
    for name in export_object_names():
        obj = bpy.data.objects.get(name)
        if obj is None:
            continue
        objects.append(obj)
        if obj.type == "MESH":
            meshes[obj.data.name] = obj.data
        elif obj.type == "ARMATURE":
            armatures[obj.data.name] = obj.data
    return objects, list(meshes.values()), list(armatures.values())


def _apply_scale_factor(factor):
    """Scale object locations and mesh/armature data by ``factor``.

    Object-level ``scale`` stays (1,1,1) on purpose: baking into DATA keeps
    node transforms clean, which is the whole point (root must import at
    scale (1,1,1), see D-090). ``matrix_parent_inverse`` translation must be
    scaled too, or parented objects (wheels under the armature) would drift.
    """
    import mathutils

    matrix = mathutils.Matrix.Scale(factor, 4)
    objects, meshes, armatures = _bake_targets()

    for obj in objects:
        obj.location = [c * factor for c in obj.location]
        mpi = obj.matrix_parent_inverse.copy()
        mpi.translation = mpi.translation * factor
        obj.matrix_parent_inverse = mpi

    for mesh in meshes:
        mesh.transform(matrix)

    for arm in armatures:
        arm.transform(matrix)

    scene = bpy.context.scene
    scene.unit_settings.scale_length = scene.unit_settings.scale_length / factor
    bpy.context.view_layer.update()


def bake_cm():
    """Bake the m->cm factor into scene data just before export (D-090).

    After this, vertex/bone numbers are in cm and scale_length is 0.01, so the
    exporter's effective unit factor is 100 * 0.01 = 1.0: no unit conversion is
    left for the FBX file to carry, and no x100 can leak into the root bone.
    """
    _apply_scale_factor(cfg.CM_PER_UNIT)


def unbake_cm():
    """Exact inverse of :func:`bake_cm`; restores the metre-based scene."""
    _apply_scale_factor(1.0 / cfg.CM_PER_UNIT)
    # Guard against float drift on the one value other scripts assert on.
    bpy.context.scene.unit_settings.scale_length = cfg.BLENDER_SCALE_LENGTH


def export_all():
    selected, missing = select_for_export()
    if missing:
        raise RuntimeError(
            "cannot export, missing object(s): %s" % ", ".join(missing))

    bake_cm()
    try:
        fbx_info = export_fbx()
        glb_info = export_glb()
    finally:
        unbake_cm()

    return {
        "project": cfg.PROJECT_NAME,
        "script": os.path.basename(__file__),
        "pipeline_version": cfg.PIPELINE_VERSION,
        "config_hash": cfg.config_hash(),
        "generated_utc": datetime.datetime.now(datetime.timezone.utc)
                                  .strftime("%Y-%m-%dT%H:%M:%SZ"),
        "blender_runtime": list(bpy.app.version),
        "selected_objects": selected,
        "selected_count": len(selected),
        "exported_bone_list": [b.name for b in bpy.data.objects[
            cfg.armature_name()].data.bones],
        "expected_bone_list": list(cfg.BONE_ORDER),
        "add_leaf_bones": cfg.FBX_EXPORT_SETTINGS["add_leaf_bones"],
        "fbx": fbx_info,
        "glb": glb_info,
    }


def write_report(info):
    cfg.ensure_dirs()
    json_path = cfg.report_path(REPORT_SUBJECT, "json")
    text_path = cfg.report_path(REPORT_SUBJECT, "txt")

    with open(json_path, "w", encoding="utf-8") as handle:
        json.dump(info, handle, indent=2, sort_keys=True, default=str)
        handle.write("\n")

    lines = ["ApexFormula export report", "=" * 60]
    lines.append("pipeline version : %s" % info["pipeline_version"])
    lines.append("config hash      : %s" % info["config_hash"])
    lines.append("generated (UTC)  : %s" % info["generated_utc"])
    lines.append("Blender runtime  : %s" % (info["blender_runtime"],))
    lines.append("")
    lines.append("selected objects (%d):" % info["selected_count"])
    for name in info["selected_objects"]:
        lines.append("  %s" % name)
    lines.append("")
    lines.append("exported bone list (%d), add_leaf_bones=%s:"
                 % (len(info["exported_bone_list"]), info["add_leaf_bones"]))
    for bone in info["exported_bone_list"]:
        lines.append("  %s" % bone)
    lines.append("")
    for key in ("fbx", "glb"):
        lines.append("%s: %s" % (key.upper(),
                                 json.dumps(info[key], sort_keys=True, indent=2)))
    lines.append("")
    with open(text_path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))

    return json_path, text_path


def print_summary(info, json_path, text_path):
    print("")
    print("af_export summary")
    print("  selected objects : %d" % info["selected_count"])
    print("  bones exported   : %d (expected %d, add_leaf_bones=%s)" % (
        len(info["exported_bone_list"]), len(info["expected_bone_list"]),
        info["add_leaf_bones"]))
    fbx = info["fbx"]
    print("  FBX path         : %s" % fbx["path"])
    print("  FBX exists       : %s (%d bytes)" % (fbx["exists"], fbx["size_bytes"]))
    if fbx["settings_dropped_unknown_to_exporter"]:
        print("  DROPPED settings : %s"
              % ", ".join(fbx["settings_dropped_unknown_to_exporter"]))
        print("    (these keys are not present in this Blender's FBX exporter;")
        print("     they were designed but never verified against a running")
        print("     Blender 5.2 LTS - see VERSION_MATRIX.md)")
    else:
        print("  DROPPED settings : none")
    if fbx["settings_unfiltered_fallback"]:
        print("  WARNING: exporter properties could not be introspected;")
        print("           settings were passed through unfiltered.")
    glb = info["glb"]
    print("  GLB              : %s" % ("skipped - %s" % glb.get("reason")
                                       if glb.get("skipped") else glb.get("path")))
    print("  report (json)    : %s" % json_path)
    print("  report (text)    : %s" % text_path)


def main():
    print(cfg.describe())

    ok, problems = cfg.self_check()
    if not ok:
        print("")
        print("config self-check FAILED - refusing to export:")
        for problem in problems:
            print("  - %s" % problem)
        return EXIT_FAILED

    if bpy is None:
        print("")
        print("bpy is unavailable: this script must be run inside Blender, e.g.")
        print("  blender --background --python af_export.py")
        return EXIT_NO_BPY

    try:
        info = export_all()
        json_path, text_path = write_report(info)
    except Exception as exc:  # noqa: BLE001
        print("")
        print("af_export FAILED: %s: %s" % (type(exc).__name__, exc))
        return EXIT_FAILED

    print_summary(info, json_path, text_path)

    if not info["fbx"]["exists"] or info["fbx"]["size_bytes"] <= 0:
        print("")
        print("af_export FAILED: no FBX file was written")
        return EXIT_FAILED

    if len(info["exported_bone_list"]) != len(info["expected_bone_list"]):
        print("")
        print("af_export FAILED: bone count mismatch before export")
        return EXIT_FAILED

    print("")
    print("af_export: OK")
    print("  Note: a written FBX is not a verified FBX. Import correctness in")
    print("  Unreal is 'requires Unreal Editor verification'.")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
