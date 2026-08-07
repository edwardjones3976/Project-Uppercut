// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 07:20 UTC | START ]
#include "UppercutStaminaVectorsCommandlet.h"

#include "Dom/JsonObject.h"
#include "HAL/FileManager.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"
#include "UppercutStaminaCore.h"

// The SCENARIOS LIVE IN THE FIXTURE. This file replays a script it is handed;
// it does not re-declare what "a professional round" or "the corner" means.
// Two copies of a scenario is the same defect as two copies of a rule - they
// agree until one is edited, and the edit that matters is the one nobody
// mirrors.
//
// The vectors FILE is ordinary tooling data, so Unreal's JSON reader is fine
// for it. Canon documents are a different matter and go through the strict
// reader elsewhere.

namespace
{
    struct FLine
    {
        int32 Repeat = 0;
        EUppercutAction Action = EUppercutAction::Observe;
        FString Move;
        int64 Disp = 0;
    };

    // The fixture's canon block against the canon the runtime actually loaded.
    // This is the Q() parity check: Python rounds half to even and
    // FMath::RoundToDouble rounds half away from zero, so two loaders can read
    // one authored decimal into two different integers and every trajectory
    // after that is honestly computed from the wrong number.
    void CheckCanon(const TSharedPtr<FJsonObject>& Want,
                    const FUppercutStaminaCanon& Got,
                    FString& Report, int32& Checked, int32& Failed)
    {
        struct FPair { const TCHAR* Key; int64 Value; };
        const FPair Pairs[] = {
            { TEXT("wind_max"), Got.WindMax },
            { TEXT("wind_low"), Got.WindLow },
            { TEXT("wind_exhausted"), Got.WindExhausted },
            { TEXT("wind_start"), Got.WindStart },
            { TEXT("reserve_start"), Got.ReserveStart },
            { TEXT("reserve_max"), Got.ReserveMax },
            { TEXT("sustained_exertion"), Got.SustainedExertion },
            { TEXT("wind_per_ru"), Got.WindPerRu },
            { TEXT("reserve_per_ru"), Got.ReservePerRu },
            { TEXT("wind_between_rounds"), Got.WindBetweenRounds },
            { TEXT("reserve_between_rounds"), Got.ReserveBetweenRounds },
            { TEXT("ceiling_floor"), Got.CeilingFloor },
            { TEXT("ceiling_span"), Got.CeilingSpan },
            { TEXT("recovery_floor"), Got.RecoveryFloor },
            { TEXT("recovery_span"), Got.RecoverySpan },
        };
        for (const FPair& P : Pairs)
        {
            double W = 0.0;
            ++Checked;
            if (!Want->TryGetNumberField(P.Key, W))
            {
                Report += FString::Printf(
                    TEXT("FAIL canon %s absent from the fixture\n"), P.Key);
                ++Failed;
                continue;
            }
            const int64 Wanted = (int64)W;
            if (Wanted != P.Value)
            {
                Report += FString::Printf(
                    TEXT("FAIL canon %-24s py=%lld cpp=%lld\n"),
                    P.Key, Wanted, P.Value);
                ++Failed;
            }
        }
    }
}

