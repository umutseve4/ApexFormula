"""ApexFormula - placeholder material slot assignment.

Milestone 0B.

Blender is NOT the shading authority for this project (decision D-011). Unreal
owns final materials. What Blender must get right is the *contract*: the number
of material slots, their order, and their names, so that Unreal binds the right
material to the right part of the mesh on import.

This script therefore creates flat, unlit-looking placeholder materials named
``AF_M_<Purpose>`` and assigns them to slots in the declared order. It does not
attempt to author a look.

Slot contract, from af_pipeline_config:
  * body        -> MATERIAL_SLOTS_BODY
  * wheels      -> MATERIAL_SLOTS_WHEEL
  * suspension  -> MATERIAL_SLOTS_SUSPENSION
  * collision   -> no slots (UCX hulls are not rendered)

Honesty note: this script has NOT been executed inside Blender. Every claim
about material creation and slot assignment is "requires Blender execution".
Only syntax and structure have been statically inspected.

Usage
-----
    blender --background --python af_materials.py

Exit codes: 0 success, 2 Blender API unavailable, 3 assignment failed.
"""

from __future__ import annotations

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
# Slot plan - pure, no bpy
# ---------------------------------------------------------------------------

def slot_plan():
    """Return ``{mesh object name: (slot purposes, ...)}`` in slot order."""
    plan = {cfg.body_name(): tuple(cfg.MATERIAL_SLOTS_BODY)}
    for corner in cfg.CORNERS:
        plan[cfg.wheel_name(corner)] = tuple(cfg.MATERIAL_SLOTS_WHEEL)
        plan[cfg.suspension_name(corner)] = tuple(cfg.MATERIAL_SLOTS_SUSPENSION)
    for level in cfg.LOD_LEVELS:
        plan[cfg.lod_name(cfg.body_name(), level)] = tuple(cfg.MATERIAL_SLOTS_BODY)
    return plan


# ---------------------------------------------------------------------------
# Blender-side construction
# ---------------------------------------------------------------------------

def get_or_create_material(purpose):
    """Return the placeholder material for ``purpose``, creating it if needed."""
    name = cfg.material_name(purpose)
    material = bpy.data.materials.get(name)
    if material is None:
        material = bpy.data.materials.new(name=name)

    material.use_nodes = True
    colour = cfg.MATERIAL_PLACEHOLDER_COLOURS[purpose]
    material.diffuse_color = colour  # viewport colour

    principled = None
    for node in material.node_tree.nodes:
        if node.type == "BSDF_PRINCIPLED":
            principled = node
            break

    if principled is not None:
        principled.inputs["Base Color"].default_value = colour
        # Input names shifted between Blender releases; set defensively.
        for input_name, value in (
            ("Roughness", cfg.MATERIAL_ROUGHNESS[purpose]),
            ("Metallic", cfg.MATERIAL_METALLIC[purpose]),
        ):
            if input_name in principled.inputs:
                principled.inputs[input_name].default_value = value

    return material


def assign_slots(obj, purposes):
    """Replace ``obj``'s material slots with exactly ``purposes``, in order."""
    mesh = obj.data
    mesh.materials.clear()
    for purpose in purposes:
        mesh.materials.append(get_or_create_material(purpose))

    # Every polygon uses slot 0 by default. For wheels, push the tread band to
    # Tyre (slot 0) and leave the cap fans on Rim (slot 1) when a Rim slot
    # exists, so the two-slot contract is actually exercised.
    if len(purposes) >= 2 and "Rim" in purposes:
        rim_index = purposes.index("Rim")
        segments = cfg.DESIGN["wheel_segments"]
        for index, polygon in enumerate(mesh.polygons):
            polygon.material_index = 0 if index < segments else rim_index

    return [m.name for m in mesh.materials]


def apply_all():
    applied = {}
    missing = []
    for mesh_name, purposes in sorted(slot_plan().items()):
        obj = bpy.data.objects.get(mesh_name)
        if obj is None:
            missing.append(mesh_name)
            continue
        applied[mesh_name] = assign_slots(obj, purposes)

    return {
        "applied": applied,
        "missing_objects": missing,
        "materials_in_file": sorted(
            m.name for m in bpy.data.materials
            if m.name.startswith(cfg.MATERIAL_NAME_PREFIX)),
        "config_hash": cfg.config_hash(),
    }


def print_summary(summary):
    print("")
    print("af_materials summary")
    for mesh_name, slots in sorted(summary["applied"].items()):
        print("  %-24s slots: %s" % (mesh_name, ", ".join(slots)))
    if summary["missing_objects"]:
        print("  MISSING objects: %s" % ", ".join(summary["missing_objects"]))
    print("  materials in file: %s" % ", ".join(summary["materials_in_file"]))
    print("  config hash      : %s" % summary["config_hash"][:16])
    print("")
    print("  Note: these are placeholder materials only. Final shading is")
    print("  authored in Unreal (decision D-011).")


def main():
    print(cfg.describe())

    ok, problems = cfg.self_check()
    if not ok:
        print("")
        print("config self-check FAILED - refusing to assign materials:")
        for problem in problems:
            print("  - %s" % problem)
        return EXIT_FAILED

    if bpy is None:
        print("")
        print("bpy is unavailable: this script must be run inside Blender, e.g.")
        print("  blender --background --python af_materials.py")
        return EXIT_NO_BPY

    try:
        summary = apply_all()
    except Exception as exc:  # noqa: BLE001
        print("")
        print("af_materials FAILED: %s: %s" % (type(exc).__name__, exc))
        return EXIT_FAILED

    print_summary(summary)

    if summary["missing_objects"]:
        print("")
        print("af_materials FAILED: expected objects were not present")
        return EXIT_FAILED

    print("")
    print("af_materials: OK")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
