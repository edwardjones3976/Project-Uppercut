# [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 02:53 UTC | START ]
# [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 03:58 UTC | START edit ]
"""Pair-uniqueness for two authored fighter cards.

Rule 10 polices ONE card. Nothing required two fighters in a test matchup to
differ, so a 1-round Press Play could still look like twins. This module
checks that a declared pairing differs on expressed in-round attributes by a
minimum margin on enough keys.

WHAT COUNTS AS DIFFERENT. The comparison is taken over the attributes
`data/attribute_effects.json` actually EXPRESSES - rows in `effects` - and
never over `unexpressed_attributes.not_yet_expressed`. That set is read from
canon rather than listed here, so the day `ringcraft` acquires an effect it
enters this check automatically. A hardcoded 13-tuple previously omitted
`recovery`, which canon already expresses.

A pair that differs only on unexpressed keys (showmanship, ringcraft, ...)
would pass a naive 24-key comparison while producing two fighters who fight
identically. That is the failure this module exists to catch.
"""
from __future__ import annotations
from . import strict_json as json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

# How different is different enough. Authoring hygiene, not fight rules.
DEFAULT_MIN_DELTA = 20
DEFAULT_MIN_KEYS = 8

# Default pairing for the Unreal 1-round test harness (PR #31 cards).
DEFAULT_PAIR = ("test_pressure_power", "test_range_timing")


def expressed_attributes(path: Path | None = None) -> set:
    """Attributes that reach the fight, per canon.

    Cross-checks `effects` against `not_yet_expressed`: an attribute in both
    (or a silent hole in the taxonomy claim) is refused rather than papered over.
    """
    path = path or REPO / "data" / "attribute_effects.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    have = {e["attribute"] for e in doc["effects"]}
    named_absent = set(doc["unexpressed_attributes"]["not_yet_expressed"])
    both = have & named_absent
    if both:
        raise ValueError(
            "data/attribute_effects.json both gives an effect to and declares "
            "unexpressed: %s. One of the two statements is false."
            % sorted(both)
        )
    return have


# Back-compat alias for callers that still read the old constant name. Prefer
# expressed_attributes() — this is evaluated once at import for CLI convenience.
EXPRESSED_IN_ROUND = tuple(sorted(expressed_attributes()))


def load_fighter(fighter_id: str, root: Path | None = None) -> dict:
    root = root or REPO
    path = root / "fixtures" / "fighters" / "legal" / f"{fighter_id}.json"
    if not path.is_file():
        raise FileNotFoundError(
            f"no legal fighter fixture for id {fighter_id!r}: {path}"
        )
    return json.loads(path.read_text(encoding="utf-8"))


def expressed_diffs(
    a: dict,
    b: dict,
    min_delta: int = DEFAULT_MIN_DELTA,
    expressed: set | None = None,
) -> list:
    expressed = expressed if expressed is not None else expressed_attributes()
    aa = a.get("attributes", {})
    bb = b.get("attributes", {})
    out = []
    for key in sorted(expressed):
        va = int(aa.get(key, 0))
        vb = int(bb.get(key, 0))
        if abs(va - vb) >= min_delta:
            out.append((key, va, vb, abs(va - vb)))
    return out


def validate_pair(
    a: dict,
    b: dict,
    min_keys: int = DEFAULT_MIN_KEYS,
    min_delta: int = DEFAULT_MIN_DELTA,
    expressed: set | None = None,
) -> list:
    """Return human-readable violations. Empty list means the pair is unique enough."""
    expressed = expressed if expressed is not None else expressed_attributes()
    errs = []
    if a.get("id") == b.get("id"):
        errs.append(f"pair shares the same fighter id {a.get('id')!r}")
    diffs = expressed_diffs(a, b, min_delta=min_delta, expressed=expressed)
    if len(diffs) < min_keys:
        keys = [d[0] for d in diffs]
        errs.append(
            f"pair differs on only {len(diffs)} expressed keys by >={min_delta} "
            f"(need {min_keys} of {len(expressed)}); got {keys}"
        )
    return errs


def validate_default_pair(root: Path | None = None) -> list:
    a = load_fighter(DEFAULT_PAIR[0], root)
    b = load_fighter(DEFAULT_PAIR[1], root)
    return validate_pair(a, b)
# [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 03:58 UTC | END edit ]
# [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 02:53 UTC | END ]
