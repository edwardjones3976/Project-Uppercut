// [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 02:53 UTC | START ]
#include "UppercutThinPolicy.h"
#include "UppercutRangeCore.h"

namespace
{
    int32 LcgMod(uint32& X, int32 Mod)
    {
        if (Mod <= 0) { return 0; }
        return (int32)(UppercutLcgNext(X) % (uint32)Mod);
    }
}

const TCHAR* UppercutThinTacticName(EUppercutThinTactic T)
{
    switch (T)
    {
    case EUppercutThinTactic::Observe:      return TEXT("Observe");
    case EUppercutThinTactic::HoldPosition: return TEXT("HoldPosition");
    case EUppercutThinTactic::Rest:         return TEXT("Rest");
    case EUppercutThinTactic::Advance:      return TEXT("Advance");
    case EUppercutThinTactic::Retreat:      return TEXT("Retreat");
    case EUppercutThinTactic::Attack:       return TEXT("Attack");
    case EUppercutThinTactic::Guard:        return TEXT("Guard");
    case EUppercutThinTactic::Evade:        return TEXT("Evade");
    default:                                return TEXT("Observe");
    }
}

FUppercutThinDecision FUppercutThinPolicy::Decide(
    const FUppercutThinObservation& Obs, uint32& SubstreamX) const
{
    FUppercutThinDecision D;

    // G2: when Wind is low and there is no immediate threat, Rest or Observe.
    if (Obs.bWindLow && !Obs.bIncoming)
    {
        D.Tactic = (LcgMod(SubstreamX, 2) == 0)
            ? EUppercutThinTactic::Rest
            : EUppercutThinTactic::Observe;
        D.Reason = TEXT("RECOVER_WIND");
        return D;
    }

    // Escape the ropes when pinned.
    if (Obs.bOnRopes)
    {
        D.Tactic = EUppercutThinTactic::Retreat;
        D.Reason = TEXT("ESCAPE_ROPES");
        return D;
    }

    // Punish a recovering opponent when aggression seeks initiative.
    if (Obs.bOpponentRecovering && Obs.ThrowableHere.Num() > 0
        && (int32)(UppercutLcgNext(SubstreamX) % 10000u) < AggressionBiasQ)
    {
        D.Tactic = EUppercutThinTactic::Attack;
        D.Execution = Obs.ThrowableHere[LcgMod(SubstreamX, Obs.ThrowableHere.Num())];
        D.Reason = TEXT("PUNISH_RECOVERY");
        return D;
    }

    // Seek preferred range.
    if (Obs.Band != PreferredBand && Obs.Band != Obs.PreferredBand)
    {
        const bool bCloserWanted =
            (PreferredBand == TEXT("inside") || PreferredBand == TEXT("clinch")
             || PreferredBand == TEXT("mid"));
        D.Tactic = bCloserWanted ? EUppercutThinTactic::Advance
                                 : EUppercutThinTactic::Retreat;
        D.Reason = TEXT("SEEK_PREFERRED_RANGE");
        return D;
    }

    // At preferred range: attack or hold based on aggression bias.
    if (Obs.ThrowableHere.Num() > 0
        && (int32)(UppercutLcgNext(SubstreamX) % 10000u) < AggressionBiasQ)
    {
        D.Tactic = EUppercutThinTactic::Attack;
        D.Execution = Obs.ThrowableHere[LcgMod(SubstreamX, Obs.ThrowableHere.Num())];
        D.Reason = TEXT("HOLD_GOOD_RANGE");
        return D;
    }

    D.Tactic = EUppercutThinTactic::HoldPosition;
    D.Reason = TEXT("HOLD_GOOD_RANGE");
    return D;
}
// [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 02:53 UTC | END ]

// [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 03:13 UTC | START ]
// LCG constants live in UppercutRangeCore; this file must not re-paste them
// (Decision 0022 copy-count guard).
// [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 03:13 UTC | END ]
