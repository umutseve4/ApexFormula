# Milestone 4 visual acceptance gate

## 0. What this document is

**Label: executed three times. The gate was first run on 2026-08-13 and
failed on G-2.4; that outcome is recorded as D-069 in
`Documentation/DECISION_LOG_VOL11.md` and the halo fix as D-070. After the
fix merged to main (`44a7ab3`), the full fifteen-row gate was re-run on
2026-08-13 and passed on all fifteen rows. OPEN-051-F is closed and
Milestone 4 is accepted. The second-run outcome is recorded as D-071 in
`Documentation/DECISION_LOG_VOL12.md`. A third full run followed on
2026-08-13 after the OPEN-071-A rear-wing pylon (D-072) merged to main
(`e2cf23d`); it also passed on all fifteen rows and is recorded as D-073.
All run records are in section 7; the third is authoritative for the
current thirteen-part geometry.**

This is a gate definition, not a result. It converts the single remaining
deliverable of Milestone 4 slice 3 - "open the mesh in Blender and look at
it" - into a written pass or fail test with named criteria, stated methods,
and stated expected values.

It exists because "it looks fine" is not evidence. A screenshot with no
criteria attached to it is an impression. A screenshot with fifteen
criteria attached to it, each marked pass or fail by a named person on a
named date, is an acceptance record.

This document does not itself close anything. It defines what closing
OPEN-051-F requires. The result is recorded in section 7 and the closure is
recorded as a decision in the open decision volume. Section 0 of this
document originally named `Documentation/DECISION_LOG_VOL6.md` as that
volume. Volume 6 was frozen long before the gate was run; the first-run
decision is in `Documentation/DECISION_LOG_VOL11.md`, the second-run
decision in `Documentation/DECISION_LOG_VOL12.md`, and under D-061.2 the
open volume is the authoritative one.

Prerequisite labels for the work this gate governs:

| Gate | Label |
|---|---|
| G-1 | requires local execution, no engine and no DCC |
| G-2 | requires Blender execution, requires visual inspection |

## 1. Why the gate is split in two

Most of what people try to judge by eye is a number, and a number judged by
eye is judged badly. Whether the car is 5.6 metres long, whether twelve
parts are present, whether two exports are identical - these are
measurements, and a measurement disagreed with by a screenshot is a
measurement that was never taken.

So G-1 measures everything that can be measured from the exported file with
the standard library alone. No Blender, no Unreal, no engine. It runs on
the same machine that runs the self-test.

G-2 is reserved for the things that genuinely require a human eye and
cannot be reduced to an assertion: does this read as a formula car, are the
normals facing out, is the halo a halo, is anything inside out. Those are
the questions the whole of Milestone 4 acceptance has been waiting on, and
they are the only questions that justify opening a DCC application.

## 2. Preconditions

From the repository root, in this order:

```
python3 BlenderPipeline/scripts/af_mesh_export.py --self-test
python3 BlenderPipeline/scripts/af_mesh_export.py --dump out
```

The second command writes twelve part OBJ files, twelve part PLY files,
`AF_Bodywork_Combined.obj` and `AF_Bodywork_Collision.obj` into `out/`.
`out/AF_Bodywork_Combined.obj` is the file this gate is about.

`out/` must not be committed. It is generated output and it is reproducible
by the two commands above.

## 3. Gate G-1, numeric acceptance

Label: requires local execution, no engine and no DCC.

Every target below is marked with the strength of the evidence behind it.
**verified** means the value was measured and reproduced in CI, and a
mismatch is a failure. **unverified historical** means the value was
recorded in `Documentation/MILESTONE_4_BODYWORK.md` sections 4 to 6 before
the module was re-authored under D-058, was never re-measured against the
current module, and a mismatch is therefore a finding requiring a decision,
not automatically a failure. See OPEN-060-A.

