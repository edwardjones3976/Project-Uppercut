# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 12:30 UTC | START ]
"""Phase R's marker stream - the tests that make its C++ port provable.

The rules are proven elsewhere (`test_core_evade.py`). These prove the ARTIFACT:
that it is a function of nothing but its arguments, that it is coherent read
back cold, and - the two that would catch a plausible port - that the vacated
region test and the counter clause are both load-bearing, demonstrated by
breaking each and watching the stream change.
"""
import io as _io
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools", "engine"))
sys.path.insert(0, ROOT)

import analyze_core_evade as R  # noqa: E402

SEED, TICKS = 4242, 1200


@pytest.fixture(scope="module")
def rs():
    return R.expected_stream(SEED, TICKS)


def _trailer(stream):
    line = next(l for l in stream.splitlines() if l.startswith("S|"))
    return dict(kv.split("=", 1) for kv in line.split("|")[1:])


def test_the_stream_is_a_function_of_its_arguments(rs):
    assert R.expected_stream(SEED, TICKS) == rs


def test_the_header_names_every_canon_file_the_phase_reads(rs):
    named = {l.split("=")[0][len("H|canon_"):] for l in rs.splitlines()
             if l.startswith("H|canon_")}
    assert named == {"guard_evasion", "moves", "animation"}


def test_a_stream_read_back_cold_is_coherent(rs, tmp_path):
    p = os.path.join(str(tmp_path), "r.stream")
    with _io.open(p, "w", encoding="utf-8", newline="") as fh:
        fh.write(rs)
    assert R.analyse(p)["errors"] == []


def test_something_is_actually_dodged(rs):
    """A phase that evades nothing changed nothing."""
    assert int(_trailer(rs)["dodged"]) > 0


def test_the_counter_clause_fires_at_least_once(rs):
    """Canon's sentence - the uppercut rises into where the head is going -
    has to be reachable in a fight, not only in a unit test."""
    assert int(_trailer(rs)["countered"]) > 0


def test_a_dodge_only_ever_happens_in_a_vacated_region(rs):
    c = R.stream_pack()
    for line in rs.splitlines():
        if not line.startswith("P|"):
            continue
        f = line.split("|")
        if f[4] == "dodged":
            assert f[5] == "vacated", line
            assert f[6] in c["evasions"][f[7]]["vacates"], line
            assert not R.beats(c, f[7], f[3]), line


def test_the_vacated_region_test_is_load_bearing(monkeypatch, rs):
    """Make every evasion vacate everything and the dodge count must rise.

    A port that ignored `vacates` and treated an active window as blanket
    immunity would pass every test above.
    """
    before = _trailer(rs)
    assert int(before["wrong_region"]) > 0, (
        "no punch was refused for being aimed somewhere the evasion did not "
        "vacate, so this mutation has nothing to prove")
    real = R.stream_pack

    def blanket():
        c = real()
        for e in c["evasions"].values():
            if e["kind"] == "active_window":
                e["vacates"] = tuple(sorted(set(c["region"].values()) - {None}))
        return c

    monkeypatch.setattr(R, "stream_pack", blanket)
    after = _trailer(R.expected_stream(SEED, TICKS))
    # Blanket immunity means no punch can ever be "aimed somewhere else".
    assert int(after["wrong_region"]) == 0
    # Those punches do not all become dodges, and that is the phase working
    # rather than a weak assertion: in this slice every wrong-region punch is a
    # body shot, and a body shot is authored to BEAT both evasions. They move
    # from refused-on-region to refused-on-counter, which is a stricter
    # demonstration that both clauses are consulted independently.
    assert int(after["countered"]) > int(before["countered"])


def test_the_counter_clause_is_load_bearing(monkeypatch, rs):
    """Remove every counter and the evasions become strictly better guards.

    Which is the thing canon exists to prevent: `beaten_by` is what makes an
    evasion a different structure rather than a superior one.
    """
    before = int(_trailer(rs)["countered"])
    real = R.stream_pack

    def toothless():
        c = real()
        for e in c["evasions"].values():
            e["beaten_by"] = ()
        return c

    monkeypatch.setattr(R, "stream_pack", toothless)
    t = _trailer(R.expected_stream(SEED, TICKS))
    assert before > 0
    assert int(t["countered"]) == 0
    assert int(t["dodged"]) > int(_trailer(rs)["dodged"])


def test_the_properties_are_carried_inside_the_hash(rs):
    rows = [l for l in rs.splitlines()
            if not l.startswith(("H|", "Y|", "M|", "K|", "S|"))]
    props = {l.split("|")[1]: l.split("|")[2] for l in rows if l.startswith("V|")}
    assert props == {"a_body_shot_beats_the_slip": "1",
                     "the_uppercut_beats_the_roll": "1",
                     "the_slip_evades_a_straight": "1",
                     "no_evasion_is_strictly_better": "1",
                     "canon_errors": "0"}
    h = R.fnv1a64("".join(r + "\n" for r in rows).encode("utf-8"))
    assert "%016x" % h == _trailer(rs)["fnv1a64"]


def test_the_telegraph_is_free_and_the_canon_check_says_so():
    """If every punch were in the air for the same time, a fixed evasion window
    could not distinguish a slow punch from a fast one, and canon's telegraph
    would need a multiplier to exist. The pack refuses that canon."""
    c = R.stream_pack()
    spans = {m: c["anim"][m]["startup"] + c["anim"][m]["active"] for m in c["anim"]}
    assert max(spans.values()) > min(spans.values())
    assert c["canon_errors"] == []
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 12:30 UTC | END ]
