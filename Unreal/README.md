# ApexFormula — Unreal Project

The Unreal Engine 5.8 project and its six C++ modules. Milestone 1 created the structure;
Milestone 2 added the vehicle implementation behind it.

**Nothing in this directory has been compiled.** No Unreal Engine, Unreal Build Tool, MSVC or
clang existed in the environment where this code was authored. Everything below that is stated
as fact was checked by a program; everything else is labelled. See §7.

---

## 1. Layout

```
Unreal/
  ApexFormula.uproject
  Config/
    DefaultEngine.ini
    DefaultGame.ini
    DefaultInput.ini
    DefaultApexFormula.ini
  Source/
    ApexFormula.Target.cs
    ApexFormulaEditor.Target.cs
    ApexFormulaCore/      Public/  Private/
    ApexFormulaVehicle/   Public/  Private/
    ApexFormulaRace/      Public/  Private/
    ApexFormulaUI/        Public/  Private/
    ApexFormulaEditor/    Public/  Private/
    ApexFormulaTests/     Public/  Private/
```

The project sits under `Unreal/` rather than at the repository root because this repository also
holds a Blender pipeline, a document set and standalone tooling, none of which belong inside an
engine tree. Quarantining the engine tree makes every generated directory ignorable by prefix.
Recorded as decision **D-027**.

There is no `Content/` directory yet. The project is C++ and configuration only — no art, no
Blueprints, no assets. It will appear at the milestone that first needs it.

---

## 2. Modules

| Module | Type | Loading phase | Depends on |
| --- | --- | --- | --- |
| `ApexFormulaCore` | Runtime | PreDefault | Engine, CoreUObject, DeveloperSettings |
| `ApexFormulaVehicle` | Runtime | Default | Core, PhysicsCore, ChaosVehicles, EnhancedInput |
| `ApexFormulaRace` | Runtime | Default | Core |
| `ApexFormulaUI` | Runtime | Default | Core, UMG, Slate, SlateCore |
| `ApexFormulaEditor` | Editor | PostEngineInit | Core, Vehicle, Race, UnrealEd, EditorSubsystem |
| `ApexFormulaTests` | DeveloperTool | Default | Core, Vehicle, Race |

This table matches `Documentation/TECHNICAL_ARCHITECTURE.md` §2, and the match is enforced by a
program rather than by review — see §6.

Three boundary rules hold and are checked:

- **`ApexFormulaCore` depends on no ApexFormula module.** It is the bottom of the graph.
- **`ApexFormulaRace` must not depend on `ApexFormulaVehicle`.** Race timing, sector logic and
  lap validation are expressed against the `IAFRaceParticipant` interface, so they can be tested
  with no vehicle in existence. This is why `UAFSectorTimer` and `UAFLapValidator` are plain
  `UObject`s that tick nothing and own no world: every input is an explicit `double SessionTime`.
- **The dependency graph is acyclic.**

`ChaosVehicles` is an assumption, not an observed module name — see `VERSION_MATRIX.md` §5.21.

---

## 3. The vehicle backend chokepoint (D-008)

`AFVehicleCompatibilityLayer.h` and `AFVehicleCompatibilityLayer.cpp` are the **only** two files
in the entire project permitted to name an engine vehicle type. Every other file that needs
vehicle behaviour goes through this layer.

**A Chaos Vehicles backend is now bound in code.** `BindBackend` resolves the movement component,
sets `BackendId` and `bBackendAvailable`, and `ApplyInputFrame` forwards a sanitised frame to it.
The layer no longer returns `false` unconditionally.

Two things follow, and they are not the same thing:

- The backend is **implemented**. `automatically validated` — the chokepoint still holds, and no
  engine vehicle token appears outside these two files.
- The backend is **not verified**. Every engine symbol the layer names is an assumption about the
  UE 5.8 Chaos Vehicles API. `requires local compilation`, then `requires playtesting`.

The layer also holds wheel setups supplied before binding, in `PendingWheels`, and applies them
idempotently once a backend exists (**D-036**). Applying to a null backend would discard
suspension geometry silently, and silent loss surfaces much later as a handling bug with no
traceable cause.

The validator enforces the chokepoint by scanning every source file for engine vehicle API tokens
and failing if one appears outside the two permitted files.

---

## 4. Data assets and configuration

