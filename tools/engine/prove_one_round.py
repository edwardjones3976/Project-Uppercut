# [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 02:53 UTC | START ]
"""Prove a 1-round integrated bout with unique cards ends like boxing.

Python-side contract for the Unreal 1-round MVP (Decision 0022). Runs two
seeds with the default pair (test_pressure_power vs test_range_timing) and
requires:

  - each fighter carries a non-empty attribute card
  - the bout ends with a decision, count_expired, or stoppage (not a silent
    tick-budget death without cards)
  - decision_path_must_survive: not every seed is an R1 stoppage
  - cards differ on expressed in-round attributes (pair uniqueness)

C++ Play dumps are checked separately on Windows via prove_live_arena after
build. This module is the instrument that can run in CI / Linux cloud.
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from tools.uppercut_integrated.bout import IntegratedBout
from tools.uppercut_validate import fighter_pair as FP


def run_one(seed: int, round_seconds: int = 180) -> dict:
    bout = IntegratedBout(
        seed=seed,
        rounds=1,
        round_ticks=round_seconds * 60,
        fighter_cards="default_pair",
    )
    bout.run_fight()
    cards = {f.id: dict(f.attrs) for f in bout.fighters}
    return {
        "seed": seed,
        "result": dict(bout.result or {}),
        "tick": bout.tick,
        "kd": dict(bout.kd_bout),
        "cards": cards,
        "rows": len(bout.rows),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seeds", default="4242,777")
    ap.add_argument("--round-seconds", type=int, default=180)
    args = ap.parse_args(argv)

    pair_errs = FP.validate_default_pair()
    if pair_errs:
        print("FAIL pair uniqueness:", *pair_errs, sep="\n  ")
        return 1
    print("PASS pair uniqueness:", FP.DEFAULT_PAIR[0], "vs", FP.DEFAULT_PAIR[1])

    seeds = [int(s.strip()) for s in args.seeds.split(",") if s.strip()]
    results = []
    stoppages = 0
    for seed in seeds:
        r = run_one(seed, args.round_seconds)
        results.append(r)
        method = (r["result"] or {}).get("method") or ""
        detail = (r["result"] or {}).get("detail") or ""
        print("seed=%d tick=%d method=%s detail=%s kd=%s"
              % (seed, r["tick"], method, detail, r["kd"]))
        for fid, attrs in r["cards"].items():
            card_id = attrs.get("_card_id", "")
            if not card_id or len(attrs) < 10:
                print("FAIL fighter %s missing card attrs" % fid)
                return 1
        if not method:
            print("FAIL seed %d: no result method (tick-budget death without ending)"
                  % seed)
            return 1
        if method not in ("UD", "SD", "MD", "KO", "TKO", "DQ") and detail not in (
                "decision", "count_expired", "referee_judgement",
                "knockdown_limit"):
            # Accept integrated result vocabulary.
            if detail not in ("decision",) and "decision" not in detail:
                if method == "UD" or detail == "decision":
                    pass
                else:
                    print("FAIL seed %d: unrecognized ending %r / %r"
                          % (seed, method, detail))
                    return 1
        if detail != "decision" and method not in ("UD", "SD", "MD"):
            stoppages += 1

    if stoppages == len(seeds) and len(seeds) > 1:
        print("FAIL decision_path_must_survive: every seed stopped before cards")
        return 1

    print("PASS prove_one_round: %d seeds, stoppages=%d"
          % (len(seeds), stoppages))
    return 0


if __name__ == "__main__":
    sys.exit(main())
# [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 02:53 UTC | END ]
