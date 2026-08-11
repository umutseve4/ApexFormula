# ApexFormula — Decision Log

**Document status:** statically authored (Milestone 0A).

**Purpose.** One numbered entry per decision that shapes the project. Each entry records what was decided, why, what was rejected, and how reversible it is. Later milestones append entries; they do not silently edit earlier ones. When a decision is superseded, the original entry stays and gains a "Superseded by" line.

**Date convention.** All entries below were established during Milestone 0A, on **2025-06-01** (project foundation date). Later entries carry their own dates.

**Reversibility scale.**
- **High** — can be changed in a single milestone with local edits.
- **Medium** — changeable, but requires rework across several systems or re-export of assets.
- **Low** — changing it invalidates substantial completed work.

---

## D-001 — Project identity is ApexFormula

**Date:** 2025-06-01
**Decision.** The project is named **ApexFormula**. Asset prefix `AF_`, C++ prefixes `UAF` / `AAF` / `FAF` / `IAF`, Blender script prefix `af_`.
**Rationale.** A single unambiguous identity that carries no real-world motorsport association and produces short, greppable prefixes.
**Rejected.** Any name containing the token `F1`, any real series, team, manufacturer or circuit name.
**Reversibility:** Medium — a rename touches every file, class and asset, but is mechanical.

---

## D-002 — Strict originality constraint

**Date:** 2025-06-01
**Decision.** No real motorsport branding, team names, driver names, sponsor marks, logos, liveries, or exact reproductions of real cars or circuits. The token `F1` must not appear in any project name, filename, class name, asset name, script name, folder name, document title or public-facing term.
**Rationale.** Legal safety and creative independence. The project is a formula-style racing game, not a licensed product.
**Rejected.** "Inspired-by" liveries and thinly renamed real circuits — both were judged to carry the same risk as direct use.
**Reversibility:** Low — every asset produced under this rule assumes it.

---

## D-003 — Fixed technology stack

**Date:** 2025-06-01
**Decision.** Unreal Engine 5.8, Blender 5.2 LTS, Windows, C++ for gameplay architecture, Blueprints for asset assignment/visual configuration/tuning/animation/UI/level configuration, Blender Python for procedural generation and validation, Git plus Git LFS for version control.
**Rationale.** Removes an entire class of recurring debate. Details in `VERSION_MATRIX.md` §1.
**Rejected.** Alternative engines and DCC applications; a Blueprint-first gameplay architecture.
**Reversibility:** Low.

---

## D-004 — Five-layer architecture

**Date:** 2025-06-01
**Decision.** Core, Vehicle, Rules and Timing, Session, Presentation — with dependencies flowing in one direction only. Detailed in `TECHNICAL_ARCHITECTURE.md` §2.
**Rationale.** Keeps simulation testable without the renderer, and keeps presentation replaceable without touching simulation.
**Rejected.** A monolithic gameplay module; a presentation layer permitted to write simulation state.
**Reversibility:** Medium.

---

## D-005 — Six C++ modules

**Date:** 2025-06-01
**Decision.** `ApexFormulaCore`, `ApexFormulaVehicle`, `ApexFormulaRace`, `ApexFormulaUI`, `ApexFormulaEditor`, `ApexFormulaTests`.
**Rationale.** Maps the five layers onto compilable units, plus editor-only and test-only code that must not ship in the runtime.
**Rejected.** A single game module — it makes editor-only code leak into packaged builds.
**Reversibility:** Medium.

---

## D-006 — Component-based vehicle composition

**Date:** 2025-06-01
**Decision.** Vehicle behaviour is composed from components — `UAFTyreSetComponent`, `UAFAeroComponent`, `UAFEnergySystemComponent`, `UAFFuelComponent`, `UAFBrakeComponent`, `UAFDrivetrainComponent`, `UAFVehicleSetupComponent`, `UAFVehicleTelemetryComponent`, `UAFRaceParticipantComponent` — rather than from a deep pawn inheritance chain.
**Rationale.** Each model can be developed, unit-tested and migrated independently at Milestone 10.
**Rejected.** A monolithic vehicle pawn holding all simulation state.
**Reversibility:** Medium.

---

## D-007 — Data-Asset-driven configuration

**Date:** 2025-06-01
**Decision.** Tuning values live in Data Assets, not in code constants or Blueprint literals. Twelve Data Asset types are defined in `TECHNICAL_ARCHITECTURE.md` §5, including `UAFBoneNameMap` and `UAFQualityProfile`.
**Rationale.** Tuning must be changeable without recompilation, diffable, and shareable between the editor and automated tests.
**Rejected.** Config `.ini` files as the primary tuning surface; hardcoded constants.
**Reversibility:** Medium.

---

## D-008 — Prototype vehicle system is Chaos Vehicles behind a compatibility layer

**Date:** 2025-06-01
**Decision.** Milestone 2 uses the engine's Chaos Vehicles system, but every access goes through `UAFVehicleCompatibilityLayer`. No gameplay code calls the engine vehicle API directly.
**Rationale.** Fastest route to a drivable car without committing the project to the engine's model. Full analysis in `VEHICLE_SYSTEM_DECISION.md` §4.
**Rejected.** Building a custom vehicle model immediately (too slow to first playable); using Chaos directly without a layer (blocks D-009).
**Reversibility:** High — that is the entire point of the layer.

---

## D-009 — Long-term vehicle system is a hybrid

