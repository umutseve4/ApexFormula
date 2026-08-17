# M5.6 — Wheel Spin (Visual) Plan

**Status:** statically authored plan; nothing herein has been executed. Prerequisite: M5.5 drive test (`m56m_drive_test_v2.py`) must PASS first (D-098 currently OPEN).

## Recommended route (skeletal wheels)

Use a Vehicle Animation Blueprint (parent class `VehicleAnimInstance`) with the **Wheel Controller** node feeding Output Pose. This handles roll + steer + suspension for skeletal wheel bones together; manual per-tick rotation of skeletal bones is not the standard route.

## Python automation limit (UE 5.8)

Stock Python API can create an AnimBlueprint asset shell, but has NO verified support for authoring AnimGraph nodes/pins (Wheel Controller wiring). Therefore the AnimGraph step is editor work (~3 clicks); everything else is scripted. Full automation would require a C++ editor extension exposing AnimGraph construction APIs — `UAnimBlueprintFactory` alone only creates the asset, it does not author the graph.

## Cosmetic separate meshes (if any)

Read angle via `ChaosWheeledVehicleMovementComponent.Wheels[i].GetRotationAngle()` — preferred over integrating angular velocity (avoids drift). Note: UE 5.8 docs do not clarify the unit/semantic difference between `GetRotationAngularVelocity` and `GetWheelAngularVelocity`; do not assume RPM conversion without source verification.

## Acceptance criteria (planned)

- Wheels visually rotate proportionally to vehicle speed during an m56m-style scripted drive.
- Front wheels visually steer with input.
- Verification labels: these criteria carry `requires Unreal Editor verification` and `requires visual inspection` until tested; upon PASS they are replaced with `verified in Unreal Editor` plus recorded visual evidence.
