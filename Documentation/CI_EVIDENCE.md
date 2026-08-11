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

The `Static validation` job also carries the explicit **execution** steps —
the lap rules model self-test, the drift guard self-test, the drift guard
itself, and the circuit generator self-test. None of them carry
`continue-on-error`. They exist as separate steps because the `compileall`
step byte-compiles every script and executes none of them; without a
dedicated step a self-test would compile cleanly and prove nothing.

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

## 3A. What the drift guard proves

`automatically validated`. Added by **D-044**, recorded in full in
`MILESTONE_3_IMPLEMENTATION.md` §6A. Merged as
`bf602b2c053fb886a0d83741d4e6f8c51b6003dd` (PR #10).

Two steps run inside `Static validation`, in this order, neither with
`continue-on-error`:

```yaml
- name: Drift guard self-test
  run: python3 Tools/af_drift_guard.py --self-test

- name: Drift guard (C++ / Python parity)
  run: python3 Tools/af_drift_guard.py --root . --verbose
```

`Tools/af_drift_guard.py` (38,557 bytes, standard library only, Python 3.9
compatible) reads the C++ sources and `Tools/af_lap_rules_model.py` **as
text** and fails the job when they disagree on:

| Check | Compares |
|---|---|
| A — enum parity | `EAFLapInvalidationReason` in `AFTypes.h` against `LapInvalidationReason` in the model — membership **and** order |
| B — method surface | `Class::Method` definitions in `AFSectorTimer.cpp` / `AFLapValidator.cpp` against `def` names in the mirrored Python classes |
| C — behavioural rules | 16 named rules (R-01…R-16), each asserting a specific construct is present on both sides |

The Python side is parsed with `ast`, never `exec`, so validating the model
can never execute it as a side effect. Exit codes: `0` parity holds, `1`
drift detected, `2` a source is missing or the invocation is wrong — `2` is
distinct from `1` on purpose, because a guard that cannot find its inputs
must not be mistaken for a guard that found nothing wrong.

### Why this is believed to work

Three levels, in increasing strength:

1. The guard passes against the current repository. On its own this proves
   nothing — a guard that returns `0` unconditionally also passes.
2. Its self-test passes: **31 cases over 17 methods**, locally and in CI.
3. **11 mutation tests** corrupt a copy of each input — remove an enum
   member, reorder the enum, rename a method, delete a rule construct on one
   side — and assert the guard exits non-zero. Only this level distinguishes
   a working guard from a decorative one.

### What it does not prove

- **Nothing about compilation.** The guard reads text. A file can be
  parity-correct and still fail to build. `not claimed` is unchanged.
- **Not semantic equivalence.** Parity is proven on the enum, on the method
  surface, and on sixteen named rules. That is a subset. A change touching
  none of the three can still drift silently.
- **Not the circuit mirror.** `validate_track_definition()` versus
  `UAFTrackDefinition::ValidateSelf()` (D-043 decision B) has the same drift
  exposure and **no** guard. Open gap.
- **Not observed at step level.** See §6.

---

## 4. The defects and defect classes CI has addressed so far

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

**D-044 — a defect class, caught before it occurred.** D-041 was one instance
of a general shape: the same fact written twice, in two files, kept in
agreement by attention. D-042 and D-043 each deliberately created another
instance of that shape in exchange for executable evidence. No drift defect
has actually been observed in the lap rules mirror — the guard was added
because the failure mode is **silent**, and a silent failure of an evidence
mechanism is worse than having no mechanism. This entry is recorded here for
symmetry with D-040 and D-041, with the distinction stated rather than
blurred: those two were found, this one was pre-empted.

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

### Check runs are readable at job level only

This is a hard limitation of the tooling used here and it constrains every
step-level claim in this repository.

What is retrievable per check run: `name`, `status`, `conclusion` and an
`html_url`. **Step-level logs are not retrievable.** So a sentence such as
"the drift guard ran on the runner" is an **inference** from three facts —
the step exists in the committed workflow, it carries no
`continue-on-error`, and the job it belongs to concluded `success`. A
non-zero exit from that step would have failed the job, so the inference is
sound. It is still an inference, not a log reading, and documents in this
repository must not upgrade it to one.

A second consequence: post-merge, the only mechanical evidence available is
the merge commit's own diff. An **additions-only** diff on a file is
therefore treated as meaningful, because `.github/workflows/validate.yml`
was once silently truncated by roughly 900 bytes and had to be restored in
PR #7.

---

## 6A. Milestone 3 pull request evidence

| PR | Contents | Merge commit | Diff |
|---|---|---|---|
| #5 | `Tools/af_lap_rules_model.py` (68 cases) + workflow step | `7ec380e14fe315a245a4898c79dee3c7aef0650b` | — |
| #6 | `Documentation/MILESTONE_3_IMPLEMENTATION.md` | `6b8038fa05fd5a6a40e2fc1dbf7ef6febbfa5e1a` | — |
| #7 | `af_circuit_generate.py` (84 cases), workflow step, workflow restore | `7617a530392d155039a4ea81e5ed032f0b0f3d3f` | — |
| #10 | `Tools/af_drift_guard.py` (31 cases, 11 mutation tests) + two workflow steps | `bf602b2c053fb886a0d83741d4e6f8c51b6003dd` | 2 files, **+1132 / −0** |

**PR #10 detail.** Every distinct check name concluded `success`. Workflow
runs observed: `31513676365`, `31513676386`, `31513773974`, `31513774193`.
Each check name appears twice because push and pull-request triggers create
parallel runs with identical job names; the merge criterion applied was
**every distinct check name green**, not a run count.

The diff is additions-only: `Tools/af_drift_guard.py` +1113 (new file) and
`.github/workflows/validate.yml` +19 (modified). Zero deletions on the
workflow is direct evidence the PR #7 truncation class of bug did not recur.

Post-merge blob verification on `main`:

| Path | Blob SHA | Bytes |
|---|---|---|
| `Tools/af_drift_guard.py` | `a296588c8f2068232d1f02782ab88f5da945b847` | 38,557 |
| `.github/workflows/validate.yml` | `f69ff898294292456d7b8404b5a1cd342d82ef26` | 7,652 |

The guard blob SHA equals the Git blob SHA computed locally over the exact
bytes that passed the self-test before the push, so the file CI executed is
byte-identical to the file that was verified.

Job duration is recorded elsewhere for completeness only and is **not**
evidence of anything.

---

## 7. Verification ledger

| Claim | Label |
|---|---|
| Five jobs run on push, pull request and dispatch | `statically inspected` |
| Blender 5.2.0 LTS downloads and executes headless on the runner | `automatically validated` |
| All seven smoke-test stages pass | `automatically validated` |
| The generated placeholder is 132 polygons, 176 vertices, 11 bones | `automatically validated` |
| Bone order matches the configured order; 9 meshes bound | `automatically validated` |
| The drift guard's own self-test passes (31 cases, 17 methods) | `automatically validated` |
| The drift guard fails on corrupted input (11 mutation tests) | `automatically validated` |
| `EAFLapInvalidationReason` and the Python mirror agree on membership and order | `automatically validated` |
| The two implementations are semantically equivalent beyond the 16 checked rules | `not claimed` |
| `validate_track_definition()` matches `UAFTrackDefinition::ValidateSelf()` | `not claimed` |
| Any individual CI **step** was observed executing | `not claimed` — job level only, see §6 |
| FBX exporter option drops | `not claimed` |
| Blender behaves the same on the pinned Windows workstation | `not claimed` |
| Any C++ in this repository compiles | `not claimed` |
| The exported FBX imports into Unreal with matching bone names | `requires Unreal Editor verification` |
| The vehicle drives | `requires playtesting` |
