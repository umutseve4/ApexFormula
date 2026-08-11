> Uludağ Formula - original work. Not affiliated with any real motorsport
> series, championship, team, driver or car. All shapes, dimensions and
> names in this document were created for this project.

# Milestone 4 - Procedural Bodywork Surface

Status: **partially delivered, and currently unreproducible**. Not complete.
Read section 0 before reading anything else in this file.

This document follows the honesty rules in the project brief. Every claim
below carries one of the eight verification labels. A claim with no label,
or with a label it has not earned, is a defect in this document.

---

## 0. Provenance banner - read this first

This section was added when the document was landed on `main`. It was not
part of the original text. It is here because the rest of the file would be
misleading without it.

**The module this document describes is not in this repository.**

`BlenderPipeline/scripts/af_bodywork_profile.py` (reported at 1,814 lines /
71,760 B) was written and run on a local machine that no longer exists in
this working environment. It was never pushed. It is not on `main`, not on
branch `milestone-4-bodywork`, and not in `BlenderPipeline/scripts/`, which
contains exactly nine files, none of them this one.

Consequences, stated so that nobody has to infer them:

1. **Every number in sections 4, 5 and 6 is unreproducible here.** The part
   table, the 936 faces / 1,068 vertices, the 5.600 x 1.918 x 0.940 m
   envelope, the seven convex proxies at 0.0 m deviation, and the
   "42 methods, 514 assertions, 0 failures" self-test banner were all
   measured on that lost machine. They are recorded as *history*, not as
   evidence. No one in this repository can re-run them today.
2. **No Milestone 4 acceptance criterion may be counted from this file.**
   Section 7's table describes what *was* observed, not what the repository
   can currently demonstrate. Until the module is re-authored and
   re-measured, Milestone 4's status in `MILESTONE_PLAN.md` stays
   "not started" for criteria purposes.
3. **The self-test source does survive**, on branch `milestone-4-bodywork`
   (head `c94bcade1dd68428c40b6de7fad3ecd0fee9bd01`), as
   `BlenderPipeline/scripts/af_bodywork_selftest.py`, 505 lines. It is
   deliberately **not** merged to `main`, because it imports roughly
   thirty-five symbols from the missing module and would therefore be a
   test that cannot run. It is kept on the branch as a specification of the
   module's public surface, which is genuinely useful when the module is
   re-authored.
4. **Decision D-044, in section 2, remains in force.** It is a design ruling
   about module boundaries and does not depend on the lost bytes.

The alternative to this banner was to reconstruct the module from prose.
That would have produced code that had never been executed, sitting under a
document asserting measurements it had never produced. That is fabricated
evidence, and it is refused. See D-056.

Label for this section: `statically inspected`.

---

## 1. What Milestone 4 asks for

From `MILESTONE_PLAN.md`, verbatim objective:

> Extend the 0B generator to produce a recognisably formula-style, entirely
> original vehicle body with wheels, wings, sidepods and a halo-style
> structure.

Acceptance criteria:

1. Generation is deterministic from config.
2. Validation passes including face budgets, UVs, collision convexity and
   naming.
3. Design is original - not a reproduction of any real car.
4. LOD chain generated in Blender, not by importer auto-reduction.

---

## 2. Decision D-044 - a new module, not a rewrite

**Decision.** The Milestone 4 bodywork is implemented as a new module,
`BlenderPipeline/scripts/af_bodywork_profile.py`, rather than as an in-place
rewrite of `af_vehicle_generate.py`.

**Context.** `af_vehicle_generate.py` produces the 132-polygon box placeholder
that the entire Milestone 0B chain is proven against: the rig binds to it, the
material stage assigns slots on it, the pre-export validator measures it, the
exporter writes it, and the smoke test runs all five stages over it in
sequence. That chain currently reports 19 passed / 0 failed / 1 skipped of 21
checks under `automatically validated`.

