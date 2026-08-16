// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 20:40 UTC | START ]
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "UppercutFightSubsystem.h"
#include "UppercutFighterBase.generated.h"

class USkeletalMeshComponent;
class UAnimSequence;

// A FIGHTER YOU CAN SEE. Not a fighter you can move.
//
// This actor reads one index out of the fight subsystem's snapshot and places
// itself. It holds no state the simulation cares about, has no authority over
// anything, and cannot write back - which is the whole of Decision 0012's
// "C++ authoritative, Blueprints presentation" in one class. If this actor is
// deleted mid-fight the fight is unaffected, and that is the test of whether
// the separation is real.
//
// Animation hooks fire on EDGES of the snapshot rather than on parsed marker
// rows. A presentation layer that parses the evidence stream would be a second
// reader of it, and the second reader is always the one that drifts.

UCLASS(Blueprintable)
class UPPERCUTCORE_API AUppercutFighterBase : public AActor
{
    GENERATED_BODY()

public:
    AUppercutFighterBase();

    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;

    // 0 or 1. Fighter 0 starts on the low side of the axis.
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Uppercut")
    int32 FighterIndex = 0;

    // Centimetres per ring unit. Presentation scale only - changing it changes
    // where the actor stands, never where the fighter is.
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Uppercut")
    float WorldUnitsPerRingUnit = 100.f;

    // The axis the fight runs along, in world space. Phase Q is one-dimensional
    // on purpose: lateral steps are authored as inert on this axis and marked as
    // such in the stream, so a fighter sliding sideways here would be an
    // invention.
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Uppercut")
    FVector AxisDirection = FVector(1.f, 0.f, 0.f);

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Uppercut")
    FVector AxisOrigin = FVector::ZeroVector;

    // Face the opponent. Off if a Blueprint would rather drive rotation itself.
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Uppercut")
    bool bFaceOpponent = true;

    // A placeholder body, so the arena shows two fighters the first time it is
    // opened instead of two empty transforms. Soft-replaced by Manny/Quinn when
    // BoxingAttacks is present; nothing about the fight depends on either mesh.
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Uppercut")
    TObjectPtr<class UStaticMeshComponent> Body = nullptr;

    // [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 03:53 UTC | START ]
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Uppercut")
    TObjectPtr<USkeletalMeshComponent> Mannequin = nullptr;
    // [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 03:53 UTC | END ]

    // Presentation-only: loop one authored clip and ignore the fight snapshot.
    // Enabled by -UppercutPoseStudio (and optional -UppercutPoseFighter=N).
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Uppercut|PoseStudio")
    bool bPoseStudio = false;

    // [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-16 01:50 UTC | START ]
    // LOOK-AT. A boxer never takes his eyes off the other one, and a clip does
    // not know that: every punch and every hit reaction turns the head wherever
    // the animator put it. This bends the head (and a share of the upper spine)
    // back onto the opponent AFTER the clip has been evaluated.
    //
    // It reads the fight snapshot and writes only to the skeletal mesh's
    // component-space transforms. It cannot reach the simulation - Decision
    // 0012, and the pins are what make that checkable rather than promised.
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Uppercut|Presentation")
    bool bLookAtOpponent = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Uppercut|Presentation")
    FName LookAtHeadBone = FName(TEXT("head"));

    // The upper spine takes a share of the turn before the neck finishes it,
    // because a boxer turns his chest into the man, not just his face.
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Uppercut|Presentation")
    FName LookAtSpineBone = FName(TEXT("spine_03"));

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Uppercut|Presentation")
    float LookAtSpineShare = 0.3f;

    // A neck has limits. Past this the head stops following and the fighter has
    // genuinely lost sight of him, which is information worth being able to see.
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Uppercut|Presentation")
    float LookAtMaxDegrees = 60.f;

    // Where on the opponent the eyes go, above his floor position. Canon has no
    // opinion about eye height; this is a presentation number and nothing reads
    // it back.
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Uppercut|Presentation")
    float LookAtTargetHeightCm = 165.f;
    // [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-16 01:50 UTC | END ]

    // --- what presentation is told -----------------------------------------

