# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 11:44 UTC | START ]
"""The declared-but-inert check, held to the same standard it imposes.

This checker exists because three separate passes over this repository each
found a major inert mechanism by accident. A checker written for that reason
had better fail when the thing it is looking for is present, so every test
below plants one and asserts it is caught.
"""
from __future__ import annotations
import copy

from tools.uppercut_validate import coverage as cov

CANON = cov.load()


def _mut():
    return copy.deepcopy(CANON)


def test_canonical_data_passes_every_check():
    assert cov.run_all(CANON) == []


def test_every_simulated_file_carries_a_registry_with_a_reason():
    for name, doc in CANON.items():
        block = doc.get("reference_model_coverage")
        assert block is not None, f"{name} declares no coverage registry"
        assert len(block["reason"]) > 40, f"{name}'s registry reason is not a reason"


def test_an_inert_key_is_caught():
    """The whole point. A new mechanical key nothing executes must fail."""
    d = _mut()
    d["punch_model.json"]["invented_mechanism_nothing_reads"] = 0.5
    errs = cov.check_no_inert_canon(d)
    assert any("invented_mechanism_nothing_reads" in e for e in errs)


def test_removing_a_key_from_the_registry_is_caught():
    """Deleting the registry entry does not make the debt go away."""
    d = _mut()
    reg = d["movement_model.json"]["reference_model_coverage"]["not_yet_expressed"]
    dropped = reg.pop()
    errs = cov.check_no_inert_canon(d)
    assert any(f"'{dropped}'" in e for e in errs)


def test_the_registry_may_not_claim_credit_for_executed_canon():
    """Listing something as unexpressed while the bout runs it is the failure
    that flatters - the list would understate what works and, worse, would be
    consulted as if it were accurate."""
    d = _mut()
    d["punch_model.json"]["reference_model_coverage"]["not_yet_expressed"].append("chaining")
    errs = cov.check_registry_is_honest(d)
    assert any("flattering direction" in e for e in errs)


def test_a_dead_registry_entry_is_caught():
    d = _mut()
    d["crowd_model.json"]["reference_model_coverage"]["not_yet_expressed"].append(
        "key_this_file_never_declares")
    errs = cov.check_registry_is_honest(d)
    assert any("dead entry" in e for e in errs)


def test_a_per_second_rate_wearing_a_per_tick_name_is_caught():
    """The 2026-08-03 stamina defect, replanted. 0.09/tick refilled the pool
    roughly ten times per round and survived two steps because a CPU policy was
    capping volume by refusing inputs, so the economy never bound anything."""
    d = _mut()
    d["condition_model.json"]["stamina"]["regen_per_tick_idle"] = 0.09
    errs = cov.check_rates_are_per_tick(d)
    assert any("per-second rate wearing a per-tick name" in e for e in errs)


def test_an_unaffordable_guard_is_caught():
    d = _mut()
    d["guard_evasion_model.json"]["postures"][0]["stamina_per_tick"] = 0.05
    errs = cov.check_rates_are_per_tick(d)
    assert any("more than a fighter has" in e for e in errs)


def test_a_bar_that_evaporates_is_caught():
    d = _mut()
    d["crowd_model.json"]["bar"]["decay_per_tick_idle"] = 0.012
    errs = cov.check_rates_are_per_tick(d)
    assert any("evaporate" in e for e in errs)


def test_the_scope_list_is_deliberate():
    """A file leaving SIMULATED is a design decision, not a way to silence the
    checker, so the set is asserted rather than trusted."""
    assert cov.SIMULATED == {
        "punch_model.json", "collision_model.json", "condition_model.json",
        "guard_evasion_model.json", "crowd_model.json", "movement_model.json",
        "combat_states.json", "ability_model.json",
        # Added 2026-08-03. attribute_effects entered scope when attributes entered
        # the bout; before that the attribute files sat outside this checker while
        # carrying exactly the inert-mechanism defect it exists to catch. This test
        # failing on a scope change is the intended behaviour - widening or narrowing
        # the set is a design decision, so it has to be restated here on purpose.
        "attribute_effects.json",
        # [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 02:13 UTC | START edit ]
        # Added 2026-08-04. referee_semantics entered scope when the bout began
        # consuming officiating profiles (Decision 0012 slice item 2) - restated
        # here on purpose, per this test's own rule.
        "referee_semantics.json",
        # [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 02:13 UTC | END edit ]
    }
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 11:44 UTC | END ]
