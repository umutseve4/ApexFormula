# ApexFormula — Technical Architecture

**Document status:** statically authored design document. Nothing in this file
was compiled, opened, executed, imported, or visually inspected.
**Milestone:** 0A
**Target environment:** Unreal Engine 5.8, Blender 5.2 LTS, Windows, C++ primary.

---

## 1. Overall System Architecture

ApexFormula is composed of four cooperating systems.

```
┌─────────────────────────────────────────────────────────┐
│ 1. AUTHORING SYSTEM (Blender 5.2 LTS + Blender Python)        │
│    procedural generation, rigging, validation, FBX export     │
└───────────────┬─────────────────────────────────────────┘
                │ FBX (skeletal/static)  ·  GLB (optional preview)
                ▼
┌─────────────────────────────────────────────────────────┐
│ 2. CONTENT SYSTEM (Unreal assets + Blueprints + Data Assets)  │
│    visual assignment, level assembly, UI, audio, tuning data  │
└───────────────┬─────────────────────────────────────────┘
                │ typed interfaces, Data Assets, config structs
                ▼
┌─────────────────────────────────────────────────────────┐
│ 3. GAMEPLAY SYSTEM (Unreal C++ modules)                       │
│    vehicle sim extensions, race rules, timing, telemetry, AI  │
└───────────────┬─────────────────────────────────────────┘
                │ logs, telemetry frames, save data
                ▼
┌─────────────────────────────────────────────────────────┐
│ 4. TOOLING & VALIDATION SYSTEM                                │
│    naming checks, report generation, profile enforcement      │
└─────────────────────────────────────────────────────────┘
```

**Directional rule:** authoring flows forward into content, content flows forward
into gameplay. Gameplay code never reaches backward into Blender-specific
assumptions, and Blender scripts never encode undocumented Unreal internals.

## 2. Unreal C++ Module Boundaries

The project is split into focused modules rather than one monolithic game
module. Module names use the `ApexFormula` root identity.

| Module | Type | Responsibility | Depends on |
|---|---|---|---|
| `ApexFormulaCore` | Runtime | Shared types, enums, math helpers, unit constants, logging categories, config structs. No gameplay behaviour. | Engine core only |
| `ApexFormulaVehicle` | Runtime | Vehicle pawn, vehicle simulation components, aero, tires, brakes, fuel, hybrid energy, setup application, bone-name mapping. | Core |
| `ApexFormulaRace` | Runtime | Checkpoints, sectors, lap validation, timing, session state (practice/qualifying/race), grid, race control, penalties, pit rules. | Core, Vehicle (interfaces only) |
| `ApexFormulaAI` | Runtime | AI driver controllers, racing line following, opponent behaviour, difficulty scaling. | Core, Vehicle, Race |
| `ApexFormulaTelemetry` | Runtime | Telemetry frame definition, sampling, ring buffer, export, replay-oriented recording. | Core |
| `ApexFormulaUI` | Runtime | C++-side HUD/view-model data providers and setup-screen data contracts. Layout itself lives in Blueprints/UMG. | Core, Race, Vehicle, Telemetry |
| `ApexFormulaEditor` | Editor | Editor-only validation commandlets, asset naming checks, data asset auditing. | All runtime modules |
| `ApexFormulaTests` | Developer | Automation tests for pure logic (timing, lap validity, energy budgets, unit conversion). | All runtime modules |

**Boundary rules:**

1. `ApexFormulaCore` never depends on any other project module.
2. `ApexFormulaRace` must not include vehicle implementation headers; it consumes
   vehicle state through interfaces defined in `ApexFormulaCore`.
3. No runtime module may depend on `ApexFormulaEditor`.
4. Circular module dependencies are prohibited. If two modules appear to need
   each other, the shared contract moves down into `ApexFormulaCore`.
5. Anything performance-sensitive, rules-defining, or multiplayer-authoritative
   belongs in C++, never in Blueprints.

