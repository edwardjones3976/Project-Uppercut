// [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 07:15 UTC | START ]
#include "UppercutGuardCore.h"

#include "UppercutRangeCore.h"

FString FUppercutGuardCanon::LaneOf(const FString& MoveId) const
{
    const FString* Interaction = InteractionByMove.Find(MoveId);
    if (!Interaction) { return FString(); }
    const FString* Lane = HeightByInteraction.Find(*Interaction);
    return Lane ? *Lane : FString();
}

TSet<FString> FUppercutGuardCanon::CoveredLanes(const FString& PostureId,
                                                bool bCommitted,
                                                int32 ReadinessQ) const
{
    TSet<FString> Out;
    const FUppercutGuardPosture* Ps = Postures.Find(PostureId);
    if (!Ps) { return Out; }
    const int64 Mult = bCommitted ? CommittedMultiplier : 10000;
    for (const TPair<FString, FString>& VC : VolByClass)
    {
        const int64* Ext = Ps->Extents.Find(VC.Value);
        if (!Ext) { continue; }
        const int64 Scaled = UppercutFloorDiv(
            UppercutFloorDiv((*Ext) * Mult * ReadinessQ, 10000), 10000);
        if (Scaled >= Threshold)
        {
            Out.Add(VC.Key);
        }
    }
    return Out;
}

bool FUppercutGuardCanon::Intercepts(const FString& PostureId, bool bCommitted,
                                     const FString& MoveId,
                                     int32 ReadinessQ) const
{
    const FString Lane = LaneOf(MoveId);
    if (Lane.IsEmpty()) { return false; }
    return CoveredLanes(PostureId, bCommitted, ReadinessQ).Contains(Lane);
}

int32 FUppercutGuardCanon::CanonErrors() const
{
    int32 Errors = 0;
    if (Postures.Num() == 0) { ++Errors; }
    if (VolByClass.Num() == 0) { ++Errors; }
    if (Threshold <= 0) { ++Errors; }
    if (CommittedMultiplier <= 0 || CommittedMultiplier >= 10000) { ++Errors; }
    return Errors;
}
// [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 07:15 UTC | END ]
