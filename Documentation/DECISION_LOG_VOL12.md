# Decision log, volume 12

Volume 11 closed at approximately 18.3 kilobytes with D-070. Under D-057 a
decision volume is frozen as it approaches twenty kilobytes, because every
write from the agent side is a full-file rewrite and an 18 KB retype is an
18 KB opportunity to corrupt a correct record. D-071 is a long entry;
appending it to volume 11 would have pushed that file past the threshold.
Volume 11 is therefore **frozen**. It is not edited again, not to append,
not to correct, not to reformat, and specifically not to change its own
header from "open" to "frozen" - the same treatment volume 11 gave volume
10, and the same condition already recorded as OPEN-065-A.

The tables in this volume are now the authoritative ones (D-061.2). Where
this volume and any earlier volume disagree, this volume is current and the
earlier volume is history. Errata are recorded here; frozen volumes are
never retro-edited.

Next decision id: **D-073**.

---

## D-071 - The Milestone 4 visual gate was re-run and passed on all fifteen rows. Milestone 4 is accepted.

**Status: verified.** The gate defined by D-060 was executed end to end a
second time, in full, after the OPEN-069-A halo fix (D-070) was merged to
main via PR #30 (merge commit `44a7ab330d34a1b9955983dc4bbb2671722e6c31`).
Every row carries a pass or a finding. No row carries a fail.

**Date:** 2026-08-13
**Milestone:** 4, acceptance
**Run by:** umutseve4
**Artefact:** `Documentation/MILESTONE_4_VISUAL_ACCEPTANCE.md` section 7,
second run record
**Evidence commit:** screenshots at `5ba919a` in
`Documentation/acceptance/`
**CI:** none, and none is owed. The gate is by definition manual.

### D-071.1 - The headline

**OPEN-051-F closes. Milestone 4 is accepted.**

The whole gate was re-run, not G-2.4 alone, exactly as D-069.4 required: a
geometry change invalidates every row until every row is re-checked. All
seven G-1 rows were re-measured headlessly on the Codespace against main at
`44a7ab3`, and all eight G-2 rows were re-judged in Blender 5.2.0 LTS
against a freshly exported `AF_Bodywork_Combined.obj`.

Findings are not failures. Under D-060.3, rows whose targets carry the
strength marker "unverified historical" record mismatches as findings under
OPEN-060-A, and three rows do so below, as they did in the first run. A
finding row carries a result and the definition of done is met.

### D-071.2 - G-1 results, measured

| Row | Result | Measured |
|---|---|---|
| G-1.1 | pass | exit `0`; `af_mesh_export: 21 cases, 227 assertions, 0 failures`; `export plan: 14 files, 862 serialised faces` |
| G-1.2 | pass | 26 files, 120,108 bytes |
| G-1.3 | pass | two dumps compared with `diff -r`, silent, all 26 files byte identical |
| G-1.4 | finding | 12 groups; same 3-name delta against the historical set as the first run; OPEN-060-A |
| G-1.5 | finding | 5.600 m long, 1.960 m wide, Z extent 0.920 m, Zmax 0.940 m; width delta +0.042 m against historical; OPEN-060-A |
| G-1.6 | finding | 532 vertices, 416 faces in `AF_Bodywork_Combined.obj`; historical 1068/936; OPEN-060-A |
| G-1.7 | pass | zero matches against `cfg.PROHIBITED_NAME_TOKENS` |

The G-1.1 face count and the G-1.2 byte count both shifted from the first
run (798 to 862 faces; 112,123 to 120,108 bytes). D-070.4 filed these
shifts in advance: the halo gained faces and the files grew. D-070.4
estimated approximately 830 faces and the measured figure is 862; the
32-face difference between the estimate and the measurement is recorded
here under OPEN-060-A with the standing instruction - record the measured
number, adjust nothing, reconcile nothing. The combined mesh likewise
moved from 500/384 to 532/416, which is exactly the +32 vertices and +32
faces the D-070.2 halo rework predicted for the part (104/98 to 136/130).

### D-071.3 - G-2 results, observed

