# [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 02:53 UTC | START ]
"""Pair-uniqueness for two authored fighter cards.

Rule 10 polices ONE card. Nothing required two fighters in a test matchup to
differ, so a 1-round Press Play could still look like twins. This module
checks that a declared pairing differs on expressed in-round attributes by a
minimum margin on enough keys.
"""
from __future__ import annotations
from . import strict_json as json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

# Attributes that already reach the fight through data/attribute_effects.json.
# Unexpressed keys (ringcraft, showmanship, ...) do not count toward pair
# uniqueness for a 1-round test - differing on inert numbers is not uniqueness.
EXPRESSED_IN_ROUND = (
    "power",
    "chin",
    "durability",
    "hand_speed",
    "foot_speed",
    "stamina_pool",
    "reach",
    "accuracy",
    "defensive_technique",
    "guard_structure",
    "counter_timing",
    "body_work",
    "combination_fluency",
)

# Default pairing for the Unreal 1-round test harness.
DEFAULT_PAIR = ("test_pressure_power", "test_range_timing")
DEFAULT_MIN_KEYS = 8
DEFAULT_MIN_DELTA = 15


def load_fighter(fighter_id: str, root: Path | None = None) -> dict:
    root = root or REPO
    path = root / "fixtures" / "fighters" / "legal" / f"{fighter_id}.json"
    if not path.is_file():
        raise FileNotFoundError(f"no legal fighter fixture for id {fighter_id!r}: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def expressed_diffs(a: dict, b: dict, min_delta: int = DEFAULT_MIN_DELTA) -> list:
    aa = a.get("attributes", {})
    bb = b.get("attributes", {})
    out = []
    for key in EXPRESSED_IN_ROUND:
        va = int(aa.get(key, 0))
        vb = int(bb.get(key, 0))
        if abs(va - vb) >= min_delta:
            out.append((key, va, vb, abs(va - vb)))
    return out


def validate_pair(a: dict, b: dict,
                  min_keys: int = DEFAULT_MIN_KEYS,
                  min_delta: int = DEFAULT_MIN_DELTA) -> list:
    """Return human-readable violations. Empty list means the pair is unique enough."""
    errs = []
    if a.get("id") == b.get("id"):
        errs.append(f"pair shares the same fighter id {a.get('id')!r}")
    diffs = expressed_diffs(a, b, min_delta=min_delta)
    if len(diffs) < min_keys:
        keys = [d[0] for d in diffs]
        errs.append(
            f"pair differs on only {len(diffs)} expressed keys by >={min_delta} "
            f"(need {min_keys}); got {keys}"
        )
    return errs


def validate_default_pair(root: Path | None = None) -> list:
    a = load_fighter(DEFAULT_PAIR[0], root)
    b = load_fighter(DEFAULT_PAIR[1], root)
    return validate_pair(a, b)
# [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 02:53 UTC | END ]
