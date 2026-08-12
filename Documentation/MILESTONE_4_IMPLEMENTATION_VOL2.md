# Milestone 4 — Implementation Record, volume 2

Volume 1, `MILESTONE_4_IMPLEMENTATION.md`, is 23,694 bytes and is closed by
size under D-057. It carries D-046, D-047 and D-048, and its section 2
still reads "next free decision identifier: **D-049**". The decision log
has since reached D-060.

That gap is the reason this volume exists. Twelve decisions have landed
since volume 1 was last written, and the milestone's own implementation
record has not reflected any of them. Retranscribing 23,694 bytes to
append to it would put the entire file at risk to gain a few sections, in
an environment with no patch interface, which is exactly the situation
D-057 exists to prevent and exactly the reasoning that produced
`DECISION_LOG_VOL2.md`.

The verification labels are unchanged from volume 1 and are not repeated
here. `statically inspected`, `automatically validated`, `verified by
inspection`, `requires local compilation`, `requires Unreal Editor
verification`, `requires Blender execution`, `requires visual inspection`,
`requires playtesting`, `not claimed`.

---

## 1. Scope of this volume, and what it deliberately does not contain

This volume records only what has been read from the live repository and
verified against it. It does **not** reconstruct D-049 through D-058 from
memory.

| Decisions | Where the authoritative record lives | Transcribed here |
| --- | --- | --- |
| D-046 .. D-048 | `MILESTONE_4_IMPLEMENTATION.md` (volume 1) | closed, do not edit |
| D-049 .. D-055 | `DECISION_LOG_VOL3.md`, `DECISION_LOG_VOL4.md` | **no** |
| D-056 .. D-058 | `DECISION_LOG_VOL5.md` | **no** |
| D-059, D-060 | `DECISION_LOG_VOL6.md` | yes, sections 3 and 4 below |

The middle two rows are a known and disclosed gap, not an omission
discovered later. Writing a milestone record for a decision without
re-reading that decision's log entry in full would produce a plausible
summary rather than a record, and a plausible summary is precisely the
artefact this repository's evidence rules exist to forbid. Those rows are
filled in when their volumes are re-read, and not before.

What is already known and requires no re-reading: OPEN-M4-01, the
collision proxy datum defect opened during D-047 and recorded in volume 1
section 5, was **closed by D-056**. Volume 1 describes it as open. That
statement is stale rather than wrong — it was true when volume 1 was
written — and volume 1 is closed, so it is corrected here by erratum in
the manner D-057 prescribes, not by editing the closed file.

---

## 2. Milestone 4 status as of 2026-08-12

**Milestone 4 is not started for acceptance purposes.**

That sentence is deliberate and it is not pessimism. It is what the
evidence supports.

| Question | Answer | Label |
| --- | --- | --- |
| Does bodywork geometry exist as code? | yes | *automatically validated* |
| Does it pass its own self-tests? | yes | *automatically validated* |
| Has continuous integration executed those self-tests? | yes, batches 8 and 9 | *automatically validated, job level* |
| Can the geometry be written to a file a human can open? | yes | *automatically validated* |
| Has any C++ been compiled? | no | *not claimed* |
| Has Unreal Editor been opened? | no | *not claimed* |
| Has Blender been executed against this geometry? | no | *not claimed* |
| Has any human seen the mesh? | **no** | *not claimed* |
| Has a lap been driven? | no | *not claimed* |

Nine of nine rows are honest. The last four are the milestone.

Cumulative continuous integration across evidence volumes 1 to 5: **100
check runs, all `success`**. That number is a measure of how much text has
been validated. It is not a measure of how much of the game exists, and it
must never be quoted as one.

---

## 3. D-059 — the mesh export slice

**Status: merged and CI-verified.** Full record in `DECISION_LOG_VOL6.md`.

| Field | Value |
| --- | --- |
| Artefact | `BlenderPipeline/scripts/af_mesh_export.py` |
| Blob | `26d135e37997db20b41132fafc157f80b0f80576` |
| Size | 23,654 bytes |
| Commit | `b5b935f8646368e5fd1a08b4df6d4b9fcaee6f82` |
| CI | batch 9, ten check runs, all `success` |
| Evidence | `Documentation/CI_EVIDENCE_VOL5.md` section 9 |

Reproduced in continuous integration:

```
af_mesh_export: 21 cases, 227 assertions, 0 failures
export plan: 14 files, 798 serialised faces
```

Measured locally only, **not** covered by continuous integration because
the self-test writes nothing to disk: two consecutive `--dump` runs
produced **26 byte-identical files totalling 112,123 bytes**. The writers
are deterministic. That determinism is currently proven by hand, not by a
gate, and is listed in section 6 below as unfinished business.

Three design decisions from D-059 that constrain everything downstream and
are restated here so they are visible from the milestone record:

1. The exporter is a **separate module** that hard-imports the geometry
   module. No `try` / `except ImportError`. A gate that can silently skip
   itself is not a gate.
2. Coordinates are written with `%.17g`, the shortest decimal field that
   round-trips an IEEE 754 double exactly. This is what allows the
   round-trip cases to assert **equality** rather than a tolerance the
   author chose after seeing a failure.
3. `parse_obj` **raises** on records it does not recognise instead of
   skipping them, so the reader is a real witness for the writer.

### What D-059 does not prove

*not claimed.* The exporter proves that whatever the generator produces
survives a write and a read without losing a bit. It has no opinion on
whether the generator produces a plausible racing car, and no test in this
repository can form one.

---

## 4. D-060 — the visual acceptance gate

**Status: the gate is written; the gate has not been run.**

