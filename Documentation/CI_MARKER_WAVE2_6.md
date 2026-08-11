# CI Marker - Verification Batch 6

Purpose: force a fresh workflow run so that the Wave 2A revert commits are
covered by recorded evidence. This file is disposable. The branch that
carries it is never merged.

## Commits under verification

| # | Commit | Change |
|---|---|---|
| 1 | 243c5a45 | Wave 2A step A: added Unreal/Source/UludagFormulaEditor/ (5 files) |
| 2 | 74925c88 | Revert 1/5: removed UludagFormulaEditor.Build.cs |
| 3 | 6ad9e2a0 | Revert 2/5: removed Public/UludagFormulaEditor.h |
| 4 | ee7b9c04 | Revert 3/5: removed Private/UludagFormulaEditor.cpp |
| 5 | 60bebc47 | Revert 4/5: removed Public/AFDataValidator.h |
| 6 | 63039649 | Revert 5/5: removed Private/AFDataValidator.cpp |

Net effect on the tree: none. Commit 1 created a directory and commits
2 to 6 removed it again. The purpose of this batch is to prove that the
round trip left no residue and that the static guard still passes.

## What this batch proves

1. Unreal/Source contains exactly six module directories, all named
   ApexFormula*, plus the two target files.
2. Tools/af_static_validate.py was never modified during the round trip.
   Its MODULES list, its dependency tables and its target assertions are
   byte identical to their state before commit 1.
3. Unreal/ApexFormula.uproject was never modified. Its Modules array
   still names the six ApexFormula* modules.
4. Unreal/Source/ApexFormulaEditor.Target.cs was never modified.
5. The header hygiene walk over Unreal/Source no longer sees the extra
   five files, so the copyright and pragma once counts return to their
   pre commit 1 values.

## What this batch does not prove

Nothing in this repository has been compiled. No Unreal project has been
opened. No mesh has been imported or inspected. Green CI here is a
structural gate over text files, not an execution gate over a build.

## Decision recorded

D-055 freezes the UBT module names ApexFormula* as an internal code name,
extending the reasoning already applied to the AF_ symbol prefix in D-048.
The player visible identity, delivered and verified in Wave 1, is the
rename that matters: README files, Documentation prose, the product name
in Unreal/Config/DefaultGame.ini, and the repository name itself.

Measured cost of continuing the module rename instead of freezing it:
61 further file recreations, 122 write calls, and five separate full
retranscriptions of a 52702 byte guard script, none of which could be
compile verified in the authoring environment.

## Acceptance rule for this batch

Ten check runs, all with conclusion success, and every started_at value
later than the author date of this marker commit. Any run still reported
as in_progress invalidates the reading and the poll is repeated.
