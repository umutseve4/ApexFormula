# CI run note — wave 1 closing verification

**This file lives only on `ci/doc-wave-verify-3`. It must never be
merged into `main`.**

## Why it exists

Check runs in this environment are readable only through a pull request,
and a pull request's check runs belong to its **head commit**. Commits
pushed directly to `main` are invisible to any pull request whose head is
a different branch — the failure mode that made PR #9 return the same
frozen batch for hours while eleven documentation commits landed
unobserved.

A pull request also needs a non-empty diff. This file is that diff, and
nothing else. It carries no design content and no claim.

## What this run certifies

Branch cut from `main` at `be181489`, **after** the last write. Its tree
therefore contains every commit of D-048 wave 1, including:

| Commit | File |
| --- | --- |
| `71ef6d45` | `BlenderPipeline/README.md` |
| `76fdcb31` | `Documentation/CI_EVIDENCE_VOL2.md` (created) |
| `078b4383` | `Documentation/DECISION_LOG_VOL2.md` (D-049) |
| — | `Documentation/CI_EVIDENCE_VOL2.md` (PR #17 outcome) |
| `be181489` | `Documentation/DECISION_LOG_VOL2.md` (D-050) |

## Acceptance criteria

1. Ten of ten check runs conclude `success`.
2. Every `started_at` is later than this commit's author date.

A green batch that started earlier is evidence about a different tree and
is rejected as stale. Anything short of both criteria is not a pass and
is not to be recorded as one.

## Specific risk under test

D-050 quotes the sixteen-character configuration digest short form next
to a `config_hash` anchor, inside `Documentation/`, which is in the set
scanned by `Tools/af_config_hash_guard.py` check B. The value is the
correct short form of the current pin, so the check should pass. This run
is what establishes that it does.

## Disposal

Read the check runs, record the outcome in `CI_EVIDENCE_VOL2.md`, then
close the pull request **without merging** and leave the branch dead.
