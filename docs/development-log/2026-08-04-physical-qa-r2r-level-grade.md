<!-- [ Auto (Cursor Agent) | Composer | 2026-08-04 20:39 UTC | START ] -->

# Physical QA + Indie R2R-level grade — 2026-08-04

**Disclaimer:** This grades Project Uppercut as an **indie spiritual successor loosely inspired by Ready 2 Rumble**, at **Phase 1A sandbox level** (CPU-sim foundation + first rendered slice). It is **not** a grade against Midway shipping polish, Buffer trademarks, R2R roster IP, or a finished indie boxing game. No playable match is claimed (Rule 18). Report-only: no code or balance fixes were made in this pass.

## Environment under test

| Field | Value |
|---|---|
| Commit | `566fff9` — `fix(render): ring scale was 44% oversized - scale from the rope line, ropes to regulation` |
| BoutDirector arena/camera work | **Included** (landed on HEAD before this QA; plan item 2B) |
| Engine | UE 5.8 at `C:\Program Files\Epic Games\UE_5.8` |
| Project | `sandbox/UppercutSandbox.uproject` |
| Comparison bar | Indie R2R-inspired at this level — see `docs/design/ready_2_rumble_design_study.md` |
| GitHub web fetch | `edwardjones3976/Project-Uppercut` returned 404 from this harness (likely private); local clone used |

## Physical probe results

| Probe | Result | Evidence |
|---|---|---|
| `pytest -q` | **PASS** — **559 passed** in ~129s | Fresh suite. `STATUS.md` still cites 544 / Phase L / slice item 8 — **stale** vs HEAD |
| `python -m tools.uppercut_validate.cli all` | **PASS** — `RESULT: OK` | Rule 3/10/16 + all Phase 1A definition validators green |
| `build_uppercut_core.ps1` (Editor Development) | **PASS** — exit 0, ~5.6s link | `UnrealEditor-UppercutCore.dll` rebuilt with ring-scale director |
| Phase N `UppercutCoreCondition` A1/A2/B1 @ 5400 | **PASS** | A1=A2 sha256 `88af6f30…14ddc37` (matches documented proof); B1 `cf94d644…ae807f7` differs as required; analyzer `ok: true`, float probes bit-identical to CPython |
| Guard erosion at 5400 ticks | **Noted, not fail** | `opened=0`; horizon ~216000 ticks (~hour). Named tuning finding still live |
| Render probe R1/R2 `-Arena -Markers` @ 5400 | **PASS** | R1=R2 sha256 `b6f1c24b…276bda` — **byte-identical to Phase K / mannequin stream**; analyzer `ok: true`. Arena presentation holds **zero** authority |
| Screenshots | Captured | `sandbox/Saved/phaseM/shots_R1/` ticks 240, 900, 1800, 3000, 4200 |

## Visual QA (Director-facing slice)

Screens inspected: `shots_R1/tick_*.png` from this session’s arena run.

**What works at this level**

- Fighters are **inside** a real ring that reads as a ring. Earlier arena mis-spawn evidence (`shots_ARENA1`) had bodies on a checker floor beside the ring; the rope-line scale fix on `566fff9` closes that.
- Four ropes are visible; neon posts / apron lights give a cartoon-arcade silhouette without copying R2R venues.
- Ring occupancy looks plausible vs 6.4 m rope-line canon (`docs/design/ring_and_fighter_scale.md`).
- Marker stream unchanged under `-arena` proves the render path still does not author combat truth.

**What hurts spectator readability (gate item 5 — now testable, not yet passed)**

- Fighters often read as **dark silhouettes** against the lit canvas; punch/guard intent is hard to call from stills alone.
- Black void, no crowd, no broadcast chrome, no stamina/condition HUD — Phase N condition is proven in commandlets, **not yet visible** in the rendered slice.
- Comedy / personality signal is charter-only on screen: mannequins + Fab cartoon ring, no character identity yet.
- Floating debug-ish spheres above heads in some frames read as probe chrome, not arcade juice.

## Phase 1A gate (live judgment)

