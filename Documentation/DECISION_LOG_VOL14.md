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

---

## D-080 — OPEN-079-A resolved: the extra `AF_Armature_Proto` root is inherent Interchange behaviour; ACCEPTED as skeleton root; D-078 C-3 criteria amended; C-3 PASS (2026-08-14)

**Re-verification result (D-079 plan executed).** Developer's machine,
same day. Pull → smoke test: 7/7 stages, exit 0, `v0B.1.1`, config hash
`6486736f83b6fb7f`, wheel meshes `AF_WheelMesh_*`, FBX 218,236 bytes.
Force Delete of the previously imported vehicle assets → re-import.

- **Wheel bone defect: FIXED and verified.** Skeleton tree shows
  `AF_Wheel_FL/FR/RL/RR` exactly — no numeric suffixes. The D-079 fix is
  `verified (Unreal Editor)` on the consuming side.
- **Extra root: PERSISTS.** Controlled experiment: re-import performed with
  *Convert Statics in Bone Hierarchy to Skeletals* **OFF** (screenshot of
  the non-default setting captured). `AF_Armature_Proto` still appears as
  the root node above `AF_Root`. The import-setting hypothesis from D-079
  is therefore **eliminated with evidence**.

**Root cause (final).** Blender's FBX exporter always writes the armature
*object* as a node in the FBX scene graph; `armature_nodetype='NULL'`
controls that node's *type*, not its *existence*, and the exporter offers
no option to omit it. UE 5.8 Interchange promotes this container node to a
root bone of the imported skeleton. This is inherent exporter+importer
behaviour, not a defect in this project's scripts or import steps.

**Alternatives considered and rejected.**

1. *Rename the armature object to `AF_Root`* — collides with the existing
   `AF_Root` bone in the flat FBX namespace; the importer would suffix one
   of them. Same defect class D-079 just fixed. Rejected.
2. *Delete the `AF_Root` bone and let the armature act as root* — invasive:
   `BONE_ORDER`, `BONE_PARENTS`, the rig script, both validators, the
   automation tests and the `UAFBoneNameMap` C++ contract all change, for
   zero functional gain. Rejected.
3. *Rely on the legacy importer's special-case handling of an armature
   named literally "Armature"* — unverified under Interchange, breaks the
   `AF_` naming convention, and costs another full import loop. Rejected.

**Decision.** **Accept `AF_Armature_Proto` as the imported skeleton root.**
The D-078 C-3 acceptance criteria are amended as follows:

> Skeleton tree contains **12 nodes**: root `AF_Armature_Proto` (the
> armature container node, accepted per D-080), and beneath it the **11
> contract bones** in exact `BONE_ORDER`, with wheel bones exactly
> `AF_Wheel_FL/FR/RL/RR`.

`UAFBoneNameMap` needs **no change**: it names bones and parent relations;
it does not assert tree depth, and all consuming code looks bones up by
name. Any *future* skeleton-shape validation (M2/M5 C++) must treat
`AF_Armature_Proto` as the accepted root.

**Evidence.** Post-import Skeleton Tree screenshot: 12 nodes,
`AF_Armature_Proto` → `AF_Root` → 10 remaining contract bones in order;
mesh 696 triangles / 1,584 vertices; approx size 560×196×198 cm — matching
the design envelope (5.600 m length) at correct scale.

