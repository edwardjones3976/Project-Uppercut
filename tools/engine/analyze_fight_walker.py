# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 13:30 UTC | START ]
"""Canon-conformance analysis for BP_FightWalker markers (Phase G: a scored bout).

Phase E proved the collision pipeline resolves correctly in the Blueprint VM. Phase F
proved the bout structure - rounds off the authoritative clock, per-round banking, a
sealed card past the final bell. Neither connected them: Phase E's verdicts scored
nothing, and Phase F's round card was fed by a raw stream draw standing in for offence.

Phase G joins them, so the round card is computed from RESOLVED CONTACT. That makes a
new class of defect possible, and it is the one this file exists for: every stage could
be individually correct while the scoring chain between them is wrong. A pipeline that
resolved perfectly and then scored a blocked punch, or scored a clean punch at a grazed
punch's weight, would hash identically to a correct one and pass every Phase E and F
check.

So every marker carries the pipeline's four inputs, the class it produced, and the
running round accumulator. This file recomputes the whole chain from canon -
`quality_bands` for both the thresholds and the delivered force fractions,
`contact_classes` for the class ordering - and compares it row by row. Nothing here
trusts a number the Blueprint reported except as a claim to be checked.

Marker: F|<idx>|<round>|<tickInRound>|<cls>|<q(r1)>|<q(r2)>|<q(r3)>|<q(align)>|<q20 acc>
Sealed: S|<idx>|<round>|<q20 SealedTotal>

Usage: python analyze_fight_walker.py <markers.txt> [...]
"""
import io
import json
import os
import sys

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
QI = 65536.0          # pipeline input quantization (matches Phase E)
QA = 1048576.0        # accumulator quantization (matches Phase F)
WHIFF_RATE, EVADE_RATE, GUARD_RATE = 0.15, 0.20, 0.35


def canon():
    col = json.load(io.open(os.path.join(REPO, "data", "collision_model.json"), encoding="utf-8"))
    bands = sorted(col["quality_bands"], key=lambda q: q["min_alignment"])
    qthr = [float(b["min_alignment"]) for b in bands[1:]]
    force = {b["class"]: float(b["delivered_force_fraction"]) for b in bands}
    cc = json.load(io.open(os.path.join(REPO, "data", "contact_classes.json"), encoding="utf-8"))
    order = [c["key"] for c in cc["classes"]]
    return order, qthr, force


def expected_class(order, qthr, r1, r2, r3, a):
    """The canonical pipeline, in its canonical order, as plain Python."""
    if r1 < WHIFF_RATE:
        return order.index("whiffed")
    if r2 < EVADE_RATE:
        return order.index("dodged")
    if r3 < GUARD_RATE:
        return order.index("blocked")
    qc = sum(1 for t in qthr if a >= t)
    return order.index(["brushed", "grazed", "solid", "clean"][qc])


def parse(path_or_lines):
    lines = (list(path_or_lines) if isinstance(path_or_lines, (list, tuple))
             else list(io.open(path_or_lines, encoding="utf-8")))
    obs, sealed, stream = [], [], []
    for raw in lines:
        line = raw.strip()
        if line.startswith("F|"):
            p = tuple(int(x) for x in line.split("|")[1:10])
            obs.append(p)
            stream.append(("F", p[0], p[1], p[2]))
        elif line.startswith("S|"):
            p = tuple(int(x) for x in line.split("|")[1:4])
            sealed.append(p)
            stream.append(("S", p[0], p[1], None))
    return obs, sealed, stream