| Row | Result | Observed |
|---|---|---|
| G-2.1 | pass | twelve `AF_Surface_*` objects in the outliner, none empty |
| G-2.2 | pass | face orientation overlay with front alpha 0.25 per the D-069.2 note; zero exterior faces read red at any angle |
| G-2.3 | pass | top view: sidepods and both endplate pairs mirror across the centreline |
| G-2.4 | **pass** | the halo is a closed loop over the cockpit: Y span 0.770 m symmetric about the centreline, legs landing on Z 0.560000 (the monocoque deck), apex at Z 0.940000. Measured per part: `AF_Surface_Halo` 136 vertices, 130 faces, Z `[0.560000 .. 0.940000]`, Y `[-0.385000 .. 0.385000]`. The 0.112646 m gap of D-069.3 is gone and the hoop spans the cockpit |
| G-2.5 | pass, with a finding | both wings terminate flush against their endplates at both ends, which is the criterion as written. Separately: the rear wing assembly as a whole (wing plus both endplates, X `[-2.800 .. -2.350]`) has no connecting structure to the tail (X `[-2.100 .. -0.750]`) - a 0.250 m longitudinal gap with nothing in it. This does not meet either stated failure condition of G-2.5, it pre-existed this run, and it passed the first gate run unremarked. Filed as OPEN-071-A, not a failure of this row |
| G-2.6 | pass, judgement | reads as a low, long, open-wheel single seater |
| G-2.7 | pass | no surface passes through another in a way a viewer would call broken |
| G-2.8 | pass, judgement | no resemblance to an identifiable real-world team's car |

Screenshot evidence, `Documentation/acceptance/` at commit `5ba919a`:
`M4_G2_side_orthographic.PNG`, `M4_G2_front_orthographic.PNG`,
`M4_G2_top_orthographic.PNG`, `M4_G2_halo_detail.PNG`. The committed files
use an uppercase `.PNG` extension where the gate document spells `.png`;
the content is what matters and the names are otherwise exact, so this is
recorded and not churned.

### D-071.4 - A near miss on the evidence, recorded so it is not repeated

The first attempt to satisfy OPEN-069-B pointed at the wrong images. The
four screenshots on main before this run were committed at `f676a51`
(02:49), during the **failed** first run - they depict the pre-fix,
floating halo. Presenting them as pass evidence for the re-run would have
been a record that contradicts itself. The check that caught it was
mechanical: the head of main carried no commit newer than the fix merge,
so no new evidence could exist. The four files were then replaced at
`5ba919a` and all four blob hashes changed
(`57c30373…`, `a3398d45…`, `2c329c99…`, `06834506…` against the stale
`365b162e…`, `afa578ac…`, `4918a889…`, `3c532f91…`), which is the
verification that the replacement actually happened. The lesson is the
same one OPEN-052-C encodes: an evidence pointer is verified by content,
not by filename.

### D-071.5 - What closes

* **OPEN-051-F closes.** Every one of the fifteen rows carries a result,
  no row is blank, no row is a fail, the screenshots exist in the
  repository, and this entry is the decision the gate's definition of done
  requires. Milestone 4 moves off "not started for acceptance purposes"
  and is **accepted**.
* **OPEN-069-A closes.** The halo defect is fixed (D-070), and the
  15-of-15 re-run that D-069.4 made the closure condition has now
  happened.
* **OPEN-069-B closes.** The four screenshots exist under
  `Documentation/acceptance/` at `5ba919a` and were verified by blob hash
  to be the post-fix images.

### D-071.6 - OPEN-071-A is opened

**OPEN-071-A - the rear wing assembly is not structurally connected to the
body.** Measured from the part files: `AF_Surface_RearWing` X
`[-2.800 .. -2.350]`, Z `[0.785 .. 0.855]`; `AF_Surface_EndplateRear_L/R`
X `[-2.800 .. -2.350]`, Z `[0.700 .. 0.940]`; `AF_Surface_Tail` X
`[-2.100 .. -0.750]`, Z `[0.020 .. 0.560]`. The assembly is internally
coherent - the wing is flush with its endplates - but the nearest body
surface ends 0.250 m ahead of it and 0.140 m below it, and no part among
the twelve spans the gap. A real car carries this load through the
endplates to the floor or through a swan-neck pylon to the tail.

