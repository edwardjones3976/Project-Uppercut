// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 20:20 UTC | START ]
#include "UppercutFightSubsystem.h"

#include "Dom/JsonObject.h"
#include "HAL/FileManager.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"

namespace
{
    // q10000 back to the float a transform wants. This conversion happens HERE
    // and at no point upstream: the simulation never sees a float, so a
    // rounding difference in presentation can never reach the fight.
    float Ru(int64 Q) { return (float)((double)Q / 10000.0); }

    // The authoritative clock's rate. Read from canon rather than assumed,
    // because Rule 9 says one clock read by everything, and a hardcoded 60 here
    // would be a second one.
    int32 ReadTickRateHz(const FString& RepoDir)
    {
        FString Text;
        if (!FFileHelper::LoadFileToString(Text, *(RepoDir / TEXT("data/clock_model.json"))))
        {
            return 60;
        }
        TSharedPtr<FJsonObject> Root;
        const TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(Text);
        if (!FJsonSerializer::Deserialize(Reader, Root) || !Root.IsValid())
        {
            return 60;
        }
        const TSharedPtr<FJsonObject>* Auth = nullptr;
        if (!Root->TryGetObjectField(TEXT("authority"), Auth)) { return 60; }
        double Hz = 60.0;
        (*Auth)->TryGetNumberField(TEXT("tick_rate_hz"), Hz);
        return (Hz > 0.0) ? (int32)Hz : 60;
    }

    // Clean home: data/ next to the .uproject.
    // Legacy sandbox: data/ one level above sandbox/UppercutSandbox.uproject.
    FString InferRepoDir()
    {
        const FString Project = FPaths::ConvertRelativePathToFull(FPaths::ProjectDir());
        if (FPaths::FileExists(Project / TEXT("data/movement_model.json")))
        {
            return Project;
        }
        const FString Parent = FPaths::ConvertRelativePathToFull(Project / TEXT(".."));
        if (FPaths::FileExists(Parent / TEXT("data/movement_model.json")))
        {
            return Parent;
        }
        return Project;
    }
}

void UUppercutFightSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);

    // Prefer ProjectDir when data/ sits next to the .uproject; otherwise parent
    // (sandbox layout). Failing here is not fatal - the arena comes up with no
    // fight and says so, which is more useful than a crash on a different layout.
    const FString InferredRepo = InferRepoDir();
    FString Error;
    if (!LoadCanon(InferredRepo, Error))
    {
        UE_LOG(LogTemp, Warning, TEXT("UppercutFight: no canon (%s)"), *Error);
    }
}

void UUppercutFightSubsystem::Deinitialize()
{
    CapturedRows.Empty();
    Scratch.Empty();
    Super::Deinitialize();
}

bool UUppercutFightSubsystem::DoesSupportWorldType(const EWorldType::Type Type) const
{
    // Game and PIE only. An editor-preview world running a fight in the
    // background would be a second simulation nobody asked for.
    return Type == EWorldType::Game || Type == EWorldType::PIE;
}

TStatId UUppercutFightSubsystem::GetStatId() const
{
    RETURN_QUICK_DECLARE_CYCLE_STAT(UUppercutFightSubsystem, STATGROUP_Tickables);
}

bool UUppercutFightSubsystem::LoadCanon(const FString& InRepoDir, FString& OutError)
{
    if (!UppercutLoadRangeCanon(InRepoDir, Canon, Sources, OutError))
    {
        State = EUppercutFightState::NoCanon;
        return false;
    }
    RepoDir = InRepoDir;
    const FString& RepoDirRef = RepoDir;
    TickRateHz = ReadTickRateHz(RepoDirRef);

    // [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 02:53 UTC | START ]
    bIntegratedLoaded = false;
    if (bIntegratedOneRound)
    {
        FString IntError;
        if (Integrated.Load(RepoDir, FighterCardA, FighterCardB, RulesetId, IntError))
        {
            bIntegratedLoaded = true;
            Sources = Integrated.Sources;
        }
        else
        {
            UE_LOG(LogTemp, Warning,
                   TEXT("UppercutFight: integrated load failed (%s); falling back to Phase Q"),
                   *IntError);
            bIntegratedOneRound = false;
        }
    }
    // [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 02:53 UTC | END ]

    ResetSession(Seed);
    State = EUppercutFightState::Ready;
    UE_LOG(LogTemp, Display,
           TEXT("UppercutFight: canon loaded from %s, %d bands, %d moves, %d Hz, integrated=%d"),
           *RepoDir, Canon.BandKey.Num(), Canon.Moves.Num(), TickRateHz,
           bIntegratedLoaded ? 1 : 0);
    return true;
}

