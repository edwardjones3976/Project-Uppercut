// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 03:40 UTC | START ]
#include "UppercutCanonVectorsCommandlet.h"

#include "Dom/JsonObject.h"
#include "HAL/FileManager.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"
#include "UppercutCanonHash.h"

// NOTE ON THE READER USED HERE. The vectors FILE is ordinary tooling data, not
// canon, so Unreal's JSON reader is fine for it. The canon documents INSIDE it
// are handed to UppercutCanonHashes as raw text and parsed by the strict reader
// - which is the only one allowed to decide what a canon document says.

int32 UUppercutCanonVectorsCommandlet::Main(const FString& Params)
{
    FString Repo, OutPath;
    FParse::Value(*Params, TEXT("repo="), Repo);
    FParse::Value(*Params, TEXT("out="), OutPath);
    if (Repo.IsEmpty() || OutPath.IsEmpty())
    {
        UE_LOG(LogTemp, Error, TEXT("UppercutCanonVectors: need -repo= -out="));
        return 1;
    }

    const FString VectorsPath = Repo / TEXT("tests/fixtures/canon_hash_vectors.json");
    FString Text;
    if (!FFileHelper::LoadFileToString(Text, *VectorsPath))
    {
        UE_LOG(LogTemp, Error, TEXT("UppercutCanonVectors: cannot read %s"), *VectorsPath);
        return 1;
    }

    TSharedPtr<FJsonObject> Root;
    const TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(Text);
    if (!FJsonSerializer::Deserialize(Reader, Root) || !Root.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("UppercutCanonVectors: vectors file is not JSON"));
        return 1;
    }

    FString Report;
    int32 Checked = 0, Failed = 0;

    Report += FString::Printf(TEXT("canonicalizer=%s\nhash_contract=%s\n"),
                              UppercutCanonicalizerVersion, UppercutHashContractVersion);

    const FString DeclaredContract = Root->GetStringField(TEXT("canonicalizer_contract"));
    if (DeclaredContract != UppercutCanonicalizerVersion)
    {
        Report += FString::Printf(TEXT("FAIL contract: vectors say %s, build is %s\n"),
                                  *DeclaredContract, UppercutCanonicalizerVersion);
        ++Failed;
    }

    // ---- accept vectors ---------------------------------------------------
    const TArray<TSharedPtr<FJsonValue>>* Vectors = nullptr;
    if (Root->TryGetArrayField(TEXT("vectors"), Vectors))
    {
        for (const TSharedPtr<FJsonValue>& V : *Vectors)
        {
            const TSharedPtr<FJsonObject> Obj = V->AsObject();
            const FString Name = Obj->GetStringField(TEXT("name"));
            const FString Input = Obj->GetStringField(TEXT("input_json"));
            const FString Schema = Obj->GetStringField(TEXT("schema_identity"));
            const FString PolicyId = Obj->GetStringField(TEXT("policy_identity"));
            const FString RoleSetId = Obj->GetStringField(TEXT("role_set_identity"));
            const FString WantRaw = Obj->GetStringField(TEXT("raw_sha256"));
            const FString WantSem = Obj->GetStringField(TEXT("semantic_sha256"));
            const FString WantHex = Obj->GetStringField(TEXT("canonical_hex"));

            TArray<FString> Patterns;
            const TArray<TSharedPtr<FJsonValue>>* Pats = nullptr;
            if (Obj->TryGetArrayField(TEXT("patterns"), Pats))
            {
                for (const TSharedPtr<FJsonValue>& P : *Pats) { Patterns.Add(P->AsString()); }
            }

            FString GotRaw, GotSem, Error;
            ++Checked;

            // Decision 0024: canonical BYTES first. A hash mismatch says two
            // encoders disagree; the bytes say where, and that is the
            // difference between a lead and a shrug.
            TArray<uint8> GotBytes;
            if (!UppercutCanonicalBytes(Input, Patterns, GotBytes, Error))
            {
                Report += FString::Printf(TEXT("FAIL %-26s refused: %s\n"), *Name, *Error);
                ++Failed;
                continue;
            }
            FString GotHex;
            for (uint8 B : GotBytes) { GotHex += FString::Printf(TEXT("%02x"), B); }
            if (GotHex != WantHex)
            {
                int32 At = 0;
                while (At < GotHex.Len() && At < WantHex.Len()
                       && GotHex[At] == WantHex[At]) { ++At; }
                Report += FString::Printf(
                    TEXT("FAIL %-26s canonical bytes differ at hex offset %d\n")
                    TEXT("  py  %s\n  cpp %s\n"),
                    *Name, At, *WantHex, *GotHex);
                ++Failed;
                continue;
            }

            if (!UppercutCanonHashes(Input, Patterns, Schema, PolicyId, RoleSetId,
                                     GotRaw, GotSem, Error))
            {
                Report += FString::Printf(TEXT("FAIL %-26s refused: %s\n"), *Name, *Error);
                ++Failed;
                continue;
            }
            if (GotRaw != WantRaw)
            {
                Report += FString::Printf(TEXT("FAIL %-24s raw\n  py  %s\n  cpp %s\n"),
                                          *Name, *WantRaw, *GotRaw);
                ++Failed;
                continue;
            }
            if (GotSem != WantSem)
            {
                Report += FString::Printf(TEXT("FAIL %-24s semantic\n  py  %s\n  cpp %s\n"),
                                          *Name, *WantSem, *GotSem);
                ++Failed;
                continue;
            }
            Report += FString::Printf(TEXT("OK   %-24s %s\n"), *Name, *GotSem);
        }
    }

    // ---- rejection vectors ------------------------------------------------
    const TArray<TSharedPtr<FJsonValue>>* Rejects = nullptr;
    if (Root->TryGetArrayField(TEXT("rejection_vectors"), Rejects))
    {
        for (const TSharedPtr<FJsonValue>& V : *Rejects)
        {
            const TSharedPtr<FJsonObject> Obj = V->AsObject();
            const FString Name = Obj->GetStringField(TEXT("name"));
            const FString Input = Obj->GetStringField(TEXT("input_json"));
            const FString Schema = Obj->GetStringField(TEXT("schema_identity"));

            TArray<FString> Patterns;
            const TArray<TSharedPtr<FJsonValue>>* Pats = nullptr;
            if (Obj->TryGetArrayField(TEXT("patterns"), Pats))
            {
                for (const TSharedPtr<FJsonValue>& P : *Pats) { Patterns.Add(P->AsString()); }
            }

            FString GotRaw, GotSem, Error;
            ++Checked;
            const bool bAccepted = UppercutCanonHashes(Input, Patterns, Schema,
                                                       TEXT(""), TEXT(""),
                                                       GotRaw, GotSem, Error);
            if (bAccepted)
            {
                Report += FString::Printf(
                    TEXT("FAIL %-24s was ACCEPTED and should have been refused\n"), *Name);
                ++Failed;
            }
            else
            {
                Report += FString::Printf(TEXT("OK   %-24s refused: %s\n"), *Name, *Error);
            }
        }
    }

    // ---- the real manifest ------------------------------------------------
    FString ManifestText;
    if (FFileHelper::LoadFileToString(ManifestText, *(Repo / TEXT("data/hash_roles.json"))))
    {
        FString Identity, Version, Error;
        ++Checked;
        if (UppercutCanonManifestIdentity(ManifestText, Identity, Version, Error))
        {
            Report += FString::Printf(TEXT("POLICY %s %s\n"), *Version, *Identity);

            // Decision 0024 required proof 8: the PER-FILE role sets must agree
            // too. A global policy that matched while the per-file scopes
            // diverged would be the worst of both - parity claimed, dependency
            // graph different.
            TSharedPtr<FJsonObject> ManRoot;
            const TSharedRef<TJsonReader<>> MR = TJsonReaderFactory<>::Create(ManifestText);
            if (FJsonSerializer::Deserialize(MR, ManRoot) && ManRoot.IsValid())
            {
                const TSharedPtr<FJsonObject>* FilesObj = nullptr;
                if (ManRoot->TryGetObjectField(TEXT("files"), FilesObj))
                {
                    TArray<FString> Rels;
                    for (const TPair<FString, TSharedPtr<FJsonValue>>& KV
                         : (*FilesObj)->Values)
                    {
                        Rels.Add(KV.Key);
                    }
                    Rels.Sort();
                    for (const FString& Rel : Rels)
                    {
                        TArray<FString> Patterns;
                        const TArray<TSharedPtr<FJsonValue>>* Arr = nullptr;
                        if ((*FilesObj)->GetObjectField(Rel)->TryGetArrayField(
                                TEXT("non_authoritative"), Arr))
                        {
                            for (const TSharedPtr<FJsonValue>& P : *Arr)
                            {
                                Patterns.Add(P->AsString());
                            }
                        }
                        FString RoleSetId;
                        ++Checked;
                        if (UppercutCanonRoleSetIdentity(Identity, Rel, Patterns,
                                                         true, RoleSetId))
                        {
                            Report += FString::Printf(TEXT("ROLESET %s %s\n"),
                                                      *Rel, *RoleSetId);
                        }
                        else
                        {
                            Report += FString::Printf(
                                TEXT("FAIL roleset %s\n"), *Rel);
                            ++Failed;
                        }
                    }
                }
            }
        }
        else
        {
            Report += FString::Printf(TEXT("FAIL manifest identity: %s\n"), *Error);
            ++Failed;
        }
    }

    Report += FString::Printf(TEXT("SUMMARY checked=%d failed=%d\n"), Checked, Failed);

    IFileManager::Get().MakeDirectory(*FPaths::GetPath(OutPath), true);
    FFileHelper::SaveStringToFile(Report, *OutPath,
                                  FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);
    UE_LOG(LogTemp, Display, TEXT("UppercutCanonVectors: checked=%d failed=%d"),
           Checked, Failed);
    return Failed == 0 ? 0 : 1;
}
// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 03:40 UTC | END ]
