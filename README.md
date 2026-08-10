# ApexFormula

An original 3D formula racing game built with Unreal Engine 5.8 and Blender 5.2 LTS.

> **Current state:** Milestone 1 complete, unverified — documentation, the Blender pipeline
> scripts and the Unreal C++ project foundation. There is no art asset in this repository yet.
> Nothing here has been compiled, executed, imported or visually inspected.

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

## Privacy

Reference photographs and any biometric-adjacent material must remain in a machine-local
`LocalReference/` directory, which is excluded by `.gitignore` by name. No such material is
committed, packaged or transmitted. See `Documentation/DRIVER_PIPELINE_DESIGN.md` §1–§2.

## Progress

| Milestone | State | Output |
| --- | --- | --- |
| **0A — Technical foundation** | Complete | `Documentation/` — eight design documents |
| **0B — Blender pipeline foundation** | Complete | `BlenderPipeline/` — eight `af_*.py` scripts |
| **1 — Unreal project foundation** | Complete, unverified | `Unreal/` — six C++ modules; `Tools/af_static_validate.py` |
| **2 onwards** | Not started | See `Documentation/MILESTONE_PLAN.md` |

"Complete, unverified" for Milestone 1 means every file is authored and the static validator
passes at 2300 checks with zero failures, but **nothing has been compiled**, no editor has been
opened and no automation test has been executed — no Unreal Engine exists in the environment
where this was authored. See `Unreal/README.md` §7 for the full ledger.

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

## Next milestone

**2.** See `Documentation/MILESTONE_PLAN.md`.
