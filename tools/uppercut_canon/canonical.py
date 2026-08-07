# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 01:30 UTC | START ]
"""The semantic canonicalizer. Decision 0023, contract `uppercut-semantic-json-v1`.

TWO IDENTITIES, ONE FILE.

    raw hash      SHA-256 of the file's exact bytes. Provenance. Moves whenever
                  anything moves, including a corrected comment.
    semantic hash SHA-256 of the canonical encoding below, after removing the
                  fields the hash-role manifest explicitly declares
                  non-authoritative. Evidence. Moves when the fight can move.

WHY NOT `json.dumps(..., sort_keys=True)`. Because a C++ implementation has to
produce the same bytes, and two JSON serialisers agree on nothing that matters:
float formatting, string escaping, unicode escapes, separators,
integer-versus-float rendering. So the canonical form is NOT JSON. It is a small
typed byte stream with one representation per value, chosen so that a second
implementation has nothing left to decide.

    null        'n'
    false       'f'
    true        't'
    number      'd' u32be(len) ascii            fixed 10 decimal places
    string      's' u32be(len) utf-8 bytes      no escaping, ever
    array       'a' u32be(count) items...       order preserved, it is canon
    object      'o' u32be(count) (key value)... keys sorted by UTF-8 bytes

Numbers are always rendered `%.10f`, integers included, so `3500` and `3500.0`
are the same value and hash the same - which is right, they ARE the same value.
Anything that will not survive that round trip is REFUSED rather than rounded,
because silently truncating a canon value inside the evidence layer is the worst
bug this file could have.

The hashed payload is prefixed with the canonicalizer contract version and the
schema identity, per Decision 0023, so a change to this encoding moves every
semantic identity deliberately and visibly rather than by accident.
"""
import hashlib
import io
import json
import os
import struct

# How the bytes are produced.
CANONICALIZER_VERSION = "uppercut-semantic-json-v1"
# How the identity envelope in front of them is laid out.
HASH_CONTRACT_VERSION = "uppercut-hash-contract-v1"

# Kept as the old name so existing readers do not break; it is the canonicalizer
# version, which is what `canonicalizer_contract` in the manifest names.
CONTRACT = CANONICALIZER_VERSION

# 2**53: beyond this an integer is not exactly representable as a double, so the
# two languages could disagree about what the file even says.
_MAX_EXACT_INT = 9007199254740992


class CanonError(ValueError):
    """A canon file cannot be hashed, and guessing would be worse than failing."""


# ---------------------------------------------------------------- parsing ----

def _no_duplicate_keys(pairs):
    seen = {}
    for k, v in pairs:
        if k in seen:
            raise CanonError(
                "duplicate key %r - JSON parsers silently keep one of the two, "
                "so a file like this means different things to different "
                "readers and cannot have one identity" % k)
        seen[k] = v
    return seen


def _reject_constant(name):
    raise CanonError(
        "%s is not a canon value. It has no agreed encoding, no ordering, and "
        "in one of the two languages it silently poisons every arithmetic it "
        "touches" % name)


def parse(text):
    """Parse with duplicate keys refused and NaN/Infinity refused."""
    try:
        return json.loads(text, object_pairs_hook=_no_duplicate_keys,
                          parse_constant=_reject_constant)
    except CanonError:
        raise
    except ValueError as exc:
        raise CanonError("not parseable as JSON: %s" % exc)


# --------------------------------------------------------------- pointers ----

def _unescape(seg):
    return seg.replace("~1", "/").replace("~0", "~")


def parse_pointer(pattern):
    """RFC 6901, plus '*' meaning exactly one array index."""
    if pattern == "":
        raise CanonError("the whole document cannot be non-authoritative")
    if not pattern.startswith("/"):
        raise CanonError("pointer %r must start with '/'" % pattern)
    segs = [_unescape(s) for s in pattern[1:].split("/")]
    if segs[-1] == "*":
        raise CanonError(
            "pointer %r ends in a wildcard, which would delete whole array "
            "elements and renumber their neighbours. Array order is "
            "authoritative." % pattern)
    return segs


