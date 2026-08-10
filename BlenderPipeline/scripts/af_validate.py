"""ApexFormula - pipeline validation gate.

Milestone 0B.

Implements the twenty-one checks specified in
``Documentation/BLENDER_PIPELINE_DESIGN.md`` section 4. This script never
mutates the scene: it measures, compares against ``af_pipeline_config`` and
reports. A check that cannot be evaluated is reported as SKIPPED with a reason,
never silently passed.

Every measured length is reported in both metres and centimetres, because the
Blender side works in metres and the Unreal side works in centimetres, and the
majority of pipeline mistakes live in exactly that gap.

Outputs (deterministic filenames, so reruns overwrite and diffs are meaningful):
  reports/af_report_validate.json
  reports/af_report_validate.txt

Honesty note: this script has NOT been executed inside Blender. Every check
result is "requires Blender execution" until a real run produces a report.
The JSON report, once produced by a real run, is the only artefact that
supports an "automatically validated" claim.

Usage
-----
    blender --background --python af_validate.py

Exit codes: 0 all checks passed, 1 one or more checks failed,
2 Blender API unavailable, 3 validation itself errored.
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
EXIT_FAILED_CHECKS = 1
EXIT_NO_BPY = 2
EXIT_ERROR = 3

REPORT_SUBJECT = "validate"

PASS = "PASS"
FAIL = "FAIL"
SKIP = "SKIP"


class Results:
    """Accumulates check outcomes in declaration order."""

    def __init__(self):
        self.checks = []

    def add(self, number, name, status, expected=None, measured=None,
            tolerance=None, detail=""):
        self.checks.append({
            "number": number,
            "name": name,
            "status": status,
            "expected": expected,
            "measured": measured,
            "tolerance": tolerance,
            "detail": detail,
        })

    def record(self, number, name, ok, expected=None, measured=None,
               tolerance=None, detail=""):
        self.add(number, name, PASS if ok else FAIL,
                 expected, measured, tolerance, detail)

    @property
    def failed(self):
        return [c for c in self.checks if c["status"] == FAIL]

    @property
    def skipped(self):
        return [c for c in self.checks if c["status"] == SKIP]

    @property
    def passed(self):
        return [c for c in self.checks if c["status"] == PASS]


# ---------------------------------------------------------------------------
# Scene inspection helpers
# ---------------------------------------------------------------------------

def exported_mesh_objects():
    """Every mesh the exporter will emit: body, wheels, suspension, LODs."""
    names = [cfg.body_name()]
    names.extend(cfg.all_wheel_names())
    names.extend(cfg.all_suspension_names())
    names.extend(cfg.lod_name(cfg.body_name(), level) for level in cfg.LOD_LEVELS)
    return [(n, bpy.data.objects.get(n)) for n in names]


def collision_objects():
    names = [cfg.collision_name(cfg.body_name(), index)
             for _t, index, _c, _h in cfg.COLLISION_PIECES]
    return [(n, bpy.data.objects.get(n)) for n in names]


def deformable_objects():
    names = [cfg.body_name()]
    names.extend(cfg.all_wheel_names())
    names.extend(cfg.all_suspension_names())
    return [(n, bpy.data.objects.get(n)) for n in names]


def world_bounds(objects):
    """Return ``(min_xyz, max_xyz)`` over the given objects, in metres."""
    mins = [float("inf")] * 3
    maxs = [float("-inf")] * 3
    for obj in objects:
        if obj is None or obj.type != "MESH":
            continue
        for corner in obj.bound_box:
            world = obj.matrix_world @ _vector(corner)
            for axis in range(3):
                mins[axis] = min(mins[axis], world[axis])
                maxs[axis] = max(maxs[axis], world[axis])
    return tuple(mins), tuple(maxs)


def _vector(triple):
    from mathutils import Vector  # imported lazily; only exists in Blender
    return Vector(triple)


def both_units(value_m):
    """Return a dict quoting a metre value in metres and centimetres."""
    return {"m": round(value_m, 6), "cm": round(cfg.metres_to_cm(value_m), 4)}


def is_identity_transform(obj):
    eps = cfg.TOLERANCE["transform_epsilon"]
    loc_ok = all(abs(v) <= eps for v in obj.location)
    rot_ok = all(abs(v) <= eps for v in obj.rotation_euler)
    scale_ok = all(abs(v - 1.0) <= eps for v in obj.scale)
    return loc_ok and rot_ok and scale_ok


# ---------------------------------------------------------------------------
# Checks 1-7: geometry
# ---------------------------------------------------------------------------

def check_geometry(results):
    offenders = []
    for name, obj in exported_mesh_objects() + collision_objects():
        if obj is None:
            offenders.append("%s: missing" % name)
        elif not is_identity_transform(obj):
            offenders.append("%s: loc=%s rot=%s scale=%s" % (
                name, tuple(obj.location), tuple(obj.rotation_euler),
                tuple(obj.scale)))
    results.record(1, "identity object transforms", not offenders,
                   expected="identity on every exported object",
                   measured=offenders or "all identity",
                   tolerance=cfg.TOLERANCE["transform_epsilon"])

    offenders = []
    for name, obj in exported_mesh_objects() + collision_objects():
        if obj is None:
            continue
        if any(v <= 0.0 for v in obj.scale):
            offenders.append("%s: non-positive scale %s" % (name, tuple(obj.scale)))
        elif len(set(round(v, 6) for v in obj.scale)) != 1:
            offenders.append("%s: non-uniform scale %s" % (name, tuple(obj.scale)))
    results.record(2, "no negative or accidental non-uniform scale", not offenders,
                   expected="uniform positive scale", measured=offenders or "clean")

    offenders = []
    for name, obj in exported_mesh_objects() + collision_objects():
        if obj is None:
            continue
        mesh = obj.data
        used = set()
        for polygon in mesh.polygons:
            used.update(polygon.vertices)
        loose_verts = len(mesh.vertices) - len(used)

        edge_users = {}
        for polygon in mesh.polygons:
            for edge_key in polygon.edge_keys:
                edge_users[edge_key] = edge_users.get(edge_key, 0) + 1
        loose_edges = sum(1 for e in mesh.edges
                          if e.key not in edge_users)
        zero_area = sum(1 for p in mesh.polygons if p.area <= 1.0e-9)

        if loose_verts or loose_edges or zero_area:
            offenders.append(
                "%s: %d loose vert, %d loose edge, %d zero-area face"
                % (name, loose_verts, loose_edges, zero_area))
    results.record(3, "no loose vertices, loose edges or zero-area faces",
                   not offenders, expected="0 of each",
                   measured=offenders or "0 of each on every mesh")

    offenders = []
    for name, obj in collision_objects():
        if obj is None:
            continue
        mesh = obj.data
        edge_faces = {}
        for polygon in mesh.polygons:
            for edge_key in polygon.edge_keys:
                edge_faces[edge_key] = edge_faces.get(edge_key, 0) + 1
        bad = [k for k, v in edge_faces.items() if v != 2]
        if bad:
            offenders.append("%s: %d non-manifold edge(s)" % (name, len(bad)))
    results.record(4, "collision meshes are manifold", not offenders,
                   expected="every edge shared by exactly 2 faces",
                   measured=offenders or "manifold")

    offenders = []
    budgets = {}
    for name, obj in exported_mesh_objects():
        if obj is None:
            continue
        if name.startswith(cfg.COLLISION_NAME_PREFIX):
            budget_key = "collision"
        elif cfg.body_name() in name:
            budget_key = "body"
        elif any(w == name for w in cfg.all_wheel_names()):
            budget_key = "wheel"
        else:
            budget_key = "suspension"
        budget = cfg.FACE_BUDGET[budget_key]
        count = len(obj.data.polygons)
        budgets[name] = {"faces": count, "budget": budget, "class": budget_key}
        if count > budget:
            offenders.append("%s: %d faces > budget %d" % (name, count, budget))
    for name, obj in collision_objects():
        if obj is None:
            continue
        count = len(obj.data.polygons)
        budget = cfg.FACE_BUDGET["collision"]
        budgets[name] = {"faces": count, "budget": budget, "class": "collision"}
        if count > budget:
            offenders.append("%s: %d faces > budget %d" % (name, count, budget))
    results.record(5, "face count within budget", not offenders,
                   expected=dict(cfg.FACE_BUDGET), measured=budgets,
                   detail="; ".join(offenders))

    offenders = []
    for name, obj in exported_mesh_objects() + collision_objects():
        if obj is None:
            continue
        mesh = obj.data
        # A closed, consistently wound mesh has every interior edge used once
        # in each direction. Count directed edges to detect flipped islands.
        directed = set()
        conflicts = 0
        for polygon in mesh.polygons:
            verts = list(polygon.vertices)
            for i, a in enumerate(verts):
                b = verts[(i + 1) % len(verts)]
                if (a, b) in directed:
                    conflicts += 1
                directed.add((a, b))
        if conflicts:
            offenders.append("%s: %d duplicated winding(s)" % (name, conflicts))
    results.record(6, "consistent normals / no inverted islands", not offenders,
                   expected="no duplicated directed edges",
                   measured=offenders or "consistent")

    offenders = []
    for name, obj in deformable_objects():
        if obj is None:
            continue
        ngons = sum(1 for p in obj.data.polygons if len(p.vertices) > 4)
        if ngons:
            offenders.append("%s: %d n-gon(s)" % (name, ngons))
    results.record(7, "no n-gons on deformable meshes", not offenders,
                   expected="0 n-gons", measured=offenders or "0 n-gons")


# ---------------------------------------------------------------------------
# Checks 8-11: UV and materials
# ---------------------------------------------------------------------------

def check_uv_and_materials(results):
    offenders = []
    for name, obj in exported_mesh_objects():
        if obj is None:
            continue
        layers = [layer.name for layer in obj.data.uv_layers]
        if not layers:
            offenders.append("%s: no UV map" % name)
        elif layers[0] != cfg.UV_MAP_NAME:
            offenders.append("%s: first UV map is %r, expected %r"
                             % (name, layers[0], cfg.UV_MAP_NAME))
    results.record(8, "UV map present and correctly named", not offenders,
                   expected=cfg.UV_MAP_NAME, measured=offenders or "correct")

    results.add(9, "no overlapping UVs on lightmap channel", SKIP,
                expected="no overlap on a declared lightmap channel",
                measured=None,
                detail="No separate lightmap UV channel is declared for the "
                       "0B placeholder vehicle, so there is nothing to test. "
                       "Reported as SKIP rather than PASS.")

    import af_materials  # local import so this module stays importable alone
    plan = af_materials.slot_plan()

    offenders = []
    measured = {}
    for mesh_name, purposes in sorted(plan.items()):
        obj = bpy.data.objects.get(mesh_name)
        if obj is None:
            offenders.append("%s: missing" % mesh_name)
            continue
        actual = [m.name if m else None for m in obj.data.materials]
        expected = [cfg.material_name(p) for p in purposes]
        measured[mesh_name] = actual
        if actual != expected:
            offenders.append("%s: slots %s, expected %s"
                             % (mesh_name, actual, expected))
    results.record(10, "material slot count and order match", not offenders,
                   expected={k: [cfg.material_name(p) for p in v]
                             for k, v in sorted(plan.items())},
                   measured=measured, detail="; ".join(offenders))

    offenders = []
    for mesh_name in sorted(plan):
        obj = bpy.data.objects.get(mesh_name)
        if obj is None:
            continue
        for index, material in enumerate(obj.data.materials):
            if material is None:
                offenders.append("%s: slot %d empty" % (mesh_name, index))
    results.record(11, "no empty material slots", not offenders,
                   expected="every slot assigned",
                   measured=offenders or "all assigned")


# ---------------------------------------------------------------------------
# Checks 12-16: rig
# ---------------------------------------------------------------------------

def check_rig(results):
    arm_obj = bpy.data.objects.get(cfg.armature_name())
    if arm_obj is None:
        for number, name in ((12, "bone list matches config"),
                             (13, "bone hierarchy matches config"),
                             (14, "no zero-weight vertices"),
                             (15, "weights per vertex within maximum"),
                             (16, "armature transform is identity")):
            results.add(number, name, FAIL,
                        expected="armature %s present" % cfg.armature_name(),
                        measured="missing")
        return

    actual = [b.name for b in arm_obj.data.bones]
    expected = list(cfg.BONE_ORDER)
    results.record(12, "bone list matches config", sorted(actual) == sorted(expected),
                   expected=expected, measured=actual,
                   detail="extra=%s missing=%s" % (
                       sorted(set(actual) - set(expected)),
                       sorted(set(expected) - set(actual))))

    mismatches = []
    hierarchy = {}
    for bone in arm_obj.data.bones:
        parent = bone.parent.name if bone.parent else None
        hierarchy[bone.name] = parent
        want = cfg.BONE_PARENTS.get(bone.name, "<unknown bone>")
        if parent != want:
            mismatches.append("%s: parent %r, expected %r"
                              % (bone.name, parent, want))
    results.record(13, "bone hierarchy matches config", not mismatches,
                   expected=dict(cfg.BONE_PARENTS), measured=hierarchy,
                   detail="; ".join(mismatches))

    zero_weight = []
    over_budget = []
    max_weights = cfg.TOLERANCE["max_weights_per_vertex"]
    for name, obj in deformable_objects():
        if obj is None:
            continue
        group_names = {g.index: g.name for g in obj.vertex_groups}
        bone_names = set(b.name for b in arm_obj.data.bones)
        zero = 0
        worst = 0
        for vertex in obj.data.vertices:
            influences = [g for g in vertex.groups
                          if g.weight > 0.0
                          and group_names.get(g.group) in bone_names]
            if not influences:
                zero += 1
            worst = max(worst, len(influences))
        if zero:
            zero_weight.append("%s: %d unweighted vertex(es)" % (name, zero))
        if worst > max_weights:
            over_budget.append("%s: %d influences" % (name, worst))

    results.record(14, "every deformable vertex has a weight", not zero_weight,
                   expected="0 unweighted vertices",
                   measured=zero_weight or "0 unweighted vertices")
    results.record(15, "weights per vertex within maximum", not over_budget,
                   expected=max_weights,
                   measured=over_budget or "<= %d everywhere" % max_weights,
                   tolerance=max_weights)

    at_origin = is_identity_transform(arm_obj)
    results.record(16, "armature transform is identity at world origin", at_origin,
                   expected="identity at (0, 0, 0)",
                   measured={"location": both_units_triple(arm_obj.location),
                             "rotation_euler": tuple(arm_obj.rotation_euler),
                             "scale": tuple(arm_obj.scale)},
                   tolerance=cfg.TOLERANCE["transform_epsilon"])


def both_units_triple(vector):
    return {"m": [round(v, 6) for v in vector],
            "cm": [round(cfg.metres_to_cm(v), 4) for v in vector]}


# ---------------------------------------------------------------------------
# Checks 17-19: scale and placement
# ---------------------------------------------------------------------------

def check_scale_and_placement(results):
    body_and_wheels = []
    for _name, obj in exported_mesh_objects():
        if obj is None:
            continue
        if "_LOD" in obj.name:
            continue
        body_and_wheels.append(obj)

    if not body_and_wheels:
        for number, name in ((17, "bounding box within tolerance"),
                             (18, "Z=0 contact plane"),
                             (19, "wheel centres within tolerance")):
            results.add(number, name, FAIL, expected="meshes present",
                        measured="none found")
        return

    mins, maxs = world_bounds(body_and_wheels)
    size = tuple(maxs[i] - mins[i] for i in range(3))
    tol = cfg.TOLERANCE["length_m"]

    expected_size = (cfg.DESIGN["overall_length_m"],
                     cfg.DESIGN["overall_width_m"],
                     cfg.DESIGN["overall_height_m"])
    deltas = tuple(size[i] - expected_size[i] for i in range(3))
    # The placeholder must not exceed the design envelope; being smaller than
    # the envelope is acceptable for a blockout, being larger is not.
    ok = all(deltas[i] <= tol for i in range(3))
    results.record(17, "bounding box within design envelope", ok,
                   expected={"length": both_units(expected_size[0]),
                             "width": both_units(expected_size[1]),
                             "height": both_units(expected_size[2])},
                   measured={"length": both_units(size[0]),
                             "width": both_units(size[1]),
                             "height": both_units(size[2]),
                             "min": both_units_triple(mins),
                             "max": both_units_triple(maxs)},
                   tolerance=both_units(tol),
                   detail="deltas (measured - design) m: %s" % (
                       [round(d, 6) for d in deltas],))

    contact_tol = cfg.TOLERANCE["contact_plane_m"]
    wheel_bottoms = {}
    offenders = []
    for corner in cfg.CORNERS:
        obj = bpy.data.objects.get(cfg.wheel_name(corner))
        if obj is None:
            offenders.append("%s: missing" % cfg.wheel_name(corner))
            continue
        wmin, _wmax = world_bounds([obj])
        wheel_bottoms[corner] = both_units(wmin[2])
        if abs(wmin[2]) > contact_tol:
            offenders.append("%s: lowest Z = %.6f m (%.3f cm)"
                             % (corner, wmin[2], cfg.metres_to_cm(wmin[2])))
    results.record(18, "Z=0 is the tyre contact plane", not offenders,
                   expected=both_units(0.0), measured=wheel_bottoms,
                   tolerance=both_units(contact_tol),
                   detail="; ".join(offenders))

    centre_tol = cfg.TOLERANCE["wheel_centre_m"]
    offenders = []
    centres = {}
    for corner in cfg.CORNERS:
        obj = bpy.data.objects.get(cfg.wheel_name(corner))
        if obj is None:
            offenders.append("%s: missing" % corner)
            continue
        wmin, wmax = world_bounds([obj])
        measured_centre = tuple((wmin[i] + wmax[i]) / 2.0 for i in range(3))
        design_centre = cfg.wheel_centre_m(corner)
        delta = tuple(measured_centre[i] - design_centre[i] for i in range(3))
        centres[corner] = {
            "design": both_units_triple(design_centre),
            "measured": both_units_triple(measured_centre),
            "delta_m": [round(d, 6) for d in delta],
        }
        if any(abs(d) > centre_tol for d in delta):
            offenders.append("%s: delta %s m" % (corner, [round(d, 6) for d in delta]))
    results.record(19, "wheel centres at configured wheelbase/track", not offenders,
                   expected={"wheelbase": both_units(cfg.DESIGN["wheelbase_m"]),
                             "track_front": both_units(cfg.DESIGN["track_front_m"]),
                             "track_rear": both_units(cfg.DESIGN["track_rear_m"])},
                   measured=centres, tolerance=both_units(centre_tol),
                   detail="; ".join(offenders))


# ---------------------------------------------------------------------------
# Checks 20-21: naming
# ---------------------------------------------------------------------------

def expected_name_set():
    names = {cfg.body_name(), cfg.armature_name()}
    names.update(cfg.all_wheel_names())
    names.update(cfg.all_suspension_names())
    names.update(cfg.lod_name(cfg.body_name(), level) for level in cfg.LOD_LEVELS)
    names.update(cfg.collision_name(cfg.body_name(), index)
                 for _t, index, _c, _h in cfg.COLLISION_PIECES)
    return names


def check_naming(results):
    expected = expected_name_set()
    owned = set(cfg.OWNED_COLLECTIONS)

    actual = set()
    for collection_name in owned:
        collection = bpy.data.collections.get(collection_name)
        if collection is None:
            continue
        for obj in collection.all_objects:
            actual.add(obj.name)

    unexpected = sorted(actual - expected)
    missing = sorted(expected - actual)
    results.record(20, "object names match the declared patterns",
                   not unexpected and not missing,
                   expected=sorted(expected), measured=sorted(actual),
                   detail="unexpected=%s missing=%s" % (unexpected, missing))

    hits = []
    candidates = set(actual)
    candidates.update(cfg.OWNED_COLLECTIONS)
    candidates.update(m.name for m in bpy.data.materials)
    candidates.update(b.name for a in bpy.data.armatures for b in a.bones)
    candidates.update(os.path.basename(p) for p in (
        cfg.export_fbx_path(), cfg.export_glb_path(),
        cfg.report_path(REPORT_SUBJECT, "json"),
        cfg.report_path(REPORT_SUBJECT, "txt")))

    for name in sorted(candidates):
        for token in cfg.PROHIBITED_NAME_TOKENS:
            if token in name:
                hits.append("%s contains %r" % (name, token))
    results.record(21, "no prohibited tokens in any name", not hits,
                   expected="none of %s" % (cfg.PROHIBITED_NAME_TOKENS,),
                   measured=hits or "none found")


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def build_report(results, export_info=None):
    return {
        "project": cfg.PROJECT_NAME,
        "script": os.path.basename(__file__),
        "pipeline_version": cfg.PIPELINE_VERSION,
        "config_hash": cfg.config_hash(),
        "generated_utc": datetime.datetime.now(datetime.timezone.utc)
                                  .strftime("%Y-%m-%dT%H:%M:%SZ"),
        "blender_runtime": list(bpy.app.version) if bpy else None,
        "target_blender": list(cfg.TARGET_BLENDER_VERSION),
        "target_unreal": cfg.TARGET_UNREAL_VERSION,
        "units": {"blender": "metres", "unreal": "centimetres",
                  "cm_per_unit": cfg.CM_PER_UNIT},
        "expected_bone_list": list(cfg.BONE_ORDER),
        "expected_bone_count": len(cfg.BONE_ORDER),
        "summary": {
            "total": len(results.checks),
            "passed": len(results.passed),
            "failed": len(results.failed),
            "skipped": len(results.skipped),
        },
        "checks": results.checks,
        "export": export_info or {},
    }


def render_text(report):
    lines = []
    lines.append("ApexFormula validation report")
    lines.append("=" * 60)
    lines.append("pipeline version : %s" % report["pipeline_version"])
    lines.append("config hash      : %s" % report["config_hash"])
    lines.append("generated (UTC)  : %s" % report["generated_utc"])
    lines.append("Blender runtime  : %s" % (report["blender_runtime"],))
    lines.append("target Blender   : %s LTS" % (report["target_blender"],))
    lines.append("target Unreal    : %s" % report["target_unreal"])
    lines.append("units            : Blender metres -> Unreal centimetres "
                 "(x%.1f)" % report["units"]["cm_per_unit"])
    lines.append("")
    summary = report["summary"]
    lines.append("checks: %d total, %d passed, %d failed, %d skipped" % (
        summary["total"], summary["passed"], summary["failed"],
        summary["skipped"]))
    lines.append("")
    for check in report["checks"]:
        lines.append("[%s] %2d. %s" % (
            check["status"], check["number"], check["name"]))
        if check["expected"] is not None:
            lines.append("        expected : %s" % _short(check["expected"]))
        if check["measured"] is not None:
            lines.append("        measured : %s" % _short(check["measured"]))
        if check["tolerance"] is not None:
            lines.append("        tolerance: %s" % _short(check["tolerance"]))
        if check["detail"]:
            lines.append("        detail   : %s" % _short(check["detail"]))
    lines.append("")
    lines.append("expected bone list (%d, no leaf bones):" %
                 report["expected_bone_count"])
    for bone in report["expected_bone_list"]:
        lines.append("  %s" % bone)
    if report["export"]:
        lines.append("")
        lines.append("export:")
        for key, value in sorted(report["export"].items()):
            lines.append("  %-20s %s" % (key, _short(value)))
    lines.append("")
    return "\n".join(lines)


def _short(value, limit=400):
    text = value if isinstance(value, str) else json.dumps(value, sort_keys=True)
    if len(text) > limit:
        return text[:limit] + " ...(truncated)"
    return text


def write_reports(report):
    cfg.ensure_dirs()
    json_path = cfg.report_path(REPORT_SUBJECT, "json")
    text_path = cfg.report_path(REPORT_SUBJECT, "txt")

    with open(json_path, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, sort_keys=True, default=str)
        handle.write("\n")
    with open(text_path, "w", encoding="utf-8") as handle:
        handle.write(render_text(report))

    return json_path, text_path


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def run_all_checks():
    results = Results()
    check_geometry(results)
    check_uv_and_materials(results)
    check_rig(results)
    check_scale_and_placement(results)
    check_naming(results)
    return results


def validate(export_info=None):
    results = run_all_checks()
    report = build_report(results, export_info)
    json_path, text_path = write_reports(report)
    return results, report, json_path, text_path


def main():
    print(cfg.describe())

    ok, problems = cfg.self_check()
    if not ok:
        print("")
        print("config self-check FAILED - validation cannot be trusted:")
        for problem in problems:
            print("  - %s" % problem)
        return EXIT_ERROR

    if bpy is None:
        print("")
        print("bpy is unavailable: this script must be run inside Blender, e.g.")
        print("  blender --background --python af_validate.py")
        return EXIT_NO_BPY

    try:
        results, report, json_path, text_path = validate()
    except Exception as exc:  # noqa: BLE001
        print("")
        print("af_validate ERRORED: %s: %s" % (type(exc).__name__, exc))
        return EXIT_ERROR

    print("")
    print(render_text(report))
    print("report (json): %s" % json_path)
    print("report (text): %s" % text_path)

    if results.failed:
        print("")
        print("af_validate: %d check(s) FAILED" % len(results.failed))
        return EXIT_FAILED_CHECKS

    print("")
    print("af_validate: all checks passed (%d skipped)" % len(results.skipped))
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
