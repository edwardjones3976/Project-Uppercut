# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-14 09:35 UTC | START ]
"""Read an INTEGRATED_1R marker stream back and check it is a coherent fight.

WHY THIS IS NOT AN ANALYZER IN THE PHASE Q SENSE. Every other phase in this
repository is proven by an analyzer that PREDICTS the stream: the Python
contract emits the bytes, the C++ port must reproduce them, and byte-identity
is the proof. That order is inverted here on purpose. Decision 0040 R1 makes
the shared C++ `INTEGRATED_1R` session the combat authority and R2 makes Python
`IntegratedBout` reference-only, converging to C++ rather than the reverse. A
Python module that predicted these bytes would BE a second implementation of
the rules - exactly what the convergence rule exists to prevent - and it would
quietly become the authority the moment the two disagreed.

So this module concludes nothing about what the fight should be. It reads what
the fight said and checks the stream cannot be lying to itself:

  - the grammar is the grammar (row types, arity, field shapes);
  - ticks never run backwards;
  - a punch resolved is a punch that was thrown, by a fighter who decided to;
  - the trailer's counts are the rows' counts;
  - the verdict, the trailer and the knockdown rows tell the same story;
  - the 10-point-must card is arithmetically possible.

An internally coherent stream can still describe a bad fight. That judgement is
the Director's and this file does not make it. What this file makes impossible
is a stream whose trailer says one thing and whose rows say another - which is
the failure that would let real drift pass review unnoticed.

    python -m tools.engine.analyze_integrated_arena <stream> [...]

Pairs with `tools/engine/prove_integrated_arena.py`, which records the bytes
from Unreal and diffs them against the pins in `docs/phase1a/golden/`.
"""
import collections
import io
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

CONTRACT = "uppercut-integrated-v3"
PHASE = "INTEGRATED_1R"

# The count canon the round core emits against: mandatory eight, then a rise.
MANDATORY_COUNT = 8

# Row arity, counting the leading type field. Rows whose arity varies by shape
# carry None and are checked by hand below.
ARITY = {"H": None, "D": 6, "A": 4, "P": None, "K": 7, "N": None, "V": 7, "S": 9}


class Row(object):
    __slots__ = ("n", "raw", "f")

    def __init__(self, n, raw):
        self.n = n
        self.raw = raw
        self.f = raw.split("|")

    @property
    def kind(self):
        return self.f[0]

    def __repr__(self):
        return "line %d: %s" % (self.n, self.raw)


def _int(row, i, name, errors):
    try:
        return int(row.f[i])
    except (IndexError, ValueError):
        errors.append("line %d: %s is not an integer: %s" % (row.n, name, row.raw))
        return None


def _kv(field, key):
    """`key=value` -> value, or None if this is not that field."""
    if not field.startswith(key + "="):
        return None
    return field[len(key) + 1:]


def parse(text):
    """Split into rows. Refuses nothing; the checks are `analyse`'s job."""
    return [Row(i + 1, ln) for i, ln in enumerate(text.splitlines()) if ln]


