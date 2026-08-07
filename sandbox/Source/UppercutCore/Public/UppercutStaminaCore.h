// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 10:45 UTC | START ]
#pragma once

#include "CoreMinimal.h"

// Decision 0021's two-tier stamina economy, in the shared runtime.
//
//   Wind      the acute exchange resource. Movement, guard, evasion, punches.
//             Recovers during Observe, HoldPosition and especially Rest,
//             because a boxer can regain breath inside a round.
//   Reserve   whole-fight conditioning. Drains slowly, does NOT recover inside
//             a round, and reaches a knockdown only INDIRECTLY - through the
//             Wind ceiling and the Wind recovery rate. Decision 0021 refuses a
//             second direct multiplier until the indirect path is proven
//             insufficient, because that would count deep fatigue twice.
//
// A short pause may restore Wind. It may not restore Reserve or erase the
// history of the fight.
//
// EVERYTHING IS q10000 INTEGERS and every division goes through
// UppercutFloorDiv. Python's // floors and C++'s / truncates; an economy that
// diverges by one unit per tick is wrong by a whole round after twelve.
//
// The contract is tools/uppercut_stamina/economy.py and the parity fixtures are
// tests/fixtures/stamina_vectors.json. This file must reproduce them EXACTLY -
// an integer economy that agrees approximately has already failed.

// The eight action families from Decision 0014's G2 ruling. The family decides
// RECOVERY; a move id decides COST. They are separate on purpose: conflating
// them is what made every punch free in the contract's first draft.
enum class EUppercutAction : uint8
{
    Observe, HoldPosition, Rest, MicroAdjust, Move, Guard, Evade, Attack
};

UPPERCUTCORE_API const TCHAR* UppercutActionName(EUppercutAction Action);
UPPERCUTCORE_API bool UppercutActionFromName(const FString& Name,
                                             EUppercutAction& Out);

struct UPPERCUTCORE_API FUppercutMoveCost
{
    // The move id EXACTLY as canon spells it. Carried in the value because
    // FString hashing and comparison are case-INSENSITIVE in Unreal, so
    // TMap::Find(TEXT("Jab_Lead")) returns jab_lead's price. Keeping the
    // authored spelling here lets the lookup confirm the case it actually
    // matched instead of trusting the map. The canonicalizer was bitten by the
    // same operator on 2026-08-07; this is that lesson applied before it costs
    // anything.
    FString Id;
    int64 Effort = 0;
    int64 Wind = 0;
    int64 Reserve = 0;
    // Decision 0015: ordinary movement is priced by the ground it covers, not
    // by a flat fee. `Wind`/`Reserve` are meaningless when this is set.
    bool bDisplacement = false;
};

struct UPPERCUTCORE_API FUppercutStaminaCanon
{
    int64 WindMax = 0, WindStart = 0, WindLow = 0, WindExhausted = 0;
    int64 WindBetweenRounds = 0;
    int64 Recover[8] = { 0, 0, 0, 0, 0, 0, 0, 0 };   // indexed by EUppercutAction
    int64 CeilingFloor = 0, CeilingSpan = 0;
    int64 RecoveryFloor = 0, RecoverySpan = 0;

    int64 ReserveMax = 0, ReserveStart = 0, ReserveLow = 0;
    int64 ReserveInRound = 0, ReserveBetweenRounds = 0;
    int64 SustainedExertion = 0, BodyDamageMult = 0;

    int64 WindPerRu = 0, ReservePerRu = 0;

    TMap<FString, FUppercutMoveCost> Moves;

    // Reserve limits how much Wind a fighter can hold. Indirect path one.
    int64 WindCeiling(int64 Reserve) const;
    // A drained fighter gets his breath back slower. Indirect path two.
    int64 RecoveryRate(EUppercutAction Action, int64 Reserve) const;

    // Canon this model cannot execute, counted rather than assumed.
    int32 CanonErrors(TArray<FString>* OutErrors = nullptr) const;
};

// Parse the two-tier economy out of data/stamina_economy.json and
// data/moves/generic_sandbox_effort.json. ONE reader, as everywhere else.
UPPERCUTCORE_API bool UppercutLoadStaminaCanon(const FString& RepoDir,
                                               FUppercutStaminaCanon& Out,
                                               FString& OutError);

// One fighter's two resources.
struct UPPERCUTCORE_API FUppercutStamina
{
    int64 Wind = 0;
    int64 Reserve = 0;

    void Reset(const FUppercutStaminaCanon& C);

    // One tick. `MoveId` empty means this tick commits nothing.
    //
    // AN UNKNOWN MOVE FAILS CLOSED. It never means "free". The contract's first
    // draft returned zero cost for an unrecognised id and a fighter throwing
    // 120 punches a round finished with a full pool - nothing raised, and the
    // model simply reported that boxing is not tiring.
    bool Step(const FUppercutStaminaCanon& C, EUppercutAction Action,
              const FString& MoveId, int64 DisplacementRu, FString& OutError);

    // The corner. Wind comes back substantially; Reserve barely.
    void BetweenRounds(const FUppercutStaminaCanon& C);
};
// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 10:45 UTC | END ]
