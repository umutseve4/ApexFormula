# Uludağ Formula — Blender → Unreal Pipeline Design

**Document status:** statically authored design document (Milestone 0A). **No Blender script exists yet.** Nothing in this document has been executed. No `.blend` file, no FBX, no GLB and no mesh has been produced. Script names below are the *planned* file names for Milestone 0B.

**Fixed environment:** Blender 5.2 LTS, Unreal Engine 5.8, Windows. Blender Python is used for procedural generation and validation. FBX is the primary skeletal pipeline format; GLB is optional and preview-only.

> **Naming note (D-048).** The product is **Uludağ Formula** (previously *Apex Formula*). Every `af_` script name, every `AF_` object, collection, bone, material and export-file name in this document is **permanent and unchanged**: D-048 reclassified `AF_`/`af_` from "old product name" to the project's **internal code name**. In particular the eleven bone names are asserted directly by `Tools/af_static_validate.py` (the prefix check, the `AF_Root`/`AF_Steering` presence checks and the `bone.startswith("AF_")` loop) and are mirrored in `af_pipeline_config.py`, so they are load-bearing, not leftovers. Only product prose has been renamed in this document.

---

## 1. Blender Project Conventions

### 1.1 Directory layout

```
BlenderPipeline/
  scripts/
    af_pipeline_config.py
    af_scene_setup.py
    af_vehicle_generate.py
    af_vehicle_rig.py
    af_materials.py
    af_export.py
    af_validate.py
    af_smoke_test.py
  source/            # authored .blend files — committed, Git LFS
  generated/         # script output .blend files — reproducible, not hand-edited
  exports/           # FBX / GLB output — Git LFS
  reports/           # JSON validation reports — plain text, committed
  local/             # machine-local, never committed (see .gitignore)
```

**Source vs. generated separation is absolute.** A file under `generated/` or `exports/` may be deleted at any time and reproduced by re-running the scripts. A human must never hand-edit a generated file; if a change is needed, the generator changes.

### 1.2 Script responsibilities

| Script | Responsibility |
| --- | --- |
| `af_pipeline_config.py` | Single source of truth: unit scale, axis convention, bone-name list, collection names, export settings, naming prefixes, tolerance values, vehicle dimension parameters. Contains **no** scene operations. |
| `af_scene_setup.py` | Creates/normalises the scene: unit system, scene scale, collection hierarchy, clears prior generated data. Idempotent. |
| `af_vehicle_generate.py` | Procedural generation of vehicle body, wheels, suspension proxies, collision proxies, LODs. Deterministic given the same config. |
| `af_vehicle_rig.py` | Creates the armature, bones, hierarchy, orientation and mesh binding using names from `af_pipeline_config.py`. |
| `af_materials.py` | Creates material slots and placeholder materials for correct slot ordering on export. Does not attempt final shading. |
| `af_export.py` | Applies transforms, performs the FBX export with the settings in §7, optionally emits a GLB preview. |
| `af_validate.py` | Pre- and post-export validation; writes a JSON report to `reports/`. Never modifies the scene. |
| `af_smoke_test.py` | End-to-end run: setup → generate → rig → materials → validate → export → validate. Returns non-zero on failure. |

Rules: `af_pipeline_config.py` imports nothing from the others. Every other script imports config. No script hardcodes a bone name, a unit, an axis or a path.

### 1.3 Owned collections

The pipeline owns, and may clear, exactly these collections. It must never touch anything else in a `.blend`.

```
AF_Source
AF_Generated
AF_Generated/AF_Body
AF_Generated/AF_Wheels
AF_Generated/AF_Suspension
AF_Generated/AF_Collision
AF_Generated/AF_LOD
AF_Rig
AF_Export
```

Before generation, `af_scene_setup.py` clears `AF_Generated`, `AF_Rig` and `AF_Export` only. Deleting anything outside the `AF_` collection namespace is prohibited. The `AF_` collection namespace is permanent under D-048 and is unaffected by the product rename.

## 2. Unit, Axis and Scale Conventions — Explicit

This section is deliberately explicit. Vague statements such as "convert Z-up to Unreal" are prohibited.

### 2.1 Blender side

- **Unit system:** Metric.
- **Unit scale:** `1.0`.
- **Length unit displayed:** Meters.
- **Interpretation:** 1 Blender unit = 1 metre.
- **World axes:** X = right, Y = forward-into-screen in the default view, **Z = up**.
- **Uludağ Formula authoring convention:** the vehicle is modelled with **+X as the vehicle's forward direction**, **+Z as up**, **+Y as the vehicle's left side**. The vehicle origin sits at the ground plane directly below the chassis reference point, i.e. `Z = 0` is the tyre contact plane at design ride height.
- **Scene scale property** (`scene.unit_settings.scale_length`) is left at `1.0` and is never used to compensate for size errors.

