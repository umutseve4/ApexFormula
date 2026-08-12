# CI batch 9 marker - bodywork mesh export gate

This file exists for one reason: a pull request needs a commit, and the
two commits this batch is meant to exercise are already on `main`. It is
documentation only. **It is never merged.** The branch that carries it,
`ci-batch-9-mesh-export`, exists to make the check matrix run and to give
the resulting job identifiers a stable home in `CI_EVIDENCE_VOL5.md`.

## What this batch is evidence for

| Commit | File | Bytes | Blob |
|---|---|---|---|
| `b5b935f8646368e5fd1a08b4df6d4b9fcaee6f82` | `BlenderPipeline/scripts/af_mesh_export.py` | 23654 | `26d135e37997db20b41132fafc157f80b0f80576` |
| `b2b427396eb16efba56787a6202a63d332911bfc` | `.github/workflows/validate.yml` | 14140 | `1f84f7bc4fea238e7b7c2854a07ed33fd5942c98` |

Both commits touch gate-scoped extensions (`.py` and `.yml`), so under
decision D-054 both owe a batch. This is that batch.

## What a green result here does and does not mean

It **does** mean that `af_mesh_export.py` imports `af_bodywork_profile`
successfully on a machine that is not the author's, that its 21 cases and
227 assertions execute and pass under both Python 3.9 and Python 3.12, and
that every one of the twelve bodywork surfaces plus every collision proxy
survives a write-and-read-back cycle with bit exact vertices, bit exact
face indices and an identical signed volume.

It does **not** mean the mesh is correct. Nothing in this batch opens
Blender, writes a file, or looks at anything. A round trip proves the
serialiser is faithful to the generator; it says nothing about whether the
generator produces a shape that resembles a racing car. That question can
only be answered by a human being opening `AF_Bodywork_Combined.obj`, and
until that happens Milestone 4 remains **not started for acceptance
purposes**.

## Local measurements this batch is meant to reproduce

```
af_mesh_export: 21 cases, 227 assertions, 0 failures
export plan: 14 files, 798 serialised faces
```

Two consecutive `--dump` runs produced 26 byte identical files totalling
112123 bytes, so the writers are deterministic.

## Disposal

Closed unmerged once the ten check runs report `success`. The branch is
kept; the pull request is not merged.
