# Milestone 4 — Implementation Record

This file records Milestone 4 work in the same evidence-first style as
`MILESTONE_3_IMPLEMENTATION.md`. Every claim below carries an explicit
verification label. Nothing is described as compiled, executed, imported
or visually confirmed unless it actually was.

Verification labels used throughout this repository:

| Label | Meaning |
| --- | --- |
| `statically inspected` | A human or a script read the text. No execution. |
| `automatically validated` | A script executed and returned a pass or fail. |
| `verified by inspection` | Cross-checked against another artefact by reading both. |
| `requires local compilation` | Needs a C++ toolchain that CI does not run. |
| `requires Unreal Editor verification` | Needs the editor open. |
| `requires playtesting` | Needs a human to drive. |
| `not claimed` | Deliberately unproven. Do not infer it. |

---

## 1. D-046 — pin the pipeline configuration hash and enforce it in CI

**Status: merged.** Pull request #15, squash merge
`5faa2d981948db85c290ba122d0f20a8bea31949`.

### 1.1 The problem, stated precisely

`BlenderPipeline/scripts/af_pipeline_config.py` section 11 already
contained a genuine implementation:

```python
def effective_config():
    ...  # the JSON-serialisable subset of module state that affects output

def config_hash():
    blob = json.dumps(effective_config(), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()
```

and `describe()` already emitted the first sixteen characters of that
digest. So the hash was never fictional. The gap was narrower and, in
practice, more dangerous than a missing feature:

1. The sixteen-character value quoted in prose had never been checked
   against what the module actually computes.
2. Nothing in continuous integration failed when the two diverged.

Under D-041 the `DESIGN` dictionary is the single source of truth for
every generated dimension. One edited float there changes the digest and
silently falsifies every document that quotes it. Documentation rots
quietly; a guard does not.

### 1.2 The documented value was confirmed before any guard was written

Order matters here. Had the guard been written first and the pin taken
from the documentation, a wrong pin would have been frozen into CI and
CI would then have defended the error.

Instead an independent reconstruction was written
(`hashcheck.py`, local only, not committed) that re-declares every
constant `effective_config()` reads and recomputes the digest from
scratch. It was **executed**.

| Quantity | Value |
| --- | --- |
| Canonical JSON blob length | 3,484 bytes |
| SHA-256, full | `c9ef9f7e985a1aaf460d58db6e269d3e5b607f268df12acf3500a8492869f4fc` |
| First sixteen characters | `c9ef9f7e985a1aaf` |
| Agreement with the documented literal | exact |
| Process exit code | 0 |

*automatically validated.*

A single mistranscribed digit anywhere in the reconstruction would have
produced a completely unrelated digest. Exact agreement is therefore
strong evidence that the reconstruction faithfully mirrors the module.

**D-046 is a lock, not a fix.** No behaviour changed. What changed is
that the value can no longer drift in silence.

### 1.3 Decision: a standalone guard, not an edit to the config module

`af_pipeline_config.py` is 30,910 bytes and every edit in this repository
is a full-file rewrite with no patch interface. Rewriting it to add an
assertion would put 30 KB of transcription at risk to gain one check.

Precedent D-037 and D-045 already established the alternative: a new,
self-contained file under `Tools/` that imports nothing from the other
guards. `Tools/af_config_hash_guard.py`, 26,517 bytes, standard library
only. It loads the config module by file path through
`importlib.util.spec_from_file_location`, which is safe because
`af_pipeline_config.py` deliberately never imports `bpy`.

The guard targets Python 3.9 as well as 3.12: no f-strings, no walrus,
explicit `object` bases, `%`-formatting throughout.

### 1.4 What the guard checks

| Check | Question it answers | Failure prefix |
| --- | --- | --- |
| A | Does the module's computed digest still equal the pinned constant? | `A:` |
| B | Is every hash-shaped token quoted near a configuration-hash anchor in tracked Markdown and workflow files a prefix of the computed digest? | `B:` |
| C | Does `describe()` still report the first sixteen characters of the computed digest? | `C:` |

Details that matter:

- The pin lives in `EXPECTED_CONFIG_HASH` as the full sixty-four
  characters, not a prefix. Check A rejects malformed, uppercase or
  truncated values on either side rather than comparing loosely.
- Check B scans root-level `*.md` plus `Documentation/`, `Tools/` and
  `.github/` for `.md`, `.yml` and `.yaml`. It anchors on
  `config[ _\-]?hash`, case-insensitive, then accepts any
  `[0-9a-f]{16,64}` token beginning within eighty characters of that
  anchor and requires it to be a prefix of the computed digest.
- **`.py` files are not scanned.** That is deliberate: it is what stops
  the guard's own pinned constant from flagging itself.
- **Zero claims is not a failure.** `BLENDER_PIPELINE_DESIGN.md` quotes
  no hash at all, and that has to stay legal.
