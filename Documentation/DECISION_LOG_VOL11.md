# Decision log, volume 11

Volume 10 closed at approximately 17.4 kilobytes with D-068. Under D-057 a
decision volume is frozen as it approaches twenty kilobytes, because every
write from the agent side is a full-file rewrite and a 20 KB retype is a
20 KB opportunity to corrupt a correct record. D-069 is a long entry;
appending it to volume 10 would have pushed that file past the threshold and
would have required retyping 17 KB of verified record to add it. Volume 10
is therefore **frozen**. It is not edited again, not to append, not to
correct, not to reformat, and specifically not to change its own header from
"open" to "frozen" - the same treatment volume 10 gave volume 9, and the
same condition already recorded as OPEN-065-A for volume 8.

The tables in this volume are now the authoritative ones (D-061.2). Where
this volume and any earlier volume disagree, this volume is current and the
earlier volume is history. Errata are recorded here; frozen volumes are
never retro-edited.

Next decision id: **D-070**.

---

## D-069 - The Milestone 4 visual gate was run, and it failed on one row

**Status: verified.** The gate defined by D-060 was executed end to end on a
machine with Blender 5.2.0 LTS. Fourteen of fifteen rows carry a pass or a
finding. One row, G-2.4, carries a fail, supported by measured coordinates
rather than by an impression.

**Date:** 2026-08-13
**Milestone:** 4, acceptance
**Run by:** umutseve4
**Artefact:** `Documentation/MILESTONE_4_VISUAL_ACCEPTANCE.md` section 7
**CI:** none, and none is owed. Markdown only, D-054 gate scoped coverage.

### D-069.1 - The headline

**OPEN-051-F stays open. Milestone 4 is not accepted.**

Section 7 of the gate says a partial pass is a fail, and D-060.4 says the
same thing in the decision that created the gate. Fourteen agreeing rows do
not release a hold that has stood through twelve consecutive all-green CI
batches. The hold existed precisely because nobody had looked at the mesh.
Somebody has now looked at the mesh, and the mesh has a defect.

This is the gate working. A gate that only ever returns pass is a
decoration.

### D-069.2 - What passed

G-1.1, G-1.2, G-1.3 and G-1.7 matched their **verified** targets exactly:
the self-test at 21 cases and 227 assertions with an export plan of 14 files
and 798 serialised faces; the dump at 26 files and 112,123 bytes; two
consecutive dumps byte identical under `diff -r`; zero prohibited name
tokens.

This is the first time the 26-file, 112,123-byte determinism figure has been
reproduced anywhere other than the machine that first measured it. D-064.7
and D-067.4 both record that step-level CI logs are unreachable through the
available interface, so this figure had never been independently confirmed.
It now has been, on a second machine. That does not make it a CI-verified
figure, and it is not being upgraded to one.

On the visual side G-2.1, G-2.2, G-2.3, G-2.5 and G-2.7 passed on evidence,
and G-2.6 and G-2.8 passed as the judgement calls section 5 declared them to
be in advance.

G-2.2 is worth a note for whoever runs this next. The face orientation
overlay appeared to do nothing when it was first enabled, and the temptation
at that moment was to record "no red visible" and move on - which would have
been a pass awarded by a broken instrument. The cause was the Blender theme:
the front-face alpha under Preferences, Themes, 3D Viewport, face
orientation defaults to 0, so correct faces are drawn invisibly and only
incorrect ones show. Raising it to 0.25 made the overlay report. The pass is
therefore a real pass, and the near miss is recorded because an overlay that
silently shows nothing is indistinguishable from an overlay that shows
nothing wrong.

### D-069.3 - What failed: G-2.4, the halo

The halo is not a halo. It is a thin arc floating in mid-air above the car.

The measurements, taken with the section 6 helper against the individual
part files:

| Object | Vertices | Faces | Z range | Y extent |
|---|---|---|---|---|
| `AF_Surface_Halo` | 104 | 98 | `[0.672646 .. 0.940000]` | `0.050000` |
| `AF_Surface_Monocoque` | 48 | 38 | `[0.020000 .. 0.560000]` | `0.720000` |

Two independent defects follow from those four numbers.

**It is detached.** The lowest point of the halo sits at Z 0.672646 and the
highest point of the monocoque sits at Z 0.560000. The gap is **0.112646
metres**. There is nothing in between. A halo is a structure bolted to the
survival cell at three points; this one touches the car nowhere.