### 2.2 Unreal side

- **Unreal world unit:** 1 Unreal unit = 1 centimetre.
- **Unreal axes:** X = forward, Y = right, **Z = up**.
- **Unreal is left-handed; Blender is right-handed.** The handedness difference manifests as a **Y-axis sign flip** between the two coordinate systems, given both use Z as up.

### 2.3 The conversion, stated precisely

Because this project authors with +X forward and +Z up in Blender, and Unreal uses +X forward and +Z up:

- **No axis re-mapping of the vertical or longitudinal axis is required.** Blender +Z maps to Unreal +Z. Blender +X maps to Unreal +X.
- **The lateral axis is mirrored:** Blender +Y (vehicle left) maps to Unreal −Y; Unreal +Y is the vehicle's right. This is the handedness flip, not an authoring error. It is handled by the FBX exporter's axis settings (§7), **not** by manually rotating objects in the scene and **not** by negative object scale.
- **Scale conversion is ×100.** A vehicle modelled 5.0 Blender units long is 500 Unreal units = 5 metres long. This factor is applied by the FBX export scale setting (§7), so that Blender source data stays in metres and Unreal receives centimetres.
- **The centimetre boundary is the Unreal-facing boundary.** All Uludağ Formula design values quoted to Unreal — wheelbase, track width, ride height, wheel radius, centre-of-mass offset — are quoted in **centimetres** in Data Assets. All values inside Blender scripts are in **metres**. `af_pipeline_config.py` stores metres and exposes a single documented `CM_PER_UNIT = 100.0` constant used only when emitting values intended for Unreal (e.g. in the validation report), so the two representations never drift silently.

### 2.4 Applied transforms

Before export, `af_export.py` must, for every exported object:

- Apply **location, rotation and scale** so that object transforms are identity and all transformation is baked into mesh data. Non-identity object scale on export is a validation error.
- Ensure **no negative scale** anywhere. Negative scale is a validation error, not something to be corrected by the exporter.
- Set object origins deliberately: vehicle body origin at the vehicle origin (§2.1); each wheel origin at its wheel-centre axis point.
- Ensure the **armature object transform is identity** and the armature is at the world origin.

### 2.5 Armature export behaviour

- The armature is exported as the skeleton root. `AF_Root` sits at the world origin with identity transform.
- Bone roll is set deliberately and recorded in the validation report; it is not left to whatever bone creation produced.
- **Leaf/tip bones:** Blender bones have a head and a tail; some FBX paths add an extra leaf bone per chain. The export setting for adding leaf bones is explicitly **disabled** (§7) so the Unreal skeleton bone list matches `af_pipeline_config.py` exactly. A mismatch between the exported bone list and the configured bone list is a validation error.
- The armature is exported together with the deforming meshes in a single FBX so the skeletal binding is preserved.
- Bone names are taken verbatim from `af_pipeline_config.py`. The same list is mirrored in `UAFBoneNameMap` on the Unreal side (`Documentation/TECHNICAL_ARCHITECTURE.md` §5). Both must be changed in the same change set.

**Status of all of §2:** `requires Blender execution` and `requires Unreal Editor verification`. The conventions are internally consistent as written, but no export has been performed and no import has been reviewed.

## 3. Object and Data Naming

All pipeline-produced Blender data uses the `AF_` prefix. All pipeline scripts use the `af_` prefix. Both prefixes are permanent (D-048). The token `F1` is prohibited in every name.

| Data | Pattern | Example |
| --- | --- | --- |
| Vehicle body mesh | `AF_Body_<Variant>` | `AF_Body_Proto` |
| Wheel mesh | `AF_Wheel_<Corner>` | `AF_Wheel_FL` |
| Suspension proxy | `AF_Susp_<Corner>` | `AF_Susp_RR` |
| Collision mesh | `AF_UCX_<Target>_<Index>` | `AF_UCX_Body_01` |
| LOD mesh | `AF_<Base>_LOD<N>` | `AF_Body_Proto_LOD1` |
| Armature object | `AF_Armature_<Variant>` | `AF_Armature_Proto` |
| Bone | `AF_<Part>[_<Corner>]` | `AF_Wheel_FL` |
| Material | `AF_M_<Purpose>` | `AF_M_Bodywork` |
| Export file | `AF_<Subject>_<Variant>.fbx` | `AF_Vehicle_Proto.fbx` |
| Report file | `af_report_<subject>_<timestamp>.json` | `af_report_vehicle_20250101_120000.json` |

Corner codes are exactly `FL`, `FR`, `RL`, `RR`. Mesh datablock names match their object names.

## 4. Validation Rules

`af_validate.py` checks, and reports rather than silently fixes:

**Geometry**
1. No object with non-identity transform at export time.
2. No negative or non-uniform-by-accident scale.
3. No loose vertices, loose edges or zero-area faces.
4. No non-manifold geometry on collision meshes.
5. Face count per object within a configured budget.
6. Consistent normals; no inverted face islands.
7. No n-gons on meshes flagged as deformable.

**UV & materials**
8. At least one UV map on every exported mesh; UV map name matches config.
9. No overlapping UVs on the lightmap-intent channel where one is declared.
10. Material slot count and order match `af_materials.py` expectations.
11. Every material slot is assigned; no empty slots.

**Rig**
12. Every bone in `af_pipeline_config.py` exists in the armature; no extra bones.
13. Bone hierarchy matches the configured parent map.
14. Every deformable vertex has at least one weight; no zero-weight vertices.
15. Weight influences per vertex within the configured maximum.
16. Armature object transform is identity and at world origin.

**Scale & placement**
17. Vehicle bounding box dimensions within configured tolerance of the design dimensions.
18. `Z = 0` is the contact plane at design ride height, within tolerance.
19. Wheel centres at the configured wheelbase/track positions, within tolerance.

**Naming**
20. Every object, mesh, material, bone and file matches the §3 patterns.
21. The token `F1` appears nowhere.

**Reporting.** Every run writes a JSON report to `reports/` containing: script version, config hash, timestamp, per-check pass/fail, measured values against expected values with tolerances, exported file paths and sizes, the full exported bone list, and the bounding box in both metres and centimetres. The report is the pipeline's evidence; a claim not backed by a report line is not a claim. **Reports are plain text and are committed** — they are not binaries.

Exit behaviour: `af_validate.py` returns non-zero on any failed check. `af_smoke_test.py` fails the whole run if validation fails either before or after export.

## 5. Collision Strategy

- Collision is authored in Blender, not generated in Unreal, so it is reproducible and reviewable.
- Convex hull proxies named `AF_UCX_<Target>_<Index>` following Unreal's UCX convention, so the importer recognises them.
- The vehicle body uses a small number of convex pieces (a monocoque hull plus nose, sidepod and rear-structure hulls) rather than one hull, so the silhouette is not grossly over-approximated.
- Wheels use engine-side simple collision from the wheel setup, not authored UCX, because wheel contact is handled by the vehicle system's suspension traces.
- Collision meshes are excluded from rendering, excluded from LOD chains, and must be closed and convex — checked by validation rules 4 and 20.

**Status:** `requires Unreal Editor verification` that the UCX naming is honoured on import in Unreal Engine 5.8.

## 6. LOD Strategy

- LOD0 is the authored/generated full-detail mesh.
- LOD1–LOD3 are generated in Blender by the generator with configured decimation ratios, so the result is deterministic and version-controlled — not left to an importer's automatic reduction.
- LOD meshes carry the same material slot order as LOD0; validation rule 10 covers this.
- **LODs are never used to compensate for weak hardware by lowering the Final Quality target.** LOD ratios belong to the Development Preview profile only when explicitly overridden; the Final Quality LOD chain is authored to look correct at its intended screen sizes. See `Documentation/PROJECT_VISION.md` on the two quality profiles.
- The rig and LOD interaction (whether LODs share the skeletal binding) is `requires Unreal Editor verification`.

## 7. FBX Export Settings

The exact settings `af_export.py` will request. **These are the intended settings; none has been executed or verified.**

| Setting | Value | Reason |
| --- | --- | --- |
| Path mode | Copy, embed textures **off** | Textures are managed in Unreal, not embedded |
| Selected objects only | On | Export exactly the `AF_Export` set |
| Object types | Armature + Mesh only | No cameras, lights or empties |
| Forward axis | `X Forward` | Matches the Uludağ Formula authoring convention (§2.1) and Unreal's +X forward |
| Up axis | `Z Up` | Both Blender and Unreal use Z up |
| Apply scalings | `FBX All` | Bakes scale cleanly; avoids unit-scale surprises downstream |
| Global scale | `1.0` at export, with the metre→centimetre factor carried by the FBX scene unit | Blender stays in metres; Unreal receives centimetres |
| Apply unit scale | On | Ensures the emitted FBX declares its unit correctly rather than relying on the importer guessing |
| Apply modifiers | On | Generated meshes are exported as evaluated |
| Mesh smooth type | Face | Deterministic normals |
| Tangent space | On | Needed for normal-mapped materials later |
| Add leaf bones | **Off** | Prevents phantom bones; keeps the skeleton identical to `af_pipeline_config.py` (§2.5) |
| Primary/secondary bone axis | Set explicitly from config, not left default | Reproducible bone orientation |
| Armature `FBXNode` type | Null | Avoids extra transform nodes |
| Only deform bones | On | Non-deform helper bones are not exported |
| Bake animation | Off | No animation is exported in this pipeline stage |