**Date:** 2025-06-01
**Decision.** Long term, the engine provides rigid-body dynamics and collision; ApexFormula owns the tyre, aerodynamic, energy, fuel and brake models. Migration order is documented in `VEHICLE_SYSTEM_DECISION.md` §5 and executed at Milestone 10.
**Rationale.** The engine's built-in models are not sufficient for the intended simulation depth, but replacing rigid-body dynamics and collision would be a large cost with little gain.
**Rejected.** Full custom physics including integration and collision; permanent reliance on the engine's vehicle model.
**Reversibility:** Medium — reversible per model, since each is migrated separately behind the layer.

---

## D-010 — Blender is the source of truth for geometry and rigs

**Date:** 2025-06-01
**Decision.** Vehicle geometry, collision proxies, LODs and the armature are generated and validated in Blender. Unreal imports; it does not author geometry.
**Rationale.** Procedural generation is reproducible from config and reviewable as text.
**Rejected.** Modelling inside Unreal; hand-modelled one-off assets as the primary path.
**Reversibility:** Medium.

---

## D-011 — Unreal owns final shading

**Date:** 2025-06-01
**Decision.** Blender exports placeholder materials only. Final material authoring, instancing and shading happen in Unreal.
**Rationale.** Avoids maintaining two divergent material systems, and avoids importing a material library that must then be replaced.
**Rejected.** Authoring production materials in Blender and attempting to translate them on import.
**Reversibility:** High.

---

## D-012 — Central bone-name convention

**Date:** 2025-06-01
**Decision.** Eleven bones: `AF_Root`, `AF_Chassis`, `AF_Steering`, `AF_Wheel_FL/FR/RL/RR`, `AF_Suspension_FL/FR/RL/RR`. Hierarchy: `AF_Root` → `AF_Chassis` → { `AF_Steering`, `AF_Suspension_*` }, with each `AF_Wheel_*` parented to its matching `AF_Suspension_*`. The names are defined once in `af_pipeline_config.py` and mirrored in `UAFBoneNameMap`; they are never hardcoded elsewhere.
**Rationale.** Bone names are the single most fragile contract between Blender and Unreal. Centralising them makes a rename a one-line change plus a re-export.
**Rejected.** Hardcoding bone names at each use site; relying on bone indices.
**Reversibility:** Medium — a rename requires re-export and re-import of every skeletal asset.

---

## D-013 — Explicit unit and axis contract

**Date:** 2025-06-01
**Decision.** Metres inside Blender (scene scale 1.0, 1 BU = 1 m, +X forward, +Z up, +Y vehicle-left); centimetres at the Unreal boundary (1 uu = 1 cm, +X forward, +Y right, +Z up); handedness reconciled by a Y-sign flip; a single constant `CM_PER_UNIT = 100.0` performs the scale conversion. Full statement in `BLENDER_PIPELINE_DESIGN.md` §2.
**Rationale.** Scale and mirroring errors are the classic silent failure of a Blender→Unreal pipeline, and they surface only after significant downstream work.
**Rejected.** Working in centimetres inside Blender; relying on the exporter's automatic conversion without stating the expectation.
**Reversibility:** Low — every exported asset encodes this contract.

---

## D-014 — Replay uses periodic authoritative state snapshots with interpolation

**Date:** 2025-06-01
**Decision.** The replay system records **periodic authoritative state snapshots** of race entities and reconstructs playback by **interpolating between snapshots**. Simulation determinism is **not** assumed and is **not** relied upon. Input-replay (recording inputs and re-simulating) is explicitly rejected as the primary mechanism.
**Rationale.** Reproducing a session by re-simulating recorded inputs requires bit-level determinism across builds, hardware, frame rates and physics substepping. That guarantee does not exist here and would be extremely expensive to establish and maintain. Snapshot-plus-interpolation trades storage for correctness, and correctness is what a replay must deliver. It also degrades gracefully: a dropped or corrupted snapshot costs a short interpolation artefact rather than divergence of the entire replay.
**Consequences.**
- Snapshot rate and payload size become a tuning problem, addressed at Milestone 12.
- The telemetry bus (`UAFTelemetryBus`, `TECHNICAL_ARCHITECTURE.md` §10) is the natural capture point.
- Replay fidelity is bounded by snapshot rate, and this is accepted openly rather than hidden.
- The same snapshot structure is a useful starting point for the Milestone 12 multiplayer-boundary preparation.
**Rejected.** Deterministic input replay; full per-frame state recording (storage cost); replay driven by the presentation layer (wrong ownership).
**Reversibility:** Medium — the capture point is generic, so a future deterministic path could be added alongside, but assets and tooling built on snapshots would need rework.

---

## D-015 — Two quality profiles, permanently separated

**Date:** 2025-06-01
**Decision.** Development Preview and Final Quality are distinct profiles, expressed as `UAFQualityProfile` Data Assets. Preview settings are non-destructive overrides. Preview output is never used for presentation. Weak development hardware never lowers the Final Quality target.
**Rationale.** Prevents the common failure where the project's quality ceiling quietly collapses to whatever the development machine renders comfortably.
**Rejected.** A single scalable quality setting; permanently reducing asset quality to improve editor performance.
**Reversibility:** High.

---

## D-016 — FBX is primary, GLB is optional preview only

**Date:** 2025-06-01
**Decision.** FBX is the production interchange format for skeletal meshes, skeletons, static meshes, collision and LODs. GLB may be produced for quick external viewing but is never an import path and never a source of truth.
**Rationale.** One authoritative path avoids two subtly divergent pipelines.
**Rejected.** GLB or USD as the primary path at this stage.
**Reversibility:** Medium.

---

## D-017 — Validation is a gate, not a report

**Date:** 2025-06-01
**Decision.** `af_validate.py` enforces twenty-one checks (`BLENDER_PIPELINE_DESIGN.md` §4) and writes a JSON report to `BlenderPipeline/reports/`. Reports are committed as plain text. A failing validation blocks export.
**Rationale.** A warning that can be ignored will be ignored. Committed reports make regressions visible in diffs.
**Rejected.** Advisory-only validation; reports written to an ignored directory.
**Reversibility:** High.

