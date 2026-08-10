# ApexFormula — Decision Log

**Document status:** statically authored (Milestone 0A).

**Purpose.** One numbered entry per decision that shapes the project. Each entry records what was decided, why, what was rejected, and how reversible it is. Later milestones append entries; they do not silently edit earlier ones. When a decision is superseded, the original entry stays and gains a "Superseded by" line.

**Date convention.** All entries below were established during Milestone 0A, on **2025-06-01** (project foundation date). Later entries carry their own dates.

**Reversibility scale.**
- **High** — can be changed in a single milestone with local edits.
- **Medium** — changeable, but requires rework across several systems or re-export of assets.
- **Low** — changing it invalidates substantial completed work.

---

## D-001 — Project identity is ApexFormula

**Date:** 2025-06-01
**Decision.** The project is named **ApexFormula**. Asset prefix `AF_`, C++ prefixes `UAF` / `AAF` / `FAF` / `IAF`, Blender script prefix `af_`.
**Rationale.** A single unambiguous identity that carries no real-world motorsport association and produces short, greppable prefixes.
**Rejected.** Any name containing the token `F1`, any real series, team, manufacturer or circuit name.
**Reversibility:** Medium — a rename touches every file, class and asset, but is mechanical.

---

## D-002 — Strict originality constraint

**Date:** 2025-06-01
**Decision.** No real motorsport branding, team names, driver names, sponsor marks, logos, liveries, or exact reproductions of real cars or circuits. The token `F1` must not appear in any project name, filename, class name, asset name, script name, folder name, document title or public-facing term.
**Rationale.** Legal safety and creative independence. The project is a formula-style racing game, not a licensed product.
**Rejected.** "Inspired-by" liveries and thinly renamed real circuits — both were judged to carry the same risk as direct use.
**Reversibility:** Low — every asset produced under this rule assumes it.

---

## D-003 — Fixed technology stack

**Date:** 2025-06-01
**Decision.** Unreal Engine 5.8, Blender 5.2 LTS, Windows, C++ for gameplay architecture, Blueprints for asset assignment/visual configuration/tuning/animation/UI/level configuration, Blender Python for procedural generation and validation, Git plus Git LFS for version control.
**Rationale.** Removes an entire class of recurring debate. Details in `VERSION_MATRIX.md` §1.
**Rejected.** Alternative engines and DCC applications; a Blueprint-first gameplay architecture.
**Reversibility:** Low.

---

## D-004 — Five-layer architecture

**Date:** 2025-06-01
**Decision.** Core, Vehicle, Rules and Timing, Session, Presentation — with dependencies flowing in one direction only. Detailed in `TECHNICAL_ARCHITECTURE.md` §2.
**Rationale.** Keeps simulation testable without the renderer, and keeps presentation replaceable without touching simulation.
**Rejected.** A monolithic gameplay module; a presentation layer permitted to write simulation state.
**Reversibility:** Medium.

---

## D-005 — Six C++ modules

**Date:** 2025-06-01
**Decision.** `ApexFormulaCore`, `ApexFormulaVehicle`, `ApexFormulaRace`, `ApexFormulaUI`, `ApexFormulaEditor`, `ApexFormulaTests`.
**Rationale.** Maps the five layers onto compilable units, plus editor-only and test-only code that must not ship in the runtime.
**Rejected.** A single game module — it makes editor-only code leak into packaged builds.
**Reversibility:** Medium.

---

## D-006 — Component-based vehicle composition

**Date:** 2025-06-01
**Decision.** Vehicle behaviour is composed from components — `UAFTyreSetComponent`, `UAFAeroComponent`, `UAFEnergySystemComponent`, `UAFFuelComponent`, `UAFBrakeComponent`, `UAFDrivetrainComponent`, `UAFVehicleSetupComponent`, `UAFVehicleTelemetryComponent`, `UAFRaceParticipantComponent` — rather than from a deep pawn inheritance chain.
**Rationale.** Each model can be developed, unit-tested and migrated independently at Milestone 10.
**Rejected.** A monolithic vehicle pawn holding all simulation state.
**Reversibility:** Medium.

