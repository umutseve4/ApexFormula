# Decision log, volume 6

Volume 5 was closed by size at 20,132 bytes, carrying D-056 through D-058.
This volume opens at D-059.

## Volume history

Corrected by D-061. The table previously carried here was wrong in four of
its five rows. Ranges below are taken from the section 0 tables of volumes
3 and 4, which agree with each other and with the range header volume 3
states for itself. Sizes are measured blob sizes from a directory listing
of `Documentation/` taken on 2026-08-12.

| Volume | File | Decisions | Size | Basis |
|---|---|---|---|---|
| 1 | `DECISION_LOG.md` | D-001 .. D-044 | 50,726 bytes | measured |
| 2 | `DECISION_LOG_VOL2.md` | D-045 .. D-050 | 20,441 bytes | measured |
| 3 | `DECISION_LOG_VOL3.md` | D-051 .. D-052 | 25,950 bytes | measured |
| 4 | `DECISION_LOG_VOL4.md` | D-053 .. D-055 | 27,898 bytes | measured |
| 5 | `DECISION_LOG_VOL5.md` | D-056 .. D-058 | 20,132 bytes | measured |
| 6 | `DECISION_LOG_VOL6.md` | D-059 .. | open | measured |

The convention is unchanged. A volume is closed when it passes roughly
twenty kilobytes, because past that point a full file retranscription
becomes the dominant risk in every edit, and this repository has no patch
mode. Closed volumes are never reopened, never reordered, and never
silently corrected; an error in a closed volume is fixed by an erratum in
the current one, per D-057.

Note that volumes 1, 3 and 4 exceed twenty kilobytes, volume 1 by a factor
of two and a half. The threshold was adopted after those volumes were
written, and it is applied going forward rather than retroactively. Volume
4 in particular must not be appended to; its own section 0 says so.

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

## D-061. The volume history table was wrong in four of five rows

**Status:** decided, corrected, and verified against primary evidence
**Date:** 2026-08-12
**Milestone:** none; documentation integrity
**Supersedes:** the volume history table previously carried in section 0 of
this volume
**Superseded by:** nothing
**Artefact:** this file
**CI:** none, and none is owed. Markdown only, D-054 gate scoped coverage.

### Context

Volumes 3, 4 and 5 of this log were read end to end while discharging the
transcription gap disclosed in
`Documentation/MILESTONE_4_IMPLEMENTATION_VOL2.md`. Each closed volume
carries its own section 0 volume history table. They do not all agree, and
the table carried in this volume agreed with none of them.

That is not a cosmetic problem. The volume history table is the index by
which any future reader locates a decision. If it points at the wrong
volume, a decision that exists is functionally lost, and the natural
recovery - reading volumes until the decision turns up - is exactly the
expensive operation the volume split was created to avoid.

### The evidence

Two independent kinds, both primary.

**Ranges.** Volume 3 states its own range in its header: *Range: D-051
onward*. Its body contains exactly two decisions, D-051 and D-052, and
nothing else. Volume 4's section 0 table independently gives volume 1 as
D-001 to D-044, volume 2 as D-045 to D-050, volume 3 as D-051 and D-052,
and volume 4 as D-053 onward. Volume 3's section 0 table agrees with volume
4 on volumes 1 and 2. Two closed volumes written at different times agree
with each other and with volume 3's self-declared header.

**Sizes.** A directory listing of `Documentation/` requesting only name,
size and blob hash returns the byte count of every file without
downloading any body - the technique recorded in D-055.6. Taken on
2026-08-12 it returns: `DECISION_LOG.md` 50,726 bytes,
`DECISION_LOG_VOL2.md` 20,441, `DECISION_LOG_VOL3.md` 25,950,
`DECISION_LOG_VOL4.md` 27,898, `DECISION_LOG_VOL5.md` 20,132,
`DECISION_LOG_VOL6.md` 13,477 before this entry.

### The defect

The table this volume carried before this entry read:

