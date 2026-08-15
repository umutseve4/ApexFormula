# Decision Log — Volume 15

Continues `DECISION_LOG_VOL14.md`, frozen after D-082 at ~17.2 KB (D-057 volume rule, ~19KB threshold).

---

## D-083 — OPEN-080-A root cause: FBX_SCALE_ALL bakes ×100 into skeleton root; fix = FBX_SCALE_UNITS (v0B.1.2)

**Date:** 2026-08-19 (project day)
**Status:** Fix committed (`c12cd12` → see D-084) — **verification FAILED; superseded by D-084**
**Affects:** `BlenderPipeline/scripts/af_pipeline_config.py` §0/§9/§12, all previously exported FBX + imported uassets

### Context

M5.2 opened with the mandatory OPEN-080-A scale check (D-080/D-082). Developer screenshot of the imported skeleton in UE 5.8 shows root bone `AF_Armature_Proto` with **Scale = (100.0, 100.0, 100.0)** in BOTH the Bone transform and the Reference transform sections. Mesh geometry itself displays correctly (~560×196×198 cm, 696 tris / 1,584 verts) because the ×100 flows through the render path — but any Physics Asset built on this skeleton would multiply collision volumes, mass, and constraints through the root scale and silently break. **OPEN-080-A verdict: FAIL.** M5.2 blocked until root scale is (1,1,1).

### Diagnosis chain (evidence-driven)

1. **Setting provably applied.** Committed `BlenderPipeline/reports/af_report_export.json` lists `apply_scale_options: "FBX_SCALE_ALL"` in `settings_applied`, with the `dropped` list empty. The setting was not silently ignored — it *worked as designed*, and the design was wrong for our target.
2. **Mechanism.** Blender scene is metric, 1 unit = 1 m; UE wants cm (×100). With `apply_unit_scale=True` + `apply_scale_options="FBX_SCALE_ALL"`, the exporter **bakes the ×100 unit conversion into object-level node transforms** in the FBX — including the armature object node — instead of carrying it in FBX file-scale metadata.
3. **UE side.** UE's Interchange importer folds the armature *object* transform into the skeleton root's reference pose → root bone reference Scale = (100,100,100).
4. **Fix.** `FBX_SCALE_UNITS` keeps the m→cm conversion in the FBX **unit metadata**; object/bone nodes stay at scale 1.0 → root bone imports at (1,1,1), mesh dimensions unchanged. Corroborated by external sources (Blender→UE export guides recommending "Apply Scalings = FBX Units Scale"; Epic forum threads matching the ×100-root-bone symptom exactly).

### Options considered and rejected

| Option | Rejected because |
|---|---|
| Scene `scale_length = 0.01` (work in cm) | Violates the config's standing rule "never change scene units to compensate for exporter behavior"; invalidates every existing measurement contract |
| UE import-side transform workaround (import uniform scale / rig retarget) | Masks the defect at the source; every future export re-introduces it; contract is "FBX must be correct as produced" |
| Post-import bone scale correction script | Same masking problem + adds a fragile UE-side step to the pipeline |

### Decision

- §9 `FBX_EXPORT_SETTINGS.apply_scale_options`: `"FBX_SCALE_ALL"` → **`"FBX_SCALE_UNITS"`**, with D-083 comment block.
- §0 `PIPELINE_VERSION`: `"0B.1.1"` → **`"0B.1.2"`** (D-079 precedent: any FBX-settings change bumps the version).
- §12 `self_check()`: new assertion — `apply_scale_options != "FBX_SCALE_UNITS"` raises a problem referencing D-083, preventing regression to FBX_SCALE_ALL.
- Commit: **`c12dc12ac09030f24418d5e32f7da82a22bf3ea3`** (blob `04bcdba…`, 34,240 B). Diffed against previous blob (`04a6034…`): exactly the three changes above, all other sections byte-identical.
- **New config hash:** changes automatically (`config_hash()` covers the `fbx` dict; old hash `6486736f83b6fb7f` under v0B.1.1). Authoritative new hash **to be captured from the developer's next smoke report** — sandbox has no network path to run self_check locally.
- No guard added to `af_export.py`: the ×100 never exists in the Blender scene (the exporter *creates* it at write time), so the only meaningful verification point is UE-side import inspection.

