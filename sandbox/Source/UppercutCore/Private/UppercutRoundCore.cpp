// [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 02:53 UTC | START ]
#include "UppercutRoundCore.h"

#include "Dom/JsonObject.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"

namespace
{
    int64 QFromFloat(double V)
    {
        return (int64)FMath::RoundToDouble(V * 10000.0);
    }

    bool LoadJson(const FString& Path, TSharedPtr<FJsonObject>& Out, FString& Err)
    {
        FString Text;
        if (!FFileHelper::LoadFileToString(Text, *Path))
        {
            Err = FString::Printf(TEXT("cannot read %s"), *Path);
            return false;
        }
        const TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(Text);
        if (!FJsonSerializer::Deserialize(Reader, Out) || !Out.IsValid())
        {
            Err = FString::Printf(TEXT("bad json %s"), *Path);
            return false;
        }
        return true;
    }
}

void FUppercutRoundState::Reset(int32 InBudget)
{
    Phase = EUppercutRoundPhase::Boxing;
    Result = EUppercutRoundResult::None;
    Tick = 0;
    TickBudget = InBudget;
    DownedFighter = -1;
    CountNumber = 0;
    CountTicksLeft = 0;
    KdRound[0] = KdRound[1] = 0;
    KdBout[0] = KdBout[1] = 0;
    Landed[0] = Landed[1] = 0;
    Card[0] = Card[1] = 0;
    // [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-16 00:50 UTC |
    //   edit: reset means the cards are open again ]
    bCardsSealed = false;
    Winner = -1;
    Method.Reset();
}

void FUppercutRoundState::WitnessLanding(int32 Scorer)
{
    if (Scorer == 0 || Scorer == 1) { ++Landed[Scorer]; }
}

bool FUppercutRoundState::TryKnockdown(int32 Defender, int64 PressureQ,
                                       int64 ThresholdQ,
                                       TArray<FString>* OutRows)
{
    if (Phase != EUppercutRoundPhase::Boxing) { return false; }
    if (Defender != 0 && Defender != 1) { return false; }
    if (PressureQ < ThresholdQ) { return false; }

    ++KdRound[Defender];
    ++KdBout[Defender];
    DownedFighter = Defender;
    CountNumber = 0;
    CountTicksLeft = 0;
    Phase = EUppercutRoundPhase::Counting;
    if (OutRows)
    {
        OutRows->Add(FString::Printf(
            TEXT("K|%d|%d|pressure=%lld|threshold=%lld|round_kd=%d|bout_kd=%d\n"),
            Tick, Defender, (long long)PressureQ, (long long)ThresholdQ,
            KdRound[Defender], KdBout[Defender]));
    }
    return true;
}

void FUppercutRoundState::TickCount(TArray<FString>* OutRows)
{
    if (Phase != EUppercutRoundPhase::Counting) { return; }
    // Default: mandatory eight at 60 ticks per number (canon).
    const int32 PerNumber = 60;
    const int32 Mandatory = 8;
    if (CountTicksLeft <= 0)
    {
        ++CountNumber;
        CountTicksLeft = PerNumber;
        if (OutRows)
        {
            OutRows->Add(FString::Printf(
                TEXT("N|%d|count|%d|fighter=%d\n"), Tick, CountNumber, DownedFighter));
        }
    }
    --CountTicksLeft;
    if (CountNumber >= Mandatory && CountTicksLeft <= 0)
    {
        // Rise after the mandatory eight (Python integrated always rises
        // unless count_to is reached without rise - for 1-round MVP we rise).
        if (OutRows)
        {
            OutRows->Add(FString::Printf(
                TEXT("N|%d|rise|fighter=%d\n"), Tick, DownedFighter));
        }
        DownedFighter = -1;
        CountNumber = 0;
        Phase = EUppercutRoundPhase::Boxing;
    }
}

