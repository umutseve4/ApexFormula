# ApexFormula — Vehicle System Architecture Decision Record

**Document status:** statically authored decision record (Milestone 0A). No vehicle code exists. No engine benchmark was run. No profiling data is presented, because none was collected.

**Rule this document satisfies:** advanced vehicle implementation must not begin before a written architecture decision record exists. This is that record. It is the gate for Milestone 2 and Milestone 10.

---

## 1. Decision Question

Which vehicle physics foundation should ApexFormula use in Unreal Engine 5.8 for (a) the **first playable prototype** and (b) the **long-term simulation direction**?

## 2. Candidates

**A. Chaos Vehicles** — Unreal's built-in vehicle system. A wheeled vehicle movement component with wheel setups, suspension, engine/transmission/differential models, driven by bone-mapped wheels on a skeletal mesh.

**B. Chaos Modular Vehicles** — the newer modular decomposition of vehicle behaviour into composable simulation modules rather than one monolithic movement component.

**C. Custom simulation on top of Unreal physics** — ApexFormula authors its own tyre, suspension, aero and drivetrain models, applying forces to a rigid body each sub-step; the engine supplies rigid-body integration and collision only.

**D. Hybrid** — a built-in system carries chassis, suspension and collision; ApexFormula overrides or layers the physically expressive parts (tyre force generation, aero, energy, fuel mass, brake thermals) on top.

## 3. Evaluation Criteria

Each candidate is scored against fifteen criteria. Scores are **design-judgement estimates from documented system characteristics, not measurements**. There are no benchmark numbers in this document because no benchmark was run.

Scale: `++` strong, `+` adequate, `~` neutral/uncertain, `-` weak, `--` poor. `?` means the honest answer is unknown until verified in the editor.

| # | Criterion | A. Chaos Vehicles | B. Chaos Modular | C. Custom | D. Hybrid |
| --- | --- | --- | --- | --- | --- |
| 1 | Physical realism ceiling | + | + | ++ | ++ |
| 2 | Tyre model control | - | ~ | ++ | ++ |
| 3 | Suspension control | + | + | ++ | + |
| 4 | Aerodynamic control | ~ | + | ++ | ++ |
| 5 | Setup/tuning depth | + | + | ++ | ++ |
| 6 | Determinism & repeatability | ~ | ~ | + | ~ |
| 7 | Multiplayer readiness | + | ? | - | ~ |
| 8 | Development speed to first drivable car | ++ | + | -- | + |
| 9 | Engine-version upgrade risk | ++ | ~ | ++ | + |
| 10 | Debuggability / introspection | ~ | + | ++ | + |
| 11 | Telemetry richness | ~ | + | ++ | ++ |
| 12 | AI opponent integration | + | + | ~ | + |
| 13 | Team/solo maintenance cost | ++ | + | -- | ~ |
| 14 | Documentation & community support | ++ | ~ | -- | + |
| 15 | Risk of dead-end rewrite | + | ? | ~ | + |

### Criterion notes

1. **Physical realism ceiling** — how good can it eventually get. Custom and hybrid are unbounded; built-in systems are bounded by their internal models.
2. **Tyre model control** — the single most decisive criterion for a formula-style car. Grip, slip curves, temperature windows, wear and pressure response define the driving experience. Built-in tyre behaviour is comparatively opaque; a custom force model is fully owned.
3. **Suspension control** — geometry, ride height sensitivity, anti-roll, damper response. Built-in suspension is usable; custom offers full control at high cost.
4. **Aerodynamic control** — downforce vs. speed and ride height, aero balance shift, dirty air, active aero. All approaches allow *adding* aero forces; the difference is how cleanly aero couples to the suspension/ride-height state.
5. **Setup/tuning depth** — how many meaningful, physically coupled setup parameters can be exposed to the player.
6. **Determinism & repeatability** — needed for regression tests, replays and fair racing. No approach is assumed deterministic. A custom model reduces hidden state but cannot make the underlying solver deterministic by itself.
7. **Multiplayer readiness** — built-in vehicle movement components ship with network prediction concepts already considered; a from-scratch model requires bespoke prediction work.
8. **Development speed to first drivable car** — measured in developer effort to a car that steers, accelerates and brakes on a surface.
9. **Engine-version upgrade risk** — how exposed the project is when the engine version moves.
10. **Debuggability** — ability to see why the car did what it did.
11. **Telemetry richness** — availability of per-corner slip, load, temperature and force values for the HUD and analysis.
12. **AI opponent integration** — how straightforwardly an AI controller can drive the same vehicle.
13. **Maintenance cost** — ongoing burden for a small team.
14. **Documentation & community support** — availability of reference material when something breaks.
15. **Risk of dead-end rewrite** — probability that the choice must be thrown away later.

### Honest uncertainty

Entries marked `?` are genuine unknowns for Unreal Engine 5.8 specifically:

- The exact module name, maturity, API surface and production-readiness of **Chaos Modular Vehicles** in 5.8.
- Whether Chaos Modular Vehicles' networking support in 5.8 is at parity with the classic path.
- Whether the classic Chaos Vehicles path remains fully supported, deprecated, or is in transition in 5.8.

These are **assumptions requiring verification** and are listed in `Documentation/VERSION_MATRIX.md` §5. They must be resolved in the Unreal Editor before Milestone 10 begins. They do **not** block Milestone 2.

## 4. Decision — First Playable Prototype

**Chosen: A. Chaos Vehicles (built-in), wrapped behind an ApexFormula abstraction layer.**

Rationale:

1. Milestone 2's objective is "a placeholder vehicle that drives", not "a correct formula car". Criterion 8 dominates at this stage.
2. It exercises the whole pipeline — Blender-generated skeletal mesh with `AF_*` bones → FBX → import → wheel setup → drivable pawn — which is the actual risk being retired in Milestones 0B–2. Vehicle *fidelity* is not the risk; *pipeline integrity* is.
3. Criterion 14 matters most when the developer is learning the engine's vehicle path.
4. Choosing it does not foreclose C or D, **provided the abstraction layer exists from the first commit**.

### Mandatory conditions attached to this decision

This choice is only acceptable with all of the following in place:

- **`UAFVehicleCompatibilityLayer`** isolates every direct call into the engine vehicle API. Gameplay code never calls the engine vehicle component directly.
- **ApexFormula-owned state stays ApexFormula-owned.** Tyre temperature/wear, aero, energy, fuel mass and brake thermals live in ApexFormula components from the start (see `Documentation/TECHNICAL_ARCHITECTURE.md` §4), even while the underlying force generation is still the built-in one. Only the *force source* is borrowed, never the *state model*.
- **`StepSimulation(DeltaTime, InputFrame)`** is the entry point for ApexFormula subsystems, so the force source can later be swapped without touching call sites.
- **Bone names come from `UAFBoneNameMap`**, never from hardcoded strings, so a later change of vehicle system does not become a rig rewrite.
- **Telemetry is captured through `UAFTelemetryBus`** from day one, so behaviour before and after any future migration is comparable.

## 5. Decision — Long-Term Direction

**Chosen: D. Hybrid — engine-provided rigid body, collision and suspension solving; ApexFormula-authored tyre force generation, aerodynamics, energy, fuel-mass and brake-thermal models.**

Rationale:

1. Criteria 1, 2, 4, 5 and 11 — the criteria that decide whether the game feels like a formula car — all favour ApexFormula owning the force model.
2. Criteria 8, 13 and 14 — the criteria that decide whether the project survives — all favour not rewriting rigid-body dynamics, collision, or broadphase.
3. Full custom (C) is rejected primarily on criteria 7, 13 and 14: bespoke network prediction plus bespoke solver maintenance is not a realistic burden for this project, and the realism gain over a hybrid is marginal.
4. Pure built-in (A or B) is rejected as a *long-term* answer on criterion 2: the tyre model is the game, and it must be owned.

**Migration path (A → D):** the abstraction layer means the migration is incremental, not a rewrite. Order: (1) aero forces move first — additive and low risk; (2) brake thermals and fuel mass — state-only, then force-affecting; (3) energy deployment; (4) tyre force generation last, because it is the largest behavioural change and requires the most re-tuning.

**Gate:** migration steps 1–3 may begin during Milestone 10. Step 4 requires a re-review of this document and a new dated entry in `Documentation/DECISION_LOG.md`.

## 6. Explicitly Rejected

- **B. Chaos Modular Vehicles as the prototype foundation** — rejected for now on unresolved uncertainty (criteria 7, 14, 15 and the `?` entries in §3), not on technical merit. It should be re-evaluated at the start of Milestone 10; if 5.8's modular path is mature and network-ready, it becomes a strong hybrid host and may replace the classic path underneath the same abstraction layer.
- **C. Full custom simulation** — rejected on criteria 7, 8, 13, 14. Revisit only if the hybrid is proven insufficient with evidence from playtesting.

## 7. Verification Ledger for This Document

| Claim | Label |
| --- | --- |
| Criteria table is internally consistent and complete (15 criteria × 4 candidates) | statically inspected |
| No benchmark, frame-time or physics-accuracy measurement is asserted anywhere in this document | statically inspected |
| Chaos Vehicles exists and is usable in Unreal Engine 5.8 | requires Unreal Editor verification |
| Chaos Modular Vehicles module name, maturity and network support in 5.8 | requires Unreal Editor verification |
| Abstraction layer compiles and isolates the engine vehicle API as designed | requires local compilation |
| Built-in vehicle behaviour is acceptable as a Milestone 2 placeholder | requires playtesting |
| Hybrid tyre model produces better feel than built-in | requires playtesting |

## 8. Reversibility

This record is reversible. Superseding it requires: a new dated entry in `Documentation/DECISION_LOG.md`, an amendment section appended to this document (originals are not deleted), and an explicit statement of which milestone the change affects.
