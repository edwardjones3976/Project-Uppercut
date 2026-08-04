<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 08:50 UTC | START ] -->

# Design study — Ready 2 Rumble Boxing (1999), from public documentation

**Provenance note first (Rule 1, and the study's own legitimacy):** this study is
compiled from published reviews, retrospectives and documentation only. A
disc-image download offered by the Director on 2026-08-04 was **declined** — the game
remains copyrighted commercial work and an unauthorized copy is not a research
method this project uses. If first-hand feel-reference is ever wanted, legitimate
physical copies circulate secondhand and playing one is the Director's own
prerogative. Nothing in this document licenses anything; it maps spirit and draws
the identity line.

## What it was

Midway San Diego, ~75 credits, 11 months to the Dreamcast launch window. ~1.57M
units, ~83% aggregate, eighth best-selling Dreamcast title in the US, nominated for
Console Fighting Game of the Year 2000. The pitch that worked: exaggerated,
cartoonish, *accessible* boxing against the simulation tide — "arcade-style fun
translated to home console graphics" — at a committed 60 fps, with mocap deliberately
exaggerated by hand-keyed animation, dynamic bruising on fighters, twelve original
comedic boxers, and Michael Buffer's licensed announcing.

## Mechanics anatomy → where Project Uppercut already reinterprets it honestly

| Ready 2 Rumble | The mechanic underneath | Uppercut's standing answer |
|---|---|---|
| RUMBLE meter: letters earned by hard punches **and taunts** | Showmanship and clean work convert to spectacle currency | **Crowd Bar** — observable gain sources, novelty-decayed, taunt-adjacent `showmanship` already in the event vocabulary |
| Rumble Flurry: cinematic super on full meter | Meter cashes into a spectacle attack | **Instrument Ultimate** — rides the heaviest real punch through the ordinary pipeline: blockable, dodgeable, whiffable. The bar buys force, never safety |
| High/low blocks on two triggers | Coverage as a binary height choice | **Ten postures over two guard volumes** (Decision 0010) — lanes from structure, already live in the C++ core (Phase L) |
| Sways, ducks, full dodges | Active evasion distinct from guard | **Evasion table** — slip/roll frame-locked windows that outrank guard (Phase L) |
| Simple inputs, combo momentum | Accessibility without input complexity | Charter promise: "instantly responsive… much deeper than it initially appears" — depth in the model, not the fingers |
| Championship gym: training minigames buy stats | Progression made tactile | Attribute families under the Decision 0007 budget; training design pending |
| Dynamic bruising | Damage as visible storytelling | `animation_model.damage_visualization` + regional condition tracks — authored, and honest by construction |
| Committed 60 fps | Readability as a hard budget | The authoritative 60 Hz tick; gate item 5 (visual speed readable) now testable |
| Predictable AI (its most-cited flaw) | The part that aged worst | CPU from observable evidence with `opponent_read`; planning/adaptation named as unbuilt — their weakness is our named roadmap item |

The pattern worth stating: Uppercut's canon has already re-derived R2R's crowd-pleasing
economy **with the dishonesty removed**. R2R's meter state granted enhanced speed and
power; Uppercut's bar buys one amplified punch that obeys every collision law. That is
Rule 17's line — spectacle without outcome dishonesty — applied to the inspiration
itself.

## The protected-identity line (hard NOs, per the originality gate)

- **"Let's get ready to rumble"** is Michael Buffer's famously guarded trademark
  (licensing reportedly ran to nine figures in perpetuity). The phrase, the
  letter-spelling meter gimmick built on it, and any soundalike announcer riff on it
  are radioactive. Uppercut's announcer is an original personality with original
  catchphrases, full stop.
- Character names, likenesses, gimmick-and-name pairings (Afro Thunder, Boris
  Knokimov, Damien Black, et al.) and the roster's specific ethnic-archetype
  presentations do not carry. What carries is the *casting philosophy* the Midway team
  themselves described: personality-first, beyond default-hero tropes — executed with
  original people and 2026 sensibilities (Rule 17's comedy constraints).
- No audio, UI motif, logo, venue likeness or presentation element crosses.

## What to absorb as spirit

Taunting as gameplay currency with risk attached; training that makes attributes
tactile rather than menu numbers; unlockable venues and outfits as championship
texture; injury that tells the fight's story on the fighter's face; exaggeration
layered on honest motion (their mocap-plus-hand-keying is precisely the
mannequin-plus-licensed-pack plan adopted 2026-08-04); and the confidence to be
loudly, deliberately funny while the boxing underneath stays real. That last sentence
is the project charter in one line, which is why this game is the named inspiration.

<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 08:50 UTC | END ] -->
