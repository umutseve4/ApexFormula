# Decision Log — Volume 3

Status: **active**
Range: **D-051 onward**
Next free identifier: **D-053**

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

*Honesty label:* this finding was **read-verified, not execution-verified**
when D-051 was written. It has since been promoted to execution-verified
by CI batch 1 (PR #19). See D-052.1.

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

## D-052 — Wave 1.5 closure record and the corrections it forced

**Date recorded:** immediately after CI batch 3 (PR #21) returned 10/10.
**Supersedes:** nothing. **Amends:** D-051 sections 051.1, 051.2, 051.3.
**Status:** accepted. Wave 1.5 is closed.

### 052.0 Statement

**All seven wave-1.5 items are shipped to `main` and covered by a green CI
batch.** Three batches were required, all of them 10/10 `success`, all of
them closed unmerged. Wave 1.5 is therefore **content complete and
CI-verified**, which is the strongest label available in this environment
and is still weaker than "working".

| # | File | Commit | Size | Delta | Substitutions | Batch |
|---|---|---|---|---|---|---|
| 1 | `BlenderPipeline/scripts/af_pipeline_config.py` | `86d74ecc` | 30,922 B | +12 B | 6 | #19 |
| 2 | `Tools/af_validate_interfaces.py` | `f1cea387` | 17,155 B | +22 B | 11 | #19 |
| 3 | `Tools/af_config_hash_guard.py` | `aa5283c7` | 26,519 B | +2 B | 1 | #19 |
| 4 | `Tools/af_drift_guard.py` | `baa6427b` | 38,569 B | +12 B | 4 (predicted +8) | #20 |
| 5 | `Tools/af_track_drift_guard.py` | `d2afee20` | 30,180 B | +8 B | 4 | #20 |
| 6a | `Tools/af_lap_rules_model.py` | `62477469` | 30,250 B | +8 B | 4 | #21 |
| 6b | `Tools/af_mesh_quality.py` | `cc85f950` | 30,783 B | +8 B | 4 | #21 |
| 7 | `Documentation/VERSION_MATRIX.md` | `edfd74ba` | 40,439 B | +12 B | 3 (display form) | #21 |

Supporting documentation commits covered by the same batches:
`2267c6de` (VOL2 close), `bb9a83e2` (VOL3 open, D-051), `d20d041c`
(CI_EVIDENCE_VOL3 open).

### 052.1 F-2 is promoted to execution-verified

D-051 labelled F-2 "read-verified, not execution-verified". Item 1 changed
`PROJECT_NAME` to `UludagFormula` and batch 1 ran the digest guard's check
A twice, both `success`. The pinned digest did not move. **No D-046 re-pin
is required, and the largest risk carried into wave 2 is closed by
measurement rather than by argument.**

### 052.2 The lockstep rule is broader than D-051.2 stated

D-051.2 named `af_static_validate.py` as the artifact that must be patched
in the same commit as a module rename. Reading the remaining tools proved
that is **necessary but not sufficient**. Module *directory* names are also
embedded as path constants, docstrings and prose in four further artifacts.

Measured inventory:

| Artifact | Old-identity carrier | Module named |
|---|---|---|
| `Tools/af_track_drift_guard.py` | `PATH_TRACK_CPP` | Race |
| `Tools/af_drift_guard.py` | `PATH_TYPES_H` | Core |
| `Tools/af_drift_guard.py` | `PATH_SECTOR_CPP`, `PATH_VALIDATOR_CPP`, module docstring | Race |
| `Tools/af_lap_rules_model.py` | module docstring, two lines | Race |
| `Documentation/VERSION_MATRIX.md` | section 5.21, section 5.28 | Race, Vehicle |
| `Documentation/VERSION_MATRIX.md` | section 5.26, section 5.28 | Core, Editor |
| `Tools/af_mesh_quality.py` | **none** — dynamic generator lookup | — |

**Amended rule.** The atomic commit set per module is:

* **Race** — five artifacts in one commit: `af_static_validate.py`,
  `af_track_drift_guard.py`, `af_drift_guard.py` (constants **and**
  docstring), `af_lap_rules_model.py` (docstring), `VERSION_MATRIX.md`
  (5.21 and 5.28).
* **Core** — three artifacts: `af_static_validate.py`, `af_drift_guard.py`,
  `VERSION_MATRIX.md` (5.26 and 5.28).
* **Vehicle** — `af_static_validate.py` plus `VERSION_MATRIX.md` (5.21,
  5.28).
* **Editor** — `af_static_validate.py` plus `VERSION_MATRIX.md` (5.26).
* **UI, Tests** — `af_static_validate.py` only, on current evidence.

`af_mesh_quality.py` is the negative control that makes the rule
believable: it was renamed alone, with no companion patch, and CI stayed
green. The rule is a property of artifacts that hard-code module directory
names, not a blanket property of `Tools/`.

The eight strings deliberately left in `VERSION_MATRIX.md` are enumerated
in `Documentation/CI_EVIDENCE_VOL3.md` section 7.4 and in OPEN-052-B below.
They are **not defects**. Renaming them before their module exists would
make the document describe a tree that does not exist.

### 052.3 Byte-delta arithmetic is the transcription safeguard

Every edit in this environment is a full-file retranscription. There is no
patch mode. The only cheap, automatic check that a 30–40 KB rewrite was not
silently truncated is to predict the resulting size and compare it with the
size the write API returns.

Two substitution forms, measured, not assumed:

| Form | Replacement | Cost per substitution |
|---|---|---|
| Identifier | `ApexFormula` (11 B) → `UludagFormula` (13 B) | **+2 B** |
| Display | `ApexFormula` (11 B) → `Uludağ Formula` (15 B) | **+4 B** |

The display form is 15 bytes and not 14 characters' worth: `ğ` is two bytes
in UTF-8. **This arithmetic must always be done in bytes, never in
characters.** Item 7 confirmed it exactly: three display substitutions,
+12 B, zero deviation.

Result across wave 1.5: seven of eight rewrites matched their prediction
exactly. The single miss is item 4, discussed next.

### 052.4 OPEN-052-A is resolved — cosmetic only

`af_drift_guard.py` grew +12 B on four substitutions where +8 B was
predicted. Truncation is excluded: both `Python syntax check` jobs in batch
2 compiled the module and reported `success`, and a truncated Python file
does not compile. A full re-read confirmed every rule, every self-test
method and every path constant present and unmodified. **The delta is
cosmetic whitespace with no functional impact.**

**The limit of that resolution is recorded explicitly.** A syntax check is
not a self-test. CI compiles the guards; it never invokes `--self-test` on
any of them. This was confirmed again in batch 3. Therefore:

* the guards' internal assertion counts remain **unmeasured**;
* **OPEN-051-B stays open** — the drift guard's banner claims 27 cases, the
  documentation claims 31 over 17 methods, and a static reading of the
  dispatcher counts 16 methods emitting 6 + 5 + 4 + 1 + 11 + 4 = **31**.
  The documentation reconciles with the code; the guard's own banner is the
  outlier. **Do not "fix" either number without running the self-test.**

### 052.5 Markdown has no compile gate

Python rewrites have a real safety net: the CI syntax check. Markdown
rewrites have **none**. No workflow parses, lints or renders Markdown.

**Consequence, and it is a rule, not an observation:** for every Markdown
rewrite the byte-delta prediction is mandatory and is the only automated
truncation detector available. A Markdown write whose returned size does
not match the prediction must be re-read in full before the session moves
on. This applies to the largest files in the repository, including
`VERSION_MATRIX.md` at 40,439 B.

### 052.6 Corrections to recorded facts

* `BlenderPipeline/scripts/af_circuit_generate.py` is **43,731 B**, not the
  figure quoted in earlier planning notes.
* The inline read and write ceiling is now measured at **≥ 40,439 B**.
  `VERSION_MATRIX.md` was fetched whole and rewritten whole through the
  same channel at that size without truncation. Files above this size have
  not been tested.
* `create_or_update_file` returns `content.size`, `content.sha`,
  `commit.sha` and `commit.author.date` inline. A separate confirmation
  read is therefore unnecessary for the size check — but size alone is
  **not** proof of fidelity, only of length.

### 052.7 CI timing and trigger behaviour

Five batches now agree:

* jobs start **5 – 28 s** after their triggering event;
* a batch completes within **~70 s**;
* one 55-second wait followed by a single read is sufficient;
* a repeat read must vary at least one argument, or the harness rejects it
  as an identical call.

Batch 3 added a new observation. Its ten runs arrived in **two triggering
waves** — five at the marker push, five when the pull request was opened
three minutes later. Both waves post-date the marker, so the acceptance
rule held, and the total was still exactly ten. **Do not assume a single
trigger group.** Acceptance is judged on the count against the job matrix
and on the timestamp threshold, never on the number of workflow runs.

### 052.8 What wave 1.5 does not claim

Eight files now carry the new identity and five CI batches are green.
Nothing in that sentence describes a game.

* No C++ has been compiled; the engine is not installed here.
* No Unreal project has been opened.
* No FBX or GLB has been imported.
* No mesh has been visually inspected.
* No lap has been driven; no playtest has occurred.
* No guard's `--self-test` has been executed by CI.

Wave 1.5 means: **the tooling layer is internally consistent under the new
name.** That is the whole claim.

### 052.9 Immediate consequences for wave 2A

1. The local rehearsal gate of D-051.6 is now the **blocking** item. It is
   the only route to closing OPEN-051-B, and it must be attempted before
   the first module commit. If the tree cannot be assembled faithfully, the
   gate is recorded as **not met** and the risk is carried explicitly.
2. The Editor module remains commit 1, because it is the smallest possible
   test of the amended lockstep rule of 052.2.
3. `af_static_validate.py` is still touched exactly once, per D-051.5.

---

## Open items carried into volume 3

| Id | Item | State |
|---|---|---|
| OPEN-M4-01 | Bodywork profile work on branch `milestone-4-bodywork`, draft PR #9 — merge or close undecided | open, carried from volume 2 |
| OPEN-051-A | `af_drift_guard.py` and `af_track_drift_guard.py` identity maps not yet taken | **closed** by D-052.2 — both maps taken and both files shipped |
| OPEN-051-B | Drift-guard self-test count disagreement: the guard reports 27 cases, the documentation says "31 cases over 17 methods"; a static reading of the dispatcher counts 31 | open, **do not "fix" without evidence** — CI never runs `--self-test` |
| OPEN-051-C | Commit `2267c6de` has no CI batch of its own | **closed** — covered by batch 1, PR #19 |
| OPEN-051-D | Volume 2's header says the file "starts at D-047" while its index lists D-045 and D-046 | open, deliberately left unedited — volume 2 is frozen |
| OPEN-051-E | The master specification file still fixes the root identity as `ApexFormula`. Only Umut can update his copy; the repository cannot | open, external |
| OPEN-051-F | Blender verification never performed: Face Orientation overlay with zero red faces, bounds `[5.6, 1.94, 0.94]`, halo apex `0.940`, and `af_mesh_quality.py --self-test` at 46/46 | open, external — requires a machine with Blender |
| OPEN-052-A | `af_drift_guard.py` +12 B on four substitutions | **closed** by D-052.4 — cosmetic, no functional impact |
| OPEN-052-B | Old-identity strings deliberately retained until their module commit: `af_drift_guard.py` docstring plus three `PATH_*` constants; `af_track_drift_guard.py` `PATH_TRACK_CPP`; `af_lap_rules_model.py` docstring; `VERSION_MATRIX.md` sections 5.21, 5.26 and 5.28 (eight strings) | open by design — resolved atomically in wave 2A |
| OPEN-052-C | `VERSION_MATRIX.md` section 5.28 quotes "2300 checks" as a Milestone 1 figure and explicitly refuses to re-guess the current count | open by design — **never silently refresh this number** |

---

*Next free identifier: **D-053**.*
