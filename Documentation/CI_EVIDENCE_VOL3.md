# CI Evidence — Volume 3

**Status:** CLOSED by size after section 9. Successor: `Documentation/CI_EVIDENCE_VOL4.md`
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

## 4. What seven green batches do and do not prove

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

## 5. Timing characteristics (seven batches, consistent)

| Property | Observed |
|---|---|
| Delay from marker push to first job start | 5 – 28 s |
| Full batch completion | within ~70 s in six batches, ~100 s in one |
| Polling strategy that works | one 55 s wait, then a single read |
| Second poll | only if a run is still in progress, and it must use a varied argument to avoid the harness rejecting an identical repeat call |

Batch 3 added one observation to this table. Its ten runs arrived in **two triggering waves** rather than one: five runs at the marker push (`22:24:05Z` – `22:24:15Z`) and five more when the pull request itself was opened (`22:27:18Z` – `22:27:26Z`). Both waves are later than the marker date, so the acceptance rule is satisfied, and the total is still exactly ten. The lesson is that the count must be checked against the matrix, not against the number of workflow runs.

Batch 4 added a second observation. All ten runs arrived in a single wave, but the last `Blender smoke test (headless)` job was still `in_progress` at the first read, 55 s after the marker push. The second poll, taken 40 s later with a varied argument, showed it completed. The single 55 s wait is therefore a lower bound rather than a guarantee: a batch may need up to roughly 100 s when the slow job starts late in the wave.

Batch 5 confirmed the corrected model without needing the second poll. Its slow job started 32 s after the marker and finished 70 s after it, which still fell inside the 55 s wait plus the round trip of the read call. The rule stands as written: poll once, reject any reading that contains an `in_progress` run, and only then wait again.

---

## 6. Batch index

| Batch | PR | Head branch | Marker commit | Marker date | Result | Volume |
|---|---|---|---|---|---|---|
| doc wave, run 1 | #17 | `ci/doc-wave-verify-2` | `f6de019f` | `20:27:06Z` | 10/10 | VOL2 |
| doc wave, run 2 | #18 | `ci/doc-wave-verify-3` | `219667a4` | `20:38:41Z` | 10/10 | VOL2 |
| wave 2, batch 1 | #19 | `ci/wave2-verify-1` | `099c33ea` | `21:24:15Z` | 10/10 | VOL3 §2 |
| wave 2, batch 2 | #20 | `ci/wave2-verify-2` | `2979e8aa` | `21:56:06Z` | 10/10 | VOL3 §3 |
| wave 2, batch 3 | #21 | `ci/wave2-verify-3` | `82c143cb` | `22:24:00Z` | 10/10 | VOL3 §7 |
| wave 2, batch 4 | #22 | `ci/wave2-verify-4` | `5961d95b` | `22:39:47Z` | 10/10 | VOL3 §8 |
| wave 2, batch 5 | #23 | `ci/wave2-verify-5` | `49c93957` | `23:02:47Z` | 10/10 | VOL3 §9 |

All seven completed pull requests are **closed unmerged**. None of the marker files exist on `main`.

---

## 7. Batch 3 — PR #21

| Field | Value |
|---|---|
| Pull request | #21 (draft), id `4257435914` |
| Head branch | `ci/wave2-verify-3` |
| Base | `main` |
| Marker file | `Documentation/CI_MARKER_WAVE2_3.md` |
| Marker commit | `82c143cb` |
| Marker blob | `ca28e1c9` |
| Marker size | 2,183 B |
| Marker author date | `2026-08-11T22:24:00Z` |
| Job start window | `22:24:05Z` – `22:27:26Z` |
| Result | **10 / 10 success** |
| Disposition | closed unmerged |

Workflow runs: `31542241965`, `31542242010`, `31542476386`, `31542476393`.

### 7.1 Job identifiers

