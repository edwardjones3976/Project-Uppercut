# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 03:50 UTC | START ]
"""The evidence gate: the rules a research record must satisfy to exist here.

The schema says what shape a record has. This says what a record is ALLOWED to
claim, which is the part that protects the game. Every rule below exists because
of a specific way a research pile goes wrong:

  - a scraped paragraph becomes a gameplay formula because nobody asked whether
    anyone peer reviewed it;
  - a coaching blog and a controlled study sit in the same folder and get cited
    the same way;
  - a retracted paper stays in the pile because the pile was built once;
  - "the research says" turns out to mean one observational study with n=8;
  - the record quietly grows into a copy of the source.

Discovery is free. Canon costs a decision record, and that is enforced here
rather than remembered.
"""
import io
import json
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RECORDS = os.path.join("research", "metadata")
DECISIONS = os.path.join("docs", "decisions")
QUOTE_WORD_CAP = 25

LANES = ("punch_biomechanics", "fatigue_and_recovery", "knockdowns_and_stoppages",
         "tactics_and_ringcraft", "responsiveness_and_determinism",
         "training_and_spectator_design")


def load_all(root: str = None) -> list:
    root = root or os.path.join(REPO, RECORDS)
    out = []
    if not os.path.isdir(root):
        return out
    for name in sorted(os.listdir(root)):
        if name.endswith(".json"):
            with io.open(os.path.join(root, name), encoding="utf-8") as fh:
                rec = json.load(fh)
            rec["_file"] = name
            out.append(rec)
    return out


def check(rec: dict, repo: str = None) -> list:
    """Every rule that is not simply the schema. Returns a list of problems."""
    repo = repo or REPO
    where = rec.get("_file", rec.get("id", "?"))
    errs = []

    def bad(msg):
        errs.append("%s: %s" % (where, msg))

    # A source with no DOI is not disqualified - commission rules and engine docs
    # do not have one - but the absence has to be a stated fact rather than a
    # gap, or an unfindable source looks the same as an unpublished one.
    if not rec.get("doi") and not rec.get("no_doi_reason"):
        bad("no DOI and no no_doi_reason; say why this source has no DOI")

    # Tier 3 is inspiration. It may start a hypothesis and may never end one.
    if rec.get("tier") == 3 and rec.get("canon_status") == "accepted":
        bad("tier 3 is inspiration, not canon - it may not be accepted. If this "
            "source really should inform the game, find the study behind it")

    # "High confidence" is a claim about the evidence, not about the reader.
    if rec.get("confidence") == "high" and rec.get("peer_review_status") != "verified":
        bad("confidence 'high' requires peer_review_status 'verified'; an "
            "unverified source can be believed, it cannot be relied on")

    # Accepting evidence is a Director-level act with a paper trail.
    if rec.get("canon_status") == "accepted":
        ref = rec.get("accepted_by_decision")
        if not ref:
            bad("canon_status 'accepted' requires accepted_by_decision naming the "
                "decision record that accepted it")
        elif not os.path.exists(os.path.join(repo, DECISIONS, ref)):
            bad("accepted_by_decision names %s, which is not in %s"
                % (ref, DECISIONS))
    if rec.get("canon_status") == "rejected" and not rec.get("rejected_because"):
        bad("a rejected source must say why, or it will be rediscovered next month")

    # A retracted paper is not evidence, whatever it says.
    # "no retraction or correction recorded" contains the word, and a naive
    # substring check flagged every clean record in the pile. The negation has
    # to be read before the keyword is.
    status = (rec.get("retraction_or_correction_status") or "").lower().strip()
    if "retract" in status and not status.startswith("no ") \
            and rec.get("canon_status") == "accepted":
        bad("this source is marked retracted and cannot be accepted")

    # A record is a pointer to a source, not a copy of one.
    for i, q in enumerate(rec.get("quoted_evidence") or []):
        n = len(q.get("quote", "").split())
        if n > QUOTE_WORD_CAP:
            bad("quote %d is %d words; the cap is %d. Summarise instead - the "
                "record cites a source, it does not reproduce it"
                % (i + 1, n, QUOTE_WORD_CAP))

    # A finding without a method is an opinion with a citation attached.
    if rec.get("main_findings") and not rec.get("methodology"):
        bad("main_findings are recorded with no methodology; a finding whose "
            "method is unknown cannot be weighed against another finding")

    for lane in rec.get("research_lane") or []:
        if lane not in LANES:
            bad("unknown research lane %r" % lane)
    return errs


def check_all(root: str = None, repo: str = None) -> list:
    recs = load_all(root)
    errs = []
    seen = {}
    for rec in recs:
        errs.extend(check(rec, repo))
        key = (rec.get("doi") or "").lower()
        if key:
            if key in seen:
                errs.append("%s duplicates the DOI of %s"
                            % (rec.get("_file"), seen[key]))
            seen[key] = rec.get("_file")
    return errs


def summary(root: str = None) -> dict:
    recs = load_all(root)
    by_lane = {l: 0 for l in LANES}
    by_status = {}
    for r in recs:
        for l in r.get("research_lane") or []:
            by_lane[l] = by_lane.get(l, 0) + 1
        s = r.get("canon_status", "?")
        by_status[s] = by_status.get(s, 0) + 1
    return {"records": len(recs), "by_lane": by_lane, "by_status": by_status}
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 03:50 UTC | END ]
