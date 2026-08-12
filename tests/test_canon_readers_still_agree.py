# [ Claude Fable 5 (claude-fable-5) | 2026-08-12 19:11 UTC | START ]
"""The duplicated canon readers must still SAY the same thing, not just exist.

`tests/test_live_arena_is_one_implementation.py` already counts the drift the
Phase Q extraction left behind: six phase commandlets parse `movement_model.json`
inline, and eight files carry their own LCG. Those tests pin *how many* copies
there are, so a seventh is a deliberate act.

They do not check that the copies AGREE. Counting occurrences catches a new
copy; it is blind to an edited one. That is the exact failure the convergence
rule names - "two implementations of one rule, agreeing right up until one of
them is edited" - and the count tests leave it uncovered:

  - `test_the_canon_reader_sprawl_is_on_the_record` pins six inline readers.
  - `test_the_two_unbounded_band_sentinels_still_agree` guards the ring-size
    coupling by asserting the ring axis stays below a HARD-CODED 99.0 ru. It
    never reads the six sources to check they actually use 99.0. If one
    commandlet's ceiling were edited to 95.0, five phases would agree, one
    would silently differ, and that test would still pass - it is checking the
    ring, not the readers.

These two tests close that specific hole, at the two places duplication is
currently load-bearing: the quantizer that turns authored canon into integers,
and the open-ended top band's sentinel. Both need no engine. Neither proves the
phases correct; they stop the copies from diverging without a failure.

If the real single-reader fix lands (docs/plans/2026-08-07-what-the-integrated-
schema-has-to-absorb.md), these tests get simpler or disappear, and that is
progress - say so in the phase record rather than deleting them quietly.
"""
import io
import os
import re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRIVATE = os.path.join(REPO, "sandbox", "Source", "UppercutCore", "Private")

# The Phase Q chain reads canon through the shared loader on purpose; it is not
# an inline reader and is not this file's subject. Kept in step with the list in
# test_live_arena_is_one_implementation.py.
PHASE_Q_CHAIN = (
    "UppercutRangeCore.cpp",
    "UppercutRangeCanonLoader.cpp",
    "UppercutRangeStream.cpp",
    "UppercutCoreRangeCommandlet.cpp",
    "UppercutFightSubsystem.cpp",
    "UppercutLiveArenaCommandlet.cpp",
)

# The quantizer every reader uses to turn an authored ru value into a q10000
# integer. There are TEN owners today: nine helper sites (`Q` or `QFromFloat`)
# plus one inline probe reader. Duplicated quantization is tolerated ONLY while
# every owner still applies the same RoundToDouble(... * 10000.0) rule.
HELPER_Q_DEF_RE = re.compile(
    r"int64\s+(?:Q|QFromFloat)\s*\(\s*double\s+\w+\s*\)\s*\{[^}]*\}"
)
PROBE_Q_EXPR_RE = re.compile(
    r"\(int64\)FMath::RoundToDouble\((?P<operand>.+?)\s*\*\s*10000\.0\)",
    re.S,
)
EXPECTED_QUANTIZER_HELPER_OWNERS = (
    "UppercutAttrCore.cpp",
    "UppercutBoutDirector.cpp",
    "UppercutCoreConditionCommandlet.cpp",
    "UppercutCoreGuardCommandlet.cpp",
    "UppercutCoreLoopCommandlet.cpp",
    "UppercutCoreSweepCommandlet.cpp",
    "UppercutRangeCanonLoader.cpp",
    "UppercutRoundCore.cpp",
    "UppercutStaminaCore.cpp",
)
PROBE_INLINE_QUANTIZER_OWNER = "UppercutCoreProbeCommandlet.cpp"
NORMALIZED_Q10000_RULE = "(int64)FMath::RoundToDouble(_ * 10000.0)"

# The open-ended top band (`max_ru: null`) has no authored ceiling. The inline
# readers substitute a finite sentinel. Two spellings are in the tree today:
#   literal   `: (int64)990000)`            (five commandlets + the bout director)
#   defaulted `double MaxRu = 99.0;`        (the probe commandlet, * 10000 later)
# Both must land on the same q10000 value or the readers disagree about which
# band a far-apart pair is in.
SENTINEL_LITERAL_RE = re.compile(r"max_ru[^;]*?:\s*\(int64\)\s*(\d+)")
SENTINEL_DEFAULT_RE = re.compile(r"double\s+\w*Max\w*\s*=\s*([0-9]+(?:\.[0-9]+)?)\s*;")

EXPECTED_SENTINEL_Q = 990000     # 99.0 ru in q10000


def read(name):
    path = os.path.join(PRIVATE, name)
    assert os.path.exists(path), "%s is missing" % path
    return io.open(path, encoding="utf-8", errors="replace").read()


def _cpp_files():
    return [n for n in sorted(os.listdir(PRIVATE)) if n.endswith(".cpp")]


def _inline_band_readers():
    """The readers the sprawl test counts: parse range_bands, not Phase Q's chain."""
    out = []
    for name in _cpp_files():
        if name in PHASE_Q_CHAIN:
            continue
        if "range_bands" in read(name):
            out.append(name)
    return out


