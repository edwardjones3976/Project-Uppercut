# [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 02:53 UTC | START ]
"""Attribute multipliers for the integrated bout. Same mapping as uppercut_sim.

Reads data/attribute_effects.json. An empty card multiplies every mechanic by
exactly 1.0 (Rule 10 baseline). Fixed-point q10000 so C++ can port the same
arithmetic without float drift.
"""
from __future__ import annotations
import os
from tools.uppercut_validate import strict_json as json

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ONE = 10000
_EFFECTS = None


def _effects():
    global _EFFECTS
    if _EFFECTS is None:
        path = os.path.join(REPO, "data", "attribute_effects.json")
        _EFFECTS = json.loads(open(path, encoding="utf-8").read())["effects"]
    return _EFFECTS


def load_card_attrs(fighter_id, root=None):
    """Load a complete legal fixture card's attributes by id, or {} if absent."""
    root = root or REPO
    path = os.path.join(root, "fixtures", "fighters", "legal",
                        "%s.json" % fighter_id)
    if not os.path.isfile(path):
        return {}
    data = json.loads(open(path, encoding="utf-8").read())
    return dict(data.get("attributes") or {})


def multiplier_q10000(attrs, scales):
    """q10000 multiplier for a named mechanic from this card. Silent = ONE."""
    attrs = attrs or {}
    for e in _effects():
        if e["scales"] != scales:
            continue
        v = attrs.get(e["attribute"])
        if v is None:
            return ONE
        lo = int(round(float(e["multiplier_at_minus_100"]) * ONE))
        hi = int(round(float(e["multiplier_at_plus_100"]) * ONE))
        t = (max(-100, min(100, int(v))) + 100)  # 0..200
        return lo + ((hi - lo) * t) // 200
    return ONE


def apply_q(value_q, attrs, scales):
    """Scale a q10000 quantity by the card's multiplier for `scales`."""
    return (int(value_q) * multiplier_q10000(attrs, scales)) // ONE
# [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 02:53 UTC | END ]