---

## D-018 — Driver reference material never enters the repository

**Date:** 2025-06-01
**Decision.** Reference photographs and any biometric-adjacent material stay in a machine-local `LocalReference/` directory, which is excluded by `.gitignore` by name. Nothing from it is committed, packaged or transmitted. The seven prohibited claims in `DRIVER_PIPELINE_DESIGN.md` §2 are binding.
**Rationale.** Privacy is not a feature to be added later, and a photograph committed once is in history forever.
**Rejected.** Committing "just the low-resolution ones"; storing reference material in LFS.
**Reversibility:** Low — a leak cannot be undone by a later decision.

---

## D-019 — MetaHuman is the driver destination, with a tiered approach

**Date:** 2025-06-01
**Decision.** The driver's destination is the UE 5.8 MetaHuman system. Quality tiers A (helmeted cockpit), B (visible face at presentation distance) and C (close-up detail) are defined, and **Tier A is built first** (Milestone 6), with MetaHuman integration at Milestone 7.
**Rationale.** A helmeted cockpit driver delivers most of the in-race value at a fraction of the cost and risk, and it validates scale, pose and attachment before any facial work begins.
**Rejected.** Starting from a photorealistic close-up head; hand-building a facial rig in Blender.
**Reversibility:** Medium.

---

## D-020 — Milestone numbering is fixed and shared

**Date:** 2025-06-01
**Decision.** Milestones 0A, 0B, 1–12 as enumerated in `MILESTONE_PLAN.md`. Every document uses these numbers identically. Renumbering is a decision-log event.
**Rationale.** Cross-document references are worthless if the numbering drifts.
**Rejected.** Per-document ad-hoc phase names.
**Reversibility:** High, but disruptive.

---

## D-021 — Honesty and verification labelling

**Date:** 2025-06-01
**Decision.** No document, comment or commit message may claim that the project compiled, the editor opened, a Blender script ran, an asset imported, or a model looks correct, unless that action was genuinely performed. Every stated result carries exactly one label: `statically inspected`, `automatically validated`, `requires Blender execution`, `requires Unreal Editor verification`, `requires local compilation`, `requires visual inspection`, `requires playtesting`. Every document ends with a Verification Ledger.
**Rationale.** Unverified claims compound: a false "this works" at Milestone 2 costs days at Milestone 10. The label makes the epistemic status of every statement explicit and cheap to audit.
**Rejected.** Informal confidence language ("should work", "presumably fine").
**Reversibility:** Low by intent — this is a standing rule, not a phase.

---

## D-022 — Repository hygiene

**Date:** 2025-06-01
**Decision.** The repository excludes Unreal build output (`Binaries/`, `Intermediate/`, `Saved/`, `DerivedDataCache/`), Blender working files under `BlenderPipeline/local/`, `LocalReference/`, credentials, keys and machine configuration. Git LFS tracks binary asset types. `BlenderPipeline/reports/` is **not** excluded, because validation reports are committed plain text (D-017).
**Rationale.** A clean repository is diffable, cloneable and safe to publish.
**Rejected.** Committing build output for convenience; excluding reports along with other generated files.
**Reversibility:** High for the ignore rules, Low for anything already committed.

---

## D-023 — Report filenames are deterministic and carry no timestamp

**Date:** 2025-06-01
**Decision.** `af_pipeline_config.report_path(subject, extension)` builds report filenames from the subject and extension only. No timestamp, run counter, host name or user name enters the path. Re-running the pipeline overwrites the previous report in place.
**Rationale.** A committed report (D-017, D-022) must be diffable. If the filename changed on every run the repository would accumulate near-identical files and `git diff` could never answer the only question that matters: *what changed since the last run?* Overwriting turns the report into a tracked state file whose history lives in Git, where it belongs.
**Rejected.** Timestamped filenames (`report_20250601_1432.json`) — untrackable churn; a `runs/` directory of retained history — duplicates what Git already does.
**Reversibility:** High. Adding a timestamp later is a one-function change; the reports themselves are unaffected.

---

## D-024 — Geometry is authored in world space with identity object transforms

**Date:** 2025-06-01
**Decision.** Every mesh generated by `af_vehicle_generate.py` has its vertices placed at final world coordinates, and each resulting object keeps location `(0,0,0)`, rotation `(0,0,0)` and scale `(1,1,1)`. Placement is baked into vertex data, never into the object transform.
**Rationale.** FBX export and Unreal import both apply object transforms, and each applies them with its own axis and scale conventions. A non-identity transform is therefore a second place where the unit and axis contract (D-013) can be violated, and it is a place that is invisible in the viewport. Identity transforms make `apply_scale_options` and `axis_forward`/`axis_up` the *only* transform-bearing settings in the pipeline, so there is exactly one thing to verify. It also means validation can compare a vertex coordinate directly against a design value without composing a matrix first.
**Rejected.** Authoring parts at the origin and positioning them with object transforms — conventional Blender practice, but it defers the transform question to import time, which is exactly where it is hardest to debug.
**Reversibility:** Medium. Changing this would require reworking generation, the validation position checks, and the rig's head/tail placement together.

---

## D-025 — Rigid binding: one bone per mesh, one weight per vertex

