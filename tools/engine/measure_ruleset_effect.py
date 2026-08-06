# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 06:50 UTC | START ]
"""What Decision 0018 changed, measured on the contract rather than argued.

The three-knockdown rule was the termination condition in every measurement
taken the week of 2026-08-03, and Decision 0018 made it an arcade modifier
rather than the default. That means every stoppage figure from that week is
measured against a rule the project no longer uses by default, and this is the
re-run those figures need.

Both columns come from the SAME contract with the SAME seeds. The only thing
that differs is which rulebook the bout ran under, which is exactly the
comparison the old measurements could not make, because there was only one.

    python -m tools.engine.measure_ruleset_effect [--rounds 3] [--bouts 24]
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def run(ruleset: str, seeds, rounds: int) -> dict:
    # The ruleset is read at import time from the environment, so each column
    # needs its own interpreter state. Reloading is cheaper than a subprocess
    # and keeps the two columns provably on one code path.
    os.environ["UPPERCUT_RULESET"] = ruleset
    for mod in ("analyze_core_round",):
        if mod in sys.modules:
            del sys.modules[mod]
    import analyze_core_round as O
    out = {"ruleset": ruleset, "bouts": 0, "stoppages": 0, "decisions": 0,
           "knockdowns": 0, "rounds_completed": 0, "kd_per_round": 0.0,
           "reached_the_cards": 0, "stop_reasons": {}}
    for seed in seeds:
        s = O.expected_stream(seed, rounds, with_floats=False)
        trail = next(l for l in s.splitlines() if l.startswith("S|"))
        f = dict(kv.split("=", 1) for kv in trail.split("|")[1:])
        verdict = next((l for l in s.splitlines() if l.startswith("V|")), "")
        out["bouts"] += 1
        out["knockdowns"] += int(f["knockdowns"])
        out["rounds_completed"] += int(f["rounds"])
        if f["stopped"] == "1":
            out["stoppages"] += 1
            reason = verdict.split("|")[3] if verdict.count("|") >= 3 else "?"
            out["stop_reasons"][reason] = out["stop_reasons"].get(reason, 0) + 1
        else:
            out["decisions"] += 1
            out["reached_the_cards"] += 1
    if out["rounds_completed"]:
        out["kd_per_round"] = round(out["knockdowns"] / out["rounds_completed"], 2)
    return out


def main(argv) -> int:
    rounds = int(argv[argv.index("--rounds") + 1]) if "--rounds" in argv else 3
    bouts = int(argv[argv.index("--bouts") + 1]) if "--bouts" in argv else 24
    seeds = [4242 + i for i in range(bouts)]
    cols = [run("professional", seeds, rounds),
            run("arcade_three_knockdown", seeds, rounds)]

    print("\n%d bouts x %d rounds, seeds %d..%d, one contract, two rulebooks\n"
          % (bouts, rounds, seeds[0], seeds[-1]))
    print("  %-26s %10s %10s" % ("", "professional", "arcade"))
    for label, key in (("reached the cards", "reached_the_cards"),
                       ("stopped", "stoppages"),
                       ("knockdowns", "knockdowns"),
                       ("rounds completed", "rounds_completed"),
                       ("knockdowns per round", "kd_per_round")):
        print("  %-26s %10s %10s" % (label, cols[0][key], cols[1][key]))
    for col in cols:
        if col["stop_reasons"]:
            print("\n  %s stoppages: %s" % (col["ruleset"], col["stop_reasons"]))

    print("\nRead this carefully before quoting it. Reaching the cards is not the")
    print("same as the fight being right: if the knockdown rate is high, removing")
    print("the rule that ended bouts early does not fix the fight, it reveals it.")

    out = os.path.join(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))), "sandbox", "Saved",
        "ruleset_effect.json")
    if os.path.isdir(os.path.dirname(out)):
        with io.open(out, "w", encoding="utf-8", newline="\n") as fh:
            json.dump({"rounds": rounds, "seeds": [seeds[0], seeds[-1]],
                       "columns": cols}, fh, indent=2)
        print("\nwrote %s" % out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 06:50 UTC | END ]
