"""ApexFormula - end-to-end pipeline smoke test.

Milestone 0B.

Runs the whole Blender-side pipeline in order, inside a single Blender session:

    1. af_scene_setup   - units, axes, owned collection tree
    2. af_vehicle_generate - placeholder blockout meshes, collision, LODs
    3. af_vehicle_rig   - 11-bone armature and rigid binding
    4. af_materials     - placeholder material slots
    5. af_validate      - 21 checks (pre-export gate)
    6. af_export        - FBX with runtime-filtered exporter settings
    7. af_validate      - the same checks again (post-export confirmation)

Stages are invoked as Python function calls on the imported modules, not as
subprocesses: one Blender session, one scene, real state passed between stages.

The run stops at the first failing stage and returns a non-zero exit code, so
``blender --background --python af_smoke_test.py`` is usable as a CI gate.

Honesty note: this orchestration has NOT been run inside Blender. Its structure
is "statically inspected"; every claim about what it produces is "requires
Blender execution".

Usage
-----
    blender --background --python af_smoke_test.py

Exit codes: 0 all stages passed, 2 Blender API unavailable, 3 a stage failed.
"""

from __future__ import annotations

import datetime
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import af_pipeline_config as cfg  # noqa: E402

try:
    import bpy
except ImportError:  # pragma: no cover
    bpy = None


EXIT_OK = 0
EXIT_NO_BPY = 2
EXIT_FAILED = 3

REPORT_SUBJECT = "smoke_test"

RULE = "=" * 70


# ---------------------------------------------------------------------------
# Stage definitions
# ---------------------------------------------------------------------------

def _stage_scene_setup():
    import af_scene_setup
    info = af_scene_setup.setup_scene()
    af_scene_setup.print_summary(info)
    after = info["units"]["after"]
    ok = (after["system"] == cfg.BLENDER_UNIT_SYSTEM
          and abs(after["scale_length"] - cfg.BLENDER_SCALE_LENGTH) < 1e-9)
    return ok, {
        "collections_created": info["collections_created"],
        "objects_cleared": info["objects_cleared"],
        "orphans_purged": info["orphans_purged"],
        "unit_system": after["system"],
        "scale_length": after["scale_length"],
    }


def _stage_generate():
    import af_vehicle_generate
    info = af_vehicle_generate.generate_all()
    af_vehicle_generate.print_summary(info)
    ok = (bool(info["body"])
          and len(info["wheels"]) == len(cfg.CORNERS)
          and len(info["suspension"]) == len(cfg.CORNERS)
          and len(info["collision"]) == len(cfg.COLLISION_PIECES)
          and len(info["lods"]) == len(cfg.LOD_LEVELS))
    return ok, {
        "body": info["body"],
        "body_polygons": info["body_polygons"],
        "wheels": len(info["wheels"]),
        "suspension": len(info["suspension"]),
        "collision": len(info["collision"]),
        "lods": len(info["lods"]),
    }


def _stage_rig():
    import af_vehicle_rig
    info = af_vehicle_rig.rig_all()
    af_vehicle_rig.print_summary(info)
    ok = list(info["bone_names"]) == list(cfg.BONE_ORDER)
    return ok, {
        "armature": info["armature"],
        "bone_count": info["bone_count"],
        "expected_bone_count": info["expected_bone_count"],
        "bone_order_matches_config": ok,
        "bound_meshes": len(info["bound_meshes"]),
    }


def _stage_materials():
    import af_materials
    info = af_materials.apply_all()
    af_materials.print_summary(info)
    ok = not info["missing_objects"]
    return ok, {
        "meshes_with_slots": len(info["applied"]),
        "missing_objects": info["missing_objects"],
        "materials_in_file": len(info["materials_in_file"]),
    }


def _stage_validate_pre():
    return _run_validate("pre-export")


def _stage_validate_post():
    return _run_validate("post-export")


def _run_validate(phase):
    import af_validate
    _results, report, json_path, _text_path = af_validate.validate()
    counts = report["summary"]
    failed = counts["failed"]
    return failed == 0, {
        "phase": phase,
        "total": counts["total"],
        "passed": counts["passed"],
        "failed": failed,
        "skipped": counts["skipped"],
        "report": os.path.relpath(json_path, cfg.REPO_ROOT),
        "failed_checks": [c["name"] for c in report["checks"]
                          if c["status"] == "FAIL"],
    }


def _stage_export():
    import af_export
    info = af_export.export_all()
    af_export.write_report(info)
    fbx = info["fbx"]
    ok = bool(fbx.get("exists")) and fbx.get("size_bytes", 0) > 0
    return ok, {"fbx_path": fbx.get("path"),
                "fbx_bytes": fbx.get("size_bytes"),
                "dropped_settings": fbx.get(
                    "settings_dropped_unknown_to_exporter", []),
                "bones_exported": len(info.get("exported_bone_list", []))}


