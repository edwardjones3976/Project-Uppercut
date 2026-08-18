// [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 07:45 UTC | START ]
#include "UppercutConditionCore.h"

#include "UppercutRangeCore.h"

#include "Dom/JsonObject.h"
#include "Misc/FileHelper.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"

namespace
{
    int64 Q(double V) { return (int64)FMath::RoundToDouble(V * 10000.0); }

    bool ReadJson(const FString& Path, TSharedPtr<FJsonObject>& OutRoot, FString& OutSha)
    {
        TArray<uint8> Bytes;
        if (!FFileHelper::LoadFileToArray(Bytes, *Path)) { return false; }
        OutSha = UppercutSha256Hex(Bytes.GetData(), Bytes.Num());
        FString Text;
        FFileHelper::BufferToString(Text, Bytes.GetData(), Bytes.Num());
        const TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(Text);
        return FJsonSerializer::Deserialize(Reader, OutRoot) && OutRoot.IsValid();
    }
}

int32 FUppercutConditionCanon::CanonErrors() const
{
    return Regions.Num() == 0 ? 1 : 0;
}

void FUppercutRegionalCondition::Reset(const FUppercutConditionCanon& Canon)
{
    Damage.Reset();
    for (const auto& Pair : Canon.Regions)
    {
        Damage.Add(Pair.Key, 0);
    }
}

int32 FUppercutRegionalCondition::Absorb(const FUppercutConditionCanon& Canon,
                                         const FString& Region, int32 Force)
{
    if (Force < 0) { return 0; }
    int32* D = Damage.Find(Region);
    if (!D) { return 0; }
    const FUppercutConditionRegion* Spec = Canon.Regions.Find(Region);
    if (!Spec) { return 0; }
    *D = FMath::Min(Spec->Capacity, *D + Force);
    return Spec->Capacity > 0 ? (*D * 10000) / Spec->Capacity : 0;
}

int32 FUppercutRegionalCondition::WorstKnockdownFractionQ(
    const FUppercutConditionCanon& Canon) const
{
    int32 Worst = 0;
    for (const auto& Pair : Canon.Regions)
    {
        if (!Pair.Value.bKnockdownRelevant) { continue; }
        const int32* D = Damage.Find(Pair.Key);
        if (!D) { continue; }
        const int32 Frac = Pair.Value.Capacity > 0
            ? (*D * 10000) / Pair.Value.Capacity : 0;
        Worst = FMath::Max(Worst, Frac);
    }
    return Worst;
}

void FUppercutRegionalCondition::ApplyCountRelief(const FUppercutConditionCanon& Canon)
{
    for (auto& Pair : Damage)
    {
        Pair.Value -= (int32)UppercutFloorDiv(Pair.Value * Canon.CountReliefQ, 10000);
    }
}

bool UppercutLoadConditionCanon(const FString& RepoDir,
                                FUppercutConditionCanon& Out,
                                TArray<FUppercutCanonSource>& OutSources,
                                FString& OutError)
{
    Out = FUppercutConditionCanon();
    OutSources.Reset();
    TSharedPtr<FJsonObject> Cond;
    FUppercutCanonSource Src;
    Src.RelPath = TEXT("data/condition_model.json");
    Src.Label = TEXT("condition");
    if (!ReadJson(RepoDir / Src.RelPath, Cond, Src.Sha256))
    {
        OutError = TEXT("cannot read condition_model.json");
        return false;
    }
    OutSources.Add(Src);

    for (const TSharedPtr<FJsonValue>& V : Cond->GetArrayField(TEXT("damage_regions")))
    {
        const TSharedPtr<FJsonObject> R = V->AsObject();
        FUppercutConditionRegion Spec;
        Spec.Capacity = (int32)R->GetNumberField(TEXT("capacity"));
        Spec.bKnockdownRelevant = R->GetBoolField(TEXT("knockdown_relevant"));
        Out.Regions.Add(R->GetStringField(TEXT("region")), Spec);
    }
    const TSharedPtr<FJsonObject> Kd = Cond->GetObjectField(TEXT("knockdown"));
    Out.PressureBaselineQ = Q(Kd->GetObjectField(TEXT("pressure_modifiers"))
                                  ->GetNumberField(TEXT("undamaged_baseline")));
    Out.CountReliefQ = Q(Kd->GetNumberField(TEXT("count_condition_relief_fraction")));

    TSharedPtr<FJsonObject> Effort;
    FString Sha;
    if (ReadJson(RepoDir / TEXT("data/moves/generic_sandbox_effort.json"), Effort, Sha))
    {
        for (const TSharedPtr<FJsonValue>& V : Effort->GetArrayField(TEXT("moves")))
        {
            const TSharedPtr<FJsonObject> M = V->AsObject();
            Out.EffortByMove.Add(M->GetStringField(TEXT("move_id")),
                                 (int64)M->GetNumberField(TEXT("effort")));
        }
    }
    TSharedPtr<FJsonObject> Moves;
    if (ReadJson(RepoDir / TEXT("data/moves/generic_sandbox_moves.json"), Moves, Sha))
    {
        for (const TSharedPtr<FJsonValue>& V : Moves->GetArrayField(TEXT("moves")))
        {
            const TSharedPtr<FJsonObject> M = V->AsObject();
            const TArray<TSharedPtr<FJsonValue>>* Regions = nullptr;
            if (M->TryGetArrayField(TEXT("target_regions"), Regions)
                && Regions && Regions->Num() > 0)
            {
                Out.PrimaryRegionByMove.Add(
                    M->GetStringField(TEXT("id")),
                    (*Regions)[0]->AsString());
            }
        }
    }
    if (Out.CanonErrors() > 0)
    {
        OutError = TEXT("condition canon failed contract checks");
        return false;
    }
    return true;
}

int64 UppercutDeliveredImpactQ(const FUppercutConditionCanon& Canon,
                               const FString& MoveId)
{
    const int64* Effort = Canon.EffortByMove.Find(MoveId);
    return Effort ? (*Effort) * 100 : 500000; // q10000 scale proxy
}

int64 UppercutKnockdownPressureQ(
    const FUppercutConditionCanon& Canon,
    const FString& MoveId,
    const FUppercutRegionalCondition& Defender,
    int32 DefenderWindFractionQ,
    bool bDefenderCommitted,
    bool bDefenderEvading,
    const FUppercutFighterCard& DefenderCard,
    const FUppercutAttrCanon& AttrCanon)
{
    const int64 ForceQ = UppercutDeliveredImpactQ(Canon, MoveId);
    const int32 Worst = Defender.WorstKnockdownFractionQ(Canon);
    int64 CondQ = Canon.PressureBaselineQ
        + ((10000 - Canon.PressureBaselineQ) * Worst) / 10000;
    int64 FatigueQ = 10000 + (10000 - DefenderWindFractionQ);
    int64 PressureQ = UppercutFloorDiv(ForceQ * CondQ, 10000);
    PressureQ = UppercutFloorDiv(PressureQ * FatigueQ, 10000);
    if (bDefenderCommitted) { PressureQ = UppercutFloorDiv(PressureQ * 11500, 10000); }
    if (bDefenderEvading) { PressureQ = UppercutFloorDiv(PressureQ * 12000, 10000); }
    PressureQ = AttrCanon.Apply(PressureQ, DefenderCard, TEXT("knockdown_pressure"));
    return PressureQ;
}
// [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 07:45 UTC | END ]
