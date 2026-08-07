# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 04:30 UTC | START ]
"""Decision 0023 step 6: migrate the active phase headers exactly once.

    python -m tools.engine.migrate_canon_headers --capture   # BEFORE the change
    python -m tools.engine.migrate_canon_headers --verify    # AFTER it

The ruling is unambiguous about what makes this legitimate:

    all authoritative event rows remain byte-identical to the immediately
    preceding active pins; only the declared header/schema fields may change;
    any event-row divergence aborts migration and requires separate diagnosis.

So this is deliberately two commands with a code change in between. `--capture`
records the CURRENT streams while the old header is still being emitted;
`--verify` regenerates them afterwards and compares everything that is not a
header line. There is no single command that does both, because a tool that
captured its baseline after the change would be comparing the new world against
itself and would always pass.

An abort here is not a failure of the migration tooling. It means the header
change altered a fight, which is a real finding and belongs in a diagnosis
rather than in a re-blessed pin.
"""
import io
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "tools", "engine"))

BASELINE = os.path.join(REPO, "sandbox", "Saved", "premigration")

# (phase, module, callable args). These are the five ACTIVE streams Decision
# 0023 permits to move once. Nothing else may be touched by this migration.
PHASES = [
    ("N", "analyze_core_condition", (4242, 5400)),
    ("K", "analyze_render_probe", (4242, 5400)),
    ("O", "analyze_core_round", (4242, 1)),
    ("Q", "analyze_core_range", (4242, 5400)),
    ("R", "analyze_core_evade", (4242, 5400)),
]


def stream_for(module, args):
    mod = __import__(module)
    return mod.expected_stream(*args)


def is_header(line):
    """Header lines are the ONLY thing this migration is allowed to change.

    `H|` carries canon identity and run parameters. Everything else - B, K, M,
    Y rows describing canon, every event row, and the S trailer - is compared
    byte for byte. Being strict here is the point: if a canon-describing row
    moved, that is a canon change wearing a migration's clothes.
    """
    return line.startswith("H|")


def capture():
    if not os.path.isdir(BASELINE):
        os.makedirs(BASELINE)
    for phase, module, args in PHASES:
        text = stream_for(module, args)
        path = os.path.join(BASELINE, "phase_%s.stream" % phase)
        with io.open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)
        body = [l for l in text.splitlines() if not is_header(l)]
        print("captured %s  %d lines (%d non-header)"
              % (phase, len(text.splitlines()), len(body)))
    print("\nBaselines in %s" % BASELINE)
    print("Now make the header change, then run --verify.")
    return 0


def verify():
    failed = 0
    for phase, module, args in PHASES:
        path = os.path.join(BASELINE, "phase_%s.stream" % phase)
        if not os.path.exists(path):
            print("NO BASELINE for phase %s - run --capture before the change"
                  % phase)
            return 2
        before = io.open(path, encoding="utf-8", newline="").read().splitlines()
        after = stream_for(module, args).splitlines()

        b_body = [l for l in before if not is_header(l)]
        a_body = [l for l in after if not is_header(l)]

        if b_body == a_body:
            b_head = [l for l in before if is_header(l)]
            a_head = [l for l in after if is_header(l)]
            print("OK   phase %s  %d authoritative rows unchanged; "
                  "header %d -> %d lines"
                  % (phase, len(a_body), len(b_head), len(a_head)))
            continue

        failed = 1
        print("ABORT phase %s - an authoritative row moved." % phase)
        # Decision 0022: report the FIRST divergent authoritative event, not
        # only the fact that something moved.
        for i in range(max(len(b_body), len(a_body))):
            x = b_body[i] if i < len(b_body) else "<end of stream>"
            y = a_body[i] if i < len(a_body) else "<end of stream>"
            if x != y:
                print("  first divergence at authoritative row %d" % (i + 1))
                print("    before %s" % x)
                print("    after  %s" % y)
                break
        print("  Migration must not proceed. This is a diagnosis, not a re-bless.")

    print("\n%s" % ("MIGRATION CLEAN - no authoritative row moved" if not failed
                    else "MIGRATION ABORTED"))
    return failed


def main(argv):
    if "--capture" in argv:
        return capture()
    if "--verify" in argv:
        return verify()
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 04:30 UTC | END ]
