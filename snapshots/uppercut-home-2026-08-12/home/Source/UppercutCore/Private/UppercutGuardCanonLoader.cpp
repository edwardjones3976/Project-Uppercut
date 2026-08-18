// [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 07:15 UTC | START ]
#include "UppercutGuardCore.h"

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

bool UppercutLoadGuardCanon(const FString& RepoDir,
                            FUppercutGuardCanon& Out,
                            TArray<FUppercutCanonSource>& OutSources,
                            FString& OutError)
{
    Out = FUppercutGuardCanon();
    OutSources.Reset();
    OutError.Reset();

    const TCHAR* Rel[3] = { TEXT("data/guard_evasion_model.json"),
                              TEXT("data/collision_model.json"),
                              TEXT("data/pose_geometry.json") };
    const TCHAR* Label[3] = { TEXT("guard"), TEXT("collision"), TEXT("pose") };
    TSharedPtr<FJsonObject> Root[3];
    for (int32 i = 0; i < 3; ++i)
    {
        FUppercutCanonSource Src;
        Src.RelPath = Rel[i];
        Src.Label = Label[i];
        if (!ReadJson(RepoDir / Rel[i], Root[i], Src.Sha256))
        {
            OutError = FString::Printf(TEXT("cannot read canon file %s"), Rel[i]);
            return false;
        }
        OutSources.Add(Src);
    }

    const TSharedPtr<FJsonObject> GuardRoot = Root[0];
    const TSharedPtr<FJsonObject> Pose = Root[2];
    Out.Threshold = Q(Pose->GetObjectField(TEXT("guard"))
                        ->GetNumberField(TEXT("plane_interception_min_extent")));
    Out.CommittedMultiplier = Q(GuardRoot->GetObjectField(TEXT("committed_defense"))
                                    ->GetNumberField(
                                        TEXT("guard_extent_multiplier_while_committed")));

    for (const TSharedPtr<FJsonValue>& V :
         Root[1]->GetObjectField(TEXT("volumes"))->GetArrayField(TEXT("guard_volumes")))
    {
        const TSharedPtr<FJsonObject> GV = V->AsObject();
        Out.VolByClass.Add(GV->GetStringField(TEXT("height_class")),
                           GV->GetStringField(TEXT("id")));
    }

    for (const TSharedPtr<FJsonValue>& V :
         Pose->GetArrayField(TEXT("height_by_guard_interaction")))
    {
        const TSharedPtr<FJsonObject> E = V->AsObject();
        Out.HeightByInteraction.Add(E->GetStringField(TEXT("guard_interaction")),
                                    E->GetStringField(TEXT("height_class")));
    }

    const TSharedPtr<FJsonObject> MovesJson;
    {
        FString Sha;
        TSharedPtr<FJsonObject> MovesRoot;
        if (!ReadJson(RepoDir / TEXT("data/moves/generic_sandbox_moves.json"),
                      MovesRoot, Sha))
        {
            OutError = TEXT("cannot read moves canon for guard interactions");
            return false;
        }
        for (const TSharedPtr<FJsonValue>& V : MovesRoot->GetArrayField(TEXT("moves")))
        {
            const TSharedPtr<FJsonObject> M = V->AsObject();
            if (M->HasField(TEXT("guard_interaction")))
            {
                Out.InteractionByMove.Add(M->GetStringField(TEXT("id")),
                                          M->GetStringField(TEXT("guard_interaction")));
            }
        }
    }

    for (const TSharedPtr<FJsonValue>& V : GuardRoot->GetArrayField(TEXT("postures")))
    {
        const TSharedPtr<FJsonObject> P = V->AsObject();
        FUppercutGuardPosture Ps;
        Ps.Mobility = Q(P->GetNumberField(TEXT("mobility_multiplier")));
        Ps.HoldPerTick = Q(P->GetNumberField(TEXT("stamina_per_tick")));
        const TSharedPtr<FJsonObject> Ex = P->GetObjectField(TEXT("extents"));
        for (const auto& Pair : Ex->Values)
        {
            Ps.Extents.Add(FString(Pair.Key), Q(Pair.Value->AsNumber()));
        }
        Out.Postures.Add(P->GetStringField(TEXT("id")), Ps);
    }

    if (Out.CanonErrors() > 0)
    {
        OutError = TEXT("guard canon failed contract checks");
        return false;
    }
    return true;
}
// [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 07:15 UTC | END ]