**Why not rewrite in place.** Replacing the geometry inside
`af_vehicle_generate.py` in one commit would invalidate all of those proofs
simultaneously. Worse, it would invalidate them *indirectly*: the visible
symptom would be "the smoke test broke", not "the new surface is wrong". The
signal that tells you which of the two happened would be gone at exactly the
moment you need it.

**Consequence.** The new surface is built and gated on its own first, with its
own diagnostic suite, in its own file. Adoption into the exported asset - that
is, pointing the rig, materials and export stages at the new surface and
retiring the box body - is a later and separate step, and it will be its own
decision with its own evidence. Until that step happens, the exported asset is
still the Milestone 0B box body.

**Cost accepted.** For a period, the repository contains two body generators.
That is the price of being able to tell the two failure modes apart.

**Status under D-056.** Still in force as a design ruling. The module it
governs is absent, so the "two body generators" cost has not actually been
incurred: the repository currently contains one.

---

## 3. How the surface is built

The module contains no copied coordinates. There is no lookup table of section
ordinates anywhere in it. Two closed-form shape functions, written for this
project, generate every aerofoil-style section:

```
thickness shape   g(s) = sqrt(s) * (1 - s) * (1 + 0.6 * (1 - s))
camber shape      h(s) = sin(pi * s ** 0.85)
```

where `s` runs 0.0 at the leading edge to 1.0 at the trailing edge. `g` is
normalised once, over a fixed 1001-point reference grid, so that the peak
half-thickness equals the requested value no matter how many points a caller
samples at.

Chassis cross-sections use a superellipse ring with exponent 3.2 - flat-sided
with soft corners, which is what a monocoque section actually looks like.
Sidepods use 2.6.

Every part is then produced by lofting a sequence of rings and capping both
ends, so every part is a closed surface by construction. That is what makes
the manifold and Euler checks below meaningful rather than decorative.

All proportions come from `af_pipeline_config.DESIGN`, which is the single
source of truth for vehicle dimensions (Cross-Milestone Rule 7, D-041). No
dimension is written twice.

Label: was `statically inspected`; **now unverifiable**, because the source
text being described is not present. Retained as a design specification for
the re-authoring work.

---

## 4. Measured results (HISTORICAL - not reproducible in this repository)

Produced by running the module in plain Python 3.12.9 outside Blender on a
machine that is no longer available. These were measurements when they were
taken. They are **not** current evidence. See section 0.

| Part | Verts | Faces | Closed manifold |
| --- | ---: | ---: | --- |
| AF_Surface_Monocoque | 176 | 162 | OK |
| AF_Surface_Nose | 112 | 98 | OK |
| AF_Surface_Cover | 96 | 82 | OK |
| AF_Surface_Sidepod_L | 60 | 50 | OK |
| AF_Surface_Sidepod_R | 60 | 50 | OK |
| AF_Surface_WingFront | 198 | 178 | OK |
| AF_Surface_WingRear | 198 | 178 | OK |
| AF_Surface_EndplateFront_L | 16 | 10 | OK |
| AF_Surface_EndplateFront_R | 16 | 10 | OK |
| AF_Surface_EndplateRear_L | 16 | 10 | OK |
| AF_Surface_EndplateRear_R | 16 | 10 | OK |
| AF_Surface_Halo | 104 | 98 | OK |
| **Total** | **1068** | **936** | **12 of 12** |

Budget, all inside limits:

| Quantity | Measured | Limit |
| --- | ---: | ---: |
| Body faces | 936 | 1600 |
| Body vertices | 1068 | 2400 |
| Largest single part (AF_Surface_WingFront) | 178 | 260 |

Bounding box, against the design envelope:

| Axis | Min (m) | Max (m) | Size (m) | Envelope (m) |
| --- | ---: | ---: | ---: | ---: |
| X | -2.800 | +2.800 | 5.600 | 5.600 |
| Y | -0.959 | +0.959 | 1.918 | 2.000 |
| Z | +0.044 | +0.940 | 0.940 | 0.950 |

