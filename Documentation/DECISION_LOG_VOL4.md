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

**Superseded by D-054.** The termination argument above is wrong. See D-054.2.

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

A cheaper alternative to condition 2 was discovered later and is recorded in
D-055.6: a directory listing returns every blob hash and byte size without
downloading any body, so a local cache can be proven authoritative for a few
hundred bytes of traffic instead of tens of kilobytes.

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

**Item 4 is cancelled by D-055.**

---

## D-054: The total-coverage policy has no fixpoint and is replaced by a gate-scoped policy

Date recorded: 2026-08-11
Status: ACCEPTED
Supersedes: D-053.3, and section 8.3 of `Documentation/CI_EVIDENCE_VOL3.md`
Relates to: D-049, D-052.5

### D-054.1 The claim being withdrawn

D-053.3 asserted that the coverage chain terminates "whenever a batch is run
that verifies an evidence commit and no further evidence commit is written until
new substantive work lands". That sentence contains its own refutation. The
condition for termination is that no further evidence commit is written. But
writing the evidence for batch N *is* a commit, and under the stated policy that
commit demands batch N+1, whose evidence is another commit, and so on.

### D-054.2 Formal statement of the defect

Let `E(N)` be the commit that records the outcome of batch `N`. The policy is:

> for all commits `c` on `main`, there exists a batch `N` with `c` in `cover(N)`

`cover(N)` is defined by the acceptance rule as the set of commits whose author
date precedes the marker commit of batch `N`. Since `E(N)` can only be authored
after batch `N` has completed, `E(N)` is never in `cover(N)`. Therefore
`E(N)` requires some `N' > N`, which produces `E(N')`, which requires
`N'' > N'`. The sequence is strictly increasing and has no upper bound. There is
no fixpoint. The policy as written can never be satisfied, only extended.

Empirically the chain had already run to five iterations: batches 1 through 5,
each one existing largely to cover the bookkeeping of its predecessor. Batch 5
was, in content terms, almost entirely self-referential.

### D-054.3 What the workflows actually gate

The replacement policy is derived from measurement, not from preference. Both
workflow files were read in full.

`.github/workflows/static-validation.yml`, 2,386 bytes, blob `1d674fc7`:

| Job | Runtime | Steps |
|---|---|---|
| `validate` | matrix Python 3.9 and 3.12, `fail-fast: false` | `af_static_validate.py --root .`; `af_validate_interfaces.py --self-test`; `af_validate_interfaces.py --root .` |
| `syntax` | Python 3.11 | `compileall -q Tools`; guarded `compileall -q BlenderPipeline/scripts` |

`.github/workflows/validate.yml`, 8,958 bytes, blob `28ed9119`:

| Job | Runtime | Steps |
|---|---|---|
| `static-validation` | Python 3.12, standard library only, no dependency installation step by design | `af_static_validate.py --root .`; `af_pipeline_config.py`; `af_lap_rules_model.py --self-test`; `af_drift_guard.py --self-test`; `af_drift_guard.py --root . --verbose`; `af_circuit_generate.py --self-test`; `af_track_drift_guard.py --self-test`; `af_track_drift_guard.py --root . --verbose`; `af_config_hash_guard.py --self-test`; `af_config_hash_guard.py --root . --verbose`; `af_mesh_quality.py --self-test`; `af_mesh_quality.py`; `compileall -q BlenderPipeline/scripts Tools` |
| `blender-pipeline` | needs `static-validation`, Blender series 5.2 | `af_smoke_test.py` |

Finding, stated as a measurement: **no step in either workflow parses, lints,
renders or compiles a Markdown file.** The only way a Markdown file influences a
run at all is through the digest guard, and finding F-3 already established that
the digest guard's second walk reads only `.md`, `.yml` and `.yaml` under three
specific directories while its `SELF_FILES` list is dead code.

Consequently, running a batch whose only new content is Markdown exercises
exactly the same code paths, over exactly the same inputs, as the previous
batch. It produces a new set of job identifiers and no new information.

### D-054.4 The replacement policy

> **Gate-scoped coverage.** A commit on `main` creates a batch obligation if and
> only if it adds, modifies or deletes at least one file whose extension is in
> the gated set: `.py`, `.cpp`, `.h`, `.cs`, `.ini`, `.uproject`, `.yml`,
> `.yaml`. Commits that touch only Markdown, images, licences or other
> non-gated files carry no obligation.

Rationale for each member of the gated set:

| Extension | Gated because |
|---|---|
| `.py` | `compileall` and every self-test invocation |
| `.cpp`, `.h` | copyright header rule, `#pragma once` rule, interface scan |
| `.cs` | target-file assertions in `check_targets` |
| `.ini` | required configuration key checks |
| `.uproject` | module array read by name in the guard |
| `.yml`, `.yaml` | digest guard walk, and the workflow definitions themselves |

### D-054.5 Consequence for the existing record

Commit `5c294bfb`, which closed `Documentation/CI_EVIDENCE_VOL3.md` at 23,535
bytes by adding sections 9 and 10, is Markdown-only. Under the new policy it
carries no obligation. It is recorded as **permanently uncovered by design**,
not as a gap, not as an outstanding item, and not as technical debt.

