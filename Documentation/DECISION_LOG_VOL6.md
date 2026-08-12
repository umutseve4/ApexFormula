# Decision log, volume 6

Volume 5 was closed by size at 20,132 bytes, carrying D-056 through D-058.
This volume opens at D-059.

## Volume history

| Volume | Decisions | Closed at | Reason |
|---|---|---|---|
| 1 | D-001 .. D-018 | 19,904 bytes | size |
| 2 | D-019 .. D-035 | 21,470 bytes | size |
| 3 | D-036 .. D-045 | 20,663 bytes | size |
| 4 | D-046 .. D-055 | 22,118 bytes | size |
| 5 | D-056 .. D-058 | 20,132 bytes | size |
| 6 | D-059 .. | open | - |

The convention is unchanged. A volume is closed when it passes roughly
twenty kilobytes, because past that point a full file retranscription
becomes the dominant risk in every edit, and this repository has no patch
mode. Closed volumes are never reopened, never reordered, and never
silently corrected; an error in a closed volume is fixed by an erratum in
the current one, per D-057.

---

## D-059. The mesh export slice: a new module, seventeen digits, and a parser that refuses to guess

**Status:** decided and implemented
**Date:** 2026-08-12
**Milestone:** 4, slice 3
**Supersedes:** nothing
**Superseded by:** nothing
**Artefact:** `BlenderPipeline/scripts/af_mesh_export.py`, blob
`26d135e37997db20b41132fafc157f80b0f80576`, 23,654 bytes, commit
`b5b935f8646368e5fd1a08b4df6d4b9fcaee6f82`
**CI:** batch 9, ten check runs, all `success`, recorded in
`Documentation/CI_EVIDENCE_VOL5.md` section 9

### Context

After D-058 closed OPEN-056-B, the bodywork geometry existed as numbers and
nothing else. `build_parts()` returned twelve named surfaces and
`collision_proxies()` returned a set of convex hulls, all of them verified
by 22 core cases and a 42 case acceptance suite, and none of them ever seen
by anybody. The gap between "the arithmetic is self consistent" and "the
car looks like a car" cannot be closed by adding more assertions. It can
only be closed by writing a file a human can open.

That is the entire purpose of this slice. It is deliberately the smallest
thing that makes visual verification possible.

### Decision 1: a new module, not an edit to the existing one

`af_bodywork_profile.py` is 42,219 bytes. Under D-057, files past roughly
twenty kilobytes are corrected by erratum and never retranscribed, because
this environment has no patch mode and every write is a full file
retranscription. Adding an exporter to that module would have meant
retranscribing forty two kilobytes of verified, CI green geometry code in
order to append a few hundred lines of serialisation, and a single dropped
character anywhere in the untouched 42 KB would have been invisible in the
diff and fatal in the mesh.

The exporter is therefore a separate module that imports the geometry
module. This is not merely a workaround for the environment; it is also the
correct decomposition. Geometry generation and serialisation are different
concerns with different failure modes, and the exporter has no business
knowing how a superellipse ring is computed.

**Consequence:** the import is hard. `import af_bodywork_profile as bw`,
with no `try` and no `except ImportError`. A gate that can silently skip
itself is not a gate, which is the same principle D-058 applied to the
acceptance suite import.

### Decision 2: `%.17g`, not `%.6f`

Coordinates are written with `FLOAT_FORMAT = "%.17g"`.

Almost every OBJ exporter in existence writes `%.6f`. Six decimal places is
plenty for a renderer and hopeless for a test. Seventeen significant digits
is the shortest decimal field that round trips an IEEE 754 double
**exactly**: write with fewer and the value you read back is a different
number, close but not equal.

This choice is what makes the round trip cases meaningful. Because the
serialisation is lossless, those cases assert **equality** - vertex by
vertex, face index by face index, and on the signed volume of the
reconstructed solid - rather than asserting that two numbers are within
some tolerance the author chose after seeing the failure. A tolerance based
round trip test passes by construction and proves nothing. An equality
based one fails the moment a digit is lost.

The cost is file size. 112,123 bytes across 26 dumped files instead of
perhaps sixty thousand. That is an entirely acceptable price for assertions
that can actually fail.

### Decision 3: `parse_obj` raises on unrecognised records

