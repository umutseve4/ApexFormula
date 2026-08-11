# Uludağ Formula — Milestone Plan

**Document status:** statically authored plan, first written at Milestone 0A and kept current as later milestones are authored. Milestone numbering in this document is authoritative and is used identically in every other document of this project. Milestone *bodies* below (objective, inputs, outputs, acceptance criteria) are the plan as authored and are not rewritten as work proceeds; current status is recorded separately in the Milestone Status table at the end of this document.

**Verification labels used throughout:** `statically inspected`, `automatically validated`, `requires Blender execution`, `requires Unreal Editor verification`, `requires local compilation`, `requires visual inspection`, `requires playtesting`.

> **Naming note (D-048).** The product is **Uludağ Formula** (previously *Apex Formula*). Two categories of old-name strings appear below and are treated differently:
> - **Queued for wave 2 — will change:** the six module identifiers `ApexFormulaCore`, `ApexFormulaVehicle`, `ApexFormulaRace`, `ApexFormulaUI`, `ApexFormulaEditor`, `ApexFormulaTests` in the Milestone 1 outputs. These are asserted by `Tools/af_static_validate.py` in at least eight places, so each rename must patch the guard in the same commit or CI turns red.
> - **Permanent — will not change:** `AF_`, `af_`, `UAF*`, `FAF*`, `AAF*`, `IAF*`, `LogAF*` and the `af.` cvar prefix. D-048 reclassified these from "old product name" to this project's **internal code name**.
>
> Only product prose has been renamed in this document. No milestone status, acceptance criterion or verification label was altered.

---

## Milestone Index

| # | Name |
| --- | --- |
| 0A | Architecture and Decision Records |
| 0B | Blender → Unreal Pipeline Foundation |
| 1 | Unreal Engine 5.8 C++ Project Foundation |
| 2 | First Playable Placeholder Vehicle |
| 3 | Race Test Environment and Valid Lap System |
| 4 | Procedural Vehicle Visual Prototype |
| 5 | Vehicle Visual + Physics Integration |
| 6 | Cockpit Driver Pipeline |
| 7 | MetaHuman Driver Integration |
| 8 | AI Opponent Prototype |
| 9 | Race Session Framework |
| 10 | Advanced Vehicle Simulation |
| 11 | Presentation, Audio, Effects and Menus |
| 12 | Optimization, Replay, Multiplayer Prep, Packaging and Release Validation |

---

## Milestone 0A — Architecture and Decision Records

**Objective.** Establish the written technical foundation: vision, architecture, vehicle-system decision, both pipeline designs, this plan, the version matrix and the decision log — before any code or asset exists.

**Inputs.** The project brief; the fixed environment decisions (UE 5.8, Blender 5.2 LTS, Windows, C++/Blueprint split, FBX primary, Git + Git LFS).

**Outputs.** Eight documents under `Documentation/`, plus `README.md`, `.gitignore`, `.gitattributes`; a distribution archive; a published Git repository with a clean initial commit.

**Dependencies.** None.

**Acceptance criteria.**
- All eight documents exist and are internally consistent.
- Milestone numbering identical across documents.
- No `F1` token anywhere; no real motorsport branding.
- No claim of execution anywhere; every result carries a verification label.
- Repository contains no binaries, build output, caches, credentials or private reference material.

**Local verification.** `statically inspected` — read every document; grep for prohibited tokens; confirm every cross-reference resolves to a real file and a real section.

**Risks.** Documents drifting apart as later milestones change decisions; over-specification of APIs that have not been confirmed against the installed engine and DCC versions.

**Explicitly excluded.** No Unreal project. No Blender scripts. No vehicle or driver geometry. No photo requests. No binary files. No pretended execution.

---

## Milestone 0B — Blender → Unreal Pipeline Foundation

**Objective.** Implement the eight `af_*.py` scripts and prove a clean, validated, reproducible export path from Blender 5.2 LTS to an FBX suitable for Unreal Engine 5.8.

