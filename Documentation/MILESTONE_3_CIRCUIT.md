# Milestone 3 — Test Circuit Generator

Companion to `MILESTONE_3_IMPLEMENTATION.md`. That document covers the lap
rules model and D-042; this one covers acceptance criterion 5 (race test
environment geometry), decision **D-043**, and the CI evidence for the
Milestone 3 pull requests.

Every claim below carries one of the eight verification labels defined in the
project brief. Nothing is described as working unless the label says how that
was established.

---

## 1. What was built

`BlenderPipeline/scripts/af_circuit_generate.py` (42,975 bytes) generates the
**Crescent Vale Test Circuit** — an invented layout in an invented region,
`Vale Province`, track id `af_test_crescent`.

It is not a copy, a tracing, a rescaling, or an approximation of any real
circuit. It was produced by choosing polygon vertices and corner radii and
letting the fillet maths resolve the rest. The self-test includes an explicit
originality guard (4 cases) asserting that the identifiers carry no real-world
motorsport names.

### Measured layout

Values below are read from an actual run of the script, exit code 0
(`automatically validated`).

| Property | Value |
|---|---|
| track id | `af_test_crescent` |
| display name | Crescent Vale Test Circuit |
| region | Vale Province |
| lap length | 3480.6 m |
| track width | 13.0 m |
| corners | 12 |
| straights | 12 |
| straight distance | 2731.3 m |
| corner distance | 749.3 m |
| centreline samples | 550 |
| grid slots | 20 |
| pit lane | present, 80 kph limit |

### Checkpoints and sectors

| Checkpoint | Index | Station |
|---|---|---|
| `AF_CP_Line` | 0 | 0.0 m — **timing line** |
| `AF_CP_Alpha` | 1 | 556.9 m |
| `AF_CP_Bravo` | 2 | 1148.6 m |
| `AF_CP_Charlie` | 3 | 1740.3 m |
| `AF_CP_Delta` | 4 | 2297.2 m |
| `AF_CP_Echo` | 5 | 2888.9 m |

Sectors: S1 closes at Bravo (index 2), S2 at Delta (index 4), S3 back at the
timing line (index 0).

Six checkpoints rather than three is deliberate. Cut detection gets finer with
more gates, while the three-sector lap still matches what
`Tools/af_lap_rules_model.py` and `UAFSectorTimer` implement. The final sector
closing at index 0 mirrors the C++ exactly.

---

## 2. How the geometry is built

**Closed polygon with fillets.** For each vertex, the incoming and outgoing
unit directions give a signed turn:

```
turn   = normalise(heading_out - heading_in)
t      = radius * tan(|turn| / 2)
entry  = vertex - incoming * t
exit   = vertex + outgoing * t
sign   = +1 if turn > 0 else -1
normal = (-incoming.y * sign, incoming.x * sign)
centre = entry + normal * radius
```

Straight length is the distance from one corner's exit to the next corner's
entry. Closure is guaranteed by construction rather than by iteration, and
the signed turns sum to exactly ±2π — that identity is used directly as the
closure test. The segment list always satisfies
`len(segments) == 2 * len(vertices)`.

Sampling: straights every 8.0 m, arcs every 3°, with
`steps = max(1, ceil(length / step))` emitting `step/steps` ratios so the
closing point is never duplicated. `polyline_length()` recomputes the lap
independently by chord summation, which runs slightly short of the true arc
length — hence `LENGTH_TOLERANCE_M = 0.5`.

### Inputs that are rejected

Each of these is covered by a self-test case:

- fewer than 3 vertices
- a collinear vertex (`|turn| < 1e-9`)
- a non-positive corner radius
- coincident consecutive vertices
- overlapping fillets, where `t_i + t_{i+1}` exceeds the gap between vertices

---

## 3. Verification

### Self-test — `automatically validated`

`python3 BlenderPipeline/scripts/af_circuit_generate.py --self-test` runs
**84 cases across 11 methods**:

| Method | Cases |
|---|---|
| corner resolution | 7 |
| closure | 5 |
| lap length | 10 |
| overlapping fillets rejected | 1 |
| degenerate inputs rejected | 4 |
| checkpoints | 11 |
| sectors | 7 |
| track definition | 11 |
| validator catches bad definitions | 16 |
| determinism | 3 |
| agreement with lap rules model | 5 |
| originality guard | 4 |

Result: **84 passed, 0 failed, exit 0.**

The self-test is wired into the `static-validation` job as its own step:

