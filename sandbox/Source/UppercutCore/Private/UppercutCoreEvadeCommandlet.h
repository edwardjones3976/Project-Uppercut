// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 12:45 UTC | START ]
#pragma once

#include "CoreMinimal.h"
#include "Commandlets/Commandlet.h"
#include "UppercutCoreEvadeCommandlet.generated.h"

// Phase R: the head is not where the punch is going. Canon authors evasion
// GEOMETRICALLY - each evasion vacates named regions for an authored window and
// is beaten by named punch categories - so no die is needed and none is added.
//
// The whole rule, and it is canon's sentence rather than this port's: during an
// evasion's active window a punch aimed at a vacated region finds nothing there,
// UNLESS the punch is one the evasion is authored to be beaten by, in which case
// it lands into the movement.
//
// Contract: tools/engine/analyze_core_evade.py, mutation-proven before this
// class existed. Proven when its stream is byte-identical to that module's;
// the comparison is tools/engine/prove_core_evade.py.
//
// Usage:
//   UnrealEditor-Cmd <uproject> -run=UppercutCoreEvade
//       -seed=4242 -ticks=5400 -repo=<project-uppercut root> -out=<file>
UCLASS()
class UUppercutCoreEvadeCommandlet : public UCommandlet
{
    GENERATED_BODY()

public:
    virtual int32 Main(const FString& Params) override;
};
// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 12:45 UTC | END ]
