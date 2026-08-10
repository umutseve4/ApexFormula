# ApexFormula — Unreal Project

Milestone 1 output: the Unreal Engine 5.8 project and its six C++ modules.

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

There is no `Content/` directory yet. Milestone 1 is C++ and configuration only — no art, no
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

**No backend is currently bound.** `BackendId` is `none`, `bBackendAvailable` is `false`, and
`ApplyInputFrame` stores the frame, calls `Sanitise()` on it, logs at Verbose and returns `false`.
This is deliberate: Milestone 1 excludes vehicle physics. The layer exists so that when a backend
is bound, exactly one file changes.

The validator enforces the chokepoint by scanning every source file for engine vehicle API tokens
and failing if one appears outside the two permitted files.

---

## 4. Data assets and configuration

`UAFBoneNameMap` and `UAFQualityProfile` are `UPrimaryDataAsset` types with a `ValidateSelf()`
that returns a list of problems rather than a bare bool, so the editor validator can report *what*
is wrong. `UAFVehicleDefinition`, `UAFTrackDefinition` and `UAFSessionRules` follow the same shape.

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

---

## 6. Validation

```
python3 Tools/af_static_validate.py --root .
```

Standard library only. No Unreal, no Blender, no third-party packages. Exit code 0 = pass,
1 = violations found, 2 = could not run. Current result on this tree:

```
checks passed : 2300
failures      : 0
warnings      : 0
RESULT: PASS  (static validation only - nothing was compiled)
```

Fifteen checks run: build graph, module boundaries, acyclicity, module implementations,
`.uproject` consistency, targets, header hygiene, include resolution, originality, path
portability, vehicle backend isolation, telemetry literal containment, bone convention,
configuration keys, and test declarations.

The validator has itself been mutation-tested — **11 of 11 injected defects detected**, with a
negative control (a prohibited word inside a comment) correctly ignored. A checker that cannot
fail proves nothing. Recorded as decision **D-030**; details in `VERSION_MATRIX.md` §5.30.

---

## 7. Verification Ledger for This Document

| Claim | Label |
| --- | --- |
| The directory layout in §1 is what exists in this repository | automatically validated |
| The module table in §2 matches `TECHNICAL_ARCHITECTURE.md` §2 | automatically validated |
| Core depends on no ApexFormula module; Race does not depend on Vehicle; the graph is acyclic | automatically validated |
| No engine vehicle API appears outside the two D-008 files (§3) | automatically validated |
| Every key in `DefaultApexFormula.ini` maps to a real `UPROPERTY(Config)` (§4) | automatically validated |
| The Blender and Unreal bone conventions agree (§5) | automatically validated |
| The validator result quoted in §6 is a measured value | automatically validated |
| The mutation score quoted in §6 is a measured value | automatically validated |
| Design intent, rationale and the reasons behind each decision | statically inspected |
| Default numeric values are ApexFormula design values, not measurements | statically inspected |
| Any file in this directory compiles | not claimed — `requires local compilation` |
| The Unreal Editor loads these six modules without error | not claimed — `requires Unreal Editor verification` |
| The 27 declared automation tests are discovered, or pass | not claimed — `requires local compilation`, then `requires Unreal Editor verification` |
| `ChaosVehicles` and `ChaosVehiclesPlugin` are the correct 5.8 names | not claimed — see `VERSION_MATRIX.md` §5.21 |
| The APIs assumed throughout the C++ exist with the assumed signatures | not claimed — see `VERSION_MATRIX.md` §5.21–§5.26 |
| Anything here has been run, opened, packaged or played | not claimed — no engine exists in the authoring environment |
