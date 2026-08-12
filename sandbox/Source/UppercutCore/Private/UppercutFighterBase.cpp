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
    // [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 03:53 UTC | START ]
    TryEnableMannequin();
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

void AUppercutFighterBase::PlayActionClip(const FString& Action)
{
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