## 3. Blueprint Responsibilities

Blueprints **own or configure**:

- Visual asset assignment (meshes, materials, decals, livery slots)
- Vehicle appearance and cosmetic variation
- Level assembly and level-specific configuration
- UI layout (UMG widget trees, styling, animation)
- Animation connections (Animation Blueprints, blend logic wiring)
- Audio assignment and audio parameter routing
- Camera presentation and camera rigs
- Exposed tuning values surfaced by C++ as `UPROPERTY(EditAnywhere)`
- Design iteration that does not require architectural change

Blueprints **must not** own:

- Race rules, lap validity, or penalty determination
- Timing, sector logic, or checkpoint ordering
- Vehicle simulation math (aero, tire, brake, fuel, energy)
- Save data definitions
- Telemetry frame layout
- Anything intended to be authoritative in future multiplayer
- Tick-heavy per-frame numeric loops

**Interface convention:** every C++ system exposes a small, stable
`BlueprintCallable` / `BlueprintPure` surface plus `BlueprintImplementableEvent`
or `BlueprintNativeEvent` hooks for presentation. Blueprint reads state and
reacts; it does not compute state.

## 4. Component Strategy

**Composition over inheritance is mandatory.** Deep pawn inheritance chains are
prohibited.

The vehicle pawn is a thin actor that owns independent components:

| Component | Responsibility |
|---|---|
| `AeroComponent` | Front/rear downforce, drag, configurable aero balance, fictional active aero state |
| `TireComponent` (per axle or per corner) | Temperature, wear, grip state |
| `BrakeComponent` | Brake temperature, brake bias |
| `FuelComponent` | Fuel mass, consumption, mass feedback into the vehicle |
| `HybridEnergyComponent` | Fictional deployment and regeneration budget |
| `DrivetrainComponent` | Differential configuration, torque delivery |
| `SetupComponent` | Applies a setup Data Asset to all other components |
| `VehicleTelemetryComponent` | Samples the above into telemetry frames |
| `LapTrackerComponent` | Per-vehicle checkpoint/sector progress, reported to race subsystem |

Rules:

1. Components communicate through the owning vehicle's interface, not by
   directly reaching into sibling components' internals.
2. Each component owns its own state and exposes read-only accessors.
3. Each component is independently testable with synthetic inputs.
4. A component that needs a value from another component receives it through an
   explicitly ordered update step on the vehicle, not through hidden coupling.
5. Update order among simulation components is explicit and documented in code,
   because implicit tick ordering is a determinism hazard.

## 5. Data Asset Strategy

All tunable content-facing data lives in typed Data Assets, not in code
constants and not in loose Blueprint variables.

Planned Data Asset families (created in later milestones, defined here):

| Data Asset | Contents |
|---|---|
| `AF_VehicleDefinition` | Mass, dimensions, wheelbase, track width, CG, inertia targets |
| `AF_AeroProfile` | Downforce curves, drag coefficients, aero balance range, active aero states |
| `AF_TireCompound` | Grip curves, temperature windows, wear rates, degradation model inputs |
| `AF_BrakeProfile` | Torque, thermal capacity, cooling, bias range |
| `AF_EnergyProfile` | Fictional deployment/regeneration budgets and rates |
| `AF_VehicleSetup` | Player-editable setup values with valid ranges |
| `AF_BoneMapping` | Central bone-name mapping (see §7) |
| `AF_TrackDefinition` | Checkpoint order, sector boundaries, pit lane geometry references |
| `AF_SessionRules` | Session type, lap count, penalty rules, validity rules |
| `AF_QualityProfile` | Preview vs Final quality settings |
| `AF_TeamIdentity` | Fictional team name, livery slots, colours |
| `AF_DriverIdentity` | Fictional driver name, number, helmet reference |

Rules:

