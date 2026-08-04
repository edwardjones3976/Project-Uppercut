<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 20:35 UTC | START ] -->

# Ring and fighter scale — researched reference and the numbers we use

Written after the Director caught the rendered ring being badly out of scale. The
first arena spawn sized the ring by eye — "1.7× the fighting axis," applied to the
widest mesh in the set — and produced a ring **44% too large** with two fighters
lost inside it. This is the reference that replaces the guess, and the record of
what the numbers actually are.

## Researched dimensions (2026-08-04)

| Thing | Real value | Source |
|---|---|---|
| Ring, inside the ropes | 16–20 ft (4.88–6.10 m) standard for professional bouts; 20 ft for major title fights; range extends to 24 ft (7.3 m) | BoxingInsider, Wikipedia, Dimensions.com |
| Apron beyond the ropes | ≥ 2 ft (0.61 m); one reference gives 33.5 in (85 cm) | BoxingInsider, Dimensions.com |
| Platform above the floor | 3–4 ft (0.91–1.22 m) | BoxingInsider, Wikipedia |
| **Ropes** | **Four**, at 18 / 30 / 42 / 54 in = **46 / 76 / 107 / 137 cm** above the canvas | Wikipedia, BoxingInsider |
| Corner posts | ~5 ft (1.5 m) above the canvas | Wikipedia |
| Canvas padding | ~1 in (25 mm) | BoxingInsider |

Fighter height, top-10 averages by division:

| Division | Average height |
|---|---|
| Heavyweight | 194.3 cm |
| Cruiserweight | 186.4 cm |
| Light heavyweight | 185.9 cm |
| Super middleweight | 184.8 cm |
| **Middleweight** | **180.6 cm** |
| Welterweight | 173.2 cm |
| Featherweight → strawweight | ~158–169 cm |

## What canon already said, and it was right

`data/movement_model.json` carries its own derivation and it does not need
changing:

    axis_length_ru: 4.92
    axis_length_derivation: "side_m / spatial_units.reference_reach_span_m = 6.4 / 1.30"

So **one ru is 1.30 m** and **the ring is 6.4 m a side** — 21 ft, between boxing's
20-foot championship standard and its 24-foot maximum, and a legitimate pro size.
The render's `RuToCm = 130` is therefore correct. A suspicion that it was inflating
the world by 30% was checked against this derivation and dropped; the geometry
around it agrees (`half_depth_ru` 0.14 → 18 cm of half-body including the arms,
`min_center_distance_ru` 0.28 → bodies touch at 36 cm centre to centre).

## Measured, in-engine

| Thing | Measured | Verdict |
|---|---|---|
| SKM_Manny height | **180.5 cm** | Middleweight, to within a millimetre of the divisional average. No scaling needed |
| SKM_Quinn height | **180.2 cm** | Same |
| Ring rope rectangle | 19,581 pack units | Scaled to 639.6 cm = canon's ring side |
| Resulting scale | **0.03266** | Was 0.0472 — a ring 44% oversized |
| Apron at that scale | 56.4 cm each side | Just under the 61 cm regulation minimum; acceptable |
| Corner posts at that scale | ~192 cm above canvas | Above the ~150 cm reference; the posts share a mesh with the frame and cannot be isolated without editing geometry |

## The ropes, and what we do about them

The pack ships **four** ropes, which is correct. Their spacing is not. Measured at
the right scale they sit at **154 / 118 / 52 / 23 cm** — the top pair about 12%
high, the bottom pair less than half where they belong, bunched near the mat.

Because they are four separate meshes, `AUppercutBoutDirector::BuildArena` places
each on its own regulation line — 137 / 107 / 76 / 46 — rather than accepting the
artist's spacing. This is presentation correcting presentation; the sim has no
opinion about ropes and never reads them.

## The rule this establishes

**The rope line is what "ring size" means, and canon's track axis is the rope
line.** Scale is taken from the rope rectangle, never from the widest mesh in a
set, and never from an invented multiple of anything. Everything else — apron,
platform, posts — follows from that one reference, and can then be checked against
the table above instead of against an impression.

## One correction on the record

The pale shape in the middle of the canvas was called a rendering artifact twice —
first the debug floor, then z-fighting between ring surfaces. Both were wrong.
Removing the floor did not move it and neither did a 2 cm depth separation, which
is what finally prompted opening the source texture: it is the pack's own painted
emblem, **two boxing gloves** in the centre of the mat. It is artwork, not a bug.
See the arena audit's originality gate for what that means for shipping.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 20:35 UTC | END ] -->
