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

// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 15:40 UTC | the loop | START ]
namespace
{
    const uint32 LcgA = 1664525u;
    const uint32 LcgC = 1013904223u;

    const TCHAR* GActionName[9] = { TEXT("idle"), TEXT("step_in"), TEXT("step_out"),
                                    TEXT("step_lateral"), TEXT("jab_lead"),
                                    TEXT("cross_rear"), TEXT("hook_lead"),
                                    TEXT("uppercut_rear"),
                                    TEXT("body_straight_rear") };
}

const TCHAR* UppercutRangeActionName(int32 Index)
{
    return GActionName[FMath::Clamp(Index, 0, 8)];
}

void FUppercutRangeSession::Reset(const FUppercutRangeCanon& InCanon, uint32 Seed)
{
    Canon = &InCanon;
    Fighter[0] = FUppercutRangeFighter();
    Fighter[1] = FUppercutRangeFighter();
    Fighter[0].Pos = InCanon.Axis / 2 - 4500;
    Fighter[1].Pos = InCanon.Axis / 2 + 4500;
    const int64 Sep = Fighter[1].Pos - Fighter[0].Pos;
    Fighter[0].Band = Fighter[1].Band = InCanon.BandAt(Sep);
    X = Seed;
    Tick = 0;
    Decisions = Idles = Steps = Laterals = Punches = 0;
    Landed = WhiffBand = WhiffReach = Transitions = 0;
    Roped = Clamped = Applied = 0;
    SepMin = SepMax = Sep;
}

