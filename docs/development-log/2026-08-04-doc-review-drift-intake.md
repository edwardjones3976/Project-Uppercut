<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 20:04 UTC | START ] -->

# Doc-review drift intake — 9 items reported, one root cause

A review pass reported 9 drift items across the two project docs and the synced
repo, flagging two for a Director call: a "stale repo copy" of
`docs/design/boxing_guard_matchups.md` still carrying a contradiction the
reconciliation log marks resolved, and a "missing" Decision 0010.

**Both are real observations and both diagnoses are inverted. No repo edit is
warranted, and making one would be actively harmful.**

## What the repository actually contains

`docs/design/boxing_guard_matchups.md` is current at 746 lines. It carries the
2026-08-03 06:31 UTC amendment that softened the "wrong by construction" clause,
and its reconciliation log runs to **five** items — including item 4, the Philly
shell versus the overhand, resolved across all four locations that disagreed.
Commit `cca155e`, 2026-08-02 23:38.

Decision 0010 exists: `docs/decisions/0010-guard-postures-as-coverage-extents.md`,
alongside 0011 (target-region taxonomy) and 0012 (C++ fight core and slice freeze).

Local `HEAD` equals `origin/main` at `35b2d9d`, nothing unpushed.

## The actual defect: the project's GitHub sync is stale

The project knowledge holds a snapshot taken on 2026-08-03 somewhere between
05:33 and 06:31 UTC. The evidence is exact: the synced copy contains the 05:33
edit and not the 06:31 amendment, and its reconciliation log stops at item 3 with
the older preamble ("Two source references disagreed on points below").

**27 commits have landed since.** Everything in them is invisible to anything
reading the project's synced view — Decisions 0010, 0011 and 0012; the entire C++
fight core (Phases H through N); the Judge subsystem and referee consumption; every
asset audit; the mannequin visual pass; the arena import.

So a reviewer comparing the *uploaded project doc* (current) against the *synced
repo path* (stale) sees a real difference and correctly calls it drift. The
difference is real. Its cause is snapshot age, not repository content.

## Why "fixing" this in the repo would have been the wrong move

The reported contradiction is the shell-versus-overhand conflict, and the
resolution is deliberate: a shell `guard_alignment_state`
{roll_timed_aligned, roll_late_or_misaligned}, because a timed roll turns the
overhand off the shoulder and a late one lets it arc over. The log says in terms:
*do not flatten it back to a single verdict in either direction.* Editing the repo
to match a two-day-old snapshot would have re-opened a resolved design call by
reverting to the older text — the precise failure the reconciliation log exists to
prevent, arriving through a review rather than through an edit.

## Two structural fixes, both outside the repo

**1. The project carries two copies of the same document.** `boxing_guard_matchups.md`
is uploaded as a project doc *and* synced as `docs/design/boxing_guard_matchups.md`.
That duplication is what let a reviewer diff two versions of one file and conclude
the repo had drifted. Once the sync catches up, the uploaded duplicate should be
removed so the synced repo path is the single source. **Not before** — right now
the uploaded copy is the only current one in the project.

**2. The project instructions are themselves stale, and will keep generating this
report.** They read: *"Known drift: pinned execution plan flags '10 guards vs. 2
guard volumes need reconciling.' Surface this in any doc-review pass."* That drift
was closed by Decision 0010 on 2026-08-02 — ten postures resolve as coverage-extent
modulation over the same two volumes, and `cca155e`'s own message records the
closure. A standing instruction to surface a resolved item guarantees every future
review re-raises it, which is likely one of the nine reported here. The instruction
should be updated to point at Decision 0010 as the closure.

## Status of the other seven

Not assessed — the full list was said to be sent by notification and did not reach
this session. Given that one snapshot age explains both flagged items and 27
commits of invisibility, the working hypothesis is that most or all of the
remainder share it. Each should still be read individually against the repository
rather than assumed; that is a short job once the list is in hand.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 20:04 UTC | END ] -->
