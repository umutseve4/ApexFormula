# Milestone 2 — Vehicle Implementation

Status of this document: written alongside the Milestone 2 code. It
describes what the code is intended to do. It is not a report of
observed behaviour, because no behaviour has been observed.

> **Naming note (D-048).** The product is now called **Uludağ Formula**; it was
> previously *Apex Formula*. Old-name strings that remain in this document are
> deliberate, not oversights, and fall into two classes:
>
> - **Queued for wave 2** — the module directories `ApexFormulaVehicle/` and
>   `ApexFormulaTests/`, and the automation test namespace `ApexFormula.Vehicle.*`.
>   These name artefacts that still exist under those exact names.
> - **Permanent** — the `AF_` asset/bone prefix and the `UAF*`/`FAF*`/`AAF*`
>   C++ symbol prefixes. These are reclassified as the project's internal code
>   name and will not be renamed.

---

## 1. Verification status

Read this before anything else in this document.

Nothing described here has been compiled. The environment in which
Milestone 2 was written contains no Unreal Engine, no UnrealBuildTool,
no MSVC or clang, and no Blender. Python is the only thing that has
executed.

What has genuinely executed:

| Evidence | What it proves |
| --- | --- |
| `Tools/af_static_validate.py` in CI, Python 3.9 and 3.12 | The tree satisfies the structural rules: module boundaries, include resolution, originality, backend isolation, test shape. |
| `Tools/af_validate_interfaces.py` in CI | Every override's return type agrees with the interface that declares it. |
| `Tools/af_validate_interfaces.py --self-test` in CI | The above checker still detects nine seeded mutations and still ignores four things it must not flag. |
| `python -m compileall Tools` in CI | The tooling parses. |

What has **not** happened, and must not be inferred from the above:

- No C++ has been compiled. `requires local compilation`
- No map has been opened, no Blueprint has been created, no asset has
  been imported. `requires Unreal Editor verification`
- No vehicle has been driven. `requires playtesting`

The Milestone 2 acceptance criteria are behavioural:

1. The vehicle accelerates, brakes and steers.
2. It does not fall through the ground, oscillate, or invert at rest.
3. All engine vehicle access goes through `UAFVehicleCompatibilityLayer`.
4. Imported skeleton bone names match `UAFBoneNameMap`.

Criterion 3 is **structural** and is enforced by
`check_vehicle_backend_isolation` in the static validator, which passes.
Criteria 1, 2 and 4 are **not met** by this work and cannot be assessed
without an engine. The code they will be assessed against exists; the
assessment does not.

---

## 2. What was delivered

| File | State |
| --- | --- |
| `ApexFormulaVehicle/Private/AFVehicleCompatibilityLayer.cpp` | New. The whole backend binding. |
| `ApexFormulaVehicle/Private/AFVehiclePawn.cpp` | Rewritten against the corrected participant contract. |
| `ApexFormulaVehicle/Private/AFPlayerController.cpp` | New. Input to intent. |
| `ApexFormulaVehicle/Public/AFVehiclePawn.h` | Return type corrected (D-035). |
| `ApexFormulaVehicle/Public/AFVehicleCompatibilityLayer.h` | Deferred wheel state added (D-036). |
| `ApexFormulaTests/Private/AFVehicleBackendSetupTests.cpp` | New. Ten tests, never executed. |
| `Tools/af_validate_interfaces.py` | New. Executed, in CI. |

The two module directory names in this table are the current on-disk names.
They are scheduled to become `UludagFormulaVehicle/` and `UludagFormulaTests/`
in wave 2 of D-048, together with the corresponding entries in
`Tools/af_static_validate.py`, in the same commit.

---

## 3. The compatibility layer contract

`UAFVehicleCompatibilityLayer` exists so that exactly one file in the
repository names an engine vehicle type. Every other module talks to
the layer in Uludağ Formula's own vocabulary — metres, kilograms,
newton-metres, `FAFWheelSetup`, `FAFVehicleInputFrame` — and never sees
a Chaos symbol.

This is enforced mechanically, not by convention.
`VEHICLE_BACKEND_ALLOWED_FILES` in `Tools/af_static_validate.py` lists
`AFVehicleCompatibilityLayer.h` and `AFVehicleCompatibilityLayer.cpp`
and nothing else. Any occurrence of `ChaosVehicleMovementComponent`,
`UChaosWheeledVehicleMovementComponent`, `UChaosVehicleWheel`,
`WheeledVehiclePawn`, `ChaosVehicles/` or `ChaosVehicleWheel` in any
other file fails CI.

The layer has three states:

