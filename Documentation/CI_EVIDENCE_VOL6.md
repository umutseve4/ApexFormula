# CI evidence, volume 6

Volume 5 was closed at 11,758 bytes. That is well below the roughly 20 KB
threshold that closed volumes 1 through 4, so the reason is different and
is recorded here rather than left to be guessed at later.

## 0. Why volume 5 was closed early

The only way to write a file to this repository from the current working
environment is to send its complete content to a create-or-update call.
There is no working copy, no `git add`, no patch application. Appending a
section to an existing file therefore means retyping every byte that was
already in it, and then trusting that the retype was perfect.

For a source file that is a survivable risk, because something downstream
checks it. A corrupted YAML file fails to parse and the workflow turns red.
A corrupted Python file fails `compileall` in the next batch. The mistake
announces itself.

An evidence log has no such backstop. If a single digit of a check run id
or a `started_at` timestamp were altered during a retype, nothing anywhere
would notice. The record would still look orderly, still parse as Markdown,
still read as authoritative, and would be wrong. The whole value of this
file is that its numbers were read back from the API rather than recalled,
and a silent retype error destroys exactly that property while leaving the
appearance of it intact.

So the rule from here on, for as long as this toolchain is what is
available:

> An evidence volume is frozen the moment it is committed. New evidence is
> written to a new volume. An existing evidence volume is never retyped,
> not to append, not to reformat, and not to fix a typo. A genuine error in
> a frozen volume is corrected by an erratum in the open volume, which is
> the same rule already in force for the decision logs.

The cost is more volumes, each holding fewer sections. That is a real cost
and it makes the record more tedious to read. It is the cheaper of the two
mistakes.

The rules of the record itself are unchanged from volumes 1 through 5:

1. Every entry names the pull request, the marker commit, and every check
   run by id, with its conclusion and its `started_at`.
2. A batch counts only if every check run reports `success` and each one
   started after the marker commit that triggered it.
3. Evidence pull requests are drafts and are closed unmerged. They are
   never merged into `main`.
4. Nothing here is written from memory. Every value below was read back
   from the GitHub API in the same session that produced it.

---

## 10. Batch 10, the export determinism gate

**Pull request:** #28, `CI evidence batch 10 - export determinism gate (D-064)`
**Head branch:** `ci-batch-10-export-determinism`, created at `a5ed3bfb5c384bd61f5385d92a5dc000affc9de9`, the tip of `main`
**Base:** `ci-batch-9-mesh-export`, **not** `main` (see the method note below)
**Marker commit:** `a5ed3bfb5c384bd61f5385d92a5dc000affc9de9`, authored `2026-08-12T12:45:48Z`
**Disposition:** draft, to be closed unmerged

### What was under test

| Commit | File | Blob | Bytes before | Bytes after |
|---|---|---|---|---|
| `a5ed3bfb5c384bd61f5385d92a5dc000affc9de9` | `.github/workflows/validate.yml` | `b4ad549947eaf1d57c0ce36cce31703bcb501001` | 14,140 | 19,229 |

The change adds one step to the `static-validation` job, `Bodywork export
determinism (double dump, byte comparison)`, at index 16 of 18, between the
mesh export self-test and the `compileall` step. It runs
`af_mesh_export.py --dump` twice into two separate directories and compares
the two trees byte for byte. No new module was added; the step is workflow
only, because `--dump` already existed and a new guard script would have
been code written to make a check possible rather than to make the project
work.

The `.yml` extension is gate scoped under D-054, so this commit owed a batch.
The four commits before it were all Markdown and owed none.

### Method note: the evidence route had to be rebuilt

The procedure recorded in volume 5 section 9 no longer works. It depended on
a long-lived draft pull request, #27, whose branch could be updated to point
at each new marker commit so that check runs could be read through it. At
the start of this batch `list_pull_requests` with state `open` returned an
empty list. Pull request #27 is no longer open, and no other pull request
was available to inherit the role.

The underlying constraint is unchanged and is worth restating because it
will keep forcing this shape: no interface available here lists check runs
for a bare branch. A commit pushed directly to `main` produces check runs
that exist and cannot be read back. A pull request is the only handle.

