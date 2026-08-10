# ApexFormula — Project Vision

**Document status:** statically authored design document. No engine or tool execution occurred.
**Milestone:** 0A — Technical architecture and decision records.

---

## 1. Project Identity

**Internal project name:** ApexFormula

ApexFormula is an original 3D open-wheel formula-style racing game. It is an
original fictional motorsport intellectual property. It is not a simulation of,
adaptation of, or successor to any real-world racing series.

- Root project identity: `ApexFormula`
- Unreal asset prefix: `AF_`
- Blender Python script prefix: `af_`
- Repository name: `ApexFormula`

No real-world racing series abbreviation or mark is used in project names,
filenames, class names, asset names, script names, folder names, documentation
titles, or public-facing terminology.

## 2. Originality Rules

The following are **prohibited** anywhere in the project — code, assets,
documentation, UI text, marketing text, or metadata:

- Any real motorsport series name, abbreviation, or mark
- Real racing team names
- Real driver names
- Real sponsor names
- Official logos of any real series, team, or sponsor
- Real liveries
- Exact real-world car reproductions
- Exact real-world track reproductions
- Any protected motorsport branding

The following are **required** instead:

- Fictional teams
- Fictional drivers
- Fictional sponsors
- Fictional vehicles
- Fictional circuits
- Fictional liveries, helmets, and racing suits
- Fictional championship rules

Vehicle dimensions, aerodynamic values, tire models, and energy systems are
**ApexFormula design values**. They are never described as the official
measurements or official regulations of any real series or governing body.

If real motorsport technical regulations are ever consulted as a general
engineering reference, that use is documented separately with source, season,
units, and limited purpose — and never presented as project-authoritative.

## 3. Design Goals

1. **An original open-wheel racing experience** with high-downforce handling
   character, sharp braking, and precise corner entry.
2. **A believable simulation layer** covering aerodynamics, tires, brakes, fuel,
   and hybrid energy — expressed through fictional, tunable design values.
3. **Readable driver feedback.** The simulation must communicate its state to the
   player through handling, HUD, audio, and telemetry — not through hidden math.
4. **Deterministic, authoritative gameplay logic in C++**, so that replay and
   future multiplayer remain viable without rewriting core systems.
5. **A data-driven asset pipeline** where Blender-generated content flows into
   Unreal through documented, repeatable, validated steps.
6. **A separation of preview quality from final quality**, so that development on
   modest hardware never caps the ceiling of the finished product.

## 4. Gameplay Direction

The core loop is: **prepare the car → drive the session → evaluate the result.**

Target session types (implemented progressively across milestones, not at once):

- Practice
- Qualifying
- Race

Supporting gameplay pillars:

- Ordered checkpoint and sector timing with valid/invalid lap rules
- Vehicle setup screens that meaningfully change handling
- Tire, brake, fuel, and energy state that evolves over a stint
- AI opponents with race-legal behaviour
- Pit lane, pit stops, race control, and penalties
- HUD, telemetry, gamepad and steering wheel input
- Replay preparation and future multiplayer preparation

## 5. Simulation versus Accessibility Philosophy

ApexFormula is a **simulation-leaning racing game with layered accessibility**,
not a hardcore-only simulator and not an arcade racer.

Guiding rules:

1. **The underlying model is always the simulation model.** Assists are applied as
   input conditioning and correction layers on top of a single physics truth.
   There is no separate "arcade physics" code path.
2. **Assists are explicit and enumerable.** Steering assist, braking assist,
   traction control, stability control, automatic gearbox, and racing line are
   individually toggleable and individually recorded in session metadata.
3. **Difficulty never invalidates the rules.** Lap validity, penalties, and timing
   behave identically at every assist level.
4. **Depth is opt-in, not mandatory.** A player who never opens the setup screen
   must still be able to complete a competitive session on a default setup.
5. **The telemetry is the tutorial.** Advanced players learn the model by reading
   the same telemetry the developers use.

## 6. Platform Assumptions

- **Primary development and build platform:** Windows
- **Primary engine:** Unreal Engine 5.8
- **Primary DCC tool:** Blender 5.2 LTS
- **Primary gameplay language:** C++
- **Configuration and presentation layer:** Blueprints
- **Procedural asset generation and validation:** Blender Python
- **Primary skeletal asset interchange:** FBX
- **Optional static preview / interchange:** GLB
- **Source control:** Git, with Git LFS for appropriate large binary assets

Input targets: keyboard, gamepad, and steering wheel (with pedals). Steering
wheel support is a first-class target, not an afterthought, because force
feedback fidelity constrains how the vehicle model exposes forces.

No console platform is assumed. No mobile platform is assumed. The architecture
avoids Windows-only gameplay logic so that a future platform decision is not
blocked, but no non-Windows target is promised.

## 7. Quality Targets

Quality is expressed in three tiers that apply across vehicles, tracks, and
characters.

| Tier | Purpose | Applies to |
|---|---|---|
| Preview | Fast iteration on modest hardware | Development only |
| Production | Shipping in-game quality | The default deliverable |
| Hero | Close-up cinematic presentation | Menus, garage, podium, replays |

Character-specific tiers (see `DRIVER_PIPELINE_DESIGN.md`):

- **TIER A — Cockpit Driver:** gameplay-optimized, helmet normally worn, limited
  face visibility, animation and performance prioritized.
- **TIER B — Presentation Driver:** menus, garage, podium; recognizable likeness;
  improved skin, eyes, hair, facial hair, and clothing.
- **TIER C — Hero Driver:** close-up cinematic presentation, highest practical
  facial and material quality, optional advanced facial animation. Not required
  for the first playable release.

## 8. Preview versus Final-Quality Principles

The development laptop may not be able to run every stage of the final
production pipeline. This **does not** reduce the final quality target.

Five binding principles:

1. **Two profiles, one source of truth.** `DevelopmentPreview` and `FinalQuality`
   are separate configuration profiles. Both read the same source assets and the
   same design data. Neither profile is the "real" asset.
2. **Preview is derived, never destructive.** Preview-quality output is written to
   generated/derived locations. A preview run never overwrites, downsamples, or
   deletes a source asset or a final-quality artifact.
3. **Heavy stages are deferrable.** Lightmap and distance-field baking, high-LOD
   generation, shader permutation compilation, texture compression at final
   resolution, cinematic rendering, and packaging are all designed to be executed
   later on a stronger Windows machine without reauthoring content.
4. **Profile state is visible.** The active profile is logged at startup, shown in
   development HUD builds, and stamped into validation reports, so a preview
   result is never mistaken for a final result.
5. **Acceptance criteria name their profile.** Every milestone acceptance
   criterion states whether it is satisfied under Preview, Final, or both.

## 9. Verification Posture

This project follows strict honesty rules. In all project documentation and all
generated reports, every result carries one of the following labels:

- statically inspected
- automatically validated
- requires Blender execution
- requires Unreal Editor verification
- requires local compilation
- requires visual inspection
- requires playtesting

No document in this repository claims that Unreal Engine compiled, that an
Unreal project opened, that a Blender script executed, that an FBX or GLB
imported, or that any generated model was visually confirmed. Milestone 0A
produced documentation only.

## 10. Privacy Posture

Personal reference photographs remain local to the product owner's computer.
They are never uploaded, transmitted, embedded, packaged, or committed. A
private local input convention exists and is excluded from Git. No photographs
are requested in Milestone 0A. See `DRIVER_PIPELINE_DESIGN.md`.
