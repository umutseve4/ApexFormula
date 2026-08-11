# Uludag Formula - Continuous Integration Evidence, Volume 4

Project: Uludag Formula (ASCII identifier form: UludagFormula)
Author: Umut Sever
Status: ACTIVE volume. New batch records are appended here.

---

## 0. Relationship to earlier volumes

| Volume | File | Batches | Size | State |
|---|---|---|---|---|
| 1 | `Documentation/CI_EVIDENCE.md` | pre-rename history | 23,864 B | frozen |
| 2 | `Documentation/CI_EVIDENCE_VOL2.md` | pull requests #17, #18 | 15,534 B | frozen |
| 3 | `Documentation/CI_EVIDENCE_VOL3.md` | batches 1 to 5, pull requests #19 to #23 | 23,535 B | frozen, closed by section 10 |
| 4 | this file | batch 6 onward | - | ACTIVE |

Volume 3 was closed by size. Every edit in this environment is a full-file
retranscription with no patch mode, so a file above roughly 20,000 bytes carries
a real risk of silent truncation during a rewrite, and Markdown has no compile
gate that would catch it. Volumes 1 to 3 are not to be edited again.

---

## 1. Acceptance rule

A batch is accepted if and only if **all** of the following hold:

1. The check-run query returns exactly **ten** runs. Ten is the fixed matrix
   size and is itself a check: any other number means a workflow failed to
   trigger.
2. Every run has `status` equal to `completed`.
3. Every run has `conclusion` equal to `success`.
4. Every run's `started_at` is strictly later than the author date of the marker
   commit. This is what proves the run observed the code under test rather than
   an earlier state of the branch.

A reading in which any run is still `in_progress` is **rejected**. It is never
rounded up, never described as nine of ten passing, and never reported as a
pass. See section 4 for what to do instead.

The ten runs are always the same five job names, each appearing twice because
two workflow files both trigger on pull request:

| Job name | Count |
|---|---|
| `Blender smoke test (headless)` | 2 |
| `Static validation (no engine, no DCC)` | 2 |
| `af_static_validate (py3.9)` | 2 |
| `af_static_validate (py3.12)` | 2 |
| `Python syntax check` | 2 |

---

## 2. Batch 6

### 2.1 Setup

| Field | Value |
|---|---|
| Branch | `ci/wave2-verify-6`, created from `main` |
| Branch head at creation | `63039649ec9ec49563628994b9c7483d5f48dd01`, verified equal to the `main` tip |
| Marker file | `Documentation/CI_MARKER_WAVE2_6.md`, present on the branch only |
| Marker commit | `23f5c1cf61c8cb372e0ed6ef3e38c194abb1121f` |
| Marker blob | `9c9d8e2521feb5c46f80697c6ecb939c831594df` |
| Marker size | 2,725 bytes |
| Marker author date | `2026-08-11T23:28:51Z` |
| Pull request | #24, draft, head `ci/wave2-verify-6`, base `main`, identifier `4257746851` |
| Disposition | closed without merging |

### 2.2 Commits covered

Batch 6 covers the complete Wave 2A creation and revert round trip. These are
the only gated-file commits authored since batch 5.

| # | Commit | Change |
|---|---|---|
| 1 | `243c5a45` | created five files under `Unreal/Source/UludagFormulaEditor/` |
| 2 | `74925c88` | deleted `UludagFormulaEditor/UludagFormulaEditor.Build.cs` |
| 3 | `6ad9e2a0` | deleted `UludagFormulaEditor/Public/UludagFormulaEditor.h` |
| 4 | `ee7b9c04` | deleted `UludagFormulaEditor/Private/UludagFormulaEditor.cpp` |
| 5 | `60bebc47` | deleted `UludagFormulaEditor/Public/AFDataValidator.h` |
| 6 | `63039649` | deleted `UludagFormulaEditor/Private/AFDataValidator.cpp` |

