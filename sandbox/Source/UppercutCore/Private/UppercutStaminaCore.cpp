// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 10:45 UTC | START ]
#include "UppercutStaminaCore.h"

#include "Dom/JsonObject.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"
#include "UppercutRangeCore.h"   // UppercutFloorDiv

namespace
{
    const TCHAR* GActionNames[8] = {
        TEXT("observe"), TEXT("hold_position"), TEXT("rest"), TEXT("micro_adjust"),
        TEXT("move"), TEXT("guard"), TEXT("evade"), TEXT("attack")
    };

    // The families that buy no Wind back at all (Decision 0021).
    bool IsWorking(EUppercutAction A)
    {
        return A == EUppercutAction::Move || A == EUppercutAction::Guard
            || A == EUppercutAction::Evade || A == EUppercutAction::Attack;
    }

    int64 Q(double V) { return (int64)FMath::RoundToDouble(V * 10000.0); }
}

const TCHAR* UppercutActionName(EUppercutAction Action)
{
    const int32 I = (int32)Action;
    return (I >= 0 && I < 8) ? GActionNames[I] : TEXT("");
}

bool UppercutActionFromName(const FString& Name, EUppercutAction& Out)
{
    for (int32 i = 0; i < 8; ++i)
    {
        if (Name.Equals(GActionNames[i], ESearchCase::CaseSensitive))
        {
            Out = (EUppercutAction)i;
            return true;
        }
    }
    return false;
}

int64 FUppercutStaminaCanon::WindCeiling(int64 Reserve) const
{
    const int64 Frac = ReserveMax ? UppercutFloorDiv(Reserve * 10000, ReserveMax) : 0;
    const int64 Mult = CeilingFloor + UppercutFloorDiv(CeilingSpan * Frac, 10000);
    return UppercutFloorDiv(WindMax * Mult, 10000);
}

int64 FUppercutStaminaCanon::RecoveryRate(EUppercutAction Action, int64 Reserve) const
{
    const int64 Base = Recover[(int32)Action];
    if (Base == 0) { return 0; }
    const int64 Frac = ReserveMax ? UppercutFloorDiv(Reserve * 10000, ReserveMax) : 0;
    const int64 Mult = RecoveryFloor + UppercutFloorDiv(RecoverySpan * Frac, 10000);
    return UppercutFloorDiv(Base * Mult, 10000);
}

int32 FUppercutStaminaCanon::CanonErrors(TArray<FString>* OutErrors) const
{
    TArray<FString> Errs;

    if (ReserveInRound != 0)
    {
        Errs.Add(TEXT("reserve recovers during a round, which erases the "
                      "distinction between getting your breath back and "
                      "getting your legs back"));
    }
    const int64 Rest = Recover[(int32)EUppercutAction::Rest];
    for (int32 i = 0; i < 8; ++i)
    {
        if (Recover[i] > Rest)
        {
            Errs.Add(FString::Printf(TEXT("%s recovers Wind faster than rest"),
                                     GActionNames[i]));
        }
        if (IsWorking((EUppercutAction)i) && Recover[i] != 0)
        {
            Errs.Add(FString::Printf(
                TEXT("%s recovers Wind, but Decision 0021 says working buys "
                     "none back"), GActionNames[i]));
        }
    }

    // THE UNITS GUARD. Made twice: 2026-08-03 and again 2026-08-07. A rate
    // authored as a small per-tick decimal that carries per-second magnitude
    // refills the pool inside a round and nobody ever tires. The numbers look
    // innocent until multiplied by the round length.
    const int64 RoundTicks = 180 * 60;
    for (int32 i = 0; i < 8; ++i)
    {
        if (Recover[i] * RoundTicks > WindMax)
        {
            Errs.Add(FString::Printf(
                TEXT("%s could refill the whole Wind pool inside one round - "
                     "this is the units error, twice made"), GActionNames[i]));
        }
    }

    if (CeilingFloor + CeilingSpan != 10000)
    {
        Errs.Add(TEXT("the Wind ceiling does not reach a full pool at full "
                      "Reserve, so a fresh fighter could never be fresh"));
    }

    // The inversion that justifies three numbers instead of one.
    const FUppercutMoveCost* Head = Moves.Find(TEXT("hook_lead"));
    const FUppercutMoveCost* Body = Moves.Find(TEXT("body_hook_lead"));
    if (Head && Body && Head->Effort == Body->Effort)
    {
        if (!(Body->Wind < Head->Wind && Body->Reserve > Head->Reserve))
        {
            Errs.Add(TEXT("body and head work of equal effort no longer differ "
                          "in the two tiers - the three-value model has "
                          "collapsed"));
        }
    }

    if (OutErrors) { *OutErrors = Errs; }
    return Errs.Num();
}

