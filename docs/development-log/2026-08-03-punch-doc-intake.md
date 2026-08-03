<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 07:26 UTC | START ] -->

# Punch-doc intake — PR history and source-filtering record (2026-08-03)

## Pull request history

- **PR #2** — "Add boxing punch, target, angle, and guard matchup reference", branch
  `docs/boxing-punch-guard-reference`. Two files: the new design reference plus a `README.md` edit.
  Opened while Phase 1A step 6 was in flight and reported merge conflicts, caused by the README
  status-block edits in `8461a97`, `cca155e` and `77b4810` the same morning. **Closed, superseded.**
- **PR #3** — branch `docs/boxing-punch-guard-reference-v2`, single file, 813 additions. Merged as
  `524df30`. The README change was dropped in the rework, which is why the status block survived
  intact and why the new document was not linked from the README until this commit.

Recorded because an unexplained conflicted PR in the history is the kind of gap that later reads as
something hidden. Nothing was hidden; the conflict was ordinary and the rework resolved it.

## Source filtering — the part worth keeping

The source material behind the document contained three claims that contradict logged reconciliation
calls in `docs/design/boxing_guard_matchups.md`. **The merged document did not ingest any of them**,
which is the outcome the reconciliation log exists to produce. Verified by search against `524df30`:

| Source claim | Canon | Present in merged doc? |
|---|---|---|
| Cross-arm forearms "completely block the vertical center line, making it impossible for the uppercut to land flush" | Reconciliation item 1, mechanized by Decision 0010: conditional on bar alignment | **No.** Zero occurrences of "impossible" or "completely block". The doc instead states the path-not-target rule correctly and lists cross-arm as vulnerable to an "uppercut through seam". |
| Long guard "smothering the overhand" against the bicep | Canon resolves the other way: the overhand looping over the extended arm is the long guard's signature vulnerability | **No.** The only "smother" is the forearm frame against short hooks. The overhand row places long guard in the challenged column. |
| Philly shell as a best anti-jab guard via lead-hand parry | Canon: the shell is a weaker jab answer in every table — the lead hand is down | **Partially.** The shell appeared as a *conditional* answer rather than a challenged one. Corrected on intake to challenged, with skill-gated mitigation noted. |

An "impossible to land flush" claim would also have been structurally illegal in spirit:
`move.schema.json` prohibits `unblockable_by_design`, and a guard that makes a legal punch impossible
is the defensive mirror of that. Counterplay runs in both directions.

## Intake actions taken on `524df30`

All additive; the original author's body text is unmodified and the file arrived with no tags to
conflict with.

- Contribution tags and a Rule 18 status header added (the file arrived without either, contrary to
  Decision 0006 and `CONTRIBUTION_TAGGING.md`).
- **Table authority note.** Section 5 duplicates matchup content that `boxing_guard_matchups.md`
  owns and reconciles. Two live copies of a reconciled table is this project's signature failure
  mode — the shell-versus-overhand contradiction propagated across four locations exactly this way.
  The guard doc is named authoritative; section 5 is a reading aid.
- **Canonical region mapping.** The document's `intended_target_region` vocabulary (temple, cheek,
  nose, forehead, sternum, solar plexus, liver, ribs, guard_arm) is finer-grained than the eight
  strikeable regions in `data/condition_regions.json`, and the collision validator rejects any move
  targeting a region without a hurtbox. The mapping is now stated in-doc, with two gaps flagged
  rather than silently bridged: the canonical `eye_left` / `eye_right` regions have no counterpart
  in the finer vocabulary, and the collarbone is a mistarget outcome rather than a region.
- **Shell-versus-jab row** aligned to canon (above).

## Move-table catch-up

The document treated the overhand as a first-class punch family while `generic_sandbox_moves.json`
had no `overhand_*` entry at all — and the step-6 punch validator named `overhand` in its offensive
category set, so both documents were referencing a punch the table did not have. `overhand_rear` is
now authored as a tuning hypothesis: 11 startup, 3 active, 21 recovery, mid band, 3.2 stamina,
`blockable_high`, the highest counter vulnerability in the generic set because the looping path
telegraphs and the head travels forward with it.

The animation frame-lock caught this immediately and correctly: adding the move failed
`move_frame_lock_rule13` with "move 'overhand_rear' has no animation" until `anim_overhand_rear`
landed at matching ticks. That cross-file lock did exactly the job it was built for.

## Still open

- **Taxonomy decision (Director).** Whether the finer target vocabulary is promoted into
  `condition_regions.json` — which would mean new hurtboxes — or stays design prose that maps down to
  the eight canonical regions. Until ruled, the mapping note holds the line.
- **Fouls.** Illegal-target content did land (back of head, neck, spine, kidneys, groin, below belt,
  downed opponent), along with a validator-requirements section and a prohibition on a fixed
  left/right liver target that ignores stance. No referee profile consumes it yet; that arrives with
  the referee behavioural depth in a later phase.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 07:26 UTC | END ] -->
