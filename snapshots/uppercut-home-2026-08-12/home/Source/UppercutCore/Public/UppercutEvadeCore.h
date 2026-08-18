// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 15:00 UTC | START ]
#pragma once

#include "CoreMinimal.h"
#include "UppercutCanonSource.h"

// Phase R's rules, extracted from the commandlet for the same reason Phase Q's
// were: a live session cannot call code that lives inside a commandlet's
// `Main()`, and re-implementing a rule for the runtime would give this project
// two copies of it. The parity proof is the safety net - after the extraction
// the commandlet must still emit a byte-identical stream.
//
// Same design rules as UppercutRangeCore: no UObject, no ticking, no file IO,
// canon arrives as data.

struct UPPERCUTCORE_API FUppercutEvasion
{
    FString Id;
    FString Kind;                 // "active_window" or "positional"
    int32 Startup = 0;
    int32 Active = 0;
    int32 Recovery = 0;
    TArray<FString> Vacates;      // sorted
    TArray<FString> BeatenBy;     // sorted
};

struct UPPERCUTCORE_API FUppercutEvadePunch
{
    FString Id;
    FString Category;
    FString Region;
    int32 Startup = 0;
    int32 Active = 0;
    int32 Frames = 0;
};

struct UPPERCUTCORE_API FUppercutEvadeCanon
{
    TMap<FString, FUppercutEvasion> Evasions;
    TMap<FString, FUppercutEvadePunch> Punches;
    TMap<FString, FString> Category;   // every move in the table
    TMap<FString, FString> Region;     // every move in the table
    TSet<FString> HasRangeBand;        // move ids that declare one

    bool bOutranksGuard = false;
    int32 MistimeTicks = 0;

    // Is this punch the authored punishment for this evasion? `beaten_by` names
    // categories and tactics; only categories can be matched to a move, and a
    // tactic this core cannot express simply never matches - which is the honest
    // behaviour. It must not silently match everything, or nothing would ever be
    // evaded; and it must not silently match nothing, or the tactic would look
    // implemented.
    bool Beats(const FString& EvasionId, const FString& MoveId) const;

    // The whole rule. True means the punch finds empty air; false means it
    // continues to the guard stage exactly as before - evasion outranks the
    // guard but does not replace it.
    bool Evades(const FString& EvasionId, const FString& MoveId,
                const FString& InRegion) const;

    // The four properties, proven rather than asserted.
    bool BodyShotBeatsTheSlip() const;
    bool UppercutBeatsTheRoll() const;
    bool SlipEvadesAStraight() const;
    bool NoEvasionIsStrictlyBetter() const;

    // Canon this phase cannot execute. Counted, because only the count reaches
    // the marker stream.
    int32 CanonErrors() const;
};
// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 15:00 UTC | END ]

// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 19:55 UTC | the loop | START ]

// Six punches, two evasions, one wait: the index into this order IS the LCG
// word modulo nine, so the order is part of the artifact.
UPPERCUTCORE_API const TCHAR* UppercutEvadePunchId(int32 Index);    // 0..5
UPPERCUTCORE_API const TCHAR* UppercutEvadeEvasionId(int32 Index);  // 0..1

// Parse Phase R's canon out of its three JSON files. One reader, shared by the
// commandlet and the live subsystem, for the reason given in
// UppercutRangeCore.h - two readers are two chances to disagree about canon.
// Reuses FUppercutCanonSource so a caller handles both phases' headers the same
// way.
UPPERCUTCORE_API bool UppercutLoadEvadeCanon(const FString& RepoDir,
                                             FUppercutEvadeCanon& Out,
                                             TArray<FUppercutCanonSource>& OutSources,
                                             FString& OutError);

// One fighter's live evasion state.
struct UPPERCUTCORE_API FUppercutEvadeFighter
{
    int32 Busy = 0;
    bool bInFlight = false;
    FString PunchMove;
    int32 PunchT0 = 0;
    bool bEvading = false;
    FString EvName;
    int32 EvFrom = 0;
    int32 EvUntil = 0;
};

// THE LOOP, so a live subsystem advances the same object the marker stream is
// proven against. Fighter 0 is resolved completely before fighter 1 within a
// tick; that asymmetry is in the proven stream, so it is preserved rather than
// tidied.
struct UPPERCUTCORE_API FUppercutEvadeSession
{
    const FUppercutEvadeCanon* Canon = nullptr;
    FUppercutEvadeFighter Fighter[2];
    uint32 X = 0;
    int32 Tick = 0;

    int64 Commits = 0, Punches = 0, Evasions = 0, Waits = 0;
    int64 Arrived = 0, Dodged = 0, Countered = 0, WrongRegion = 0, Clear = 0;

    void Reset(const FUppercutEvadeCanon& InCanon, uint32 Seed);
    void Step(TArray<FString>* OutRows);
};
// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 19:55 UTC | the loop | END ]
