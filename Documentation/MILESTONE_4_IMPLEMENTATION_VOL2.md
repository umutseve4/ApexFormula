# Milestone 4 — Implementation Record, volume 2

Volume 1, `MILESTONE_4_IMPLEMENTATION.md`, is 23,694 bytes and is closed by
size under D-057. It carries D-046, D-047 and D-048, and its section 2
still reads "next free decision identifier: **D-049**". The decision log
has since reached D-061.

That gap is the reason this volume exists. Thirteen decisions have landed
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
verified against it. It does **not** reconstruct decisions from memory.

| Decisions | Where the authoritative record lives | Transcribed here |
| --- | --- | --- |
| D-046 .. D-048 | `MILESTONE_4_IMPLEMENTATION.md` (volume 1) | closed, do not edit |
| D-049, D-050 | `DECISION_LOG_VOL2.md` | **no** — file unread, see OPEN-061-A |
| D-051, D-052 | `DECISION_LOG_VOL3.md` | yes, section 7 below |
| D-053 .. D-055 | `DECISION_LOG_VOL4.md` | yes, section 7 below |
| D-056 .. D-058 | `DECISION_LOG_VOL5.md` | yes, section 7 below |
| D-059, D-060 | `DECISION_LOG_VOL6.md` | yes, sections 3 and 4 below |
| D-061 | `DECISION_LOG_VOL6.md` | yes, section 1.1 below |

When this volume was created the gap ran from D-049 to D-058. Volumes 3, 4
and 5 have since been read end to end and section 7 discharges that range.
The residue is **two decisions**, D-049 and D-050, which live in
`DECISION_LOG_VOL2.md`. That file is frozen at 20,441 bytes and has not
been read. Summarising it from surrounding context would produce a
plausible account rather than a record, which D-053.6 already ruled out in
a more consequential setting: evidence about a file must be produced by
that file. The residue is therefore left explicitly empty and tracked as
OPEN-061-A.

### 1.1 Two errata against closed files

**OPEN-M4-01**, the collision proxy datum defect opened during D-047 and
recorded in volume 1 section 5, was **closed by D-056**. Volume 1
describes it as open. That statement is stale rather than wrong — it was
true when volume 1 was written — and volume 1 is closed, so it is
corrected here by erratum in the manner D-057 prescribes, not by editing
the closed file.

**The decision log volume history** carried in `DECISION_LOG_VOL6.md`
section 0 was wrong in four of its five rows, in both the decision ranges
and the recorded sizes. D-061 corrected it in place, which was permitted
because volume 6 is the open volume. The corrected partition is the one
used in the table above. Any volume history table in a *closed* decision
log volume that disagrees with volume 6 is superseded on sight and must
not be edited.

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
| OPEN-061-A | `DECISION_LOG_VOL2.md` unread, so D-049 and D-050 are unsummarised | open, closes by reading that file, which would also settle OPEN-051-D |

Closed and not to be reopened: OPEN-051-A, OPEN-051-C, OPEN-051-E,
OPEN-052-A, OPEN-052-B, **OPEN-M4-01** (closed by D-056; volume 1 section
5 still describes it as open and is stale), OPEN-056-A, OPEN-056-B.

### Unfinished business that is not yet a numbered open question

1. **Export determinism is not gated.** The 26-file, 112,123-byte
   byte-identical result was measured by hand. The self-test writes
   nothing to disk, so continuous integration cannot currently regress on
   it. A determinism check that dumps to a temporary directory twice and
   compares would close this, and would owe a CI batch.
2. **D-049 and D-050 are unsummarised.** Now tracked as OPEN-061-A.
3. **The rename is finished, not pending.** This item previously said the
   rename waves from D-048 section 4.6 remained planned and not
   implemented, listing six module directories, six `.Build.cs` files, two
   `.Target.cs` files, the `.uproject` and 65 copyright lines as
   outstanding work. **That was wrong.** D-055 measured the cost of that
   ladder and refused it, and D-055.8 cancelled wave 2A and wave 2C,
   closed OPEN-052-B and OPEN-051-E, and declared the rename effort
   **complete**. The six module identifiers, the `.uproject` name, the
   `AF_` / `af_` symbol prefixes and the `Unreal/Source` directory names
   are **frozen permanently** and reclassified as an internal code name.
   There is no outstanding rename work and nothing here is owed.

---

## 7. D-051 to D-058, from volumes read in full

Summarised from `DECISION_LOG_VOL3.md` (25,950 bytes),
`DECISION_LOG_VOL4.md` (27,898 bytes) and `DECISION_LOG_VOL5.md` (20,132
bytes), each read end to end. All three are frozen. Where a figure appears
below it was read from those files, not recalled. This section is a
navigation aid; the log entries remain authoritative.

### D-051 — the rename scope, and the lockstep rule

Restated D-048 option 2: the product identity is renamed, and the
`AF_` / `af_` / `UAF*` / `FAF*` / `AAF*` / `IAF*` / `LogAF*` symbol
prefixes are **not**, being reclassified as a permanent internal code
name. `Uludağ` is legal in ini display strings and in Markdown and
**illegal in a module name**, because Unreal Build Tool requires the module
name, its directory, its `.Build.cs` filename and its C# class to be the
same ASCII token. `ğ` is two bytes in UTF-8, so all size arithmetic in
this repository is done in bytes rather than characters.