Envelope check result: `passed: True`.

Note on width: peak `|y|` is 0.959, marginally outside half the front wing
span (0.950), because the endplate half-thickness of 0.009 sits outboard of
the wing tip. Total width 1.918 m is inside the 2.000 m envelope. This was
intended, not a tolerance escape.

Collision: seven convex proxies, `UCX_AF_Body_Proto_01` through `_07`, each 20
vertices and 12 faces. Largest measured deviation of any vertex outside any
face plane, across all seven: **0.0 m**. All seven had positive signed volume.

Label: **historical measurement, not currently verifiable**. When the module
is re-authored, these numbers are a useful regression target - but they must
be re-measured, never copied forward as if observed.

### 4.1 Why seven proxies when `COLLISION_PIECES` is 5

`af_pipeline_config.COLLISION_PIECES = 5` was set during Milestone 0B, when the
body was a single box and five hulls comfortably wrapped it. The Milestone 4
surface has seven naturally convex regions - monocoque, nose, engine cover,
two sidepods, and the two wing assemblies - and forcing them into five would
require a hull that spans a concave gap, which is exactly the thing convex
collision must not do.

The self-test therefore bounds the proxy count rather than fixing it: at least
5, at most 16 (`BUDGET["collision_pieces_max"]`). `COLLISION_PIECES` is left
untouched because the Milestone 0B export path still reads it and still ships
the box body. Reconciling the two constants belongs to the adoption step
described in D-044, not here.

---

## 5. The diagnostic suite, and what it caught (HISTORICAL)

The module shipped a self-test that ran outside Blender:

```
af_bodywork_profile self test
  methods : 42
  passed  : 514
  failed  : 0
  -> all cases passed
```

That banner is history. The suite source survives on branch
`milestone-4-bodywork` as `af_bodywork_selftest.py`; the module it tests does
not. Nobody can produce this banner today.

The suite checked, per part: closed 2-manifold edges, Euler characteristic
exactly 2, positive signed volume, no degenerate faces, no coincident
vertices. Across the assembly it checked the bounding box against the
envelope, the polygon budget, proxy convexity plane by plane, texture
coordinates inside the unit square with non-zero area, naming, absence of
reserved marks, and determinism by generating twice and comparing coordinates.

This is the part worth reading, because a test suite that never fails is not
evidence of anything. It failed, repeatedly, and each failure was real. These
findings are the most valuable thing the lost module produced, because they
are design knowledge rather than bytes - they will still be true when the
module is re-authored.

**Four geometry defects it caught and forced fixed:**

1. Parts lofted towards negative X, or across positive Y with an X-Z profile,
   came out inside-out - closed and manifold, but with inward-facing normals.
   Caught only by the positive signed volume check. Fixed by reversing the
   ring order before lofting.
2. Front and rear wing endplates initially pushed the bounding box past the
   5.600 m length envelope. Fixed by anchoring endplate centres to the wing
   half-chord rather than to the wing leading edge.
3. The halo apex was computed with a fixed multiplier that ignored the tube
   radius, so the real surface sat above the value the code claimed. Replaced
   with arithmetic that includes tube thickness and clearance; apex became
   exactly 0.940 m.
4. Collision proxies spanning a concave region reported non-zero convexity
   deviation. Fixed by splitting into the seven regions described above.

**Four false assumptions in the tests themselves, corrected:**

1. `section_points(n)` returns `n - 2` points, not `n`. The leading and
   trailing edge samples are shared between the upper and lower surface runs
   and are emitted once, not twice. The test asserted the wrong contract; the
   geometry was right.
2. The sampled peak half-thickness can never exactly equal the requested peak,
   because the thickness function is normalised on a fixed grid while callers
   sample at cosine-spaced stations that do not land on the peak. Measured at
   a requested 0.05: 0.04212 at 6 points, 0.04910 at 12, 0.04995 at 24,
   0.04990 at 40. The equality assertion was replaced with an upper bound, a
   realistic-resolution lower bound, and a convergence check at 400 stations
   (0.05 within 1e-4).
