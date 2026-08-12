> Uludağ Formula - original work. Not affiliated with any real motorsport
> series, championship, team, driver or car.

# Decision Log - Volume 5

## 0. Volume history

Every file in this repository is written by full-file retranscription. There
is no patch mode and no compile gate on Markdown, so a long file can be
silently truncated with nothing to catch it. Decision logs are therefore
closed by size at roughly 20 KB and continued in a new volume.

| Volume | Final size | Status | Decisions |
| --- | ---: | --- | --- |
| `DECISION_LOG.md` | 50,726 B | closed | D-001 .. D-030 |
| `DECISION_LOG_VOL2.md` | 20,441 B | closed | D-031 .. D-042 |
| `DECISION_LOG_VOL3.md` | 25,950 B | closed | D-043 .. D-052 |
| `DECISION_LOG_VOL4.md` | 27,898 B | closed, over threshold | D-053, D-054, D-055 |
| `DECISION_LOG_VOL5.md` | this file | **active** | D-056, D-057, D-058 |

Do not append to VOL4. It is already past the size at which retranscription
is safe.

---

## D-056 - Pull request 9 is closed unmerged

**Status:** decided and executed.
**Closes:** OPEN-M4-01.
**Opens:** OPEN-056-B (re-author the bodywork module).

### The question

OPEN-M4-01 has been outstanding since Milestone 4 began: merge pull request 9
or close it. It was left open because the branch was believed to carry a
documentation file whose companion module would follow.

### What was actually measured

Pull request 9 was read directly from the API this session, not from memory.
Branch `milestone-4-bodywork`, head `c94bcade1dd68428c40b6de7fad3ecd0fee9bd01`,
7 commits, 798 additions, **2 changed files**:

| File | Lines | Present on main before this ruling |
| --- | ---: | --- |
| `BlenderPipeline/scripts/af_bodywork_selftest.py` | 505 | no |
| `Documentation/MILESTONE_4_BODYWORK.md` | 293 | no |

`BlenderPipeline/scripts/` was listed in the same session. It contains exactly
nine files:

| File | Size |
| --- | ---: |
| `af_circuit_generate.py` | 43,731 |
| `af_export.py` | 10,996 |
| `af_materials.py` | 6,258 |
| `af_pipeline_config.py` | 30,922 |
| `af_scene_setup.py` | 8,534 |
| `af_smoke_test.py` | 10,774 |
| `af_validate.py` | 28,683 |
| `af_vehicle_generate.py` | 22,460 |
| `af_vehicle_rig.py` | 9,259 |

`af_bodywork_profile.py` is not among them, is not on the branch, and is not
on `main`. The pull request body itself states this plainly: "the module it
documents ... is written and green locally but is **not yet in this branch**".

The self-test opens with a single import statement pulling roughly thirty-five
names out of that missing module - `build_parts`, `collision_proxies`,
`section_points`, `superellipse_ring`, `loft`, `mesh_diagnostics`,
`envelope_report`, `budget_report`, `lod_plan` and the rest. It raises
`ModuleNotFoundError` on line 1 of execution.

### The ruling

**Pull request 9 is closed without merging.**

Reasoning, in the order that decided it:

1. **Merging would place unrunnable evidence on `main`.** The document asserts
   "42 methods, 514 assertions, 0 failures" and a full table of measured
   geometry. Merged as-is, `main` would carry that assertion next to a test
   file that cannot import its own subject. Anyone auditing the repository
   would find a claim with no way to check it. That is the definition of
   fabricated evidence, and it is refused for the same reason the
   `af_mesh_quality` rehearsal gate was declared not met rather than
   reconstructed from prose.

