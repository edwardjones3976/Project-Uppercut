// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 14:15 UTC | START ]
#include "UppercutRangeCore.h"

int64 UppercutFloorDiv(int64 A, int64 B)
{
    int64 R = A / B;
    if ((A % B != 0) && ((A < 0) != (B < 0))) { --R; }
    return R;
}

int32 FUppercutRangeCanon::BandAt(int64 Sep) const
{
    for (int32 i = 0; i < BandKey.Num(); ++i)
    {
        if (Sep >= BandLo[i] && (BandHi[i] == Unbounded || Sep < BandHi[i]))
        {
            return i;
        }
    }
    return BandKey.Num() - 1;
}

int32 FUppercutRangeCanon::ResolveBand(int32 Current, int64 Sep) const
{
    if (Current < 0 || Current >= BandKey.Num()) { return BandAt(Sep); }
    if (Sep < BandLo[Current] - Hyst) { return BandAt(Sep); }
    if (BandHi[Current] != Unbounded && Sep >= BandHi[Current] + Hyst)
    {
        return BandAt(Sep);
    }
    return Current;
}

bool FUppercutRangeCanon::InBand(const FString& MoveId, int32 BandIndex) const
{
    const FString* B = MoveBand.Find(MoveId);
    return B != nullptr && *B == BandKey[BandIndex];
}

int64 FUppercutRangeCanon::Drain(int64 Pending, int64& OutPending) const
{
    if (Pending == 0) { OutPending = 0; return 0; }
    const int64 Step = FMath::Max(-Cap, FMath::Min(Cap, Pending));
    OutPending = Pending - Step;
    return Step;
}

int64 FUppercutRangeCanon::ClampSeparation(int64 Sep) const
{
    return FMath::Max(MinSep, Sep);
}

int64 FUppercutRangeCanon::RopeScaled(int64 Pos, int64 Delta, int64 Opponent) const
{
    if (Delta == 0) { return 0; }
    const bool bRetreating = (Pos < Opponent) ? (Delta < 0) : (Delta > 0);
    if (!bRetreating) { return Delta; }
    const int64 Edge = (Delta < 0) ? Pos : Axis - Pos;
    if (Edge <= Ropes) { return UppercutFloorDiv(Delta * RopeRetreat, 10000); }
    return Delta;
}

int64 FUppercutRangeCanon::TipExtension(const FUppercutRangeMove& Move, int32 K) const
{
    const int32 Span = Move.Startup + Move.Active;
    return Retracted + UppercutFloorDiv((Move.Ext - Retracted) * K, Span);
}

bool FUppercutRangeCanon::FootworkIsNotInert() const
{
    const int64 Start = 9000;                 // 0.90 ru, the frozen separation
    const int32 Band0 = BandAt(Start);
    int64 Sep = Start;
    int32 Cur = Band0;
    for (int32 i = 0; i < 20; ++i)
    {
        Sep = ClampSeparation(Sep - Stride);   // step_in
        Cur = ResolveBand(Cur, Sep);
        if (Cur != Band0) { return true; }
    }
    return false;
}

bool FUppercutRangeCanon::UppercutIsReachable() const
{
    const int64 MidSep = 9000;
    if (InBand(TEXT("uppercut_rear"), BandAt(MidSep))) { return false; }
    const FUppercutRangeMove* M = Moves.Find(TEXT("uppercut_rear"));
    if (!M) { return false; }
    int64 Sep = MidSep;
    int32 Cur = BandAt(MidSep);
    for (int32 i = 0; i < 20; ++i)
    {
        Sep = ClampSeparation(Sep - Stride);
        Cur = ResolveBand(Cur, Sep);
        if (InBand(TEXT("uppercut_rear"), Cur) && M->Ext >= Sep - HalfDepth)
        {
            return true;
        }
    }
    return false;
}

bool FUppercutRangeCanon::HysteresisKillsFlicker() const
{
    for (int32 i = 0; i < BandKey.Num(); ++i)
    {
        if (BandHi[i] == Unbounded) { continue; }
        const int32 Here = BandAt(BandHi[i] - 1);
        if (ResolveBand(Here, BandHi[i] + Hyst / 2) != Here) { return false; }
    }
    return true;
}

bool FUppercutRangeCanon::RunningIsFinite() const
{
    int64 Pos = Axis / 2 - 4500;
    const int64 Opp = Axis / 2 + 4500;
    int64 Last = MIN_int64;
    for (int32 i = 0; i < 200; ++i)
    {
        const int64 D = RopeScaled(Pos, -Cap, Opp);
        Pos = FMath::Max((int64)0, FMath::Min(Axis, Pos + D));
        if (D == 0) { return true; }
        if (Pos == Last) { return true; }
        Last = Pos;
    }
    return false;
}

int32 FUppercutRangeCanon::CanonErrors() const
{
    int32 Errors = 0;
    for (int32 i = 0; i + 1 < BandKey.Num(); ++i)
    {
        if (BandHi[i] != BandLo[i + 1]) { ++Errors; }
    }
    if (BandKey.Num() > 0 && BandLo[0] != 0) { ++Errors; }
    if (BandKey.Num() > 0 && BandHi.Last() != Unbounded) { ++Errors; }
    int64 Narrowest = MAX_int64;
    for (int32 i = 0; i < BandKey.Num(); ++i)
    {
        if (BandHi[i] != Unbounded)
        {
            Narrowest = FMath::Min(Narrowest, BandHi[i] - BandLo[i]);
        }
    }
    if (Hyst >= Narrowest) { ++Errors; }
    if (Stride <= 0 || Cap <= 0) { ++Errors; }
    if (BandKey.Num() > 0 && MinSep >= BandHi[0]) { ++Errors; }
    for (const TPair<FString, FUppercutRangeMove>& It : Moves)
    {
        if (!It.Value.bPunch) { continue; }
        if (It.Value.Ext <= HalfDepth) { ++Errors; }
        if (It.Value.Active <= 0) { ++Errors; }
        if (!MoveBand.Contains(It.Key)) { ++Errors; }
    }
    return Errors;
}
// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 14:15 UTC | END ]
