# Decision log, volume 8

Volume 7 was closed by size at 23,235 bytes. This volume continues the
record from D-064 onward.

The rules are unchanged. A closed volume is never edited; an error in one is
corrected by an erratum in the open volume. The tables in the open volume
are the authoritative copies (D-061.2).

## Volume history

| Vol | File | Decisions | Bytes | State |
|---|---|---|---|---|
| 1 | `DECISION_LOG.md` | D-001..D-044 | 50,726 | frozen |
| 2 | `DECISION_LOG_VOL2.md` | D-045..D-050 | 20,441 | frozen |
| 3 | `DECISION_LOG_VOL3.md` | D-051..D-052 | 25,950 | frozen |
| 4 | `DECISION_LOG_VOL4.md` | D-053..D-055 | 27,898 | frozen |
| 5 | `DECISION_LOG_VOL5.md` | D-056..D-058 | 20,132 | frozen |
| 6 | `DECISION_LOG_VOL6.md` | D-059..D-061 | 19,640 | closed |
| 7 | `DECISION_LOG_VOL7.md` | D-062..D-063 | 23,235 | closed |
| 8 | `DECISION_LOG_VOL8.md` | D-064.. | open | **open** |

---

# D-064. The export determinism gate

## 64.1 What was decided

`MILESTONE_4_IMPLEMENTATION_VOL2.md` section 6 listed, as the first item of
remaining work that does not require Umut's machine, a CI-gateable check
that the mesh exporter writes the same bytes twice. That check is now
implemented, rehearsed, committed and green. It lives in
`.github/workflows/validate.yml`, which grew from 14,140 to 19,229 bytes in
commit `a5ed3bfb5c384bd61f5385d92a5dc000affc9de9`, and its CI result is
recorded as batch 10 in `CI_EVIDENCE_VOL6.md`.

Status label: **tested**. Not verified. See 64.7.

## 64.2 Why no new guard module was written

The obvious implementation was a new `Tools/af_export_determinism.py` that
would drive the exporter, hash the outputs and compare. It was rejected.

`af_mesh_export.py` already has a `--dump` entry point that writes the full
export tree to a directory given on the command line. Everything the check
needs already exists. A new module would have been roughly three hundred
lines of code whose only reason to exist is to make a check possible, and
this repository already carries seven files in `Tools/` totalling more than
226 KB, all of them guards. Guard code has the same defect rate as any other
code, needs the same tests, and rots the same way, but it produces nothing a
user ever sees. The bar for adding more of it should be high, and "I could
have done it in the workflow instead" clears that bar in the wrong
direction.

So the check is workflow-only: two invocations of an entry point that
already exists, and a comparison. It adds no importable surface, no new
test burden, and no new file to keep in sync with the config.

## 64.3 Why it is not a new job

The step sits inside the existing `static-validation` job, at index 16 of
18, rather than being a job of its own. A separate job would have added a
sixth named check run and changed the shape of every future batch, making
the ten-run batches in volumes 1 through 5 non-comparable with everything
after. It would also have paid a second runner startup and a second
checkout to run one command twice. The evidence in
`CI_EVIDENCE_VOL6.md` section 10 accordingly attributes the determinism
result to check runs 3, 6 and 14, the three `Static validation (no engine,
no DCC)` runs, and says so explicitly rather than letting the reader assume
a dedicated check exists.

## 64.4 The defect the rehearsal caught

This is the substantive finding of D-064 and the reason the rehearsal step
was worth the time it cost.

The comparison was first drafted as:

```
if ! diff -r "$a" "$b"; then
  echo "::error::export not reproducible"
  exit 1
fi
```

That is wrong. `diff` exits 0 when the trees match, 1 when they differ, and
127 when the command is not found. `! diff` treats 1 and 127 identically, so
a runner image without `diff` on `PATH` would report a determinism failure
that had nothing whatever to do with determinism. The failure message would
name the wrong cause, and the person debugging it would go looking at the
serialiser.

It was found because of the rule that a check which has only ever passed has
not been tested (D-046). The step body was extracted from the committed YAML
and run against stand-in exporters in five scenarios. The first run reported
three passes and one failure. The three passes were false: this sandbox does
not have `diff` installed at all, so those cases were exiting non-zero
because of the missing binary, and the harness was reading that as the
intended behaviour. The failing case was failing for the same reason.

Had the rehearsal not been run, this would very likely never have fired,
because GitHub's runner images do ship `diff`. It would have sat in the
workflow as a latent trap, correct-looking and wrong, waiting for an image
change. That is the worst class of defect in a guard: one that makes the
guard lie about *why* it failed.

## 64.5 The replacement, and the vacuity guard