---

## D-007 — Data-Asset-driven configuration

**Date:** 2025-06-01
**Decision.** Tuning values live in Data Assets, not in code constants or Blueprint literals. Twelve Data Asset types are defined in `TECHNICAL_ARCHITECTURE.md` §5, including `UAFBoneNameMap` and `UAFQualityProfile`.
**Rationale.** Tuning must be changeable without recompilation, diffable, and shareable between the editor and automated tests.
**Rejected.** Config `.ini` files as the primary tuning surface; hardcoded constants.
**Reversibility:** Medium.

---

## D-008 — Prototype vehicle system is Chaos Vehicles behind a compatibility layer

**Date:** 2025-06-01
**Decision.** Milestone 2 uses the engine's Chaos Vehicles system, but every access goes through `UAFVehicleCompatibilityLayer`. No gameplay code calls the engine vehicle API directly.
**Rationale.** Fastest route to a drivable car without committing the project to the engine's model. Full analysis in `VEHICLE_SYSTEM_DECISION.md` §4.
**Rejected.** Building a custom vehicle model immediately (too slow to first playable); using Chaos directly without a layer (blocks D-009).
**Reversibility:** High — that is the entire point of the layer.

---

## D-009 — Long-term vehicle system is a hybrid

**Date:** 2025-06-01
**Decision.** Long term, the engine provides rigid-body dynamics and collision; ApexFormula owns the tyre, aerodynamic, energy, fuel and brake models. Migration order is documented in `VEHICLE_SYSTEM_DECISION.md` §5 and executed at Milestone 10.
**Rationale.** The engine's built-in models are not sufficient for the intended simulation depth, but replacing rigid-body dynamics and collision would be a large cost with little gain.
**Rejected.** Full custom physics including integration and collision; permanent reliance on the engine's vehicle model.
**Reversibility:** Medium — reversible per model, since each is migrated separately behind the layer.

---

## D-010 — Blender is the source of truth for geometry and rigs

**Date:** 2025-06-01
**Decision.** Vehicle geometry, collision proxies, LODs and the armature are generated and validated in Blender. Unreal imports; it does not author geometry.
**Rationale.** Procedural generation is reproducible from config and reviewable as text.
**Rejected.** Modelling inside Unreal; hand-modelled one-off assets as the primary path.
**Reversibility:** Medium.

---

## D-011 — Unreal owns final shading

**Date:** 2025-06-01
**Decision.** Blender exports placeholder materials only. Final material authoring, instancing and shading happen in Unreal.
**Rationale.** Avoids maintaining two divergent material systems, and avoids importing a material library that must then be replaced.
**Rejected.** Authoring production materials in Blender and attempting to translate them on import.
**Reversibility:** High.

---

## D-012 — Central bone-name convention

**Date:** 2025-06-01
**Decision.** Eleven bones: `AF_Root`, `AF_Chassis`, `AF_Steering`, `AF_Wheel_FL/FR/RL/RR`, `AF_Suspension_FL/FR/RL/RR`. Hierarchy: `AF_Root` → `AF_Chassis` → { `AF_Steering`, `AF_Suspension_*` }, with each `AF_Wheel_*` parented to its matching `AF_Suspension_*`. The names are defined once in `af_pipeline_config.py` and mirrored in `UAFBoneNameMap`; they are never hardcoded elsewhere.
**Rationale.** Bone names are the single most fragile contract between Blender and Unreal. Centralising them makes a rename a one-line change plus a re-export.
**Rejected.** Hardcoding bone names at each use site; relying on bone indices.
**Reversibility:** Medium — a rename requires re-export and re-import of every skeletal asset.

---

## D-013 — Explicit unit and axis contract

