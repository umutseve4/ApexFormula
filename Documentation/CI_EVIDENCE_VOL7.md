# CI evidence, volume 7

Volume 6 closed at 13,206 bytes with batch 10. It was not appended to, and
this is not a matter of headroom.

Section 0 of volume 6 states the rule plainly: an evidence volume is frozen
the moment it is committed. New evidence is written to a new volume. An
existing evidence volume is never retyped, not to append, not to reformat,
and not to fix a typo. The reason is mechanical rather than aesthetic. Every
write to this repository from the agent side is a full-file rewrite, so
"appending" one section to a 13 KB file means retyping 13 KB of already
verified record and hoping the reconstruction is faithful. A transcription
error introduced that way would corrupt evidence that was correct when it
was committed, and it would be invisible, because the corrupted text would
look exactly as authoritative as the original.

So volume 6 stays exactly as it was committed, and batch 11 starts here.

The four standing rules of the record carry forward unchanged:

1. A check run is quoted with its id, its conclusion and its timestamps, or
   it is not quoted.
2. A partial read is never rounded up to a result. If fifteen runs were
   expected and twelve were read, the record says twelve.
3. Green is quoted together with what it does not cover.
4. A discrepancy is never reconciled by adjusting either number.

---

## 11. Batch 11, the smoke test rename

### What was under test

One code change, and only one:

| Property | Value |
|---|---|
| File | `BlenderPipeline/scripts/af_smoke_test.py` |
| Blob before | 10,774 bytes |
| Blob after | 10,778 bytes |
| Delta | +4 bytes |
| Blob sha after | `491a921b4dc3257b92829bbaad44833979523965` |
| Marker commit | `2023b16db08f6243ecaea970ef31f1b8b256c1c3` |
| Authored | 2026-08-12T13:47:31Z |

Two string literals changed, both prose, neither an identifier:

* the first line of the module docstring, and
* `lines = ["UludagFormula pipeline smoke test", RULE]` in `write_report()`,
  which is the title line of the generated report.

The `AF_` and `af_` prefixes were deliberately left alone. That is D-048
option 2, reaffirmed as F-2 in D-051: the prefix is a namespace, not an
abbreviation of the project name, and rewriting it would touch C++ class
names, Blueprint asset names, export filenames and every hand-quoted hash in
the documentation for no functional gain.

The predicted size delta was +4 bytes: two occurrences of `ApexFormula`
(11 characters) becoming `UludagFormula` (13 characters). The observed delta
was +4 bytes. Every rename commit in this project has predicted its byte
delta in advance and every prediction has been correct, which is the cheapest
available check that the edit landed exactly as intended and nothing else
moved.

### Why this batch exists at all

Under D-054, a markdown-only commit creates no CI obligation and a code
commit does. Five commits were pushed to `main` in the working session that
produced this batch:

| Commit | Path | Kind | Obligation |
|---|---|---|---|
| `993e588b` | `Documentation/DECISION_LOG_VOL9.md` | markdown | none |
| `2b9a909e` | `Documentation/DECISION_LOG_VOL9.md` | markdown | none |
| `618811c6` | `Documentation/SCRIPT_INVENTORY.md` | markdown | none |
| `e265dd97` | `Documentation/DECISION_LOG_VOL9.md` | markdown | none |
| `2023b16d` | `BlenderPipeline/scripts/af_smoke_test.py` | code | **this batch** |

Four documents and one script. The four documents are not exempt because
documents are unimportant; they are exempt because nothing in either workflow
reads them, so a green tick after a markdown commit would be evidence about
the previous code state wearing a new commit's timestamp. The script is not
exempt for the mirror-image reason: `af_smoke_test.py` is executed by the
`blender-pipeline` job, so a change to it can genuinely break something.

### Route

Same reading device as batches 9 and 10. A branch is created at the marker
commit, a draft pull request is opened purely so the check runs are
addressable, the runs are read back, and the pull request is closed unmerged.
Nothing is merged, nothing is deleted, and the pull request is never a
proposal.