**Verdict.** **C-3 PASS** under the amended criteria —
`requires Unreal Editor verification` performed, screenshot evidence.
Milestone 2 criterion 4 ("Imported skeleton bone names match
`UAFBoneNameMap`") is now **met**. B-3 sweep closes: C-3 verified;
C-1/C-2 remain deferred to M5 content authoring (D-079).

**New watch item — OPEN-080-A.** An earlier import showed Scale
(100, 100, 100) on the root node in the UE details panel, while mesh
dimensions import correctly (560×196×198 cm). Whether a non-identity
transform sits on `AF_Armature_Proto` must be re-checked when the Physics
Asset is authored in M5; a baked ×100 on the root would distort physics
shape authoring even though the render mesh looks right.

**Status.** OPEN-079-A **CLOSED**. C-3 `verified (Unreal Editor)`.

---

## D-081 — Milestone 5 execution plan; M5.2 DECIDED: skeletal mesh + Physics Asset; LFS verification gate before any binary commit; working-tree disposition (2026-08-14)

**Context.** M1 accepted (D-076/D-077); B-3 sweep closed (D-080): C-3
`verified (Unreal Editor)`, C-1/C-2 blocked until M5 authors content. The
developer's working tree holds untracked artefacts from the D-080 session:
`Unreal/Content/` (the imported vehicle assets), 
`BlenderPipeline/exports/AF_Vehicle_Proto.fbx`, seven
`BlenderPipeline/reports/af_report_*` files, and a new
`Unreal/Config/DefaultEditor.ini`. This decision plans M5 and disposes of
those files. Nothing in this decision is executed yet.

**M5.2 DECIDED — skeletal mesh + Physics Asset (static collision companion
rejected).** Rationale:

1. Chaos Vehicles consumes a `USkeletalMesh`; wheel setup binds to wheel
   *bones*. A static companion mesh cannot feed that path at all.
2. The Physics Asset authors collision bodies per bone — exactly the
   granularity the vehicle needs (chassis body + four wheel bodies).
3. A companion static mesh duplicates geometry that must be regenerated and
   kept in sync with `af_vehicle_generate.py` by hand, and reintroduces the
   flat-FBX-namespace collision class D-079 just eliminated.

**LFS verification gate — OPEN-081-A (blocks every binary commit).**
`.gitattributes` routes `*.uasset`, `*.umap` and `*.fbx` through Git LFS.
OPEN-076-A proves this repository has already committed LFS-pattern files
as normal blobs once. The D-080 session machine currently shows **no LFS
filter activity** (the four acceptance PNGs no longer read "modified"),
consistent with Git LFS being absent or uninitialized in that clone.
Therefore, before ANY `.uasset`/`.umap`/`.fbx` is staged:

1. `git lfs version` must succeed (install Git LFS if not);
2. `git lfs install` must have been run in the clone;
3. after staging the first binary, `git lfs status` must list it as an LFS
   object, and the staged blob must be a pointer (text beginning
   `version https://git-lfs.github.com/spec/v1`), verified with
   `git show :path/to/file | Select-Object -First 3`.

A binary committed while this gate fails is a repeat of OPEN-076-A and
must be reverted before push.

**Working-tree disposition.**

| Path | Decision |
| --- | --- |
| `BlenderPipeline/reports/af_report_*` (7 files) | **Commit now** — plain-text validation evidence; committing reports is standing policy (D-017), which is why `.gitignore` deliberately does not ignore `BlenderPipeline/reports/`. |
| `BlenderPipeline/exports/AF_Vehicle_Proto.fbx` | **Hold behind OPEN-081-A** — `*.fbx` is an LFS pattern. Whether the export FBX is committed at all is decided at M5.1 acceptance; the pipeline can always regenerate it (v0B.1.1, hash `6486736f83b6fb7f`). |
| `Unreal/Content/` | **Hold behind OPEN-081-A + content audit** — must contain ONLY the vehicle assets (skeletal mesh, skeleton, physics asset when authored); no accidental untitled map (D-080 warned against File→Save All). First Content commit happens inside M5, deliberately. |
| `Unreal/Config/DefaultEditor.ini` | **Inspect before deciding** — editor-generated; if it is churn of the OPEN-079-B class, it stays untracked pending that decision; if it carries project-relevant settings, commit as text. |

**M5 execution steps (in order).**

1. **M5.1 — FBX authoritative.** The sole import source is
   `AF_Vehicle_Proto.fbx` produced by pipeline v0B.1.1
   (config hash `6486736f83b6fb7f`). Any regeneration must reproduce that
   hash or record a new decision.
2. **M5.2 — Physics Asset authoring** on the imported skeleton, per the
   decision above. During authoring, execute the **OPEN-080-A check**:
   inspect the `AF_Armature_Proto` node transform in the editor; if a
   non-identity Scale (100,100,100) is present, STOP, record findings, and
   resolve before any collision body is authored.
3. **M5.3 — numeric acceptance.** Measured in-editor, not assumed:
   wheelbase 360 ± 1 cm; overall length 560 ± 1 cm; +X forward; +Z up;
   vehicle not mirrored (verified via an asymmetric marker or bone
   positions, not by eye alone).
4. **M5.4 — `UAFVehicleDefinition` asset** authored in Content;
   `ValidateSelf()` reports clean; all 13 vehicle parts represented;
   material slot order preserved against the pipeline report.
5. **M5.5 — C-1/C-2 unblock.** Author the minimal test map (floor + placed
   `AAFVehiclePawn` wired to the definition asset), then execute M2
   criteria 1–2 (`requires playtesting`): accelerates/brakes/steers; no
   fall-through, oscillation, or inversion at rest.

**Acceptance for this plan.** Each step carries its own verification label
at execution time; no step is reported complete without evidence
(Cross-Milestone Rule 1). M2 closes fully when M5.5 evidence lands.

**Status.** Plan authored (`statically inspected`). Nothing executed.
Next decision id: D-082.

### Open questions in this volume

| ID | Summary | Status |
| --- | --- | --- |
| OPEN-079-A | Extra `AF_Armature_Proto` skeleton root — importer option suspected; exporter-side investigation only if it survives re-import with the option off | **CLOSED by D-080** — inherent Interchange behaviour; root accepted, criteria amended |
| OPEN-079-B | `AndroidFileServer` block auto-injected into `DefaultEngine.ini` by every editor launch — commit or ignore? | OPEN |
| OPEN-076-A | 4 acceptance PNGs tracked by LFS pattern but committed as normal blobs | OPEN (carried) |
| OPEN-080-A | Possible non-identity Scale (100,100,100) on the `AF_Armature_Proto` root node — verify at M5 Physics Asset authoring (D-081 step 2) | OPEN |
| OPEN-081-A | Git LFS not verified functional in the developer clone — gate blocking every `.uasset`/`.umap`/`.fbx` commit until `git lfs install` + pointer verification pass (D-081) | OPEN |
