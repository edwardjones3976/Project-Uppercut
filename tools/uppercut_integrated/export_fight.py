# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-08 22:58 UTC | START ]
"""Export an integrated fight for the First Bell viewer. Read-only over the bout.

WHAT THIS IS. The standing order is "work until we can all watch a fight."
The bout emits its authoritative stream; the viewer is a broadcast booth that
replays it. This module is the cable between them: it runs one fight, walks
the rows the bout already emitted, and writes the viewer's JSON schema.

WHAT THIS REFUSES TO BE. An authority on anything. Every number here is read
off `bout.rows`, `bout.samples`, `bout.result` and the sealed cards AFTER the
panel has closed - nothing is recomputed, nothing is smoothed, and a fight
that looks strange in the viewer is a fact about the fight, not a rendering
choice. Presentation may explain the result; it may not rewrite it.

THE SCHEMA (the viewer's contract, mirrored from its own demo builder):

    meta     seed, rounds_planned, round_ticks, tick_hz, participants,
             referee {id, display_name}, result, axis_ru
    samples  [{t, r, pos[q], wind[q], reserve[q], dmg[q]}]   (q = q10000)
    events   punch / window / knockdown / count / rise / stoppage / round_end
    cards    {judge: {totals: [a, b], rounds: [[round, a, b], ...]}}

Ticks are GLOBAL throughout - the viewer detects that and does not need the
per-round form. `target` is the broadcast's upstairs/downstairs word, derived
from canon's damage region: the torso and arm regions are "body", everything
else is "head". That mapping is presentation vocabulary, not a combat rule.
"""
import argparse
import io
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from tools.uppercut_integrated.bout import IntegratedBout  # noqa: E402

# Canon's damage regions, sorted into the two words a commentator uses.
# eye/jaw/head are upstairs; torso and the arms that shell it are the body.
BODY_REGIONS = ("torso_lower", "torso_upper", "arm_left", "arm_right")

TICK_HZ = 60  # the project's tick rate: round_ticks is authored as 180 * 60

MARKER_OPEN = "/*FIGHT_DATA*/"
MARKER_CLOSE = "/*END_FIGHT_DATA*/"
MARKER = MARKER_OPEN + "null" + MARKER_CLOSE


def _target(region):
    return "body" if region in BODY_REGIONS else "head"


def fight_events(bout):
    """The viewer's event list, read off the rows in emission order.

    The current round is tracked from the bout's own B rows rather than
    derived from tick arithmetic, because the bell defers while a count runs
    ("nobody is saved by the bell") and arithmetic would put those ticks in
    the wrong round.
    """
    events = []
    r = 1
    for row in bout.rows:
        parts = row.split("|")
        kind = parts[0]
        if kind == "B":
            if parts[2] == "round_start":
                r = int(parts[3])
            elif parts[2] == "round_end":
                events.append({"t": int(parts[1]), "r": int(parts[3]),
                               "kind": "round_end"})
        elif kind == "P":
            t, who, move = int(parts[1]), parts[2], parts[4]
            place = parts[5]  # "region=X" for a resolved punch, "band=X" whiffed
            outcome = parts[7]
            ev = {"t": t, "r": r, "kind": "punch", "who": who, "move": move,
                  "outcome": "whiff_band" if outcome == "whiffed" else outcome,
                  "reason": parts[8]}
            if place.startswith("region="):
                ev["target"] = _target(place.split("=", 1)[1])
            events.append(ev)
        elif kind == "W":
            events.append({"t": int(parts[1]), "r": r, "kind": "window",
                           "who": parts[2], "ev": parts[3], "what": parts[4]})
        elif kind == "N":
            events.append({"t": int(parts[1]), "r": r, "kind": "knockdown",
                           "who": parts[2], "by": parts[5]})
        elif kind == "K":
            events.append({"t": int(parts[1]), "r": r, "kind": "count",
                           "who": parts[2],
                           "n": int(parts[3].split("=", 1)[1])})
        elif kind == "U":
            events.append({"t": int(parts[1]), "r": r, "kind": "rise",
                           "who": parts[2],
                           "at": int(parts[4].split("=", 1)[1])})
        elif kind == "F":
            method, detail = parts[2], parts[3]
            if method in ("KO", "TKO"):
                events.append({"t": int(parts[1]), "r": r, "kind": "stoppage",
                               "detail": detail})
    return events


