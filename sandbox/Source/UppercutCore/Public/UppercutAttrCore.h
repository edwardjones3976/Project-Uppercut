// [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 02:53 UTC | START ]
#pragma once

#include "CoreMinimal.h"

// Attribute multipliers for the integrated 1-round session.
// Same mapping as tools/uppercut_integrated/attributes.py and
// tools/uppercut_sim/engine.py Bout._attr: silent card => 1.0 (q10000 ONE).

static constexpr int64 UppercutAttrOne = 10000;

struct UPPERCUTCORE_API FUppercutAttrEffect
{
    FString Attribute;
    FString Scales;
    int64 MultAtMinus100 = UppercutAttrOne;
    int64 MultAtPlus100 = UppercutAttrOne;
};

struct UPPERCUTCORE_API FUppercutFighterCard
{
    FString Id;
    TMap<FString, int32> Attributes;   // -100..+100

    int32 Get(const FString& Key) const
    {
        const int32* V = Attributes.Find(Key);
        return V ? *V : 0;
    }
};

struct UPPERCUTCORE_API FUppercutAttrCanon
{
    TArray<FUppercutAttrEffect> Effects;

    int64 Multiplier(const FUppercutFighterCard& Card, const FString& Scales) const;
    int64 Apply(int64 ValueQ, const FUppercutFighterCard& Card, const FString& Scales) const;
};

UPPERCUTCORE_API bool UppercutLoadAttrCanon(const FString& RepoDir,
                                            FUppercutAttrCanon& Out,
                                            FString& OutError);

UPPERCUTCORE_API bool UppercutLoadFighterCard(const FString& RepoDir,
                                              const FString& FighterId,
                                              FUppercutFighterCard& Out,
                                              FString& OutError);
// [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 02:53 UTC | END ]
