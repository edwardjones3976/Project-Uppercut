// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 19:55 UTC | START ]
#pragma once

#include "CoreMinimal.h"

// One canon file as it was actually read: its path, the label the marker stream
// calls it by, and the SHA-256 of the exact bytes that were parsed.
//
// This lives in its own header because every phase's loader returns it, and a
// phase should not have to include another phase's rules to describe where its
// canon came from.
//
// The hash and the parse come from ONE read, deliberately. A header that hashes
// the files separately is asserting the fight ran on those bytes; one built this
// way has actually parsed them.
struct UPPERCUTCORE_API FUppercutCanonSource
{
    FString RelPath;
    FString Label;
    FString Sha256;
};

// SHA-256 (FIPS 180-4) of a byte range, lowercase hex. File-local to this
// module rather than a platform library's, so a stream header never depends on
// which version of anything is installed.
UPPERCUTCORE_API FString UppercutSha256Hex(const uint8* Data, uint64 Len);
// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 19:55 UTC | END ]
