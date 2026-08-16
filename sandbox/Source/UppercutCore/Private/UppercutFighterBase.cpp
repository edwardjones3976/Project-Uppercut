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
    // [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) |
    //   2026-08-15 17:15 UTC | START edit: the mesh faces the actor's forward ]
    // UE mannequin-family skeletal meshes are authored facing +Y; every stock
    // character setup counter-rotates the mesh component by -90 yaw so the
    // character faces the actor's +X. This component had no relative rotation,
    // so both fighters stood bladed 90 degrees off the ring axis - facing the
    // same side wall, never each other - no matter what the (correct) facing
    // maths in Tick computed for the ACTOR.
    Mannequin->SetRelativeRotation(FRotator(0.f, -90.f, 0.f));
    // [ ... | 2026-08-15 17:15 UTC | END edit ]
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
        // [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) |
        //   2026-08-15 17:15 UTC | edit: guard is sustained, so it loops ]
        PlayActionClip(TEXT("guard"), /*bOneShot=*/false);
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
    // Unsupported keys are refused so we never loop the wrong punch under a
    // mislabelled capture name.
    FString ClipPath;
    if (ClipKey.Equals(TEXT("overhand_right"), ESearchCase::IgnoreCase) ||
        ClipKey.Equals(TEXT("overhand_rear"), ESearchCase::IgnoreCase) ||
        ClipKey.Equals(TEXT("overhand_right_hook"), ESearchCase::IgnoreCase))
    {
        ClipPath = TEXT("/Game/BoxingAttacks/TRADITIONAL/Attacks/In-Place/KB_Overhand-R_T_IP.KB_Overhand-R_T_IP");
    }
    else if (ClipKey.Equals(TEXT("hook_rear"), ESearchCase::IgnoreCase) ||
             ClipKey.Equals(TEXT("rear_hook"), ESearchCase::IgnoreCase))
    {
        ClipPath = TEXT("/Game/BoxingAttacks/TRADITIONAL/Attacks/In-Place/KB_Hook-R_T_IP.KB_Hook-R_T_IP");
    }
    else
    {
        UE_LOG(LogTemp, Error,
               TEXT("UppercutFighter %d: unsupported -UppercutPoseClip=%s "
                    "(allowed: overhand_right, overhand_rear, overhand_right_hook, "
                    "hook_rear, rear_hook)"),
               FighterIndex, *ClipKey);
        return;
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

// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) |
//   2026-08-15 17:15 UTC | START edit: restart discipline + hit reactions ]
void AUppercutFighterBase::PlayActionClip(const FString& Action, bool bOneShot)
{
    if (bPoseStudio) { return; }
    if (!bMannequinOn || !Mannequin || ActionClips.Num() == 0) { return; }

    // While a hit reaction owns the body, sustained actions wait - they are
    // visually near-idle and the reaction is the truth worth showing. A punch
    // commitment always takes the body back: offence must never be invisible.
    if (bReactionHold)
    {
        if (!bOneShot) { return; }
        bReactionHold = false;
    }

    UAnimSequence* A = ActionClips.FindRef(Action);
    if (!A) { A = ActionClips.FindRef(TEXT("guard")); }
    if (!A) { return; }

    // Unconditionally restart. The old code skipped SetAnimation when the
    // asset matched and resumed the running clip, so the second of two
    // identical commitments played nothing - while the comment at the call
    // site correctly explained why it must not. And one-shots do not loop:
    // Play(true) here is where the self-repeating punches and the hard cuts
    // ("random body jerking") came from.
    Mannequin->SetAnimation(A);
    Mannequin->SetPosition(0.f, false);
    Mannequin->Play(!bOneShot);
}

// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-16 01:50 UTC | START ]
namespace
{
    // A bone's reference-pose transform in COMPONENT space, by walking to root.
    // FTransform A * B reads "A, then B", so multiplying childward-to-rootward
    // accumulates exactly the component-space pose.
    bool UppercutRefBoneCS(const FReferenceSkeleton& Ref, int32 Index,
                           FTransform& Out)
    {
        if (!Ref.IsValidIndex(Index)) { return false; }
        Out = FTransform::Identity;
        for (int32 I = Index; I != INDEX_NONE; I = Ref.GetParentIndex(I))
        {
            Out = Out * Ref.GetRefBonePose()[I];
        }
        return true;
    }

    bool UppercutIsDescendantOf(const FReferenceSkeleton& Ref, int32 Bone,
                                int32 Ancestor)
    {
        for (int32 I = Ref.GetParentIndex(Bone); I != INDEX_NONE;
             I = Ref.GetParentIndex(I))
        {
            if (I == Ancestor) { return true; }
        }
        return false;
    }
}

bool AUppercutFighterBase::CalibrateLookAt()
{
    if (bLookAtRefused) { return false; }
    if (!Mannequin) { bLookAtRefused = true; return false; }
    USkeletalMesh* Mesh = Mannequin->GetSkeletalMeshAsset();
    if (!Mesh) { bLookAtRefused = true; return false; }
    const FReferenceSkeleton& Ref = Mesh->GetRefSkeleton();

    LookAtHeadIndex = Mannequin->GetBoneIndex(LookAtHeadBone);
    LookAtSpineIndex = Mannequin->GetBoneIndex(LookAtSpineBone);
    if (LookAtHeadIndex == INDEX_NONE)
    {
        bLookAtRefused = true;
        UE_LOG(LogTemp, Warning,
               TEXT("UppercutFighter %d: look-at OFF (no bone '%s')"),
               FighterIndex, *LookAtHeadBone.ToString());
        return false;
    }

    // Which way is "out of the face"? Measured, not assumed. Inside component
    // space the mesh sits as authored - facing +Y - because the -90 yaw this
    // class puts on the component maps component space to the actor, and does
    // not move anything within it.
    const FVector FacingCS(0.f, 1.f, 0.f);
    FTransform RefCS;
    if (UppercutRefBoneCS(Ref, LookAtHeadIndex, RefCS))
    {
        LookAtHeadAxis =
            RefCS.GetRotation().Inverse().RotateVector(FacingCS).GetSafeNormal();
    }
    if (LookAtSpineIndex != INDEX_NONE && UppercutRefBoneCS(Ref, LookAtSpineIndex, RefCS))
    {
        LookAtSpineAxis =
            RefCS.GetRotation().Inverse().RotateVector(FacingCS).GetSafeNormal();
    }

    // Turning a bone in component space turns ONLY that bone's skinning: its
    // children keep their old transforms and the mesh tears at the neck. So
    // every descendant is carried by the same delta, gathered once here.
    LookAtHeadChildren.Reset();
    LookAtSpineChildren.Reset();
    for (int32 B = 0; B < Ref.GetNum(); ++B)
    {
        if (UppercutIsDescendantOf(Ref, B, LookAtHeadIndex))
        {
            LookAtHeadChildren.Add(B);
        }
        if (LookAtSpineIndex != INDEX_NONE
            && UppercutIsDescendantOf(Ref, B, LookAtSpineIndex))
        {
            LookAtSpineChildren.Add(B);
        }
    }

    bLookAtCalibrated = true;
    UE_LOG(LogTemp, Display,
           TEXT("UppercutFighter %d: look-at ON (head '%s' +%d children, "
                "spine '%s' +%d children)"),
           FighterIndex, *LookAtHeadBone.ToString(), LookAtHeadChildren.Num(),
           *LookAtSpineBone.ToString(), LookAtSpineChildren.Num());
    return true;
}

void AUppercutFighterBase::ApplyLookAt(const FUppercutFightView& View)
{
    if (!bLookAtOpponent || bPoseStudio || !bMannequinOn || !Mannequin) { return; }
    if (!bLookAtCalibrated && !CalibrateLookAt()) { return; }
    if (!View.Fighters.IsValidIndex(1 - FighterIndex)) { return; }

    const FVector Axis = AxisDirection.GetSafeNormal();
    const FVector FoeEyes =
        AxisOrigin
        + Axis * (View.Fighters[1 - FighterIndex].PositionRu * WorldUnitsPerRingUnit)
        + FVector(0.f, 0.f, LookAtTargetHeightCm);

    TArray<FTransform>& CS = Mannequin->GetEditableComponentSpaceTransforms();
    if (!CS.IsValidIndex(LookAtHeadIndex)) { return; }
    const FVector TargetCS =
        Mannequin->GetComponentTransform().InverseTransformPosition(FoeEyes);

    const float MaxRad = FMath::DegreesToRadians(FMath::Max(0.f, LookAtMaxDegrees));

    // Aim one bone at the target and carry its descendants with it.
    auto Aim = [&](int32 Bone, const FVector& LocalAxis,
                   const TArray<int32>& Carried, float Share)
    {
        if (Bone == INDEX_NONE || !CS.IsValidIndex(Bone) || Share <= KINDA_SMALL_NUMBER)
        {
            return;
        }
        FTransform& T = CS[Bone];
        const FVector Pivot = T.GetLocation();
        const FVector Have = T.GetRotation().RotateVector(LocalAxis).GetSafeNormal();
        const FVector Want = (TargetCS - Pivot).GetSafeNormal();
        if (Have.IsNearlyZero() || Want.IsNearlyZero()) { return; }

        FQuat Delta = FQuat::FindBetweenNormals(Have, Want);
        FVector DeltaAxis;
        float DeltaAngle = 0.f;
        Delta.ToAxisAndAngle(DeltaAxis, DeltaAngle);
        if (DeltaAxis.IsNearlyZero()) { return; }
        DeltaAngle = FMath::Clamp(DeltaAngle * Share, -MaxRad, MaxRad);
        if (FMath::IsNearlyZero(DeltaAngle)) { return; }
        Delta = FQuat(DeltaAxis, DeltaAngle);

        T.SetRotation((Delta * T.GetRotation()).GetNormalized());
        for (int32 Child : Carried)
        {
            if (!CS.IsValidIndex(Child)) { continue; }
            FTransform& C = CS[Child];
            C.SetLocation(Pivot + Delta.RotateVector(C.GetLocation() - Pivot));
            C.SetRotation((Delta * C.GetRotation()).GetNormalized());
        }
    };

    // Chest first, then the neck finishes whatever is left over - which is why
    // the head is aimed AFTER the spine has already moved it partway.
    Aim(LookAtSpineIndex, LookAtSpineAxis, LookAtSpineChildren,
        FMath::Clamp(LookAtSpineShare, 0.f, 1.f));
    Aim(LookAtHeadIndex, LookAtHeadAxis, LookAtHeadChildren, 1.f);

    Mannequin->FinalizeBoneTransform();
    Mannequin->MarkRenderDynamicDataDirty();
}
// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-16 01:50 UTC | END ]

void AUppercutFighterBase::PlayHitReaction(const FString& AttackerMove)
{
    if (bPoseStudio) { return; }
    if (!bMannequinOn || !Mannequin || ActionClips.Num() == 0) { return; }
    // The move's own name says where it went: body_* downstairs, the rest
    // upstairs. Presentation vocabulary, derived at the boundary - canon's
    // region model stays where it lives.
    const bool bBody = AttackerMove.StartsWith(TEXT("body_"));
    const FString Key = bBody ? TEXT("hit_body") : TEXT("hit_high");
    UAnimSequence* A = ActionClips.FindRef(Key);
    if (!A) { return; }
    Mannequin->SetAnimation(A);
    Mannequin->SetPosition(0.f, false);
    Mannequin->Play(false);
    bReactionHold = true;
}
// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) |
//   2026-08-15 17:15 UTC | END edit ]
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

    // [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) |
    //   2026-08-15 17:15 UTC | START edit: a finished one-shot hands back ]
    // Runs every frame, BEFORE the tick guard below: clips play in real time,
    // so a punch can finish while the simulation is paused, and a fighter
    // frozen on the last frame of a jab is a statue, not a boxer.
    if (bMannequinOn && !bPoseStudio && Mannequin && ActionClips.Num() > 0
        && !Mannequin->IsPlaying())
    {
        bReactionHold = false;
        PlayActionClip(TEXT("guard"), /*bOneShot=*/false);
    }
    // [ ... | 2026-08-15 17:15 UTC | END edit ]

    // [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-16 01:50 UTC |
    //   START edit: the eyes stay on him ]
    // Also before the tick guard, and for the same reason: the clip that is
    // turning the head away is playing in real time, so the correction has to
    // be applied in real time or it stutters at the simulation's cadence. This
    // actor ticks at TG_PostPhysics, after animation has been evaluated, which
    // is what makes writing finalized bone transforms here legitimate.
    ApplyLookAt(V);
    // [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-16 01:50 UTC |
    //   END edit ]

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
        // [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) |
        //   2026-08-15 17:15 UTC | edit: punches are one-shots; the snapshot
        //   already says whether this commitment threw one ]
        PlayActionClip(F.LastAction, /*bOneShot=*/F.bPunchInFlight);
        // [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 03:53 UTC | END ]
    }

    // [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) |
    //   2026-08-15 17:15 UTC | START edit: the hit edge ]
    // After the action edge on purpose: if a fighter is hit on the same tick
    // he commits, the hit is what the audience must see. Being hit is the one
    // event LastAction can never carry - the four reaction clips sat loaded
    // and unreachable until this edge existed.
    if (F.LastImpactTick != LastImpactTick)
    {
        LastImpactTick = F.LastImpactTick;
        if (LastImpactTick >= 0)
        {
            OnHitTaken(F.LastImpactMove);
            PlayHitReaction(F.LastImpactMove);
        }
    }
    // [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) |
    //   2026-08-15 17:15 UTC | END edit ]

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
