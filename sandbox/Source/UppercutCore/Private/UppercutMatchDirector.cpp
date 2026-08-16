// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 20:50 UTC | START ]
#include "UppercutMatchDirector.h"

#include "UppercutArenaPresentation.h"
#include "UppercutFighterBase.h"

#include "Camera/CameraActor.h"
#include "Components/InputComponent.h"
#include "Components/LightComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/DirectionalLight.h"
#include "Engine/Engine.h"
#include "Engine/StaticMesh.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/World.h"
#include "GameFramework/PlayerController.h"
#include "HAL/FileManager.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "UnrealClient.h"

namespace
{
    // Resolve -UppercutPoseClip= to a filename slug. Unknown non-empty keys are
    // rejected so captures are never labelled with the wrong punch.
    bool ResolvePoseClipSlug(const FString& ClipKey, FString& OutSlug, FString& OutError)
    {
        if (ClipKey.IsEmpty() ||
            ClipKey.Equals(TEXT("overhand_right"), ESearchCase::IgnoreCase) ||
            ClipKey.Equals(TEXT("overhand_rear"), ESearchCase::IgnoreCase) ||
            ClipKey.Equals(TEXT("overhand_right_hook"), ESearchCase::IgnoreCase))
        {
            OutSlug = TEXT("overhand_right");
            return true;
        }
        if (ClipKey.Equals(TEXT("hook_rear"), ESearchCase::IgnoreCase) ||
            ClipKey.Equals(TEXT("rear_hook"), ESearchCase::IgnoreCase))
        {
            OutSlug = TEXT("hook_rear");
            return true;
        }
        OutError = FString::Printf(
            TEXT("unsupported -UppercutPoseClip=%s (allowed: overhand_right, "
                 "overhand_rear, overhand_right_hook, hook_rear, rear_hook)"),
            *ClipKey);
        return false;
    }
}

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

    // Presentation-only pose studio: isolate a fighter, do not start a round.
    // Combat authority is untouched - this path never calls StartFight.
    // Lit floor + locked camera + FScreenshotRequest (not Desktop CopyFromScreen /
    // HighResShot) are what produce a non-black JPG of the looping clip.
    // Actor scan uses GameplayStatics (whitelist-safe); capture delay uses Tick
    // instead of TimerManager.h so check_core_compiles stays honest and green.
    const bool bPoseStudio = FParse::Param(FCommandLine::Get(), TEXT("UppercutPoseStudio"));
    if (bPoseStudio)
    {
        bPoseStudioActive = true;
        UE_LOG(LogTemp, Display,
               TEXT("UppercutMatchDirector: POSE STUDIO on - no auto-start, no Fab ring"));
        if (UWorld* World = GetWorld())
        {
            int32 PoseFighter = 0;
            FParse::Value(FCommandLine::Get(), TEXT("UppercutPoseFighter="), PoseFighter);
            FString ClipKey;
            FParse::Value(FCommandLine::Get(), TEXT("UppercutPoseClip="), ClipKey);
            FString ClipSlug;
            FString ClipError;
            if (!ResolvePoseClipSlug(ClipKey, ClipSlug, ClipError))
            {
                UE_LOG(LogTemp, Error,
                       TEXT("UppercutMatchDirector: pose capture refused - %s"),
                       *ClipError);
                if (bBindDefaultKeys) { BindKeys(); }
                return;
            }

            // Key + fill lights so geometry reads against the void.
            if (ADirectionalLight* Sun = World->SpawnActor<ADirectionalLight>(
                    FVector(200.f, -200.f, 500.f), FRotator(-55.f, -40.f, 0.f)))
            {
                if (ULightComponent* C = Sun->GetLightComponent())
                {
                    C->SetIntensity(12.f);
                    C->SetVisibility(true);
                }
            }
            if (ADirectionalLight* Fill = World->SpawnActor<ADirectionalLight>(
                    FVector(-200.f, 200.f, 300.f), FRotator(-35.f, 140.f, 0.f)))
            {
                if (ULightComponent* C = Fill->GetLightComponent())
                {
                    C->SetIntensity(4.f);
                    C->SetVisibility(true);
                }
            }

            if (UStaticMesh* Plane = LoadObject<UStaticMesh>(
                    nullptr, TEXT("/Engine/BasicShapes/Plane.Plane")))
            {
                if (AStaticMeshActor* Floor = World->SpawnActor<AStaticMeshActor>(
                        FVector(0.f, 0.f, 0.f), FRotator::ZeroRotator))
                {
                    Floor->SetActorLabel(TEXT("PoseStudioFloor"));
                    Floor->GetStaticMeshComponent()->SetStaticMesh(Plane);
                    Floor->SetActorScale3D(FVector(12.f, 12.f, 1.f));
                }
            }

            FVector Focus(0.f, 0.f, 110.f);
            TArray<AActor*> FighterActors;
            UGameplayStatics::GetAllActorsOfClass(
                World, AUppercutFighterBase::StaticClass(), FighterActors);
            for (AActor* Actor : FighterActors)
            {
                AUppercutFighterBase* Fighter = Cast<AUppercutFighterBase>(Actor);
                if (!Fighter || Fighter->FighterIndex != PoseFighter) { continue; }
                Focus = Fighter->GetActorLocation() + FVector(0.f, 0.f, 110.f);
                if (Fighter->Body)
                {
                    Fighter->Body->SetHiddenInGame(false);
                    Fighter->Body->SetVisibility(true);
                }
                break;
            }
            const FVector CamLoc = Focus + FVector(40.f, -320.f, 50.f);
            const FRotator CamRot = (Focus - CamLoc).Rotation();
            ACameraActor* Cam = World->SpawnActor<ACameraActor>(CamLoc, CamRot);
            if (Cam)
            {
                Cam->SetActorLabel(TEXT("PoseStudioCamera"));
                if (APlayerController* PC =
                        UGameplayStatics::GetPlayerController(World, 0))
                {
                    PC->bAutoManageActiveCameraTarget = false;
                    PC->SetViewTargetWithBlend(Cam, 0.f);
                }
                UE_LOG(LogTemp, Display,
                       TEXT("UppercutMatchDirector: pose camera at %s -> %s"),
                       *CamLoc.ToCompactString(), *Focus.ToCompactString());
            }

            const FString ShotName = FString::Printf(
                TEXT("fighter%d_%s_orthodox.png"), PoseFighter, *ClipSlug);
            const FString ShotPath = FPaths::ConvertRelativePathToFull(
                FPaths::ProjectSavedDir() / TEXT("pose_studio") / ShotName);
            IFileManager::Get().MakeDirectory(*FPaths::GetPath(ShotPath), true);
            ArmPoseStudioCapture(Cam, ShotPath);
        }
        if (bBindDefaultKeys) { BindKeys(); }
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

void AUppercutMatchDirector::ArmPoseStudioCapture(ACameraActor* Cam, const FString& ShotPath)
{
    PoseCamera = Cam;
    PoseShotPath = ShotPath;
    PoseShotDelayRemaining = 6.0f;
    bPoseShotArmed = true;
    UE_LOG(LogTemp, Display,
           TEXT("UppercutMatchDirector: pose screenshot armed (%.1fs) -> %s"),
           PoseShotDelayRemaining, *PoseShotPath);
}

void AUppercutMatchDirector::FirePoseStudioCapture()
{
    if (ACameraActor* Cam = PoseCamera.Get())
    {
        if (UWorld* World = GetWorld())
        {
            if (APlayerController* PC =
                    UGameplayStatics::GetPlayerController(World, 0))
            {
                PC->bAutoManageActiveCameraTarget = false;
                PC->SetViewTargetWithBlend(Cam, 0.f);
            }
        }
    }
    FScreenshotRequest::RequestScreenshot(PoseShotPath, false, false);
    UE_LOG(LogTemp, Display,
           TEXT("UppercutMatchDirector: pose screenshot requested -> %s"),
           *PoseShotPath);
}

// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-16 02:30 UTC | START ]
namespace
{
    // A meter, in text. Ten cells of q10000.
    FString UppercutBar(int32 FractionQ)
    {
        const int32 Filled = FMath::Clamp(FMath::RoundToInt(FractionQ / 1000.f), 0, 10);
        FString Out = TEXT("[");
        for (int32 I = 0; I < 10; ++I)
        {
            Out += (I < Filled) ? TEXT("|") : TEXT(".");
        }
        return Out + FString::Printf(TEXT("] %3d%%"), FMath::Clamp(FractionQ / 100, 0, 100));
    }
}

void AUppercutMatchDirector::DrawVitalsPanel(const FUppercutFightView& View)
{
    if (!bShowVitalsPanel || !GEngine) { return; }

    // The on-screen debug channel stacks by INSERTION order and draws the
    // first message lowest, so a panel written top-down renders upside down.
    // Two attempts confirmed it: ascending keys, then descending keys - the
    // key does not decide the order at all. Lines are collected here and
    // emitted in reverse below. Stable keys keep each row updating in place
    // instead of scrolling; the block is reserved from 9100 upward.
    TArray<TPair<FColor, FString>> Lines;
    auto Line = [&](const FColor& Colour, const FString& Text)
    {
        Lines.Emplace(Colour, Text);
    };

    Line(FColor::White, TEXT("-- FIGHTER VITALS TELEMETRY ---------------"));
    Line(FColor::Silver, FString::Printf(
        TEXT("  seed %d   tick %d / %d   x%.2f   %s"),
        View.Seed, View.Tick, View.TickBudget, View.SpeedMultiplier,
        View.bRoundFinished ? *View.RoundMethod : TEXT("boxing")));

    for (int32 I = 0; I < View.Fighters.Num(); ++I)
    {
        const FUppercutFighterView& F = View.Fighters[I];
        const FColor Corner = (I == 0) ? FColor(255, 120, 120) : FColor(120, 170, 255);
        Line(Corner, FString::Printf(TEXT("  %-11s %s"),
             (I == 0) ? TEXT("RED") : TEXT("BLUE"), *F.CardId));
        Line(Corner, FString::Printf(TEXT("    wind    %s"),
             *UppercutBar(F.WindFractionQ)));
        Line(Corner, FString::Printf(TEXT("    reserve %s"),
             *UppercutBar(F.ReserveFractionQ)));
        Line(Corner, FString::Printf(
            TEXT("    landed %-4d  kd against %d   band %s   %s%s"),
            F.Landings, F.KnockdownsAgainst, *F.BandKey, *F.LastAction,
            F.bPunchInFlight ? (F.bPunchIsInRange ? TEXT(" (in flight)")
                                                  : TEXT(" (in flight, short)"))
                             : TEXT("")));
    }

    // The counters the trailer will end with, live - so what is on screen and
    // what the marker stream says are checkably the same fight.
    Line(FColor::Silver, FString::Printf(
        TEXT("  punches %d  landed %d  cards %d-%d"),
        View.Punches, View.Landed, View.CardRed, View.CardBlue));
    Line(FColor::Silver, FString::Printf(TEXT("  marker %s  rows %d"),
        *View.MarkerHash, View.RowCount));

    // Said out loud rather than drawn as an empty meter. Two of the three
    // meters a boxing HUD normally carries cannot exist yet: the integrated
    // session has no damage model (Issue #12). A head bar sitting at 100%
    // would be presentation inventing a fighter who is unhurt.
    Line(FColor(150, 150, 150),
         TEXT("  head/body condition: NOT MODELLED YET (Issue #12)"));

    int32 Key = 9100;
    for (int32 I = Lines.Num() - 1; I >= 0; --I)
    {
        GEngine->AddOnScreenDebugMessage(Key++, 0.f, Lines[I].Key, Lines[I].Value);
    }
}
// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-16 02:30 UTC | END ]

void AUppercutMatchDirector::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);

    if (bPoseStudioActive)
    {
        if (bPoseShotArmed)
        {
            PoseShotDelayRemaining -= DeltaSeconds;
            if (PoseShotDelayRemaining <= 0.f)
            {
                bPoseShotArmed = false;
                FirePoseStudioCapture();
            }
        }
        return;
    }

    if (!Fight) { return; }
    const FUppercutFightView V = Fight->GetView();

    // [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-16 02:30 UTC |
    //   edit: drawn BEFORE the finish guard, so the panel still reads out the
    //   round that just ended instead of vanishing at the bell ]
    DrawVitalsPanel(V);

    if (bAnnouncedFinish) { return; }
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
