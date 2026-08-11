# Decision Log — Volume 3

Status: **active**
Range: **D-051 onward**
Next free identifier: **D-052**

---

## 0. Why this file exists

The decision ledger is split by size, not by topic. Each volume is closed
once it passes roughly 20 KB, so that a single decision can still be read,
diffed and reviewed without loading a 50 KB file.

| Volume | File | Range | Size at close | Status |
|---|---|---|---|---|
| 1 | `Documentation/DECISION_LOG.md` | D-001 … D-044 | 50,726 B | frozen |
| 2 | `Documentation/DECISION_LOG_VOL2.md` | D-045 … D-050 (+ OPEN-M4-01) | 20,441 B | **frozen** |
| 3 | `Documentation/DECISION_LOG_VOL3.md` | D-051 … | — | **active** |

Volume 2 was closed at 20,441 B immediately after D-050. Nothing may be
appended to it. Volume 1 has been frozen since D-044 and is quoted, never
edited.

Two conventions carried forward unchanged:

1. Commit identifiers are quoted as **8-character** short SHAs. Full
   40-character SHAs are avoided in prose because a 16+ character hex run
   near a configuration-hash anchor is inspected by
   `Tools/af_config_hash_guard.py` check B.
2. A decision records what was **measured**, and separately what was
   **assumed**. Anything not executed is labelled as not executed.

---

## D-051 — Wave 2 opening decision: scope, lockstep rule and sequencing

**Date recorded:** during the wave 2 preparation session, immediately after
wave 1 was closed out.
**Supersedes:** nothing. **Depends on:** D-046, D-048, D-049, D-050.
**Status:** accepted, execution in progress.

### 051.0 Context

The product rename from *Apex Formula* to **Uludağ Formula** was split into
waves by D-048 and D-050:

