# Uludağ Formula — Technical Architecture

**Document status:** statically authored design document (Milestone 0A). Nothing in this document has been compiled, opened in the Unreal Editor, or executed. All module, class and interface names below are *proposed* and become real only in Milestone 1.

**Fixed environment:** Unreal Engine 5.8, Blender 5.2 LTS, Windows, C++ primary, Blueprints for configuration and presentation. See `Documentation/VERSION_MATRIX.md`.

> **Naming note (D-048).** The product is **Uludağ Formula** (previously *Apex Formula*). This document still contains the old string in two different roles, and they are not the same thing:
>
> - **Queued for wave 2 — will change:** the six module identifiers `ApexFormulaCore`, `ApexFormulaVehicle`, `ApexFormulaRace`, `ApexFormulaUI`, `ApexFormulaEditor`, `ApexFormulaTests`, and the settings file `Config/DefaultApexFormula.ini`. These are directory names, `.Build.cs` class names and `.uproject` entries that are asserted by `Tools/af_static_validate.py`; they can only move in the same commit that patches the guard, so they are deliberately untouched here.
> - **Permanent — will not change:** `AF_`, `af_`, `UAF*`, `FAF*`, `AAF*`, `IAF*`, `LogAF*` and the `af.` console-variable prefix. D-048 reclassified `AF_` from "old product name" to the project's **internal code name**. It is retained indefinitely.
>
> Everything else in this document is product prose and has been renamed.

---

## 1. Overall System Architecture

Uludağ Formula is structured as **five horizontal layers**. Dependencies point downward only. A lower layer never includes a higher layer's headers.

```
Layer 5  Presentation      HUD, menus, garage, podium, cameras, audio, VFX
Layer 4  Session           practice / qualifying / race, grid, race control, penalties
Layer 3  Rules & Timing    checkpoints, sectors, lap validation, standings, pit rules
Layer 2  Vehicle           physics extension, tyres, aero, energy, fuel, brakes, setup
Layer 1  Core              data models, config, math, telemetry, logging, save data
```

Cross-layer communication rules:

1. **Downward calls:** direct, via interfaces or component accessors.
2. **Upward notification:** never a direct call. Upward flow uses declared delegates (`FOnLapCompleted`, `FOnSectorCrossed`, `FOnPenaltyIssued`, `FOnPitStopCompleted`, etc.) or the telemetry bus.
3. **Sideways within a layer:** allowed only through interfaces, never concrete classes.

This layering is what makes the future multiplayer boundary (section 8) and the testing strategy (section 9) tractable.

## 2. Unreal C++ Module Boundaries

Proposed module split. Each is a real Unreal build module with its own `.Build.cs`.

| Module | Type | Depends on | Owns |
| --- | --- | --- | --- |
| `ApexFormulaCore` | Runtime | Engine, CoreUObject | Data models, config structs, unit helpers, math utilities, telemetry bus, logging categories, save data definitions, shared enums, shared interfaces |
| `ApexFormulaVehicle` | Runtime | Core, ChaosVehicles* | Vehicle pawn, vehicle simulation components (tyre, aero, energy, fuel, brake), setup application, vehicle telemetry sources, input mapping to vehicle controls |
| `ApexFormulaRace` | Runtime | Core | Checkpoints, sector definitions, lap validation, timing, standings, session state machine, grid, race control, penalties, pit rules, AI driver logic |
| `ApexFormulaUI` | Runtime | Core, UMG, Slate | HUD view models, setup screen view models, telemetry display models, menu backing data |
| `ApexFormulaEditor` | Editor | Core, Vehicle, Race, UnrealEd | Data Asset validation, naming-convention checks, track authoring helpers, asset audit commandlets |
| `ApexFormulaTests` | Runtime (dev) | Core, Vehicle, Race | Automation tests, deterministic replay harness |

`*` The exact Chaos Vehicles module dependency name and availability in Unreal Engine 5.8 is **an assumption requiring verification** — see `Documentation/VERSION_MATRIX.md` §5 and `Documentation/VEHICLE_SYSTEM_DECISION.md` §7.

The six module identifiers above are **wave-2 items**, per the naming note. They are asserted by `Tools/af_static_validate.py` in at least eight places (the module list, the dependency table, the engine-dependency table, the `.uproject` checks, the target-file checks and the per-module `startswith` filters), so renaming them in a documentation commit would turn CI red immediately. They move only in a commit that also patches the guard.

**Boundary rules:**

- `ApexFormulaCore` depends on no other module of this project. It must remain free of vehicle-specific and race-specific types.
- `ApexFormulaRace` must not depend on `ApexFormulaVehicle`. It talks to vehicles only through interfaces declared in Core (e.g. `IAFRaceParticipant`, `IAFTelemetrySource`). This is what allows AI cars, player cars and future networked cars to be treated uniformly.
- `ApexFormulaUI` reads; it does not decide. No race rule, penalty or lap validity may be computed in the UI module.
- Editor-only code never leaks into runtime modules.