Net effect on the tree is zero. The rationale for the revert is D-055 in
`Documentation/DECISION_LOG_VOL4.md`.

### 2.3 Result

Ten check runs, all `completed`, all `success`. Earliest `started_at` was
`23:28:55Z`, which is four seconds after the marker author date; latest
completion was `23:29:52Z`. The acceptance rule is satisfied on all four
clauses.

| Job | Identifier | Started | Completed |
|---|---|---|---|
| `Blender smoke test (headless)` | 93960511296 | 23:29:19Z | 23:29:52Z |
| `Blender smoke test (headless)` | 93960486875 | 23:29:12Z | 23:29:47Z |
| `Static validation (no engine, no DCC)` | 93960466501 | 23:29:05Z | 23:29:17Z |
| `Static validation (no engine, no DCC)` | 93960451854 | 23:29:00Z | 23:29:10Z |
| `af_static_validate (py3.9)` | 93960466347 | 23:29:05Z | 23:29:17Z |
| `af_static_validate (py3.9)` | 93960433592 | 23:28:55Z | 23:29:06Z |
| `af_static_validate (py3.12)` | 93960466306 | 23:29:05Z | 23:29:09Z |
| `af_static_validate (py3.12)` | 93960433493 | 23:28:56Z | 23:29:04Z |
| `Python syntax check` | 93960466251 | 23:29:05Z | 23:29:10Z |
| `Python syntax check` | 93960433638 | 23:28:55Z | 23:29:02Z |

All timestamps are on `2026-08-11`. The four workflow runs were `31546627945`,
`31546627966`, `31546638963` and `31546638974`.

Only one poll was needed. The second Blender job completed 61 seconds after the
marker, and the poll was issued at approximately 55 seconds plus tool latency,
which was sufficient. This does not repeal the two-poll rule in section 4.

### 2.4 Independent post-batch verification

Two facts were checked directly against the repository rather than inferred from
the green result.

**Tree uniformity.** A field-limited listing of `Unreal/Source` returned exactly
eight entries and no `UludagFormulaEditor`:

| Name | Type | Hash | Size |
|---|---|---|---|
| `ApexFormula.Target.cs` | file | `38f0501e27c58bc78643080685639dacbf8a6ae1` | 885 |
| `ApexFormulaCore` | dir | `4b48845e01dd6f545a7e5bc2bfa9ca67b9af55f3` | - |
| `ApexFormulaEditor.Target.cs` | file | `cc67d8b90f682b6f88f3794c2374f9ca61e274b1` | 858 |
| `ApexFormulaEditor` | dir | `090b88b491cb32feb2964a4d09ce4e49e6e747d8` | - |
| `ApexFormulaRace` | dir | `e80a7644cfb19cd50f8dba55f8547b7d065b5905` | - |
| `ApexFormulaTests` | dir | `39d1bcf689972149f54a5b8c0d044ee619510261` | - |
| `ApexFormulaUI` | dir | `bdd54a0d6ad4014714094399be217350270bc985` | - |
| `ApexFormulaVehicle` | dir | `60be9eecbd82d32faa809e6fcb3090c039d64727` | - |

**Guard integrity.** `Tools/af_static_validate.py` still hashes to
`e9ab8f95d04a8239d76f49e9a376a514136b8e79` at **52,702 bytes**, identical to its
state before the round trip. The prepared 52,726-byte edit was discarded
unpushed. This matters because a green batch would not by itself distinguish a
pristine guard from a modified one that still passes.

---

## 3. Coverage policy, superseding volume 3 section 8.3

Section 8.3 of `Documentation/CI_EVIDENCE_VOL3.md` required every commit on
`main` to be covered by a green batch, including commits whose only purpose was
to record a previous batch. That policy has no fixpoint: the commit recording
batch `N` is always authored after batch `N`, so it always requires batch
`N + 1`, indefinitely. The full argument is D-054 in
`Documentation/DECISION_LOG_VOL4.md`.

**Policy in force from this volume onward:**

