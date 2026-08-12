// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 20:50 UTC | START ]
#include "UppercutMatchDirector.h"

#include "UppercutArenaPresentation.h"

#include "Components/InputComponent.h"
#include "Engine/World.h"
#include "GameFramework/PlayerController.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/Paths.h"

AUppercutMatchDirector::AUppercutMatchDirector()
{
    PrimaryActorTick.bCanEverTick = true;
    // Before the fighters (TG_PostPhysics), so a round that ends this frame is
    // announced before anything draws the frame after it.
    PrimaryActorTick.TickGroup = TG_PrePhysics;
    AutoReceiveInput = EAutoReceiveInput::Player0;
}

void AUppercutMatchDirector::BeginPlay()
{
    Super::BeginPlay();

    if (UWorld* W = GetWorld())
    {
        Fight = W->GetSubsystem<UUppercutFightSubsystem>();
    }
    if (!Fight)
    {
        UE_LOG(LogTemp, Error,
               TEXT("UppercutMatchDirector: no fight subsystem - nothing to direct"));
        return;
    }

    // [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 03:53 UTC | START ]
    // Presentation-only Fab ring. Soft-fails when vendor packs are missing.
    // Axis scale matches AUppercutFighterBase's default 100 cm per ring unit.
    {
        const double AxisCm = (double)Fight->GetRingAxisRu() * 100.0;
        UppercutSpawnFabRing(GetWorld(), AxisCm);
    }
    // [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 03:53 UTC | END ]

    if (bBindDefaultKeys) { BindKeys(); }
    if (bAutoStart) { StartRound(); }
}

int32 AUppercutMatchDirector::AuthoredRoundLength(int32 Requested) const
{
    // clock_model.json: one, two or three minutes. Free-form lengths are
    // prohibited by Rule 8, so an unauthored number is snapped rather than
    // honoured - quietly running a 47-second round would be the invention.
    const int32 Authored[3] = { 60, 120, 180 };
    int32 Best = Authored[2];
    int32 BestGap = MAX_int32;
    for (int32 i = 0; i < 3; ++i)
    {
        const int32 Gap = FMath::Abs(Authored[i] - Requested);
        if (Gap < BestGap) { BestGap = Gap; Best = Authored[i]; }
    }
    if (Best != Requested)
    {
        UE_LOG(LogTemp, Warning,
               TEXT("UppercutMatchDirector: %ds is not an authored round length; using %ds"),
               Requested, Best);
    }
    return Best;
}

void AUppercutMatchDirector::StartRound()
{
    if (!Fight) { return; }
    Fight->bCaptureRows = bCaptureRows;
    const int32 Seconds = AuthoredRoundLength(RoundLengthSeconds);
    const int32 Budget = Seconds * Fight->GetTickRateHz();
    bAnnouncedFinish = false;
    SpeedNow = 1.f;
    Fight->SetSpeed(SpeedNow);
    Fight->StartFight(Seed, Budget);
    UE_LOG(LogTemp, Display,
           TEXT("UppercutMatchDirector: round started, seed %d, %d ticks (%ds at %d Hz)"),
           Seed, Budget, Seconds, Fight->GetTickRateHz());
}

void AUppercutMatchDirector::TogglePause()   { if (Fight) { Fight->TogglePause(); } }
void AUppercutMatchDirector::StepOneTick()   { if (Fight) { Fight->SingleStep(1); } }
void AUppercutMatchDirector::RestartSameSeed() { if (Fight) { bAnnouncedFinish = false; Fight->Restart(); } }

void AUppercutMatchDirector::StepOneSecond()
{
    if (Fight) { Fight->SingleStep(Fight->GetTickRateHz()); }
}

void AUppercutMatchDirector::NextSeed()
{
    if (!Fight) { return; }
    // A stride, not +1: adjacent seeds in a linear congruential generator open
    // with correlated draws, and a "different fight" that opens the same way is
    // not much of a second opinion.
    Seed = Seed + 7919;
    bAnnouncedFinish = false;
    Fight->Reseed(Seed);
    UE_LOG(LogTemp, Display, TEXT("UppercutMatchDirector: reseeded to %d"), Seed);
}