**Status:** `requires Blender execution` — the exact option names, defaults and behaviour of the Blender 5.2 LTS FBX exporter must be confirmed against the installed version before these are treated as final. Option names are quoted here as intent, not as verified API.

## 8. Optional GLB Path

- GLB is emitted **only** as an optional preview artefact for quick visual checks and interchange.
- GLB is **never** the authoritative skeletal pipeline. Unreal skeletal import uses FBX.
- The GLB export is skipped by default and enabled by a config flag.
- No Uludağ Formula decision, validation rule or acceptance criterion may depend on a GLB.

## 9. Unreal Import Review Checklist

To be performed by a human in the Unreal Editor after the first export. **Nothing on this list has been performed.**

1. Skeleton bone list matches `af_pipeline_config.py` exactly — count, names, order, hierarchy.
2. `AF_Root` is at the origin with identity transform.
3. Imported vehicle dimensions in centimetres match the design values within tolerance.
4. Forward direction is +X; the car faces forward, not sideways or backwards.
5. Up direction is +Z; the car is not on its roof or its side.
6. The car is not mirrored — left/right asymmetric features appear on the correct side (this is the handedness check from §2.3).
7. Scale is not 100× or 0.01× off.
8. Material slot count and order match the Blender source.
9. UCX collision was recognised as collision, not imported as visible geometry.
10. LODs imported into the correct LOD slots.
11. No import warnings about non-uniform scale, degenerate triangles or missing weights.
12. Physics asset generation produced sane bodies (or was correctly suppressed).

Each item's outcome must be recorded. Until then, all twelve are `requires Unreal Editor verification`.

## 10. Material Boundaries

- **Blender creates placeholder materials only** — enough to establish correct slot count, slot order and slot naming for export.
- **Unreal owns final shading**: master materials, material instances, parameter exposure, texture assignment, and all appearance decisions.
- Blender never attempts to author a material intended to survive into final quality. There is no node-graph transfer expectation between the two applications.
- Texture authoring and assignment happen on the Unreal side or in dedicated texturing tools, not in the generator.

## 11. Rig Conventions

- Single armature per vehicle: `AF_Armature_<Variant>`.
- Bone list is exactly the eleven bones defined in `af_pipeline_config.py` and mirrored in `UAFBoneNameMap`:
  `AF_Root`, `AF_Chassis`, `AF_Steering`, `AF_Wheel_FL/FR/RL/RR`, `AF_Suspension_FL/FR/RL/RR`.
- Hierarchy: `AF_Root` → `AF_Chassis` → { `AF_Steering`, `AF_Suspension_*` }; each `AF_Wheel_*` parented to its matching `AF_Suspension_*`.
- These names are **this project's own convention**, not an assumed engine default, and they are **permanent under D-048** — the rename to Uludağ Formula explicitly does not touch them. Whether Unreal Engine 5.8's vehicle setup accepts arbitrary bone names via data-driven mapping is `requires Unreal Editor verification`.
- Bone orientation and roll are set from config, never left implicit.
- The rig is built by script, so it is reproducible; it is never hand-tweaked in `generated/`.

## 12. Reporting Requirements

Every pipeline run produces a JSON report (§4). Beyond per-check results it records:

- Blender version string as reported by the running Blender.
- Script versions and a hash of the effective configuration.
- Full exported bone list, in order, with parents.
- Bounding box in metres and centimetres.
- Wheelbase, track width front/rear, wheel radius, ride height — measured, not assumed — in both units.
- Triangle counts per object and per LOD.
- Material slot listing per object.
- Export file paths, byte sizes and timestamps.
- Overall pass/fail and the list of failed checks.

**The report is the only acceptable evidence that the pipeline ran.** No document, commit message or status update in this project may claim a successful export without a corresponding report file.

## 13. Verification Ledger for This Document

| Claim | Label |
| --- | --- |
| Conventions in this document are internally consistent and non-contradictory | statically inspected |
| Script names match the required `af_` naming set | statically inspected |
| The token `F1` appears in no name in this document | statically inspected |
| The product name "Uludağ Formula" matches none of the prohibited identifier patterns in `af_static_validate.py` | automatically validated |
| The `AF_`/`af_` prefixes are retained deliberately as the internal code name (D-048) | statically inspected |
| Blender 5.2 LTS FBX exporter option names and defaults | requires Blender execution |
| Scripts run without error and produce the described outputs | requires Blender execution |
| Bone list survives export exactly, with no leaf bones added | requires Blender execution, then requires Unreal Editor verification |
| Unit/axis/handedness conversion produces a correctly oriented, correctly scaled, unmirrored car | requires Unreal Editor verification |
| UCX collision recognised on import in UE 5.8 | requires Unreal Editor verification |
| Generated LODs land in the correct LOD slots | requires Unreal Editor verification |
| Vehicle looks correct | requires visual inspection |
