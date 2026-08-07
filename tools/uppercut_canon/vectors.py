# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 02:30 UTC | START ]
"""Generate the cross-language test vectors. Decision 0023 step 2.

    python -m tools.uppercut_canon.vectors

The C++ canonicalizer must reproduce every semantic hash below from the same
input, patterns and schema identity, and must refuse every rejection vector.

The cases are chosen for the places two implementations drift rather than for
coverage of ordinary data: key sorting where '$' and '_' sit either side of the
letters in ASCII, non-ASCII strings, negative zero, the tenth-decimal boundary,
integers spelled as floats, and nested arrays.
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

from tools.uppercut_canon import canonical as C  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))), "tests", "fixtures", "canon_hash_vectors.json")

# Fixed, deliberately not the real manifest's identity: the vectors must be
# checkable by an implementation that has never read data/hash_roles.json.
MANIFEST_ID = "0" * 64
MANIFEST_VERSION = "uppercut-hash-roles-v1"

CASES = [
    ("empty_object", "obj-v1", [], {}),
    ("negative_zero_is_zero", "negz-v1", [],
     {"a": -0.0, "b": 0.0, "c": 0, "d": -0}),
    ("scalars", "scal-v1", [], {"n": None, "t": True, "f": False,
                                "i": 3500, "fl": 0.132, "neg": -12.5,
                                "zero": 0, "negzero": -0.0}),
    ("key_sorting", "sort-v1", [], {"b": 1, "A": 2, "a": 3, "_": 4, "$c": 5}),
    ("unicode", "uni-v1", [], {"s": "café — 日本語"}),
    ("nested_arrays", "arr-v1", [], {"bands": [[0, 1], [2, 3]], "m": [{"i": 1}]}),
    ("precision_edge", "prec-v1", [], {"x": 0.0000000001, "y": 123.45678901}),
    ("exclusions", "excl-v1",
     ["/$comment", "/contribution", "/guard/$comment",
      "/guard/authoring_margin_note", "/moves/*/note"],
     {"$comment": "header prose",
      "contribution": {"agent": "a", "model": "m"},
      "guard": {"$comment": "p", "authoring_margin": 0.05,
                "authoring_margin_note": "p2",
                "plane_interception_min_extent": 0.6},
      "moves": [{"id": "jab_lead", "cost": 1.0, "note": "p"},
                {"id": "step_in", "cost": 0.132, "cost_model": "displacement",
                 "note": "p"}],
      "bands": [0, 1, 2]}),
]

REJECTIONS = [
    ("duplicate_keys", '{"a": 1, "a": 2}', [], "duplicate key"),
    ("nan", '{"x": NaN}', [], "non-finite"),
    ("infinity", '{"x": Infinity}', [], "non-finite"),
    ("too_precise", '{"x": 0.00000000001}', [], "precision"),
    ("dead_pattern", '{"a": 1}', ["/nope"], "pattern matches nothing"),
    ("wildcard_terminal", '{"m": [{"x": 1}]}', ["/m/*"],
     "wildcard may not end a pattern"),
]


def build():
    out = {
        "$comment": ("Cross-language fixtures for Decision 0023 step 4. The C++ "
                     "canonicalizer must reproduce every semantic_sha256 below "
                     "byte for byte from the same input_json, patterns and "
                     "schema_identity. A disagreement here means the two "
                     "runtimes do not share one notion of canon identity, which "
                     "would make every dual-hash header a guess."),
        "canonicalizer_contract": C.CONTRACT,
        "vectors": [],
        "rejection_vectors": [],
    }
    # A FIXED manifest identity and version, so the vectors are self-contained
    # and the C++ side does not need the real manifest to check parity. The
    # values are part of the binding under requirement 6, so they are stated per
    # vector rather than assumed.
    out["manifest_identity"] = MANIFEST_ID
    out["manifest_version"] = MANIFEST_VERSION
    out["hash_contract_version"] = C.HASH_CONTRACT_VERSION
    for name, schema, pats, doc in CASES:
        text = json.dumps(doc)
        raw, sem, _ = C.hashes(text, pats, schema, MANIFEST_ID, MANIFEST_VERSION)
        out["vectors"].append({
            "name": name, "schema_identity": schema, "patterns": pats,
            "manifest_identity": MANIFEST_ID, "manifest_version": MANIFEST_VERSION,
            "input_json": text, "raw_sha256": raw, "semantic_sha256": sem,
        })
    for name, text, pats, why in REJECTIONS:
        out["rejection_vectors"].append({
            "name": name, "input_json": text, "patterns": pats,
            "schema_identity": "rej-v1", "must_reject": why,
        })
    return out


def main():
    data = build()
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print("wrote %s" % OUT)
    for v in data["vectors"]:
        print("  %-16s %s" % (v["name"], v["semantic_sha256"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 02:30 UTC | END ]