> A commit on `main` creates a batch obligation if and only if it adds, modifies
> or deletes at least one file whose extension is in the gated set: `.py`,
> `.cpp`, `.h`, `.cs`, `.ini`, `.uproject`, `.yml`, `.yaml`. Commits touching
> only Markdown, images, licences or other non-gated files carry no obligation.

The gated set is derived from measurement of both workflow files. No step in
either workflow parses, lints, renders or compiles Markdown. A batch whose only
new content is Markdown exercises identical code paths over identical inputs and
yields no new information.

Consequences already in effect:

* Commit `5c294bfb`, which closed volume 3, is Markdown-only and is
  **permanently uncovered by design**. It is not a gap and not technical debt.
* Commit `dc966c21`, which carries D-054 and D-055, is Markdown-only and carries
  no obligation.
* The commit that creates this file is Markdown-only and carries no obligation.

The acceptance rule in section 1 is unchanged. This policy governs *when* a
batch is owed, never *what counts as passing*.

---

## 4. Polling model

1. Push all work to `main` first. Create the verification branch only after the
   final write, and confirm the branch object hash equals the `main` tip.
2. Push exactly one marker commit to the branch, at a path that did not
   previously exist, and record its author date. That date is the acceptance
   clock.
3. Open a draft pull request from the branch to `main`. A pull request number is
   required: no available tool lists check runs for a bare branch.
4. Wait at least 55 seconds, then poll once.
5. If any run is `in_progress`, wait a further 40 seconds and poll again. The
   second poll must carry at least one **varied argument**, for example an
   explicit results-per-page value, because the tool harness deduplicates calls
   with identical arguments and will otherwise refuse to re-issue the query.
6. Apply the section 1 acceptance rule.
7. Close the pull request **without merging**. Marker branches never merge into
   `main`; the marker files exist only on their disposable branches.

Fifty-five seconds is a lower bound observed to be usually but not always
sufficient. Batch 4 required the second poll; batch 6 did not.

---

## 5. Standing limits on what a green batch proves

A green batch proves exactly three things:

1. Every Python file under `Tools/` and `BlenderPipeline/scripts/` compiles
   under Python 3.9, 3.11 and 3.12.
2. The static validation entry point exits zero, meaning the declared module
   graph, dependency table, prohibited-identifier rules, C++ copyright and
   pragma rules, required configuration keys and bone-name expectations are
   internally consistent; and the self-tests invoked by `validate.yml` pass.
3. The headless Blender smoke test completes.

It proves none of the following, none of which has ever occurred in this
project:

* No C++ has been compiled. No build tool has been invoked.
* No Unreal project has been opened.
* No exported mesh has been imported into an engine.
* No mesh has been inspected visually.
* No lap has been driven. No playtest has occurred.

Continuous integration here is a **structural** gate, not an **execution** gate.
It confirms that the declared structure is self-consistent. It cannot confirm
that anything runs. Milestone advancement requires the author's own machine with
Unreal Engine and Blender installed, and no number of green batches substitutes
for that.

---

## 6. Batch index

| Batch | Pull request | Marker commit | Marker date | Result |
|---|---|---|---|---|
| Wave 1 verify | #17 | see volume 2 | 2026-08-11 | 10/10 success |
| Wave 1 verify 2 | #18 | `219667a4` | 20:38:41Z | 10/10 success |
| 1 | #19 | see volume 3 | 2026-08-11 | 10/10 success |
| 2 | #20 | see volume 3 | 2026-08-11 | 10/10 success |
| 3 | #21 | see volume 3 | 2026-08-11 | 10/10 success |
| 4 | #22 | `5961d95b` | 22:39:47Z | 10/10 success, second poll required |
| 5 | #23 | `49c93957` | 23:02:47Z | 10/10 success |
| 6 | #24 | `23f5c1cf` | 23:28:51Z | 10/10 success |

Eight batches, eighty check runs, zero failures.
