# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 07:40 UTC | START ]
"""Phase L analyzer, mutation-proven before the C++ guard-and-slip exists."""
import importlib.util
import os

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.join(HERE, "..", "tools", "engine", "analyze_core_guard.py")
spec = importlib.util.spec_from_file_location("analyze_core_guard", MOD)
acg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(acg)

SEED, TICKS = 4242, 5400


def _write(tmp_path, text):
    p = tmp_path / "markers.txt"
    p.write_text(text, encoding="utf-8")
    return str(p)


def test_canon_is_coherent_and_the_pair_mirrors():
    c = acg.canon_pack()
    assert c["canon_errors"] == []
    assert c["posture"]["high_guard"]["covered_free"] == frozenset({"high"})
    assert c["posture"]["tight_elbow"]["covered_free"] == frozenset({"low"})
    assert not c["posture"]["high_guard"]["covered_committed"]


def test_a_clean_stream_passes_with_all_four_outcomes(tmp_path):
    s = acg.expected_stream(SEED, TICKS)
    rep = acg.analyse(_write(tmp_path, s))
    assert rep["ok"], rep["errors"]
    results = {l.split("|")[4] for l in s.splitlines() if l.startswith("P|")}
    assert {"blocked", "landed", "whiffed", "dodged"} <= results


def test_seeds_reproduce_and_differ():
    assert acg.expected_stream(SEED, TICKS) == acg.expected_stream(SEED, TICKS)
    assert acg.expected_stream(SEED, TICKS) != acg.expected_stream(SEED + 1, TICKS)


def test_a_dodge_of_a_body_punch_is_caught(tmp_path):
    s = acg.expected_stream(SEED, TICKS)
    s = s.replace("|body_straight_rear|landed|torso_upper|",
                  "|body_straight_rear|dodged|-|", 1)
    rep = acg.analyse(_write(tmp_path, s))
    assert any("vacates the head" in e or "diverges" in e for e in rep["errors"])


def test_a_missing_counter_window_is_caught(tmp_path):
    """Strip the 'c' flag from every landed punch: the counter law must object."""
    s = acg.expected_stream(SEED, TICKS).splitlines()
    out = []
    for l in s:
        if l.startswith("P|") and "|landed|" in l:
            p = l.split("|")
            p[10] = p[10].replace("c", "")
            l = "|".join(p)
        out.append(l)
    rep = acg.analyse(_write(tmp_path, "\n".join(out) + "\n"))
    assert any("counter window is untested" in e or "diverges" in e
               for e in rep["errors"])


def test_a_tampered_posture_column_is_caught(tmp_path):
    s = acg.expected_stream(SEED, TICKS).splitlines()
    i = next(n for n, l in enumerate(s) if l.startswith("D|") and "|t|" in l)
    s[i] = s[i].replace("|t|", "|h|", 1)
    rep = acg.analyse(_write(tmp_path, "\n".join(s) + "\n"))
    assert not rep["ok"]


def test_a_wrong_guard_canon_hash_is_caught(tmp_path):
    s = acg.expected_stream(SEED, TICKS)
    line = next(l for l in s.splitlines() if l.startswith("H|canon_guard="))
    s = s.replace(line, "H|canon_guard=" + "0" * 64)
    rep = acg.analyse(_write(tmp_path, s))
    assert any("canon_guard" in e for e in rep["errors"])
# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 07:40 UTC | END ]
