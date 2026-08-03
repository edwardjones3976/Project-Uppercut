# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 08:26 UTC | START ]
"""Canon-conformance analysis for BP_PipelineWalker markers.

The hash proves the run reproduces. This proves the run is RIGHT: every marker carries
the four pipeline inputs alongside the verdict, so the canonical pipeline is recomputed
here from data/collision_model.json and data/contact_classes.json and compared row by
row. A pipeline that resolved guard before evasion, or that let a non-overlapping sweep
reach a landed class, would hash perfectly and fail here.

Usage: python analyze_pipeline_walker.py <markers.txt> [...]
"""
import io, json, os, sys

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
Q = 65536.0
WHIFF_RATE, EVADE_RATE, GUARD_RATE = 0.15, 0.20, 0.35


def canon():
    col = json.load(io.open(os.path.join(REPO, "data", "collision_model.json"), encoding="utf-8"))
    qb = sorted(col["quality_bands"], key=lambda q: q["min_alignment"])
    qthr = [float(q["min_alignment"]) for q in qb[1:]]
    cc = json.load(io.open(os.path.join(REPO, "data", "contact_classes.json"), encoding="utf-8"))
    order = [c["key"] for c in cc["classes"]]
    stages = sorted((s["order"], s["id"], s["verdict_if_true"])
                    for s in col["resolution_pipeline"])
    return order, qthr, stages


def expected(order, qthr, r1, r2, r3, a):
    """The canonical pipeline, in its canonical order, as plain Python."""
    if r1 < WHIFF_RATE:                 # stage 0, inverted: no overlap
        return order.index("whiffed")
    if r2 < EVADE_RATE:                 # stage 1, ranked ABOVE guard on purpose
        return order.index("dodged")
    if r3 < GUARD_RATE:                 # stage 2
        return order.index("blocked")
    qc = sum(1 for t in qthr if a >= t)  # stage 3
    return order.index(["brushed", "grazed", "solid", "clean"][qc])


def analyse(path):
    order, qthr, stages = canon()
    rep = {"file": os.path.basename(path), "errors": [], "class_counts": {}}
    rows = []
    for line in io.open(path, encoding="utf-8"):
        line = line.strip()
        if not line.startswith("C|"):
            continue
        p = line.split("|")
        rows.append(tuple(int(x) for x in p[1:8]))
    rep["markers"] = len(rows)
    if not rows:
        rep["errors"].append("no markers")
        return rep

    # The pipeline's stage order must still be the one this analyzer assumes.
    if [s[2] for s in stages] != ["whiffed", "dodged", "blocked", "dispatch_quality_bands"]:
        rep["errors"].append("collision_model pipeline order changed: %s" % stages)

    mismatch = 0
    first_bad = None
    for idx, tick, cls, q1, q2, q3, qa in rows:
        exp = expected(order, qthr, q1 / Q, q2 / Q, q3 / Q, qa / Q)
        name = order[cls] if 0 <= cls < len(order) else "OUT_OF_RANGE(%d)" % cls
        rep["class_counts"][name] = rep["class_counts"].get(name, 0) + 1
        if exp != cls:
            mismatch += 1
            if first_bad is None:
                first_bad = {"idx": idx, "tick": tick, "got": name,
                             "expected": order[exp], "inputs": [q1, q2, q3, qa]}
    rep["verdict_mismatches"] = mismatch
    if mismatch:
        rep["errors"].append("%d rows disagree with the canonical pipeline" % mismatch)
        rep["first_mismatch"] = first_bad

    # Criterion A.5: every class must be REACHABLE, or the pipeline is untested there.
    missing = [k for k in order if k not in rep["class_counts"]]
    rep["classes_reached"] = len(rep["class_counts"])
    if missing:
        rep["errors"].append("classes never reached in this run: %s" % missing)

    # Rule 13: a non-overlapping sweep may never produce a landed class.
    landed = {"clean", "solid", "grazed", "brushed"}
    bad_miss = sum(1 for _, _, cls, q1, _, _, _ in rows
                   if q1 / Q < WHIFF_RATE and order[cls] in landed)
    rep["miss_classified_as_hit"] = bad_miss
    if bad_miss:
        rep["errors"].append("Rule 13 violated: %d visible misses classified as landed" % bad_miss)

    # Rule 13 tier order: an evading defender must never be recorded as blocking.
    bad_rank = sum(1 for _, _, cls, q1, q2, _, _ in rows
                   if q1 / Q >= WHIFF_RATE and q2 / Q < EVADE_RATE and order[cls] != "dodged")
    rep["evasion_outranked_by_guard"] = bad_rank
    if bad_rank:
        rep["errors"].append("Rule 13 tier order violated in %d rows: an active evasion did not "
                             "outrank guard interception" % bad_rank)
    rep["ok"] = not rep["errors"]
    return rep


if __name__ == "__main__":
    all_ok = True
    for p in sys.argv[1:]:
        rp = analyse(p)
        all_ok &= rp["ok"]
        print(json.dumps(rp, indent=1, sort_keys=True))
    sys.exit(0 if all_ok else 1)
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 08:26 UTC | END ]
