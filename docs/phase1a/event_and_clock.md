<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 10:44 UTC | START ] -->

# Event Presentation and the Authoritative Clock

Canon: `data/event_model.json`, `data/clock_model.json` ·
Validators: `tools/uppercut_validate/event.py`, `tools/uppercut_validate/clock.py` ·
Tests: `tests/test_event_clock.py`

**Rule 18.** Definitions only.

## Where the event model came from

`docs/design/event_presentation_reference.md` was merged as `a1c900e`, authored by a third
contributor (OpenAI GPT-5.6) and properly tagged. It ends with a section called "Validation
requirements" listing eleven things future validators should reject.

This is those validators. A design document that asks for enforcement and never gets it is how good
intentions turn into folklore, so the list is implemented rather than admired. The author's tags and
prose are untouched; the intake note recording the cross-lock sits in its own tagged block.

## Presentation is loud and powerless

That is the single idea the event model exists to enforce. Prestige, broadcast, crowd spectacle and
venue dressing all sit outside the simulation's authority — the same position the camera already
occupies, and for the same reason the camera is excluded from the determinism hash: it has to be
*provably* outside rather than politely outside.

Eight authority flags are schema constants pinned to `false`. Prestige alters no combat value and no
attribute — a bigger event does not make a punch land harder. Crowd presentation neither reads nor
alters the cards. Broadcast holds no privileged, hidden or future knowledge; it sees what a spectator
sees. And no dynamic incident may alter a fight outcome, because an incident that changes a result is
a rigged fight with good lighting.

Two more are worth naming. **Ring size is real space**, read by the Elastic Footwork model, never a
hidden stat modifier — implementing it as a stat would be the same category of error as a rubber-band
multiplier. And **presentation may never obscure authoritative evidence**: contact classification,
knockdowns, fouls, counts and stoppage reasons stay visible, because spectacle that hides the
decisive moment has failed at the one job the presentation layer has.

Officials are required rather than assumed: a referee, three judges, a timekeeper and a ringside
physician, each declaring what they actually decide.

## The clock, and the check it unblocked

`schemas/clock_settings.schema.json` has existed since Phase 0 with nothing behind it. That is why
"accelerated-clock synchronization" — one of the ROADMAP's eleven required automated checks — could
not run: there was no clock to test.

One authoritative clock at 60Hz, read by simulation, judging, officiating, corners, commentary,
crowd, broadcast, camera, replay and statistics. The validator requires each of those to be named,
because a system on its own schedule is a second clock wearing a different name.

The Accelerated Clock is a **display mapping** — 3:00 displayed over 1:45 real, exactly as Rule 8
states — and four flags keep it there. It may not touch the simulation tick rate, the authored frame
data, stamina per tick, or the knockdown count clock. The count exemption is deliberate and is the
one I would defend hardest: a knockdown count is a safety instrument, and it does not speed up
because somebody toggled a display option.

Round lengths are one, two or three minutes with free-form values prohibited, and the between-rounds
break is thirty real seconds — cross-checked against `condition_model.json`, which states the same
break in ticks. Two files disagreeing about the break would be two clocks by another name, so the
validator computes one from the other rather than trusting both.

## Gate progress

Nine of the ROADMAP's eleven required automated checks now run green against the reference simulator.
Two remain, and they are named rather than rounded away: style-viability and dominant-loop detection
at scale, and the full repetition abuse list — safe-animation abuse, stun loops, clinch abuse,
excessive running, passive blocking.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 10:44 UTC | END ] -->
