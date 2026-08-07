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
# RE-PINNED AGAIN 2026-08-06, and this time for a reason that is not a canon
# change at all. Commit fb4bdea renumbered Decisions 0018 -> 0019 and 0019 ->
# 0020 during the post-merge reconciliation, and updated the prose inside canon
# files that cited them: `$comment`, `note` and `notes` strings in
# pose_geometry.json and both rulesets. Not one authoritative value moved.
#
# Four pins broke anyway - N, K, and the Phase O and Q golden streams - because
# a stream header hashes the whole canon FILE. Decision 0022 freezes these pins
# and permits a move only when canon or implementation changes inside the phase's
# declared scope. A corrected comment is neither, so this re-pin is recorded as
# an implementation correction rather than as a canon ruling.
#
# The claim that only prose moved is MECHANICAL, not editorial. Strip every
# documentation key ($comment, note, notes, contribution, *_note) from each
# changed file at both revisions and the remainder is byte-identical:
#
#   data/pose_geometry.json                   raw=differs  semantics=identical
#   data/rulesets/professional.json           raw=differs  semantics=identical
#   data/rulesets/arcade_three_knockdown.json raw=differs  semantics=identical
#
# Decision 0022 requires "the first divergent authoritative event, not only the
# final hash". There is no divergent authoritative event. Every tick of both
# fights is unchanged; the divergence is confined to the header's canon hashes.
#
# THIS IS A DEFECT IN THE EVIDENCE SCHEME, not merely an accident, and it is
# written up in docs/plans/2026-08-06-the-canon-hash-cannot-see-the-difference.md:
# whole-file hashing cannot distinguish a retuned value from a fixed typo, so it
# trains re-blessing as routine, which is exactly how pin discipline dies.
#
# MIGRATED 2026-08-07 under Decision 0023, and this is the ONE move that ruling
# permits. The whole-file `H|canon_<name>=` lines became a dual-hash header:
#
#     H|canon_hash_contract=uppercut-hash-contract-v1
#     H|canon_hash_roles=uppercut-hash-roles-v1
#     H|canon_hash_roles_id=<the manifest's own semantic identity>
#     H|canon_<label>_semantic=<moves when the fight can>
#     H|canon_<label>_raw=<moves whenever the file does>
#
# Every `_raw` value is IDENTICAL to the whole-file hash it replaced, so the
# provenance the old pins carried is not lost - it is relabelled with the
# question it was always answering.
#
# Migration acceptance, run as `python -m tools.engine.migrate_canon_headers`
# with baselines captured BEFORE the change and verified after:
#
#     OK  phase N   5688 authoritative rows unchanged
#     OK  phase K   3025 authoritative rows unchanged
#     OK  phase O  10952 authoritative rows unchanged
#     OK  phase Q   1312 authoritative rows unchanged
#     OK  phase R   1007 authoritative rows unchanged
#     MIGRATION CLEAN - no authoritative row moved
#
# 21,984 authoritative rows across five phases, not one of them different. The
# ruling says any event-row divergence aborts migration and requires separate
# diagnosis; there was none to diagnose. Every phase also re-proved against its
# C++ artifact after the change, which is why this is a migration and not a
# re-bless: the fights are provably the same fights.
#
# AND ONCE MORE the same day, for a reason that is the design working rather
# than a defect. `units_correction_2026_08_07` was added to stamina_economy.json
# and classified as documentation in the hash-role manifest. Director
# requirement 1 binds the MANIFEST'S OWN identity into every semantic payload,
# so changing a classification moves every hash taken under it - including
# phases that do not read the file whose classification changed.
#
# That is deliberate and fail-safe: it is what stops someone reclassifying a
# live combat field as documentation and having the evidence system politely
# look away. The cost is real and worth stating - ANY manifest edit re-blesses
# every active stream. The migration verifier was re-run and again found no
# authoritative row moved, so this is header identity and nothing else.
#
#   Phase N  88af6f30... (2026-08-04, flat step cost)
#            -> 7b2b9000... (2026-08-05, displacement pricing)
#            -> 3df854f4... (2026-08-06, PROSE ONLY - no value changed)
#            -> ff2e793f... (2026-08-07, DUAL-HASH HEADER - no row changed)
#            -> 74e0c48b... (2026-08-07, MANIFEST IDENTITY - no row changed)
#            -> 8108c027... (2026-08-07, DECISION 0024 SCOPE - no row changed)
#   Phase K  b6f1c24b... (2026-08-04)
#            -> 4826e82c... (2026-08-05, same cause)
#            -> d2032592... (2026-08-06, PROSE ONLY - no value changed)
#            -> 6aba9c09... (2026-08-07, DUAL-HASH HEADER - no row changed)
#            -> 16e3efa8... (2026-08-07, MANIFEST IDENTITY - no row changed)
#            -> 274c597b... (2026-08-07, DECISION 0024 SCOPE - no row changed)
#
# The last move is Decision 0024 replacing the whole-manifest binding with a
# GLOBAL POLICY identity plus a PER-FILE role set - the narrowing that stops a
# classification change in one file from moving phases that never read it. This
# is the final shape of the header, and the cost it removes is the one recorded
# in the entry above: from here, editing one file's classification moves that
# file and nothing else.
#
# (module, callable args, the hash the phase record swears to, where it is recorded)
PINS = [
    ("analyze_core_condition", (4242, 5400),
     "8108c027abeebaa63425a4f0da155fe771f1775638d1482a1dead935a485c76b",
     "Phase N - visible stamina and condition"),
    ("analyze_render_probe", (4242, 5400),
     "274c597b5d54001cf737dc965160e9d9d87aadcc2fa0f03e40d8ee7da37c10bd",
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
