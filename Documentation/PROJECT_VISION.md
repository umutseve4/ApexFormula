# ApexFormula — Project Vision

**Document status:** statically authored design document (Milestone 0A). No engine or tool execution is claimed anywhere in this document.

---

## 1. Project Identity

- **Internal project name:** ApexFormula
- **Root project identity string:** `ApexFormula`
- **Asset prefix:** `AF_`
- **Blender Python script prefix:** `af_`
- **Genre:** original 3D open-wheel formula-style racing game
- **Intellectual property status:** original fictional motorsport IP

ApexFormula is an entirely fictional motorsport universe. It has its own championship, its own regulation set, its own teams, drivers, sponsors, circuits and liveries. It is not a simulation of, adaptation of, or companion to any existing real-world racing series.

## 2. Originality Rules (binding)

These rules are binding on all code, assets, documentation, commit messages and user-facing text.

**Forbidden in project names, filenames, class names, asset names, script names, folder names, documentation titles and public-facing terminology:**

- The token `F1`.

**Forbidden as content:**

- Formula 1 branding of any kind
- Real racing team names
- Real driver names
- Real sponsor names
- Official logos of any real organisation
- Real liveries
- Exact real-world car reproductions
- Exact real-world track reproductions
- Any protected motorsport branding

**Required instead:**

- Fictional teams, fictional drivers, fictional sponsors, fictional vehicles, fictional circuits, fictional liveries, fictional helmets, fictional racing suits and a fictional championship rule set, all authored for ApexFormula.

**Regulation references:** ApexFormula vehicle dimensions, aerodynamic limits, energy limits and tyre rules are *ApexFormula design values*. They must never be described as official FIA measurements or as any real sanctioning body's regulations. If real motorsport regulations are ever consulted as a general engineering reference, that use must be recorded separately in `Documentation/DECISION_LOG.md` with source, season, units and the limited purpose of the reference. No such reference is used in Milestone 0A.

**Driver likeness exception:** the product owner's own likeness is an intentional, authorised original character and is not third-party IP. Its handling is governed by `Documentation/DRIVER_PIPELINE_DESIGN.md`.

## 3. Design Goals

1. **Original identity first.** Every visible name, logo, livery and circuit is authored for ApexFormula.
2. **Credible open-wheel feel.** High downforce, low mass, sharp braking, narrow tolerance for error — the vehicle should feel fast, delicate and rewarding.
3. **Deterministic, inspectable simulation.** Race rules, lap validation and timing must be reproducible and auditable, not emergent side effects of visual code.
4. **Data-driven tuning.** A designer must be able to change vehicle balance, aero maps, tyre models and session rules without recompiling C++.
5. **Pipeline reproducibility.** Any generated asset must be regenerable from scripts and configuration, not from undocumented manual steps.
6. **Milestone honesty.** Nothing is declared working until it has been verified on the product owner's machine.

## 4. Gameplay Direction

The target experience is a **single-player-first, offline, session-based open-wheel racing game**, structured around:

- Practice, qualifying and race sessions
- Ordered checkpoints, sector timing, valid/invalid lap detection
- A starting grid with false-start preparation
- AI opponents with configurable pace and aggression
- A pit lane with pit stops and stop timing
- Race control with penalties
- Telemetry and a HUD that surfaces tyre, brake, fuel, energy and delta information
- Vehicle setup screens for aero balance, brake bias, differential, suspension and steering

Multiplayer is **not a Milestone 0A–12 feature**. It is a *boundary requirement*: authoritative logic is placed where it could later be server-owned, so that adding replication is an extension rather than a rewrite.

## 5. Simulation versus Accessibility Philosophy

ApexFormula targets the **"deep simulation core, layered assistance"** model.