`diff` was replaced with an inline `python3` heredoc that walks both trees
with `os.walk`, sorting `dirnames` and `filenames` so traversal order is
stable, builds a `{relpath: (length, sha256)}` map for each side, and
reports three categories separately: paths present only in the first tree,
paths present only in the second, and paths present in both whose contents
differ. Each category is emitted as its own `::error::` line before the
summary error, so a failure says which files and in what way.

It also fails when the tree is empty. That guard is not decoration. A
comparison of two empty directories succeeds trivially, so an exporter that
silently produced nothing at all, or a `--dump` invocation whose output path
was wrong, would have passed the gate cleanly and reported reproducibility.
A check that passes when the thing it checks did not happen is worse than no
check, because it is credited in the record.

On success the step prints
`export determinism: N files, M bytes, byte-identical across two runs`.

The rehearsal was then re-run over five cases: deterministic output,
non-deterministic output, a file present in one tree only, an exporter that
crashes, and an exporter that produces nothing. All five behaved correctly,
and each was confirmed to be passing for the intended reason rather than
incidentally.

## 64.6 The YAML round trip, and the false one-byte alarm

Two verification steps were run before commit, and the second one produced a
wrong answer that is worth recording.

First, the step body was extracted **back out of the parsed YAML** with a
script that loads the file, prints the step inventory, and writes the
extracted `run:` block to disk. The rehearsal was then re-run against that
extracted copy rather than against the hand-written original. This matters
because YAML block scalars strip the common leading indentation, so the
`<<'PY'` heredoc marker and its terminating `PY` both have to land in column
0 after dedent. Reasoning about that is not the same as checking it. All
five cases passed again against the extracted body, so what CI executes is
what was rehearsed.

Second, a fidelity check compared the reconstructed 19,229-byte file against
the 14,140 bytes known to be live, by removing the added span and requiring
the remainder to match the original byte count exactly. It reported a
one-byte discrepancy.

The instinct was to hunt for a dropped character in the retype. The cause
was in the checker: it sliced the added span as `lines[start:end-1]`, and
line 307 was a blank line belonging to the added block, so the remainder
kept one byte it should have dropped. Corrected to `lines[start:end]`, the
remainder came out at exactly 14,140 bytes, delta zero. The reconstruction
had never been wrong.

The lesson, recorded because it will recur: when a fidelity check disagrees
by a single byte, the checker's own arithmetic is the first suspect, not the
data. But do not commit on that suspicion. Prove which of the two is wrong,
then commit. The proof here took one edit and one re-run.

After commit, the remote reported the blob at 19,229 bytes, exactly the
local size. That confirms the retype introduced no length error. It cannot
rule out a compensating substitution of one character for another, and it is
not claimed to. YAML has a compile gate behind it, so a transcription error
of that kind turns CI red rather than rotting quietly; this is precisely the
asymmetry that justified opening a new evidence volume rather than retyping
the old one, recorded in `CI_EVIDENCE_VOL6.md` section 0.

## 64.7 What the gate proves, and what it does not

It proves that two consecutive `--dump` runs, under one interpreter, inside
one workflow run, on a hosted runner that is not the author's machine,
produce byte-identical output trees.

It does not prove determinism across Python versions, across platforms, or
across time. It does not prove the export is *correct*: a serialiser that
reproducibly emits the wrong vertex passes this gate without complaint.
Stability and correctness are different properties and are being kept apart
on purpose.

One further limitation is structural and currently unfixable from here.
GitHub step-level logs are not reachable from this environment, so the
`export determinism: N files, M bytes` line cannot be read back. What the
runner proves is exit status. The locally measured figures from the D-059
session were 26 files totalling 112,123 bytes, on one machine, never checked
by CI. If the runner's figures differ from those, that is a finding to
record, not a discrepancy to suppress — and at present it would go
unnoticed. Making that line readable, most likely by having the step write a
small artifact, is the honest next improvement to this gate, and it is not
being claimed as done.

## 64.8 On local execution, and why it was not attempted

The correct way to develop this would have been to run the real
`af_mesh_export.py --dump` locally first. That was ruled out under D-053.6
and the ruling is restated here because it keeps coming up.

File content retrieved through the available interface must be **retyped**
to reach the sandbox disk. What lands there is a reconstruction, not a copy.
Running self-tests against a 23,654-byte reconstruction and reporting the
result as "the self-tests pass" would be reporting on a file that does not
exist anywhere else. The rehearsal therefore used deliberate stand-in
exporters, which prove things about the *check*, and prove nothing about the
real asset. The rehearsal figure of 26 files and 8,320 bytes is an artefact
of the stand-ins and must never be quoted as a project measurement.

## 64.9 The CI evidence route was rebuilt

The method used for batches 1 through 9 stopped working. It relied on a
long-lived draft pull request, #27, whose head branch could be repointed at
each new marker commit. `list_pull_requests` with state `open` returned an
empty list at the start of this batch: #27 is closed and nothing inherited
its role.

