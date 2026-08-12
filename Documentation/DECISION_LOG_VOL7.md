# Decision Log — Volume 7

This volume continues `DECISION_LOG_VOL6.md`, which closed at 19,640
bytes under the rule adopted in volume 2: open a new volume once the
current one passes roughly 20 KB.

## Volume history

This table is authoritative. Under D-061.2, a `§0` table inside a closed
volume that disagrees with this one is superseded on sight and must not
be edited.

| Volume | File | Decisions | Size | State |
| --- | --- | --- | --- | --- |
| 1 | `DECISION_LOG.md` | D-001 .. D-044 | 50,726 B | frozen |
| 2 | `DECISION_LOG_VOL2.md` | D-045 .. D-050 | 20,441 B | frozen, now read |
| 3 | `DECISION_LOG_VOL3.md` | D-051 .. D-052 | 25,950 B | frozen |
| 4 | `DECISION_LOG_VOL4.md` | D-053 .. D-055 | 27,898 B | frozen |
| 5 | `DECISION_LOG_VOL5.md` | D-056 .. D-058 | 20,132 B | frozen |
| 6 | `DECISION_LOG_VOL6.md` | D-059 .. D-061 | 19,640 B | closed |
| 7 | this file | D-062 onward | open | open |

Volumes 1, 3 and 4 exceed the threshold because the rule was adopted
later and applies forward, not retroactively.

## Index

| Identifier | Title | Status |
| --- | --- | --- |
| D-062 | Volume 2 read; D-049 and D-050 registered; the orphaned matrix obligation | recorded |
| OPEN-062-A | `VERSION_MATRIX.md` deferred to a wave that was later cancelled | open |

Next free decision identifier: **D-063**.

---

## D-062 — volume 2 read, and what it changed

**Decision.** Read `DECISION_LOG_VOL2.md` end to end, register D-049 and
D-050 in the open volume so they are usable without re-opening a frozen
file, and act on what the reading exposed rather than filing it.

**Why this was owed.** D-061.3 refused to summarise D-049 and D-050
because the only source was a frozen volume nobody had opened.
Reconstruction from context is forbidden by D-053.6 — *evidence about a
file must be produced by that file, byte for byte.* OPEN-061-A recorded
the gap. This decision closes it by reading, not by inferring.

### 062.1 OPEN-061-A — closed

`Documentation/DECISION_LOG_VOL2.md`, 20,441 B, blob
`8ac4dfbc7079c7376704f5c546b75e897cc605ac`, fetched in full. The two
missing decisions are summarised below from that text.

### 062.2 D-049 — documentation wave scope, triage rule, evidence procedure

Wave 1 of D-048 treated as a bounded unit: rename product prose across
the documentation set, change nothing any guard reads, prove it with a
purpose-built pull request. Thirteen commits — one ini display string,
ten files under `Documentation/`, the root `README.md`, and the two
nested `README.md` files under `Unreal/` and `BlenderPipeline/`. The
commit table lives in section 3 of `CI_EVIDENCE_VOL2.md` and is
deliberately not duplicated, *because two copies of a table are two
chances to disagree.*

Three provisions still binding:

1. **Triage-before-rewrite.** A candidate file is fetched and scanned
   for actual product prose *before* replacement text is composed. It
   earned its keep immediately: `MILESTONE_3_CIRCUIT.md` was read, found
   to contain no product prose, and deliberately left untouched. A file
   is skipped only after it has been read, **and the skip is recorded** —
   otherwise the absence of a commit is indistinguishable from an
   oversight.
2. **Evidence procedure.** Check runs are readable only through a pull
   request, and a pull request's check runs belong to its *head commit*.
   Order, and no other: push to `main`; cut the verification branch
   **after the final write**; add one marker commit; open the pull
   request, read the check runs, close it unmerged. Step 2's ordering is
   load-bearing — a branch cut too early certifies a tree missing the
   last write.
3. **Acceptance.** Ten of ten `success` with every start time later than
   the last commit under test. A green batch that started earlier is
   evidence about a different tree and is rejected as stale.

