// [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 05:10 UTC | START ]
#pragma once

#include "CoreMinimal.h"
#include "Commandlets/Commandlet.h"
#include "UppercutCoreLoopCommandlet.generated.h"

// Phase I: the two-fighter authoritative loop (Decision 0012 slice item 4).
// Two fighters, one clock, decisions interleaved in fixed index order, five
// canon files consumed in contract-defined integer arithmetic, plus the
// float-conformance probe whose result is reported either way. The contract
// lives in tools/engine/analyze_core_loop.py, mutation-proven before this
// class existed; nothing here is evidence until that analyzer says ok and
// A1 = A2 = A3(rebuild) != B1 byte-for-byte.
//
// Usage:
//   UnrealEditor-Cmd <uproject> -run=UppercutCoreLoop
//       -seed=4242 -ticks=5400 -repo=<project-uppercut root> -out=<file>
UCLASS()
class UUppercutCoreLoopCommandlet : public UCommandlet
{
    GENERATED_BODY()

public:
    virtual int32 Main(const FString& Params) override;
};
// [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 05:10 UTC | END ]
