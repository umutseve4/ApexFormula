# Milestone 3 — Race Test Environment and Valid Lap System

Implementation record. This document follows the same structure as
`MILESTONE_2_IMPLEMENTATION.md`.

It is written to the honesty rules in the project brief: every claim below
carries one of the eight verification labels, and anything that has not
actually been executed is marked as such.

---

## 1. Status summary

Milestone 3 is **partially delivered**. It is not complete and is not
claimed as complete.

| Output | State | Label |
| --- | --- | --- |
| Lap timing rules (`UAFSectorTimer`) | Source written, rules verified by executable model | `automatically validated` (rules only) |
| Lap validity rules (`UAFLapValidator`) | Source written, rules verified by executable model | `automatically validated` (rules only) |
| Checkpoint actor (`AAFCheckpoint`) | Source written | `requires local compilation` |
| Session rules (`UAFSessionRules`) | Source written | `requires local compilation` |
| Track definition (`UAFTrackDefinition`) | Source written | `requires local compilation` |
| Test circuit geometry | **Not started** | — |

The C++ in `Unreal/Source/ApexFormulaRace/` **has never been compiled**.
No Unreal Editor exists in the build environment. That is unchanged from
Milestone 2 and is disclosed rather than hidden.

---

## 2. What was actually done in this milestone

### 2.1 The problem

`Unreal/Source/ApexFormulaRace/` already contained the Milestone 3
scaffolding: six headers and six translation units implementing sector
timing, lap validity, checkpoints, session rules and track definition.

