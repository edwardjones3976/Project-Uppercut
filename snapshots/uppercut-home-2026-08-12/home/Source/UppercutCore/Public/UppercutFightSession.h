// [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 02:53 UTC | START ]
#pragma once

#include "CoreMinimal.h"
#include "UppercutAttrCore.h"
#include "UppercutCanonSource.h"
#include "UppercutConditionCore.h"
#include "UppercutEvadeCore.h"
#include "UppercutGuardCore.h"
#include "UppercutPunchEconomyCore.h"
#include "UppercutRangeCore.h"
#include "UppercutRoundCore.h"
#include "UppercutStaminaCore.h"
#include "UppercutThinPolicy.h"

// THE INTEGRATED 1-ROUND SESSION (Decision 0022).
//
// Commandlets and Play must call the same Step(). This composes existing
// Range / Evade / Stamina cores, applies attribute cards, drives a thin
// observable policy (not the Phase Q nine-way LCG), and ends the round with a
// knockdown/count or a sealed decision.
//
// N/Q/R unit pins stay historical evidence. This contract is separate.

struct UPPERCUTCORE_API FUppercutFightFighter
{
    FUppercutRangeFighter Range;
    FUppercutFighterCard Card;
    FUppercutThinPolicy Policy;
    FString ParticipantId;
    FString Posture = TEXT("high_guard");
    int64 Wind = 0;
    int64 Reserve = 0;
    int64 WindMax = 100000000;     // filled from stamina canon
    uint32 PolicyStream = 0;
    int32 DecisionBusy = 0;
    int32 RecoveryTicks = 0;

    // Decision 0032: committed evasion window (id, open, close, used).
    bool bEvasion = false;
    FString EvasionId;
    int32 EvasionOpenAt = 0;
    int32 EvasionCloseAt = 0;
    bool bEvasionUsed = false;

    int64 ArmWorkLeadQ = 0;
    int64 ArmWorkRearQ = 0;
    bool bSteppedSinceThrow = true;

    FUppercutRegionalCondition Condition;
};

struct UPPERCUTCORE_API FUppercutFightSession
{
    FUppercutRangeCanon RangeCanon;
    FUppercutEvadeCanon EvadeCanon;
    FUppercutGuardCanon GuardCanon;
    FUppercutPunchEconomyCanon PunchEconomyCanon;
    FUppercutConditionCanon ConditionCanon;
    FUppercutStaminaCanon StaminaCanon;
    FUppercutAttrCanon AttrCanon;
    FUppercutRoundCanon RoundCanon;
    TArray<FUppercutCanonSource> Sources;

    FUppercutFightFighter Fighter[2];
    FUppercutRoundState Round;
    FUppercutRangeSession RangeBridge;   // reused geometry helpers only
    int32 Tick = 0;
    int32 DecisionInterval = 4;
    bool bReady = false;

    // Running totals for HUD / trailer.
    int64 Decisions = 0;
    int64 Punches = 0;
    int64 Landed = 0;
    int64 Blocked = 0;

    bool Load(const FString& RepoDir,
              const FString& CardA,
              const FString& CardB,
              const FString& RulesetId,
              FString& OutError);

    void Reset(uint32 Seed, int32 TickBudget);
    void Step(TArray<FString>* OutRows);

    int64 Separation() const;
    bool IsFinished() const { return Round.IsFinished(); }

private:
    void TickEvasions(TArray<FString>* OutRows);
    bool CommitEvasion(int32 Who, const FString& EvasionId);
    bool EvasionActive(int32 Who) const;
    void DecideAndCommit(int32 Who, TArray<FString>* OutRows);
    void AdvanceRangeFromTactic(int32 Who, const FUppercutThinDecision& D,
                                TArray<FString>* OutRows);
    void ResolveContacts(TArray<FString>* OutRows);
};

UPPERCUTCORE_API FString UppercutFightStreamHeader(
    const FUppercutFightSession& Session, uint32 Seed, int32 Ticks,
    const FString& RepoDir);

UPPERCUTCORE_API FString UppercutFightStreamTrailer(
    const FUppercutFightSession& Session, int64 Rows, uint64 Fnv);
// [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 02:53 UTC | END ]
