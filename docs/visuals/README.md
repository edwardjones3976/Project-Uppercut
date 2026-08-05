<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 20:40 UTC | START ] -->

# Visuals

Screenshots of the rendered slice, committed so they can be looked at from any
machine rather than only on the box that produced them.

Regenerate with one command from the repo root:

```
.\tools\engine\show_me.ps1
```

Naming is `YYYY-MM-DD_TAG_tick_NNNNN.png`. The tick is the simulation tick the
frame was captured at, so two frames with the same seed, tick count and tag
should be the same picture — and if they are not, something in the sim moved.

## What is here

| file | what it shows |
|---|---|
| `2026-08-04_mannequins.png` | the mannequin pass with no ring — two demo mannequins on a checker floor, plus the two position markers |
| `2026-08-04_ring_close.png` | the Fab arena close in |
| `2026-08-04_ring_scaled.png` | the arena after the 44% oversize fix — scaled from the rope rectangle to canon's 6.4 m, ropes reset to 137/107/76/46 cm |
| `2026-08-05_SELFTEST_tick_*.png` | a full run at seed 4242, three frames from the same fight |

## Known and unfixed, so nobody reports them as new

- The far-left and far-right posts and rope lines are **extra geometry from the
  arena pack**, outside the ring proper.
- The white blotch on the canvas is the **pack's own painted glove emblem**. It
  was diagnosed as a debug floor and then as z-fighting before that was
  established; both diagnoses were wrong.
- The fighters are **Unreal demo mannequins**, not boxers.
- The lighting is a **probe rig**, not a look — black background, no crowd,
  nothing beyond the ring.

## What the pictures do NOT prove

Rendering holds zero authority over the fight. The marker stream is byte-identical
with primitives, with mannequins and with the full arena — hash
`b6f1c24b62671b8dc81b37057f851f33e075f9280d34b68f5cdcc346c0276bda`, reproduced
again on 2026-08-05. A screenshot shows what the presentation layer did with a
result it had no part in deciding.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 20:40 UTC | END ] -->