D-049 also states plainly what it does not do: it upgrades no milestone
status, no verification label and no measured value.

### 062.3 D-050 — doc-tail verdicts, and D-049 correcting itself

D-049's deferral paragraph classified two large files as still carrying
the old product name **from a size estimate and an occurrence count, not
from a reading** — breaking the triage rule D-049 had adopted four
paragraphs earlier. D-050 corrects it and leaves the wrong sentence
standing in place, *because the point of a ledger is to show what was
believed and when.*

- **`MILESTONE_3_IMPLEMENTATION.md` (37,137 B) — no rewrite, ever.**
  Every occurrence of the old identity is `Unreal/Source/ApexFormulaRace/`,
  a **source path**, not a product name. It is literally correct today.
  A second, independent reason not to touch it: section 7 contains
  `config_hash = c9ef9f7e985a1aaf`, a sixteen-character token in exactly
  the shape `af_config_hash_guard.py` check B scans for within its
  eighty-character claim window. It passes only because the value is
  right. Any retranscription carries a live CI failure mode unrelated to
  its content — one mistyped hex character turns the build red. This is
  the origin of the permanent skip cited by D-051.8.
- **`VERSION_MATRIX.md` (40,427 B at the time) — deferred to wave 2.**
  It does contain genuine product prose: **three** product-name
  occurrences (the H1 title; a clause in §5.21; a clause in §5.28) and
  roughly **fifteen** module, file, ini and script identifiers across
  §5.21, §5.26 and §5.28 which must stay literal until the artefacts are
  renamed. A `VERSION_MATRIX_VOL2.md` was considered and **rejected** —
  a side file cannot correct the H1 title of volume 1; it would leave a
  wrong name atop a 40 KB document and add a second document explaining
  why. D-050 closes with the same discipline as D-049: closing wave 1
  upgrades no milestone. *Nothing has been compiled, no editor opened, no
  mesh imported or looked at, and no lap driven.*

### 062.4 OPEN-051-D — settled, erratum only

The volume 2 header reads *"It starts at **D-047**"* while its index and
body carry **D-045** and **D-046**, both marked *registered
retrospectively*.

**Verdict: the header is a statement of intent, the index is the fact.**
Volume 2 was opened because appending D-047 to a 50,726 B volume 1 was
refused three times; D-045 and D-046 were then back-filled into the new
volume rather than into the frozen one. Both readings are honest; only
the index is load-bearing.

**Volume 2 is frozen. It is not edited.** Under D-057, the correction is
published here and the file is left byte-identical. The authoritative
range for volume 2 is **D-045 .. D-050**, as stated in the table above.

### 062.5 Independent corroboration of D-061

D-061 corrected the volume-history table on four of five closed rows,
using volume 3's header and volume 4's §0 as sources. Volume 2 had not
been read at that point. It has now, and its index lists exactly D-045
through D-050 — the range D-061 assigned it. The correction is confirmed
by a source that was not consulted when it was made.

Volume 2's header is also the origin of the 20 KB rule itself: *"open a
new volume once the current one passes roughly 20 KB"*, adopted with the
reasoning that **the cost of recording a decision must never scale with
the number of decisions already recorded.**

### 062.6 The orphaned obligation — OPEN-062-A

D-050.3 made `VERSION_MATRIX.md` a **wave 2 deliverable**, on the
explicit arithmetic that deferring buys one 40 KB retranscription
instead of two.

**D-055.8 then cancelled wave 2 and declared the rename effort
complete.** The module identifiers are frozen permanently, which retires
fifteen of the eighteen occurrences by making them correct forever. The
**three product-name occurrences have no remaining owner.** The vehicle
that was going to carry them no longer exists.

This is not a new defect. It is a pre-existing one that became visible
only when the two decisions were held side by side, which required
reading a volume nobody had opened. It is raised as **OPEN-062-A** and
deliberately **not** fixed in this pass, because the fix is a 40 KB
retranscription of a document this session has never read, and D-050.2
has already demonstrated that this particular corpus punishes rewrites
of large files that were classified without reading.