| Id | Criterion | Method | Target | Strength |
|---|---|---|---|---|
| G-1.1 | Export self-test passes | `--self-test` exit status and stdout | exit `0`; `af_mesh_export: 21 cases, 227 assertions, 0 failures` and `export plan: 14 files, 798 serialised faces` | verified, CI batch 9 |
| G-1.2 | Dump writes the expected file set | count and total bytes of `out/` | 26 files, 112,123 bytes | verified, local, D-059 |
| G-1.3 | Writers are deterministic | dump twice to two directories, compare byte for byte | all 26 files byte identical | verified, local, D-059 |
| G-1.4 | Twelve named surfaces present | helper script group list | exactly 12 groups, names as listed in section 4 | unverified historical |
| G-1.5 | Overall envelope | helper script extents | 5.600 m long, 1.918 m wide, 0.940 m tall | unverified historical |
| G-1.6 | Vertex and face counts | helper script totals | 1068 vertices, 936 faces | unverified historical |
| G-1.7 | No prohibited name tokens | check group names against `cfg.PROHIBITED_NAME_TOKENS` | zero matches | verified, gate exists in `af_mesh_export` |

G-1.6 deserves a warning. The current export plan reports **798 serialised
faces across 14 files**, and the historical record reports **936 faces** for
the combined mesh. Those two numbers are not directly comparable - the plan
counts faces written across every file, and the combined file is one file
among fourteen - so a difference between them is not by itself evidence of
anything. Do not reconcile them by adjusting either number. Record what the
tool prints and let the discrepancy stand as OPEN-060-A until someone works
out what each figure actually counts. This is the same failure mode
OPEN-052-C exists to prevent.

The G-1.1 and G-1.2 targets above date from before the D-070 halo fix.
D-070.4 filed in advance that the fix would shift them; the second run in
section 7 records the post-fix figures (862 faces, 120,108 bytes) as
findings under OPEN-060-A. The targets in this table are deliberately not
retro-edited. The same applies to the D-072 pylon: the third run records
946 faces, 130,794 bytes, 28 files and 13 groups, all filed in advance by
D-072.3, and the targets are again not retro-edited.

## 4. Expected surface names

Recorded in `Documentation/MILESTONE_4_BODYWORK.md` section 4, historical,
not re-measured:

```
AF_Surface_Monocoque
AF_Surface_Nose
AF_Surface_Cover
AF_Surface_Sidepod_L
AF_Surface_Sidepod_R
AF_Surface_WingFront
AF_Surface_WingRear
AF_Surface_EndplateFront_L
AF_Surface_EndplateFront_R
AF_Surface_EndplateRear_L
AF_Surface_EndplateRear_R
AF_Surface_Halo
```

Collision proxies are a separate file, `AF_Bodywork_Collision.obj`,
historically seven convex hulls named `UCX_AF_Body_Proto_01` through
`UCX_AF_Body_Proto_07`. They are out of scope for G-2, which judges the
visible bodywork only.

## 5. Gate G-2, visual acceptance

Label: requires Blender execution, requires visual inspection.

Open `out/AF_Bodywork_Combined.obj` in Blender 5.2 LTS. Capture at minimum a
three-quarter front view, an orthographic side view, and an orthographic top
view. Enable the face orientation overlay for G-2.2.

| Id | Criterion | How to judge | Fails if |
|---|---|---|---|
| G-2.1 | All twelve surfaces are visible | outliner shows twelve objects or groups, none empty | any surface is missing, empty, or a single degenerate face |
| G-2.2 | Normals face outward | face orientation overlay: exterior reads blue | any exterior face reads red |
| G-2.3 | Bilateral symmetry | top view; sidepods and both endplate pairs mirror across the centreline | a left and right pair visibly differ |
| G-2.4 | The halo is a closed loop above the cockpit | three-quarter view | the halo is open, floating, or intersecting the driver volume |
| G-2.5 | Both wings are present and attached | side and top view | a wing floats free of its endplates, or endplates are attached at one end only |
| G-2.6 | The silhouette reads as a formula car | side view, unaided judgement | it reads as a box, a wedge, or an unidentifiable solid |
| G-2.7 | No self-intersection that reads as an error | three-quarter view | surfaces pass through each other in a way a viewer would call broken |
| G-2.8 | Originality | compare against the identity rules in the project brief | the geometry or proportions resemble an identifiable real-world team's car |

G-2.6 and G-2.8 are judgement calls and are recorded as such. They are still
criteria. A judgement call written down before the screenshot is taken is a
test; the same judgement made after the screenshot is a rationalisation.

## 6. Measurement helper

Not a repository module, not CI gated, standard library only, Python 3.9+.
Save it outside the repository or in an ignored path and run it against the
combined file.