## 3. Blueprint Responsibilities

**Blueprints own or configure:**

- Visual asset assignment (meshes, materials, decals, liveries)
- Vehicle appearance and cosmetic variants
- Level assembly and placement of track pieces, checkpoints, grid slots, pit boxes
- UI layout, widget hierarchy, animation of widgets
- Animation Blueprint connections (driver, steering wheel, suspension visuals)
- Audio assignment and audio component wiring
- Camera presentation, camera rigs, post-process volumes
- Level-specific configuration overrides
- Exposed tuning values marked `EditAnywhere` / `BlueprintReadWrite`
- Design iteration that does not change architecture

**Blueprints must never own:**

- Lap validity, sector timing, penalty decisions, standings
- Tyre, aero, energy, fuel or brake state evolution
- Save data format
- Anything that will later need to be server-authoritative
- Anything performance-critical evaluated per physics sub-step

**Pattern:** every gameplay C++ class exposes a *thin Blueprint-facing surface* — `BlueprintNativeEvent` hooks for presentation reactions, `BlueprintCallable` read accessors, and `EditDefaultsOnly` configuration pointers to Data Assets. Blueprints subclass C++ classes; C++ never subclasses Blueprints.

## 4. Component Strategy

**Composition over inheritance is mandatory.** Deep pawn inheritance chains are prohibited.

Proposed vehicle composition (`AAFVehiclePawn` + components):

- `UAFTyreSetComponent` — per-corner temperature, wear, grip state, pressure
- `UAFAeroComponent` — front/rear downforce, drag, aero balance, active aero state
- `UAFEnergySystemComponent` — hybrid deployment, regeneration, stored energy
- `UAFFuelComponent` — fuel mass, consumption, mass feedback into physics
- `UAFBrakeComponent` — brake temperature, brake bias, fade model
- `UAFDrivetrainComponent` — differential configuration, gear selection
- `UAFVehicleSetupComponent` — applies a setup Data Asset to all of the above
- `UAFVehicleTelemetryComponent` — samples all of the above onto the telemetry bus
- `UAFRaceParticipantComponent` — implements `IAFRaceParticipant`, holds checkpoint progress, lap state, penalties

Rules:

1. A component owns exactly one concern and one state block.
2. Components communicate through the owning pawn or through Core interfaces, not by casting to each other's concrete types where an interface will do.
3. Any component that mutates physically meaningful state exposes a pure read accessor for telemetry and UI.
4. Components are individually testable with a null/mock owner where practical.
5. Adding a new simulated subsystem must mean adding a component, not editing the pawn.

## 5. Data Asset Strategy

All tuning lives in Data Assets. Proposed set (all `UPrimaryDataAsset` subclasses in `ApexFormulaCore` or `ApexFormulaVehicle`):

| Data Asset | Purpose |
| --- | --- |
| `UAFVehicleDefinition` | Mass, dimensions, wheelbase, track width, inertia, bone-name mapping table, default setup |
| `UAFTyreCompound` | Grip curves, optimal temperature window, wear rate, degradation response |
| `UAFAeroProfile` | Downforce and drag coefficients vs. speed and ride height, aero balance range, active aero states |
| `UAFEnergyProfile` | Deployment rate, regeneration rate, capacity, per-lap limits |
| `UAFBrakeProfile` | Thermal capacity, fade curve, bias range |
| `UAFVehicleSetup` | A saveable, player-editable configuration instance |
| `UAFTrackDefinition` | Checkpoint order, sector boundaries, pit lane entry/exit, grid slots, track limits policy |
| `UAFSessionRules` | Session type, length, penalty table, false-start rules, pit rules |
| `UAFAIDriverProfile` | Fictional driver identity, pace, aggression, error rate, tyre management |
| `UAFDifficultyProfile` | Assist configuration, consumption multipliers |
| `UAFQualityProfile` | Development Preview vs. Final Quality overrides |
| `UAFBoneNameMap` | The single central location for all skeletal bone names (see §6) |

Rules:

- **No magic numbers in code.** Any physically or design-meaningful constant lives in a Data Asset or a named `UAFSettings` config field.
- Data Assets are validated by `ApexFormulaEditor` (`UAFDataValidator`), which reports missing curves, out-of-range values and broken bone mappings.
- Data Assets are versioned; a `DataVersion` integer allows migration code in Core.

### Central bone-name convention

The skeletal convention is:

```
AF_Root
AF_Chassis
AF_Steering
AF_Wheel_FL
AF_Wheel_FR
AF_Wheel_RL
AF_Wheel_RR
AF_Suspension_FL
AF_Suspension_FR
AF_Suspension_RL
AF_Suspension_RR
```