**It is not a loop.** The halo spans 0.050 m in Y against a cockpit 0.720 m
wide. It is a flat strip lying in the XZ plane, not a ring enclosing the
driver. Even if it were lowered onto the monocoque it would still fail the
criterion as written, because G-2.4 asks for a closed loop above the
cockpit.

Both of the failure conditions G-2.4 states in advance - "open" and
"floating" - are met. This is not a marginal call and it is not being
softened.

**The cause is authored geometry, not import.** The object's transform is
identity on location and rotation and 1.000 on all three scale axes, so
nothing in the Blender scene moved it. The OBJ import was performed with
Up = Z and Forward = Y, which is correct for this pipeline; the same import
placed every other part correctly, and eleven other parts do not have a
0.112 m hole under them. The defect is in the numbers `af_mesh_export.py`
writes.

### D-069.4 - OPEN-069-A is opened

**OPEN-069-A - `AF_Surface_Halo` is authored detached from the monocoque and
is not a closed loop.** The arc's base sits 0.112646 m above the monocoque's
highest point and its Y extent is 0.050 m against a 0.720 m cockpit. The fix
is in the halo geometry in `af_mesh_export.py` and its upstream in
`af_bodywork_profile.py`: the legs must reach the monocoque deck, and the
hoop must span the cockpit rather than lie in the centreline plane.

This is the numbered open question that section 7 requires the failure to
become. It is a defect in the mesh, not a documentation discrepancy, and it
is the only thing now standing between Milestone 4 and a re-run of the gate.

When it is fixed, the **whole** gate is re-run. Not G-2.4 alone. A change to
the geometry module invalidates the self-test counts, the file sizes, the
determinism check and every visual row, and re-running one row would be
asserting that a geometry change is local without having checked.

### D-069.5 - OPEN-069-B is opened

**OPEN-069-B - the four G-2 screenshots are named in section 7 but not yet
committed.** The authoring environment writes text through a file-contents
API and cannot commit binary content, so `Documentation/acceptance/` does not
yet contain the images that section 7 points at. Until Umut commits them,
the evidence pointer is dangling.

This is recorded rather than glossed because section 7's definition of done
says "the screenshots exist", and a document that claims screenshots exist
while they do not is exactly the kind of quiet untruth OPEN-052-C exists to
prevent. The gate result does not depend on the files being in the
repository - the images were examined, and the decisive G-2.4 evidence is
numeric and reproducible from `out/` - but the record is incomplete without
them.

Required filenames, under `Documentation/acceptance/`:
`M4_G2_side_orthographic.png`, `M4_G2_front_orthographic.png`,
`M4_G2_top_orthographic.png`, `M4_G2_halo_detail.png`.

### D-069.6 - The three G-1 findings feed OPEN-060-A, and none of them is a failure

G-1.4, G-1.5 and G-1.6 each disagree with `MILESTONE_4_BODYWORK.md`. Every
one of those targets carries the strength marker **unverified historical**,
so under D-060.3 a mismatch is a finding requiring a decision, not a
failure. The gate was written that way before the numbers were known, which
is the only reason this paragraph can be trusted.

| Row | Historical | Measured | Delta |
|---|---|---|---|
| G-1.4 | `AF_Surface_Cover`, `AF_Surface_WingFront`, `AF_Surface_WingRear` | `AF_Surface_Tail`, `AF_Surface_FrontWing`, `AF_Surface_RearWing` | 3 of 12 names; count correct |
| G-1.5 | 5.600 x 1.918 x 0.940 m | 5.600 m long, 1.960 m wide, Z extent 0.920 m, Zmax 0.940 m | width +0.042 m |
| G-1.6 | 1068 vertices, 936 faces | 500 vertices, 384 faces | -568 vertices, -552 faces |

G-1.6 is the one that should not be waved through. The current mesh has
fewer than half the vertices the historical record claims. That is not a
rounding difference or a naming convention; it is a different mesh. The
honest position is that nobody knows which figure describes what, because
the historical numbers predate the D-058 re-authoring and were never
re-measured. All three findings are filed under **OPEN-060-A**, which
already holds the 936-versus-798 face discrepancy and already carries the
instruction that neither number is to be adjusted. That instruction stands
and is extended to these three rows.