The replacement, used for this batch and intended as the pattern going
forward:

1. Create a branch at the marker commit, here `ci-batch-10-export-determinism`
   at `a5ed3bfb`.
2. Open a draft pull request whose **head** is that branch, so that the head
   commit is the commit under test.
3. Choose a **base** that is an ancestor far enough back that the diff is
   non-empty, since a pull request with no commits between base and head is
   rejected. Here the base is `ci-batch-9-mesh-export`, an existing branch
   left over from the previous batch.

The base being an old evidence branch rather than `main` makes the diff on
this pull request meaningless as a change proposal. It contains every commit
made since batch 9, which is not a coherent unit of review. That is
acceptable only because this pull request is never going to be reviewed or
merged; it is a reading device. It is marked draft and titled to say so, and
its body says so again in the first line.

### Check runs, all fifteen

Three separate events triggered the workflow against this same commit: the
original push to `main`, the creation of the evidence branch, and the
opening of the pull request. Each fired both workflow files, five check runs
per event. All fifteen are listed. None is discarded, and none is counted
twice.

**Wave A, push to `main`, workflow runs 31598016535 and 31598016588**

| # | Name | Id | Conclusion | started_at | completed_at |
|---|---|---|---|---|---|
| 1 | af_static_validate (py3.12) | 94118196662 | success | 2026-08-12T12:45:53Z | 2026-08-12T12:45:59Z |
| 2 | af_static_validate (py3.9) | 94118196644 | success | 2026-08-12T12:45:53Z | 2026-08-12T12:46:08Z |
| 3 | Static validation (no engine, no DCC) | 94118196388 | success | 2026-08-12T12:45:54Z | 2026-08-12T12:46:04Z |
| 4 | Python syntax check | 94118196608 | success | 2026-08-12T12:46:01Z | 2026-08-12T12:46:09Z |
| 5 | Blender smoke test (headless) | 94118259777 | success | 2026-08-12T12:46:14Z | 2026-08-12T12:46:50Z |

**Wave B, branch creation, workflow runs 31598053110 and 31598053201**

| # | Name | Id | Conclusion | started_at | completed_at |
|---|---|---|---|---|---|
| 6 | Static validation (no engine, no DCC) | 94118317837 | success | 2026-08-12T12:46:19Z | 2026-08-12T12:46:33Z |
| 7 | Python syntax check | 94118317731 | success | 2026-08-12T12:46:19Z | 2026-08-12T12:46:28Z |
| 8 | af_static_validate (py3.12) | 94118317649 | success | 2026-08-12T12:46:20Z | 2026-08-12T12:46:29Z |
| 9 | af_static_validate (py3.9) | 94118317565 | success | 2026-08-12T12:46:20Z | 2026-08-12T12:46:36Z |
| 10 | Blender smoke test (headless) | 94118388777 | success | 2026-08-12T12:46:35Z | 2026-08-12T12:47:10Z |

**Wave C, pull request opened, workflow runs 31598076039 and 31598075981**

| # | Name | Id | Conclusion | started_at | completed_at |
|---|---|---|---|---|---|
| 11 | Python syntax check | 94118395778 | success | 2026-08-12T12:46:36Z | 2026-08-12T12:46:41Z |
| 12 | af_static_validate (py3.12) | 94118395752 | success | 2026-08-12T12:46:36Z | 2026-08-12T12:46:44Z |
| 13 | af_static_validate (py3.9) | 94118395741 | success | 2026-08-12T12:46:36Z | 2026-08-12T12:46:51Z |
| 14 | Static validation (no engine, no DCC) | 94118395665 | success | 2026-08-12T12:46:36Z | 2026-08-12T12:46:43Z |
| 15 | Blender smoke test (headless) | 94118433385 | success | 2026-08-12T12:46:51Z | 2026-08-12T12:47:31Z |

`total_count` reported by the API: 15. Conclusions: 15 `success`, 0 of any
other value. The earliest `started_at` is `2026-08-12T12:45:53Z`, five
seconds after the marker commit at `2026-08-12T12:45:48Z`, so every run in
all three tables postdates the marker.

