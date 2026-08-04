# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 21:40 UTC | START ]
"""Phase O analyzer - and the finding that stopped the phase before the C++.

The contract for slice item 9 was written first, as every phase is. It then
refused its own stream: with Phase N's named simplification in force - every
landing graded `solid` - the knockdown pressure formula fires so often that
100% of swept seeds end by stoppage inside round one, and canon's
`decision_path_must_survive: true` is dead.

That is not a bug in the contract. It is the contract doing its job: the
simplification was harmless in Phase N, where grading only fed accumulation, and
becomes decisive in Phase O, where it feeds knockdown pressure. Canon's 0.57
threshold was swept against the reference model, where most landings are brushed
or grazed and carry a fraction of solid force. Grade everything solid and the
threshold is not a line, it is a floor.

So the tests below assert the finding as it stands. When contact-quality grading
lands and the decision path revives, `test_the_decision_path_is_currently_dead`
FAILS - deliberately - and forces this record to be rewritten rather than
quietly outgrown.
"""
import io
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(
    __file__))), "tools", "engine"))
import analyze_core_round as O  # noqa: E402

SEED, ROUNDS = 4242, 3
SWEEP = range(4240, 4264)


@pytest.fixture(scope="module")
def stream() -> str:
    return O.expected_stream(SEED, ROUNDS)


def _write(tmp_path, text: str) -> str:
    p = os.path.join(str(tmp_path), "markers.txt")
    io.open(p, "w", encoding="utf-8", newline="\n").write(text)
    return p


def test_canon_supports_the_phase():
    assert O.canon_pack()["canon_errors"] == []


def test_the_honest_stream_passes(tmp_path, stream):
    rep = O.analyse(_write(tmp_path, stream))
    assert rep["ok"], rep["errors"]


def test_canon_still_requires_the_decision_path_to_survive():
    """The invariant the finding is measured against. If canon ever drops this,
    the finding stops being a defect and becomes a design choice - and that
    should be a deliberate edit, not a silent one."""
    import json
    cm = json.load(io.open(os.path.join(O.REPO, "data", "condition_model.json"),
                           encoding="utf-8"))
    assert cm["knockdown"]["decision_path_must_survive"] is True


def test_the_decision_path_is_currently_dead():
    """THE FINDING. Every swept seed ends by stoppage in round one.

    When this fails, the phase has been fixed - update the record in
    docs/phase1a/determinism_probe_results.md rather than deleting this test."""
    s = O.sweep(SWEEP)
    assert s["decision"] == 0, (
        "the decision path has revived (%d of %d seeds) - rewrite the Phase O "
        "finding" % (s["decision"], s["seeds"]))
    assert s["stopped_in_round_1"] == s["seeds"]


def test_no_knockdown_fires_below_the_canon_threshold(stream):
    c = O.canon_pack()
    ks = [l.split("|") for l in stream.splitlines() if l.startswith("K|")]
    assert ks, "the sweep says every bout ends early; this one has no knockdown"
    for k in ks:
        assert int(k[4]) >= int(k[5]) == c["kd_threshold"]


def test_knockdowns_only_come_from_knockdown_regions(stream):
    c = O.canon_pack()
    for k in [l.split("|") for l in stream.splitlines() if l.startswith("K|")]:
        assert c["moves"][k[3]]["region"] in c["kd_regions"]


def test_a_knockdown_below_threshold_is_caught(tmp_path, stream):
    lines = stream.splitlines()
    for n, l in enumerate(lines):
        if l.startswith("K|"):
            f = l.split("|")
            f[4] = str(int(f[5]) - 1)
            lines[n] = "|".join(f)
            break
    assert not O.analyse(_write(tmp_path, "\n".join(lines) + "\n"))["ok"]


def test_a_verdict_that_contradicts_the_cards_is_caught(tmp_path):
    """Force a decision stream by asking for the cards to disagree with it."""
    s = O.expected_stream(SEED, ROUNDS)
    lines = s.splitlines()
    for n, l in enumerate(lines):
        if l.startswith("V|"):
            f = l.split("|")
            f[1], f[2], f[5], f[6] = "decision", "a", "20", "30"
            lines[n] = "|".join(f)
            break
    assert not O.analyse(_write(tmp_path, "\n".join(lines) + "\n"))["ok"]


def test_a_missing_verdict_is_caught(tmp_path, stream):
    lines = [l for l in stream.splitlines() if not l.startswith("V|")]
    assert not O.analyse(_write(tmp_path, "\n".join(lines) + "\n"))["ok"]


def test_the_trailer_hash_covers_the_knockdown_rows(tmp_path, stream):
    lines = [l for l in stream.splitlines() if not l.startswith("K|")]
    assert not O.analyse(_write(tmp_path, "\n".join(lines) + "\n"))["ok"]


def test_the_count_is_the_canon_count():
    """Rule 16: officiating philosophy never touches the count arithmetic."""
    c = O.canon_pack()
    assert c["count_ticks"] == 480, "eight seconds at 60 ticks"


def test_relief_is_partial_not_a_fresh_fighter():
    c = O.canon_pack()
    assert 0 < c["cond_relief"] < 10000
    assert 0 < c["stam_relief"] < 10000
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 21:40 UTC | END ]
