# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 09:10 UTC | START ]
"""What the staged policy did, against the numbers it was supposed to fix.

Decisions 0015 and 0016 replaced a flat eleven-way draw - in which 5 of 11
outcomes were a punch regardless of where the fighter stood, what he could
reach, or how tired he was - with a staged one: intent, opportunity, action.

The three figures that matter, and where they came from:

  volume       55-78 punches per fighter per round is professional. The flat
               draw produced 175-219, which is what gate G3 was opened about.
  connect      the reference simulator lands 42.4% of what it throws.
  knockdowns   the reference reaches the cards in 20 of 24 bouts; this core
               measured 22.89 knockdowns per round on 2026-08-06 with the
               stoppage rule removed, which is what made the size of the
               conversion problem visible.

    python -m tools.engine.measure_staged_policy [--rounds 3] [--bouts 24]
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import analyze_core_round as O  # noqa: E402

REFERENCE = {"volume_low": 55, "volume_high": 78, "connect": 42.4}


def main(argv) -> int:
    rounds = int(argv[argv.index("--rounds") + 1]) if "--rounds" in argv else 3
    bouts = int(argv[argv.index("--bouts") + 1]) if "--bouts" in argv else 24
    tot = {k: 0 for k in ("punches", "landed", "blocked", "whiffed", "dodged",
                          "knockdowns", "rounds", "observes", "rests",
                          "no_opportunity", "steps", "slips")}
    cards = 0
    for i in range(bouts):
        s = O.expected_stream(4242 + i, rounds, with_floats=False)
        f = dict(kv.split("=", 1) for kv in
                 next(l for l in s.splitlines()
                      if l.startswith("S|")).split("|")[1:])
        for k in tot:
            tot[k] += int(f[k])
        if f["stopped"] == "0":
            cards += 1

    fighter_rounds = tot["rounds"] * 2
    volume = tot["punches"] / max(1, fighter_rounds)
    arrived = tot["landed"] + tot["blocked"]
    connect = 100.0 * tot["landed"] / max(1, tot["punches"])
    kd = tot["knockdowns"] / max(1, tot["rounds"])
    decisions = tot["observes"] + tot["rests"] + tot["no_opportunity"]

    print("\n%d bouts x %d rounds, tier %s, ruleset %s\n"
          % (bouts, rounds, O.canon_pack()["tier"],
             O.canon_pack()["ruleset"]["id"]))
    print("  punches per fighter-round   %6.1f   (professional %d-%d, flat draw "
          "was 175-219)" % (volume, REFERENCE["volume_low"],
                            REFERENCE["volume_high"]))
    print("  connect rate                %6.1f%%  (reference %.1f%%)"
          % (connect, REFERENCE["connect"]))
    print("  arrived (landed or blocked) %6.1f%%  of everything thrown"
          % (100.0 * arrived / max(1, tot["punches"])))
    print("  knockdowns per round        %6.2f   (was 22.89 before the policy)"
          % kd)
    print("  reached the cards           %6d   of %d" % (cards, bouts))
    print("\n  the policy's own numbers, per bout:")
    print("    observations              %6.0f" % (tot["observes"] / bouts))
    print("    rests                     %6.0f" % (tot["rests"] / bouts))
    print("    attacks with no legal band%6.0f" % (tot["no_opportunity"] / bouts))
    print("    steps                     %6.0f" % (tot["steps"] / bouts))
    print("    slips                     %6.0f" % (tot["slips"] / bouts))
    print("\n  Read the connect rate before celebrating the volume. A fight in")
    print("  which everything thrown arrives is not an accurate fight - it is a")
    print("  fight with nothing left to miss.")

    out = os.path.join(O.REPO, "sandbox", "Saved", "staged_policy.json")
    if os.path.isdir(os.path.dirname(out)):
        with io.open(out, "w", encoding="utf-8", newline="\n") as fh:
            json.dump({"bouts": bouts, "rounds": rounds, "totals": tot,
                       "volume_per_fighter_round": round(volume, 2),
                       "connect_pct": round(connect, 2),
                       "knockdowns_per_round": round(kd, 3),
                       "reached_the_cards": cards}, fh, indent=2)
        print("\nwrote %s" % out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 09:10 UTC | END ]
