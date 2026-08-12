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

## Open questions carried into this volume

| Id | Subject | State |
|---|---|---|
| OPEN-051-B | drift guard banner count 27 vs `VERSION_MATRIX.md` 31 | open, deferred by D-059 decision 4 |
| OPEN-051-D | volume 2 header and index inconsistency | open, volume frozen, erratum only |
| OPEN-051-F | Blender visual verification of the bodywork | open, needs Umut's machine, unblocked by this slice |
| OPEN-052-C | `VERSION_MATRIX.md` section 5.28 "2300 checks" | open, never to be silently refreshed |
| OPEN-053-A | local rehearsal gate for `af_mesh_quality.py` | open, declared not met rather than faked |

Closed and not to be reopened: OPEN-051-A, OPEN-051-C, OPEN-051-E,
OPEN-052-A, OPEN-052-B, OPEN-M4-01 (D-056), OPEN-056-A (D-057),
OPEN-056-B (D-058).
