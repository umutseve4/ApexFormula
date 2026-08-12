# Decision log, volume 10

Volume 9 closed at 19,545 bytes with D-066. Under D-057 a decision volume is
frozen once it approaches twenty kilobytes, because every write from the
agent side is a full-file rewrite and a 20 KB retype is a 20 KB opportunity
to corrupt a correct record. Volume 9 is **frozen**. It is not edited again,
not to append, not to correct, not to reformat.

The tables in this volume are now the authoritative ones (D-061.2). Where
this volume and any earlier volume disagree, this volume is current and the
earlier volume is history. Errata are recorded here; frozen volumes are never
retro-edited.

Next decision id: **D-068**.

---

## D-067 — The smoke test rename is verified in CI, and the Blender gate is examined rather than trusted

**Status: verified.** Code committed, byte-verified, CI-green, and the gate
that produced the green was read in full before the green was believed.

### D-067.1 — OPEN-066-C is closed

OPEN-066-C was opened in `SCRIPT_INVENTORY.md` §8: `af_smoke_test.py` still
contained the old project name in two string literals, and the question was
whether changing them would disturb anything that executes.

It did not. The evidence:

| Property | Value |
|---|---|
| Blob before | 10,774 bytes |
| Blob after | 10,778 bytes |
| Delta | +4 bytes, exactly as predicted |
| Blob sha | `491a921b4dc3257b92829bbaad44833979523965` |
| Commit | `2023b16db08f6243ecaea970ef31f1b8b256c1c3` |
| Authored | 2026-08-12T13:47:31Z |
| CI | batch 11, fifteen check runs, fifteen `success` |

Two occurrences of `ApexFormula` (11 characters) became `UludagFormula`
(13 characters): the first line of the module docstring, and the report title
in `write_report()`. The +2 bytes per occurrence prediction has now held for
every rename commit in this project without exception.

The `af_` prefix was not touched, per D-048 option 2 and D-051 F-2. The
prefix is a namespace, not an abbreviation of the project name.

**OPEN-066-C: closed.**

### D-067.2 — Erratum: finding F-4 of SCRIPT_INVENTORY.md is wrong

F-4, written in commit `618811c6`, recorded that it was unknown whether the
`blender-pipeline` job had ever gone green.

That was false when it was written, and the evidence contradicting it was
already committed to this repository. `CI_EVIDENCE_VOL6.md` records batch 10
with three green `Blender smoke test (headless)` runs, at 36, 35 and 40
seconds. Batch 11 adds three more, at 41, 38 and 36 seconds. The job has gone
green at least six times.

The error was one of method, not of transcription. F-4 was derived by reading
the workflow definition and the script inventory and reasoning about what
*should* have been exercised, without cross-checking the claim against the
evidence volumes that record what *was*. The inventory and the evidence
volumes are two halves of the same record and neither is complete alone.

Standing correction, applicable beyond this instance: a claim of the form
"it is unknown whether X has ever run" is a claim about the evidence
volumes, and it may not be written without reading them.

`SCRIPT_INVENTORY.md` is **not** edited to fix this. It is a 18,276-byte file
and a full retype to correct one paragraph is a disproportionate corruption
risk under D-053.6. The erratum lives here, and this volume is authoritative.

### D-067.3 — The Blender job was suspected of short-circuiting; the suspicion was wrong

Batch 11's three Blender runs completed in 36 to 41 seconds. For a job that
downloads a full Blender 5.2 LTS archive, extracts it, and then runs a
seven-stage pipeline, that is fast enough to be worth doubting, and the
initial reading was that the job might be exiting 0 without doing anything —
which would have made every green tick on it worthless and would have made
this an urgent defect rather than a footnote.

The honest move was to check rather than to publish the suspicion, so
`.github/workflows/validate.yml` was re-read in full at the marker tree, sha
`b4ad549947eaf1d57c0ce36cce31703bcb501001`. The suspicion does not survive:

1. `continue-on-error` does not appear anywhere in the workflow file.
2. No step in `blender-pipeline` carries an `if:` guard. The only conditional
   in the job is `if: always()` on the artifact upload, which makes a step run
   more often, not less.
3. The resolution step runs under `set -uo pipefail` and exits 1 on all four
   of its failure paths, each with a self-naming `::error::` annotation:
   series directory not listed, no `linux-x64` archive for the series,
   download failed after resolution, archive not extractable.
4. `set -e` was removed from that step deliberately, and the in-file comment
   says why: under `-e` the interesting failures were being swallowed. The
   explicit `exit 1` paths are the replacement.
5. `blender --version` is its own step, so a binary that extracted but cannot
   execute fails before the smoke test is reached.
6. The smoke test invocation carries no `|| true` and no exit-code
   suppression, and per `BlenderPipeline/README.md` §5 the script exits 1 on
   validation failure, 2 when `bpy` is unavailable, and 3 on a failed run.

Therefore a green `blender-pipeline` means: archive resolved, downloaded and
extracted; Blender executed; `bpy` importable; `af_smoke_test.py` ran all
seven stages and returned 0. That is a stronger statement than this project
has previously been willing to make about that job, and it is now backed by
the workflow text rather than by the absence of a red tick.