```yaml
- name: Circuit generator self-test
  run: python3 BlenderPipeline/scripts/af_circuit_generate.py --self-test
```

This step is deliberately separate from the `compileall` step. `compileall`
byte-compiles every script but executes none of them — without a dedicated
execution step the self-test would compile cleanly and prove nothing. The step
carries no `continue-on-error`, so a green job **is** the evidence that all 84
cases ran on the runner and passed.

Scope note, added with D-044: that inference is drawn at **job** level. Check
runs expose `name`, `status` and `conclusion` only; step-level logs are not
retrievable by the tooling used in this project. See `CI_EVIDENCE.md` §6.

### What is NOT verified

- `build_in_blender()` has **never executed** — no Blender is available in the
  authoring environment. Label: `requires Blender execution`. It is written to
  create an `AF_Circuit` collection containing an `AF_CircuitSurface` quad
  ribbon plus one empty per checkpoint, but no mesh has ever been produced.
- Nothing in this repository has ever been compiled. The C++ side of the track
  contract remains `requires local compilation`.
- No FBX import, no editor load, no playtesting, no visual inspection of the
  circuit. The layout is correct arithmetically; whether it is *enjoyable to
  drive* is unknown and untestable from here.

---

## 4. D-043 — circuit layout values live in the generator, and the validator
mirror is hand-maintained

**Status:** accepted, with a named risk. Partially superseded by **D-044** —
see the amendment at the end of decision B.

### Decision A — layout values are not in `DESIGN`

Cross-Milestone Rule 7 binds **vehicle** dimensions to
`af_pipeline_config.py::DESIGN`, so that the Blender rig and the Unreal
vehicle cannot silently disagree about wheelbase or track width. Circuit
geometry is a different concern with a different consumer: no Unreal vehicle
class reads the lap length or the corner radii. Putting the polygon into
`DESIGN` would widen a config surface that exists to solve a problem the
circuit does not have.

Layout values therefore live in the generator itself. Rule 7 is not weakened —
it still says exactly what it said, and the vehicle values it governs are
unchanged.

### Decision B — `validate_track_definition()` mirrors the C++ by hand

`validate_track_definition()` reimplements `UAFTrackDefinition::ValidateSelf()`
in Python: the same checks, in the same order, against the same thresholds.
Nothing mechanically ties the two together. If someone edits the C++ validator
and not the Python one, they will diverge silently.

This is the **same class of drift risk as D-042**, and it is recorded rather
than hidden. Two mitigations are in place:

1. `test_validator_catches_bad_definitions` mutates a known-good definition
   **16 different ways** and asserts the specific error string produced by
   each. The mirror is therefore proven to *reject* bad input, not merely to
   accept good input — a validator that returns "fine" unconditionally would
   fail 16 cases.
2. `test_agreement_with_lap_rules` (5 cases) checks the generated checkpoint
   order against `Tools/af_lap_rules_model.py`, so a checkpoint-ordering change
   in one place breaks the other.

~~Neither mitigation is automation across the language boundary. That gap is
real and is the reason this decision is written down.~~

**Amended by D-044.** The struck-through sentence is kept visible rather than
deleted, because it was an accurate statement of the risk and the record
should show when and how the risk changed rather than presenting the current
state as if it had always held.

What changed, precisely: D-044 added `Tools/af_drift_guard.py`, which is
automation across the language boundary and which runs in CI on every push
and pull request. It closes that gap **for the D-042 lap-rules mirror only** —
`UAFSectorTimer` / `SectorTimer` and `UAFLapValidator` / `LapValidator`.

What did **not** change: the guard's `CLASS_PAIRS` table does not include
`UAFTrackDefinition`, and none of its 16 behavioural rules reference
`ValidateSelf()` or `validate_track_definition()`. **Decision B's mirror is
still hand-maintained and still unguarded.** After D-044 it is the *remaining*
instance of this drift class in the repository, not one of two.

| Mirror | Decision | Automated parity check |
|---|---|---|
| `UAFSectorTimer` ↔ `SectorTimer` | D-042 | yes — D-044, checks A/B/C |
| `UAFLapValidator` ↔ `LapValidator` | D-042 | yes — D-044, checks A/B/C |
| `UAFTrackDefinition::ValidateSelf()` ↔ `validate_track_definition()` | D-043 B | **no — open gap** |

The 16 mutation cases and the 5 agreement cases remain the only mitigations
here, and both test the Python side against itself. Neither can observe the
C++ file. Closing this properly means extending `CLASS_PAIRS` and the `RULES`
table in `Tools/af_drift_guard.py` to cover the track definition pair; that
work is **not** scheduled and is **not** claimed.

