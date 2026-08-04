<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 04:52 UTC | START ] -->

# UppercutCore — activated 2026-08-04

The C++ scaffold that was staged here moved to its real home when the toolchain
landed: **`sandbox/Source/UppercutCore/`**, active in `UppercutSandbox.uproject`
as a Runtime module. One copy, in the place it runs — a second copy here would
only drift.

The record of what it is and how it was proven: Phase H in
`docs/phase1a/determinism_probe_results.md` (analyzer-first, byte-identical
across processes and a full rebuild, identical bytes to the Python reference).
The contract it satisfies: `tools/engine/analyze_core_scaffold.py`. The
toolchain and its install lessons: the engine setup runbook, "C++ toolchain for
Phase H".

<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 04:52 UTC | END ] -->