// ------------------------------------------------------------------ loader ----

static bool ReadJson(const FString& Path, TSharedPtr<FJsonObject>& Out)
{
    FString Text;
    if (!FFileHelper::LoadFileToString(Text, *Path)) { return false; }
    const TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(Text);
    return FJsonSerializer::Deserialize(Reader, Out) && Out.IsValid();
}

bool UppercutLoadStaminaCanon(const FString& RepoDir,
                              FUppercutStaminaCanon& Out,
                              FString& OutError)
{
    Out = FUppercutStaminaCanon();

    TSharedPtr<FJsonObject> Econ, Effort;
    if (!ReadJson(RepoDir / TEXT("data/stamina_economy.json"), Econ))
    {
        OutError = TEXT("cannot read data/stamina_economy.json");
        return false;
    }
    if (!ReadJson(RepoDir / TEXT("data/moves/generic_sandbox_effort.json"), Effort))
    {
        OutError = TEXT("cannot read data/moves/generic_sandbox_effort.json");
        return false;
    }

    const TSharedPtr<FJsonObject> Wind = Econ->GetObjectField(TEXT("wind"));
    const TSharedPtr<FJsonObject> Reserve = Econ->GetObjectField(TEXT("reserve"));

    Out.WindMax = Q(Wind->GetNumberField(TEXT("max")));
    Out.WindStart = UppercutFloorDiv(
        Out.WindMax * Q(Wind->GetNumberField(TEXT("start_fraction"))), 10000);
    Out.WindLow = UppercutFloorDiv(
        Out.WindMax * Q(Wind->GetNumberField(TEXT("low_threshold_fraction"))), 10000);
    Out.WindExhausted = UppercutFloorDiv(
        Out.WindMax * Q(Wind->GetNumberField(TEXT("exhausted_threshold_fraction"))), 10000);
    Out.WindBetweenRounds = Q(Wind->GetNumberField(TEXT("between_rounds_recovery_fraction")));

    // ONLY the eight declared families, by name. Taking everything that is not
    // a "$" key means a new prose field gets fed to a number parser - the
    // contract's loader had exactly that bug.
    const TSharedPtr<FJsonObject> Rec =
        Wind->GetObjectField(TEXT("recovery_per_tick_by_action"));
    for (int32 i = 0; i < 8; ++i)
    {
        double V = 0.0;
        if (!Rec->TryGetNumberField(GActionNames[i], V))
        {
            OutError = FString::Printf(TEXT("no Wind recovery rate declared for %s"),
                                       GActionNames[i]);
            return false;
        }
        Out.Recover[i] = Q(V);
    }

    const TSharedPtr<FJsonObject> Ceil = Wind->GetObjectField(TEXT("ceiling_from_reserve"));
    Out.CeilingFloor = Q(Ceil->GetNumberField(TEXT("floor_fraction")));
    Out.CeilingSpan = Q(Ceil->GetNumberField(TEXT("span_fraction")));
    const TSharedPtr<FJsonObject> RecFrom = Wind->GetObjectField(TEXT("recovery_from_reserve"));
    Out.RecoveryFloor = Q(RecFrom->GetNumberField(TEXT("floor_multiplier")));
    Out.RecoverySpan = Q(RecFrom->GetNumberField(TEXT("span_multiplier")));

    Out.ReserveMax = Q(Reserve->GetNumberField(TEXT("max")));
    Out.ReserveStart = UppercutFloorDiv(
        Out.ReserveMax * Q(Reserve->GetNumberField(TEXT("start_fraction"))), 10000);
    Out.ReserveLow = UppercutFloorDiv(
        Out.ReserveMax * Q(Reserve->GetNumberField(TEXT("low_threshold_fraction"))), 10000);
    Out.ReserveInRound = Q(Reserve->GetNumberField(TEXT("in_round_recovery_per_tick")));
    Out.ReserveBetweenRounds = Q(Reserve->GetNumberField(TEXT("between_rounds_recovery")));

    const TSharedPtr<FJsonObject> Drains = Reserve->GetObjectField(TEXT("drains"));
    Out.SustainedExertion = Q(Drains
        ->GetObjectField(TEXT("sustained_exertion_per_tick_below_low_wind"))
        ->GetNumberField(TEXT("value")));
    Out.BodyDamageMult = Q(Drains->GetObjectField(TEXT("body_damage_multiplier"))
                                 ->GetNumberField(TEXT("value")));

    const TSharedPtr<FJsonObject> Disp = Effort->GetObjectField(TEXT("displacement_movement"));
    Out.WindPerRu = Q(Disp->GetNumberField(TEXT("wind_per_ru")));
    Out.ReservePerRu = Q(Disp->GetNumberField(TEXT("reserve_per_ru")));

    for (const TSharedPtr<FJsonValue>& V : Effort->GetArrayField(TEXT("moves")))
    {
        const TSharedPtr<FJsonObject> M = V->AsObject();
        FUppercutMoveCost Cost;
        Cost.Effort = Q(M->GetNumberField(TEXT("effort")));
        FString Model;
        Cost.bDisplacement = M->TryGetStringField(TEXT("cost_model"), Model)
                             && Model == TEXT("displacement");
        if (!Cost.bDisplacement)
        {
            double W = 0.0, R = 0.0;
            M->TryGetNumberField(TEXT("wind_cost"), W);
            M->TryGetNumberField(TEXT("reserve_load"), R);
            Cost.Wind = Q(W);
            Cost.Reserve = Q(R);
        }
        Cost.Id = M->GetStringField(TEXT("move_id"));

        // Two ids differing only by case would collapse into one entry, because
        // FString keys hash case-insensitively. Silently keeping one row's
        // prices under the other row's name is exactly the class of bug this
        // economy cannot afford, so it is refused at load rather than found in
        // a trajectory later.
        if (const FUppercutMoveCost* Clash = Out.Moves.Find(Cost.Id))
        {
            OutError = FString::Printf(
                TEXT("move ids '%s' and '%s' collide - FString keys are "
                     "case-insensitive, so one of these would silently inherit "
                     "the other's costs"), *Clash->Id, *Cost.Id);
            return false;
        }
        Out.Moves.Add(Cost.Id, Cost);
    }

    return true;
}

