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
| D-063 | `VERSION_MATRIX.md` read; the orphaned obligation was already discharged | recorded |
| OPEN-062-A | `VERSION_MATRIX.md` deferred to a wave that was later cancelled | **closed in 063.1** |
| OPEN-063-A | `§5.20` still says *eight* `af_*.py` scripts | open |

Next free decision identifier: **D-064**.

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

> **Superseded by D-063.1.** The premise of this section — that the
> three occurrences still carry the old name — was never verified. It
> was false. See 063.1.

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

> **Resolved by D-063.2.** The second hypothesis was correct, and the
> conditional in the last sentence is the outcome that obtained.

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

## D-063 — `VERSION_MATRIX.md` read, and the obligation that turned out to be already discharged

**Decision.** Read `Documentation/VERSION_MATRIX.md` end to end — 40,439 B,
blob `8fb657e51e4eb1fba08aef43f976305c03461c28`, the largest document in
the repository and the only one no session had ever opened — and settle
every open question that names it, in one pass, from the text.

**Why this was chosen.** Three of the six open questions named this one
file: OPEN-062-A, OPEN-051-B and OPEN-052-C. Every one of them had been
deferred on the same reasoning — that touching a 40 KB document was
expensive. That reasoning conflated two different operations. **Reading
a file is cheap; rewriting it is expensive.** D-052.6 had already
established the inline read ceiling at ≥40,439 B, which is exactly this
file's size, so the read was known to be within reach before it was
attempted. The three deferrals had been paying the price of a rewrite
to avoid the cost of a read.

### 063.1 OPEN-062-A — closed as a no-op

**The three product-name occurrences already carry the new identity.**
All three sites named by D-050.3 were located and read:

| Site | Current text |
| --- | --- |
| H1 title | `# Uludağ Formula — Version Matrix` |
| §5.21 | *"no Uludağ Formula file outside `AFVehicleCompatibilityLayer.h/.cpp` names any engine vehicle type"* |
| §5.28 | *"`ApexFormulaCore` depends on no Uludağ Formula module"* |

Wave 1.5 discharged this obligation. It was never orphaned; it was
completed and not recorded against the deferral that created it.

The fifteen identifier occurrences are all still literal and all still
correct: `ApexFormulaVehicle.Build.cs`, `ApexFormula.uproject`,
`ApexFormulaVehicle`, `ApexFormulaRace`, `ApexFormulaCore`,
`DefaultApexFormula.ini`, `ApexFormulaEditor.Build.cs` and
`/Script/ApexFormulaCore.AFQualityProfile`. D-055 froze those names
permanently, which is precisely what makes them correct forever rather
than pending. **`VERSION_MATRIX.md` requires no rewrite.** OPEN-062-A is
closed.

**What this cost.** D-062.6 wrote four paragraphs describing a defect
that did not exist, on a premise it explicitly declined to verify. It
was labelled honestly — *"that must be read, not assumed"* — and the
label was correct, but the section still reads as a finding. It is
marked superseded above rather than deleted, under the D-050 rule.

### 063.2 The +12 B drift — explained, one hypothesis proven, one disproven

D-062.7 offered two arithmetically valid explanations and refused to
choose. The reading decides it.

`ApexFormula` is 11 bytes. `Uludağ Formula` is **15 bytes**, not 14 — `ğ`
is two bytes in UTF-8, per D-051. The display-form substitution is
therefore **+4 B**, and three of them are **+12 B exactly**.

The competing hypothesis — six identifier substitutions at +2 B — is
**disproven by direct reading**: every identifier occurrence in the file
still reads `ApexFormula*`. Not one was renamed, so that path
contributed zero bytes. 40,427 + 12 = **40,439 B**, the observed size,
with no residual.

This is the first time in this project that a D-052.3 byte prediction
has been used **backwards** — to identify which of two edits was made,
from the size difference alone, and then confirmed against the text. The
arithmetic was right; what D-062.7 lacked was not a better estimate but
the two-minute read that would have settled it.

### 063.3 OPEN-052-C — closed, no defect

§5.28 does report **2300 checks, 0 failures, 0 warnings, exit code 0**.
The open question existed because a stale count read as current is a
false claim. The document already forecloses that reading, in three
independent places:

1. §5.28 body: *"That number is a **Milestone 1 measurement** and is
   quoted here as history, not as a current figure. Milestone 2 added
   five source files, so the current count is certainly higher; it has
   deliberately **not** been re-guessed. The live figure is whatever the
   `af_static_validate` job prints in the most recent CI run — that job
   is the authority, not this sentence."*
2. §7 ledger: *"The validator reported 2300 checks … **on the Milestone
   1 tree** | automatically validated — a Milestone 1 measurement, not a
   current figure."*
3. §7 ledger, the following row: *"The current check count after
   Milestone 2 | **not claimed** — read the latest CI run; it has
   deliberately not been re-guessed."*

The figure is correctly scoped, correctly labelled, and explicitly
delegates authority to the CI job. There is nothing to fix and nothing
to refresh. **OPEN-052-C is closed.** The standing rule that produced it
— never silently refresh a deferred count — is what made the original
author write those three sentences, so the question closes by having
been answered before it was asked.

### 063.4 OPEN-051-B — not settled; the question is misdescribed

OPEN-051-B is recorded as *"Drift guard banner says 27, `VERSION_MATRIX.md`
says 31"*. The file was read end to end. **It contains no figure 31, and
it does not mention the track drift guard anywhere.**

The number 27 does appear in it, in §5.28 — *"37 declared automation
tests (**27** from Milestone 1, 10 added in
`AFVehicleBackendSetupTests.cpp`)"*. That is a count of Unreal
automation test declarations. The drift guard's 27 is a count of
self-test cases in a pure-Python tool under `Tools/` (D-045). **Two
unrelated counters that happen to share a value.** The most probable
origin of OPEN-051-B is that collision.

