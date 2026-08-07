# Decision 0024 — Semantic-hash dependency scope

**Status:** accepted  
**Date:** 2026-08-06  
**Authority:** Director  
**Extends:** Decision 0023  

## RULING

Decision 0023 remains correct that documentation classification is load-bearing evidence. Its first implementation bound the semantic identity of the **entire** hash-role manifest into every canon file. That is fail-safe but too broad.

The final contract must use **precise dependency scope**:

1. **Global hash-policy identity** — covers contract-wide rules that genuinely affect every canon file, including canonicalizer version, hash-contract version, manifest schema/version, wildcard semantics, unknown-field policy, numeric rules, pointer rules, and other global classification behavior.
2. **Per-file role-set identity** — covers only the target file's explicit non-authoritative pointers and binds the global hash-policy identity.
3. **File semantic identity** — hashes the target file's authoritative canonical payload while binding the global hash-policy identity and that file's role-set identity.
4. **Raw manifest hash** — remains exact provenance for the complete manifest file.

A classification change for `data/pose_geometry.json` must move the role-set and semantic identity for `pose_geometry`, but must not move unrelated movement, condition, or ruleset semantic identities merely because their classifications share the same manifest file.

A change to a genuinely global hashing rule must move every affected semantic identity.

## WHY

The first self-binding prototype proved the safety property but also exposed excessive fan-out: adding or changing one documentation classification moved every semantic hash under the manifest, even for phases that never read the affected canon file.

That recreates part of the attrition risk Decision 0023 exists to eliminate. Evidence identities should change when **their authoritative dependencies** change, not when an unrelated file's documentation classification changes elsewhere in the same registry.

The project therefore keeps the stronger rule — classification is evidence — while narrowing the dependency graph to the smallest honest scope.

## REQUIRED PROOFS

Before Decision 0023 implementation may merge, tests must prove:

- changing one file's excluded pointer moves that file's role-set identity;
- the same change moves that file's semantic identity;
- the same change does **not** move an unrelated file's semantic identity;
- changing a global hash-policy rule moves all semantic identities governed by it;
- changing the exact manifest bytes while preserving both global policy and the relevant file role-set changes only the raw manifest provenance hash;
- removing or renaming a file classification entry cannot silently fall back when that file was previously classified;
- unknown canon files remain fully authoritative by default;
- Python and C++ compute identical global-policy, per-file role-set, canonical-byte, and semantic hashes.

## POINTER REPRESENTATION

The implementation must also preserve RFC 6901 segment identity without aliasing. Internal concrete paths must be represented as segment vectors/tuples or another unambiguous structure. Human-visible pointers may be serialized to RFC 6901 only with `~` and `/` escaped correctly.

A literal key `a/b` and nested path `a -> b` must remain distinguishable in both classification and mutation tests.

## WHAT DOES NOT CHANGE

- No name-based documentation stripping.
- Unknown fields remain authoritative by default.
- Array order remains authoritative.
- Raw-file hashes remain exact provenance.
- Existing unit phase event rows may not move during migration.
- No integrated golden bout stream before Python/C++ parity and mutation coverage pass.

## IMPLEMENTATION ORDER

1. Fix internal RFC 6901 path identity.
2. Split manifest identity into global-policy and per-file role-set identities.
3. Update Python vectors and mutation tests.
4. Implement the same model in C++.
5. Prove cross-language canonical-byte and hash parity.
6. Migrate historical headers exactly once with zero authoritative event-row drift.

This Decision is an implementation refinement of Decision 0023, not a reopening of the semantic-versus-raw hashing decision.
