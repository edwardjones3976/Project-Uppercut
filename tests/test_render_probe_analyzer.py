# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 06:25 UTC | START ]
"""Phase K analyzer, mutation-proven before the rendered slice exists."""
import importlib.util
import os

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.join(HERE, "..", "tools", "engine", "analyze_render_probe.py")
spec = importlib.util.spec_from_file_location("analyze_render_probe", MOD)
arp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(arp)

SEED, TICKS = 4242, 5400


def _write(tmp_path, text):
    p = tmp_path / "markers.txt"
    p.write_text(text, encoding="utf-8")
    return str(p)


def test_a_clean_stream_passes_and_the_uppercut_splits_the_guard(tmp_path):
    s = arp.expected_stream(SEED, TICKS)
    rep = arp.analyse(_write(tmp_path, s))
    assert rep["ok"], rep["errors"]
    prow = [l.split("|") for l in s.splitlines() if l.startswith("P|")]
    assert any(r[3] == "uppercut_rear" and r[4] == "landed" for r in prow)
    assert not any(r[3] in ("jab_lead", "cross_rear", "hook_lead") and r[4] == "landed"
                   for r in prow), "high-lane punches through a closed guard"


def test_seeds_reproduce_and_differ():
    assert arp.expected_stream(SEED, TICKS) == arp.expected_stream(SEED, TICKS)
    assert arp.expected_stream(SEED, TICKS) != arp.expected_stream(SEED + 1, TICKS)


def test_a_missing_uppercut_landing_is_caught(tmp_path):
    s = arp.expected_stream(SEED, TICKS)
    s = s.replace("|uppercut_rear|landed|jaw_chin|", "|uppercut_rear|whiffed|-|")
    rep = arp.analyse(_write(tmp_path, s))
    assert not rep["ok"]
    assert any("guard-splitter" in e or "diverges" in e for e in rep["errors"])


def test_a_cross_through_the_closed_lane_is_caught(tmp_path):
    s = arp.expected_stream(SEED, TICKS)
    s = s.replace("|cross_rear|blocked|-|", "|cross_rear|landed|head|", 1)
    rep = arp.analyse(_write(tmp_path, s))
    assert any("closed lane" in e or "diverges" in e for e in rep["errors"])


def test_a_tampered_row_is_caught(tmp_path):
    s = arp.expected_stream(SEED, TICKS).splitlines()
    i = next(n for n, l in enumerate(s) if l.startswith("P|"))
    p = s[i].split("|")
    p[7] = str(int(p[7]) + 1)
    s[i] = "|".join(p)
    rep = arp.analyse(_write(tmp_path, "\n".join(s) + "\n"))
    assert not rep["ok"]


def test_a_wrong_canon_hash_is_caught(tmp_path):
    s = arp.expected_stream(SEED, TICKS)
    # Decision 0023: tamper with the SEMANTIC identity, because that is the one
    # that answers "is this the same fight". Corrupting the raw hash alone would
    # only prove provenance is checked.
    line = next(l for l in s.splitlines() if l.startswith("H|canon_pose_semantic="))
    s = s.replace(line, "H|canon_pose_semantic=" + "0" * 64)
    rep = arp.analyse(_write(tmp_path, s))
    assert any("canon_pose" in e for e in rep["errors"])
# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 06:25 UTC | END ]
