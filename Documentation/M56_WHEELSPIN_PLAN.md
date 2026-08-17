# M5.6 — Wheel Spin (Visual) Plan

**Status:** statically authored plan; nothing herein has been executed. Prerequisite: M5.5 drive test (`m56m_drive_test_v2.py`) must PASS first — D-098 is still OPEN.

## Recommended route (skeletal wheels)

Use a Vehicle Animation Blueprint whose parent class is `VehicleAnimationInstance` (Python: `unreal.VehicleAnimationInstance`, C++: `UVehicleAnimationInstance`) with the **Wheel Controller** node feeding Output Pose. This node drives roll + steer + suspension for skeletal wheel bones from the Chaos vehicle movement component; manual per-tick rotation of skeletal wheel bones is not the standard route.

## Python automation limit (UE 5.8)

The stock Python API can create an AnimBlueprint asset shell (`AnimBlueprintFactory` with `target_skeleton` and `parent_class` set before `create_asset`), but it has NO verified support for authoring AnimGraph nodes/pins (the Wheel Controller wiring). Full automation would require a C++ editor extension exposing AnimGraph construction APIs.

Shell-creation script `m56w_animbp_shell.py` is statically authored and not executed; it creates/loads a candidate AnimBP shell and attempts a candidate CDO/template `anim_class` assignment; both require Unreal Editor verification. AnimGraph wiring is always manual, and the anim-class assignment may also require manual editor work if the candidate assignment does not persist.

## Cosmetic separate meshes (if any)

Wheel rotation angle is runtime simulation state; no exact UE 5.8 Python call chain for reading it is verified in the Python API reference. Any Python access to a live wheel's rotation angle is a candidate requiring Unreal Editor/API verification. C++/Blueprint expose wheel state via the Chaos vehicle movement component, but no specific accessor or RPM conversion should be assumed without source verification; UE 5.8 documentation does not clarify the unit/semantic difference between `GetRotationAngularVelocity` and `GetWheelAngularVelocity`.

## Acceptance criteria (planned)

- Wheels visibly rotate proportionally to vehicle speed during a drive test.
- Front wheels visibly steer with input.
- No visual detachment of wheels from the chassis.
- Evidence: editor screenshot/video from the drive test after AnimBP wiring.

> Verification labels: these criteria remain `requires Unreal Editor verification` and `requires visual inspection` until tested; a PASS must be recorded as `verified in Unreal Editor` with screenshot/video evidence.
