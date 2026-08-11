# CI run note — documentation wave verification

This file exists on the branch `ci/doc-wave-verify-2` only. It is **not**
intended to be merged into `main`.

## Why it exists

Check runs in this environment are readable only through a pull request,
and a pull request's check runs belong to its head commit. A branch whose
tip is identical to `main` cannot be turned into a pull request, because
the diff would be empty. This file is that diff, and nothing more.

## What the run is meant to prove

The branch was cut from `main` **after** the final commit of the
documentation rename wave, so its tip contains every file in that wave.
A green result therefore certifies the tree as it stands after the wave,
not some earlier tree.

Acceptance criteria, stated in advance and not relaxed afterwards:

1. Ten of ten check runs conclude `success`.
2. Every check run start time is later than the author date of the last
   documentation commit. An earlier batch is evidence about a different
   tree and is rejected as stale.
3. The head commit of this branch contains every commit in the wave.

The full criteria and the commit table live in `CI_EVIDENCE_VOL2.md`.
The decision that established this procedure is D-049 in
`DECISION_LOG_VOL2.md`.

## What it does not prove

Nothing about compilation, nothing about the Unreal Editor, nothing
about Blender, and nothing about how the vehicle looks or drives. The
documentation wave changed prose. Module identifiers, target files, the
project file and every guard constant still carry the internal code
name, exactly as each rewritten document states on its own page.

After the run is read, the pull request is closed without merging.