**Inputs.** `BLENDER_PIPELINE_DESIGN.md`; Blender 5.2 LTS installed locally.

**Outputs.** `af_pipeline_config.py`, `af_scene_setup.py`, `af_vehicle_generate.py`, `af_vehicle_rig.py`, `af_materials.py`, `af_export.py`, `af_validate.py`, `af_smoke_test.py`; a JSON validation report; an exported placeholder vehicle FBX.

**Dependencies.** 0A.

**Acceptance criteria.**
- `af_smoke_test.py` runs end to end and exits zero.
- The validation report shows every check passing, with measured values, not assumed values.
- The exported bone list matches `af_pipeline_config.py` exactly, with no leaf bones added.
- Bounding box and wheel positions within tolerance, reported in both metres and centimetres.
- No hardcoded bone names, units, axes or paths outside `af_pipeline_config.py`.

**Local verification.** `automatically validated` — CI downloads Blender 5.2 LTS and runs `blender --background --factory-startup --python BlenderPipeline/scripts/af_smoke_test.py` on every push. The exit code, the stage results and the measured JSON report are the evidence. `requires visual inspection` remains open for whether the generated geometry *looks* right in the viewport, which no automated check can answer.

**Risks.** Blender 5.2 LTS FBX exporter option names or defaults differing from expectation; leaf-bone injection; unit-scale surprises; UCX naming not surviving export.

**Explicitly excluded.** No Unreal project yet. No final art. No driver work.

---

## Milestone 1 — Unreal Engine 5.8 C++ Project Foundation

**Objective.** Create the Unreal project and the six C++ modules with their base classes, so that the architecture in `TECHNICAL_ARCHITECTURE.md` exists as compilable code.

**Inputs.** `TECHNICAL_ARCHITECTURE.md`; UE 5.8 installed with a working Windows toolchain.

**Outputs.** Unreal project; modules `ApexFormulaCore`, `ApexFormulaVehicle`, `ApexFormulaRace`, `ApexFormulaUI`, `ApexFormulaEditor`, `ApexFormulaTests`; base classes and empty Data Asset types including `UAFBoneNameMap` and `UAFQualityProfile`; logging category and `UAFTelemetryBus` skeleton; first automation tests.

These six module identifiers still carry the previous product name. They are **wave-2 rename items** under D-048 and are quoted here exactly as they exist in the tree, so this plan keeps matching the source. Renaming them requires patching `af_static_validate.py`'s module list, dependency dictionary, engine-dependency table, `startswith` filters, `.uproject` checks, target-file checks and the C++ copyright literal — all in the same commit.

**Dependencies.** 0A.

**Acceptance criteria.**
- Project compiles from clean.
- Editor opens without module load errors.
- Automation tests discovered and passing.
- Module dependency graph is acyclic and matches the architecture document.

**Local verification.** `requires local compilation`; `requires Unreal Editor verification`; `automatically validated` for the test suite.

**Risks.** UE 5.8 API differences from expectation; module dependency mistakes surfacing only at link time.

**Explicitly excluded.** No vehicle physics. No art. No gameplay.

---

## Milestone 2 — First Playable Placeholder Vehicle

**Objective.** A drivable placeholder vehicle using the prototype vehicle-system decision (Chaos Vehicles behind `UAFVehicleCompatibilityLayer`), on a flat test surface.

**Inputs.** Milestone 1 project; `VEHICLE_SYSTEM_DECISION.md`; the 0B placeholder FBX.

**Outputs.** Vehicle pawn, input mapping, camera, placeholder mesh + skeleton import, basic wheel setup, drivable build.

**Dependencies.** 0B, 1.

**Acceptance criteria.**
- Vehicle accelerates, brakes and steers.
- Vehicle does not fall through the ground, oscillate, or invert at rest.
- All engine vehicle access goes through `UAFVehicleCompatibilityLayer` — no direct engine vehicle calls in gameplay code.
- Imported skeleton bone names match `UAFBoneNameMap`.

