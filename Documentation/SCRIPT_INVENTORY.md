# Script Inventory

Status: **statically inspected** (this document), citing **automatically validated** evidence.
Created by: **D-066**.
Scope: every `af_*.py` script in the repository as of commit `2b9a909e2549267ffa950a3415c8648b01d662b7`.

---

## 1. Why this document exists

`VERSION_MATRIX.md` §5.20 says the Blender pipeline consists of "the eight scripts".
That sentence was written by commit `0b82ed31` on 2026-08-10T15:49:33Z. It was accurate
for about seven minutes. `af_pipeline_config.py` landed at 15:56:11Z the same day, and
three more scripts followed during Milestones 3 and 4. The pipeline directory now holds
twelve scripts, not eight.

D-065.4 established that this is **stale scope, not a miscount** — nobody counted wrong,
the sentence simply was never revisited. OPEN-065-B was opened to record the real set
somewhere durable. This file is that record.

It also answers a question the repository could not previously answer in one place:
**for each script, what has actually been executed against it?** Not "what is it for" —
what has *run*.

---

## 2. Method and its limits

The execution column is not inferred from file names, docstrings, or intent. It is read
from three primary sources, each read in full:

| Source | Size | What it proves |
|---|---|---|
| `.github/workflows/validate.yml` | 19,229 B | Which scripts CI invokes directly, and in what order |
| `.github/workflows/static-validation.yml` | 2,386 B | The Python 3.9 / 3.12 matrix job and the byte-compile job |
| `BlenderPipeline/scripts/af_smoke_test.py` | 10,774 B | Which modules are driven as function calls inside Blender |

Self-test case counts are quoted only where they appear **verbatim in a commit message**
or **verbatim in a workflow comment**. Where no such figure exists, the cell says so.

**Hard limits on this document:**

1. **Nothing in this repository was executed in the environment that produced this file.**
   No Python interpreter was run, no Blender session opened, no Unreal project loaded.
   Every execution claim here is attributed to GitHub Actions or to a cited commit.
2. "Invoked by CI" means a workflow step names the script. It does **not** mean the most
   recent run of that workflow was green. Green-run evidence lives in `CI_EVIDENCE*.md`,
   which records 115 green check runs across six volumes; this file does not restate it.
3. The Blender job resolves the newest `blender-5.2.x-linux-x64.tar.xz` from
   `download.blender.org` **at run time**. The exact Blender build behind any past green
   run is therefore not recoverable from the repository alone.
4. Byte sizes are the live values reported by the GitHub contents API at the commit named
   above. They are not measured on a local checkout.

---

## 3. How CI invokes scripts

Two workflows exist. Both must be read to see the whole picture — neither alone is complete.

### 3.1 `static-validation.yml` — job `validate`, matrix Python **3.9 and 3.12**

3.9 is the documented floor declared inside `af_static_validate.py`; the matrix exists to
hold that floor honestly rather than assert it.

```
python Tools/af_static_validate.py --root .
python Tools/af_validate_interfaces.py --self-test
python Tools/af_validate_interfaces.py --root .
```

The self-test runs **before** the checker runs for real — that ordering is D-030's rule:
a checker that has not proved it can detect a defect is not evidence of anything.

### 3.2 `static-validation.yml` — job `syntax`, Python **3.11**

Byte-compiles `Tools`, then — guarded by a directory-existence check —
`BlenderPipeline/scripts`. This is the only place several pipeline scripts are touched
by CI at all.

### 3.3 `validate.yml` — job `static-validation`, Python **3.12**, stdlib only

No `pip install` step exists, by design: every script in this job must run against a bare
interpreter. Steps, in order:

