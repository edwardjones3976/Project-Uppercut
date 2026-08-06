// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 14:10 UTC | START ]
#pragma once

#include "CoreMinimal.h"
#include "UppercutCanonSource.h"

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

// The nine actions, drawn flat, in the contract's order. The index into this
// array IS the LCG word modulo nine, so the order is part of the artifact.
UPPERCUTCORE_API const TCHAR* UppercutRangeActionName(int32 Index);

// Parse canon out of the repository's four JSON files. ONE parser, called by
// the commandlet and by the live subsystem. Two parsers would be two chances to
// read canon differently, which is the defect this whole extraction exists to
// avoid.
//
// The hash comes back from the same read that produced the canon, so a stream
// header cannot name bytes other than the ones the fight ran on - hashing the
// files a second time would be a second chance to disagree.
//
// `RepoDir` is the project-uppercut root - the directory containing `data/`.
UPPERCUTCORE_API bool UppercutLoadRangeCanon(const FString& RepoDir,
                                             FUppercutRangeCanon& Out,
                                             TArray<FUppercutCanonSource>& OutSources,
                                             FString& OutError);

// One fighter's live state, exposed so presentation can read it without being
// able to change it.
struct UPPERCUTCORE_API FUppercutRangeFighter
{
    int64 Pos = 0;
    int64 Pending = 0;
    int32 Busy = 0;
    int32 Band = 0;
    bool bInFlight = false;
    FString PunchMove;
    int32 PunchT0 = 0;
    int32 PunchBand = 0;
    bool bPunchLegal = false;
    FString LastAction;

    // The tick the last commitment was drawn on. Never emitted - it exists so
    // presentation can tell two identical actions apart, which comparing the
    // action string alone cannot do.
    int32 LastActionTick = 0;
};

// THE LOOP ITSELF, not only the rules.
//
// The commandlet drives this to write a marker stream; a live subsystem drives
// the same object to advance a fight on a timer. That is the point: "press
// Play" runs the code the parity proof is taken against, rather than a second
// implementation that merely agrees for now.
//
// `Step()` advances exactly one tick and appends every row that tick produced.
// A caller that does not want rows passes nullptr and pays nothing.
struct UPPERCUTCORE_API FUppercutRangeSession
{
    const FUppercutRangeCanon* Canon = nullptr;
    FUppercutRangeFighter Fighter[2];
    uint32 X = 0;
    int32 Tick = 0;

    // Running totals, which are the trailer and also what a HUD wants.
    int64 Decisions = 0, Idles = 0, Steps = 0, Laterals = 0, Punches = 0;
    int64 Landed = 0, WhiffBand = 0, WhiffReach = 0, Transitions = 0;
    int64 Roped = 0, Clamped = 0, Applied = 0;
    int64 SepMin = 0, SepMax = 0;

    void Reset(const FUppercutRangeCanon& InCanon, uint32 Seed);
    void Step(TArray<FString>* OutRows);

    int64 Separation() const { return Fighter[1].Pos - Fighter[0].Pos; }
};

// ---- the artifact's SHAPE, so a live session can write one too -------------
//
// The header, the property rows and the trailer used to be inline in the
// commandlet, which meant a stream written from anywhere else would be a
// lookalike rather than the same thing. They live here now, so a fight watched
// in the editor can be dumped and handed to `prove_core_range` unchanged. That
// is the difference between "the arena runs the proven code" and "the arena can
// be proven".

// H / B / K / M rows: canon before any tick. Not hashed - it is the statement of
// what the hash below was taken over.
UPPERCUTCORE_API FString UppercutRangeStreamHeader(
    const FUppercutRangeCanon& Canon,
    const TArray<FUppercutCanonSource>& Sources,
    uint32 Seed, int32 Ticks);

// The five V rows. Hashed, because a property that is not inside the hash is a
// claim rather than evidence.
UPPERCUTCORE_API TArray<FString> UppercutRangePropertyRows(
    const FUppercutRangeCanon& Canon);

// The S row: totals and the FNV-1a of every row emitted.
UPPERCUTCORE_API FString UppercutRangeStreamTrailer(
    const FUppercutRangeSession& Session, int64 Rows, uint64 Fnv);

// FNV-1a 64 over a row's UTF-8 bytes, folded into a running value. The one
// place the marker hash is defined.
UPPERCUTCORE_API uint64 UppercutFnv1a64(uint64 Running, const FString& Row);
UPPERCUTCORE_API uint64 UppercutFnv1a64Offset();
// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 14:10 UTC | END ]
