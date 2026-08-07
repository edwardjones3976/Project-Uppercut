// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 07:20 UTC | START ]
#include "UppercutStaminaVectorsCommandlet.h"

#include "Dom/JsonObject.h"
#include "HAL/FileManager.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"
#include "UppercutRangeCore.h"   // UppercutFloorDiv
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

    // Decision 0025 proof 8: what the tick REQUESTED, carried per checkpoint.
    struct FTel
    {
        int64 Load = 0;        // the move's declared reserve_load
        int64 Exertion = 0;    // sustained exertion, charged separately
        int64 Requested = 0;   // load + exertion
        int64 Applied = 0;     // what the balance could absorb
        int64 Unpaid = 0;
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
            TMap<int64, FTel> TelMarks;
            const TArray<TSharedPtr<FJsonValue>>* CPs = nullptr;
            if (Obj->TryGetArrayField(TEXT("checkpoints"), CPs))
            {
                for (const TSharedPtr<FJsonValue>& PV : *CPs)
                {
                    const TSharedPtr<FJsonObject> P = PV->AsObject();
                    const int64 At = (int64)P->GetNumberField(TEXT("tick"));
                    Marks.Add(At, TPair<int64, int64>(
                                  (int64)P->GetNumberField(TEXT("wind")),
                                  (int64)P->GetNumberField(TEXT("reserve"))));

                    const TSharedPtr<FJsonObject>* T = nullptr;
                    if (P->TryGetObjectField(TEXT("telemetry"), T))
                    {
                        FTel Tel;
                        Tel.Load = (int64)(*T)->GetNumberField(
                            TEXT("requested_reserve_load"));
                        Tel.Exertion = (int64)(*T)->GetNumberField(
                            TEXT("sustained_exertion"));
                        Tel.Requested = (int64)(*T)->GetNumberField(
                            TEXT("requested_reserve_total"));
                        Tel.Applied = (int64)(*T)->GetNumberField(
                            TEXT("reserve_applied"));
                        Tel.Unpaid = (int64)(*T)->GetNumberField(
                            TEXT("reserve_unpaid"));
                        TelMarks.Add(At, Tel);
                    }
                }
            }

            // Decision 0025 proofs 3, 4 and 5 are checked at EVERY tick of
            // EVERY case, not by one vector each. A floor that holds in the
            // single scenario written to test it, and is never looked at again
            // across 10800 ticks of the others, is not a floor.
            const int64 CeilingFloorValue =
                UppercutFloorDiv(Canon.WindMax * Canon.CeilingFloor, 10000);

            int64 Tick = 0;
            int32 Diverged = 0;
            FString FirstDivergence;
            for (const FLine& L : Script)
            {
                for (int32 r = 0; r < L.Repeat; ++r)
                {
                    FString StepError;
                    FUppercutStepTelemetry Tel;
                    if (!St.Step(Canon, L.Action, L.Move, L.Disp, StepError, &Tel))
                    {
                        FirstDivergence = FString::Printf(
                            TEXT("  tick %lld refused: %s\n"), Tick + 1, *StepError);
                        Diverged = 1;
                        break;
                    }
                    ++Tick;

                    if (St.Reserve < 0 || St.Reserve > Canon.ReserveMax)
                    {
                        if (Diverged == 0)
                        {
                            FirstDivergence = FString::Printf(
                                TEXT("  D0025 proof 3 BROKEN at tick %lld: ")
                                TEXT("stored Reserve is %lld, outside [0, %lld]\n"),
                                Tick, St.Reserve, Canon.ReserveMax);
                        }
                        ++Diverged;
                    }
                    const int64 Base = Canon.Recover[(int32)L.Action];
                    if (Base != 0)
                    {
                        const int64 Rate = Canon.RecoveryRate(L.Action, St.Reserve);
                        const int64 FloorRate =
                            UppercutFloorDiv(Base * Canon.RecoveryFloor, 10000);
                        if (Rate < FloorRate)
                        {
                            if (Diverged == 0)
                            {
                                FirstDivergence = FString::Printf(
                                    TEXT("  D0025 proof 4 BROKEN at tick %lld: ")
                                    TEXT("recovery %lld is below the declared ")
                                    TEXT("floor %lld\n"), Tick, Rate, FloorRate);
                            }
                            ++Diverged;
                        }
                    }
                    if (Canon.WindCeiling(St.Reserve) < CeilingFloorValue)
                    {
                        if (Diverged == 0)
                        {
                            FirstDivergence = FString::Printf(
                                TEXT("  D0025 proof 5 BROKEN at tick %lld: ")
                                TEXT("Wind ceiling %lld is below the declared ")
                                TEXT("floor %lld\n"), Tick,
                                Canon.WindCeiling(St.Reserve), CeilingFloorValue);
                        }
                        ++Diverged;
                    }

                    const FTel* WantTel = TelMarks.Find(Tick);
                    if (WantTel && (WantTel->Requested != Tel.RequestedReserveTotal
                                    || WantTel->Applied != Tel.ReserveApplied
                                    || WantTel->Unpaid != Tel.ReserveUnpaid
                                    || WantTel->Load != Tel.RequestedReserveLoad
                                    || WantTel->Exertion != Tel.SustainedExertion))
                    {
                        if (Diverged == 0)
                        {
                            // Proof 8. This is the number that would silently
                            // report a 2.0-load punch as having cost 0.5.
                            FirstDivergence = FString::Printf(
                                TEXT("  D0025 proof 8 at tick %lld: requested ")
                                TEXT("py=%lld cpp=%lld, applied py=%lld cpp=%lld, ")
                                TEXT("unpaid py=%lld cpp=%lld\n"),
                                Tick, WantTel->Requested, Tel.RequestedReserveTotal,
                                WantTel->Applied, Tel.ReserveApplied,
                                WantTel->Unpaid, Tel.ReserveUnpaid);
                        }
                        ++Diverged;
                    }

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
            if (bBetween)
            {
                FString CornerError;
                if (!St.BetweenRounds(Canon, CornerError))
                {
                    if (Diverged == 0)
                    {
                        FirstDivergence = FString::Printf(
                            TEXT("  the corner refused: %s\n"), *CornerError);
                    }
                    ++Diverged;
                }
                else if (St.Reserve > Canon.ReserveMax)
                {
                    // Decision 0025 proof 7.
                    if (Diverged == 0)
                    {
                        FirstDivergence = FString::Printf(
                            TEXT("  D0025 proof 7 BROKEN: the corner left ")
                            TEXT("Reserve at %lld against a maximum of %lld\n"),
                            St.Reserve, Canon.ReserveMax);
                    }
                    ++Diverged;
                }
            }

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

    // ---- Decision 0025 proof 6: refusals --------------------------------
    //
    // Refusals are evidence in their own right, and they are the easiest thing
    // to skip: a C++ side that merely fails to crash looks like agreement.
    // What protects the model is that both implementations say no to the same
    // states. A save, replay or fixture carrying an out-of-interval Reserve
    // must not be silently normalised into a plausible fighter.
    const TArray<TSharedPtr<FJsonValue>>* Rejects = nullptr;
    if (Root->TryGetArrayField(TEXT("rejection_cases"), Rejects))
    {
        for (const TSharedPtr<FJsonValue>& RV : *Rejects)
        {
            const TSharedPtr<FJsonObject> R = RV->AsObject();
            const FString Name = R->GetStringField(TEXT("name"));
            FUppercutStamina St;
            St.Wind = (int64)R->GetNumberField(TEXT("wind"));
            St.Reserve = (int64)R->GetNumberField(TEXT("reserve"));

            ++Checked;
            FString StepError, CornerError;
            const bool bStepped = St.Step(Canon, EUppercutAction::Rest,
                                          FString(), 0, StepError);
            FUppercutStamina St2;
            St2.Wind = (int64)R->GetNumberField(TEXT("wind"));
            St2.Reserve = (int64)R->GetNumberField(TEXT("reserve"));
            const bool bCornered = St2.BetweenRounds(Canon, CornerError);

            if (bStepped || bCornered)
            {
                Report += FString::Printf(
                    TEXT("FAIL %-30s ACCEPTED invalid state (step=%s corner=%s) ")
                    TEXT("- Decision 0025 requires rejection, not silent ")
                    TEXT("normalisation\n"),
                    *Name, bStepped ? TEXT("accepted") : TEXT("refused"),
                    bCornered ? TEXT("accepted") : TEXT("refused"));
                ++Failed;
            }
            else
            {
                Report += FString::Printf(TEXT("OK   %-30s refused: %s\n"),
                                          *Name, *StepError);
            }
        }
    }
    else
    {
        Report += TEXT("FAIL the fixture carries no rejection_cases - ")
                  TEXT("Decision 0025 proof 6 would go unchecked\n");
        ++Failed;
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
