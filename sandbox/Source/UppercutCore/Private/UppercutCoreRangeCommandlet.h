// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 21:20 UTC | START ]
#pragma once

#include "CoreMinimal.h"
#include "Commandlets/Commandlet.h"
#include "UppercutCoreRangeCommandlet.generated.h"

// Phase Q: the fight gets a distance. Two fighters on canon's ring axis, a
// stride delivered over several ticks by the per-frame displacement cap, five
// bands with hysteresis, and Rule 12's range gate tested at THROW time - a
// punch from the wrong band travels its whole arc into empty air and whiffs
// even when the fist demonstrably arrived.
//
// Contract: tools/engine/analyze_core_range.py, mutation-proven before this
// class existed. This commandlet is proven when its stream is byte-identical
// to that module's `expected_stream` for the same seed and tick count; the
// comparison is tools/engine/run_core_range.ps1.
//
// Usage:
//   UnrealEditor-Cmd <uproject> -run=UppercutCoreRange
//       -seed=4242 -ticks=5400 -repo=<project-uppercut root> -out=<file>
UCLASS()
class UUppercutCoreRangeCommandlet : public UCommandlet
{
    GENERATED_BODY()

public:
    virtual int32 Main(const FString& Params) override;
};
// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 21:20 UTC | END ]
