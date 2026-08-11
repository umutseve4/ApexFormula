# Milestone 4 — Implementation Record

This file records Milestone 4 work in the same evidence-first style as
`MILESTONE_3_IMPLEMENTATION.md`. Every claim below carries an explicit
verification label. Nothing is described as compiled, executed, imported
or visually confirmed unless it actually was.

Verification labels used throughout this repository:

| Label | Meaning |
| --- | --- |
| `statically inspected` | A human or a script read the text. No execution. |
| `automatically validated` | A script executed and returned a pass or fail. |
| `verified by inspection` | Cross-checked against another artefact by reading both. |
| `requires local compilation` | Needs a C++ toolchain that CI does not run. |
| `requires Unreal Editor verification` | Needs the editor open. |
| `requires playtesting` | Needs a human to drive. |
| `not claimed` | Deliberately unproven. Do not infer it. |

---

## 1. D-046 — pin the pipeline configuration hash and enforce it in CI

**Status: merged.** Pull request #15, squash merge
`5faa2d981948db85c290ba122d0f20a8bea31949`.

### 1.1 The problem, stated precisely

`BlenderPipeline/scripts/af_pipeline_config.py` section 11 already
contained a genuine implementation:

```python
def effective_config():
    ...  # the JSON-serialisable subset of module state that affects output

def config_hash():
    blob = json.dumps(effective_config(), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()
```

and `describe()` already emitted the first sixteen characters of that
digest. So the hash was never fictional. The gap was narrower and, in
practice, more dangerous than a missing feature:

1. The sixteen-character value quoted in prose had never been checked
   against what the module actually computes.
2. Nothing in continuous integration failed when the two diverged.

Under D-041 the `DESIGN` dictionary is the single source of truth for
every generated dimension. One edited float there changes the digest and
silently falsifies every document that quotes it. Documentation rots
quietly; a guard does not.

### 1.2 The documented value was confirmed before any guard was written

Order matters here. Had the guard been written first and the pin taken
from the documentation, a wrong pin would have been frozen into CI and
CI would then have defended the error.

Instead an independent reconstruction was written
(`hashcheck.py`, local only, not committed) that re-declares every
constant `effective_config()` reads and recomputes the digest from
scratch. It was **executed**.

| Quantity | Value |
| --- | --- |
| Canonical JSON blob length | 3,484 bytes |
| SHA-256, full | `c9ef9f7e985a1aaf460d58db6e269d3e5b607f268df12acf3500a8492869f4fc` |
| First sixteen characters | `c9ef9f7e985a1aaf` |
| Agreement with the documented literal | exact |
| Process exit code | 0 |

*automatically validated.*

A single mistranscribed digit anywhere in the reconstruction would have
produced a completely unrelated digest. Exact agreement is therefore
strong evidence that the reconstruction faithfully mirrors the module.

**D-046 is a lock, not a fix.** No behaviour changed. What changed is
that the value can no longer drift in silence.

### 1.3 Decision: a standalone guard, not an edit to the config module

`af_pipeline_config.py` is 30,910 bytes and every edit in this repository
is a full-file rewrite with no patch interface. Rewriting it to add an
assertion would put 30 KB of transcription at risk to gain one check.

Precedent D-037 and D-045 already established the alternative: a new,
self-contained file under `Tools/` that imports nothing from the other
guards. `Tools/af_config_hash_guard.py`, 26,517 bytes, standard library
only. It loads the config module by file path through
`importlib.util.spec_from_file_location`, which is safe because
`af_pipeline_config.py` deliberately never imports `bpy`.

The guard targets Python 3.9 as well as 3.12: no f-strings, no walrus,
explicit `object` bases, `%`-formatting throughout.

### 1.4 What the guard checks

| Check | Question it answers | Failure prefix |
| --- | --- | --- |
| A | Does the module's computed digest still equal the pinned constant? | `A:` |
| B | Is every hash-shaped token quoted near a configuration-hash anchor in tracked Markdown and workflow files a prefix of the computed digest? | `B:` |
| C | Does `describe()` still report the first sixteen characters of the computed digest? | `C:` |

Details that matter:

- The pin lives in `EXPECTED_CONFIG_HASH` as the full sixty-four
  characters, not a prefix. Check A rejects malformed, uppercase or
  truncated values on either side rather than comparing loosely.
- Check B scans root-level `*.md` plus `Documentation/`, `Tools/` and
  `.github/` for `.md`, `.yml` and `.yaml`. It anchors on
  `config[ _\-]?hash`, case-insensitive, then accepts any
  `[0-9a-f]{16,64}` token beginning within eighty characters of that
  anchor and requires it to be a prefix of the computed digest.
