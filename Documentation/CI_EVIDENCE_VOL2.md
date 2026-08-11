# CI Evidence — Volume 2

Continuation of [`CI_EVIDENCE.md`](CI_EVIDENCE.md), which is **frozen** at volume 1.

Volume 1 is 23,864 B. There is no patch API available in this authoring environment — every write
is a full-file retranscription — so appending a single row to volume 1 costs a 23 KB rewrite and
carries a real truncation risk each time. The same volume-split policy already applied to
`DECISION_LOG.md` (frozen, D-001…D-044) is therefore applied here. **Volume 1 is not deleted, not
edited and not superseded.** It remains the record for everything up to and including Milestone 4's
first CI batch. This volume starts at the documentation-rename wave.

Rule inherited from the ledger split: **open a new volume once a file passes ~20 KB.**

---

## 1. What this volume covers

The wave-1 documentation rename of the product identity from the previous name to **Uludağ
Formula**, recorded as **D-048**, and the CI evidence for it.

Scope reminder, so this file is not misread later:

- **Wave 1 — display identity and documentation prose.** Markdown files, `DefaultGame.ini`
  display strings. No compiled artefact, no build input, no guard.
- **Wave 2 — module identifiers.** The six `ApexFormula*` modules, `ApexFormula.uproject`, both
  `*.Target.cs` files, `DefaultApexFormula.ini`, `APEXFORMULAX_API`, `FApexFormulaXModule`, the
  C++ copyright literal in 65 files, and the matching rewrite of `Tools/af_static_validate.py`.
  **Not started.**
- **Never — the `AF_`/`af_` prefix family.** D-048 reclassified it as the project's permanent
  internal code name. It is not a rename backlog item.

---

## 2. Diagnosed cause of the stale check-run batch

For several pushes the check-run timestamps did not advance. The cause has been identified and it
is not a CI fault:

| Fact | Value |
| --- | --- |
| Pull request read for evidence | **#9** |
| Its head branch | **`milestone-4-bodywork`** |
| Its head SHA | `c94bcade` |
| Its base | `main` |
| Its `updated_at` | `2026-08-11T20:06:36Z` |
| Where every wave-1 documentation commit was pushed | **`main`** |

A pull request's check runs belong to **its head commit**. Commits pushed directly to `main` are
not in PR #9's diff and cannot fire its workflows, so reading PR #9 returned the same frozen
`20:06:39Z`–`20:07:47Z` batch no matter how many documentation commits landed on `main`.

**Consequence for method, not just for this incident:** in this environment there is no tool that
lists check runs for a bare branch. Check runs are readable only through a pull request. Therefore
**evidence for work pushed to `main` requires a pull request whose head contains that work.** The
procedure adopted is:

1. Push the work to `main`.
2. Create a branch from `main` **after** the last write, so the branch tip contains everything.
3. Add one marker commit to that branch so the pull request has a non-empty diff.
4. Open the pull request against `main`, read its check runs, then close it without merging.

Step 2 ordering is not optional. A branch cut before the final write produces evidence for a tree
that is missing that write. This was learned the expensive way: an earlier branch,
`ci/doc-wave-verify`, was cut too early and had to be abandoned in favour of
`ci/doc-wave-verify-2`.

The procedure has now been executed twice — §5 and §5A — with identical results. It is no longer
a proposal; it is the standing method for this repository until a branch-level check-run reader
becomes available.

---

## 3. Commits in the documentation wave

Author timestamps are as recorded by the API. Short SHAs are used deliberately: the config-hash
guard flags 16–64 character hex tokens near a `config hash` anchor, and 8-character SHAs cannot
trip it.

