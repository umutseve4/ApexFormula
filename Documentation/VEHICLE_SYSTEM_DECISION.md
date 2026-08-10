# ApexFormula — Vehicle System Technical Decision Record

**Document status:** statically authored decision record.
**Milestone:** 0A
**Decision ID:** TDR-001
**Target:** Unreal Engine 5.8, Windows, C++ primary.

---

## 0. Scope and Honesty Statement

This record compares four candidate vehicle architectures for ApexFormula and
recommends one for the first playable prototype and one long-term direction.

**No benchmark results are presented, because none were run.** No frame times,
no substep timings, no comparative physics accuracy measurements, and no
determinism test results exist for this project. Any statement that would
require running Unreal Engine is labelled **requires Unreal Editor
verification** or **requires local compilation**.

**No undocumented engine capability is asserted.** Where the exact feature set,
API surface, or maturity of a system in Unreal Engine 5.8 is not confirmed by
the product owner's local installation, this document says so explicitly rather
than claiming it.

Terminology used below refers to Unreal's vehicle offerings by their commonly
used names — Chaos Vehicles and Chaos Modular Vehicles. **Whether both are
present, enabled by default, or production-ready in the specific Unreal Engine
5.8 build installed locally is `requires Unreal Editor verification`.** This is
the single largest open assumption in this record and is tracked in
`VERSION_MATRIX.md` and `DECISION_LOG.md`.

---

## 1. Candidate Architectures

### A. Chaos Vehicles

Unreal's established vehicle plugin providing a wheeled vehicle pawn with
suspension raycasts/sweeps, wheel setup definitions, engine/transmission/
differential modelling, and a movement component integrated with Chaos physics.

### B. Chaos Modular Vehicles

Unreal's newer modular approach, in which a vehicle is assembled from discrete
simulation modules rather than a single monolithic movement component.

### C. Custom Simulation Layer on Unreal Physics

A bespoke vehicle model written in C++ on top of Unreal's rigid body physics:
custom suspension, custom tire model, custom drivetrain, custom integration
step, with the engine providing only the rigid body and collision queries.

### D. Hybrid Architecture

Unreal's vehicle system provides the base rigid body, suspension, and wheel
contact solution. ApexFormula-specific C++ components layer on top of it:
aerodynamics, tire thermal and wear state, brake thermal state, fuel mass,
fictional hybrid energy, setup application, and telemetry — applying forces and
modulating parameters through documented, engine-provided interfaces.

---

## 2. Evaluation Criteria

Each criterion is assessed qualitatively. Ratings are **engineering judgement**,
not measurements.

Legend: ●●● strong fit · ●●○ workable · ●○○ weak / high cost · ??? unverified

| Criterion | A. Chaos Vehicles | B. Chaos Modular | C. Custom | D. Hybrid |
|---|---|---|---|---|
| High-downforce open-wheel racing | ●●○ | ●●○ | ●●● | ●●● |
| Open-wheel suspension fidelity | ●●○ | ●●○ | ●●● | ●●○ |
| Tire temperature and degradation | ●○○ | ●●○ | ●●● | ●●● |
| Active aerodynamics | ●●○ | ●●○ | ●●● | ●●● |
| Hybrid energy systems | ●○○ | ●●○ | ●●● | ●●● |
| Advanced telemetry | ●●○ | ●●○ | ●●● | ●●● |
| AI drivers | ●●● | ●●○ | ●○○ | ●●● |
| Controller input | ●●● | ●●● | ●●○ | ●●● |
| Steering wheel input / force feedback | ●●○ | ●●○ | ●●● | ●●● |
| Determinism | ●●○ | ●●○ | ●●● | ●●○ |
| Replay preparation | ●●○ | ●●○ | ●●● | ●●● |
| Future multiplayer support | ●●● | ●●○ | ●○○ | ●●○ |
| Debugging | ●●● | ●●○ | ●●○ | ●●● |
| Maintainability | ●●● | ●●○ | ●○○ | ●●● |
| Unreal Engine 5.8 support | ??? | ??? | ●●● | ??? |

### Criterion notes

**High-downforce open-wheel racing.** Downforce is fundamentally an external
force applied to the chassis as a function of velocity, ride height, and aero
configuration. Every option can receive such a force; the difference is how
naturally the tire and suspension model responds to the resulting large load
transfer. A custom or hybrid model gives explicit control over that response.

**Open-wheel suspension.** Formula-style suspension has very low travel, high
stiffness, and significant aero-induced load variation. Ray/sweep-based
suspension models are common and workable in games, but stiff, low-travel setups
are the regime where they are most sensitive to substep count and contact
stability. **The behaviour of the engine's suspension solver at ApexFormula's
target stiffness is `requires local compilation` and `requires playtesting`.**