None of it had been run. There is no compiler and no engine in this
environment, so the C++ automation tests cannot execute. The five
Milestone 3 acceptance criteria are mostly arithmetic and ordering
claims — laps timed accurately and reproducibly, sector times summing to
lap time, cutting the circuit invalidating a lap, restart being
deterministic — and asserting those without running anything would breach
Cross-Milestone Rule 1 ("no completion claim without a labelled
evidence").

### 2.2 The approach taken

`UAFSectorTimer` and `UAFLapValidator` were deliberately written as
**pure** classes. They do not tick, do not touch the world, do not read a
frame time and do not depend on an actor. Every input is an explicit
session time passed by the caller.

That property makes the rules testable **without an engine**, in any
language.

So `Tools/af_lap_rules_model.py` was authored: a standard-library-only
Python mirror of both classes, transcribed from the live `.cpp` sources,
with an embedded self-test.

### 2.3 The CI gap that had to be closed

The `static-validation` job ended with:

```
python3 -m compileall -q BlenderPipeline/scripts Tools
```

`compileall` **byte-compiles**; it does not execute. A self-test dropped
into `Tools/` would therefore have produced no evidence at all — it would
have been compiled and then ignored.

An explicit execution step was added to `.github/workflows/validate.yml`,
after the Blender pipeline config self-check and before the byte-compile
step:

```yaml
- name: Lap rules reference model self-test
  run: python3 Tools/af_lap_rules_model.py --self-test
```

The step has no `continue-on-error`. If the model self-test fails, the
job fails.

The `blender-pipeline` job was reproduced verbatim and **not** altered.
Its Blender 5.2 archive resolution is known to work and is not to be
"fixed".

---

## 3. The reference model

`Tools/af_lap_rules_model.py` — 30,021 bytes, standard library only,
Python 3.9 compatible.

It mirrors, line for line against the live sources:

* `SectorSplit` / `FAFSectorSplit`
* `LapResult` / `FAFLapResult`
* `LapInvalidationReason` / `EAFLapInvalidationReason` (all seven values)
* `SectorTimer` / `UAFSectorTimer`
* `LapValidator` / `UAFLapValidator`

### 3.1 Rules transcribed

**Sector timer.**

* `Configure(n)` rejects `n < 1`.
* `RecordSectorBoundary(t)` rejects a non-advancing time — `t` must be
  **strictly** greater than the current sector entry time.
* Recording the final sector boundary closes the lap. A new lap needs an
  explicit `BeginLap`, so a missed timing line can never be silently
  absorbed into the following lap.
* `GetLapTimeSeconds()` is the sum of the split durations, not an
  independent measurement. Criterion 2 therefore holds by construction
  and is additionally asserted by test.

**Lap validator.**

* Index 0 of the checkpoint order is the timing line; `Configure`
  requires at least two entries, rejects unset names and rejects
  duplicates.
* An unknown, out-of-order or extra checkpoint invalidates the lap with
  `MissedCheckpoint`.
* `InvalidateLap` is **first-cause-wins**: once a reason is set it cannot
  be overwritten, and `NotInvalidated` can never clear an existing
  reason.
* A lap that is invalidated **still finishes and is still timed**. A
  driver who cuts the circuit does not vanish; they need a recorded
  result that is clearly marked invalid. That is exactly criterion 3.
* A completion time that does not advance past the start time clamps the
  lap time to `0.0` and invalidates the lap.

### 3.2 Self-test coverage

68 cases across 9 groups:

| Group | What it pins down |
| --- | --- |
| `test_sector_timer` | configure rejection, three-sector lap, split index and adjacency, **sum == lap time**, auto-close after the final sector, non-advancing time rejection, no-lap-open rejection, reset behaviour |
| `test_validator_configure` | fewer than two entries, duplicates, unset names including `""`, `None` and `"None"` |
| `test_validator_clean_lap` | the ordinary valid case |
| `test_validator_cutting` | out-of-order, early line, unknown checkpoint, extra checkpoint — all produce `MissedCheckpoint` and all still produce a timed result |
| `test_validator_invalidation_precedence` | first-cause-wins; `NotInvalidated` cannot clear; all six real reasons carried through |
| `test_validator_time_guards` | equal and backwards completion times clamp to `0.0` and invalidate |
| `test_determinism_and_reset` | identical input three times, reset equals a fresh instance, an invalid lap does not contaminate the next |
| `test_timer_validator_agreement` | the two independent classes agree to within 1e-12 |
| `test_originality_guard` | every checkpoint name uses the neutral `AF_CP_` prefix |

The harness rejects duplicate case names with an `AssertionError`, so a
copy-paste that silently replaced a test cannot pass unnoticed.

Exit codes: `0` pass, `1` fail, `2` bad invocation.

---

## 4. Evidence

### 4.1 Local execution

Run under Python 3.12.9 in the build environment:

```
  cases passed : 68
  cases failed : 0

SELF-TEST PASS
```

Exit code 0, first attempt.

### 4.2 CI execution

Pull request #5, branch `m3-lap-rules-model`, squash-merged to `main` as
`7ec380e14fe315a245a4898c79dee3c7aef0650b`.

Every distinct check name reported `success`:

| Check | Conclusion |
| --- | --- |
| Static validation (no engine, no DCC) | success |
| af_static_validate (py3.9) | success |
| af_static_validate (py3.12) | success |
| Python syntax check | success |
| Blender smoke test (headless) | success |

The **Static validation** job is the one that contains the new
`Lap rules reference model self-test` step. Its passing is what
demonstrates the self-test ran under both a clean checkout and a Python
version other than the local one.

Two duplicate check entries from superseded workflow runs stayed at
`queued` / `in_progress` and never advanced across three polls spanning
roughly four minutes. Each has a completed, passing twin of the same name
in the sibling run. They are queue artefacts, not failures. This is
recorded rather than quietly ignored.

Post-merge verification by directory listing on `main`:

* `Tools/af_lap_rules_model.py` — `9ab572f89bf366cba5d3db37927f19773f241280`, 30,021 bytes
* `.github/workflows/validate.yml` — `61bac3a75261d6b6801782d514898b2acbd7bdd1`, 5,992 bytes

The model blob size is byte-identical to the file executed locally.

---

## 5. Acceptance criteria

| # | Criterion | Status | Label |
| --- | --- | --- | --- |
| 1 | Laps are timed accurately and reproducibly | Rules verified; identical input produces identical output across repeated runs and across a reset | `automatically validated` (arithmetic only) |
| 2 | Sector times sum to the lap time | Verified; also true by construction, since lap time **is** the sum | `automatically validated` |
| 3 | Cutting the circuit invalidates the lap | Verified for out-of-order, early-line, unknown and extra checkpoints; the lap still produces a timed, clearly-invalid result | `automatically validated` (rules only) |
| 4 | Restart and reset are deterministic | Verified; reset equals a fresh instance and an invalid lap does not contaminate the next | `automatically validated` |
| 5 | No real-world circuit is reproduced | Satisfied by construction — no circuit geometry exists yet, and all checkpoint identifiers use the neutral `AF_CP_` prefix, which the self-test enforces | `verified by inspection` |

Criteria 1, 3 and 4 are marked "rules only" on purpose. The rules are
proven. Whether the rules are *invoked correctly at runtime* — with real
overlap events, real trigger volumes and a real frame time — is not
proven and cannot be proven here.

---

## 6. Decision D-042 — mirror the lap rules in an executable model

**Context.** The Milestone 3 acceptance criteria are almost entirely
arithmetic and ordering claims. The C++ that implements them cannot be
compiled or run in this environment, and the Unreal automation tests have
never executed.

**Decision.** Mirror `UAFSectorTimer` and `UAFLapValidator` in
`Tools/af_lap_rules_model.py`, a standard-library Python module with an
embedded self-test, and run that self-test as an explicit CI step.

**Why.** The two classes were written pure specifically so their rules
could be checked without an engine. Taking that property and doing
nothing with it would waste it. Running the rules somewhere is strictly
better evidence than asserting them nowhere.

**Consequences, stated plainly.**

* This does **not** prove the C++ compiles.
* This does **not** prevent the model drifting from the C++. Changing one
  and not the other will not be caught. The mitigation is process, not
  automation: the model and the sources are edited together.
* It says nothing about geometry, trigger volumes, overlap events, frame
  rate or how track limits feel to drive.
* An explicit workflow step was required because `compileall` executes
  nothing.

**Alternatives rejected.**

* *Write Unreal automation tests only.* They would never run here, so
  they would produce no evidence at all in this milestone.
* *Claim the criteria are met by code review.* That is
  `verified by inspection` at best, and weaker than actually running the
  arithmetic.
* *Generate the model from the C++.* No parser, no compiler, no network
  to fetch one. Out of reach.

---

## 7. Known gaps carried forward

* The C++ in `Unreal/Source/ApexFormulaRace/` has never been compiled.
  Label: `requires local compilation`.
* No FBX import, no editor load, no visual inspection, no playtesting.
* The Milestone 3 output "test circuit geometry" is **not started**. When
  it is written it must be an original layout; criterion 5 forbids
  reproducing any real circuit.
* Model/source drift is unguarded, as stated in D-042.
* `config_hash = c9ef9f7e985a1aaf` is still asserted **by construction
  only**. This is the single evidence gap carried over from Milestone 2
  and it remains open.

---

## 8. Cross-milestone rules honoured

1. No completion claim without a labelled evidence — Milestone 3 is
   reported as partially delivered, not complete.
2. Preview quality never damages Final assets — not touched.
3. Hardware weakness never lowers the Final target — not touched.
4. Engine vehicle access stays behind `UAFVehicleCompatibilityLayer` —
   nothing added here touches the engine vehicle API.
5. Bone names change in both places together — not touched.
6. Nothing under `LocalReference/` committed — nothing was.
7. Vehicle dimensions live in `af_pipeline_config.py::DESIGN` — not
   touched.