| Volume | Decisions | Closed at |
|---|---|---|
| 1 | D-001 .. D-018 | 19,904 bytes |
| 2 | D-019 .. D-035 | 21,470 bytes |
| 3 | D-036 .. D-045 | 20,663 bytes |
| 4 | D-046 .. D-055 | 22,118 bytes |
| 5 | D-056 .. D-058 | 20,132 bytes |

Every range on rows 1 through 4 is wrong. Every size on rows 1 through 4 is
wrong, row 1 by 30,822 bytes. Only row 5 is correct, and row 5 is the row
this volume was written immediately after.

### Decision 1: correct in place, because this volume is open

D-057 requires that an error in a **closed** volume be fixed by erratum in
the current volume, never by editing the closed file. This error is in the
current volume, so that rule does not apply and the table is corrected
directly. Nothing frozen is touched.

The defect is recorded here in full rather than quietly overwritten. A
corrected table with no record of what it replaced would leave a reader
unable to tell whether an old citation was wrong or merely unfamiliar.

### Decision 2: this table supersedes any section 0 table in a closed volume

Closed volumes each carry their own copy of the history, and copies made at
different times cannot all be right. Rather than adjudicate each one, the
rule is positional: the volume history in the **open** volume is
authoritative, and any table in a closed volume that disagrees with it is
superseded on sight and must not be edited.

This has a specific consequence worth stating. Volume 5's section 0 table
was not re-read while writing this entry, so this decision makes no claim
about whether it agrees or disagrees. It does not need to. If it
disagrees, it is superseded by this rule without further work.

### Decision 3: D-049 and D-050 are in volume 2, and volume 2 has not been read

The corrected table places D-045 through D-050 in `DECISION_LOG_VOL2.md`.
That file is frozen at 20,441 bytes and has **not** been read in this
session. Any statement about the content of D-049 or D-050 would therefore
be reconstruction, which D-053.6 already ruled out in a more consequential
setting: evidence about a file must be produced by that file.

So the transcription gap disclosed in
`MILESTONE_4_IMPLEMENTATION_VOL2.md` narrows but does not close. D-051
through D-058 can now be summarised from volumes read in full. D-049 and
D-050 remain genuinely unread and are to be labelled as such, not
paraphrased from context.

### Related open question

This is the same family of defect as **OPEN-051-D**, which records that
volume 2's header says the volume starts at D-047 while its index lists
D-045 and D-046. OPEN-051-D stays open; it concerns a frozen file and can
only ever be an erratum. Reading volume 2 would settle both it and decision
3 above in a single pass, and that is the cheapest way to close either.

### What this decision does not establish

Nothing about the mesh, the geometry, the exporter, or Milestone 4. It
corrects an index. The correctness of the individual decision entries
themselves was not audited and is not claimed; only their location is.

---

## Open questions carried into this volume

| Id | Subject | State |
|---|---|---|
| OPEN-051-B | drift guard banner count 27 vs `VERSION_MATRIX.md` 31 | open, deferred by D-059 decision 4 |
| OPEN-051-D | volume 2 header and index inconsistency | open, volume frozen, erratum only; would be settled by reading volume 2 |
| OPEN-051-F | Blender visual verification of the bodywork | open, gate defined by D-060, blocked only on execution on Umut's machine |
| OPEN-052-C | `VERSION_MATRIX.md` section 5.28 "2300 checks" | open, never to be silently refreshed |
| OPEN-053-A | local rehearsal gate for `af_mesh_quality.py` | open, declared not met rather than faked |
| OPEN-060-A | 936 historical faces vs 798 serialised faces in the export plan | open, raised by D-060, not to be reconciled by adjusting either number |
| OPEN-061-A | `DECISION_LOG_VOL2.md` is unread, so D-049 and D-050 are unsummarised | open, raised by D-061 decision 3, closes by reading the file |

Closed and not to be reopened: OPEN-051-A, OPEN-051-C, OPEN-051-E,
OPEN-052-A, OPEN-052-B, OPEN-M4-01 (D-056), OPEN-056-A (D-057),
OPEN-056-B (D-058).