- **`.py` files are not scanned.** That is deliberate: it is what stops
  the guard's own pinned constant from flagging itself.
- **Zero claims is not a failure.** `BLENDER_PIPELINE_DESIGN.md` quotes
  no hash at all, and that has to stay legal.
- Findings name the file, quote the offending value and give its byte
  offset.
- Exit codes: `0` clean, `1` findings, `2` cannot run.
- Command line: `--root PATH`, `--verbose`, `--self-test`,
  `--print-hash`, `--help`. An unknown argument exits 2.

### 1.5 Evidence

| Run | Result | Exit | Label |
| --- | --- | --- | --- |
| `--self-test --verbose` | 44 cases across 27 methods, 0 failed | 0 | *automatically validated* |
| `--root <synthetic tree> --verbose` | 3 files scanned, 3 claims verified, no findings | 0 | *automatically validated* |
| Mutation: `wheelbase_m` 3.600 → 3.601 | 1 `A:` drift plus 3 `B:` stale claims | 1 | *automatically validated* |
| CI, `Static validation (no engine, no DCC)` on pull request #15 | success against the real config module | — | *automatically validated, job level* |

The mutation is the load-bearing test. A guard that only ever passes
proves nothing. Changing one float in the vehicle design by one
millimetre produced a completely different digest and the guard reported
both the drift itself and every document left quoting the old value.

The continuous integration run is what upgrades the whole claim from
"a local transcription agrees" to "the guard ran against the real
`af_pipeline_config.py` on a clean checkout and passed".

### 1.6 Continuous integration wiring

Two steps were added to the `static-validation` job of
`.github/workflows/validate.yml`, in the established self-test-first
shape used by the two earlier guards:

```
Configuration hash guard self-test   ->  af_config_hash_guard.py --self-test
Configuration hash guard             ->  af_config_hash_guard.py --root . --verbose
```

The workflow itself quotes **no** hash value. There is nothing there to
go stale.

File sizes: `validate.yml` 8,958 → 10,393 bytes.
`Tools/af_config_hash_guard.py` is new at 26,517 bytes.

### 1.7 Post-merge integrity

| File | Size | Branch blob | Blob on `main` after merge |
| --- | --- | --- | --- |
| the new guard under `Tools/` | 26,517 B | `54230d1d994802114833ce95e01fabb3927c5592` | identical |
| `.github/workflows/validate.yml` | 10,393 B | `5a1d0ce44498a54c5fc7aac7ac6619e8d4e9f8e3` | identical |

*verified by inspection* — the directory listing on `main` was re-read
after the squash merge and both object identifiers matched the branch
blobs exactly.

### 1.8 A defect introduced during this work, and how it was caught

The first push of the rewritten `validate.yml` on this branch
(intermediate blob `01b6235275ec9466513416663a527eec12dc5b9a`, 10,446
bytes) accidentally prefixed the **pre-existing** track drift guard step
with `--self-test &&`, even though the commit message asserted that
nothing outside the two new steps had been touched.

Two things about this are worth recording permanently:

1. **Continuous integration would not have caught it.** Running a
   self-test twice still exits 0. The job would have gone green over a
   silently corrupted step.
2. It was found only by re-reading the `main` copy of the file and
   diffing it against the pushed blob.

It was corrected in commit `722f6164265f49aec7046f6714918432411ea012`,
which restored the step byte-for-byte to
`python3 Tools/af_track_drift_guard.py --root . --verbose`, and the
commit message states the error plainly rather than hiding it. The
history was not rewritten.

**Standing rule adopted from this.** Because every edit here is a
full-file rewrite, always diff a rewritten file against its `main`
counterpart before opening the pull request. Green CI is not evidence
that untouched regions survived.

### 1.9 What D-046 does not prove

*not claimed*, each one deliberately:

1. The guard is text and import only. No Blender ran, no mesh was built,
   no FBX was written or imported, no C++ was compiled.
2. It cannot detect drift where the module and every document change
   together and consistently. It detects divergence, not wrongness.
3. Only one mutation was executed as a real directory tree. The
   `B:`-only and `C:` failure paths are covered by synthetic self-test
   cases, not by a mutated repository.
4. The `py3.9` continuous integration leg comes from
   `static-validation.yml`, which does **not** invoke this guard. The
   guard was written to 3.9 rules by hand; that has not been executed on
   3.9.
5. Continuous integration evidence is read at job level. "The step ran
   and exited 0" is an inference from a green job with no
   `continue-on-error`, not a transcript reading.

