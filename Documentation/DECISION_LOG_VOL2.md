# Decision Log — Volume 2

This volume continues `DECISION_LOG.md`. It starts at **D-047**.

## Why the log is split

`DECISION_LOG.md` is 50,726 bytes. Every edit in this repository is a
full-file retranscription — there is no patch interface. Appending one
paragraph therefore means re-emitting 50 KB of text and hoping nothing
is lost in transit. That is a bad trade for a single table row, and it
was correctly refused for D-045 and D-046.

The problem is what happened next: it was refused a third time for
D-047, and at that point the ledger had quietly stopped recording
decisions. A ledger that is too expensive to append to is not a ledger.

Splitting into volumes removes the trade. Volume 1 is frozen and remains
authoritative for D-001 through D-044. This volume is small, so
appending is cheap. When this volume becomes large, volume 3 opens. The
cost of recording a decision must never again scale with the number of
decisions already recorded.

**Rule adopted:** open a new volume once the current one passes roughly
20 KB.

## Index

| Identifier | Title | Status |
| --- | --- | --- |
| D-045 | Track drift guard as a standalone tool | merged, registered retrospectively |
| D-046 | Pin the pipeline configuration digest and enforce it | merged, registered retrospectively |
| D-047 | Mesh quality gate, and the inward winding fix | merged, registered retrospectively |
| D-048 | Rename: Apex Formula becomes Uludağ Formula | wave 1 merged, later waves planned |
| D-049 | Documentation wave scope, triage rule, and evidence procedure | merged |
| OPEN-M4-01 | Collision proxies authored from the wrong datum | open |

Next free decision identifier: **D-050**.

---

## D-045 — track drift guard as a standalone tool

*Registered retrospectively. The implementation record is in
`MILESTONE_3_IMPLEMENTATION.md`.*

**Decision.** Enforce circuit-geometry drift with a new self-contained
file under `Tools/` rather than by editing the circuit generator.

**Reasoning.** The generator is large and every edit is a full-file
rewrite. Precedent D-037 already established that guards live in their
own file, import nothing from each other and depend only on the standard
library, so that one guard failing to import cannot take the others
down with it.

**Consequence.** 27 self-test cases. Wired into `validate.yml` in the
house shape adopted as D-030: two adjacent steps, self-test first, real
run second.

**Status.** merged. *automatically validated* at job level in CI.

---

## D-046 — pin the pipeline configuration digest and enforce it

*Registered retrospectively. The full implementation record, including
the evidence tables, is section 1 of `MILESTONE_4_IMPLEMENTATION.md`.*

**Decision.** Pin the full sixty-four character digest of
`effective_config()` in a new standalone guard and fail continuous
integration when the module drifts from the pin, or when any document
quotes a stale value.

**Reasoning.** Under D-041 the `DESIGN` dictionary is the single source
of truth for every generated dimension. One edited float silently
falsifies every document quoting the digest. Documentation rots quietly;
a guard does not.

**Order of work, and why it mattered.** The documented value was
independently reconstructed and executed **before** the guard was
written. Had the guard been written first and the pin taken from the
documentation, a wrong pin would have been frozen into CI and CI would
then have defended the error. The reconstruction agreed exactly.

**Consequence.** `Tools/af_config_hash_guard.py`, 26,517 bytes, standard
library only, 44 self-test cases. Three checks: drift of the module
against the pin, stale claims in tracked Markdown and workflow files,
and agreement of the sixteen-character short form emitted by
`describe()`.

**Load-bearing evidence.** Mutating `wheelbase_m` from 3.600 to 3.601
produced a completely unrelated digest and the guard reported both the
drift and every document left quoting the old value, exiting 1. A guard
that only ever passes proves nothing.

**Standing obligation.** Any change to `af_pipeline_config.py` must
re-pin the digest and update every document quoting it **in the same
commit**.

**Status.** merged. *automatically validated* at job level in CI.

---

## D-047 — mesh quality gate, and the inward winding fix

*Registered retrospectively. The full implementation record is section 3
of `MILESTONE_4_IMPLEMENTATION.md`.*

**Decision.** Add a mesh-level quality gate that runs in continuous
integration without Blender, and fix whatever it finds in the generator
rather than relaxing the check.

**Reasoning.** Every earlier guard checks text. None had ever looked at
a mesh. A mesh can be inside out, non-manifold, degenerate or duplicated
while every text guard stays green. The pure-Python generators were
already capable of being exercised headlessly; that capability was
simply unused.

