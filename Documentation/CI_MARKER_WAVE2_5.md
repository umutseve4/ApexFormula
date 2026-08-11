# CI verification marker - wave 2, batch 5

This file exists only to trigger a continuous integration run on a disposable
branch. It is never merged into the main branch. It carries no project meaning
and must not be referenced by any other document except the evidence file.

Branch: ci/wave2-verify-5
Base: main
Purpose: verify that the main branch is green at the commit that introduced
Decision Log Volume 4, and at the preceding commit that recorded batch 4.

## Commits under verification

| Commit | File | Size | Note |
|---|---|---|---|
| 3a20762b | Documentation/CI_EVIDENCE_VOL3.md | 18896 | section 8, batch 4 record |
| 232bb31c | Documentation/DECISION_LOG_VOL4.md | 13450 | new volume, decision D-053 |

Both are Markdown. Markdown has no compile gate in this project, so the only
automated protection against a truncated rewrite is the byte-size prediction
recorded at write time. Both sizes above were returned by the write call itself.

## Acceptance rule

The batch is accepted only if all of the following hold.

1. The check run total is exactly ten.
2. Every one of the ten reports conclusion success.
3. No run is still in progress at the moment of the accepted reading.
4. Every start timestamp is later than the author date of this marker commit.

A reading of nine completed out of ten, with any run still in progress, is
rejected. On such a reading the correct action is to wait a further forty
seconds and poll again with at least one varied query argument.

## Expected check run matrix

| Job name | Count |
|---|---|
| Blender smoke test (headless) | 2 |
| Static validation (no engine, no DCC) | 2 |
| af_static_validate (py3.9) | 2 |
| af_static_validate (py3.12) | 2 |
| Python syntax check | 2 |

Total: ten. The duplication is expected. Two workflow files define overlapping
job sets, so each logical job appears twice.

## What this batch proves

It proves that the declared module graph, dependency table, prohibited
identifier rules, copyright header rule over C++ sources, required configuration
keys and bone name expectations remain internally consistent, and that every
Python artifact compiles under both supported interpreter versions.

## What this batch does not prove

It does not prove that any C++ has been compiled, that any project has been
opened in an engine, that any exported mesh has been imported, that any mesh has
been inspected visually, or that any lap has been driven. None of those has ever
been done in this project. See decision D-053 section 8 for the full statement.
