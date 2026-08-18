// [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 07:35 UTC | START ]
#pragma once

#include "CoreMinimal.h"
#include "UppercutCanonSource.h"

struct UPPERCUTCORE_API FUppercutPunchEconomyCanon
{
    TMap<FString, int64> RecoveryMultiplierQ;   // outcome class -> q10000
    TMap<FString, FString> HandByMove;
    int64 PerThrowSameArm = 0;
    int64 RecoveryPerIdleTick = 0;
    int64 MaxArmMultiplierQ = 10000;
    int64 RuCededPerThrowWithoutStep = 0;
    int32 CanonErrors() const;
};

UPPERCUTCORE_API bool UppercutLoadPunchEconomyCanon(
    const FString& RepoDir,
    FUppercutPunchEconomyCanon& Out,
    TArray<FUppercutCanonSource>& OutSources,
    FString& OutError);

UPPERCUTCORE_API int64 UppercutArmMultiplierQ(
    const FUppercutPunchEconomyCanon& Canon, int64 ArmWorkQ);

UPPERCUTCORE_API int64 UppercutApplyOutcomeRecovery(
    const FUppercutPunchEconomyCanon& Canon,
    const FString& OutcomeClass, int32 BaseRecoveryTicks);
// [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 07:35 UTC | END ]