def fight_cards(bout):
    """The sealed cards, through the only door that opens them.

    `verdict()` refuses to speak before `close()`, and this function does not
    work around that: an export of an unfinished fight has no cards, the same
    way a broadcast of an unfinished fight has none.
    """
    if not bout.result:
        return {}
    # [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-09
    #   10:00 UTC | edit: Section 4's consumer guard ] A bout stopped before
    # the first round closed has NO scored rounds, and the panel now refuses
    # to invent a card from that absence (NoCardToRead). The export says the
    # same thing the broadcast would: there are no cards to show.
    if not bout.panel.seal_check():
        return {}
    v = bout.panel.verdict()
    return {judge: {"totals": list(card["totals"]),
                    "rounds": [list(rnd) for rnd in card["rounds"]]}
            for judge, card in v["cards"].items()}


def export_fight(bout):
    """One finished (or stopped-early) bout as the viewer's JSON object."""
    return {
        "meta": {
            "seed": bout.rng.bout_seed,
            "rounds_planned": bout.rounds_planned,
            "round_ticks": bout.state.round_ticks,
            "tick_hz": TICK_HZ,
            "participants": list(bout.state.participants),
            "referee": {"id": bout.referee["id"],
                        "display_name": bout.referee["display_name"]},
            "result": bout.result,
            "axis_ru": bout.range["axis"] / 10000.0,
        },
        "samples": bout.samples,
        "events": fight_events(bout),
        "cards": fight_cards(bout),
    }


def inject(template_text, fight):
    """The viewer template with the fight where its null was.

    The marker must appear exactly once and exactly as authored; anything
    else means the template drifted, and a silent .replace() over a drifted
    template is how a demo ships wearing a real fight's name.
    """
    if template_text.count(MARKER) != 1:
        raise SystemExit(
            "the viewer template does not carry exactly one %r marker; "
            "refusing to guess where the fight goes" % MARKER)
    payload = json.dumps(fight, separators=(",", ":"), sort_keys=True)
    return template_text.replace(
        MARKER, MARKER_OPEN + payload + MARKER_CLOSE)


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Run one integrated fight and export it for the viewer.")
    ap.add_argument("--seed", type=int, default=4242)
    ap.add_argument("--referee", default="nkiru_okafor")
    ap.add_argument("--rounds", type=int, default=12)
    ap.add_argument("--out-dir", required=True,
                    help="directory for fight.json (created if missing)")
    ap.add_argument("--template", default=None,
                    help="viewer HTML template; when given, watch.html is "
                         "written next to fight.json")
    # [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 00:20 UTC
    #   | START edit: choose the fighters ]
    # WHO BOXES is a harness choice, not a canon change - the profiles are
    # dispositions the policy already accepts, and Decision 0017 fixed what
    # aggression means (initiative, not throw rate). This exists because the
    # default pairing ends on the knockdown limit in every seed tried, and a
    # milestone that claims "capable of ending by valid decision" has to be
    # able to RUN the fighters that reach one.
    ap.add_argument("--profile", action="append", default=None,
                    metavar="AGGRESSION:BAND",
                    help="per-fighter disposition in participant order, e.g. "
                         "--profile 1500:outside --profile 6500:mid")
    args = ap.parse_args(argv)

    profiles = None
    if args.profile:
        from tools.uppercut_integrated import contract as C
        from tools.uppercut_integrated import policy as P
        if len(args.profile) != len(C.DEFAULT_PARTICIPANTS):
            raise SystemExit(
                "--profile must be given once per participant (%d), got %d"
                % (len(C.DEFAULT_PARTICIPANTS), len(args.profile)))
        profiles = {}
        for who, spec in zip(C.DEFAULT_PARTICIPANTS, args.profile):
            bias, _, band = spec.partition(":")
            profiles[who] = P.Profile(int(bias), band or "mid")

    bout = IntegratedBout(seed=args.seed, rounds=args.rounds,
                          referee=args.referee, profiles=profiles)
    # [ ... | 2026-08-09 00:20 UTC | END edit ]
    bout.run_fight()
    fight = export_fight(bout)

    os.makedirs(args.out_dir, exist_ok=True)
    json_path = os.path.join(args.out_dir, "fight.json")
    with io.open(json_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(fight, f, separators=(",", ":"), sort_keys=True)
        f.write("\n")

    html_path = None
    if args.template:
        with io.open(args.template, "r", encoding="utf-8") as f:
            template_text = f.read()
        html_path = os.path.join(args.out_dir, "watch.html")
        with io.open(html_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(inject(template_text, fight))

    r = bout.result
    print("fight: seed=%d ticks=%d rounds=%d result=%s %s winner=%s"
          % (args.seed, bout.tick, bout.round_no, r["method"], r["detail"],
             r["winner"] or "-"))
    print("events=%d samples=%d -> %s" % (len(fight["events"]),
                                          len(fight["samples"]), json_path))
    if html_path:
        print("watchable -> %s" % html_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-08 22:58 UTC | END ]