**Consequence.** `Tools/af_mesh_quality.py`, 773 lines, thirteen check
families, 46 self-test cases. Edge manifoldness, edge orientation and
signed volume are the three that detect an inside-out mesh.

**What it found.** `box_mesh` wound every face inward. A unit cube
returned signed volume `-1.0`. Every box-derived part in the pipeline
carried inverted normals.

**The decision that matters.** The generator was fixed; the expectation
was not relaxed. A gate that is loosened the first time it fires is
theatre. Corrected winding:

```
[(3,2,1,0), (5,6,7,4), (1,5,4,0), (2,6,5,1), (3,7,6,2), (0,4,7,3)]
```

which yields `+1.0`. Cylinder winding was audited in the same pass and
written down so it cannot regress silently.

**Side effect.** Check 11 was split into C11c and C11d to expose, rather
than conceal, the collision proxy datum defect. Audit check count
273 → 274. See OPEN-M4-01.

**Status.** merged. *automatically validated.* **Not visually
confirmed** — the Blender Face Orientation overlay has still not been
used on this geometry.

---

## D-048 — rename: Apex Formula becomes Uludağ Formula

*The full implementation record is section 4 of
`MILESTONE_4_IMPLEMENTATION.md`.*

**Decision.** Rename the product to **Uludağ Formula**. Adopt three
distinct name forms. Rename the display identity and the project and
module identifiers. **Retain `AF_` and `af_` as a documented internal
code name.**

**The three forms.**

| Role | Form |
| --- | --- |
| Product name | `Uludağ Formula` |
| Identifier form | `UludagFormula` |
| Internal code name | `ApexFormula` / `AF_` |

This is forced, not chosen. Unreal Build Tool requires module name,
directory name and `.Build.cs` class name to be the same ASCII token,
and `ğ` is not available there. It is also unavailable in asset names,
FBX bone names, `.gitattributes` patterns and CI shell paths. It is
legal in ini display strings and Markdown prose, which is exactly where
it is used.

**Scope: option 2 of three.** Option 1 was display identity only,
option 3 additionally renamed `AF_` to `UF_` everywhere. Option 2 —
display identity plus project and module identifiers — was chosen and
option 3 was explicitly dropped.

Why `AF_` is retained:

1. It is embedded in the **bone contract**. Eleven bone names begin with
   it and the static validator asserts on the prefix in four places.
   Renaming breaks the agreement between the Blender rig, the FBX
   export, the Unreal skeleton and the mesh gate simultaneously.
2. `AF_CP_` is the checkpoint prefix baked into two modules carrying 84
   and 68 self-test cases. 152 assertions at risk for no visible gain.
3. Renaming `af_pipeline_config.py` breaks a hard-coded path in the
   digest guard and forces a re-pin in the same commit.
4. Nobody sees it. It is an internal symbol prefix — invisible to a
   player, a recruiter or a repository visitor. Roughly eighty per cent
   of the total cost for zero additional visible value.

**Lockstep rule.** `Tools/af_static_validate.py` hard-codes the old
identity in 87 places and inspects the whole tree atomically on every
push. Every module rename commit must patch the guard's module
dictionaries, path constants and C++ copyright literal **in the same
commit**. There is no valid intermediate state.

**Wave 1, done and verified.** `DefaultGame.ini` and `README.md`, both
chosen precisely because the static guard never reads them — the guard
source was read to confirm that before a byte was written, not assumed.
Ten of ten CI check runs concluded success with start times after both
commits. The accented `ğ` round-trips byte-clean as UTF-8.

**Wave 2 onward: planned, not implemented.** Six module directories, six
`.Build.cs` files, two `.Target.cs` files, the `.uproject`, the
per-project ini together with its UCLASS `Config=` specifier and section
name, the export macros, the module classes, the copyright line in all
65 C++ files, and the corresponding rewrite of the static validator.
Order: Editor → UI → Tests → Race → Vehicle → **Core last**.

**Repository.** Renamed to `UludagFormula` by the author.

**Outstanding.** The author's master specification still fixes the root
identity as `ApexFormula`. Its `AF_` / `af_` provisions remain valid;
only the product name contradicts. It needs updating on his side.

**Status.** wave 1 merged and *automatically validated* at job level.
Waves 2 onward: *not claimed*.

---

## D-049 — documentation wave scope, triage rule, and evidence procedure

**Decision.** Treat wave 1 of D-048 as a bounded, separately recorded
unit of work: rename product prose across the documentation set, change
nothing that any guard reads, and prove it with a purpose-built pull
request rather than by assertion.

