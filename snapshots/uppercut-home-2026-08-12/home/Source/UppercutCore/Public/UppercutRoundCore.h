// [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 02:53 UTC | START ]
#pragma once

#include "CoreMinimal.h"
#include "UppercutConditionCore.h"

// One-round ending: knockdown, mandatory count, rise/fail/stoppage, or
// sealed 10-point-must decision. Professional ruleset: no 3-KD auto-stop.
// pressure_threshold stays 0.57 (Decisions 0035-0037).

enum class EUppercutRoundPhase : uint8
{
    Boxing,
    Counting,
    Finished
};

enum class EUppercutRoundResult : uint8
{
    None,
    Decision,
    CountExpired,
    RefereeStoppage,
    KnockdownLimit
};

struct UPPERCUTCORE_API FUppercutRoundCanon
{
    int64 PressureThresholdQ = 5700;   // 0.57
    int32 CountTicksPerNumber = 60;
    int32 MandatoryEight = 8;
    int32 CountTo = 10;
    bool bMandatoryEight = true;
    // Professional: null limits mean no auto-stop by KD count.
    bool bHasRoundKdLimit = false;
    int32 RoundKdLimit = 0;
    bool bHasBoutKdLimit = false;
    int32 BoutKdLimit = 0;
    int32 RoundWin = 10;
    int32 RoundLose = 9;
};

struct UPPERCUTCORE_API FUppercutRoundState
{
    EUppercutRoundPhase Phase = EUppercutRoundPhase::Boxing;
    EUppercutRoundResult Result = EUppercutRoundResult::None;
    int32 Tick = 0;
    int32 TickBudget = 0;
    int32 DownedFighter = -1;
    int32 CountNumber = 0;
    int32 CountTicksLeft = 0;
    int32 KdRound[2] = {0, 0};
    int32 KdBout[2] = {0, 0};
    int32 Landed[2] = {0, 0};
    int32 Card[2] = {0, 0};          // sealed until Finished
    bool bCardsSealed = true;
    int32 Winner = -1;               // 0/1, or -1 draw
    FString Method;

    void Reset(int32 InBudget);
    void WitnessLanding(int32 Scorer);
    bool TryKnockdown(int32 Defender, int64 PressureQ, int64 ThresholdQ,
                      const FUppercutRoundCanon& Canon,
                      TArray<FString>* OutRows);
    bool CheckKnockdownLimitStoppage(const FUppercutRoundCanon& Canon,
                                     TArray<FString>* OutRows);
    void TickCount(const FUppercutRoundCanon& Canon,
                   const FUppercutConditionCanon& CondCanon,
                   FUppercutRegionalCondition& Cond0,
                   FUppercutRegionalCondition& Cond1,
                   TArray<FString>* OutRows);
    void SealDecision(TArray<FString>* OutRows);
    bool IsFinished() const { return Phase == EUppercutRoundPhase::Finished; }
};

UPPERCUTCORE_API bool UppercutLoadRoundCanon(const FString& RepoDir,
                                             const FString& RulesetId,
                                             FUppercutRoundCanon& Out,
                                             FString& OutError);
// [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 02:53 UTC | END ]
