# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 02:13 UTC | START ]
"""Referee semantics laws (Rule 16, Decision 0012 slice item 2).

data/referees/ holds seven qualitative officiating profiles;
data/referee_semantics.json is the dictionary that makes them executable. These
checks keep that pairing honest:

  1. every level any official uses resolves in every table it feeds - the
     'referee who maps to nothing' is the inert class this step closes;
  2. the numbers are ordered by what the words claim - a 'high' tolerance that
     warns earlier than a 'low' one is a dictionary lying about its words;
  3. the neutral rows are the incumbent constants - the file's own comment
     promises that 'moderate'/'standard' reproduce the pre-consumption engine
     (warning at 6, break patience 90, no judgement stoppage), and a promise a
     check does not enforce is prose (Rule 18);
  4. the seven officials actually differ - consuming profiles that all derive
     identical enforcement would be the old inertness wearing a new file.
"""
from __future__ import annotations
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 21:58 UTC | F1: strict canon JSON ]
from . import strict_json as json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

TOLERANCE_ORDER = ["low", "moderate", "high", "very_high"]
THRESHOLD_ORDER = ["early", "standard", "late", "very_late"]


def load() -> dict:
    sem = json.loads((REPO / "data" / "referee_semantics.json").read_text(encoding="utf-8"))
    refs = {}
    for p in sorted((REPO / "data" / "referees").glob("*.json")):
        refs[p.stem] = json.loads(p.read_text(encoding="utf-8"))
    return {"semantics": sem, "referees": refs}


def _value(rows: list, level: str):
    for r in rows:
        if r["level"] == level:
            return r["value"]
    raise KeyError(level)


def derived(doc: dict, rid: str) -> tuple:
    """One official's enforcement numbers, exactly as the engine derives them."""
    sem, enf = doc["semantics"], doc["referees"][rid]["enforcement"]
    cl = sem["clinch"]
    warning = max(1, _value(cl["warning_after_entries_by_clinch_tolerance"],
                            enf["clinch_tolerance"])
                  + _value(cl["warning_offset_by_warning_threshold"],
                           enf["warning_threshold"]))
    gap = _value(cl["deduction_gap_entries_by_deduction_threshold"],
                 enf["deduction_threshold"])
    patience = _value(cl["break_patience_by_clinch_tolerance"], enf["clinch_tolerance"])
    stop = _value(sem["stoppage"]["unanswered_after_knockdown_by_stoppage_disposition"],
                  enf["stoppage_disposition"])
    return (warning, gap, patience, stop)


def check_every_official_resolves(doc: dict) -> list:
    """Check 1: no official maps to a missing level in any table it feeds."""
    errs = []
    for rid in sorted(doc["referees"]):
        try:
            derived(doc, rid)
        except KeyError as e:
            errs.append(f"{rid}: enforcement level {e} has no row in the semantics "
                        f"table it feeds - this official would be inert or crash")
    return errs


def check_words_order_the_numbers(doc: dict) -> list:
    """Check 2: values increase with the level words, strictly."""
    errs = []
    cl = doc["semantics"]["clinch"]
    for table, order in (
            ("warning_after_entries_by_clinch_tolerance", TOLERANCE_ORDER),
            ("break_patience_by_clinch_tolerance", TOLERANCE_ORDER),
            ("warning_offset_by_warning_threshold", THRESHOLD_ORDER),
            ("deduction_gap_entries_by_deduction_threshold", THRESHOLD_ORDER)):
        try:
            vals = [_value(cl[table], lv) for lv in order]
        except KeyError as e:
            errs.append(f"{table}: missing level {e}")
            continue
        if any(b <= a for a, b in zip(vals, vals[1:])):
            errs.append(f"{table}: values {vals} do not strictly increase over "
                        f"{order} - the dictionary contradicts its words")
    st = doc["semantics"]["stoppage"]["unanswered_after_knockdown_by_stoppage_disposition"]
    prot = _value(st, "protective")
    if not (isinstance(prot, int) and prot > 0):
        errs.append("stoppage: the protective disposition must carry a positive integer "
                    "threshold, or the referee_judgement stoppage stays inert")
    return errs


def check_neutral_is_the_incumbent(doc: dict) -> list:
    """Check 3: the calibration promise, enforced. moderate/standard reproduce
    the constants the engine hardcoded before referees were consumed."""
    errs = []
    cl = doc["semantics"]["clinch"]
    st = doc["semantics"]["stoppage"]["unanswered_after_knockdown_by_stoppage_disposition"]
    for what, got, want in (
            ("moderate warning entries", _value(cl["warning_after_entries_by_clinch_tolerance"], "moderate"), 6),
            ("standard warning offset", _value(cl["warning_offset_by_warning_threshold"], "standard"), 0),
            ("moderate break patience", _value(cl["break_patience_by_clinch_tolerance"], "moderate"), 90),
            ("standard stoppage threshold", _value(st, "standard"), None)):
        if got != want:
            errs.append(f"{what} is {got}, not the incumbent {want} - either recalibrate "
                        f"deliberately (and update this check with the argument) or the "
                        f"neutral official no longer means 'the engine as it was proven'")
    return errs


def check_officials_differ(doc: dict) -> list:
    """Check 4: seven philosophies must be more than one philosophy."""
    tuples = {rid: derived(doc, rid) for rid in doc["referees"]}
    distinct = len(set(tuples.values()))
    if distinct < 4:
        return [f"only {distinct} distinct enforcement derivations across "
                f"{len(tuples)} officials - the profiles are consumed but barely differ"]
    return []


ALL_CHECKS = [
    ("every official resolves in every table", check_every_official_resolves),
    ("the words order the numbers", check_words_order_the_numbers),
    ("the neutral official is the incumbent", check_neutral_is_the_incumbent),
    ("the seven officials actually differ", check_officials_differ),
]
# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 02:13 UTC | END ]
