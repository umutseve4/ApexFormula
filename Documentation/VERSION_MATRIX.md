# ApexFormula — Version Matrix

**Document status:** statically authored (Milestone 0A). No tool listed here has been launched, compiled against or executed by this document's author. Every entry is a *pinned intent*, not an observed installation.

---

## 1. Pinned Environment

| Component | Pinned value | Role | How it was fixed |
| --- | --- | --- | --- |
| Game engine | Unreal Engine **5.8** | Runtime, rendering, physics host, MetaHuman destination, packaging | Fixed by project decision — not to be re-opened |
| DCC application | Blender **5.2 LTS** | Procedural vehicle generation, rigging, validation, export | Fixed by project decision |
| Operating system | **Windows** | Development and target platform | Fixed by project decision |
| Gameplay language | **C++** | Architecture, systems, simulation, data types | Fixed by project decision |
| Configuration/visual layer | **Blueprints** | Asset assignment, visual configuration, tuning, animation, UI, level configuration | Fixed by project decision |
| Pipeline scripting | **Blender Python** | Procedural generation and validation | Fixed by project decision |
| Primary interchange format | **FBX** | Skeletal mesh, skeleton, static mesh, collision, LODs | Fixed by project decision |
| Secondary interchange format | **GLB** | Optional, preview only — never the production path | Fixed by project decision |
| Version control | **Git** | Source of truth for text assets | Fixed by project decision |
| Large file handling | **Git LFS** | Binary and large asset storage | Fixed by project decision |

**Rule:** these choices are not to be re-litigated during implementation milestones. Changing any of them is a decision-log event, not an implementation detail.

---

## 2. Language and Authoring Split

| Concern | Owner | Rationale |
| --- | --- | --- |
| Module and class architecture | C++ | Type safety, refactorability, testability |
| Vehicle simulation models (tyre, aero, energy, fuel, brake, drivetrain, setup) | C++ | Numerical stability, per-tick cost, unit-testability |
| Race rules, timing, session state | C++ | Correctness matters more than iteration speed |
| Telemetry bus and logging | C++ | Must be available to every layer |
| Asset assignment (which mesh, which material, which Data Asset) | Blueprint | Iteration without recompilation |
| Visual configuration and tuning values | Blueprint / Data Asset | Designed to change often |
| Animation graphs and state machines | Blueprint | Authored, not computed |
| UI and menus | Blueprint | Layout iteration |
| Level configuration | Blueprint | Per-level variation |
| Procedural geometry, rig construction, mesh validation, export | Blender Python | Runs outside the engine, before import |

**Boundary rule:** no gameplay decision may exist only in a Blueprint. Blueprints select and configure; C++ decides.

---

## 3. Interchange Format Policy

| Format | Status | Used for | Not used for |
| --- | --- | --- | --- |
| FBX | **Primary** | Skeletal meshes, skeletons, static meshes, UCX collision, LOD chains | — |
| GLB | **Optional, preview only** | Quick external viewing and sanity checks outside Unreal | Never the import path into the project; never a source of truth |
| JSON | Supporting | Blender validation reports under `BlenderPipeline/reports/`, committed as plain text | Not an asset format |
| PNG / TGA | Supporting | Textures, stored via Git LFS | Not a source-of-truth authoring format |

If FBX and GLB ever disagree, FBX is correct by definition and the GLB path is regenerated or dropped.

---

## 4. Version-Sensitive Areas

These are the places where a version difference is most likely to break something. Each is listed with the failure mode to look for.

| # | Area | Version-sensitive because | Failure mode to watch for |
| --- | --- | --- | --- |
| 4.1 | Blender FBX exporter option names and defaults | Exporter options have historically been renamed and re-defaulted between Blender releases | `af_export.py` raising unexpected-keyword errors, or silently exporting with the wrong scale/axes |
| 4.2 | Blender leaf-bone injection | The exporter can append leaf bones unless explicitly disabled | Unreal skeleton containing `*_end` bones absent from `UAFBoneNameMap` |
| 4.3 | Blender unit scale and scene scale | Scene scale interacts multiplicatively with exporter scale | Vehicle imported 100× too large or too small |
| 4.4 | Coordinate handedness | Blender is right-handed (+Z up), Unreal is left-handed (+Z up) | Mirrored vehicle; steering reversed; wheels on the wrong side |
| 4.5 | Blender Python API breaking changes | `bpy` API is not stable across major releases | Scripts failing at import time rather than at run time |
| 4.6 | Unreal Chaos Vehicles API | The engine vehicle system evolves between releases | Compile failures in `UAFVehicleCompatibilityLayer`; changed wheel setup semantics |
| 4.7 | Unreal module and build system | Build rules and module dependency declarations change | Link errors; modules failing to load in the editor |
| 4.8 | Unreal MetaHuman tooling | MetaHuman authoring moved into the editor and continues to change | Milestone 7 workflow steps not matching the installed toolset |
| 4.9 | Unreal FBX import defaults | Import options such as skeleton reuse, normals and smoothing change between versions | Duplicate skeletons; broken normals; auto-generated LODs replacing authored ones |
| 4.10 | UCX collision naming convention | Import-time convex collision recognition depends on exact prefix handling | Collision silently discarded, vehicle falling through the world |
| 4.11 | Git LFS tracking rules | Patterns must exist before the first commit of a matching file | Large binaries committed directly into Git history |
| 4.12 | Windows path length and casing | Deep asset paths and case-insensitive filesystems | Assets that build locally but fail on a case-sensitive checkout |

---

## 5. Assumptions Requiring Verification

Everything in this section is an **assumption**, not a fact. None of it has been observed. Each item states what must be checked and how.

