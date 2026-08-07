// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 20:15 UTC | START ]
//
// The marker stream's SHAPE. Lifted out of the commandlet so that a stream is
// the same artifact wherever it was written from - headless, or a fight someone
// watched in the editor and dumped afterwards. A lookalike written by a second
// piece of code would prove nothing about the first.

#include "UppercutRangeCore.h"
#include "UppercutCanonHash.h"

namespace
{
    const uint64 FnvOffset = 14695981039346656037ull;
    const uint64 FnvPrime = 1099511628211ull;
}

uint64 UppercutFnv1a64Offset() { return FnvOffset; }

uint64 UppercutFnv1a64(uint64 Running, const FString& Row)
{
    const FTCHARToUTF8 Utf8(*Row);
    const uint8* P = (const uint8*)Utf8.Get();
    for (int32 b = 0; b < Utf8.Length(); ++b)
    {
        Running = (Running ^ P[b]) * FnvPrime;
    }
    return Running;
}

FString UppercutRangeStreamHeader(const FUppercutRangeCanon& C,
                                  const TArray<FUppercutCanonSource>& Sources,
                                  uint32 Seed, int32 Ticks,
                                  const FString& RepoDir)
{
    FString Out;
    Out += TEXT("H|phase=Q\n");

    // Decision 0023: dual identities, built by the SHARED builder so the
    // commandlet and the Python contract cannot drift into two opinions about
    // what a header says. Migrated 2026-08-07 with no authoritative row moved.
    TArray<TPair<FString, FString>> Entries;
    for (const FUppercutCanonSource& Src : Sources)
    {
        Entries.Add(TPair<FString, FString>(Src.Label, Src.RelPath));
    }
    TArray<FString> HeaderLines;
    FString Error;
    if (!UppercutCanonHeaderLines(RepoDir, Entries, HeaderLines, Error))
    {
        // Refusing loudly. A stream with no canon identity is worse than no
        // stream: it looks like evidence and is not.
        return FString::Printf(TEXT("H|phase=Q\nH|ERROR=%s\n"), *Error);
    }
    for (const FString& L : HeaderLines) { Out += L + TEXT("\n"); }

    Out += FString::Printf(TEXT("H|seed=%u\nH|ticks=%d\n"), Seed, Ticks);
    for (int32 i = 0; i < C.BandKey.Num(); ++i)
    {
        Out += FString::Printf(TEXT("B|%d|%s|%lld|%lld\n"), i, *C.BandKey[i],
                               C.BandLo[i], C.BandHi[i]);
    }
    Out += FString::Printf(
        TEXT("K|hyst=%lld|stride=%lld|cap=%lld|min_sep=%lld|axis=%lld|ropes=%lld")
        TEXT("|rope_retreat=%lld|advance=%lld|retreat=%lld|lateral=%lld")
        TEXT("|half_depth=%lld|retracted=%lld\n"),
        C.Hyst, C.Stride, C.Cap, C.MinSep, C.Axis, C.Ropes, C.RopeRetreat,
        C.DirAdvance, C.DirRetreat, C.DirLateral, C.HalfDepth, C.Retracted);

    // Sorted, because a TMap's iteration order is not part of canon and must
    // never become part of the artifact.
    TArray<FString> BandedMoves;
    C.MoveBand.GetKeys(BandedMoves);
    BandedMoves.Sort();
    for (const FString& Id : BandedMoves)
    {
        Out += FString::Printf(TEXT("M|%s|%s\n"), *Id, *C.MoveBand[Id]);
    }
    return Out;
}

TArray<FString> UppercutRangePropertyRows(const FUppercutRangeCanon& C)
{
    TArray<FString> Rows;
    Rows.Add(FString::Printf(TEXT("V|footwork_is_not_inert|%d\n"),
                             C.FootworkIsNotInert() ? 1 : 0));
    Rows.Add(FString::Printf(TEXT("V|uppercut_is_reachable|%d\n"),
                             C.UppercutIsReachable() ? 1 : 0));
    Rows.Add(FString::Printf(TEXT("V|hysteresis_kills_flicker|%d\n"),
                             C.HysteresisKillsFlicker() ? 1 : 0));
    Rows.Add(FString::Printf(TEXT("V|running_is_finite|%d\n"),
                             C.RunningIsFinite() ? 1 : 0));
    Rows.Add(FString::Printf(TEXT("V|canon_errors|%d\n"), C.CanonErrors()));
    return Rows;
}

FString UppercutRangeStreamTrailer(const FUppercutRangeSession& S,
                                   int64 Rows, uint64 Fnv)
{
    return FString::Printf(
        TEXT("S|rows=%lld|decisions=%lld|idles=%lld|steps=%lld|laterals=%lld")
        TEXT("|punches=%lld|landed=%lld|whiff_band=%lld|whiff_reach=%lld")
        TEXT("|transitions=%lld|roped=%lld|clamped=%lld|applied=%lld")
        TEXT("|sep_min=%lld|sep_max=%lld|fnv1a64=%016llx\n"),
        Rows, S.Decisions, S.Idles, S.Steps, S.Laterals, S.Punches, S.Landed,
        S.WhiffBand, S.WhiffReach, S.Transitions, S.Roped, S.Clamped, S.Applied,
        S.SepMin, S.SepMax, Fnv);
}
// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 20:15 UTC | END ]
