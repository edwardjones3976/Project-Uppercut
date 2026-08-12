# [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 02:53 UTC | START ]
"""The Unreal 1-round test pairing must be unique on expressed attributes."""
from __future__ import annotations
from tools.uppercut_validate import fighter_pair as FP
from tools.uppercut_validate import attributes, budget
from tools.uppercut_validate import strict_json as json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def test_default_pair_files_exist():
    for fid in FP.DEFAULT_PAIR:
        path = REPO / "fixtures" / "fighters" / "legal" / f"{fid}.json"
        assert path.is_file(), path


def test_default_pair_each_card_is_rule10_legal_and_budget_complete():
    families = attributes.load_families()
    cfg = budget.load_config()
    tax = budget.taxonomy_keys()
    for fid in FP.DEFAULT_PAIR:
        card = FP.load_fighter(fid)
        rep = attributes.validate_fighter(card, families)
        assert rep.legal, [str(v) for v in rep.violations]
        assert set(card["attributes"]) == tax
        net = budget.profile(card["attributes"], refund_rate=cfg["refund_rate"])[
            cfg["curve"]
        ]["net"]
        assert net <= cfg["cap"], (fid, net, cfg["cap"])


def test_default_pair_is_unique_on_expressed_in_round_attrs():
    errs = FP.validate_default_pair()
    assert errs == [], errs
    a = FP.load_fighter(FP.DEFAULT_PAIR[0])
    b = FP.load_fighter(FP.DEFAULT_PAIR[1])
    diffs = FP.expressed_diffs(a, b)
    assert len(diffs) >= FP.DEFAULT_MIN_KEYS


def test_identical_cards_fail_pair_uniqueness():
    a = FP.load_fighter(FP.DEFAULT_PAIR[0])
    errs = FP.validate_pair(a, a)
    assert errs
# [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 02:53 UTC | END ]
