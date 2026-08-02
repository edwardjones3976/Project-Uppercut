<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-02 19:34 UTC | START ] -->

# Phase 0 Gate Item — Generic Technical Sandbox Acceptance Criteria (ADOPTED)

> **Status: adopted** in [Decision 0007](../decisions/0007-phase0-gate-rulings.md) (D-2), 2026-08-02, under Director delegation. Individual criteria may be struck or added without disturbing the rest.


Approved **separately** from the character vertical-slice criteria. That separation is the whole point
of prototype separation: it keeps shared-system faults distinguishable from character-specific faults.
The sandbox uses generic test fixtures only. Named roster characters are out of scope here.

## A. Combat foundation

1. Combat states, movement and facing, camera behaviour and animation states exist and are inspectable.
2. Hitboxes, hurtboxes and guard regions produce authoritative collision; a visible miss is never
   classified as a clean hit.
3. Basic punches exist with every attack defining startup, active contact, recovery, range, stamina
   cost, guard interaction, hit reaction, counter vulnerability and positional consequence.
4. Guard and evasion exist, with commitment consequence strictly increasing blocked → dodged → whiffed.
5. Contact resolves into all seven classes: clean, solid, grazed, brushed, blocked, dodged, whiffed.
6. Condition is tracked per region — head, jaw/chin, each eye, upper and lower torso, each arm and
   guard, stamina, balance, guard integrity, Composure, Chin, Durability, Recovery. No single health bar.
7. Knockdowns, the authoritative count clock, rises, recovery and early stoppages resolve, with no flat
   per-punch knockout roll and Chin +100 conferring maximum resistance rather than immunity.
8. The Elastic Footwork model is continuous and threat-responsive: longer navigation at safe distance,
   compressed boxing steps inside threatening range, planted pivots, visible weight transfer, and no
   ice skating, magnetic range correction, invisible lunges, or uncontrolled body overlap.
9. Stance switching works for every fixture, with authored penalties outside the stated stance.

## B. CPU behaviour

10. Two CPU fighters complete full bouts using observable information only — no official scores, no
    opponent input reading, no privileged state.
11. Every decision emits a decision-reason record with cited observable evidence, a belief and an
    explicit confidence.
12. Fixtures show distinct tendencies, tactical plans, pattern recognition and adaptation.
13. All six stress profiles run: Rusher, Drainer, Technician, Counterpuncher, Showman, Power Threat.

## C. Officiating, judging and clock

14. Judge subsystem produces cards behind the firewall; `scan_source` and `check_event_log` pass
    against the real tree.
15. Referee provisioning: assignment, pre-fight disclosure, enforcement hooks, universal knockdown-count
    and medical minimums, and no power to alter damage, stamina, collision classification, Crowd gain,
    attributes, input responsiveness or judging criteria.
16. One authoritative synchronised clock; Accelerated Clock ON shows 3:00 across 1:45 real; OFF permits
    only 1, 2 or 3 minutes; 30 real-second breaks that menus do not pause.

## D. Crowd and abilities

17. Crowd Bar rewards clean offense, defense, evasions, counters, reversals, combinations, variety,
    Ringcraft, appropriate Showmanship, high-risk success and momentum change — and refuses to reward
    low-risk farming.
18. At a full bar the fighter chooses Ultimate **or** Full-Crowd Trait; one completed bar never
    activates both. Architecture for two Specials per fighter exists.

## E. Evidence

19. Deterministic resimulation: same seed plus same authoritative initial state reproduces a
    byte-identical authoritative event log.
20. Replay reproduces recorded presentation from a saved log without rerunning uncertain decisions.
21. Event logs explain major combat and judging exchanges via causal `explains` links.
22. Batch simulation and telemetry tooling produce matchup reports across seed sweeps.
23. Every required automated check runs: score-access denial, accelerated-clock sync, repetition-vs-spam,
    attribute fixtures, knockdown/stoppage/result states, determinism and seeded replay, large-batch
    invalid-state and deadlock, First Bell Firestorm, Long Drain, style viability and dominant loop,
    Crowd farming prohibition.

## F. Readability and balance

24. A spectator can watch a bout and understand why decisive exchanges happened.
25. No known infinite stun, clinch, running, meter or safe-animation exploit.
26. Effective aggression can win without volume-only dominance; patient stamina control can win without
    empty avoidance. Technician, Counterpuncher, Showman and Power Threat all retain legitimate routes
    to victory. Dominant extremes and nonviable styles are gate failures.
27. Balance reports identify dominant loops, ineffective traits, inexplicable dominance and absent
    counterplay. **No universal win-rate band is used as pass/fail** (Decision 0005).

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-02 19:34 UTC | END ] -->