| # | Gate item | Judgment after this QA |
|---|---|---|
| 1 | Complete CPU vs CPU, selection → post-fight | **No** — still no shell |
| 2 | CPU uses no hidden score / privileged state | **Yes** — validators + live repo scan |
| 3 | No known infinite exploits on the abuse list | **Yes** — suite/exploit hunt standing |
| 4 | Replay/event log explains major events | **Yes** in Python reference; not the rendered engine path |
| 5 | Visual speed readable for spectators | **Testable, not passed** — ring framing improved; fighter readability still weak |
| 6–9 | Aggression / stamina / style routes / balance reports | **Checks green; style balance still open** (drainer & showman below 30% floors per `attributes_in_the_loop.md`) |

Minimum-scope gaps unchanged: quick menu/statistics, knockdown/decision/stoppage in the rendered round (slice item 9), clinch unused in natural CPU play.

## Letter grades (indie R2R at this level)

| Dimension | Grade | One-line rationale |
|---|---|---|
| Product direction / identity | **A−** | Comedy-first arcade with real boxing bones is clear; R2R study absorbs spirit and correctly hard-NO’s Buffer IP and dishonest meter cheats |
| Combat logic depth | **A** | Punches, lanes, guard/slip, per-region condition, attributes-in-loop, Crowd Bar architecture — far ahead of a typical indie prototype at this stage |
| Simulation honesty / Rule integrity | **A** | Score firewall, Judge subsystem, observable-only CPU — the right anti-R2R-AI-flaw bet |
| Engine execution (physical) | **A** | Build clean; Phase N hashes match proof; render R1=R2=Phase K with arena on — discipline holds |
| Visual / spectator readability | **C+** | Ring scale fixed and arcade-adjacent; fighters too dark, no HUD/crowd; gate 5 not passed |
| Arcade fun signal | **C** | Charter is loud R2R energy; the slice is still a competent tech demo, not a funny fight yet |
| Production maturity for indie peer | **A−** | Docs, CI, 559 tests, analyzer-first determinism are elite; STATUS drift and missing match shell are the maturity gaps |
| **Overall** | **B+** | Keep the direction. Systems honesty is best-in-class for an indie R2R spiritual successor at sandbox stage; the distance to “demo day” is spectacle, readability, and one finished round |

### Keep / change / kill

- **KEEP:** Sim-first unified combat; score isolation; Crowd Bar / Instrument Ultimate honesty vs R2R meter cheats; C++ fight core + Blueprint presentation; analyzer-first evidence.
- **CHANGE:** Guard-erosion coefficients so pressure opens a guard inside a real bout; style floors for drainer/showman; fighter lighting / silhouette readability; slice item 9 (knockdown, decision, stoppage) so condition has somewhere to go; regenerate `STATUS.md` so evidence stops lying about phase.
- **KILL:** Nothing structural. Do not chase Midway shipping juice or Buffer-adjacent presentation.

## Rule 19 — current slice only

| Priority | Held? | Notes |
|---|---|---|
| impressively responsive | Partial | Authoritative 60 Hz tick + commitment model; no human input path yet |
| visually fast | Partial | Boxing clips scrub to sim; dark silhouettes blunt readable speed |
| fun and funny | Missing | On-screen comedy not present |
| boxing-logic accurate | Held | In Python + C++ core; visible only as poses |
| enjoyable across repeated matches | Missing | No match shell |
| steady-paced | Partial | Round clock authored; rendered slice is a fixed-tick probe |
| secretly layered | Partial | Depth in data/sim; spectator cannot yet feel it |

## Named findings (not rounded away)

1. **Guard erosion unreachable in a real fight** at current coefficients (~243 blocked punches / ~216k ticks). Mechanism correct; tuning call still open.
2. **Style balance open** — drainer and showman below 30% on both seed bases after attributes-in-loop.
3. **Phase N not visible in render** — condition lives in `UppercutCoreCondition`; BoutDirector stream header still `phase=K`.
4. **`STATUS.md` stale** — generated at older commit; cites Phase L / 544 tests while HEAD is Phase N+render and suite is 559.
5. **Fighter silhouette readability** — primary blocker for gate item 5 after ring scale was fixed.
6. **CPU never clinches in natural play** — referee clinch tendencies remain unreachable (standing finding).

## Recommended next slice (informational only)

Canon next step remains **slice item 9: one rendered round with knockdown, decision, and stoppage** — where accumulated condition finally has somewhere to go — plus a Director call on guard-erosion coefficients if passive blocking must be answerable inside twelve rounds. No implementation in this report.

<!-- [ Auto (Cursor Agent) | Composer | 2026-08-04 20:39 UTC | END ] -->
