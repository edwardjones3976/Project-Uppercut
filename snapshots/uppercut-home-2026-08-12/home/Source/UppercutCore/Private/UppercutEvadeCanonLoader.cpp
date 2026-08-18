// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 19:55 UTC | START ]
//
// THE ONLY PLACE PHASE R'S CANON IS READ. Same argument as the Phase Q loader:
// a second reader is a second set of decisions about which JSON field means
// what, and the two agree right up until one of them is edited.

#include "UppercutEvadeCore.h"

#include "Dom/JsonObject.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"

namespace
{
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

bool UppercutLoadEvadeCanon(const FString& RepoDir,
                            FUppercutEvadeCanon& Out,
                            TArray<FUppercutCanonSource>& OutSources,
                            FString& OutError)
{
    Out = FUppercutEvadeCanon();
    OutSources.Reset();
    OutError.Reset();

    // Three files, and deliberately not more. This phase reads no separation,
    // no geometry, no guard and no stamina - a fourth file would be a claim the
    // contract does not make.
    const TCHAR* Rel[3] = { TEXT("data/guard_evasion_model.json"),
                            TEXT("data/moves/generic_sandbox_moves.json"),
                            TEXT("data/animation_model.json") };
    const TCHAR* Label[3] = { TEXT("guard_evasion"), TEXT("moves"),
                              TEXT("animation") };

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

    // ---- the whole move table, not only the punches -----------------------
    // `Beats()` matches on category, so a move this phase never throws still
    // has to be describable or the match would silently narrow.
    TMap<FString, TSharedPtr<FJsonObject>> MoveTable;
    for (const TSharedPtr<FJsonValue>& V : Root[1]->GetArrayField(TEXT("moves")))
    {
        const TSharedPtr<FJsonObject> M = V->AsObject();
        const FString Id = M->GetStringField(TEXT("id"));
        MoveTable.Add(Id, M);
        FString Cat;
        M->TryGetStringField(TEXT("category"), Cat);
        Out.Category.Add(Id, Cat);
        FString Reg;
        const TArray<TSharedPtr<FJsonValue>>* Regs = nullptr;
        if (M->TryGetArrayField(TEXT("target_regions"), Regs) && Regs->Num() > 0)
        {
            Reg = (*Regs)[0]->AsString();
        }
        Out.Region.Add(Id, Reg);
        FString Band;
        if (M->TryGetStringField(TEXT("range_band"), Band) && !Band.IsEmpty())
        {
            Out.HasRangeBand.Add(Id);
        }
    }

    // ---- evasions ---------------------------------------------------------
    for (const TSharedPtr<FJsonValue>& V : Root[0]->GetArrayField(TEXT("evasions")))
    {
        const TSharedPtr<FJsonObject> E = V->AsObject();
        FUppercutEvasion Ev;
        Ev.Id = E->GetStringField(TEXT("id"));
        Ev.Kind = E->GetStringField(TEXT("kind"));
        E->TryGetNumberField(TEXT("active_ticks"), Ev.Active);
        const TArray<TSharedPtr<FJsonValue>>* Arr = nullptr;
        if (E->TryGetArrayField(TEXT("vacates"), Arr))
        {
            for (const TSharedPtr<FJsonValue>& X : *Arr) { Ev.Vacates.Add(X->AsString()); }
        }
        if (E->TryGetArrayField(TEXT("beaten_by"), Arr))
        {
            for (const TSharedPtr<FJsonValue>& X : *Arr) { Ev.BeatenBy.Add(X->AsString()); }
        }
        Ev.Vacates.Sort();
        Ev.BeatenBy.Sort();
        const FString MoveId = E->GetStringField(TEXT("move_id"));
        if (const TSharedPtr<FJsonObject>* M = MoveTable.Find(MoveId))
        {
            (*M)->TryGetNumberField(TEXT("startup_frames"), Ev.Startup);
            (*M)->TryGetNumberField(TEXT("recovery_frames"), Ev.Recovery);
        }
        Out.Evasions.Add(Ev.Id, Ev);
    }

    const TSharedPtr<FJsonObject> Econ =
        Root[0]->GetObjectField(TEXT("evasion_economy"));
    Out.bOutranksGuard = Econ->GetBoolField(TEXT("outranks_guard"));
    Out.MistimeTicks = (int32)Econ->GetNumberField(TEXT("mistime_penalty_ticks"));

    // ---- the six punches, with their animation timings --------------------
    TMap<FString, TSharedPtr<FJsonObject>> Anim;
    for (const TSharedPtr<FJsonValue>& V :
         Root[2]->GetArrayField(TEXT("move_animations")))
    {
        Anim.Add(V->AsObject()->GetStringField(TEXT("move_id")), V->AsObject());
    }
    for (int32 i = 0; i < 6; ++i)
    {
        const FString Id = UppercutEvadePunchId(i);
        const TSharedPtr<FJsonObject>* A = Anim.Find(Id);
        if (!A)
        {
            OutError = FString::Printf(TEXT("%s has no animation"), *Id);
            return false;
        }
        FUppercutEvadePunch P;
        P.Id = Id;
        P.Category = Out.Category.FindRef(Id);
        P.Region = Out.Region.FindRef(Id);
        P.Startup = (int32)(*A)->GetNumberField(TEXT("startup_ticks"));
        P.Active = (int32)(*A)->GetNumberField(TEXT("active_ticks"));
        P.Frames = P.Startup + P.Active
                 + (int32)(*A)->GetNumberField(TEXT("recovery_ticks"));
        Out.Punches.Add(Id, P);
    }

    return true;
}
// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 19:55 UTC | END ]