// ------------------------------------------------------------------- state ----

void FUppercutStamina::Reset(const FUppercutStaminaCanon& C)
{
    Wind = C.WindStart;
    Reserve = C.ReserveStart;
}

bool FUppercutStamina::Step(const FUppercutStaminaCanon& C,
                            EUppercutAction Action,
                            const FString& MoveId,
                            int64 DisplacementRu,
                            FString& OutError)
{
    // ORDER MATTERS AND IS DELIBERATE:
    //   1. pay for the move, if this tick commits one;
    //   2. pay sustained exertion if working below the low-Wind line;
    //   3. recover, capped by the Reserve-limited ceiling.
    //
    // Recovery last means a fighter who spends and rests in the same tick is
    // not refunded before he has paid. Paying first also means the low-Wind
    // test sees the Wind he actually has after the spend, which is the honest
    // reading of "working while already short of breath".
    if (!MoveId.IsEmpty())
    {
        const FUppercutMoveCost* Cost = C.Moves.Find(MoveId);
        // A map hit is not a match. FString keys compare case-insensitively, so
        // Find() answers "some authored id equals this ignoring case" - the
        // stored spelling is what says whether canon actually declares THIS id.
        if (Cost != nullptr && !Cost->Id.Equals(MoveId, ESearchCase::CaseSensitive))
        {
            Cost = nullptr;
        }
        if (Cost == nullptr)
        {
            // FAILS CLOSED. Never "free".
            OutError = FString::Printf(
                TEXT("'%s' is not an authored move. Action families say how a "
                     "tick recovers; move ids say what it costs, and they are "
                     "not interchangeable."), *MoveId);
            return false;
        }
        if (Cost->bDisplacement)
        {
            Wind -= UppercutFloorDiv(DisplacementRu * C.WindPerRu, 10000);
            Reserve -= UppercutFloorDiv(DisplacementRu * C.ReservePerRu, 10000);
        }
        else
        {
            Wind -= Cost->Wind;
            Reserve -= Cost->Reserve;
        }
    }

    if (IsWorking(Action) && Wind < C.WindLow)
    {
        Reserve -= C.SustainedExertion;
    }

    Wind += C.RecoveryRate(Action, Reserve);

    if (Reserve < 0) { Reserve = 0; }
    if (Reserve > C.ReserveMax) { Reserve = C.ReserveMax; }
    const int64 Ceiling = C.WindCeiling(Reserve);
    if (Wind > Ceiling) { Wind = Ceiling; }
    if (Wind < 0) { Wind = 0; }
    return true;
}

void FUppercutStamina::BetweenRounds(const FUppercutStaminaCanon& C)
{
    Reserve = FMath::Min(C.ReserveMax, Reserve + C.ReserveBetweenRounds);
    const int64 Ceiling = C.WindCeiling(Reserve);
    Wind = FMath::Min(Ceiling,
                      Wind + UppercutFloorDiv((Ceiling - Wind) * C.WindBetweenRounds,
                                              10000));
}
// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 10:45 UTC | END ]