**Local verification.** `requires local compilation`; `requires Unreal Editor verification`; `requires playtesting` for whether it drives acceptably.

**Risks.** Chaos Vehicles behaviour differing from expectation in UE 5.8; bone naming not accepted by the engine's vehicle setup.

**Explicitly excluded.** No realistic tyre model, no aero, no energy, no fuel, no setup system. No final art.

---

## Milestone 3 — Race Test Environment and Valid Lap System

**Objective.** A closed test circuit and a lap timing system that can determine whether a lap is valid.

**Inputs.** Milestone 2 vehicle.

**Outputs.** Test circuit geometry; start/finish line; sector splits; track-limits volumes; lap validity rules; timing display.

**Dependencies.** 2.

**Acceptance criteria.**
- Laps are timed accurately and reproducibly.
- Sector times sum to the lap time.
- Cutting the circuit invalidates the lap.
- Restart and reset behave deterministically.
- No real-world circuit is reproduced.

**Local verification.** `requires Unreal Editor verification`; `automatically validated` for timing arithmetic under unit test; `requires playtesting` for track-limits feel.

**Risks.** Track-limit volume tuning; timing precision under variable frame rate.

**Explicitly excluded.** No opponents. No race rules beyond lap validity. No final environment art.

---

## Milestone 4 — Procedural Vehicle Visual Prototype

**Objective.** Extend the 0B generator to produce a recognisably formula-style, entirely original vehicle body with wheels, wings, sidepods and a halo-style structure.

**Inputs.** 0B scripts; `BLENDER_PIPELINE_DESIGN.md`.

**Outputs.** Improved `af_vehicle_generate.py`; collision proxies; LOD chain; placeholder materials; exported FBX; validation report.

**Dependencies.** 0B.

**Acceptance criteria.**
- Generation is deterministic from config.
- Validation passes including face budgets, UVs, collision convexity and naming.
- Design is original — not a reproduction of any real car.
- LOD chain generated in Blender, not by importer auto-reduction.

**Local verification.** `requires Blender execution`; `automatically validated` via the JSON report; `requires visual inspection` for whether it looks right.

**Risks.** Procedural geometry producing non-manifold or self-intersecting surfaces; face budget overruns. The Milestone 2 halo defect (D-040) is the worked example of this risk arriving early: a generated arc overshot the design height envelope by 24 mm and only the executed validator could see it.

**Explicitly excluded.** No physics integration yet. No final shading.

---

## Milestone 5 — Vehicle Visual + Physics Integration

**Objective.** Replace the placeholder with the Milestone 4 vehicle and make the visual and physical representations agree.

**Inputs.** Milestone 2 vehicle; Milestone 4 assets.

**Outputs.** Imported vehicle in the project; wheel/suspension bone driving; collision assignment; centre-of-mass and inertia configuration; material instances.

**Dependencies.** 2, 4.

**Acceptance criteria.**
- Wheels rotate and steer with correct bone mapping; no wheel spins at the wrong axis.
- Suspension travel is visible and matches physical travel.
- Collision matches the visual silhouette closely enough for fair contact.
- Scale is correct in centimetres against the design dimensions.
- Car is not mirrored.

**Local verification.** `requires Unreal Editor verification`; `requires visual inspection`; `requires playtesting`.

**Risks.** Handedness/mirroring errors surfacing only here; visual/physical suspension mismatch.

**Explicitly excluded.** No advanced simulation. No driver.

---

## Milestone 6 — Cockpit Driver Pipeline

**Objective.** A Tier A driver — helmeted, visor down — correctly seated in the cockpit.

**Inputs.** `DRIVER_PIPELINE_DESIGN.md`; Milestone 5 vehicle.

**Outputs.** Driver basemesh, helmet, suit, gloves; cockpit pose; hand-to-wheel attachment; steering link.

**Dependencies.** 5.

