# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 21:05 UTC | START ]
"""The decision index is generated, contiguous, and unique — enforced.

An external audit at `main` 1e434fed found the README indexing decisions
through 0012 while the repository carried 0032. Twenty decisions were invisible
from the front door, and nothing failed. Separately, two numbering collisions
(a duplicate 0032 and a duplicate 0034) were found by hand on 2026-08-09, both
created by branches that could not see each other.

These tests are the machine that would have caught all three.
"""
import os
import subprocess
import sys

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

from tools import gen_decision_index as GEN  # noqa: E402


def test_the_index_is_not_stale():
    """The generated file matches what the generator would write today."""
    r = subprocess.run([sys.executable, "-m", "tools.gen_decision_index",
                        "--check"], cwd=REPO,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert r.returncode == 0, (
        "docs/decisions/INDEX.md is stale - run "
        "`python -m tools.gen_decision_index`.\n"
        + r.stderr.decode("utf-8", "replace"))


def test_no_two_files_claim_the_same_decision_number():
    """A decision number is an identity, not a label.

    On 2026-08-09 two files claimed 0032 and two claimed 0034, because the
    Director's branch and the working branch each numbered from what they could
    see. Neither collision was a disagreement about substance - and that is
    exactly why it could have merged silently.
    """
    _rows, problems = GEN.collect()
    dupes = [p for p in problems if "claimed by TWO files" in p]
    assert not dupes, "\n".join(dupes)


def test_decision_numbers_are_contiguous():
    """A gap means a decision was lost or never written."""
    _rows, problems = GEN.collect()
    gaps = [p for p in problems if "not contiguous" in p]
    assert not gaps, "\n".join(gaps)


def test_every_decision_headline_matches_its_filename():
    _rows, problems = GEN.collect()
    liars = [p for p in problems if "disagree" in p or "no '# Decision" in p]
    assert not liars, "\n".join(liars)


def test_the_readme_points_at_the_generated_index_and_not_a_copy():
    """The README must not carry a hand-maintained list that can rot again."""
    with open(os.path.join(REPO, "README.md"), encoding="utf-8") as fh:
        readme = fh.read()
    assert "docs/decisions/INDEX.md" in readme, \
        "the README no longer links the generated decision index"
    # A curated shortlist is fine; a full enumeration is the thing that rotted.
    linked = readme.count("](docs/decisions/00")
    assert linked <= 12, (
        "the README links %d individual decisions - that is an enumeration "
        "growing back, and enumerations are what went stale. Link the index."
        % linked)


@pytest.mark.parametrize("num", ["0032", "0034"])
def test_the_two_collided_numbers_resolve_to_exactly_one_file(num):
    """Regression for Decision 0038's two resolutions, by number."""
    rows, _ = GEN.collect()
    hits = [r for r in rows if r[0] == num]
    assert len(hits) == 1, "Decision %s resolves to %d files" % (num, len(hits))
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 21:05 UTC | END ]