**Date:** 2025-06-01
**Decision.** `af_vehicle_rig.py` binds each mesh to exactly one deform bone with weight 1.0 via a single vertex group. The body binds to `AF_Chassis`, each wheel to its own wheel bone, each suspension mesh to its own suspension bone. `AF_Root` and `AF_Steering` carry no geometry. No automatic weights, no envelopes, no smoothing.
**Rationale.** A formula car is a rigid assembly; nothing on it deforms. Rigid binding makes the skin weights *verifiable by arithmetic* rather than by eyeball — the validator can assert one weight per vertex at exactly 1.0 and be done, which trivially satisfies the four-weights-per-vertex budget. Automatic weighting would produce plausible-looking results that nobody could check without visual inspection, which is precisely the class of claim the honesty rule (D-021) forbids.
**Rejected.** `ARMATURE_AUTO` weighting; envelope weighting; a single mesh bound across multiple bones.
**Reversibility:** High while the vehicle is rigid. If deforming parts are ever introduced they would be added alongside this scheme, not in place of it.

---

## D-026 — Exporter settings are filtered against the operator's RNA at run time

**Date:** 2025-06-01
**Decision.** `af_export.py` does not pass `FBX_EXPORT_SETTINGS` to the exporter blindly. It introspects the export operator's RNA properties, passes only the keys the installed Blender actually accepts, and **reports every dropped key loudly** in its output before exporting.
**Rationale.** The exporter option names in `FBX_EXPORT_SETTINGS` are stated intent, not a verified Blender 5.2 LTS API (`VERSION_MATRIX.md` §5). Passing an unknown keyword raises `TypeError` and aborts the run; silently swallowing it would be worse, because the export would then succeed with a *different* configuration than the one documented — for example with leaf bones enabled — and nothing downstream would notice until the skeleton arrived wrong in Unreal. Filtering plus a loud report converts an unverified assumption into an observable fact printed at run time.
**Rejected.** Passing settings unfiltered and letting the exception surface — brittle across point releases; filtering silently — hides a real configuration divergence.
**Reversibility:** High. Once the true option set is observed on a real Blender 5.2 LTS install, the filter becomes a no-op and can be removed or downgraded to an assertion.

---

## D-027 — The Unreal project lives in `Unreal/`, not at the repository root

**Date:** 2025-06-01
**Decision.** `ApexFormula.uproject`, `Config/` and `Source/` live under a top-level `Unreal/` directory. The repository root holds `Documentation/`, `BlenderPipeline/`, `Unreal/`, `Tools/`, `README.md` and the git metadata files.
**Rationale.** The project brief specifies the architecture, the module list and the naming rules, but **does not dictate a repository layout** — this was confirmed by searching the brief for `uproject`, `Source/` and `Config/`, which returned a single incidental hit. The layout is therefore a project decision and is recorded as one rather than left implicit.

This project is not only an Unreal project. It is an Unreal project *plus* a Blender pipeline *plus* a document set *plus* standalone tooling, and three of those four are useless inside an Unreal tree. Putting the `.uproject` at the root would force `BlenderPipeline/` and `Documentation/` to sit alongside `Content/`, `Binaries/` and `Intermediate/`, where engine-generated directories would interleave with authored ones and `.gitignore` would have to distinguish them by name rather than by location. With the engine tree quarantined under `Unreal/`, every generated directory is ignorable by prefix.
**Rejected.** `.uproject` at the repository root (standard for engine-only projects, wrong for this one); a nested `ApexFormula/ApexFormula.uproject` double-directory (the Unreal launcher convention, but it produces `ApexFormula/ApexFormula/Source/ApexFormula*` path stutter).
**Consequence.** Any instruction to open the project must say `Unreal/ApexFormula.uproject`. Build artefacts appear at `Unreal/Binaries`, `Unreal/Intermediate`, `Unreal/Saved` and `Unreal/DerivedDataCache`, and `.gitignore` excludes them at that path.
**Reversibility:** High, but not free. Moving the project is a directory rename plus a `.gitignore` edit; the C++ is unaffected because no source file refers to its own location.

---

## D-028 — Static validation is written as a program, not a checklist

**Date:** 2025-06-01
**Decision.** The Milestone 1 architectural rules — the dependency graph, the module boundaries, the D-008 vehicle chokepoint, telemetry literal containment, the prohibited-token rule, path portability, header hygiene and the bone convention — are enforced by an executable program, `Tools/af_static_validate.py`, which exits non-zero on any violation. They are not enforced by a review checklist.
**Rationale.** No Unreal Engine, Unreal Build Tool, MSVC or clang exists in the authoring environment, so the compiler — normally the first thing that enforces a dependency graph — is unavailable. Without a substitute, every architectural claim in this milestone would rest on the author having looked carefully, which is exactly the kind of claim D-021 forbids stating as fact.

A program converts "I believe Race does not depend on Vehicle" into "a process asserted it and returned 0". It is also the only artefact of this milestone that a reviewer can *run* rather than read, and it keeps working after the author has forgotten the rules.

The validator is standard-library-only and takes a `--root`, so it runs anywhere Python 3 runs, including in CI, with no project-specific setup.
**Rejected.** A written checklist (unenforceable, and rots); waiting for a machine with the engine installed (would leave the entire milestone unverified in the meantime); a linter configuration (cannot express project-specific rules such as the D-008 chokepoint).
**Consequence.** The rules now have two representations — prose in `TECHNICAL_ARCHITECTURE.md` and code in the validator — which can drift. The validator is written to fail loudly rather than silently, and D-030 addresses drift directly.
**Reversibility:** High. Once a compiler is available it becomes an additional check, not a replacement — a compiler enforces dependencies but says nothing about prohibited tokens, telemetry literal containment or bone agreement.

---

## D-029 — The bone convention is checked by emulation, never by textual comparison