The constraint behind this is worth stating because it will keep dictating
the shape of the evidence: no interface available here can list check runs
for a bare branch. Commits pushed straight to `main` generate check runs
that exist and cannot be read. A pull request is the only handle on them.

The replacement pattern, now used for batch 10 and intended to be reused:
branch at the marker commit, open a draft pull request with that branch as
**head**, and pick as **base** any ancestor far enough back that the diff is
non-empty, since an empty pull request is rejected. Batch 10 used the
leftover `ci-batch-9-mesh-export` branch as base.

This makes the pull request's diff meaningless as a change proposal — it
contains everything since batch 9, which is not a reviewable unit. That is
tolerable only because the pull request is a reading device that will never
be reviewed or merged. It is marked draft, titled to say so, and its body
says so in the first line. It must be closed unmerged like every evidence
pull request before it.

A side effect worth recording: this route fires the workflow three times
against the same commit — push to `main`, branch creation, pull request
opening — so batch 10 has fifteen check runs where earlier batches had ten.
All fifteen are listed individually in `CI_EVIDENCE_VOL6.md` section 10,
grouped by wave. They are not folded into a round number, and the batch is
not described as a ten-run batch.

## 64.10 A rejected read, recorded

The first check-run read of batch 10 returned `total_count` 14, of which
four were `queued` and three `in_progress`. Seven were green. That is not a
result and was not treated as one, under D-053.4: a partial read is never
rounded up, and "seven of fourteen green so far" has no place in an evidence
log. The read was repeated after a wait, by which point the count had
settled at 15 and every run had reached `completed` with conclusion
`success`. The rejected first read is recorded in the evidence volume too,
because a record that only shows the reads that worked is a record that has
been curated.

## 64.11 OPEN-064-A, two unexplained size deltas

Two live file sizes disagree with what the decision log records. Neither is
resolved and neither is being quietly overwritten.

| File | Recorded | Live | Source of the record |
|---|---|---|---|
| `Tools/af_config_hash_guard.py` | 26,517 bytes | **26,519** | D-046 |
| `Tools/af_mesh_quality.py` | "773 lines"; a "~13 KB reconstruction" | **30,783 bytes** | D-047, D-053.6 |

The first is a two-byte difference, small enough to be a transcription slip
in D-046 and large enough that guessing is not acceptable. The second is not
a small discrepancy at all: a 30,783-byte file was described in D-053.6 as
having been reconstructed at roughly 13 KB, which means either the
reconstruction covered less than half the file or the figure was wrong when
written.

Both are raised as **OPEN-064-A**. The standing rule applies: never
reconcile a discrepancy by adjusting either number to match the other. The
resolution requires reading both files in full and determining which record
is wrong, which is a read this session did not perform.

---

## Open questions

| Id | Subject | State |
|---|---|---|
| OPEN-051-B | Drift guard banner says 27; the counterparty is still unidentified. `VERSION_MATRIX.md` has been eliminated as the source. | open |
| OPEN-051-F | Blender visual verification of the exported bodywork. Gate defined by D-060 and written out in `MILESTONE_4_VISUAL_ACCEPTANCE.md`. Blocked only on Umut's machine. | open |
| OPEN-053-A | Local rehearsal gate for `af_mesh_quality.py`. **Not met**, and unachievable in this environment under D-053.6. | open |
| OPEN-060-A | 936 historical faces versus 798 serialised faces. Never to be reconciled by adjusting either number. | open |
| OPEN-063-A | `VERSION_MATRIX.md` section 5.20 says eight `af_*.py` scripts; a 2026 listing shows twelve. Never silently refresh the count. | open |
| OPEN-064-A | Two file sizes disagree with D-046 and D-047/D-053.6. See 64.11. | **new** |

Closed, and not to be reopened: OPEN-051-A, OPEN-051-C, OPEN-051-D,
OPEN-051-E, OPEN-052-A, OPEN-052-B, OPEN-052-C, OPEN-M4-01, OPEN-056-A,
OPEN-056-B, OPEN-061-A, OPEN-062-A.

---

## Standing position after D-064

Milestone 4 is **not accepted**. Slices 1 through 3 are implemented and
CI-green; the export path is now additionally shown to be reproducible on a
machine that is not the author's. One hundred and fifteen green check runs
are recorded across six evidence volumes.

None of that is a substitute for looking at the mesh. The single remaining
acceptance item is the fifteen-criterion visual gate in
`MILESTONE_4_VISUAL_ACCEPTANCE.md`: seven numeric criteria measurable from
the exported OBJ, eight visual criteria requiring Blender 5.2 LTS with the
face-orientation overlay enabled. A partial pass is a fail. It cannot be
performed from this environment, and no amount of further CI work will
change that. Additional guards at this point would be motion without
progress.