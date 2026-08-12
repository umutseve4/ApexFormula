# Decision Log — Volume 9

**Status:** open
**Range:** D-065 ..
**Opened:** 2026-08-12, at commit following `b8b319a9` (volume 8 closing state).

## Volume map

| Volume | Range | State |
|---|---|---|
| `DECISION_LOG.md` | D-001 .. D-044 | frozen |
| `DECISION_LOG_VOL2.md` | D-045 .. D-050 | frozen |
| `DECISION_LOG_VOL3.md` | D-051 .. D-052 | frozen |
| `DECISION_LOG_VOL4.md` | D-053 .. D-055 | frozen |
| `DECISION_LOG_VOL5.md` | D-056 .. D-058 | frozen |
| `DECISION_LOG_VOL6.md` | D-059 .. D-061 | closed |
| `DECISION_LOG_VOL7.md` | D-062 .. D-063 | closed |
| `DECISION_LOG_VOL8.md` | D-064 | closed by this volume (see D-065.6) |
| `DECISION_LOG_VOL9.md` | D-065 .. | **open** |

Per D-061.2 the open volume's tables are authoritative. As of this commit that
is this file. Frozen and closed volumes are never edited; corrections to them
are recorded here as errata.

## Why this volume exists

Volume 8 stands at 15,893 B. D-057 freezes a volume at roughly 20 KB. D-065
below is approximately 10 KB of prose and tables, so appending it would breach
that threshold. Appending would additionally require retranscribing the whole of
volume 8 through a write interface that has no patch mode, which D-053.6 names
as a real corruption risk with no correctness gain. Opening volume 9 avoids
both. This is the ordinary freeze mechanism, not an exception to it.

---

# D-065 — OPEN-064-A and OPEN-063-A resolved from commit history

**Date:** 2026-08-12
**Type:** bookkeeping resolution. No source file changed, no behaviour changed.
**Status label:** *statically inspected.* Every claim below rests on commit
metadata and on file sizes reported by the repository host. Nothing was
executed, compiled, imported, or opened in Blender or Unreal to produce it.

## D-065.1 — Method, and its limits

Three of the open questions in this project are of one kind: a number recorded
in the documentation disagrees with a number observable in the repository today.
The standing rule (D-060, restated for OPEN-060-A and OPEN-063-A) is that such a
disagreement is **never** to be settled by editing either number until the cause
is known. A refreshed count is not a resolution; it is the destruction of the
evidence that something drifted.

The method used here is the only one available in this environment: read the
commit history of the file in question, find the commits that changed its size,
and compare their stated intent against the observed delta. This proves *when*
and *why* a number moved. It does not prove the file is correct, and it does not
substitute for executing anything.

What this method cannot do, stated plainly:

- It cannot confirm the current file contents are correct. Only CI can, and only
  for the parts CI executes.
- It cannot recover a figure that was never written down.
- It cannot distinguish a wrong measurement from a measurement of a different
  object. Where that ambiguity remains, it is named below rather than resolved.

## D-065.2 — OPEN-064-A row 1: `Tools/af_config_hash_guard.py`

Recorded discrepancy: D-046 states 26,517 B; the file is 26,519 B.

