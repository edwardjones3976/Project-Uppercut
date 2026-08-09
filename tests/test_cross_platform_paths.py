# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 14:40 UTC | START ]
"""CI parity: every canon path a tool names must exist with EXACT case.

Why this exists. All development happens on Windows, where the filesystem is
case-insensitive, and CI runs on ubuntu-latest, where it is not. A tool that asks
for `data/moves/Generic_Sandbox_Moves.json` works forever locally and fails on
the first push - and the failure arrives as a red check on a commit whose author
has already moved on, with a message that looks like a missing file rather than a
typo.

Four phases of new tooling were written on Windows on 2026-08-05 without this
guard. It is cheap, it is exact, and it turns a class of CI-only failure into a
local one.

The check is deliberately literal: it scans the tool and test sources for string
literals that look like repository-relative canon paths, and asserts each resolves
on disk with the case as written, compared against the real directory listing
rather than against `os.path.exists` (which would answer case-insensitively on the
machine this is usually run from and prove nothing).
"""
import os
import re
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

# A repo-relative path literal: "data/..." or "docs/..." or "tools/...", in
# either slash style, ending in a file extension we actually read.
PATH_RE = re.compile(
    r"""['"]((?:data|docs|tools|tests)[\\/][^'"]*?\.(?:json|md|py|txt|yml))['"]"""
)
SCAN_DIRS = ("tools", "tests")
# Path literals that are constructed, templated, or intentionally absent.
IGNORE = ("*",)

# Literals that SHOULD NOT resolve, each named individually with its reason.
# A blanket "skip anything in a test" would defeat the guard, because the tools
# most likely to name a canon path wrongly are the ones that read canon.
EXEMPT = {
    ("tests/test_guard.py", "docs/design/some_other_file.md"):
        "a deliberately non-existent path, fed to check_matchup_reference to "
        "prove it rejects a third copy of the matchup tables",
    # [ Claude Fable 5 (claude-fable-5) | 2026-08-09 10:58 UTC ]
    ("tools/uppercut_integrated/contract.py", "data/rulesets/%s.json"):
        "a TEMPLATE, not a path: the ruleset actually fought under is chosen "
        "per bout (Decision 0033 Ruling 2) and the %s is filled with its id. "
        "The resolved path is validated by ruleset_pack, which refuses an "
        "unauthored ruleset by name.",
}
# This file names wrong-case paths on purpose, to prove the guard can fail.
SELF = "tests/test_cross_platform_paths.py"


def _real_case(path: str) -> bool:
    """Does this path exist with exactly this spelling?

    Walks it segment by segment against the true directory listing, so the answer
    is the same on Windows as it is on Linux.
    """
    cur = ROOT
    for part in path.replace("\\", "/").split("/"):
        if not part or part == ".":
            continue
        try:
            entries = os.listdir(cur)
        except (NotADirectoryError, FileNotFoundError):
            return False
        if part not in entries:
            return False
        cur = os.path.join(cur, part)
    return True


def _literals():
    found = []
    for d in SCAN_DIRS:
        base = os.path.join(ROOT, d)
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [x for x in dirnames if x != "__pycache__"]
            for fn in filenames:
                if not fn.endswith(".py"):
                    continue
                p = os.path.join(dirpath, fn)
                with open(p, "r", encoding="utf-8") as fh:
                    src = fh.read()
                rel = os.path.relpath(p, ROOT).replace("\\", "/")
                if rel == SELF:
                    continue
                for m in PATH_RE.finditer(src):
                    lit = m.group(1)
                    if any(ig in lit for ig in IGNORE):
                        continue
                    if (rel, lit) in EXEMPT:
                        continue
                    found.append((rel, lit))
    return found


def test_the_scan_finds_something():
    """A regex that matches nothing would pass every assertion below."""
    lits = _literals()
    assert len(lits) >= 5, "the path scan found %d literals; it is not working" % len(lits)


@pytest.mark.parametrize("where,lit", _literals(),
                         ids=lambda v: v if isinstance(v, str) else str(v))
def test_every_named_canon_path_exists_with_exact_case(where, lit):
    assert _real_case(lit), (
        "%s names '%s', which does not exist with that exact spelling. This "
        "passes on a case-insensitive filesystem and fails on CI." % (where, lit))


def test_every_exemption_is_still_needed():
    """An exemption that has become unnecessary is a hole nobody is watching."""
    for (where, lit), why in EXEMPT.items():
        assert not _real_case(lit), (
            "%s now resolves, so its exemption in this guard is stale and "
            "should be removed (reason on file: %s)" % (lit, why))
        assert os.path.exists(os.path.join(ROOT, where)), \
            "%s no longer exists, so its exemption is dead" % where


def test_the_guard_itself_catches_a_wrong_case():
    """The check must be able to fail, or it is decoration."""
    assert _real_case("data/movement_model.json")
    assert not _real_case("data/Movement_Model.json")
    assert not _real_case("DATA/movement_model.json")


def test_no_absolute_or_windows_paths_in_tooling():
    """A hard-coded C:\\ path is a machine-specific tool, not a repository one."""
    bad = []
    for d in SCAN_DIRS:
        for dirpath, dirnames, filenames in os.walk(os.path.join(ROOT, d)):
            dirnames[:] = [x for x in dirnames if x != "__pycache__"]
            for fn in filenames:
                if not fn.endswith(".py"):
                    continue
                p = os.path.join(dirpath, fn)
                with open(p, "r", encoding="utf-8") as fh:
                    for i, line in enumerate(fh, 1):
                        if re.search(r"['\"][A-Za-z]:\\\\", line) or \
                                re.search(r"['\"]/(home|Users|mnt)/", line):
                            bad.append("%s:%d" % (os.path.relpath(p, ROOT), i))
    assert not bad, "machine-specific absolute paths: %s" % ", ".join(bad)
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 14:40 UTC | END ]
