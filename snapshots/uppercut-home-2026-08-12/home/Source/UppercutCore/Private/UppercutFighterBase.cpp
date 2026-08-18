// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 20:40 UTC | START ]
#include "UppercutFighterBase.h"

#include "UppercutArenaPresentation.h"

#include "Animation/AnimSequence.h"
#include "Animation/AnimSingleNodeInstance.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "UObject/ConstructorHelpers.h"

AUppercutFighterBase::AUppercutFighterBase()
{
    PrimaryActorTick.bCanEverTick = true;
    // After the subsystem, so a fighter never draws a frame older than the tick
    // it is meant to be showing.
    PrimaryActorTick.TickGroup = TG_PostPhysics;

    // The root is an empty transform and the body hangs off it, so the actor's
    // location is the fighter's position on the floor rather than the middle of
    // a mesh. SetActorLocation would otherwise fight the mesh's own offset.
    USceneComponent* Pivot = CreateDefaultSubobject<USceneComponent>(TEXT("Pivot"));
    SetRootComponent(Pivot);

    Body = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Body"));
    Body->SetupAttachment(Pivot);
    Body->SetCollisionEnabled(ECollisionEnabled::NoCollision);

    // [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 03:53 UTC | START ]
    Mannequin = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("Mannequin"));
    Mannequin->SetupAttachment(Pivot);
    Mannequin->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    Mannequin->SetHiddenInGame(true);
    Mannequin->SetVisibility(false);
    // [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 03:53 UTC | END ]

    // An engine primitive, so the arena is watchable before anybody authors a
    // character. If it is missing the actor is simply invisible - a placeholder
    // that could fail the fight would be worse than no placeholder.
    static ConstructorHelpers::FObjectFinder<UStaticMesh> Cylinder(
        TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
    if (Cylinder.Succeeded())
    {
        Body->SetStaticMesh(Cylinder.Object);
        // A boxer is roughly 1.8 m of a 1 m unit cylinder, half a metre wide.
        Body->SetRelativeScale3D(FVector(0.5f, 0.5f, 1.8f));
        Body->SetRelativeLocation(FVector(0.f, 0.f, 90.f));
    }
}

void AUppercutFighterBase::BeginPlay()
{
    Super::BeginPlay();
    if (UWorld* W = GetWorld())
    {
        Fight = W->GetSubsystem<UUppercutFightSubsystem>();
    }
    if (!Fight)
    {
        UE_LOG(LogTemp, Warning,
               TEXT("UppercutFighter %d: no fight subsystem in this world"),
               FighterIndex);
    }
    else
    {
        WorldUnitsPerRingUnit = Fight->GetRuToCm();
    }
    // [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 03:53 UTC | START ]
    TryEnableMannequin();
    EnterPoseStudioIfRequested();
    // [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 03:53 UTC | END ]
}

// [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 03:53 UTC | START ]
void AUppercutFighterBase::TryEnableMannequin()
{
    USkeletalMesh* Mesh = UppercutLoadFighterMannequinMesh(FighterIndex);
    if (!Mesh || !Mannequin)
    {
        return;
    }
    Mannequin->SetSkeletalMeshAsset(Mesh);
    Mannequin->SetMobility(EComponentMobility::Movable);
    Mannequin->VisibilityBasedAnimTickOption =
        EVisibilityBasedAnimTickOption::AlwaysTickPoseAndRefreshBones;
    Mannequin->SetAnimationMode(EAnimationMode::AnimationSingleNode);
    Mannequin->SetHiddenInGame(false);
    Mannequin->SetVisibility(true);
    if (Body)
    {
        Body->SetHiddenInGame(true);
        Body->SetVisibility(false);
    }
    bMannequinOn = true;
    if (UppercutLoadFighterActionClips(ActionClips))
    {
        PlayActionClip(TEXT("guard"));
        UE_LOG(LogTemp, Display,
               TEXT("UppercutFighter %d: mannequin ON (%d clips)"),
               FighterIndex, ActionClips.Num());
    }
    else
    {
        UE_LOG(LogTemp, Display,
               TEXT("UppercutFighter %d: mannequin mesh ON (clips off)"),
               FighterIndex);
    }
}

void AUppercutFighterBase::EnterPoseStudioIfRequested()
{
    const TCHAR* Cmd = FCommandLine::Get();
    const bool bWantPose = bPoseStudio || FParse::Param(Cmd, TEXT("UppercutPoseStudio"));
    if (!bWantPose) { return; }

    int32 PoseFighter = 0;
    FParse::Value(Cmd, TEXT("UppercutPoseFighter="), PoseFighter);
    if (FighterIndex != PoseFighter)
    {
        SetActorHiddenInGame(true);
        SetActorEnableCollision(false);
        SetActorTickEnabled(false);
        UE_LOG(LogTemp, Display,
               TEXT("UppercutFighter %d: hidden (pose studio isolates %d)"),
               FighterIndex, PoseFighter);
        return;
    }

    bPoseStudio = true;
    // Center on the floor; face along +X like an orthodox fighter looking at
    // the opponent side of the axis. Presentation only.
    SetActorLocation(FVector(0.f, 0.f, 0.f));
    SetActorRotation(FRotator(0.f, 0.f, 0.f));
    bFaceOpponent = false;

    FString ClipKey;
    FParse::Value(Cmd, TEXT("UppercutPoseClip="), ClipKey);
    if (ClipKey.IsEmpty()) { ClipKey = TEXT("overhand_right"); }

    // Boxing geometry (orthodox): lead = left, rear = right.
    // Overhand right = rear-hand looping overhand (KB_Overhand-R_*).
    // Rear hook     = rear-hand HORIZONTAL hook (KB_Hook-R_*) — different punch.
    // Demo language "overhand right hook" / "rear power hand overhand" maps to
    // Overhand-R, not Hook-R. Ask explicitly for hook_rear to get the lateral hook.
    FString ClipPath =
        TEXT("/Game/BoxingAttacks/TRADITIONAL/Attacks/In-Place/KB_Overhand-R_T_IP.KB_Overhand-R_T_IP");
    if (ClipKey.Equals(TEXT("hook_rear"), ESearchCase::IgnoreCase) ||
        ClipKey.Equals(TEXT("rear_hook"), ESearchCase::IgnoreCase))
    {
        ClipPath = TEXT("/Game/BoxingAttacks/TRADITIONAL/Attacks/In-Place/KB_Hook-R_T_IP.KB_Hook-R_T_IP");
    }
    else if (ClipKey.Equals(TEXT("overhand_rear"), ESearchCase::IgnoreCase) ||
             ClipKey.Equals(TEXT("overhand_right"), ESearchCase::IgnoreCase) ||
             ClipKey.Equals(TEXT("overhand_right_hook"), ESearchCase::IgnoreCase))
    {
        ClipPath = TEXT("/Game/BoxingAttacks/TRADITIONAL/Attacks/In-Place/KB_Overhand-R_T_IP.KB_Overhand-R_T_IP");
    }

    PlayPoseStudioLoop(ClipPath);
}