int32 UUppercutStaminaVectorsCommandlet::Main(const FString& Params)
{
    FString Repo, OutPath;
    FParse::Value(*Params, TEXT("repo="), Repo);
    FParse::Value(*Params, TEXT("out="), OutPath);
    if (Repo.IsEmpty() || OutPath.IsEmpty())
    {
        UE_LOG(LogTemp, Error, TEXT("UppercutStaminaVectors: need -repo= -out="));
        return 1;
    }

    FString Report, LoadError;
    int32 Checked = 0, Failed = 0;

    FUppercutStaminaCanon Canon;
    if (!UppercutLoadStaminaCanon(Repo, Canon, LoadError))
    {
        UE_LOG(LogTemp, Error, TEXT("UppercutStaminaVectors: %s"), *LoadError);
        return 1;
    }

    // Canon the economy itself calls impossible must stop the run. A parity
    // report generated from broken canon does not report the breakage; it
    // launders it, by proving two implementations agree about nonsense.
    TArray<FString> CanonErrs;
    ++Checked;
    if (Canon.CanonErrors(&CanonErrs) != 0)
    {
        for (const FString& E : CanonErrs)
        {
            Report += FString::Printf(TEXT("FAIL canon contract: %s\n"), *E);
        }
        Failed += CanonErrs.Num();
    }

    const FString VectorsPath = Repo / TEXT("tests/fixtures/stamina_vectors.json");
    FString Text;
    if (!FFileHelper::LoadFileToString(Text, *VectorsPath))
    {
        UE_LOG(LogTemp, Error, TEXT("UppercutStaminaVectors: cannot read %s"),
               *VectorsPath);
        return 1;
    }

    TSharedPtr<FJsonObject> Root;
    const TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(Text);
    if (!FJsonSerializer::Deserialize(Reader, Root) || !Root.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("UppercutStaminaVectors: fixture is not JSON"));
        return 1;
    }

    const TSharedPtr<FJsonObject>* WantCanon = nullptr;
    if (Root->TryGetObjectField(TEXT("canon"), WantCanon))
    {
        CheckCanon(*WantCanon, Canon, Report, Checked, Failed);
    }
    else
    {
        Report += TEXT("FAIL the fixture carries no canon block\n");
        ++Failed;
    }

    // ---- the trajectories -------------------------------------------------
    const TArray<TSharedPtr<FJsonValue>>* Cases = nullptr;
    if (Root->TryGetArrayField(TEXT("cases"), Cases))
    {
        for (const TSharedPtr<FJsonValue>& CV : *Cases)
        {
            const TSharedPtr<FJsonObject> Obj = CV->AsObject();
            const FString Name = Obj->GetStringField(TEXT("name"));

            TArray<FLine> Script;
            bool bBadScript = false;
            const TArray<TSharedPtr<FJsonValue>>* Steps = nullptr;
            if (Obj->TryGetArrayField(TEXT("script"), Steps))
            {
                for (const TSharedPtr<FJsonValue>& SV : *Steps)
                {
                    const TSharedPtr<FJsonObject> S = SV->AsObject();
                    FLine L;
                    L.Repeat = (int32)S->GetNumberField(TEXT("repeat"));
                    const FString ActionName = S->GetStringField(TEXT("action"));
                    if (!UppercutActionFromName(ActionName, L.Action))
                    {
                        Report += FString::Printf(
                            TEXT("FAIL %-30s unknown action family '%s'\n"),
                            *Name, *ActionName);
                        bBadScript = true;
                        break;
                    }
                    // A null move means this tick commits nothing. It does NOT
                    // mean an unrecognised move is free - that distinction is
                    // the whole of the fail-closed rule.
                    S->TryGetStringField(TEXT("move"), L.Move);
                    L.Disp = (int64)S->GetNumberField(TEXT("disp"));
                    Script.Add(L);
                }
            }
            if (bBadScript) { ++Failed; ++Checked; continue; }

            FUppercutStamina St;
            St.Wind = (int64)Obj->GetNumberField(TEXT("start_wind"));
            St.Reserve = (int64)Obj->GetNumberField(TEXT("start_reserve"));

            // Checkpoints are 1-based ticks over the FLATTENED script, so a
            // checkpoint means the same tick in both languages however the
            // repeats happen to be grouped.
            TMap<int64, TPair<int64, int64>> Marks;
            const TArray<TSharedPtr<FJsonValue>>* CPs = nullptr;
            if (Obj->TryGetArrayField(TEXT("checkpoints"), CPs))
            {
                for (const TSharedPtr<FJsonValue>& PV : *CPs)
                {
                    const TSharedPtr<FJsonObject> P = PV->AsObject();
                    Marks.Add((int64)P->GetNumberField(TEXT("tick")),
                              TPair<int64, int64>(
                                  (int64)P->GetNumberField(TEXT("wind")),
                                  (int64)P->GetNumberField(TEXT("reserve"))));
                }
            }

            int64 Tick = 0;
            int32 Diverged = 0;
            FString FirstDivergence;
            for (const FLine& L : Script)
            {
                for (int32 r = 0; r < L.Repeat; ++r)
                {
                    FString StepError;
                    if (!St.Step(Canon, L.Action, L.Move, L.Disp, StepError))
                    {
                        FirstDivergence = FString::Printf(
                            TEXT("  tick %lld refused: %s\n"), Tick + 1, *StepError);
                        Diverged = 1;
                        break;
                    }
                    ++Tick;
                    const TPair<int64, int64>* Want = Marks.Find(Tick);
                    if (Want && (St.Wind != Want->Key || St.Reserve != Want->Value))
                    {
                        if (Diverged == 0)
                        {
                            // The FIRST divergence, not the last. A run that
                            // reports only its final numbers hides where the
                            // two implementations parted company, and the
                            // first tick that differs is the whole diagnosis.
                            FirstDivergence = FString::Printf(
                                TEXT("  first at tick %lld: ")
                                TEXT("py wind=%lld reserve=%lld / ")
                                TEXT("cpp wind=%lld reserve=%lld\n"),
                                Tick, Want->Key, Want->Value, St.Wind, St.Reserve);
                        }
                        ++Diverged;
                    }
                }
                if (Diverged && FirstDivergence.Contains(TEXT("refused"))) { break; }
            }

            bool bBetween = false;
            Obj->TryGetBoolField(TEXT("between_rounds_after"), bBetween);
            if (bBetween) { St.BetweenRounds(Canon); }

            const int64 WantWind = (int64)Obj->GetNumberField(TEXT("wind"));
            const int64 WantReserve = (int64)Obj->GetNumberField(TEXT("reserve"));
            ++Checked;
            if (Diverged || St.Wind != WantWind || St.Reserve != WantReserve)
            {
                Report += FString::Printf(
                    TEXT("FAIL %-30s ticks=%lld checkpoints_off=%d\n")
                    TEXT("  end: py wind=%lld reserve=%lld / cpp wind=%lld reserve=%lld\n%s"),
                    *Name, Tick, Diverged, WantWind, WantReserve,
                    St.Wind, St.Reserve, *FirstDivergence);
                ++Failed;
            }
            else
            {
                Report += FString::Printf(
                    TEXT("OK   %-30s ticks=%-6lld marks=%-2d wind=%-10lld reserve=%lld\n"),
                    *Name, Tick, Marks.Num(), St.Wind, St.Reserve);
            }
        }
    }

    // ---- fail closed ------------------------------------------------------
    // Decision 0024: "Unknown move IDs, action families, resource keys, or cost
    // sources fail closed. They never mean free." Proven here rather than
    // asserted, because the contract's first draft returned zero cost for an
    // unrecognised id and NOTHING failed - the model simply reported that
    // boxing is not tiring. A parity suite that only replays valid scripts
    // would have agreed with it perfectly.
    {
        FUppercutStamina St;
        St.Reset(Canon);
        const int64 BeforeWind = St.Wind, BeforeReserve = St.Reserve;
        FString StepError;
        ++Checked;
        // "attack" is a real ACTION FAMILY and not a move id. This is the exact
        // confusion that made every punch free.
        if (St.Step(Canon, EUppercutAction::Attack, TEXT("attack"), 0, StepError))
        {
            Report += TEXT("FAIL unknown move id 'attack' was ACCEPTED - an ")
                      TEXT("economy that charges nothing for what it does not ")
                      TEXT("recognise is not an economy\n");
            ++Failed;
        }
        else if (St.Wind != BeforeWind || St.Reserve != BeforeReserve)
        {
            Report += TEXT("FAIL a refused step still moved the state; a ")
                      TEXT("failure that half-applies is worse than one that ")
                      TEXT("does not fail\n");
            ++Failed;
        }
        else
        {
            Report += FString::Printf(TEXT("OK   %-30s refused: %s\n"),
                                      TEXT("unknown_move_fails_closed"), *StepError);
        }
    }

    // Case sensitivity, learned the hard way on 2026-08-07: FString comparison
    // AND FString map hashing are case-INSENSITIVE in Unreal. Python's dict is
    // not. So this is not a tidiness check - it is a place where the two
    // implementations disagree about what canon says, and it fails silently in
    // the direction of charging a price for a move canon never declared.
    {
        EUppercutAction Parsed = EUppercutAction::Observe;
        ++Checked;
        if (UppercutActionFromName(TEXT("Rest"), Parsed))
        {
            Report += TEXT("FAIL action family names matched case-insensitively\n");
            ++Failed;
        }
        else
        {
            Report += TEXT("OK   action_names_are_case_sensitive\n");
        }

        FUppercutStamina St;
        St.Reset(Canon);
        FString StepError;
        ++Checked;
        // TMap<FString,...>::Find WILL return jab_lead's entry for this key.
        // Only the stored spelling can refuse it.
        if (St.Step(Canon, EUppercutAction::Attack, TEXT("Jab_Lead"), 0, StepError))
        {
            Report += TEXT("FAIL 'Jab_Lead' collected jab_lead's price - the ")
                      TEXT("move table matched case-insensitively, so C++ and ")
                      TEXT("Python disagree about which ids canon declares\n");
            ++Failed;
        }
        else
        {
            Report += TEXT("OK   move_ids_are_case_sensitive\n");
        }
    }

    Report += FString::Printf(TEXT("SUMMARY checked=%d failed=%d\n"), Checked, Failed);

    IFileManager::Get().MakeDirectory(*FPaths::GetPath(OutPath), true);
    FFileHelper::SaveStringToFile(Report, *OutPath,
                                  FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);
    UE_LOG(LogTemp, Display, TEXT("UppercutStaminaVectors: checked=%d failed=%d"),
           Checked, Failed);
    return Failed == 0 ? 0 : 1;
}
// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 07:20 UTC | END ]
