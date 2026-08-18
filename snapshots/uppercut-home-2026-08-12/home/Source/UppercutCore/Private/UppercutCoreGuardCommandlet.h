// [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 07:40 UTC | START ]
#pragma once

#include "CoreMinimal.h"
#include "Commandlets/Commandlet.h"
#include "UppercutCoreGuardCommandlet.generated.h"

// Phase L: guard and slip (Decision 0012 slice item 7). Posture switching
// makes lane coverage per-fighter and dynamic (high_guard <-> tight_elbow,
// the mirror pair the data picks at the one interception threshold); the
// slip is a frame-locked active evasion window that outranks guard; and
// committed_defense degrades a mid-action defender's extents so the counter
// window is real. Contract: tools/engine/analyze_core_guard.py, mutation-
// proven before this class existed.
//
// Usage:
//   UnrealEditor-Cmd <uproject> -run=UppercutCoreGuard
//       -seed=4242 -ticks=5400 -repo=<project-uppercut root> -out=<file>
UCLASS()
class UUppercutCoreGuardCommandlet : public UCommandlet
{
    GENERATED_BODY()

public:
    virtual int32 Main(const FString& Params) override;
};
// [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 07:40 UTC | END ]