def analyse(path_or_text):
    """Return {header, trailer, verdict, counts, errors}. Never raises on a
    malformed stream - a crash is a worse diagnostic than a list of faults."""
    if "\n" in path_or_text or "|" in path_or_text:
        text = path_or_text
    else:
        text = io.open(path_or_text, "r", encoding="utf-8", newline="").read()

    rows = parse(text)
    errors = []
    header = {}
    trailer = {}
    verdict = {}

    # Which moves are punches is a question about canon, and this file is not
    # allowed a second opinion about canon. So it asks the stream instead: a
    # move that ever resolves in a P row is a punch. A punch move that is
    # thrown and NEVER resolves anywhere in the file is invisible to this
    # derivation - the trailer's `punches` cross-check below is what catches
    # that case, which is why both checks exist.
    punch_moves = set(r.f[3] for r in rows if r.kind == "P" and len(r.f) > 3)

    if not rows:
        return {"header": header, "trailer": trailer, "verdict": verdict,
                "counts": {}, "errors": ["the stream is empty"], "rows": 0}

    # ---------------------------------------------------------------- header
    head = [r for r in rows if r.kind == "H"]
    if len(head) != 2:
        errors.append("expected exactly two H rows, found %d" % len(head))
    if head:
        for field in head[0].f[1:]:
            if "=" in field:
                k, v = field.split("=", 1)
                header[k] = v
        if header.get("phase") != PHASE:
            errors.append("line 1: phase is %r, expected %r"
                          % (header.get("phase"), PHASE))
        if header.get("contract") != CONTRACT:
            errors.append("line 1: contract is %r, expected %r"
                          % (header.get("contract"), CONTRACT))
        for key in ("seed", "ticks"):
            if key not in header:
                errors.append("line 1: the header does not declare %s" % key)
    if len(head) > 1:
        cards = _kv(head[1].f[1], "cards") if len(head[1].f) > 1 else None
        if cards is None or len([c for c in cards.split(",") if c]) != 2:
            errors.append("line 2: expected `H|cards=a,b`, got %r" % head[1].raw)
        else:
            header["cards"] = cards.split(",")
            if header["cards"][0] == header["cards"][1]:
                errors.append("line 2: both fighters carry the same card %r - "
                              "a bout needs two fighters" % header["cards"][0])
    if rows[0].kind != "H":
        errors.append("line 1: the stream does not open with a header")

    # --------------------------------------------------------------- ordering
    last_tick = -1
    for r in rows:
        if r.kind in ("H", "V", "S"):
            continue
        t = _int(r, 1, "tick", errors)
        if t is None:
            continue
        if t < last_tick:
            errors.append("line %d: tick %d runs backwards from %d"
                          % (r.n, t, last_tick))
        last_tick = t

    # ------------------------------------------------------------- the fight
    # A decision authorises an action; an action is what a punch resolves from.
    decided = {}          # participant -> tick of its most recent D row
    in_flight = {}        # fighter index -> [(tick, move), ...] thrown, unresolved
    thrown = collections.Counter()
    resolved = collections.Counter()   # outcome -> n
    kd_rows = collections.Counter()    # fighter index -> knockdowns
    per_fighter_landed = collections.Counter()
    counting = {"who": None, "n": 0}
    ids = list(header.get("cards", [])) and None  # participant ids come from D rows
    participants = []

    for r in rows:
        k = r.kind
        if k == "D":
            if len(r.f) != ARITY["D"]:
                errors.append("line %d: a D row is `D|tick|who|intent|move|reason`: %s"
                              % (r.n, r.raw))
                continue
            who = r.f[2]
            if who not in participants:
                participants.append(who)
            decided[who] = _int(r, 1, "tick", errors)
            if not r.f[5]:
                errors.append("line %d: a decision with no reason code: %s"
                              % (r.n, r.raw))
        elif k == "A":
            if len(r.f) != ARITY["A"]:
                errors.append("line %d: an A row is `A|tick|idx|action`: %s"
                              % (r.n, r.raw))
                continue
            idx = _int(r, 2, "fighter index", errors)
            if idx not in (0, 1):
                errors.append("line %d: fighter index %r is not 0 or 1"
                              % (r.n, r.f[2]))
                continue
            t = _int(r, 1, "tick", errors)
            move = r.f[3]
            if not move:
                errors.append("line %d: an action with no move: %s" % (r.n, r.raw))
            # An action must be authorised by a decision at the same tick.
            if idx < len(participants) and decided.get(participants[idx]) != t:
                errors.append("line %d: fighter %d acts at tick %s with no "
                              "decision at that tick: %s" % (r.n, idx, t, r.raw))
            if move in punch_moves:
                in_flight.setdefault(idx, []).append((t, move))
        elif k == "P":
            if len(r.f) < 5:
                errors.append("line %d: a P row needs at least "
                              "`P|tick|idx|move|outcome`: %s" % (r.n, r.raw))
                continue
            idx = _int(r, 2, "fighter index", errors)
            if idx not in (0, 1):
                errors.append("line %d: fighter index %r is not 0 or 1"
                              % (r.n, r.f[2]))
                continue
            move, outcome = r.f[3], r.f[4]
            if outcome not in ("landed", "evaded", "whiff_band"):
                errors.append("line %d: unknown punch outcome %r" % (r.n, outcome))
            if outcome == "landed":
                if len(r.f) != 6 or _kv(r.f[5], "force") is None:
                    errors.append("line %d: a landed punch must carry force=: %s"
                                  % (r.n, r.raw))
                else:
                    force = _kv(r.f[5], "force")
                    try:
                        if int(force) <= 0:
                            errors.append("line %d: a landed punch with force %s"
                                          % (r.n, force))
                    except ValueError:
                        errors.append("line %d: force is not an integer: %s"
                                      % (r.n, r.raw))
                per_fighter_landed[idx] += 1
            elif len(r.f) != 5:
                errors.append("line %d: a %s punch carries no extra fields: %s"
                              % (r.n, outcome, r.raw))
            resolved[outcome] += 1
            # The punch must have been thrown before it resolved.
            pending = in_flight.get(idx, [])
            match = None
            for i in range(len(pending) - 1, -1, -1):
                if pending[i][1] == move:
                    match = i
                    break
            if match is None:
                errors.append("line %d: fighter %d resolves %s that was never "
                              "thrown: %s" % (r.n, idx, move, r.raw))
            else:
                thrown[idx] += 1
                pending.pop(match)
        elif k == "K":
            if len(r.f) != ARITY["K"]:
                errors.append("line %d: a K row is `K|tick|idx|pressure=|"
                              "threshold=|round_kd=|bout_kd=`: %s" % (r.n, r.raw))
                continue
            idx = _int(r, 2, "fighter index", errors)
            press = _kv(r.f[3], "pressure")
            thresh = _kv(r.f[4], "threshold")
            if press is None or thresh is None:
                errors.append("line %d: a knockdown must show pressure and "
                              "threshold: %s" % (r.n, r.raw))
            else:
                try:
                    if int(press) < int(thresh):
                        errors.append("line %d: a knockdown below its own "
                                      "threshold (%s < %s)" % (r.n, press, thresh))
                except ValueError:
                    errors.append("line %d: pressure/threshold are not "
                                  "integers: %s" % (r.n, r.raw))
            if idx in (0, 1):
                kd_rows[idx] += 1
            if counting["who"] is not None:
                errors.append("line %d: a knockdown while fighter %s is already "
                              "being counted" % (r.n, counting["who"]))
            counting["who"] = idx
            counting["n"] = 0
        elif k == "N":
            if len(r.f) < 3:
                errors.append("line %d: a malformed N row: %s" % (r.n, r.raw))
                continue
            what = r.f[2]
            if what == "count":
                n = _int(r, 3, "count number", errors)
                if counting["who"] is None:
                    errors.append("line %d: a count with nobody down: %s"
                                  % (r.n, r.raw))
                elif n != counting["n"] + 1:
                    errors.append("line %d: the count goes %d -> %s"
                                  % (r.n, counting["n"], n))
                if n is not None:
                    counting["n"] = n
            elif what == "rise":
                if counting["who"] is None:
                    errors.append("line %d: a rise with nobody down: %s"
                                  % (r.n, r.raw))
                elif counting["n"] < MANDATORY_COUNT:
                    errors.append("line %d: fighter rises at %d, before the "
                                  "mandatory %d" % (r.n, counting["n"],
                                                    MANDATORY_COUNT))
                counting["who"] = None
                counting["n"] = 0
            else:
                errors.append("line %d: unknown N row %r" % (r.n, what))
        elif k == "V":
            if len(r.f) != ARITY["V"]:
                errors.append("line %d: a V row is `V|decision|winner|a|b|kd_a|"
                              "kd_b`: %s" % (r.n, r.raw))
                continue
            verdict = {"method": r.f[1],
                       "winner": _int(r, 2, "winner", errors),
                       "cards": [_int(r, 3, "card a", errors),
                                 _int(r, 4, "card b", errors)],
                       "kd": [_int(r, 5, "kd a", errors),
                              _int(r, 6, "kd b", errors)]}
        elif k == "S":
            for field in r.f[1:]:
                if "=" in field:
                    key, v = field.split("=", 1)
                    trailer[key] = v
        elif k != "H":
            errors.append("line %d: unknown row type %r" % (r.n, k))

    if counting["who"] is not None:
        errors.append("the stream ends with fighter %s on the canvas and no "
                      "rise or stoppage" % counting["who"])

    # -------------------------------------------------------------- trailers
    if rows[-1].kind != "S":
        errors.append("the stream does not end with a trailer")
    n_punch_rows = sum(resolved.values())
    unresolved = sum(len(v) for v in in_flight.values())

    def _t(key):
        try:
            return int(trailer.get(key, ""))
        except ValueError:
            return None

    t_punches, t_landed = _t("punches"), _t("landed")
    if t_landed is not None and t_landed != resolved["landed"]:
        errors.append("the trailer claims landed=%d; the stream has %d landed "
                      "punch rows" % (t_landed, resolved["landed"]))
    if t_punches is not None and t_punches != n_punch_rows + unresolved:
        errors.append("the trailer claims punches=%d; the stream resolves %d "
                      "and leaves %d in flight" % (t_punches, n_punch_rows,
                                                   unresolved))
    t_rows = _t("rows")
    if t_rows is not None and t_rows != len(rows) - 3:
        # rows = every row the session emitted: everything but the two H rows
        # and the S row itself.
        errors.append("the trailer claims rows=%d; the file carries %d "
                      "non-header rows" % (t_rows, len(rows) - 3))
    kd_field = trailer.get("kd", "")
    if "-" in kd_field:
        a, b = kd_field.split("-", 1)
        try:
            if (int(a), int(b)) != (kd_rows[0], kd_rows[1]):
                errors.append("the trailer claims kd=%s; the stream has %d and "
                              "%d knockdown rows" % (kd_field, kd_rows[0],
                                                     kd_rows[1]))
        except ValueError:
            errors.append("the trailer's kd field is not two integers: %r"
                          % kd_field)

    # ------------------------------------------------- the card must add up
    if verdict:
        cards_field = trailer.get("cards", "")
        if "-" in cards_field:
            a, b = cards_field.split("-", 1)
            try:
                if [int(a), int(b)] != verdict["cards"]:
                    errors.append("the verdict scores %s-%s and the trailer "
                                  "says %s" % (verdict["cards"][0],
                                               verdict["cards"][1], cards_field))
            except ValueError:
                pass
        ca, cb = verdict["cards"]
        if None not in (ca, cb):
            want = 0 if ca > cb else (1 if cb > ca else -1)
            if verdict["winner"] != want:
                errors.append("the verdict names winner %s on a %d-%d card"
                              % (verdict["winner"], ca, cb))
            # 10-point must: the fighter who wins the round takes 10 unless a
            # knockdown was scored against them.
            kda, kdb = verdict["kd"]
            if None not in (kda, kdb):
                if ca > cb and ca != 10 - kda:
                    errors.append("a 10-point-must round winner scores %d with "
                                  "%d knockdown(s) against" % (ca, kda))
                if cb > ca and cb != 10 - kdb:
                    errors.append("a 10-point-must round winner scores %d with "
                                  "%d knockdown(s) against" % (cb, kdb))
                if (kda, kdb) != (kd_rows[0], kd_rows[1]):
                    errors.append("the verdict counts %d/%d knockdowns; the "
                                  "stream has %d/%d" % (kda, kdb, kd_rows[0],
                                                        kd_rows[1]))
        if trailer.get("result") and trailer["result"] != verdict["method"]:
            errors.append("the trailer's result is %r and the verdict's method "
                          "is %r" % (trailer["result"], verdict["method"]))
    elif trailer.get("result") == "decision":
        errors.append("the trailer reports a decision with no V row")

    counts = {
        "rows": len(rows),
        "punch_rows": n_punch_rows,
        "unresolved_punches": unresolved,
        "landed": resolved["landed"],
        "evaded": resolved["evaded"],
        "whiff_band": resolved["whiff_band"],
        "knockdowns": [kd_rows[0], kd_rows[1]],
        "landed_by_fighter": [per_fighter_landed[0], per_fighter_landed[1]],
        "participants": participants,
    }
    return {"header": header, "trailer": trailer, "verdict": verdict,
            "counts": counts, "errors": errors, "rows": len(rows)}