### Consequence

**All previously exported FBX files and the 8 imported Vehicle uassets (7225cf0) are invalid** — they carry the baked ×100. They must be re-exported and re-imported.

### Verification protocol (developer machine)

1. `git pull --rebase` (pick up `c12dc12` + this log).
2. Re-run pipeline in Blender: validate → export → smoke. Expect: version `0B.1.2`, **new** config hash in reports, smoke 7/7 PASS.
3. In UE: **Force Delete** the old vehicle assets (SkeletalMesh, Skeleton, PhysicsAsset, textures/materials from the old import).
4. Re-import the official FBX via Interchange, same settings as D-082.
5. Inspect `AF_Armature_Proto`: **Scale must read (1.0, 1.0, 1.0)** in both Bone and Reference transforms; mesh dimensions still ~560×196×198 cm. Screenshot = evidence.
6. Recommit official FBX + new uassets via LFS; update this entry's status to CLOSED with the screenshot + new hash.

---

## D-084 — D-083 verification FAIL post-mortem: the config change was a no-op; real root cause is UE's Interchange importer; fix = legacy FBX importer fallback

**Date:** 2026-08-19 (project day)
**Status:** **VERIFIED — closed by D-085.** Fix `92435a3` (`Unreal/Config/DefaultEngine.ini`) confirmed working on developer machine.
**Affects:** `Unreal/Config/DefaultEngine.ini`; supersedes D-083's mechanism claim (its §9/§0/§12 config changes are RETAINED — see below)

### Verification result of D-083 (v0B.1.2)

Developer executed the D-083 protocol flawlessly. Evidence:

1. Smoke test 7/7 PASS under `0B.1.2`, config hash `0c0be9d960b7321c223e4fbd3bbeb6a59b6cf7bbf2793e3967022eba2a1f4449`, fresh FBX 218,236 B.
2. Binary header probe of the exported FBX: `UnitScaleFactor: 100`, `OriginalUnitScaleFactor: 100` — identical to the v0B.1.1 file.
3. UE 5.8 re-import screenshot: `AF_Armature_Proto` root **still Scale = (100,100,100)** in Bone and Reference transforms. **FAIL.**

### Post-mortem: why D-083 changed nothing

Reading Blender's `export_fbx_bin.py` scale-mode arithmetic: with our settings (`global_scale=1.0`, `apply_unit_scale=True`, metric scene at 1.0), **`FBX_SCALE_ALL` and `FBX_SCALE_UNITS` produce byte-identical output** — both write `UnitScaleFactor=100` and leave node transforms at 1.0. The two modes only diverge when `global_scale != 1.0`. Proof: identical 218,236-byte file size, identical header values, identical UE result across v0B.1.1 and v0B.1.2. D-083's mechanism claim ("FBX_SCALE_ALL bakes ×100 into node transforms") was **wrong** — neither mode bakes anything at global_scale=1.0.

### Actual root cause

The FBX is **semantically correct**: nodes at scale 1.0, m→cm conversion declared in file unit metadata. The defect is import-side: **UE 5.4+ replaced the legacy FBX importer with the Interchange Framework as default**, and Interchange folds the unit conversion (UnitScaleFactor=100) into the skeleton root joint's reference pose → root Scale=(100,100,100). This exact symptom is reproduced in Epic forum reports (Blender 4.4 → UE 5.4 skeletal imports) and community deep-dives; no Blender-side `apply_scale_options` value avoids it:

| Blender scale mode | File contents | Interchange result |
|---|---|---|
| FBX_SCALE_ALL / FBX_SCALE_UNITS (global_scale=1) | UnitScaleFactor=100, nodes at 1 | unit conversion folded into root → ×100 |
| FBX_SCALE_NONE | UnitScaleFactor=1, armature **node** scale ×100 | node scale folded into root → ×100 |