This convention is **not** assumed to be any Chaos Vehicles default. It is this project's own convention, and under D-048 it is **permanent**: the rename to Uludağ Formula explicitly does not touch these eleven bone names. `Tools/af_static_validate.py` asserts the `AF_` prefix directly (the prefix check plus the `AF_Root` / `AF_Steering` presence checks and the `bone.startswith("AF_")` loop), and the same names are hard-coded in `af_pipeline_config.py` and in the circuit and lap-rules self-tests. Renaming them would be a large, high-risk change with no user-visible benefit — see `Documentation/PROJECT_VISION.md` §1 for the full three-name identity model.

The names are stored in exactly one place — `UAFBoneNameMap` — and both the Unreal wheel/suspension setup and the Blender generator read their names from a shared source of truth (`af_pipeline_config.py` mirrors the same list; see `Documentation/BLENDER_PIPELINE_DESIGN.md`). Changing a bone name must be a one-file change plus a re-export, never a code hunt.

**Status:** `requires Unreal Editor verification` — that Unreal Engine 5.8's vehicle setup accepts a fully data-driven bone mapping with these names.

## 6. Configuration Strategy

Three tiers, in increasing specificity:

1. **Project settings** — `UAFDeveloperSettings` (`UDeveloperSettings` subclass), stored in `Config/DefaultApexFormula.ini`. Holds pipeline paths, default Data Asset references, telemetry toggles, quality profile default. *(Wave-2 item: this filename, the matching `Config=` UCLASS specifier and the `[/Script/ApexFormulaCore.AFDeveloperSettings]` section header all move together, in one commit, with the guard patched alongside.)*
2. **Data Assets** — all gameplay and vehicle tuning, as in §5.
3. **Level / instance overrides** — Blueprint-exposed properties on placed actors, for level-specific configuration only.

Rules:

- No gameplay constant is read from a hardcoded literal in a `.cpp` file.
- Machine-specific configuration (local paths, personal reference directories, editor layout) is **never committed**; it is excluded by `.gitignore`.
- Console variables (`af.` prefix) are permitted for debugging and profiling only, never as the primary configuration route. The `af.` prefix is permanent under D-048.

## 7. Asset Pipeline Boundaries

The Blender/Unreal boundary is a **hard, documented contract**, defined in full in `Documentation/BLENDER_PIPELINE_DESIGN.md`. Summary of the boundary as it affects architecture:

- **Blender owns:** procedural geometry generation, UV layout, LOD generation, collision mesh authoring, rig/armature construction, FBX export, pre-export validation, JSON validation reports.
- **Unreal owns:** import settings, material instancing, physics asset configuration, LOD assignment policy inside the engine, texture streaming, final shading.
- **Neither owns unilaterally:** the bone-name convention, unit scale, forward/up axis, and the vehicle dimension design values. These are *contract items* — they are documented in both `af_pipeline_config.py` and `UAFBoneNameMap`/`UAFVehicleDefinition`, and any change must be made in both, in the same change set.
- **Transfer formats:** FBX is the primary skeletal pipeline format. GLB is optional, and only for static preview or interchange — never the authoritative skeletal path.
- **Directory separation:** Blender source files and generated exports live in separate trees; generated exports are reproducible and are candidates for Git LFS, not for hand editing.

## 8. Future Multiplayer Boundaries

Multiplayer is **not implemented** in the current milestone plan. The architecture nonetheless observes these boundaries from day one, because retrofitting them is expensive:

1. **Authority classification.** Every piece of state is classified as `Authoritative`, `Predicted` or `Cosmetic` in its owning class's header comment.
   - Authoritative: lap validity, sector times, penalties, standings, session state, pit stop completion, fuel/energy/tyre/brake state.
   - Predicted: vehicle transform and velocity.
   - Cosmetic: VFX, audio, camera, HUD animation.
2. **No authoritative state in Blueprints.** Enforced by review and by the `ApexFormulaEditor` audit.
3. **No authoritative state in the UI module.**
4. **Input is a value object.** Vehicle input is captured into a serialisable `FAFVehicleInputFrame` struct with a frame index and timestamp, then applied. This same struct is what a future client would send and what the replay system records.
5. **Simulation stepping is explicit.** Vehicle subsystems advance via an explicit `StepSimulation(DeltaTime, InputFrame)` call rather than scattered `Tick` side effects, so a future server can drive them deterministically.
6. **No reliance on singletons for participant state.** Participants are discovered through the race subsystem, not through global mutable state.
7. **Determinism concerns are documented, not promised.** Full lockstep determinism is *not* claimed for Unreal's physics. The replay strategy (§10) is therefore state-recording, not input-replay-only.