void AUppercutFighterBase::PlayPoseStudioLoop(const FString& ClipPath)
{
    if (!Mannequin)
    {
        UE_LOG(LogTemp, Warning, TEXT("UppercutFighter %d: pose studio needs Mannequin"),
               FighterIndex);
        return;
    }
    if (!bMannequinOn)
    {
        TryEnableMannequin();
    }
    UAnimSequence* A = LoadObject<UAnimSequence>(nullptr, *ClipPath);
    if (!A)
    {
        UE_LOG(LogTemp, Error,
               TEXT("UppercutFighter %d: pose clip missing (%s)"),
               FighterIndex, *ClipPath);
        return;
    }
    Mannequin->SetAnimationMode(EAnimationMode::AnimationSingleNode);
    Mannequin->SetAnimation(A);
    Mannequin->SetPlayRate(1.f);
    Mannequin->Play(true);  // looping
    UE_LOG(LogTemp, Display,
           TEXT("UppercutFighter %d: POSE STUDIO looping %s (orthodox)"),
           FighterIndex, *ClipPath);
}

void AUppercutFighterBase::PlayActionClip(const FString& Action)
{
    if (bPoseStudio) { return; }
    if (!bMannequinOn || !Mannequin || ActionClips.Num() == 0) { return; }
    UAnimSequence* A = ActionClips.FindRef(Action);
    if (!A) { A = ActionClips.FindRef(TEXT("guard")); }
    if (!A) { return; }
    UAnimSingleNodeInstance* SN = Mannequin->GetSingleNodeInstance();
    if (!SN || SN->GetAnimationAsset() != A)
    {
        Mannequin->SetAnimation(A);
    }
    Mannequin->Play(true);
}
// [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 03:53 UTC | END ]

FUppercutFighterView AUppercutFighterBase::GetFighterView() const
{
    if (!Fight) { return FUppercutFighterView(); }
    const FUppercutFightView V = Fight->GetView();
    return V.Fighters.IsValidIndex(FighterIndex)
           ? V.Fighters[FighterIndex]
           : FUppercutFighterView();
}

void AUppercutFighterBase::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    // Pose studio owns transform + clip; never let the fight snapshot move him.
    if (bPoseStudio) { return; }
    if (!Fight) { return; }

    const FUppercutFightView V = Fight->GetView();
    if (!V.Fighters.IsValidIndex(FighterIndex)) { return; }
    const FUppercutFighterView& F = V.Fighters[FighterIndex];

    // ---- place him --------------------------------------------------------
    const FVector Axis = AxisDirection.GetSafeNormal();
    const FVector Where = AxisOrigin + Axis * (F.PositionRu * WorldUnitsPerRingUnit);
    SetActorLocation(Where);

    if (bFaceOpponent && V.Fighters.IsValidIndex(1 - FighterIndex))
    {
        const float Other = V.Fighters[1 - FighterIndex].PositionRu;
        const float Sign = (Other >= F.PositionRu) ? 1.f : -1.f;
        SetActorRotation((Axis * Sign).Rotation());
    }

    // ---- edges, only when the simulation actually advanced ----------------
    // Guarding on the tick means a paused fight does not re-fire an animation
    // every frame, and a single-step fires it exactly once.
    if (V.Tick == LastSeenTick) { return; }
    LastSeenTick = V.Tick;

    if (F.BandKey != LastBand)
    {
        OnBandChanged(LastBand, F.BandKey);
        LastBand = F.BandKey;
    }

    // Compare the DECISION TICK, not the action string: two jabs in a row are
    // two commitments, and a string comparison would play one animation.
    if (F.LastActionTick != LastActionTick)
    {
        LastActionTick = F.LastActionTick;
        OnActionCommitted(F.LastAction, F.bPunchInFlight);
        // [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 03:53 UTC | START ]
        PlayActionClip(F.LastAction);
        // [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 03:53 UTC | END ]
    }

    if (F.bPunchInFlight && !bWasPunching)
    {
        LastPunchMove = F.PunchMove;
        OnPunchStarted(F.PunchMove, F.bPunchIsInRange);
    }
    else if (!F.bPunchInFlight && bWasPunching)
    {
        OnPunchEnded(LastPunchMove);
    }
    bWasPunching = F.bPunchInFlight;
}
// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 20:40 UTC | END ]
