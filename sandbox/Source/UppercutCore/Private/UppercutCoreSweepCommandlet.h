// [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 05:45 UTC | START ]
#pragma once

#include "CoreMinimal.h"
#include "Commandlets/Commandlet.h"
#include "UppercutCoreSweepCommandlet.generated.h"

// Phase J: real movement and swept collision (Decision 0012 slice item 5).
// The fist is an authored extension profile sampled per tick, swept as an
// interval, live only during animation_model's active ticks, evaluated
// against the defender's position at that tick. Lanes open and close from
// posture extents against pose_geometry's one interception threshold - the
// design promise ('body shots pay off against most guards') as geometry, not
// as a rule. Contract: tools/engine/analyze_core_sweep.py, mutation-proven
// before this class existed.
//
// Usage:
//   UnrealEditor-Cmd <uproject> -run=UppercutCoreSweep
//       -seed=4242 -ticks=5400 -repo=<project-uppercut root> -out=<file>
UCLASS()
class UUppercutCoreSweepCommandlet : public UCommandlet
{
    GENERATED_BODY()

public:
    virtual int32 Main(const FString& Params) override;
};
// [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 05:45 UTC | END ]