void UUppercutFightSubsystem::GetCanonSources(TArray<FString>& OutLabels,
                                              TArray<FString>& OutHashes,
                                              TArray<FString>& OutPaths) const
{
    OutLabels.Reset(); OutHashes.Reset(); OutPaths.Reset();
    for (const FUppercutCanonSource& S : Sources)
    {
        OutLabels.Add(S.Label);
        OutHashes.Add(S.Sha256);
        OutPaths.Add(S.RelPath);
    }
}

void UUppercutFightSubsystem::ResetSession(uint32 InSeed)
{
    // [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 02:53 UTC | START ]
    if (bIntegratedLoaded)
    {
        Integrated.Reset(InSeed, TickBudget);
    }
    else
    {
        Session.Reset(Canon, InSeed);
    }
    // [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 02:53 UTC | END ]
    Fnv = UppercutFnv1a64Offset();
    RowCount = 0;
    Accumulator = 0.0;
    CapturedRows.Reset();
    Scratch.Reset();
}

void UUppercutFightSubsystem::StartFight(int32 InSeed, int32 InTickBudget)
{
    if (State == EUppercutFightState::NoCanon)
    {
        UE_LOG(LogTemp, Warning, TEXT("UppercutFight: cannot start, no canon"));
        return;
    }
    Seed = (uint32)InSeed;
    TickBudget = FMath::Max(0, InTickBudget);
    ResetSession(Seed);
    State = EUppercutFightState::Running;
}

void UUppercutFightSubsystem::Pause()
{
    if (State == EUppercutFightState::Running) { State = EUppercutFightState::Paused; }
}

void UUppercutFightSubsystem::Resume()
{
    if (State == EUppercutFightState::Paused)
    {
        // Drop whatever fraction of a tick was owed when we paused. Keeping it
        // would make the resume depend on when the pause happened, and nothing
        // about a deterministic fight should care about that.
        Accumulator = 0.0;
        State = EUppercutFightState::Running;
    }
}

void UUppercutFightSubsystem::TogglePause()
{
    if (State == EUppercutFightState::Running) { Pause(); }
    else if (State == EUppercutFightState::Paused) { Resume(); }
}

void UUppercutFightSubsystem::SingleStep(int32 NumTicks)
{
    if (State != EUppercutFightState::Running && State != EUppercutFightState::Paused)
    {
        return;
    }
    State = EUppercutFightState::Paused;
    Accumulator = 0.0;
    for (int32 i = 0; i < FMath::Max(1, NumTicks); ++i)
    {
        const int32 CurTick = bIntegratedLoaded ? Integrated.Tick : Session.Tick;
        if (TickBudget > 0 && CurTick >= TickBudget) { break; }
        if (bIntegratedLoaded && Integrated.IsFinished()) { break; }
        AdvanceOneTick();
    }
}

void UUppercutFightSubsystem::Restart()
{
    if (State == EUppercutFightState::NoCanon) { return; }
    ResetSession(Seed);
    State = EUppercutFightState::Running;
}

void UUppercutFightSubsystem::Reseed(int32 NewSeed)
{
    Seed = (uint32)NewSeed;
    Restart();
}

void UUppercutFightSubsystem::SetSpeed(float Multiplier)
{
    Speed = FMath::Clamp(Multiplier, 0.05f, 8.0f);
}

