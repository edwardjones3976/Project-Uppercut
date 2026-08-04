# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 03:42 UTC | START ]
"""Phase H analyzer, mutation-proven before any C++ exists to judge.

Every check in tools/engine/analyze_core_scaffold.py must catch a synthetic
violation and pass a clean stream - the same discipline every engine phase has
run under, applied to the phase that moves the fight core to C++."""
import importlib.util
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.join(HERE, "..", "tools", "engine", "analyze_core_scaffold.py")
spec = importlib.util.spec_from_file_location("analyze_core_scaffold", MOD)
acs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(acs)


def _write(tmp_path, text):
    p = tmp_path / "markers.txt"
    p.write_text(text, encoding="utf-8")
    return str(p)


def test_a_clean_stream_passes(tmp_path):
    rep = acs.analyse(_write(tmp_path, acs.expected_stream(7777, 400)))
    assert rep["ok"], rep["errors"]
    assert rep["rows"] == 400
    assert rep["transitions"] > 0


def test_same_seed_is_byte_identical_and_seeds_differ():
    a1 = acs.expected_stream(7777, 400)
    a2 = acs.expected_stream(7777, 400)
    b1 = acs.expected_stream(7778, 400)
    assert a1 == a2
    assert a1 != b1


def test_a_tampered_distance_is_caught(tmp_path):
    s = acs.expected_stream(7777, 400).splitlines()
    i = next(n for n, l in enumerate(s) if l.startswith("R|20|"))
    p = s[i].split("|")
    p[3] = str(int(p[3]) + 1)
    s[i] = "|".join(p)
    rep = acs.analyse(_write(tmp_path, "\n".join(s) + "\n"))
    assert not rep["ok"]
    assert any("diverges" in e for e in rep["errors"])


def test_a_tampered_band_is_caught(tmp_path):
    s = acs.expected_stream(7777, 400).splitlines()
    i = next(n for n, l in enumerate(s) if l.startswith("R|30|"))
    p = s[i].split("|")
    p[4] = str((int(p[4]) + 2) % 5)
    s[i] = "|".join(p)
    rep = acs.analyse(_write(tmp_path, "\n".join(s) + "\n"))
    assert not rep["ok"]


def test_a_wrong_canon_hash_is_caught(tmp_path):
    s = acs.expected_stream(7777, 400)
    s = s.replace(s.splitlines()[0], "H|canon_sha256=" + "0" * 64)
    rep = acs.analyse(_write(tmp_path, s))
    assert any("different canon" in e for e in rep["errors"])


def test_a_wrong_trailer_hash_is_caught(tmp_path):
    s = acs.expected_stream(7777, 400).splitlines()
    assert s[-1].startswith("S|")
    s[-1] = s[-1][:-4] + "beef"
    rep = acs.analyse(_write(tmp_path, "\n".join(s) + "\n"))
    assert any("vouch" in e or "diverges" in e for e in rep["errors"])


def test_truncation_is_caught(tmp_path):
    s = acs.expected_stream(7777, 400).splitlines()
    del s[50:60]
    rep = acs.analyse(_write(tmp_path, "\n".join(s) + "\n"))
    assert not rep["ok"]


def test_a_drifted_seed_line_is_caught(tmp_path):
    """A stream honest about its own arithmetic but lying about its seed."""
    s = acs.expected_stream(7777, 400)
    s = s.replace("H|seed=7777", "H|seed=1234")
    rep = acs.analyse(_write(tmp_path, s))
    assert any("diverges" in e for e in rep["errors"])


def test_a_constant_emitter_is_caught(tmp_path):
    """The dead-accumulator shape from Phase B: plausible headers, one row
    value repeated forever, self-consistent hash. The property checks must
    kill it even though it hashes its own bytes correctly."""
    rows = [f"R|{i}|5|5|2" for i in range(50)]
    blob = "".join(l + "\n" for l in rows).encode()
    _, _, _, sha = acs.canon_quantized()
    s = "\n".join([f"H|canon_sha256={sha}", "H|seed=5", "H|steps=50"] + rows
                  + [f"S|rows=50|transitions=0|fnv1a64={acs.fnv1a64(blob):016x}"]) + "\n"
    rep = acs.analyse(_write(tmp_path, s))
    assert any("constant" in e for e in rep["errors"])
    assert any("never changed" in e for e in rep["errors"])
# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 03:42 UTC | END ]
