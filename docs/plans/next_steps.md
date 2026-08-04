<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 15:10 UTC | START ] -->

# Next steps, measured against the Phase 1A gate

Written after a QA pass on the audit, Phase F and Phase G. Everything below is checked
against the repository rather than recalled, and the three findings that reorder the
priorities are stated first because they change what "nearly done" means.

## Three findings that move the order

### 1. Attributes are canon, validated, and the bout has never read one

`data/attribute_budget.json` and `data/attribute_families.json` are authored, schema-
locked, fixture-tested and enforced by `tools/uppercut_validate/attributes.py` and
`budget.py`. The reference bout reads **none of them**. It runs on six hardcoded
`BIAS` tuples in `tools/uppercut_sim/policy.py`.

The sharpest instance is Chin. `condition_model.chin` declares `attribute: "chin"`,
`scales: [knockdown_resistance, stun_duration]`, and
`max_resistance_confers_immunity: false` — a bound Rule 14 states explicitly and a
validator enforces against the data. Searching the simulator for `chin` returns ten
hits: every one is either the *region* `jaw_chin` or the word "machine". **Nothing in
the bout knows what a chin is.** Two fighters cannot differ in durability, because
there are no fighters — only stress profiles with tuning constants.

The ROADMAP's Phase 1A minimum scope requires "explainable outcomes tied to
**attributes**, tactics, fatigue, positioning, and recorded events". Fatigue and
positioning now execute. Attributes do not exist in the loop at all.

This is the same declared-but-inert class the coverage checker closed inside `data/` —
and the checker misses it, because `SIMULATED` scopes to combat-model files and the
attribute files sit outside it. That scope line was a deliberate call and it is now
demonstrably one file too narrow.

### 2. There is no Judge subsystem

Minimum scope names "a deterministic Judge subsystem behind the score firewall". What
exists is `Bout._score_round` — a ten-point-must computed inline, on the same object
that resolves contact, reading `self._cards` directly. Rule 3 holds today only because
`observe()` hands policies a plain dict. That is a real firewall, but it is a property
of one method's return type rather than of a subsystem boundary.

Referee profiles are authored data — Rule 16's seven philosophies, the stoppage
conditions in `condition_model` — and **nothing consumes them**. Every referee in the
model behaves identically.

### 3. Style balance regressed and is currently open

Logged in `exploit_hunt.md` under "Superseded". The drainer sits at **22%** on seed
base 7000, below the 30% floor an earlier pass had achieved, because the units
correction changed what recovery is worth. Viability still passes — the gate Rule 21
actually sets — but the band claim does not.

## Where the gate actually stands

Quality gate, nine items:

| # | Gate item | Status |
|---|---|---|
| 1 | Complete CPU vs CPU matches, selection → post-fight flow | **No.** Neither the reference sim nor the engine has selection, quick menu, statistics or post-fight flow |
| 2 | CPU uses no hidden score, opponent input or privileged state | **Yes**, proven as a set relation plus the call-signature firewall |
| 3 | No known infinite stun, clinch, running, meter or safe-animation exploit | **Yes**, the abuse list plays each one as a policy |
| 4 | Replay/event log explains major combat and judging events | **Yes** in the reference sim; not in the engine |
| 5 | Visual speed readable enough for spectators | **Untestable** — nothing renders yet |
| 6 | Effective aggression wins without volume-only dominance | **Yes** (First Bell Firestorm) |
| 7 | Patient stamina control wins without empty avoidance | **Yes** by the check; see finding 3 |
| 8 | Technician, Counterpuncher, Showman, Power Threat keep routes to victory | **Yes** by viability; balance open |
| 9 | Balance reports identify dominant loops and ineffective traits | **Yes** |

Minimum-scope items not yet met: the Judge subsystem (finding 2), attributes in the
loop (finding 1), quick menu and statistics, and "distinct tactical plans and
adaptation" — pattern recognition exists as `opponent_read`; planning and adaptation do
not.

## Recommended order

> **Step A is done** (2026-08-03, `docs/phase1a/attributes_in_the_loop.md`). Fourteen
> attributes now reach the fight through `data/attribute_effects.json`, ten are named as
> unexpressed, and the coverage checker's scope was widened to include the file. Balance
> did **not** improve — the drainer and showman are still below 30% — but it is now a
> consequence of cards traceable to each style's canon rather than of six constants.
> Steps B onward stand as written.

**A. Put attributes into the loop.** *Largest gate item, and it unblocks the rest.*
Fighters become attribute-derived rather than constant-derived: Chin scales knockdown
resistance and stun duration inside the pressure function; reach shifts the range bands
per pairing; power and speed replace the hardcoded halves of `BIAS`. The stress profiles
survive — they become *attribute loadouts plus a tendency mapping* rather than tuples.
Then widen the coverage checker's `SIMULATED` set to include the attribute files and
register whatever remains unexpressed, with a reason.

Why first: gate item 1 and half of minimum scope depend on there being fighters. It also
converts finding 3 from a tuning argument into a measurable one — the drainer's 22% is
currently a property of six constants nobody can defend from canon.

