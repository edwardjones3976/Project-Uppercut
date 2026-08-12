# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 08:00 UTC | START ]
"""The semantic canonicalizer. Decisions 0023 and 0024.

TWO IDENTITIES PER FILE.

    raw hash      SHA-256 of the file's exact bytes. Provenance. Moves whenever
                  anything moves, including a corrected comment.
    semantic hash SHA-256 of the canonical encoding, after removing the fields
                  the hash-role manifest explicitly declares non-authoritative.
                  Evidence. Moves when the fight can move.

THREE IDENTITIES DECIDE WHAT "SEMANTIC" MEANS (Decision 0024).

    global policy identity   contract-wide rules that genuinely affect every
                             canon file: canonicalizer and hash-contract
                             versions, manifest version, wildcard semantics,
                             unknown-field policy, numeric and pointer rules.
    per-file role-set        only the target file's own excluded pointers,
                             binding the global policy.
    file semantic identity   the file's authoritative payload, binding both.

The first prototype bound the WHOLE manifest into every file, which was
fail-safe and far too broad: reclassifying a comment in one file moved the
identity of phases that never read it. Decision 0024 narrows the dependency
graph to the smallest honest scope while keeping the rule that classification
is evidence.

WHY THE CANONICAL FORM IS NOT JSON. A C++ implementation must produce the same
bytes, and two JSON serialisers agree on nothing that matters: float formatting,
string escaping, unicode escapes, separators, integer-versus-float rendering. So
the canonical form is a typed byte stream with one representation per value.

    null        'n'
    false       'f'
    true        't'
    number      'd' u32be(len) ascii            fixed 10 decimal places
    string      's' u32be(len) utf-8 bytes      no escaping, ever
    array       'a' u32be(count) items...       order preserved, it is canon
    object      'o' u32be(count) (key value)... keys sorted by UTF-8 bytes

POINTERS ARE SEGMENT TUPLES INTERNALLY, never reconstructed slash strings.
RFC 6901 escapes `/` as `~1`, so the pointer `/a~1b` names the single key
"a/b" while `/a/b` names "a" then "b". Joining segments with "/" to compare
them makes those two the same path - a literal alias that could drop a field
nobody classified. Strings are produced only for humans, at the edge.
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

# Kept as the old name so existing readers do not break.
CONTRACT = CANONICALIZER_VERSION

# 2**53: beyond this an integer is not exactly representable as a double, so the
# two languages could disagree about what the file even says.
_MAX_EXACT_INT = 9007199254740992

# The manifest keys that are GLOBAL policy - they change how every file is
# classified, so they belong in the global identity. `files` is deliberately
# absent: that is per-file scope (Decision 0024).
POLICY_KEYS = ("manifest_version", "canonicalizer_contract",
               "hash_contract_version", "default_role", "rules", "coverage",
               "self")


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
    """RFC 6901: ~1 is '/', ~0 is '~', and ~1 must be decoded FIRST.

    Decoding ~0 first would turn "~01" into "~1" and then into "/", so a key
    literally named "~1" would become "/". The order is the specification's.
    """
    return seg.replace("~1", "/").replace("~0", "~")


def escape_segment(seg):
    """RFC 6901 escaping, for display only. ~ first, then /."""
    return seg.replace("~", "~0").replace("/", "~1")


def serialize_pointer(segments):
    """Segment tuple -> an RFC 6901 string a human can read.

    Only ever used for messages and snapshots. Nothing compares these.
    """
    return "".join("/" + escape_segment(s) for s in segments)


def parse_pointer(pattern):
    """RFC 6901 -> a tuple of segments, plus '*' meaning one array index."""
    if pattern == "":
        raise CanonError("the whole document cannot be non-authoritative")
    if not pattern.startswith("/"):
        raise CanonError("pointer %r must start with '/'" % pattern)
    segs = tuple(_unescape(s) for s in pattern[1:].split("/"))
    if segs[-1] == "*":
        raise CanonError(
            "pointer %r ends in a wildcard, which would delete whole array "
            "elements and renumber their neighbours. Array order is "
            "authoritative." % pattern)
    return segs


def expand(doc, pattern):
    """Every concrete path in `doc` that `pattern` matches, as SEGMENT TUPLES.

    Tuples, not strings: `/a~1b` and `/a/b` are different paths and joining
    segments with "/" would make them the same one.
    """
    segs = parse_pointer(pattern)
    out = []

    def walk(node, i, trail):
        if i == len(segs):
            out.append(tuple(trail))
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
    """Return (pruned copy, {pattern: [segment tuples]}).

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
                here = trail + (k,)
                if here in drop:
                    continue
                out[k] = prune(v, here)
            return out
        if isinstance(node, list):
            return [prune(v, trail + (str(i),)) for i, v in enumerate(node)]
        return node

    return prune(doc, ()), matched


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
    # still distinguishes how the source spelled it.
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


def payload(doc, schema_identity, policy_identity="", role_set_identity=""):
    """The exact bytes that get hashed.

    Decision 0023 requirement 6, narrowed by Decision 0024. Four identities are
    bound in front of the data, so changing the rules that decide "sameness"
    changes what sameness means - but only the rules that actually govern THIS
    file:

        canonicalizer version   how bytes are produced
        hash-contract version   how this envelope is laid out
        schema identity         what the document claims to be
        global policy identity  contract-wide classification rules
        role-set identity       THIS file's own excluded pointers
    """
    parts = [
        CANONICALIZER_VERSION.encode("ascii"),
        HASH_CONTRACT_VERSION.encode("ascii"),
        schema_identity.encode("utf-8"),
        policy_identity.encode("ascii"),
        role_set_identity.encode("ascii"),
    ]
    return b"\x00".join(parts) + b"\x00" + encode(doc)


