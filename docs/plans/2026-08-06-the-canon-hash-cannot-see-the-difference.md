<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 00:05 UTC | START ]

# Decision packet — the canon hash cannot tell a retune from a typo

**Status:** open, awaiting a Director ruling
**Raised by:** implementation, while verifying the merge commit
**Bears on:** Decision 0022 (frozen unit pins), and every future pin move

## What happened

Nobody had run the gates against the merge itself. Both sides of a merge being
green does not make the merge green, so they were run against `fb4bdea`.

**Seven tests failed.** Four of them were frozen unit pins — Phase N, Phase K,
and the Phase O and Q golden streams — the exact pins Decision 0022 declares
immutable, broken in the same working cycle as the decision that froze them.

The cause is not a bad merge and not a canon change. Commit `fb4bdea`
renumbered Decisions 0018 → 0019 and 0019 → 0020 during the post-merge
reconciliation, and correctly updated the prose that cited them — `$comment`,
`note` and `notes` strings inside `data/pose_geometry.json` and both rulesets.

Not one authoritative value moved. The proof is mechanical rather than
editorial: strip every documentation key (`$comment`, `note`, `notes`,
`contribution`, `*_note`) from each changed file at both revisions and the
remainder is byte-identical.

| file | raw bytes | semantics |
|---|---|---|
| `data/pose_geometry.json` | differ | **identical** |
| `data/rulesets/professional.json` | differ | **identical** |
| `data/rulesets/arcade_three_knockdown.json` | differ | **identical** |

The Phase Q golden diff is the whole story in one line:

```diff
-H|canon_pose=6bdbda5e3e9b4193ab114bbf5b0cc5b1a05d83716cb148e221bbc0647d82e16a
+H|canon_pose=e99660be40ffcf3ce11c736fead07df997203c27829ad79ed54ef230ef8f0899
```

One header line. The other 1,318 lines — every decision, every step, every
punch, every whiff across 5,400 ticks — are unchanged. Decision 0022 requires a
change record to identify "the first divergent authoritative event, not only the
final hash". **There is no divergent authoritative event.**

## The defect

> A stream header hashes the whole canon **file**, so the evidence scheme cannot
> distinguish a retuned value from a corrected comment.

This is not a one-off. Every decision renumbering, every typo fix, every improved
explanation inside a canon file will break four or more frozen pins from now on.

The damage is not the wasted re-run. It is that **re-blessing becomes routine**.
The discipline that makes a pin worth anything is that a failing pin means
something happened; a scheme that cries drift over punctuation trains everyone to
regenerate first and read afterwards. That is how pin discipline dies, and it
would die by attrition rather than by anybody deciding to abandon it.

It also puts two of this project's rules in direct conflict. Canon files are
richly commented *on purpose* — the comments are where a deliberate call is
logged so a later edit cannot silently flip it. Under whole-file hashing, that
documentation practice is now a recurring evidence cost.

## What was done for now

The four pins were re-run and re-blessed in one commit, recorded as an
**implementation correction** rather than a canon ruling, with the mechanical
prose-only proof written into `tests/test_phase_evidence_pins.py` beside the
superseded hashes. Main is green again.

That is the honest short-term move. It does not fix the defect.

## The options

### A. Leave it. Re-bless pins whenever prose changes.
Cheapest today. Accepts that pin failures will routinely mean nothing, which is
the failure mode described above. Not recommended.

### B. Hash canon semantically. *(recommended)*
The stream header carries the hash of a **canonicalised, documentation-stripped**
form of each canon file: keys sorted, `$comment` / `note` / `notes` /
`contribution` / `*_note` excluded, separators fixed.

- a changed **value** moves the pin — correct, and still unmissable;
- a changed **comment** does not — correct;
- provenance survives, because the raw file hash is *also* recorded in the
  header as a non-load-bearing `H|canon_<name>_raw=` line.

Cost: every stream header changes once, deliberately, under this ruling — and
never again for prose. There is one hasher on each side to change, which is only
true because the loaders were unified last night; six weeks ago this would have
been six edits and a divergence risk.

Risk to name honestly: the canonicaliser becomes load-bearing evidence code, and
a bug in it would silently mask a real canon change. It needs its own mutation
tests — a value change inside a commented block must still move the hash.

### C. Move documentation out of canon files.
Keep `data/*.json` as pure values with a parallel `docs/canon/*.md`. Clean
hashing, and it destroys the thing that makes this canon good: the reason sitting
next to the number. Not recommended.

## Recommendation

**B.** It restores the property Decision 0022 actually wants — that a moved pin
means the fight moved — and it is a one-time cost paid at the moment the project
is about to create a brand-new integrated contract anyway, which is the cheapest
hour it will ever be.

If B is ruled, the sequencing matters: do it **before** the integrated marker
stream is designed, so the new contract is born with the right hashing and only
the historical pins move once.

## What this does not touch

Not proposed: any change to what the pins assert, to byte-identity as the
standard of proof, or to which phases are frozen. The question is narrow — what
exactly the header hashes — and everything else about the scheme stays.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 00:05 UTC | END ] -->
