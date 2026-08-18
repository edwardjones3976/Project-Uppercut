// [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 03:53 UTC | START ]
#include "UppercutArenaPresentation.h"

#include "Animation/AnimSequence.h"
#include "Engine/StaticMesh.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/World.h"
#include "Components/StaticMeshComponent.h"
#include "Misc/Paths.h"

FUppercutArenaRingSpawn UppercutSpawnFabRing(UWorld* World, double AxisCm)
{
    FUppercutArenaRingSpawn Out;
    if (!World || AxisCm <= 1.0)
    {
        UE_LOG(LogTemp, Warning,
               TEXT("UppercutArenaPresentation: arena OFF (AxisCm=%.3f; need canon)"),
               AxisCm);
        return Out;
    }

    // Ring five is a CLUSTER IN SPACE (measured with import_fab_bounds.py).
    // Same part list as AUppercutBoutDirector::BuildArena — one source of truth.
    static const TCHAR* Parts[] = {
        TEXT("cartoon_boxing_arena_511"), TEXT("cartoon_boxing_arena_5_1"),
        TEXT("cartoon_boxing_arena_5_2"), TEXT("cartoon_boxing_arena_5_3"),
        TEXT("cartoon_boxing_arena_5_4"), TEXT("cartoon_boxing_arena_5_5"),
        TEXT("cartoon_boxing_arena_5_6") };
    const TCHAR* CanvasPart = TEXT("cartoon_boxing_arena_511");
    static const TCHAR* RopeParts[4] = {
        TEXT("cartoon_boxing_arena_5_3"), TEXT("cartoon_boxing_arena_5_4"),
        TEXT("cartoon_boxing_arena_5_5"), TEXT("cartoon_boxing_arena_5_6") };
    static const double RopeHeightCm[4] = { 137.0, 107.0, 76.0, 46.0 };
    const TCHAR* SpanPart = TEXT("cartoon_boxing_arena_5_3");

    double CanvasTop = 0.0;
    double SpanWidth = 0.0;
    TArray<AStaticMeshActor*> RopeActor;
    TArray<double> RopeCentreZ;
    RopeActor.SetNumZeroed(4);
    RopeCentreZ.SetNumZeroed(4);

    TArray<AStaticMeshActor*> Spawned;
    FBox Bounds(ForceInit);
    for (const TCHAR* Part : Parts)
    {
        const FString Path = FString::Printf(
            TEXT("/Game/FabImports/CartoonBoxingArena/%s.%s"), Part, Part);
        UStaticMesh* Mesh = LoadObject<UStaticMesh>(nullptr, *Path);
        if (!Mesh) { continue; }
        AStaticMeshActor* A = World->SpawnActor<AStaticMeshActor>(
            FVector::ZeroVector, FRotator::ZeroRotator);
        if (!A) { continue; }
        A->SetMobility(EComponentMobility::Movable);
        UStaticMeshComponent* C = A->GetStaticMeshComponent();
        C->SetStaticMesh(Mesh);
        C->SetCollisionEnabled(ECollisionEnabled::NoCollision);
        const FBox MeshBox = Mesh->GetBoundingBox();
        Bounds += MeshBox;
        if (FCString::Strcmp(Part, CanvasPart) == 0) { CanvasTop = MeshBox.Max.Z; }
        if (FCString::Strcmp(Part, SpanPart) == 0)
        {
            SpanWidth = FMath::Max(MeshBox.Max.X - MeshBox.Min.X,
                                   MeshBox.Max.Y - MeshBox.Min.Y);
        }
        for (int32 R = 0; R < 4; ++R)
        {
            if (FCString::Strcmp(Part, RopeParts[R]) == 0)
            {
                RopeActor[R] = A;
                RopeCentreZ[R] = MeshBox.GetCenter().Z;
            }
        }
        Spawned.Add(A);
    }
    if (Spawned.Num() == 0)
    {
        UE_LOG(LogTemp, Warning,
               TEXT("UppercutArenaPresentation: arena OFF (no ring meshes)"));
        return Out;
    }

    const double Scale = (SpanWidth > 1.0) ? AxisCm / SpanWidth : 1.0;
    const FVector Centre = Bounds.GetCenter();
    const FVector Target(AxisCm / 2.0, 0.0, 0.0);
    const double DepthNudgeCm = 2.0;
    for (AStaticMeshActor* A : Spawned)
    {
        A->SetActorScale3D(FVector(Scale));
        const bool bIsCanvas = (A->GetStaticMeshComponent()->GetStaticMesh()
            && A->GetStaticMeshComponent()->GetStaticMesh()->GetName() == CanvasPart);
        A->SetActorLocation(FVector(Target.X - Centre.X * Scale,
                                    Target.Y - Centre.Y * Scale,
                                    -CanvasTop * Scale + (bIsCanvas ? 0.0 : DepthNudgeCm)));
    }
    for (int32 R = 0; R < 4; ++R)
    {
        if (!RopeActor[R]) { continue; }
        const FVector L = RopeActor[R]->GetActorLocation();
        RopeActor[R]->SetActorLocation(
            FVector(L.X, L.Y, RopeHeightCm[R] - RopeCentreZ[R] * Scale));
    }

    Out.bSpawned = true;
    Out.PartCount = Spawned.Num();
    Out.Scale = Scale;
    UE_LOG(LogTemp, Display,
           TEXT("UppercutArenaPresentation: arena ON (%d parts, ropes %.2f m a side, "
                "scale %.5f)"),
           Spawned.Num(), SpanWidth * Scale / 100.0, Scale);
    return Out;
}