`UAFBoneNameMap` and `UAFQualityProfile` are `UPrimaryDataAsset` types with a `ValidateSelf()`
that returns a list of problems rather than a bare bool, so the editor validator can report *what*
is wrong. `UAFVehicleDefinition`, `UAFTrackDefinition` and `UAFSessionRules` follow the same shape.

`FAFVehicleBackendSetup` and `FAFWheelSetup` use the same convention. `ApplyVehicleDefinition`
transfers only the fields `UAFVehicleDefinition` actually carries — mass, wheelbase, track widths,
overall length, centre-of-mass bias and height. Powertrain and aerodynamic values keep their
struct defaults rather than being invented here, because a definition asset is chassis geometry
and duplicating tuning data across two assets is what D-007 exists to prevent (**D-038**).

### Where vehicle dimensions come from (D-041)

`BlenderPipeline/scripts/af_pipeline_config.py`, dictionary `DESIGN`, is the **single source of
truth** for every vehicle dimension in this project. `UAFVehicleDefinition` carries a subset of
those numbers so that Unreal-side code does not have to parse a Python file, and that subset is
required to agree.

It did not agree. Milestone 2 found two live contradictions:

| Field | `UAFVehicleDefinition` before | `af_pipeline_config.py::DESIGN` | Now |
| --- | --- | --- | --- |
| `OverallLengthM` | 5.30 | `overall_length_m` = 5.60 | **5.60** |
| `RearTrackM` | 1.55 | `track_rear_m` = 1.540 | **1.54** |

The Blender values won because Blender is what actually builds the mesh: the generated body is
5.600 m long and the rear track is 1.540 m, and the pre-export validator measures the result and
compares it against `DESIGN`. Had the Unreal numbers won, the physics chassis would have been
30 cm longer than the visual mesh sitting on top of it — the kind of defect that reads as
"the collision feels wrong" three milestones later.

`AFVehicleDefinition.h` now carries a source-of-truth comment block naming the file, the
dictionary and the specific keys, so the next person to edit a number is told where the other
copy lives before they change one and not the other.

Unchanged and still agreeing: `WheelbaseM` 3.60, `FrontTrackM` 1.60, `DryMassKg` 740.0,
`CentreOfMassBiasRear` 0.55, `CentreOfMassHeightM` 0.28. `DataVersion` is 2.

All default numeric values are **ApexFormula design values**. They are not measurements of any
real vehicle or circuit and are not claimed to be realistic.

`Config/DefaultApexFormula.ini` configures `UAFDeveloperSettings`. Every key in that file is
checked to correspond to a real `UPROPERTY(Config)` on the class — a stale key is a silent
failure otherwise, since Unreal ignores keys it does not recognise.

Path settings reject absolute paths, drive letters and UNC paths, so a machine-specific path
cannot be committed. `AFDeveloperSettings.cpp` is consequently the one file allowed to *contain*
a UNC path, because rejecting one requires naming one; three explicit assertions verify that this
exemption still guards a file that really does the rejecting.

---

## 5. Bone convention

The eleven-bone convention (D-012) has two implementations: `af_pipeline_config.py` on the Blender
side and `AFBoneNameMap` on the Unreal side. They are checked for agreement by **emulation** — the
validator imports the Python module live, parses the C++, and re-derives the ordering and parent
map the compiled code would produce.

It is done this way because both bone bugs found in this project were doc comments that had
drifted away from correct code. A text comparison would have compared the drifted comment.
Recorded as decision **D-029**.

Consequence: changing the *style* of `AFBoneNameMap.cpp` can break the validator's parser even if
behaviour is unchanged, and requires an emulator update.

There are now two independent checks on the Blender side of this contract, and they cover
different things:

- The **static** check, above, proves the two *conventions* agree with each other.
- The **executed** check, in CI, proves the Blender rig stage actually *produces* that
  convention. Every push runs `af_smoke_test.py` under headless Blender, and stage 3 prints all
  eleven bones with parent and head position in metres and centimetres, then asserts
  `bone_order_matches_config == True` and `bone_count == 11` against nine bound meshes.

Neither is the same as agreement between a convention and an **imported asset**. Milestone 2
acceptance criterion 4 concerns that third thing, and it still `requires Unreal Editor
verification` — no FBX has been imported here, because no editor exists here.

---

## 6. Validation

Two validators run, both standard-library-only. No Unreal, no Blender, no third-party packages.
Exit code 0 = pass, 1 = violations found, 2 = could not run.

```
python3 Tools/af_static_validate.py     --root .
python3 Tools/af_validate_interfaces.py --self-test
python3 Tools/af_validate_interfaces.py --root .
```

