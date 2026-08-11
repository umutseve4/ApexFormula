# CI Marker - Wave 2, Batch 4

Disposable verification scaffolding. This file exists only on the branch
`ci/wave2-verify-4` and must never be merged into `main`.

## Purpose

Trigger a full check-run matrix so that the decision-log closure commit and the
evidence-volume update can be verified against the same gate that covered every
earlier batch in this migration.

## Base

Branch created from `main` at commit `0ca1d70f`.

## Commits under test

| File | Commit | Note |
|---|---|---|
| `Documentation/DECISION_LOG_VOL3.md` | `0ca1d70f` | D-052 appended, wave 1.5 closure record |
| `Documentation/CI_EVIDENCE_VOL3.md` | earlier on `main` | section 7, batch 3 record |

Both are Markdown. Neither carries a compile gate, so the byte-delta
prediction was the only automated truncation detector applied before the push.

## Acceptance rule

1. Exactly ten check runs.
2. Every run reports success.
3. Every run starts later than this marker commit author date.
4. The pull request is closed unmerged afterwards.

## Expected matrix

| Job | Count |
|---|---|
| Blender smoke test (headless) | 2 |
| Static validation (no engine, no DCC) | 2 |
| af_static_validate (py3.9) | 2 |
| af_static_validate (py3.12) | 2 |
| Python syntax check | 2 |

## Scope limit

A green batch here proves structural consistency only. It does not compile
C++, does not open the editor, does not import any mesh, and does not run any
guard self-test. Those remain unproven and are recorded as such.
