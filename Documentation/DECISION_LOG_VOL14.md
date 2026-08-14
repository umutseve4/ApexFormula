# Decision Log — Volume 14

Continues `DECISION_LOG_VOL13.md`, frozen after D-078 at 15,942 bytes: appending
D-079 (~3.5 KB) would have pushed it past the ~19 KB volume threshold that froze
VOL12 (D-057 volume rule). First decision in this volume: D-079.

---

## D-079 — B-3 first execution: C-1/C-2 blocked by design, smoke test PASS, C-3 FAILED on wheel mesh/bone name collision; fix committed (2026-08-14)

**Context.** The D-078 execution protocol ran for the first time on the
developer's machine (editor open, M1 accepted per D-077).

**C-1 / C-2 — BLOCKED by design, not failed.** The repository contains no
`Unreal/Content/` assets: no map with a floor, no placed `AAFVehiclePawn`,
no `UAFVehicleDefinition` asset. Both playtesting criteria are unexecutable
until M5 authors that content. They stay OPEN and move under the M5 plan
(D-078 §c); no code defect is implied.

**Smoke test — PASS.** Full pipeline on Blender 5.2.0 LTS (Windows):
7/7 stages, exit 0, FBX 218,188 bytes, `bones_exported=11`, config hash
`c9ef9f7e985a1aaf` (v0B.1.0). The producing side of the bone contract was
green immediately before the import attempt — which is exactly what makes
the C-3 result attributable to the FBX/import boundary.

**C-3 — FAIL.** `AF_Vehicle_Proto.fbx` imported into UE 5.8 (Interchange).
Skeleton tree showed **12 nodes instead of 11**, with two defects:

1. **Extra root node `AF_Armature_Proto`** above `AF_Root` — the armature
   *object* name appears as a skeleton node despite
   `armature_nodetype='NULL'`. Suspected import-side cause: the Interchange
   option *Convert Statics in Bone Hierarchy to Skeletals* was enabled.
2. **Wheel bones renamed** `AF_Wheel_FL1/FR1/RL1/RR1`. Root cause is a
   pipeline design bug, not an importer bug: wheel **mesh objects** were
   named identically to wheel **bones** (`AF_Wheel_FL` etc.). The FBX node
   namespace is flat, so the importer deduplicated by renaming the bones —
   breaking the exact-name contract with `UAFBoneNameMap` (Cross-Milestone
   Rule 5). Suspension never collided (mesh `AF_Susp_*` vs bone
   `AF_Suspension_*`); the wheels were the only identical pair.

**Fix (commit `8ff9190`, `af_pipeline_config.py` only).**

- §5 `NAME_WHEEL`: `AF_Wheel_{corner}` → `AF_WheelMesh_{corner}`. Bone
  names are UNCHANGED — the C++ contract (`BONE_ORDER`, `UAFBoneNameMap`,
  vertex-group names) is untouched. All six other pipeline scripts derive
  mesh names from config functions, so the rename propagates with zero
  edits elsewhere.
- §0 `PIPELINE_VERSION`: 0B.1.0 → **0B.1.1**.
- §11 `effective_config()` now includes a `naming` templates dict, so the
  config hash covers the node-name contract. Old hash `c9ef9f7e985a1aaf`
  → new hash `6486736f83b6fb7f`.
- §12 `self_check()` gained a bone-name ∩ object-name collision assertion,
  so this defect class can never re-enter silently.

Functional drift check: reverting the four intended edits in memory
reproduces the old hash exactly — the rewrite changes nothing else.

**Consequence.** Every FBX exported before `8ff9190` is invalid for import
and must be re-exported. Re-verification plan (developer's machine):
pull → smoke test (expect 7/7, v0B.1.1, hash `6486736f83b6fb7f`, wheel
meshes `AF_WheelMesh_*`) → delete the previously imported vehicle assets →
re-import with *Convert Statics in Bone Hierarchy to Skeletals* **OFF** →
Skeleton tree screenshot. PASS = exactly 11 bones, root `AF_Root`, wheel
bones exactly `AF_Wheel_FL/FR/RL/RR`. If the extra armature root persists
with the option off, the exporter side is investigated next
(OPEN-079-A below).

**Also recorded — Windows editor ini churn.** UE 5.8 re-injects an
`AndroidFileServer` settings block into `Unreal/Config/DefaultEngine.ini`
on every editor launch. Until a decision is made whether to commit it,
the developer discards it before pulling
(`git checkout -- Unreal/Config/DefaultEngine.ini`). Tracked as OPEN-079-B.

**Status.** C-3 fix committed, `re-verification pending` on the developer's
machine. C-1/C-2 deferred to M5 content authoring.

### Open questions in this volume

| ID | Summary | Status |
| --- | --- | --- |
| OPEN-079-A | Extra `AF_Armature_Proto` skeleton root — importer option suspected; exporter-side investigation only if it survives re-import with the option off | OPEN |
| OPEN-079-B | `AndroidFileServer` block auto-injected into `DefaultEngine.ini` by every editor launch — commit or ignore? | OPEN |
| OPEN-076-A | 4 acceptance PNGs tracked by LFS pattern but committed as normal blobs | OPEN (carried) |