# ------------------------------------------------------------------ public ----

def canonical_bytes(text, patterns=()):
    """The canonical payload WITHOUT the identity envelope.

    Decision 0024 asks for canonical bytes to be compared before hashes, so a
    cross-language disagreement shows WHERE the encoders differ instead of only
    that two hex strings differ.
    """
    doc = parse(text)
    stripped, _ = strip(doc, list(patterns))
    return encode(stripped)


def hashes(text, patterns=(), schema_identity="", policy_identity="",
           role_set_identity=""):
    """(raw_sha256, semantic_sha256, expansion) for one canon file's text."""
    raw = hashlib.sha256(text.encode("utf-8")).hexdigest()
    doc = parse(text)
    stripped, matched = strip(doc, list(patterns))
    sem = hashlib.sha256(payload(stripped, schema_identity, policy_identity,
                                 role_set_identity)).hexdigest()
    return raw, sem, matched


def hashes_for_file(path, patterns=(), schema_identity="", policy_identity="",
                    role_set_identity=""):
    with io.open(path, "r", encoding="utf-8", newline="") as fh:
        return hashes(fh.read(), patterns, schema_identity, policy_identity,
                      role_set_identity)


# ---------------------------------------------------------------- manifest ----

class Manifest(object):
    """The hash-role manifest, with Decision 0024's precise dependency scope.

    Three identities, and the difference between them is the whole ruling:

        raw_hash          the manifest's exact bytes. Provenance only.
        policy_identity   the rules that govern EVERY file.
        role_set(rel)     the pointers that govern ONE file.
    """

    def __init__(self, doc, raw_text=None):
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
        self.raw_hash = (hashlib.sha256(raw_text.encode("utf-8")).hexdigest()
                         if raw_text is not None else "")
        self.policy_identity = self._policy_identity()

    @classmethod
    def load(cls, path):
        with io.open(path, "r", encoding="utf-8", newline="") as fh:
            text = fh.read()
        # [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 03:13 UTC | START ]
        # Provenance is repository bytes (LF). A Windows checkout may present
        # CRLF for the same commit; normalize before hashing so roles_raw is
        # platform-stable and goldens do not drift on windows-authority.
        if "\r" in text:
            text = text.replace("\r\n", "\n").replace("\r", "\n")
        # [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 03:13 UTC | END ]
        return cls(parse(text), text)

    # -- global policy --------------------------------------------------------

    def _policy_identity(self):
        """The contract-wide rules, and nothing about any particular file.

        `files` is excluded on purpose: that is per-file scope. Prose inside the
        policy blocks is excluded by the manifest's own `self` declarations, so
        rewording a rule's explanation does not move every identity in the
        project - but changing the rule itself does.
        """
        policy = {k: self.doc[k] for k in POLICY_KEYS if k in self.doc}
        # The manifest's own documentation exclusions apply to the policy view
        # too; only those that actually point inside it.
        wanted = []
        for pattern in self.doc.get("self", {}).get("non_authoritative", []):
            segs = parse_pointer(pattern)
            if segs and segs[0] in POLICY_KEYS:
                wanted.append(pattern)
        stripped, _ = strip(policy, wanted) if wanted else (policy, {})
        head = (CANONICALIZER_VERSION.encode("ascii") + b"\x00"
                + HASH_CONTRACT_VERSION.encode("ascii") + b"\x00"
                + self.version.encode("utf-8") + b"\x00")
        return hashlib.sha256(head + encode(stripped)).hexdigest()

    # -- per-file scope -------------------------------------------------------

    def patterns_for(self, rel):
        spec = self.doc["files"].get(rel)
        # Silence in the manifest means "hash the whole file", never "exclude
        # something". A file nobody classified is fully authoritative.
        return list(spec["non_authoritative"]) if spec else []

    def is_classified(self, rel):
        return rel in self.doc["files"]

    def role_set_identity(self, rel):
        """Only this file's excluded pointers, binding the global policy.

        A file with no entry still gets a role-set identity - the identity of
        "nothing is excluded here" - so that classifying a previously unlisted
        file MOVES its semantic hash rather than silently changing what it
        covers.
        """
        patterns = self.patterns_for(rel)
        body = {"file": rel, "non_authoritative": patterns,
                "classified": self.is_classified(rel)}
        head = self.policy_identity.encode("ascii") + b"\x00"
        return hashlib.sha256(head + encode(body)).hexdigest()

    def hashes_for(self, root, rel, schema_identity):
        return hashes_for_file(os.path.join(root, rel.replace("/", os.sep)),
                               self.patterns_for(rel), schema_identity,
                               self.policy_identity,
                               self.role_set_identity(rel))

    def canonical_bytes_for(self, root, rel):
        path = os.path.join(root, rel.replace("/", os.sep))
        with io.open(path, "r", encoding="utf-8", newline="") as fh:
            return canonical_bytes(fh.read(), self.patterns_for(rel))
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 08:00 UTC | END ]
