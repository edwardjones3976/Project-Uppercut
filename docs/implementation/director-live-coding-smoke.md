<!-- [ Claude (Claude Code) | Director routine DIR-7FF9D2700F | 2026-08-16 06:34 UTC | START ] -->

# Director live-coding smoke

A smoke test of the Director's three-model loop, run end to end on a change small
enough that nothing about the result is ambiguous. The point is not the document
it produces — this file *is* that document — but whether three providers can hand
work to each other and leave behind evidence a reviewer can check without
trusting any of them.

This file is documentation only. It changes no gameplay, source, configuration or
canon, and it asserts nothing about any phase's evidence.

## The three-model contract

Three providers, three roles, and the separation is the whole design: the model
that decides what "done" means never writes the change, and the model that
reviews it never wrote it either.

| Provider | Role | Writes? |
|---|---|---|
| **OpenAI** | Plans the assignment, and performs **final acceptance** against the acceptance checks. | No |
| **Claude** | Makes the **sole scoped change** and opens the **draft PR**. Exactly one branch, exactly one PR. | Yes — the one change |
| **Cursor** | **Independently reviews the exact PR-head SHA**, read-only. | No |

Three properties make this more than a relay:

- **One writer.** Claude is the only provider that produces a commit, a branch or
  a PR. If a second provider writes, the loop has failed regardless of the
  outcome, because no one can any longer say which change came from where.
- **The review is pinned to a SHA, not to a branch.** Cursor reviews a named head
  commit. A branch is a moving pointer; a review of "the branch" is a review of
  whatever it happened to contain at read time, which is not a reviewable claim.
  The SHA under review appears verbatim in the evidence.
- **Acceptance does not merge.** OpenAI's final acceptance is a judgement about
  whether the acceptance checks are met. It is not a merge, and the loop leaves
  the PR in draft. Merging is an owner action, outside this loop.

This mirrors the rule the rest of the repository already runs on: a harness may
explore, only the contract may conclude. Here the acceptance checks are the
contract, and no provider grades its own work.

## Required evidence fields

Every run records all of the following. These are the fields a reviewer needs to
reconstruct the run without re-running it.

| Field | What it pins |
|---|---|
| Repository | Which repository was touched |
| Base ref | What the branch was cut from |
| Branch | The one isolated topic branch |
| Head commit SHA | The exact reviewed revision — full SHA, not abbreviated |
| Draft PR URL and state | Where the change is, and that it is still draft and unmerged |
| Changed-file list | Every tracked path added, modified or deleted |
| CI check names and states | Named checks, with the state each was in |
| Provider run IDs | One per provider, so each leg is traceable to its own log |
| UTC start and end timestamps | When the run began and ended, 24h UTC |
| Duration | Wall-clock elapsed |
| Token and cost telemetry | **Actual** measured usage, when the provider exposes it |

### Unavailable values are labeled, never inferred

This is the field's own rule and it is not a formality. Any value a provider does
not expose is written as **`unavailable`**, with a short note saying why —
`unavailable: provider does not expose per-run token counts`, or
`unavailable: CI had not reported as of <UTC timestamp>`.

An unavailable value is never estimated, back-calculated from a price list,
carried over from a previous run, or replaced with a plausible number. A recorded
estimate is indistinguishable from a measurement once it is written down, and
"telemetry unavailable" is a true statement about the run where an invented
figure is a false one. The same applies to CI: a check that has not reported is
`pending` observed at a stated UTC timestamp, not a predicted pass.

CI states in particular are a snapshot. Record the timestamp at which they were
observed, because they change after the observation and the record must not
silently claim otherwise.

## Rollback: close without merge

The smoke test leaves exactly one branch and one draft PR behind. Rolling it back
removes both, and touches nothing else — no revert commit is needed, because
nothing was merged.

**These steps are for an authorized owner. The automated loop does not execute
them.** Providers in this loop have no authority to close a PR or delete a
branch; the instructions exist so that a human who wants the artifacts gone knows
exactly what to remove.

1. **Close the draft PR without merging.** Open the PR and use *Close pull
   request*. Do not merge it, and do not squash-merge it — the change carries no
   value worth landing, and a merge would put a documentation file on `main`
   under the impression that a smoke test called for it.
2. **Delete the topic branch, if you want it gone.** After the PR is closed,
   delete the branch from the PR page, or:

       git push origin --delete <branch>
       git branch -D <branch>          # local copy, if one exists

   Keeping the branch is also fine — it is isolated from `main` and costs
   nothing. Delete it only if you would rather the repository not carry it.

Nothing else needs undoing: `main` was never written to, no tags or releases were
created, no credentials or permissions were altered, and no other remote ref
exists.

<!-- [ Claude (Claude Code) | Director routine DIR-7FF9D2700F | 2026-08-16 06:34 UTC | END ] -->
