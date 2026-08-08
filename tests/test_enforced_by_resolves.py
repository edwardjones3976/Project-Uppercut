# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 08:00 UTC | START ]
"""Every module an `enforced_by` names must actually exist.

WHY. On 2026-08-07 `data/stamina_economy.json` was found declaring five
invariants, each naming `tools/uppercut_validate/stamina.py::<fn>` as its
enforcer. That module did not exist. The rules were documented as checked and
were checked by nothing.

That is worse than an unchecked rule with no claim attached, because
`enforced_by` is precisely what a reviewer reads to decide they need not look
further. A dangling enforcer is a trapdoor with a polite label - the same shape
as the name-based exclusion Decision 0023 forbids, and the same shape as a move
id that silently costs nothing.

SCOPE, STATED HONESTLY. The convention is prose that may embed one or more
module references: "schema const + tools/uppercut_validate/camera.py::
check_authority". This guard resolves every embedded `<path>.py` and
`<path>.py::<function>` it finds. It does NOT check the prose clauses - "schema
const", "pipeline order", "data statement" - because those name mechanisms, not
call sites, and pretending to verify them would be the same overclaim this file
exists to catch. What it guarantees is narrower and real: no canon file names a
Python enforcer that cannot be imported.
"""
import importlib
import json
import os
import re

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

# A path ending in .py, optionally followed by ::function.
REFERENCE = re.compile(r"[\w./-]+\.py(?:::\w+)?")


def _claims(node, path, out):
    if isinstance(node, dict):
        for k, v in node.items():
            if k == "enforced_by" and isinstance(v, str):
                out.append((path, v))
            else:
                _claims(v, "%s/%s" % (path, k), out)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            _claims(v, "%s/%d" % (path, i), out)


def _all_references():
    """(canon file, pointer, reference) for every module an invariant names."""
    found = []
    for base, _dirs, names in os.walk(DATA):
        for n in sorted(names):
            if not n.endswith(".json"):
                continue
            full = os.path.join(base, n)
            try:
                doc = json.loads(open(full, encoding="utf-8").read())
            except ValueError:
                continue
            here = []
            _claims(doc, "", here)
            rel = os.path.relpath(full, ROOT).replace(os.sep, "/")
            for where, claim in here:
                for ref in REFERENCE.findall(claim):
                    found.append((rel, where, ref))
    return found


REFS = _all_references()


def test_the_guard_is_not_vacuous():
    """A guard that finds nothing reports the codebase as safe.

    If the convention moves to another key, or the references stop looking like
    paths, this test fails rather than passing silently - which is the whole
    lesson of the missing validator it was written for.
    """
    assert len(REFS) >= 20, (
        "only %d enforced_by module references found across data/ - either the "
        "convention moved and this guard is now blind, or the claims were "
        "deleted" % len(REFS))


@pytest.mark.parametrize("rel,where,ref", REFS,
                         ids=["%s%s->%s" % r for r in REFS])
def test_every_named_enforcer_exists(rel, where, ref):
    target, _, func = ref.partition("::")

    disk = os.path.join(ROOT, target.replace("/", os.sep))
    assert os.path.exists(disk), (
        "%s%s says it is enforced by %r, and that file does not exist. A rule "
        "documented as checked and checked by nothing is worse than an "
        "unchecked rule, because the claim is what stops anyone looking."
        % (rel, where, target))

    if not func:
        return

    module = target[:-3].replace("/", ".")
    mod = importlib.import_module(module)
    assert hasattr(mod, func), (
        "%s%s says it is enforced by %s::%s, and %s declares no such function"
        % (rel, where, target, func, module))
    assert callable(getattr(mod, func)), (
        "%s.%s is named as an enforcer but is not callable" % (module, func))


def test_the_stamina_invariants_that_prompted_this_are_covered():
    """The specific gap, pinned so it cannot silently reopen."""
    doc = json.loads(open(os.path.join(DATA, "stamina_economy.json"),
                          encoding="utf-8").read())
    named = [i["enforced_by"] for i in doc["invariants"]]
    assert named, "stamina_economy.json declares no enforced invariants"

    from tools.uppercut_validate import stamina
    for claim in named:
        for ref in REFERENCE.findall(claim):
            target, _, func = ref.partition("::")
            assert target == "tools/uppercut_validate/stamina.py", (
                "a stamina invariant is enforced from %s - if that is "
                "deliberate, widen this test rather than deleting it" % target)
            assert hasattr(stamina, func)

    # And the validator must actually pass over committed canon. A validator
    # that exists but fails is a different failure from one that is missing,
    # and both were live possibilities before this file.
    docs = stamina.load()
    problems = []
    for name, fn in stamina.ALL_CHECKS:
        problems.extend("%s: %s" % (name, e) for e in fn(docs))
    assert not problems, "\n".join(problems)
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 08:00 UTC | END ]
