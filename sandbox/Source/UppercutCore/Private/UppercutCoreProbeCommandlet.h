// [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 03:42 UTC | START ]
#pragma once

#include "CoreMinimal.h"
#include "Commandlets/Commandlet.h"
#include "UppercutCoreProbeCommandlet.generated.h"

// Phase H probe: canon bytes in, deterministic integer arithmetic, a
// self-hashing marker stream out. The contract lives in
// tools/engine/analyze_core_scaffold.py and was mutation-proven before this
// class existed; nothing this commandlet writes is evidence until that
// analyzer says PASS and A1 = A2 = A3(rebuild) != B1 byte-for-byte.
//
// Usage:
//   UnrealEditor-Cmd <uproject> -run=UppercutCoreProbe
//       -seed=7777 -steps=400 -canon=<data/movement_model.json> -out=<file>
UCLASS()
class UUppercutCoreProbeCommandlet : public UCommandlet
{
    GENERATED_BODY()

public:
    virtual int32 Main(const FString& Params) override;
};
// [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 03:42 UTC | END ]