def describe(line):
    """One row, in words. A diff nobody can read is a hash with extra steps."""
    f = line.split("|")
    k = f[0]
    if k == "D":
        return ("tick %s: %s decides %s%s (%s)"
                % (f[1], f[2], f[3], (" " + f[4]) if f[4] else "", f[5]))
    if k == "A":
        return "tick %s: fighter %s does %s" % (f[1], f[2], f[3])
    if k == "P":
        if f[4] == "landed":
            return ("tick %s: fighter %s LANDS %s (%s)" % (f[1], f[2], f[3], f[5]))
        if f[4] == "evaded":
            return "tick %s: fighter %s throws %s and it is slipped" % (f[1], f[2], f[3])
        return "tick %s: fighter %s throws %s from the wrong band" % (f[1], f[2], f[3])
    if k == "K":
        return ("tick %s: fighter %s KNOCKED DOWN (%s vs %s)"
                % (f[1], f[2], f[3], f[4]))
    if k == "N":
        if f[2] == "count":
            return "tick %s: the count reaches %s over fighter %s" % (f[1], f[3], f[4])
        return "tick %s: %s rises" % (f[1], f[3])
    if k == "V":
        return ("the verdict: %s, winner %s, cards %s-%s" % (f[1], f[2], f[3], f[4]))
    if k == "S":
        return "the trailer: " + "|".join(f[1:])
    if k == "H":
        return "the header: " + "|".join(f[1:])
    return line


