# Continuous Integration — what it proves

Status of this document: `statically inspected`, except where a line is
labelled otherwise.

Other documents in this repository cite CI as evidence. This page says what
that evidence actually is, so that a reader does not have to infer the scope
of a claim from a green tick.

---

## 1. Jobs that run

Defined in `.github/workflows/`. Both workflows trigger on push to `**`, on
pull request, and on manual dispatch.

| Job | Workflow | Runner | What it executes |
|---|---|---|---|
| `Static validation` | `static-validation.yml`, `validate.yml` | ubuntu-latest, py3.12 | `Tools/af_static_validate.py` over the repository tree |
| `af_static_validate (py3.9)` | `static-validation.yml` | ubuntu-latest, py3.9 | same checker, oldest supported interpreter |
| `af_static_validate (py3.12)` | `static-validation.yml` | ubuntu-latest, py3.12 | same checker, newest supported interpreter |
| `Python syntax check` | `static-validation.yml` | ubuntu-latest | `compileall` over every `.py` in the repository |
| `Blender smoke test (headless)` | `validate.yml` | ubuntu-latest, Blender 5.2 LTS | `blender --background --factory-startup --python BlenderPipeline/scripts/af_smoke_test.py` |

The Blender job declares `needs: static-validation`, so a static failure
short-circuits it and the smoke test does not run at all.

---

## 2. What the Blender job proves

`automatically validated`. The job downloads Blender 5.2 LTS from
`download.blender.org`, resolving the point release by listing the series
directory and taking the highest match rather than hard-coding a filename, then
runs the seven-stage smoke test with `--factory-startup` so that no user
preference, no add-on and no saved startup file can influence the result.

Seven stages run in order, and the harness stops at the first failure so that
later stages cannot report success against a scene that was never built:

1. scene setup — collections, unit system, orphan purge
2. generate geometry — body, wheels, suspension, collision hulls, LODs
3. rig — armature, bone count, bone order, mesh binding
4. materials — placeholder slot assignment
5. validate (pre-export) — 21 checks
6. export
7. validate (post-export)

Exit codes: `0` success, `1` validation failure, `2` bpy unavailable,
`3` run failed.

### What it does not prove

- **Nothing about Unreal.** Blender executing says nothing about whether the
  C++ compiles, whether the FBX imports, or whether the imported skeleton
  matches `UAFBoneNameMap`. Those remain `requires Unreal Editor verification`.
- **Nothing about the Windows workstation.** The pinned development machine is
  Windows; the runner is Ubuntu. The twelve version-sensitive areas in
  `VERSION_MATRIX.md` section 4 that concern Blender did not trigger *on this
  runner, on this build*. They are not retired.
- **Nothing about exporter option drops.** Post-export validation passes, and
  the exporter did not reject the call, but the printed list of dropped or
  renamed FBX options has never been read out of a job log. That specific claim
  stays `not claimed`.
- **Nothing about the Milestone 4 vehicle.** The polygon and bone budgets are
  confirmed for the Milestone 0B placeholder only — 132 polygons, 176 vertices,
  11 bones. The production budget is untested.

---

## 3. What the static jobs prove

`automatically validated`. `af_static_validate.py` enforces the repository's
own conventions: the exact copyright line as line 1 of every C++ file,
`#pragma once`, module API macro containment, `.generated.h` ordering, the
originality token blacklist, containment of engine vehicle types to
`AFVehicleCompatibilityLayer.{h,cpp}`, and automation test naming and placement.

`Tools/af_validate_interfaces.py` additionally checks that every interface
method a class claims to implement matches the interface's declared return
type and signature. It carries an embedded `--self-test` with nine cases and
was mutation-tested before being trusted.

### What they do not prove

These are text checks. **No C++ in this repository has ever been compiled.**
A file can satisfy every rule above and still fail to build.

---

## 4. The two defects CI has caught so far

Recorded in full in `DECISION_LOG.md` and `VERSION_MATRIX.md` section 5.33.

**D-040 — halo apex breached the design envelope.** Stage 5 check 17 measured a
world-space Z extent of 0.97415 m against `overall_height_m` 0.950 m with a
tolerance of 0.010 m — a delta of +0.02415 m. X measured 5.60000 m exactly and
Y measured 1.94000 m, both inside the envelope, so this was a height defect and
not, as first guessed, a length defect. The halo arc height is now solved from
the envelope rather than scaled from the halo radius, and the apex lands at
0.94000 m, which is `overall_height_m` minus `HALO_APEX_CLEARANCE_M` of 0.010.
`check_design_envelope()` now runs before `bpy` is touched, so the same class of
defect fails fast and without a Blender session.

**D-041 — the Unreal and Blender dimension tables disagreed.**
`UAFVehicleDefinition` carried `OverallLengthM` 5.30 and `RearTrackM` 1.55
while `af_pipeline_config.py::DESIGN` carried 5.60 and 1.54. The Blender config
is now named the single source of truth, the Unreal values were corrected to
follow it, and `DataVersion` was bumped to 2. This conflict was static and had
been sitting in the tree unnoticed; CI did not detect it, a human reading the
CI output did.

---

## 5. A retracted hypothesis, kept on the record

When the Blender job first failed, the working hypothesis was that Blender 5.2
did not exist on `download.blender.org` and that the pin should be moved back to
4.x. **That hypothesis was wrong.** The job log opens with
`Blender 5.2.0 LTS (hash fbe6228777e7 built 2026-07-14 01:32:04)`. Blender 5.2
LTS exists, downloads and runs. The pin was correct and was not changed.

The reasoning error is worth naming: job *duration* was treated as evidence of
where the failure occurred. It is not. The same passing job has run in 36
seconds and in roughly 8 minutes, depending on runner cache state.

This is recorded rather than deleted, per the project's honesty rules.

---

## 6. How a commit's status is observed

`statically inspected`. Check runs are read per pull request. There is no
lookup by bare commit SHA in the tooling used here, and the combined status
endpoint reports `pending` with `total_count: 0` on this repository even when
every job has succeeded, so it must not be used as a signal.

The practical consequence: a commit pushed directly to `main` outside a pull
request has an **unobserved** status until something opens a pull request whose
head contains it. Unobserved is not the same as failing, and it is not the same
as green. Documents in this repository must say which one they mean.

---

## 7. Verification ledger

| Claim | Label |
|---|---|
| Five jobs run on push, pull request and dispatch | `statically inspected` |
| Blender 5.2.0 LTS downloads and executes headless on the runner | `automatically validated` |
| All seven smoke-test stages pass | `automatically validated` |
| The generated placeholder is 132 polygons, 176 vertices, 11 bones | `automatically validated` |
| Bone order matches the configured order; 9 meshes bound | `automatically validated` |
| FBX exporter option drops | `not claimed` |
| Blender behaves the same on the pinned Windows workstation | `not claimed` |
| Any C++ in this repository compiles | `not claimed` |
| The exported FBX imports into Unreal with matching bone names | `requires Unreal Editor verification` |
| The vehicle drives | `requires playtesting` |
