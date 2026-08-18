// [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 07:15 UTC | START ]
#pragma once

#include "CoreMinimal.h"
#include "UppercutCanonSource.h"

// Phase L guard rules, extracted for the integrated session (Decision 0012).
// A posture covers a lane when its extent over that volume meets canon's
// interception threshold; commitment scales extents via
// guard_extent_multiplier_while_committed.

struct UPPERCUTCORE_API FUppercutGuardPosture
{
    TMap<FString, int64> Extents;   // volume id -> q10000
    int64 Mobility = 10000;
    int64 HoldPerTick = 0;
};

struct UPPERCUTCORE_API FUppercutGuardCanon
{
    TMap<FString, FUppercutGuardPosture> Postures;
    TMap<FString, FString> VolByClass;           // height class -> volume id
    TMap<FString, FString> HeightByInteraction;  // guard_interaction -> class
    TMap<FString, FString> InteractionByMove;    // move id -> interaction

    int64 Threshold = 0;
    int64 CommittedMultiplier = 6000;

    FString LaneOf(const FString& MoveId) const;
    TSet<FString> CoveredLanes(const FString& PostureId, bool bCommitted,
                               int32 ReadinessQ = 10000) const;
    bool Intercepts(const FString& PostureId, bool bCommitted,
                    const FString& MoveId, int32 ReadinessQ = 10000) const;
    int32 CanonErrors() const;
};

UPPERCUTCORE_API bool UppercutLoadGuardCanon(const FString& RepoDir,
                                             FUppercutGuardCanon& Out,
                                             TArray<FUppercutCanonSource>& OutSources,
                                             FString& OutError);
// [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 07:15 UTC | END ]
