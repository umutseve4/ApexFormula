# ApexFormula — Version Matrix

**Document status:** statically authored. First written at Milestone 0A; §5.21–§5.30 added at Milestone 1; §5.31–§5.32 added at Milestone 2. No tool listed in §1 has been launched, compiled against or executed by this document's author. Every entry in §1 is a *pinned intent*, not an observed installation. The only things in this document that were mechanically measured are the ones explicitly labelled `automatically validated`.

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

### 5.21 — `ChaosVehicles` module name and `ChaosVehiclesPlugin` plugin name

`ApexFormulaVehicle.Build.cs` lists `ChaosVehicles` as a private dependency and `ApexFormula.uproject` enables the plugin `ChaosVehiclesPlugin`. Both strings are stated intent, not observed fact. The module name and the plugin name are *not* the same string, and either could have been renamed in 5.8. If the module name is wrong, `ApexFormulaVehicle` fails to build with an unresolved module error; if the plugin name is wrong, the editor reports a missing plugin on project load.

This is contained by decision D-008: no ApexFormula file outside `AFVehicleCompatibilityLayer.h/.cpp` names any engine vehicle type. That containment is statically enforced by `Tools/af_static_validate.py` and has not weakened.

**Corrected at Milestone 2.** An earlier revision of this section stated that the compatibility layer "binds **no backend at all** (`BackendId` is `none`, `bBackendAvailable` is `false`)". That was accurate for the Milestone 1 tree and is **no longer accurate**: `AFVehicleCompatibilityLayer.cpp` now binds a Chaos backend, sets `BackendId` accordingly and can report `bBackendAvailable == true`. The consequence is that a wrong module or plugin name is *no longer* a pure build-configuration fix in one file — it is still confined to one file, but that file now contains real binding logic that would need to change with it. Nothing about that binding has been compiled or executed; see §5.31.

### 5.22 — `DECLARE_DYNAMIC_MULTICAST_DELEGATE_ThreeParams` with a `double` parameter

`AFCheckpoint.h` declares `FAFOnCheckpointPassed` as a three-parameter dynamic multicast delegate, one parameter of which is a `double`. Dynamic delegates are reflected and Blueprint-exposed, and Blueprint's historical floating-point pin was `float`; UE5 introduced double-precision Blueprint reals, but whether a `double` is accepted in a *dynamic* delegate signature in 5.8 is unverified.

**This is the highest-risk single declaration in the Milestone 1 C++.** If it is rejected, the fix is to change the parameter to `float` at the delegate boundary only — the timing types themselves stay `double`, because lap timing precision must not be reduced to satisfy a delegate signature.

### 5.23 — `EAutomationTestFlags` used as an `int32` mask

All six Milestone 1 test files declare a file-local `static const int32 AF<Area>TestFlags = EAutomationTestFlags::EditorContext | EAutomationTestFlags::CommandletContext | EAutomationTestFlags::ClientContext | EAutomationTestFlags::ProductFilter;`. This is the historical idiom and relies on the flags being a plain (unscoped) enum that decays to `int32`.

If 5.8 converted `EAutomationTestFlags` to an `enum class`, every one of those files fails to compile at that line. The fix is mechanical but touches all of them: either use the engine's own flag type for the constant or insert explicit casts. Flagged here because a single upstream change produces many simultaneous failures that could otherwise look like many unrelated bugs. The Milestone 2 test file added in `AFVehicleBackendSetupTests.cpp` follows the same idiom and is exposed to the same risk.

### 5.24 — `AddExpectedError(...)` matching a `UE_LOG(..., Warning, ...)`

Three test files call `AddExpectedError(<substring>, EAutomationExpectedErrorFlags::Contains, 0)` before deliberately invoking a rejected operation. The rejections in `AFSectorTimer` and `AFLapValidator` log at **Warning** level, not **Error**.

Whether `AddExpectedError` suppresses and matches Warnings as well as Errors in 5.8 is unverified. **This is the single most likely reason the automation tests would run but fail as written.** If Warnings are not covered, the options are to raise those specific rejections to Error, or to drop the expectation and assert only the return value. Note the third argument `0` means "any number of occurrences, including zero", which was chosen precisely to reduce this fragility.

### 5.25 — `TestEqual` overloads and tolerance behaviour

Double comparisons pass an explicit tolerance (`1.0e-9`). Two call sites compare `float`s **without** an explicit tolerance argument and therefore rely on the engine's default tolerance rather than exact equality; if no such overload exists the comparison may fall through to an exact-match overload and become brittle. `TestEqual` is also used with an `int64` expected value (telemetry sample counters) and `TestNotEqual` with two `int32`s. All are ordinary usage; none is observed.

### 5.26 — Reflection and container idioms used across the modules

