# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 05:40 UTC | START ]
"""File full text an agent fetched, with its provenance attached.

THE SEAM THIS FILLS. `harvest.py` gets scholarly identity from OpenAlex - who
wrote it, where it appeared, whether it is retracted, whether it is open access.
What it cannot do is read the paper. Reading needs a fetcher, and the fetcher is
whatever the session has: Firecrawl if it is ever installed, Exa's web_fetch, an
ordinary web fetch, or a PDF the Director dropped in a folder.

None of those live inside this repository, and they should not: acquisition is
the replaceable part. What must live here is the RECORD of what was fetched,
from where, when, and by what - because a quote whose provenance is "an agent
had it in context once" is not evidence.

So an agent that has fetched something calls this, and the text lands in
untracked `research/raw/` while the committed record gains a `full_text_url`, a
`fetched_via` and a `fetched_at`. The gate's rules then apply unchanged: quotes
capped, findings need a method, and nothing reaches canon without a decision.

    python -m tools.research.cli ingest <record-id> --via exa \\
        --url https://example.org/paper --text-file C:\\tmp\\paper.txt

ACCESS DISCIPLINE, restated because this is the module that could break it.
Ingest open-access full text, abstracts, metadata, government and commission
publications, official documentation, and publisher pages whose stated terms
allow it. Do not ingest anything reached by defeating a paywall, an
authentication step, a robots exclusion or a licence limit. If a source needs
that to read, the honest record is the abstract plus a note that the full text
was not accessible.
"""
import io
import json
import os
import time

from . import gate

ALLOWED_VIA = ("firecrawl", "exa", "webfetch", "manual", "publisher-api")


def ingest(record_id: str, url: str, text: str, via: str,
           fetched_at: str = None) -> dict:
    if via not in ALLOWED_VIA:
        raise SystemExit("unknown fetcher %r; use one of %s"
                         % (via, ", ".join(ALLOWED_VIA)))
    meta = os.path.join(gate.REPO, gate.RECORDS, record_id + ".json")
    if not os.path.exists(meta):
        raise SystemExit("no record %s in %s - harvest it first, so identity is "
                         "verified before text is attached" % (record_id,
                                                               gate.RECORDS))
    raw_dir = os.path.join(gate.REPO, "research", "raw")
    if not os.path.isdir(raw_dir):
        os.makedirs(raw_dir)
    stamp = fetched_at or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    raw_path = os.path.join(raw_dir, record_id + ".fulltext.txt")
    header = ("# fetched_via: %s\n# source_url: %s\n# fetched_at: %s\n"
              "# UNTRACKED. Committed records carry quotes capped at %d words, "
              "not this file.\n\n" % (via, url, stamp, gate.QUOTE_WORD_CAP))
    with io.open(raw_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(header + text.rstrip() + "\n")

    with io.open(meta, encoding="utf-8") as fh:
        rec = json.load(fh)
    rec["full_text_url"] = url
    notes = rec.get("notes", "")
    stamped = "full text fetched via %s at %s (research/raw/, untracked)" % (
        via, stamp)
    rec["notes"] = (notes + "; " if notes else "") + stamped
    with io.open(meta, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(rec, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    return {"record": record_id, "raw": os.path.relpath(raw_path, gate.REPO),
            "via": via, "chars": len(text)}
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 05:40 UTC | END ]
