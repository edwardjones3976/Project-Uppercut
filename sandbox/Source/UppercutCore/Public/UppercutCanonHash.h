// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 03:20 UTC | START ]
#pragma once

#include "CoreMinimal.h"

// The C++ half of Decision 0023. It must agree with
// tools/uppercut_canon/canonical.py BYTE FOR BYTE, which is why almost nothing
// here is left to the platform.
//
// WHY THIS DOES NOT USE FJsonSerializer.
// Decision 0023 requires duplicate JSON keys to be REJECTED. Unreal's JSON
// object silently keeps one of the two, and it is the reader that decides
// which. An evidence layer must not depend on a parser whose behaviour it
// cannot control on the one case it is required to detect - so this carries its
// own strict reader. It is small, it refuses more than it accepts, and refusing
// is the correct bias for code that decides whether other evidence counts.
//
// The canonical encoding, identical to the Python contract:
//
//     null    'n'
//     false   'f'
//     true    't'
//     number  'd' u32be(len) ascii          always %.10f, integers included
//     string  's' u32be(len) utf-8 bytes    no escaping, ever
//     array   'a' u32be(count) items...     order preserved - order is canon
//     object  'o' u32be(count) (key value)  keys sorted by UTF-8 bytes
//
// Four identities are bound in front of the data (Director requirement 6), so
// changing the rules that decide sameness changes what sameness means.

UPPERCUTCORE_API extern const TCHAR* UppercutCanonicalizerVersion;   // uppercut-semantic-json-v1
UPPERCUTCORE_API extern const TCHAR* UppercutHashContractVersion;    // uppercut-hash-contract-v1

// Compute both identities for one canon document.
//
//   OutRaw       SHA-256 of the text's UTF-8 bytes - provenance.
//   OutSemantic  SHA-256 of the bound canonical payload - evidence.
//
// Returns false and fills OutError on any refusal: duplicate keys, non-finite
// numbers, a value needing more than ten decimal places, a pattern that matches
// nothing, a pattern ending in a wildcard, or malformed JSON. Refusal is never
// silently downgraded to a hash.
UPPERCUTCORE_API bool UppercutCanonHashes(const FString& JsonText,
                                          const TArray<FString>& Patterns,
                                          const FString& SchemaIdentity,
                                          const FString& PolicyIdentity,
                                          const FString& RoleSetIdentity,
                                          FString& OutRaw,
                                          FString& OutSemantic,
                                          FString& OutError);

// The canonical payload WITHOUT the identity envelope. Decision 0024 asks for
// canonical BYTES to be compared before hashes, so a cross-language
// disagreement names WHERE the encoders differ instead of only that two hex
// strings do.
UPPERCUTCORE_API bool UppercutCanonicalBytes(const FString& JsonText,
                                             const TArray<FString>& Patterns,
                                             TArray<uint8>& OutBytes,
                                             FString& OutError);

// Decision 0024's per-file scope: only this file's excluded pointers, binding
// the global policy. `bClassified` distinguishes "declared with no exclusions"
// from "not declared at all", so classifying a previously unlisted file MOVES
// its identity rather than silently changing what it covers.
UPPERCUTCORE_API bool UppercutCanonRoleSetIdentity(const FString& PolicyIdentity,
                                                   const FString& Rel,
                                                   const TArray<FString>& Patterns,
                                                   bool bClassified,
                                                   FString& OutIdentity);

// The hash-role manifest's own semantic identity, under its own declared
// exclusions (`/self/non_authoritative`). Bound with only the canonicalizer and
// manifest versions, because binding the manifest identity into the computation
// of the manifest identity would not terminate - the same shallower binding the
// Python side documents and the manifest itself declares.
UPPERCUTCORE_API bool UppercutCanonManifestIdentity(const FString& ManifestJson,
                                                    FString& OutIdentity,
                                                    FString& OutVersion,
                                                    FString& OutError);

// The dual-hash stream header, byte-identical to
// tools/uppercut_canon/header.py::canon_header_lines. `Entries` is
// (label, repo-relative path) in the phase's declared order.
//
// Each returned line has NO trailing newline, so a caller joins them the way
// its own stream does. Decision 0023 prohibits an unlabelled `canon_<name>`
// hash in a new contract - the header must say which question its number
// answers.
UPPERCUTCORE_API bool UppercutCanonHeaderLines(
    const FString& RepoDir,
    const TArray<TPair<FString, FString>>& Entries,
    TArray<FString>& OutLines,
    FString& OutError);
// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 03:20 UTC | END ]
