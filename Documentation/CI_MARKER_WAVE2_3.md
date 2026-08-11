# CI Marker — Wave 2, Batch 3

This file exists only to force the workflows to run against a branch so
that a pull request can expose the check runs. It is disposable. The
branch that carries it is never merged and the pull request that carries
it is closed unmerged once the results are read.

## Why this file exists

No available tool lists check runs for a bare branch. The check-run
listing is addressed by pull request number. Therefore a branch is cut
from the trunk after the last real commit, one marker commit is pushed
to it, a draft pull request is opened, and the check runs of that pull
request are read. The marker commit's author date is the acceptance
threshold: every job whose start time is later than that date was
launched by this push and therefore ran against a tree that already
contains every commit listed below.

## Covered commits

The trunk tip at the moment this branch was cut is edfd74ba. The
following commits are the ones this batch is meant to prove:

| Short SHA | Path | What changed |
| --- | --- | --- |
| 62477469 | Tools/af_lap_rules_model.py | display identity in prose only, four substitutions |
| cc85f950 | Tools/af_mesh_quality.py | display identity in prose only, four substitutions |
| d20d041c | Documentation/CI_EVIDENCE_VOL3.md | new evidence volume |
| edfd74ba | Documentation/VERSION_MATRIX.md | three prose renames, module names untouched |

## Acceptance rule

The batch is accepted only if all four conditions hold at once.

1. Every check run reports a conclusion of success.
2. The number of check runs equals the number produced by the previous
   accepted batches, so no job silently disappeared.
3. Every start time is later than this marker commit's author date.
4. No job is still queued or in progress when the reading is taken.

Anything short of all four is a failure and is recorded as one.

## What a green result here does not prove

It proves the Python files still parse, the guards still agree with the
tree, and the documents still satisfy the document checks. It does not
prove any C++ compiles, it does not prove the vehicle drives, and it
does not prove the mesh looks right. Those labels are unchanged.