**Date:** 2025-06-01
**Decision.** The validator imports `af_pipeline_config.py` live as the single source of truth for bone names, ordering and parenting, then parses `AFBoneNameMap.cpp`, extracts its prefix, literal names, corner order and `Printf` format strings, and **re-derives** the ordering and parent map that the compiled C++ would produce. The derived structures are compared against the Python constants. No bone list is duplicated in the validator.
**Rationale.** Both bone bugs found in this project so far were **doc comments that had drifted away from correct code** — once in `AFBoneNameMap.h` (two wrong names in a comment) and once in `AFTelemetryTypes.h` (a comment embedding a live channel literal). A textual comparison would have happily compared the drifted comment. Emulation compares behaviour, so a comment cannot influence the result, and a third copy of the bone list — which would be a third thing to drift — is never created.
**Rejected.** Hard-coding the eleven bone names in the validator (creates a third source of truth); diffing the C++ against a generated file (compares text, not behaviour); trusting the doc comments (already demonstrated to be the failure mode).
**Consequence.** The validator is coupled to the *style* of `AFBoneNameMap.cpp`, not only its behaviour. A refactor that preserves behaviour but changes the shape of the constructor loop or `GetCornersInOrder()` will break the parser and must be accompanied by an emulator update. This is an accepted cost: a parser that breaks loudly is better than a comparison that passes wrongly.
**Reversibility:** Medium. The approach could be replaced by code generation — deriving `AFBoneNameMap.cpp` from `af_pipeline_config.py` — which would eliminate the drift class entirely. That is a larger change and was not needed to satisfy Milestone 1.

---

## D-030 — Validators are mutation-tested before their results are believed

**Date:** 2025-06-01
**Decision.** Before any static validator's PASS is reported as evidence, the validator is subjected to deliberate defect injection: a scratch harness copies the tree to a temporary directory, injects one known violation at a time, and asserts a non-zero exit. A PASS is only quoted alongside the mutation score. The harness is scratch tooling and is **not** committed.
**Rationale.** A checker that cannot fail is indistinguishable from a checker that always passes, and both print the same reassuring output. Milestone 0B produced a concrete instance: an audit reported PASS while a real name-literal leak sat in `bone_head_m()`, because the audit's own blind spot hid it.

Mutation testing immediately paid for itself on this milestone. It found a **genuine gap**: the prohibited-token rule used `\bF1\b`, which cannot match `F1SeasonCount` because the trailing word boundary fails when `1` is followed by a word character — so the rule was checking the one place the token did not matter and skipping identifiers, the place it did. `Formula1` matched no pattern at all. Both are now substring matches.