void FUppercutRoundState::SealDecision(TArray<FString>* OutRows)
{
    if (Phase == EUppercutRoundPhase::Finished) { return; }
    // 10-point must: more landings win the round; each KD suffered costs a point.
    int32 Score[2] = {10, 10};
    if (Landed[0] > Landed[1]) { Score[1] = 9; }
    else if (Landed[1] > Landed[0]) { Score[0] = 9; }
    // [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-16 00:50 UTC |
    //   START edit: an even round is 10-10 ]
    // The 10-point MUST system: somebody must get 10 unless a knockdown takes
    // it away. The old branch scored a drawn round 9-9, which no judge has
    // ever turned in, and it silently repriced what a knockdown costs on an
    // even round. Untaken in every pinned fight (all end 10-9 on landings),
    // which the byte-identical reproof of the pins confirms.
    // [ ... | 2026-08-16 00:50 UTC | END edit ]
    Score[0] = FMath::Max(0, Score[0] - KdRound[0]);
    Score[1] = FMath::Max(0, Score[1] - KdRound[1]);
    Card[0] = Score[0];
    Card[1] = Score[1];
    // [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-16 00:50 UTC |
    //   edit: sealing is what sets the seal ]
    bCardsSealed = true;
    if (Card[0] > Card[1]) { Winner = 0; }
    else if (Card[1] > Card[0]) { Winner = 1; }
    else { Winner = -1; }
    Result = EUppercutRoundResult::Decision;
    Method = TEXT("decision");
    Phase = EUppercutRoundPhase::Finished;
    if (OutRows)
    {
        OutRows->Add(FString::Printf(
            TEXT("V|decision|%d|%d|%d|%d|%d\n"),
            Winner, Card[0], Card[1], KdRound[0], KdRound[1]));
    }
}

bool UppercutLoadRoundCanon(const FString& RepoDir, const FString& RulesetId,
                            FUppercutRoundCanon& Out, FString& OutError)
{
    Out = FUppercutRoundCanon();
    TSharedPtr<FJsonObject> Cond;
    if (!LoadJson(RepoDir / TEXT("data/condition_model.json"), Cond, OutError))
    {
        return false;
    }
    const TSharedPtr<FJsonObject>* Kd = nullptr;
    if (Cond->TryGetObjectField(TEXT("knockdown"), Kd) && Kd)
    {
        double Th = 0.57;
        (*Kd)->TryGetNumberField(TEXT("pressure_threshold"), Th);
        Out.PressureThresholdQ = QFromFloat(Th);
        double Ctn = 60.0;
        (*Kd)->TryGetNumberField(TEXT("count_ticks_per_number"), Ctn);
        Out.CountTicksPerNumber = (int32)Ctn;
        (*Kd)->TryGetBoolField(TEXT("mandatory_eight_count"), Out.bMandatoryEight);
    }

    TSharedPtr<FJsonObject> Rules;
    const FString RulesPath = RepoDir / TEXT("data/rulesets")
        / (RulesetId + TEXT(".json"));
    if (!LoadJson(RulesPath, Rules, OutError))
    {
        return false;
    }
    // Professional: knockdown stoppage fields are null => no auto-stop.
    bool bThree = false;
    Rules->TryGetBoolField(TEXT("three_knockdown_rule"), bThree);
    if (bThree)
    {
        Out.bHasRoundKdLimit = true;
        Out.RoundKdLimit = 3;
    }
    double PerRound = 0, PerBout = 0;
    if (Rules->TryGetNumberField(TEXT("knockdowns_per_round_stoppage"), PerRound))
    {
        Out.bHasRoundKdLimit = true;
        Out.RoundKdLimit = (int32)PerRound;
    }
    if (Rules->TryGetNumberField(TEXT("knockdowns_per_bout_stoppage"), PerBout))
    {
        Out.bHasBoutKdLimit = true;
        Out.BoutKdLimit = (int32)PerBout;
    }
    return true;
}
// [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 02:53 UTC | END ]