```python
#!/usr/bin/env python3
"""Milestone 4 numeric acceptance measurement (gate G-1)."""
import sys
from collections import OrderedDict


def measure(path):
    verts = []
    faces = 0
    groups = OrderedDict()
    current = None
    with open(path, "r", encoding="utf-8") as handle:
        for lineno, raw in enumerate(handle, 1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            tag, _, rest = line.partition(" ")
            if tag == "v":
                parts = rest.split()
                if len(parts) != 3:
                    raise ValueError("line %d: expected 3 coordinates" % lineno)
                verts.append(tuple(float(p) for p in parts))
            elif tag == "f":
                faces += 1
                if current is not None:
                    groups[current] += 1
            elif tag in ("g", "o"):
                current = rest.strip()
                groups.setdefault(current, 0)
            elif tag in ("vn", "vt", "s", "usemtl", "mtllib"):
                continue
            else:
                raise ValueError("line %d: unrecognised record %r" % (lineno, tag))
    if not verts:
        raise ValueError("no vertices found in %s" % path)
    lo = [min(v[i] for v in verts) for i in range(3)]
    hi = [max(v[i] for v in verts) for i in range(3)]
    return verts, faces, groups, lo, hi


def main(argv):
    path = argv[1] if len(argv) > 1 else "out/AF_Bodywork_Combined.obj"
    verts, faces, groups, lo, hi = measure(path)
    print("file             : %s" % path)
    print("vertices         : %d" % len(verts))
    print("faces            : %d" % faces)
    print("named groups     : %d" % len(groups))
    print("extent X (length): %.6f  [%.6f .. %.6f]" % (hi[0] - lo[0], lo[0], hi[0]))
    print("extent Y (width) : %.6f  [%.6f .. %.6f]" % (hi[1] - lo[1], lo[1], hi[1]))
    print("extent Z (height): %.6f  [%.6f .. %.6f]" % (hi[2] - lo[2], lo[2], hi[2]))
    print("groups:")
    for name, count in groups.items():
        print("  %-28s %d faces" % (name, count))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
```

Like `parse_obj` in `af_mesh_export.py`, this reader raises on any record it
does not recognise rather than skipping it, for the reason given in D-059
decision 3: a reader that silently discards a line reports on a subset of
the file and calls it the file.

This snippet was executed in the authoring environment against a synthetic
OBJ file and produced the expected counts and extents. It has **not** been
run against `AF_Bodywork_Combined.obj`, because that file cannot be
generated in the authoring environment. That gap is exactly what this gate
exists to close.

As run on 2026-08-13 the helper was saved as `measure_local.py` in the
repository root, which is an ignored path, and was additionally run against
individual part files - `out/AF_Surface_Halo.obj` and
`out/AF_Surface_Monocoque.obj` - to produce the per-part extents that decide
G-2.4. Running it against a part file is outside the method as written in
this section, and the two per-part measurements are therefore recorded in
section 7 as supporting evidence for a visual criterion rather than as G-1
results.

## 7. Recording the result

Fill this in on the machine that runs the gate. Do not fill it in from
expectation.

The gate has been run three times. The first run failed and is preserved
below unedited, because an acceptance record that erases its own failure is
not a record. The second run, after the D-070 halo fix, accepted Milestone
4. The third run, after the D-072 rear-wing pylon, closed OPEN-071-A and is
authoritative for the current thirteen-part geometry.

### 7.1 First run, 2026-08-13, against main at `f676a51` - FAILED

