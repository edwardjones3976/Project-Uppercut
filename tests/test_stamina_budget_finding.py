# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 11:25 UTC | START ]
"""Gate G7's evidence, pinned so it cannot drift quietly in either direction.

The finding: canon's pool, regeneration rate and punch costs together pay for
about 19 punches in a round, against a professional 55-78. Fighters therefore
spend eleven of every twelve minutes at 1% stamina, and `1.4 - stamina_fraction`
is - with force - one of only two terms in Rule 14's pressure product that
discriminate between a landing that knocks a man down and one that does not.
Accumulated damage, balance and guard do not.

These tests do not assert that the numbers are RIGHT. They assert that the
numbers are what the decision packet says they are, so that:

  - if canon moves, the packet stops being true and this says so;
  - if someone "fixes" the knockdown model instead of the economy, the term
    ratios change and this says so;
  - when the Director rules on G7, these fail, and the packet, the development
    log and the Phase O record get rewritten in the same commit as the ruling.

Packet: docs/plans/2026-08-06-the-stamina-economy-decision-packet.md
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools", "engine"))
sys.path.insert(0, ROOT)

import analyze_core_round as O  # noqa: E402

PROFESSIONAL_VOLUME_LOW = 55


def test_a_round_of_resting_does_not_pay_for_a_round_of_boxing():
    """The arithmetic at the centre of G7. No simulation needed."""
    c = O.canon_pack()
    regen_round = c["regen"] * c["round_ticks"]
    costs = [c["moves"][p]["cost"] for p in O.PUNCHES]
    mean_punch = sum(costs) // len(costs)
    affordable = regen_round / mean_punch
    assert affordable < 25, (
        "a round of pure resting now pays for %.1f punches. If canon changed, "
        "gate G7's packet is out of date and must be re-run, not re-read."
        % affordable)
    shortfall = (PROFESSIONAL_VOLUME_LOW * mean_punch) / regen_round
    assert shortfall > 2.0, "the shortfall is %.1fx" % shortfall


def test_stamina_is_the_only_term_that_discriminates_at_a_knockdown():
    """The measurement that sent the fourth investigation away from Rule 14.

    Force, accumulated damage, balance and guard are the SAME at a landing that
    fires as at one that does not. If that ever stops being true, the diagnosis
    in the G7 packet no longer holds and the packet needs rewriting before
    anybody acts on it.
    """
    c = O.canon_pack()
    thr = c["kd_threshold"]
    cols = {k: ([], []) for k in ("force", "cond", "stam", "bal", "guard")}
    idx = {"force": 7, "cond": 8, "stam": 9, "bal": 10, "guard": 11}
    for seed in (4242, 4243):
        for line in O.expected_stream(seed, 1, with_floats=False,
                                      with_terms=True).splitlines():
            if not line.startswith("E|"):
                continue
            f = line.split("|")
            fired = int(f[5]) >= thr
            for k, i in idx.items():
                cols[k][1 if fired else 0].append(int(f[i]))

    def med(xs):
        return sorted(xs)[len(xs) // 2] if xs else 0

    assert cols["stam"][1], "no eligible landing fired; nothing to compare"
    ratios = {k: (med(v[1]) / med(v[0]) if med(v[0]) else 0)
              for k, v in cols.items()}
    # THREE terms must not discriminate. Accumulated damage at ~1.02 is its own
    # finding and is recorded in the packet: a knockdown here is a single-punch
    # event, not a man breaking down from what he has taken.
    for k in ("cond", "bal", "guard"):
        assert 0.9 < ratios[k] < 1.1, (
            "%s now discriminates at a knockdown (ratio %.2f). The G7 diagnosis "
            "says only force and stamina do - re-run the packet before acting "
            "on it." % (k, ratios[k]))
    # TWO must. Force discriminating is a hard punch being a hard punch, which
    # is correct. Stamina discriminating is a fighter who has been on the floor
    # since minute one, which is the gate.
    #
    # The first draft of this test asserted force did NOT discriminate, because
    # the packet said so, because at eight bouts its medians coincided at 7124
    # on both sides of the threshold. The test caught the overclaim inside an
    # hour. That is what these are for.
    for k in ("force", "stam"):
        assert ratios[k] > 1.1, (
            "%s has stopped discriminating (ratio %.2f). Either the economy was "
            "fixed - in which case rewrite the packet and this test together - "
            "or something is wrong with the pressure product."
            % (k, ratios[k]))


def test_the_packet_survives_its_own_ruling():
    """Rewritten 2026-08-06, the same day the Director closed G7.

    This test used to assert that G7 was OPEN, and the docstring at the top of
    this file predicted its own death: "when the Director rules on G7, these
    fail, and the packet, the development log and the Phase O record get
    rewritten in the same commit as the ruling." Decision 0021 ruled - Wind over
    Reserve - so the guard fired exactly as designed and is rewritten rather than
    deleted.

    What it now holds is the thing that can still rot: a ruling must not orphan
    the evidence that produced it. The packet is what makes Decision 0021
    auditable by someone who was not here, so the packet has to outlive the gate.
    """
    packet = os.path.join(ROOT, "docs", "plans",
                          "2026-08-06-the-stamina-economy-decision-packet.md")
    assert os.path.exists(packet), (
        "the G7 evidence packet is gone. Decision 0021 cites it; a decision "
        "whose evidence has been deleted is an assertion.")
    gates = open(os.path.join(ROOT, "docs", "decisions", "OPEN_GATES.md"),
                 encoding="utf-8").read()
    assert "G7" in gates, "a gate row is edited to CLOSED, never deleted"
    ruling = os.path.join(ROOT, "docs", "decisions",
                          "0021-two-tier-stamina-economy.md")
    assert os.path.exists(ruling), "G7's closure names Decision 0021"


def test_the_two_tier_economy_has_not_yet_reached_the_frozen_contracts():
    """Decision 0021 is authored but deliberately not yet wired in.

    The two tests above measure the SINGLE-tier economy in
    `condition_model.stamina`, which is still what the frozen Phase N/O
    contracts read. Decision 0022 freezes those pins, so Wind and Reserve were
    authored as new canon beside the old block rather than as an edit to it.

    This test holds that separation. When the integrated contract starts reading
    the two-tier economy, the two tests above stop describing anything real and
    must be rewritten in the same commit - not left to pass on canon nothing
    uses any more, which is the quietest way for evidence to go stale.
    """
    import json

    econ = json.load(open(os.path.join(ROOT, "data", "stamina_economy.json"),
                          encoding="utf-8"))
    assert econ["authority"]["supersedes_for_integrated_contract"] == \
        "condition_model.stamina"
    assert econ["calibration_status"]["values_are_fitted"] is False, (
        "stamina_economy.json now claims fitted values. Decision 0021 step 7 "
        "forbids calibration until the integrated policy produces boxing-like "
        "cadence - and the moment it is fitted, the two tests above are "
        "measuring the wrong economy.")
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 11:25 UTC | END ]
