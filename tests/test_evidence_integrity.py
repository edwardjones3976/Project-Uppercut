# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 22:10 UTC | START ]
"""Evidence-integrity regressions from the 2026-08-09 external audit (F1-F4).

Each test here is the Python-checkable half of an audit finding. The C++ halves
(F4's loader guard, F5's exit codes) cannot run under pytest; their harness is
`prove_core_range` / `prove_core_evade` against a compiled UppercutCore, and
they are recorded in Decision 0039 rather than asserted here.
"""
import json as stdlib_json
from pathlib import Path

import pytest

from tools.uppercut_canon import canonical as C
from tools.uppercut_canon.header import canon_header_lines
from tools.uppercut_validate import movement, score_isolation as si, strict_json

REPO = Path(__file__).resolve().parents[1]


# ---------------------------------------------------------------------- F1 ----

def test_strict_loader_refuses_non_finite_numbers():
    """NaN/Infinity have no agreed cross-language encoding: the C++ canon parser
    refuses them (Decision 0023) and the evidence hasher refuses them, so a
    validator that ACCEPTED them was approving files the evidence layer cannot
    even name. Before the F1 fix stdlib json accepted all three literals."""
    for bad in ('{"a": NaN}', '{"a": Infinity}', '{"a": -Infinity}'):
        assert stdlib_json.loads(bad)  # the stdlib really does accept these
        with pytest.raises(C.CanonError):
            strict_json.loads(bad)


def test_strict_loader_refuses_duplicate_keys_however_deep():
    """A duplicate key means the file says two different things depending on
    the reader. The hook runs at every object, so depth cannot hide one."""
    with pytest.raises(C.CanonError):
        strict_json.loads('{"a": 1, "a": 2}')
    with pytest.raises(C.CanonError):
        strict_json.loads('{"x": {"y": [{"z": 1, "z": 2}]}}')


def test_strict_loader_is_the_evidence_layers_parser():
    """One opinion of what a canon file says, not a third one."""
    assert strict_json.parse is C.parse


def test_every_validator_module_parses_with_the_strict_loader():
    """Uniformity is the finding: ONE permissive module re-opens the hole.
    Any validator module that binds a name `json` must bind the strict alias -
    including modules added after this test was written."""
    import importlib
    import pkgutil
    import tools.uppercut_validate as pkg
    lax = []
    for info in pkgutil.iter_modules(pkg.__path__):
        if info.name == "strict_json":
            continue
        mod = importlib.import_module("tools.uppercut_validate." + info.name)
        if getattr(mod, "json", None) is not None and mod.json is not strict_json:
            lax.append(info.name)
    assert not lax, ("these validator modules still parse with a permissive "
                     "json: %s" % lax)


# ---------------------------------------------------------------------- F2 ----

F2_ENTRIES = [("movement", "data/movement_model.json")]


def test_header_lines_from_identical_texts_are_byte_identical():
    """The fix must not move a single pinned value: supplying the same bytes
    the disk holds must produce the same header the disk-read path produces."""
    rel = F2_ENTRIES[0][1]
    with open(REPO / rel, encoding="utf-8", newline="") as fh:
        disk = fh.read()
    assert (canon_header_lines(str(REPO), F2_ENTRIES)
            == canon_header_lines(str(REPO), F2_ENTRIES, texts={rel: disk}))


def test_header_lines_derive_from_the_supplied_bytes_not_a_second_read():
    """F2: the header must name the bytes the simulation consumed. Simulate a
    midflight edit by supplying text that differs from disk only in raw bytes
    (a trailing newline - semantically identical, provenance different). The
    raw hash line must follow the SUPPLIED bytes. Before the fix this call
    signature did not exist and every hash came from a fresh disk read."""
    rel = F2_ENTRIES[0][1]
    with open(REPO / rel, encoding="utf-8", newline="") as fh:
        disk = fh.read()
    baseline = canon_header_lines(str(REPO), F2_ENTRIES)
    mutated = canon_header_lines(str(REPO), F2_ENTRIES,
                                 texts={rel: disk + "\n"})

    def raw_of(lines):
        return [l for l in lines if l.startswith("H|canon_movement_raw=")]

    def sem_of(lines):
        return [l for l in lines if l.startswith("H|canon_movement_semantic=")]

    assert raw_of(baseline) != raw_of(mutated), \
        "the raw hash ignored the supplied bytes - it must have re-read disk"
    assert sem_of(baseline) == sem_of(mutated), \
        "whitespace moved the semantic hash - that would be a canonicalizer bug"


# ---------------------------------------------------------------------- F3 ----

def _contract(paths):
    return {"sealed_symbols": {"identifiers": ["official_scorecard"],
                               "event_types": []},
            "forbidden_consumers": [{"id": "probe", "paths": paths}]}


def test_scan_source_refuses_dotdot_escape():
    """A contract is data; data must not aim the scanner outside the tree it
    polices. Refusal, not skipping: a skipped consumer is an unscanned one."""
    root = REPO / "tests" / "isolation_samples" / "compliant_sample"
    with pytest.raises(ValueError):
        si.scan_source(root, _contract(["../../.."]))


def test_scan_source_refuses_absolute_escape():
    """pathlib REPLACES the base when joined with an absolute path, so an
    absolute consumer path silently retargets the whole scan."""
    root = REPO / "tests" / "isolation_samples" / "compliant_sample"
    with pytest.raises(ValueError):
        si.scan_source(root, _contract([str(REPO.parent)]))


def test_scan_source_still_accepts_contained_paths():
    """The guard must not break the real contract: the shipped scan of the
    compliant sample stays clean, exactly as before. (Guard-rail: this also
    passed before the F3 fix.)"""
    assert si.scan_source(REPO / "tests" / "isolation_samples" /
                          "compliant_sample") == []


# ---------------------------------------------------------------------- F4 ----

def test_empty_range_band_canon_is_refused_by_the_validator():
    """F4's Python half, held so it cannot regress. The C++ loader guard
    (pending its build window - Decision 0039) refuses zero bands because
    BandAt() would hand a -1 to an Unreal TArray; the Python law that makes
    that refusal canon-consistent lives here: a band table that is not exactly
    the five canonical bands is rejected before any index math runs.
    (Guard-rail: this passed before the audit too - it is recorded as the
    contract the C++ guard mirrors, and the compiled parity check is
    prove_core_range, not this test.)"""
    errs = movement.check_bands({"range_bands": {"bands": [],
                                                 "hysteresis_ru": 0.05}})
    assert errs, "an empty band table must be refused, never defaulted"
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 22:10 UTC | END ]