| # | Command |
|---|---|
| 1 | `python3 Tools/af_static_validate.py --root .` |
| 2 | `python3 BlenderPipeline/scripts/af_pipeline_config.py` |
| 3 | `python3 Tools/af_lap_rules_model.py --self-test` |
| 4 | `python3 Tools/af_drift_guard.py --self-test` |
| 5 | `python3 Tools/af_drift_guard.py --root . --verbose` |
| 6 | `python3 BlenderPipeline/scripts/af_circuit_generate.py --self-test` |
| 7 | `python3 Tools/af_track_drift_guard.py --self-test` |
| 8 | `python3 Tools/af_track_drift_guard.py --root . --verbose` |
| 9 | `python3 Tools/af_config_hash_guard.py --self-test` |
| 10 | `python3 Tools/af_config_hash_guard.py --root . --verbose` |
| 11 | `python3 Tools/af_mesh_quality.py --self-test` |
| 12 | `python3 Tools/af_mesh_quality.py` |
| 13 | `python3 BlenderPipeline/scripts/af_bodywork_profile.py --self-test` |
| 14 | `python3 BlenderPipeline/scripts/af_mesh_export.py --self-test` |
| 15 | export determinism gate: `--dump` twice, byte-compared by an inline `python3` heredoc (D-064) |
| 16 | `python3 -m compileall -q BlenderPipeline/scripts Tools` |

Note the pattern in steps 4/5, 7/8, 9/10, 11/12: **self-test first, real run second.**
Four guards follow D-030 rather than one.

### 3.4 `validate.yml` — job `blender-pipeline` (`needs: static-validation`)

`BLENDER_SERIES: '5.2'`. Installs `libgl1 libxi6 libxxf86vm1 libxfixes3 libxrender1
libsm6 libice6`, resolves and unpacks Blender 5.2.x, runs `blender --version`, then:

```
blender --background --factory-startup --python BlenderPipeline/scripts/af_smoke_test.py
```

and uploads `BlenderPipeline/reports`, `exports`, `generated` as artifact
`blender-pipeline-output`. `--factory-startup` matters: no user preferences, no add-ons,
no local state can influence the result.

Exit codes, per `BlenderPipeline/README.md` §5 and confirmed by the constants in
`af_smoke_test.py` (`EXIT_OK = 0`, `EXIT_NO_BPY = 2`, `EXIT_FAILED = 3`):

| Code | Meaning |
|---|---|
| 0 | all stages passed |
| 1 | validation failure |
| 2 | `bpy` unavailable — **not** a pipeline result |
| 3 | a stage failed |

### 3.5 What `af_smoke_test.py` drives

This is the missing link. Six pipeline scripts are named by **no** workflow step, yet are
exercised under Blender, because the smoke test imports them and calls their entry points
inside a **single Blender session** — one scene, real state passed between stages, not
seven subprocesses. Its `STAGES` tuple, read verbatim:

| Stage | Module | Entry point called |
|---|---|---|
| 1. scene setup | `af_scene_setup` | `setup_scene()` |
| 2. generate geometry | `af_vehicle_generate` | `generate_all()` |
| 3. rig | `af_vehicle_rig` | `rig_all()` |
| 4. materials | `af_materials` | `apply_all()` |
| 5. validate (pre-export) | `af_validate` | `validate()` |
| 6. export FBX | `af_export` | `export_all()` |
| 7. validate (post-export) | `af_validate` | `validate()` again |

`af_pipeline_config` is imported at module scope as `cfg`, and `main()` refuses to run the
pipeline at all if `cfg.self_check()` fails. The run stops at the first failing stage —
later stages would test nothing meaningful against a broken scene.

**`af_validate` runs twice on purpose**: the same checks before export and after, so an
exporter that mutates the scene cannot hide. The docstring puts that check count at 21.

---

## 4. The inventory — `Tools/` (7 scripts)

All seven are invoked directly by CI. This directory has no unexercised script.

