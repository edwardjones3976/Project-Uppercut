# Decision 0023 — Semantic canon identity and raw-file provenance

**Status:** accepted  
**Date:** 2026-08-06  
**Authority:** Director  
**Extends:** Decision 0022  
**Evidence:** `docs/plans/2026-08-06-the-canon-hash-cannot-see-the-difference.md`

## RULING

Every canon dependency recorded by an authoritative stream carries two distinct SHA-256 identities:

1. **Semantic hash** — the load-bearing evidence identity. It changes when authoritative data changes.
2. **Raw hash** — the exact-byte provenance identity. It changes whenever the source file changes, including comments, formatting, or contribution metadata.

A raw-file change alone does not move an authoritative golden pin. A semantic change does.

The integrated contract must be born with this dual-hash design. Historical active unit streams migrate once under this Decision; their earlier whole-file hashes remain preserved in phase records as historical evidence.

## WHY

The merge-authority synchronization changed only decision references inside documentation fields. No authoritative value and no fight event changed, yet Phase N, K, O, and Q pins failed because their headers hashed entire JSON files.

That mechanism could not distinguish a retune from corrected prose. Repeated false-positive pin movement would make re-blessing routine and eventually destroy the meaning of a pin.

The project needs both facts:

- what exact file was present;
- what authoritative values the simulation consumed.

One hash cannot honestly represent both.

## WHAT CHANGES

### Stream header

New and migrated stream schemas record explicit fields such as:

```text
H|canon_pose_semantic=<sha256>
H|canon_pose_raw=<sha256>
H|canon_hash_contract=uppercut-semantic-json-v1
```

The names must state which identity they carry. An unlabeled `canon_<name>` hash is prohibited in a new contract.

### Semantic canonicalization

The semantic representation is produced by a versioned canonicalizer with these rules:

- parse JSON with duplicate keys rejected;
- reject NaN, Infinity, and values outside the accepted schema vocabulary;
- remove only fields explicitly declared non-authoritative by the file's schema or by a versioned hash-role manifest;
- never exclude a field merely because its name is `$comment`, `note`, `notes`, `contribution`, or ends in `_note`;
- sort object keys deterministically;
- preserve array order;
- encode strings as UTF-8;
- serialize numbers through one declared deterministic representation;
- include the canonicalizer contract version and schema identity in the hashed payload.

Unknown fields are authoritative by default and must not disappear silently. Where schemas prohibit unknown fields, validation fails before hashing.

### Documentation classification

Existing documentation fields may be marked non-authoritative, including contribution records and explanatory notes, but the classification must be explicit and reviewable.

A field that influences loading, validation, selection, formulas, tuning, rules, state, or execution is authoritative even when its name sounds explanatory.

### Historical migration

The current active N, K, O, Q, and R evidence may move once to the semantic-hash header contract in one atomic implementation change.

Migration acceptance requires:

- all authoritative event rows remain byte-identical to the immediately preceding active pins;
- only the declared header/schema fields may change;
- the old and new hashes are both recorded in the phase evidence;
- any event-row divergence aborts migration and requires separate diagnosis.

This is an evidence-implementation migration, not a canon retune.

## WHAT DOES NOT CHANGE

- Byte identity remains the proof standard for a declared contract.
- Existing phase claims remain scoped unit evidence.
- The integrated bout still receives its own new contract and pin under Decision 0022.
- Raw files remain richly documented beside their values.
- A semantic pin may not be re-blessed without a numbered canon Decision or documented implementation correction.
- The first divergent authoritative event must still be reported when a semantic pin moves.

## IMPLEMENTATION ORDER

1. Define the hash-role schema annotation or versioned manifest.
2. Implement one Python semantic canonicalizer and shared test-vector format.
3. Implement the C++ counterpart used by the authoritative runtime and commandlets.
4. Add cross-language parity tests over the same fixtures.
5. Add mutation tests before migrating any pin.
6. Migrate historical active streams once, proving event rows unchanged.
7. Design the integrated stream using dual hashes from its first version.
8. Resume Decision 0021 runtime work: state-dependent Wind recovery, Reserve expenditure, and between-round recovery.

No integrated golden stream may be created before steps 1–5 pass.

## EVIDENCE REQUIRED TO CLOSE IMPLEMENTATION

The hashing implementation must prove:

1. changing only a declared documentation field changes the raw hash and not the semantic hash;
2. changing any authoritative scalar, object member, array item, or array order changes the semantic hash;
3. changing an authoritative value inside an object that also contains excluded documentation still changes the semantic hash;
4. adding an undeclared field cannot be silently excluded;
5. duplicate JSON keys are rejected;
6. Python and C++ produce identical semantic hashes for all fixtures;
7. canonicalizer-version changes move the semantic identity deliberately;
8. historical migration changes no authoritative event row.

Mutation coverage must include every exclusion rule. A blanket recursive name-stripper is not acceptable evidence code.

## SUPERSEDING CONDITION

This ruling may be superseded only if a later implementation proves a simpler identity mechanism can preserve exact provenance, ignore documentation-only edits for authoritative pins, detect every authoritative mutation, and remain byte-identical across Python and C++ without hidden classification rules.