- The physical model is always fully simulated. Assists never disable the simulation; they modulate *input into* the simulation or *output torque from* it.
- Assist layers planned: steering assist, braking assist, traction/stability assist, automatic gearbox, racing line guidance, automatic energy deployment, simplified tyre/fuel consumption multipliers.
- Every assist is a named, serialisable value in a difficulty profile Data Asset, never a hardcoded branch inside physics code.
- The default out-of-box profile is **approachable**: assists on, consumption multipliers reduced, damage cosmetic.
- The reference profile is **unassisted**: all assists off, full consumption, full penalties. This is the profile used for tuning and for validation of the physical model.
- No assist may create physically impossible behaviour (e.g. grip above the tyre model's own limit).

## 6. Platform Assumptions

- **Primary development and build platform:** Windows.
- **Primary engine:** Unreal Engine 5.8.
- **Primary DCC tool:** Blender 5.2 LTS.
- **Primary gameplay language:** C++, with Blueprints for configuration and presentation.
- **Primary input:** gamepad. **Also targeted:** keyboard, and direct-drive/consumer force-feedback steering wheels with pedals.
- **Source control:** Git, with Git LFS for large binary assets.
- Console and non-Windows platforms are explicitly **out of scope** for the milestone plan defined in `Documentation/MILESTONE_PLAN.md`. Nothing in the architecture may make them impossible, but nothing is built or validated for them.

## 7. Quality Targets

Quality targets are expressed as *final-quality* targets. They are **not** reduced to match the current development laptop.

| Area | Final-quality target |
| --- | --- |
| Vehicle mesh | Original high-detail open-wheel car with LOD chain and dedicated collision meshes |
| Vehicle physics | Sub-stepped, telemetry-instrumented, tyre/aero/energy aware |
| Track | Original circuit geometry with correct racing surface classification, run-off, kerbs and pit lane |
| Driver | MetaHuman-based original driver, Tier A/B/C as defined in `Documentation/DRIVER_PIPELINE_DESIGN.md` |
| Presentation | Cinematic-grade garage, menu and podium scenes |
| Frame budget (final target machine) | Stable 60 FPS at high settings during a full grid race |
| Frame budget (development preview) | Playable, not shippable — visual fidelity may be sacrificed freely |

**Explicit statement:** the current laptop's capability does not lower any number in this table. It only determines which *profile* is used day to day.

## 8. Preview versus Final-Quality Principles

Two named quality profiles exist for the entire project lifetime.

### Development Preview profile

- Purpose: allow gameplay iteration, logic testing and playtesting on weaker hardware.
- Permitted: reduced texture resolution, reduced shadow quality, disabled ray tracing, disabled advanced post-processing, low-poly proxy meshes, reduced AI grid size, reduced physics sub-steps *for non-validation sessions*, skipped LOD bakes, fast/dirty light builds.
- Location: engine scalability configuration plus an ApexFormula-specific preview settings object. Never a source-code branch.

### Final Quality profile

- Purpose: the actual shipping target, produced on a stronger Windows machine.
- Includes: full-resolution textures, full LOD chains, full lighting bake/Lumen configuration, full grid, full physics sub-stepping, full validation passes.

### Non-destruction rules

1. **Source assets are never overwritten by preview generation.** Preview outputs go to a distinct generated directory; source assets live in a separate source directory (see `Documentation/BLENDER_PIPELINE_DESIGN.md`).
2. **Preview settings are additive overrides.** Selecting the preview profile must never edit, downsample or delete a final-quality asset on disk.
3. **Profile selection is data, not code.** Switching profiles must require no recompilation and no asset re-authoring.
4. **Any generated artefact records which profile produced it**, so a preview-quality bake can never be mistaken for a final-quality bake.
5. **Validation of physics and race rules always runs at final-quality physics settings**, even on weak hardware, even if the frame rate is poor. Correctness is never sampled at preview fidelity.

## 9. Verification Posture

Every claim in this project is labelled with exactly one of:

- `statically inspected`
- `automatically validated`
- `requires Blender execution`
- `requires Unreal Editor verification`
- `requires local compilation`
- `requires visual inspection`
- `requires playtesting`

No document in this repository asserts that Unreal Engine compiled, that an Unreal project opened, that a Blender script executed, that an FBX or GLB imported, or that a generated model looks correct. The Milestone 0A execution environment contained neither Unreal Engine nor Blender.

## 10. Related Documents

- `Documentation/TECHNICAL_ARCHITECTURE.md`
- `Documentation/VEHICLE_SYSTEM_DECISION.md`
- `Documentation/BLENDER_PIPELINE_DESIGN.md`
- `Documentation/DRIVER_PIPELINE_DESIGN.md`
- `Documentation/MILESTONE_PLAN.md`
- `Documentation/VERSION_MATRIX.md`
- `Documentation/DECISION_LOG.md`

## 11. Verification Ledger for This Document

| Claim | Label |
| --- | --- |
| The originality rules stated here are complete and internally consistent | statically inspected |
| The related documents listed in §10 exist in this repository | statically inspected |
| Quality targets in §8 are achievable on target hardware | requires playtesting |
| Preview and Final Quality profiles behave as described | requires Unreal Editor verification |
| Any part of this project has been compiled, executed or rendered | not claimed — no engine or DCC ran during Milestone 0A |
