# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 22:20 UTC | START ]
"""A proven phase's recorded hash must stay reproducible from its analyzer.

Written after a real incident on 2026-08-04. Another agent, trying to help,
added contact-quality grading to Phase N's analyzer and Phase N's C++
commandlet. Both edits were reasonable in isolation. Together they silently
invalidated Phase N's PASS: the record says the C++ and the Python recomputation
agree at

    sha256 88af6f3011b93c12540ead0c016062425e20abf9c7cda994322d1a98c14ddc37

and after the edit the Python produced 974c12ef... while the committed C++
artifact still produced 88af6f30. The phase record had become false.

**The whole suite passed anyway** - 580 tests - because every phase test
regenerates its stream from the same analyzer it then checks. Self-consistency
is not evidence. Nothing in the suite compared an analyzer against the number a
phase had already sworn to.

That is what these pins are. They hold the recomputation against the hash in the
record, so editing a frozen phase's contract fails here immediately instead of
quietly rotting the evidence. A phase's analyzer is a historical artifact: once
its PASS is recorded, changing it is changing the past, and improvements belong
in the NEXT phase.

If one of these fails and the change was deliberate, the phase must be re-run,
re-proven and re-recorded - and the pin updated in the same commit as the record.
Never update the pin alone.
"""
import hashlib
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(
    __file__))), "tools", "engine"))

# RE-PINNED 2026-08-05 under Decision 0014 (gate G1), which is the case this
# file's docstring describes as the legitimate one: a formal decision changed
# canon, so the phases were RE-RUN and RE-PROVEN rather than having their pins
# quietly edited to match. Both C++ artifacts still reproduce their analyzers
# byte for byte against the repriced move table; the streams moved only because
# both phases hash that file into their headers, not because either fight
# changed. The superseded hashes are kept beside the new ones so the record of
# what was proven when survives, which is the whole point of pinning.
#
#   Phase N  88af6f30... (2026-08-04, flat step cost)
#            -> 7b2b9000... (2026-08-05, displacement pricing)
#   Phase K  b6f1c24b... (2026-08-04)
#            -> 4826e82c... (2026-08-05, same cause)
#
# (module, callable args, the hash the phase record swears to, where it is recorded)
PINS = [
    ("analyze_core_condition", (4242, 5400),
     "7b2b90001b541b8e145ab4fe501de15e45b3780b3c1e821a866a3b4786cea1ff",
     "Phase N - visible stamina and condition"),
    ("analyze_render_probe", (4242, 5400),
     "4826e82c532b98e481080b8603321e2e406c4f706681361b7a1996ff153b36ce",
     "Phase K / the rendered slice - primitives, mannequins and the arena alike"),
]


@pytest.mark.parametrize("mod,args,want,phase", PINS)
def test_the_recorded_phase_hash_is_still_reproducible(mod, args, want, phase):
    m = __import__(mod)
    got = hashlib.sha256(m.expected_stream(*args).encode("utf-8")).hexdigest()
    assert got == want, (
        "%s no longer reproduces its recorded hash.\n"
        "  recorded: %s\n  now:      %s\n"
        "A proven phase's analyzer is a historical artifact. If this change was "
        "deliberate, re-run the phase, re-record it in "
        "docs/phase1a/determinism_probe_results.md, and update this pin in the "
        "SAME commit. If it was not, revert it." % (phase, want, got))


def test_the_pins_are_not_vacuous():
    """A pin that cannot fail protects nothing."""
    import analyze_core_condition as N
    got = hashlib.sha256(N.expected_stream(4242, 5401).encode("utf-8")).hexdigest()
    assert got != PINS[0][2], "the pin does not discriminate between streams"
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 22:20 UTC | END ]