| # | Path | Commit | Size after | Author date (UTC) |
| --- | --- | --- | --- | --- |
| 1 | `Unreal/Config/DefaultGame.ini` | `da7cf78d` | 2,174 B | 2026-08-11 |
| 2 | `Documentation/MILESTONE_4_IMPLEMENTATION.md` | `ac1abc79` | 23,694 B | 2026-08-11 |
| 3 | `Documentation/DECISION_LOG_VOL2.md` | `a235f4ae` | 10,921 B | 2026-08-11 |
| 4 | `README.md` | `1e25d9a6` | 16,318 B | 2026-08-11 |
| 5 | `Documentation/PROJECT_VISION.md` | `39cb8e75` | 12,679 B | 2026-08-11 |
| 6 | `Documentation/VEHICLE_SYSTEM_DECISION.md` | `7008b61d` | 10,897 B | 2026-08-11 |
| 7 | `Documentation/MILESTONE_2_IMPLEMENTATION.md` | `4aae276d` | 14,348 B | 20:07:45Z |
| 8 | `Documentation/DRIVER_PIPELINE_DESIGN.md` | `9d5bc731` | 15,311 B | 20:09:47Z |
| 9 | `Documentation/TECHNICAL_ARCHITECTURE.md` | `e0c931b5` | 19,530 B | 20:12:26Z |
| 10 | `Documentation/BLENDER_PIPELINE_DESIGN.md` | `31e0ea40` | 20,246 B | 20:14:30Z |
| 11 | `Documentation/MILESTONE_PLAN.md` | `dd93bd2f` | 24,860 B | 20:17:22Z |
| 12 | `Unreal/README.md` | `7156b335` | 15,948 B | 20:19:42Z |
| 13 | `BlenderPipeline/README.md` | `71ef6d45` | 10,868 B | 20:22:09Z |
| 14 | `Documentation/CI_EVIDENCE_VOL2.md` (this file, created) | `76fdcb31` | 8,487 B | 20:23:10Z |
| 15 | `Documentation/DECISION_LOG_VOL2.md` (D-049 appended) | `078b4383` | 14,596 B | 20:25:20Z |
| 16 | `Documentation/CI_EVIDENCE_VOL2.md` (PR #17 result recorded) | SHA `e24e2c61` | 15,690 B | 20:33Z |
| 17 | `Documentation/DECISION_LOG_VOL2.md` (D-050 appended) | `be181489` | 20,441 B | 20:37:06Z |

Rows 1–6 were confirmed green by the `20:06:39Z`–`20:07:47Z` batch. **Rows 7–15 had no fresh
evidence at the time this file was first written** — that is precisely the gap §2 explains and the
verification pull request in §5 closes. **Rows 16–17 postdate that run** and are covered by the
second verification pull request in §5A.

Two further commits exist and are **not** in the table above, on purpose:

| Path | Commit | Size | Author date (UTC) | Location |
| --- | --- | --- | --- | --- |
| `Documentation/CI_RUN_NOTE.md` | `f6de019f` | 1,687 B | 20:27:06Z | branch `ci/doc-wave-verify-2` only |
| `Documentation/CI_RUN_NOTE.md` | `219667a4` | 1,958 B | 20:38:41Z | branch `ci/doc-wave-verify-3` only |

Those are the marker commits from step 3 of the procedure. They exist solely to give a
verification pull request a non-empty diff, they live on their branches and **must never be merged
to `main`.** They are listed here so that a future reader who finds them in the reflog is not left
guessing.

`Documentation/MILESTONE_3_CIRCUIT.md` was triaged and **deliberately not rewritten**: it carries
no product prose, only circuit identifiers and merge SHAs. Absence of a commit for it is a
recorded decision, not an oversight. See D-049.

`Documentation/DECISION_LOG.md` (50,726 B) is **frozen** by the same policy that produced this
volume. `Documentation/DECISION_LOG_VOL2.md` reached 20,441 B at row 17 and is now **full** by the
same rule: D-051 onward opens volume 3.

---

## 4. Why these files are CI-safe

Not an assumption — this was established by extracting `Tools/af_static_validate.py` (52,702 B,
1,382 lines, 84 `report.check()` calls) and reading it directly.

| Finding | Consequence |
| --- | --- |
| The guard contains **zero** references to `README` or to `Documentation/` | Every Markdown file in the wave is outside its scope |
| `DefaultGame.ini` is checked for **existence only**; its content is never parsed | The display-name change in it cannot fail the guard |
| The prohibited-identifier list is `F1`, `FIA`, `FormulaOne`, `Formula1`, `[Ff]ormula[ _-]1`, `GrandPrix`, `[Gg]rand[ _-][Pp]rix` | **"Uludağ Formula" matches none of them.** Bare "Formula" is not a prohibited token |
| `Unreal/README.md` and `BlenderPipeline/README.md` are outside the config-hash guard's scanned set entirely | Neither can trip it |
| No file in the wave contains a hex token of ≥16 characters | The config-hash guard's second condition cannot be met |

The name-collision result is stronger than "we checked by hand": the originality check runs on
every push, so the new product name is **continuously** cleared rather than cleared once.

The prediction in this section was made before the verification run and is recorded here
unchanged. §5 reports what actually happened. Predicting first and measuring second is the point;
a prediction rewritten after the fact is not evidence of anything.

**One qualification, added after row 17.** The last row of the table above stopped being true of
the whole repository when D-050 was written: D-050.2 quotes the sixteen-character configuration
digest short form immediately after a `config_hash` anchor, inside `Documentation/`, which is in
the config-hash guard's scanned set. Both of the guard's conditions are therefore met in that
paragraph, and it passes only because the quoted value is the **correct** short form of the current
pin. That is a real, deliberate exposure and it is the specific risk §5A was run to settle. The
original sentence is left standing rather than quietly edited, because it was true when written
and the correction is more informative than a silent rewrite.

---

## 5. The first verification run — result

**Status: passed.** The prediction in §4 held.

| Field | Value |
| --- | --- |
| Pull request | **#17**, `ci/doc-wave-verify-2` → `main`, draft |
| Head commit | `f6de019f` (marker commit, author date 20:27:06Z) |
| Check runs | **10 of 10 `success`** |
| Earliest start | `2026-08-11T20:27:19Z` |
| Latest start | `2026-08-11T20:27:37Z` |
| Latest completion | `2026-08-11T20:28:12Z` |
| Disposition | **closed without merging** |

The acceptance criteria were fixed **before** the run, not after:

1. **Ten of ten check runs report `success`.** The expected set is fixed: `Blender smoke test
   (headless)` ×2, `Static validation (no engine, no DCC)` ×2, `af_static_validate (py3.9)` ×2,
   `af_static_validate (py3.12)` ×2, `Python syntax check` ×2. — **met.** All ten names appeared,
   all ten concluded `success`.
2. **Every `started_at` is later than the newest commit in the tree**, `20:27:06Z`. A green batch
   that started earlier proves nothing about this tree and must be rejected as stale. — **met.**
   The earliest start, `20:27:19Z`, is thirteen seconds after the marker commit; the previous
   batch at `20:06:39Z` is correctly excluded.
3. The pull request head contains every commit in §3. — **met**, by construction: the branch was
   cut from `main` after commit `078b4383`, the last write of the wave.
4. The pull request is **closed without merging** afterwards. It exists to produce evidence, not
   to change `main`. — **met.**

Criterion 2 is the one that was missing before, and it is the reason this file states it as a rule
rather than as a note. Four workflow runs fired — `31533005896`, `31533006001`, `31533015325`,
`31533015328` — which is the expected fan-out for two workflows across two trigger events.

Note on reading discipline: the first read of the check runs returned nine `success` and one
`in_progress`. That is **not** a passing result and was not recorded as one. The run was re-read
after the remaining job completed. A partially green batch reported as green is exactly the class
of error this file exists to prevent.

---

## 5A. The second verification run — rows 16–17

**Status: passed.**

| Field | Value |
| --- | --- |
| Pull request | **#18**, `ci/doc-wave-verify-3` → `main`, draft |
| Head commit | `219667a4` (marker commit, author date `2026-08-11T20:38:41Z`) |
| Branch cut from | `main` at `be181489`, after the D-050 write |
| Commits newly covered | rows 16 and 17 of §3 |
| Check runs | **10 of 10 `success`** |
| Earliest start | `2026-08-11T20:38:46Z` |
| Latest start | `2026-08-11T20:39:15Z` |
| Latest completion | `2026-08-11T20:39:54Z` |
| Disposition | **closed without merging** |

The same four acceptance criteria were applied unchanged, and the same reading discipline was
required: the first read returned nine `success` and one `in_progress` — the second
`Blender smoke test (headless)` job, started `20:39:15Z` — and was **not** recorded as a pass. The
run was re-read after that job completed at `20:39:54Z`.

Criterion 2 margin: the earliest start, `20:38:46Z`, is five seconds after the marker commit's
author date. Five seconds is a thinner margin than the thirteen of §5 but it is unambiguous, and
every one of the ten runs starts after the cutoff, not merely the earliest.

**What this run specifically settles.** The `af_static_validate` and static-validation jobs passed
with D-050's `config_hash` quotation present in `Documentation/DECISION_LOG_VOL2.md`. That is the
measured answer to the exposure described at the end of §4: the config-hash guard compares the
**value**, not the shape, of a hex token in its claim window, so quoting the correct pinned short
form is safe and quoting a stale one would not be. The exposure is real and the guard behaves as
read. The safe rule for new prose is unchanged — prefer 8-character SHAs — but the failure mode is
now understood rather than merely avoided.

---

## 6. What this evidence does and does not prove

| Claim | Label |
| --- | --- |
| The renamed documents are syntactically valid and pass every static guard | `automatically validated` |
| The product name collides with no reserved motorsport mark | `automatically validated` |
| The module identifiers, `.uproject`, target files and project ini still carry the previous name | `statically inspected` |
| The documentation wave is internally consistent — no document claims the rename is finished | `statically inspected` |
| Any C++ in this repository compiles | not claimed — `requires local compilation` |
| The Unreal Editor opens the project under either name | not claimed — `requires Unreal Editor verification` |
| The Blender pipeline produces the documented geometry | not claimed — `requires Blender execution` |
| The vehicle drives | not claimed — `requires playtesting` |

**A green CI batch here means the documentation wave is consistent and safe. It does not upgrade
a single milestone status.** No status in `MILESTONE_PLAN.md` was changed by this wave, and none
may be changed by it. Neither green result, in §5 or §5A, changes anything about that sentence.

---

## 7. What remains open after these runs

Recorded here so the wave is not mistaken for finished:

| Item | State |
| --- | --- |
| `Documentation/MILESTONE_3_IMPLEMENTATION.md` (37,137 B) | **no rewrite, ever** — D-050.2. Every occurrence is the source path `Unreal/Source/ApexFormulaRace/`, which wave 2 will move; there is no product prose in the file. It also contains a live `config_hash` claim, so a needless retranscription is a needless CI risk |
| `Documentation/VERSION_MATRIX.md` (40,427 B) | **deferred to wave 2** — D-050.3. It mixes 3 product-prose occurrences with roughly 15 module and file identifiers; rewriting it now costs two 40 KB transcriptions instead of one. The "volume-style side file" suggested by the earlier revision of this section is **superseded**: a side file cannot correct an H1 title |
| Wave 2 — modules, `.uproject`, targets, project ini, guard | not started |
| `Documentation/DECISION_LOG_VOL2.md` | full at 20,441 B; D-051 onward opens volume 3 |
| Compilation, Editor, Blender and driving evidence | unavailable in this environment; only Umut can produce it |

Wave 1 is **content complete and twice CI-verified**. That is the whole of the claim.

---

## 8. Volume index

| Volume | Range | State |
| --- | --- | --- |
| `CI_EVIDENCE.md` | Milestones 0B–4, first batch | frozen |
| `CI_EVIDENCE_VOL2.md` | Documentation rename wave (D-048) onward | **live** |