void UUppercutFightSubsystem::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    if (State != EUppercutFightState::Running) { return; }

    // CRITERION E.19. Wall-clock time decides WHEN a tick runs; it never scales
    // one. A frame worth four ticks runs four identical ticks, and a hitch runs
    // the same ticks late rather than a bigger tick.
    Accumulator += (double)DeltaSeconds * (double)Speed;
    const double TickSeconds = 1.0 / (double)TickRateHz;

    // A hitch must not turn into a thousand-tick catch-up that itself hitches.
    // The fight then runs behind real time, which is honest and visible, rather
    // than silently skipping ticks, which would not be.
    int32 Budget = 240;

    while (Accumulator >= TickSeconds && Budget-- > 0)
    {
        Accumulator -= TickSeconds;
        const int32 CurTick = bIntegratedLoaded ? Integrated.Tick : Session.Tick;
        if (bIntegratedLoaded && Integrated.IsFinished())
        {
            State = EUppercutFightState::Finished;
            break;
        }
        if (TickBudget > 0 && CurTick >= TickBudget && !bIntegratedLoaded)
        {
            State = EUppercutFightState::Finished;
            break;
        }
        AdvanceOneTick();
        if (bIntegratedLoaded && Integrated.IsFinished())
        {
            State = EUppercutFightState::Finished;
            break;
        }
    }
    if (Budget <= 0) { Accumulator = 0.0; }

    if (!bIntegratedLoaded && TickBudget > 0 && Session.Tick >= TickBudget)
    {
        State = EUppercutFightState::Finished;
    }
}

void UUppercutFightSubsystem::AdvanceOneTick()
{
    Scratch.Reset();
    // [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 02:53 UTC | START ]
    if (bIntegratedLoaded)
    {
        Integrated.Step(&Scratch);
    }
    else
    {
        Session.Step(&Scratch);
    }
    // [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 02:53 UTC | END ]

    for (const FString& Row : Scratch)
    {
        Fnv = UppercutFnv1a64(Fnv, Row);
        ++RowCount;
        if (bCaptureRows) { CapturedRows.Add(Row); }
        OnMarkerRow.Broadcast(Row);
    }
    OnFightTick.Broadcast(GetView());
}

FUppercutFightView UUppercutFightSubsystem::GetView() const
{
    FUppercutFightView V;
    V.State = State;
    V.TickBudget = TickBudget;
    V.Seed = (int32)Seed;
    V.SpeedMultiplier = Speed;
    V.MarkerHash = FString::Printf(TEXT("%016llx"), Fnv);
    V.RowCount = (int32)RowCount;

    // [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 02:53 UTC | START ]
    if (bIntegratedLoaded)
    {
        V.Tick = Integrated.Tick;
        V.SeparationRu = Ru(Integrated.Separation());
        V.Decisions = (int32)Integrated.Decisions;
        V.Punches = (int32)Integrated.Punches;
        V.Landed = (int32)Integrated.Landed;
        V.RoundMethod = Integrated.Round.Method;
        V.CardRed = Integrated.Round.Card[0];
        V.CardBlue = Integrated.Round.Card[1];
        V.bRoundFinished = Integrated.IsFinished();
        V.CardIdA = Integrated.Fighter[0].Card.Id;
        V.CardIdB = Integrated.Fighter[1].Card.Id;
        for (int32 i = 0; i < 2; ++i)
        {
            const FUppercutRangeFighter& F = Integrated.Fighter[i].Range;
            FUppercutFighterView W;
            W.PositionRu = Ru(F.Pos);
            W.PendingRu = Ru(F.Pending);
            W.BandIndex = F.Band;
            W.BandKey = Integrated.RangeCanon.BandKey.IsValidIndex(F.Band)
                ? Integrated.RangeCanon.BandKey[F.Band] : FString();
            W.LastAction = F.LastAction;
            W.LastActionTick = F.LastActionTick;
            W.BusyTicks = F.Busy;
            W.bPunchInFlight = F.bInFlight;
            W.PunchMove = F.PunchMove;
            W.bPunchIsInRange = F.bPunchLegal;
            // [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) |
            //   2026-08-15 17:15 UTC | START edit: impact telemetry crosses ]
            W.LastImpactTick = Integrated.Fighter[i].LastImpactTick;
            W.LastImpactMove = Integrated.Fighter[i].LastImpactMove;
            // [ ... | 2026-08-15 17:15 UTC | END edit ]
            // [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) |
            //   2026-08-16 02:30 UTC | START edit: vitals cross the boundary ]
            const FUppercutFightFighter& FF = Integrated.Fighter[i];
            W.CardId = FF.Card.Id;
            W.WindFractionQ = (FF.WindMax > 0)
                ? (int32)((FF.Wind * 10000) / FF.WindMax) : 0;
            const int64 ReserveMax = Integrated.StaminaCanon.ReserveMax;
            W.ReserveFractionQ = (ReserveMax > 0)
                ? (int32)((FF.Reserve * 10000) / ReserveMax) : 0;
            W.Landings = Integrated.Round.Landed[i];
            W.KnockdownsAgainst = Integrated.Round.KdRound[i];
            // [ ... | 2026-08-16 02:30 UTC | END edit ]
            V.Fighters.Add(W);
        }
        return V;
    }
    // [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 02:53 UTC | END ]

    V.Tick = Session.Tick;
    V.SeparationRu = Ru(Session.Separation());

    for (int32 i = 0; i < 2; ++i)
    {
        const FUppercutRangeFighter& F = Session.Fighter[i];
        FUppercutFighterView W;
        W.PositionRu = Ru(F.Pos);
        W.PendingRu = Ru(F.Pending);
        W.BandIndex = F.Band;
        W.BandKey = Canon.BandKey.IsValidIndex(F.Band) ? Canon.BandKey[F.Band] : FString();
        W.LastAction = F.LastAction;
        W.LastActionTick = F.LastActionTick;
        W.BusyTicks = F.Busy;
        W.bPunchInFlight = F.bInFlight;
        W.PunchMove = F.PunchMove;
        W.bPunchIsInRange = F.bPunchLegal;
        V.Fighters.Add(W);
    }

    V.Decisions = (int32)Session.Decisions;
    V.Punches = (int32)Session.Punches;
    V.Landed = (int32)Session.Landed;
    V.WhiffFromWrongBand = (int32)Session.WhiffBand;
    V.WhiffOutOfReach = (int32)Session.WhiffReach;
    V.BandTransitions = (int32)Session.Transitions;
    V.Steps = (int32)Session.Steps;
    V.RopeBlockedRetreats = (int32)Session.Roped;
    return V;
}

