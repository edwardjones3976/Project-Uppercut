# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 04:40 UTC | START ]
"""The dual-hash stream header. Decision 0023.

One builder, used by every phase, so five analyzers cannot drift into five
opinions about what a header says. The C++ counterpart is
`UppercutCanonHeaderLines` and the two are held together by the parity vectors.

    H|canon_hash_contract=uppercut-hash-contract-v1
    H|canon_hash_roles=uppercut-hash-roles-v1
    H|canon_hash_roles_id=<sha256 of the manifest under its own exclusions>
    H|canon_<label>_semantic=<sha256>     the load-bearing identity
    H|canon_<label>_raw=<sha256>          exact-byte provenance

Decision 0023 prohibits an unlabelled `canon_<name>` hash in a new contract, and
that prohibition is the whole point: the old header could not say WHICH question
its number answered, so a corrected comment and a retuned value produced the
same kind of change.

The manifest's identity is in the header as well as inside every semantic hash.
Inside, it makes reclassification move the number; here, it lets a reader see
which classification was in force without recomputing anything.
"""
import io
import os

from tools.uppercut_canon import canonical as C


def load_manifest(repo):
    return C.Manifest.load(os.path.join(repo, "data", "hash_roles.json"))


def schema_identity_for(repo, rel):
    """What the document claims to be: which file, at which schema version.

    Including the path means two canon files that happened to hold identical
    values still have different identities, which is correct - they are
    different dependencies. Including the declared schema_version means a schema
    bump moves identity deliberately rather than silently.
    """
    path = os.path.join(repo, rel.replace("/", os.sep))
    with io.open(path, "r", encoding="utf-8", newline="") as fh:
        doc = C.parse(fh.read())
    version = ""
    if isinstance(doc, dict):
        version = doc.get("schema_version") or ""
    return "%s@%s" % (rel, version)


def canon_header_lines(repo, entries, manifest=None):
    """`entries` is [(label, relative_path), ...] in the phase's declared order.

    Returns the H| lines WITHOUT trailing newlines, for a caller that joins them
    the way its own stream does.
    """
    man = manifest or load_manifest(repo)
    lines = [
        "H|canon_hash_contract=%s" % C.HASH_CONTRACT_VERSION,
        "H|canon_hash_roles=%s" % man.version,
        "H|canon_hash_roles_id=%s" % man.identity,
    ]
    for label, rel in entries:
        raw, sem, _ = man.hashes_for(repo, rel, schema_identity_for(repo, rel))
        lines.append("H|canon_%s_semantic=%s" % (label, sem))
        lines.append("H|canon_%s_raw=%s" % (label, raw))
    return lines


def verify_header(repo, heads, entries, manifest=None):
    """Check a stream's header against the canon on disk. Returns errors.

    `heads` is the parsed H| map, without the "H|" or the "canon_" prefix
    stripped - keys are exactly as they appear, e.g. "canon_pose_raw".

    BOTH identities are checked, and they answer different questions:

      raw       is this the same FILE the stream was written from?
      semantic  is it the same FIGHT that file describes?

    Checking only raw would make the migration cosmetic - the stream would
    carry a semantic hash nothing ever verified. Checking only semantic would
    lose the provenance the raw hash exists to give.
    """
    man = manifest or load_manifest(repo)
    errors = []

    if heads.get("canon_hash_contract") != C.HASH_CONTRACT_VERSION:
        errors.append("the stream was written under hash contract %r, not %r"
                      % (heads.get("canon_hash_contract"),
                         C.HASH_CONTRACT_VERSION))
    if heads.get("canon_hash_roles_id") != man.identity:
        errors.append(
            "the stream was written under a different hash-role manifest "
            "(%s), so its exclusions were decided by rules this checkout does "
            "not have" % (heads.get("canon_hash_roles_id") or "none"))

    for label, rel in entries:
        raw, sem, _ = man.hashes_for(repo, rel, schema_identity_for(repo, rel))
        if heads.get("canon_%s_raw" % label) != raw:
            errors.append("canon_%s_raw does not match the local file" % label)
        if heads.get("canon_%s_semantic" % label) != sem:
            errors.append("canon_%s_semantic does not match the local file - "
                          "an authoritative value moved" % label)
    return errors
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 04:40 UTC | END ]