**Date:** 2025-06-01
**Decision.** Metres inside Blender (scene scale 1.0, 1 BU = 1 m, +X forward, +Z up, +Y vehicle-left); centimetres at the Unreal boundary (1 uu = 1 cm, +X forward, +Y right, +Z up); handedness reconciled by a Y-sign flip; a single constant `CM_PER_UNIT = 100.0` performs the scale conversion. Full statement in `BLENDER_PIPELINE_DESIGN.md` §2.
**Rationale.** Scale and mirroring errors are the classic silent failure of a Blender→Unreal pipeline, and they surface only after significant downstream work.
**Rejected.** Working in centimetres inside Blender; relying on the exporter's automatic conversion without stating the expectation.
**Reversibility:** Low — every exported asset encodes this contract.

---

## D-014 — Replay uses periodic authoritative state snapshots with interpolation

**Date:** 2025-06-01
**Decision.** The replay system records **periodic authoritative state snapshots** of race entities and reconstructs playback by **interpolating between snapshots**. Simulation determinism is **not** assumed and is **not** relied upon. Input-replay (recording inputs and re-simulating) is explicitly rejected as the primary mechanism.
**Rationale.** Reproducing a session by re-simulating recorded inputs requires bit-level determinism across builds, hardware, frame rates and physics substepping. That guarantee does not exist here and would be extremely expensive to establish and maintain. Snapshot-plus-interpolation trades storage for correctness, and correctness is what a replay must deliver. It also degrades gracefully: a dropped or corrupted snapshot costs a short interpolation artefact rather than divergence of the entire replay.
**Consequences.**
- Snapshot rate and payload size become a tuning problem, addressed at Milestone 12.
- The telemetry bus (`UAFTelemetryBus`, `TECHNICAL_ARCHITECTURE.md` §10) is the natural capture point.
- Replay fidelity is bounded by snapshot rate, and this is accepted openly rather than hidden.
- The same snapshot structure is a useful starting point for the Milestone 12 multiplayer-boundary preparation.
**Rejected.** Deterministic input replay; full per-frame state recording (storage cost); replay driven by the presentation layer (wrong ownership).
**Reversibility:** Medium — the capture point is generic, so a future deterministic path could be added alongside, but assets and tooling built on snapshots would need rework.

---

## D-015 — Two quality profiles, permanently separated

**Date:** 2025-06-01
**Decision.** Development Preview and Final Quality are distinct profiles, expressed as `UAFQualityProfile` Data Assets. Preview settings are non-destructive overrides. Preview output is never used for presentation. Weak development hardware never lowers the Final Quality target.
**Rationale.** Prevents the common failure where the project's quality ceiling quietly collapses to whatever the development machine renders comfortably.
**Rejected.** A single scalable quality setting; permanently reducing asset quality to improve editor performance.
**Reversibility:** High.

---

## D-016 — FBX is primary, GLB is optional preview only

**Date:** 2025-06-01
**Decision.** FBX is the production interchange format for skeletal meshes, skeletons, static meshes, collision and LODs. GLB may be produced for quick external viewing but is never an import path and never a source of truth.
**Rationale.** One authoritative path avoids two subtly divergent pipelines.
**Rejected.** GLB or USD as the primary path at this stage.
**Reversibility:** Medium.

---

## D-017 — Validation is a gate, not a report

**Date:** 2025-06-01
**Decision.** `af_validate.py` enforces twenty-one checks (`BLENDER_PIPELINE_DESIGN.md` §4) and writes a JSON report to `BlenderPipeline/reports/`. Reports are committed as plain text. A failing validation blocks export.
**Rationale.** A warning that can be ignored will be ignored. Committed reports make regressions visible in diffs.
**Rejected.** Advisory-only validation; reports written to an ignored directory.
**Reversibility:** High.

---

## D-018 — Driver reference material never enters the repository

**Date:** 2025-06-01
**Decision.** Reference photographs and any biometric-adjacent material stay in a machine-local `LocalReference/` directory, which is excluded by `.gitignore` by name. Nothing from it is committed, packaged or transmitted. The seven prohibited claims in `DRIVER_PIPELINE_DESIGN.md` §2 are binding.
**Rationale.** Privacy is not a feature to be added later, and a photograph committed once is in history forever.
**Rejected.** Committing "just the low-resolution ones"; storing reference material in LFS.
**Reversibility:** Low — a leak cannot be undone by a later decision.