**Tire temperature and degradation.** This is domain-specific state that a
general-purpose vehicle plugin is not expected to provide in the depth this
project wants. In every option it is realistically ApexFormula's own code. The
question is only whether that code can cleanly modulate the underlying grip
each frame — which favours architectures with a documented parameter surface.

**Active aerodynamics.** Fictional active aero means the aero coefficients change
at runtime based on a state machine. This is straightforward as an external
force/coefficient system in all four options.

**Hybrid energy systems.** Fictional deployment and regeneration is a
torque-and-budget accounting problem layered onto the drivetrain. Cleanest when
ApexFormula owns the accounting and applies the result as additional or reduced
drive torque.

**Advanced telemetry.** Depends on read access to per-corner load, slip, and
contact state. A custom layer trivially exposes everything it computes. Plugin
solutions expose what they choose to expose — **the precise per-wheel telemetry
surface available in 5.8 is `requires Unreal Editor verification`.**

**AI drivers.** AI benefits enormously from a vehicle system that already
integrates with engine navigation, input abstraction, and existing tooling.
Writing a fully custom vehicle also means writing the AI's control model against
that custom vehicle with no engine support — a substantial extra cost.

**Controller and steering wheel input.** Input abstraction is largely
independent of the physics choice. Force feedback fidelity, however, depends on
having access to meaningful per-frame force data (self-aligning torque, load) —
which again favours architectures where ApexFormula computes or can read those
values.

**Determinism.** Fully deterministic vehicle simulation across machines is hard
in any floating-point physics engine. A custom fixed-step integrator is the most
controllable. Plugin-based solutions inherit the engine's substepping and solver
behaviour. **No determinism testing has been performed for this project.**

**Replay preparation.** Replay can be implemented either as state recording
(record transforms/telemetry, play back) or as input recording plus
deterministic re-simulation. State recording works with all four options and is
the low-risk default. Input-based replay would require determinism guarantees
that are unverified.

**Future multiplayer.** Established engine vehicle systems are more likely to
have existing replication considerations; a fully custom model must solve
replication from scratch. **The specific networking support of each option in
5.8 is `requires Unreal Editor verification`.**

**Debugging and maintainability.** A custom simulation means owning every bug in
suspension, contact, and integration — permanently, with one developer. This is
the single strongest argument against option C for this project's staffing
reality.

**Unreal Engine 5.8 support.** Marked `???` for the three plugin-dependent
options because the presence, default-enabled state, and production maturity of
each system in the locally installed 5.8 build has not been verified. Option C
is marked strong only in the narrow sense that it depends on core rigid body
physics rather than on a specific vehicle plugin.

---

## 3. Analysis

### Why not A alone

Chaos Vehicles as a base is credible and well-understood, and it scores well on
AI, debugging, maintainability, and networking familiarity. But ApexFormula's
distinguishing systems — tire thermal/wear state, active aero, hybrid energy,
deep telemetry, setup-driven handling — are all outside what a stock wheeled
vehicle component is expected to provide. Using option A "alone" is not actually
a real option: it inevitably becomes option D the moment those systems are
added. Listing A alone therefore describes a scope this project does not want.

### Why not B as the first step

Modular vehicles are conceptually the best long-term match for ApexFormula's
component-oriented architecture: independent simulation modules map almost
one-to-one onto the component strategy in `TECHNICAL_ARCHITECTURE.md`. The
obstacle is purely one of verification. **Its availability, API stability,
documentation quality, and production maturity in the locally installed Unreal
Engine 5.8 have not been confirmed.** Committing the first playable prototype to
an unverified system risks discovering a blocking limitation at the worst
possible time — during Milestone 2, when the goal is simply to get a car moving.

### Why not C

A fully custom simulation gives maximum control and maximum determinism, and it
is genuinely the right answer for some hardcore simulators. For ApexFormula it
is the wrong trade:

- It front-loads months of suspension/contact/integration engineering before the
  first playable milestone.
- It provides no engine support for AI vehicle control.
- It makes future multiplayer strictly harder, not easier.
- It concentrates all long-term maintenance risk on a single developer.
- It offers no benefit that a hybrid cannot substantially match for a game that
  is simulation-leaning rather than a licensed-grade simulator.

### Why D

The hybrid architecture matches the project's actual shape:

- The engine solves the problems that are expensive to write and cheap to
  inherit: rigid body dynamics, collision, suspension contact, wheel kinematics,
  and integration with AI and input systems.