Candidate fixes, for whoever picks this up: extend `_tail()` rearward to
X = -2.350 so the endplates land on it, or author a thirteenth surface as
a centreline pylon. Either change re-invalidates the whole gate under the
D-069.4 rule and requires a full fifteen-row re-run before any claim is
made. This is post-Milestone-4 work; it does not reopen OPEN-051-F,
because G-2.5 as written was passed and re-judging a criterion after the
screenshot is the rationalisation section 5 warns against.

### D-071.7 - What is still not true

* No C++ in this repository has ever been compiled.
* `requires local compilation`, `requires Unreal Editor verification` and
  `requires playtesting` are all still unsatisfied.
* `requires visual inspection` is satisfied for this one mesh at
  `44a7ab3` and for nothing else. A geometry change resets it.
* Acceptance of Milestone 4 is acceptance of the mesh pipeline slice, not
  of the vehicle: OPEN-071-A is an open geometry defect, found and filed
  on the same day the milestone closed.

---

## D-072 - A thirteenth part, `AF_Surface_RearWingPylon`, connects the tail to the rear wing. Implemented and locally verified; the gate re-run is owed.

**Status: implemented, locally verified. NOT accepted.** Under the
D-069.4 rule this geometry change invalidates every row of the D-060 gate;
OPEN-071-A stays open until a full fifteen-row re-run passes.

**Date:** 2026-08-13
**Branch:** `fix/open-071-a-rear-wing-pylon`
**Implementation commit:** `707d7f8` (files verified by blob sha:
`af_bodywork_profile.py` `8e427f45a83c8fb8e590b11a812d32907cde2c40`,
`af_bodywork_selftest.py` `3614b4cdd179fc4c38e0539e1fefbfb5248f4025`)
**Patch tooling:** `tools/apply_open071a.py` at `6c7105c`, a self-verifying
script that refuses to touch non-pristine files and checks the resulting
blob shas before reporting success. It was used once to apply the patch on
the Codespace and is kept as the audit trail of exactly what changed.

### D-072.1 - The decision

Of the two candidate fixes D-071.6 filed, the thirteenth-part option is
taken: a single centreline swan-neck pylon, `_rear_wing_pylon()`, swept as
a closed manifold tube and registered in `build_parts()` immediately after
the halo. Extending `_tail()` rearward was rejected because it would
reshape an already-accepted surface and move G-1.5/G-1.6 baselines for a
purely structural need; the pylon adds structure without touching any
existing part, the same pattern the halo already uses (interpenetrating
solids, each an independent closed manifold).

### D-072.2 - The geometry, measured

* Path: six stations in the X/Z plane on the centreline, from
  `(-2.04, 0.36)` inside the tail solid, rising through the engine-cover
  region, to `(tail_x() + rear_wing_chord/2, rear_wing_height)` inside the
  wing solid. Circular section, radius 0.030 m, `_HALO_RING_POINTS`
  vertices per ring, swept with per-station central-difference tangents.
* Part: `AF_Surface_RearWingPylon`, 48 vertices, 42 faces, closed
  manifold. Bounds: X `[-2.601833 .. -2.019728]`,
  Y `[-0.030000 .. 0.030000]`, Z `[0.337885 .. 0.878335]`.
* Both ends are buried: X min sits inside the wing chord and X max inside
  the tail, so the 0.250 m gap of D-071.6 is now spanned by structure.

### D-072.3 - Local verification, all green

Run on the Codespace at `707d7f8` (and independently reproduced in the
agent sandbox before push):

* `af_bodywork_profile core: 22 cases, 72 assertions, 0 failures`
* `af_bodywork_selftest: 42 cases, 394 assertions, 0 failures`
* `af_mesh_export: 21 cases, 241 assertions, 0 failures`
* `export plan: 15 files, 946 serialised faces`
* Dump: `wrote 28 files` twice; `diff -r out out2` silent - byte
  identical, determinism holds. Sandbox-measured dump size: 130,794
  bytes.
