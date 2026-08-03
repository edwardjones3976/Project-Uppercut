# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 09:30 UTC | START ]
"""Python reference simulator for Project Uppercut (WS5 / T5.1).

**Authority note, stated first because it matters most.** Unreal is the
authoritative simulation (Decision 0002). This package is a *reference model*:
it executes the canonical JSON in `data/` so balance evidence, exploit hunts and
the ROADMAP's required automated checks have something to run against before the
engine can host them. Where this and the engine ever disagree, the engine is
right and this is a bug - and the disagreement is itself a finding worth having.

Decision 0002 assigns Python to tools, analysis, simulation analysis and
telemetry, which is exactly this.

What it is not: a second combat system. It reads the same files the engine reads
and holds no tuning values of its own.
"""
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 09:30 UTC | END ]
