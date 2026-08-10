"""ApexFormula - armature construction and skin binding.

Milestone 0B.

Builds AF_Armature_Proto with exactly the eleven bones declared in
``af_pipeline_config.BONE_ORDER``, in that order, with the parenting declared
in ``BONE_PARENTS``, and binds the generated meshes to it.

Binding strategy (deliberately rigid, not smooth):
  * Each wheel mesh is weighted 1.0 to its own wheel bone.
  * Each suspension mesh is weighted 1.0 to its own suspension bone.
  * The body mesh is weighted 1.0 to AF_Chassis.
This gives exactly one weight per vertex, which trivially satisfies the
four-weights-per-vertex budget and makes the export verifiable by inspection
rather than by eyeball.

No leaf bones are created here, and ``add_leaf_bones`` is False in the export
settings, so the exported skeleton must contain eleven bones and no more.

Honesty note: this script has NOT been executed inside Blender. All rig claims
are "requires Blender execution". Only syntax and structure have been
statically inspected.

Usage
-----
    blender --background --python af_vehicle_rig.py

Exit codes: 0 success, 2 Blender API unavailable, 3 rigging failed.
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
# Bone head positions - pure, no bpy
# ---------------------------------------------------------------------------

def bone_head_m(bone_name):
    """Return the design head position of a bone, in Blender metres."""
    if bone_name == cfg.BONE_ROOT:
        return (0.0, 0.0, 0.0)
    if bone_name == cfg.BONE_CHASSIS:
        return cfg.chassis_origin_m()
    if bone_name == cfg.BONE_STEERING:
        return cfg.steering_pivot_m()
    for index, corner in enumerate(cfg.CORNERS):
        # Bone names come from the config, never from a literal built here.
        if bone_name == cfg.BONE_SUSPENSIONS[index]:
            return cfg.suspension_pickup_m(corner)
        if bone_name == cfg.BONE_WHEELS[index]:
            return cfg.wheel_centre_m(corner)
    raise KeyError("no head position defined for bone %r" % (bone_name,))


def bone_tail_m(bone_name):
    """Return the design tail position of a bone, in Blender metres.

    Bones extend along +X (vehicle forward) by BONE_LENGTH_M so that bone
    direction is deterministic and never zero length.
    """
    head = bone_head_m(bone_name)
    return (head[0] + cfg.BONE_LENGTH_M, head[1], head[2])


def bone_layout():
    """Return ``[(name, parent, head, tail), ...]`` in BONE_ORDER order."""
    layout = []
    for name in cfg.BONE_ORDER:
        layout.append((
            name,
            cfg.BONE_PARENTS[name],
            bone_head_m(name),
            bone_tail_m(name),
        ))
    return layout


def binding_plan():
    """Return ``{mesh object name: bone name}`` for rigid binding."""
    plan = {cfg.body_name(): cfg.BONE_CHASSIS}
    for index, corner in enumerate(cfg.CORNERS):
        # Note the deliberate naming asymmetry documented in the config: the
        # suspension *mesh* is AF_Susp_<corner> while its *bone* is
        # AF_Suspension_<corner>. Both come from the config, never from a
        # literal built here.
        plan[cfg.wheel_name(corner)] = cfg.BONE_WHEELS[index]
        plan[cfg.suspension_name(corner)] = cfg.BONE_SUSPENSIONS[index]
    return plan


# ---------------------------------------------------------------------------
# Blender-side construction
# ---------------------------------------------------------------------------

def _collection(name):
    coll = bpy.data.collections.get(name)
    if coll is None:
        raise RuntimeError(
            "collection %r is missing - run af_scene_setup.py first" % (name,))
    return coll


def create_armature():
    """Create the armature object with all eleven bones."""
    name = cfg.armature_name()

    existing = bpy.data.objects.get(name)
    if existing is not None:
        bpy.data.objects.remove(existing, do_unlink=True)

    arm_data = bpy.data.armatures.new(name)
    arm_obj = bpy.data.objects.new(name, arm_data)
    arm_obj.location = (0.0, 0.0, 0.0)
    arm_obj.rotation_euler = (0.0, 0.0, 0.0)
    arm_obj.scale = (1.0, 1.0, 1.0)
    _collection(cfg.COLLECTION_RIG).objects.link(arm_obj)

    # Edit-mode bone creation requires the object to be active.
    view_layer = bpy.context.view_layer
    view_layer.objects.active = arm_obj
    arm_obj.select_set(True)

    bpy.ops.object.mode_set(mode="EDIT")
    try:
        created = {}
        for name_, parent_name, head, tail in bone_layout():
            bone = arm_data.edit_bones.new(name_)
            bone.head = head
            bone.tail = tail
            bone.roll = cfg.BONE_ROLL_RAD
            bone.use_deform = name_ in cfg.DEFORM_BONES
            # use_connect False keeps head positions exactly where the design
            # says they are, instead of snapping to the parent's tail.
            bone.use_connect = False
            created[name_] = bone

        for name_, parent_name, _head, _tail in bone_layout():
            if parent_name is not None:
                created[name_].parent = created[parent_name]
    finally:
        bpy.ops.object.mode_set(mode="OBJECT")

    return arm_obj


def bind_meshes(arm_obj):
    """Parent each mesh to the armature and weight it rigidly to one bone."""
    bound = {}
    for mesh_name, bone_name in sorted(binding_plan().items()):
        obj = bpy.data.objects.get(mesh_name)
        if obj is None:
            raise RuntimeError(
                "mesh %r is missing - run af_vehicle_generate.py first"
                % (mesh_name,))

        # Remove any pre-existing armature modifiers so reruns stay clean.
        for modifier in list(obj.modifiers):
            if modifier.type == "ARMATURE":
                obj.modifiers.remove(modifier)

        obj.parent = arm_obj
        obj.parent_type = "OBJECT"
        obj.matrix_parent_inverse.identity()

        modifier = obj.modifiers.new(name=cfg.MODIFIER_ARMATURE,
                                     type="ARMATURE")
        modifier.object = arm_obj
        modifier.use_vertex_groups = True
        modifier.use_bone_envelopes = False

        # Exactly one vertex group, exactly one weight per vertex.
        for group in list(obj.vertex_groups):
            obj.vertex_groups.remove(group)
        group = obj.vertex_groups.new(name=bone_name)
        group.add(range(len(obj.data.vertices)), 1.0, "REPLACE")

        bound[mesh_name] = {
            "bone": bone_name,
            "vertices": len(obj.data.vertices),
            "vertex_groups": len(obj.vertex_groups),
        }
    return bound


def rig_all():
    arm_obj = create_armature()
    bound = bind_meshes(arm_obj)

    bone_names = [b.name for b in arm_obj.data.bones]
    return {
        "armature": arm_obj.name,
        "bone_count": len(bone_names),
        "bone_names": bone_names,
        "expected_bone_count": len(cfg.BONE_ORDER),
        "bound_meshes": bound,
        "config_hash": cfg.config_hash(),
    }


def print_summary(summary):
    print("")
    print("af_vehicle_rig summary")
    print("  armature   : %s" % summary["armature"])
    print("  bones      : %d (expected %d)" % (
        summary["bone_count"], summary["expected_bone_count"]))
    for name in cfg.BONE_ORDER:
        head = bone_head_m(name)
        print("    %-20s parent=%-16s head=(%.3f, %.3f, %.3f) m"
              "  (%.1f, %.1f, %.1f) cm" % (
                  name,
                  cfg.BONE_PARENTS[name] or "-",
                  head[0], head[1], head[2],
                  cfg.metres_to_cm(head[0]),
                  cfg.metres_to_cm(head[1]),
                  cfg.metres_to_cm(head[2])))
    print("  bound meshes:")
    for mesh_name, info in sorted(summary["bound_meshes"].items()):
        print("    %-20s -> %-20s (%d verts, %d group)" % (
            mesh_name, info["bone"], info["vertices"], info["vertex_groups"]))
    print("  config hash: %s" % summary["config_hash"][:16])


def main():
    print(cfg.describe())

    ok, problems = cfg.self_check()
    if not ok:
        print("")
        print("config self-check FAILED - refusing to build the rig:")
        for problem in problems:
            print("  - %s" % problem)
        return EXIT_FAILED

    if bpy is None:
        print("")
        print("bpy is unavailable: this script must be run inside Blender, e.g.")
        print("  blender --background --python af_vehicle_rig.py")
        return EXIT_NO_BPY

    try:
        summary = rig_all()
    except Exception as exc:  # noqa: BLE001
        print("")
        print("af_vehicle_rig FAILED: %s: %s" % (type(exc).__name__, exc))
        return EXIT_FAILED

    print_summary(summary)

    if summary["bone_count"] != summary["expected_bone_count"]:
        print("")
        print("af_vehicle_rig FAILED: bone count mismatch")
        return EXIT_FAILED

    print("")
    print("af_vehicle_rig: OK")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