It also disciplined the investigation. Three apparent gaps in the first run turned out to be two flaws in the *test* — injections placed inside `//` comments, which the validator strips by design — and one wrong anchor. That produced the symmetric rule to the 0B lesson: **when a mutation is missed, suspect the mutation first, but prove it by reading the source.** A negative control was then added — a prohibited word inside a comment, which must remain undetected — so the suite verifies the validator's deliberate silences as well as its alarms.
**Rejected.** Trusting a PASS on its own (the exact 0B failure); testing the validator only with hand-written unit tests (tests the checker's helpers, not its end-to-end verdict on a real tree); mutating the real tree in place (unsafe, and impossible anyway — the tree is root-owned and read-only to the sandbox user, which is why the harness copies first).
**Consequence.** Every validator edit must be followed by two things: re-running the mutation suite, and checking the assertion-count arithmetic. When the prohibited-token patterns were tightened, the count moved 2117 → 2300, exactly 3 new patterns × 61 scanned files — arithmetic that proves the change added checks rather than silently weakening existing ones.
**Reversibility:** High as a practice; there is no reason to stop.

---

## Numbering note — D-031 to D-034

**Date:** 2025-06-08

D-031 to D-034 are cited by Milestone 2 header comments but were never transcribed into this log. The entries below therefore resume at D-035, leaving a visible gap rather than closing it with invented text.

This is recorded rather than quietly fixed because the alternative — writing four plausible entries reconstructed from the code that cites them — would produce a log that reads complete while containing rationale nobody ever decided. A gap that is labelled is auditable. A fabricated entry is not.

Whoever holds the Milestone 2 header authoring context should transcribe the real four. Until then, the citations are dangling and this note is the reason why.

---

## D-035 — The participant contract wins over the pawn's convenience

**Date:** 2025-06-08
**Decision.** `AAFVehiclePawn::GetParticipantDisplayName()` returns `FString`, matching `IAFRaceParticipant`. The stored member `DriverDisplayName` stays `FText`, and the accessor returns `DriverDisplayName.ToString()`.
**Rationale.** The pawn declared the override returning `FText` while the interface declared `FString`. That is not a style disagreement; it is a guaranteed compile failure the moment both translation units are seen together, and it sat in `main` undetected because nothing in this repository compiles.

Both types were defensible in isolation. `FText` is right for the member: the driver's name is user-facing and localisable, and `FText` is the type that carries localisation. `FString` is right for the interface: race logic compares, sorts, logs and keys on participant names, and none of those operations want a localised display type.

The conflict is resolved in favour of the interface because an interface is a contract with unknown callers, whereas the member is private to the pawn. Changing the interface to `FText` would have pushed a presentation concern into every future implementer — the AI driver, the replay ghost, the network proxy — none of which have anything to display. The conversion is explicit and happens in exactly one place.
**Rejected.** Changing `IAFRaceParticipant` to return `FText` (spreads a presentation type across implementers that do not present); storing the member as `FString` (loses localisation for the one thing that genuinely is user-facing); an overload pair (two names for one concept, and the interface still has to pick one).
**Consequence.** Any implementer of `IAFRaceParticipant` that holds a localisable name pays a `ToString()` at the boundary. This is the correct place for that cost to appear.
**Verification.** The corrected return type is checked by `Tools/af_validate_interfaces.py`, which passes in CI. That the file *compiles* is not claimed — `requires local compilation`.
**Reversibility:** High. Both types are one-line changes; the surrounding design does not depend on which was chosen.

---

## D-036 — Wheel parameters are deferred and applied idempotently

**Date:** 2025-06-08
**Decision.** `UAFVehicleCompatibilityLayer` holds `TArray<FAFWheelSetup> PendingWheels` and `bool bWheelParametersApplied`. Wheel setups supplied before a backend is bound are retained, not discarded. `TryApplyWheelParameters()` applies them if a backend exists and is safe to call any number of times; `AreWheelParametersApplied()` exposes the state.
**Rationale.** Configuration and backend availability arrive in an order the layer does not control. A designer sets wheel data on the pawn; the movement component may not yet be constructed and registered. Applying to a null backend would discard the data silently, and silent loss of suspension geometry surfaces later as a handling bug with no obvious cause — the worst available failure mode.

Idempotency is a correctness requirement rather than a convenience. Possession can occur more than once for a single pawn, and reapplying suspension parameters to a running simulation would be visible as a physics discontinuity. Making the second call a no-op means neither call site needs to know whether the other ran, which is what allows the layer to be called from both binding and possession without coordination.

Exposing `AreWheelParametersApplied()` follows the same reasoning as D-017: state that matters should be observable, not inferred. Tests assert on it directly instead of guessing from side effects.
**Rejected.** Requiring callers to order binding before configuration (a documented ordering constraint is a bug waiting for the one call site that forgets); applying to a null backend and logging a warning (the data is still lost, and warnings are ignored); an assertion on unbound application (turns a recoverable ordering difference into a crash).
**Verification.** `requires local compilation`. The unbound-layer inert case has a written test that has never been executed.
**Reversibility:** High. The pending buffer is internal; removing it would change only the layer.

---

## D-037 — The interface override check ships as a separate script

**Date:** 2025-06-08
**Decision.** The return-type agreement check lives in a new file, `Tools/af_validate_interfaces.py`, rather than as an additional check inside `Tools/af_static_validate.py`. CI runs both.
**Rationale.** D-035 was a defect that `af_static_validate.py` was structurally incapable of finding. It checks module boundaries, include resolution, originality, backend isolation, header hygiene and test shape — but it had never compared an override against the contract it claims to implement. The gap needed closing, and D-028 says gaps are closed with programs.

The check was first written *inside* the existing validator and worked. It was then moved out, for a reason specific to this environment: every write to the repository goes through an API that requires the **complete file contents**, because no patch mechanism is available. Committing the modified validator would have meant re-transmitting roughly sixty kilobytes verbatim. A single silent transcription error in that payload would have corrupted the project's primary validator — the one artefact every other verification claim in this project rests on — and it would have corrupted it in a way that still exits 0 and still looks reassuring.

A new file cannot damage an existing one. The cost is a second entry point and a second CI step; the benefit is that the tool the whole project trusts is never rewritten in order to extend it.
**Rejected.** Extending `af_static_validate.py` in place (unacceptable transcription risk against this project's most load-bearing file, under this environment's write constraints); deferring the check until a compiler is available (a compiler catches this specific bug but says nothing until someone has an engine, which is exactly the situation that let D-035 survive).
**Consequence.** Two validators must both stay green, and a future reader may reasonably ask why the check is not in the obvious place. This entry is that answer. If the write constraint ever lifts, merging the two is a mechanical change and the mutation suite makes it safe.
**Verification.** `automatically validated` — the checker and its nine-case mutation suite both execute in CI on Python 3.9 and 3.12, and both pass against the real tree.
**Reversibility:** High.

---

## D-038 — `ApplyVehicleDefinition` leaves powertrain and aero at defaults

**Date:** 2025-06-08
**Decision.** `ApplyVehicleDefinition` transfers only the fields `UAFVehicleDefinition` actually carries — mass, wheelbase, track widths, overall length, centre-of-mass bias and height. Powertrain and aerodynamic fields on `FAFVehicleBackendSetup` (`PeakDriveTorqueNm`, `PeakTorqueRpm`, `MaxRpm`, `ForwardGearCount`, `bUseAutomaticGears`, `DragCoefficient`, `FrontalAreaM2`) keep their struct defaults.
**Rationale.** `UAFVehicleDefinition` is a Milestone 1 chassis-geometry asset. It has no powertrain or aero fields, and inventing them here would put the same tuning data in two places before anything has driven — the exact duplication D-007 exists to prevent.

The struct defaults are deliberately conservative and centralised, so a car built from a definition alone is coherent rather than undefined. When powertrain tuning arrives it belongs in its own Data Asset with its own version field, not bolted onto the geometry asset.
**Rejected.** Extending `UAFVehicleDefinition` with powertrain and aero fields now (guesses at a schema before any tuning has happened, and bumps `DataVersion` for data nobody has authored); leaving the fields uninitialised (produces a car whose behaviour depends on what the struct happened to contain).
**Consequence.** Two cars built from different definitions share identical powertrain behaviour until a powertrain asset exists. This is visible and expected, not a bug.
**Numbering.** Earlier working notes used D-037 for this decision. That number was published in the commit message that added `Tools/af_validate_interfaces.py` before this entry was written, and commit history cannot be edited, so the log yields: D-037 is the separate-script decision and this is D-038.
**Verification.** `requires local compilation`.
**Reversibility:** High.

---

## D-039 — The Blender 5.2 LTS pin stands, and the hypothesis against it is retracted in writing

**Date:** 2026-08-11
**Decision.** `BLENDER_SERIES` in `.github/workflows/validate.yml` stays at `'5.2'`. The workflow continues to resolve the exact point release by listing the upstream directory and selecting the highest `blender-5.2.*-linux-x64.tar.xz` by version sort, rather than hardcoding a patch number. No repin to a 4.x series.
**Rationale.** When the first Blender CI job failed, the working hypothesis was that Blender 5.2 might not exist on `download.blender.org` and that the pin recorded in `VERSION_MATRIX.md` §5.2 was aspirational. That hypothesis was **wrong**, and it was wrong in the most expensive available direction: acting on it would have repinned the entire pipeline to a series the project had not chosen, in order to fix a fault that was never in the pin.

The evidence that settled it is the first line of the job's own output: `Blender 5.2.0 LTS (hash fbe6228777e7 built 2026-07-14 01:32:04)`. The download resolved, the archive extracted, the binary launched headless, and it executed four full pipeline stages before failing on a geometry assertion. A version that does not exist cannot print its own build hash.

The entry is written as a retraction rather than as a silent correction because the hypothesis had already been stated aloud as a probable cause. D-021 governs claims about what was verified; the symmetric obligation is that a stated diagnosis which turns out to be false is withdrawn explicitly, in the same place a reader would look for it.
**Rejected.** Repinning to Blender 4.x (would have changed the project's stated stack, D-003, to work around a fault that was not in the stack); hardcoding an exact patch version such as `5.2.0` (the directory listing plus version sort survives point releases, and the point release is exactly the part nobody should have to maintain by hand); quietly deleting the wrong hypothesis from the working notes.
**Consequence.** A false diagnosis is now on the record next to the true one. That is the intended cost. Two secondary lessons are recorded with it, both learned the expensive way:

1. **Job duration is not evidence.** The same passing smoke-test job took 36 seconds in one run and roughly eight minutes in another. Runtime was briefly treated as a signal about what the job was doing; it is noise from download and runner variance.
2. **A failing job that produces detailed correct output is not failing at the step you assumed.** Four stages of correct summary output preceded the failure, and they were available in the log from the first run.

**Verification.** `automatically validated` — Blender 5.2.0 LTS downloads, extracts and executes the full seven-stage smoke test in CI, and the job is green on the merged `main`.
**Reversibility:** High. The series is one string in one workflow file.

---

## D-040 — Halo arc height is solved from the design envelope, and the envelope is checked before `bpy`

**Date:** 2026-08-11
**Decision.** In `af_vehicle_generate.py` the halo's arc height is **derived from `DESIGN["overall_height_m"]`** rather than scaled from the halo radius. Five module-level helpers implement it — `halo_segment_thetas()`, `halo_max_sin()`, `halo_base_z_m()`, `halo_arc_height_m()`, `halo_apex_z_m()` — and a new module-level constant `HALO_APEX_CLEARANCE_M = 0.010` reserves headroom beneath the envelope ceiling. A second new function, `check_design_envelope()`, computes the predicted bounding box arithmetically and is called from `main()` **before any `bpy` call**.
**Rationale.** Stage 5 of the smoke test failed on a single check, `bounding box within design envelope`, with 19 of 21 checks passing. The cause was not length, which is where attention went first. It was height:

| Axis | Design | Measured | Delta | Tolerance |
| --- | --- | --- | --- | --- |
| X | 5.600 m | 5.60000 m | 0.00000 | 0.010 m |
| Y | 2.000 m | 1.94000 m | −0.06000 | 0.010 m |
| **Z** | **0.950 m** | **0.97415 m** | **+0.02415** | **0.010 m** |

The old code read `arc = halo_radius_m * 0.55 = 0.231 m` and placed segment centres at `base + 0.5·arc + arc·sin θ`, with `base = 0.605` and a maximum `sin θ` of `0.98982` over the twelve segments. That put the apex segment's centre at `0.94915 m` and its crown, after half the `0.050 m` tube thickness, at `0.97415 m`.

The defect is structural rather than numeric. The arc height was tied to the halo *radius*, a value that has nothing to do with how much vertical room the car is allowed. Any future change to `halo_radius_m` — a plausible styling change — would have silently moved the roofline again. Solving the arc height from the ceiling inverts the dependency so that the envelope constrains the geometry instead of the geometry accidentally deciding the envelope.

`check_design_envelope()` exists for a second-order reason. The failure surfaced at stage 5, after scene setup, generation, rigging and materials had all run and passed. Everything upstream of the check was correct and all of it was wasted. An arithmetic pre-flight that needs no Blender at all turns a five-stage round trip through CI into an immediate, local, readable failure naming the axis, the measured value, the design value and the overage.
**Rejected.** Raising `overall_height_m` to accommodate the halo (fixes the assertion by moving the goalposts, and the envelope is a design constraint, not a derived quantity); loosening `TOLERANCE["length_m"]` (would have masked a real 24 mm breach and every future one); shrinking `halo_radius_m` (changes a styling value to fix an arithmetic bug, and leaves the structural dependency in place); scaling the whole halo (same objection, larger blast radius).
**Consequence.** The halo apex now sits at exactly `0.940 m`, ten millimetres clear of the `0.950 m` ceiling, and it will follow the ceiling if the ceiling ever moves. The arc height is no longer a round number — it is `0.20807862693170662` — and that is the expected shape of a solved value rather than a chosen one. The body mesh is unchanged at 176 vertices and 132 polygons, so no downstream count, weight or LOD assumption is disturbed.
**Verification.** `automatically validated`, at two levels. Locally, the shipped module was executed against a stub config carrying the real `DESIGN` numbers: `halo_arc_height_m()` returned `0.20807862693170662`, `halo_apex_z_m()` returned `0.94`, `measured_bounds_m()` returned `(5.6, 1.94, 0.94)`, and `check_design_envelope()` returned `(True, [])`. In CI, Blender 5.2.0 LTS runs the full seven-stage smoke test to completion and the job is green on the merged `main`.
**Reversibility:** High. The helpers are module-level and self-contained; `af_pipeline_config.py` was deliberately not modified, so `config_hash()` is untouched by construction.

---

## D-041 — `af_pipeline_config.py::DESIGN` is the single source of truth for vehicle dimensions

**Date:** 2026-08-11
**Decision.** Where the Unreal side and the Blender side disagree about a physical dimension of the car, the Blender side wins. `UAFVehicleDefinition` is corrected to match: `OverallLengthM` `5.30` → `5.60`, `RearTrackM` `1.55` → `1.54`. `WheelbaseM` (`3.60`) and `FrontTrackM` (`1.60`) already agreed and are unchanged. A block comment in `AFVehicleDefinition.h` names `af_pipeline_config.py::DESIGN` as canonical so the next author does not have to rediscover the ordering.
**Rationale.** The two halves of the project described **different cars**, and had done so since Milestone 1. The Unreal data asset claimed a 5.30 m car on a 1.55 m rear track; the Blender config generates a 5.60 m car on a 1.54 m rear track. Neither value is wrong in isolation, which is precisely why the disagreement survived: each side is internally consistent and nothing crosses between them yet.

It would have surfaced eventually as a physics-versus-visual mismatch — a collision body that does not match the mesh it wraps — and that class of bug is diagnosed slowly because the symptom appears far from the cause. Ten minutes of dimension reconciliation now is worth considerably more later.

Blender is chosen as canonical because D-010 already made it the source of truth for geometry, and these are geometry values. Blender's numbers are also the ones with a consumer: they are what `af_vehicle_generate.py` builds, what `af_validate.py` asserts against, and what the smoke test exercises on every push. The Unreal values had no consumer at all — nothing reads `OverallLengthM` yet, which is another reason the conflict went unnoticed. Making the *checked* side canonical means the invariant is maintained by a program rather than by memory.
**Rejected.** Making Unreal canonical (contradicts D-010, and would require regenerating and re-validating all geometry to satisfy numbers nothing currently reads); leaving both and reconciling at import time (a conversion layer to paper over a disagreement that has no reason to exist); leaving both and documenting the discrepancy (records a defect instead of fixing a two-line one).
**Consequence.** `UAFVehicleDefinition::DataVersion` stays at `2`. The changed fields have no runtime consumer yet, so no migration is required, and bumping the version would signal a schema change where only values moved. When a future dimension conflict appears, the resolution rule is now written down in the header itself.
**Verification.** `statically inspected` and `requires local compilation`. The values were compared against the confirmed `DESIGN` dictionary and corrected; the header has never been compiled, because no compiler exists in the authoring environment.
**Reversibility:** High. Four numbers and a comment.

---

## Superseded Decisions

None. No decision recorded here has yet been superseded.

## Verification Ledger for This Document

| Claim | Label |
| --- | --- |
| Every decision listed originates from the project brief or from Milestone 0A authoring | statically inspected |
| D-014 is the replay decision and states snapshot-plus-interpolation without assuming determinism | statically inspected |
| Cross-referenced documents and sections exist | statically inspected |
| Reversibility ratings are judgements, not measurements | statically inspected |
| D-023 to D-026 describe the behaviour actually written into the Milestone 0B scripts | statically inspected |
| The rigid binding scheme in D-025 is what `binding_plan()` returns — nine meshes, deform bones only, nothing on Root or Steering | automatically validated |
| The Blender-side effects of D-024, D-025 and D-026 occur as described when the scripts run | requires Blender execution |
| D-027 records a layout choice the project brief genuinely leaves open | statically inspected — confirmed by searching the brief |
| The Milestone 1 tree is laid out as D-027 describes | automatically validated |
| The rules named in D-028 are enforced by a program that exits non-zero on violation | automatically validated |
| D-029 describes how the bone check actually works | automatically validated |
| The mutation score and the assertion arithmetic quoted in D-030 are measured values | automatically validated |
| The `\bF1\b` gap described in D-030 was real, and is now closed | automatically validated |
| D-031 to D-034 are absent from this log and their citing comments are dangling | statically inspected |
| The D-035 return type in the pawn now agrees with `IAFRaceParticipant` | automatically validated |
| The D-037 checker and its nine-case mutation suite pass on Python 3.9 and 3.12 | automatically validated |
| The D-036 deferred-application behaviour occurs as described at run time | requires local compilation |
| The D-038 defaults produce a coherent vehicle | requires playtesting |
| Blender 5.2.0 LTS downloads, launches headless and runs the seven-stage smoke test (D-039) | automatically validated |
| The D-039 retraction describes a hypothesis that was genuinely stated and is genuinely withdrawn | statically inspected |
| The 0.97415 m measured height and the 0.02415 m overage quoted in D-040 are measured values | automatically validated |
| The D-040 halo apex sits at 0.940 m and the design envelope check passes | automatically validated |
| The D-040 body mesh is unchanged at 176 vertices and 132 polygons | automatically validated |
| The D-041 dimension conflict existed as described, and the corrected values match `DESIGN` | statically inspected |
| The D-041 header compiles, or `UAFVehicleDefinition` loads in the editor | not claimed — `requires local compilation` |
| Any Milestone 1 or Milestone 2 C++ affected by these decisions has been compiled | not claimed — `requires local compilation` |
