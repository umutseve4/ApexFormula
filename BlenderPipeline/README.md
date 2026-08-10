# ApexFormula — Blender Pipeline

Milestone 0B. This directory holds the Blender-side authoring and export
pipeline for the ApexFormula vehicle. It is the source of truth for geometry,
rig and export settings; Unreal consumes what leaves `exports/`.

The design this code implements is documented in
[`../Documentation/BLENDER_PIPELINE_DESIGN.md`](../Documentation/BLENDER_PIPELINE_DESIGN.md).

---

## 1. Honesty statement — read this first

**No script in this directory has been executed inside Blender.** The authoring
environment used to write them has Python 3.12 but does not have `bpy`
installed, so the Blender-dependent code paths cannot be imported, let alone
run.

What has actually been done:

| Item | Label |
| --- | --- |
| All eight scripts parse and byte-compile under Python 3.12 (`py_compile`) | `automatically validated` |
| `af_pipeline_config.self_check()` executed standalone, exit code 0 | `automatically validated` |
| Pure, `bpy`-free helper functions executed standalone (see §6) | `automatically validated` |
| Script structure, naming, config-symbol usage, absence of hardcoded values | `statically inspected` |
| Anything a script *does* to a Blender scene | `requires Blender execution` |
| Blender 5.2 LTS FBX exporter option names | `requires Blender execution` |
| Correct import of the FBX into Unreal Engine 5.8 | `requires Unreal Editor verification` |
| The vehicle looking right | `requires visual inspection` |

If `reports/` in this repository is empty, the pipeline has never been run.
The presence of a committed report is the only evidence that it has.

---

## 2. Layout

```
BlenderPipeline/
  scripts/     the af_*.py pipeline (committed)
  source/      hand-authored .blend files (committed when they exist)
  generated/   script-produced .blend files (regenerable)
  exports/     FBX / GLB written by af_export.py (regenerable)
  reports/     JSON + text reports written by the pipeline
  local/       machine-specific scratch, git-ignored
```

`source/` is never cleared by a script. `generated/`, `exports/` and `reports/`
are treated as reproducible output.

---

## 3. Scripts

| Script | Responsibility |
| --- | --- |
| `af_pipeline_config.py` | Single source of truth: units, axes, bone list, design dimensions, naming patterns, tolerances, export settings, paths. Every other script imports it and hardcodes nothing. Runnable standalone as a self-check. |
| `af_scene_setup.py` | Metric units, scale length, the nine owned `AF_*` collections. Clears only collections it owns; refuses anything else. |
| `af_vehicle_generate.py` | Builds the placeholder blockout: body, four wheels, four suspension arms, UCX collision, three LOD levels. Geometry is authored in world space so object transforms stay at identity. |
| `af_vehicle_rig.py` | Creates the eleven-bone armature and binds meshes rigidly — exactly one vertex group per mesh at weight 1.0. |
| `af_materials.py` | Creates and assigns placeholder `AF_M_*` materials. Blender-side material work is deliberately minimal; Unreal owns final shading (decision D-011). |
| `af_validate.py` | The twenty-one validation checks from `BLENDER_PIPELINE_DESIGN.md` §4. Reports measured values, in metres **and** centimetres, not assumed ones. |
| `af_export.py` | Selects the export set and writes FBX. Filters `FBX_EXPORT_SETTINGS` against the exporter's actual runtime properties and reports any dropped keys. |
| `af_smoke_test.py` | Runs every stage in order in one Blender session and exits non-zero at the first failure. |

---

## 4. Running

All scripts are designed for Blender's background mode. Run them from this
directory (or any directory — paths are derived from `__file__`, never
absolute).

```bat
:: full pipeline, the normal entry point
blender --background --python scripts/af_smoke_test.py

:: individual stages, in dependency order
blender --background --python scripts/af_scene_setup.py
blender --background --python scripts/af_vehicle_generate.py
blender --background --python scripts/af_vehicle_rig.py
blender --background --python scripts/af_materials.py
blender --background --python scripts/af_validate.py
blender --background --python scripts/af_export.py
```

Individual stages operate on the *current* Blender session's scene. Running
them one at a time from separate `--background` invocations will not accumulate
state — each invocation starts from an empty scene. To run stages separately
against persistent state, open a `.blend` file first:

```bat
blender generated\AF_Vehicle_Proto.blend --background --python scripts\af_validate.py
```

`af_smoke_test.py` exists precisely so that the normal case is one session.

The config module is the only script that is useful outside Blender:

```bat
python scripts\af_pipeline_config.py
```

It prints the effective configuration, the config hash, and runs its internal
consistency self-check.

---

## 5. Exit codes

