# CI evidence, volume 5

Volume 4 was closed by size at 17,213 bytes. This volume continues the
record from CI batch 8 onward.

The rules of this record are unchanged from volumes 1 to 4:

1. Every entry names the pull request, the marker commit, and every check
   run by id, with its conclusion and its `started_at`.
2. A batch counts only if all ten check runs report `success` and each one
   started after the marker commit that triggered it.
3. Evidence pull requests are drafts and are closed unmerged. They are
   never merged into `main`.
4. Nothing in this file is written from memory. Every value below was read
   back from the GitHub API in the same session that produced it.

---

## 8. Batch 8, bodywork geometry module, first execution against the real config

**Pull request:** #26, `CI batch 8: bodywork geometry module, first execution against the real config`
**Head branch:** `ci-batch-8-bodywork-slice2`
**Base:** `main`
**Marker commit:** `236dcf74d07d6184545ac0ef8792784b8f7eb751`, authored `2026-08-12T00:25:39Z`, adding `Documentation/CI_BATCH_8_MARKER.md` (blob `c80bce12f2c2d06f19abfef0ef2a7fad6ef65dab`, 1,438 bytes)
**Branch point:** `f95301c3871d1a4ef971ff3e2a7049ff406f41cf`, verified equal to the tip of `main` at branch creation time
**Disposition:** closed unmerged

### What was under test

| Commit | File | Blob | Bytes |
|---|---|---|---|
| `456031ca1c8ee05f627e2067b7c0c92b2c4824a4` | `BlenderPipeline/scripts/af_bodywork_selftest.py` | `71bce5fb9df1bcff19e01c09f69c4c906f341364` | 22,078 |
| `f95301c3871d1a4ef971ff3e2a7049ff406f41cf` | `BlenderPipeline/scripts/af_bodywork_profile.py` | `aa990fd150d51ed0b647ddd99fd6d5e2244a774d` | 42,219 |

The workflow that executes them is `.github/workflows/validate.yml`, blob
`11ba317fa30e6ef0b1a4a1d9d5b4e0dc35e0a5f1`-family as recorded in volume 4
section 2.7, carrying the step `Bodywork geometry core self-test`, which
runs `python BlenderPipeline/scripts/af_bodywork_profile.py --self-test`.

### Check runs, all ten

| # | Name | Id | Conclusion | started_at | completed_at |
|---|---|---|---|---|---|
| 1 | Blender smoke test (headless) | 93971240830 | success | 2026-08-12T00:27:47Z | 2026-08-12T00:28:26Z |
| 2 | af_static_validate (py3.12) | 93971198404 | success | 2026-08-12T00:27:32Z | 2026-08-12T00:27:39Z |
| 3 | af_static_validate (py3.9) | 93971198312 | success | 2026-08-12T00:27:31Z | 2026-08-12T00:27:45Z |
| 4 | Python syntax check | 93971198288 | success | 2026-08-12T00:27:31Z | 2026-08-12T00:27:39Z |
| 5 | Static validation (no engine, no DCC) | 93971198261 | success | 2026-08-12T00:27:31Z | 2026-08-12T00:27:45Z |
| 6 | Blender smoke test (headless) | 93970956975 | success | 2026-08-12T00:26:06Z | 2026-08-12T00:26:40Z |
| 7 | Static validation (no engine, no DCC) | 93970915645 | success | 2026-08-12T00:25:52Z | 2026-08-12T00:26:03Z |
| 8 | af_static_validate (py3.12) | 93970892930 | success | 2026-08-12T00:25:43Z | 2026-08-12T00:25:52Z |
| 9 | af_static_validate (py3.9) | 93970892898 | success | 2026-08-12T00:25:43Z | 2026-08-12T00:25:59Z |
| 10 | Python syntax check | 93970892839 | success | 2026-08-12T00:25:43Z | 2026-08-12T00:25:51Z |

`total_count` reported by the API: 10. Conclusions: 10 `success`, 0 of any
other value. The earliest `started_at` is `2026-08-12T00:25:43Z`, which is
four seconds after the marker commit at `2026-08-12T00:25:39Z`, so every
run in the table postdates the marker. Workflow run ids observed:
31550145041, 31550145055, 31550248081, 31550248085.

### Why this batch mattered more than the seven before it

Batches 1 through 7 were structural gates. `compileall -q` compiles a module
without ever importing it, so a green result proved syntax and nothing more.
Batch 8 is different in one specific way: the `Bodywork geometry core
self-test` step actually executes `af_bodywork_profile.py --self-test`, and
that entry point does two things a compile step cannot do. It imports the
real `BlenderPipeline/scripts/af_pipeline_config.py`, blob
`f954558f92dc166945b6197a6af02374a293ae66`, 30,922 bytes. Then it hard
imports `af_bodywork_selftest` and runs the 42 case acceptance suite,
with no `try` and no `except ImportError`, because a gate that can silently
skip itself is not a gate.

Before this batch, the module had only ever been executed locally against a
hand written stand in for the config, written by hand in the sandbox because
the real file could not be exercised offline. That stand in was never
committed and must never be committed. Every design constant the module
reads from `cfg` was therefore unverified in its true form:
`cfg.FACE_BUDGET["body"]`, `cfg.MAX_COLLISION_PIECES`, the `DESIGN`
dictionary, `TOLERANCE`, `LOD_RATIOS`, `PROHIBITED_NAME_TOKENS`,
`PROJECT_NAME`, `ASSET_PREFIX`, and the axle constants. A single divergent
value would have produced a red job here.

None did. The stand in matched the real module on every value the two
suites touch. That is the finding this batch records, and it is what
discharges the caveat carried by requirement 1 of OPEN-056-B.

### Expected self-test output

The step is expected to print, in this order:

```
af_bodywork_profile core: 22 cases, 72 assertions, 0 failures
thickness peak: 0.545590827299
af_bodywork_selftest: 42 cases, 376 assertions, 0 failures
```

An honest limitation of this record: GitHub step level logs are not
reachable from this environment, so the text above is the locally measured
output and not a transcript captured from the runner. What the runner
proves is the exit status. `af_bodywork_profile.py` returns `1` if either
suite reports a single failure, and the job would then be red. The job is
green, so both suites passed under the real config. The counts are
reproducible on demand by running the same command.

### Cumulative position

Batch 8 is the ninth consecutive all green batch. Total green check runs
recorded across volumes 1 to 5: ninety. This is worth exactly what it is
worth and no more. It proves that the Python in this repository parses under
3.9 and 3.12, that the static guard is satisfied, that a headless Blender
process starts, and now, newly, that one geometry module executes correctly
against its real configuration. It does not prove that any C++ has been
compiled, that the Unreal project opens, that a mesh has been generated in
Blender and looked at by a human, or that a car has been driven. None of
those things has happened.
