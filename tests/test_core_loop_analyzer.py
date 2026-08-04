# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 05:10 UTC | START ]
"""Phase I analyzer, mutation-proven before the C++ loop exists to judge.

Same discipline as every phase: a clean synthetic stream passes, every check
catches a synthetic violation, and the float probe is verified to be a
reported experiment rather than a pass criterion."""
import importlib.util
import os

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.join(HERE, "..", "tools", "engine", "analyze_core_loop.py")
spec = importlib.util.spec_from_file_location("analyze_core_loop", MOD)
acl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(acl)

SEED, TICKS = 4242, 5400


def _write(tmp_path, text):
    p = tmp_path / "markers.txt"
    p.write_text(text, encoding="utf-8")
    return str(p)


def _clean():
    return acl.expected_stream(SEED, TICKS)


def test_a_clean_stream_passes_and_exercises_everything(tmp_path):
    rep = acl.analyse(_write(tmp_path, _clean()))
    assert rep["ok"], rep["errors"]
    assert rep["rows"] == 2700
    assert any("BIT-IDENTICAL" in n for n in rep["notes"])


def test_same_seed_identical_different_seed_not():
    assert acl.expected_stream(SEED, TICKS) == acl.expected_stream(SEED, TICKS)
    assert acl.expected_stream(SEED, TICKS) != acl.expected_stream(SEED + 1, TICKS)


def test_a_tampered_state_snapshot_is_caught(tmp_path):
    s = _clean().splitlines()
    i = next(n for n, l in enumerate(s) if l.startswith("D|") and "|jab_lead|" in l)
    p = s[i].split("|")
    p[9] = str(int(p[9]) + 1)          # one stamina point of drift
    s[i] = "|".join(p)
    rep = acl.analyse(_write(tmp_path, "\n".join(s) + "\n"))
    assert any("diverges" in e for e in rep["errors"])


def test_a_wrong_canon_hash_is_caught(tmp_path):
    s = _clean()
    line = next(l for l in s.splitlines() if l.startswith("H|canon_condition="))
    s = s.replace(line, "H|canon_condition=" + "0" * 64)
    rep = acl.analyse(_write(tmp_path, s))
    assert any("canon_condition" in e for e in rep["errors"])


def test_a_band_jump_is_caught_independently(tmp_path):
    """Property check, not just the byte compare: force a two-band jump."""
    s = _clean().splitlines()
    idx = [n for n, l in enumerate(s) if l.startswith("D|")]
    p = s[idx[40]].split("|")
    p[8] = str((int(p[8]) + 2) % 5)
    s[idx[40]] = "|".join(p)
    rep = acl.analyse(_write(tmp_path, "\n".join(s) + "\n"))
    assert any("more than one" in e for e in rep["errors"])


def test_a_broken_self_hash_is_caught(tmp_path):
    s = _clean().splitlines()
    s[-1] = s[-1][:-4] + "dead"
    rep = acl.analyse(_write(tmp_path, "\n".join(s) + "\n"))
    assert any("fnv1a64" in e or "diverges" in e for e in rep["errors"])


def test_a_diverging_float_probe_is_a_note_not_an_error(tmp_path):
    """The experiment reports; it does not judge. A stream whose integer core
    is perfect but whose float bits differ must PASS with the divergence
    named in notes - that is the whole design of the probe."""
    s = _clean().splitlines()
    i = next(n for n, l in enumerate(s) if l.startswith("F|"))
    s[i] = s[i][:-4] + "beef"
    rep = acl.analyse(_write(tmp_path, "\n".join(s) + "\n"))
    assert rep["ok"], rep["errors"]
    assert any("DIVERGES" in n for n in rep["notes"])


def test_a_missing_action_is_caught(tmp_path):
    """A loop that never jabs is not exercising the decision surface."""
    s = _clean()
    s = s.replace("|jab_lead|", "|idle|")
    rep = acl.analyse(_write(tmp_path, s))
    assert not rep["ok"]          # byte-compare fails AND the surface check
    assert any("never taken" in e or "diverges" in e for e in rep["errors"])
# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 05:10 UTC | END ]