The OBJ reader does not skip lines it does not understand. It raises
`ExportError`.

The tempting behaviour is to ignore unknown records, since the format has
many and most are irrelevant to geometry. The problem is what that does to
the round trip test: if the writer emits a record the reader silently
discards, the comparison still passes while data is being lost on every
cycle. The test would be reporting on a subset of the file and calling it
the file.

Refusing to guess makes the reader strict enough to be a witness for the
writer. If a future change to the writer emits something new, the reader
fails loudly and the author has to decide, explicitly, what that record
means.

### Decision 4: OPEN-051-B stays deferred, on the record

OPEN-051-B is the discrepancy between the 27 banner count reported by
`Tools/af_drift_guard.py` and the 31 recorded in `VERSION_MATRIX.md`. It is
still open and it is being deferred deliberately, not forgotten.

The reason is cost and risk. The guard is 38,569 bytes, this environment
has no remote grep and no working code search index for this repository,
and under D-057 the file must not be retranscribed. Resolving the count
honestly means reading the whole module and reconciling it against the
matrix by hand - a dedicated turn's work, with nothing to show for it in
the mesh. Doing it badly means either editing the matrix to match a number
nobody has verified, or editing the guard and risking a 38 KB
retranscription for a documentation discrepancy.

Neither is acceptable, and neither is quietly refreshing the number, which
is the same failure OPEN-052-C exists to prevent. It waits.

### What this slice does not establish

Measured locally and reproduced in CI:

```
af_mesh_export: 21 cases, 227 assertions, 0 failures
export plan: 14 files, 798 serialised faces
```

Twenty six byte identical files across two consecutive `--dump` runs,
112,123 bytes in total, so the writers are deterministic.

None of that is visual verification. The exporter proves that whatever the
generator produces survives a write and a read without losing a bit. It has
no opinion about whether the generator produces a plausible racing car, and
no test in this repository can form one.

**Milestone 4 remains not started for acceptance purposes.** It stays that
way until `AF_Bodywork_Combined.obj` is opened in Blender and a screenshot
comes back. That screenshot is the only thing that can close OPEN-051-F,
and it is the only remaining deliverable of this slice.

### Reproduction

```
python3 BlenderPipeline/scripts/af_mesh_export.py --self-test
python3 BlenderPipeline/scripts/af_mesh_export.py --dump out
```

The second command writes twelve part OBJ files, twelve part PLY files,
`AF_Bodywork_Combined.obj` and `AF_Bodywork_Collision.obj` into `out/`. The
combined file is the one to open.

---

## D-060. The visual verification is defined before the screenshot, not after

**Status:** decided; the gate is written, the gate has not been run
**Date:** 2026-08-12
**Milestone:** 4, acceptance
**Supersedes:** nothing
**Superseded by:** nothing
**Artefact:** `Documentation/MILESTONE_4_VISUAL_ACCEPTANCE.md`, blob
`bf1b33b524fe110344abd7034b7480051550abeb`, 11,392 bytes, commit
`046775c0965dd7442d19d1fa6a8ac964c8e973b0`
**CI:** none, and none is owed. The commit is markdown only and under D-054
gate scoped coverage a documentation only change creates no CI batch
obligation.

### Context

D-059 left Milestone 4 with exactly one outstanding deliverable and exactly
one person who can produce it: a screenshot of `AF_Bodywork_Combined.obj`,
taken on a machine that has Blender 5.2 LTS. The authoring environment has
no Blender, no Unreal, and no network, so it cannot take that screenshot
and must not pretend otherwise.

What the authoring environment can do is decide, in advance, what the
screenshot has to show. That is the whole of this decision.

### Decision 1: the criteria are written before the screenshot exists

A screenshot judged against no criteria produces the sentence "looks fine",
which is an impression wearing the costume of a result. The failure is not
laziness; it is ordering. Once an image exists, any criterion invented
afterwards is fitted to the image rather than applied to it, and the
verification quietly becomes a rationalisation of whatever came out.

So the gate is fifteen numbered criteria, each with a method and a stated
failure condition, committed before the mesh has been seen. Two of them,
G-2.6 silhouette and G-2.8 originality, are openly judgement calls. They
are still criteria, because a judgement recorded in advance is a test and
the same judgement recorded afterwards is not.