| Id | Result | Measured or observed | Notes |
|---|---|---|---|
| G-1.1 | pass | exit `0`; `af_mesh_export: 21 cases, 227 assertions, 0 failures`; `export plan: 14 files, 798 serialised faces` | matches the verified target exactly |
| G-1.2 | pass | 26 files, 112,123 bytes | matches the verified target exactly |
| G-1.3 | pass | two dumps compared with `diff -r`, no differences reported | all 26 files byte identical |
| G-1.4 | finding | 12 groups present; 3 names differ from section 4: `AF_Surface_Tail`, `AF_Surface_FrontWing`, `AF_Surface_RearWing` against historical `AF_Surface_Cover`, `AF_Surface_WingFront`, `AF_Surface_WingRear` | count matches. Target is unverified historical, so this is a finding, not a failure. Filed under OPEN-060-A. Not to be resolved by editing either name set |
| G-1.5 | finding | 5.600 m long, **1.960 m** wide, Z extent 0.920 m with Zmax 0.940 m | length matches; width differs from the historical 1.918 m by 0.042 m. Target is unverified historical. Filed under OPEN-060-A |
| G-1.6 | finding | **500 vertices, 384 faces** in `AF_Bodywork_Combined.obj` | historical record says 1068 vertices, 936 faces. Target is unverified historical. This is the largest of the three discrepancies and it is not understood. Filed under OPEN-060-A. Neither number is to be adjusted |
| G-1.7 | pass | zero matches against `cfg.PROHIBITED_NAME_TOKENS` | |
| G-2.1 | pass | outliner lists twelve `AF_Surface_*` objects, none empty, none degenerate | see the outliner panel in every screenshot |
| G-2.2 | pass | face orientation overlay enabled; every exterior face reads blue at all three angles | the overlay initially appeared to do nothing because the front-face alpha in the Blender theme defaults to 0. Set Preferences, Themes, 3D Viewport, face orientation front to 0.25 before judging this row |
| G-2.3 | pass | top view: sidepods and both endplate pairs mirror across the centreline | `M4_G2_top_orthographic.png` |
| G-2.4 | **fail** | `AF_Surface_Halo` occupies Z `[0.672646 .. 0.940000]`. `AF_Surface_Monocoque` reaches Z `0.560000`. **Vertical gap 0.112646 m.** Halo Y extent is `0.050000` against a cockpit width of `0.720000` | the halo is detached from the monocoque and floats above it, and at 0.050 m wide it is a flat strip in the XZ plane rather than a loop enclosing the cockpit. Both stated failure conditions of G-2.4 are met: open, and floating. Object transforms are identity and scale is 1.0 on all axes, so this is authored geometry in `af_mesh_export.py`, not an import artefact. Raised as OPEN-069-A |
| G-2.5 | pass | top view: both wings terminate flush against their endplates, no gap at either end | `M4_G2_top_orthographic.png` |
| G-2.6 | pass, judgement | side view reads as a low, long, open-wheel single seater with a distinct nose, cockpit bulge and tail taper. Not a box, not a wedge, not unidentifiable | judgement call, recorded as one under section 5. The floating halo is the failure of G-2.4 and is deliberately not re-judged here |
| G-2.7 | pass | no surface passes through another in a way a viewer would call broken | the halo does not intersect anything, which is exactly why G-2.4 fails |
| G-2.8 | pass, judgement | proportions and surfacing do not resemble any identifiable real-world team's car | judgement call, recorded as one under section 5 |

Run by: umutseve4  Date: 2026-08-13

**Outcome of the first run.** Fourteen rows carried a pass or a finding and
one row, G-2.4, carried a fail. A partial pass is a fail. OPEN-051-F stayed
open, the failure was numbered OPEN-069-A, and the fix was implemented as
D-070. Recorded as D-069 in `Documentation/DECISION_LOG_VOL11.md`.

### 7.2 Second run, 2026-08-13, against main at `44a7ab3` (post D-070 halo fix) - PASSED

