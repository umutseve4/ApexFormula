# CI Evidence — Volume 3

**Status:** active volume
**Opened:** 2026-08-11
**Predecessors:** `Documentation/CI_EVIDENCE.md` (frozen, 23,864 B) → `Documentation/CI_EVIDENCE_VOL2.md` (frozen at 15,534 B)
**Scope of this volume:** verification batches executed during the *Uludağ Formula* identity migration, wave 2 onwards.

---

## 0. Why a third volume

Volume 2 closed at 15,534 B after recording the two wave-1 documentation batches (PR #17 and PR #18). Appending the two wave-2 batches would have pushed it past the point where a reviewer can read the file in one sitting. The decision logs already follow a volume pattern for the same reason; the evidence files now match it.

Volume 2 is **frozen**. Nothing is edited there except, at most, a one-line pointer to this file.

---

## 1. The acceptance rule used throughout

A batch is accepted only when **all** of the following hold:

1. Every check run reports `conclusion: success`.
2. The batch contains exactly **ten** check runs — the full matrix for this repository.
3. Every run's `started_at` is **later** than the marker commit's author date. This is the anti-staleness rule: it proves the reported runs were triggered by *this* batch and are not a cached earlier result.
4. The verification pull request is **closed unmerged**. Marker commits are disposable scaffolding and must never reach `main`.

The ten runs per batch are always:

| Job | Count |
|---|---|
| `Blender smoke test (headless)` | 2 |
| `Static validation (no engine, no DCC)` | 2 |
| `af_static_validate (py3.9)` | 2 |
| `af_static_validate (py3.12)` | 2 |
| `Python syntax check` | 2 |

Duplication is by design: two workflow files each define an overlapping job set.

---

## 2. Batch 1 — PR #19

| Field | Value |
|---|---|
| Pull request | #19 (draft), id `4257072201` |
| Head branch | `ci/wave2-verify-1` |
| Base | `main` |
| Marker file | `Documentation/CI_MARKER_WAVE2_1.md` |
| Marker commit | `099c33ea` |
| Marker size | 2,207 B |
| Marker author date | `2026-08-11T21:24:15Z` |
| Job start window | `21:24:19Z` – `21:24:50Z` |
| Result | **10 / 10 success** |
| Disposition | closed unmerged |

Workflow runs: `31537718647`, `31537718652`, `31537743454`, `31537743505`.

### 2.1 Commits covered

| File | Commit | Size | Note |
|---|---|---|---|
| `Documentation/CI_EVIDENCE_VOL2.md` | `2267c6de` | 15,534 B | PR #18 outcome recorded |
| `Documentation/DECISION_LOG_VOL3.md` | `bb9a83e2` | 16,196 B | new volume, carries D-051 |
| `Tools/af_validate_interfaces.py` | `f1cea387` | 17,155 B | +22 B (11 substitutions) |
| `BlenderPipeline/scripts/af_pipeline_config.py` | `86d74ecc` | 30,922 B | +12 B (6 substitutions) |
| `Tools/af_config_hash_guard.py` | `aa5283c7` | 26,519 B | +2 B (1 substitution) |

### 2.2 Verdicts

- **F-2 promoted from reasoned to execution-verified.** `86d74ecc` changed `PROJECT_NAME` to `UludagFormula` inside the pipeline configuration module. The digest guard's check A ran twice in this batch and both runs reported success, which proves the pinned digest did **not** move. The reasoning behind F-2 was that `PROJECT_NAME` sits outside the function that feeds the digest; the batch turned that reasoning into a measurement.
- **No re-pin of the D-046 digest is required.** This was the single largest risk carried into wave 1.5 and it is now closed by execution rather than by argument.
- **OPEN-051-C is closed in fact by this batch.** It was recorded as closed only informally before this volume existed; the record now lives here.
- Three Python modules changed identity strings and every static-validation job stayed green, which is the fourth independent confirmation of finding **F-1**: the copyright rule applies to C++ under `Unreal/Source` only, so Python headers and docstrings are cosmetic and carry no gate.

---

## 3. Batch 2 — PR #20

| Field | Value |
|---|---|
| Pull request | #20 (draft), id `4257254837` |
| Head branch | `ci/wave2-verify-2` |
| Base | `main` |
| Marker file | `Documentation/CI_MARKER_WAVE2_2.md` |
| Marker commit | `2979e8aa` |
| Marker size | 1,403 B |
| Marker author date | `2026-08-11T21:56:06Z` |
| Job start window | `21:56:13Z` – `21:56:34Z` |
| Result | **10 / 10 success** |
| Disposition | closed unmerged |

Workflow runs: `31540169469`, `31540169479`, `31540180395`, `31540180453`.

### 3.1 Job identifiers

| Run | Job | Job id |
|---|---|---|
| `31540180453` | Blender smoke test (headless) | `93940626929` |
| `31540180453` | Static validation (no engine, no DCC) | `93940573793` |
| `31540169479` | Blender smoke test (headless) | `93940592078` |
| `31540169479` | Static validation (no engine, no DCC) | `93940549453` |
| `31540180395` | af_static_validate (py3.9) | `93940573645` |
| `31540180395` | af_static_validate (py3.12) | `93940573573` |
| `31540180395` | Python syntax check | `93940573613` |
| `31540169469` | af_static_validate (py3.9) | `93940553693` |
| `31540169469` | af_static_validate (py3.12) | `93940553726` |
| `31540169469` | Python syntax check | `93940553641` |

Slowest job in the batch: `Blender smoke test (headless)`, 35–48 s.

### 3.2 Commits covered

| File | Commit | Size | Note |
|---|---|---|---|
| `Tools/af_track_drift_guard.py` | `d2afee20` | 30,180 B | +8 B, exactly 4 substitutions |
| `Tools/af_drift_guard.py` | `baa6427b` | 38,569 B | +12 B with only 4 substitutions — investigated below |

### 3.3 Verdict on the byte anomaly

Every identity substitution replaces an 11-character ASCII token with a 13-character one, so a clean rewrite must grow by exactly two bytes per substitution. Six of the seven wave-1.5 rewrites matched that prediction exactly. `af_drift_guard.py` did not: four substitutions predicted +8 B, the API reported +12 B.

Two hypotheses were possible: silent truncation or reformatting somewhere in the write path, or a harmless whitespace/line-ending divergence.

Truncation is excluded. Both `Python syntax check` jobs in this batch compiled the module and reported success; a truncated Python file does not compile. A full re-read of the stored blob additionally confirmed all sixteen rules, all sixteen self-test methods and every path constant were present and unmodified.

**OPEN-052-A is therefore resolved: the delta is cosmetic, with no functional impact.**

### 3.4 The explicit limit of that resolution

A syntax check is **not** a self-test. The workflow compiles the module; it never invokes `--self-test`. Consequently the drift guard's internal assertion count remains unmeasured, and **OPEN-051-B stays open**: the guard's banner claims 27 cases, the documentation claims 31 cases over 17 methods, and a static reading of the dispatcher counts 16 methods emitting 6 + 5 + 4 + 1 + 11 + 4 = 31. The documentation reconciles with the code; the guard's own banner is the outlier. Only an actual self-test run settles it, and that requires an environment this session does not have.

This limitation is recorded deliberately. Reporting the batch as "the guards are verified" would overstate what ten green check runs actually prove.

---

## 4. What four green batches do and do not prove

**Proven by CI:**

- The repository's static structure survives every identity rename shipped so far.
- The `.uproject`, module list, dependency table and copyright rule remain internally consistent.
- The prohibited-token screen is not tripped by *Uludağ Formula* or by `UludagFormula`.
- The digest pinned under D-046 is unchanged.
- Every rewritten Python module still compiles under both 3.9 and 3.12.
- The Blender smoke test still runs headless.

**Not proven by any batch, and not to be described as complete:**

- No C++ has been compiled. The engine is not installed in this environment.
- No Unreal project has been opened.
- No FBX or GLB has been imported.
- No generated mesh has been inspected visually.
- No lap has been driven and no playtest has occurred.
- No guard has had its `--self-test` executed by CI.

Green CI is a structural gate, not an execution gate. The distinction is maintained throughout the milestone documents and is not softened here.

---

## 5. Timing characteristics (four batches, consistent)

| Property | Observed |
|---|---|
| Delay from marker push to first job start | 7 – 28 s |
| Full batch completion | within ~67 s |
| Polling strategy that works | one 55 s wait, then a single read |
| Second poll | only if a run is still in progress, and it must use a varied argument to avoid the harness rejecting an identical repeat call |

---

## 6. Batch index

| Batch | PR | Head branch | Marker commit | Marker date | Result | Volume |
|---|---|---|---|---|---|---|
| doc wave, run 1 | #17 | `ci/doc-wave-verify-2` | `f6de019f` | `20:27:06Z` | 10/10 | VOL2 |
| doc wave, run 2 | #18 | `ci/doc-wave-verify-3` | `219667a4` | `20:38:41Z` | 10/10 | VOL2 |
| wave 2, batch 1 | #19 | `ci/wave2-verify-1` | `099c33ea` | `21:24:15Z` | 10/10 | VOL3 §2 |
| wave 2, batch 2 | #20 | `ci/wave2-verify-2` | `2979e8aa` | `21:56:06Z` | 10/10 | VOL3 §3 |
| wave 2, batch 3 | pending | `ci/wave2-verify-3` | pending | pending | pending | VOL3 §7 |

All four completed pull requests are **closed unmerged**. None of the marker files exist on `main`.

---

## 7. Batch 3 — reserved

Batch 3 will cover the remaining wave-1.5 commits:

- `Tools/af_lap_rules_model.py` — commit `62477469`, 30,250 B, +8 B exact
- `Tools/af_mesh_quality.py` — commit `cc85f950`, 30,783 B, +8 B exact
- `Documentation/VERSION_MATRIX.md` — pending

Until batch 3 returns 10/10 with all job starts later than its marker, those three items are **shipped but unverified**. Wave 1.5 does not close before then.

---

*Volume 3 opened after volume 2 reached its practical size ceiling. Records are appended in batch order and are not rewritten once accepted.*