2. **Continuous integration would not have caught it.** This was checked, not
   assumed. Neither workflow imports the module. `static-validation` runs
   `compileall -q BlenderPipeline/scripts Tools`, and `compileall` compiles
   without importing, so a broken import is invisible to it. No workflow step
   invokes `af_bodywork_selftest.py`. The batch would have come back 10 of 10
   green over a file that cannot run. This is a concrete instance of the
   standing rule that CI green is a structural gate, not an execution gate -
   and it is the strongest example the project has produced so far.

3. **The bytes are not recoverable here.** The module lived on a local machine
   and was never pushed. It cannot be fetched, and reconstructing 71,760 B
   from a prose summary would produce code that had never been executed under
   a document claiming measurements it had never produced. Refused.

4. **Uniform beats mixed.** This is D-055's reasoning applied again. A
   repository with no bodywork module is a coherent state. A repository with
   a bodywork test but no bodywork module is not.

### What was preserved, and how

Closing a pull request does not delete its branch. `milestone-4-bodywork`
remains at `c94bcade`, so the 505-line self-test survives in full and is
recoverable at any time. It is genuinely valuable: it is a precise, executable
specification of the module's public surface, its invariants and its
tolerances. When the module is re-authored, that suite is the acceptance
target.

The document was landed on `main` separately, in commit `8140edf2`
(`Documentation/MILESTONE_4_BODYWORK.md`, 16,829 B), with a new section 0
stating without hedging that the module is absent, that every number in
sections 4 through 6 is historical and unreproducible, and that no acceptance
criterion may be counted from the file. Two further edits were made: the
display name was changed to Uludağ Formula per the rename, and section 7's
status table was split into "when last observed" and "in this repository" so
the two can never be confused again.

The design knowledge in section 5 is the part that actually mattered. Four
geometry defects and four defective test assumptions, each with the measured
values that exposed them - the inward-wound lofts caught only by signed
volume, the endplates breaching the 5.600 m envelope, the halo apex computed
without tube radius, the non-monotone convergence of cosine-spaced sampling at
0.04212 / 0.04910 / 0.04995 / 0.04990. None of that depends on the lost bytes.
It transfers to the re-authored module unchanged.

### Consequence for Milestone 4 status

Milestone 4 is **not started for acceptance purposes**. Its criteria were
previously carried as "partially delivered" on the strength of a module that
is not in the repository. That accounting is withdrawn here.

---

## D-057 - MILESTONE_PLAN.md is corrected by erratum, not by rewrite

**Status:** decided.
**Closes:** OPEN-056-A.

### The defect

`Documentation/MILESTONE_PLAN.md` (24,860 B) contains three statements that
D-055 falsified when it froze the build-tool module identifiers:

1. The naming note describes the six module identifiers as "Queued for wave 2
   - will change".
2. The rename status paragraph states that wave 1 "is in progress" and that
   wave 2 "has not started".
3. The verification ledger's last row repeats that the six module identifiers
   are queued for wave 2.

All three are false. Wave 1 is complete and continuous-integration verified.
Wave 2A was executed, then fully reverted, then verified absent. Wave 2C was
cancelled. The module identifiers are permanent.

### Why an erratum and not an edit

The obvious fix is to open the file and change three passages. That fix is
rejected on measured risk. Every write in this environment is a full-file
retranscription: to change three lines, all 24,860 B must be re-emitted by
hand. The file is already well past the 20 KB threshold at which this project
closes documents precisely because silent truncation cannot be detected -
there is no schema, no linter and no compile step over Markdown anywhere in
either workflow. Trading three stale sentences for an unbounded risk of losing
part of the roadmap is a bad trade.

### The ruling

The corrections are published **here**, in the active decision log, and
`MILESTONE_PLAN.md` is left byte-identical until it is next rewritten for a
substantive reason - at which point these three corrections are folded in and
the erratum is retired.

**Correction 1.** The six identifiers `ApexFormulaCore`, `ApexFormulaVehicle`,
`ApexFormulaRace`, `ApexFormulaUI`, `ApexFormulaEditor` and `ApexFormulaTests`,
together with the `AF_` symbol prefix and the copyright line, are **frozen
permanently** by D-055. They are not queued for any wave. They are an internal
build-tool code name, visible only in build logs and the `.uproject` modules
array, and they will not change.