1. Every Data Asset has documented units and valid ranges.
2. Every numeric field that a designer can change has a defined default.
3. Data Assets are validated by an editor-side validator (`ApexFormulaEditor`).
4. No gameplay code reads a magic number that is not sourced from a Data Asset,
   a typed settings object, or a named constant in `ApexFormulaCore`.

## 6. Configuration Strategy

Three configuration layers, in increasing specificity:

1. **Project settings (`UDeveloperSettings`)** — engine-lifetime values such as
   the active quality profile, telemetry sampling rate, logging verbosity, and
   the bone mapping asset reference. Editable in Project Settings, saved to
   `Config/DefaultApexFormula.ini`.
2. **Data Assets** — content-authored, per-vehicle / per-track / per-session.
3. **Instance overrides** — per-level or per-actor overrides via Blueprint
   exposed properties, used only for level-specific configuration.

Quality profiles:

- `DevelopmentPreview` — reduced texture streaming pool, reduced shadow and
  reflection cost, lower LOD bias, simplified post-processing, reduced AI
  opponent count. Intended for a modest laptop.
- `FinalQuality` — full settings, full baking, full LODs, full effects.

Binding rule: switching to `DevelopmentPreview` changes only runtime/derived
settings. It never rewrites source assets, never re-imports at lower resolution,
and never overwrites final-quality generated output.

## 7. Vehicle Bone and Mapping Convention

The project defines its own stable convention rather than assuming a single
universal Chaos Vehicles bone naming standard.

Initial ApexFormula convention:

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

Rules:

1. These names are stored in **one central location** — the `AF_BoneMapping`
   Data Asset, referenced from project settings.
2. No C++ or Blueprint code hardcodes a bone-name string literal. All lookups go
   through the mapping.
3. The Blender generator reads the same logical names from its own centralized
   pipeline config (`af_pipeline_config.py`) so both sides can be changed
   together.
4. The convention changes **only** if a documented Unreal Engine 5.8 requirement
   proves it must. Any such change is recorded in `DECISION_LOG.md`.

**Uncertainty label:** whether Unreal Engine 5.8 imposes any additional naming or
hierarchy constraint on the chosen vehicle system is **requires Unreal Editor
verification**. It is not asserted here.

## 8. Asset Pipeline Boundaries

| Concern | Owner |
|---|---|
| Mesh generation, topology, UVs, rig construction | Blender |
| Collision mesh authoring intent | Blender (exported), reviewed in Unreal |
| LOD source generation | Blender |
| Material *definition* and shading | Unreal |
| Material *slot naming and assignment intent* | Blender (slot names), Unreal (actual materials) |
| Texture authoring | External / Blender bake outputs |
| Skeleton and bone naming | Blender, per the central convention |
| Physics asset tuning | Unreal |
| Animation Blueprint wiring | Unreal Blueprints |
| Unit conversion at the boundary | Blender export step, documented explicitly |

Hard boundary: **Blender does not attempt to author Unreal materials.** It emits
deterministic material slot names; Unreal owns the actual material graphs.

## 9. Future Multiplayer Boundaries

Multiplayer is not implemented in early milestones, but the architecture is
prepared now so it does not require a rewrite.

Preparation rules:

1. **Authoritative logic is server-shaped from day one.** Race rules, lap
   validity, timing, penalties, and energy/fuel accounting live in C++ in
   `ApexFormulaRace` and vehicle simulation components, written so they could
   execute authoritatively.
2. **Input is separated from state.** Player intent (throttle, brake, steer,
   gear, deploy) is captured as a discrete input struct, distinct from resulting
   vehicle state. This is the natural seam for future replication and for replay.
3. **No gameplay decision depends on client-only presentation.** Camera, HUD,
   audio, and effects never feed back into rules.
4. **Determinism hazards are documented, not ignored.** Variable tick rate,
   floating-point divergence, and physics substepping are known hazards; the
   vehicle architecture decision (`VEHICLE_SYSTEM_DECISION.md`) evaluates them
   explicitly.
