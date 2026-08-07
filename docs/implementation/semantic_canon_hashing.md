<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 02:00 UTC | START ] -->

# Semantic canon hashing — the implementation

Decision 0023, contract `uppercut-semantic-json-v1`. This covers implementation
steps 1 and 2, and the Python half of step 5.

## Two identities, and why one was never enough

| | what it is | moves when |
|---|---|---|
| **raw** | SHA-256 of the file's exact bytes | anything changes, including a comment |
| **semantic** | SHA-256 of the canonical encoding, after removing explicitly declared non-authoritative fields | the fight can change |

On 2026-08-06 a decision renumbering edited comment strings inside three canon
files and broke four frozen pins. No value moved and no fight event changed. The
project needs both facts — what file was present, and what values were consumed —
and one hash cannot honestly carry both.

## Why the canonical form is not JSON

A C++ implementation has to produce the same bytes, and two JSON serialisers
agree on nothing that matters: float formatting, string escaping, `\uXXXX`
escapes, separators, integer-versus-float rendering. Every one of those is a
place the two runtimes could silently disagree about what canon says.

So the canonical form is a small typed byte stream with exactly one
representation per value, leaving the second implementation nothing to decide:

```text
null    'n'
false   'f'
true    't'
number  'd' u32be(len) ascii          always %.10f, integers included
string  's' u32be(len) utf-8 bytes    no escaping, ever
array   'a' u32be(count) items...     order preserved — order is canon
object  'o' u32be(count) (key value)  keys sorted by UTF-8 bytes
```

The payload is prefixed with the contract version and the schema identity, so
changing this encoding moves every semantic identity deliberately and visibly.

Three consequences worth stating:

- `3500` and `3500.0` hash identically. They are the same value, so this is
  correct, and it means a reformat is not a retune.
- Object key order does not matter; **array order does**. The five range bands
  are a sequence, not a set.
- A number needing more than ten decimal places is **refused, not rounded**.
  Silently truncating a canon value inside the evidence layer would be
  undetectable, which makes it the worst available bug in this file.

## The manifest, and the trapdoor it avoids

`data/hash_roles.json` is the only place a field may be declared
non-authoritative. The rule that makes it safe is the Director's amendment to
the original recommendation:

> Nothing is excluded because of what it is called.

Every pointer is explicit and was classified by hand against 0023's test — a
field that influences loading, validation, selection, formulas, tuning, rules,
state or execution is authoritative even when its name sounds explanatory. Four
guard rails hold the line:

- **unknown fields are authoritative.** Silence never means exclusion.
- **`*` matches one array index only.** No recursive wildcard, no key matching.
- **a pattern may not end in `*`.** Deleting an array element would renumber its
  neighbours, and order is canon.
- **a pattern that matches nothing is an error.** Dead patterns are how an
  exclusion list quietly widens onto fields nobody reviewed.

The clearest case in the repository is `cost_note` and `cost_model`, siblings in
the same move: the note explains, the model *selects* displacement pricing. One
is excluded and the other is not, which no name-based rule could express.

Deliberately left authoritative despite reading like prose: `reader_rule`,
`migration_rule`, `prohibitions`, and every `invariants/*` field. They are
declarative rules a validator may come to enforce. The cost is that improving
that wording moves the semantic hash. The alternative is deciding by vibe which
sentences are rules, which is the failure the manifest exists to prevent.

### The one honest gap

A field added at an already-declared wildcard position — a nineteenth move's
`note` — is covered automatically. The expansion snapshot in the test suite
turns that into a failing count rather than a silent disappearance, so it is not
invisible; but it *is* automatic, and it is the single place this design trades
strictness for practicality. Recorded here rather than discovered later.

## Evidence

`tests/test_semantic_canon_hashing.py`, 40 tests, one per numbered requirement
in 0023 plus the manifest's own guard rails. The tests are adversarial: each
tries to sneak a change past the semantic hash.