| Run | Job | Job id | Started | Completed |
|---|---|---|---|---|
| `31542241965` | Static validation (no engine, no DCC) | `93947069423` | `22:24:05Z` | `22:24:13Z` |
| `31542242010` | af_static_validate (py3.9) | `93947071183` | `22:24:06Z` | `22:24:22Z` |
| `31542242010` | af_static_validate (py3.12) | `93947071194` | `22:24:06Z` | `22:24:11Z` |
| `31542242010` | Python syntax check | `93947071269` | `22:24:06Z` | `22:24:13Z` |
| `31542241965` | Blender smoke test (headless) | `93947106157` | `22:24:15Z` | `22:24:50Z` |
| `31542476393` | af_static_validate (py3.12) | `93947790941` | `22:27:18Z` | `22:27:25Z` |
| `31542476386` | Static validation (no engine, no DCC) | `93947790310` | `22:27:18Z` | `22:27:24Z` |
| `31542476393` | af_static_validate (py3.9) | `93947790884` | `22:27:19Z` | `22:27:36Z` |
| `31542476393` | Python syntax check | `93947790754` | `22:27:19Z` | `22:27:27Z` |
| `31542476386` | Blender smoke test (headless) | `93947817341` | `22:27:26Z` | `22:28:04Z` |

Earliest start `22:24:05Z` is five seconds after the marker author date, so the anti-staleness rule holds for every run in the batch. Slowest job: `Blender smoke test (headless)`, 35–38 s.

### 7.2 Commits covered

| File | Commit | Blob | Size | Delta |
|---|---|---|---|---|
| `Tools/af_lap_rules_model.py` | `62477469` | `b18635e0` | 30,250 B | +8 B, exactly 4 substitutions |
| `Tools/af_mesh_quality.py` | `cc85f950` | `889cbbdd` | 30,783 B | +8 B, exactly 4 substitutions |
| `Documentation/CI_EVIDENCE_VOL3.md` | `d20d041c` | `cef3ead4` | 9,790 B | new file, no delta to predict |
| `Documentation/VERSION_MATRIX.md` | `edfd74ba` | `8fb657e5` | 40,439 B | +12 B, exactly 3 substitutions |

### 7.3 The byte arithmetic in this batch

Batch 3 is the first to mix the two substitution forms in one batch, and both predictions held exactly.

- The **identifier form** replaces an 11-byte ASCII token with a 13-byte ASCII token: **+2 B per substitution**. Both Python modules matched (4 × 2 = +8 B each).
- The **display form** replaces the same 11-byte token with a 15-byte UTF-8 string — five letters, a two-byte `ğ`, a space, then seven letters: **+4 B per substitution**. `VERSION_MATRIX.md` matched (3 × 4 = +12 B).

This matters because Markdown has **no compile gate**. A truncated Python file is caught by the syntax check; a truncated Markdown file is caught by nothing. For documentation rewrites the byte-delta prediction is the only automated truncation detector available, so it must be computed in UTF-8 bytes and never in characters.

### 7.4 Verdicts

- **Wave 1.5 is now fully CI-verified: seven of seven items shipped and green.** Items 1–3 in batch 1, items 4–5 in batch 2, items 6a, 6b and 7 in batch 3.
- **The lockstep rule survived a negative control.** `af_mesh_quality.py` was measured to contain no module-directory path constants — it locates the generator dynamically — and it renamed cleanly with no companion patch. The rule is therefore specific to the artifacts that hard-code module directory names, not a blanket property of the tools directory.
- **Deliberately retained old-identity strings did not trip any gate.** `af_lap_rules_model.py` still names `Unreal/Source/ApexFormulaRace/Private/...` in its module docstring and `VERSION_MATRIX.md` still carries eight module and file names in sections 5.21, 5.26 and 5.28. All ten runs stayed green, which confirms those strings are safe to carry until their module commit renames them atomically.
- **The inline read and write ceiling is now measured at 40,439 B.** `VERSION_MATRIX.md` was both fetched and rewritten whole through the same channel at that size without truncation.

### 7.5 What batch 3 still does not prove

Nothing in section 4 changes. In particular, `af_mesh_quality.py` was renamed and compiled, but its 46-case self-test was **not** executed by CI, and neither was the drift guard's. OPEN-051-B remains open, and the local rehearsal gate — mesh self-test 46/46 and the 274-check audit at exit 0 — remains the only route to closing it.

---

## 8. Batch 4 — PR #22

