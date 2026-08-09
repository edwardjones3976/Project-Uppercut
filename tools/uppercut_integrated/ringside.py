# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 00:50 UTC | START ]
"""What a credible ringside observer could know. The broadcast fence, executable.

WHY THIS EXISTS. The council's elder-commentator brief states a hard rule:
"the commentator knows only what a credible ringside observer could know."
Commentary may not announce hidden RNG, exact internal condition values,
future actions, sealed judge scores, invisible CPU reasoning, or private
opponent state. It may infer - "that right hand looks slower" - and it may not
report - "his Reserve has dropped to 26.4%".

A rule like that is a promise until something enforces it. This module is the
enforcement: it takes the authoritative fight export and PROJECTS it down to
the observable, dropping everything a person in the third row could not have
seen. Anything written from this projection is safe by construction, because
the hidden material is not in the room.

WHAT IT DROPS, and why each one is hidden:

  D rows          the CPU's own reasoning - its strategic aim, its tactic, its
                  reason code. A fighter's intentions are the one thing nobody
                  at ringside can read, and the reason codes are the most
                  seductive material in the whole stream precisely because they
                  are so articulate. They are also the most dishonest thing a
                  broadcast could quote.
  exact numbers   Wind and Reserve are internal quantities. What a person sees
                  is a fighter breathing through his mouth, or hands drifting
                  down. So the projection converts them to CHANGE and to
                  coarse, human-scale observation - and never prints a number.
  sealed cards    unreadable until the panel closes, by the same rule that
                  governs the fight itself.
  the future      the projection is generated in order and never looks ahead.
                  A camera that leans toward a knockdown three seconds early
                  is foreknowledge, and everybody feels it even when nobody
                  can say why.

WHAT IT KEEPS. Everything a person could see: who threw what, whether it
landed, where it landed, whether the other man slipped it or it fell short,
head movement and when it came too early, knockdowns, the count, the rise,
the referee's intervention, the bell, and the result. Boxing's own vocabulary
is already in the stream - a punch missed "because the slip was still active"
is an observation, not a readout.
"""
import argparse
import io
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

# What the projection is allowed to carry through. Anything not named here is
# dropped, which is the fail-closed direction: a new event family is invisible
# to the broadcast until somebody decides it is observable and says so.
OBSERVABLE = ("punch", "window", "knockdown", "count", "rise", "stoppage",
              "round_end")

# Coarse, human-scale readings. A person at ringside does not measure; he
# notices that a man is blowing hard, or that his hands have come down.
WIND_READINGS = ((8000, "moving easily"), (6000, "working"),
                 (4000, "breathing hard"), (2000, "labouring"),
                 (0, "running on empty"))
DAMAGE_READINGS = ((7500, "badly marked up"), (5000, "showing real damage"),
                   (2500, "starting to wear it"), (0, "unmarked"))


def _read(table, value):
    for floor, phrase in table:
        if value >= floor:
            return phrase
    return table[-1][1]


def _name(who):
    return " ".join(w.capitalize() for w in str(who).split("_"))


def _move(move_id):
    parts = str(move_id or "punch").split("_")
    if len(parts) > 1 and parts[-1] in ("lead", "rear"):
        hand = parts.pop()
        return "%s %s" % (hand, " ".join(parts))
    return " ".join(parts)