* **Wave 1 — display identity and documentation prose.** Complete. 18
  commits on `main`, 17 of them covered by two green CI batches (PR #17 and
  PR #18, both 10/10 `success`, both closed unmerged). Commit `2267c6de`
  is pushed but not yet covered by a batch of its own.
* **Wave 2 — modules, `.uproject`, targets, ini, guards.** This decision
  opens it.

The scope boundary from D-048 stands and is restated here so wave 2 can be
read without loading volume 2:

> **Option 2 — apply decision A, drop decision B.** The product identity
> (`ApexFormula` → `UludagFormula` in module names, the `.uproject`, target
> files, ini file and section names, and copyright lines) is renamed. The
> symbol prefix `AF_` / `af_` / `UAF*` / `FAF*` / `AAF*` / `IAF*` /
> `LogAF*` is **not** renamed. It is reclassified from "old product name"
> to **permanent internal code name**.

`Uludağ` is legal in ini display strings and Markdown prose. It is **not**
legal in a module name: Unreal Build Tool requires module name = directory
name = `.Build.cs` filename = C# class name, all ASCII. The ASCII form
`UludagFormula` is therefore the identifier and `Uludağ Formula` is the
display name. The `ğ` is two bytes in UTF-8, which matters when predicting
a file size before a write.

### 051.1 Measured findings that changed the plan

These were read directly from the guard sources on `main`, not inferred
from documentation. Each one is stated with its evidence.

**F-1 — the copyright rule applies to C++ only.**
`Tools/af_static_validate.py` defines, at line 574:

```
COPYRIGHT_LINE = (
    "// Copyright ApexFormula. Original work. "
```

and applies it at line 595 as `text.startswith(COPYRIGHT_LINE)` against the
C++ file set under `Unreal/Source`. A scan of every line in that guard
mentioning `Tools`, `.py` or `Copyright` returns exactly ten lines: the
guard's own header, its own module docstring, three usage examples in its
docstring, the `af_pipeline_config.py` path constant, the two
`COPYRIGHT_LINE` lines, one comment about `AFBoneNameMap.h`, and the label
of the import check. **No check reads a copyright header out of any
`Tools/*.py` file.**

*Consequence:* the `# Copyright ApexFormula.` header line and the
docstrings of the Python tools are **cosmetic**. They can be renamed in
isolation, in any order, with the same near-zero CI risk that wave 1 had.
This was an open question before this session and is now closed.

**F-2 — the pinned configuration hash cannot move under a product rename.**
`Tools/af_config_hash_guard.py` pins

```
EXPECTED_CONFIG_HASH = "c9ef9f7e985a1aaf…"   (64 hex characters)
```

and computes its comparison value as a SHA-256 over
`json.dumps(effective_config(), sort_keys=True, separators=(",", ":"))`
from `BlenderPipeline/scripts/af_pipeline_config.py`.

`effective_config()` returns exactly these keys: `pipeline_version`,
`target_blender_version`, `target_unreal_version`, `units`, `bones`,
`design`, `variant`, `collections`, `materials`, `collision_pieces`,
`lod_ratios`, `face_budget`, `tolerance`, `fbx`, `glb_enabled`.

`PROJECT_NAME`, `ASSET_PREFIX` and `SCRIPT_PREFIX` are **not members of
that dictionary**. The only identity-bearing values inside it are the bone
names and collection names, and every one of those begins with `AF_`,
which Option 2 preserves.

*Consequence:* `PROJECT_NAME = "ApexFormula"` may be changed to
`"UludagFormula"` without moving the pinned hash and without forcing a
D-046 re-pin. `PROJECT_NAME` is read only by `describe()`, whose first line
becomes `UludagFormula pipeline config v0B.1.0`. Check C of the hash guard
constrains `describe()` only in two ways — the short hash must appear, and
no hash-like token that is not a prefix of the computed hash may appear —
and a product name satisfies both trivially.

*Honesty label:* this finding is **read-verified, not execution-verified**.
It follows from the fact that `PROJECT_NAME` does not appear anywhere in
the body of `effective_config()`, which is a structural property of the
source, not an estimate. It has not been confirmed by running the guard,
because neither Blender nor a clone of the repository is available in this
environment. The first wave 2 CI batch will confirm it.

**F-3 — Python docstrings are outside the hash guard's prose scan.**
Check B of `af_config_hash_guard.py` walks `Documentation/`, `Tools/` and
`.github/` but only reads files ending in `.md`, `.yml` or `.yaml`, plus
root-level `.md`. A `.py` file is never yielded. The guard's own
`SELF_FILES` tuple names `Tools/af_config_hash_guard.py`, but since that
path is a `.py` it is never produced by the scanner, so the tuple has no
observable effect. **Recorded as an observation, not corrected** — an
unused constant is not a defect worth a change during a rename wave.

**F-4 — the interface guard is self-contained.**
`Tools/af_validate_interfaces.py` (17,133 B) contains nine occurrences of
the old identity. All of them are in strings, comments, or synthetic test
fixtures built under `tempfile.mkdtemp()`. Its real logic keys only on the
regex for `class … IAF\w+` and on `SOURCE_DIR = Unreal/Source`, neither of
which changes under Option 2. Its `Report` class is a private copy, so it
imports nothing from `af_static_validate.py`. It has 9 self-test cases.

**F-5 — the prohibited-token lists do not collide with the new name.**
`af_static_validate.py` lines 694–702 prohibit `F1`, `FIA`, `FormulaOne`,
`Formula1`, `[Ff]ormula[ _-]1`, `GrandPrix`, `[Gg]rand[ _-][Pp]rix`.
`af_pipeline_config.py` additionally prohibits the tokens `F1`, `f1`,
`FIA`, `fia` inside generated asset names. **"Uludağ Formula" and
"UludagFormula" match none of these.** The name-safety position from
D-042 is unaffected by the rename.

### 051.2 Decision — the lockstep rule

Unreal Build Tool tolerates modules being renamed one at a time. **CI does
not.** `af_static_validate.py` inspects the whole tree on every push, and
it hard-codes the old identity in a module-name list, a dependency
dictionary, an engine-dependency table, dependency prefix filters, the
`.uproject` path and its JSON checks, three module lookups by name, two
target filenames, the C++ copyright literal, the required-ini list, and the
`UCLASS` config specifier plus ini section name.

**Rule:** every commit that renames a module directory, a `.Build.cs`, a
`.Target.cs`, the `.uproject` or the project ini **must patch
`af_static_validate.py` in the same commit**. A commit that renames source
without patching the guard turns CI red immediately and is a defect, not a
work-in-progress state.

There is **no rename API** available in this environment. Every move is
"create at the new path, then `delete_file` at the old path". Directory
moves do not exist. Every edit is a full-file retranscription.

### 051.3 Decision — split wave 2 into a free part and a locked part

Findings F-1, F-2 and F-4 mean that a meaningful slice of wave 2 carries
the same near-zero risk as wave 1. Merging that slice into the atomic
module commits would inflate them for no reason.

**Wave 1.5 — free identity work.** Independent commits, no lockstep, no
guard patch required:

| # | File | Change | Risk |
|---|---|---|---|
| 1 | `BlenderPipeline/scripts/af_pipeline_config.py` | `PROJECT_NAME`, module docstring, section-4 comment | none (F-2) |
| 2 | `Tools/af_config_hash_guard.py` | docstring line 3 | none (F-1, F-3) |
| 3 | `Tools/af_validate_interfaces.py` | header, docstring, fixtures, argparse text, banner | none (F-1, F-4) |
| 4 | `Tools/af_drift_guard.py` | header and docstring, pending its identity map | to be measured |
| 5 | `Tools/af_track_drift_guard.py` | header and docstring, pending its identity map | to be measured |
| 6 | `Tools/af_lap_rules_model.py`, `af_mesh_quality.py` | header and docstring only | to be measured |
| 7 | `Documentation/VERSION_MATRIX.md` | single 40,427 B transcription per D-050.3 | prose only |

**Wave 2A — locked module work.** Atomic, lockstep, one module per commit.

**Explicitly excluded from wave 1.5:** `Tools/af_static_validate.py`. See
051.5.

### 051.4 Decision — migration order, smallest first

Modules are migrated in ascending file count so that the first atomic
commit is the smallest possible test of the lockstep rule:

1. `ApexFormulaEditor` → `UludagFormulaEditor` (4 files)
2. `ApexFormulaUI` → `UludagFormulaUI` (6)
3. `ApexFormulaTests` → `UludagFormulaTests` (9)
4. `ApexFormulaRace` → `UludagFormulaRace` (12)
5. `ApexFormulaVehicle` → `UludagFormulaVehicle` (13)
6. `ApexFormulaCore` → `UludagFormulaCore` (21) — **last**, because it is
   the dependency root and because the `APEXFORMULACORE_API` macro appears
   in the widest set of headers.

Then, in this order: the two `.Target.cs` files, the `.uproject` recreated
as `UludagFormula.uproject`, and `Config/DefaultApexFormula.ini` renamed
**together with** the `UCLASS(Config=ApexFormula)` specifier and the
`[/Script/ApexFormulaCore.AFDeveloperSettings]` section name. Those three
are one semantic change and must not be split across commits.

The two workflow YAML files land **last**. `.github/workflows/validate.yml`
is 8,958 B and has been truncated once before, in an incident repaired by
commit `7617a530`; its returned size must be checked against a prediction
after the write.

### 051.5 Decision — `af_static_validate.py` is touched exactly once

The guard is 52,702 B across 1,382 lines and must be retranscribed in full
for any edit. Every retranscription of a file that size is an opportunity
for silent truncation.

Its identity strings fall into two groups: **structural** (module lists,
dependency dictionaries, `.uproject` and target filenames, ini names,
section name, the C++ copyright literal) and **cosmetic** (its own header
comment and docstring). The structural group is locked to the module
commits by 051.2.

**Rule:** the cosmetic group is **not** renamed separately. Both groups are
changed in a single write, during the module wave. This trades a slightly
larger locked commit for one fewer 52 KB transcription.

### 051.6 Decision — local rehearsal gate

No module commit is pushed until the rename has been rehearsed against a
local copy of the tree, and the rehearsal reproduces:

* `af_mesh_quality.py --self-test` — 46 of 46 cases, exit 0;
* the full static audit — 274 assertions, 0 failures, exit 0.

A rehearsal that does not reproduce the guard's exact assertions is not a
rehearsal. If the local tree cannot be assembled faithfully, this gate is
recorded as **not met** rather than quietly skipped, and the risk is
carried explicitly into the CI batch.

### 051.7 Decision — verification protocol, unchanged

The wave 1 evidence recipe is now the standing method and is reused
verbatim, because it has produced two independent green batches:

1. Push all work to `main`.
2. `create_branch` from `main` **after** the last write. The ordering is
   not optional: a branch cut before the last write does not contain it.
3. Push one marker commit to that branch.
4. Open a **draft** pull request, head = branch, base = `main`.
5. Wait roughly 45 seconds and read the check runs. Expect nine of ten
   green with the headless Blender job still running. **Nine of ten is not
   a pass.**
6. Wait roughly a further 90 seconds and re-read.
7. Accept only **ten of ten `success`**, and only if every job start time
   is later than the marker commit's author date. The second condition is
   what proves the batch is fresh rather than a cached earlier run.
8. Close the pull request **unmerged**. These branches exist to make CI
   observable; none of them may ever be merged.

Branch naming for this wave: `ci/wave2-verify-N`. The first such batch also
retroactively covers commit `2267c6de`, which is currently pushed but
unverified.

### 051.8 Consequences

* Wave 1.5 can proceed immediately and in any order. It does not need a
  rehearsal, because none of its files are read structurally by any guard.
* The riskiest single moment of the whole rename is commit 1 of wave 2A —
  the first time a module directory and the guard change together. If the
  lockstep rule is right, CI stays green. If it is wrong, CI goes red on
  the smallest possible change set, which is exactly why the Editor module
  goes first.
* `Documentation/MILESTONE_3_IMPLEMENTATION.md` remains permanently
  skipped per D-050.2, including through wave 2. It references module
  paths, but it also carries a live configuration-hash claim, and the cost
  of a 37,137 B transcription is not justified by the benefit.

### 051.9 What this decision does **not** claim

Unchanged from every previous milestone, and worth repeating because a
rename is cosmetic work that can easily be mistaken for progress:

* No C++ in this repository has ever been **compiled**.
* The Unreal project has never been **opened**.
* No FBX or GLB has ever been **imported**.
* No mesh has ever been **visually inspected**.
* No lap has ever been **driven**, and no playtest has occurred.
* Neither green CI batch changes any of the above. CI proves that the
  static guards agree with the tree. It proves nothing about the game.

A successful wave 2 means the repository is **internally consistent under
its new name**. That is all it means.

---

## Open items carried into volume 3

| Id | Item | State |
|---|---|---|
| OPEN-M4-01 | Bodywork profile work on branch `milestone-4-bodywork`, draft PR #9 — merge or close undecided | open, carried from volume 2 |
| OPEN-051-A | `af_drift_guard.py` (38,557 B) and `af_track_drift_guard.py` (30,172 B) identity maps not yet taken | open |
| OPEN-051-B | Drift-guard self-test count disagreement: the guard reports 27 cases, `MILESTONE_3_IMPLEMENTATION.md` section 6A says "31 cases over 17 methods" plus 11 mutation tests | open, **do not "fix" without evidence** |
| OPEN-051-C | Commit `2267c6de` has no CI batch of its own; rides along in `ci/wave2-verify-1` | open |
| OPEN-051-D | Volume 2's header says the file "starts at D-047" while its index lists D-045 and D-046 | open, deliberately left unedited — volume 2 is frozen |
| OPEN-051-E | The master specification file still fixes the root identity as `ApexFormula`. Only Umut can update his copy; the repository cannot | open, external |
| OPEN-051-F | Blender verification never performed: Face Orientation overlay with zero red faces, bounds `[5.6, 1.94, 0.94]`, halo apex `0.940` | open, external — requires a machine with Blender |

---

*Next free identifier: **D-052**.*