**What wave 1 actually covered.** Thirteen commits. One ini display
string, ten files under `Documentation/`, the root `README.md`, and the
two nested `README.md` files under `Unreal/` and `BlenderPipeline/`. The
full table, with commit identifiers and resulting file sizes, is section
3 of `CI_EVIDENCE_VOL2.md`. It is not duplicated here, because two
copies of a table are two chances to disagree.

**Triage-before-rewrite rule, adopted here.** Every candidate file was
fetched and scanned for actual product prose **before** any replacement
text was composed. This is not a formality. It produced a real result:
`MILESTONE_3_CIRCUIT.md` was fetched, scanned, and found to contain no
product prose at all — only circuit identifiers and merge references.
It was therefore **deliberately left untouched**.

The reason this is recorded rather than left implicit: without it, the
absence of a commit for that file is indistinguishable from an
oversight. A skipped file that is not written down is a defect waiting
to be re-discovered. The rule is now standing — a file is skipped only
after it has been read, and the skip is recorded.

**Two files deferred, not forgotten.** `MILESTONE_3_IMPLEMENTATION.md`
(37,137 B) and `VERSION_MATRIX.md` (40,427 B) still carry the previous
product name in prose. Both exceed the size at which a full
retranscription becomes the dominant risk in the change. They are
handled under the volume-split policy already applied to the decision
log and to the CI evidence file, rather than rewritten wholesale.
`DECISION_LOG.md` (50,726 B) stays **frozen** under that same policy.

Deferral is a decision with a stated reason. It is not a backlog item
that quietly never happens, and the state of these files is not to be
described as complete.

**Evidence procedure, corrected.** Check runs in this environment are
readable only through a pull request, and a pull request's check runs
belong to its **head commit**. Work pushed directly to `main` is
therefore invisible to any pull request whose head is a different
branch. That is exactly what happened: PR #9 tracks
`milestone-4-bodywork`, so reading it returned the same frozen batch no
matter how many documentation commits landed on `main`.

Procedure adopted, in this order and no other:

1. Push the work to `main`.
2. Cut a verification branch from `main` **after the final write**, so
   its tip contains everything.
3. Add one marker commit so the pull request has a non-empty diff.
4. Open the pull request, read its check runs, then close it without
   merging.

Acceptance is **10 of 10 `success` with every start time later than the
last documentation commit**. A green batch that started earlier is
evidence about a different tree and is rejected as stale. Step 2's
ordering is load-bearing: a branch cut too early certifies a tree that
is missing the last write.

**What this decision does not do.** It upgrades no milestone status, no
verification label, and no measured value. Wave 1 renamed prose. Every
module identifier, target file, project file and guard constant still
carries the internal code name, and every rewritten document says so on
its own page.

**Status.** merged. *automatically validated* at job level, subject to
the acceptance criteria above.

---

## OPEN-M4-01 — collision proxies authored from the wrong datum

**Status: open. Workaround in place, not a fix.**

| Field | Value |
| --- | --- |
| Opened | during D-047 |
| Symptom | Collision proxies dip up to 45 mm below the chassis floor |
| Cause | `COLLISION_PIECES` is authored from the ground plane instead of from `ride_height_m` |
| Handling | Check 11 split: C11c enforces the envelope with a lower bound of `z = 0`, C11d separately forbids `z < 0` |
| Why deferred | The fix edits `af_pipeline_config.py`, which changes the pinned digest and forces a re-pin under D-046 in the same commit |
| Fix procedure | Re-author `COLLISION_PIECES` from the chassis floor, obtain the new digest with `--print-hash`, update the pin and every document quoting it, one commit |
| Blocked on | Nothing external. Deferred by choice. |

The gate currently passes on geometry authored from the wrong reference,
and the check structure says so explicitly rather than hiding it behind
a widened tolerance. That is the only acceptable form of a workaround
in this repository.

---

## Verification labels

The same labels used elsewhere apply here.

| Label | Meaning |
| --- | --- |
| `statically inspected` | A human or a script read the text. No execution. |
| `automatically validated` | A script executed and returned a pass or fail. |
| `verified by inspection` | Cross-checked against another artefact by reading both. |
| `requires local compilation` | Needs a C++ toolchain that CI does not run. |
| `requires Unreal Editor verification` | Needs the editor open. |
| `requires playtesting` | Needs a human to drive. |
| `not claimed` | Deliberately unproven. Do not infer it. |
