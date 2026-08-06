<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 22:25 UTC | START ] -->
# There is something to press Play on

Phases Q and R were proven a day apart, and both proofs lived somewhere nobody
could reach. The C++ sat inside commandlet `Main()` functions: monolithic,
file-scoped, and callable only by launching the editor headless with arguments.
A runtime subsystem could not call one line of it.

That is a worse position than it sounds. It is not that the arena was unbuilt —
it is that the only way to build one was to write the rules a second time.
Two implementations of one rule is the defect this repository spends most of its
discipline avoiding, and it would have arrived wearing the clothes of progress.

So the work was not "build an arena". It was: take the proven artifact apart
into pieces a runtime can hold, without changing the fight.

## The safety net was the proof, not the tests

Every extraction was followed by a rebuild and a re-run of the parity prover,
and the bar was byte-identity. Not similar. Not agreeing in the trailer.

Six hashes went into this and six came out unchanged, across four separate
extractions — the canon reader, the loop, the stream's shape, and the same for
Phase R. That is a stronger statement about a refactor than a test suite can
make: 796 passing tests say the code still does what the tests describe, while
an identical stream says the fight is the same fight, decision for decision,
across 5400 ticks.

## What is now true that was not

The subsystem, the commandlet and the live arena parse canon with one function,
run one loop, and write one stream format. `tools/engine/prove_live_arena.py`
builds a real `UWorld`, lets the real `UUppercutFightSubsystem` come up in it,
drives it through the same single-step control the Director's period key uses,
and compares the dump to the contract:

    LIVE PROVEN seed=4242  ticks=1200  sha256=213cd787fa01ad8e...
    LIVE PROVEN seed=777   ticks=900   sha256=ee958e820886d2d2...

That is the sentence worth having. Not "the arena runs code like the proven
code" — the arena runs the proven code, and there is a command that says so.

## Two things that went wrong, kept because they are instructive

**A build that depended on `git status`.** Adding two source files broke the
module with redefinition errors in a commandlet neither file touched. Each
phase's commandlet keeps its constants in an anonymous namespace, which is
correct per file and collides the moment two of them land in the same unity
blob — and which files share a blob depends on the adaptive build's working set,
which is `git status`. So the module compiled or failed depending on which files
happened to be uncommitted. Unity is now off for `UppercutCore`. A build whose
success depends on the state of the working tree is not something an evidence
pipeline should tolerate, and the seconds it costs are worth the failure mode it
removes.

**A test that was too broad to be true.** The first draft of
`test_only_one_place_reads_phase_q_canon` asserted that one file reads movement
canon. It failed immediately: six other phases' commandlets read it too, each
legitimately, each proven against its own contract. The claim that is true is
narrower — one reader *within Phase Q's chain* — and the wider observation
became its own test that counts the six rather than forbidding them. A test that
fails the moment it is written has done its job; the temptation is to widen the
exemption rather than narrow the claim.

That count is a real finding and it is on the record: the sprawl is harmless
while each phase is only ever run headless against its own contract, and stops
being harmless the moment a live runtime wants to run those phases too — which
is exactly what Phase O will want.

## What this does not claim

Phase Q is a fight about distance. The arena has no guard, no stamina, no
damage, no knockdown and no round structure, because those are Phases O, P and S
and **Phase O is held on gate G7**. Nothing in this work anticipates that
ruling, and the arena shows exactly what Phase Q's contract describes and no
more.

The stamina economy decision packet is still the one thing waiting on the
Director. Everything built here attaches to it when it lands.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 22:25 UTC | END ] -->
