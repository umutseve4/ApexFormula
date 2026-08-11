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
| `DECISION_LOG_VOL5.md` | this file | **active** | D-056, D-057 |

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
| OPEN-056-B | Re-author `af_bodywork_profile.py` against the surviving self-test | **new** |

### OPEN-056-B in detail

The re-authoring is the natural next tranche of real work, and it is one of
the very few tranches that can be genuinely advanced in this environment,
because it needs neither Unreal nor Blender to be gated.

Requirements, fixed now so they cannot drift later:

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