| Idiom | Where used | Risk if wrong |
| --- | --- | --- |
| `AActor::GetComponents<T>(TArray<T*>&)` | `AFVehiclePawn.cpp` | Signature/overload changed; local fix |
| `FName::LexicalLess` as a sort predicate | `AFVehiclePawn.cpp` component ordering | Determinism of subsystem order lost |
| `AActor::IsActorBeingDestroyed()` called from an interface override | `AFVehiclePawn.cpp` | Constness mismatch |
| `CreateDefaultSubobject<UAFVehicleCompatibilityLayer>` for a plain `UObject` | `AFVehiclePawn.cpp` | Fallback is `NewObject` in `BeginPlay` |
| A `UCLASS` deriving both `UActorComponent` and a `UINTERFACE` interface | `AFVehicleComponentBase` | Multiple-inheritance/UHT rejection |
| `TSet::Add(Value, &bAlreadyInSet)` | `AFLapValidator.cpp` | Out-parameter overload absent |
| `TArray::Last()` on a `TArray<USTRUCT>` | `AFSectorTimer.cpp` | None expected |
| `FAFOnTelemetrySample::FDelegate` nested typedef, `CreateLambda` / `CreateWeakLambda` | `AFHudViewModel.cpp` | Subscription cannot be expressed as written |
| `UPROPERTY(Transient)` on a `TWeakObjectPtr<UAFTelemetryBus>` | `AFHudViewModel.h` | UHT rejects weak pointer as a UPROPERTY |
| `meta=(AllowedClasses="/Script/ApexFormulaCore.AFQualityProfile")` on `FSoftObjectPath` | `AFDeveloperSettings.h` | Filter ignored; picker shows everything |
| `UDeveloperSettings::GetCategoryName()` as a virtual override | `AFDeveloperSettings.h/.cpp` | Settings appear in the wrong category |
| `static constexpr int32` declared inside a `UCLASS` body | `AFSaveGame.h` | UHT parse error |
| `Cast<IAFRaceParticipant>(AActor*)` | `AFCheckpoint.cpp` | Fallback is `Implements<UAFRaceParticipant>()` then `Cast` |
| `SetGenerateOverlapEvents(true)` and `SetCollisionResponseToAllChannels(ECR_Overlap)` in a `UBoxComponent` constructor | `AFCheckpoint.cpp` | Overlaps never fire |
| `TStringBuilder<2048>` with `Appendf` | `AFDataValidator.cpp` | Header/API moved |
| A `UFUNCTION` returning `TArray<FAFValidationIssue>` | `AFDataValidator.h` | UHT return-type restriction |
| `IMPLEMENT_SIMPLE_AUTOMATION_TEST` and `Misc/AutomationTest.h` reachable from a non-editor module | all test files | Tests module must become editor-only |
| `EditorSubsystem` as a private dependency of an Editor-type module | `ApexFormulaEditor.Build.cs` | Module name changed |

### 5.27 — Nothing in this section has been compiled

Every entry in §5.21 to §5.26 is a **statement about C++ that has never been fed to a compiler**. No Unreal Engine installation, no Unreal Build Tool, no MSVC and no clang exist in the environment where this project was authored. The whole of §5.21 to §5.26 therefore carries the label `requires local compilation`, and no claim to the contrary appears anywhere in this repository. The same is true of §5.31.

What *was* mechanically verified is described in §5.28 and §5.32.

### 5.28 — What the static validator actually proves

`Tools/af_static_validate.py` is pure-Python, standard-library only, and runs without Unreal or Blender.

**On the Milestone 1 tree it reported 2300 checks passed, 0 failures, 0 warnings, exit code 0.** That number is a *Milestone 1 measurement* and is quoted here as history, not as a current figure. Milestone 2 added five source files, so the current count is certainly higher; it has deliberately **not** been re-guessed. The live figure is whatever the `af_static_validate` job prints in the most recent CI run — that job is the authority, not this sentence.

It proves, mechanically: the module dependency graph matches `TECHNICAL_ARCHITECTURE.md` §2 and is acyclic; `ApexFormulaRace` does not depend on `ApexFormulaVehicle`; `ApexFormulaCore` depends on no ApexFormula module; every module declared in the `.uproject` has a `.Build.cs` and an `IMPLEMENT_MODULE`; every header has `#pragma once`; every include resolves to a file that exists; no prohibited token appears in any name; no absolute or container-specific path is hard-coded; no engine vehicle API appears outside the D-008 chokepoint; no telemetry channel string literal appears outside `AFTelemetryTypes.cpp`; every key in `DefaultApexFormula.ini` maps to a real `UPROPERTY(Config)`; and the Unreal bone convention agrees with `af_pipeline_config.py`.

