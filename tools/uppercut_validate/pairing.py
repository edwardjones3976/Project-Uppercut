# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-12 03:26 UTC | START ]
"""Two fighters in a match must actually be two fighters.

THE HOLE THIS CLOSES. Every existing Rule 10 check judges ONE card in
isolation: is it inside the economy, is it compensated, does it stay under the
cap. Nothing anywhere required two cards put in a ring together to differ. Two
byte-identical cards were a legal matchup, and the live C++ fighters were
exactly that - identical empty cards, all multipliers 1.0 - so "press Play and
tell the fighters apart" was not a thing the repository could fail at, because
it was not a thing the repository asserted.

WHAT COUNTS AS DIFFERENT, AND WHY IT IS NOT ALL 24 KEYS. The comparison is
taken over the attributes `data/attribute_effects.json` actually EXPRESSES -
the ones with a declared effect row - and never over the ten it names in
`unexpressed_attributes.not_yet_expressed`. That set is read from canon rather
than listed here, so the day `ringcraft` acquires an effect it enters this
check automatically and nobody has to remember to widen it.

The distinction matters more than it looks. A pair that differs by 60 points of
`showmanship` and nothing else would pass a naive 24-key comparison while
producing two fighters who fight identically, because showmanship scales
nothing yet. That pair is precisely the failure this module exists to catch, so
counting it as a difference would make the check agree with the bug.
"""
from __future__ import annotations
from . import strict_json as json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

# How different is different enough. These are authoring hygiene, not fight
# rules: they change no outcome, they only refuse a matchup that cannot produce
# one worth watching. Stated as constants rather than canon for that reason.
#
# MIN_DELTA = 20 is a tenth of the -100..+100 economy. On the widest expressed
# band (chin, 0.82 -> 1.32) that is 0.05 of multiplier; on the narrowest
# (accuracy, 0.88 -> 1.15) it is 0.027. Small on purpose - the bar is "these
# fighters are not the same man", not "these fighters are opposites".
#
# MIN_DIFFERING = 8 of the 14 currently expressed attributes is a majority. A
# pair differing on seven or fewer is one style with an accent, and the point of
# a matched pair is that a viewer can tell which is which from behaviour.
MIN_DELTA = 20
MIN_DIFFERING = 8


def expressed_attributes(path: Path | None = None) -> set:
    """The attributes that reach the fight, per canon.

    An attribute is expressed when `attribute_effects.json` gives it an effect
    row. `not_yet_expressed` is read too, and the two are cross-checked: if an
    attribute appears in both, or in neither, this file is not the authority it
    claims to be and the caller is told so rather than handed a plausible set.
    """
    path = path or REPO / "data" / "attribute_effects.json"
    doc = json.loads(path.read_text())
    have = {e["attribute"] for e in doc["effects"]}
    named_absent = set(doc["unexpressed_attributes"]["not_yet_expressed"])
    both = have & named_absent
    if both:
        raise ValueError(
            "data/attribute_effects.json both gives an effect to and declares "
            "unexpressed: %s. One of the two statements is false."
            % sorted(both))
    return have


def compare(card_a: dict, card_b: dict, expressed: set | None = None) -> dict:
    """How these two cards differ where the fight can see it.

    Returns the per-attribute deltas over the expressed set, which attributes
    clear MIN_DELTA, and whether the pair is legal. Reporting the whole table
    rather than a boolean is deliberate: a rejected pair should tell its author
    which knob to turn, not merely that one of them needs turning.
    """
    expressed = expressed if expressed is not None else expressed_attributes()
    a = card_a.get("attributes", {})
    b = card_b.get("attributes", {})

    deltas = {}
    for k in sorted(expressed):
        # A card silent on an attribute sits at the baseline (Rule 10: zero
        # multiplies by exactly one), so absence is 0 rather than an error.
        deltas[k] = abs(int(a.get(k, 0)) - int(b.get(k, 0)))

    differing = sorted(k for k, d in deltas.items() if d >= MIN_DELTA)
    return {
        "a": card_a.get("id", "<a>"),
        "b": card_b.get("id", "<b>"),
        "expressed_count": len(expressed),
        "deltas": deltas,
        "differing": differing,
        "differing_count": len(differing),
        "min_delta": MIN_DELTA,
        "min_differing": MIN_DIFFERING,
        "legal": len(differing) >= MIN_DIFFERING,
    }


def check_pair(card_a: dict, card_b: dict, expressed: set | None = None) -> list:
    """Findings for a matched pair. Empty means the pair is a real matchup."""
    r = compare(card_a, card_b, expressed)
    out = []
    if r["a"] == r["b"]:
        out.append(
            "a fighter cannot be matched with himself: both cards declare id "
            "'%s'" % r["a"])
    if not r["legal"]:
        near = sorted(((d, k) for k, d in r["deltas"].items()
                       if d < MIN_DELTA), reverse=True)[:4]
        out.append(
            "'%s' and '%s' differ by >= %d on only %d of the %d expressed "
            "attributes (need %d). Closest un-cleared: %s"
            % (r["a"], r["b"], MIN_DELTA, r["differing_count"],
               r["expressed_count"], MIN_DIFFERING,
               ", ".join("%s=%d" % (k, d) for d, k in near) or "none"))
    return out


# The pair the live 1-round match is fought with. Named here so one edit moves
# both the validator and the simulator, rather than the two drifting apart with
# nobody noticing which pair was actually measured.
MATCH_PAIR = ("generic_pressure_a", "generic_range_b")


def load_card(fighter_id: str) -> dict:
    """A fixture card by id.

    Fixtures live under `fixtures/fighters/`, NOT `data/fighters/` - there is
    deliberately no such directory, because a roster is Phase 1B and a
    directory is an invitation.
    """
    for kind in ("legal", "illegal"):
        p = REPO / "fixtures" / "fighters" / kind / ("%s.json" % fighter_id)
        if p.exists():
            return json.loads(p.read_text())
    raise FileNotFoundError(
        "no fixture card '%s.json' under fixtures/fighters/" % fighter_id)


def check_match_pair() -> list:
    """The declared match pair, checked. This is what the CLI runs."""
    a, b = (load_card(i) for i in MATCH_PAIR)
    return check_pair(a, b)
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-12 03:26 UTC | END ]