### 062.7 A size drift, recorded and not explained

D-049 and D-050 both give `VERSION_MATRIX.md` as **40,427 B**. The
current directory listing gives **40,439 B** — a drift of **+12 bytes**.

The wave 1.5 byte arithmetic pinned in D-052.3 makes +12 reachable two
ways: six identifier substitutions at +2 B, or three display-form
substitutions at +4 B. **Both are consistent, so neither is proven.**
Choosing between them without reading the file would be exactly the
reconstruction D-053.6 forbids, and exactly the error D-050.1 corrected.
The drift is therefore recorded as an unexplained observation and folded
into OPEN-062-A. If wave 1.5 already fixed the three product-name
occurrences, OPEN-062-A closes as a no-op — but that must be read, not
assumed.

### 062.8 Method note — code search is not available on this repository

An attempt was made to settle §062.7 cheaply by searching the repository
index for occurrences instead of downloading a 40 KB body. The query for
the old identity returned `total_count: 0` with `incomplete_results:
true`.

**That zero was not treated as evidence.** A control query for the
current identity — a token that unquestionably appears in this
repository many times — returned `total_count: 0` and
`incomplete_results: true` as well. The index does not cover this
repository.

**Rule adopted:** a search-shaped tool must be proven with a control
query that is known to match before any of its zero results are cited.
An unvalidated search returning nothing is indistinguishable from a
search that is not running at all. Code search is struck off the list of
usable instruments here; the D-055.6 metadata-listing technique remains
the only cheap non-downloading measurement available.

### 062.9 Byte-delta prediction

D-052.5 records that Markdown has no compile gate, so a predicted size
compared against what the write API returns is the only automated
truncation detector available. The previous prediction in this series
missed **14% low**, so this estimate is biased upward per that finding.

**Predicted: 14.5–16.5 KB.** The measured size is recorded in the commit
response and compared on sight; a large shortfall means truncation and
the write is repeated, not patched.

**Status.** *verified by inspection* — volume 2 was read in full before
any of the summaries above were written, which is the rule D-050
restored. No code was executed, no milestone status changed, and no
verification label was upgraded by this decision.

---

## Open questions

| Id | Subject | State |
| --- | --- | --- |
| OPEN-051-B | Drift guard banner says 27, `VERSION_MATRIX.md` says 31 | open, deferred by D-059 |
| OPEN-051-F | Blender visual verification of the exported bodywork | open, gate defined by D-060, blocked only on execution |
| OPEN-052-C | `VERSION_MATRIX.md` §5.28 "2300 checks" | open, never silently refresh |
| OPEN-053-A | Local rehearsal gate for `af_mesh_quality.py` | open, **not met** |
| OPEN-060-A | 936 historical faces vs 798 serialised | open, never reconcile by adjusting either number |
| OPEN-062-A | Three product-name occurrences in `VERSION_MATRIX.md` orphaned by the cancellation of wave 2; unexplained +12 B drift | open |

Closed and not to be reopened: OPEN-051-A, OPEN-051-C, **OPEN-051-D**
(settled in 062.4), OPEN-051-E, OPEN-052-A, OPEN-052-B, OPEN-M4-01,
OPEN-056-A, OPEN-056-B, **OPEN-061-A** (closed in 062.1).

## Verification labels

| Label | Meaning |
| --- | --- |
| `statically inspected` | A human or a script read the text. No execution. |
| `automatically validated` | A script executed and returned a pass or fail. |
| `verified by inspection` | Cross-checked against another artefact by reading both. |
| `requires local compilation` | Needs a C++ toolchain that CI does not run. |
| `requires Blender execution` | Needs Blender installed and running. |
| `requires Unreal Editor verification` | Needs the editor open. |
| `requires playtesting` | Needs a human to drive. |
| `not claimed` | Deliberately unproven. Do not infer it. |