Note also that the Z extent, 0.920 m, is smaller than Zmax, 0.940 m, because
the lowest geometry sits at Z 0.020 rather than at zero. The historical
0.940 figure is a height above the ground plane; the measured 0.920 is an
extent. They are not the same measurement, and the gate asked for the
second while the historical record supplied the first.

### D-069.7 - Section 0 of the gate named a frozen volume

`MILESTONE_4_VISUAL_ACCEPTANCE.md` section 0 and its definition of done both
directed the outcome to `Documentation/DECISION_LOG_VOL6.md`. That was
correct when D-060 was written on 2026-08-12 and volume 6 was open. Volumes
7 through 10 were opened and frozen in the interval, so following the
instruction literally would have appended a decision to a frozen volume and
numbered it out of sequence.

Under D-061.2 the open volume is authoritative, and the outcome therefore
lives here as D-069. The gate document has been updated in the same commit
to point at the open volume rather than at a specific frozen filename, since
a pointer to a named volume in a document that outlives that volume will
fail the same way again.

This is a small instance of a general defect: a cross-reference to a
rotating file is a dated cross-reference, and it ages without any signal
that it has aged.

### D-069.8 - What is still not true

Restated, because this entry closes nothing and it would be easy to read a
fourteen-of-fifteen result as progress toward acceptance rather than as a
fail:

* No C++ in this repository has ever been compiled.
* A generated mesh **has** now been seen by a human being. That sentence has
  been false in every prior volume and is true from 2026-08-13. It is the
  only claim in this list that has changed.
* **Milestone 4 is not accepted.** OPEN-051-F remains the sole blocker. It is
  no longer blocked on execution - the gate has been run - it is blocked on
  OPEN-069-A, a real defect in the halo geometry, and on the full re-run that
  the fix requires.
* `requires local compilation`, `requires Unreal Editor verification` and
  `requires playtesting` are all still unsatisfied. `requires visual
  inspection` is satisfied for this one mesh at this one revision and for
  nothing else.

---

## Open questions, authoritative table

| Id | Subject | Status |
|---|---|---|
| OPEN-051-B | Drift guard banner announces 27 entries; the counterparty count has never been identified | open |
| OPEN-051-F | Milestone 4 visual acceptance, 15 criteria | **open - M4 blocker.** Gate run 2026-08-13, failed on G-2.4. Now blocked on OPEN-069-A, not on execution |
| OPEN-053-A | Local rehearsal gate for `af_mesh_quality.py` | open |
| OPEN-060-A | Historical versus measured mesh figures. Extended by D-069.6 to cover the G-1.4 name set, the G-1.5 width and the G-1.6 vertex and face counts. Neither side is to be adjusted | open, widened |
| OPEN-065-A | VOL8 header still reads "open" although VOL9 superseded it. Volume 10 now has the same condition | open |
| OPEN-065-B | Cross-reference from `VERSION_MATRIX.md` section 5.20 to `SCRIPT_INVENTORY.md` | narrowed to one pointer |
| OPEN-066-A | `af_static_validate.py` has no `--self-test` step in either workflow | open |
| OPEN-066-B | `af_bodywork_selftest.py`, 22,078 bytes, exercised by nothing but `compileall` | open |
| OPEN-068-A | Should the Blender patch be pinned as `BLENDER_VERSION: '5.2.0'` rather than floating on the series. D-069 raises the stakes: the visual gate has now been run on 5.2.0 by hand | open |
| OPEN-068-B | Bump `actions/checkout` and `actions/upload-artifact` from `@v4` to `@v5` | open |
| OPEN-068-C | Propagate Blender 5.2.0 into `VERSION_MATRIX.md` section 5 | open |
| OPEN-069-A | `AF_Surface_Halo` is detached from the monocoque by 0.112646 m and is a 0.050 m strip rather than a closed loop | **open - new, M4 blocker** |
| OPEN-069-B | The four G-2 screenshots are named in the gate but not yet committed to `Documentation/acceptance/` | **open - new** |

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
| `DECISION_LOG.md` ... `DECISION_LOG_VOL9.md` | - | frozen |
| `DECISION_LOG_VOL10.md` | ~17.4 KB | frozen at D-068 |
| `DECISION_LOG_VOL11.md` | this file | **open** |
| `CI_EVIDENCE.md` ... `CI_EVIDENCE_VOL6.md` | - | frozen |
| `CI_EVIDENCE_VOL7.md` | 11,984 B | **open** |

Next decision id: **D-070**.