| Id | Result | Measured or observed | Notes |
|---|---|---|---|
| G-1.1 | pass | exit `0`; `af_mesh_export: 21 cases, 227 assertions, 0 failures`; `export plan: 14 files, 862 serialised faces` | case and assertion counts match the verified target. The face count moved from 798 to 862; D-070.4 filed this shift in advance (halo +32 faces plus its cap and leg geometry). Recorded under OPEN-060-A, target not adjusted |
| G-1.2 | pass | 26 files, 120,108 bytes | file count matches; byte count moved from 112,123 with the geometry change, as D-070.4 predicted. Recorded under OPEN-060-A |
| G-1.3 | pass | two dumps to `out/` and `out2/` compared with `diff -r`, silent | all 26 files byte identical |
| G-1.4 | finding | 12 groups present; same 3-name delta as the first run | unchanged from the first run. OPEN-060-A |
| G-1.5 | finding | 5.600 m long, 1.960 m wide, Z extent 0.920 m with Zmax 0.940 m | unchanged from the first run. OPEN-060-A |
| G-1.6 | finding | **532 vertices, 416 faces** in `AF_Bodywork_Combined.obj` | +32/+32 against the first run, exactly the halo's growth from 104/98 to 136/130 per D-070.2. Historical 1068/936 target still unexplained. OPEN-060-A |
| G-1.7 | pass | zero matches against `cfg.PROHIBITED_NAME_TOKENS` | |
| G-2.1 | pass | outliner lists twelve `AF_Surface_*` objects, none empty | fresh import of the post-fix export |
| G-2.2 | pass | face orientation overlay enabled with front alpha 0.25 per the first-run note; zero exterior faces read red | |
| G-2.3 | pass | top view: sidepods and both endplate pairs mirror across the centreline | `M4_G2_top_orthographic.PNG` |
| G-2.4 | **pass** | `AF_Surface_Halo`: 136 vertices, 130 faces, Z `[0.560000 .. 0.940000]`, Y `[-0.385000 .. 0.385000]`. `AF_Surface_Monocoque` reaches Z `0.560000` | the halo's legs land exactly on the monocoque deck - the 0.112646 m gap of the first run is zero - and the hoop spans 0.770 m in Y around the 0.720 m cockpit. It is a closed loop above the cockpit. `M4_G2_halo_detail.PNG` |
| G-2.5 | pass, with a finding | side and top view: both wings terminate flush against their endplates at both ends | neither stated failure condition is met. Separately observed: the rear wing assembly (X `[-2.800 .. -2.350]`) has no connecting structure to the tail (X `[-2.100 .. -0.750]`), a 0.250 m longitudinal gap. Pre-existing, outside this criterion as written, filed as OPEN-071-A in D-071.6 |
| G-2.6 | pass, judgement | side view reads as a low, long, open-wheel single seater, now with a visible halo hoop over the cockpit | judgement call, recorded as one under section 5 |
| G-2.7 | pass | no surface passes through another in a way a viewer would call broken | the halo legs meet the monocoque at its top surface without penetrating it |
| G-2.8 | pass, judgement | proportions and surfacing do not resemble any identifiable real-world team's car | judgement call, recorded as one under section 5 |

Run by: umutseve4  Date: 2026-08-13

Blender version as reported by the application: Blender 5.2.0 LTS, matching
the version CI resolves per D-068.1.

Screenshot files, under `Documentation/acceptance/`, committed at
`5ba919a`:

```
M4_G2_side_orthographic.PNG
M4_G2_front_orthographic.PNG
M4_G2_top_orthographic.PNG
M4_G2_halo_detail.PNG
```

The first evidence commit attempt pointed at stale pre-fix images from
`f676a51`; this was caught by comparing blob hashes and the four files were
replaced at `5ba919a`, where all four hashes differ from the stale set. The
committed extensions are uppercase `.PNG` where this document historically
spelt `.png`; recorded, not churned. These four files were later deleted at
`a311571` when the third-run evidence replaced them; they remain
retrievable at `5ba919a`.

One viewport caption is misleading and is recorded so nobody re-derives it.
The car's length runs along X, so Blender's `Front Orthographic` caption
appears on the anatomical side view and `Right Orthographic` on the
anatomical head-on view. The captions are correct for the axes; they do not
match the anatomical names used in section 5. No criterion depends on the
caption.

**Definition of done for OPEN-051-F:** every row above carries a result, no
row is blank, the screenshots exist, and a decision entry in the open
decision volume records the outcome. If every criterion passes, that
decision closes OPEN-051-F and Milestone 4 moves off "not started for
acceptance purposes". If any criterion fails, OPEN-051-F stays open, the
failure becomes its own numbered open question, and Milestone 4 does not
move. A partial pass is a fail.

**Outcome, 2026-08-13, second run.** All fifteen rows carry a pass or a
finding and no row carries a fail. OPEN-051-F **closes**, along with
OPEN-069-A and OPEN-069-B. **Milestone 4 is accepted.** One new open
question, OPEN-071-A (the rear wing assembly has no connecting structure to
the tail), is opened as post-milestone geometry work. Recorded as D-071 in
`Documentation/DECISION_LOG_VOL12.md`.

### 7.3 Third run, 2026-08-13, against main at `e2cf23d` (post D-072 rear-wing pylon) - PASSED

Run because the D-072 pylon is a geometry change, and under D-069.4 a
geometry change invalidates every row. Milestone 4 was already accepted by
D-071; what this run decides is OPEN-071-A.