| Script | Bytes | Created by | Date (UTC) | Origin | What has actually been executed |
|---|---|---|---|---|---|
| `af_static_validate.py` | 52,702 | `1c2a6e52` | 2026-08-10T18:01:42Z | M1 | Invoked by **both** workflows — `--root .` on py3.9, py3.12 and (as a step-1 gate) in `validate.yml`. Its commit records **2300 checks, 0 failures, 0 warnings, exit 0**, and a mutation test under D-030: **11 injected defects, 11 detected**, plus a negative control. |
| `af_validate_interfaces.py` | 17,155 | `2e4bde3c` | 2026-08-11T13:40:47Z | M2 (PR #3), D-037 | `--self-test` then `--root .`, on **py3.9 and py3.12**. Commit records **9 self-test cases green on both**. Only `static-validation.yml` runs it — it is absent from `validate.yml`. Renamed by `f1cea387` (9 occurrences). |
| `af_lap_rules_model.py` | 30,250 | `7ec380e1` | 2026-08-11T14:22:41Z | M3 (PR #5) | `--self-test` (step 3). Stdlib mirror of `UAFSectorTimer` / `UAFLapValidator`; commit records a **68-case self-test**. Rename `62477469` (+8 B) left all 68 `AF_CP_` assertions untouched. |
| `af_drift_guard.py` | 38,569 | `bf602b2c` | 2026-08-11T16:43:55Z | D-044 | **Two** non-optional steps: `--self-test` and `--root . --verbose`. Checks enum parity, API parity and a **16-entry rule parity table** against the C++ source. Rename `baa6427b` (+8 B, 38,557 → 38,565) — the first file to bind **two** modules at once. |
| `af_track_drift_guard.py` | 30,180 | `a77dcd50` | 2026-08-11T17:26:55Z | D-045 (PR #12) | Two steps, as above. Commit records `--self-test` **27 cases / 0 failed**; `--root .` → **16 templates / 16 predicate pairs / 11 field-key pairs, exit 0**; and **five negative mutations, each exit 1**. Caution: `5fb08f20`'s message overstated the CI wiring; `99cf8078` is the commit that actually wired it. |
| `af_config_hash_guard.py` | 26,519 | `5faa2d98` | 2026-08-11T18:15:10Z | D-046 (PR #15) | Two steps. Commit records a **44-case self-test across 27 methods, 0 failed**; clean tree exit 0; a `wheelbase_m 3.600 → 3.601` mutation exit 1. Canonical blob **3,484 bytes**, SHA-256 begins `c9ef9f7e985a1aaf`. Fix `722f6164` restored a step that had been wrongly prefixed with `--self-test &&`. |
| `af_mesh_quality.py` | 30,783 | `ed691f90` | 2026-08-11T19:06:06Z | D-047 | Two steps: `--self-test` (**46 tests**) and the real audit (**274 checks / 274 passed, exit 0**), covering criteria C0–C12. The audit **imports `af_vehicle_generate`**, so that module's geometry code executes under plain CPython here — the only place it does. Found the inward-winding defect later fixed by `f4c19f9`. |

---

## 5. The inventory — `BlenderPipeline/scripts/` (12 scripts)

Five are invoked directly by a workflow step. Six more are driven by `af_smoke_test.py`
under Blender. One is exercised by nothing.

| Script | Bytes | Created by | Date (UTC) | Origin | What has actually been executed |
|---|---|---|---|---|---|
| `af_pipeline_config.py` | 30,922 | `5e6e230d` | 2026-08-10T15:56:11Z | M0B | **Directly invoked** (step 2) as a self-check. Also imported by `af_config_hash_guard`, `af_mesh_quality` and `af_smoke_test` — the most-exercised module in the repository. Landed **7 minutes after** §5.20's "eight scripts" sentence was written. |
| `af_circuit_generate.py` | 43,731 | `7617a530` | 2026-08-11T14:44:07Z | M3, criterion 5 | **Directly invoked**: `--self-test` (step 6). Also the text-comparison target of `af_track_drift_guard`. Grew 42,975 → 43,731 (+756) at `163f9b9b`. |
| `af_bodywork_profile.py` | 42,219 | `a09728e8` | 2026-08-11T23:51:24Z | M4 slice 1 | **Directly invoked**: `--self-test` (step 13). `validate.yml` states honestly that the **42-case suite on branch `milestone-4-bodywork` is still outstanding** — the CI step exercises the config-free half only. |
| `af_mesh_export.py` | 23,654 | `b5b935f8` | 2026-08-12T00:42:38Z | M4 slice 3 | **Directly invoked** twice over: `--self-test` (step 14, **21 cases** per the workflow comment) and then `--dump` **twice** in step 15, whose outputs are byte-compared to prove export determinism (D-064). That comparison was also measured by hand once: **26 files, 112123 bytes**, identical across two runs. |
| `af_smoke_test.py` | 10,774 | `1b6e050c` | 2026-08-10T15:47:25Z | M0B | The **only** script executed under a real Blender: `blender --background --factory-startup --python …` in the `blender-pipeline` job. Orchestrates the seven stages in §3.5. Its own docstring is blunt: *"this orchestration has NOT been run inside Blender. Its structure is 'statically inspected'; every claim about what it produces is 'requires Blender execution'."* That disclaimer predates the CI job and has not been revised — see §6. |
| `af_scene_setup.py` | 8,534 | `f2a16792` | 2026-08-10 | M0B | Not named by any workflow step. **Driven under Blender** as smoke-test stage 1 via `setup_scene()`; the stage asserts unit system and scale length against config. Otherwise byte-compiled only. |
| `af_vehicle_generate.py` | 22,460 | `d8971634` | 2026-08-10 | M0B | Not named by any workflow step. Two real execution paths: **imported by `af_mesh_quality`** under plain CPython (step 12), and **driven under Blender** as smoke-test stage 2 via `generate_all()`. |
| `af_vehicle_rig.py` | 9,259 | `e7b8468b` | 2026-08-10 | M0B | Not named by any workflow step. **Driven under Blender** as smoke-test stage 3 via `rig_all()`; the stage asserts the produced bone names equal `cfg.BONE_ORDER` exactly. Otherwise byte-compiled only. |
| `af_materials.py` | 6,258 | `38026954` | 2026-08-10 | M0B | Not named by any workflow step. **Driven under Blender** as smoke-test stage 4 via `apply_all()`. Otherwise byte-compiled only. Smallest script in the repository. |
| `af_validate.py` | 28,683 | `69eed3b3` | 2026-08-10 | M0B | Not named by any workflow step. **Driven under Blender twice per run** — smoke-test stages 5 and 7, pre- and post-export, via `validate()`. Docstring puts the check count at **21**. Otherwise byte-compiled only. |
| `af_export.py` | 10,996 | `604bb531` | 2026-08-10 | M0B | Not named by any workflow step. **Driven under Blender** as smoke-test stage 6 via `export_all()`; the stage asserts the FBX exists with non-zero size. Otherwise byte-compiled only. |
| `af_bodywork_selftest.py` | 22,078 | `456031ca` | 2026-08-12T00:20:32Z | M4 | **Exercised by nothing.** No workflow step names it. It is not a smoke-test stage. `compileall` proves only that it parses. See OPEN-066-B. |

---

## 6. Findings

**F-1 — Every `Tools/` script is invoked; one pipeline script is not.**
7 of 7 in `Tools/` run in CI. In `BlenderPipeline/scripts/`, 5 of 12 are named by a
workflow step and 6 more are driven by the smoke test. `af_bodywork_selftest.py`
(22,078 B) is in neither set. A file whose name is `selftest` that no gate ever calls is
the exact shape of a test that silently stops mattering. → **OPEN-066-B**.

**F-2 — `af_validate_interfaces.py` runs in only one of the two workflows.**
It appears in `static-validation.yml` and not in `validate.yml`. That is survivable while
both workflows fire on the same events, and becomes a hole the moment they diverge.
Recorded, not "fixed" — this document does not change CI.

**F-3 — `af_smoke_test.py` still says `ApexFormula`.**
Its module docstring opens `"""ApexFormula - end-to-end pipeline smoke test.` and its
report header writes `"ApexFormula pipeline smoke test"`. Wave 1.5 renamed `Tools/`
scripts; this file was not in that wave. It is also **not** covered by D-051.2's
deliberate lockstep exclusion, which applies only to strings naming
`Unreal/Source/ApexFormulaCore|ApexFormulaRace`. This is an ordinary un-migrated string,
and it is emitted into every generated report. → **OPEN-066-C**.

**F-4 — The smoke test's honesty note may now be out of date, and that is not this
document's call to make.**
The docstring states the orchestration has never been run inside Blender. A CI job now
exists that runs exactly that command. Whether it has ever gone green is a question for
`CI_EVIDENCE*.md`, not for a file-reading exercise. Until someone checks, **the docstring
stands and the pipeline output remains "requires Blender execution"**. The rule is
unchanged: a CI job existing is not a CI job passing.

**F-5 — Four of five guards follow the self-test-first pattern; `af_static_validate.py`
does not.**
`af_drift_guard`, `af_track_drift_guard`, `af_config_hash_guard` and `af_mesh_quality`
each run `--self-test` immediately before their real invocation.
`af_static_validate.py` is invoked directly, with no self-test step. Its mutation
evidence (11/11) lives in a commit message from 2026-08-10, not in a gate that re-proves
it on every run. Recorded as an asymmetry, not asserted to be a defect.

---

## 7. What this document does not claim

- It does **not** claim any of these scripts passed on the most recent CI run.
- It does **not** claim the Blender job has ever completed successfully.
- It does **not** claim any FBX or GLB has been imported into Unreal.
- It does **not** claim Milestone 4 is accepted. It is **not**. Slices 1–3 are implemented
  and CI-green; the sole blocker is OPEN-051-F, the 15-criterion visual acceptance gate,
  8 of whose criteria require Blender 5.2 LTS running on a workstation with the
  face-orientation overlay. **Partial pass = fail.**
- It does **not** revise `VERSION_MATRIX.md` §5.20. That sentence still reads "the eight
  scripts" and still has no pointer here.

---

## 8. Open questions raised by this document

| Id | Question | State |
|---|---|---|
| OPEN-066-A | `af_static_validate.py` has no `--self-test` step in either workflow, unlike the four later guards. Should the D-030 pattern be applied retroactively? | open |
| OPEN-066-B | `af_bodywork_selftest.py` (22,078 B) is invoked by no workflow step and by no smoke-test stage. Wire it, fold it into `af_bodywork_profile --self-test`, or delete it — but do not leave it unexercised. | open |
| OPEN-066-C | `af_smoke_test.py` emits the literal string `ApexFormula` in its docstring and in every generated report header. Not covered by D-051.2's lockstep exclusion. | open |

`OPEN-065-B` is **partially discharged** by this file: the twelve-script record now exists.
It remains **open** with narrowed scope — `VERSION_MATRIX.md` §5.20 still needs a pointer
to this document.

---

## 9. Provenance

| Fact class | Source |
|---|---|
| Byte sizes | GitHub contents API at `2b9a909e2549267ffa950a3415c8648b01d662b7` |
| Creation commits and dates | Per-file commit history via the GitHub commits API |
| CI step lists | `.github/workflows/validate.yml`, `.github/workflows/static-validation.yml`, read in full |
| Smoke-test stage list | `BlenderPipeline/scripts/af_smoke_test.py`, read in full |
| Self-test case counts | Commit messages and workflow comments, quoted verbatim |
| Script counts and the §5.20 discrepancy | D-065.4 |

Recorded under decision **D-066** in `DECISION_LOG_VOL9.md`.
