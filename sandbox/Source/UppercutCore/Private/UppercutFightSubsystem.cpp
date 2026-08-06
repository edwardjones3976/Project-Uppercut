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
}

void UUppercutFightSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);

    // The project lives at <repo>/sandbox, so the repository is one level up.
    // Failing here is not fatal - the arena comes up with no fight and says so,
    // which is more useful than a crash on a machine with a different layout.
    const FString RepoDir = FPaths::ConvertRelativePathToFull(
        FPaths::ProjectDir() / TEXT(".."));
    FString Error;
    if (!LoadCanon(RepoDir, Error))
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

bool UUppercutFightSubsystem::LoadCanon(const FString& RepoDir, FString& OutError)
{
    if (!UppercutLoadRangeCanon(RepoDir, Canon, Sources, OutError))
    {
        State = EUppercutFightState::NoCanon;
        return false;
    }
    TickRateHz = ReadTickRateHz(RepoDir);
    ResetSession(Seed);
    State = EUppercutFightState::Ready;
    UE_LOG(LogTemp, Display,
           TEXT("UppercutFight: canon loaded from %s, %d bands, %d moves, %d Hz"),
           *RepoDir, Canon.BandKey.Num(), Canon.Moves.Num(), TickRateHz);
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
    Session.Reset(Canon, InSeed);
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
        if (TickBudget > 0 && Session.Tick >= TickBudget) { break; }
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
        if (TickBudget > 0 && Session.Tick >= TickBudget)
        {
            State = EUppercutFightState::Finished;
            break;
        }
        AdvanceOneTick();
    }
    if (Budget <= 0) { Accumulator = 0.0; }

    if (TickBudget > 0 && Session.Tick >= TickBudget)
    {
        State = EUppercutFightState::Finished;
    }
}

void UUppercutFightSubsystem::AdvanceOneTick()
{
    Scratch.Reset();
    Session.Step(&Scratch);

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
    V.Tick = Session.Tick;
    V.TickBudget = TickBudget;
    V.Seed = (int32)Seed;
    V.SpeedMultiplier = Speed;
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

    V.MarkerHash = FString::Printf(TEXT("%016llx"), Fnv);
    V.RowCount = (int32)RowCount;
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
    FString Out = UppercutRangeStreamHeader(Canon, Sources, Seed, Session.Tick);
    for (const FString& Row : CapturedRows) { Out += Row; }

    // The property rows are hashed, so a dump has to fold them in exactly where
    // the commandlet does: after the last tick, before the trailer.
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
    UE_LOG(LogTemp, Display, TEXT("UppercutFight: wrote %lld rows to %s"), EndRows, *Path);
    return true;
}
// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 20:20 UTC | END ]
