# ApexFormula

An original 3D formula racing game built with Unreal Engine 5.8 and Blender 5.2 LTS.

> **Current state:** Milestones 0B and 1 are **authored but unverified** — documentation, the
> Blender pipeline scripts and the Unreal C++ project foundation all exist and pass static
> validation. There is no art asset in this repository yet. Nothing has been compiled, no
> Blender scene has been built, no editor has been opened and nothing has been visually
> inspected.

---

## What this repository contains

Design documents, the Blender-side authoring and export pipeline, the Unreal Engine 5.8 C++
project foundation, and the standalone static validator that checks them against each other.

```
ApexFormula/
├── Documentation/          eight design documents, decision log, version matrix
├── BlenderPipeline/        eight af_*.py scripts + README
├── Unreal/                 .uproject, Config/, Source/ with six C++ modules
├── Tools/
│   └── af_static_validate.py
├── .github/workflows/      continuous validation (static + headless Blender)
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

- Asset prefix `AF_`; C++ prefixes `UAF`, `AAF`, `FAF`, `IAF`; Blender script prefix `af_`.
- Metres inside Blender, centimetres at the Unreal boundary (`CM_PER_UNIT = 100.0`).
- Bone names are defined once (`af_pipeline_config.py` / `UAFBoneNameMap`) and never hardcoded.
- The project uses no real motorsport branding, teams, drivers, sponsors, liveries, or exact
  reproductions of real cars or circuits.

## Verification labels

Every claim in this repository carries one of the following labels. They are used literally,
not decoratively.

`statically inspected` · `automatically validated` · `requires Blender execution` ·
`requires Unreal Editor verification` · `requires local compilation` ·
`requires visual inspection` · `requires playtesting`

Each document ends with a Verification Ledger applying these labels to its own claims.

### Milestone state vocabulary

Milestone state and milestone verification are two different things, and this repository keeps
them apart deliberately:

| State | Meaning |
| --- | --- |
| **Authored, unverified** | Every file exists and static checks pass, but nothing carrying an execution label has been run. |
| **Verified** | Evidence exists for every label the milestone declares in `MILESTONE_PLAN.md`. |
| **Complete** | Verified, and checked against that milestone's acceptance criteria. |

This follows Cross-Milestone Rule 1: *no milestone may claim completion without evidence
carrying a verification label.* Authoring code is not evidence about that code.

## Privacy

Reference photographs and any biometric-adjacent material must remain in a machine-local
`LocalReference/` directory, which is excluded by `.gitignore` by name. No such material is
committed, packaged or transmitted. See `Documentation/DRIVER_PIPELINE_DESIGN.md` §1–§2.

## Progress

| Milestone | State | Blocking label | Output |
| --- | --- | --- | --- |
| **0A — Technical foundation** | Complete | — | `Documentation/` — eight design documents |
| **0B — Blender pipeline foundation** | Authored, unverified | `requires Blender execution` | `BlenderPipeline/` — eight `af_*.py` scripts |
| **1 — Unreal project foundation** | Authored, unverified | `requires local compilation`, `requires Unreal Editor verification` | `Unreal/` — six C++ modules; `Tools/af_static_validate.py` |
| **2 onwards** | Not started | — | See `Documentation/MILESTONE_PLAN.md` |

**Milestone 0A is genuinely complete** — its only verification label is `statically inspected`,
and that has been satisfied.

**Milestone 0B is authored, not complete.** The scripts compile, `af_pipeline_config.self_check()`
passes and the `bpy`-free helpers were exercised by an offline harness at 47 checks with 0
failures — but no script has ever run inside Blender, so the twenty-one scene checks, the
exported bone list and the exporter option names remain unproven. See
`BlenderPipeline/README.md` §1 and §9. As of this commit, the CI workflow runs
`af_smoke_test.py` headlessly on every push; when it is green, the execution-dependent rows of
that ledger become evidence rather than intent.

**Milestone 1 is authored, not complete.** The static validator passes at 2300 checks with zero
failures and zero warnings, and is itself mutation-tested at 11 of 11 injected defects detected
(D-030). But nothing has been compiled, no editor has been opened, and none of the 27 declared
automation tests has ever been discovered or executed — no Unreal Engine exists in the
environment where this was authored. The `ChaosVehicles` module names and the API signatures in
`VERSION_MATRIX.md` §5.21–§5.26 remain **assumptions**. See `Unreal/README.md` §7.

### What can progress without Unreal Engine

Milestone dependencies are recorded in `Documentation/MILESTONE_PLAN.md`. One branch of the
graph does not touch the engine at all:

| Milestone | Dependencies | Needs Unreal? |
| --- | --- | --- |
| **4 — Procedural Vehicle Visual Prototype** | 0B | **No** — `requires Blender execution`, `automatically validated`, `requires visual inspection` |
| 2, 3, 5–12 | 1 and onward | Yes |

Milestone 4 is therefore reachable on any machine that can run Blender, which is a far lower
bar than UE 5.8 plus a Windows C++ toolchain.

This does not lower the target. Cross-Milestone Rule 3: *hardware weakness never lowers the
Final Quality target — it changes what is previewed, not what is authored.*

## Repository layout

```
Documentation/     Design documents, decision log, version matrix
BlenderPipeline/   Blender-side authoring, validation and export scripts
Unreal/            The Unreal Engine 5.8 project and its six C++ modules  (D-027)
Tools/             Standalone tooling that needs neither Blender nor Unreal
```

## Validation

```
python3 Tools/af_static_validate.py --root .
```

Standard library only; needs neither engine. Enforces the module dependency graph, the module
boundaries, the vehicle-backend chokepoint, telemetry literal containment, path portability,
header hygiene, the originality rules and the Blender/Unreal bone agreement. The validator is
itself mutation-tested — 11 of 11 injected defects detected (D-030).

### Continuous validation

`.github/workflows/validate.yml` runs on every push and pull request:

| Job | What it proves | Label satisfied |
| --- | --- | --- |
| `static-validation` | The 2300 repository checks, the config self-check, byte compilation of all scripts | `automatically validated` |
| `blender-pipeline` | `af_smoke_test.py` executed end to end in headless Blender; `reports/`, `exports/` and `generated/` uploaded as artifacts | `requires Blender execution` |

Unreal Engine cannot run on hosted runners. `requires local compilation`,
`requires Unreal Editor verification`, `requires playtesting` and `requires visual inspection`
are **not** covered by CI and must still be satisfied on a real machine. A green tick here
never implies otherwise.

## Next milestone

**2** if an Unreal-capable machine is available; otherwise **4**, which depends only on 0B.
See `Documentation/MILESTONE_PLAN.md`.
