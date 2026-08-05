<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 04:50 UTC | START ] -->

# The research pipeline

Published evidence enters this project through one path, and it is narrow on
purpose. The failure being designed against is specific: **a scraped paragraph
quietly becoming a gameplay formula**, with a citation attached that nobody
re-read.

    harvest            ask a scholarly index a written-down question
      ->  metadata     one record per source, identity verified, nothing claimed
      ->  review       a human reads the method and records what it measured
      ->  synthesis    what a lane collectively supports, and what it does not
      ->  decision     a Decision record accepts evidence into canon. Only this.

## Layout

| Path | What lives here |
|---|---|
| `queries/` | the exact searches run, per lane, so a harvest is reproducible and its bias is visible |
| `raw/` | reconstructed abstracts and fetched text. **Untracked.** Copyright and size both say keep it out of git |
| `metadata/` | one JSON evidence record per source. This is the committed artifact |
| `rejected/` | sources read and set aside, each with `rejected_because`. Kept so they are not rediscovered monthly |
| `reviewed/` | longer reading notes when a record's fields are not enough |
| `syntheses/` | working notes behind the lane documents in `docs/research/` |
| `citations/INDEX.md` | generated: every source, by lane, with its status |

## Commands

    python -m tools.research.cli harvest punch_biomechanics --limit 14
    python -m tools.research.cli validate      # schema + the evidence gate
    python -m tools.research.cli index         # regenerate the citation index
    python -m tools.research.cli summary

## The six lanes

Narrow collections, ten to twenty strong sources each, rather than "all boxing
research":

`punch_biomechanics`, `fatigue_and_recovery`, `knockdowns_and_stoppages`,
`tactics_and_ringcraft`, `responsiveness_and_determinism`,
`training_and_spectator_design`.

## The gate

`tools/research/gate.py`, proven by `tests/test_research_gate.py`, which breaks
each rule on purpose and asserts it is caught. In short:

- **Tier 3 can never be accepted.** Reviews, retrospectives, coaching articles
  and community analysis may start a hypothesis and may never end one.
- **Accepting evidence needs a decision record that exists on disk.** There is
  no way to mark a source `accepted` from inside the research pipeline.
- **`confidence: high` requires `peer_review_status: verified`**, and a script
  may never write `verified` — the honest ceiling for a machine is `likely`.
- **Quotes are capped at 25 words**, with a locator. A record cites a source; it
  does not reproduce one.
- **Findings without a method are refused.** Two findings that disagree cannot be
  weighed if one of them has no method to weigh.
- **No DOI is fine; an unexplained missing DOI is not.** Commission rules and
  engine documentation have no DOI, and saying so is one field.
- **A retracted source cannot be accepted**, and a rejection must say why.

## On Firecrawl

The brief names Firecrawl as the acquisition layer. It is not installed here and
this pipeline does not pretend to be it. What is built instead is the part of
that architecture that carries the correctness: **scholarly identity from
OpenAlex**, which is where DOIs, venues, document types, retraction flags and
open-access status actually live, plus the review gate that decides what any of
it is allowed to mean.

If Firecrawl is added it slots in *ahead* of the harvester — discovering and
cleaning full text into `research/raw/` — and nothing downstream changes. That
ordering is the point: acquisition is the replaceable part, and the gate is not.

## Access discipline

Metadata APIs and open-access material only. No paywall, no authentication, no
robots exclusion, no license limit is worked around. Abstracts arrive from
OpenAlex as an inverted index, which is how OpenAlex distributes them; the
reconstruction stays in untracked `raw/`, and only short quoted extracts reach a
committed record.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 04:50 UTC | END ] -->
