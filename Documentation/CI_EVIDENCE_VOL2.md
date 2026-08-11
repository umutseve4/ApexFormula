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
that is missing that write.

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

Rows 1–6 were confirmed green by the `20:06:39Z`–`20:07:47Z` batch. **Rows 7–13 had no fresh
evidence at the time this file was written** — that is precisely the gap §2 explains and the
verification pull request closes.

`Documentation/MILESTONE_3_CIRCUIT.md` was triaged and **deliberately not rewritten**: it carries
no product prose, only circuit identifiers and merge SHAs. Absence of a commit for it is a
recorded decision, not an oversight.

`Documentation/DECISION_LOG.md` (50,726 B) is **frozen** by the same policy that produced this
volume.

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

---

## 5. Acceptance criteria for the verification run

The verification pull request is accepted only if **all** of the following hold:

1. **10 of 10 check runs report `success`.** The expected set is fixed: `Blender smoke test
   (headless)` ×2, `Static validation (no engine, no DCC)` ×2, `af_static_validate (py3.9)` ×2,
   `af_static_validate (py3.12)` ×2, `Python syntax check` ×2.
2. **Every `started_at` is later than `2026-08-11T20:22:09Z`**, the author date of the last
   documentation commit. A green batch that started earlier proves nothing about this tree and
   must be rejected as stale.
3. The pull request head contains all thirteen commits in §3.
4. The pull request is **closed without merging** afterwards. It exists to produce evidence, not
   to change `main`.

Criterion 2 is the one that was missing before, and it is the reason this file states it as a
rule rather than as a note.

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
may be changed by it.

---

## 7. Volume index

| Volume | Range | State |
| --- | --- | --- |
| `CI_EVIDENCE.md` | Milestones 0B–4, first batch | frozen |
| `CI_EVIDENCE_VOL2.md` | Documentation rename wave (D-048) onward | **live** |
