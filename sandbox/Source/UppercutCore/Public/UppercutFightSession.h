// [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 02:53 UTC | START ]
#pragma once

#include "CoreMinimal.h"
#include "UppercutAttrCore.h"
#include "UppercutCanonSource.h"
#include "UppercutEvadeCore.h"
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
    int64 Wind = 0;
    int64 Reserve = 0;
    int64 WindMax = 100000000;     // filled from stamina canon
    uint32 PolicyStream = 0;
    int32 DecisionBusy = 0;

    // [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-15 17:15 UTC | START ]
    // The last punch that resolved AGAINST this fighter: the tick it landed and
    // the attacker's move. View-facing telemetry ONLY - the stream already
    // recorded it as a P row, no decision reads it, and no row is emitted from
    // it. It exists because being hit is not an action a fighter commits, so a
    // presentation layer reading only LastAction can never see it - which left
    // the four reaction clips loaded and unreachable. -1 = never hit.
    int32 LastImpactTick = -1;
    FString LastImpactMove;
    // [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-15 17:15 UTC | END ]
};

struct UPPERCUTCORE_API FUppercutFightSession
{
    FUppercutRangeCanon RangeCanon;
    FUppercutEvadeCanon EvadeCanon;
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
