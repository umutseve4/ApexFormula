# Uludağ Formula — Driver Pipeline Design

**Document status:** statically authored design document (Milestone 0A). **No driver geometry exists. No reference photograph has been requested, received, processed or stored. No MetaHuman has been created.** This document defines the intended workflow only.

**Destination:** Unreal Engine 5.8 MetaHuman. **Source-side tooling:** Blender 5.2 LTS.

**Scope note:** driver work begins at Milestone 6 (cockpit driver) and Milestone 7 (MetaHuman integration). Nothing in this document is to be executed during Milestone 0A.

> **Naming note (D-048).** The product is now **Uludağ Formula**; it was previously *Apex Formula*. The `AF_` prefix used throughout this document (`AF_DriverReference`, `AF_DriverHead_*`, and so on) is **not** a leftover of the old name — it is the project's permanent internal code name and is explicitly retained by D-048. Only the product name changes.

---

## 1. Privacy Boundaries — Binding

These rules are constraints on the project, not suggestions.

1. Personal reference photographs are **local input only**. They are never uploaded, never transmitted to any service, never embedded in a document, never packaged into a build, and never committed to Git.
2. Reference photographs live under a single, machine-local directory that is excluded from version control by name:

   ```
   LocalReference/           # excluded in .gitignore, never committed
     Driver/
       Front/
       ThreeQuarter/
       Profile/
       Neutral/
   ```

3. `.gitignore` excludes `LocalReference/` explicitly. A commit containing anything under that path is a process failure and must be rejected, not amended around.
4. Derived intermediate artefacts that still encode facial likeness (projected textures, likeness-baked normal maps, photogrammetry point clouds) are treated with the same restriction and are stored under `LocalReference/` as well.
5. The finished MetaHuman asset in the Unreal project is a **stylised original character**, not a biometric record, and is not represented as an identity document, a biometric template, or a means of identification.
6. No third-party likeness is used. Only the project owner's own reference material may be used, and only locally.
7. No real motorsport driver, team, sponsor or personality is depicted, named or implied.

## 2. Explicitly Prohibited Claims

The following must never be stated in any Uludağ Formula document, commit, comment or status report:

- That camera projection creates real geometry. It does not; it projects colour onto existing geometry.
- That a single photograph provides depth information. It does not.
- That photographs guarantee resemblance. They do not.
- That naming blendshapes after ARKit targets alone produces a valid MetaHuman facial rig. It does not.
- That a custom Blender armature can replace the MetaHuman facial rig. It cannot.
- That image projection output is production-ready texture. It is not; it is a guide.
- That the resulting avatar is a biometric replica of a person. It is not.

Any wording that implies one of these is a defect in the document and must be corrected.

## 3. Reference Material Requirements

*(Requirements are recorded here for Milestone 6. No photographs are being requested now.)*

**Views required**
- Front, level with the eyes, head straight, no tilt.
- Three-quarter left and three-quarter right, roughly 45°.
- Left profile and right profile, roughly 90°.
- Optional: slightly raised and slightly lowered angles to disambiguate brow and jaw.

**Conditions**
- **Neutral expression**: mouth closed and relaxed, eyes open and level, no smile, no brow movement, jaw unclenched.
- **Flat, even lighting**: diffuse, no hard shadow across the face, no strong single-side key, no coloured light. Baked shadows are the main cause of false geometry inference.
- No glasses, no hat, no hair over the face, hair pulled back from the hairline.
- Consistent camera distance and focal length across views; long focal length preferred to reduce perspective distortion.
- Same session, same lighting, same appearance across all views.

**What reference material is for.** Reference photographs guide a human sculpting and adjustment process. They are a visual target. They are not an input to an automatic likeness generator in this pipeline, and no step in this document converts a photograph into geometry automatically.

## 4. Blender-Side Workflow

### 4.1 Reference setup
- Reference images loaded as background/reference planes aligned to the Blender front, side and three-quarter views.
- Alignment is done against a small number of stable landmarks (eye line, base of nose, chin, ear position), accepting that photographs are not orthographic and will never align perfectly.
- Reference planes live in a collection named `AF_DriverReference` and are **never exported**.

### 4.2 Basemesh preparation
- Start from a clean, topology-correct human head/body basemesh, not from a scan.
- Retain edge loops around the eyes and mouth suitable for facial deformation.
- Sculpting is proportion-first: skull mass, jaw width, brow projection, nose length, ear placement — before surface detail.
- All driver meshes use the `AF_` prefix: `AF_DriverHead_<Variant>`, `AF_DriverBody_<Variant>`, `AF_DriverHelmet_<Variant>`, `AF_DriverSuit_<Variant>`.

