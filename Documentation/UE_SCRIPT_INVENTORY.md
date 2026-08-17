# UE Editor Script Inventory (BlenderPipeline/tools/)

**Scope:** the `m5x`/vehicle UE-editor Python scripts under `BlenderPipeline/tools/`. Companion to `SCRIPT_INVENTORY.md` (which covers only the `af_*.py` Blender scripts and predates these).

**Honesty rule:** this table records authorship, not execution; execution evidence lives in the decision logs (D-076..D-098) and the project ledger. `statically inspected: no CI workflow references these scripts` (inspected at HEAD `182bc3e`); they require a locally open UE 5.8 editor.

| Script | Purpose | Status label |
|---|---|---|
| `m56s_shrink_chassis.py` | Shrink oversized `AF_Chassis` collision box bottom to +2 cm above wheel centers — **candidate fix** for the suspected airborne-hull cause | delivered at `93fb41f`; `requires Unreal Editor verification` — not yet run |
| `m56m_drive_test_v2.py` | Scripted drive acceptance: settle t=3 s, measure t=12 s; PASS = XY > 300 cm AND speed > 100 cm/s | delivered at `93fb41f`; `requires Unreal Editor verification` — not yet run |
| `m56w_animbp_shell.py` | Create/load a **candidate** Vehicle AnimBP shell (parent `VehicleAnimationInstance`) + attempt **candidate** persistent `anim_class` CDO/template assignment; AnimGraph Wheel Controller wiring is always manual editor work | statically authored; `requires Unreal Editor verification` — not yet run |
| `m54a..m55a` series (35 scripts) | Diagnostic/fix iterations during M5.4–M5.5 (pawn, input, torque, physics asset, bone checks) | authored and superseded where noted in decision logs; per-script execution status: see DECISION_LOG volumes |

**Open item:** after `m56m_drive_test_v2` PASS, record evidence in D-098 and update the MILESTONE_PLAN status table.