**B. Extract the Judge subsystem.** *Cheap, and it hardens the rule this project cares
about most.* Move scoring out of `Bout` into a module that receives only an observation
stream and returns sealed cards. Rule 3 stops being a property of one method and becomes
a boundary a validator can check. Consume referee profiles so the seven philosophies
differ in warnings, deductions and stoppage thresholds while sharing the count
arithmetic — exactly as Rule 16 states.

> **The Judge subsystem is extracted** (2026-08-04, `docs/phase1a/judge_subsystem.md`):
> `tools/uppercut_sim/judge.py`, witnessed facts in, sealed cards out, five
> source-relation checks in `cli all`, byte-identical over 72 bouts.
>
> **Referee profiles are consumed** (2026-08-04, `docs/phase1a/referee_consumption.md`):
> `data/referee_semantics.json` turns the seven philosophies into executed
> enforcement — the clinch warning/deduction ladder, break patience, and the
> `referee_judgement` stoppage — with the neutral official proven identical to
> the incumbent engine (72/72) and the protective official genuinely stopping
> fights the others let run (2/72). Named finding: no stress policy ever
> clinches, so clinch-side tendencies are unreachable in natural play until
> step C gives the CPU the clinch. **Step B is done.** Next slice item: the
> C++ core scaffold (Phase H).

**C. Re-open style balance with attributes in place.** After A, re-run the sweeps. If the
drainer still floors out, the question is answerable from canon instead of from `BIAS`.

**D. Phase H in the engine — or the C++ decision first.** See below.

> **Phase H is proven** (2026-08-04, `docs/phase1a/determinism_probe_results.md`):
> `UppercutCore` lives in the sandbox as a real C++ module, compiled by a toolchain
> installed on the Director's license acceptance, and its probe reproduced the
> Phase D hysteresis walk byte-identically across processes and a full rebuild —
> identical bytes to the Python reference, analyzer-first as always. Next slice
> item: **4. the two-fighter authoritative loop in C++** — where the core starts
> being a core.
>
> **Phase I is proven** (2026-08-04, same doc): the two-fighter loop runs in
> `UppercutCore` — five canon files, real ring positions, stamina economy,
> commitment, band hysteresis from real separations — byte-identical across a
> full rebuild and identical to the Python recomputation. And the float probe
> came back **bit-identical to CPython** on all checkpoints, so the reference
> sim's float arithmetic has an evidenced road into C++. Next slice item:
> **5. real movement and swept collision**.
>
> **Phase J is proven** (2026-08-04, same doc): punches have geometry. An
> authored fist sweep (`data/pose_geometry.json`), live only during animation
> active ticks, against the defender's real position — and the lane result is
> emergent in the engine evidence: 132/132 jabs blocked by the closed high
> lane, 114/114 body straights landed through the open one, written as a rule
> nowhere. Byte-identical across a full rebuild, identical to the Python
> recomputation. Next slice item: **6. the four punches animated on generic
> fighters** — the first thing a spectator can see.

**E. Housekeeping.** Four stale remote branches (`docs/boxing-punch-guard-reference`,
`-v2`, `docs/confirmed-uppercut-direction-2026-08-02`, `docs/event-presentation-reference`)
are merged or superseded and should be deleted. Quick menu and statistics are small and
unbuilt.

## The one decision that is yours

> **Decided** (Director, 2026-08-03): the trigger fires. C++ authoritative fight core,
> Blueprints for presentation and orchestration, Python tooling unchanged — logged as
> `docs/decisions/0012-cpp-fight-core-and-slice-sprint-freeze.md`, together with a
> document freeze for the slice sprint. Step D now reads: Phase H is a C++ scaffold
> proven by the established analyzer-first discipline. The argument below is retained
> as the record it was decided on.

**Does the fight core stay in Blueprint, or does Rule 22's C++ trigger fire now?**

For firing it: Phase G's graph is already large, and it produced a defect — rule 7,
pure-node re-evaluation — that exists *only* because Blueprint's evaluation model differs
from an imperative one. A full fight core (attributes, stamina, guard postures,
knockdowns, referee, judges) is perhaps an order of magnitude more graph than Phase G,
and every one of those systems is already readable, testable Python. Decision 0002 names
"deterministic simulation" and "reusable core systems" as C++ territory.

For staying: Blueprint has now carried seven phases with byte-identical reproduction,
including a full asset regeneration. The trigger was left "armed for scale, not
correctness", and nothing has failed on correctness.

My read: the Blueprint phases have proven what they were built to prove — that the
canonical models *are* implementable deterministically in-engine. Continuing to
hand-author the entire fight core as graphs buys little further evidence and costs a
great deal of authoring. I would fire the trigger for the simulation core and keep
Blueprints for presentation and glue, which is what Rule 22 describes. It is a
production-strategy call with real cost either way, and it is yours.

Decide it **before** step A: attributes-in-the-loop is the first piece of work large
enough that doing it twice would hurt.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 15:10 UTC | END ] -->