def expand(doc, pattern):
    """Every concrete pointer in `doc` that `pattern` actually matches."""
    segs = parse_pointer(pattern)
    out = []

    def walk(node, i, trail):
        if i == len(segs):
            out.append("/" + "/".join(trail))
            return
        seg = segs[i]
        if seg == "*":
            if not isinstance(node, list):
                return
            for idx, item in enumerate(node):
                walk(item, i + 1, trail + [str(idx)])
        else:
            if not isinstance(node, dict) or seg not in node:
                return
            walk(node[seg], i + 1, trail + [seg])

    walk(doc, 0, [])
    return out


def strip(doc, patterns):
    """Return a copy of `doc` with every matched pointer removed.

    Raises if a pattern matches nothing: a dead exclusion is how a list quietly
    widens to cover fields nobody reviewed.
    """
    matched = {}
    for pattern in patterns:
        hits = expand(doc, pattern)
        if not hits:
            raise CanonError(
                "hash-role pattern %r matches nothing in this file. Remove it "
                "or fix it - a pattern that matches nothing today may match "
                "something nobody reviewed tomorrow." % pattern)
        matched[pattern] = hits

    drop = set()
    for hits in matched.values():
        drop.update(hits)

    def prune(node, trail):
        if isinstance(node, dict):
            out = {}
            for k, v in node.items():
                here = "/" + "/".join(trail + [k])
                if here in drop:
                    continue
                out[k] = prune(v, trail + [k])
            return out
        if isinstance(node, list):
            return [prune(v, trail + [str(i)]) for i, v in enumerate(node)]
        return node

    return prune(doc, []), matched


# --------------------------------------------------------------- encoding ----

def _u32(n):
    return struct.pack(">I", n)


def _number(value):
    if value != value or value in (float("inf"), float("-inf")):
        raise CanonError("non-finite number")
    if isinstance(value, int):
        if abs(value) >= _MAX_EXACT_INT:
            raise CanonError(
                "integer %d is too large to be exactly representable as a "
                "double, so the two implementations could disagree about the "
                "value itself" % value)
    text = "%.10f" % value
    if float(text) != float(value):
        raise CanonError(
            "%r needs more precision than the canonical form's ten decimal "
            "places. Refused rather than rounded: quietly truncating a canon "
            "value inside the evidence layer would be undetectable." % value)
    # Requirement 3: -0, 0, -0.0 and 0.0 are one gameplay quantity. The RAW hash
    # still distinguishes how the source spelled it; the semantic one must not,
    # or a formatter that drops a minus sign would read as a retune.
    if text.startswith("-") and float(text) == 0.0:
        text = text[1:]
    return text


def encode(value):
    """The canonical byte stream for one JSON value."""
    if value is None:
        return b"n"
    if value is True:
        return b"t"
    if value is False:
        return b"f"
    if isinstance(value, (int, float)):
        raw = _number(value).encode("ascii")
        return b"d" + _u32(len(raw)) + raw
    if isinstance(value, str):
        raw = value.encode("utf-8")
        return b"s" + _u32(len(raw)) + raw
    if isinstance(value, list):
        out = [b"a", _u32(len(value))]
        out.extend(encode(v) for v in value)
        return b"".join(out)
    if isinstance(value, dict):
        items = sorted(value.items(), key=lambda kv: kv[0].encode("utf-8"))
        out = [b"o", _u32(len(items))]
        for k, v in items:
            raw = k.encode("utf-8")
            out.append(b"s" + _u32(len(raw)) + raw)
            out.append(encode(v))
        return b"".join(out)
    raise CanonError("value of type %s has no canonical form" % type(value).__name__)