**Correction 2.** Wave 1 of the rename is **complete**, delivered in 18
commits and verified by continuous-integration batches 1 through 5. Wave 2 is
**cancelled**: wave 2A was executed in commit `243c5a45`, reverted in five
commits ending `63039649`, and the revert was verified green by batch 6 - all
ten check runs successful, independently re-polled from the API afterwards.
Wave 2C was cancelled before any work began.

**Correction 3.** The verification ledger row concerning the six module
identifiers is superseded by correction 1.

**Correction 4, added by D-056.** The milestone status table's treatment of
Milestone 4 is withdrawn. Milestone 4 is not started for acceptance purposes.

### Precedent

This is the same discipline the plan already applies to itself: the 0B row
records that its status changed and why, rather than quietly presenting the
new value. A reader who finds a stale sentence in the plan and the correction
here can see both, and can see which came first. A reader of a silently
rewritten file can see neither.

---

## D-058 - The bodywork module is re-authored in two verified slices

**Status:** decided, executed, and verified in continuous integration.
**Closes:** OPEN-056-B, all five requirements.

D-056 left the repository in a deliberately coherent state: no bodywork
module, and a 505-line acceptance suite preserved on a closed branch as the
specification to build against. This decision records how that module was
re-authored, what was measured at each step, and the four sub-rulings taken
along the way.

### The method: slices, not a single push

The module was written in two slices, each authored locally, each executed
locally before any byte reached GitHub, and each landed separately with a
blob-hash identity check on arrival.

**Slice 1 - geometry core.** Section mathematics, superellipse rings, lofting,
mesh diagnostics, convexity, unit fixtures and planar UVs. Measured on
execution:

```
af_bodywork_profile core: 22 cases, 72 assertions, 0 failures
thickness peak: 0.545590827299
```

`_THICKNESS_PEAK` is solved numerically at import over 200,001 samples of
`sqrt(s) * (1 - s) * (1 + 0.6 * (1 - s))`; `0.545590827299` is the measured
argmax, printed to twelve places by the self-test so it can never be quietly
adjusted. The peak half-thickness convergence ladder was re-measured, not
copied from `MILESTONE_4_BODYWORK.md` as requirement 5 demands:

| Samples | Peak half-thickness |
| ---: | ---: |
| 6 | 0.04212 |
| 12 | 0.04910 |
| 24 | 0.04995 |
| 40 | 0.04990 |
| 400 | 0.05000 |

The non-monotone step from 24 to 40 is real and is the same behaviour D-056
recorded: cosine-spaced sampling does not straddle the analytic peak
monotonically. A backward loft was measured at signed volume
`+0.19952084794791036`, confirming that winding is detected rather than
assumed. Landed in commit `a09728e8`, blob
`57a3d74e5ca06169982597be2744403cd8351183`.

**Slice 2 - parts, envelope, collision, LOD.** The twelve parts, halo
arithmetic, station layout, envelope and budget reports, collision proxies and
the LOD plan. Measured on execution, against the full surviving suite:

```
af_bodywork_selftest: 42 cases, 376 assertions, 0 failures
```

**376 assertions is a newly measured figure and is not the 514 asserted by
`MILESTONE_4_BODYWORK.md`.** This is expected and is not a defect. The lost
module and this one are different code; only the public surface and the
invariants are shared, because only the suite survived. Under requirement 5,
the measured number wins and the historical number stays historical. Nobody
should ever reconcile them.

### Sub-ruling A - one merged module, not a split