- Findings name the file, quote the offending value and give its byte
  offset.
- Exit codes: `0` clean, `1` findings, `2` cannot run.
- Command line: `--root PATH`, `--verbose`, `--self-test`,
  `--print-hash`, `--help`. An unknown argument exits 2.

### 1.5 Evidence

| Run | Result | Exit | Label |
| --- | --- | --- | --- |
| `--self-test --verbose` | 44 cases across 27 methods, 0 failed | 0 | *automatically validated* |
| `--root <synthetic tree> --verbose` | 3 files scanned, 3 claims verified, no findings | 0 | *automatically validated* |
| Mutation: `wheelbase_m` 3.600 → 3.601 | 1 `A:` drift plus 3 `B:` stale claims | 1 | *automatically validated* |
| CI, `Static validation (no engine, no DCC)` on pull request #15 | success against the real config module | — | *automatically validated, job level* |

The mutation is the load-bearing test. A guard that only ever passes
proves nothing. Changing one float in the vehicle design by one
millimetre produced a completely different digest and the guard reported
both the drift itself and every document left quoting the old value.

The continuous integration run is what upgrades the whole claim from
"a local transcription agrees" to "the guard ran against the real
`af_pipeline_config.py` on a clean checkout and passed".

### 1.6 Continuous integration wiring

Two steps were added to the `static-validation` job of
`.github/workflows/validate.yml`, in the established self-test-first
shape used by the two earlier guards:

```
Configuration hash guard self-test   ->  af_config_hash_guard.py --self-test
Configuration hash guard             ->  af_config_hash_guard.py --root . --verbose
```

The workflow itself quotes **no** hash value. There is nothing there to
go stale.

File sizes: `validate.yml` 8,958 → 10,393 bytes.
`Tools/af_config_hash_guard.py` is new at 26,517 bytes.

### 1.7 Post-merge integrity

| File | Size | Branch blob | Blob on `main` after merge |
| --- | --- | --- | --- |
| the new guard under `Tools/` | 26,517 B | `54230d1d994802114833ce95e01fabb3927c5592` | identical |
| `.github/workflows/validate.yml` | 10,393 B | `5a1d0ce44498a54c5fc7aac7ac6619e8d4e9f8e3` | identical |

*verified by inspection* — the directory listing on `main` was re-read
after the squash merge and both object identifiers matched the branch
blobs exactly.

### 1.8 A defect introduced during this work, and how it was caught

The first push of the rewritten `validate.yml` on this branch
(intermediate blob `01b6235275ec9466513416663a527eec12dc5b9a`, 10,446
bytes) accidentally prefixed the **pre-existing** track drift guard step
with `--self-test &&`, even though the commit message asserted that
nothing outside the two new steps had been touched.

Two things about this are worth recording permanently:

1. **Continuous integration would not have caught it.** Running a
   self-test twice still exits 0. The job would have gone green over a
   silently corrupted step.
2. It was found only by re-reading the `main` copy of the file and
   diffing it against the pushed blob.

It was corrected in commit `722f6164265f49aec7046f6714918432411ea012`,
which restored the step byte-for-byte to
`python3 Tools/af_track_drift_guard.py --root . --verbose`, and the
commit message states the error plainly rather than hiding it. The
history was not rewritten.

**Standing rule adopted from this.** Because every edit here is a
full-file rewrite, always diff a rewritten file against its `main`
counterpart before opening the pull request. Green CI is not evidence
that untouched regions survived.

### 1.9 What D-046 does not prove

*not claimed*, each one deliberately:

1. The guard is text and import only. No Blender ran, no mesh was built,
   no FBX was written or imported, no C++ was compiled.
2. It cannot detect drift where the module and every document change
   together and consistently. It detects divergence, not wrongness.
3. Only one mutation was executed as a real directory tree. The
   `B:`-only and `C:` failure paths are covered by synthetic self-test
   cases, not by a mutated repository.
4. The `py3.9` continuous integration leg comes from
   `static-validation.yml`, which does **not** invoke this guard. The
   guard was written to 3.9 rules by hand; that has not been executed on
   3.9.
5. Continuous integration evidence is read at job level. "The step ran
   and exited 0" is an inference from a green job with no
   `continue-on-error`, not a transcript reading.

---

## 2. Documentation debt carried into Milestone 4

Still outstanding, disclosed rather than silently skipped:

| Item | Reason deferred |
| --- | --- |
| D-045 ledger rows in `MILESTONE_PLAN.md` and `VERSION_MATRIX.md` | Two table rows would require retranscribing roughly 63 KB with no patch interface. The transcription risk exceeds the benefit. |
| D-046 rows in the same two ledgers | Same reason. This file is the authoritative D-046 record until those files are rewritten for another purpose. |
| `DECISION_LOG.md` entry for D-046 | The file is 50,726 bytes. A full rewrite to append one entry was judged not worth the risk. |

Next free decision identifier: **D-047**.
