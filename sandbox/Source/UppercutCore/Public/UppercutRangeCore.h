// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 14:10 UTC | START ]
#pragma once

#include "CoreMinimal.h"

// Phase Q's rules, extracted from the commandlet so a LIVE session can run them.
//
// WHY THIS EXISTS. The proven C++ lives inside commandlet `Main()` functions -
// monolithic, file-scoped, and reachable only by running the editor headless.
// A runtime subsystem cannot call any of it, so a live arena would have to
// re-implement the rules, and two implementations of one rule is the defect
// this repository spends most of its discipline avoiding.
//
// So the rules move here and the commandlet becomes a caller. The safety net is
// the parity proof itself: after the extraction the commandlet must still emit a
// byte-identical marker stream, which is a stronger statement about a refactor
// than any test suite - the fight is provably unchanged.
//
// DESIGN RULES FOR THIS FILE, so it stays usable from both sides:
//   - no UObject, no ticking, no logging, no file IO in the rules themselves;
//   - fixed-point integers only (q10000), never float;
//   - every division through FloorDiv, because Python's // floors and C++ /
//     truncates and this is the seam where a port silently diverges;
//   - canon arrives as data (FUppercutRangeCanon), loaded by whoever has a file
//     system - the commandlet from disk, the subsystem from a data asset.

// Python's // floors toward negative infinity; C++ / truncates toward zero.
UPPERCUTCORE_API int64 UppercutFloorDiv(int64 A, int64 B);

struct UPPERCUTCORE_API FUppercutRangeMove
{
    int32 Startup = 0;
    int32 Active = 0;
    int32 Frames = 0;
    int64 Ext = 0;
    bool bPunch = false;
};

// Everything Phase Q reads, in the shared integer contract. Populated by a
// loader; the rules below never touch a file.
struct UPPERCUTCORE_API FUppercutRangeCanon
{
    static const int64 Unbounded = -1;

    TArray<FString> BandKey;
    TArray<int64> BandLo;
    TArray<int64> BandHi;          // Unbounded for the last band

    int64 Hyst = 0;
    int64 Stride = 0;
    int64 Cap = 0;                 // max displacement in one tick
    int64 MinSep = 0;
    int64 Axis = 0;
    int64 Ropes = 0;
    int64 RopeRetreat = 0;
    int64 DirAdvance = 0;
    int64 DirRetreat = 0;
    int64 DirLateral = 0;
    int64 HalfDepth = 0;
    int64 Retracted = 0;

    TMap<FString, FString> MoveBand;
    TMap<FString, FUppercutRangeMove> Moves;

    // Which band a separation sits in, ignoring history.
    int32 BandAt(int64 Sep) const;

    // The band a fighter is IN, which is not always the band he is AT.
    // Hysteresis is canon's anti-flicker rule: leaving the current band costs
    // the boundary plus `Hyst` in the direction of travel.
    int32 ResolveBand(int32 Current, int64 Sep) const;

    // Rule 12. A move declares one band; anywhere else it hits empty air. A
    // move with no authored band is REFUSED rather than silently permitted.
    bool InBand(const FString& MoveId, int32 BandIndex) const;

    // One tick of movement: at most the displacement cap, no teleports.
    // Returns what was applied and writes what is still owed.
    int64 Drain(int64 Pending, int64& OutPending) const;

    // Bodies do not overlap (Rule 13).
    int64 ClampSeparation(int64 Sep) const;

    // A retreat with your back on the ropes buys nothing - canon's
    // `rope_retreat_multiplier` of 0.0, which is the whole anti-running rule.
    int64 RopeScaled(int64 Pos, int64 Delta, int64 Opponent) const;

    // How far the fist has travelled at tick K of its own animation.
    int64 TipExtension(const FUppercutRangeMove& Move, int32 K) const;

    // The four properties this phase must have, proven rather than asserted.
    bool FootworkIsNotInert() const;
    bool UppercutIsReachable() const;
    bool HysteresisKillsFlicker() const;
    bool RunningIsFinite() const;

    // Canon this phase cannot execute. Counted, because only the count reaches
    // the marker stream.
    int32 CanonErrors() const;
};
// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 14:10 UTC | END ]
