<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-08 23:08 UTC | first watchable fight record start ] -->
# The first complete integrated fight

**complete integrated fights = 1.**

This directory holds the first fight the integrated bout ever finished on its
own: every system in the chain ran, something ended the fight, and the sealed
cards opened. It is committed as evidence of that fact, not as a claim that
the fight is *good* yet.

## The fight

| | |
|---|---|
| Seed | 4242 |
| Referee | Nkiru Okafor (protective) |
| Scheduled | 12 × 3:00 |
| Result | **TKO — red_corner**, 0:50 of round 2 (tick 13847), `knockdown_limit` |
| Knockdowns | blue_corner down 4 (bout limit exceeded), red_corner down 3 |
| Counts | every knockdown counted; every rise at the mandatory 8 |
| Cards at stoppage | Bello 8–10, Reyes 8–10, Wojcik 9–9 (sealed until close, unused — inside the distance) |

Deterministic: re-running the exporter reproduces this fight byte-identically
from the seed.

## The files

- `fight.json` — the export of the bout's authoritative stream in the viewer's
  schema. Every number is read off `bout.rows` / `bout.samples` / the sealed
  cards; nothing is recomputed (see `tools/uppercut_integrated/export_fight.py`).
- `watch.html` — `../first_bell_viewer.html` with `fight.json` injected at its
  `/*FIGHT_DATA*/` marker. Open in a browser. Presentation only: the broadcast
  ticker's sentences cite the stream's reason codes, and no part of the page
  has combat authority.

## Diagnostics, deliberately not conclusions

Decision 0032 §3 is in force: until the Director rules otherwise, cadence and
outcome numbers from integrated runs are **diagnostics, not calibration
evidence**, and no lab observation may change canon, tuning, acceptance
criteria, or authoritative implementation without an explicit Director
disposition. In that spirit, observed and recorded only:

- Seven knockdowns in under two rounds; the fight ended on the bout knockdown
  limit, not on the count or the cards.
- Punch volume remains high (336 resolved punches in ~3:50 of fight time;
  73% accuracy both corners) — the round-three panel's "the fight punches too
  much" observation survives evasion integration so far.
- Evasion reasons in this fight: `vacated=5`, `counter=0`, `region=0`,
  `clear=246`. Slips happen and occasionally work; the authored counter
  relationships never fired. Whether that is policy, timing windows, or
  matchup authoring is exactly the kind of question that now has a fight to
  be asked against.

None of these numbers proposes a change. They are the first entries in the
ledger the Director said this milestone would open.
<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-08 23:08 UTC | first watchable fight record end ] -->
