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

Next decision id: **D-069**.

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

## D-068 — The Blender patch release resolved by CI is 5.2.0

**Status: verified.** Read from the live step log of a green run by Umut and
transcribed here. Two independent values inside the same job agree.

### D-068.1 — The evidence

Workflow `validate`, run **#208**, job **Blender smoke test (headless)**,
result `succeeded`, duration 35 seconds, 2026-08-12. The two relevant steps
produced:

| Source | Value |
|---|---|
| Step `Resolve and install Blender 5.2 LTS`, echoed archive | `blender-5.2.0-linux-x64.tar.xz` |
| Step `Record the Blender version actually used`, `blender --version` | `Blender 5.2.0 LTS` |
| Build date | 2026-07-14 |
| Build time | 01:32:04 |
| Build commit date | 2026-07-13 |
| Build commit time | 15:20 |
| Build hash | `fbe6228777e7` |
| Build branch | `blender-v5.2-release` |
| Build platform | Linux |
| Build type | Release |

The directory listed immediately before resolution was
`https://download.blender.org/release/Blender5.2/`.

This matters more than a version string usually would, because the two values
come from different mechanisms. The first is a filename chosen by
`sort -V | tail -n 1` over a scraped directory index; the second is the
binary's own self-report after extraction and execution. If the resolver had
picked one archive and the runner had somehow executed another — a stale
cached binary on `PATH`, an extraction into an unexpected prefix — the two
lines would disagree. They do not. The archive that was resolved is the
binary that ran.

**OPEN-067-A: closed.** The answer is **5.2.0**.

### D-068.2 — What 5.2.0 implies about the resolver

The resolver takes the highest `blender-5.2.x-linux-x64.tar.xz` in the series
directory. It returned `5.2.0`. Therefore, as of 2026-08-12, **no patch
release above 5.2.0 exists in that directory**.

This is a fact about today, not a property of the build. It is precisely the
kind of statement that ages badly, so it is dated here rather than asserted
generally. The moment 5.2.1 is published, this repository's CI will begin
using it, silently, with no commit, no review and no note in any log that a
human reads by default. That is the substance of D-068.3.

Note also that the build is dated 2026-07-14 and the commit it was built from
is dated 2026-07-13 — a one-day lag consistent with an ordinary release
build, and a small corroboration that this is the official upstream artifact
rather than something rebuilt or repackaged.

### D-068.3 — OPEN-068-A is opened: the patch is unpinned, and that is a real drift risk

`BLENDER_SERIES: '5.2'` pins the series. Nothing pins the patch.

The argument for leaving it unpinned is genuine: within an LTS series, patch
releases are bug fixes, and floating means the pipeline is continuously
tested against the version Umut's own machine would most likely install.

The argument against is stronger for this project specifically. The one
outstanding Milestone 4 blocker, OPEN-051-F, is a **visual** acceptance gate.
Eight of its fifteen criteria are judged by eye in Blender. If CI silently
moves to 5.2.1 while Umut's machine stays on 5.2.0, and a mesh renders
differently, the difference is attributable to nothing in this repository and
there is no record of the change to point at. A floating dependency behind a
visual gate is a bad combination.

**OPEN-068-A — should `BLENDER_SERIES` be replaced by a pinned
`BLENDER_VERSION: '5.2.0'`, with a documented procedure for bumping it
deliberately?** Not decided here. This is a design decision with a real
trade-off, and it should be taken by Umut rather than assumed. Recording it
as a question is the honest state.

### D-068.4 — OPEN-068-B is opened: Node 20 deprecation

Run #208 carried exactly one annotation, a warning, quoted verbatim:

> Node.js 20 is deprecated. The following actions target Node.js 20 but are
> being forced to run on Node.js 24: `actions/checkout@v4`,
> `actions/upload-artifact@v4`.

This does not block anything. Both actions are being force-migrated by the
runner and both completed successfully. It is recorded because a deprecation
warning is a dated promise of a future failure, and the cost of acting on it
now — bumping two action versions — is trivial compared to the cost of
discovering it when the forced migration ends.

**OPEN-068-B — bump `actions/checkout` and `actions/upload-artifact` from
`@v4` to `@v5` in both workflow files.** Deferred, not forgotten. It requires
editing `.github/workflows/validate.yml` (19,229 bytes) and
`.github/workflows/static-validation.yml` (2,386 bytes), and the former is a
full retype under D-053.6. It should be batched with OPEN-066-A, OPEN-066-B
and D-064.7, which all require the same retype, so that the 19 KB file is
rewritten **once** rather than four times.

### D-068.5 — Step timings from run #208, and what they do and do not show

Run #208's step durations, in order, as displayed:

| Step | Duration |
|---|---|
| Set up job | 1s |
| Check out | 1s |
| Install runtime libraries | 6s |
| Resolve and install Blender 5.2 LTS | 20s |
| Record the Blender version actually used | 0s |
| Run `af_smoke_test.py` end to end | 2s |
| Upload pipeline output | 2s |
| Post Check out | 0s |
| Complete job | 0s |