STAGES = (
    ("1. scene setup", _stage_scene_setup),
    ("2. generate geometry", _stage_generate),
    ("3. rig", _stage_rig),
    ("4. materials", _stage_materials),
    ("5. validate (pre-export)", _stage_validate_pre),
    ("6. export FBX", _stage_export),
    ("7. validate (post-export)", _stage_validate_post),
)


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_stages():
    results = []
    all_ok = True

    for name, func in STAGES:
        print("")
        print(RULE)
        print("STAGE %s" % name)
        print(RULE)

        started = time.time()
        try:
            ok, detail = func()
            error = None
        except Exception as exc:  # noqa: BLE001
            ok = False
            detail = {}
            error = "%s: %s" % (type(exc).__name__, exc)
            print("  EXCEPTION: %s" % error)

        elapsed = time.time() - started
        status = "PASS" if ok else "FAIL"
        print("  -> %s (%.2fs)" % (status, elapsed))
        for key in sorted(detail):
            value = detail[key]
            if isinstance(value, list) and len(value) > 8:
                value = "%d items" % len(value)
            print("     %-20s %s" % (key, value))

        results.append({
            "stage": name,
            "status": status,
            "seconds": round(elapsed, 3),
            "detail": detail,
            "error": error,
        })

        if not ok:
            all_ok = False
            print("")
            print("  stopping: stage failed, later stages would test nothing "
                  "meaningful")
            break

    return all_ok, results


def build_report(all_ok, results):
    return {
        "project": cfg.PROJECT_NAME,
        "script": os.path.basename(__file__),
        "pipeline_version": cfg.PIPELINE_VERSION,
        "config_hash": cfg.config_hash(),
        "generated_utc": datetime.datetime.now(datetime.timezone.utc)
                                  .strftime("%Y-%m-%dT%H:%M:%SZ"),
        "blender_runtime": list(bpy.app.version) if bpy else None,
        "target_blender_version": list(cfg.TARGET_BLENDER_VERSION),
        "target_unreal_version": cfg.TARGET_UNREAL_VERSION,
        "overall": "PASS" if all_ok else "FAIL",
        "stages_run": len(results),
        "stages_defined": len(STAGES),
        "stages": results,
    }


def write_report(report):
    cfg.ensure_dirs()
    json_path = cfg.report_path(REPORT_SUBJECT, "json")
    text_path = cfg.report_path(REPORT_SUBJECT, "txt")

    with open(json_path, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, sort_keys=True, default=str)
        handle.write("\n")

    lines = ["ApexFormula pipeline smoke test", RULE]
    lines.append("pipeline version : %s" % report["pipeline_version"])
    lines.append("config hash      : %s" % report["config_hash"])
    lines.append("generated (UTC)  : %s" % report["generated_utc"])
    lines.append("Blender runtime  : %s" % (report["blender_runtime"],))
    lines.append("target Blender   : %s" % (report["target_blender_version"],))
    lines.append("overall          : %s" % report["overall"])
    lines.append("stages run       : %d of %d"
                 % (report["stages_run"], report["stages_defined"]))
    lines.append("")
    for entry in report["stages"]:
        lines.append("%-28s %-4s  %6.2fs"
                     % (entry["stage"], entry["status"], entry["seconds"]))
        if entry["error"]:
            lines.append("    error: %s" % entry["error"])
        for key in sorted(entry["detail"]):
            lines.append("    %-24s %s" % (key, entry["detail"][key]))
        lines.append("")
    lines.append("Honesty: results above are produced by an actual Blender run.")
    lines.append("If this file is absent from the repository, no such run has")
    lines.append("happened and every pipeline claim remains 'requires Blender")
    lines.append("execution'.")
    lines.append("")

    with open(text_path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))

    return json_path, text_path


def main():
    print(cfg.describe())

    ok, problems = cfg.self_check()
    if not ok:
        print("")
        print("config self-check FAILED - refusing to run the pipeline:")
        for problem in problems:
            print("  - %s" % problem)
        return EXIT_FAILED

    if bpy is None:
        print("")
        print("bpy is unavailable: this smoke test must be run inside Blender:")
        print("  blender --background --python af_smoke_test.py")
        print("")
        print("Nothing was built, exported or validated. Do not interpret this")
        print("exit as a pipeline result.")
        return EXIT_NO_BPY

    if tuple(bpy.app.version[:2]) != tuple(cfg.TARGET_BLENDER_VERSION):
        print("")
        print("WARNING: Blender %s.%s detected, pipeline targets %s.%s. "
              "Continuing, but exporter options may differ."
              % (bpy.app.version[0], bpy.app.version[1],
                 cfg.TARGET_BLENDER_VERSION[0], cfg.TARGET_BLENDER_VERSION[1]))

    all_ok, results = run_stages()
    report = build_report(all_ok, results)
    json_path, text_path = write_report(report)

    print("")
    print(RULE)
    print("SMOKE TEST %s  (%d of %d stages run)"
          % (report["overall"], report["stages_run"], report["stages_defined"]))
    print(RULE)
    for entry in results:
        print("  %-28s %s" % (entry["stage"], entry["status"]))
    print("")
    print("  report (json) : %s" % json_path)
    print("  report (text) : %s" % text_path)

    return EXIT_OK if all_ok else EXIT_FAILED


if __name__ == "__main__":
    sys.exit(main())
