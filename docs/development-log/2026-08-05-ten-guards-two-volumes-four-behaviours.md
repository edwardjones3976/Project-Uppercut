<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 15:40 UTC | START ] -->

# Ten guards, two volumes, four behaviours — the pinned drift, as arithmetic

**2026-08-05.** The execution plan has carried *"10 guards vs. 2 guard volumes
need reconciling"* as known drift for days, with a standing instruction to
surface it in any doc-review pass. Several doc-review passes went by today
without it being surfaced. That is my miss. It is surfaced here as arithmetic
rather than as another note saying it needs reconciling.

It is three problems wearing one label, and one of them is a defect nobody has
seen.

## 1. Ten postures, two numbers

`guard_evasion_model.postures` authors ten guards.
`collision_model.guard_interception` knows three punch paths — `blockable_high`,
`blockable_low`, `blockable_either` — mapped onto two coverage volumes,
`guard_high` and `guard_body`. So each of the ten guards is a point in a 2-D
space, and the entire structural difference between a philly shell and an ear
muff is two numbers.

| posture | high | body | head lane | body lane | in core |
|---|---|---|---|---|---|
| high_guard | 0.95 | 0.55 | closed | OPEN | yes |
| peek_a_boo | 0.90 | 0.75 | closed | closed | — |
| philly_shell | 0.70 | 0.60 | closed | closed | — |
| cross_arm | 0.95 | 0.70 | closed | closed | — |
| long_guard | 0.80 | 0.45 | closed | OPEN | — |
| low_lead | 0.45 | 0.50 | OPEN | OPEN | — |
| tight_elbow | 0.55 | 0.95 | OPEN | closed | yes |
| ear_muff | 1.00 | 0.40 | closed | OPEN | — |
| forearm_frame | 0.70 | 0.50 | closed | OPEN | — |
| active_hands | 0.60 | 0.50 | closed | OPEN | — |

## 2. Four behaviours, not ten

Coverage is tested against a hard threshold: a lane is closed when the extent
reaches 0.60 and open when it does not. Two lanes, two states each — **the most a
two-volume model can express is four behaviours**, and all ten guards land in
them:

- **head only** — five of ten: high_guard, long_guard, ear_muff, forearm_frame, active_hands
- **both** — three: peek_a_boo, philly_shell, cross_arm
- **body only** — one: tight_elbow
- **neither** — one: low_lead

Half the catalogue is one behaviour. The ear muff and the forearm frame differ by
0.30 of head coverage and 0.10 of body, and at contact they do the same thing.

The nuance is not entirely gone — condition erosion, the committed multiplier and
the Director's per-hand rule all scale extents continuously, so *when* a lane
opens still differs. But at full health, against a fresh threshold, ten guards
are four.

## 3. Eight of the ten are inert

The core loads `high_guard` and `tight_elbow`. The other eight are authored,
validated, documented and unreachable — the declared-but-inert class this
repository keeps a checker for, sitting in the subsystem the project's core
design rule is written about.

## 4. And two guards sit exactly on the threshold

This one is a defect rather than a tension, and it is invisible in the extent
table:

    philly_shell   body lane = 0.60 = the threshold exactly
    active_hands   head lane = 0.60 = the threshold exactly

A lane at exactly the threshold is closed while the fighter is perfectly fresh
and open the instant *any* arm damage lands — a break multiplier of 1.000, the
earliest possible value. Expressed as the erosion horizon, the head lane's break
point across the whole catalogue runs from 0.600 (ear_muff, the last to open) to
1.000 (active_hands, which opens immediately). Nobody chooses that on purpose.

## What it means against the design rule

The project's core rule says a guard is a body structure that (a) protects some
lanes while exposing others, (b) changes what offence is available from inside
it, and (c) costs resources to hold.

(a) is expressible today, in two numbers and four outcomes. (c) is expressible,
as `stamina_per_tick`. **(b) is authored per posture — `offense_cheap` and
`offense_expensive`, on every one of the ten — and is read by nothing.** That is
a fourth inert mechanism in the same file, and it is the clause that would make a
philly shell different from an ear muff even if their coverage numbers agreed.

## For the Director

This is not a tuning question and I have not proposed a number. Three things are
decidable and one is a straightforward fix:

**The threshold coincidence is a fix, not a decision** — two lanes authored at
exactly the interception threshold almost certainly want to be either side of it,
and which side is a one-line call per guard.

**Does a third volume exist?** Decision 0013 already deferred lateral geometry
(left/right rather than only high/low) and sequenced it after the CPU policy. A
third axis would take four behaviours to eight. That is the reconciliation the
execution plan's drift note is asking for, and it is a phase rather than an edit.

**Or does `offense_cheap` become the differentiator?** If what a guard *permits*
carries the identity, two coverage volumes may be enough and the ten stop
colliding without new geometry. This is the cheaper answer and it reads more like
boxing: a philly shell and an ear muff differ mostly in what you can throw from
them.

Measured by `tools/engine/measure_guard_expressiveness.py`; figures in
`sandbox/Saved/guard_expressiveness.json`.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 15:40 UTC | END ] -->
