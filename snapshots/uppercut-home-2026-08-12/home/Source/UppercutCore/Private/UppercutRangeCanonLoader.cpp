// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 19:25 UTC | the canon loader | START ]
//
// THE ONLY PLACE PHASE Q'S CANON IS READ.
//
// This used to live inside the commandlet's `Main()`, which was fine while the
// commandlet was the only thing that ran the phase. It stops being fine the
// moment a live subsystem wants to run the same fight: a second reader is a
// second set of decisions about which JSON field means what, and the two agree
// right up until one of them is edited.
//
// The hashes come out of the same read as the canon, deliberately. A header
// that hashes the files separately is asserting the fight ran on those bytes;
// this one has actually parsed them.

#include "UppercutRangeCore.h"
#include "UppercutCanonSource.h"

#include "Dom/JsonObject.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"

namespace
{
    // q10000. Every canon number crosses into the integer contract here and
    // nowhere else, which is why nothing downstream ever sees a double.
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

bool UppercutLoadRangeCanon(const FString& RepoDir,
                            FUppercutRangeCanon& Out,
                            TArray<FUppercutCanonSource>& OutSources,
                            FString& OutError)
{
    Out = FUppercutRangeCanon();
    OutSources.Reset();
    OutError.Reset();

    // Exactly the four files the phase reads. A fifth would be a claim this
    // contract does not make.
    const TCHAR* Rel[4] = { TEXT("data/movement_model.json"),
                            TEXT("data/moves/generic_sandbox_moves.json"),
                            TEXT("data/animation_model.json"),
                            TEXT("data/pose_geometry.json") };
    const TCHAR* Label[4] = { TEXT("movement"), TEXT("moves"),
                              TEXT("animation"), TEXT("pose") };

    TSharedPtr<FJsonObject> Root[4];
    for (int32 i = 0; i < 4; ++i)
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

    // ---- range bands ------------------------------------------------------
    const TSharedPtr<FJsonObject> RB = Root[0]->GetObjectField(TEXT("range_bands"));
    for (const TSharedPtr<FJsonValue>& V : RB->GetArrayField(TEXT("bands")))
    {
        const TSharedPtr<FJsonObject> B = V->AsObject();
        Out.BandKey.Add(B->GetStringField(TEXT("key")));
        Out.BandLo.Add(Q(B->GetNumberField(TEXT("min_ru"))));
        Out.BandHi.Add(B->HasTypedField<EJson::Number>(TEXT("max_ru"))
                       ? Q(B->GetNumberField(TEXT("max_ru")))
                       : FUppercutRangeCanon::Unbounded);
    }
    Out.Hyst = Q(RB->GetNumberField(TEXT("hysteresis_ru")));

    // ---- locomotion -------------------------------------------------------
    const TSharedPtr<FJsonObject> Loco = Root[0]->GetObjectField(TEXT("locomotion"));
    for (const TSharedPtr<FJsonValue>& V : Loco->GetArrayField(TEXT("modes")))
    {
        const TSharedPtr<FJsonObject> M = V->AsObject();
        if (M->GetStringField(TEXT("posture_mode")) == TEXT("boxing_steps"))
        {
            Out.Stride = Q(M->GetNumberField(TEXT("stride_length_ru")));
        }
    }
    Out.Cap = Q(Loco->GetNumberField(TEXT("max_frame_displacement_ru")));
    const TSharedPtr<FJsonObject> Dir = Loco->GetObjectField(TEXT("directional"));
    Out.DirAdvance = Q(Dir->GetNumberField(TEXT("advance_stride_multiplier")));
    Out.DirRetreat = Q(Dir->GetNumberField(TEXT("retreat_stride_multiplier")));
    Out.DirLateral = Q(Dir->GetNumberField(TEXT("lateral_stride_multiplier")));
    Out.MinSep = Q(Root[0]->GetObjectField(TEXT("separation"))
                   ->GetNumberField(TEXT("min_center_distance_ru")));

    const TSharedPtr<FJsonObject> Track =
        Root[0]->GetObjectField(TEXT("ring"))->GetObjectField(TEXT("track"));
    Out.Axis = Q(Track->GetNumberField(TEXT("axis_length_ru")));
    Out.Ropes = Q(Track->GetNumberField(TEXT("back_to_ropes_ru")));
    Out.RopeRetreat = Q(Track->GetNumberField(TEXT("rope_retreat_multiplier")));

    // ---- geometry ---------------------------------------------------------
    const TSharedPtr<FJsonObject> Pose = Root[3];
    Out.HalfDepth = Q(Pose->GetObjectField(TEXT("body"))->GetNumberField(TEXT("half_depth_ru")));
    const TSharedPtr<FJsonObject> Fist = Pose->GetObjectField(TEXT("fist"));
    Out.Retracted = Q(Fist->GetNumberField(TEXT("retracted_ru")));
    TMap<FString, int64> ExtBy;
    for (const TSharedPtr<FJsonValue>& V : Fist->GetArrayField(TEXT("extension_by_move")))
    {
        const TSharedPtr<FJsonObject> E = V->AsObject();
        ExtBy.Add(E->GetStringField(TEXT("move_id")), Q(E->GetNumberField(TEXT("extended_ru"))));
    }

    // ---- moves and their animations ---------------------------------------
    TMap<FString, TSharedPtr<FJsonObject>> Anim;
    for (const TSharedPtr<FJsonValue>& V : Root[2]->GetArrayField(TEXT("move_animations")))
    {
        Anim.Add(V->AsObject()->GetStringField(TEXT("move_id")), V->AsObject());
    }
    TMap<FString, TSharedPtr<FJsonObject>> Moves;
    for (const TSharedPtr<FJsonValue>& V : Root[1]->GetArrayField(TEXT("moves")))
    {
        const TSharedPtr<FJsonObject> M = V->AsObject();
        const FString Id = M->GetStringField(TEXT("id"));
        Moves.Add(Id, M);
        FString Band;
        if (M->TryGetStringField(TEXT("range_band"), Band) && !Band.IsEmpty())
        {
            Out.MoveBand.Add(Id, Band);
        }
    }

    // Index 0 is idle, which is the absence of a move and therefore has no
    // entry to find.
    for (int32 a = 1; a < 9; ++a)
    {
        const FString Id = UppercutRangeActionName(a);
        const TSharedPtr<FJsonObject>* M = Moves.Find(Id);
        if (!M)
        {
            OutError = FString::Printf(TEXT("move %s is not in canon"), *Id);
            return false;
        }
        FUppercutRangeMove D;
        if (a >= 4)
        {
            const TSharedPtr<FJsonObject>* A = Anim.Find(Id);
            if (!A)
            {
                OutError = FString::Printf(TEXT("%s has no animation"), *Id);
                return false;
            }
            D.bPunch = true;
            D.Startup = (int32)(*A)->GetNumberField(TEXT("startup_ticks"));
            D.Active = (int32)(*A)->GetNumberField(TEXT("active_ticks"));
            D.Frames = D.Startup + D.Active + (int32)(*A)->GetNumberField(TEXT("recovery_ticks"));
            const int64* E = ExtBy.Find(Id);
            D.Ext = E ? *E : 0;
        }
        else
        {
            D.Frames = (int32)(*M)->GetNumberField(TEXT("startup_frames"))
                     + (int32)(*M)->GetNumberField(TEXT("recovery_frames"));
        }
        Out.Moves.Add(Id, D);
    }

    return true;
}
// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 19:25 UTC | the canon loader | END ]