| Field | Value |
| --- | --- |
| Artefact | `Documentation/MILESTONE_4_VISUAL_ACCEPTANCE.md` |
| Blob | `bf1b33b524fe110344abd7034b7480051550abeb` |
| Size | 11,392 bytes |
| Commit | `046775c0965dd7442d19d1fa6a8ac964c8e973b0` |
| CI | none, and none is owed — markdown only, D-054 gate-scoped coverage |

The gate defines fifteen numbered criteria in two halves.

**G-1, seven numeric criteria.** Measurable from the exported OBJ with the
standard library alone, on any machine that can run the self-test. No
Blender required. Part count, envelope dimensions, vertex and face totals,
determinism, prohibited name tokens. These are measurements, and a
measurement checked by eye off a viewport panel is checked badly.

**G-2, eight visual criteria.** Reserved for the questions that genuinely
need a human eye: outward-facing normals under the Face Orientation
overlay, bilateral symmetry, whether the halo reads as a halo, whether the
silhouette reads as a formula car, and originality.

Two of the G-2 criteria are openly judgement calls. They are still
criteria, because a judgement recorded before the image exists is a test
and the same judgement recorded afterwards is a rationalisation of
whatever came out.

Section 6 of the gate document contains a measurement helper. It is
printed in the markdown and is **deliberately not** a repository module
under `BlenderPipeline/scripts/`: committing it there would create a
gate-scoped artefact owing a continuous integration batch, and it is a
one-off measuring tape rather than a permanent gate. It was executed in
the authoring environment against a synthetic OBJ file to confirm it
parses and counts correctly. *automatically validated* — against a
synthetic file, **not** against the real bodywork export.

### The strength markers matter

Targets taken from `MILESTONE_4_BODYWORK.md` sections 4 to 6 — 12 parts,
1068 vertices, 936 faces, a 5.600 × 1.918 × 0.940 m envelope — predate the
D-058 re-authoring of the geometry module and have **never been
re-measured**. Each carries the marker **unverified historical**, and a
mismatch against one is a finding requiring a decision, not a failure.
Only the CI-reproduced figures are marked **verified**, where a mismatch
is a straightforward failure.

The alternative is worse in both directions: a mismatch would either be
reported as a bug in working code, or quietly resolved by editing the
target to match the output.

### What D-060 does not prove

*not claimed.* Nothing whatsoever about the mesh. The gate is written; the
gate has not been run. Its result table is empty by design. No part of
that document may be cited as evidence that the bodywork is correct,
present, symmetrical or plausible.

---

## 5. The one remaining Milestone 4 deliverable

**OPEN-051-F**, Blender visual verification of the bodywork. It is the
only thing standing between the current state and Milestone 4 acceptance,
and it cannot be discharged from the authoring environment, which has no
Blender, no Unreal and no network.

Procedure, in order:

```
python3 BlenderPipeline/scripts/af_mesh_export.py --self-test
python3 BlenderPipeline/scripts/af_mesh_export.py --dump out
```

The second command writes twelve part OBJ files, twelve part PLY files,
`AF_Bodywork_Combined.obj` and `AF_Bodywork_Collision.obj` into `out/`.
`out/` is build output and is never committed.

Then, in order: run the section 6 helper against
`out/AF_Bodywork_Combined.obj` to settle G-1; open that file in Blender
5.2 LTS; capture three views — three-quarter front, orthographic side,
orthographic top — with the **Face Orientation overlay enabled**; settle
G-2 against those images; record all fifteen rows.

*requires Blender execution, requires visual inspection.*

**A partial pass is a fail.** If any row fails, OPEN-051-F stays open, the
failure becomes its own numbered open question, and this milestone stays at
not started for acceptance purposes. The hold has survived nine continuous
integration batches and a hundred green check runs precisely because
nobody has looked at the mesh; releasing it on fourteen of fifteen would
make the whole exercise decorative.

---

## 6. Open questions live at the end of Milestone 4

| Id | Subject | State |
| --- | --- | --- |
| OPEN-051-B | drift guard banner count 27 vs `VERSION_MATRIX.md` 31 | open, deferred by D-059 |
| OPEN-051-D | decision log volume 2 header and index inconsistency | open, volume frozen, erratum only |
| OPEN-051-F | Blender visual verification of the bodywork | open, gate defined by D-060, blocked only on execution |
| OPEN-052-C | `VERSION_MATRIX.md` section 5.28 "2300 checks" | open, never to be silently refreshed |
| OPEN-053-A | local rehearsal gate for `af_mesh_quality.py` | open, declared not met rather than faked |
| OPEN-060-A | 936 historical faces vs 798 serialised faces in the export plan | open, not to be reconciled by adjusting either number |

Closed and not to be reopened: OPEN-051-A, OPEN-051-C, OPEN-051-E,
OPEN-052-A, OPEN-052-B, **OPEN-M4-01** (closed by D-056; volume 1 section
5 still describes it as open and is stale), OPEN-056-A, OPEN-056-B.

### Unfinished business that is not yet a numbered open question

1. **Export determinism is not gated.** The 26-file, 112,123-byte
   byte-identical result was measured by hand. The self-test writes
   nothing to disk, so continuous integration cannot currently regress on
   it. A determinism check that dumps to a temporary directory twice and
   compares would close this, and would owe a CI batch.
2. **Volume 1 rows for D-049 to D-058.** Disclosed in section 1 above.
3. **The rename waves 2 onward** from D-048 section 4.6 remain planned and
   not implemented. Six module directories, six `.Build.cs` files, two
   `.Target.cs` files, the `.uproject`, the export macros, the copyright
   line in 65 C++ files, and the lockstep rewrite of
   `af_static_validate.py`. None of this is started. *not claimed.*
