// [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 07:35 UTC | START ]
#include "UppercutPunchEconomyCore.h"

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

int32 FUppercutPunchEconomyCanon::CanonErrors() const
{
    int32 Errors = 0;
    if (!RecoveryMultiplierQ.Contains(TEXT("blocked"))) { ++Errors; }
    if (!RecoveryMultiplierQ.Contains(TEXT("dodged"))) { ++Errors; }
    if (!RecoveryMultiplierQ.Contains(TEXT("whiffed"))) { ++Errors; }
    if (MaxArmMultiplierQ <= 10000) { ++Errors; }
    return Errors;
}

bool UppercutLoadPunchEconomyCanon(const FString& RepoDir,
                                   FUppercutPunchEconomyCanon& Out,
                                   TArray<FUppercutCanonSource>& OutSources,
                                   FString& OutError)
{
    Out = FUppercutPunchEconomyCanon();
    OutSources.Reset();
    OutError.Reset();

    TSharedPtr<FJsonObject> PunchRoot;
    FUppercutCanonSource Src;
    Src.RelPath = TEXT("data/punch_model.json");
    Src.Label = TEXT("punch");
    if (!ReadJson(RepoDir / Src.RelPath, PunchRoot, Src.Sha256))
    {
        OutError = TEXT("cannot read punch_model.json");
        return false;
    }
    OutSources.Add(Src);

    for (const TSharedPtr<FJsonValue>& V :
         PunchRoot->GetObjectField(TEXT("outcome_recovery"))
             ->GetArrayField(TEXT("rows")))
    {
        const TSharedPtr<FJsonObject> R = V->AsObject();
        Out.RecoveryMultiplierQ.Add(R->GetStringField(TEXT("class")),
                                    Q(R->GetNumberField(TEXT("recovery_multiplier"))));
    }

    const TArray<TSharedPtr<FJsonValue>>* Mechs = nullptr;
    PunchRoot->GetObjectField(TEXT("repetition_economy"))
        ->TryGetArrayField(TEXT("mechanisms"), Mechs);
    if (Mechs)
    {
        for (const TSharedPtr<FJsonValue>& V : *Mechs)
        {
            const TSharedPtr<FJsonObject> M = V->AsObject();
            const FString Id = M->GetStringField(TEXT("id"));
            const TSharedPtr<FJsonObject> K = M->GetObjectField(TEXT("coefficients"));
            if (Id == TEXT("arm_fatigue"))
            {
                Out.PerThrowSameArm = Q(K->GetNumberField(TEXT("per_throw_same_arm")));
                Out.RecoveryPerIdleTick =
                    Q(K->GetNumberField(TEXT("recovery_per_idle_tick")));
                Out.MaxArmMultiplierQ = Q(K->GetNumberField(TEXT("max_multiplier")));
            }
            else if (Id == TEXT("position_cost"))
            {
                Out.RuCededPerThrowWithoutStep =
                    Q(K->GetNumberField(TEXT("ru_ceded_per_throw_without_step")));
            }
        }
    }

    TSharedPtr<FJsonObject> MovesRoot;
    FString Sha;
    if (ReadJson(RepoDir / TEXT("data/moves/generic_sandbox_moves.json"),
                 MovesRoot, Sha))
    {
        for (const TSharedPtr<FJsonValue>& V : MovesRoot->GetArrayField(TEXT("moves")))
        {
            const TSharedPtr<FJsonObject> M = V->AsObject();
            if (M->HasField(TEXT("hand")))
            {
                Out.HandByMove.Add(M->GetStringField(TEXT("id")),
                                   M->GetStringField(TEXT("hand")));
            }
        }
    }

    if (Out.CanonErrors() > 0)
    {
        OutError = TEXT("punch economy canon failed contract checks");
        return false;
    }
    return true;
}

int64 UppercutArmMultiplierQ(const FUppercutPunchEconomyCanon& Canon, int64 ArmWorkQ)
{
    const int64 Ceiling = Canon.MaxArmMultiplierQ - 10000;
    const int64 Work = FMath::Min(Ceiling, FMath::Max((int64)0, ArmWorkQ));
    return FMath::Min(Canon.MaxArmMultiplierQ, 10000 + Work);
}

int64 UppercutApplyOutcomeRecovery(const FUppercutPunchEconomyCanon& Canon,
                                   const FString& OutcomeClass,
                                   int32 BaseRecoveryTicks)
{
    const int64 MultQ = Canon.RecoveryMultiplierQ.FindRef(OutcomeClass);
    if (MultQ <= 10000 || BaseRecoveryTicks <= 0) { return BaseRecoveryTicks; }
    return (int32)UppercutFloorDiv(BaseRecoveryTicks * MultQ, 10000);
}
// [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 07:35 UTC | END ]