Slice 2 was written as a second file and spliced into slice 1 to form a single
`af_bodywork_profile.py` of 42,219 bytes across 1,157 lines. Splitting it into
`af_bodywork_core.py` and `af_bodywork_parts.py` was considered and rejected.
The surviving suite imports thirty-eight names from one module name. Splitting
would have forced an edit to the acceptance suite purely for packaging
convenience, and requirement 1 permits changing that suite only deliberately
and for a recorded reason. Packaging convenience is not such a reason.

### Sub-ruling B - the acceptance-suite import is hard, never guarded

`_self_test()` imports `af_bodywork_selftest` with a bare `import`. No `try`,
no `except ImportError`, no skip path. If the suite is missing the module
crashes and the job goes red.

This was a deliberate choice against the more forgiving pattern, and the
reason is D-056 itself. A guarded import would mean that deleting or renaming
the suite silently reduces the gate to the 22-case core while still printing a
green banner. **A gate that can silently skip itself is not a gate.** That
sentence is in the module docstring so the next reader inherits the reasoning
along with the code.

### Sub-ruling C - commit order is suite first, module second

Two commits were required and the order was not arbitrary. The module hard
imports the suite, so landing the module first would have left `main` in a
state where the self-test entry point crashes on a missing import - a real
red-CI window between two commits, for no benefit. The suite alone is inert:
it defines a class and does nothing at import time.

Executed in that order:

| Order | Commit | File | Blob | Bytes |
| ---: | --- | --- | --- | ---: |
| 1 | `456031ca1c8ee05f627e2067b7c0c92b2c4824a4` | `af_bodywork_selftest.py` | `71bce5fb9df1bcff19e01c09f69c4c906f341364` | 22,078 |
| 2 | `f95301c3871d1a4ef971ff3e2a7049ff406f41cf` | `af_bodywork_profile.py` | `aa990fd150d51ed0b647ddd99fd6d5e2244a774d` | 42,219 |

Both blob hashes and both byte counts were read back from the API response and
matched the local files exactly, on the first attempt in each case. The
42,219-byte module was retranscribed by hand in a single call after being read
in three chunks; byte identity is what proves no line was dropped.

### Sub-ruling D - the local stand-in config is never committed

Slice 2 reads design constants from `af_pipeline_config`. That module is
30,922 bytes and could not be exercised offline, so a 2,662-byte hand-written
stand-in was created in the sandbox to iterate against. It reproduced only the
values the two suites touch: the `DESIGN` dictionary, `TOLERANCE`,
`LOD_LEVELS` and `LOD_RATIOS`, `FACE_BUDGET`, `MAX_COLLISION_PIECES`,
`PROHIBITED_NAME_TOKENS`, `PROJECT_NAME`, `ASSET_PREFIX`, the axle constants
and the `collision_name` / `lod_name` helpers.

**That file is a test fixture and must never be pushed.** Committing it would
overwrite the real 30,922-byte configuration with a 2,662-byte skeleton and
break every other pipeline script in the directory. It stays in the sandbox.

The honest consequence, stated plainly at the time rather than discovered
later: until the module ran in continuous integration, every constant it read
from `cfg` was unverified in its true form. The green local banner proved the
geometry, not the configuration coupling.

### How the caveat was discharged

Requirement 3 was satisfied first, deliberately before the module was
complete: `.github/workflows/validate.yml` was retranscribed to add a step
named `Bodywork geometry core self-test` running
`python BlenderPipeline/scripts/af_bodywork_profile.py --self-test`. That
landed in commit `c6b1013e`, workflow blob `11ba317f...`, 12,999 bytes, and
was proven live by continuous-integration batch 7, recorded in
`CI_EVIDENCE_VOL4.md` section 2.7.

Requirement 4 followed from D-054: the workflow edit and both source commits
touch gated extensions, so they owe a batch. **Batch 8 is that batch**, and it
is the first execution of slice 2 against the real configuration. Recorded in
full in the new `Documentation/CI_EVIDENCE_VOL5.md`: pull request 26, marker
commit `236dcf74d07d6184545ac0ef8792784b8f7eb751`, ten check runs, ten
`success`, every `started_at` after the marker, earliest at
`2026-08-12T00:25:43Z`. Closed unmerged.

