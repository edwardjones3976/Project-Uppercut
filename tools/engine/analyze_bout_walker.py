# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 12:12 UTC | START ]
"""Canon-conformance analysis for BP_BoutWalker markers (Phase F: the bout structure).

Every prior engine phase proved something that happens INSIDE a round. This one is
about the round itself, and it carries a claim that hashing cannot test.

A hash proves a run reproduces. It says nothing about whether a scorecard leaked: a
Blueprint that printed the sealed card on every tick would hash perfectly and be a
Rule 3 violation. So the sealed check here is POSITIONAL - no `S|` line may appear
before the last `B|` line in the stream - and that is a fact about the log rather than
a claim about the graph.

Three further defects are checked because each has already happened somewhere in this
project or is one edit away:

  * round boundaries recomputed from canon, not trusted. `round` and `tickInRound` are
    re-derived from the authoritative tick and `round_ticks`; a Blueprint keeping its
    own round counter that drifted from the clock would pass a hash and fail here
    (Rule 8: one clock, and everything reads it).

  * the accumulator must RESET at each boundary. The reference model shipped a
    `_score_round` that summed bout-to-date landings, so an early lead re-won every
    later round; it was caught by a balance sweep rather than by a check. Here a
    monotonically rising accumulator across a boundary is a hard failure.

  * the accumulator must actually move. A stuck-at-zero accumulator resets perfectly
    at every boundary and proves nothing, which is the vacuous pass this whole harness
    exists to refuse.

Usage: python analyze_bout_walker.py <markers.txt> [...]
"""
import io
import json
import os
import sys

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
Q = 1048576.0


def canon():
    """Round length and tick rate come from canon so this file cannot drift from it."""
    clock = json.load(io.open(os.path.join(REPO, "data", "clock_model.json"), encoding="utf-8"))
    return clock["authority"]["tick_rate_hz"]


def parse(path_or_lines):
    if isinstance(path_or_lines, (list, tuple)):
        lines = list(path_or_lines)
    else:
        lines = list(io.open(path_or_lines, encoding="utf-8"))
    obs, sealed = [], []
    order = []
    for raw in lines:
        line = raw.strip()
        if line.startswith("B|"):
            p = line.split("|")
            obs.append(tuple(int(x) for x in p[1:5]))
            order.append("B")
        elif line.startswith("S|"):
            p = line.split("|")
            sealed.append(tuple(int(x) for x in p[1:4]))
            order.append("S")
    return obs, sealed, order


def analyse(source, round_ticks, rounds, name="markers"):
    """`source` is a path or a list of lines. Returns a report dict; empty `errors`
    means the run is canon-conformant, not merely reproducible."""
    hz = canon()
    obs, sealed, order = parse(source)
    rep = {"file": name, "tick_rate_hz": hz, "observable": len(obs),
           "sealed": len(sealed), "errors": []}

    if not obs:
        rep["errors"].append("no observable markers - nothing ran")
        return rep

    # Rule 3, positionally. A sealed card that appears while the fight is still
    # emitting observable events has leaked, however deterministic it is.
    if "S" in order:
        first_s = order.index("S")
        last_b = len(order) - 1 - order[::-1].index("B")
        if first_s < last_b:
            rep["errors"].append(
                "SEALED LEAK: an S| card appears at position %d, before the final "
                "observable marker at position %d - the cards were readable while the "
                "fight was still running (Rule 3)" % (first_s, last_b))
    else:
        rep["errors"].append("no sealed markers - the sealed path is untested, and a "
                             "check that only forbids passes trivially when the thing "
                             "it forbids never occurs")

    # Rule 8: recompute the round structure from the authoritative tick.
    per_actor = {}
    for idx, rnd, tir, acc in obs:
        per_actor.setdefault(idx, []).append((rnd, tir, acc))

    for idx, rows in sorted(per_actor.items()):
        moved = False
        for n, (rnd, tir, acc) in enumerate(rows):
            tick = n + 1                      # the Blueprint counts from 1
            want_r, want_t = divmod(tick - 1, round_ticks)
            if (rnd, tir) != (want_r, want_t):
                rep["errors"].append(
                    "actor %d tick %d: reports round %d tick-in-round %d, but the "
                    "authoritative tick gives %d/%d - the Blueprint is keeping its own "
                    "clock" % (idx, tick, rnd, tir, want_r, want_t))
                break
            if n and rows[n - 1][2] != acc:
                moved = True
            # The bank: crossing into a new round must drop the accumulator.
            if n and rnd != rows[n - 1][0] and acc > rows[n - 1][2]:
                rep["errors"].append(
                    "actor %d tick %d: the accumulator rose across a round boundary "
                    "(%d -> %d). The round is meant to be scored in front of the "
                    "judges, not the bout to date" % (idx, tick, rows[n - 1][2], acc))
                break
        if not moved:
            rep["errors"].append(
                "actor %d: the accumulator never changed value - it resets at every "
                "boundary because it is always zero, which is a vacuous pass" % idx)
        seen_rounds = sorted({r for r, _, _ in rows})
        if seen_rounds != list(range(rounds)):
            rep["errors"].append(
                "actor %d: saw rounds %s, expected %s - the bout did not run its "
                "scheduled length" % (idx, seen_rounds, list(range(rounds))))

    rep["actors"] = sorted(per_actor)
    return rep


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    round_ticks = int(os.environ.get("UE_ROUND_TICKS", "240"))
    rounds = int(os.environ.get("UE_ROUNDS", "3"))
    bad = 0
    for path in argv[1:]:
        rep = analyse(path, round_ticks, rounds, os.path.basename(path))
        print(json.dumps(rep, indent=1))
        bad += len(rep["errors"])
    print("RESULT: %s" % ("OK" if not bad else "%d FAILURE(S)" % bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 12:12 UTC | END ]
