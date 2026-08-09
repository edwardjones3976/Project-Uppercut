# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 21:58 UTC | F1 strict canon JSON | START ]
"""Strict JSON for every validator: duplicate keys refused, NaN/Infinity refused.

The 2026-08-09 external audit (finding F1) observed that the validators parsed
canon with stdlib defaults, which accept NaN/Infinity literals and silently
keep one of two duplicate keys - while the evidence layer
(tools/uppercut_canon/canonical.py) and the C++ canon parser both refuse them.
Two parsers with two opinions about what a file says is exactly the drift the
dual-hash work exists to prevent, so this module does not implement a third
opinion: `loads` IS the evidence layer's `parse`.

A validator module aliases this as its `json` (`from . import strict_json as
json`) so every existing `json.loads(...)` call site becomes strict in one
edit, and any call site added to that module later is strict by default - fail
closed rather than fail open. `CanonError` subclasses ValueError, the same base
class json.JSONDecodeError uses, so existing error handling keeps working.
"""
from tools.uppercut_canon.canonical import CanonError, parse  # noqa: F401


def loads(text):
    """Parse canon text; refuses duplicate keys and non-finite numbers."""
    return parse(text)
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 21:58 UTC | F1 strict canon JSON | END ]
