# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 10:35 UTC | START ]
"""Authoritative clock validator (Rule 8, Rule 9).

`schemas/clock_settings.schema.json` has existed since Phase 0 with nothing
behind it, which is why "accelerated-clock synchronization" - one of the
ROADMAP's eleven required automated checks - could not run. It could not run
because there was no clock to test.

The rule the checks defend: the Accelerated Clock is a *display mapping*. It
changes how much displayed time passes per real second and nothing else. The
moment it reaches the tick rate, the authored frame data, stamina, or the
knockdown count, two fighters are running on different physics from the same
bell - and the knockdown count in particular is a safety instrument that does
not speed up because a display option was toggled.
"""
from __future__ import annotations
import json
from pathlib import Path

from . import schema_check

REPO = Path(__file__).resolve().parents[2]

REQUIRED_READERS = ("simulation", "judging", "referee", "commentary", "replay")

REQUIRED_PROHIBITIONS = ("second clock", "tick rate", "free-form round", "menus pause",
                         "wall-clock")

REQUIRED_INVARIANTS = (
    "one_clock_only", "acceleration_is_display_only", "acceleration_ratio_is_canonical",
    "round_lengths_are_authored", "break_is_thirty_real_seconds",
    "count_clock_runs_on_real_seconds", "wall_clock_is_not_authoritative",
)


def load() -> dict:
    return json.loads((REPO / "data" / "clock_model.json").read_text())


def _condition() -> dict:
    return json.loads((REPO / "data" / "condition_model.json").read_text())


def check_schema(doc: dict) -> list:
    return schema_check.validate(doc, "clock_model.schema.json")


def check_authority(doc: dict) -> list:
    a = doc["authority"]
    errs = []
    if not a["single_clock"]:
        errs.append("Rule 9: one authoritative clock, read by everything")
    for r in REQUIRED_READERS:
        if r not in a["read_by"]:
            errs.append(f"Rule 9: '{r}' must read the authoritative clock - a system on its own "
                        f"schedule is a second clock wearing a different name")
    if a["tick_rate_hz"] != 60:
        errs.append("the authoritative tick rate is 60Hz")
    if a["wall_clock_drives_simulation"]:
        errs.append("Criterion E.19: wall-clock time may not drive the simulation")
    if a["menus_pause_between_round_break"]:
        errs.append("Rule 8: menus do not pause the between-rounds break")
    return errs


def check_acceleration(doc: dict) -> list:
    """The check that gives the gate item something to test."""
    ac = doc["accelerated_clock"]
    errs = []
    if (ac["on_display_seconds"], ac["on_real_seconds"]) != (180, 105):
        errs.append("Rule 8: the Accelerated Clock displays 3:00 over 1:45 of real time")
    for k, why in (
        ("affects_simulation_tick_rate",
         "acceleration may not change the tick rate - the simulation runs at one speed"),
        ("affects_authored_frame_data",
         "acceleration may not change authored frames, or a jab means something different "
         "depending on a display toggle"),
        ("affects_stamina_per_tick",
         "acceleration may not change stamina per tick, or pacing becomes a settings choice"),
        ("affects_knockdown_count_clock",
         "Rule 16: the knockdown count is a safety instrument and runs on real seconds whatever "
         "the display says"),
    ):
        if ac[k]:
            errs.append(why)
    return errs


def check_rounds(doc: dict) -> list:
    errs = []
    if doc["free_form_round_length_permitted"]:
        errs.append("Rule 8: round length is one, two or three minutes - no free-form values")
    for s in doc["round_lengths_seconds"]:
        if s not in (60, 120, 180):
            errs.append(f"round length {s}s is outside the authored set")
    if doc["between_rounds_break_seconds"] != 30:
        errs.append("Rule 8: the between-rounds break is thirty real seconds")
    # Cross-file lock: the condition model states the same break in ticks.
    ticks = _condition()["recovery"]["between_rounds_break_ticks"]
    expected = doc["between_rounds_break_seconds"] * doc["authority"]["tick_rate_hz"]
    if ticks != expected:
        errs.append(f"the condition model's break of {ticks} ticks disagrees with this clock's "
                    f"{doc['between_rounds_break_seconds']}s at {doc['authority']['tick_rate_hz']}Hz "
                    f"({expected} ticks)")
    return errs


def check_segments(doc: dict) -> list:
    errs = []
    for need in ("round", "break", "count"):
        if need not in doc["segments"]:
            errs.append(f"clock segment '{need}' is missing")
    return errs


def check_prohibitions(doc: dict) -> list:
    blob = " ".join(doc["prohibitions"]).lower()
    return [f"missing required prohibition covering '{p}'"
            for p in REQUIRED_PROHIBITIONS if p not in blob]


def check_invariants(doc: dict) -> list:
    present = {i["id"] for i in doc["invariants"]}
    return [f"missing required invariant '{r}'" for r in REQUIRED_INVARIANTS if r not in present]


ALL_CHECKS = [
    ("schema", check_schema),
    ("authority_rule9", check_authority),
    ("acceleration_rule8", check_acceleration),
    ("rounds_rule8", check_rounds),
    ("segments", check_segments),
    ("prohibitions", check_prohibitions),
    ("invariants_declared", check_invariants),
]


def run_all(doc: dict | None = None) -> list:
    doc = load() if doc is None else doc
    out = []
    for name, fn in ALL_CHECKS:
        out.extend(f"{name}: {e}" for e in fn(doc))
    return out
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 10:35 UTC | END ]