- ApexFormula owns exactly the systems that define its identity: aerodynamics,
  tires, brakes, fuel, hybrid energy, setup, and telemetry — all as independent
  C++ components, exactly as `TECHNICAL_ARCHITECTURE.md` §4 specifies.
- The seam between the two is a narrow, documented interface, which means the
  underlying vehicle base can be swapped later without discarding ApexFormula's
  simulation layer.

That last point is decisive. In a hybrid architecture, ApexFormula's proprietary
value lives above the seam. Changing the base vehicle system later is a
migration, not a rewrite.

---

## 4. Recommendation

### 4.1 First playable prototype (Milestones 2–5)

**Recommended: D — Hybrid architecture, using Chaos Vehicles as the base layer.**

Rationale: it reaches a driveable car fastest, keeps AI and input support, and
places every ApexFormula-specific system in project-owned C++ components from
the very first implementation. The base is the most conservative available
choice; the value layer is entirely ours.

Implementation constraints for the prototype:

1. All ApexFormula simulation components are written against a project-owned
   interface (`IApexVehicleBase` or equivalent), **not** directly against the
   plugin's concrete types.
2. All plugin-specific calls are isolated behind a named compatibility layer
   (`ApexFormulaCompat`), so a base-layer swap touches one file set.
3. Bone names are resolved through the central `AF_BoneMapping` Data Asset only.
4. No ApexFormula component assumes a specific suspension solver internal.
5. Milestone 2 targets a *placeholder* vehicle — driveable, not tuned.

### 4.2 Long-term direction

**Recommended: remain on D, with a planned evaluation of Chaos Modular Vehicles
as the base layer once it is verified locally.**

The long-term architecture stays hybrid. What may change is which system sits
below the seam. Modular vehicles are the preferred future base *if and only if*
local verification confirms availability, maturity, and a workable API in 5.8.

Re-evaluation triggers — any one of these reopens TDR-001:

- Local verification confirms Chaos Modular Vehicles is available and mature in
  the installed 5.8 build.
- The base suspension solver proves unable to hold ApexFormula's target
  stiffness and downforce range in playtesting.
- Determinism requirements harden because multiplayer or input-based replay is
  promoted from "prepared for" to "required".
- Telemetry needs per-corner data the base layer does not expose.

### 4.3 Explicitly rejected

- **Option C (fully custom)** is rejected for the first playable prototype and
  for the medium term. It is only reconsidered if a hard determinism requirement
  emerges that neither base layer can satisfy.
- **Option A described as "stock only"** is rejected because it does not
  describe an architecture capable of delivering the project's stated systems.

---

## 5. Consequences of This Decision

**Accepted:**

- ApexFormula inherits the base vehicle system's solver behaviour, including its
  substepping characteristics and any determinism limitations.
- Force feedback fidelity depends partly on data the base layer exposes.
- A future base-layer migration is a real, planned possibility with real cost —
  budgeted as a migration, not a rewrite.

**Mitigated by:**

- The compatibility layer and project-owned interface (§4.1.1, §4.1.2).
- Owning tire, aero, brake, fuel, and energy models entirely in project code.
- State-based replay as the default plan, avoiding a determinism dependency.

**Not claimed:**

- That this architecture compiles. **Requires local compilation.**
- That it produces good handling. **Requires playtesting.**
- That the base layer meets any specific performance figure. **No benchmarks
  were run.**
- That any named plugin exists in a particular form in the installed 5.8 build.
  **Requires Unreal Editor verification.**

---

## 6. Gate Condition

Per project rules, advanced vehicle implementation does not begin until this
decision record exists. This document satisfies that gate for the **prototype**
decision.

Before **Milestone 10** (advanced tire, aero, energy, fuel, brake, and setup
simulation) begins, TDR-001 must be revisited and either reaffirmed or amended,
using verification results gathered during Milestones 2–5.

---

## 7. Verification Checklist (to be performed locally by the product owner)

| # | Item | Label |
|---|---|---|
| 1 | Confirm which vehicle plugins ship with and are enabled in the installed Unreal Engine 5.8 | requires Unreal Editor verification |
| 2 | Confirm the per-wheel data surface available for telemetry | requires Unreal Editor verification |
| 3 | Confirm physics substepping configuration options and defaults | requires Unreal Editor verification |
| 4 | Confirm the vehicle system's expectations for skeletal mesh hierarchy and wheel bone references against the AF_ bone convention | requires Unreal Editor verification |
| 5 | Build a placeholder vehicle and assess suspension stability under high downforce | requires local compilation, then requires playtesting |
| 6 | Assess force feedback data availability with a steering wheel | requires playtesting |