### 4.3 Cleanup requirements
- Manifold geometry, consistent normals, no loose geometry.
- Symmetry deliberately controlled: a fully symmetric face reads as artificial; asymmetry is introduced intentionally, not left as sculpting noise.
- Scale in metres in Blender, centimetres at the Unreal boundary — identical conventions to `Documentation/BLENDER_PIPELINE_DESIGN.md` §2.
- Axis and export conventions are the same as the vehicle pipeline; the driver is not a special case.

### 4.4 What Blender does *not* do here
- Blender does not build the facial rig for the MetaHuman path.
- Blender does not author final skin shading.
- Blender does not produce hair, eyes or teeth for the MetaHuman path.

## 5. MetaHuman Destination Workflow (UE 5.8)

The intended sequence, with manual checkpoints. **Every step below is `requires Unreal Editor verification`; none has been performed, and the exact UE 5.8 MetaHuman tooling behaviour must be confirmed against the installed version rather than assumed.**

1. **Prepare the Uludağ Formula head mesh** in Blender per §4 and export it under the conventions of `BLENDER_PIPELINE_DESIGN.md`.
   *Checkpoint:* geometry is clean, scaled correctly, and oriented correctly.
2. **Bring the mesh into the MetaHuman authoring workflow in UE 5.8** as the shape target.
   *Checkpoint:* the mesh is accepted and the proportions survive the transfer.
3. **Let the MetaHuman system produce a rigged MetaHuman** from that shape. The facial rig comes from the MetaHuman system — it is never hand-built.
   *Checkpoint:* the rig drives the face; expressions do not tear the mesh.
4. **Adjust proportions inside the MetaHuman authoring tools**, comparing against reference. Iterate here, not by re-sculpting in Blender, once the rig exists.
   *Checkpoint:* front, three-quarter and profile silhouettes read correctly.
5. **Assign hair, eyebrows, eyelashes, eyes and teeth** from the MetaHuman system's own assets and parameters.
   *Checkpoint:* no bald/eyeless placeholder remains; hairline reads correctly against reference.
6. **Assign skin material and tune tone/roughness/subsurface** using MetaHuman skin materials.
   *Checkpoint:* skin does not read as plastic or as flat diffuse under the project's lighting.
7. **Add racing suit, gloves and helmet** as Uludağ Formula original assets. Helmet and suit designs are original; no real team, sponsor or driver livery.
   *Checkpoint:* helmet fits the head shape at cockpit camera distance; no interpenetration in the driving pose.
8. **Import into the Uludağ Formula Unreal project** and place in the cockpit.
   *Checkpoint:* driver scale matches the vehicle cockpit; hands reach the wheel; eyeline matches the cockpit camera.

### 5.1 Responsibility split

| Element | Owner |
| --- | --- |
| Head shape / proportions | Blender sculpt, guided by reference |
| Facial rig | MetaHuman system (UE 5.8) — never hand-built |
| Hair, eyebrows, eyelashes | MetaHuman system assets |
| Eyes, teeth | MetaHuman system assets |
| Skin material | MetaHuman skin material, tuned in Unreal |
| Racing suit, gloves | Uludağ Formula original assets |
| Helmet | Uludağ Formula original asset |
| Cockpit pose, hand placement, steering link | Uludağ Formula Unreal-side setup |
| Body proportions in cockpit | Uludağ Formula Unreal-side setup |

## 6. Quality Tiers

| Tier | Purpose | Requirements | Cost |
| --- | --- | --- | --- |
| **A — Cockpit** | Seen from behind and slightly above, helmet on, visor down, at speed, partially occluded by the halo/roll structure and the cockpit surround. | Correct silhouette, correct scale, correct pose, correct helmet fit, plausible gloves and suit. Face detail is largely invisible. | Low |
| **B — Presentation** | Garage, pre-race, podium, menus. Helmet off or visor up, static or slow camera, moderate distance. | Everything in A, plus a credible face at mid distance, believable hair, working skin material, correct hairline, no uncanny eye placement. | Medium |
| **C — Hero** | Close-up cinematics, replays that hold on the face, marketing shots. | Everything in B, plus fine surface detail, expression range under the facial rig, high-quality hair grooming, eye wetness and subsurface behaviour that survives close inspection. | High |

### 6.1 Recommended first tier — Tier A

**Build Tier A first.** Reasons:

- Tier A is what Milestone 6 actually needs: a driver visible in the cockpit during the first playable and race-test milestones.
- Tier A validates the parts most likely to be wrong and most expensive to fix late — scale, seating pose, hand-to-wheel placement, eyeline versus cockpit camera, helmet fit — none of which requires facial likeness.
- Tier A is a small investment that unblocks Milestones 6, 8, 9 and 11.
- Tier B and C both build on top of the same MetaHuman asset, so nothing done for Tier A is thrown away.
- Investing in facial fidelity before the cockpit integration is proven risks producing a high-quality head that is the wrong scale or in the wrong pose.

