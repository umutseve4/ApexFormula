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

### Open questions carried into this volume

| ID | Summary | Status |
| --- | --- | --- |
| OPEN-051-B, 053-A, 060-A, 065-A, 065-B, 066-A, 066-B, 068-A, 068-B, 068-C | Documentation/CI hygiene items carried from VOL12 | OPEN |
| OPEN-074-A | `out/` and `out2/` tracked on `main` despite D-069.4 | RESOLVED (D-075) |
