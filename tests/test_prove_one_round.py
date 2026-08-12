# [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 02:53 UTC | START ]
"""1-round integrated bout with unique cards must end like boxing."""
from tools.engine import prove_one_round as P


def test_prove_one_round_default_seeds():
    assert P.main(["--seeds", "4242,777", "--round-seconds", "180"]) == 0


def test_run_one_carries_cards():
    r = P.run_one(4242, round_seconds=60)
    assert r["result"]
    assert all(a.get("_card_id") for a in r["cards"].values())
# [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 02:53 UTC | END ]