| # | Assumption | How to verify | Verification label |
| --- | --- | --- | --- |
| 5.1 | Unreal Engine 5.8 is installed and a Windows C++ toolchain is present and working | Create the Milestone 1 project and build it from clean | requires local compilation |
| 5.2 | Blender 5.2 LTS is installed and its Python interpreter can run the `af_*.py` scripts headless | Run `af_smoke_test.py` from the command line | requires Blender execution |
| 5.3 | The Blender 5.2 LTS FBX exporter accepts the option names used in `af_export.py` | Execute the exporter with the documented option set and read the resulting error or success | requires Blender execution |
| 5.4 | Leaf-bone injection can be disabled in the installed exporter | Export the rig, then list the bones in the resulting FBX | requires Blender execution |
| 5.5 | The unit and axis conversion described in `BLENDER_PIPELINE_DESIGN.md` §2 produces a correctly scaled, non-mirrored vehicle in Unreal | Import the FBX and measure the bounding box in centimetres; check which side the steering wheel is on | requires Unreal Editor verification |
| 5.6 | Chaos Vehicles in UE 5.8 supports the wheel and suspension configuration assumed by the prototype decision | Build the Milestone 2 vehicle and drive it | requires local compilation, then requires playtesting |
| 5.7 | `UAFVehicleCompatibilityLayer` is a sufficient abstraction to allow the Milestone 10 migration without rewriting gameplay code | Attempt the first model migration behind the layer | requires local compilation |
| 5.8 | UCX convex collision survives export and is recognised on import | Import and inspect the collision on the static mesh | requires Unreal Editor verification |
| 5.9 | Authored LODs are preserved rather than replaced by importer-generated LODs | Inspect LOD count and triangle counts after import | requires Unreal Editor verification |
| 5.10 | The MetaHuman workflow steps in `DRIVER_PIPELINE_DESIGN.md` §5 match the tooling actually present in UE 5.8 | Walk the eight steps in the editor and record deviations | requires Unreal Editor verification |
| 5.11 | Git LFS is installed and its filters are active in this repository | Commit a tracked binary and confirm the pointer file, not the binary, is in the tree | automatically validated |
| 5.12 | The reference development machine can reach the Final Quality frame-rate target | Profile at Milestone 12 and record measured numbers | requires playtesting |
| 5.13 | The face and bone budgets in `BLENDER_PIPELINE_DESIGN.md` are achievable for a formula-style vehicle at the intended visual quality | Generate the Milestone 4 vehicle and read the validation report | requires Blender execution, then requires visual inspection |
| 5.14 | Placeholder materials authored in Blender import without polluting the Unreal material library | Import and inspect the created material assets | requires Unreal Editor verification |
| 5.15 | Nothing in the committed tree contains private reference material, credentials, machine configuration or build output | Inspect the repository tree and `.gitignore` coverage | statically inspected |
| 5.16 | The FBX exporter option names in `af_pipeline_config.FBX_EXPORT_SETTINGS` are the names Blender 5.2 LTS actually accepts | Run `af_export.py`; it introspects the operator's RNA and prints every key it had to drop (D-026) | requires Blender execution |
| 5.17 | `bpy.types.MeshPolygon.edge_keys` and `bpy.types.MeshEdge.key` exist in Blender 5.2 LTS | Run `af_validate.py`; validation checks 3 and 4 (non-manifold and boundary edges) depend on them | requires Blender execution |
| 5.18 | `bpy.ops.export_scene.fbx` is still the export operator's path in Blender 5.2 LTS, and the FBX add-on is enabled by default | Run `af_export.py` and observe whether the operator resolves | requires Blender execution |
| 5.19 | The `DECIMATE` modifier's `COLLAPSE` ratio produces LOD meshes within the face budgets in `BLENDER_PIPELINE_DESIGN.md` | Generate LODs and read the measured polygon counts in the validation report | requires Blender execution |
| 5.20 | The eight `af_*.py` scripts are syntactically valid Python for the interpreter Blender 5.2 LTS embeds | `python -m py_compile` passes on all eight under CPython 3.12; Blender's embedded interpreter version is unobserved | automatically validated for CPython 3.12 only |

**Reading rule for this section:** if a later document, script comment or commit message asserts any of the above as settled, it is wrong unless it also cites the verification that settled it.

---

## 6. What Is Deliberately Not Pinned

| Item | Why it is left open |
| --- | --- |
| Exact UE 5.8 patch/hotfix revision | Not yet observed; will be recorded once the project is created |
| Exact Blender 5.2 LTS point release | Not yet observed; will be recorded once the scripts are first executed |
| Windows edition and build number | Not yet observed |
| Git and Git LFS client versions | Not yet observed |
| Compiler/toolchain version | Determined by the installed engine's requirements |
| Target hardware specification | Recorded at Milestone 12 when profiling actually happens |

When any of these becomes observed, it is recorded here with the date and the command that produced it — never guessed.

---

## 7. Verification Ledger for This Document

| Claim | Label |
| --- | --- |
| The pinned versions in §1 are the project's fixed decisions | statically inspected |
| The C++/Blueprint split in §2 matches `TECHNICAL_ARCHITECTURE.md` | statically inspected |
| The FBX-primary / GLB-optional policy in §3 matches `BLENDER_PIPELINE_DESIGN.md` §7 and §8 | statically inspected |
| The version-sensitive areas in §4 are real risk surfaces | statically inspected — none has been triggered, because nothing has been run |
| Every item in §5 is unverified | statically inspected — §5 exists precisely because these are unverified |
| §5.16 to §5.19 are the version-sensitive surfaces introduced by the Milestone 0B scripts | statically inspected |
| §5.20 records the one thing about the scripts that was actually measured, and states its limit | automatically validated |
| Any listed tool is installed, runnable, or of the stated version | not claimed — see §5.1, §5.2, §5.11 |