Total 35 seconds, consistent with the 33-second and 35-second figures shown
on the run header at two different moments while it was being read.

This corroborates D-067.3 concretely. The 20-second resolve step is the
download and `xz` extraction of a full Blender archive; that is real work and
it dominates the job, exactly as D-067.3 predicted from reading the workflow
rather than from timing it. The job is not short-circuiting.

**One observation is recorded without being turned into a finding.** The
smoke test itself runs in 2 seconds for seven stages. That is fast. Under the
method note in D-067.3 the correct response is to read the source before
saying anything about it, and that has not been done in this pass —
`af_smoke_test.py` was read in full earlier this session and its stages are
procedural mesh construction with no I/O beyond a report write, which makes
2 seconds plausible rather than suspicious. It is not being logged as a
defect, and it is not being logged as cleared either. If it is ever
investigated, the number to compare against is here.

### D-068.6 — Where 5.2.0 is recorded, and where it is not yet

The value is recorded **here**, and under D-061.2 the tables in the open
decision volume are authoritative. That is sufficient for the record to be
correct and findable.

It is **not** yet in `VERSION_MATRIX.md`. That file is 40,439 bytes. Under
D-053.6 every write from the agent side is a full-file retype, and retyping
40 KB of verified reference material to insert one version string is a
disproportionate corruption risk — the same reasoning that left
`SCRIPT_INVENTORY.md` unedited in D-067.2.

**OPEN-068-C — propagate the Blender 5.2.0 patch version into
`VERSION_MATRIX.md` §5.** To be done when that file is being edited for an
independent reason, or by Umut directly, for whom it is a one-line edit
carrying none of this risk.

### D-068.7 — Correction to the instruction given, not to the record

The procedure handed over for resolving OPEN-067-A was under-specified and
cost Umut a failed attempt. It said to open a `blender-pipeline` job log and
read the `Resolved:` line. Three things were wrong with that:

1. The job's **display name** is `Blender smoke test (headless)`.
   `blender-pipeline` is only the YAML key and appears nowhere in the UI.
2. `Resolved:` prints a **filename**, not a version, so searching the log for
   a bare `5.2` finds nothing useful.
3. Step output is **collapsed by default**, and the browser's find function
   cannot see inside a collapsed group.

The better instruction, established after the fact, is the adjacent step
`Record the Blender version actually used`, whose entire output is the
version banner. It is the shortest step in the job at 0 seconds, which is
also why it is easy to scroll past.

Recorded because the failure mode is general: an instruction that names an
internal identifier instead of the label a human actually sees is not a
usable instruction, and the cost of the error lands on the person following
it rather than the person writing it.

### D-068.8 — What is still not true

Unchanged by anything in D-068, and restated because D-068 closes a question
and closures create a false sense of progress:

* No C++ in this repository has ever been compiled.
* No generated mesh has ever been seen by a human being. Knowing the exact
  Blender version that generated it does not change this.
* **Milestone 4 is not accepted.** OPEN-051-F remains the sole blocker,
  fifteen criteria, eight of them visual and requiring Blender 5.2 LTS on
  Umut's machine with the face-orientation overlay at three angles.
  **Partial pass is fail.**
* D-068 identifies which Blender built the CI artifacts. It says nothing
  about whether those artifacts are correct.

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
| OPEN-066-C | Old project name in two `af_smoke_test.py` literals | closed by D-067.1 |
| OPEN-067-A | Which Blender 5.2.x patch does CI resolve | **closed by D-068.1 — 5.2.0** |
| OPEN-068-A | Should the patch be pinned as `BLENDER_VERSION: '5.2.0'` rather than floating on the series | **open — new** |
| OPEN-068-B | Bump `actions/checkout` and `actions/upload-artifact` from `@v4` to `@v5` | **open — new** |
| OPEN-068-C | Propagate Blender 5.2.0 into `VERSION_MATRIX.md` §5 | **open — new** |

Fifteen entries. Four closed, one narrowed, ten open. OPEN-051-F is still the
only one gating a milestone.

**Batching note.** OPEN-066-A, OPEN-066-B, OPEN-068-B and the deferred
D-064.7 work all require editing `.github/workflows/validate.yml`, a 19,229
byte full retype under D-053.6. They should be done in a single pass. Doing
them separately multiplies the corruption risk by four for no benefit.

---

## Volume status

| Volume | Size | Status |
|---|---|---|
| `DECISION_LOG.md` … `DECISION_LOG_VOL8.md` | — | frozen |
| `DECISION_LOG_VOL9.md` | 19,545 B | frozen at D-066 |
| `DECISION_LOG_VOL10.md` | this file | **open** |
| `CI_EVIDENCE.md` … `CI_EVIDENCE_VOL6.md` | — | frozen |
| `CI_EVIDENCE_VOL7.md` | 11,984 B | **open** |

Next decision id: **D-069**.