| Code | Meaning |
| --- | --- |
| `0` | Success. Everything the script was asked to do completed. |
| `1` | Validation ran and one or more checks **failed** (`af_validate.py` only). The scene is intact; the report lists what failed. |
| `2` | `bpy` was unavailable — the script was run under plain Python instead of Blender. **Nothing was done. Do not read this as a result.** |
| `3` | The script ran inside Blender and failed: an exception, a config self-check failure, or a missing prerequisite. |

`af_smoke_test.py` returns `3` if any stage fails, and stops at the first
failure rather than running later stages against a broken scene.

These codes make the pipeline usable as a build gate: a non-zero exit is always
a real problem, and `2` is distinguishable from `1` and `3` so a
mis-invocation is never mistaken for a content failure.

---

## 6. What is verifiable without Blender

Several helpers are deliberately written free of `bpy` so they can be tested in
plain Python:

| Function | Module |
| --- | --- |
| `box_mesh`, `cylinder_mesh`, `merge_meshes`, `body_parts`, `suspension_arm_parts` | `af_vehicle_generate` |
| `bone_head_m`, `bone_tail_m`, `bone_layout`, `binding_plan` | `af_vehicle_rig` |
| `slot_plan` | `af_materials` |
| everything except the path constants | `af_pipeline_config` |

This is intentional: the further geometry and rig maths can be pushed out of
`bpy`-dependent code, the more of the pipeline can be checked before Blender is
ever opened.

---

## 7. Rules this pipeline follows

- Repeatable — rerunning produces the same result, not a duplicate.
- Non-destructive outside owned `AF_*` collections. `clear_collection()` raises
  rather than touching anything it does not own.
- No pip dependencies. Standard library plus `bpy` only.
- Project-relative paths, always derived from `__file__`.
- Deterministic report filenames — no timestamps in names, so reruns overwrite
  cleanly and Git diffs show what actually changed (decision D-023).
- Source is separate from generated output.
- Execution results are never fabricated. A report file exists only if a run
  produced it.

---

## 8. What Was Actually Measured

The pure, `bpy`-free helpers in these scripts were exercised by an offline
harness outside Blender. The harness is a development tool and is not part of
the deliverable, but the numbers below are its output, not estimates.

**47 checks, 0 failures.**

Body blockout bounding box, computed from the merged part meshes:

| Axis | Measured | Measured (cm) | Design maximum |
| --- | --- | --- | --- |
| Length (X) | 5.600 m | 560.0 cm | 5.600 m |
| Width (Y) | 1.900 m | 190.0 cm | 2.000 m |
| Height (Z) | 0.929 m | 92.9 cm | 0.950 m |

Wheel bone head positions from `bone_layout()`:

| Bone | Measured | Measured (cm) |
| --- | --- | --- |
| `AF_Wheel_FL` | (1.800, 0.800, 0.360) m | (180.0, 80.0, 36.0) cm |
| `AF_Wheel_FR` | (1.800, −0.800, 0.360) m | (180.0, −80.0, 36.0) cm |
| `AF_Wheel_RL` | (−1.800, 0.770, 0.380) m | (−180.0, 77.0, 38.0) cm |
| `AF_Wheel_RR` | (−1.800, −0.770, 0.380) m | (−180.0, −77.0, 38.0) cm |

Also measured: 11 bones in exactly `BONE_ORDER` with no leaf or extra bones;
every bone length exactly 0.200 m / 20.0 cm; every parent matching
`BONE_PARENTS` with the root's parent `None`; wheel cylinder rim radius correct
to within 1.11 × 10⁻¹⁶ m; merged body mesh 176 vertices / 132 faces with all
face indices in range; `binding_plan()` binding 9 meshes to deform bones only,
with nothing bound to `AF_Root` or `AF_Steering`; `slot_plan()` covering 12
meshes with purposes drawn only from the configured set.

These numbers describe the geometry the scripts *compute*. They do not
describe a Blender scene, because no Blender scene has been built.

---

## 9. Verification Ledger

| Claim | Status |
| --- | --- |
| Eight scripts exist with the responsibilities listed in §3 | `statically inspected` |
| All eight compile under Python 3.12 | `automatically validated` |
| Config self-check passes | `automatically validated` |
| The measured values in §8 are the helpers' real output | `automatically validated` |
| The body blockout fits inside the design envelope | `automatically validated` |
| The bone list matches the config exactly, with no leaf bones | `automatically validated` |
| No script hardcodes a bone name, unit, axis, modifier name or path outside the config | `automatically validated` — verified by an automated sweep, not by reading |
| The token `F1` appears nowhere in the pipeline as a name | `automatically validated` — word-boundary scan across all eight scripts |
| A scene built by these scripts passes all 21 checks | `requires Blender execution` |
| The exported FBX contains exactly 11 bones and no leaf bones | `requires Blender execution` |
| The FBX imports into Unreal Engine 5.8 with correct scale and orientation | `requires Unreal Editor verification` |
| The blockout resembles a formula car | `requires visual inspection` |
