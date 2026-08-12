# Milestone 4 visual acceptance gate

## 0. What this document is

**Label: planned. Nothing in this document has been executed.**

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
recorded as a decision in `Documentation/DECISION_LOG_VOL6.md`.

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

## 7. Recording the result

Fill this in on the machine that runs the gate. Do not fill it in from
expectation.

| Id | Result | Measured or observed | Notes |
|---|---|---|---|
| G-1.1 | | | |
| G-1.2 | | | |
| G-1.3 | | | |
| G-1.4 | | | |
| G-1.5 | | | |
| G-1.6 | | | |
| G-1.7 | | | |
| G-2.1 | | | |
| G-2.2 | | | |
| G-2.3 | | | |
| G-2.4 | | | |
| G-2.5 | | | |
| G-2.6 | | | |
| G-2.7 | | | |
| G-2.8 | | | |

Run by: _____________  Date: _____________

Blender version as reported by the application: _____________

Screenshot files: _____________

**Definition of done for OPEN-051-F:** every row above carries a result, no
row is blank, the screenshots exist, and a decision entry in
`Documentation/DECISION_LOG_VOL6.md` records the outcome. If every criterion
passes, that decision closes OPEN-051-F and Milestone 4 moves off "not
started for acceptance purposes". If any criterion fails, OPEN-051-F stays
open, the failure becomes its own numbered open question, and Milestone 4
does not move. A partial pass is a fail.

## 8. What this gate still does not cover

It does not cover import into Unreal, material assignment, collision
behaviour in the engine, LOD generation, or anything driven. It judges one
exported mesh, on one screen, once. Nothing here permits any claim about
compilation, import, or gameplay.