Findings recorded against `Tools/af_static_validate.py`, then **52,702
bytes and 1,382 lines**: the copyright line is asserted only over C++ under
`Unreal/Source`, so Python headers are cosmetic; the pinned config hash is
computed over a canonical JSON dump whose members do not include the
project name or the asset and script prefixes, so a rename cannot move it;
one check's self-file tuple names a path the check can never yield, which
is dead code and was **deliberately left uncorrected**; and the prohibited
token list matches neither "Uludağ Formula" nor "UludagFormula".

**The lockstep rule (051.2), still in force:** any commit that renames a
module directory, a `.Build.cs`, a `.Target.cs`, the `.uproject` or a
project ini **must patch `af_static_validate.py` in the same commit**.
There is no rename API here — every move is create-then-delete and every
edit is a full retranscription.

### D-052 — wave 1.5 closed, and the byte-delta safeguard

Seven items in three batches, all ten check runs green, evidence pull
requests closed unmerged.

The durable output is the **byte-delta safeguard (052.3)**: predict the
size change of a write before making it, then compare against the size the
write API returns. `ApexFormula` to `UludagFormula` is plus two bytes; the
display form is plus four. Seven of eight predictions matched exactly.
This matters because **Markdown has no compile gate (052.5)** — byte-delta
prediction is the only automated truncation detector documentation has.
Note the limit stated in 052.6: the returned size proves *length*, not
*fidelity*.

Also closed here: a syntax check is not a self-test, and continuous
integration never invokes `--self-test` on the guards, which is why
OPEN-051-B could not be settled as a side effect and remains open.

### D-053 — timing discipline and a rehearsal that failed

A batch is not complete until all ten runs report a terminal status;
**nine of ten with any run still in progress must be rejected, never
rounded up**. The local file-creation tool does not behave like `mkdir -p`
— creating under a missing parent fails and the content is discarded.

**OPEN-053-A** was opened here and is still open: a roughly 13 KB
reconstruction of `af_mesh_quality.py` was deleted without ever being
executed, so it proved nothing. The rule it produced is quoted throughout
this repository — *evidence about a file must be produced by that file,
byte for byte*.

D-053.8 is the honest ceiling on all of it: the green batches prove that
the Python compiles under 3.9 and 3.12, that the static entry point exits
zero, and that a headless Blender smoke test completes. Nothing more.

### D-054 — gate-scoped coverage

Total coverage has no fixpoint, because the file that measures coverage
cannot be inside its own measurement. Coverage is therefore scoped to
gates: **a commit owes a CI batch if and only if it touches `.py`, `.cpp`,
`.h`, `.cs`, `.ini`, `.uproject`, `.yml` or `.yaml`.** Markdown owes
nothing and is *permanently uncovered by design* — no step in either
workflow parses, lints or compiles it. This is the rule under which every
documentation commit in this milestone, including this one, owes no batch.

### D-055 — the module names are frozen

The rename ladder was costed and refused: 61 file recreations, 122 write
calls and five full retranscriptions of a 52,702-byte guard, none of it
compile-verifiable in this environment, with every intermediate state
strictly worse than either endpoint. `ApexFormulaCore`, `…Vehicle`,
`…Race`, `…UI`, `…Editor`, `…Tests`, the `.uproject`, the `.Target.cs`
files and the `Unreal/Source` directory names **will not be renamed**.

Two findings worth carrying forward. The guard has exactly three directory
enumeration sites and **no check asserts that every directory under
`Unreal/Source` appears in the module list**, so a stray module directory
is not caught. And D-055.6 records the technique used repeatedly since: a
directory listing requesting only name, size and blob hash returns every
blob hash and byte count **without downloading any body**, which combined
with computing the git blob hash locally proves a cached copy is byte
identical to the repository copy for a few hundred bytes of traffic.

### D-056 — the pull request that could not have worked

Pull request 9 was closed unmerged. The acceptance suite imported roughly
thirty-five names from a module that had **never been pushed**, so it
would have failed on line 1 with `ModuleNotFoundError`. Continuous
integration would **not** have caught it, because `compileall` compiles
without importing. This is the direct ancestor of the D-058 sub-ruling
that the import must be hard and unguarded.

The bodywork document landed on `main` carrying a section 0 absence banner
and preserving four geometry defects rather than hiding them: inward-wound
lofts, endplates breaching the 5.600 m envelope, a halo apex without tube
radius, and non-monotone convergence.

### D-057 — erratum discipline

`MILESTONE_PLAN.md`, 24,860 bytes, carries three statements falsified by
D-055. The corrections were published **in the decision log** and the file
was left byte identical. This is the rule invoked twice in section 1.1
above and it is the reason no closed file in this repository is ever
edited.

### D-058 — the bodywork re-authored in two slices

Slice 1, the profile core: `af_bodywork_profile core: 22 cases, 72
assertions, 0 failures`, with the thickness peak located at
`0.545590827299` — the argmax of `sqrt(s)*(1-s)*(1+0.6*(1-s))` over
200,001 samples, reported to twelve places. The loft convergence ladder
runs 6 → 0.04212, 12 → 0.04910, 24 → 0.04995, 40 → 0.04990, 400 →
0.05000, which is **not monotone** and is recorded as such.

Slice 2, the acceptance suite: `af_bodywork_selftest: 42 cases, 376
assertions, 0 failures`. **The 376 replaces the historical 514 and the two
must never be reconciled** — they count different things in different
modules, and adjusting either to match the other would destroy the record.

Four sub-rulings still in force: one merged 42,219-byte geometry module
rather than a split; a hard import with no guard, because *a gate that can
silently skip itself is not a gate*; the suite is committed before the
module it tests; and the 2,662-byte stand-in configuration **must never be
pushed**.
