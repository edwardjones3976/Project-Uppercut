// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 03:40 UTC | START ]
#pragma once

#include "CoreMinimal.h"
#include "Commandlets/Commandlet.h"
#include "UppercutCanonVectorsCommandlet.generated.h"

// Decision 0023 step 4: cross-language parity, checked rather than assumed.
//
// Feeds tests/fixtures/canon_hash_vectors.json through the C++ canonicalizer
// and writes a report. Every accept vector must reproduce both hashes exactly;
// every rejection vector must be REFUSED. A C++ side that merely fails to crash
// would prove nothing - the refusals carry as much of the contract as the
// hashes do, because they are what stops a malformed canon file from quietly
// acquiring an identity.
//
// Usage:
//   UnrealEditor-Cmd <uproject> -run=UppercutCanonVectors
//       -repo=<project-uppercut root> -out=<file>
UCLASS()
class UUppercutCanonVectorsCommandlet : public UCommandlet
{
    GENERATED_BODY()

public:
    virtual int32 Main(const FString& Params) override;
};
// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 03:40 UTC | END ]