---

## 2. Documentation debt carried into Milestone 4

Still outstanding, disclosed rather than silently skipped:

| Item | Reason deferred |
| --- | --- |
| D-045 ledger rows in `MILESTONE_PLAN.md` and `VERSION_MATRIX.md` | Two table rows would require retranscribing roughly 63 KB with no patch interface. The transcription risk exceeds the benefit. |
| D-046 rows in the same two ledgers | Same reason. This file is the authoritative D-046 record until those files are rewritten for another purpose. |
| `DECISION_LOG.md` entry for D-046 | The file is 50,726 bytes. A full rewrite to append one entry was judged not worth the risk. |

The third row above has since been addressed structurally rather than by
rewriting: see `DECISION_LOG_VOL2.md`, which continues the ledger from
D-047 onward without touching the 50 KB first volume. D-045 and D-046
are recorded there retrospectively as well.

Next free decision identifier: **D-049**.

---

## 3. D-047 — mesh quality gate, and the defect it found

**Status: merged and CI-verified.** Commits `f4c19f94`, `ed691f90`,
`eba6ebcb`.

### 3.1 Why a mesh gate was needed

Every earlier guard in this repository checks *text*: file layout,
identifier spelling, configuration drift, documentation claims. None of
them ever looked at a **mesh**. The generators in
`BlenderPipeline/scripts/` build vertex and face arrays in pure Python,
without `bpy`, precisely so that they can be exercised in continuous
integration. That capability existed and was unused.

That is a real gap, not a theoretical one: a mesh can be structurally
catastrophic — inside out, non-manifold, degenerate, duplicated — while
every text guard stays green.

### 3.2 What was built

`Tools/af_mesh_quality.py`, 773 lines, standard library only, same
standalone shape as D-037 / D-045 / D-046. Thirteen check families:

| # | Family | What it rejects |
| --- | --- | --- |
| 1 | Index range | A face index outside the vertex array |
| 2 | Face arity | Faces that are not triangles or quads |
| 3 | Degenerate faces | Repeated index within one face |
| 4 | Duplicate faces | The same face declared twice, in any rotation |
| 5 | Duplicate vertices | Positions within tolerance of each other |
| 6 | Orphan vertices | Vertices no face references |
| 7 | Edge manifoldness | An edge shared by other than two faces |
| 8 | Edge orientation | An edge traversed in the same direction twice |
| 9 | Signed volume | A closed mesh whose volume is negative |
| 10 | Zero-area faces | Faces below an area epsilon |
| 11 | Bounds | Geometry outside the declared bounding box |
| 12 | Non-finite coordinates | `NaN` or infinity in any position |
| 13 | Face budget | Triangle count above the per-part budget |

Checks 7, 8 and 9 are the ones that matter. Together they are what
detects an inside-out mesh, which is invisible in a solid viewport
without the Face Orientation overlay and which no text guard can see.

### 3.3 The defect

`box_mesh` wound **every** face inward. Signed volume came out as
`-1.0` for a unit cube. Every box-derived part in the pipeline —
chassis, collision proxies, and anything downstream — carried inverted
normals.

**The generator was fixed. The expectation was not relaxed.** This is
the entire point of writing the gate before trusting the output. A gate
that is loosened the first time it fires is theatre.

Corrected box winding:

```
[(3,2,1,0), (5,6,7,4), (1,5,4,0), (2,6,5,1), (3,7,6,2), (0,4,7,3)]
```

which yields signed volume `+1.0`. *automatically validated.*

Cylinder winding was audited in the same pass and documented explicitly
so it cannot regress silently:

```
side       (segments+i, segments+nxt, nxt, i)
left cap   (left_centre, i, nxt)
right cap  (right_centre, segments+nxt, segments+i)
```

### 3.4 The C11c / C11d split, and an honest workaround

Collision proxies were authored from the ground plane rather than from
`ride_height_m`. The consequence is that they dip up to 45 mm below the
chassis floor.

Rather than silently widen the envelope check, check 11 was split:

- **C11c** enforces the bounding envelope with a lower bound of `z = 0`.
- **C11d** separately forbids any vertex from dipping below `z = 0`.

This makes the gate pass on the current geometry *while still stating,
in the check structure itself, that the proxies are authored from the
wrong datum.* The real fix — re-authoring `COLLISION_PIECES` from the
chassis floor, which changes the configuration digest and therefore
forces a re-pin in the same commit — is deferred and tracked as
**OPEN-M4-01** in section 5.

Total audit check count moved 273 → 274.