**Acceptance criteria.**
- Driver scale matches the cockpit.
- Hands reach and follow the wheel.
- Eyeline matches the cockpit camera position.
- No interpenetration between driver, helmet, halo structure and cockpit surround.
- No reference photograph is committed or packaged.

**Local verification.** `requires Blender execution`; `requires Unreal Editor verification`; `requires visual inspection`; `statically inspected` for the privacy/commit check.

**Risks.** Pose and scale errors; helmet occluding the cockpit view.

**Explicitly excluded.** No facial likeness. No MetaHuman yet. No Tier B or C quality.

---

## Milestone 7 — MetaHuman Driver Integration

**Objective.** Create the MetaHuman driver in UE 5.8 and integrate it, progressing toward Tier B.

**Inputs.** Milestone 6 driver; `DRIVER_PIPELINE_DESIGN.md` §5.

**Outputs.** MetaHuman asset with facial rig, hair, eyes, teeth and skin material; integration into the cockpit and into presentation contexts.

**Dependencies.** 6.

**Acceptance criteria.**
- Facial rig comes from the MetaHuman system, not a hand-built armature.
- Expressions do not tear the mesh.
- Skin reads as skin under project lighting.
- Performance cost measured, not assumed.
- Privacy rules still hold: nothing under `LocalReference/` committed or packaged.

**Local verification.** `requires Unreal Editor verification`; `requires visual inspection`.

**Risks.** MetaHuman tooling behaviour in UE 5.8 differing from expectation; performance cost of hair and skin.

**Explicitly excluded.** No claim of biometric replication. No Tier C detail.

---

## Milestone 8 — AI Opponent Prototype

**Objective.** AI cars that drive the circuit at a controllable pace and can be raced against.

**Inputs.** Milestones 3 and 5.

**Outputs.** Racing line representation; AI controller; throttle/brake/steer control; basic overtaking and collision avoidance; pace scaling.

**Dependencies.** 3, 5.

**Acceptance criteria.**
- AI completes clean laps unassisted.
- AI does not drive off-circuit or stall.
- Pace scales predictably.
- AI reacts to the player rather than driving through them.

**Local verification.** `requires Unreal Editor verification`; `requires playtesting`.

**Risks.** Racing line authoring effort; AI instability under contact.

**Explicitly excluded.** No strategy, no pit stops, no race rules — those are Milestone 9.

---

## Milestone 9 — Race Session Framework

**Objective.** Structured sessions: practice, qualifying and race, with grid, standings, flags and results.

**Inputs.** Milestones 3 and 8.

**Outputs.** Session state machine; grid formation; classification and standings; flag states; penalties for track limits; results screen data.

**Dependencies.** 3, 8.

**Acceptance criteria.**
- Session transitions are correct and cannot deadlock.
- Standings are correct including lapped cars.
- Penalties apply consistently with the Milestone 3 lap validity rules.
- Results are reproducible from the session state.

**Local verification.** `automatically validated` for state machine and standings under unit test; `requires playtesting` for the full session.

**Risks.** Edge cases in classification; lapped-car ordering.

**Explicitly excluded.** No multiplayer. No pit-stop simulation depth.

---

## Milestone 10 — Advanced Vehicle Simulation

**Objective.** Replace simplified behaviour with the project's own tyre, aerodynamic, energy, fuel, brake and setup models, per the long-term hybrid decision.

**Inputs.** `VEHICLE_SYSTEM_DECISION.md` §5 migration order; Milestone 5 vehicle.

**Outputs.** `UAFTyreSetComponent`, `UAFAeroComponent`, `UAFEnergySystemComponent`, `UAFFuelComponent`, `UAFBrakeComponent`, `UAFDrivetrainComponent`, `UAFVehicleSetupComponent` implementations and their Data Assets; garage setup UI hooks.

**Dependencies.** 5, 9.

**Acceptance criteria.**
- Each model is migrated in the documented order, one at a time, each behind the compatibility layer.
- Each migration is reversible; the previous behaviour remains selectable until the new model is accepted.
- Tyre temperature/wear, downforce/drag, energy deployment, fuel load and brake temperature all measurably affect lap time.
- Setup changes produce directionally correct, explainable results.