void FUppercutRangeSession::Step(TArray<FString>* OutRows)
{
    const FUppercutRangeCanon& C = *Canon;
    ++Tick;
    const int32 T = Tick;

    auto Row = [&](const FString& S) { if (OutRows) { OutRows->Add(S); } };

    for (int32 i = 0; i < 2; ++i)
    {
        FUppercutRangeFighter& F = Fighter[i];

        // ---- 1. deliver movement already owed, at most the cap ------------
        if (F.Pending != 0)
        {
            int64 NextPending = 0;
            const int64 StepDelta = C.Drain(F.Pending, NextPending);
            F.Pending = NextPending;
            const int64 Before = F.Pos;
            F.Pos = FMath::Max((int64)0, FMath::Min(C.Axis, F.Pos + StepDelta));
            FString Flags;
            if (Fighter[1].Pos - Fighter[0].Pos < C.MinSep)
            {
                if (i == 0) { Fighter[0].Pos = Fighter[1].Pos - C.MinSep; }
                else { Fighter[1].Pos = Fighter[0].Pos + C.MinSep; }
                Fighter[0].Pos = FMath::Max((int64)0, Fighter[0].Pos);
                Fighter[1].Pos = FMath::Min(C.Axis, Fighter[1].Pos);
                // The rest of the stride is refused, not banked.
                F.Pending = 0;
                Flags += TEXT("m");
                ++Clamped;
            }
            const int64 Moved = F.Pos - Before;
            if (Moved != 0) { ++Applied; }
            const int64 Sep = Separation();
            SepMin = FMath::Min(SepMin, Sep);
            SepMax = FMath::Max(SepMax, Sep);
            Row(FString::Printf(TEXT("X|%d|%d|%lld|%lld|%lld|%lld|%lld|%s\n"),
                                T, i, Moved, Fighter[0].Pos, Fighter[1].Pos, Sep,
                                F.Pending, Flags.IsEmpty() ? TEXT("-") : *Flags));
            for (int32 j = 0; j < 2; ++j)
            {
                const int32 Nb = C.ResolveBand(Fighter[j].Band, Sep);
                if (Nb != Fighter[j].Band)
                {
                    Row(FString::Printf(TEXT("R|%d|%d|%s|%s|%lld\n"), T, j,
                                        *C.BandKey[Fighter[j].Band],
                                        *C.BandKey[Nb], Sep));
                    Fighter[j].Band = Nb;
                    ++Transitions;
                }
            }
        }

        // ---- 2. a punch in flight -----------------------------------------
        if (F.bInFlight)
        {
            const FUppercutRangeMove& M = C.Moves[F.PunchMove];
            const int32 Kk = T - F.PunchT0;
            const int32 Span = M.Startup + M.Active;
            if (Kk > M.Startup && Kk <= Span)
            {
                const int64 TipExt = C.TipExtension(M, Kk);
                int64 Tip = 0, Surface = 0;
                bool bArrived = false;
                if (i == 0)
                {
                    Tip = Fighter[0].Pos + TipExt;
                    Surface = Fighter[1].Pos - C.HalfDepth;
                    bArrived = Tip >= Surface;
                }
                else
                {
                    Tip = Fighter[1].Pos - TipExt;
                    Surface = Fighter[0].Pos + C.HalfDepth;
                    bArrived = Tip <= Surface;
                }
                const TCHAR* Result = nullptr;
                const TCHAR* Reason = TEXT("-");
                if (bArrived && F.bPunchLegal)
                {
                    Result = TEXT("landed");
                    ++Landed;
                }
                else if (Kk == Span)
                {
                    Result = TEXT("whiffed");
                    // The band is tested first on purpose: a punch from the
                    // wrong band is refused even when the fist arrived.
                    Reason = F.bPunchLegal ? TEXT("reach") : TEXT("band");
                    if (F.bPunchLegal) { ++WhiffReach; } else { ++WhiffBand; }
                }
                if (Result != nullptr)
                {
                    Row(FString::Printf(
                        TEXT("P|%d|%d|%s|%s|%s|%d|%lld|%lld|%s|%d\n"), T, i,
                        *F.PunchMove, Result, Reason, Kk, Tip, Surface,
                        *C.BandKey[F.PunchBand], F.bPunchLegal ? 1 : 0));
                    F.bInFlight = false;
                }
            }
            else if (Kk > Span)
            {
                F.bInFlight = false;
            }
        }

        // ---- 3. commitment -------------------------------------------------
        // A step keeps draining while its owner is committed: that is what makes
        // "entering is when counters land" true rather than stated.
        if (F.Busy > 0)
        {
            --F.Busy;
            continue;
        }

        // ---- 4. one decision -----------------------------------------------
        X = LcgA * X + LcgC;              // uint32 wraps, which IS mod 2^32
        const int32 Choice = (int32)(X % 9u);
        const FString Action = GActionName[Choice];
        F.LastAction = Action;
        // Presentation-only, and never emitted: two identical actions in a row
        // are two commitments, and an animation layer comparing strings alone
        // would silently drop the second one.
        F.LastActionTick = T;
        ++Decisions;
        FString Mark = TEXT("-");
        if (Choice == 0)
        {
            ++Idles;
        }
        else if (Choice >= 4)
        {
            F.Busy = C.Moves[Action].Frames;
            const bool bLegal = C.InBand(Action, F.Band);
            F.bInFlight = true;
            F.PunchMove = Action;
            F.PunchT0 = T;
            F.PunchBand = F.Band;
            F.bPunchLegal = bLegal;
            ++Punches;
            Mark = bLegal ? TEXT("1") : TEXT("0");
        }
        else
        {
            F.Busy = C.Moves[Action].Frames;
            ++Steps;
            if (Choice == 3)
            {
                // Knowingly inert on one axis, and marked in the row so a reader
                // never has to infer it from a zero.
                ++Laterals;
                Mark = TEXT("l");
            }
            else
            {
                const int64 Toward = (i == 0) ? 1 : -1;
                const int64 Sign = (Choice == 1) ? Toward : -Toward;
                const int64 Mul = (Choice == 1) ? C.DirAdvance : C.DirRetreat;
                const int64 Delta = Sign * UppercutFloorDiv(C.Stride * Mul, 10000);
                const int64 Scaled = C.RopeScaled(F.Pos, Delta, Fighter[1 - i].Pos);
                if (Scaled != Delta) { ++Roped; Mark = TEXT("r"); }
                F.Pending = Scaled;
            }
        }
        Row(FString::Printf(TEXT("D|%d|%d|%s|%u|%lld|%lld|%lld|%s|%lld|%s\n"),
                            T, i, *Action, X, Fighter[0].Pos, Fighter[1].Pos,
                            Separation(), *C.BandKey[F.Band], F.Pending, *Mark));
    }
}
// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 15:40 UTC | the loop | END ]

// [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 03:13 UTC | START ]
uint32 UppercutLcgNext(uint32& X)
{
    X = LcgA * X + LcgC;
    return X;
}

uint32 UppercutMixSeed(uint32 Seed, const FString& Name)
{
    uint32 X = Seed;
    for (TCHAR C : Name)
    {
        X = LcgA * X + LcgC + (uint32)C;
    }
    return X ? X : 1u;
}
// [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 03:13 UTC | END ]
