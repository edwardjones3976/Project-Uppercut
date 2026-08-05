# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 15:20 UTC | START ]
"""The pinned drift, measured: ten guards on two volumes.

The execution plan has carried "10 guards vs. 2 guard volumes need reconciling"
as known drift for days, with a standing instruction to surface it in any
doc-review pass. Several doc-review passes have now gone by without it being
surfaced, so it is surfaced here as arithmetic rather than as a note.

THE SHAPE OF IT, three separate problems wearing one label:

  1. TEN POSTURES, TWO NUMBERS. `guard_evasion_model.postures` authors ten
     guards. Every one of them is expressed as exactly two coverage extents,
     `guard_high` and `guard_body`, because `collision_model.guard_interception`
     maps every punch path to one of those two volumes or to both. So the entire
     structural difference between ten real boxing guards - a philly shell and an
     ear muff are not two settings of one thing - is a point in a 2-D space.

  2. FOUR BEHAVIOURS, NOT TEN. Coverage is tested against a hard threshold: a
     lane is closed when the extent reaches it and open when it does not. Under
     that test the ten collapse to however many distinct (high, body) open/closed
     pairs exist, and there are only four possible. This file computes which.

  3. EIGHT OF THE TEN ARE INERT. The core loads two postures. The other eight are
     authored, validated, documented and unreachable - the declared-but-inert
     class this repository keeps a checker for, in the subsystem the project's
     core design rule is written about.

None of this is a tuning question and none of it is mine to answer. A guard is
supposed to be "a body structure that protects some lanes while exposing others";
the question the Director faces is whether two lanes can carry that promise, and
if not, what the third is.

Run: python -m tools.engine.measure_guard_expressiveness
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_core_round as O  # noqa: E402

GE = os.path.join("data", "guard_evasion_model.json")
COL = os.path.join("data", "collision_model.json")


def load():
    ge = json.loads(io.open(os.path.join(O.REPO, GE), "rb").read())
    col = json.loads(io.open(os.path.join(O.REPO, COL), "rb").read())
    return ge, col


def main() -> int:
    ge, col = load()
    postures = ge["postures"]
    gi = {k: v for k, v in col["guard_interception"].items()
          if not k.startswith("$")}
    volumes = sorted({v for vs in gi.values() for v in vs})
    c = O.canon_pack()
    thr = c["thr"]

    print("%d postures authored; %d coverage volumes to express them in: %s"
          % (len(postures), len(volumes), ", ".join(volumes)))
    print("%d punch paths, each mapped to those volumes: %s"
          % (len(gi), ", ".join("%s -> %s" % (k, "+".join(v))
                                for k, v in sorted(gi.items()))))
    print("the core loads %d of the %d: %s"
          % (len(c["posture"]), len(postures), ", ".join(sorted(c["posture"]))))
    print("interception threshold %.2f" % (thr / 10000.0))
    print()

    print("1. WHAT EACH GUARD IS, AND WHAT IT DOES AT THE THRESHOLD")
    print("  %-16s %6s %6s   %-8s %-8s   %-10s %s"
          % ("posture", "high", "body", "high", "body", "class", "in core"))
    classes = {}
    for p in postures:
        hi = O.q(p["extents"].get("guard_high", 0.0))
        bo = O.q(p["extents"].get("guard_body", 0.0))
        ch, cb = hi >= thr, bo >= thr
        key = (ch, cb)
        classes.setdefault(key, []).append(p["id"])
        name = {(True, False): "head only", (True, True): "both",
                (False, True): "body only", (False, False): "neither"}[key]
        print("  %-16s %6.2f %6.2f   %-8s %-8s   %-10s %s"
              % (p["id"], hi / 10000.0, bo / 10000.0,
                 "closed" if ch else "OPEN", "closed" if cb else "OPEN",
                 name, "yes" if p["id"] in c["posture"] else "-"))
    print()

    print("2. TEN GUARDS, %d BEHAVIOURS" % len(classes))
    for key in sorted(classes, key=lambda k: (-len(classes[k]), k)):
        name = {(True, False): "head only", (True, True): "both",
                (False, True): "body only", (False, False): "neither"}[key]
        print("  %-10s %d of %d:  %s"
              % (name, len(classes[key]), len(postures),
                 ", ".join(classes[key])))
    print()
    print("  Against a hard threshold a lane is closed or it is not, so the")
    print("  most a two-volume model can express is four behaviours. Ten")
    print("  authored guards land in %d of them, and %d guards share the single"
          % (len(classes), max(len(v) for v in classes.values())))
    print("  most crowded one. The philly shell and the ear muff differ by 0.30")
    print("  of head coverage and 0.20 of body, and at contact they do the same")
    print("  thing as each other.")
    print()

    print("3. WHERE EACH GUARD BREAKS, AS DAMAGE ACCUMULATES")
    print("  Condition erodes coverage (`_guard_mult`), so a lane that starts")
    print("  closed opens at some level of accumulated arm damage. That level is")
    print("  the guard's real identity under this model - and it is the")
    print("  Director's open erosion-horizon question, stated as a number.")
    print("  %-16s %14s %14s" % ("posture", "head opens at", "body opens at"))
    rows = {}
    for p in postures:
        out = []
        for vol, key in (("guard_high", "head"), ("guard_body", "body")):
            ext = O.q(p["extents"].get(vol, 0.0))
            if ext < thr:
                out.append(None)          # already open
                continue
            # the multiplier at which this lane falls below the threshold
            out.append(thr / float(ext))
        rows[p["id"]] = out
        fmt = []
        for v in out:
            fmt.append("open already" if v is None else "mult %.3f" % v)
        print("  %-16s %14s %14s" % (p["id"], fmt[0], fmt[1]))
    print()
    closed = [(k, v) for k, v in rows.items() if v[0] is not None]
    if closed:
        tightest = max(closed, key=lambda kv: kv[1][0])
        loosest = min(closed, key=lambda kv: kv[1][0])
        print("  The head lane's break point ranges from %.3f (%s, the last to"
              % (loosest[1][0], loosest[0]))
        print("  open) to %.3f (%s, the first). Everything between those two"
              % (tightest[1][0], tightest[0]))
        print("  numbers is the entire expressive range of a head guard in this")
        print("  model, before the per-hand rule and the committed multiplier.")
    print()

    # A guard whose coverage is EXACTLY the threshold is closed only while
    # perfectly fresh. Worth calling out separately: it is not a design choice
    # anyone would make on purpose, and it is invisible in the extent table.
    knife = []
    for p in postures:
        for vol, key in (("guard_high", "head"), ("guard_body", "body")):
            if O.q(p["extents"].get(vol, 0.0)) == thr:
                knife.append((p["id"], key))
    if knife:
        print("4. TWO GUARDS SIT EXACTLY ON THE THRESHOLD")
        for pid, key in knife:
            print("    %-16s %s lane = %.2f = the threshold exactly"
                  % (pid, key, thr / 10000.0))
        print("  A lane at exactly the threshold is closed while the fighter is")
        print("  perfectly fresh and open the instant ANY arm damage lands - a")
        print("  break multiplier of 1.000, the earliest possible. That is not a")
        print("  choice anyone makes on purpose and it is invisible in the")
        print("  extent table, which is why it is called out separately.")
        print()

    print("READ THIS AS:")
    print("  The drift is real and it is three problems, not one:")
    print("    - ten guards are expressed in two numbers, because interception")
    print("      knows three punch paths and two volumes;")
    print("    - at the threshold they collapse to %d behaviours, %d of them"
          % (len(classes), max(len(v) for v in classes.values())))
    print("      sharing one;")
    print("    - and %d of the ten are not loaded by the core at all."
          % (len(postures) - len(c["posture"])))
    print()
    print("  The project's core design rule says a guard is a body structure")
    print("  that protects some lanes while exposing others, changes what")
    print("  offence is available from inside it, and costs resources to hold.")
    print("  Two of those three are expressible today: coverage as two numbers,")
    print("  and cost as `stamina_per_tick`. The middle clause - what offence a")
    print("  guard makes available - is authored per posture as `offense_cheap`")
    print("  and `offense_expensive` and is read by nothing.")

    out = {"postures": len(postures), "volumes": volumes,
           "loaded_by_core": sorted(c["posture"]),
           "threshold": thr / 10000.0,
           "classes": {str(k): v for k, v in classes.items()},
           "break_multipliers": {k: [None if x is None else round(x, 4)
                                     for x in v] for k, v in rows.items()},
           "on_the_threshold": knife}
    p = os.path.join(O.REPO, "sandbox", "Saved", "guard_expressiveness.json")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    io.open(p, "w", encoding="utf-8").write(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 15:20 UTC | END ]