def _clock(tick, round_ticks, tick_hz, round_no=None):
    """Elapsed time within the round, the way a broadcast clock reads.

    NOBODY IS SAVED BY THE BELL, so a count that starts at 2:54 finishes after
    the round has expired - and the first version of this function, which took
    `tick % round_ticks`, wrapped that count back to 0:02 and made a knockdown
    look like it happened at the start of the next round. The round number is
    authoritative (the bout defers the bell), so elapsed time is measured from
    the round's own start and is allowed to exceed three minutes. A clock
    reading 3:02 is the correct way to say "this is still round one, and the
    round should have ended eight seconds ago."
    """
    within = tick % round_ticks if round_no is None \
        else tick - (round_no - 1) * round_ticks
    seconds = max(0, within) // tick_hz
    return "%d:%02d" % (seconds // 60, seconds % 60)


def observable_events(fight):
    """The fight's events, filtered to what a person could have seen.

    Order is preserved and never re-sorted by outcome, because a broadcast
    that knows how the round ends before it starts is the foreknowledge
    problem wearing a filter's clothes.
    """
    return [e for e in fight.get("events", []) if e.get("kind") in OBSERVABLE]


def round_summaries(fight):
    """Per round: what was thrown, what arrived, and what the eye would catch.

    Counts are the honest kind - a person at ringside counts punches, and
    CompuBox has done exactly this for forty years. What this refuses to do is
    report a fraction of a resource nobody can see.
    """
    rounds = {}
    for e in observable_events(fight):
        r = rounds.setdefault(e["r"], {
            "thrown": {}, "landed": {}, "slipped": {}, "short": {},
            "knockdowns": {}, "windows": {}, "mistimed": {}, "counts": []})
        who = e.get("who")
        if e["kind"] == "punch":
            r["thrown"][who] = r["thrown"].get(who, 0) + 1
            if e.get("outcome") == "arrived":
                r["landed"][who] = r["landed"].get(who, 0) + 1
            elif e.get("outcome") == "dodged":
                r["slipped"][who] = r["slipped"].get(who, 0) + 1
            else:
                r["short"][who] = r["short"].get(who, 0) + 1
        elif e["kind"] == "window":
            if e.get("what") == "open":
                r["windows"][who] = r["windows"].get(who, 0) + 1
            elif e.get("what") == "mistimed":
                r["mistimed"][who] = r["mistimed"].get(who, 0) + 1
        elif e["kind"] == "knockdown":
            r["knockdowns"][who] = r["knockdowns"].get(who, 0) + 1
        elif e["kind"] == "count":
            r["counts"].append((e["r"], e.get("n")))
    return rounds


def condition_reads(fight, participants):
    """Coarse per-round readings of how each man LOOKS, never what he is.

    Taken from the last per-second sample inside each round, converted through
    the two phrase tables and never printed as a number. Two fighters at 41%
    and 39% wind both read "breathing hard", which is correct: that is the
    resolution a human eye actually has.
    """
    rt = fight["meta"]["round_ticks"]
    last = {}
    for s in fight.get("samples", []):
        last[s["r"]] = s
    reads = {}
    for r, s in sorted(last.items()):
        reads[r] = {}
        for i, who in enumerate(participants):
            reads[r][who] = (_read(WIND_READINGS, s["wind"][i]),
                             _read(DAMAGE_READINGS, s["dmg"][i]))
    return reads


def transcript(fight, beats=True):
    """A readable ringside account. Every line is something a person saw."""
    m = fight["meta"]
    P = m["participants"]
    rt, hz = m["round_ticks"], m["tick_hz"]
    out = []
    w = out.append

    w("RINGSIDE ACCOUNT - what a person in the building could have seen")
    w("=" * 66)
    w("%s vs %s, scheduled for %d rounds. Referee %s."
      % (_name(P[0]), _name(P[1]), m["rounds_planned"],
         m["referee"]["display_name"]))
    w("")

    rounds = round_summaries(fight)
    reads = condition_reads(fight, P)
    last_land = {}          # per round: when something last arrived

    for r in sorted(rounds):
        d = rounds[r]
        w("ROUND %d" % r)
        w("-" * 66)
        if beats:
            # A broadcast does not narrate a thing that happens twice a
            # second; it names the pattern once and moves on. The first
            # generated transcript of seed 4242 was 186 lines of "moves his
            # head to nothing", which is both unreadable AND the most
            # interesting thing in the fight - so it is reported as what it
            # is: a habit, counted, not an event list.
            mistimes = sum(d["mistimed"].values())
            if mistimes:
                # TERMINOLOGY, corrected by the elder commentator: this line
                # used to say "feinting at ghosts", and a feint is OFFENSE -
                # a lie you tell to draw a reaction. Two men slipping at
                # punches nobody threw are doing the opposite of feinting.
                # "In the gym you'd say they're jumpy, or working on air."
                w("  Both men are jumpy - %d pieces of head movement this "
                  "round came to nothing. They are working on air."
                  % mistimes)
            for e in observable_events(fight):
                if e["r"] != r:
                    continue
                if e["kind"] == "window":
                    continue        # counted above, not narrated
                t = _clock(e["t"], rt, hz, e["r"])
                who = _name(e.get("who", ""))
                if e["kind"] == "punch":
                    # THE DEFECT THE ELDER COMMENTATOR CAUGHT, in his words:
                    # "not one landed punch appears in the ringside account -
                    # a fight where you see men fall down but never see
                    # anybody get hit is not a broadcast, it's a rumor."
                    # He was right and the fence was drawn in the wrong place:
                    # landed punches were counted into the round summary and
                    # never narrated, so the timeline showed only misses and
                    # knockdowns. A broadcast does not call all 118 landed
                    # punches either - it SELECTS. So: the first punch to land
                    # in a round, anything landing after a lull, and the last
                    # thing to land before a man goes down.
                    if e.get("outcome") != "arrived":
                        continue
                    gap = e["t"] - last_land.get(e["r"], -10 ** 9)
                    opening = e["r"] not in last_land
                    last_land[e["r"]] = e["t"]
                    if opening:
                        w("  %s  %s opens the round - the %s lands %s."
                          % (t, who, _move(e.get("move")),
                             "to the body" if e.get("target") == "body"
                             else "upstairs"))
                    elif gap >= hz * 8:
                        w("  %s  %s breaks the lull - %s, %s."
                          % (t, who, _move(e.get("move")),
                             "downstairs" if e.get("target") == "body"
                             else "clean upstairs"))
                    continue
                if e["kind"] == "knockdown":
                    w("  %s  %s is DOWN, dropped by the %s."
                      % (t, who, _move(e.get("by"))))
                elif e["kind"] == "count":
                    if e.get("n") in (1, 5, 8, 10):
                        w("  %s  the count reaches %s." % (t, e.get("n")))
                elif e["kind"] == "rise":
                    w("  %s  %s is up at %s." % (t, who, e.get("at")))
                elif e["kind"] == "stoppage":
                    w("  %s  the referee steps in. It is over." % t)
        for who in P:
            thrown = d["thrown"].get(who, 0)
            landed = d["landed"].get(who, 0)
            slipped = d["slipped"].get(who, 0)
            short = d["short"].get(who, 0)
            pct = (landed * 100 // thrown) if thrown else 0
            look = reads.get(r, {}).get(who, ("", ""))
            w("  %-13s threw %3d, landed %3d (%d%%); %d slipped, %d fell "
              "short. Head movement %d times, %d of it early. He looks %s "
              "and %s."
              % (_name(who), thrown, landed, pct, slipped, short,
                 d["windows"].get(who, 0), d["mistimed"].get(who, 0),
                 look[0], look[1]))
        w("")
    return "\n".join(out)


def result_paragraph(fight):
    """The finish and the cards - and the cards only because it is over."""
    m = fight["meta"]
    r = m.get("result") or {}
    out = []
    method = r.get("method", "?")
    if method in ("KO", "TKO"):
        out.append("%s by %s at %s of round %d (%s)."
                   % (_name(r.get("winner")), method,
                      _clock(r.get("tick", 0), m["round_ticks"], m["tick_hz"],
                             r.get("round")),
                      r.get("round", 0), r.get("detail", "")))
    else:
        out.append("It goes to the cards: %s%s."
                   % (method, "" if not r.get("winner")
                      else ", " + _name(r["winner"])))
    for judge, card in sorted((fight.get("cards") or {}).items()):
        out.append("  %-16s %s-%s" % (_name(judge), card["totals"][0],
                                      card["totals"][1]))
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Project an exported fight down to what ringside could see.")
    ap.add_argument("fight_json")
    ap.add_argument("--out", default=None)
    ap.add_argument("--no-beats", action="store_true",
                    help="round summaries only, no moment-by-moment lines")
    args = ap.parse_args(argv)

    fight = json.load(io.open(args.fight_json, encoding="utf-8"))
    text = (transcript(fight, beats=not args.no_beats) + "\n"
            + result_paragraph(fight) + "\n")
    if args.out:
        io.open(args.out, "w", encoding="utf-8", newline="\n").write(text)
        print("wrote %s (%d lines)" % (args.out, text.count("\n")))
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 00:50 UTC | END ]
