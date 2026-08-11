# ApexFormula

An original 3D formula racing game built with Unreal Engine 5.8 and Blender 5.2 LTS.

> **Current state:** Milestone 2 authored, largely unverified — documentation, the Blender
> pipeline scripts, the Unreal C++ project foundation, and the vehicle implementation behind it.
> There is no art asset in this repository yet. Nothing here has been compiled, executed,
> imported or visually inspected.

---

## What this repository contains

Design documents, the Blender-side authoring and export pipeline, the Unreal Engine 5.8 C++
project foundation and vehicle implementation, and the standalone static validators that check
them against each other.

```
ApexFormula/
├── Documentation/          design documents, decision log, version matrix
├── BlenderPipeline/        eight af_*.py scripts + README
├── Unreal/                 .uproject, Config/, Source/ with six C++ modules
├── Tools/
│   ├── af_static_validate.py
│   └── af_validate_interfaces.py
├── .github/workflows/      static validation on every push
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
| **0A — Technical foundation** | Complete | `Documentation/` — design documents |
| **0B — Blender pipeline foundation** | Complete | `BlenderPipeline/` — eight `af_*.py` scripts |
| **1 — Unreal project foundation** | Complete, unverified | `Unreal/` — six C++ modules; `Tools/af_static_validate.py` |
| **2 — Vehicle implementation** | Authored; 1 of 4 acceptance criteria met | Vehicle/pawn/controller implementations, 10 automation tests, `Tools/af_validate_interfaces.py` |
| **3 onwards** | Not started | See `Documentation/MILESTONE_PLAN.md` |

"Complete, unverified" for Milestone 1 means every file is authored and the static validator
passes with zero failures, but **nothing has been compiled**, no editor has been opened and no
automation test has been executed — no Unreal Engine exists in the environment where this was
authored.

For Milestone 2 the four acceptance criteria are:

1. The vehicle accelerates, brakes and steers — **not met**, `requires playtesting`.
2. It does not fall through the ground, oscillate or invert at rest — **not met**,
   `requires playtesting`.
3. All engine vehicle access goes through `UAFVehicleCompatibilityLayer` — **met**,
   `automatically validated`.
4. Imported skeleton bone names match `UAFBoneNameMap` — **not met**,
   `requires Unreal Editor verification`.

Only the third can be evaluated without an engine, and it is enforced on every push. See
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

## Next milestone

**3.** See `Documentation/MILESTONE_PLAN.md`.