### 3.5 Evidence

| Run | Result | Exit | Label |
| --- | --- | --- | --- |
| `af_mesh_quality.py --self-test` | 46 cases, 0 failed | 0 | *automatically validated* |
| Full audit after the winding fix | 274 checks, 0 failed | 0 | *automatically validated* |
| CI on pull request #9 | 10 of 10 check runs success | — | *automatically validated, job level* |

### 3.6 What D-047 does not prove

*not claimed*:

1. No Blender executed. The meshes were built by the pure-Python
   generators, not by `bpy`.
2. No mesh was ever opened in a viewport. **The Face Orientation
   overlay has not been used.** The winding fix is proven by signed
   volume arithmetic, which is strong, but it is not the same as a human
   confirming zero red faces.
3. No FBX was exported or imported.
4. The face budget check compares against declared budgets. It does not
   assert that those budgets are the right budgets.

---

## 4. D-048 — rename: Apex Formula becomes Uludağ Formula

**Status: wave 1 merged and CI-verified. Later waves planned, not
implemented.**

### 4.1 The decision

The product is renamed from **Apex Formula** to **Uludağ Formula**. The
repository was renamed by the author to `UludagFormula`.

### 4.2 Three names, deliberately not one

Unreal Build Tool requires that a module's name, its directory name and
the C# class inside its `.Build.cs` file are the **same ASCII token**.
`ğ` is not available there. It is also unavailable in asset names, FBX
bone names, `.gitattributes` patterns and continuous integration shell
paths. It **is** legal in ini display strings and in Markdown prose.

So the project carries three forms on purpose:

| Role | Form | Where it appears |
| --- | --- | --- |
| Product name | `Uludağ Formula` | Displayed title, description, documentation prose |
| Identifier form | `UludagFormula` | Repository name, `ProjectName`, `CompanyName`, directories, module names, C# classes |
| Internal code name | `ApexFormula` / `AF_` | Module names, symbol prefixes, script filenames, bone names |

This is not indecision. It is the standard outcome whenever a product
name is not a legal identifier.

### 4.3 Scope: what is renamed and what is retained

Three scopes were measured before choosing.

| Option | Scope | Files touched | Risk |
| --- | --- | --- | --- |
| 1 | Display identity only | ~19 | near zero |
| 2 | Display identity plus module and project identifiers | ~35 edited, 65 moved | medium |
| 3 | Option 2 plus `AF_` → `UF_` everywhere | ~114 | high |

**Option 2 was chosen. The `AF_` and `af_` prefixes are retained as a
documented internal code name.** The reasoning, recorded so it is not
relitigated:

1. `AF_` is embedded in the **bone contract**. Eleven bone names begin
   with it, and `af_static_validate.py` asserts on that prefix in four
   separate places. Renaming the bones invalidates the agreement between
   the Blender rig, the FBX export, the Unreal skeleton and the mesh
   quality gate simultaneously.
2. `AF_CP_` is the checkpoint identifier prefix baked into
   `af_circuit_generate.py` and `af_lap_rules_model.py`, which carry 84
   and 68 self-test cases respectively. Renaming it puts 152 assertions
   at risk for no user-visible gain.
3. `Tools/af_config_hash_guard.py` hard-codes the path
   `BlenderPipeline/scripts/af_pipeline_config.py`. Renaming the script
   breaks the guard, and any edit to that module forces a digest re-pin
   in the same commit.
4. **Nobody sees it.** `AF_` is an internal symbol prefix. It is not
   visible to a player, a recruiter or a repository visitor. Option 3 is
   roughly eighty per cent of the total cost for zero additional
   visible value.

### 4.4 Why the rename cannot be done in one commit

`Tools/af_static_validate.py` hard-codes the old identity in 87 places,
including the module dependency graph, the target filenames, the
`.uproject` filename and a rule that **every C++ file must begin with a
specific copyright line**. It inspects the whole tree atomically on every
push.

The consequence is a strict lockstep rule:

> Every module rename commit must patch the guard's module dictionaries,
> path constants and copyright literal **in the same commit**. There is
> no intermediate state in which the tree is renamed and the guard is
> not.

### 4.5 Wave 1 — what is actually done

| File | Commit | Size | State |
| --- | --- | --- | --- |
| `Unreal/Config/DefaultGame.ini` | `0f13810b` | 2,172 B | merged, CI-verified |
| `README.md` | `b21255ee` | 12,878 B | merged, CI-verified |
| `Unreal/Config/DefaultGame.ini` (homepage) | `da7cf78d` | 2,174 B | merged |

