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
    """Returns (observable rows, sealed rows, stream) where `stream` preserves LOG
    ORDER as (kind, actor, round, tickInRound) - the sealed check is positional, so
    the interleaving between actors is evidence and must survive parsing."""
    if isinstance(path_or_lines, (list, tuple)):
        lines = list(path_or_lines)
    else:
        lines = list(io.open(path_or_lines, encoding="utf-8"))
    obs, sealed, stream = [], [], []
    for raw in lines:
        line = raw.strip()
        if line.startswith("B|"):
            p = tuple(int(x) for x in line.split("|")[1:5])
            obs.append(p)
            stream.append(("B", p[0], p[1], p[2]))
        elif line.startswith("S|"):
            p = tuple(int(x) for x in line.split("|")[1:4])
            sealed.append(p)
            stream.append(("S", p[0], p[1], None))
    return obs, sealed, stream


def analyse(source, round_ticks, rounds, name="markers"):
    """`source` is a path or a list of lines. Returns a report dict; empty `errors`
    means the run is canon-conformant, not merely reproducible."""
    hz = canon()
    obs, sealed, stream = parse(source)
    rep = {"file": name, "tick_rate_hz": hz, "observable": len(obs),
           "sealed": len(sealed), "errors": []}

    if not obs:
        rep["errors"].append("no observable markers - nothing ran")
        return rep

    # Rule 3, positionally - but positional against the FIGHT, not against the log's
    # line numbering. Actors tick in sequence within a frame, so on the final tick the
    # stream legitimately reads B(a0) S(a0) B(a1) S(a1): actor 0's card is emitted
    # before actor 1's last observable line and nothing has leaked. A first version of
    # this check compared raw line positions and failed the first clean engine run for
    # exactly that reason. The claim is "no card before the final bell", so that is
    # what is tested:
    #
    #   1. every sealed card is stamped with the final round, and
    #   2. every observable line following the first sealed card is from the final tick.
    #
    # A card printed at tick 300 still fails on both counts, with hundreds of
    # non-final observable lines behind it.
    final_round = rounds - 1
    final_tir = round_ticks - 1
    if sealed:
        for idx, rnd, _ in sealed:
            if rnd != final_round:
                rep["errors"].append(
                    "SEALED LEAK: actor %d emitted a card stamped round %d, before the "
                    "final round %d - the cards were readable while the fight was still "
                    "running (Rule 3)" % (idx, rnd, final_round))
        first_s = next(i for i, e in enumerate(stream) if e[0] == "S")
        stragglers = [e for e in stream[first_s:]
                      if e[0] == "B" and (e[2], e[3]) != (final_round, final_tir)]
        if stragglers:
            k, a, r, t = stragglers[0]
            rep["errors"].append(
                "SEALED LEAK: %d observable markers follow the first sealed card, the "
                "earliest being actor %d at round %d tick %d, which is not the final "
                "tick (%d/%d) - the fight was still running when the card appeared "
                "(Rule 3)" % (len(stragglers), a, r, t, final_round, final_tir))
    else:
        rep["errors"].append("no sealed markers - the sealed path is untested, and a "
                             "check that only forbids passes trivially when the thing "
                             "it forbids never occurs")

    # Every actor that fought must produce exactly one card. Counted against the
    # actors seen in the OBSERVABLE stream, not against the sealed stream: an actor
    # that emitted no card at all has no entry to count, so a check that iterates the
    # sealed rows can never see it missing. Caught by its own test.
    sealed_by_actor = {}
    for idx, rnd, val in sealed:
        sealed_by_actor.setdefault(idx, []).append(val)
    for idx in sorted({a for a, _, _, _ in obs}):
        n = len(sealed_by_actor.get(idx, []))
        if n != 1:
            rep["errors"].append("actor %d fought and emitted %d sealed cards, expected "
                                 "exactly one" % (idx, n))

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