| Property | Value |
|---|---|
| Branch | `ci-batch-11-smoke-rename` |
| Head | `2023b16db08f6243ecaea970ef31f1b8b256c1c3` |
| Base | `ci-batch-10-export-determinism` |
| Pull request | #29, draft, closed unmerged |
| Id | 4262862235 |

### Check runs, all fifteen

Fifteen runs, `total_count` fifteen, fifteen `completed`, fifteen `success`,
zero of anything else. Three trigger waves — the push to `main`, the branch
creation, and the pull request opening — each firing both workflow files.

**Wave A — push to `main`, workflow runs 31603274857 and 31603274881**

| Name | Id | Conclusion | Started | Completed |
|---|---|---|---|---|
| Python syntax check | 94135713629 | success | 13:47:44Z | 13:47:51Z |
| af_static_validate (py3.9) | 94135713739 | success | 13:47:36Z | 13:47:52Z |
| af_static_validate (py3.12) | 94135713764 | success | 13:47:36Z | 13:47:44Z |
| Static validation (no engine, no DCC) | 94135714145 | success | 13:47:36Z | 13:47:43Z |
| Blender smoke test (headless) | 94135759184 | success | 13:47:45Z | 13:48:26Z |

**Wave B — branch creation, workflow runs 31603378960 and 31603378979**

| Name | Id | Conclusion | Started | Completed |
|---|---|---|---|---|
| Python syntax check | 94136069335 | success | 13:48:48Z | 13:48:56Z |
| af_static_validate (py3.12) | 94136069399 | success | 13:48:48Z | 13:48:58Z |
| af_static_validate (py3.9) | 94136069492 | success | 13:48:48Z | 13:49:03Z |
| Static validation (no engine, no DCC) | 94136070057 | success | 13:48:48Z | 13:48:54Z |
| Blender smoke test (headless) | 94136113434 | success | 13:48:57Z | 13:49:35Z |

**Wave C — pull request opened, workflow runs 31603412626 and 31603412661**

| Name | Id | Conclusion | Started | Completed |
|---|---|---|---|---|
| af_static_validate (py3.9) | 94136183254 | success | 13:49:11Z | 13:49:23Z |
| Python syntax check | 94136183302 | success | 13:49:11Z | 13:49:20Z |
| Static validation (no engine, no DCC) | 94136183356 | success | 13:49:11Z | 13:49:22Z |
| af_static_validate (py3.12) | 94136183364 | success | 13:49:11Z | 13:49:19Z |
| Blender smoke test (headless) | 94136249856 | success | 13:49:25Z | 13:50:01Z |

All timestamps 2026-08-12.

### Attribution

The earliest `started_at` in the batch is 13:47:36Z. The marker commit was
authored at 13:47:31Z. Every run in the batch therefore started after the
code change existed, by five seconds at the tightest, and no run can be a
stale result from the previous tree wearing this batch's label.

Five seconds is a small margin, so it is worth saying why it is sufficient
rather than merely favourable. The ordering is not inferred from wall-clock
proximity: the workflow runs were resolved through the marker commit itself,
so the association is structural. The timestamp comparison is a consistency
check on that association, not the basis for it.

### The Blender job, examined rather than assumed

The three `Blender smoke test (headless)` runs lasted 41, 38 and 36 seconds.
That was flagged, on first reading, as implausibly short for a job that
downloads and unpacks a full Blender 5.2 LTS build and then executes a
seven-stage pipeline — and the honest suspicion was that the job might be
short-circuiting, exiting 0 without ever running anything, which would make
every green tick on that job worthless.

Rather than record that suspicion as a finding, `.github/workflows/validate.yml`
was re-read in full at the marker tree, sha `b4ad549947eaf1d57c0ce36cce31703bcb501001`.
The suspicion does not survive contact with the file:

* The string `continue-on-error` does not appear anywhere in the workflow.
* No step in `blender-pipeline` carries an `if:` guard. The only conditional
  in the job is `if: always()` on the artifact upload, which makes that step
  run more often, not less.
* The resolution step runs under `set -uo pipefail` and terminates with
  `exit 1` on all four of its failure paths: series directory not listed,
  no `linux-x64` archive published for the series, download failed after the
  archive was resolved, archive downloaded but not extractable. Each one
  emits a `::error::` annotation naming itself.
* `set -e` was deliberately removed from that step, and the comment in the
  file explains why: under `-e` the failures were being swallowed silently.
  The explicit `exit 1` paths replaced it.
* `blender --version` runs as its own step, so a binary that unpacked but
  cannot execute fails before the smoke test is reached.
* The smoke test step is a bare `blender --background --factory-startup
  --python BlenderPipeline/scripts/af_smoke_test.py` with no `|| true` and
  no exit-code suppression, and per `BlenderPipeline/README.md` §5 the script
  exits 1 on validation failure, 2 when `bpy` is unavailable and 3 when a run
  fails.

So a green `blender-pipeline` means the archive was resolved and extracted,
the Blender binary executed, `bpy` was importable, and `af_smoke_test.py`
completed all seven stages and returned 0. The duration is tight but not
impossible: the runner's link to `download.blender.org` is fast and `xz`
extraction of a single archive is the dominant cost.

This corrects, rather than confirms, finding F-4 of `SCRIPT_INVENTORY.md`,
which recorded it as unknown whether the `blender-pipeline` job had ever gone
green. It had. Batch 10 shows the same job green three times at 36, 35 and 40
seconds, and that evidence was already in volume 6 when F-4 was written. F-4
is wrong and is corrected in the decision log, not here and not by editing
the inventory.

One question genuinely remains and is opened as **OPEN-067-A**: which exact
5.2.x patch release was resolved. The workflow resolves it at run time by
listing the release directory and taking the highest version, and prints it
via `blender --version`, but that value lives in the step log, and step-level
logs are not reachable through the interface available here — the same
limitation recorded as D-064.7. The series is pinned; the patch is unpinned
by design and currently unrecorded.

### What this batch establishes, precisely

* The two renamed string literals did not break the smoke test. The script
  parses, imports and runs to completion under Blender.
* The 16-step static validation gate is unaffected, on both Python 3.9 and
  3.12.
* The export determinism gate introduced in batch 10 still passes on this
  tree.
* The `blender-pipeline` job is a real gate with no escape hatch, established
  by reading the workflow rather than by trusting a tick.

### What it does not establish

* No C++ has been compiled. Nothing in this repository ever has been.
* No mesh has been seen by a human being. The exported surfaces are byte
  stable and pass every arithmetic audit written for them, and not one of
  them has been looked at.
* Milestone 4 is **not accepted**. Its sole remaining blocker is OPEN-051-F,
  a fifteen-criterion visual acceptance gate whose eight G-2 criteria require
  Blender 5.2 LTS running on a real machine with the face-orientation overlay
  at three angles. Partial pass is fail.
* `requires local compilation`, `requires Unreal Editor verification`,
  `requires playtesting` and `requires visual inspection` remain unsatisfied,
  exactly as the header comment of `validate.yml` says they must.

### Cumulative position

Batch 11 adds fifteen green check runs to the one hundred and fifteen
recorded across volumes 1 to 6. The running total is **one hundred and
thirty**, and batch 11 is the **twelfth consecutive all-green batch**.

A hundred and thirty green ticks is a statement about a static validator, a
byte-compiler, seven self-testing guards, a determinism comparison and a
headless Blender run. It is not a statement about a car, a track, a lap, or a
frame of rendered output. Nothing in this volume moves Milestone 4 one step
closer to acceptance; only Blender on Umut's machine can do that.
