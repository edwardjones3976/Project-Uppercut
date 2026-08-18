<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-18 06:48 UTC | START ] -->
# Snapshot: the `C:\Users\edwar\Uppercut` Unreal home, as of 2026-08-12

**This is preservation, not integration.** Nothing here is merged, proven,
compiled or blessed. It exists so that work which lived in no commit, no branch
and no remote cannot be lost while the Director decides what to do with it.

## Why this branch exists

On 2026-08-17 a review of the folders attached to this project found a second
Unreal home at `C:\Users\edwar\Uppercut`, created 2026-08-12 and described by its
own README as a "clean Unreal home collected from `project-uppercut`". It is a
git repository with **zero commits, no remote, no stash, and 19 untracked
entries**. Its `Source/` and `Content/ProjectUppercut/` are real directories, not
junctions back to this repo — only `data/ docs/ fixtures/ schemas/ tests/ tools/`
and `Content/{BoxingAttacks,FabImports}` are junctions.

Nine of its source files existed **nowhere in git**. That was checked against
live `origin/main` and against every remote branch, not against a mirror and not
against the local checkout (which was 18 commits behind at the time).

## What is preserved here

`home/` is a verbatim copy of the parts of that home which are not build output
and not junctions: `Source/`, `Config/`, `Uppercut.uproject`, the four root
`.ps1` scripts, and its `README.md`. The copy was verified **byte-identical on
disk** before staging — `diff -r` reported no differences across `Source` and
`Config`, and each root file compared equal with `cmp`.

One qualification, stated because this is a preservation record and the
distinction is real: the committed blobs are **not** byte-identical to the
originals. This repository's `.gitattributes` sets `* text=auto eol=lf`, so the
home's CRLF line endings were normalised to LF on commit. That policy exists
deliberately — it is what stops Windows runners converting JSON to CRLF and
drifting `canon_hash_roles_raw` from committed goldens, producing a false
"fight changed" signal — and it was not worth defeating here. **Content is
preserved in full; line endings are not.** If an exact-byte original is ever
needed, it is the working copy at `C:\Users\edwar\Uppercut`, not this snapshot.

Deliberately excluded: `Binaries/ DerivedDataCache/ Intermediate/ Saved/ .vs/`
(build output), the six junction directories (they point back into this repo),
and `Content/`. `Content/ProjectUppercut/Maps/L_UppercutDevArena.umap` was
compared against `sandbox/Content/ProjectUppercut/Maps/L_UppercutDevArena.umap`
and is **identical**, so nothing is lost by omitting it; `BoxingAttacks` and
`FabImports` are gitignored vendor junctions.

One rename: the home's `.gitignore` is stored as `home/.gitignore.snapshot`.
A nested live `.gitignore` would apply real ignore rules to this subtree, which
would defeat the point of a verbatim snapshot. Its content is unchanged.

## The divergence this records

Against `origin/main` at `af4cafc`, the home's `Source/UppercutCore` (66 files)
versus `sandbox/Source/UppercutCore` (57 files):

**Nine files present only in the home — in no commit and on no branch.** All
carry `[ Auto (Cursor Agent) | 2026-08-12 ]` tags, authored 07:15–07:55 UTC:

| File | What it declares itself to be |
|---|---|
| `Private/UppercutGuardCore.cpp`, `Public/UppercutGuardCore.h` | "Phase L guard rules, extracted for the integrated session (Decision 0012)" — `CoveredLanes`, `Intercepts`, commitment-scaled extents |
| `Private/UppercutGuardCanonLoader.cpp` | the canon reader paired with the above |
| `Private/UppercutConditionCore.cpp`, `Public/UppercutConditionCore.h` | regional condition, knockdown-relevant regions, count relief |
| `Private/UppercutPunchEconomyCore.cpp`, `Public/UppercutPunchEconomyCore.h` | per-arm work, outcome-class recovery multipliers |
| `Private/UppercutDevHUDWidget.cpp`, `Public/UppercutDevHUDWidget.h` | `UUserWidget` base for `WBP_UppercutDevHUD` (PRO-8), presentation mirroring `GetView()` |

`UppercutGuardCore` + `UppercutGuardCanonLoader` is the rules-seam and
canon-reader pair the convergence rule asks for, which is part of why losing it
would have mattered.

**Fourteen files shared with `main` differ, and the home is the STALE side of
them:**

```
Private/UppercutArenaPresentation.cpp   Public/UppercutArenaPresentation.h
Private/UppercutFightSession.cpp        Public/UppercutFightSession.h
Private/UppercutFightSubsystem.cpp      Public/UppercutFightSubsystem.h
Private/UppercutFighterBase.cpp         Public/UppercutFighterBase.h
Private/UppercutMatchDirector.cpp       Public/UppercutMatchDirector.h
Private/UppercutRoundCore.cpp           Public/UppercutRoundCore.h
Private/UppercutThinPolicy.cpp          UppercutCore.Build.cs
```

Direction is not ambiguous: every file in the home is dated 2026-08-12, and the
arena work merged into `main` afterwards (PRs #50–#55 — reactions and facing,
ringside camera and lights, look-at IK, telemetry vitals) is absent from it.
`UppercutFighterBase.cpp` carries **33** look-at references on `main` and **0**
here.

So the two trees are ahead of each other in opposite directions: the home holds
rules `main` never received, `main` holds presentation the home never received.
That is the two-implementations-of-one-rule condition, already real.

`UppercutCore.Build.cs` differs by one line — the home adds `UMG`, `Slate`,
`SlateCore`, which `UppercutDevHUDWidget` needs.

## A defect in the home's own README, recorded not fixed

`home/README.md` instructs the reader to set `$env:UPPERCUT_HOME` and run
`python -m tools.engine.prove_integrated_arena`. `UPPERCUT_HOME` has **zero**
references anywhere in this repository. `tools/engine/prove_integrated_arena.py`
derives `REPO` from `__file__` and hardcodes
`REPO/sandbox/UppercutSandbox.uproject` — a path which does not exist under
`C:\Users\edwar\Uppercut`, as that home has no `sandbox/` directory at all.

This is a **code read, not an executed run**. It is recorded here rather than
repaired because repairing it is a change to the tooling, not preservation.

## What was NOT done, stated plainly

- **Not compiled.** No UBT build was run against this tree, here or anywhere.
- **Not proven.** No parity proof, no golden compare, no marker stream was
  produced or checked. This snapshot makes no evidentiary claim whatsoever.
- **Not merged, and not mergeable as-is.** It sits at an additive path precisely
  so that merging it could never revert `main`'s arena work. Do not resolve the
  divergence by copying `home/Source` over `sandbox/Source`; that would silently
  undo PRs #50–#55.
- **Not a Director call.** Reconciling these trees changes what the integrated
  contract asserts, which is Ed's decision, not an agent's.

## Suggested next step, for whoever picks this up

The question worth answering first is whether the nine files still describe the
guard, condition and punch-economy model that canon holds today, or whether the
six days of decisions since 2026-08-12 have moved past them. That is a reading
task against `data/*.json` and `docs/decisions/`, and it should happen before any
attempt to port them onto current `main`.
<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-18 06:48 UTC | END ] -->