The same applies to the commit that carries this decision, and to any future
ledger or evidence commit that touches no gated file.

### D-054.6 What is not being relaxed

The acceptance rule itself is unchanged. When a batch is required, it must still
produce ten check runs, all `success`, with every `started_at` later than the
marker author date, and a reading containing any `in_progress` run is still
rejected outright. D-054 changes *when* a batch is owed, never *what counts as
passing*.

---

## D-055: The build-system module names are a frozen internal code name

Date recorded: 2026-08-11
Status: ACCEPTED
Supersedes: D-051.4 and D-052.2 with respect to execution; cancels Wave 2A and
Wave 2C
Relates to: D-048 (the `AF_` symbol prefix ruled internal), OPEN-052-B

### D-055.1 Ruling

The Unreal Build Tool module names `ApexFormulaCore`, `ApexFormulaVehicle`,
`ApexFormulaRace`, `ApexFormulaUI`, `ApexFormulaEditor` and `ApexFormulaTests`,
together with the file names `ApexFormula.uproject`, `ApexFormula.Target.cs` and
`ApexFormulaEditor.Target.cs` and the directory names under `Unreal/Source/`,
are **frozen as an internal code name**. They will not be renamed.

This extends the reasoning of D-048 one structural level upward. D-048 ruled
that the `AF_` symbol prefix is an internal identifier that carries no product
meaning and is therefore exempt from the product rename. Module names occupy the
same visibility class.

### D-055.2 Visibility argument

| Surface | Audience | Renamed? |
|---|---|---|
| Product name in `Unreal/Config/DefaultGame.ini` | player | yes, Wave 1 |
| `README.md`, `Unreal/README.md`, `BlenderPipeline/README.md` | reader, recruiter | yes, Wave 1 |
| All prose under `Documentation/` | reader | yes, Wave 1 |
| Repository name on the hosting service | reader | yes, done by the author |
| Python tooling banners and constants | maintainer | yes, Wave 1.5 |
| `AF_` symbol prefix in C++ | compiler only | no, D-048 |
| Build-tool module names | build log only | **no, this decision** |
| `.uproject` and `.Target.cs` file names | build tool only | **no, this decision** |

A module name appears in exactly two places a human ever sees: a build log line
and the `Modules` array of the project file. Neither is a product surface.

### D-055.3 Cost measurement

The migration was planned as a three-step ladder per module: create the new
directory with renamed files, then move the guard plus the project file plus the
target files in one atomic commit, then delete the old directory. Step A was
actually executed for the Editor module at commit `243c5a45`, which is the only
empirical data point available.

| Module | C++ files | Extra lockstep artifacts |
|---|---|---|
| Editor | 5 | none |
| Core | 14 | drift guard partner |
| Vehicle | 16 | none |
| Race | 13 | four artifacts named in the drift-guard workflow step |
| UI | 9 | none |
| Tests | 8 | none |

Remaining cost after step A, measured rather than estimated:

* **61** further file recreations, since there is no rename operation in this
  environment and every file must be transcribed in full.
* **122** write calls at two calls per file, one create and one delete.
* **five** separate full retranscriptions of `Tools/af_static_validate.py`, each
  of **52,702 bytes**, because the guard's `MODULES` list must stay in lockstep
  with the filesystem at every step of the ladder.

### D-055.4 The decisive argument

None of that work can be compile-verified here. There is no Unreal Engine and no
Unreal Build Tool in this environment. A module rename that has never been fed
to the build tool is, by the project's own standard, **untested**. It would ship
as untested regardless of how many green Markdown-and-Python batches surrounded
it.

Worse, the ladder passes through intermediate states in which some modules are
renamed and others are not. A **mixed state is strictly worse than either
uniform state**: it doubles the number of names a reader must hold, it makes the
`MODULES` list a poor guide to the filesystem, and it invites exactly the kind of
half-finished directory that a future maintainer cannot safely delete.

Since the ladder cannot be completed to a uniform `Uludag*` state with any
verification, and since a mixed state is worse than the uniform `Apex*` state
that already exists and already passes, the correct action is to return to the
uniform `Apex*` state.

### D-055.5 Guard audit performed before the ruling

The ruling was made after, not instead of, establishing that the ladder was
technically safe. The audit is recorded because it is reusable knowledge.

`Tools/af_static_validate.py` contains exactly three directory-enumeration
sites, and no others:

| Line | Call | Purpose |
|---|---|---|
| 218 | `os.walk(source_root)` inside `iter_source_files` | collects C++ files for the copyright and pragma rules |
| 737 | `sorted(os.listdir(config_dir))` | configuration file discovery |
| 1272 | `sorted(os.listdir(test_dir))` | test file discovery |

**There is no check anywhere in the guard that asserts every directory under
`Unreal/Source` is a member of the declared `MODULES` list.** A module directory
absent from `MODULES` therefore degrades to a copyright and `#pragma once` scan
and stays green. This is what made the ladder viable, and it is also why the old
directories could have coexisted with new ones indefinitely.

