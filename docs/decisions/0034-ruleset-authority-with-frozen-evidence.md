# Decision 0034 — Ruleset authority with frozen historical evidence

**Status:** ACCEPTED — Director refinement of Decision 0033 DD2.

Decision 0033 correctly makes the selected ruleset the exclusive authority for the live contest. One implementation step is changed: do **not** physically delete `condition_model.knockdown.max_per_round` or `max_per_bout` during First Bell ruleset wiring.

Decision 0018 deliberately preserved those fields because frozen Phases N and K depend on the condition file. They are mechanically checked echoes of the arcade ruleset, not live authority.

## Binding ruling

1. `data/rulesets/*` exclusively governs live contest rules.
2. `IntegratedBout` must never read the legacy condition limits as authority, fallback, or default.
3. `null` in the selected ruleset means that mechanism is inactive.
4. Keep the two legacy condition fields physically present only as validator-bound historical echoes for frozen N/K evidence.
5. Physical deletion requires a later explicit evidence-migration decision.
6. Decision 0033 otherwise stands: professional is the generic default; arcade remains selectable; the selected ruleset id, version, and semantic identity enter the integrated contract/header; contradictory ruleset data fails closed; and an authored knockdown limit stops the bout on the Nth knockdown.
7. DD1, DD3, and DD4 stand unchanged.
8. DD5 remains provisional: `pressed × landed` may be used temporarily, but must be re-evaluated after `thrown` exists and before judging/verdict evidence is pinned.

## Stop conditions

Stop and diagnose if live ruleset wiring moves frozen N/K authoritative event rows, if live code reads the legacy echoes, if a null professional limit silently becomes a default limit, or if a replay cannot identify the ruleset it actually used.