def _normalize_helper_quantizer(src):
    src = re.sub(r"\s+", " ", src).strip()
    src = re.sub(r"\b(?:Q|QFromFloat)\b", "Q_HELPER", src, count=1)
    src = re.sub(r"\(\s*double\s+\w+\s*\)", "(double _)", src, count=1)
    src = re.sub(r"RoundToDouble\(\s*\w+\s*\*", "RoundToDouble(_ *", src, count=1)
    return src


def _normalize_probe_quantizer(expr):
    expr = re.sub(r"\s+", " ", expr).strip()
    return re.sub(
        r"\(int64\)FMath::RoundToDouble\((?P<operand>.+?)\s*\*\s*10000\.0\)",
        NORMALIZED_Q10000_RULE,
        expr,
        count=1,
    )


def test_every_quantizer_definition_is_byte_identical():
    """All ten quantizer owners still apply the same q10000 rounding rule.

    The module currently owns q10000 quantization in ten places: nine helper
    definitions (`Q` or `QFromFloat`) and the probe commandlet's inline
    range-band quantization. That duplication is a known, tolerated shortcut -
    but it is only harmless while every owner still uses the same
    RoundToDouble(... * 10000.0) rule. A single owner edited to truncate, floor
    or scale differently would quantize the same authored canon into different
    integers and two phases would disagree about a boundary.
    """
    defs = {}
    for name in EXPECTED_QUANTIZER_HELPER_OWNERS:
        matches = list(HELPER_Q_DEF_RE.finditer(read(name)))
        assert len(matches) == 1, (
            "expected exactly one helper quantizer definition in %s; found %d. "
            "If the helper moved or multiplied, update this owner list and the "
            "drift test together." % (name, len(matches))
        )
        defs[name] = _normalize_helper_quantizer(matches[0].group(0))

    assert set(defs) == set(EXPECTED_QUANTIZER_HELPER_OWNERS), (
        "the helper quantizer owner set drifted: expected %s, found %s"
        % (sorted(EXPECTED_QUANTIZER_HELPER_OWNERS), sorted(defs))
    )

    canonical = defs[sorted(defs)[0]]
    disagreeing = {n: d for n, d in defs.items() if d != canonical}
    assert not disagreeing, (
        "the helper quantizer is not identical everywhere. %d file(s) differ from\n"
        "  %s\n%s\n"
        "A quantizer that rounds differently turns the same authored canon into "
        "different integers - the exact 'agree until edited' divergence the "
        "convergence rule exists to stop."
        % (len(disagreeing), canonical,
           "\n".join("  %s: %s" % (n, d) for n, d in sorted(disagreeing.items())))
    )

    probe_text = read(PROBE_INLINE_QUANTIZER_OWNER)
    probe_quantizers = [
        _normalize_probe_quantizer(m.group(0))
        for m in PROBE_Q_EXPR_RE.finditer(probe_text)
        if "10000.0" in m.group(0)
    ]
    assert len(probe_quantizers) == 3, (
        "%s should own exactly three inline q10000 quantizers (min, max, "
        "hysteresis); found %d: %s"
        % (PROBE_INLINE_QUANTIZER_OWNER, len(probe_quantizers), probe_quantizers)
    )
    assert set(probe_quantizers) == {NORMALIZED_Q10000_RULE}, (
        "%s no longer uses the shared q10000 rounding rule everywhere: %s"
        % (PROBE_INLINE_QUANTIZER_OWNER, probe_quantizers)
    )


def test_every_inline_band_reader_uses_the_same_open_ended_sentinel():
    """The six inline readers agree on the top band's ceiling - checked, not assumed.

    `test_the_two_unbounded_band_sentinels_still_agree` reasons about the ring
    being smaller than 99.0 ru, but takes on faith that all six readers use
    99.0. This reads the sources and proves it: each inline band reader must
    substitute a sentinel that quantizes to exactly 990000, whether it writes
    the literal `(int64)990000` or defaults a double to `99.0`.
    """
    readers = _inline_band_readers()
    assert len(readers) == 6, (
        "expected six inline band readers (the count pinned in "
        "test_live_arena_is_one_implementation.py); found %d: %s. Reconcile the "
        "two tests before trusting either." % (len(readers), readers)
    )

    missing, wrong = [], {}
    for name in readers:
        text = read(name)
        found = set()
        for m in SENTINEL_LITERAL_RE.finditer(text):
            found.add(int(m.group(1)))
        for m in SENTINEL_DEFAULT_RE.finditer(text):
            found.add(int(round(float(m.group(1)) * 10000.0)))
        if not found:
            missing.append(name)
        elif found != {EXPECTED_SENTINEL_Q}:
            wrong[name] = sorted(found)

    assert not missing, (
        "no open-ended-band sentinel could be read from: %s. Either the reader "
        "stopped substituting a ceiling for max_ru:null, or it spells it a third "
        "way this test does not recognise - extend the patterns knowingly."
        % missing
    )
    assert not wrong, (
        "inline band readers disagree on the open-ended ceiling (expected only "
        "%d = 99.0 ru): %s. Five phases would place a far-apart pair in a "
        "different range band than the sixth." % (EXPECTED_SENTINEL_Q, wrong)
    )
# [ Claude Fable 5 (claude-fable-5) | 2026-08-12 19:11 UTC | END ]