It proves **nothing** about whether the C++ compiles, whether the editor loads the modules, or whether the declared automation tests pass. After Milestone 2 there are **37** declared automation tests (27 from Milestone 1, 10 added in `AFVehicleBackendSetupTests.cpp`); that count is obtained by counting declarations in the source, not by running anything. Execution remains `requires local compilation` and `requires Unreal Editor verification`.

### 5.29 — The bone check is an emulation, and that is deliberate

The Blender/Unreal bone agreement is not checked by comparing text. The validator **imports `af_pipeline_config.py` live** as the source of truth, then parses `AFBoneNameMap.cpp`, extracts its prefix, literal bone names, corner order and the two `Printf` format strings, and *re-derives* the ordering and parent map the compiled C++ would produce. The derived structures are compared against the Python constants.

This matters because the two known bone bugs in this project were both **doc comments that drifted away from correct code**, not wrong code. A textual diff would have compared the drifted comment; an emulation compares behaviour. Consequence: a change to the *style* of `AFBoneNameMap.cpp` — not its behaviour — can break the parser and must be accompanied by an emulator update.

**Scope limit worth restating at Milestone 2:** this check proves the two *conventions* agree. It says nothing about whether an actually imported skeleton carries those bone names, because no FBX has been exported or imported. That is Milestone 2 acceptance criterion 4 and it is not met.

### 5.30 — The validator itself was mutation-tested

A checker that cannot fail proves nothing. `/app/workspace/mutation_test.py` (a scratch harness, deliberately **not** committed) copies the tree to a temporary directory, injects one deliberate defect at a time, and asserts the validator rejects it.

Result: **11 of 11 mutations detected**, plus one negative control — a prohibited word placed inside a comment — correctly *ignored*, and the tree correctly restored afterwards.

Two findings deserve recording because they are the reason this section exists:

1. **The first run appeared to show three validator gaps. Two were flaws in the test**, which injected leaks inside `//` comments that the validator strips by design. The lesson from Milestone 0B — when a residual issue contradicts a PASS, suspect the checker — has a symmetric form: **when a mutation is missed, suspect the mutation first, but prove it by reading the source.**
2. **One gap was real.** `PROHIBITED_IDENTIFIER_PATTERNS` used `\bF1\b`, which *cannot* match `F1SeasonCount`, because the trailing `\b` fails when `1` is followed by a word character. The prohibited token must never appear in any *name*, so identifier-embedded occurrences were exactly the case being skipped. `Formula1` was invisible to every pattern, containing neither `F1` nor `FormulaOne`. The patterns are now substring matches and the suite reaches 11/11.

Two earlier failures were also checker defects rather than code defects, and are recorded for the same reason: `check_portability` flagged the very line in `AFDeveloperSettings.cpp` whose job is to *reject* UNC paths, and `check_telemetry_literals` was the only containment check that did not strip comments before searching. Both were fixed; the path exemption carries three explicit guard assertions proving the exempted file still contains its rejection logic, so the exemption cannot silently start covering a file that validates nothing.

### 5.31 — Version-sensitive surfaces introduced by the Milestone 2 C++

Milestone 2 added `AFVehicleCompatibilityLayer.cpp`, `AFVehiclePawn.cpp`, `AFPlayerController.cpp` and `AFVehicleBackendSetupTests.cpp`. Every engine API named below is an **assumption** with the label `requires local compilation`.

| # | Assumption | Failure mode if wrong |
| --- | --- | --- |
| 5.31.1 | The Chaos Vehicles movement-component type, its wheel-setup container and its per-wheel class exist in 5.8 under the names used in `AFVehicleCompatibilityLayer.cpp` | The layer does not compile; contained to one file by D-008 |
| 5.31.2 | Wheel radius, width, steering, suspension, brake and handbrake parameters are settable through the properties the layer writes | Compiles but the vehicle is misconfigured; a `requires playtesting` failure, not a build failure |
| 5.31.3 | Engine wheel radii are expressed in centimetres, so the layer's metres→centimetres conversion at the boundary is the correct direction | Wheels 100× wrong; vehicle sinks or launches |
| 5.31.4 | Deferred wheel application (D-036) is safe — that the backend tolerates wheel parameters being written after component registration rather than in the constructor | Parameters silently ignored; `AreWheelParametersApplied()` reports true while nothing took effect |
| 5.31.5 | Enhanced Input types (`UInputMappingContext`, `UInputAction`, `UEnhancedInputComponent::BindAction`, `UEnhancedInputLocalPlayerSubsystem`) are reachable with the signatures used in `AFPlayerController.cpp` | The controller does not compile; input is unbound |
| 5.31.6 | `USpringArmComponent::SocketName`, `bEnableCameraRotationLag` and `CameraRotationLagSpeed` exist as used in `AFVehiclePawn.cpp` | Camera boom misconfigured or does not compile |
| 5.31.7 | The Milestone 2 test file's assumptions hold: `NewObject<>(GetTransientPackage())` is sufficient to construct the layer under test, and the accessors `GetForwardSpeedKph()`, `GetAppliedFrameCount()` and `AreAllWheelsGrounded()` behave as the tests expect | Tests compile but fail, or fail to compile |
| 5.31.8 | `FAFVehicleBackendSetup::ValidateSelf()` emits the exact message substrings the tests match on | Tests fail on message text rather than on behaviour |

