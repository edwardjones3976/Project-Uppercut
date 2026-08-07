<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 06:10 UTC | START ] -->

# PR body — Decision 0023 implementation (Issue #17)

Branch `impl/0023-semantic-canon-hashing`, three commits, no other work mixed in.

Create at:
`https://github.com/edwardjones3976/Project-Uppercut/compare/main...impl/0023-semantic-canon-hashing`

Suggested title:

> Decision 0023: semantic canon identity, C++ parity, and the one permitted header migration

---

## What this closes

Issue #17, steps 1–6 of Decision 0023's implementation order. Step 7 (the
integrated stream) is deliberately **not** here — it remains prohibited until
this merges.

## The problem it fixes

A decision renumbering on 2026-08-06 edited comment strings inside three canon
files and broke four frozen pins. No value moved and no fight event changed. The
old header hashed whole files, so it could not tell a retuned value from a fixed
typo — and a scheme that cries drift over punctuation trains re-blessing as
routine, which is how pin discipline dies by attrition.

## What is now true

| | |
|---|---|
| Manifest | `data/hash_roles.json`, every pointer classified by hand |
| Canonicalizer | Python + C++, agreeing byte for byte |
| Parity | `prove_canon_parity` → **checked=15 failed=0** |
| Migration | **21,984 authoritative rows, none moved** |
| Gates | **882 passed**, validators OK, goldens clean, all phase proofs PROVEN |

## The Director's six additional requirements

1. **The manifest is canon.** It has its own semantic identity, bound into every
   payload. Tested by performing the attack: reclassify `authoring_margin` as
   documentation, and both the manifest identity and every hash under it move.
2. **Exclusions never inferred.** Explicit pointers only; the forbidden
   name-stripper lives in the test suite and a test asserts it fails.
3. **Negative zero is zero** semantically; raw still distinguishes the spelling.
4. **Ten decimal places, refused not rounded.**
5. **Array order authoritative** — insert, delete and reorder all move identity
   even where a wildcard classifies each element's note.
6. **Hash rules hash themselves** — canonicalizer version, hash-contract
   version, schema identity and manifest identity all bound ahead of the data.

## What cross-language parity caught on its first run

`FString::operator==` is **case-insensitive** in Unreal. The C++ rejected the
`key_sorting` vector as a duplicate key because it holds both `A` and `a`.

Three places were affected, and the third is the one that mattered: duplicate
detection, pointer matching, and the exclusion set. `TSet<FString>` hashes
case-insensitively too, so an exclusion pointer spelled `/guard/Note` would have
dropped the real `/guard/note` — removing from the evidence envelope a field
nobody had classified. That is requirement 2's trapdoor, reopened by a platform
default rather than by intent.

Python never had this bug and no amount of Python testing would have found it.

## The migration

Two commands with the code change between them — baselines captured **before**,
verified after. A tool that captured its baseline afterwards would compare the
new world against itself and always pass.

Every `_raw` value is identical to the whole-file hash it replaced.

## Guard tests that fired

Five failed on the new contract, correctly, and were rewritten rather than
adjusted. Two turned out to have been weaker than they looked:

- `test_a_shifted_canon_hash_is_caught` tampered with one field and broke on the
  first match — once that field was renamed it would have passed while checking
  nothing. It now corrupts both identities and asserts it found something to
  corrupt.
- `test_every_stream_says_which_rulebook_it_ran_under` read the first sixteen
  lines. A fixed slice stops checking the moment a header grows.

## Not claimed

No integrated stream exists. Wind and Reserve remain authored canon, unwired.
Remote CI has still not independently confirmed any of these numbers — Issue #14
owns that gap, and every figure above was produced locally.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 06:10 UTC | END ] -->