The first read of this batch was rejected, and the rejection is part of the
record. It returned `total_count` 14, of which four were `queued` and three
`in_progress`. Under D-053.4 a partial read is not a result and is never
rounded up to one. The batch was re-read after waiting, at which point the
count had risen to 15 and every run had reached `completed`.

Note that the new step does not create a check run of its own. It is a step
inside the existing `Static validation (no engine, no DCC)` job, so it is
covered by check runs 3, 6 and 14. Those three are the ones that carry the
determinism result; the other twelve are unaffected by this change and are
recorded because they ran, not because they test anything new.

### What this batch establishes, precisely

On three independent hosted runners, none of them the author's machine,
`af_mesh_export.py --dump` was invoked twice into two different directories
and the resulting trees were compared file by file, name by name, byte by
byte, and the comparison found no difference. Had the two runs disagreed in
any file, or produced a file present in one tree and absent from the other,
or produced nothing at all, the step would have emitted an `::error::` line
and returned a non-zero status, and those three jobs would be red.

What it does not establish, stated as plainly as it can be:

- It does not prove determinism across Python versions. The step runs once,
  under whichever interpreter the job has selected. Two runs under one
  interpreter is the claim.
- It does not prove determinism across platforms or over time. Both runs
  happen within one workflow run, on one runner, minutes apart.
- It does not prove the exported geometry is correct. A serialiser that
  reproducibly writes the wrong vertex passes this gate cleanly. Stability
  is not correctness, and the two are being kept apart deliberately.
- It says nothing whatsoever about appearance. OPEN-051-F remains open.

The same limitation recorded in volume 5 sections 8 and 9 applies again and
has not softened: GitHub step-level logs are not reachable from this
environment. The step prints a line of the form
`export determinism: N files, M bytes, byte-identical across two runs`, and
that line cannot be read from here. What the runner proves is exit status.
The locally measured figures from the D-059 session were 26 files totalling
112,123 bytes, on one machine, never checked by CI. If the runner's figures
were to differ from those, that would be a finding worth recording, not a
failure to suppress, and it is currently unreadable either way. Making it
readable is the honest next improvement to this gate.

### A defect this gate caught before it ever ran

The step as first drafted compared the two trees with `if ! diff -r "$a" "$b"`.
That is wrong, and the error is the kind that survives review because it
reads correctly. `diff` exits 1 when files differ and 127 when the command
is not installed, and a bare negation treats both identically. A runner
image without `diff`, or with it moved off `PATH`, would report a
determinism failure that had nothing to do with determinism.

It was caught because the step body was extracted from the parsed YAML and
rehearsed against stand-in exporters before being committed, under the rule
that a check which has only ever passed has not been tested. The first
rehearsal reported three passes that were false: this sandbox has no `diff`,
so those cases exited non-zero for the missing tool rather than for the
logic. The committed version replaces `diff` with an inline `python3`
comparator that walks both trees, reports files present in only one side
and files that differ as separate errors, and fails explicitly on an empty
tree so that an exporter producing nothing cannot pass by vacuity. The
rehearsal was then re-run to five cases, all five passing for the correct
reason.

### Cumulative position

Batch 10 is the eleventh consecutive all-green batch. Total green check runs
recorded across volumes 1 to 6: one hundred and fifteen.

The honest reading is the same as it was at ninety and at one hundred, and
it will stay the same until a human looks at a mesh. These runs prove that
this repository parses under 3.9 and 3.12, that its static guards are
satisfied, that a headless Blender process starts, that the bodywork
geometry core computes what its cases expect against the real
configuration, that the exporter round-trips geometry without losing a bit,
and now that it writes the same bytes twice in a row on a machine that is
not the author's. No C++ has been compiled. The Unreal project has never
been opened. No FBX or GLB has been imported. No mesh has been seen by a
human being. No lap has been driven. Milestone 4 remains **not accepted**,
and the single thing standing between it and acceptance is still the visual
verification defined in `MILESTONE_4_VISUAL_ACCEPTANCE.md`, which cannot be
performed from here.