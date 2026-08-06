# Director decision gates

A decision gate exists only while a bounded product, design, rules, or architecture choice awaits a Director ruling. Closing a gate does not claim that implementation is complete. Engineering follow-through belongs in GitHub issues and acceptance records.

## Current state

**No Director decision gate is open.**

| # | Gate | State | Authority | Engineering follow-through |
|---|---|---|---|---|
| G1 | Normal-step cost authority | **CLOSED** | Decisions 0014 and 0015 | Issue #9 |
| G2 | Rest and no-action semantics | **CLOSED** | Decisions 0014 and 0016 | Issues #9 and #12 |
| G3 | `aggression_bias` semantics | **CLOSED** | Decisions 0014 and 0017 | Issues #9 and #12 |
| G4 | Lateral guard geometry with simple controls | **CLOSED** | Decisions 0013, 0014, and 0018 | Deferred by trigger: after complete generic live bout, before named fighters |
| G5 | Default ruleset | **CLOSED** | Decisions 0014 and 0019 | Issues #9 and #12 |
| G6 | Guard values on the interception threshold | **CLOSED** | Decisions 0014 and 0020 | Issue #9: canon validator still required |
| G7 | Stamina economy cannot pay for a round of boxing | **CLOSED** | Decision 0021: Wind over Reserve | Issue #12 |

## Integrated-contract ruling

The former hidden architecture question inside “integrate the phases” is also decided:

- Decision 0022 creates a new integrated contract and named deterministic RNG substreams.
- Existing N/Q/R/S/O phase pins remain historical unit evidence.
- Integration does not re-bless those pins into pretending they were one fight.
- Commandlets, the live arena, replay, and later networking must consume the same authoritative runtime.

## Reopening rule

A closed gate may be reopened only when new evidence directly contradicts the accepted ruling or demonstrates that its stated product behavior cannot be achieved. Incomplete code, missing tests, or pending tuning are implementation work, not unresolved Director choices.

## Current implementation path

```text
Decisions 0021–0022
→ shared integrated C++ bout
→ Play-ready complete CPU contest
→ Director game-feel review
→ lateral guard geometry
→ Adewale vs. Calvin
```

See Issue #12 and `docs/implementation/integrated_contract_acceptance.md`.