    // A new commitment was drawn this tick. `Action` is the canon move id, or
    // "idle".
    UFUNCTION(BlueprintImplementableEvent, Category = "Uppercut|Presentation")
    void OnActionCommitted(const FString& Action, bool bIsPunch);

    // A punch left the hand. `bInRange` is Rule 12's verdict at the moment of
    // the throw - false means it is already going to miss, which is exactly the
    // thing a spectator should be able to see coming.
    UFUNCTION(BlueprintImplementableEvent, Category = "Uppercut|Presentation")
    void OnPunchStarted(const FString& MoveId, bool bInRange);

    UFUNCTION(BlueprintImplementableEvent, Category = "Uppercut|Presentation")
    void OnPunchEnded(const FString& MoveId);

    // The band changed. A guard, a stance and a camera all care about this.
    UFUNCTION(BlueprintImplementableEvent, Category = "Uppercut|Presentation")
    void OnBandChanged(const FString& OldBand, const FString& NewBand);

    // [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-15 17:15 UTC | START ]
    // This fighter was hit. `MoveId` is the attacker's move. Fires on the edge
    // of the snapshot's LastImpactTick, exactly as OnActionCommitted fires on
    // LastActionTick - being hit is the one event a fighter never commits to.
    UFUNCTION(BlueprintImplementableEvent, Category = "Uppercut|Presentation")
    void OnHitTaken(const FString& MoveId);
    // [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-15 17:15 UTC | END ]

    UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Uppercut")
    FUppercutFighterView GetFighterView() const;

protected:
    UPROPERTY(BlueprintReadOnly, Category = "Uppercut")
    TObjectPtr<UUppercutFightSubsystem> Fight = nullptr;

private:
    // [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 03:53 UTC | START ]
    void TryEnableMannequin();
    // [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) |
    //   2026-08-15 17:15 UTC | START edit: restart + loop discipline ]
    // bOneShot: a punch or a reaction plays once and hands the body back;
    // everything sustained (guard, steps, idle) loops. Every call RESTARTS the
    // clip - two jabs in a row are two commitments (the comment in Tick already
    // said so; the old implementation resumed the running clip instead).
    void PlayActionClip(const FString& Action, bool bOneShot);
    void PlayHitReaction(const FString& AttackerMove);
    // [ ... | 2026-08-15 17:15 UTC | END edit ]
    void EnterPoseStudioIfRequested();
    void PlayPoseStudioLoop(const FString& ClipPath);
    // [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 03:53 UTC | END ]

    // Last snapshot, so edges can be detected without the simulation having to
    // announce them.
    int32 LastActionTick = 0;
    FString LastBand;
    bool bWasPunching = false;
    FString LastPunchMove;
    int32 LastSeenTick = -1;

    // [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-15 17:15 UTC | START ]
    // Edge memory for the impact snapshot, and the reaction's brief ownership
    // of the body: while a hit reaction plays, sustained actions do not stomp
    // it (they are visually near-idle anyway), but a new PUNCH commitment
    // always takes the body back - offence must never be invisible.
    int32 LastImpactTick = -1;
    bool bReactionHold = false;
    // [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-15 17:15 UTC | END ]

    // [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 03:53 UTC | START ]
    bool bMannequinOn = false;
    TMap<FString, UAnimSequence*> ActionClips;
    // [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 03:53 UTC | END ]

    // [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-16 01:50 UTC | START ]
    void ApplyLookAt(const FUppercutFightView& View);
    bool CalibrateLookAt();

    bool bLookAtCalibrated = false;
    bool bLookAtRefused = false;      // calibration failed once; do not retry per frame
    int32 LookAtHeadIndex = INDEX_NONE;
    int32 LookAtSpineIndex = INDEX_NONE;
    // The bone-local axis that points out of the face in the reference pose,
    // measured from the skeleton rather than assumed. A hard-coded axis is a
    // guess about an asset, and the asset is allowed to change.
    FVector LookAtHeadAxis = FVector::ForwardVector;
    FVector LookAtSpineAxis = FVector::ForwardVector;
    // Descendants move with their parent or the mesh tears. Precomputed once.
    TArray<int32> LookAtHeadChildren;
    TArray<int32> LookAtSpineChildren;
    // [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-16 01:50 UTC | END ]
};
// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 20:40 UTC | END ]
