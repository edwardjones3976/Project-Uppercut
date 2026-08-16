// [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 02:53 UTC | START ]
#pragma once

#include "CoreMinimal.h"

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
    // [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-16 00:50 UTC |
    //   edit: a round STARTS unsealed; SealDecision is what seals it. The flag
    //   was inverted at all three sites and nothing read it, which is the only
    //   reason it was harmless. ]
    bool bCardsSealed = false;
    int32 Winner = -1;               // 0/1, or -1 draw
    FString Method;

    void Reset(int32 InBudget);
    void WitnessLanding(int32 Scorer);
    bool TryKnockdown(int32 Defender, int64 PressureQ, int64 ThresholdQ,
                      TArray<FString>* OutRows);
    void TickCount(TArray<FString>* OutRows);
    void SealDecision(TArray<FString>* OutRows);
    bool IsFinished() const { return Phase == EUppercutRoundPhase::Finished; }
};

UPPERCUTCORE_API bool UppercutLoadRoundCanon(const FString& RepoDir,
                                             const FString& RulesetId,
                                             FUppercutRoundCanon& Out,
                                             FString& OutError);
// [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 02:53 UTC | END ]