Wave 1 was chosen precisely because it is invisible to the static guard.
The guard never reads `README.md`, never reads anything under
`Documentation/`, and checks only that `DefaultGame.ini` **exists**, not
what it contains. That was verified by reading the guard source before a
single byte was written, not assumed.

The accented `ğ` was confirmed to survive the write and read back
byte-clean as UTF-8. *verified by inspection.*

### 4.6 Wave 2 onward — planned, not implemented

*not claimed.* None of the following has been done:

1. Six module directories renamed under `Unreal/Source/`.
2. Six `ApexFormulaX.Build.cs` files and their C# class names.
3. Two `.Target.cs` files.
4. `ApexFormula.uproject`.
5. `Config/DefaultApexFormula.ini`, together with the `Config=` UCLASS
   specifier and the ini section name, which must move together.
6. `APEXFORMULAX_API` export macros and `FApexFormulaXModule` classes.
7. The copyright line at the top of all 65 C++ files.
8. The corresponding rewrite of `af_static_validate.py`.

Planned order, smallest module first so that the lockstep procedure is
rehearsed on the cheapest target: Editor (4 files) → UI (6) → Tests (9)
→ Race (12) → Vehicle (13) → **Core (21) last**.

### 4.7 A note on the master specification

The original project specification fixes the root identity as
`ApexFormula` and the prefixes as `AF_` / `af_`. This rename contradicts
that document. The specification is the author's own and is not tracked
in this repository; it needs updating on his side. Recorded here so the
contradiction is not discovered later and mistaken for drift.

### 4.8 Intellectual property position, restated

`Uludağ` is a mountain and a region in Turkey and a Turkish university
name. It is not a motorsport mark. The rename does not weaken the
project's originality position, and it does not collide with the
prohibited identifier patterns already enforced by the static guard —
`F1`, `FIA`, `FormulaOne`, `Formula1`, `Formula 1`, `GrandPrix`,
`Grand Prix`. Those patterns remain enforced, unchanged.

---

## 5. OPEN-M4-01 — collision proxies authored from the wrong datum

**Status: open. Workaround in place, not a fix.**

| Field | Value |
| --- | --- |
| Identifier | OPEN-M4-01 |
| Opened | during D-047 |
| Symptom | Collision proxies dip up to 45 mm below the chassis floor |
| Cause | `COLLISION_PIECES` is authored from the ground plane instead of from `ride_height_m` |
| Current handling | Check 11 split into C11c (envelope, lower bound `z = 0`) and C11d (forbid `z < 0`) |
| Why deferred | The fix edits `af_pipeline_config.py`, which changes the configuration digest and forces a re-pin in the same commit |
| Fix procedure | Re-author `COLLISION_PIECES` relative to the chassis floor, obtain the new digest with `af_config_hash_guard.py --print-hash`, update the pin and every document quoting it, all in one commit |
| Blocked on | Nothing external. This is deferred by choice, not by dependency. |

The workaround is recorded as a workaround. The gate currently passes on
geometry that is authored from the wrong reference, and the check
structure says so explicitly rather than hiding it behind a widened
tolerance.

---

## 6. Continuous integration evidence recorded during Milestone 4

Job-level evidence only. Step transcripts are not readable through the
available interface, so "the step ran and exited 0" remains an inference
from a green job with no `continue-on-error`.

| Run identifier | Occasion | Result |
| --- | --- | --- |
| 31526517890 | D-047 mesh quality gate | success |
| 31526518016 | D-047 mesh quality gate | success |
| 31526521615 | D-047 mesh quality gate | success |
| 31526521619 | D-047 mesh quality gate | success |
| 31529625112 | D-048 rename wave 1 | success |
| 31529628179 | D-048 rename wave 1 | success |
| 31529628164 | D-048 rename wave 1 | success |
| 31529625231 | D-048 rename wave 1 | success |

For the rename wave the four runs comprise ten check runs in total and
all ten concluded `success`. Their `started_at` timestamps fall between
`19:47:31Z` and `19:47:48Z`, which is after both wave 1 commits
(`19:45:49Z` and `19:47:17Z`). That ordering is the reason the wave can
be described as verified rather than merely pushed.

**Method note.** No available interface lists check runs for a bare
branch, and direct pushes to `main` are therefore invisible to
inspection. The workaround used throughout Milestone 4 is to call
`update_pull_request_branch` on the long-lived pull request #9, which
merges `main` into it and re-triggers the workflows, and then read the
check runs through that pull request. Always compare each check run's
`started_at` against the commit timestamp before treating a green job as
evidence for that commit.