def summary(report):
    """The fight in six lines, for a human reading a proof run."""
    c, t = report["counts"], report["trailer"]
    out = []
    out.append("  cards      %s" % ", ".join(report["header"].get("cards", ["?", "?"])))
    out.append("  punches    %d resolved (%d landed, %d slipped, %d wrong band)"
               % (c["punch_rows"], c["landed"], c["evaded"], c["whiff_band"]))
    if c["unresolved_punches"]:
        out.append("  in flight  %d punch(es) unresolved when the stream ended"
                   % c["unresolved_punches"])
    out.append("  landed by  fighter 0: %d, fighter 1: %d"
               % tuple(c["landed_by_fighter"]))
    out.append("  knockdowns %d / %d" % tuple(c["knockdowns"]))
    out.append("  result     %s, cards %s, kd %s"
               % (t.get("result", "?"), t.get("cards", "?"), t.get("kd", "?")))
    return "\n".join(out)


def main(argv):
    if not argv:
        print(__doc__.strip().splitlines()[0])
        print("usage: python -m tools.engine.analyze_integrated_arena <stream> [...]")
        return 2
    bad = 0
    for path in argv:
        report = analyse(path)
        print("== %s" % os.path.basename(path))
        print(summary(report))
        if report["errors"]:
            bad = 1
            print("  NOT COHERENT:")
            for e in report["errors"][:20]:
                print("    %s" % e)
            if len(report["errors"]) > 20:
                print("    ... and %d more" % (len(report["errors"]) - 20))
        else:
            print("  COHERENT: the trailer, the verdict and the rows agree")
    return bad


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-14 09:35 UTC | END ]