* `AF_Bodywork_Combined.obj`: 580 vertices, 458 faces, 13 named groups.
  Envelope unchanged against D-071.2: X 5.600 `[-2.800 .. 2.800]`,
  Y 1.960 `[-0.980 .. 0.980]`, Z `[0.020 .. 0.940]`.
* Baseline deltas against the twelve-part figures, filed here in advance
  of the gate re-run exactly as D-070.4 did: plan 14→15 files, 862→946
  faces (+84); dump 26→28 files, 120,108→130,794 bytes; combined
  532/416→580/458 (+48 vertices, +42 faces - exactly the pylon part).
  The selftest assertion moved from twelve to thirteen parts.

### D-072.4 - What this does not claim

Implemented and locally verified only. Not accepted, not merged to main,
no screenshot judged. The full fifteen-row gate (seven G-1 headless rows,
eight G-2 Blender rows with fresh screenshots) is owed on this geometry
before OPEN-071-A can close, and G-1 measured baselines above will be the
comparison figures for that run.

---

## Open questions, authoritative table

| Id | Subject | Status |
|---|---|---|
| OPEN-051-B | Drift guard banner announces 27 entries; the counterparty count has never been identified | open |
| OPEN-051-F | Milestone 4 visual acceptance, 15 criteria | **closed by D-071.** Second gate run 2026-08-13, fifteen of fifteen rows |
| OPEN-053-A | Local rehearsal gate for `af_mesh_quality.py` | open |
| OPEN-060-A | Historical versus measured mesh figures. D-071.2 adds the second-run actuals: 862 plan faces, 120,108 bytes, 532/416 combined. Neither side is to be adjusted | open, widened |
| OPEN-065-A | Frozen volume headers still read "open": VOL8, VOL10, now VOL11 | open, widened |
| OPEN-065-B | Cross-reference from `VERSION_MATRIX.md` section 5.20 to `SCRIPT_INVENTORY.md` | narrowed to one pointer |
| OPEN-066-A | `af_static_validate.py` has no `--self-test` step in either workflow | open |
| OPEN-066-B | `af_bodywork_selftest.py`, 22,078 bytes, exercised by nothing but `compileall` | open |
| OPEN-068-A | Pin Blender as `BLENDER_VERSION: '5.2.0'` rather than floating on the series | open |
| OPEN-068-B | Bump `actions/checkout` and `actions/upload-artifact` from `@v4` to `@v5` | open |
| OPEN-068-C | Propagate Blender 5.2.0 into `VERSION_MATRIX.md` section 5 | open |
| OPEN-069-A | Halo detached and not a loop | **closed by D-071** |
| OPEN-069-B | G-2 screenshots not committed | **closed by D-071** (commit `5ba919a`) |
| OPEN-071-A | Rear wing assembly floats 0.250 m behind the tail with no connecting structure | **open, fix implemented (D-072).** Pylon on `fix/open-071-a-rear-wing-pylon` at `707d7f8`, locally verified; closes only after the full fifteen-row gate re-run passes on this geometry |

Closed in earlier volumes and not reopened: OPEN-051-A, OPEN-051-C,
OPEN-051-D, OPEN-051-E, OPEN-052-A, OPEN-052-B, OPEN-052-C, OPEN-063-A,
OPEN-064-A, OPEN-066-C, OPEN-067-A, OPEN-M4-01, OPEN-056-A, OPEN-056-B.

**Batching note, carried forward unchanged.** OPEN-066-A, OPEN-066-B,
OPEN-068-B and the deferred D-064.7 work all require editing
`.github/workflows/validate.yml`, a 19,229 byte full retype under D-053.6.
They should be done in a single pass.

---

## Volume status

| Volume | Size | Status |
|---|---|---|
| `DECISION_LOG.md` ... `DECISION_LOG_VOL10.md` | - | frozen |
| `DECISION_LOG_VOL11.md` | ~18.3 KB | frozen at D-070 |
| `DECISION_LOG_VOL12.md` | this file | **open** |
| `CI_EVIDENCE.md` ... `CI_EVIDENCE_VOL6.md` | - | frozen |
| `CI_EVIDENCE_VOL7.md` | 11,984 B | **open** |

Next decision id: **D-073**.