Tier B follows when the presentation milestone (11) needs it. Tier C is deferred until there is a concrete cinematic or replay requirement; it is explicitly not a Milestone 6 or 7 goal.

## 7. Validation and Manual Checkpoints

Automatable / statically checkable:
- Mesh manifoldness, normals, loose geometry, scale, orientation — same checks as `af_validate.py` in `BLENDER_PIPELINE_DESIGN.md` §4.
- Naming conventions (`AF_` prefix, no `F1` token).
- Confirmation that no file under `LocalReference/` is staged for commit.
- Confirmation that no reference image is present in the export set or in the packaged build.

Requires human judgement (`requires visual inspection`):
- Whether the face reads as the intended person.
- Whether the hairline is credible.
- Whether the eyes sit correctly in the sockets.
- Whether the skin reads as skin under project lighting.
- Whether the driver looks natural in the cockpit at gameplay camera distance.

Requires the Unreal Editor (`requires Unreal Editor verification`):
- MetaHuman rig behaviour and expression range.
- Skin/hair rendering under the project's lighting and post-process settings.
- Cockpit integration, pose, and hand-to-wheel attachment.
- Performance cost of the driver asset at target frame rate.

Requires playtesting (`requires playtesting`):
- Whether the driver is distracting or reassuring in motion.
- Whether the helmet occludes the cockpit view.

## 8. Fallback Strategies

If likeness work does not converge, the project is not blocked:

1. **Helmeted driver, visor down** — Tier A only, indefinitely. Fully sufficient for all gameplay milestones. This is the default fallback.
2. **Stylised original driver** — an original character not based on any reference photograph. Removes the likeness problem entirely and removes all privacy concerns.
3. **MetaHuman preset with adjusted proportions** — start from a stock MetaHuman rather than a custom sculpt, then adjust. Faster, lower risk, no likeness claim.
4. **Deferred face** — ship gameplay milestones with Tier A and revisit the face at Milestone 11.

**No milestone acceptance criterion depends on facial likeness.** Likeness is an aspiration, not a requirement.

## 9. Automation vs. Artistic Boundary

| Concern | Nature |
| --- | --- |
| Mesh hygiene, scale, orientation, naming, export settings | Automatable — belongs in scripts and validation |
| Reference plane setup | Semi-automatable — placement is scripted, alignment is judged |
| Proportion sculpting | Artistic — not automatable |
| Facial rig | System-owned (MetaHuman) — neither scripted by this project nor hand-built |
| Skin/hair look | Artistic, tuned in Unreal |
| Cockpit pose and attachment | Engineering + artistic, verified in the Editor |
| Likeness judgement | Human only |

Attempting to automate anything in the "artistic" or "human only" rows would produce a confident-looking but wrong result, which is exactly the failure mode this project's honesty rules exist to prevent.

## 10. Milestone Placement

- **Milestone 6 — Cockpit driver pipeline:** Tier A. Basemesh, helmet, suit, gloves, cockpit pose, scale and eyeline verification. No likeness requirement.
- **Milestone 7 — MetaHuman driver integration:** MetaHuman creation, rig, skin, hair; progress toward Tier B. Face becomes visible in presentation contexts.
- **Milestone 11 — Presentation:** Tier B finish quality where garage/podium cameras demand it.
- **Tier C:** unscheduled; requires an explicit cinematic requirement to be justified.

## 11. Verification Ledger for This Document

| Claim | Label |
| --- | --- |
| Privacy rules are stated and `LocalReference/` is excluded in `.gitignore` | statically inspected |
| No reference photograph has been requested, received, stored, processed or committed | statically inspected |
| No driver geometry exists in this repository | statically inspected |
| Prohibited claims (§2) appear nowhere in this document as assertions | statically inspected |
| Naming conventions match `BLENDER_PIPELINE_DESIGN.md` and contain no `F1` token | statically inspected |
| The product name "Uludağ Formula" collides with none of the prohibited identifier patterns in `af_static_validate.py` | automatically validated |
| Blender sculpt/cleanup steps run and produce a clean exportable head | requires Blender execution |
| UE 5.8 MetaHuman tooling accepts the Uludağ Formula head mesh as a shape source | requires Unreal Editor verification |
| MetaHuman facial rig drives the resulting face correctly | requires Unreal Editor verification |
| Driver scale, pose and eyeline are correct in the cockpit | requires Unreal Editor verification |
| Driver asset performance cost at target frame rate | requires Unreal Editor verification |
| The face resembles the intended person | requires visual inspection |
| The driver reads correctly in motion and does not obstruct the view | requires playtesting |
