// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 20:15 UTC | START ]
#include "UppercutCoreRangeCommandlet.h"

#include "HAL/FileManager.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "UppercutRangeCore.h"

// NOTHING THE RUNTIME COULD WANT LIVES HERE ANY MORE.
//
// The rules are in UppercutRangeCore, the canon reader in
// UppercutRangeCanonLoader, the loop in UppercutRangeCore, and the stream's
// shape in UppercutRangeStream. What is left is the part a runtime does not
// want: parse arguments, run to a fixed tick count, save a file.
//
// The refactor's safety net is the parity proof itself - the stream must stay
// byte-identical, which is a stronger statement about a refactor than a test
// suite can make.

int32 UUppercutCoreRangeCommandlet::Main(const FString& Params)
{
    uint32 Seed = 0; int32 Ticks = 0; FString Repo, OutPath;
    FParse::Value(*Params, TEXT("seed="), Seed);
    FParse::Value(*Params, TEXT("ticks="), Ticks);
    FParse::Value(*Params, TEXT("repo="), Repo);
    FParse::Value(*Params, TEXT("out="), OutPath);
    if (Ticks <= 0 || Repo.IsEmpty() || OutPath.IsEmpty())
    {
        UE_LOG(LogTemp, Error, TEXT("UppercutCoreRange: need -seed= -ticks= -repo= -out="));
        return 1;
    }

    // One reader, shared with the live subsystem. The hashes come back from the
    // same read that produced the canon, so the header names the bytes the
    // fight actually ran on rather than the bytes on disk a moment later.
    FUppercutRangeCanon C;
    TArray<FUppercutCanonSource> Sources;
    FString Error;
    if (!UppercutLoadRangeCanon(Repo, C, Sources, Error))
    {
        UE_LOG(LogTemp, Error, TEXT("UppercutCoreRange: %s"), *Error);
        return 1;
    }

    FString Out = UppercutRangeStreamHeader(C, Sources, Seed, Ticks);

    FUppercutRangeSession S;
    S.Reset(C, Seed);

    uint64 Fnv = UppercutFnv1a64Offset();
    int64 Rows = 0;
    TArray<FString> Emitted;
    auto Absorb = [&]()
    {
        for (const FString& RowText : Emitted)
        {
            Out += RowText;
            Fnv = UppercutFnv1a64(Fnv, RowText);
            ++Rows;
        }
        Emitted.Reset();
    };

    for (int32 T = 1; T <= Ticks; ++T)
    {
        S.Step(&Emitted);
        Absorb();
    }

    Emitted = UppercutRangePropertyRows(C);
    Absorb();

    Out += UppercutRangeStreamTrailer(S, Rows, Fnv);

    IFileManager::Get().MakeDirectory(*FPaths::GetPath(OutPath), true);
    if (!FFileHelper::SaveStringToFile(Out, *OutPath,
            FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM))
    {
        UE_LOG(LogTemp, Error, TEXT("UppercutCoreRange: cannot write %s"), *OutPath);
        return 1;
    }
    UE_LOG(LogTemp, Display, TEXT("UppercutCoreRange: %lld rows, fnv1a64=%016llx"), Rows, Fnv);
    return 0;
}
// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 20:15 UTC | END ]
