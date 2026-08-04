# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 03:42 UTC | START ]
"""Phase H marker contract and analyzer - built and proven BEFORE the C++ runs.

The established discipline (Decision 0012: it carries to C++ unchanged): the
analyzer exists first, is mutation-proven against synthetic streams, and only
then does an implementation get to produce evidence. This file IS the contract
the UppercutCore scaffold must satisfy.

Phase H proves the C++ PIPELINE, not new boxing: canon file in, deterministic
arithmetic, marker stream out, byte-identical across same-seed runs and a full
rebuild. The computation is the Phase D hysteresis walk - already proven in the
Python reference and the Blueprint VM - so a pass makes the same rule's third
independent implementation, from the same canon bytes.

Everything is INTEGER arithmetic, so C++ and Python cannot drift in a float
tail: an explicit 32-bit LCG drives fixed-point distances, band bounds quantize
to 1e-4 reach units at load, and the stream self-hashes with FNV-1a 64.

The contract (one marker file per run):

    H|canon_sha256=<sha256 hex of data/movement_model.json, exact bytes>
    H|seed=<uint32>
    H|steps=<N>
    R|<i>|<x>|<dist_q>|<band>          one per step, i from 0
    S|rows=<N>|transitions=<T>|fnv1a64=<hex16>

  - x_{i} is the LCG draw used at step i: x = (1664525*x + 1013904223) mod 2^32
    seeded from H|seed before step 0.
  - dist_q = x mod 60001  (0..6.0000 reach units in 1e-4 fixed point).
  - band starts at 2 and moves AT MOST one band per step by the canonical
    hysteresis rule over quantized bounds: leave only when dist_q exits
    [bmin_q[band] - hyst_q, bmax_q[band] + hyst_q]; a null max_ru is 99 ru.
  - fnv1a64 runs over the UTF-8 bytes of every R line including its '\\n'
    (offset 14695981039346656037, prime 1099511628211).

Usage: python analyze_core_scaffold.py <markers.txt> [...]
"""
import hashlib
import io
import json
import os
import sys

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

LCG_A, LCG_C, LCG_M = 1664525, 1013904223, 2 ** 32
DIST_MOD = 60001                 # 0..6.0000 ru in 1e-4 fixed point
START_BAND = 2                   # same opening band as the reference engine
FNV_OFFSET, FNV_PRIME = 14695981039346656037, 1099511628211
CANON_FILE = os.path.join(REPO, "data", "movement_model.json")


def fnv1a64(data: bytes) -> int:
    h = FNV_OFFSET
    for b in data:
        h = ((h ^ b) * FNV_PRIME) % (2 ** 64)
    return h


def canon_quantized():
    raw = io.open(CANON_FILE, "rb").read()
    mv = json.loads(raw.decode("utf-8"))
    rb = mv["range_bands"]
    bmin_q = [round(float(b["min_ru"]) * 10000) for b in rb["bands"]]
    bmax_q = [990000 if b.get("max_ru") is None else round(float(b["max_ru"]) * 10000)
              for b in rb["bands"]]
    hyst_q = round(float(rb["hysteresis_ru"]) * 10000)
    return bmin_q, bmax_q, hyst_q, hashlib.sha256(raw).hexdigest()


def expected_stream(seed: int, steps: int) -> str:
    """The whole marker file the contract demands, computed from canon alone.
    This is what the C++ scaffold must reproduce byte for byte - and it is also
    how the tests build their synthetic streams, so the analyzer is proven
    against the same bytes it will later judge."""
    bmin_q, bmax_q, hyst_q, sha = canon_quantized()
    lines = [f"H|canon_sha256={sha}", f"H|seed={seed}", f"H|steps={steps}"]
    rlines = []
    x = seed % LCG_M
    band = START_BAND
    transitions = 0
    for i in range(steps):
        x = (LCG_A * x + LCG_C) % LCG_M
        dist_q = x % DIST_MOD
        lo = bmin_q[band] - hyst_q
        hi = bmax_q[band] + hyst_q
        nxt = band + (1 if dist_q > hi else 0) - (1 if dist_q < lo else 0)
        nxt = max(0, min(len(bmin_q) - 1, nxt))
        if nxt != band:
            transitions += 1
        band = nxt
        rlines.append(f"R|{i}|{x}|{dist_q}|{band}")
    h = fnv1a64("".join(l + "\n" for l in rlines).encode("utf-8"))
    lines += rlines
    lines.append(f"S|rows={steps}|transitions={transitions}|fnv1a64={h:016x}")
    return "\n".join(lines) + "\n"


