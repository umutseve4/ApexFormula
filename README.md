# Uludağ Formula

An original 3D formula racing game built with Unreal Engine 5.8 and Blender 5.2 LTS.

> **Current state:** the Blender pipeline is executed and green in CI. The Unreal side is
> authored and statically validated but **has never been compiled**. There is no art asset in
> this repository yet, nothing has been imported into an editor, and nothing has been played.

> **Rename in progress (D-048):** the project was previously called *Apex Formula*. The product
> name is now **Uludağ Formula**. The rename is being applied in waves and is **not finished**.
> The Unreal module names, the C++ file names, the `AF_`/`af_` prefixes and the validator
> scripts still carry the old identity. See [Naming](#naming) for exactly what has and has not
> moved.

---

## Naming

Three distinct names exist in this repository and they are not interchangeable.

| Form | Value | Where it is used | Status |
| --- | --- | --- | --- |
| Product name | `Uludağ Formula` | Displayed title, project description, documentation prose | **Applied** |
| Identifier form | `UludagFormula` | Repository name, `ProjectName`, `CompanyName` | **Partially applied** |
| Internal code name | `ApexFormula*` | Unreal module names, directories, `.uproject`, `.Build.cs`, `.Target.cs` | **Not yet migrated** |
| Symbol prefix | `AF_`, `af_`, `UAF`, `AAF`, `FAF`, `IAF` | C++ types, asset prefix, bone names, Python scripts | **Not yet migrated** |

The identifier form drops the breve because Unreal Build Tool requires the module name, the
directory name and the `ModuleRules` C# class name to be the same ASCII token. The same
constraint applies to FBX bone names crossing the Blender→Unreal boundary and to shell paths in
CI. The accented form is therefore confined to display strings and prose, which is where it is
actually seen.

Applied so far:

- `Unreal/Config/DefaultGame.ini` — `ProjectName`, `CompanyName`, `ProjectDisplayedTitle`,
  `Description`
- This README
- The GitHub repository itself, renamed to `UludagFormula`

Not applied yet, and each one is tracked as a separate wave:

- Six Unreal module names and their directories (`ApexFormulaCore`, `ApexFormulaVehicle`,
  `ApexFormulaRace`, `ApexFormulaUI`, `ApexFormulaEditor`, `ApexFormulaTests`)
- `ApexFormula.uproject`, `ApexFormula.Target.cs`, `ApexFormulaEditor.Target.cs`,
  `Config/DefaultApexFormula.ini`
- 65 C++ files, their `#include` graph, their `APEXFORMULA*_API` macros and the
  `// Copyright ApexFormula.` header line that `af_static_validate.py` enforces on every one
- The `AF_`/`af_` prefixes, the eleven bone names and the `AF_CP_` checkpoint prefix
- The seven `Tools/af_*.py` validators and the nine `BlenderPipeline/scripts/af_*.py` scripts
- Both workflow files, whose script paths follow the script names

`Tools/af_static_validate.py` hard-codes the module dependency graph, the `.uproject` filename,
both `.Target.cs` filenames, the settings section name and the copyright header line — 87
occurrences of the old identity in one file. Any module rename must therefore land **in the same
commit** as the corresponding validator change, or CI turns red. That constraint is the reason
this is a staged migration rather than a single sweep.

## What this repository contains

Design documents, the Blender-side authoring and export pipeline, the Unreal Engine 5.8 C++
project foundation and vehicle implementation, and the standalone static validators that check
them against each other.

```
UludagFormula/
├── Documentation/          design documents, decision log, version matrix
├── BlenderPipeline/        nine af_*.py scripts + README
├── Unreal/                 .uproject, Config/, Source/ with six C++ modules
├── Tools/                  seven standalone af_*.py validators
├── .github/workflows/      static validation + headless Blender smoke test on every push
├── .gitattributes
├── .gitignore
└── README.md
```

## Document index

| Document | Purpose |
| --- | --- |
| `PROJECT_VISION.md` | Identity, design goals, originality rules, quality philosophy |
| `TECHNICAL_ARCHITECTURE.md` | Layers, C++ modules, components, Data Assets, telemetry |
| `VEHICLE_SYSTEM_DECISION.md` | Vehicle system evaluation, prototype and long-term decisions |
| `BLENDER_PIPELINE_DESIGN.md` | Blender→Unreal contract: units, axes, naming, validation, export |
| `DRIVER_PIPELINE_DESIGN.md` | Driver/MetaHuman workflow and its privacy constraints |
| `MILESTONE_PLAN.md` | Milestones 0A–12 with acceptance criteria and exclusions |
| `MILESTONE_2_IMPLEMENTATION.md` | What Milestone 2 added, and what it does not prove |
| `VERSION_MATRIX.md` | Pinned environment and version-sensitive assumptions |
| `DECISION_LOG.md` | Numbered decision records D-001 onward |

Suggested reading order: `PROJECT_VISION` → `TECHNICAL_ARCHITECTURE` →
`VEHICLE_SYSTEM_DECISION` → `BLENDER_PIPELINE_DESIGN` → `DRIVER_PIPELINE_DESIGN` →
`MILESTONE_PLAN` → `VERSION_MATRIX` → `DECISION_LOG`.

## Technology

| Area | Choice |
| --- | --- |
| Engine | Unreal Engine 5.8 |
| DCC | Blender 5.2 LTS |
| Platform | Windows |
| Gameplay architecture | C++ |
| Asset assignment, tuning, animation, UI, level config | Blueprints |
| Procedural generation and validation | Blender Python |
| Primary interchange format | FBX |
| Optional preview format | GLB (never an import path) |
| Version control | Git with Git LFS |

Full detail and the list of assumptions that still require local verification are in
`Documentation/VERSION_MATRIX.md`.

## Conventions

These are the conventions **as they exist in the tree today**. They are pre-rename and are
scheduled to migrate; see [Naming](#naming).

- Asset prefix `AF_`; C++ prefixes `UAF`, `AAF`, `FAF`, `IAF`; Blender script prefix `af_`.
- Metres inside Blender, centimetres at the Unreal boundary (`CM_PER_UNIT = 100.0`).
- Bone names are defined once (`af_pipeline_config.py` / `UAFBoneNameMap`) and never hardcoded.
- Vehicle dimensions are defined once, in `af_pipeline_config.py::DESIGN`. `UAFVehicleDefinition`
  follows it and never contradicts it (D-041).
- The project uses no real motorsport branding, teams, drivers, sponsors, liveries, or exact
  reproductions of real cars or circuits.

## Verification labels

Every claim in this repository carries one of the following labels. They are used literally,
not decoratively.

`statically inspected` · `automatically validated` · `requires Blender execution` ·
`requires Unreal Editor verification` · `requires local compilation` ·
`requires visual inspection` · `requires playtesting`

Each document ends with a Verification Ledger applying these labels to its own claims.

As of the Milestone 2 merge, `requires Blender execution` is **no longer an open label for the
pipeline scripts** — Blender runs them in CI. It remains open for anything that needs a human
looking at the result in the Blender viewport, which is `requires visual inspection`.

## Privacy

Reference photographs and any biometric-adjacent material must remain in a machine-local
`LocalReference/` directory, which is excluded by `.gitignore` by name. No such material is
committed, packaged or transmitted. See `Documentation/DRIVER_PIPELINE_DESIGN.md` §1–§2.

## Progress

| Milestone | State | Output |
| --- | --- | --- |
| **0A — Technical foundation** | Complete | `Documentation/` — design documents |
| **0B — Blender pipeline foundation** | Complete, **executed and green in CI** | `BlenderPipeline/` — nine `af_*.py` scripts |
| **1 — Unreal project foundation** | Complete, never compiled | `Unreal/` — six C++ modules; `Tools/af_static_validate.py` |
| **2 — Vehicle implementation** | Authored and merged; 1 of 4 acceptance criteria met | Vehicle/pawn/controller implementations, 37 automation tests, `Tools/af_validate_interfaces.py` |
| **3 onwards** | Partial | See `Documentation/MILESTONE_PLAN.md` |

"Complete, never compiled" for Milestone 1 means every file is authored and the static validator
passes with zero failures, but **nothing has been compiled**, no editor has been opened and no
automation test has been executed — no Unreal Engine exists in the environment where this was
authored. That is unchanged by Milestone 2.

Milestone 0B is different, and the difference is worth stating precisely. `Blender 5.2.0 LTS`
downloads and runs headless in CI on every push, executing
`BlenderPipeline/scripts/af_smoke_test.py`. All seven stages pass: scene setup, geometry
generation, rig, materials, pre-export validation, export and post-export validation. The
pre-export validator reports **19 passed, 0 failed, 1 skipped of 21 checks** (the skip is
permanent and documented). This is `automatically validated`, not `requires Blender execution`.

For Milestone 2 the four acceptance criteria are:

1. The vehicle accelerates, brakes and steers — **not met**, `requires playtesting`.
2. It does not fall through the ground, oscillate or invert at rest — **not met**,
   `requires playtesting`.
3. All engine vehicle access goes through `UAFVehicleCompatibilityLayer` — **met**,
   `automatically validated`.
4. Imported skeleton bone names match `UAFBoneNameMap` — **not met**,
   `requires Unreal Editor verification`.

Criterion 4 deserves a note rather than a bare "not met". The Blender smoke test now prints the
full eleven-bone hierarchy on every CI run, with each bone's parent and head position in both
metres and centimetres, and the rig stage asserts `bone_order_matches_config == True`. So the
*producing* side of the contract is verified continuously. What remains unverified is the
*consuming* side: no FBX has been imported into an Unreal editor, because no Unreal editor
exists here. Criterion 4 closes when someone imports the exported asset and reads the skeleton.

Only criterion 3 can be evaluated without an engine, and it is enforced on every push. See
`Documentation/MILESTONE_2_IMPLEMENTATION.md` and `Unreal/README.md` §7.

## Repository layout

```
Documentation/     Design documents, decision log, version matrix
BlenderPipeline/   Blender-side authoring, validation and export scripts
Unreal/            The Unreal Engine 5.8 project and its six C++ modules  (D-027)
Tools/             Standalone tooling that needs neither Blender nor Unreal
```

## Validation

```
python3 Tools/af_static_validate.py     --root .
python3 Tools/af_validate_interfaces.py --self-test
python3 Tools/af_validate_interfaces.py --root .
```

Standard library only; neither needs an engine. Both run in CI on Python 3.9 and 3.12 on every
push.

`af_static_validate.py` enforces the module dependency graph, the module boundaries, the
vehicle-backend chokepoint, telemetry literal containment, path portability, header hygiene, the
originality rules and the Blender/Unreal bone agreement. It is mutation-tested — 11 of 11
injected defects detected (D-030).

`af_validate_interfaces.py` compares every `override` against the pure virtual it claims to
implement and fails on a return-type mismatch. It was written because the first validator was
structurally unable to detect D-035, a real mismatch that had been sitting in `main`. It carries
a nine-case mutation suite in `--self-test`, which CI runs *before* the real check so that a
checker which has stopped working fails the build rather than reporting a green tree (D-037).

`Tools/af_mesh_quality.py` audits generated geometry — winding, manifoldness, degenerate faces,
normals, bounds and budgets — across 13 check families. Its `--self-test` carries 46 mutation
cases and runs before the real audit, same house rule. It was written in Milestone 4 and
immediately found a real defect: every face produced by the box generator was wound inward,
giving a signed volume of −1.0. The generator was fixed, not the test (D-047).

A third job runs the Blender pipeline itself:

```
blender --background --factory-startup --python BlenderPipeline/scripts/af_smoke_test.py
```

CI resolves the newest `5.2.x` build from `download.blender.org` by directory listing rather
than pinning a patch number, installs the GL libraries a headless Blender still links against,
and uploads `BlenderPipeline/reports/` as an artifact whether the run passes or fails. The
harness exits 0 on success, 1 on validation failure, 2 if `bpy` is unavailable and 3 if a stage
raised.

This job is what caught D-040. The generated halo arc reached **0.97415 m** against a design
envelope of **0.950 m** with a **0.010 m** tolerance — a 24 mm breach that no static check could
have seen, because it only exists once the geometry is actually built. The apex is now solved
downward from the envelope instead of being scaled from the halo tube radius, and lands at
**0.940 m**. Full detail in `DECISION_LOG.md` D-040.

## Next milestone

**3.** See `Documentation/MILESTONE_PLAN.md`.