void AUppercutMatchDirector::Slower()
{
    if (!Fight) { return; }
    SpeedNow = FMath::Max(0.05f, SpeedNow * 0.5f);
    Fight->SetSpeed(SpeedNow);
}

void AUppercutMatchDirector::Faster()
{
    if (!Fight) { return; }
    SpeedNow = FMath::Min(8.0f, SpeedNow * 2.0f);
    Fight->SetSpeed(SpeedNow);
}

void AUppercutMatchDirector::NormalSpeed()
{
    if (!Fight) { return; }
    SpeedNow = 1.f;
    Fight->SetSpeed(SpeedNow);
}

void AUppercutMatchDirector::DumpRound()
{
    if (!Fight) { return; }
    const FUppercutFightView V = Fight->GetView();
    const FString Path = FPaths::ProjectSavedDir()
        / TEXT("live") / FString::Printf(TEXT("q_%d_%d.stream"), V.Seed, V.Tick);
    FString Error;
    if (Fight->DumpStream(Path, Error))
    {
        UE_LOG(LogTemp, Display,
               TEXT("UppercutMatchDirector: round written to %s - check it with "
                    "python -m tools.engine.prove_one_round"), *Path);
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("UppercutMatchDirector: no dump (%s)"), *Error);
    }
}

FUppercutFightView AUppercutMatchDirector::GetView() const
{
    return Fight ? Fight->GetView() : FUppercutFightView();
}

void AUppercutMatchDirector::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    if (!Fight || bAnnouncedFinish) { return; }
    const FUppercutFightView V = Fight->GetView();
    if (V.State == EUppercutFightState::Finished)
    {
        bAnnouncedFinish = true;
        UE_LOG(LogTemp, Display,
               TEXT("UppercutMatchDirector: round over at tick %d - %d punches, "
                    "%d landed, method=%s cards=%d-%d marker %s"),
               V.Tick, V.Punches, V.Landed, *V.RoundMethod,
               V.CardRed, V.CardBlue, *V.MarkerHash);
        OnRoundFinished(V);
    }
}

void AUppercutMatchDirector::BindKeys()
{
    // Bound directly rather than through project input mappings: a development
    // control that needs a settings file edited before it works is a control
    // that is missing at the moment somebody wants it.
    if (APlayerController* PC = UGameplayStatics::GetPlayerController(this, 0))
    {
        EnableInput(PC);
    }
    if (!InputComponent) { return; }

    InputComponent->BindKey(EKeys::SpaceBar, IE_Pressed, this,
                            &AUppercutMatchDirector::TogglePause);
    InputComponent->BindKey(EKeys::Period, IE_Pressed, this,
                            &AUppercutMatchDirector::StepOneTick);
    InputComponent->BindKey(EKeys::Comma, IE_Pressed, this,
                            &AUppercutMatchDirector::StepOneSecond);
    InputComponent->BindKey(EKeys::R, IE_Pressed, this,
                            &AUppercutMatchDirector::RestartSameSeed);
    InputComponent->BindKey(EKeys::N, IE_Pressed, this,
                            &AUppercutMatchDirector::NextSeed);
    InputComponent->BindKey(EKeys::LeftBracket, IE_Pressed, this,
                            &AUppercutMatchDirector::Slower);
    InputComponent->BindKey(EKeys::RightBracket, IE_Pressed, this,
                            &AUppercutMatchDirector::Faster);
    InputComponent->BindKey(EKeys::Backslash, IE_Pressed, this,
                            &AUppercutMatchDirector::NormalSpeed);
    InputComponent->BindKey(EKeys::P, IE_Pressed, this,
                            &AUppercutMatchDirector::DumpRound);

    UE_LOG(LogTemp, Display,
           TEXT("UppercutMatchDirector controls: Space pause, . step one tick, "
                ", step one second, R restart, N new seed, [ slower, ] faster, "
                "\\ normal speed, P dump the stream"));
}
// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 20:50 UTC | END ]