The module exits `1` if either suite reports a single failure. The job is
green, so both suites passed with the real `af_pipeline_config` imported. The
stand-in did not diverge. That is the finding, and it is what discharges
sub-ruling D's caveat.

### Requirement ledger

| # | Requirement | Status |
| ---: | --- | --- |
| 1 | Satisfy the surviving self-test, or change it deliberately | **met** - suite unmodified, 42 cases / 376 assertions / 0 failures |
| 2 | Pure standard library, no `bpy` at module scope | **met** - `math`, `os`, `sys` only; green on py3.9 and py3.12 |
| 3 | `validate.yml` gains a self-test step | **met** - commit `c6b1013e`, proven by batch 7 |
| 4 | The landing commit owes a CI batch | **met** - batch 8, 10/10, pull request 26 |
| 5 | No figure copied from `MILESTONE_4_BODYWORK.md` section 4 | **met** - every figure re-measured; 376 replaces 514 |

**OPEN-056-B is closed.**

### What this does not mean

It does not advance Milestone 4. D-056 set Milestone 4 to not started for
acceptance purposes, and that stands. What exists now is a standard-library
geometry module that computes vertices, faces, envelopes and budgets, and
proves its own arithmetic on every push. Nothing has been generated in
Blender, no mesh has been looked at by a human, no FBX or GLB has been
imported, no C++ has been compiled and no lap has been driven. The module
produces numbers that are internally consistent; whether the car they describe
looks like a car is unknown and cannot be known here. That is OPEN-051-F, and
it needs Umut's machine.

One known cosmetic inefficiency is recorded rather than fixed: `_sidepod(-1)`
lofts once and then re-lofts from mirrored rings, doing the first loft's work
for nothing. It is harmless, the output is correct, and it is left alone
because changing green code without a reason is how green code stops being
green.

---

## Open questions after this volume

| ID | Question | Status |
| --- | --- | --- |
| OPEN-051-B | Drift guard self-test count: 27 in the guard banner, 31 in `VERSION_MATRIX.md` | open, cheaply testable |
| OPEN-051-D | VOL2 header and index inconsistency | open, volume frozen |
| OPEN-051-F | Blender visual verification never performed | open, needs Umut's machine |
| OPEN-052-C | `VERSION_MATRIX.md` section 5.28 says "2300 checks" | open, never refresh silently |
| OPEN-053-A | Local rehearsal gate for `af_mesh_quality.py` | open, declared not met |
| OPEN-M4-01 | Merge or close pull request 9 | **closed by D-056** |
| OPEN-056-A | Three stale rename statements in `MILESTONE_PLAN.md` | **closed by D-057** |
| OPEN-056-B | Re-author `af_bodywork_profile.py` against the surviving self-test | **closed by D-058** |

### OPEN-056-B in detail, retained for the record

The requirements below were fixed when the question was opened, before any of
the work was done, so that they could not drift to fit whatever was
eventually produced. All five are discharged by D-058; the text is kept
unchanged so the target can be compared against the result.

1. The module must satisfy the surviving self-test on branch
   `milestone-4-bodywork` - or the self-test must be changed deliberately,
   with the change recorded as a decision, never silently.
2. It must be pure standard-library Python, importing no `bpy` at module
   scope, so it runs in the `static-validation` job.
3. `.github/workflows/validate.yml` must gain a step invoking its self-test.
   Without that step the module is unguarded and its green banner means
   nothing, which is exactly the failure this volume opens with.
4. That workflow edit makes the landing commit a gated commit under D-054,
   so it owes a continuous-integration batch.
5. No number from section 4 of `MILESTONE_4_BODYWORK.md` may be copied into
   the new module's documentation. Every figure must be re-measured.
