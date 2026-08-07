// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 19:55 UTC | START ]
#include "UppercutCoreEvadeCommandlet.h"

#include "HAL/FileManager.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "UppercutEvadeCore.h"
#include "UppercutCanonHash.h"

// NEITHER THE RULES, THE CANON READER, NOR THE LOOP LIVE HERE ANY MORE.
//
// They are in UppercutEvadeCore / UppercutEvadeCanonLoader / UppercutEvadeSession
// so a live runtime advances the same object this marker stream is proven
// against. What is left here is the part a runtime does not want: parse
// arguments, write a header, run to a fixed tick count, hash the rows, save.

namespace
{
    const uint64 FnvOffset = 14695981039346656037ull;
    const uint64 FnvPrime = 1099511628211ull;

    FString Join(const TArray<FString>& Xs)
    {
        if (Xs.Num() == 0) { return TEXT("-"); }
        FString Out;
        for (int32 i = 0; i < Xs.Num(); ++i)
        {
            if (i) { Out += TEXT(","); }
            Out += Xs[i];
        }
        return Out;
    }
}

int32 UUppercutCoreEvadeCommandlet::Main(const FString& Params)
{
    uint32 Seed = 0; int32 Ticks = 0; FString Repo, OutPath;
    FParse::Value(*Params, TEXT("seed="), Seed);
    FParse::Value(*Params, TEXT("ticks="), Ticks);
    FParse::Value(*Params, TEXT("repo="), Repo);
    FParse::Value(*Params, TEXT("out="), OutPath);
    if (Ticks <= 0 || Repo.IsEmpty() || OutPath.IsEmpty())
    {
        UE_LOG(LogTemp, Error, TEXT("UppercutCoreEvade: need -seed= -ticks= -repo= -out="));
        return 1;
    }

    FUppercutEvadeCanon C;
    TArray<FUppercutCanonSource> Sources;
    FString Error;
    if (!UppercutLoadEvadeCanon(Repo, C, Sources, Error))
    {
        UE_LOG(LogTemp, Error, TEXT("UppercutCoreEvade: %s"), *Error);
        return 1;
    }

    // ---- the header: canon before any tick --------------------------------
    FString Out;
    Out += TEXT("H|phase=R\n");

    // Decision 0023: dual identities, from the shared builder. Migrated
    // 2026-08-07 with no authoritative row moved.
    TArray<TPair<FString, FString>> Entries;
    for (const FUppercutCanonSource& Src : Sources)
    {
        Entries.Add(TPair<FString, FString>(Src.Label, Src.RelPath));
    }
    TArray<FString> HeaderLines;
    if (!UppercutCanonHeaderLines(Repo, Entries, HeaderLines, Error))
    {
        UE_LOG(LogTemp, Error, TEXT("UppercutCoreEvade: header: %s"), *Error);
        return 1;
    }
    for (const FString& L : HeaderLines) { Out += L + TEXT("\n"); }

    Out += FString::Printf(TEXT("H|seed=%u\nH|ticks=%d\n"), Seed, Ticks);
    TArray<FString> EvIds;
    C.Evasions.GetKeys(EvIds);
    EvIds.Sort();
    for (const FString& Id : EvIds)
    {
        const FUppercutEvasion& E = C.Evasions[Id];
        Out += FString::Printf(TEXT("Y|%s|%s|%d|%d|%s|%s\n"), *Id, *E.Kind,
                               E.Startup, E.Active, *Join(E.Vacates),
                               *Join(E.BeatenBy));
    }
    for (int32 i = 0; i < 6; ++i)
    {
        const FUppercutEvadePunch& P = C.Punches[UppercutEvadePunchId(i)];
        Out += FString::Printf(TEXT("M|%s|%s|%s|%d|%d\n"), *P.Id,
                               P.Category.IsEmpty() ? TEXT("-") : *P.Category,
                               P.Region.IsEmpty() ? TEXT("-") : *P.Region,
                               P.Startup, P.Active);
    }
    Out += FString::Printf(TEXT("K|outranks_guard=%d|mistime_ticks=%d\n"),
                           C.bOutranksGuard ? 1 : 0, C.MistimeTicks);

    // ---- the session drives itself; this file only writes rows ------------
    FUppercutEvadeSession S;
    S.Reset(C, Seed);

    uint64 Fnv = FnvOffset;
    int64 Rows = 0;
    TArray<FString> Emitted;
    auto Absorb = [&]()
    {
        for (const FString& RowText : Emitted)
        {
            Out += RowText;
            const FTCHARToUTF8 Utf8(*RowText);
            const uint8* P = (const uint8*)Utf8.Get();
            for (int32 b = 0; b < Utf8.Length(); ++b) { Fnv = (Fnv ^ P[b]) * FnvPrime; }
            ++Rows;
        }
        Emitted.Reset();
    };

    for (int32 T = 1; T <= Ticks; ++T)
    {
        S.Step(&Emitted);
        Absorb();
    }

    // ---- the properties, inside the hash ----------------------------------
    auto EmitOne = [&](const FString& RowText)
    {
        Emitted.Add(RowText);
        Absorb();
    };
    EmitOne(FString::Printf(TEXT("V|a_body_shot_beats_the_slip|%d\n"),
                            C.BodyShotBeatsTheSlip() ? 1 : 0));
    EmitOne(FString::Printf(TEXT("V|the_uppercut_beats_the_roll|%d\n"),
                            C.UppercutBeatsTheRoll() ? 1 : 0));
    EmitOne(FString::Printf(TEXT("V|the_slip_evades_a_straight|%d\n"),
                            C.SlipEvadesAStraight() ? 1 : 0));
    EmitOne(FString::Printf(TEXT("V|no_evasion_is_strictly_better|%d\n"),
                            C.NoEvasionIsStrictlyBetter() ? 1 : 0));
    EmitOne(FString::Printf(TEXT("V|canon_errors|%d\n"), C.CanonErrors()));

    Out += FString::Printf(
        TEXT("S|rows=%lld|commits=%lld|punches=%lld|evasions=%lld|waits=%lld")
        TEXT("|arrived=%lld|dodged=%lld|countered=%lld|wrong_region=%lld")
        TEXT("|clear=%lld|fnv1a64=%016llx\n"),
        Rows, S.Commits, S.Punches, S.Evasions, S.Waits, S.Arrived, S.Dodged,
        S.Countered, S.WrongRegion, S.Clear, Fnv);

    IFileManager::Get().MakeDirectory(*FPaths::GetPath(OutPath), true);
    if (!FFileHelper::SaveStringToFile(Out, *OutPath,
            FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM))
    {
        UE_LOG(LogTemp, Error, TEXT("UppercutCoreEvade: cannot write %s"), *OutPath);
        return 1;
    }
    UE_LOG(LogTemp, Display, TEXT("UppercutCoreEvade: %lld rows, fnv1a64=%016llx"),
           Rows, Fnv);
    return 0;
}
// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 19:55 UTC | END ]
