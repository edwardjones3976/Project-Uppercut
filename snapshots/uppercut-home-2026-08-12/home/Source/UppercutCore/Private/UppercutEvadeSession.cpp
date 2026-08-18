// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 19:55 UTC | START ]
//
// Phase R's LOOP, lifted out of the commandlet unchanged.
//
// "Unchanged" is meant literally: the row order, the per-fighter asymmetry, and
// the fact that fighter 0 resolves completely before fighter 1 within one tick
// are all in the proven stream, so they are preserved rather than tidied. The
// parity proof is what says the lift was faithful.

#include "UppercutEvadeCore.h"

namespace
{
    const uint32 LcgA = 1664525u;
    const uint32 LcgC = 1013904223u;

    const TCHAR* PunchIdTable[6] = { TEXT("jab_lead"), TEXT("cross_rear"),
                                     TEXT("hook_lead"), TEXT("uppercut_rear"),
                                     TEXT("body_straight_rear"),
                                     TEXT("body_hook_lead") };
    const TCHAR* EvasionIdTable[2] = { TEXT("slip_lead"), TEXT("roll_under") };
}

const TCHAR* UppercutEvadePunchId(int32 Index)
{
    return (Index >= 0 && Index < 6) ? PunchIdTable[Index] : TEXT("");
}

const TCHAR* UppercutEvadeEvasionId(int32 Index)
{
    return (Index >= 0 && Index < 2) ? EvasionIdTable[Index] : TEXT("");
}

void FUppercutEvadeSession::Reset(const FUppercutEvadeCanon& InCanon, uint32 Seed)
{
    Canon = &InCanon;
    X = Seed;
    Tick = 0;
    for (int32 i = 0; i < 2; ++i) { Fighter[i] = FUppercutEvadeFighter(); }
    Commits = Punches = Evasions = Waits = 0;
    Arrived = Dodged = Countered = WrongRegion = Clear = 0;
}

void FUppercutEvadeSession::Step(TArray<FString>* OutRows)
{
    if (Canon == nullptr) { return; }
    const FUppercutEvadeCanon& C = *Canon;
    const int32 T = ++Tick;

    auto Row = [&](const FString& Text)
    {
        if (OutRows) { OutRows->Add(Text); }
    };

    for (int32 i = 0; i < 2; ++i)
    {
        const int32 Opp = 1 - i;
        FUppercutEvadeFighter& F = Fighter[i];
        FUppercutEvadeFighter& O = Fighter[Opp];

        // ---- 1. a punch already in the air --------------------------------
        if (F.bInFlight)
        {
            const FUppercutEvadePunch& P = C.Punches[F.PunchMove];
            const int32 K = T - F.PunchT0;
            if (K == P.Startup + P.Active)
            {
                const FString Reg = P.Region.IsEmpty() ? TEXT("-") : P.Region;
                const bool bActive = O.bEvading && O.EvFrom < T && T <= O.EvUntil;
                const TCHAR* Result = TEXT("arrived");
                const TCHAR* Why = TEXT("clear");
                FString Name = TEXT("-");
                if (!bActive)
                {
                    ++Clear;
                }
                else
                {
                    Name = O.EvName;
                    if (!C.Evasions[Name].Vacates.Contains(Reg))
                    {
                        // The structure moved, but not out of this punch's lane.
                        Why = TEXT("region");
                        ++WrongRegion;
                    }
                    else if (C.Beats(Name, F.PunchMove))
                    {
                        // Canon's authored punishment: the evasion put the head
                        // exactly where this punch was going.
                        Why = TEXT("counter");
                        ++Countered;
                    }
                    else
                    {
                        Result = TEXT("dodged");
                        Why = TEXT("vacated");
                        ++Dodged;
                    }
                }
                if (FString(Result) == TEXT("arrived")) { ++Arrived; }
                Row(FString::Printf(TEXT("P|%d|%d|%s|%s|%s|%s|%s\n"), T, i,
                                    *F.PunchMove, Result, Why, *Reg, *Name));
                F.bInFlight = false;
            }
            else if (K > P.Startup + P.Active)
            {
                F.bInFlight = false;
            }
        }

        // ---- 2. an evasion window closing ---------------------------------
        if (F.bEvading && T == F.EvUntil)
        {
            Row(FString::Printf(TEXT("W|%d|%d|%s|close\n"), T, i, *F.EvName));
            F.bEvading = false;
        }

        // ---- 3. commitment -------------------------------------------------
        if (F.Busy > 0)
        {
            --F.Busy;
            continue;
        }

        // ---- 4. one commitment ---------------------------------------------
        X = LcgA * X + LcgC;
        const int32 Choice = (int32)(X % 9u);
        FString Action;
        if (Choice < 6) { Action = PunchIdTable[Choice]; }
        else if (Choice < 8) { Action = EvasionIdTable[Choice - 6]; }
        else { Action = TEXT("wait"); }
        ++Commits;
        if (Choice == 8)
        {
            ++Waits;
        }
        else if (Choice < 6)
        {
            F.Busy = C.Punches[Action].Frames;
            F.bInFlight = true;
            F.PunchMove = Action;
            F.PunchT0 = T;
            ++Punches;
        }
        else
        {
            const FUppercutEvasion& E = C.Evasions[Action];
            // A committed evasion that catches nothing leaves the defender in
            // recovery with no structure up. Authored, not invented.
            F.Busy = E.Startup + E.Active + E.Recovery + C.MistimeTicks;
            F.bEvading = true;
            F.EvName = Action;
            F.EvFrom = T + E.Startup;
            F.EvUntil = T + E.Startup + E.Active;
            Row(FString::Printf(TEXT("W|%d|%d|%s|open\n"), T, i, *Action));
            ++Evasions;
        }
        Row(FString::Printf(TEXT("A|%d|%d|%s|%u\n"), T, i, *Action, X));
    }
}
// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 19:55 UTC | END ]