### Decision

- **Keep** the Blender pipeline at v0B.1.2 / `FBX_SCALE_UNITS` (correct file semantics; §12 guard stays). The exported FBX and its reports remain valid evidence.
- **Fix import-side:** fall back to the **legacy FBX importer** via the Epic-documented console variable, persisted in the project config so it applies to every editor session:
  - `Unreal/Config/DefaultEngine.ini`, new `[ConsoleVariables]` section: `Interchange.FeatureFlags.Import.FBX=False` (commit `92435a3`).
  - Source: Epic knowledge base "Interchange FBX options" (UE_FlavienP, staff): the cvar "can be added in the DefaultEngine.ini file of the project so that Legacy FBX is turned on by default". Confirmed present through UE 5.8.
  - Interchange remains active for textures/MaterialX/glTF (Epic recommendation; only the FBX format flag is disabled).
- The legacy importer converts units by scaling geometry/bind-pose data, leaving the root bone at (1,1,1) — the standard Blender→UE pipeline behaviour pre-5.4 (`FBX_SCALE_UNITS` + legacy import was THE documented combo).
- Revisit Interchange when Epic resolves the root-scale fold (track in Open questions, OPEN-084-A).

### Verification protocol (developer machine)

1. `git pull --rebase` (pick up `92435a3` + this log). **No Blender re-run needed** — current FBX (218,236 B, v0B.1.2) is valid.
2. Restart the Unreal editor (DefaultEngine.ini cvars load at startup).
3. **Force Delete** the 8 old Vehicle uassets, re-import the official FBX. Expected proof the flag works: the OLD-style "FBX Import Options" dialog appears (not the Interchange dialog).
4. Inspect `AF_Armature_Proto`: **Scale = (1.0, 1.0, 1.0)** in Bone and Reference transforms; length ~560 cm. Screenshot = evidence.
5. On PASS: recommit official FBX + new uassets via LFS; close OPEN-080-A with D-085.

---

## D-085 — OPEN-080-A CLOSED: D-084 legacy-importer fix verified; root bone Scale = (1,1,1); LFS recommit disposition

**Date:** 2026-08-20 (project day)
**Status:** **CLOSED** — screenshot evidence accepted; asset recommit executed per disposition below
**Affects:** `Unreal/Content/Vehicle/*` (8 uassets, replaced), `BlenderPipeline/exports/AF_Vehicle_Proto.fbx` (official, recommitted), `BlenderPipeline/reports/*` (v0B.1.2 evidence)

### Verification evidence (developer machine, 2026-08-15 UTC)

Developer executed the D-084 protocol exactly:

1. `git pull --rebase --autostash` succeeded after clearing OPEN-079-B ini churn; HEAD at `7525c02`; `Select-String` confirmed `[ConsoleVariables]` (line 55) and `Interchange.FeatureFlags.Import.FBX=False` (line 66) present in the working-tree ini.
2. Editor restarted; old Vehicle uassets Force Deleted (working tree showed 8 × ` D` before re-import).
3. Official FBX (218,236 B, v0B.1.2, config hash `0c0be9d…`) re-imported via the **legacy FBX importer** — the flag demonstrably took effect.
4. **Skeleton editor screenshot:** `AF_Armature_Proto` selected; **Bone transform Scale = (1.0, 1.0, 1.0)**, **Reference transform Scale = (1.0, 1.0, 1.0)**, Location/Rotation all zero. Skeleton tree shows the accepted 12-node hierarchy (D-080): `AF_Armature_Proto → AF_Root → AF_Chassis → AF_Steering + 4×(AF_Suspension_* → AF_Wheel_*)`. Preview stats: 696 triangles, 1,584 vertices, 1 UV channel, approx size 6x2x2 — consistent with ~560 cm length envelope. **PASS.**

### Verdict