### Decision 2: the gate is split into a half that needs no DCC and a half that does

Most of what people try to check by eye is a number, and a number checked
by eye is checked badly. Part count, envelope dimensions, vertex and face
totals, determinism, prohibited name tokens - these are measurements, and
Blender adds nothing to any of them except an opportunity to misread a
value off a panel.

G-1 therefore measures everything measurable from the exported OBJ with the
standard library alone, on the same machine that runs the self-test, with a
helper script printed in section 6 of the gate document. G-2 is reserved
for the four or five questions that genuinely require a human eye: outward
facing normals, bilateral symmetry, whether the halo is a halo, whether the
silhouette reads as a formula car.

The helper script is deliberately not a repository module. Committing it
under `BlenderPipeline/scripts/` would create a gate scoped artefact owing
a CI batch, and it is a one off measuring tape, not a permanent gate. It
follows D-059 decision 3 regardless: it raises on unrecognised records
rather than skipping them.

### Decision 3: the historical figures are marked unverified, not promoted to expectations

`Documentation/MILESTONE_4_BODYWORK.md` sections 4 to 6 record 12 parts,
1068 vertices, 936 faces, and a 5.600 by 1.918 by 0.940 metre envelope.
Those numbers predate the D-058 re-authoring of the geometry module and
have never been re-measured against the module that exists now. Section 0
of that document already says so.

The tempting move is to treat them as the expected values, because they are
the only values anybody has. The gate refuses. Each such target carries the
strength marker **unverified historical**, and a mismatch against one is
recorded as a finding requiring a decision rather than as a failure. Only
the CI reproduced figures - the self-test counts, the 26 file 112,123 byte
dump, the determinism check - are marked **verified**, where a mismatch is
a straightforward failure.

The alternative is worse in both directions: a mismatch would either be
reported as a bug in working code, or quietly resolved by editing the
target to match the output, which is the exact failure OPEN-052-C exists to
prevent.

### Decision 4: a partial pass is a fail

If any of the fifteen rows fails, OPEN-051-F stays open, the failure
becomes its own numbered open question, and Milestone 4 stays at not
started for acceptance purposes. There is no partial credit and no "mostly
passes". The milestone has been held at zero through nine CI batches and a
hundred green check runs precisely because nobody has looked at the mesh;
it would be absurd to release that hold on a checklist that fourteen out of
fifteen rows agree with.

### New open question

**OPEN-060-A.** The current export plan reports 798 serialised faces across
14 files. The historical record reports 936 faces for the combined mesh.
The two figures are not directly comparable - one counts faces written
across every output file, the other counts a single file - so the
difference is not by itself evidence of a defect. It is also not
understood. It is recorded, and it is not to be resolved by adjusting
either number.

### What this decision does not establish

Nothing about the mesh. The gate is written; the gate has not been run.
No part of `MILESTONE_4_VISUAL_ACCEPTANCE.md` may be cited as evidence that
the bodywork is correct, present, symmetrical, or plausible. Its result
table is empty by design and stays empty until somebody with Blender fills
it in.

---

## Open questions carried into this volume

| Id | Subject | State |
|---|---|---|
| OPEN-051-B | drift guard banner count 27 vs `VERSION_MATRIX.md` 31 | open, deferred by D-059 decision 4 |
| OPEN-051-D | volume 2 header and index inconsistency | open, volume frozen, erratum only |
| OPEN-051-F | Blender visual verification of the bodywork | open, gate defined by D-060, blocked only on execution on Umut's machine |
| OPEN-052-C | `VERSION_MATRIX.md` section 5.28 "2300 checks" | open, never to be silently refreshed |
| OPEN-053-A | local rehearsal gate for `af_mesh_quality.py` | open, declared not met rather than faked |
| OPEN-060-A | 936 historical faces vs 798 serialised faces in the export plan | open, raised by D-060, not to be reconciled by adjusting either number |

Closed and not to be reopened: OPEN-051-A, OPEN-051-C, OPEN-051-E,
OPEN-052-A, OPEN-052-B, OPEN-M4-01 (D-056), OPEN-056-A (D-057),
OPEN-056-B (D-058).