def payload(doc, schema_identity, manifest_identity="", manifest_version=""):
    """The exact bytes that get hashed.

    DIRECTOR REQUIREMENT 6 - THE HASH RULES HASH THEMSELVES. Four identities are
    bound in front of the data, so that changing the rules used to decide
    "sameness" changes what sameness means:

        canonicalizer version   how bytes are produced
        hash-contract version   how this envelope is laid out
        schema identity         what the document claims to be
        manifest identity       which classification decided authority

    Without the last one, somebody could reclassify a live combat field as
    documentation and the evidence system would report a tidy, explicable hash
    change rather than an alarm.
    """
    parts = [
        CANONICALIZER_VERSION.encode("ascii"),
        HASH_CONTRACT_VERSION.encode("ascii"),
        schema_identity.encode("utf-8"),
        manifest_version.encode("utf-8"),
        manifest_identity.encode("ascii"),
    ]
    return b"\x00".join(parts) + b"\x00" + encode(doc)


# ------------------------------------------------------------------ public ----

def hashes(text, patterns=(), schema_identity="", manifest_identity="",
           manifest_version=""):
    """(raw_sha256, semantic_sha256, expansion) for one canon file's text.

    `text` is the file's exact decoded content; the raw hash is taken over its
    UTF-8 bytes so it is the provenance identity Decision 0023 asks for.
    """
    raw = hashlib.sha256(text.encode("utf-8")).hexdigest()
    doc = parse(text)
    stripped, matched = strip(doc, list(patterns))
    sem = hashlib.sha256(payload(stripped, schema_identity, manifest_identity,
                                 manifest_version)).hexdigest()
    return raw, sem, matched


def hashes_for_file(path, patterns=(), schema_identity="", manifest_identity="",
                    manifest_version=""):
    with io.open(path, "r", encoding="utf-8", newline="") as fh:
        return hashes(fh.read(), patterns, schema_identity, manifest_identity,
                      manifest_version)


# ---------------------------------------------------------------- manifest ----

class Manifest(object):
    """The hash-role manifest, and its own semantic identity.

    Requirement 1: this file is canon. It cannot decide what counts as
    authoritative from outside the evidence envelope.
    """

    def __init__(self, doc):
        self.doc = doc
        self.version = doc["manifest_version"]
        if doc.get("canonicalizer_contract") != CANONICALIZER_VERSION:
            raise CanonError(
                "manifest declares canonicalizer %r but this build is %r - "
                "refusing to hash under a contract it was not written for"
                % (doc.get("canonicalizer_contract"), CANONICALIZER_VERSION))
        if doc.get("hash_contract_version") != HASH_CONTRACT_VERSION:
            raise CanonError(
                "manifest declares hash contract %r but this build is %r"
                % (doc.get("hash_contract_version"), HASH_CONTRACT_VERSION))
        self.identity = self._identity()

    @classmethod
    def load(cls, path):
        with io.open(path, "r", encoding="utf-8", newline="") as fh:
            return cls(parse(fh.read()))

    def _identity(self):
        """Semantic hash of the manifest under its OWN declared exclusions.

        Bound with only the canonicalizer and manifest versions - binding the
        manifest identity into the computation of the manifest identity would
        not terminate. That shallower binding is declared in the file itself
        rather than left for the C++ port to rediscover.
        """
        stripped, _ = strip(self.doc, self.doc["self"]["non_authoritative"])
        head = (CANONICALIZER_VERSION.encode("ascii") + b"\x00"
                + self.version.encode("utf-8") + b"\x00")
        return hashlib.sha256(head + encode(stripped)).hexdigest()

    def patterns_for(self, rel):
        spec = self.doc["files"].get(rel)
        # Silence in the manifest means "hash the whole file", never "exclude
        # something". A file nobody classified is fully authoritative.
        return list(spec["non_authoritative"]) if spec else []

    def hashes_for(self, root, rel, schema_identity):
        return hashes_for_file(os.path.join(root, rel.replace("/", os.sep)),
                               self.patterns_for(rel), schema_identity,
                               self.identity, self.version)
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 01:30 UTC | END ]