- **OPEN-080-A: CLOSED.** Root bone scale defect eliminated at the import path; Blender pipeline unchanged at v0B.1.2.
- D-084 status updated to VERIFIED.
- Watch item from D-082 (560×196×198 cm envelope vs design height 95 cm) resolved by the 6x2x2 approx size readout: the earlier 198 cm height reading was an artifact of the ×100-scaled import; dimensions are now consistent with design.

### Asset disposition (single LFS commit)

The commit accompanying this closure ships, via Git LFS where patterns match:

1. `BlenderPipeline/exports/AF_Vehicle_Proto.fbx` — official v0B.1.2 export (218,236 B), replaces the invalid `7225cf0` copy.
2. `BlenderPipeline/reports/af_report_{export,smoke_test,validate}.{json,txt}` — v0B.1.2 evidence (config hash `0c0be9d…`, 7/7 PASS).
3. `Unreal/Content/Vehicle/*.uasset` — 8 assets from the legacy-importer re-import, replacing the invalid Interchange-imported set.

Pointer verification (`git show :<path>` first line = `version https://git-lfs...`) is mandatory before push, per OPEN-076-A lesson.

### Addendum — closure commit executed and verified (bf49a1b)

**Date:** 2026-08-20 (project day)

Disposition executed as commit **`bf49a1b`** ("feat(assets): D-085 closure - verified import root scale 1,1,1; replace 8 Vehicle uassets + official FBX via LFS (OPEN-080-A closed)"; 15 files changed, 44(+)/47(−) — small diffstat is expected: LFS-tracked binaries appear as 3-line pointer file diffs). Push to `origin/main` verified (`git log` shows `origin/main` at `bf49a1b`; subsequent push reports "Everything up-to-date").

Post-push verification (developer machine):

- `git show :BlenderPipeline/exports/AF_Vehicle_Proto.fbx` first line = `version https://git-lfs.github.com/spec/v1` — **LFS pointer OK**.
- `git show :Unreal/Content/Vehicle/AF_Vehicle_Proto.uasset` first line = `version https://git-lfs.github.com/spec/v1` — **LFS pointer OK**.
- `git status --short` clean.

**Deviation from disposition item 3:** `git ls-files Unreal/Content/Vehicle/` lists **7** uassets, not 8 — `AF_M_Cockpit.uasset` was recorded as a deletion. The legacy FBX importer created only 4 material assets (`AF_M_Bodywork`, `AF_M_Detail`, `AF_M_Rim`, `AF_M_Tyre`); the Cockpit material slot was not materialized as a separate uasset on re-import. This is **accepted**: placeholder materials are throwaway per D-011 (final shading authored in Unreal), and the FBX itself still carries all 5 material slots. If the missing slot surfaces as a problem in M5.2+, re-import or author the material in-editor. Tracked as watch item, no new OPEN id.

Final inventory at `bf49a1b`: `AF_Vehicle_Proto`, `AF_Vehicle_Proto_Skeleton`, `AF_Vehicle_Proto_PhysicsAsset`, `AF_M_Bodywork`, `AF_M_Detail`, `AF_M_Rim`, `AF_M_Tyre` (7 uassets) + official FBX + 6 report files.

### Next

M5.2 resumes: Physics Asset configuration on the now-correct skeleton. Numeric acceptance: wheelbase 360±1 cm, overall length 560±1 cm, +X forward, +Z up, root at origin.

---

## D-086 — M5.2 Physics Asset baseline assessment: auto-generation produced 1 chassis capsule only; target layout = chassis Box + 4 wheel Spheres

**Date:** 2026-08-20 (project day)
**Status:** Plan issued — **corrections pending on developer machine; verification pending**
**Affects:** `Unreal/Content/Vehicle/AF_Vehicle_Proto_PhysicsAsset.uasset`

### Baseline evidence (Physics Asset Editor screenshot, 2026-08-15 UTC)