USkeletalMesh* UppercutLoadFighterMannequinMesh(int32 FighterIndex)
{
    static const TCHAR* MeshPath[2] = {
        TEXT("/Game/BoxingAttacks/Demo/Mannequins/Meshes/SKM_Manny.SKM_Manny"),
        TEXT("/Game/BoxingAttacks/Demo/Mannequins/Meshes/SKM_Quinn.SKM_Quinn") };
    const int32 I = FMath::Clamp(FighterIndex, 0, 1);
    return LoadObject<USkeletalMesh>(nullptr, MeshPath[I]);
}

bool UppercutLoadFighterActionClips(TMap<FString, UAnimSequence*>& OutClips)
{
    OutClips.Reset();
    static const TCHAR* Map[][2] = {
        { TEXT("jab_lead"),           TEXT("Attacks/In-Place/KB_Jab-L_T_IP") },
        { TEXT("cross_rear"),         TEXT("Attacks/In-Place/KB_Cross-R_T_IP") },
        { TEXT("hook_lead"),          TEXT("Attacks/In-Place/KB_Hook-L_T_IP") },
        { TEXT("uppercut_rear"),      TEXT("Attacks/In-Place/KB_Uppercut-R_T_IP") },
        { TEXT("body_straight_rear"), TEXT("Attacks/In-Place/KB_Cross-RB_T_IP") },
        { TEXT("step_in"),            TEXT("Common/In-Place/KB_Walk-F_T") },
        { TEXT("step_out"),           TEXT("Common/In-Place/KB_Walk-B_T") },
        { TEXT("step_lateral"),       TEXT("Common/In-Place/KB_Walk-L_T") },
        { TEXT("guard"),              TEXT("Defence/In-Place/KB_Guard_T") },
        { TEXT("block_high"),         TEXT("Reactions/In-Place/KB_Block-H_T_IP") },
        { TEXT("block_body"),         TEXT("Reactions/In-Place/KB_Block-B_T_IP") },
        { TEXT("hit_high"),           TEXT("Reactions/In-Place/KB_Hit-H_T_IP") },
        { TEXT("hit_body"),           TEXT("Reactions/In-Place/KB_Hit-B_T_IP") },
    };
    for (int32 N = 0; N < UE_ARRAY_COUNT(Map); ++N)
    {
        const FString Path = FString(TEXT("/Game/BoxingAttacks/TRADITIONAL/")) + Map[N][1];
        const FString Full = Path + TEXT(".") + FPaths::GetCleanFilename(Path);
        UAnimSequence* A = LoadObject<UAnimSequence>(nullptr, *Full);
        if (!A)
        {
            OutClips.Reset();
            UE_LOG(LogTemp, Warning,
                   TEXT("UppercutArenaPresentation: mannequin clips OFF (%s missing)"),
                   *Full);
            return false;
        }
        OutClips.Add(Map[N][0], A);
        A->AddToRoot();  // map is not a UPROPERTY; keep GC off the clips
    }
    return OutClips.Num() > 0;
}
// [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 03:53 UTC | END ]