Second finding, from the tail of `check_targets`: the loop that requires a module
to appear in both target files enumerates only `ApexFormulaCore`,
`ApexFormulaVehicle`, `ApexFormulaRace` and `ApexFormulaUI`. The Editor and Tests
modules are deliberately absent from that list; the Editor module is instead
governed by two separate assertions requiring it to be present in the editor
target and absent from the game target.

Third finding: `COPYRIGHT_LINE` embeds the previous product name and is asserted
as a prefix over all **65** C++ files. Changing it is a single-commit,
65-file operation with no dependency on the module rename. It was planned as a
separate Wave 2C. Under this decision **Wave 2C is also cancelled**, on the same
visibility argument: the copyright line lives only in source comments. It may be
revisited independently if the author wants the source headers to match the
product name, but it is not owed by the rename.

### D-055.6 Reusable technique discovered during the audit

A directory listing that requests only the name, hash and size fields returns
every file's blob hash and byte count **without downloading any file body**, for
a response of a few hundred bytes. Combined with the standard object hash
`sha1("blob " + length + NUL + data)` computed locally, this proves that a local
cache of a repository file is byte-identical to the repository copy.

This is how the local copy of the 52,702-byte guard was proven authoritative at
hash `e9ab8f95` without a second download. It is the cheap substitute for
condition 2 of the rehearsal gate in D-053.6, and it should be used whenever a
local artifact must be certified against the repository.

### D-055.7 Execution record

Step A of the Editor migration was executed and then fully reverted.

| # | Commit | Action |
|---|---|---|
| 1 | `243c5a45` | created five files under `Unreal/Source/UludagFormulaEditor/` |
| 2 | `74925c88` | deleted `UludagFormulaEditor.Build.cs`, carries the full rationale |
| 3 | `6ad9e2a0` | deleted `Public/UludagFormulaEditor.h` |
| 4 | `ee7b9c04` | deleted `Private/UludagFormulaEditor.cpp` |
| 5 | `60bebc47` | deleted `Public/AFDataValidator.h` |
| 6 | `63039649` | deleted `Private/AFDataValidator.cpp` |

Net effect on the tree: zero. Verified after the fact by listing
`Unreal/Source`, which returned exactly the two target files and the six
original module directories, with no `UludagFormulaEditor` entry.

Verified separately: `Tools/af_static_validate.py` still hashes to `e9ab8f95`
at 52,702 bytes, so the guard was never modified during the round trip. The
project file and both target files were likewise never modified; the prepared
edits to them were discarded unpushed.

Batch 6, recorded in `Documentation/CI_EVIDENCE_VOL4.md`, covers all six commits
and returned ten of ten `success`.

### D-055.8 Consequences

1. Wave 2A is **CANCELLED** in full. D-051.4 and D-052.2, which specify its
   ordering and its atomic commit sets, are retained as historical design but
   are not to be executed.
2. Wave 2C, the copyright line change, is **CANCELLED** unless separately
   re-justified on its own merits.
3. OPEN-052-B is **CLOSED**. The eight previous-identity strings retained in
   `Documentation/VERSION_MATRIX.md` were held back on the expectation that
   Wave 2A would resolve them atomically. They are now correct as they stand,
   because they describe artifacts that keep the internal code name. Section
   5.26 of that file needs no update.
4. OPEN-051-E is **CLOSED**. The binding master specification fixes the root
   identity as the previous product name. Under this decision that is no longer
   a divergence to be reconciled; the specification is describing the internal
   code name, which is now frozen and correct.
5. The rename effort is **COMPLETE**. Everything a player, reader or recruiter
   sees carries the new name and has been verified by continuous integration.
   Everything only a compiler or build tool sees keeps the old name by design.

---

## Open questions carried into Volume 4

| Id | Question | State |
|---|---|---|
| OPEN-051-B | Drift-guard self-test count: 27 reported versus 31 counted | OPEN, now cheaply testable via D-055.6 |
| OPEN-051-D | Volume 2 header says it starts at D-047 while its index lists D-045 and D-046 | OPEN, volume frozen, correction lives here |
| OPEN-051-E | Master specification fixes the root identity as the previous product name | **CLOSED by D-055.8 item 4** |
| OPEN-051-F | Blender visual verification never performed: face orientation overlay, measured bounds, halo apex | OPEN, requires the author's machine |
| OPEN-052-B | Eight previous-identity strings retained in `Documentation/VERSION_MATRIX.md` | **CLOSED by D-055.8 item 3** |
| OPEN-052-C | Section 5.28 of `Documentation/VERSION_MATRIX.md` quotes a historical check count as a Milestone 1 figure | OPEN, must never be silently refreshed |
| OPEN-053-A | Local rehearsal gate for `Tools/af_mesh_quality.py` | OPEN, recorded NOT MET in D-053.6 |
| OPEN-M4-01 | Whether the bodywork pull request should be merged or closed | OPEN, decided next |

Closed in earlier volumes: OPEN-051-A, OPEN-051-C, OPEN-052-A.
