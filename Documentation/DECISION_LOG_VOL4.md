# Uludag Formula - Decision Log, Volume 4

Project: Uludag Formula (ASCII identifier form: UludagFormula)
Author: Umut Sever
Status: ACTIVE volume. New decisions are appended here.

---

## 0. Why a fourth volume

Volume 3 (`Documentation/DECISION_LOG_VOL3.md`) reached 25,950 bytes at commit
`0ca1d70f`, which carries D-051 and D-052. The working rule adopted in D-049 is
that a ledger volume is closed once it passes roughly 20,000 bytes, because
every edit in this environment is a full-file retranscription: there is no patch
mode. The larger a file grows, the higher the probability that a rewrite is
silently truncated, and Markdown has no compile gate that would catch it (see
D-052.5).

Volume history:

| Volume | File | Decisions | Size | State |
|---|---|---|---|---|
| 1 | `Documentation/DECISION_LOG.md` | D-001 - D-044 | 50,726 B | frozen |
| 2 | `Documentation/DECISION_LOG_VOL2.md` | D-045 - D-050 | 20,441 B | frozen |
| 3 | `Documentation/DECISION_LOG_VOL3.md` | D-051, D-052 | 25,950 B | frozen |
| 4 | this file | D-053 onward | - | ACTIVE |

Volumes 1 to 3 are not to be edited again. Corrections to their content are
recorded as new decisions here, with an explicit pointer back to the superseded
text.

---

## D-053: Batch-4 outcome, total-coverage policy, timing correction, and the failed local rehearsal gate

Date recorded: 2026-08-11
Status: ACCEPTED
Supersedes: nothing
Relates to: D-049 (triage before rewrite), D-051 (measurement findings),
D-052 (lockstep rule, Markdown has no compile gate), OPEN-051-B

### D-053.1 Context

Wave 1 (display identity and documentation prose) and Wave 1.5 (Python tooling
and `Documentation/VERSION_MATRIX.md`) are both content-complete and verified.
Six continuous-integration batches have been executed against pull requests #17
through #22. Every batch returned ten check runs, all `success`.

At the time of writing, the repository head on `main` is `3a20762b`, which
carried section 8 of `Documentation/CI_EVIDENCE_VOL3.md`. That commit records
batch 4 but had not itself been covered by any batch. This decision records the
outcome, the policy that follows from it, a correction to the polling recipe,
and one gate that was attempted and failed.

### D-053.2 Batch-4 outcome (recorded)

Marker file: `Documentation/CI_MARKER_WAVE2_4.md`, on the disposable branch
`ci/wave2-verify-4` only. Marker commit `5961d95b`, blob `be954418`, 1,480
bytes, author date `2026-08-11T22:39:47Z`. Pull request #22, draft, head
`ci/wave2-verify-4`, base `main`.

Result: ten check runs, all `success`. Every `started_at` value was later than
the marker author date, which is the acceptance threshold. The pull request was
closed without merging, as required: marker branches never merge into `main`.

The four workflow runs were `31543367878`, `31543367943`, `31543375917` and
`31543375920`. The full job identifier list is recorded in section 8.1 of
`Documentation/CI_EVIDENCE_VOL3.md` and is not duplicated here.

Batch 4 covered, among others, commit `0ca1d70f` (D-052, 25,950 bytes) and the
section-7 state of the evidence file. It did not and could not cover `3a20762b`,
because that commit was authored after the marker.

### D-053.3 Total-coverage policy (formalised)

The policy first stated in section 8.3 of `Documentation/CI_EVIDENCE_VOL3.md` is
promoted here to a project decision:

> Every commit on `main` must be covered by at least one green batch, including
> the commits whose only purpose is to record a previous batch.

The consequence is a deliberate, terminating chain rather than an infinite
regress. Recording batch N produces a commit; that commit is covered by batch
N+1; the commit that records batch N+1 is covered by batch N+2. The chain
terminates whenever a batch is run that verifies an evidence commit and no
further evidence commit is written until new substantive work lands.

In practice this means the correct ordering inside one cycle is:

1. Land all substantive work on `main`.
2. Land the evidence and ledger commits for the previous cycle.
3. Only then branch, mark, open the draft pull request, and poll.

