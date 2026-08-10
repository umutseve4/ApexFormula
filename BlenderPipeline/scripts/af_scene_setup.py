"""ApexFormula - scene normalisation and collection scaffolding.

Milestone 0B.

Responsibilities
----------------
1. Force the scene unit system to metric metres with scale length 1.0.
2. Create the collections the pipeline owns, if they are absent.
3. Clear ONLY the collections listed in ``CLEARABLE_COLLECTIONS``
   (AF_Generated, AF_Rig, AF_Export). AF_Source is never touched.
4. Leave every object outside the owned collections completely untouched.

This script is idempotent: running it twice in a row produces the same scene
state as running it once.

Honesty note: this script has NOT been executed inside Blender. Every claim
about how Blender responds to these calls is "requires Blender execution".
Only the module's syntax and structure have been statically inspected.

Usage
-----
    blender --background --python af_scene_setup.py

Exit codes: 0 success, 2 Blender API unavailable, 3 setup failed.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import af_pipeline_config as cfg  # noqa: E402

try:
    import bpy
except ImportError:  # pragma: no cover - only reachable outside Blender
    bpy = None


EXIT_OK = 0
EXIT_NO_BPY = 2
EXIT_FAILED = 3


# ---------------------------------------------------------------------------
# Units
# ---------------------------------------------------------------------------

def apply_unit_settings(scene):
    """Force the documented unit system onto the scene.

    Returns a dict describing what was changed, so the caller can report it.
    """
    units = scene.unit_settings
    before = {
        "system": units.system,
        "length_unit": getattr(units, "length_unit", None),
        "scale_length": units.scale_length,
    }

    units.system = cfg.BLENDER_UNIT_SYSTEM
    if hasattr(units, "length_unit"):
        units.length_unit = cfg.BLENDER_LENGTH_UNIT
    units.scale_length = cfg.BLENDER_SCALE_LENGTH

    after = {
        "system": units.system,
        "length_unit": getattr(units, "length_unit", None),
        "scale_length": units.scale_length,
    }
    return {"before": before, "after": after, "changed": before != after}


# ---------------------------------------------------------------------------
# Collections
# ---------------------------------------------------------------------------

def get_or_create_collection(name, parent):
    """Return the collection ``name``, creating and linking it under ``parent``
    if it does not already exist."""
    existing = bpy.data.collections.get(name)
    if existing is None:
        existing = bpy.data.collections.new(name)
    if existing.name not in {c.name for c in parent.children}:
        # Only link if it is not already linked somewhere under the scene.
        already_linked = any(
            existing.name in {c.name for c in coll.children}
            for coll in bpy.data.collections
        )
        if not already_linked:
            parent.children.link(existing)
    return existing


def build_collection_tree(scene):
    """Create the owned collection tree. Returns the list of names created."""
    root = scene.collection
    created = []

    for name in (cfg.COLLECTION_SOURCE, cfg.COLLECTION_GENERATED,
                 cfg.COLLECTION_RIG, cfg.COLLECTION_EXPORT):
        if bpy.data.collections.get(name) is None:
            created.append(name)
        get_or_create_collection(name, root)

    generated = bpy.data.collections[cfg.COLLECTION_GENERATED]
    for name in cfg.GENERATED_CHILDREN:
        if bpy.data.collections.get(name) is None:
            created.append(name)
        get_or_create_collection(name, generated)

    return created


def _collection_and_descendants(collection):
    yield collection
    for child in collection.children:
        for nested in _collection_and_descendants(child):
            yield nested


def clear_collection(name):
    """Delete every object inside ``name`` and its descendants.

    Refuses to act on any collection outside ``OWNED_COLLECTIONS``. Returns
    the number of objects removed.
    """
    if name not in cfg.OWNED_COLLECTIONS:
        raise ValueError(
            "refusing to clear %r: not an ApexFormula-owned collection" % (name,))

    collection = bpy.data.collections.get(name)
    if collection is None:
        return 0

    victims = []
    for coll in _collection_and_descendants(collection):
        victims.extend(coll.objects)

    # De-duplicate while preserving order (an object may be linked twice).
    unique = []
    seen = set()
    for obj in victims:
        if obj.name not in seen:
            seen.add(obj.name)
            unique.append(obj)

    for obj in unique:
        bpy.data.objects.remove(obj, do_unlink=True)

    return len(unique)


def purge_orphans():
    """Remove orphaned mesh/armature datablocks left behind by clearing.

    Only datablocks with zero users are removed, so nothing still referenced
    by the user's own scene can be lost.
    """
    removed = {"meshes": 0, "armatures": 0}
    for mesh in list(bpy.data.meshes):
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)
            removed["meshes"] += 1
    for arm in list(bpy.data.armatures):
        if arm.users == 0:
            bpy.data.armatures.remove(arm)
            removed["armatures"] += 1
    return removed


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def setup_scene(scene=None):
    """Normalise the scene. Returns a summary dict."""
    scene = scene or bpy.context.scene

    units = apply_unit_settings(scene)
    created = build_collection_tree(scene)

    cleared = {}
    for name in cfg.CLEARABLE_COLLECTIONS:
        cleared[name] = clear_collection(name)

    # Rebuild the child collections that clearing may have emptied but not
    # removed - collections themselves survive, only objects are deleted.
    build_collection_tree(scene)

    orphans = purge_orphans()
    dirs_created = cfg.ensure_dirs()

    return {
        "units": units,
        "collections_created": created,
        "objects_cleared": cleared,
        "orphans_purged": orphans,
        "directories_created": dirs_created,
        "blender_version": tuple(bpy.app.version),
        "config_hash": cfg.config_hash(),
    }


def print_summary(summary):
    print("")
    print("af_scene_setup summary")
    print("  Blender runtime      : %s" % (summary["blender_version"],))
    print("  unit system          : %s / %s / scale %.4f" % (
        summary["units"]["after"]["system"],
        summary["units"]["after"]["length_unit"],
        summary["units"]["after"]["scale_length"]))
    print("  units changed        : %s" % summary["units"]["changed"])
    print("  collections created  : %s" % (summary["collections_created"] or "none"))
    for name, count in sorted(summary["objects_cleared"].items()):
        print("  cleared %-16s : %d object(s)" % (name, count))
    print("  orphans purged       : %d mesh, %d armature" % (
        summary["orphans_purged"]["meshes"], summary["orphans_purged"]["armatures"]))
    print("  directories created  : %s" % (summary["directories_created"] or "none"))
    print("  config hash          : %s" % summary["config_hash"][:16])


def main():
    print(cfg.describe())

    ok, problems = cfg.self_check()
    if not ok:
        print("")
        print("config self-check FAILED - refusing to modify the scene:")
        for problem in problems:
            print("  - %s" % problem)
        return EXIT_FAILED

    if bpy is None:
        print("")
        print("bpy is unavailable: this script must be run inside Blender, e.g.")
        print("  blender --background --python af_scene_setup.py")
        return EXIT_NO_BPY

    runtime = tuple(bpy.app.version[:2])
    if runtime != cfg.TARGET_BLENDER_VERSION:
        print("")
        print("WARNING: running Blender %d.%d but this pipeline targets %d.%d LTS."
              % (runtime + cfg.TARGET_BLENDER_VERSION))
        print("         Continuing, but export options may differ.")

    try:
        summary = setup_scene()
    except Exception as exc:  # noqa: BLE001 - report, do not mask
        print("")
        print("af_scene_setup FAILED: %s: %s" % (type(exc).__name__, exc))
        return EXIT_FAILED

    print_summary(summary)
    print("")
    print("af_scene_setup: OK")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
