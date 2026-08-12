# CI batch 8 marker

Purpose: force a full check-run matrix over the tip of `main` after the
bodywork geometry module landed complete.

Commits under test:

| Commit | File | Blob | Bytes |
|---|---|---|---|
| `456031ca1c8ee05f627e2067b7c0c92b2c4824a4` | `BlenderPipeline/scripts/af_bodywork_selftest.py` | `71bce5fb9df1bcff19e01c09f69c4c906f341364` | 22,078 |
| `f95301c3871d1a4ef971ff3e2a7049ff406f41cf` | `BlenderPipeline/scripts/af_bodywork_profile.py` | `aa990fd150d51ed0b647ddd99fd6d5e2244a774d` | 42,219 |

Locally measured before the push, with a hand written stand in for
`af_pipeline_config`:

```
af_bodywork_profile core: 22 cases, 72 assertions, 0 failures
thickness peak: 0.545590827299
af_bodywork_selftest: 42 cases, 376 assertions, 0 failures
```

Why this batch is not a formality: the local run never touched the real
`BlenderPipeline/scripts/af_pipeline_config.py`. The `validate.yml` step
`Bodywork geometry core self-test` executes `af_bodywork_profile.py
--self-test`, which imports the real config and hard imports the acceptance
suite. This is therefore the first honest execution gate for slice 2. A
failure here is a real finding about a divergent config value, not a flake,
and it must be investigated rather than retried.

Required outcome: 10 of 10 check runs `success`, each started after this
marker commit. This pull request is opened as a draft and closed unmerged;
it exists only to trigger the matrix.
