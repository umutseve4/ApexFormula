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

---

## D-075 — OPEN-074-A resolved: out/ and out2/ untracked, .gitignore updated (2026-08-13)

**Context.** D-074 recorded that the export scratch directories `out/`
(26 files) and `out2/` (26 files) were tracked on `main`, violating D-069.4.

**Action taken.** On branch `fix/open-074-a-untrack-out` (from `main`
@ `c5d870c`), executed remotely via the GitHub API (no local clone):

1. Deleted all 52 tracked files — 26 in `out/`, 26 in `out2/` — one commit
   per file (`chore(OPEN-074-A): untrack <path> (D-069.4)`). The API has no
   equivalent of `git rm -r --cached`, so blob deletion is the remote path;
   local working copies keep their untracked `out*/` contents untouched.
2. Appended `out/` and `out2/` to `.gitignore` with a comment referencing
   D-069.4 / D-074 (commit `455ce8e`).
3. Verified the branch root tree no longer contains `out/` or `out2/`.

Branch merged to `main` as a single squash commit so `main` history carries
one hygiene change instead of ~53 commits. No geometry, pipeline, or gate
artefacts were modified — per D-074, no gate re-run is triggered.

**Verification.** `verified (remote)`: root tree listing on the merged
commit shows no `out/`/`out2/`; `.gitignore` contains both entries.
Local check for the developer: `git pull` then `git status` must show
`out/` and `out2/` as ignored, not untracked-and-listed.

**Status.** OPEN-074-A → RESOLVED. Bring-up phase B-1/B-2 (D-074) is now
the sole blocking work item.

---

## D-076 — B-1 passed; first successful compile with a 9-file UE 5.8 API compatibility fix; LFS PNG anomaly recorded (2026-08-14)

**Context.** The repository was cloned to the developer's Windows machine
(`C:\Users\umuts\Documents\UludagFormula`, HEAD `f68df52`). The D-074 B-2
acceptance run began with the first-ever compile attempt
(`Build.bat ApexFormulaEditor Win64 Development`).

**B-1 result — toolchain verified.** Visual Studio 2022 toolchain
14.44.35228, Windows SDK 10.0.26100.0, UE 5.8 bundled .NET SDK 10.0,
ISPC 1.24.0. 4 physical cores / 7.93 GB RAM (UBT limited itself to 1–2
parallel actions).

**Compile findings and fixes (commit `a5ca90c`).** The first build failed
with three classes of UE 5.8 API incompatibilities, all authored before the
project had ever seen a real engine:

1. **7× test files** (`ApexFormulaTests/Private/*Tests.cpp`):
   `static const int32 <X>TestFlags` — `EAutomationTestFlags` is an
   `enum class` in modern UE; the constants no longer implicitly convert
   to `int32`. Fix: declare the flag constants as
   `static const EAutomationTestFlags`.
2. **`AFVehicleCompatibilityLayer.cpp`:** `UChaosVehicleWheel` in UE 5.8 has
   no `SuspensionNaturalFrequency` member. The assignment was removed; the
   natural-frequency → spring-rate conversion is deferred to M10 (physics
   tuning), where the equivalent `WheelSetup`/spring parameters are decided.
3. **`AFVehiclePawn.cpp`:** one `AF_LOG_RULE(LogAFVehicle, Log, ...)` call
   did not match the macro signature
   `(Category, ParticipantId, SessionTime, Format, ...)`. Fixed by passing
   `ParticipantId` and `GetWorld() ? GetWorld()->GetTimeSeconds() : 0.0`.

Second build: **Result: Succeeded** — all six modules compiled and linked
(ApexFormulaCore/Vehicle/Race/UI, ApexFormulaEditor, ApexFormulaTests).
Verification label: `verified (local build log)`. This satisfies the
"project compiles from clean" line of B-2; the editor-open and
automation-test lines remain open.

**Hygiene — git identity and credentials (one-time setup).** The developer
machine had no git identity and no working browser association for Git
Credential Manager (GCM crashed with "Uygulama bulunamadı" and fell back to
dead password auth). Resolved with: `user.name`/`user.email` set to the
GitHub noreply address, `credential.guiPrompt false`, and
`credential.gitHubAuthModes device` — device-code flow completed at
`github.com/login/device`. No tokens or secrets stored in the repository.

**Also recorded — OPEN-076-A (LFS pointer anomaly).** The four acceptance
screenshots `Documentation/acceptance/{front,pylon_detail,side,top}.PNG`
are tracked by an LFS pattern in `.gitattributes` but were committed as
normal blobs. Every local git operation warns "should have been pointers,
but weren't", and the files sit permanently modified in the working tree
(checkout cannot clean them). Harmless as long as they are never staged;
fix options (migrate to real LFS objects, or drop the LFS pattern for
`Documentation/acceptance/`) are a post-M1 hygiene decision.

**Status.** B-1 verified. B-2 partially verified (compile only). Next:
editor opens `Unreal/ApexFormula.uproject` with no module errors →
Session Frontend automation tests green → screenshots = M1 acceptance.

### Open questions carried into this volume

| ID | Summary | Status |
| --- | --- | --- |
| OPEN-051-B, 053-A, 060-A, 065-A, 065-B, 066-A, 066-B, 068-A, 068-B, 068-C | Documentation/CI hygiene items carried from VOL12 | OPEN |
| OPEN-074-A | `out/` and `out2/` tracked on `main` despite D-069.4 | RESOLVED (D-075) |
| OPEN-076-A | 4 acceptance PNGs tracked by LFS pattern but committed as normal blobs | OPEN |