Following that order lets a single batch cover both the substantive work and the
bookkeeping, instead of requiring one batch per commit. Batch 5 is scheduled
under exactly this rule: it must cover `3a20762b` and the commit that introduces
this file.

### D-053.4 Timing correction to the polling recipe

The recipe used through batch 3 was: sleep 55 seconds, then perform a single
check-run query, then accept ten of ten. Batch 4 falsified the assumption behind
the single poll.

Measured: the second headless Blender job, identifier `93950566548`, started at
`22:40:16Z`, which is 29 seconds after the marker author date, and completed at
`22:40:57Z`, which is 70 seconds after it. A poll at 55 seconds therefore
observed ten runs of which only nine had completed, with that job still
`in_progress`.

Decision:

1. Fifty-five seconds is a lower bound, not a guarantee of completion.
2. A reading of nine completed out of ten with any run `in_progress` must be
   **rejected**, never rounded up, never reported as a pass.
3. On such a reading, sleep a further 40 seconds and poll again.
4. The second poll must be issued with at least one **varied argument**, for
   example an explicit results-per-page value, because the harness deduplicates
   tool calls that carry identical arguments and will otherwise refuse to
   re-issue the query.

Applying steps 3 and 4 to batch 4 produced ten of ten `success`. This correction
is also recorded in sections 5 and 8.4 of `Documentation/CI_EVIDENCE_VOL3.md`.

### D-053.5 Environment lesson: file creation does not create parent directories

The local file-creation tool does not behave like `mkdir -p`. Attempting to
create a file at a path whose parent directory does not exist fails outright
with a message stating that the parent directory must be created first, and the
file content is discarded.

Cost of learning this: an entire multi-kilobyte transcription was composed and
then lost, because the target directory did not exist at the moment of the call.

Rule adopted: when writing to any new local path, issue a directory-creation
command first and confirm its exit status, then create the file. This applies
only to local scratch paths. Repository writes go directly through the remote
write tool and are unaffected, because the remote write tool creates
intermediate directories implicitly.

### D-053.6 Local rehearsal gate: attempted, NOT MET

Goal of the gate: run `Tools/af_mesh_quality.py --self-test` locally and observe
the expected result of 46 of 46 cases passing with exit status 0. The module is
suitable for this because its self-test mode imports only `argparse`, `math`,
`os` and `sys`, does not import the mesh generator, and hard-codes the expected
case total. It is therefore the only guard in the repository that can be
exercised end to end without Blender or Unreal being installed.

What happened:

1. The full 30,783-byte body of the module was fetched successfully and
   returned inline. Its self-test structure was read and its case total
   confirmed as 46, distributed across vector helpers, triangulation, area and
   normal, volume, bounds, checks C1 through C10, and report behaviour.
2. A file-creation call was issued to write the module to a local scratch path.
   It failed for the reason recorded in D-053.5. No file was written.
3. The scratch directory was then created successfully.
4. Before the creation call could be retried, a context compaction occurred. The
   fetched body was evicted from working context. Only the structural summary
   survived.
5. A file was then composed from that structural summary. It was approximately
   13 kilobytes against a true size of 30,783 bytes. It omitted the collision
   sanity checks C11a through C11d and the design envelope check C12, and it
   stubbed the non-self-test code path.

Decision: that reconstruction was **deleted without being executed**, and the
gate is recorded as **NOT MET**.

Rationale. Running a reconstruction and reporting the result would have produced
a number that looks like evidence about the repository file but is not. The
reconstruction is a different program. Its self-test would still have exercised
46 hard-coded cases and would very likely have printed a passing line, which is
precisely what makes it dangerous: a plausible-looking result with no
evidentiary link to the artifact under test. The project rule that untested work
is never described as complete extends to this: **evidence about a file must be
produced by that file, byte for byte.**

Conditions under which the gate may be retried:

1. The module must be re-fetched and transcribed **byte-faithfully**, decoding
   the escaped forms of quote, plus, less-than, greater-than and backtick that
   the transport layer introduces.
2. The on-disk size must be verified as exactly **30,783 bytes** before the
   self-test result is trusted.
