# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 04:00 UTC | START ]
"""Find candidate sources and write DRAFT evidence records.

WHAT THIS IS AND IS NOT. This is the acquisition layer: it asks a public
scholarly index a question, verifies the identity of what comes back, and writes
one draft record per source with `canon_status: "discovered"`. It does not read
papers, it does not decide whether a study is good, and it cannot mark anything
accepted - the gate refuses that without a decision record.

The Director's brief names Firecrawl for acquisition. Firecrawl is not installed
here and this deliberately does not pretend to be it: what it does instead is
the part of that architecture that matters most for correctness - scholarly
identity from OpenAlex and Crossref, which is where DOIs, venues, document types,
retraction flags and open-access status actually live. If Firecrawl is added
later it slots in ahead of this and hands full text to `research/raw/`; nothing
below changes.

ACCESS DISCIPLINE. Metadata APIs only. No paywall is touched, no authentication
is used, no robots exclusion is worked around. Abstracts arrive from OpenAlex as
an inverted index, which is how OpenAlex distributes them; the reconstruction
lands in `research/raw/` (untracked) and only short quoted extracts, capped by
the gate, may reach a committed record.

    python -m tools.research.cli harvest punch_biomechanics --limit 12
    python -m tools.research.cli validate
    python -m tools.research.cli index
"""
import io
import json
import os
import re
import time
import urllib.parse
import urllib.request

from . import gate

MAILTO = os.environ.get("UPPERCUT_RESEARCH_MAILTO", "edward.jones3976@yahoo.com")
OPENALEX = "https://api.openalex.org/works"
UA = "ProjectUppercut-research/0.1 (mailto:%s)" % MAILTO

# One narrow collection per lane, as the brief asks: ten to twenty strong
# sources, not thousands of loosely related pages. The queries are committed so
# a later harvest is reproducible and so a reader can see what was asked - a
# search nobody can see is a source of bias nobody can audit.
QUERIES = {
    "punch_biomechanics": [
        "boxing punch force velocity biomechanics",
        "punch impact kinematics boxing kinetic chain",
        "boxing straight hook uppercut force comparison",
    ],
    "fatigue_and_recovery": [
        "boxing fatigue punch performance decrement",
        "combat sports repeated effort recovery heart rate",
        "fatigue accuracy impairment striking sports",
    ],
    "knockdowns_and_stoppages": [
        "boxing knockout head acceleration mechanism",
        "concussion boxing rotational acceleration",
        "referee stoppage criteria combat sports injury",
    ],
    "tactics_and_ringcraft": [
        "boxing performance analysis punch distribution outcome",
        "boxing notational analysis winners losers technique",
        "combat sports distance management footwork analysis",
    ],
    "responsiveness_and_determinism": [
        "input latency player performance games",
        "deterministic lockstep rollback netcode games",
        "reaction time visual stimulus athletes",
    ],
    "training_and_spectator_design": [
        "motor learning feedback skill transfer practice",
        "spectator comprehension esports broadcast",
        "accessibility remapping video games players disability",
    ],
}