| Field | Value |
|---|---|
| Pull request | #22 (draft), id `4257502573` |
| Head branch | `ci/wave2-verify-4` |
| Base | `main` |
| Marker file | `Documentation/CI_MARKER_WAVE2_4.md` |
| Marker commit | `5961d95b` |
| Marker blob | `be954418` |
| Marker size | 1,480 B |
| Marker author date | `2026-08-11T22:39:47Z` |
| Job start window | `22:39:54Z` – `22:40:16Z` |
| Result | **10 / 10 success** |
| Disposition | closed unmerged |

Workflow runs: `31543367878`, `31543367943`, `31543375917`, `31543375920`.

### 8.1 Job identifiers

| Run | Job | Job id | Started | Completed |
|---|---|---|---|---|
| `31543367943` | Static validation (no engine, no DCC) | `93950514962` | `22:39:54Z` | `22:40:04Z` |
| `31543367878` | af_static_validate (py3.9) | `93950521331` | `22:39:56Z` | `22:40:09Z` |
| `31543367878` | af_static_validate (py3.12) | `93950521472` | `22:39:56Z` | `22:40:02Z` |
| `31543367878` | Python syntax check | `93950521405` | `22:39:57Z` | `22:40:05Z` |
| `31543375917` | Static validation (no engine, no DCC) | `93950533826` | `22:40:00Z` | `22:40:07Z` |
| `31543375920` | af_static_validate (py3.9) | `93950533775` | `22:40:00Z` | `22:40:14Z` |
| `31543375920` | af_static_validate (py3.12) | `93950533688` | `22:40:00Z` | `22:40:08Z` |
| `31543375920` | Python syntax check | `93950533782` | `22:40:00Z` | `22:40:04Z` |
| `31543367943` | Blender smoke test (headless) | `93950555044` | `22:40:06Z` | `22:40:41Z` |
| `31543375917` | Blender smoke test (headless) | `93950566548` | `22:40:16Z` | `22:40:57Z` |

Earliest start `22:39:54Z` is seven seconds after the marker author date, so the anti-staleness rule holds for every run. Slowest job: `Blender smoke test (headless)`, 35–41 s.

### 8.2 Commits covered

| File | Commit | Blob | Size | Note |
|---|---|---|---|---|
| `Documentation/DECISION_LOG_VOL3.md` | `0ca1d70f` | `8f12d093` | 25,950 B | D-052 appended, wave 1.5 closure record |
| `Documentation/CI_EVIDENCE_VOL3.md` | earlier on `main` | `a310851b` | — | section 7, batch 3 record |

Both files are Markdown, so neither carries a compile gate. The byte-delta prediction described in section 7.3 was the only automated truncation detector available for this batch, and both files grew by the amount their new sections required.

### 8.3 Why this batch was run at all

The two files above are the closure records for wave 1.5. Every earlier wave-1.5 artifact was verified by batches 1 to 3, but the records *describing* that verification landed on `main` afterwards and were therefore themselves unverified. Batch 4 closes that gap. Without it the migration would carry an unverified tail — a documentation set claiming green status that had never itself passed the gate it describes.

This is a deliberate policy: **every commit on `main` is covered by at least one green batch, including the commits that record the batches.**

### 8.4 A timing correction

The first read of this batch, taken 55 s after the marker push, showed nine runs completed and one `Blender smoke test (headless)` still `in_progress`. A second read 40 s later showed all ten complete. The single-poll strategy in section 5 is therefore a lower bound and not a guarantee. The corrected guidance: poll once at 55 s, and if any run is still in progress, poll again after a further 40 s using a varied argument.

The batch was **not** accepted on the first read. Nine of ten with one in progress is not ten of ten, and accepting it would have violated the rule in section 1.

### 8.5 What batch 4 does not prove

Nothing in section 4 changes. Batch 4 verifies that two Markdown files did not break the static gate. It says nothing about the correctness of their contents, because no automated check reads Markdown prose. The claims inside those documents are only as good as the measurements they cite, and each such claim carries its own evidence pointer for that reason.

---

## 9. Batch 5 — PR #23

| Field | Value |
|---|---|
| Pull request | #23 (draft), id `4257617711` |
| Head branch | `ci/wave2-verify-5` |
| Base | `main` |
| Marker file | `Documentation/CI_MARKER_WAVE2_5.md` |
| Marker commit | `49c93957` |
| Marker blob | `b3e488f5` |
| Marker size | 2,535 B |
| Marker author date | `2026-08-11T23:02:47Z` |
| Job start window | `23:02:52Z` – `23:03:19Z` |
| Result | **10 / 10 success** |
| Disposition | closed unmerged |