**The question is not closed, because absence is the weakest kind of
finding and this one was established by reading rather than by counting.**
Code search is unavailable here (D-062.8) and there is no other
mechanical instrument, so a stronger negative is not currently
obtainable. OPEN-051-B is **re-described**: the counterparty document is
unidentified, and `VERSION_MATRIX.md` is eliminated as a candidate. It
must not be closed on this evidence, and it must not be cited as a live
discrepancy against this file either.

### 063.5 A real staleness, found where nobody was looking — OPEN-063-A

§5.20 reads: *"The **eight** `af_*.py` scripts are syntactically valid
Python for the interpreter Blender 5.2 LTS embeds."*

That was a Milestone 0B measurement. The Blender pipeline has grown
since — Milestone 4 alone added `af_bodywork_profile.py`,
`af_bodywork_selftest.py` and `af_mesh_export.py`. The count of eight is
stale.

Under the standing rule it is **not** refreshed here. Recording a new
number would mean counting the directory in a hurry to patch a sentence,
which is the failure mode D-052.3 and OPEN-052-C both exist to prevent.
It is raised as **OPEN-063-A** and carries the same instruction as its
siblings: the count is obtained from a directory listing at the moment
the file is next legitimately rewritten, and never guessed.

Note the asymmetry worth keeping. The two questions that were *filed*
against this document (052-C, 062-A) both closed as no-ops. The one real
drift in it was in a line nobody had ever flagged. **Open questions
record where attention has been, not where defects are.**

### 063.6 One further imprecision, recorded and not corrected

§5.13 reads: *"the Milestone 4 vehicle does not exist yet, so the budget
question is not closed."*

The conclusion is still correct — no Milestone 4 geometry has been
imported, D-044 keeps the exported asset as the Milestone 0B box body
until a separate adoption step, and the face and bone budgets remain
unverified against a real import. The phrase *"does not exist yet"* is
now imprecise: the bodywork module exists, generates twelve parts and
has measured counts. Erratum only, per D-057. The file is left
byte-identical.

### 063.7 Method — the read ceiling, re-confirmed

D-052.6 fixed the inline read-and-write ceiling at **≥40,439 B** on the
basis of this file's size. This is the first time the ceiling has been
exercised by an actual read of that file, and it returned complete in a
single response. The ceiling is confirmed rather than merely asserted.

**Rule made explicit, because three deferrals were paid for by not
having it:** reading a large file and rewriting one are different
operations with different risks. A rewrite risks silent corruption of a
document no compiler checks (D-052.5) and is properly deferred. **A read
risks nothing.** No question may be deferred on the grounds of a file's
size alone when reading it would settle the question.

### 063.8 Byte-delta estimator — demoted, with a stated tolerance

Two consecutive predictions in this series missed in **opposite**
directions:

| Write | Predicted | Actual | Miss |
| --- | --- | --- | --- |
| `MILESTONE_4_IMPLEMENTATION_VOL2.md` rewrite | 17.5–18 KB | 20,471 B | ~14% **low** |
| `DECISION_LOG_VOL7.md` creation (D-062.9) | 14.5–16.5 KB | 12,296 B | ~15% **high** |

The second was biased upward *because* of the first, and overshot by
about as much as the first undershot. Correcting for one miss produced
the opposite miss.

**Finding: the estimator has roughly ±15% dispersion in both
directions.** This is a material weakening of what D-052.5 claims for
it. A detector with a ±15% band cannot see a paragraph going missing
from a 20 KB file — that is a 2–3% change, well inside the noise.

**Ruling.** The byte-delta prediction is retained but **demoted from a
size oracle to a gross-truncation alarm.** It fires only on a shortfall
greater than 25%, which is the region where a genuine transmission
failure lives. Misses inside ±15% are recorded and otherwise ignored;
they are not evidence of anything and must not be used to bias the next
estimate, because doing so is what produced the second miss. Fidelity of
a Markdown write remains **unproven by any automated means** — D-052.6's
warning that size proves length and not content stands unchanged.

**Prediction for this write: 19.5–21.5 KB**, with the ±15% envelope
running 17.5–23 KB. This very likely closes volume 7 by size on its
second revision; if so, D-064 opens volume 8.

**Status.** *verified by inspection* — every claim in 063.1 through
063.6 was read out of `VERSION_MATRIX.md` before it was written down,
and the file itself was left untouched. No code was executed, no
milestone status changed, and no verification label was upgraded. The
absence claim in 063.4 is explicitly the weakest statement in this
decision and is labelled as such.

---

## Open questions

| Id | Subject | State |
| --- | --- | --- |
| OPEN-051-B | Drift guard banner says 27; the counterparty document is **unidentified** — `VERSION_MATRIX.md` eliminated by D-063.4 | open, re-described |
| OPEN-051-F | Blender visual verification of the exported bodywork | open, gate defined by D-060, blocked only on execution |
| OPEN-053-A | Local rehearsal gate for `af_mesh_quality.py` | open, **not met** |
| OPEN-060-A | 936 historical faces vs 798 serialised | open, never reconcile by adjusting either number |
| OPEN-063-A | `VERSION_MATRIX.md` §5.20 still says *eight* `af_*.py` scripts | open, never silently refresh |

Closed and not to be reopened: OPEN-051-A, OPEN-051-C, **OPEN-051-D**
(settled in 062.4), OPEN-051-E, OPEN-052-A, OPEN-052-B, **OPEN-052-C**
(closed in 063.3), OPEN-M4-01, OPEN-056-A, OPEN-056-B, **OPEN-061-A**
(closed in 062.1), **OPEN-062-A** (closed in 063.1).

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