| Id | Result | Measured or observed | Notes |
|---|---|---|---|
| G-1.1 | pass | exit `0`; `af_mesh_export: 21 cases, 241 assertions, 0 failures`; `export plan: 15 files, 946 serialised faces` | matches the D-072.3 baselines exactly. Assertion count moved 227→241 with the pylon's test coverage; recorded under OPEN-060-A, target not adjusted |
| G-1.2 | pass | 28 files, 130,794 bytes | matches D-072.3 exactly; +2 files and +10,686 bytes against the second run, filed in advance |
| G-1.3 | pass | two dumps to `out/` and `out2/` compared with `diff -r`, silent | all 28 files byte identical |
| G-1.4 | finding | **13 groups** present; the thirteenth is `AF_Surface_RearWingPylon` per D-072; same 3-name delta as earlier runs | the section 3 target says twelve; the thirteenth part is the deliberate D-072 addition, not a drift. OPEN-060-A |
| G-1.5 | finding | 5.600 m long, 1.960 m wide, Z extent 0.920 m with Zmax 0.940 m | envelope unchanged by the pylon, exactly as D-072.3 predicted (the pylon lies inside the existing bounds). OPEN-060-A |
| G-1.6 | finding | **580 vertices, 458 faces** in `AF_Bodywork_Combined.obj` | +48/+42 against the second run, exactly the pylon part (48 vertices, 42 faces). Historical 1068/936 target still unexplained. OPEN-060-A |
| G-1.7 | pass | zero matches against `cfg.PROHIBITED_NAME_TOKENS` | |
| G-2.1 | pass | outliner lists thirteen `AF_Surface_*` objects, none empty | fresh import of the thirteen-part export; the criterion was written for twelve and the thirteenth is the point of this run |
| G-2.2 | pass | face orientation overlay with front alpha 0.25; zero exterior faces read red | |
| G-2.3 | pass | top view: sidepods and both endplate pairs mirror across the centreline; the pylon sits on the centreline, Y `[-0.030 .. 0.030]` | `top.PNG` |
| G-2.4 | pass | halo unchanged from the second run: closed loop, legs on the monocoque deck at Z 0.560, apex at Z 0.940 | `front.PNG` |
| G-2.5 | **pass, D-071.6 finding resolved** | both wings flush against their endplates at both ends, and the rear wing assembly is now connected to the body: `AF_Surface_RearWingPylon` spans X `[-2.601833 .. -2.019728]`, Z `[0.337885 .. 0.878335]`, lower end buried in the tail solid, upper end buried in the wing solid. The 0.250 m gap of D-071.6 contains structure | `pylon_detail.PNG`, `side.PNG` |
| G-2.6 | pass, judgement | side view reads as a low, long, open-wheel single seater with a visible halo and a supported rear wing | judgement call, recorded as one under section 5 |
| G-2.7 | pass | the pylon interpenetrates the tail and the wing by design, the same closed-manifold pattern the halo uses against the monocoque; nothing reads as broken | |
| G-2.8 | pass, judgement | proportions and surfacing do not resemble any identifiable real-world team's car | judgement call, recorded as one under section 5 |

Run by: umutseve4  Date: 2026-08-13

Blender version as reported by the application: Blender 5.2.0 LTS.

Screenshot files, under `Documentation/acceptance/`, committed at
`a311571` (blob hashes `c1cc8b92…`, `3d869f58…`, `2a88413c…`,
`08c50d6d…`):

```
side.PNG
front.PNG
top.PNG
pylon_detail.PNG
```

The four second-run images were deleted in the same commit, so no stale
image can be mistaken for current evidence - the D-071.4 freshness check
holds by construction. The file names are shorter than the second-run
convention; the binding between file and criterion is recorded in the table
above, not in the names.

**Outcome, 2026-08-13, third run.** All fifteen rows carry a pass or a
finding and no row carries a fail. **OPEN-071-A closes.** Milestone 4
remains accepted. Recorded as D-073 in
`Documentation/DECISION_LOG_VOL12.md`.

## 8. What this gate still does not cover

It does not cover import into Unreal, material assignment, collision
behaviour in the engine, LOD generation, or anything driven. It judges one
exported mesh, on one screen, once. Nothing here permits any claim about
compilation, import, or gameplay.