---

## D-019 — MetaHuman is the driver destination, with a tiered approach

**Date:** 2025-06-01
**Decision.** The driver's destination is the UE 5.8 MetaHuman system. Quality tiers A (helmeted cockpit), B (visible face at presentation distance) and C (close-up detail) are defined, and **Tier A is built first** (Milestone 6), with MetaHuman integration at Milestone 7.
**Rationale.** A helmeted cockpit driver delivers most of the in-race value at a fraction of the cost and risk, and it validates scale, pose and attachment before any facial work begins.
**Rejected.** Starting from a photorealistic close-up head; hand-building a facial rig in Blender.
**Reversibility:** Medium.

---

## D-020 — Milestone numbering is fixed and shared

**Date:** 2025-06-01
**Decision.** Milestones 0A, 0B, 1–12 as enumerated in `MILESTONE_PLAN.md`. Every document uses these numbers identically. Renumbering is a decision-log event.
**Rationale.** Cross-document references are worthless if the numbering drifts.
**Rejected.** Per-document ad-hoc phase names.
**Reversibility:** High, but disruptive.

---

## D-021 — Honesty and verification labelling

**Date:** 2025-06-01
**Decision.** No document, comment or commit message may claim that the project compiled, the editor opened, a Blender script ran, an asset imported, or a model looks correct, unless that action was genuinely performed. Every stated result carries exactly one label: `statically inspected`, `automatically validated`, `requires Blender execution`, `requires Unreal Editor verification`, `requires local compilation`, `requires visual inspection`, `requires playtesting`. Every document ends with a Verification Ledger.
**Rationale.** Unverified claims compound: a false "this works" at Milestone 2 costs days at Milestone 10. The label makes the epistemic status of every statement explicit and cheap to audit.
**Rejected.** Informal confidence language ("should work", "presumably fine").
**Reversibility:** Low by intent — this is a standing rule, not a phase.

---

## D-022 — Repository hygiene

**Date:** 2025-06-01
**Decision.** The repository excludes Unreal build output (`Binaries/`, `Intermediate/`, `Saved/`, `DerivedDataCache/`), Blender working files under `BlenderPipeline/local/`, `LocalReference/`, credentials, keys and machine configuration. Git LFS tracks binary asset types. `BlenderPipeline/reports/` is **not** excluded, because validation reports are committed plain text (D-017).
**Rationale.** A clean repository is diffable, cloneable and safe to publish.
**Rejected.** Committing build output for convenience; excluding reports along with other generated files.
**Reversibility:** High for the ignore rules, Low for anything already committed.

---

## D-023 — Report filenames are deterministic and carry no timestamp

**Date:** 2025-06-01
**Decision.** `af_pipeline_config.report_path(subject, extension)` builds report filenames from the subject and extension only. No timestamp, run counter, host name or user name enters the path. Re-running the pipeline overwrites the previous report in place.
**Rationale.** A committed report (D-017, D-022) must be diffable. If the filename changed on every run the repository would accumulate near-identical files and `git diff` could never answer the only question that matters: *what changed since the last run?* Overwriting turns the report into a tracked state file whose history lives in Git, where it belongs.
**Rejected.** Timestamped filenames (`report_20250601_1432.json`) — untrackable churn; a `runs/` directory of retained history — duplicates what Git already does.
**Reversibility:** High. Adding a timestamp later is a one-function change; the reports themselves are unaffected.

---

## D-024 — Geometry is authored in world space with identity object transforms

