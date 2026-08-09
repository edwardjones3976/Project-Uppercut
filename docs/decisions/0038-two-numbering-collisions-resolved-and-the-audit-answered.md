<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 20:45 UTC | Decision 0038 start ] -->
# Decision 0038 — Two numbering collisions, resolved; and the external audit answered

**Status:** ACCEPTED (delegated).
**Authority:** the owner's standing in-session delegation, 2026-08-09.
**Occasion:** an external repository audit at `main` `1e434fed` (2026-08-08),
graded B / 84, whose recommended order of operations this decision executes.

## Why this exists

Work proceeded on two branches that could not see each other. The Director
recorded rulings against `main`; delegated implementation recorded rulings on
`wip/section-ownership-band-gate`. Both numbered their decisions from what they
could see. **Two collisions resulted, and neither was a disagreement about
substance — both were filing errors that would have become substance if merged
carelessly.**

## Collision 1 — two Decision 0032 files

`main` carried the Director's `0032-evasion-commitment-and-cadence-validity.md`.
The working branch, whose decision-drift test correctly reported that "Decision
0032" was cited everywhere and recorded nowhere *that it could see*, wrote a
transcription and filed it as `0032-evasion-commitment-and-the-lab-fence.md`.

**Ruling: the Director's file is the sole Decision 0032.** The transcription is
deleted. Its two additive passages — the round-three panel's six asks, and the
correction that Phase R already read evasion timing — are preserved as a clearly
fenced appendix beneath the Director's unaltered text.

**A citation correction falls out of it.** The codebase cites *"Decision 0032
§3"* for the lab fence. That section number came from the transcription's
layout; in the authoritative file the same rule is **Ruling 4**. Both name one
binding rule. **Ruling 4 is the authoritative reference.** Existing citations
stand rather than being rewritten across dozens of files; the appendix is the
map. New work cites Ruling 4.

## Collision 2 — two Decision 0034 files

The Director authored `0034-ruleset-authority-with-frozen-evidence`
(2026-08-08 21:16 -0700), explicitly *"Director refinement of Decision 0033
DD2."* Six hours later, delegated work authored a different 0034 without
knowledge of it.

**Ruling: the Director's 0034 keeps the number.** It is earlier in time, and it
is a refinement of 0033 — the sequence 0033 → 0034 is the record of an
argument, and breaking it to preserve a later file would destroy the only thing
the numbering is for. The three delegated decisions shift up:

| was | is | subject |
|---|---|---|
| 0034 | **0035** | the threshold is not the lever, volume is |
| 0035 | **0036** | the count was eating the round |
| 0036 | **0037** | the throw rate was never four times too much |

All references were rewritten mechanically and the result verified: decision
headers are contiguous 0001–0038, and the drift tests pass.

## The Director's 0034 was already satisfied — verified, not assumed

Decision 0034 reverses one implementation step of 0033 DD2: **do not physically
delete** `condition_model.knockdown.max_per_round` / `max_per_bout`, because
frozen Phases N and K depend on that file (Decision 0018). Checked against the
tree rather than taken on trust:

- `data/condition_model.json` **still contains both fields** (`3` and `4`) —
  Ruling 4 satisfied.
- `resolution.condition_pack()` **does not expose them**, so `IntegratedBout`
  cannot read them as authority, fallback or default — Ruling 2 satisfied.
- `tests/test_ruleset_is_declared.py` asserts both still equal the arcade
  ruleset's values — the "validator-bound historical echo" Ruling 4 requires.
- The frozen analyzers read them as `legacy_max_per_round` / `legacy_max_per_bout`,
  distinct from live ruleset authority — Ruling 1 satisfied.

Delegated implementation reached the Director's answer independently. That is
the outcome the delegation was for, and it is recorded here because "we happened
to agree" is only worth anything when someone checked.

## Disposition of the audit's seven recommendations

1. **PR #30 / Decision 0033 absent — resolved.** 0033 exists; the contiguity
   test passes. The audit was correct at its cutoff.
2. **PR #29 rebase — superseded.** `feat/phase-r-into-the-bout` is fully
   contained in the working branch (zero commits outside it). Nothing to rebase;
   the branch that lands supersedes it.
3. **Complete fight real on `main` — done by this merge**, with gates green on
   the exact merge result rather than on a branch tip that never met `main`.
4. **Stale control-plane docs — refreshed.** README decision index, STATUS,
   `SEE_AND_TEST.md`, `PROJECT_PLAN.md` archival banner, `CONTRIBUTING.md`
   branch convention.
5. **CI hardening and evidence integrity — actioned.** Recorded in Decision
   0039, authored in the same session under a section-ownership audit pass.
6. **Windows/Unreal verification lane — added**, addressing issue #14.
7. **Tuning — REFUSED, and this is the one to argue with.** The audit says to
   tune movement, accuracy, counters, knockdown frequency and cadence from
   multiple seeds once integration is stable. Multiple seeds is right and is
   already how this project measures. But **Decision 0032 Ruling 4 forbids
   fitting balance values from lab observation without an explicit Director
   disposition**, and three decisions (0034/0035 in the old numbering, 0037)
   have now refused the same threshold on evidence. Tuning is not blocked by
   engineering readiness; it is blocked by an authority gate that only the
   Director can open. **This decision does not open it.**

## The audit's central claim, tested against measurement

The audit's sharpest line is that the next grade improvement will not come from
more architecture. Decision 0037 reached the same place from inside, and the
numbers say where: volume is now inside a real round's band (58.7 thrown per
round against 40–70) and **accuracy is not** (55% connect against a real
30–35%). The named critical path is connect rate, which is a defence problem.

The audit's supporting figure — *"roughly 73% accuracy, seven knockdowns before
the second round ended, no authored counters"* — described one seed of a fight
that has since had the band gate unified, the guard extracted and wired in,
ruleset authority, the ten-point must corrected, and canon's repetition economy
read for the first time. **The conclusion survived the numbers changing under
it, which is why it is worth keeping.**
<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 20:45 UTC | Decision 0038 end ] -->