1. **Unbound.** No backend has been supplied. Every mutating call is a
   no-op and every query returns a documented neutral value. Nothing
   asserts and nothing crashes. This is the state exercised by
   `ApexFormula.Vehicle.CompatibilityLayer.UnboundBackendIsInert`.
2. **Bound, parameters pending.** A backend exists but wheel setups
   have not yet been pushed into it. See section 4.
3. **Bound and applied.** Steady state.

The unbound state is deliberate rather than defensive. It lets Race and
UI code hold a layer reference and query it during construction, before
any pawn has possessed anything, without every call site needing a null
check.

### Units at the boundary

This project stores metres. Unreal stores centimetres. The conversion
happens in the layer and nowhere else, through `UAFUnitsHelper`
(`CmPerMetre = 100.0`). A metre value that reaches the engine
unconverted is a hundred-fold error, which is why the conversion is not
open-coded at call sites.

**Every property and method of the Chaos API named in this file is an
unverified assumption.** The UE 5.8 vehicle surface has not been read
from an installed engine — not the module name, not the class names,
not the property names. This is the single largest source of expected
compile errors. `requires local compilation`

---

## 4. Deferred wheel parameters (D-036)

Wheel setups can arrive before the backend does. A designer sets
`FAFWheelSetup` data on the pawn; the movement component may not be
constructed and registered yet. Applying to nothing loses the data
silently, which is the worst of the available failures.

The layer therefore holds `TArray<FAFWheelSetup> PendingWheels` and a
`bool bWheelParametersApplied`, and exposes:

- `TryApplyWheelParameters()` — applies the pending setups if a backend
  is bound. **Idempotent.** Calling it ten times has the same effect as
  calling it once.
- `AreWheelParametersApplied()` — lets callers and tests observe the
  state instead of inferring it.

`TryApplyWheelParameters()` is called after binding and again on
possession. Neither call site needs to know whether the other ran.

Idempotency is a correctness requirement, not a nicety: possession can
happen more than once for a single pawn, and reapplying suspension
parameters mid-simulation would be visible as a physics discontinuity.

---

## 5. The input path

`AAFPlayerController` translates hardware input into
`FAFVehicleInputFrame` and hands it to the pawn. It contains no physics
and no vehicle knowledge.

`FAFVehicleInputFrame` carries `Throttle`, `Brake`, `Steer`, `Clutch`,
the flags `bShiftUp`, `bShiftDown`, `bDeployEnergy`,
`bRequestDragReduction`, and `SessionTime`. Sign convention: **positive
`Steer` is right.** `Sanitise()` clamps every axis before the frame is
consumed, so a misbehaving input device cannot push out-of-range values
into the physics backend.

The Enhanced Input symbols used here are assumptions, as are
`USpringArmComponent::SocketName`, `bEnableCameraRotationLag` and
`CameraRotationLagSpeed` on the camera boom. Each is marked at the
point of use. `requires local compilation`

Whether the resulting control feels correct is a separate question that
no amount of static checking can answer. `requires playtesting`

---

## 6. The participant interface and D-035

`AAFVehiclePawn` implements `IAFRaceParticipant`, which is how Race
code observes a car without depending on the Vehicle module. The
dependency direction matters: Race depends on Core only, never on
Vehicle, and `check_acyclic` enforces it.

The interface declares six pure virtuals, all `const`:

| Method | Returns |
| --- | --- |
| `GetParticipantId()` | `int32` |
| `GetParticipantDisplayName()` | `FString` |
| `GetParticipantLocation()` | `FVector` |
| `GetParticipantForward()` | `FVector` |
| `GetParticipantSpeedKph()` | `double` |
| `IsParticipantActive()` | `bool` |

`AAFVehiclePawn` declared `GetParticipantDisplayName()` returning
`FText`. That is a guaranteed compile failure the moment both
translation units are seen together, and it sat in `main` undetected
because nothing in this repository compiles.

The fix (D-035): the pawn returns `FString`. The stored member
`DriverDisplayName` stays `FText`, because it is user-facing and
localisable, and the accessor returns `DriverDisplayName.ToString()`.
The interface is a data contract for race logic; the member is
presentation. They are allowed to differ, but the conversion must be
explicit and in one place.

The deeper problem was not the typo. It was that no mechanism existed
to catch it. See section 7.

---

## 7. Test and check surface

### Automation tests — written, never executed

`AFVehicleBackendSetupTests.cpp` contains ten tests under
`ApexFormula.Vehicle.*`, all guarded by `WITH_DEV_AUTOMATION_TESTS`:

| Test | Asserts |
| --- | --- |
| `ValidBaselineHasNoProblems` | A well-formed four-wheel setup validates clean. |
| `EmptyWheelArrayIsRejected` | Zero wheels is an error. |
| `NoDrivenWheelIsRejected` | Something must deliver torque. |
| `NoSteeredWheelIsRejected` | Something must steer. |
| `NonPositiveMassIsRejected` | Mass must be positive. |
| `PeakTorqueRpmAboveMaxRpmIsRejected` | The torque peak cannot sit past the rev limit. |
| `ZeroForwardGearsIsRejected` | At least one forward gear. |
| `WheelProblemsAreIndexPrefixed` | Errors name the offending wheel (`"Wheel 2"`). |
| `UnderdampedSuspensionIsRejected` | Damping ratio below 0.5, per M2 criterion A2. |
| `CompatibilityLayer.UnboundBackendIsInert` | An unbound layer is a safe no-op. |

**These have never been run.** `requires local compilation`

The `ApexFormula.Vehicle.*` namespace is a string literal in C++ source. It is
part of wave 2 of D-048 and moves in the same commit as the module rename, not
before.

Note what they cover and what they do not. They test
`FAFVehicleBackendSetup::ValidateSelf()` — that bad configuration is
rejected before it reaches physics. A green run would say the
configuration gate works. It would say nothing whatsoever about whether
the car accelerates, brakes, steers, or stays on the ground. Those are
`requires playtesting`, and no unit test will ever substitute.

The assertions about `ValidateSelf()` message text and about the
accessor names on the layer are themselves assumptions that first
compilation will confirm or refute.

### The interface override checker (D-037)

D-035 revealed a gap. `af_static_validate.py` checks a great deal, but
it had never compared an override against the contract it claims to
implement.

`Tools/af_validate_interfaces.py` does exactly that and nothing else.
It collects the pure virtuals declared by `IAF*` interfaces and
compares the return type of every `override` declaration and every
out-of-line definition against them. It strips comments first —
otherwise the doc comment explaining D-035 would trip the check that
D-035 motivated.

It is not a C++ parser and does not pretend to be. Its one
false-positive shape is an unrelated method sharing a name with an
interface method, accepted deliberately: a false positive costs a
rename, a false negative costs a broken build on someone else's
machine. Its one known blind spot is a pointer return written
`FVector *Class::Method()`, which is caught in the header but not in
the definition. Both are documented in the file itself.

### Why the checker tests itself

A check nobody has seen fail is not a check.

`--self-test` builds throwaway trees, breaks one thing at a time, and
asserts the checker notices exactly the mutations and nothing else.
Nine cases: the exact D-035 shape, a definition-side mismatch, a
narrowed integer (`int32` → `uint8`), a smuggled `const&`, and four
that must **not** fire — whitespace differences, pointer spacing, a
commented-out wrong declaration, and a method belonging to no
interface.

CI runs the self-test **before** running the checker on the tree. The
order is the point: a checker that has stopped detecting its own
mutations must fail the build rather than report a green tree. A green
check from a broken checker is worse than no check at all.

---

## 8. What is still unverified

Complete list, so none of it has to be discovered in the diff.

**Requires local compilation**

- The entire UE 5.8 Chaos Vehicles API surface used by the layer:
  module name, class names, every property and method.
- Enhanced Input symbols in the player controller.
- `USpringArmComponent` properties on the camera boom.
- The exact text of `ValidateSelf()` messages asserted by the tests.
- `NewObject<>(GetTransientPackage())` construction in the tests.
- Accessor names `GetForwardSpeedKph()`, `GetAppliedFrameCount()`,
  `AreAllWheelsGrounded()`.

**Requires Unreal Editor verification**

- That the pawn's components register in the expected order.
- That a Blueprint subclass can set the vehicle definition and wheel
  setups without touching C++.
- That the skeleton imports with bones named `AF_Wheel_FL`,
  `AF_Wheel_FR`, `AF_Wheel_RL`, `AF_Wheel_RR` per D-012 — criterion 4
  is untestable until an asset exists. These bone names are permanent;
  D-048 explicitly does not rename them.

**Requires playtesting**

- Acceleration, braking and steering (criterion 1).
- No fall-through, oscillation or inversion at rest (criterion 2).
- Whether any of it feels like driving a car.

---

## 9. Suggested first steps for whoever compiles this

1. Build the Vehicle module alone. Expect Chaos API errors; they are
   the assumptions in section 3, and they are concentrated in one file
   on purpose.
2. Run `ApexFormula.Vehicle.*` in the automation window. Expect
   failures in message-text assertions before failures in logic.
3. Only then place a pawn in a level and address criteria 1 and 2.

Fixing step 1 should not require touching any file other than
`AFVehicleCompatibilityLayer.cpp`. If it does, the isolation this
milestone is built around has been broken, and CI will say so.
