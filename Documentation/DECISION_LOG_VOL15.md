# Decision Log — Volume 15

Continues `DECISION_LOG_VOL14.md`, frozen after D-082 at ~17.2 KB (D-057 volume rule, ~19KB threshold).

---

## D-083 — OPEN-080-A root cause: FBX_SCALE_ALL bakes ×100 into skeleton root; fix = FBX_SCALE_UNITS (v0B.1.2)

**Date:** 2026-08-19 (project day)
**Status:** Fix committed (`c12dc12`) — **verification PENDING on developer machine**
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

## Open questions

| ID | Question | Status |
|---|---|---|
| OPEN-076-A | 4 old PNG blobs committed as normal (non-LFS) objects — rewrite history or accept? | Carried (accepted for now, revisit before repo grows) |
| OPEN-079-B | `DefaultEngine.ini` AndroidFileServer churn — pin or ignore? | Carried |
| OPEN-080-A | Root bone scale ×100 | **Fix committed (`c12dc12`, D-083) — UE re-import verification pending** |
