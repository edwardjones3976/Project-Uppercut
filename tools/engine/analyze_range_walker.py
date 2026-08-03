# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 08:12 UTC | START ]
"""Non-vacuity and canon-conformance analysis for the BP_RangeWalker markers.

Byte-identical logs prove reproducibility. They do NOT prove the logic ran: a
Blueprint that emitted a constant would also be byte-identical, which is exactly
how the dead-accumulator defect hid during Phase B. So this checks four things
the hash cannot:

  1. Every column that should vary does vary (no dead columns).
  2. The band actually CHANGES during the run - otherwise the hysteresis rule is
     untested by the data even if it is present in the graph.
  3. Every band transition obeys hysteresis: the band only changes on the tick
     where the distance left [BandMin[band] - Hyst, BandMax[band] + Hyst].
  4. Every emitted quality class equals the canonical dispatch of its alignment.

Usage: python analyze_range_walker.py <markers.txt> [...]
"""
import io, json, os, sys

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
Q = 65536.0


def canon():
    mv = json.load(io.open(os.path.join(REPO, "data", "movement_model.json"), encoding="utf-8"))
    rb = mv["range_bands"]
    bmin = [float(b["min_ru"]) for b in rb["bands"]]
    bmax = [99.0 if b.get("max_ru") is None else float(b["max_ru"]) for b in rb["bands"]]
    col = json.load(io.open(os.path.join(REPO, "data", "collision_model.json"), encoding="utf-8"))
    qb = sorted(col["quality_bands"], key=lambda q: q["min_alignment"])
    return bmin, bmax, float(rb["hysteresis_ru"]), [float(q["min_alignment"]) for q in qb[1:]]


def rows(path):
    out = []
    for line in io.open(path, encoding="utf-8"):
        line = line.strip()
        if not line.startswith("R|"):
            continue
        p = line.split("|")
        out.append({"idx": int(p[1]), "tick": int(p[2]), "qdist": int(p[3]),
                    "band": int(p[4]), "qalign": int(p[5]), "qual": int(p[6])})
    return out


def analyse(path):
    bmin, bmax, hyst, qthr = canon()
    r = rows(path)
    rep = {"file": os.path.basename(path), "markers": len(r), "errors": [], "notes": []}
    if not r:
        rep["errors"].append("no markers")
        return rep

    for col in ("qdist", "band", "qalign", "qual"):
        distinct = len({x[col] for x in r})
        rep[col + "_distinct"] = distinct
        if distinct < 2:
            rep["errors"].append("column '%s' is constant across %d markers - dead column"
                                 % (col, len(r)))

    # Quality dispatch must equal the canonical tiling, row by row.
    bad_q = 0
    for x in r:
        a = x["qalign"] / Q
        expect = sum(1 for t in qthr if a >= t)
        if expect != x["qual"]:
            bad_q += 1
    rep["quality_mismatches"] = bad_q
    if bad_q:
        rep["errors"].append("%d rows where the emitted quality class disagrees with the "
                             "canonical dispatch of its alignment" % bad_q)

    # Hysteresis: per actor, walk consecutive ticks.
    changes = 0
    bad_h = 0
    per = {}
    for x in r:
        per.setdefault(x["idx"], []).append(x)
    for idx, seq in per.items():
        seq.sort(key=lambda x: x["tick"])
        for a, b in zip(seq, seq[1:]):
            d = b["qdist"] / Q
            lo = bmin[a["band"]] - hyst
            hi = bmax[a["band"]] + hyst
            expect = a["band"] + (1 if d > hi else 0) - (1 if d < lo else 0)
            expect = max(0, min(len(bmin) - 1, expect))
            if expect != b["band"]:
                bad_h += 1
            if b["band"] != a["band"]:
                changes += 1
    rep["band_changes"] = changes
    rep["hysteresis_violations"] = bad_h
    if changes == 0:
        rep["errors"].append("the band never changed - the hysteresis rule is present in the "
                             "graph but untested by this run")
    if bad_h:
        rep["errors"].append("%d band transitions disobey the hysteresis rule" % bad_h)
    rep["actors"] = sorted(per)
    rep["ok"] = not rep["errors"]
    return rep


if __name__ == "__main__":
    all_ok = True
    for p in sys.argv[1:]:
        rp = analyse(p)
        all_ok &= rp["ok"]
        print(json.dumps(rp, indent=1, sort_keys=True))
    sys.exit(0 if all_ok else 1)
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 08:12 UTC | END ]
