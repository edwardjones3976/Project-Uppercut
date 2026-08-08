# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 06:50 UTC | START ]
"""The integrated bout's contract identity and stream header. Decision 0022.

Decision 0022 gives the live bout "its own contract identifier and schema
version, its own marker stream and golden evidence, its own initial-state
definition, its own ruleset and data hashes, its own integrated acceptance
criteria". This file is the first four; the acceptance criteria live in the
ruling and become tests as each subsystem lands.

WHAT THIS IS NOT. It is not a rewrite of any phase. N, Q, R, S and O keep their
pins as immutable unit-contract evidence, and nothing in this package is
imported by anything those pins were taken from. Integration adds a contract;
it does not reinterpret the old ones.

WHY THE CANON HEADER IS BORROWED AND NOT REBUILT. `uppercut_canon.header`
already emits the Decision 0023/0024 dual-hash block, and on 2026-08-07 six C++
artifacts were found still emitting a hand-rolled version of it - a divergence
that survived a day precisely because it had been written twice. The integrated
contract gets exactly one header builder, and it is the existing one.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)

from tools.uppercut_canon import header as H          # noqa: E402
from tools.uppercut_integrated import rng as R        # noqa: E402

# The contract's own identity. Decision 0022: new and versioned, never a
# re-blessing of a phase stream.
CONTRACT = "uppercut-integrated-v1"
STREAM_PHASE = "INTEGRATED"

# Every canon file the integrated bout reads, in a DECLARED order. Declared,
# because the header must not depend on dictionary iteration - the same rule
# Decision 0022 states for random ownership applies to evidence identity.
CANON = (
    ("movement", "data/movement_model.json"),
    ("condition", "data/condition_model.json"),
    ("guard", "data/guard_evasion_model.json"),
    ("cpu", "data/cpu_decision_model.json"),
    ("moves", "data/moves/generic_sandbox_moves.json"),
    ("effort", "data/moves/generic_sandbox_effort.json"),
    ("stamina", "data/stamina_economy.json"),
    ("animation", "data/animation_model.json"),
    ("collision", "data/collision_model.json"),
    ("pose", "data/pose_geometry.json"),
    ("punch", "data/punch_model.json"),
    ("clock", "data/clock_model.json"),
)


class InitialState(object):
    """What a bout starts as, declared rather than assumed.

    Decision 0022 requires the integrated contract to own its initial-state
    definition. Assertion 1 - "same seed and initial state reproduce
    byte-identically" - is only meaningful if the initial state is a thing the
    stream states, so it is written into the header and can be compared.
    """

    __slots__ = ("seed", "rounds", "round_ticks")

    def __init__(self, seed, rounds=12, round_ticks=180 * 60):
        if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0:
            raise ValueError("bout seed must be a non-negative integer, got %r"
                             % (seed,))
        if rounds <= 0 or round_ticks <= 0:
            raise ValueError("a bout needs at least one round of at least one "
                             "tick, got rounds=%r round_ticks=%r"
                             % (rounds, round_ticks))
        self.seed, self.rounds, self.round_ticks = seed, rounds, round_ticks

    def header_lines(self):
        return ["H|seed=%d" % self.seed,
                "H|rounds=%d" % self.rounds,
                "H|round_ticks=%d" % self.round_ticks]


def rng_header_lines(bout_rng):
    """The substream derivation, in the stream itself.

    Decision 0022 requires the derivation be "recorded in replay metadata".
    Recording it in the marker stream is the strongest form of that: the
    evidence and the thing needed to reproduce it cannot then be separated,
    and a reader can tell which streams held authority without consulting
    another file.
    """
    meta = bout_rng.replay_metadata()
    lines = ["H|rng_derivation=%s" % meta["derivation_version"]]
    for s in meta["substreams"]:
        lines.append("H|rng_%s=%d|%s" % (
            s["name"], s["seed"],
            "authoritative" if s["authoritative"] else "presentation"))
    return lines


def header(repo, state, bout_rng=None, manifest=None):
    """The integrated stream's full header, in one declared order.

    Order is fixed here rather than left to callers: two callers emitting the
    same facts in different orders would produce two artifacts that are equally
    true and not byte-identical, and byte-identity is the entire currency.
    """
    rng = bout_rng or R.BoutRng(state.seed, CONTRACT)
    lines = ["H|phase=%s" % STREAM_PHASE,
             "H|contract=%s" % CONTRACT]
    lines.extend(H.canon_header_lines(repo, list(CANON), manifest=manifest))
    lines.extend(state.header_lines())
    lines.extend(rng_header_lines(rng))
    return lines


def new_bout(repo, seed, rounds=12, round_ticks=180 * 60, manifest=None):
    """(initial state, its substreams, its header) - the three together.

    Returned as a unit because they are only meaningful together: a header
    without the streams it declares cannot be replayed, and streams without the
    header cannot be shown to belong to this contract.
    """
    state = InitialState(seed, rounds, round_ticks)
    rng = R.BoutRng(state.seed, CONTRACT)
    return state, rng, header(repo, state, rng, manifest=manifest)
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 06:50 UTC | END ]
