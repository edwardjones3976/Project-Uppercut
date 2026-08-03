<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 09:05 UTC | START ] -->

# Logging and Replay — ROADMAP Phase 1A step 10

Canon: `data/replay_model.json` · Schema: `schemas/replay_model.schema.json` ·
Validator: `tools/uppercut_validate/replay.py` · Tests: `tests/test_replay.py`

**Rule 18.** Definitions only. No fight has been logged, and no replay has been played back.

## Two contracts, deliberately not merged

`schemas/fight_event.schema.json` has defined what an event *looks like* since Phase 0 — sequence,
tick, clock, visibility, type, actor, target, payload, and the `explains` array. What was never
defined is what the log **guarantees**. That is this step, and it holds two separate promises:

**Resimulation.** The same seed, the same authoritative initial state and the same authored data
reproduce a byte-identical authoritative event log.

**Replay.** A *saved* log reproduces the recorded presentation, without re-running any uncertain
decision.

Collapsing those two is the standard way a replay system quietly starts re-deciding fights: it
re-runs the CPU policy, gets a marginally different answer on a different build, and the "replay"
diverges from what the spectator actually watched. So `reruns_cpu_decisions`, `reruns_judging` and
`reruns_rng` are all schema constants pinned to `false`, and the validator says why in the failure
text — a replay that re-decides is not showing what happened, it is holding a second fight.

The one thing a replay may choose freely is the camera, and only because `camera_model.json` already
declares that the camera writes no simulation state and is excluded from the determinism hash.

## The exclusion list is not a convenience

Camera, presentation, audio, commentary and crowd rendering are excluded from the determinism hash.
That exclusion is safe only because every one of those systems is forbidden from writing simulation
state — the moment something authoritative gets excluded, the hash stops meaning anything and the
determinism evidence quietly becomes decorative.

So the validator holds an allowlist of non-authoritative systems and rejects any exclusion outside
it. Adding `collision` to that list fails the build, which is exactly the point.

## Causality points backward

The gate asks that the replay and event log "explain major combat and judging events." Explained
here has a precise meaning: the event names the earlier sequence numbers it causally follows, so a
reader can walk backwards from a stoppage to the exchange that produced it.

Six types must carry that explanation — punch outcomes, knockdowns, stoppages, referee deductions,
and both judge cards. The validator specifically requires knockdown and stoppage, because a stoppage
nobody can trace back is the precise failure the gate item guards against. And `explains` references
must point at *earlier* sequence numbers: nothing is caused by its own future.

## Rule 3 survives the replay

The score firewall does not weaken when the fight is over. Both judge card events are declared
sealed, with `archival_reveal` as their only reveal point, and the validator cross-checks that list
against `score_isolation_contract.json` — a sealed event with no visibility rule here, or one
declared observable, fails.

There is also a check on the replay side: `sealed_events_visible_during` may name only the archival
reveal. Adding `immediate_result` would be a tempting, small, entirely wrong change, and it fails
with the reason attached.

## Where this leaves Phase 1A

Steps 1 through 10 are now defined and validated. Steps 11 and 12 — the Crowd Bar and the
Special / Full-Crowd Trait / Ultimate architecture — remain provisioned slots only.

Definitions being complete is not the gate. The gate wants complete CPU-vs-CPU matches running from
selection through post-fight flow, and the distance between a validated definition and a running
match is still the largest item on the board. What has changed is that every layer a match needs is
now specified, cross-locked to its neighbours, and enforced by something that fails loudly.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 09:05 UTC | END ] -->