## 9. Testing Philosophy

Four tiers:

1. **Static validation (automatable, no engine):** naming conventions, document/tree consistency, JSON report schema checks, Python-side pipeline checks. This is the only tier that can run in an environment without Unreal or Blender.
2. **Editor/Automation tests (`ApexFormulaTests`):** pure-logic tests for lap validation, sector timing, checkpoint ordering, penalty rules, energy/fuel accounting, setup application, save/load round trips. These must not require a rendered frame. **Status:** `requires local compilation`.
3. **Scripted scenario tests:** a headless or minimal level that drives a vehicle through a scripted input sequence and asserts on timing/validity outcomes. **Status:** `requires Unreal Editor verification`.
4. **Human verification:** visual inspection of assets and presentation, and playtesting of feel, balance and difficulty. These can never be automated away and are always labelled `requires visual inspection` or `requires playtesting`.

Principle: **rules logic must be testable without a car, a track or a frame.** If a rule can only be tested by driving, it is in the wrong layer.

## 10. Logging and Telemetry Strategy

### Logging

- Dedicated categories: `LogAFCore`, `LogAFVehicle`, `LogAFRace`, `LogAFPipeline`, `LogAFUI`. These keep the `AF` internal code name permanently, per D-048.
- Verbosity is configuration-driven, not compile-time.
- Every rule decision that affects the player (lap invalidated, penalty issued, pit stop judged) logs at `Log` level with participant id, session time and the reason. Silent rule decisions are prohibited.

### Telemetry

- A single `UAFTelemetryBus` in `ApexFormulaCore`. Producers push named channels; consumers (HUD, recorder, debug overlay) subscribe. Producers never know their consumers.
- Channel schema: `FAFTelemetrySample { FName Channel; double SessionTime; int32 ParticipantId; double Value; }` for scalars, with a parallel vector variant.
- Planned channels: speed, engine/motor RPM, gear, throttle, brake, steering, per-corner tyre temperature, per-corner tyre wear, per-corner slip, brake temperature per axle, fuel mass, energy store, energy deploy rate, downforce front/rear, drag, aero balance, ride height, delta to reference lap.
- **Recording:** telemetry is written to a session file for later analysis and to support the replay preparation milestone. Recording is a Final-Quality-safe operation and must not alter simulation results.
- **Replay preparation:** because engine-level physics determinism is not assumed, replay is designed as *periodic authoritative state snapshots plus interpolation*, with the input frames recorded alongside for analysis. This decision is recorded in `Documentation/DECISION_LOG.md` (D-014).

## 11. Proposed Runtime Class Sketch

Illustrative only; nothing below has been compiled. Module names are wave-2 items; the class names are permanent.

```
ApexFormulaCore
  UAFDeveloperSettings
  UAFTelemetryBus
  IAFRaceParticipant
  IAFTelemetrySource
  FAFVehicleInputFrame
  UAFBoneNameMap
  UAFQualityProfile
  UAFSaveGame

ApexFormulaVehicle
  AAFVehiclePawn
  UAFTyreSetComponent
  UAFAeroComponent
  UAFEnergySystemComponent
  UAFFuelComponent
  UAFBrakeComponent
  UAFDrivetrainComponent
  UAFVehicleSetupComponent
  UAFVehicleTelemetryComponent
  UAFVehicleCompatibilityLayer   // isolates version-sensitive engine vehicle API calls

ApexFormulaRace
  AAFCheckpoint
  UAFLapValidator
  UAFSectorTimer
  UAFSessionSubsystem
  UAFRaceControl
  UAFPenaltyLedger
  AAFPitBox
  UAFAIDriverController

ApexFormulaUI
  UAFHudViewModel
  UAFSetupScreenViewModel
  UAFTelemetryViewModel
```

`UAFVehicleCompatibilityLayer` exists specifically to satisfy the rule that version-sensitive or uncertain engine API usage is isolated behind a clearly named compatibility layer with documented uncertainty.

## 12. Verification Ledger for This Document

| Claim | Label |
| --- | --- |
| Layering and module boundaries are internally consistent | statically inspected |
| No real motorsport brand appears as an identifier | statically inspected |
| The product name "Uludağ Formula" matches none of the prohibited identifier patterns in `af_static_validate.py` | automatically validated |
| Module identifiers still carry the old product name and are queued for wave 2 | statically inspected |
| Proposed module names compile as Unreal modules | requires local compilation |
| Chaos Vehicles module availability/naming in UE 5.8 | requires Unreal Editor verification |
| Data-driven bone mapping accepted by UE 5.8 vehicle setup | requires Unreal Editor verification |
| Telemetry recording does not perturb simulation | requires playtesting |
| Component split performs acceptably at full grid size | requires playtesting |