**Local verification.** `automatically validated` for model unit tests; `requires Unreal Editor verification`; `requires playtesting` for whether the car is drivable and the setup effects feel coherent.

**Risks.** The largest simulation risk in the project: instability, unrealistic coupling between models, and unbounded tuning effort.

**Explicitly excluded.** No claim of real-world physical accuracy. No real-world data reproduction.

---

## Milestone 11 — Presentation, Audio, Effects and Menus

**Objective.** Bring the game to a presentable state: audio, effects, UI, garage, podium.

**Inputs.** Milestones 7, 9, 10.

**Outputs.** Engine/tyre/wind/impact audio; particle and post-process effects; main menu, HUD, garage/setup UI, results and podium presentation; Tier B driver finish where cameras demand it.

**Dependencies.** 7, 9, 10.

**Acceptance criteria.**
- Audio responds to vehicle state, not just to speed.
- HUD conveys the information a driver needs without clutter.
- Garage UI exposes the Milestone 10 setup parameters coherently.
- Final Quality profile is used for presentation captures; Development Preview never leaks into them.

**Local verification.** `requires Unreal Editor verification`; `requires visual inspection`; `requires playtesting`.

**Risks.** Scope inflation; audio asset sourcing that must remain original and licence-clean.

**Explicitly excluded.** No real sponsor, team or broadcast branding.

---

## Milestone 12 — Optimization, Replay, Multiplayer Prep, Packaging and Release Validation

**Objective.** Make it fast, recordable, network-ready in structure, packageable and verifiable.

**Inputs.** All prior milestones.

**Outputs.** Profiling results and optimisations; replay system using periodic authoritative state snapshots plus interpolation (decision D-014); network-boundary preparation per `TECHNICAL_ARCHITECTURE.md` §8; packaged Windows build; release validation checklist and results.

**Dependencies.** 11.

**Acceptance criteria.**
- Target frame rate met at the Final Quality profile on the reference machine, measured and recorded.
- Replays reproduce a session faithfully without assuming simulation determinism.
- Packaged build launches and completes a full race session.
- No private reference material, credentials or machine configuration in the package.

**Local verification.** `requires local compilation`; `requires Unreal Editor verification`; `requires playtesting`; `automatically validated` for the packaging checklist.

**Risks.** Performance shortfalls discovered late; replay storage size; multiplayer assumptions baked in earlier than intended.

**Explicitly excluded.** No shipped multiplayer — preparation only.

---

## Cross-Milestone Rules

1. **No milestone may claim completion without evidence carrying a verification label.** "It should work" is not acceptance.
2. **Development Preview quality never permanently damages Final Quality assets.** Preview settings are overrides, not edits.
3. **Hardware weakness never lowers the Final Quality target.** It changes what is previewed, not what is authored.
4. **Engine vehicle access stays behind `UAFVehicleCompatibilityLayer`** from Milestone 2 onward, so Milestone 10 remains possible.
5. **Bone names live in `af_pipeline_config.py` and `UAFBoneNameMap`** and change together, never independently.
6. **Nothing under `LocalReference/` is ever committed or packaged**, at any milestone.
7. **Vehicle dimensions live in `af_pipeline_config.py::DESIGN`** and every other copy follows it (D-041).
8. **The product rename is staged, not opportunistic.** Wave 1 changes display identity and prose only. Wave 2 changes module identifiers, the `.uproject`, the target files and the project ini, and every such commit must patch `Tools/af_static_validate.py` in the same commit (D-048).

---

## Milestone Status

This table records what has been *authored* and what has been *verified*. Authoring and acceptance are different things: a milestone is only complete when its acceptance criteria have been checked with evidence carrying a verification label, per Cross-Milestone Rule 1.

