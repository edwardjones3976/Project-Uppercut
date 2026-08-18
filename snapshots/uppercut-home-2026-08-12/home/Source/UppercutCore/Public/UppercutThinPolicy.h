// [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 02:53 UTC | START ]
#pragma once

#include "CoreMinimal.h"

// Thin observable policy for the integrated 1-round session.
// Decisions 0016 (G2 rest/observe/hold) and 0017 (aggression = initiative).
// Not full Phase S: enough that Play is not a nine-sided LCG die.
//
// Substream: Decision 0022 policy_intent/<participant>. The policy never
// receives contact/knockdown/judging draws.

enum class EUppercutThinTactic : uint8
{
    Observe,
    HoldPosition,
    Rest,
    Advance,
    Retreat,
    Attack,
    Guard,
    Evade
};

struct UPPERCUTCORE_API FUppercutThinDecision
{
    EUppercutThinTactic Tactic = EUppercutThinTactic::Observe;
    FString Execution;     // move id when Attack, else empty
    FString Reason;        // reason code for the stream
};

struct UPPERCUTCORE_API FUppercutThinObservation
{
    FString Band = TEXT("mid");
    FString PreferredBand = TEXT("mid");
    int32 WindFractionQ = 10000;     // q10000
    bool bWindLow = false;
    bool bOnRopes = false;
    bool bOpponentRecovering = false;
    bool bIncoming = false;
    TArray<FString> ThrowableHere;
};

struct UPPERCUTCORE_API FUppercutThinPolicy
{
    // aggression_bias as q10000 desire for initiative (Decision 0017).
    int32 AggressionBiasQ = 5000;
    FString PreferredBand = TEXT("mid");

    FUppercutThinDecision Decide(const FUppercutThinObservation& Obs,
                                 uint32& SubstreamX) const;
};

UPPERCUTCORE_API const TCHAR* UppercutThinTacticName(EUppercutThinTactic T);
// [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 02:53 UTC | END ]
