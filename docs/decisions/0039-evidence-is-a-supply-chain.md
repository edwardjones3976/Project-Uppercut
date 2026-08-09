<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 22:18 UTC | Decision 0039 start ] -->
# Decision 0039 — Evidence is a supply chain, and the chain is now guarded

**Status:** ACCEPTED (delegated).
**Authority:** the owner's standing in-session delegation, 2026-08-09.
**Executes:** the external audit's recommendations 5 and 6 (CI hardening,
evidence-integrity findings, Windows verification lane), via a three-section
ownership pass whose reports are in
`docs/reviews/2026-08-09-audit-response-section-ownership.md`.

## The principle

This repository's trust model is "the same inputs produce the same bytes."
Every finding fixed here was a place where that model had a silent third
party: a mutable action tag is someone else's code running with our token; an
unpinned dependency major is someone else's future release deciding what canon
validates; a validator more permissive than the evidence layer is two opinions
about what a file says; a hash from a second filesystem read is provenance for
bytes nobody ran.

## CI and supply chain (audit medium finding)

1. **Actions pinned to commit SHAs**, resolved live from the upstream
   repositories and verified twice (independently by Section 2):
   `actions/checkout@11bd719…` (v4.2.2), `actions/setup-python@a26af69…`
   (v5.6.0). `persist-credentials: false` everywhere; workflow-level
   `permissions: contents: read`.
2. **Dependencies bounded**: `jsonschema>=4.26,<5`, `referencing>=0.37,<1`,
   `pytest>=8,<9`.
3. **Two new exact CI gates**: `gen_decision_index --check` (stale, duplicate,
   or non-contiguous decision numbers fail CI — the machine that would have
   caught both of Decision 0038's collisions) beside the existing
   `gen_status --check`.

## The Windows lane (audit recommendation 6, issue #14)

A `windows-authority` job now runs the full suite and validators on
windows-latest — path separators and case sensitivity finally meet CI — plus
`tools/engine/check_core_compiles`, a source-integrity gate over the 46-file
C++ module: strict UTF-8, every quoted include resolves, brace balance (the
file-sync truncation tripwire), commandlets actually subclass UCommandlet,
UHT generated.h placement, Build.cs invariants.

**What the lane does not claim (Rule 18):** no GitHub runner has UE 5.8, so
nothing in CI compiles the module or proves engine behavior. The step is named
`C++ core source integrity (not a compile - no UE on runner)` because its
first draft was named "still compiles as C++", and that was a claim no runner
verifies. The engine proofs remain operator-run per `docs/SEE_AND_TEST.md`.
When a self-hosted runner with UE exists, it takes this job's place.

**Known and accepted:** CI triggers remain `push: main` + `pull_request`, so a
wip branch gets CI by opening a draft PR — the repository's existing practice.
CI pins Python 3.11 while the dev box runs 3.14.5; the suite is verified on
3.14.5 today and 3.11 is verified by the first PR run. Both recorded rather
than silently assumed.

## Evidence integrity (the audit's five low findings)

- **F1 — validators were more permissive than the evidence layer.** All 24
  validator modules now parse through `tools/uppercut_validate/strict_json.py`,
  which IS the evidence layer's parser: duplicate keys refused, NaN/Infinity
  refused, at every depth. All 99 committed JSON files verified strict-clean
  first, so nothing green broke. A uniformity test fails any future validator
  module that binds a permissive `json`.
- **F2 — hashes from a second read.** `canon_header_lines` now accepts the
  canon text already in memory — the bytes the simulation ran on — and the
  Phase Q/R analyzers pass exactly those bytes; with no text supplied it reads
  once, coherently, instead of twice per file. Hash values unchanged by
  construction (same bytes, same algorithm): **golden streams for frozen
  phases O, Q and R re-verified byte-identical after the change.**
- **F3 — score-isolation path escape.** Contract paths are data, and data
  can no longer point the scanner outside the tree it polices: a path
  resolving outside the root now raises instead of scanning elsewhere or
  silently skipping.
- **F4 — empty range-band canon → negative C++ index.** The Python validator
  already refused the file (verified, held by a regression test). The C++
  loader guard is written and **deferred to the next build window** —
  UNVERIFIED-COMPILE code does not land here (Rule 18), and the editor
  currently holds the DLL.
- **F5 — H|ERROR artifact behind a success exit.** Located and confirmed:
  the range commandlet and `DumpStream` both write the refusal artifact and
  report success, and a comment in the commandlet asserts the opposite of
  what the code does. Caller-side guards are written and **deferred with F4
  to the same build window**, after which `prove_core_range` /
  `prove_core_evade` re-verify parity. Until then this stands recorded as
  the highest-priority open evidence defect (P1).

Regressions for F1–F4's Python halves: `tests/test_evidence_integrity.py`
(ten tests, each docstring naming its finding).

## What did not move

No canon value. No pinned hash. No frozen marker stream — golden re-proof is
part of this decision's evidence. No tuning: Decision 0032 Ruling 4 stands,
and the audit's recommendation 7 remains refused per Decision 0038.
<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 22:18 UTC | Decision 0039 end ] -->