bool UUppercutFightSubsystem::DumpStream(const FString& Path, FString& OutError)
{
    if (State == EUppercutFightState::NoCanon)
    {
        OutError = TEXT("no canon loaded");
        return false;
    }
    if (!bCaptureRows)
    {
        OutError = TEXT("row capture was off, so there is no stream to write - "
                        "set bCaptureRows before StartFight");
        return false;
    }

    // The header declares the tick count the stream is FOR. Writing the ticks
    // actually run keeps the file honest when a fight is dumped mid-round; it
    // also means a mid-round dump will not match a full-round pin, which is
    // correct - they are not the same run.
    // [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 02:53 UTC | START ]
    FString Out;
    if (bIntegratedLoaded)
    {
        // [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-16 00:58
        //   UTC | edit: the artifact no longer records its checkout path ]
        Out = UppercutFightStreamHeader(Integrated, Seed, Integrated.Tick);
        for (const FString& Row : CapturedRows) { Out += Row; }
        Out += UppercutFightStreamTrailer(Integrated, RowCount, Fnv);
    }
    else
    {
        Out = UppercutRangeStreamHeader(Canon, Sources, Seed, Session.Tick,
                                        RepoDir);
        for (const FString& Row : CapturedRows) { Out += Row; }

        uint64 EndFnv = Fnv;
        int64 EndRows = RowCount;
        for (const FString& Row : UppercutRangePropertyRows(Canon))
        {
            Out += Row;
            EndFnv = UppercutFnv1a64(EndFnv, Row);
            ++EndRows;
        }
        Out += UppercutRangeStreamTrailer(Session, EndRows, EndFnv);
        IFileManager::Get().MakeDirectory(*FPaths::GetPath(Path), true);
        if (!FFileHelper::SaveStringToFile(Out, *Path,
                FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM))
        {
            OutError = FString::Printf(TEXT("cannot write %s"), *Path);
            return false;
        }
        UE_LOG(LogTemp, Display, TEXT("UppercutFight: wrote %lld rows to %s"),
               (long long)EndRows, *Path);
        return true;
    }
    // [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 02:53 UTC | END ]

    IFileManager::Get().MakeDirectory(*FPaths::GetPath(Path), true);
    if (!FFileHelper::SaveStringToFile(Out, *Path,
            FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM))
    {
        OutError = FString::Printf(TEXT("cannot write %s"), *Path);
        return false;
    }
    UE_LOG(LogTemp, Display, TEXT("UppercutFight: wrote %lld rows to %s"),
           (long long)RowCount, *Path);
    return true;
}
// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 20:20 UTC | END ]