**Date:** 2025-06-01
**Decision.** Every mesh generated by `af_vehicle_generate.py` has its vertices placed at final world coordinates, and each resulting object keeps location `(0,0,0)`, rotation `(0,0,0)` and scale `(1,1,1)`. Placement is baked into vertex data, never into the object transform.
**Rationale.** FBX export and Unreal import both apply object transforms, and each applies them with its own axis and scale conventions. A non-identity transform is therefore a second place where the unit and axis contract (D-013) can be violated, and it is a place that is invisible in the viewport. Identity transforms make `apply_scale_options` and `axis_forward`/`axis_up` the *only* transform-bearing settings in the pipeline, so there is exactly one thing to verify. It also means validation can compare a vertex coordinate directly against a design value without composing a matrix first.
**Rejected.** Authoring parts at the origin and positioning them with object transforms — conventional Blender practice, but it defers the transform question to import time, which is exactly where it is hardest to debug.
**Reversibility:** Medium. Changing this would require reworking generation, the validation position checks, and the rig's head/tail placement together.

---

## D-025 — Rigid binding: one bone per mesh, one weight per vertex

**Date:** 2025-06-01
**Decision.** `af_vehicle_rig.py` binds each mesh to exactly one deform bone with weight 1.0 via a single vertex group. The body binds to `AF_Chassis`, each wheel to its own wheel bone, each suspension mesh to its own suspension bone. `AF_Root` and `AF_Steering` carry no geometry. No automatic weights, no envelopes, no smoothing.
**Rationale.** A formula car is a rigid assembly; nothing on it deforms. Rigid binding makes the skin weights *verifiable by arithmetic* rather than by eyeball — the validator can assert one weight per vertex at exactly 1.0 and be done, which trivially satisfies the four-weights-per-vertex budget. Automatic weighting would produce plausible-looking results that nobody could check without visual inspection, which is precisely the class of claim the honesty rule (D-021) forbids.
**Rejected.** `ARMATURE_AUTO` weighting; envelope weighting; a single mesh bound across multiple bones.
**Reversibility:** High while the vehicle is rigid. If deforming parts are ever introduced they would be added alongside this scheme, not in place of it.

---

## D-026 — Exporter settings are filtered against the operator's RNA at run time

**Date:** 2025-06-01
**Decision.** `af_export.py` does not pass `FBX_EXPORT_SETTINGS` to the exporter blindly. It introspects the export operator's RNA properties, passes only the keys the installed Blender actually accepts, and **reports every dropped key loudly** in its output before exporting.
**Rationale.** The exporter option names in `FBX_EXPORT_SETTINGS` are stated intent, not a verified Blender 5.2 LTS API (`VERSION_MATRIX.md` §5). Passing an unknown keyword raises `TypeError` and aborts the run; silently swallowing it would be worse, because the export would then succeed with a *different* configuration than the one documented — for example with leaf bones enabled — and nothing downstream would notice until the skeleton arrived wrong in Unreal. Filtering plus a loud report converts an unverified assumption into an observable fact printed at run time.
**Rejected.** Passing settings unfiltered and letting the exception surface — brittle across point releases; filtering silently — hides a real configuration divergence.
**Reversibility:** High. Once the true option set is observed on a real Blender 5.2 LTS install, the filter becomes a no-op and can be removed or downgraded to an assertion.

---

## Superseded Decisions

None. No decision recorded here has yet been superseded.

## Verification Ledger for This Document

| Claim | Label |
| --- | --- |
| Every decision listed originates from the project brief or from Milestone 0A authoring | statically inspected |
| D-014 is the replay decision and states snapshot-plus-interpolation without assuming determinism | statically inspected |
| Cross-referenced documents and sections exist | statically inspected |
| Reversibility ratings are judgements, not measurements | statically inspected |
| D-023 to D-026 describe the behaviour actually written into the Milestone 0B scripts | statically inspected |
| The rigid binding scheme in D-025 is what `binding_plan()` returns — nine meshes, deform bones only, nothing on Root or Steering | automatically validated |
| The Blender-side effects of D-024, D-025 and D-026 occur as described when the scripts run | requires Blender execution |
| Any decision has been validated by running the pipeline inside Blender | not claimed — `bpy` has never been available in the authoring environment |
