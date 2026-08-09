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
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 09:20 UTC | START edit: Decision 0026 ]
# v2, not v1. Decision 0026 changed what this contract DECLARES: the substream
# inventory is now hierarchical and the initial state names its participants.
# Every derived seed moves as a result, which is the correct consequence and
# costs nothing today because no integrated artifact has been pinned. It would
# cost a re-prove of every integrated stream a week from now, so the version
# moves while the move is free.
STREAM_PHASE = "INTEGRATED"
# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-09 10:28 UTC | START edit: v3 - the ruleset fought under is part of the fight's identity ]
# v3, not v2, for the same reason v2 was not v1: what the contract DECLARES
# changed. Decision 0033 Ruling 2 makes the ruleset the authority on how a
# contest may end, so two bouts under different rulesets are different
# contests and must not share a contract identity. The ruleset file actually
# fought under enters the declared canon list and the header names it. Every
# derived seed moves, which is the correct consequence and is free today for
# the same reason it was free at v2: no integrated artifact has been pinned.
CONTRACT = "uppercut-integrated-v3"
DEFAULT_RULESET = "professional"
# [ ... | 2026-08-09 10:28 UTC | END edit ]

# The bout's stable authority identities. Corner names rather than "fighter_0"
# and "fighter_1" on purpose: a slot number is one careless refactor away from
# being an array index, and Decision 0026 says runtime array position is not
# authority.
DEFAULT_PARTICIPANTS = ("red_corner", "blue_corner")
# [ ... | 2026-08-08 09:20 UTC | END edit ]

# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 00:30 UTC | START edit: Phase R enters the bout ]
# The integrated contract's own declared vocabulary. The frozen phases each
# declare these as literal tuples inside their analyzers - `REGIONS` and
# `PUNCHES` live in `analyze_core_condition` - and the integrated package may
# not import a phase analyzer, so it declares its own.
#
# That is a fork, and it is a fork with a guard rather than a shrug:
# `tests/test_evasion_in_the_bout.py` asserts these match the frozen phases'
# vocabulary today, so the day they diverge it is a visible test failure rather
# than two systems quietly disagreeing about what a body is.
REGIONS = ("head", "jaw_chin", "torso_upper", "torso_lower",
           "arm_left", "arm_right")
PUNCHES = ("jab_lead", "cross_rear", "hook_lead", "uppercut_rear",
           "body_straight_rear")
# [ ... | 2026-08-09 00:30 UTC | END edit ]

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

    __slots__ = ("seed", "rounds", "round_ticks", "participants")

    def __init__(self, seed, rounds=12, round_ticks=180 * 60,
                 participants=DEFAULT_PARTICIPANTS):
        if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0:
            raise ValueError("bout seed must be a non-negative integer, got %r"
                             % (seed,))
        if rounds <= 0 or round_ticks <= 0:
            raise ValueError("a bout needs at least one round of at least one "
                             "tick, got rounds=%r round_ticks=%r"
                             % (rounds, round_ticks))
        self.seed, self.rounds, self.round_ticks = seed, rounds, round_ticks
        # [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) |
        #   2026-08-08 09:20 UTC | START edit: Decision 0026 ]
        # Participants are part of the DECLARED initial state, which is what
        # makes "runtime array position is not authority" enforceable rather
        # than aspirational: the identity a stream is derived from comes out of
        # the contract, and the runtime's list order can never reach it.
        self.participants = tuple(participants)
        if len(self.participants) < 2:
            raise ValueError("a bout needs at least two participants, got %r"
                             % (self.participants,))
        if len(set(self.participants)) != len(self.participants):
            raise ValueError("participant identities must be unique, got %r"
                             % (self.participants,))
        for who in self.participants:
            if not isinstance(who, str) or not who or "|" in who \
                    or R.SCOPE_SEPARATOR in who:
                raise ValueError(
                    "participant identity %r is not a stable name: it must be "
                    "a non-empty string containing neither '|' (which would "
                    "break the header row shape) nor %r (which would let two "
                    "different owners spell one stream)."
                    % (who, R.SCOPE_SEPARATOR))
        # [ ... | 2026-08-08 09:20 UTC | END edit ]

    def header_lines(self):
        return ["H|seed=%d" % self.seed,
                "H|rounds=%d" % self.rounds,
                "H|round_ticks=%d" % self.round_ticks,
                # Sorted: the header records WHO is in the bout, not the order
                # somebody listed them in.
                "H|participants=%s" % ",".join(sorted(self.participants))]


def rng_header_lines(bout_rng):
    """The substream derivation, in the stream itself.

    Decision 0022 requires the derivation be "recorded in replay metadata".
    Recording it in the marker stream is the strongest form of that: the
    evidence and the thing needed to reproduce it cannot then be separated,
    and a reader can tell which streams held authority without consulting
    another file.

    ONE VALUE PER LINE, and no '|' inside a value. An earlier draft of this
    emitted "H|rng_policy_intent=<seed>|authoritative", which survives the
    split("=", 1) the analyzers use for headers but gives that row three
    '|'-fields where every other header row has two. Nothing consumes the
    integrated stream yet, so it broke nothing - which is exactly why it was
    worth fixing now, while the format is still entirely ours to choose.
    """
    meta = bout_rng.replay_metadata()
    authoritative = [s["name"] for s in meta["substreams"] if s["authoritative"]]
    lines = ["H|rng_derivation=%s" % meta["derivation_version"],
             "H|rng_authoritative=%s" % ",".join(sorted(authoritative))]
    for s in meta["substreams"]:
        lines.append("H|rng_%s=%d" % (s["name"], s["seed"]))
    return lines


def header(repo, state, bout_rng=None, manifest=None,
           ruleset=DEFAULT_RULESET):
    """The integrated stream's full header, in one declared order.

    Order is fixed here rather than left to callers: two callers emitting the
    same facts in different orders would produce two artifacts that are equally
    true and not byte-identical, and byte-identity is the entire currency.

    [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-09 10:28 UTC
      | edit: the ruleset enters the declared canon ] Decision 0033 Ruling 2:
    the ruleset actually fought under is hashed with the rest of canon and
    named in the header, so two bouts under different rules can never share an
    evidence identity. Appended to the declared tuple rather than inserted,
    so the eleven existing entries keep their declared order.
    """
    rng = bout_rng or R.BoutRng(state.seed, CONTRACT, state.participants)
    canon = list(CANON) + [("ruleset", "data/rulesets/%s.json" % ruleset)]
    lines = ["H|phase=%s" % STREAM_PHASE,
             "H|contract=%s" % CONTRACT,
             "H|ruleset=%s" % ruleset]
    lines.extend(H.canon_header_lines(repo, canon, manifest=manifest))
    lines.extend(state.header_lines())
    lines.extend(rng_header_lines(rng))
    return lines


def new_bout(repo, seed, rounds=12, round_ticks=180 * 60, manifest=None,
             participants=DEFAULT_PARTICIPANTS, ruleset=DEFAULT_RULESET):
    """(initial state, its substreams, its header) - the three together.

    Returned as a unit because they are only meaningful together: a header
    without the streams it declares cannot be replayed, and streams without the
    header cannot be shown to belong to this contract.
    """
    state = InitialState(seed, rounds, round_ticks, participants)
    rng = R.BoutRng(state.seed, CONTRACT, state.participants)
    return state, rng, header(repo, state, rng, manifest=manifest,
                              ruleset=ruleset)
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 06:50 UTC | END ]
