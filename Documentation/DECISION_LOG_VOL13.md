# Decision Log — Volume 13

Continues `DECISION_LOG_VOL12.md`, which froze full at 19,001 bytes after D-073
(per the D-057 volume rule). First decision in this volume: D-074.

---

## D-074 — Engine bring-up phase: verify Milestone 1 acceptance before starting Milestone 5 (2026-08-13)

**Context.** Milestone 4 closed 15/15 on the 13-part geometry (D-071, D-073).
Unreal Engine 5.8 is now installed on the developer's local Windows machine —
the first time this project has had access to a running engine. The obvious
next milestone is Milestone 5 (Vehicle Visual + Physics Integration), but
`MILESTONE_PLAN.md` makes M5 depend on M2, and M2 on M1, and the Milestone
Status table records that **Milestone 1 acceptance has never been verified**:
the project has never been compiled and the editor has never been opened.
Starting M5 on top of an unverified foundation would violate Cross-Milestone
Rule 1.

**Decision.** Before any M5 work, run an **engine bring-up phase** on the
local machine, in this order:

1. **B-1 — Toolchain check.** Confirm Visual Studio 2022 with the
   *Game development with C++* workload (and .NET SDK) is installed.
   Record the exact Unreal Engine version string from the editor's
   About dialog (the "5.8" figure comes from the project brief and has
   not yet been read off a running editor).
2. **B-2 — Milestone 1 acceptance run.**
   - Project compiles from clean (Development Editor | Win64).
   - Editor opens `Unreal/ApexFormula.uproject` without module load errors.
   - Automation tests are discovered and pass (Session Frontend → Automation).
   - Evidence: build log tail, screenshot of the editor open with the
     Output Log showing no module errors, screenshot of the automation
     test results. Verification labels: `requires local compilation`,
     `requires Unreal Editor verification`.
3. **B-3 — Milestone 2 criteria sweep.** With the editor running, attempt
   the three unverified M2 criteria (drives; does not fall through/oscillate/
   invert; imported skeleton bone names match `UAFBoneNameMap`). Any
   criterion that fails becomes an OPEN item; none of them blocks B-2.
4. Only after B-2 passes does Milestone 5 planning begin (import of the
   M4 bodywork; units, axis convention, UCX collision packaging and the
   OBJ-vs-FBX question are decided there, not here).

**Also recorded — repository hygiene violation (OPEN-074-A).** The export
scratch directories `out/` and `out2/` are tracked on `main`, in direct
conflict with the D-069.4 rule that they are never committed. Fix: remove
them from the index (`git rm -r --cached out out2`), add both to
`.gitignore`, commit. No geometry changes, so no gate re-run is triggered.

**Why not jump straight to M5.** The import target (UE editor) has never
been proven to even open this project. Any import problem found before B-2
passes would be unattributable: it could be the mesh, the import settings,
or a broken project. Bring-up first makes every later failure diagnosable.

**Status.** B-1..B-3 require the developer's local machine
(`requires local compilation`, `requires Unreal Editor verification`,
`requires playtesting`). OPEN-074-A can be fixed from any clone.

### Open questions carried into this volume

| ID | Summary | Status |
| --- | --- | --- |
| OPEN-051-B, 053-A, 060-A, 065-A, 065-B, 066-A, 066-B, 068-A, 068-B, 068-C | Documentation/CI hygiene items carried from VOL12 | OPEN |
| OPEN-074-A | `out/` and `out2/` tracked on `main` despite D-069.4 | OPEN |