def analyse(source, round_ticks, rounds, name="markers", tol=3):
    """`tol` is the permitted absolute drift in quantized accumulator units. The
    Blueprint accumulates in doubles and the analyzer re-adds the same values in the
    same order, so drift should be zero or one unit of the quantization; anything
    larger means the two are not computing the same thing."""
    order, qthr, force_of = canon()
    obs, sealed, stream = parse(source)
    rep = {"file": name, "observable": len(obs), "sealed": len(sealed),
           "errors": [], "class_counts": {}}
    if not obs:
        rep["errors"].append("no observable markers - nothing ran")
        return rep

    # Rule 3: the card may not precede the final bell. Positional against the FIGHT,
    # not the log's line numbering - actors tick in sequence inside a frame, so on the
    # final tick the stream legitimately interleaves F(a0) S(a0) F(a1) S(a1).
    final_round, final_tir = rounds - 1, round_ticks - 1
    if sealed:
        for idx, rnd, _ in sealed:
            if rnd != final_round:
                rep["errors"].append(
                    "SEALED LEAK: actor %d emitted a card stamped round %d before the "
                    "final round %d (Rule 3)" % (idx, rnd, final_round))
        first_s = next(i for i, e in enumerate(stream) if e[0] == "S")
        strag = [e for e in stream[first_s:]
                 if e[0] == "F" and (e[2], e[3]) != (final_round, final_tir)]
        if strag:
            _, a, r, t = strag[0]
            rep["errors"].append(
                "SEALED LEAK: %d observable markers follow the first sealed card, the "
                "earliest actor %d at round %d tick %d, which is not the final tick "
                "(%d/%d) (Rule 3)" % (len(strag), a, r, t, final_round, final_tir))
    else:
        rep["errors"].append("no sealed markers - the sealed path is untested")

    per_actor = {}
    for row in obs:
        per_actor.setdefault(row[0], []).append(row)
    for idx in sorted(per_actor):
        if len(sealed_for(sealed, idx)) != 1:
            rep["errors"].append("actor %d fought and emitted %d sealed cards, expected "
                                 "exactly one" % (idx, len(sealed_for(sealed, idx))))

    landed_names = ("clean", "solid", "grazed", "brushed")
    for idx, rows in sorted(per_actor.items()):
        acc = 0.0
        banked = 0.0
        moved = False
        for n, (_, rnd, tir, cls, q1, q2, q3, qa, qacc) in enumerate(rows):
            tick = n + 1
            want_r, want_t = divmod(tick - 1, round_ticks)
            if (rnd, tir) != (want_r, want_t):
                rep["errors"].append(
                    "actor %d tick %d: reports round %d/%d, authoritative tick gives "
                    "%d/%d - the Blueprint is keeping its own clock"
                    % (idx, tick, rnd, tir, want_r, want_t))
                break

            r1, r2, r3, a = q1 / QI, q2 / QI, q3 / QI, qa / QI
            want_cls = expected_class(order, qthr, r1, r2, r3, a)
            if cls != want_cls:
                rep["errors"].append(
                    "actor %d tick %d: pipeline produced '%s', canon gives '%s' for "
                    "inputs %.5f/%.5f/%.5f/%.5f"
                    % (idx, tick, order[cls], order[want_cls], r1, r2, r3, a))
                break
            rep["class_counts"][order[cls]] = rep["class_counts"].get(order[cls], 0) + 1

            # The scoring chain, recomputed. A landed class contributes its authored
            # delivered force fraction; everything else contributes nothing. This is
            # the join Phase E and Phase F each left untested.
            gained = force_of[order[cls]] if order[cls] in landed_names else 0.0
            if tir == 0 and tick > 1:
                banked += acc
                acc = gained
            else:
                acc += gained

            if abs(round(acc * QA) - qacc) > tol:
                rep["errors"].append(
                    "actor %d tick %d: round accumulator reads %d, canon recomputes %d "
                    "from the classes resolved so far - the pipeline and the scoring "
                    "disagree" % (idx, tick, qacc, round(acc * QA)))
                break
            if n and rows[n - 1][8] != qacc:
                moved = True
            if n and rnd != rows[n - 1][1] and qacc > rows[n - 1][8]:
                rep["errors"].append(
                    "actor %d tick %d: the accumulator rose across a round boundary - "
                    "the round is scored in front of the judges, not the bout to date"
                    % (idx, tick))
                break
        else:
            banked += acc                 # the final round is banked at the bell
            got = sealed_for(sealed, idx)
            if got and abs(round(banked * QA) - got[0]) > tol * (rounds + 1):
                rep["errors"].append(
                    "actor %d: sealed card reads %d, canon recomputes %d as the sum of "
                    "the banked rounds - the card does not follow from the fight"
                    % (idx, got[0], round(banked * QA)))
        if not moved:
            rep["errors"].append("actor %d: the accumulator never changed - a vacuous "
                                 "pass" % idx)
        seen = sorted({r[1] for r in rows})
        if seen != list(range(rounds)):
            rep["errors"].append("actor %d: saw rounds %s, expected %s"
                                 % (idx, seen, list(range(rounds))))

    # Every class must actually occur, or the pipeline is only half exercised.
    missing = [c for c in order if c not in rep["class_counts"]]
    if missing:
        rep["errors"].append("classes never produced in this run: %s - the pipeline is "
                             "not total in practice, whatever the table says" % missing)
    rep["actors"] = sorted(per_actor)
    return rep


def sealed_for(sealed, idx):
    return [v for i, _, v in sealed if i == idx]


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
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 13:30 UTC | END ]