Workflow runs: `31544921701`, `31544921709`, `31544936799`, `31544936826`.

### 9.1 Job identifiers

| Run | Job | Job id | Started | Completed |
|---|---|---|---|---|
| `31544921709` | af_static_validate (py3.9) | `93955246396` | `23:02:52Z` | `23:03:06Z` |
| `31544921709` | Python syntax check | `93955246295` | `23:02:53Z` | `23:03:00Z` |
| `31544921709` | af_static_validate (py3.12) | `93955246354` | `23:02:54Z` | `23:03:03Z` |
| `31544936799` | Static validation (no engine, no DCC) | `93955288655` | `23:03:05Z` | `23:03:13Z` |
| `31544921701` | Static validation (no engine, no DCC) | `93955285804` | `23:03:05Z` | `23:03:17Z` |
| `31544936826` | af_static_validate (py3.9) | `93955288819` | `23:03:05Z` | `23:03:18Z` |
| `31544936826` | af_static_validate (py3.12) | `93955288843` | `23:03:05Z` | `23:03:11Z` |
| `31544936826` | Python syntax check | `93955288699` | `23:03:05Z` | `23:03:14Z` |
| `31544936799` | Blender smoke test (headless) | `93955321221` | `23:03:14Z` | `23:03:47Z` |
| `31544921701` | Blender smoke test (headless) | `93955336614` | `23:03:19Z` | `23:03:57Z` |

Earliest start `23:02:52Z` is five seconds after the marker author date, so the anti-staleness rule holds for every run. Slowest job: `Blender smoke test (headless)`, 33–38 s. Total span from marker push to last completion: 70 s.

### 9.2 Commits covered

| File | Commit | Blob | Size | Note |
|---|---|---|---|---|
| `Documentation/CI_EVIDENCE_VOL3.md` | `3a20762b` | `aba2a71d` | 18,896 B | section 8, batch 4 record |
| `Documentation/DECISION_LOG_VOL4.md` | `232bb31c` | `d1eaaae8` | 13,450 B | new volume, carries D-053 |

Both are Markdown and therefore carry no compile gate. Both sizes above were returned by the write call itself and are the only automated truncation signal available for them.

### 9.3 Why this batch was run

Under the policy stated in section 8.3, the commit that records a batch must itself be covered by a later batch. Batch 4 was recorded by `3a20762b`, which no batch had covered. `232bb31c` opened Decision Log Volume 4 with D-053 and was likewise uncovered. Batch 5 covers both, which closes the chain: no commit currently on `main` is unverified.

### 9.4 Confirmation of the corrected timing model

Batch 5 completed inside a single poll. The slow `Blender smoke test (headless)` job started 32 s after the marker and finished 70 s after it, which the 55 s wait plus the read round trip happened to cover. This is consistent with the batch-4 finding rather than a contradiction of it: the 55 s wait is a lower bound that usually suffices and occasionally does not. The corrected procedure in section 8.4 stays in force and is not relaxed on the strength of one favourable sample.

### 9.5 What batch 5 does not prove

Nothing in section 4 changes. In particular, batch 5 verifies that D-053 did not break the static gate; it does not verify a single claim made inside D-053, because no automated check reads Markdown prose. Two of those claims are explicitly negative and remain so: the local rehearsal gate for `Tools/af_mesh_quality.py` is recorded as **NOT MET**, and **OPEN-051-B** — the drift guard's 27-versus-31 self-test count — remains **open**. Neither can be settled by CI, because no workflow invokes any guard's `--self-test` mode.

---

## 10. Volume closure

This volume is **closed by size** at section 9. Batch 6 and everything after it are recorded in `Documentation/CI_EVIDENCE_VOL4.md`, which must open with a pointer back to this file and must carry forward the acceptance rule in section 1, the corrected polling procedure in section 8.4, the total-coverage policy in section 8.3, and the standing limits in section 4 verbatim in substance.

Records here are appended in batch order and are not rewritten once accepted.