---

## 5. CI evidence — Milestone 3 pull requests

All merged with every distinct check name green. Label:
`automatically validated`.

| PR | Contents | Merge commit |
|---|---|---|
| #5 | `Tools/af_lap_rules_model.py` (68 self-test cases) plus the workflow step that executes it | `7ec380e14fe315a245a4898c79dee3c7aef0650b` |
| #6 | `Documentation/MILESTONE_3_IMPLEMENTATION.md` | `6b8038fa05fd5a6a40e2fc1dbf7ef6febbfa5e1a` |
| #7 | `BlenderPipeline/scripts/af_circuit_generate.py` (84 self-test cases), workflow step, workflow restore | `7617a530392d155039a4ea81e5ed032f0b0f3d3f` |
| #10 | `Tools/af_drift_guard.py` (31 self-test cases, 11 mutation tests) plus two workflow steps — **D-044** | `bf602b2c053fb886a0d83741d4e6f8c51b6003dd` |

### PR #7 check runs

Ten check runs, all `success`:

| Check | Duration |
|---|---|
| Static validation (no engine, no DCC) | 7 s, 10 s |
| `af_static_validate (py3.12)` | 6 s, 8 s |
| `af_static_validate (py3.9)` | 15 s, 17 s |
| Python syntax check | 5 s, 6 s |
| Blender smoke test (headless) | 38 s, 40 s |

Each name appears twice because push and pull-request triggers create parallel
runs with identical job names. On PR #7 both twins completed; on earlier PRs
one twin has stayed `queued` indefinitely, which is a GitHub scheduling
artefact and not a failure. The merge criterion used throughout is **every
distinct check name has a green result**, not "all N runs finished".

Job duration is recorded for completeness only and is **not** evidence of
anything. The same passing Blender job has taken 34 s, 36 s, 37 s and roughly
8 minutes across runs.

### PR #10 check runs

Every distinct check name concluded `success`. Workflow runs observed:
`31513676365`, `31513676386`, `31513773974`, `31513774193`.

The merge diff is **2 files, +1132 / −0**: `Tools/af_drift_guard.py` +1113 as
a new file and `.github/workflows/validate.yml` +19 as a modification. Zero
deletions on the workflow file is direct evidence that the PR #7 truncation
class of bug did not recur. Full detail in `CI_EVIDENCE.md` §6A.

### Blender version note

The `Blender smoke test (headless)` job resolves and runs **Blender 5.2 LTS**
on the runner. An earlier claim in this project that "Blender 5.2 may not
exist" was wrong; it was retracted in writing in `VERSION_MATRIX.md` §5.33,
`DECISION_LOG.md` D-039 and `CI_EVIDENCE.md` §5. The pin stays at 5.2 and must
not be reverted to 4.x.

---

## 6. Milestone 3 acceptance status

**Partially delivered.** Not complete — Cross-Milestone Rule 1 forbids a
completion claim without labelled evidence, and two criteria have none.

| # | Criterion | Status | Label |
|---|---|---|---|
| 1 | Lap timing and sector splits | Implemented in C++, mirrored in Python, 68 cases pass, mirror parity enforced in CI | `automatically validated` (model + parity) / `requires local compilation` (C++) |
| 2 | Lap invalidation rules | Implemented and mirrored, first-cause-wins semantics tested, mirror parity enforced in CI | `automatically validated` (model + parity) / `requires local compilation` (C++) |
| 3 | Checkpoint ordering and direction | Implemented and mirrored | `automatically validated` (model only) / `requires local compilation` (C++) |
| 4 | Session phases and types | Enums and structs authored | `requires local compilation` |
| 5 | Race test environment geometry | Generator authored, 84 cases pass, layout produced; validator mirror **unguarded** | `automatically validated` (maths) / `requires Blender execution` (mesh) |

The honest summary: the *rules* of a valid lap are specified, mirrored, tested,
and — since D-044 — mechanically proven to be the same rules on both sides of
the language boundary; the *circuit* is specified and tested arithmetically,
with its C++/Python mirror still hand-maintained; and **none of it has been
compiled, imported, or driven.** Milestone 3 becomes complete when a human
with Unreal 5.8 and Blender 5.2 compiles the module, runs the generator inside
Blender, imports the result, and drives a lap that the validator accepts and a
second lap that it correctly rejects.