3. Note that the sequence above is **not** monotone - 24 points lands closer
   than 40. Cosine spacing does not approach the peak from one side. A
   monotonicity assertion was written, failed correctly, and was removed as
   unsound rather than papered over.
4. Mirrored parts are lofted independently, so left and right vertices do not
   correspond by index. Sidepod L vertex 0 had `y = +0.6666`; sidepod R vertex
   0 had `y = -0.4734`. Index-by-index mirror error 0.42 m, and yet the parts
   were exact mirrors: the sorted multiset of mirrored positions matched. The
   test was changed to compare position sets, not indices.

The distinction matters. Four of these were bugs in the car. Four were bugs
in the ruler. Both kinds were found by running the thing - which is precisely
why losing the ability to run it costs so much.

Label: **historical measurement, not currently verifiable**.

---

## 6. Level of detail (criterion 4) (HISTORICAL)

`lod_plan(parts)` derived the whole chain as plain data from
`af_pipeline_config.LOD_RATIOS`, which is `(0.60, 0.35, 0.18)`. For twelve
parts and three ratios that is 36 entries, each naming a source object, a
target object `<Part>_LOD1` / `_LOD2` / `_LOD3`, and a ratio. The plan was
validated without Blender: names unique, ratios strictly decreasing, every
ratio inside the open interval (0, 1), coverage exactly equal to the built
part set, and identical across two runs.

`_blender_lod_chain()` then built the reduced copies inside Blender, each
carrying a decimate modifier named by `af_pipeline_config.MODIFIER_DECIMATE`
("AF_Decimate") in COLLAPSE mode at the planned ratio. The modifier was left
unapplied so the export stage bakes it, which keeps the source mesh editable.

The reduction was therefore authored in Blender and never left to
importer-side automatic reduction, which is what criterion 4 requires.

Labels: **historical** for the plan; `requires Blender execution` for the
built meshes, which were never built.

---

## 7. Acceptance criteria - honest status

The table below is the status **as observed on the lost machine**. It is
retained for the re-authoring work. It does **not** license counting any
criterion as met today.

| # | Criterion | Status when last observed | Status in this repository |
| --- | --- | --- | --- |
| 1 | Deterministic from config | Met | Not demonstrable - module absent |
| 2 | Validation passes: budgets, UVs, convexity, naming | Met in the module's own suite | Not demonstrable - module absent |
| 3 | Design is original | Met by construction | Design intent survives in section 3 |
| 4 | LOD chain generated in Blender | Plan met; built meshes unverified | Not demonstrable - module absent |

**Open, and not claimed:**

- The module is absent from the repository. Nothing in it can be run.
- The `bpy` build path in this module was never executed even when the module
  existed. No mesh, no modifier and no collection has actually been created in
  Blender. Label: `requires Blender execution`.
- Nobody has looked at the car. Whether it reads as a formula-style single
  seater, or as an unfortunate wedge, is `requires visual inspection` and no
  assertion in this file can answer it.
- The surface has not been exported, imported, or driven. Nothing has been
  compiled and no lap has been run.
- The module is not adopted by the rig, material, export or smoke test
  stages; those still operate on the Milestone 0B box body.

Under Cross-Milestone Rule 1, Milestone 4 is reported as **not started for
acceptance purposes**, with the design work in sections 2, 3 and 5 carried
forward. It will not be reported as complete until the module exists in this
repository, its self-test runs green in CI, a human runs the Blender path, and
a human looks at the result.

---

## 8. Originality

No section ordinates, dimensions, liveries, names or proportions in this module
are taken from any real car, team or series. The shape functions in section 3
were written for this project. The module additionally asserted, as a test, that
no reserved motorsport mark appears anywhere in its own source text; the check
built those strings by concatenation so the literals never appeared in the file.
That constraint is binding on the re-authored module too.

Label: `statically inspected` for the design described here.