**The suite was checked against the implementation the ruling forbids.** "A
blanket recursive name-stripper is not acceptable evidence code" — so one was
written and swapped in, and six tests failed, including both tests that encode
the safeguard:

```text
FAILED test_4_a_new_field_that_merely_LOOKS_explanatory_is_authoritative
FAILED test_4b_undeclared_prose_at_a_new_path_is_authoritative
FAILED test_a_dead_pattern_is_an_error_not_a_no_op
FAILED test_a_wildcard_cannot_delete_a_whole_array_element
FAILED test_a_wildcard_does_not_match_object_keys
FAILED test_the_whole_document_cannot_be_declared_non_authoritative
```

That is the point of mutation coverage: not that the tests pass, but that they
fail against the wrong implementation.

The 2026-08-06 incident is also replayed directly against the file that caused
it — a rewritten `authoring_margin_note` in `pose_geometry.json` moves the raw
hash and leaves the semantic hash alone, while changing `authoring_margin`
itself still moves it.

## Cross-platform determinism, already observed

The vectors were generated twice on unrelated machines — a Linux container and
the Windows workstation, on different Python versions — and all seven semantic
hashes were byte-identical. That does not prove C++ parity, but it does prove
the encoding is not quietly leaning on one platform's float formatting, which is
the most likely way this design could have been wrong from the start.

## Cross-language vectors

`tests/fixtures/canon_hash_vectors.json` carries seven accept vectors and six
rejection vectors, regenerated by `python -m tools.uppercut_canon.vectors`. The
C++ canonicalizer must reproduce every `semantic_sha256` from the same
`input_json`, `patterns` and `schema_identity`, and must refuse every rejection
vector for the stated reason.

The vectors deliberately cover where two languages drift: key sorting with `$`
and `_` sitting either side of the letters in ASCII, non-ASCII strings, negative
zero, the tenth-decimal boundary, and nested arrays.

## Status against Decision 0023's implementation order

| step | state |
|---|---|
| 1. hash-role manifest | **done** — `data/hash_roles.json` |
| 2. Python canonicalizer + vector format | **done** — `tools/uppercut_canon/` |
| 3. C++ counterpart | **done** — `UppercutCanonHash.{h,cpp}` |
| 4. cross-language parity tests | **done** — `python -m tools.engine.prove_canon_parity` → PARITY PROVEN |
| 5. mutation tests before any pin moves | **done**, including the forbidden-implementation check |
| 6. migrate historical streams | next |
| 7. integrated stream with dual hashes | blocked on 6 |
| 8. resume Decision 0021 runtime work | canon authored; runtime pending |

**No pin has been migrated and no integrated stream exists.** Nothing so far
alters any current hash: the canonicalizer is not yet wired into a stream header.

## The C++ side

`UppercutCanonHash.cpp` carries its own strict JSON reader rather than using
`FJsonSerializer`. Unreal's JSON object silently keeps one of two duplicate
keys, and Decision 0023 requires duplicates to be *rejected* — an evidence layer
must not depend on a parser whose behaviour it cannot control on the one case it
is required to detect.

`python -m tools.engine.prove_canon_parity` drives the C++ over the shared
vectors: 15 checks, every accept vector reproducing both hashes and every
rejection vector refused, plus the real manifest's identity derived
independently on both sides and compared.

### What parity caught on its first run

> `FString::operator==` is **case-insensitive** in Unreal.

The C++ rejected the `key_sorting` vector as containing a duplicate key, because
that vector deliberately holds both `A` and `a`. Three places were affected:
duplicate detection, pointer matching, and the exclusion set — and `TSet<FString>`
hashes case-insensitively too, so an exclusion pointer spelled `/guard/Note`
would have dropped the real `/guard/note`, removing a field nobody classified
from the evidence envelope.

Python never had this bug, and no amount of Python testing would have found it.
It is the exact class of defect shared vectors exist to catch: not a
disagreement about the rules, but a disagreement about what the platform quietly
means by "the same string". The regression is pinned in
`test_keys_differing_only_in_case_are_different_fields`.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 02:00 UTC | END ] -->