def _get(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA,
                                               "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as fh:
        return json.load(fh)


def _abstract(inv) -> str:
    if not inv:
        return ""
    words = [(pos, w) for w, ps in inv.items() for pos in ps]
    words.sort()
    return " ".join(w for _, w in words)


def _slug(text: str, year, doi: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    base = "-".join(base.split("-")[:8]) or "source"
    tail = (doi or "").rsplit("/", 1)[-1][:12].lower()
    tail = re.sub(r"[^a-z0-9]+", "", tail)
    return "%s-%s%s" % (base, year or 0, ("-" + tail) if tail else "")


def _tier(work: dict) -> int:
    """A first pass only, and deliberately conservative.

    Nothing here promotes a source to tier 1 on a machine's say-so: a review
    article gets tier 1 because the source type is checkable, an ordinary
    journal article gets tier 2 until a human reads the method, and everything
    else gets tier 3. Promotion is a reading job, not a metadata job.
    """
    t = (work.get("type") or "").lower()
    if t == "review":
        return 1
    if t in ("article", "journal-article") and work.get("primary_location", {}).get(
            "source"):
        return 2
    return 3


def draft(work: dict, lane: str, accessed: str) -> tuple:
    doi = (work.get("doi") or "").replace("https://doi.org/", "")
    loc = work.get("primary_location") or {}
    src = loc.get("source") or {}
    oa = work.get("open_access") or {}
    rec = {
        "id": _slug(work.get("title"), work.get("publication_year"), doi),
        "title": work.get("title") or "",
        "authors": [a["author"]["display_name"]
                    for a in (work.get("authorships") or [])[:12]
                    if a.get("author")],
        "year": int(work.get("publication_year") or 0),
        "source_url": work.get("id") or "",
        "accessed_at": accessed,
        "document_type": work.get("type") or "unknown",
        # OpenAlex knows the venue, not whether a human refereed this paper.
        # "likely" is the honest ceiling for anything a script decides.
        "peer_review_status": "likely" if _tier(work) <= 2 else "unknown",
        "tier": _tier(work),
        "research_lane": [lane],
        "canon_status": "discovered",
        "confidence": "low",
    }
    if doi:
        rec["doi"] = doi
    else:
        rec["no_doi_reason"] = ("no DOI in the OpenAlex record; verify by hand "
                               "before this source is used for anything")
    if src.get("display_name"):
        rec["journal_or_venue"] = src["display_name"]
    if src.get("host_organization_name"):
        rec["publisher"] = src["host_organization_name"]
    if oa.get("oa_url"):
        rec["full_text_url"] = oa["oa_url"]
    rec["open_access_status"] = oa.get("oa_status") or "unknown"
    rec["retraction_or_correction_status"] = (
        "RETRACTED per OpenAlex" if work.get("is_retracted")
        else "no retraction or correction recorded in OpenAlex at accessed_at")
    rec["notes"] = ("cited_by_count %s at harvest; a citation count is a measure "
                    "of attention, not of correctness"
                    % work.get("cited_by_count"))
    return rec, _abstract(work.get("abstract_inverted_index"))


def harvest(lane: str, limit: int = 12, accessed: str = None) -> dict:
    if lane not in QUERIES:
        raise SystemExit("unknown lane %r; lanes are %s"
                         % (lane, ", ".join(sorted(QUERIES))))
    accessed = accessed or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    meta_dir = os.path.join(gate.REPO, gate.RECORDS)
    raw_dir = os.path.join(gate.REPO, "research", "raw")
    for d in (meta_dir, raw_dir):
        if not os.path.isdir(d):
            os.makedirs(d)
    existing = {(r.get("doi") or "").lower() for r in gate.load_all()}
    written, skipped = [], 0
    per_query = max(1, limit // len(QUERIES[lane]) + 1)
    for query in QUERIES[lane]:
        # `title_and_abstract.search` rather than `search`, and relevance rather
        # than citation count. The first harvest used both defaults and returned
        # a triboelectric exoskeleton, an ice-hockey injury review and a handgrip
        # strength paper among twelve "punch biomechanics" hits - highly cited,
        # entirely off topic. Sorting a broad full-text search by citations
        # ranks fame, not fit, which is the brief's "thousands of loosely
        # related pages" failure arriving early and small.
        url = ("%s?filter=title_and_abstract.search:%s,type:article|review"
               "&per-page=%d&mailto=%s"
               % (OPENALEX, urllib.parse.quote(query), per_query * 2,
                  urllib.parse.quote(MAILTO)))
        for work in _get(url).get("results", []):
            if len(written) >= limit:
                break
            rec, abstract = draft(work, lane, accessed)
            key = (rec.get("doi") or "").lower()
            if key and key in existing:
                skipped += 1
                continue
            if key:
                existing.add(key)
            path = os.path.join(meta_dir, rec["id"] + ".json")
            if os.path.exists(path):
                skipped += 1
                continue
            with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
                json.dump(rec, fh, indent=2, ensure_ascii=False)
                fh.write("\n")
            if abstract:
                with io.open(os.path.join(raw_dir, rec["id"] + ".abstract.txt"),
                             "w", encoding="utf-8", newline="\n") as fh:
                    fh.write(abstract + "\n")
            written.append(rec["id"])
        time.sleep(0.4)
    qpath = os.path.join(gate.REPO, "research", "queries", lane + ".json")
    with io.open(qpath, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"lane": lane, "queries": QUERIES[lane], "index": "OpenAlex",
                   "harvested_at": accessed, "written": written,
                   "skipped_as_duplicate_or_present": skipped}, fh, indent=2)
        fh.write("\n")
    return {"lane": lane, "written": len(written), "skipped": skipped}
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 04:00 UTC | END ]
