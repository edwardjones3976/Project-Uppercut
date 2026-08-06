// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 15:05 UTC | START ]
#include "UppercutEvadeCore.h"

bool FUppercutEvadeCanon::Beats(const FString& EvasionId, const FString& MoveId) const
{
    const FUppercutEvasion* E = Evasions.Find(EvasionId);
    if (!E) { return false; }
    const FString* Cat = Category.Find(MoveId);
    return Cat != nullptr && !Cat->IsEmpty() && E->BeatenBy.Contains(*Cat);
}

bool FUppercutEvadeCanon::Evades(const FString& EvasionId, const FString& MoveId,
                                 const FString& InRegion) const
{
    const FUppercutEvasion* E = Evasions.Find(EvasionId);
    if (!E || E->Kind != TEXT("active_window")) { return false; }
    if (!E->Vacates.Contains(InRegion)) { return false; }
    return !Beats(EvasionId, MoveId);
}

bool FUppercutEvadeCanon::BodyShotBeatsTheSlip() const
{
    bool bAny = false;
    for (const TPair<FString, FString>& It : Region)
    {
        if (It.Value != TEXT("torso_upper") && It.Value != TEXT("torso_lower"))
        {
            continue;
        }
        bAny = true;
        if (Evades(TEXT("slip_lead"), It.Key, It.Value)) { return false; }
    }
    return bAny;
}

bool FUppercutEvadeCanon::UppercutBeatsTheRoll() const
{
    const FUppercutEvasion* Roll = Evasions.Find(TEXT("roll_under"));
    if (!Roll) { return false; }
    bool bAny = false;
    for (const TPair<FString, FString>& It : Category)
    {
        if (It.Value != TEXT("uppercut")) { continue; }
        bAny = true;
        const FString Reg = Region.FindRef(It.Key);
        if (!Roll->Vacates.Contains(Reg)) { return false; }
        if (Evades(TEXT("roll_under"), It.Key, Reg)) { return false; }
    }
    return bAny;
}

bool FUppercutEvadeCanon::SlipEvadesAStraight() const
{
    bool bAny = false;
    for (const TPair<FString, FString>& It : Category)
    {
        if (It.Value != TEXT("jab") && It.Value != TEXT("cross")) { continue; }
        bAny = true;
        if (!Evades(TEXT("slip_lead"), It.Key, Region.FindRef(It.Key)))
        {
            return false;
        }
    }
    return bAny;
}

bool FUppercutEvadeCanon::NoEvasionIsStrictlyBetter() const
{
    // Against the PHASE O punch set, which is what the contract compares to -
    // not this phase's six.
    const TCHAR* OPunches[5] = { TEXT("jab_lead"), TEXT("cross_rear"),
                                 TEXT("hook_lead"), TEXT("uppercut_rear"),
                                 TEXT("body_straight_rear") };
    for (const TPair<FString, FUppercutEvasion>& It : Evasions)
    {
        if (It.Value.Kind != TEXT("active_window")) { continue; }
        bool bBeaten = false;
        for (int32 i = 0; i < 5 && !bBeaten; ++i)
        {
            bBeaten = Beats(It.Key, OPunches[i]);
        }
        if (!bBeaten) { return false; }
    }
    return true;
}

int32 FUppercutEvadeCanon::CanonErrors() const
{
    int32 Errors = 0;
    TArray<FString> ActiveIds;
    for (const TPair<FString, FUppercutEvasion>& It : Evasions)
    {
        if (It.Value.Kind == TEXT("active_window")) { ActiveIds.Add(It.Key); }
        if (It.Value.Kind == TEXT("positional") && It.Value.Vacates.Num() > 0)
        {
            ++Errors;
        }
    }
    ActiveIds.Sort();
    if (ActiveIds.Num() == 0) { ++Errors; }
    const TCHAR* DamageRegions[6] = { TEXT("head"), TEXT("jaw_chin"),
                                      TEXT("torso_upper"), TEXT("torso_lower"),
                                      TEXT("arm_left"), TEXT("arm_right") };
    for (const FString& Id : ActiveIds)
    {
        const FUppercutEvasion& E = Evasions[Id];
        if (E.Active <= 0) { ++Errors; }
        if (E.Vacates.Num() == 0) { ++Errors; }
        if (E.BeatenBy.Num() == 0) { ++Errors; }
        if (!HasRangeBand.Contains(Id)) { ++Errors; }
        for (const FString& R : E.Vacates)
        {
            bool bKnown = false;
            for (int32 i = 0; i < 6 && !bKnown; ++i) { bKnown = (R == DamageRegions[i]); }
            if (!bKnown) { ++Errors; }
        }
    }
    if (!bOutranksGuard) { ++Errors; }
    if (MistimeTicks <= 0) { ++Errors; }
    // The telegraph, unpriced and asserted: if every punch spent the same time
    // in the air, a fixed evasion window could not distinguish a slow punch
    // from a fast one and canon's telegraph would need a multiplier to exist.
    if (Punches.Num() > 0)
    {
        int32 MinSpan = MAX_int32, MaxSpan = 0;
        for (const TPair<FString, FUppercutEvadePunch>& It : Punches)
        {
            const int32 Span = It.Value.Startup + It.Value.Active;
            MinSpan = FMath::Min(MinSpan, Span);
            MaxSpan = FMath::Max(MaxSpan, Span);
        }
        if (MinSpan == MaxSpan) { ++Errors; }
    }
    return Errors;
}
// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 15:05 UTC | END ]