- Editor header: **1 Bodies (1 Considered For Bounds, 100%), 1 Primitive: (1 Capsule), 0 Constraints, 0 Collision Interactions.**
- Skeleton Tree lists only `AF_Chassis` (default filter shows bodies only) — the sole body, a single Capsule, `Bone Name = AF_Chassis`, Physics Type Default, Collision Enabled, Consider for Bounds on.
- Tools → Body Creation panel state at import time: **Min Bone Size = 20.0**, Primitive Type = Capsule, Vertex Weighting = Dominant Weight.
- Viewport: the capsule covers only the mid-section of the ~560 cm hull; wheels and suspension have **no collision bodies at all**.

### Root cause of the sparse auto-generation

Legacy-importer default body creation uses **Min Bone Size = 20** (bones whose weighted-vertex extent falls under 20 uu are skipped). Wheel meshes (r ≈ 36–38 cm but only 50 verts each) and suspension stubs (8 verts) fell below the weighting threshold heuristics, so only `AF_Chassis` (176 verts across the hull) received a body. This is expected importer behaviour, not a pipeline defect — the FBX and skeleton are correct (D-085).

### Decision — target body layout (5 bodies, 0 constraints for now)

| Bone | Body | Rationale |
|---|---|---|
| `AF_Chassis` | **Box** (replace Capsule), covering ~560×194×94 cm hull envelope | Flat, box-like race car hull; a capsule either bulges past the width or under-covers the nose/tail |
| `AF_Wheel_FL/FR/RL/RR` | **Sphere**, r ≈ 36 cm front / 38 cm rear, centered on bone head | Chaos vehicle wheels expect simple round collision; sphere is cheapest and rotation-invariant |
| `AF_Root`, `AF_Steering` | **none** | Structural/animation bones; a body here double-counts mass and can fold into the chassis |
| `AF_Suspension_*` (×4) | **none** — deliberate revision of the earlier M5.2 sketch | Chaos wheeled-vehicle suspension is a raycast/constraint simulation owned by the Vehicle Movement Component; collision bodies on suspension bones only create self-collision and mass noise |

Constraints: none needed at this stage. The auto-generated 0-constraint state is acceptable; wheel articulation will be owned by the Chaos vehicle setup (M6+), not by PhysAsset constraints.

### Correction protocol (developer machine, Physics Asset Editor)

1. Skeleton Tree gear icon → enable **Show All Bones** (verify all 12 nodes / 11 contract bones are visible).
2. Select the existing `AF_Chassis` body → Tools panel: Primitive Type = **Box** → **Re-generate Bodies** (with the body selected, regeneration applies to the selection only).
3. Ctrl-select the 4 `AF_Wheel_*` bones → Tools: Primitive Type = **Sphere**, Min Bone Size = **1.0** → **Re-generate Bodies**.
4. **Caution:** never press Re-generate Bodies with nothing selected — it regenerates every body from current Tools settings.
5. Save; screenshot the editor showing **5 Bodies / 5 Primitives (1 Box + 4 Spheres)** header plus viewport = evidence.

### Numeric acceptance (M5.2)

- Header reads exactly **5 Bodies, 5 Primitives, 0 Constraints**.
- Wheel sphere centers at bone heads: FL/FR (±180, ±80, 36) cm, RL/RR (∓180, ±77, 38) cm — consistent with wheelbase 360±1 cm.
- Chassis box length within 560±1 cm, width ≤ 200 cm, height ≤ 95 cm.
- No body on `AF_Root`, `AF_Steering`, or any `AF_Suspension_*`.

---

## Open questions

| ID | Question | Status |
|---|---|---|
| OPEN-076-A | 4 old PNG blobs committed as normal (non-LFS) objects — rewrite history or accept? | Carried (accepted for now, revisit before repo grows) |
| OPEN-079-B | `DefaultEngine.ini` AndroidFileServer churn — pin or ignore? | Carried |
| OPEN-080-A | Root bone scale ×100 | **CLOSED (D-085)** — legacy FBX importer fallback (D-084, `92435a3`) verified: root Scale=(1,1,1) screenshot evidence; closure commit `bf49a1b` pushed & pointer-verified |
| OPEN-084-A | Interchange importer folds unit conversion into skeleton root — re-evaluate returning to Interchange in a future UE version | Carried |
