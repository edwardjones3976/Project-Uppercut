# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 05:45 UTC | START ]
"""Phase J analyzer, mutation-proven before the C++ sweep exists to judge."""
import importlib.util
import os

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.join(HERE, "..", "tools", "engine", "analyze_core_sweep.py")
spec = importlib.util.spec_from_file_location("analyze_core_sweep", MOD)
acs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(acs)

SEED, TICKS = 4242, 5400


def _write(tmp_path, text):
    p = tmp_path / "markers.txt"
    p.write_text(text, encoding="utf-8")
    return str(p)


def test_canon_is_coherent_and_the_lanes_split():
    c = acs.canon_pack()
    assert c["canon_errors"] == []
    assert c["covered"] == {"high"}, "high lane closed, body lane open - the demonstration"


def test_a_clean_stream_passes_with_the_emergent_lane_result(tmp_path):
    rep = acs.analyse(_write(tmp_path, acs.expected_stream(SEED, TICKS)))
    assert rep["ok"], rep["errors"]
    assert rep["punch_rows"] > 100
    assert any("BIT-IDENTICAL" in n for n in rep["notes"])


def test_seeds_reproduce_and_differ():
    assert acs.expected_stream(SEED, TICKS) == acs.expected_stream(SEED, TICKS)
    assert acs.expected_stream(SEED, TICKS) != acs.expected_stream(SEED + 1, TICKS)


def test_a_jab_through_the_closed_lane_is_caught(tmp_path):
    """The lane law as a property, independent of the byte compare."""
    s = acs.expected_stream(SEED, TICKS)
    s = s.replace("|jab_lead|blocked|-|", "|jab_lead|landed|head|", 1)
    rep = acs.analyse(_write(tmp_path, s))
    assert any("closed high lane" in e or "diverges" in e for e in rep["errors"])


def test_a_blocked_body_straight_is_caught(tmp_path):
    s = acs.expected_stream(SEED, TICKS)
    s = s.replace("|body_straight_rear|landed|torso_upper|",
                  "|body_straight_rear|blocked|-|", 1)
    rep = acs.analyse(_write(tmp_path, s))
    assert any("below the interception threshold" in e or "diverges" in e
               for e in rep["errors"])


def test_a_resolution_outside_the_active_window_is_caught(tmp_path):
    s = acs.expected_stream(SEED, TICKS).splitlines()
    i = next(n for n, l in enumerate(s) if l.startswith("P|"))
    p = s[i].split("|")
    p[6] = "1"                       # inside startup: the hitbox is not live
    s[i] = "|".join(p)
    rep = acs.analyse(_write(tmp_path, "\n".join(s) + "\n"))
    assert any("active window" in e for e in rep["errors"])


def test_a_tampered_sweep_number_is_caught(tmp_path):
    s = acs.expected_stream(SEED, TICKS).splitlines()
    i = next(n for n, l in enumerate(s) if l.startswith("P|"))
    p = s[i].split("|")
    p[7] = str(int(p[7]) + 1)        # the tip, one unit off
    s[i] = "|".join(p)
    rep = acs.analyse(_write(tmp_path, "\n".join(s) + "\n"))
    assert any("diverges" in e or "fnv1a64" in e for e in rep["errors"])


def test_a_wrong_pose_canon_hash_is_caught(tmp_path):
    s = acs.expected_stream(SEED, TICKS)
    line = next(l for l in s.splitlines() if l.startswith("H|canon_pose="))
    s = s.replace(line, "H|canon_pose=" + "0" * 64)
    rep = acs.analyse(_write(tmp_path, s))
    assert any("canon_pose" in e for e in rep["errors"])


def test_a_missing_outcome_is_caught(tmp_path):
    """A run where nothing ever whiffs is not exercising the range geometry."""
    s = acs.expected_stream(SEED, TICKS)
    s = s.replace("|whiffed|", "|landed|")
    rep = acs.analyse(_write(tmp_path, s))
    assert not rep["ok"]


def test_float_divergence_stays_a_note(tmp_path):
    s = acs.expected_stream(SEED, TICKS).splitlines()
    i = next(n for n, l in enumerate(s) if l.startswith("F|"))
    s[i] = s[i][:-4] + "beef"
    rep = acs.analyse(_write(tmp_path, "\n".join(s) + "\n"))
    assert rep["ok"], rep["errors"]
    assert any("DIVERGES" in n for n in rep["notes"])
# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 05:45 UTC | END ]