The 36-second duration is tight but not implausible: the runner's link to
`download.blender.org` is fast and a single `xz` extraction dominates.

**Method note worth keeping.** The suspicion was correct to raise and wrong
to publish unexamined. Had it been written into the evidence volume as a
finding, it would have quietly devalued six legitimate green runs on the
strength of an intuition about download speeds. Suspicion is a reason to
read the source, not a substitute for reading it.

### D-067.4 — OPEN-067-A is opened

One question survives D-067.3 and it is much narrower than the one that
started it.

The workflow pins `BLENDER_SERIES: '5.2'` and resolves the patch release at
run time, by listing the release directory and taking the highest matching
`blender-5.2.x-linux-x64.tar.xz`. The resolved filename is echoed, and
`blender --version` prints the version actually used. Both values land in the
step log.

Step-level logs are not reachable through the interface available here. This
is the same limitation already recorded as D-064.7, which is why the hand
measured determinism figures (26 files, 112,123 bytes) have never been
confirmed from a CI log either.

So: the series is pinned and verified, the patch is unpinned by design and
currently unrecorded anywhere in this repository.

**OPEN-067-A — which exact Blender 5.2.x patch release does CI resolve, and
should it be recorded in `VERSION_MATRIX.md`?** Resolvable by Umut in two
ways: open any `blender-pipeline` job log and read the `Resolved:` line, or
download the `blender-pipeline-output` artifact from a recent run. Not
resolvable from here.

### D-067.5 — Batch 11 recorded in a new evidence volume

`CI_EVIDENCE_VOL6.md` was **not** appended to. Its own §0 states that an
evidence volume is frozen on commit and is never retyped — not for an append,
not for a reformat, not for a typo — because a full-file rewrite of verified
evidence risks corrupting text that was correct when committed, invisibly.

Batch 11 is therefore recorded in `Documentation/CI_EVIDENCE_VOL7.md`,
committed as `95ec3e993f2114dcf90d9822af23aae60022c2df`, 11,984 bytes.

Cumulative position: **130 green check runs**, batch 11 being the **twelfth
consecutive all-green batch**.

### D-067.6 — What is still not true

Restated because a volume that opens with three closures is exactly where
this gets forgotten:

* No C++ in this repository has ever been compiled.
* No generated mesh has ever been seen by a human being.
* **Milestone 4 is not accepted.** Slices 1 to 3 are implemented and
  CI-green. The sole blocker is OPEN-051-F, a fifteen-criterion gate: seven
  numeric G-1 criteria measurable from the exported OBJ with the standard
  library, and eight visual G-2 criteria requiring Blender 5.2 LTS with the
  face-orientation overlay at three angles. **Partial pass is fail.**
* `requires local compilation`, `requires Unreal Editor verification`,
  `requires playtesting` and `requires visual inspection` are all unsatisfied.

---

## Open questions, authoritative table

| Id | Subject | Status |
|---|---|---|
| OPEN-051-B | Drift guard banner announces 27 entries; the counterparty count has never been identified | open |
| OPEN-051-F | Milestone 4 visual acceptance, 15 criteria, 8 requiring Blender on a real machine | **open — M4 blocker** |
| OPEN-053-A | Local rehearsal gate for `af_mesh_quality.py` | open |
| OPEN-060-A | 936 historical faces versus 798 serialised faces. Neither number is to be adjusted | open |
| OPEN-063-A | `VERSION_MATRIX.md` §5.20 "the eight scripts" predates the ninth by 7 minutes | closed by D-065.4 |
| OPEN-064-A | Creation provenance of `af_config_hash_guard.py` and `af_mesh_quality.py` | closed by D-065.2 / D-065.3 |
| OPEN-065-A | VOL8 header still reads "open" although VOL9 superseded it | open |
| OPEN-065-B | Cross-reference from `VERSION_MATRIX.md` §5.20 to `SCRIPT_INVENTORY.md` | narrowed to one pointer |
| OPEN-066-A | `af_static_validate.py` has no `--self-test` step in either workflow | open |
| OPEN-066-B | `af_bodywork_selftest.py`, 22,078 bytes, exercised by nothing but `compileall` | open |
| OPEN-066-C | Old project name in two `af_smoke_test.py` literals | **closed by D-067.1** |
| OPEN-067-A | Which Blender 5.2.x patch does CI resolve, and should it be pinned in `VERSION_MATRIX.md` | **open — new** |

Twelve entries. Three closed, one narrowed, eight open. OPEN-051-F is the
only one gating a milestone.

---

## Volume status

| Volume | Size | Status |
|---|---|---|
| `DECISION_LOG.md` … `DECISION_LOG_VOL8.md` | — | frozen |
| `DECISION_LOG_VOL9.md` | 19,545 B | **frozen at D-066** |
| `DECISION_LOG_VOL10.md` | this file | **open** |
| `CI_EVIDENCE.md` … `CI_EVIDENCE_VOL6.md` | — | frozen |
| `CI_EVIDENCE_VOL7.md` | 11,984 B | **open** |

Next decision id: **D-068**.