**None of §5.31 has been compiled or executed.** The vehicle has never moved, because nothing has ever been built or run. Milestone 2 acceptance criteria 1 (accelerates, brakes, steers), 2 (stable at rest) and 4 (imported skeleton bone names match) are **not met**. Criterion 3 (all engine vehicle access goes through `UAFVehicleCompatibilityLayer`) **is** met and is statically enforced.

### 5.32 — What the interface checker proves

`Tools/af_validate_interfaces.py` is a second, separate validator added at Milestone 2 (decision D-037). It is pure-Python, standard-library only, and targets Python 3.9 and above.

It parses every `.h` and `.cpp` under `Unreal/Source`, collects the pure-virtual method signatures declared by interfaces, and compares the **return type** of every implementing declaration and out-of-line definition against the interface's. A mismatch is an error.

This exists because Milestone 2 began with exactly that defect: `IAFRaceParticipant::GetParticipantDisplayName()` returns `FString`, while `AAFVehiclePawn` declared and defined it returning `FText`. That is a class of bug the compiler would catch immediately but which no existing static check could see, and it survived from Milestone 1 into Milestone 2 unnoticed. Decision D-035 resolved it in favour of the interface contract.

**What it proves:** it carries a `--self-test` flag driving a **9-case mutation suite**, which passes on both Python 3.9 and Python 3.12 in CI, and it reports zero errors against the real tree in the same CI run. Both facts are `automatically validated`.

**Documented limits, stated so they are not mistaken for coverage:**

- It compares return types only. Parameter lists, constness and reference qualifiers are not compared.
- An unrelated method that happens to share a name with an interface method will be compared against that interface's contract — a possible false positive.
- **Known blind spot:** an out-of-line definition written as `FVector *Class::Method()` — with the pointer asterisk bound to the type rather than the name — is not matched and is therefore not checked.
- Where two interfaces declare the same method name with *different* return types, the checker **drops** that name rather than guessing which contract applies.

It is a separate script rather than a change to `af_static_validate.py` because amending the primary validator would have required re-transmitting roughly 60 KB of source verbatim through a whole-file write API, risking silent corruption of the project's main checker. That trade-off is recorded as D-037.

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
| §5.21 to §5.26 are the version-sensitive surfaces introduced by the Milestone 1 C++ | statically inspected |
| Every API in §5.21 to §5.26 exists in UE 5.8 with the signature assumed | not claimed — `requires local compilation`; see §5.27 |
| §5.22 (`double` in a dynamic delegate) and §5.24 (`AddExpectedError` on a Warning) are the two highest-risk Milestone 1 assumptions | statically inspected — a judgement, not a measurement |
| The validator reported 2300 checks, 0 failures, exit code 0 **on the Milestone 1 tree** | automatically validated — a Milestone 1 measurement, not a current figure |
| The current check count after Milestone 2 | not claimed — read the latest CI run; it has deliberately not been re-guessed |
| The specific properties listed in §5.28 are the ones the validator actually enforces | automatically validated |
| The bone check re-derives behaviour rather than diffing text (§5.29) | automatically validated |
| The bone check says anything about an actually imported skeleton | not claimed — no FBX has been exported or imported; see §5.29 |
| `af_static_validate.py` detects 11 of 11 injected defects and ignores the negative control (§5.30) | automatically validated |
| §5.31 lists the version-sensitive surfaces introduced by the Milestone 2 C++ | statically inspected |
| Any Milestone 2 C++ file has been compiled, or the vehicle has moved | not claimed — `requires local compilation`, then `requires playtesting` |
| Milestone 2 acceptance criterion 3 (all engine vehicle access is behind the compatibility layer) holds | automatically validated |
| Milestone 2 acceptance criteria 1, 2 and 4 hold | not claimed — nothing has been built, imported or driven |
| There are 37 declared automation tests after Milestone 2 | statically inspected — counted from declarations, none executed |
| Any automation test has been executed | not claimed — no engine, UBT, MSVC or clang exists in the authoring environment |
| `af_validate_interfaces.py` passes its 9-case self-test on Python 3.9 and 3.12, and reports zero errors on the real tree | automatically validated |
| `af_validate_interfaces.py` checks anything beyond return types | not claimed — see the limits listed in §5.32 |
| Any listed tool is installed, runnable, or of the stated version | not claimed — see §5.1, §5.2, §5.11 |
