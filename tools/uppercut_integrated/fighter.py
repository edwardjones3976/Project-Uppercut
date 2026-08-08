# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 08:05 UTC | START ]
"""Wind and Reserve join the integrated fighter. Decision 0021, R4 step 4.

WHAT THIS ADDS, AND WHAT IT DELIBERATELY DOES NOT. It adds a place for a
fighter's two-tier stamina to live inside the integrated bout, and the one
translation from that state into what the policy is allowed to see. It adds no
economy rules whatsoever: every debit, every recovery, every saturation and the
corner's work all go through `tools.uppercut_stamina.economy`, which is the
implementation the C++ runtime is already proven byte-identical against.

That is the runtime convergence rule applied to a resource rather than to a
loop. A `FighterState` that recomputed even one of those rules would be a
second opinion about stamina, and second opinions in this repository agree
right up until one of them is edited.

THE SEAM THIS CLOSES. Before this file, `tools/engine/probe_policy_stamina.py`
built its own `Observation` from its own dict of fighter fields - a hand-rolled
answer to "what can a fighter see?" living in a harness. A harness may explore;
it may not own the definition of observability. `FighterState.observation()` is
now the single answer, and the probe consumes it.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from tools.uppercut_stamina import economy as E     # noqa: E402
from tools.uppercut_integrated import policy as P   # noqa: E402
from tools.uppercut_units import quantities as U    # noqa: E402


# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-08 22:10 UTC | START edit: Decision 0031 ]
def legacy_economy_travel(travel):
    """THE ONE PLACE a typed displacement becomes a raw integer.

    Director order, on the record: "Confine any raw-integer unwrap to one named
    legacy-economy adapter." The proven Wind/Reserve economy is integer-typed
    on the shared contract and byte-proven against the C++ port, so it does not
    change for this migration - but the moment more than one call site unwraps
    a `ReachUnits` to feed it, the type is a witness rather than an authority
    and any of those sites can quietly start passing a stride again.

    So: this function, or nothing. It takes a `ReachUnits` and only a
    `ReachUnits`, returns the raw q10000 integer the legacy economy charges,
    and exists solely so that deleting the legacy path later is the deletion of
    one name.
    """
    if travel is None:
        return 0
    if not isinstance(travel, U.ReachUnits):
        raise U.BasisError(
            "the legacy economy adapter takes ReachUnits, got %r. A raw "
            "integer here is a number with no basis, and a number with no "
            "basis is how a stride was billed as a displacement. Wrap actual "
            "travelled ground with quantities.displacement() first."
            % (travel,))
    return travel.q
# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-08 22:10 UTC | END edit ]


class Observable(object):
    """What one fighter can see of another, and there is nothing else on it.

    This exists so that leaking a hidden value becomes an edit to a declared
    list rather than a line buried in a call site. `Observation.__slots__`
    already refuses an unknown keyword, but that only catches a leak at the
    moment someone tries to pass it; this catches it at the moment someone
    tries to READ it, which is one step earlier and one step harder to argue
    with.

    Wind, Reserve, damage totals, the profile, the recent-decision reasons and
    the next intended action are all absent on purpose. A fighter reads breath
    off a man's shoulders, not off his gauge, and until this project models
    visible tells there is nothing here to read.
    """

    __slots__ = ("band", "committed", "recovering", "advancing",
                 "recent_moves", "on_ropes")

    def __init__(self, band, committed, recovering, advancing, recent_moves,
                 on_ropes):
        self.band = band
        self.committed = committed
        self.recovering = recovering
        self.advancing = advancing
        self.recent_moves = recent_moves
        self.on_ropes = on_ropes


class FighterState(object):
    """One fighter's authoritative state inside the integrated bout.

    Wind and Reserve are q10000 integers on the shared integer contract, and
    Reserve obeys Decision 0025: authoritative on the closed interval
    `[0, max]`, rejected rather than normalised when it arrives outside it.
    """

    __slots__ = ("id", "wind", "reserve", "profile", "band", "on_ropes",
                 "cornered", "recovery_ticks", "recent_moves", "failed_attacks",
                 "committed", "advancing", "damaged_regions", "hurt",
                 "punches_thrown", "recovery_seeking",
                 # [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) |
                 #   2026-08-08 13:40 UTC | START edit: authoritative position ]
                 # Position on the ring axis and the displacement still owed,
                 # both in q10000 reach units. These are AUTHORITATIVE: the
                 # band a punch is judged against is derived from them by the
                 # shared range core, not stored alongside them, so there is no
                 # second opinion about where a fighter is.
                 "pos", "pending")
                 # [ ... | 2026-08-08 13:40 UTC | END edit ]

    def __init__(self, fighter_id, economy, profile=None, band="mid"):
        # `fighter_id` is the STABLE PARTICIPANT IDENTITY from the contract's
        # initial state - "red_corner", not 0. Decision 0026: runtime array
        # position is not authority, and an integer id sitting next to a list
        # index is one careless refactor from becoming that index.
        if not isinstance(fighter_id, str) or not fighter_id:
            raise ValueError(
                "fighter identity must be a stable non-empty name such as "
                "'red_corner', got %r. Decision 0026 derives this fighter's "
                "private RNG stream from that name, so a positional id would "
                "make randomness depend on list order." % (fighter_id,))
        self.id = fighter_id
        self.wind = economy["wind_start"]
        self.reserve = economy["reserve_start"]
        self.profile = profile or P.Profile(preferred_band=band)
        self.band = band
        self.on_ropes = False
        self.cornered = False
        self.recovery_ticks = 0
        self.recent_moves = ()
        self.failed_attacks = 0
        self.committed = False
        self.advancing = False
        self.damaged_regions = ()
        self.hurt = False
        self.punches_thrown = 0
        self.recovery_seeking = False
        self.pos = 0
        self.pending = 0
        # Decision 0025's input rule applies to constructed state too, not only
        # to state that has been stepped. A fixture that starts a fighter
        # outside the interval is exactly the corrupt-save case the ruling
        # names.
        E.check_state(economy, self.wind, self.reserve)

    # ------------------------------------------------------------ observing --

    def observable(self):
        """This fighter as an opponent sees him."""
        return Observable(
            band=self.band,
            committed=self.committed,
            recovering=self.recovery_ticks > 0,
            advancing=self.advancing,
            recent_moves=tuple(self.recent_moves[-4:]),
            on_ropes=self.on_ropes,
        )

    def update_recovery_intent(self, economy):
        """The hysteresis, applied. Decision 0026 Ruling B.

        Two conditions and they are not each other's negation: dropping below
        the low line STARTS recovery-seeking, and only climbing back above the
        separately declared recovered line STOPS it. In between, the intent
        simply persists - which is what a boxer does and what a single
        threshold cannot express.

        Called once per tick before observing, so the observation reports an
        intent the fighter already held rather than one invented by the same
        tick that reads it.
        """
        if self.wind < economy["wind_low"]:
            self.recovery_seeking = True
        elif self.wind >= economy["wind_recovered"]:
            self.recovery_seeking = False
        return self.recovery_seeking

    def observation(self, economy, foe, round_number=1,
                    ticks_left_in_round=10800, incoming_attack=False):
        """The policy's view. The ONE translation from state to observability.

        `foe` may be a `FighterState` or an `Observable`; a `FighterState` is
        narrowed here rather than read directly, so there is no path by which
        this function can reach the opponent's Wind even by mistake.
        """
        seen = foe.observable() if isinstance(foe, FighterState) else foe
        if not isinstance(seen, Observable):
            raise TypeError(
                "an opponent is observed through Observable, got %r. Passing "
                "raw state here would make the leak a matter of discipline "
                "rather than of type." % type(seen))
        return P.Observation(
            wind_fraction=E.floordiv(self.wind * 10000, economy["wind_max"]),
            reserve_fraction=E.floordiv(self.reserve * 10000,
                                        economy["reserve_max"]),
            wind_is_low=self.wind < economy["wind_low"],
            wind_is_exhausted=self.wind < economy["wind_exhausted"],
            recovery_seeking=self.recovery_seeking,
            wind_is_recovered=self.wind >= economy["wind_recovered"],
            hands_available=("lead", "rear"),
            in_recovery=self.recovery_ticks > 0,
            recovery_ticks_left=self.recovery_ticks,
            damaged_regions=tuple(self.damaged_regions),
            hurt=self.hurt,
            range_band=self.band,
            preferred_band=self.profile.preferred_band,
            on_ropes=self.on_ropes,
            cornered=self.cornered,
            opponent_band=seen.band,
            opponent_committed=seen.committed,
            opponent_recovering=seen.recovering,
            opponent_advancing=seen.advancing,
            opponent_recent_moves=seen.recent_moves,
            opponent_on_ropes=seen.on_ropes,
            incoming_attack=incoming_attack,
            round_number=round_number,
            ticks_left_in_round=ticks_left_in_round,
            own_recent_moves=tuple(self.recent_moves[-4:]),
            consecutive_failed_attacks=self.failed_attacks,
        )

    # ------------------------------------------------------------- spending --

    def step(self, economy, action, move_id=None, displacement_ru=0,
             telemetry=None, travel=None):
        """One tick of the economy. Delegated whole, never restated.

        Decision 0031: `travel` is typed. It takes a `ReachUnits` produced by
        `quantities.displacement()` - actual ground covered, after the cap, the
        ring and the body clamp - or None for a tick that moved nothing. The
        raw integer the legacy economy needs is produced by
        `legacy_economy_travel`, the one named adapter, so the typed value is
        the authority and the unwrap is a single deletable seam rather than a
        habit. (`travel_ru=<int>` was the old spelling; it is gone rather than
        deprecated, so a caller with a bare number fails today instead of
        drifting for a month.)
        """
        self.wind, self.reserve = E.step(
            economy, self.wind, self.reserve, action, move_id=move_id,
            displacement_ru=displacement_ru, telemetry=telemetry,
            travel_ru=legacy_economy_travel(travel))
        return self.wind, self.reserve

    def between_rounds(self, economy):
        """The corner. Delegated whole, never restated."""
        self.wind, self.reserve = E.between_rounds(economy, self.wind,
                                                   self.reserve)
        return self.wind, self.reserve

    # -------------------------------------------------------------- bookkeeping

    def committed_to(self, move_id, recovery_ticks):
        """Record a punch actually thrown, with its recovery window."""
        self.recent_moves = tuple(self.recent_moves) + (move_id,)
        self.recovery_ticks = recovery_ticks
        self.failed_attacks = 0
        self.punches_thrown += 1
        self.committed = True

    def tick_recovery(self):
        if self.recovery_ticks > 0:
            self.recovery_ticks -= 1
        if self.recovery_ticks == 0:
            self.committed = False

    def wind_pct(self, economy):
        return self.wind * 100.0 / economy["wind_max"]

    def reserve_pct(self, economy):
        return self.reserve * 100.0 / economy["reserve_max"]
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 08:05 UTC | END ]
