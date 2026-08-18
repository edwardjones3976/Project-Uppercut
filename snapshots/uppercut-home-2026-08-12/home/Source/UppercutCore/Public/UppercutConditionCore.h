// [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 07:45 UTC | START ]
#pragma once

#include "CoreMinimal.h"
#include "UppercutCanonSource.h"
#include "UppercutAttrCore.h"

struct UPPERCUTCORE_API FUppercutConditionRegion
{
    int32 Capacity = 100;
    bool bKnockdownRelevant = false;
};

struct UPPERCUTCORE_API FUppercutConditionCanon
{
    TMap<FString, FUppercutConditionRegion> Regions;
    TMap<FString, FString> PrimaryRegionByMove;
    TMap<FString, int64> EffortByMove;
    int64 PressureBaselineQ = 0;
    int64 CountReliefQ = 0;
    int32 CanonErrors() const;
};

struct UPPERCUTCORE_API FUppercutRegionalCondition
{
    TMap<FString, int32> Damage;

    void Reset(const FUppercutConditionCanon& Canon);
    int32 Absorb(const FUppercutConditionCanon& Canon,
                 const FString& Region, int32 Force);
    int32 WorstKnockdownFractionQ(const FUppercutConditionCanon& Canon) const;
    void ApplyCountRelief(const FUppercutConditionCanon& Canon);
};

UPPERCUTCORE_API bool UppercutLoadConditionCanon(
    const FString& RepoDir,
    FUppercutConditionCanon& Out,
    TArray<FUppercutCanonSource>& OutSources,
    FString& OutError);

UPPERCUTCORE_API int64 UppercutDeliveredImpactQ(
    const FUppercutConditionCanon& Canon, const FString& MoveId);

UPPERCUTCORE_API int64 UppercutKnockdownPressureQ(
    const FUppercutConditionCanon& Canon,
    const FString& MoveId,
    const FUppercutRegionalCondition& Defender,
    int32 DefenderWindFractionQ,
    bool bDefenderCommitted,
    bool bDefenderEvading,
    const FUppercutFighterCard& DefenderCard,
    const FUppercutAttrCanon& AttrCanon);
// [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 07:45 UTC | END ]
