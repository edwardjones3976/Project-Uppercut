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


def test_the_decision_path_is_alive_but_for_the_wrong_reason():
    """THE FINDING, REWRITTEN 2026-08-06 — and the rewrite is the point.

    This test used to assert `decision == 0`: every swept seed ended by
    stoppage in round one, and the decision path had never executed. It failed
    the day Decision 0018 (gate G5) made the professional ruleset the default,
    because that rulebook has no three-knockdown rule and nothing stops the bout
    any more.

    The instruction the old docstring carried was "when this fails, the phase
    has been fixed — update the record rather than deleting this test." Half of
    that was right. The phase was not fixed. The LID came off:

        24 bouts, 3 rounds, professional rules:  24 of 24 reach the cards
                                                 22.89 knockdowns PER ROUND

    A fighter put down twenty-three times a round and rising each time is not a
    fixed fight. `decision_path_must_survive` is satisfied because nothing ends
    the bout, not because the fighters survive it — so the two things this file
    now holds are that the path is live AND that it is live for the wrong
    reason.

    When the second assertion fails, the conversion work has landed. THAT is
    when the Phase O record gets rewritten.
    """
    s = O.sweep(SWEEP)
    assert s["decision"] > 0, (
        "the decision path is dead again (%d of %d seeds reached the cards). "
        "Under the professional default nothing stops a bout on a knockdown "
        "count, so a stoppage now means a fighter failed the count - check "
        "whether the ruleset changed before assuming the fight did."
        % (s["decision"], s["seeds"]))
    stream = O.expected_stream(4242, 3, with_floats=False)
    f = dict(kv.split("=", 1) for kv in
             next(l for l in stream.splitlines()
                  if l.startswith("S|")).split("|")[1:])
    per_round = int(f["knockdowns"]) / max(1, int(f["rounds"]))
    assert per_round > 5.0, (
        "knockdowns per round is down to %.1f. If that is real, the conversion "
        "problem is fixed and this test, the Phase O record and the 2026-08-06 "
        "development log all need rewriting in the same commit." % per_round)


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


# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 22:10 UTC | edit: E rows ]
def test_the_terms_diagnostic_cannot_change_the_canonical_stream():
    """`with_terms=True` adds `E` rows and must change NOTHING else.

    The diagnostic exists because the conversion gap could not be decomposed
    without the pressure terms of eligible landings that did not convert. It is
    opt-in precisely so the stream a phase is judged by stays fixed - and that
    is worth asserting rather than trusting, because the first version leaked:
    the trailer's row count and self-hash both covered the E rows, so switching
    the diagnostic on silently changed two fields of the canonical output.
    """
    for seed, rounds in ((4242, 1), (4240, 3), (4255, 2)):
        plain = O.expected_stream(seed, rounds, with_floats=False)
        rich = O.expected_stream(seed, rounds, with_floats=False,
                                 with_terms=True)
        stripped = [l for l in rich.splitlines() if not l.startswith("E|")]
        assert stripped == plain.splitlines(), (
            "seed %d: with_terms changed a canonical row" % seed)
        assert any(l.startswith("E|") for l in rich.splitlines()), \
            "seed %d: with_terms emitted no E rows at all" % seed


def test_every_knockdown_has_a_terms_row_that_agrees_with_it():
    """The E rows and the K rows are two views of the same event, so where they
    overlap they must agree exactly - otherwise the diagnostic is describing a
    different fight from the one the phase records."""
    rich = O.expected_stream(4240, 3, with_floats=False, with_terms=True)
    ks, es = {}, {}
    for l in rich.splitlines():
        f = l.split("|")
        if f[0] == "K":
            ks[(int(f[1]), int(f[2]))] = int(f[4])
        elif f[0] == "E" and f[12] == "1":
            es[(int(f[1]), int(f[2]))] = int(f[5])
    assert ks, "no knockdowns in this stream to check against"
    assert set(ks) == set(es), "converted E rows and K rows disagree on which " \
                               "landings dropped a man"
    for k in ks:
        assert ks[k] == es[k], "pressure disagrees at %r: K=%d E=%d" % (
            k, ks[k], es[k])
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 21:40 UTC | END ]
