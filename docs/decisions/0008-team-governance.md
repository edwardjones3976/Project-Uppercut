<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-02 20:42 UTC | START ] -->

# Decision 0008 — Team Governance

**Date:** 2026-08-02
**Status:** Accepted under explicit Director delegation
**Supersedes:** the open item left by Decision 0006; answers D-8 in the gate review packet.

## Context

Decision 0005 rejected an imported agent-ownership split (Claude as primary builder, Codex as
presentation-only) on the grounds that it came from another project rather than from this one's actual
work. Decision 0006 deliberately declined to adopt any model on inference. Earlier discussion
contemplated a fuller structure: the Director as final authority, a coordinating strategist for
arbitration, and Codex-led and Claude-led teams working in parallel.

## Decision

**Adopt the minimal model now; leave the fuller one available as an amendment.**

1. **The Director is the final authority** on scope, canon, gate closure and reversal of any delegated
   ruling.
2. **Assignment is explicit and per task.** Each unit of work names its owner when it starts, recorded in
   the issue tracker against its workstream label. No standing agent-to-workstream mapping is created.
3. **No contributor owns a file by default.** Ownership is per task and expires with it, which is what
   makes the tagging convention (Decision 0006) load-bearing: authorship is read from tags and git
   history rather than from a static map.
4. **Concurrent work on the same file requires an explicit handoff** — the outgoing contributor states
   what changed and what is left, in the commit or in a handoff note, before another picks it up.

## Why minimal rather than the fuller model

The parallel-teams structure solves coordination problems this project does not have yet: there is one
repository, no engine code, and no concurrent workstreams in flight. Adopting a standing org chart now
would encode assumptions about a workload that has not materialised, which is the same mistake
Decision 0005 identified in the imported split. The minimal model costs nothing to run and cannot
collide with itself.

## Amendment path

When two or more workstreams genuinely run in parallel — realistically once Phase 1A combat work and
Phase 1B character-data preparation overlap — the fuller model becomes worth its overhead. Adopting it
then requires only a successor decision naming the teams, their workstreams and the arbitration route.
Nothing in this decision blocks that.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-02 20:42 UTC | END ] -->
