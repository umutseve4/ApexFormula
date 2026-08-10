# ApexFormula

An original 3D formula racing game built with **Unreal Engine 5.8** and
**Blender 5.2 LTS**.

ApexFormula is an independent, original work. It does not reference, reproduce,
or imply any real motorsport series, team, driver, sponsor, livery, circuit, or
vehicle. All vehicles, circuits, identities, and audio are original creations.

---

## Current status — Milestone 0A complete

This repository currently contains **technical documentation only**.

There is no Unreal project, no Blender script, no geometry, no rig, and no
binary asset in this repository yet. Nothing here has been compiled, opened,
executed, imported, or visually inspected.

Milestone 0B (the Blender pipeline scripts) has **not** been started.

---

## Honesty labels

Every claim in this repository carries exactly one of the following labels.
Nothing is asserted as working unless it was actually observed to work.

| Label | Meaning |
|---|---|
| `statically inspected` | Reviewed by reading only |
| `automatically validated` | Checked by an automated validator that was actually run |
| `requires Blender execution` | Must be run inside Blender to be confirmed |
| `requires Unreal Editor verification` | Must be confirmed in the Unreal Editor |
| `requires local compilation` | Must be compiled locally to be confirmed |
| `requires visual inspection` | Correctness is a visual judgement |
| `requires playtesting` | Correctness is a gameplay-feel judgement |

At the time of this commit, every statement in this repository is
`statically inspected` unless the document says otherwise.

---

## Document index

| Document | Purpose |
|---|---|
| [`Documentation/PROJECT_VISION.md`](Documentation/PROJECT_VISION.md) | Identity, originality rules, design goals, quality targets, verification and privacy posture |
| [`Documentation/TECHNICAL_ARCHITECTURE.md`](Documentation/TECHNICAL_ARCHITECTURE.md) | Modules, Blueprint boundaries, components, Data Assets, configuration, bone convention, testing, logging, units |
| [`Documentation/VEHICLE_SYSTEM_DECISION.md`](Documentation/VEHICLE_SYSTEM_DECISION.md) | TDR-001 — candidate vehicle systems, comparison, recommendation, re-evaluation triggers |
| [`Documentation/BLENDER_PIPELINE_DESIGN.md`](Documentation/BLENDER_PIPELINE_DESIGN.md) | Script set and rules, collections, units and axes, FBX export and import settings, naming, LODs, validation, reporting |
| [`Documentation/DRIVER_PIPELINE_DESIGN.md`](Documentation/DRIVER_PIPELINE_DESIGN.md) | Privacy boundaries, prohibited claims, source-mesh routes, MetaHuman responsibilities, quality tiers, manual checkpoints |
| [`Documentation/MILESTONE_PLAN.md`](Documentation/MILESTONE_PLAN.md) | All milestones `0A`, `0B`, `1`–`12` with objectives, dependencies, acceptance criteria, risks, and exclusions |
| [`Documentation/VERSION_MATRIX.md`](Documentation/VERSION_MATRIX.md) | Single source of truth for versions, responsibility split, interchange formats, compatibility layers, assumptions |
| [`Documentation/DECISION_LOG.md`](Documentation/DECISION_LOG.md) | Every decision with ID, rationale, reversibility, status, and open items |

### Single sources of truth

To prevent contradictory duplicates, the following facts are defined in exactly
one place:

- **Versions** → `VERSION_MATRIX.md`
- **Bone names and hierarchy** → `TECHNICAL_ARCHITECTURE.md` §7
- **Units, axes, and export/import settings** → `BLENDER_PIPELINE_DESIGN.md` §5–§6
- **Decisions** → `DECISION_LOG.md`

---

## Naming conventions

| Scope | Convention | Example |
|---|---|---|
| Project identity | `ApexFormula` | `ApexFormulaVehicle` |
| Unreal assets | `AF_` | `AF_VehicleDefinition` |
| Blender scripts | `af_` | `af_export.py` |
| Material instances | `MI_AF_<Category>_<Surface>` | `MI_AF_Chassis_Paint` |

---

## Privacy

Personal reference material is never uploaded, transmitted, embedded, packaged,
or committed. It stays on the local machine under `Local/`, which is excluded
from version control in its entirety. No photographs have been requested and
none are required to review this milestone.

---

## Repository layout

```
ApexFormula/
├── .gitattributes
├── .gitignore
├── README.md
└── Documentation/
    ├── PROJECT_VISION.md
    ├── TECHNICAL_ARCHITECTURE.md
    ├── VEHICLE_SYSTEM_DECISION.md
    ├── BLENDER_PIPELINE_DESIGN.md
    ├── DRIVER_PIPELINE_DESIGN.md
    ├── MILESTONE_PLAN.md
    ├── VERSION_MATRIX.md
    └── DECISION_LOG.md
```