def analyse(path: str) -> dict:
    rep = {"file": os.path.basename(path), "errors": [], "notes": []}
    text = io.open(path, encoding="utf-8").read()
    lines = [l for l in text.splitlines() if l]
    heads = {l.split("=", 1)[0][2:]: l.split("=", 1)[1]
             for l in lines if l.startswith("H|") and "=" in l}
    for need in ("canon_sha256", "seed", "steps"):
        if need not in heads:
            rep["errors"].append(f"missing header H|{need}=")
    if rep["errors"]:
        rep["ok"] = False
        return rep

    seed, steps = int(heads["seed"]), int(heads["steps"])
    rep["seed"], rep["steps"] = seed, steps

    # The whole stream, recomputed from canon and compared byte for byte. A
    # constant-emitting implementation, a drifted LCG, a float somewhere in the
    # band arithmetic - all of them land here as the first differing line.
    expect = expected_stream(seed, steps)
    if text != expect:
        for n, (got, want) in enumerate(zip(text.splitlines(), expect.splitlines()), 1):
            if got != want:
                rep["errors"].append(
                    f"stream diverges from canon recomputation at line {n}: "
                    f"got {got!r}, expected {want!r}")
                break
        else:
            rep["errors"].append(
                f"stream length differs from canon recomputation: "
                f"{len(text.splitlines())} lines vs {len(expect.splitlines())}")

    # Independent property checks - deliberately NOT derived from
    # expected_stream, so a bug in the recomputation cannot vouch for itself.
    bmin_q, bmax_q, hyst_q, sha = canon_quantized()
    if heads["canon_sha256"] != sha:
        rep["errors"].append("canon_sha256 does not match the local "
                             "data/movement_model.json - the run consumed different canon")
    rrows = []
    for l in lines:
        if l.startswith("R|"):
            p = l.split("|")
            rrows.append((int(p[1]), int(p[2]), int(p[3]), int(p[4])))
    rep["rows"] = len(rrows)
    if len(rrows) != steps:
        rep["errors"].append(f"{len(rrows)} R rows for a declared {steps} steps")
    if [r[0] for r in rrows] != list(range(len(rrows))):
        rep["errors"].append("R indices are not 0..N-1 in order")
    if len({r[2] for r in rrows}) < 2 and len(rrows) > 4:
        rep["errors"].append("distance column is constant - dead column")
    jumps = sum(1 for a, b in zip(rrows, rrows[1:]) if abs(b[3] - a[3]) > 1)
    if jumps:
        rep["errors"].append(f"{jumps} band moves of more than one band in a step")
    transitions = sum(1 for a, b in zip(rrows, rrows[1:]) if b[3] != a[3])
    if transitions == 0 and len(rrows) > 4:
        rep["errors"].append("the band never changed - the hysteresis rule is untested "
                             "by this run")
    slines = [l for l in lines if l.startswith("S|")]
    if len(slines) != 1:
        rep["errors"].append(f"{len(slines)} S trailer lines (want exactly 1)")
    else:
        trail = dict(kv.split("=") for kv in slines[0][2:].split("|"))
        blob = "".join(f"R|{i}|{x}|{d}|{b}\n" for i, x, d, b in rrows).encode("utf-8")
        if int(trail["fnv1a64"], 16) != fnv1a64(blob):
            rep["errors"].append("S trailer fnv1a64 does not hash the R lines - the "
                                 "stream does not vouch for its own bytes")
    rep["transitions"] = transitions
    rep["ok"] = not rep["errors"]
    return rep


if __name__ == "__main__":
    all_ok = True
    for p in sys.argv[1:]:
        r = analyse(p)
        all_ok &= r["ok"]
        print(json.dumps(r, indent=1, sort_keys=True))
    sys.exit(0 if all_ok else 1)
# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 03:42 UTC | END ]
