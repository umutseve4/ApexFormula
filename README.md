# ApexFormula

An original 3D formula racing game built with Unreal Engine 5.8 and Blender 5.2 LTS.

---

## What this repository contains

At Milestone 0A the repository contains **documentation only**: the architecture, pipeline
contracts, milestone plan and decision records that later milestones are built against.

```
ApexFormula/
├── Documentation/
│   ├── PROJECT_VISION.md
│   ├── TECHNICAL_ARCHITECTURE.md
│   ├── VEHICLE_SYSTEM_DECISION.md
│   ├── BLENDER_PIPELINE_DESIGN.md
│   ├── DRIVER_PIPELINE_DESIGN.md
│   ├── MILESTONE_PLAN.md
│   ├── VERSION_MATRIX.md
│   └── DECISION_LOG.md
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