5. **State that would need replication is identified early**, even while
   single-player, and kept in plain replicable-friendly types.

Explicitly **not** promised in early milestones: netcode, rollback, client
prediction, dedicated server support, or matchmaking.

## 10. Testing Philosophy

Four layers:

1. **Static inspection** — naming conventions, module dependency direction,
   documentation consistency. Cheap, runs without the engine.
2. **Automated logic tests** (`ApexFormulaTests`) — pure functions and
   deterministic subsystems: lap validity, sector timing arithmetic, unit
   conversion, energy budget accounting, setup range clamping. These require
   local compilation to run.
3. **Editor validation** (`ApexFormulaEditor`) — Data Asset completeness, bone
   mapping resolution, missing references, out-of-range values. Requires Unreal
   Editor verification.
4. **Human validation** — visual inspection and playtesting for handling feel,
   visual correctness, and likeness. Never automated, never claimed by the
   assistant.

Rules:

- Physics *feel* is never asserted by a test; it is a playtest outcome.
- A test that cannot run without the engine is labelled as requiring local
  compilation, and its result is never assumed.
- Every validation report states which of the seven honesty labels applies.

## 11. Logging and Telemetry Strategy

**Logging.** Dedicated log categories declared in `ApexFormulaCore`:

```
LogApexFormula          general
LogApexFormulaVehicle   vehicle simulation
LogApexFormulaRace      rules, timing, penalties
LogApexFormulaAI        AI drivers
LogApexFormulaPipeline  asset/import/validation
LogApexFormulaTelemetry telemetry subsystem
```

Conventions: verbosity is configurable per category; shipping builds default to
warnings and errors; the active quality profile is logged at startup; no
personally identifying information is ever logged.

**Telemetry.** A telemetry frame is a plain, versioned struct sampled at a fixed
configurable rate, independent of render frame rate.

Frame contents (initial intent, extended in later milestones): timestamp,
session time, lap number, sector, position/rotation/velocity, throttle, brake,
steering, gear, engine state, per-corner tire temperature and wear, per-corner
brake temperature, fuel mass, hybrid energy state, aero balance, downforce and
drag magnitudes, lap-validity flag.

Rules:

1. Telemetry is **read-only observation.** Recording telemetry never alters
   simulation results.
2. The frame struct is **versioned**; a version integer is written with every
   recording so older captures remain interpretable.
3. Telemetry uses a fixed-size ring buffer in memory with optional flush to
   disk, so a long session cannot exhaust memory.
4. The telemetry frame is designed to be a viable foundation for **replay**
   preparation, but replay is not implemented in early milestones.
5. Telemetry output is written to a generated/derived location, never mixed with
   source assets.

## 12. Units and Conventions

- Unreal-facing linear unit: **centimetres**.
- Unreal-facing angular unit: degrees.
- Unreal-facing mass unit: kilograms.
- Time: seconds (double precision for accumulated session time).
- All conversion at the Blender/Unreal boundary is explicit and documented in
  `BLENDER_PIPELINE_DESIGN.md` — including forward axis, up axis, scale factor,
  and applied transforms. Vague phrasing such as "convert Z-up to Unreal" is not
  acceptable anywhere in this project.

## 13. Compatibility Layer Policy

Any API surface that is version-sensitive or uncertain for Unreal Engine 5.8 or
Blender 5.2 LTS is isolated behind a clearly named compatibility wrapper — for
example a `ApexFormulaCompat` namespace in C++ and an `af_compat.py` module on
the Blender side — with the uncertainty documented in `VERSION_MATRIX.md`.

No Unreal Engine, Chaos Vehicles, Blender, MetaHuman, FBX, or Blueprint API is
invented in this project. Where an exact API name or signature is not confirmed,
the document says so and marks it as requiring verification rather than
asserting it.
