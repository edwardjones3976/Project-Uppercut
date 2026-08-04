<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 21:05 UTC | START ] -->

# External review intake — A− / 91, and the nine drift items closed out

Two documents arrived together on 2026-08-04: a graded review of the project, and
the full nine-item drift list from the review pass whose summary was triaged in
`2026-08-04-doc-review-drift-intake.md`. This records what was accepted, what was
acted on, and what is not this session's to fix.

## The grade

**A− / 91.** Direction A, engineering progression A, project discipline A,
determinism and validation A+, creative identity execution B+, documentation
accuracy B, playable-game maturity C+.

The judgement worth repeating, because it names the next problem correctly:

> The main challenge has changed. It is no longer "Can this architecture work?"
> It is now "Can this technically honest machine become responsive, funny,
> visually fast, and irresistibly enjoyable?"

Two of the review's specific findings were verified against the repository rather
than accepted on sight, and both were correct.

## Acted on this session

**Documentation drift (the review's B, and its priority 4).** The README said the
Rule 22 C++ decision "is with the Director" while Decision 0012 had already fired,
the C++ module was compiled, and six engine phases had passed inside it. STATUS.md
carried Phase L and 544 tests after Phase N landed at 559. Both corrected; STATUS
regenerated.

The deeper point is the one the review made about *kinds* of staleness:
`test_doc_drift.py` guards volatile **numbers** and cannot see a stale **sentence
about the state of the world**. `tests/test_decision_state_drift.py` now closes
that: when a decision record exists, no stable document may describe that decision
as open. The check arms itself from the presence of the decision file, so
Decision 0013 inherits the protection by existing. Proven non-vacuous against the
exact sentence that slipped.

**Drift item 5 — High Guard "moderate body protection".** Verified and real. The
High Guard block asserted `moderate_body_protection` as a flat property while
`collision_model` gives `guard_high` only head, jaw and eyes, and `pose_geometry`
gives that posture a guard_body extent of 0.55 against a 0.6 threshold — the body
lane is **open**. The flat line quietly re-hardcoded what Decision 0010 made
emergent, and the opening is load-bearing: it is why "body shots pay off against a
high guard" falls out of posture data plus one threshold instead of being written
down as a rule. Resolved as reconciliation-log item 6, stating the extent and its
consequence rather than a verdict.

## Verified against HEAD — the items the other session could not read

**Item 4 — `docs/architecture/COMBAT_SYSTEM_ARCHITECTURE.md`.** Confirmed absent;
`docs/architecture/` does not exist at all. Note that the matchups doc words this
correctly and conditionally ("When `COMBAT_SYSTEM_ARCHITECTURE.md` exists, this
document feeds its guard/defense subsystem"). The overstatement is in the project
instructions, which call it "the umbrella" as though it were there.

**Item 7, repo half — the charter.** Confirmed: no file matching *charter* exists
anywhere in the repository. The charter lives only as a project doc, so references
to `project_charter.md` resolve to nothing on this side.

Neither is a repo defect to patch by creating an empty stub — that would trade a
missing file for a lying one. Both are cases of the project instructions
describing a layout the repository does not have.

## Not this session's to fix — the Director's, in claude.ai project settings

1. **The pinned "10 guards vs. 2 guard volumes" instruction** (drift item 3).
   Decision 0010 closed it on 2026-08-02, and the standing instruction still orders
   every review pass to raise it. It manufactured part of this report and will
   manufacture it again.
2. **The stale GitHub sync**, and the duplicate `boxing_guard_matchups.md` carried
   both as an uploaded project doc and as a synced repo path — drop the duplicate
   *after* the sync catches up, not before.
3. **The charter's document path**, literally `# Project Uppercut — Charter &
   Glossary` from the paste accident its repair tag records.
4. **The review task's own prompt**, which should tell future runs to treat the
   synced GitHub view as a dated snapshot and report differences as "project doc
   vs sync of *date*", never as repository state. That kills this whole failure
   mode at the source.

## Accepted, deferred, and named rather than dropped

- **Item 2** — "Decision 0010" and Decision 0007's queue item "D-10" are different
  things with colliding names. A footnote would save a future reader the stumble.
- **Item 6** — guard naming is not canonicalised: "Double Forearm / Ear-Muff" in
  the catalog vs "Ear-Muff" in the master tables, "Tight Elbow / Body Guard", and
  "shell" overloaded between High Guard/Basic Shell and the Philly shell.
- **Item 8** — the matchups doc says the exemplar names "stop at this file"; the
  charter carries them too and words the boundary correctly. One line to align.
- **Item 9** — two tag formats coexist. If that is deliberate (project-artifact
  tags vs repo tags), recording it in `CONTRIBUTION_TAGGING.md` stops it reading
  as drift.

These are content hygiene, not correctness, and they are held rather than done so
that slice item 9 — one rendered round with knockdown, count, stoppage and
decision — stays the next thing. The review agrees that is the focal point.

## The review's other three priorities, on the record

**A game-feel gate, Director-observed rather than automated.** Responsiveness,
visual speed, impact, readability, pacing, one comedy beat, boxing accuracy. The
review is right that the strongest current evidence proves simulation correctness
and not experience.

**Do not tune the Phase N guard-erosion finding yet — set the target first.**
Decide whether sustained blocked pressure should visibly weaken a guard within one
round, three, six, or only in long championship fights, and let the coefficient
follow that product decision rather than raising damage until the mechanism
becomes visible.

**Arcade personality should not wait for polish.** The first complete rendered
round should carry at least one comedic reaction, one crowd response, one
exaggerated but truthful impact, one announcer beat, one readable momentum change.
That tests whether the intended soul can coexist with the strict architecture —
which is a real question, not a decoration.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 21:05 UTC | END ] -->