| # | Authored? | Acceptance criteria met? | Notes |
| --- | --- | --- | --- |
| 0A | Yes | Yes — `statically inspected` | Documentation set exists and is cross-consistent. |
| 0B | Yes | Yes — `automatically validated` | Blender 5.2.0 LTS runs `af_smoke_test.py` headless in CI on every push. All seven stages pass, the harness exits 0, and the pre-export validator reports 19 passed / 0 failed / 1 skipped of 21 checks against measured values. `requires visual inspection` remains open for whether the geometry looks right. |
| 1 | Yes | Not confirmed — `requires local compilation`, `requires Unreal Editor verification` | Six modules and their base classes exist as source; the project has never been compiled here and the editor has never been opened here. |
| 2 | Yes | 1 of 4 — see below | Implementation files, automation tests and a dedicated static checker landed; behaviour unverified. |
| 3–12 | No | Not started | Not begun. |

The 0B row previously read "Not confirmed — no script has been run". That was true when written and is no longer true. It was corrected rather than quietly deleted, because a status table that silently improves is indistinguishable from one that is being flattered.

**Milestone 2 acceptance criteria, individually:**

| Criterion | Status | Label |
| --- | --- | --- |
| Vehicle accelerates, brakes and steers | Not met — not demonstrated | `requires playtesting` |
| Vehicle does not fall through the ground, oscillate, or invert at rest | Not met — not demonstrated | `requires playtesting` |
| All engine vehicle access goes through `UAFVehicleCompatibilityLayer` | **Met** | `automatically validated` — enforced by `Tools/af_static_validate.py` in CI |
| Imported skeleton bone names match `UAFBoneNameMap` | Not met — no asset has been imported | `requires Unreal Editor verification` |

Criterion 4 now has partial evidence, which is not the same as being met. The naming *convention* is agreed between `af_pipeline_config.py` and `UAFBoneNameMap`, and that agreement is `automatically validated` by emulation (D-029). The Blender rig stage is *executed* in CI and prints all eleven bones with parent and head position in metres and centimetres, asserting `bone_count == 11`, `bone_order_matches_config == True` and nine bound meshes — so the producing side of the contract is continuously verified. What is unverified is the consuming side: no FBX has been imported into an Unreal editor, because no Unreal editor exists in this environment. The criterion closes when someone imports the exported asset and reads the resulting skeleton.

**Rename status.** The product rename is a documentation-and-identity change, not a milestone. It does not appear as a row above and does not alter any status in the table. Wave 1 (display identity and prose) is in progress; wave 2 (module identifiers, `.uproject`, target files, project ini and the matching guard edits) has not started. Nothing in the rename has been compiled or executed in an engine.

## Verification Ledger for This Document

| Claim | Label |
| --- | --- |
| Milestone numbering matches every other document of this project | statically inspected |
| Dependencies form an acyclic order (0A → 0B → 1 → 2 → …) | statically inspected |
| Every referenced document and section exists | statically inspected |
| Acceptance criteria are checkable rather than aspirational | statically inspected |
| Milestones 0A, 0B, 1 and 2 have been authored | statically inspected |
| Milestone 0A acceptance criteria are met | statically inspected |
| Milestone 0B acceptance criteria are met | automatically validated — headless Blender in CI, exit 0, 19/21 passed with 1 permanent skip |
| The 0B geometry looks correct in a viewport | not claimed — `requires visual inspection` |
| Milestone 1 and 2 acceptance criteria are met | not claimed — see the Milestone Status table for the per-criterion position |
| Milestone 2 criterion 3 is met | automatically validated |
| Milestone 2 criterion 4 has partial (producing-side) evidence in CI | automatically validated |
| Milestone 2 criterion 4 is met | not claimed — `requires Unreal Editor verification` |
| The product name "Uludağ Formula" matches none of the prohibited identifier patterns in `af_static_validate.py` | automatically validated |
| The six module identifiers still carry the previous product name and are queued for wave 2 | statically inspected |
| Any milestone beyond 0A and 0B is complete | not claimed |