3. The fetch and the write must occur at the start of a turn, with an
   essentially empty working context, because a 30-kilobyte artifact cannot
   survive a mid-turn compaction.

If condition 1 or 2 cannot be satisfied, the gate stays NOT MET and is reported
as such. It is not to be quietly downgraded to "approximately verified".

### D-053.7 OPEN-051-B remains open

The drift-guard self-test count discrepancy is unresolved. The guard's own
banner reports 27 cases. `Documentation/VERSION_MATRIX.md` states 31 cases over
17 methods. A static reading of the guard's dispatcher counts 16 methods
emitting 6 plus 5 plus 4 plus 1 plus 11 plus 4, which totals 31.

Continuous integration cannot settle this, because no workflow invokes any
guard's self-test mode; the workflows perform syntax compilation and the static
validation entry point only. Settling it requires the same byte-faithful local
copy procedure described in D-053.6, applied to `Tools/af_drift_guard.py`, which
is 38,569 bytes.

Until then the discrepancy is recorded, not guessed at, and neither number is
propagated into any other document as though it were settled.

### D-053.8 Honest scope statement

Six green batches prove the following and nothing beyond it:

* Every Python artifact in `Tools/` and `BlenderPipeline/scripts/` compiles
  under both Python 3.9 and Python 3.12.
* The static validation entry point exits zero, meaning the declared module
  graph, dependency table, prohibited-identifier rules, copyright header rule
  over C++ sources, required configuration keys and bone-name expectations are
  all internally consistent.
* The headless Blender smoke test completes.

They do **not** prove any of the following, none of which has ever been done in
this project:

* No C++ has been compiled. No build tool has been invoked.
* No Unreal project has been opened.
* No exported mesh has been imported into an engine.
* No mesh has been inspected visually, including the face-orientation check that
  would independently confirm the winding defect fix.
* No lap has been driven. No playtest has occurred.

Milestone 2 remains the last milestone with a merged implementation, and only
one of its four acceptance criteria was met. Milestones 1, 3 and 4 cannot be
advanced from this environment at all, because the environment has no engine, no
digital content creation tool, no version control binary and no network egress.
Advancing them requires the work to be run on the author's own machine.

### D-053.9 Consequences

1. Batch 5 is mandatory and must cover `3a20762b` and the commit that introduces
   this file. It is recorded as section 9 of
   `Documentation/CI_EVIDENCE_VOL3.md`, plus a seventh row in that file's batch
   index in section 6.
2. The polling recipe in all future batches follows D-053.4, including the
   varied-argument rule for the second poll.
3. The rehearsal gate and OPEN-051-B stay open and are listed as open, not as
   deferred and not as approximately done.
4. Wave 2A, the module and project-file migration, is unblocked with respect to
   policy but has not started. Its ordering and its per-module atomic commit
   sets are fixed by D-051.4 and D-052.2 and are not revisited here.

---

## Open questions carried into Volume 4

| Id | Question | State |
|---|---|---|
| OPEN-051-B | Drift-guard self-test count: 27 reported versus 31 counted | OPEN, needs byte-faithful local copy |
| OPEN-051-D | Volume 2 header says it starts at D-047 while its index lists D-045 and D-046 | OPEN, volume frozen, correction lives here |
| OPEN-051-E | The binding master specification still fixes the root identity as the previous product name; only the author can update his own copy | OPEN, outside repository control |
| OPEN-051-F | Blender visual verification never performed: face orientation overlay, measured bounds, halo apex | OPEN, requires the author's machine |
| OPEN-052-B | Eight previous-identity strings deliberately retained in `Documentation/VERSION_MATRIX.md` | OPEN by design, resolves atomically in wave 2A |
| OPEN-052-C | Section 5.28 of `Documentation/VERSION_MATRIX.md` quotes a historical check count as a Milestone 1 figure | OPEN, must never be silently refreshed |
| OPEN-053-A | Local rehearsal gate for `Tools/af_mesh_quality.py` | OPEN, recorded NOT MET in D-053.6 |
| OPEN-M4-01 | Whether the bodywork pull request should be merged or closed | OPEN, undecided |

Closed in earlier volumes: OPEN-051-A, OPEN-051-C, OPEN-052-A.