| Commit | Date (UTC) | Effect |
|---|---|---|
| `5faa2d981948db85c290ba122d0f20a8bea31949` | 2026-08-11T18:15:10Z | Creates the file at **26,517 B** (D-046, PR #15) |
| `aa5283c72b4795e40f8f6aff678c2c58faa05768` | 2026-08-11T21:20:53Z | Renames one product-name occurrence in the module docstring (wave 1.5 #3) |

The rename commit predicts its own delta in its message, verbatim:
*"Expected size delta: +2 B (26,517 -> 26,519)."* The live size is 26,519 B.
`ApexFormula` is 12 characters, `UludagFormula` is 14 wait — the delta is +2 B
for one substitution, consistent with every other wave 1.5 commit, which
predicted +2 B per occurrence and was correct each time.

**Cause:** D-046 was correct when written. The file grew by 2 B afterwards, in a
rename commit that documented the growth in advance. The log entry predates the
rename and was never wrong.

**Disposition:** no correction to D-046. Neither number is adjusted. Row 1 is
explained.

## D-065.3 — OPEN-064-A row 2: `Tools/af_mesh_quality.py`

Recorded discrepancy: D-053.6 describes a "~13 KB reconstruction" of
"773 lines"; the file is 30,783 B.

| Commit | Date (UTC) | Effect |
|---|---|---|
| `ed691f9039917960ff2bedf22e08ceb27f5fcaa6` | 2026-08-11T19:06:06Z | Creates the file (D-047). 13 check families C0–C12, 46 self-test cases; the audit it drove reported 274 checks / 274 passed |
| `cc85f950a63327de0cf142d6e05e0141b679fedf` | 2026-08-11T22:10:30Z | Renames four product-name occurrences (wave 1.5 #6b), message states *"Expected size delta: +8 B (4 substitutions x 2 B)"* |

The rename accounts for **8 B**. The gap to be explained is approximately
17,800 B. It is not explained by any commit in the file's history.

The decisive observation is internal to D-053.6 itself. That entry records two
figures for the same artefact: **~13 KB** and **773 lines**.

| Figure pair | Implied bytes per line |
|---|---|
| 30,783 B over 773 lines | 39.8 |
| 13,000 B over 773 lines | 16.8 |

39.8 B/line is ordinary for the commented, banner-separated Python used
throughout `Tools/`. 16.8 B/line is not attainable in that style. The line count
and the live byte size agree with each other; the byte figure disagrees with
both.

**Cause:** the "~13 KB" figure did not describe the file. Under D-053.6 the
object being measured was a *reconstruction* produced by retyping content
through this interface, and a reconstruction that reached only part of the file
would produce exactly this signature — a plausible line count carried over from
the source, a byte count belonging to the fragment.

**This is the honest reading, and it names the wrong record rather than
splitting the difference: D-053.6's byte figure is the erroneous one.** The file
was never 13 KB. D-053.6 remains in a frozen volume and is not edited; this
entry is the erratum.

**Disposition:** OPEN-064-A is **closed**. Neither 30,783 nor 26,519 is
adjusted, and no figure in a frozen volume is rewritten.

## D-065.4 — OPEN-063-A: eight `af_*.py` scripts, or twelve

Recorded discrepancy: `VERSION_MATRIX.md` §5.20 says eight; a later listing
shows twelve.

§5.20 was introduced by commit `0b82ed31312cdf0e4ed6d8832022e25158ffebef` at
**2026-08-10T15:49:33Z**, message *"M0B: VERSION_MATRIX - add 5.16-5.20, the
version risks the 0B scripts introduce."* Its text reads *"The eight scripts are
syntactically valid for the interpreter Blender embeds."* It is a Milestone 0B
statement about the Milestone 0B script set.

The eight scripts of that set, with their landing commits:

| Script | Commit | Date (UTC) |
|---|---|---|
| `af_materials.py` | `380269548e17282356f6fbab07fb7e2efb8d1490` | 2026-08-10T15:37:51Z |
| `af_scene_setup.py` | `f2a167923d5f6b86156db7c7954c8e2e27105bd6` | 2026-08-10T15:38:37Z |
| `af_vehicle_rig.py` | `e7b8468b7dcf25efc2b01c17e6f46aeb1a4be84d` | 2026-08-10T15:40:03Z |
| `af_vehicle_generate.py` | `d8971634953c63aa7f45e4d3f6b5f3a2ec9dcedc` | 2026-08-10T15:41:37Z |
| `af_validate.py` | `69eed3b3b6e2de6ef184ad6d282e9bdff4e6ba18` | 2026-08-10T15:43:54Z |
| `af_export.py` | `604bb531134a8c98ebb7b58dfb972dd38efa2b1c` | 2026-08-10T15:46:26Z |
| `af_smoke_test.py` | `1b6e050c2b6834a1c8d4f695b9840fba620ec582` | 2026-08-10T15:47:25Z |
| `af_pipeline_config.py` | `5e6e230d23c1792119d0fd063f894499bdbed73e` | 2026-08-10T15:56:11Z |

One nuance is recorded rather than smoothed over: `af_pipeline_config.py` landed
at 15:56:11Z, **seven minutes after** §5.20 was committed at 15:49:33Z. At the
instant §5.20 was written, seven of the eight were on `main`. The eighth was
authored and about to land — it is the module every other script imports, and
§5.20's own commit message calls the set "the 0B scripts". The count of eight
was therefore a statement about the authored 0B set, not a miscount of the tree,
but it was written a few minutes ahead of the tree agreeing with it.

Four scripts landed afterwards, none of them in scope for §5.20:

| Script | Commit | Date (UTC) | Milestone |
|---|---|---|---|
| `af_circuit_generate.py` | `7617a530392d155039a4ea81e5ed032f0b0f3d3f` | 2026-08-11T14:44:07Z | M3 criterion 5 |
| `af_bodywork_profile.py` | `a09728e866068d2b0f7a9d93ab4759b854452ba0` | 2026-08-11T23:51:24Z | M4 slice 1 |
| `af_bodywork_selftest.py` | `456031ca1c8ee05f627e2067b7c0c92b2c4824a4` | 2026-08-12T00:20:32Z | M4 acceptance suite |
| `af_mesh_export.py` | `b5b935f8646368e5fd1a08b4df6d4b9fcaee6f82` | 2026-08-12T00:42:38Z | M4 slice 3 |

8 + 4 = 12, which is the live count in `BlenderPipeline/scripts/`.

`VERSION_MATRIX.md` has been touched twice since §5.20 was written:
`385517d5d3487374a5569e94832ec501e6327c94` (2026-08-11T13:58:15Z, upgrades
Blender assumptions to *automatically validated*, adds §5.33) and
`edfd74ba10ba67abb32350f3385f32c2ff061af1` (2026-08-11T22:22:57Z, rename only,
message states *"No claim, label, measurement or verification verdict is
altered"*). Neither revisited §5.20. Three of the four new scripts landed after
both.

**Cause:** stale scope, not a miscount. §5.20 is a true statement about a set
that stopped being the whole set on 2026-08-11T14:44:07Z.

**Disposition:** OPEN-063-A is **closed as to cause**. §5.20's count is
deliberately **not** refreshed in place, for two reasons: the sentence is a
scoped historical claim about what `py_compile` was run against under CPython
3.12, and silently changing eight to twelve would assert that the four newer
scripts were covered by that same measurement, which they were not. The correct
repair is a new subsection recording the current script set and what has
actually been executed against it. That is not done here and is carried as
**OPEN-065-B** below.

## D-065.5 — What this entry does not claim

- No script was executed. The 274 checks / 274 passed figure for
  `af_mesh_quality.py` is quoted from D-047's commit message as a historical
  record, not re-measured.
- No file was read in full to produce D-065.3; the argument rests on the two
  figures D-053.6 recorded and on sizes reported by the repository host.
- Nothing here moves Milestone 4. Milestone 4 remains **not accepted**, blocked
  solely on OPEN-051-F, the fifteen-criterion visual gate in
  `MILESTONE_4_VISUAL_ACCEPTANCE.md`. Seven G-1 criteria are numerically
  measurable from the exported OBJ with the standard library; eight G-2 criteria
  require Blender 5.2 LTS with the face-orientation overlay at three angles.
  Partial pass is failure.
- This is a markdown-only commit. Per D-054 it creates no CI batch obligation,
  and none is claimed.

## D-065.6 — Erratum against volume 8's own header

Volume 8's header still reads **open**. This volume supersedes it as the open
volume from this commit forward, per the map at the top of this file. The
one-line header correction in volume 8 is deferred rather than performed,
because editing it means retranscribing 15,893 B through a patchless write
interface to change one word — a corruption risk out of all proportion to the
gain (the same reasoning as `163f9b9b`, which deferred two ledger rows rather
than retranscribe 63 KB). Recorded as **OPEN-065-A** so that it is a tracked
debt and not an inconsistency someone discovers later.

---

## Open questions — authoritative table

| Id | Subject | State |
|---|---|---|
| OPEN-051-B | Drift guard banner says 27; counterparty unidentified. `VERSION_MATRIX.md` eliminated as source. | open |
| OPEN-051-F | Blender visual verification of exported bodywork (D-060 gate, `MILESTONE_4_VISUAL_ACCEPTANCE.md`). Blocked only on Umut's machine. | open |
| OPEN-053-A | Local rehearsal gate for `af_mesh_quality.py`. Not met, unachievable in the authoring environment under D-053.6. | open |
| OPEN-060-A | 936 historical faces vs 798 serialised faces. Never reconcile by adjusting either number. | open |
| OPEN-063-A | `VERSION_MATRIX.md` §5.20 says eight `af_*.py`; the tree holds twelve. | **closed by D-065.4** — stale scope; §5.20 predates four later scripts. Count deliberately not refreshed in place; repair tracked as OPEN-065-B |
| OPEN-064-A | Two file sizes disagree with D-046 and D-047/D-053.6. | **closed by D-065.2 and D-065.3** — row 1 is a documented +2 B rename, D-046 was correct; row 2 is a wrong byte figure in D-053.6, the file was never 13 KB |
| OPEN-065-A | Volume 8's header still reads "open" after volume 9 opened. Deferred, not overlooked. | open |
| OPEN-065-B | `VERSION_MATRIX.md` needs a new subsection recording the current twelve-script set and what has actually been executed against it. §5.20 is not to be edited in place. | open |

Closed and not to be reopened: OPEN-051-A, OPEN-051-C, OPEN-051-D, OPEN-051-E,
OPEN-052-A, OPEN-052-B, OPEN-052-C, OPEN-M4-01, OPEN-056-A, OPEN-056-B,
OPEN-061-A, OPEN-062-A, OPEN-063-A, OPEN-064-A.

## Next decision id

**D-066.**