**`af_static_validate.py`** runs fifteen checks: build graph, module boundaries, acyclicity,
module implementations, `.uproject` consistency, targets, header hygiene, include resolution,
originality, path portability, vehicle backend isolation, telemetry literal containment, bone
convention, configuration keys, and test declarations.

Its Milestone 1 measurement was `checks passed: 2300, failures: 0, warnings: 0`. That count is
**not** quoted as the current figure — the tree has grown since and the number has not been
re-measured into this document. The live result is the CI run on `main`, which passes.

It has been mutation-tested — **11 of 11 injected defects detected**, with a negative control (a
prohibited word inside a comment) correctly ignored. Recorded as decision **D-030**; details in
`VERSION_MATRIX.md` §5.30.

**`af_validate_interfaces.py`** compares every `override` against the pure-virtual it claims to
implement and fails on a return-type mismatch. It exists because `af_static_validate.py` was
structurally incapable of finding D-035 — a pawn returning `FText` where the interface declared
`FString`, which had been sitting in `main` undetected because nothing here compiles.

It carries a **nine-case mutation suite** in `--self-test`, and CI runs the self-test *before* the
real check, so a checker that has stopped detecting its own mutations fails the build instead of
reporting a green tree. Both run on Python 3.9 and 3.12. Recorded as decision **D-037**.

Its documented blind spot: an out-of-line definition written `FVector *Class::Method()` is not
matched. The header declaration is still checked, and no interface in this project returns a
pointer.

Neither validator can see a defect that only exists once geometry is built. D-040 is the worked
example: a 24 mm halo overshoot that every static check passed and the executed Blender stage
caught immediately. That is the argument for the third CI job, not a general claim that static
checking is weak.

---

## 7. Verification Ledger for This Document

| Claim | Label |
| --- | --- |
| The directory layout in §1 is what exists in this repository | automatically validated |
| The module table in §2 matches `TECHNICAL_ARCHITECTURE.md` §2 | automatically validated |
| Core depends on no ApexFormula module; Race does not depend on Vehicle; the graph is acyclic | automatically validated |
| No engine vehicle API appears outside the two D-008 files (§3) | automatically validated |
| A Chaos backend is bound *in code* by `AFVehicleCompatibilityLayer.cpp` (§3) | statically inspected |
| That backend binding does anything at run time (§3) | not claimed — `requires local compilation`, then `requires playtesting` |
| Every key in `DefaultApexFormula.ini` maps to a real `UPROPERTY(Config)` (§4) | automatically validated |
| `UAFVehicleDefinition` dimensions now agree with `af_pipeline_config.py::DESIGN` (§4, D-041) | statically inspected |
| The Blender mesh really is 5.600 m long and 1.540 m rear track (§4) | automatically validated — measured by the pre-export validator in CI |
| The Blender and Unreal bone conventions agree with each other (§5) | automatically validated |
| The Blender rig stage produces 11 bones in config order with 9 bound meshes (§5) | automatically validated — executed under headless Blender on every push |
| An imported skeleton's bone names match `UAFBoneNameMap` (§5) | not claimed — `requires Unreal Editor verification` |
| Every `override` agrees in return type with the interface it implements (§6) | automatically validated |
| The mutation scores quoted in §6 are measured values | automatically validated |
| The 2300 figure in §6 is the Milestone 1 measurement, not the current tree | statically inspected |
| The D-040 halo overshoot was caught by the executed stage, not a static check (§6) | automatically validated |
| Design intent, rationale and the reasons behind each decision | statically inspected |
| Default numeric values are ApexFormula design values, not measurements | statically inspected |
| Any file in this directory compiles | not claimed — `requires local compilation` |
| The Unreal Editor loads these six modules without error | not claimed — `requires Unreal Editor verification` |
| The 37 declared automation tests are discovered, or pass | not claimed — `requires local compilation`, then `requires Unreal Editor verification` |
| The vehicle accelerates, brakes, steers, or stays on the ground | not claimed — `requires playtesting` |
| `ChaosVehicles` and `ChaosVehiclesPlugin` are the correct 5.8 names | not claimed — see `VERSION_MATRIX.md` §5.21 |
| The APIs assumed throughout the C++ exist with the assumed signatures | not claimed — see `VERSION_MATRIX.md` §5.21–§5.26 |
| Anything **in this directory** has been run, opened, packaged or played | not claimed — no engine exists in the authoring environment |
