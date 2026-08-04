<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 09:05 UTC | START ] -->

# Design study — Fight Night Champion (2011), from public documentation

**Director directive, recorded (2026-08-04):** the reference titles in this design
lineage — Ready 2 Rumble, Fight Night, and neighbours — are **guidance and motivation
only. No copyrighted information or material will ever be used.** This restates and
binds what Rule 1 and the originality gate already require; studies in this folder are
compiled from published documentation, never from unauthorized copies, extracted
assets, or protected material.

With this study the reference triangle closes: Ready 2 Rumble marks the arcade-comedy
pole, Tactic Boxing the indie-ragdoll pole, and Fight Night Champion the **simulation
pole** — the benchmark for what serious boxing feel means in a videogame.

## What it was

EA Canada, 2011. Full Spectrum Punch Control on the right stick, physics-driven
visual damage (bruising, swelling, cuts computed from impact force, angle and contact
point), pro-boxer motion capture, 50+ licensed real boxers across eight weight
classes, a cinematic Champion Mode and a Legacy career. ~85 Metacritic, ~1.91M units
— **and the final entry**. The series did not die of quality; it died of licensing
economics: per-boxer negotiations (Mayweather's demands were publicly declined) made
the model resource-intensive enough that EA pivoted to UFC.

**That is the strategic lesson before any mechanical one:** the simulation king was
killed by real-likeness licensing. Project Uppercut's all-original roster is not just
legal hygiene — it is the reason this project can exist on ground EA vacated.

## Mechanics anatomy → Uppercut's standing answers

| Fight Night Champion | The mechanic underneath | Uppercut's standing answer |
|---|---|---|
| Damage visualized from force, angle, contact point | Injury as computed, located consequence | **Regional condition tracks** — eye_left vs eye_right side-attributable by construction; `damage_visualization` authored in the animation model |
| Stamina drain slows punches, weakens power | Fatigue as degradation, not denial | `punch_model.stamina_gate` — a tired punch arrives later and worse-aligned, never refused (Rule 19), live in the reference sim |
| Blocks weaken over consecutive hits | Guard as an eroding resource | `guard_integrity` — blocked force accumulates in the arms and erodes coverage extents; live since the balance pass |
| Leaning/weaving counters off evasion | Evasion as timed windows feeding counters | Evasion table + `committed_defense` counter windows — live in the C++ core (Phase L, 108 counters in the canonical run) |
| Stunned state (flashing bar) invites exploitation | Vulnerability states as readable openings | `combat_states` composure/stun machinery — declared, ports with condition work (slice item 8) |
| Analog-stick punch control, button alternates, telemetry-informed | Input elegance and accessibility | Uppercut's control scheme is **undecided and open** — FSPC's lesson kept: accessibility alternates and telemetry-driven refinement, no gesture gymnastics |
| Legacy training minigames | Stats made tactile | Same lesson R2R taught; training design pending under the attribute budget |
| Champion Mode's scripted fight outcomes | Drama purchased with outcome dishonesty | **The line Uppercut will not cross**: Rule 17 extends to careers — no fight outcome is ever scripted; drama must be emergent and presented, never imposed |
| One-punch-KO balance gripes | Randomness in the decisive moment | Rule 14 — no flat KO roll; knockdown pressure is a function of observable force, quality and accumulated condition, live in the reference sim |

## The protected-identity line (hard NOs)

EA's branding and trade names (including "Full Spectrum Punch Control"), the Champion
Mode characters and story, all real-boxer names and likenesses (doubly off-limits:
licensed identities of real people), announcer audio, UI motifs, and presentation.
Mechanical *ideas* — fatigue economics, eroding guards, located damage — are common
boxing truth and are already independently derived in Uppercut's canon from boxing
itself, which this table demonstrates: most rows were built before this study was
written.

## What to absorb as spirit

Damage that tells a located, causal story on the body; fatigue that changes how
punches feel rather than whether they exist; counters as the reward for reading
commitment; input accessibility as a design value with telemetry humility; and career
drama built on fights that are always real. Where R2R teaches the volume of the
spectacle, Fight Night teaches the weight of the punch — Uppercut's charter sits
deliberately on the line between them.

<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 09:05 UTC | END ] -->
