// [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 06:25 UTC | START ]
#include "UppercutBoutDirector.h"

#include "Camera/CameraActor.h"
// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 17:32 UTC | edit: mannequin visual pass ]
#include "Animation/AnimSequence.h"
#include "Animation/AnimSingleNodeInstance.h"
#include "Animation/SkeletalMeshActor.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/SkeletalMesh.h"
// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 17:32 UTC | edit end ]
#include "Components/StaticMeshComponent.h"
#include "Dom/JsonObject.h"
#include "Engine/DirectionalLight.h"
#include "Engine/StaticMeshActor.h"
#include "GameFramework/PlayerController.h"
#include "HAL/FileManager.h"
#include "Kismet/GameplayStatics.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Misc/CommandLine.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"
#include "UnrealClient.h"

// SHA-256 (FIPS 180-4), file-local like every evidence probe's.
namespace UppercutRenderSha256
{
    static const uint32 K[64] = {
        0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
        0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
        0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
        0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
        0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
        0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
        0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
        0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2 };

    static uint32 Rotr(uint32 X, uint32 N) { return (X >> N) | (X << (32 - N)); }

    static void Hash(const uint8* Data, uint64 Len, uint8 Out[32])
    {
        uint32 H[8] = { 0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,
                        0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19 };
        const uint64 BitLen = Len * 8;
        const uint64 Total = ((Len + 8) / 64 + 1) * 64;
        TArray<uint8> Msg;
        Msg.SetNumZeroed((int32)Total);
        FMemory::Memcpy(Msg.GetData(), Data, Len);
        Msg[(int32)Len] = 0x80;
        for (int32 i = 0; i < 8; ++i)
        {
            Msg[(int32)(Total - 1 - i)] = (uint8)((BitLen >> (8 * i)) & 0xff);
        }
        for (uint64 Chunk = 0; Chunk < Total; Chunk += 64)
        {
            uint32 W[64];
            for (int32 i = 0; i < 16; ++i)
            {
                const uint8* P = Msg.GetData() + Chunk + i * 4;
                W[i] = ((uint32)P[0] << 24) | ((uint32)P[1] << 16) | ((uint32)P[2] << 8) | (uint32)P[3];
            }
            for (int32 i = 16; i < 64; ++i)
            {
                const uint32 S0 = Rotr(W[i - 15], 7) ^ Rotr(W[i - 15], 18) ^ (W[i - 15] >> 3);
                const uint32 S1 = Rotr(W[i - 2], 17) ^ Rotr(W[i - 2], 19) ^ (W[i - 2] >> 10);
                W[i] = W[i - 16] + S0 + W[i - 7] + S1;
            }
            uint32 A = H[0], B = H[1], C = H[2], D = H[3], E = H[4], F = H[5], G = H[6], Hh = H[7];
            for (int32 i = 0; i < 64; ++i)
            {
                const uint32 S1 = Rotr(E, 6) ^ Rotr(E, 11) ^ Rotr(E, 25);
                const uint32 Ch = (E & F) ^ (~E & G);
                const uint32 T1 = Hh + S1 + Ch + K[i] + W[i];
                const uint32 S0 = Rotr(A, 2) ^ Rotr(A, 13) ^ Rotr(A, 22);
                const uint32 Mj = (A & B) ^ (A & C) ^ (B & C);
                const uint32 T2 = S0 + Mj;
                Hh = G; G = F; F = E; E = D + T1; D = C; C = B; B = A; A = T1 + T2;
            }
            H[0] += A; H[1] += B; H[2] += C; H[3] += D;
            H[4] += E; H[5] += F; H[6] += G; H[7] += Hh;
        }
        for (int32 i = 0; i < 8; ++i)
        {
            Out[i * 4 + 0] = (uint8)(H[i] >> 24); Out[i * 4 + 1] = (uint8)(H[i] >> 16);
            Out[i * 4 + 2] = (uint8)(H[i] >> 8);  Out[i * 4 + 3] = (uint8)(H[i]);
        }
    }
}

namespace
{
    const uint32 LcgA = 1664525u;
    const uint32 LcgC = 1013904223u;
    const uint64 FnvOffset = 14695981039346656037ull;
    const uint64 FnvPrime = 1099511628211ull;

    int64 Q(double V) { return (int64)FMath::RoundToDouble(V * 10000.0); }

    struct FKMove
    {
        int64 Cost = 0;
        int32 Frames = 0, Startup = 0, Active = 0;
        int64 Ext = 0;
        FString Height, Region, Hand;
        bool bPunch = false;
    };
}

// Everything the sim owns, hidden from the header.
struct AUppercutBoutDirector::FImpl
{
    FString Sha[8];
    TArray<int64> BMin, BMax;
    int64 Hyst = 0, Axis = 0, Ropes = 0, RopeRetreat = 0, MinSep = 0, Stride = 0;
    int64 DirAdvance = 0, DirRetreat = 0, DirLateral = 0, DirExhausted = 0;
    int64 Mobility = 0, Hold = 0, StMax = 0, Regen = 0, ExhaustedQ = 0;
    int64 HalfDepth = 0, PlaneOff = 0, Retracted = 0;
    int32 Interval = 0;
    double RuToCm = 130.0;
    TSet<FString> Covered;
    TMap<FString, FKMove> Moves;
    double FCost = 0, FRegen = 0, FMax = 0, FHold = 0;

    // live state
    int64 Pos[2];
    int64 St[2];
    int32 Committed[2] = { 0, 0 };
    FString PunchMove[2];
    int32 PunchT0[2] = { 0, 0 };
    int32 Band = 2;
    uint32 X = 0;
    uint64 Fnv = FnvOffset;
    int64 Rows = 0, Punches = 0, Blocked = 0, Landed = 0, Whiffed = 0;
    int64 Steps = 0, Held = 0, Idles = 0, Transitions = 0;
    FString Out;
    TArray<int32> ShotTicks;
    int32 ShotsTaken = 0;

    // [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 17:32 UTC | edit: pose-only mirrors ]
    // Write-only from the sim's point of view: StepSim records what it just
    // decided, PoseMannequins reads it. NOTHING in the sim's arithmetic ever
    // reads these fields, and nothing here reaches the evidence stream - the
    // byte-identical re-run against Phase K's canon is the proof of both.
    FString LastAction[2];
    int32 ActionT0[2] = { 0, 0 };
    FString ReactClip[2];      // block/hit reaction chosen at the moment of contact
    int32 ReactT0[2] = { -1000, -1000 };

    void Emit(const FString& Row)
    {
        Out += Row;
        const FTCHARToUTF8 Utf8(*Row);
        const uint8* P = (const uint8*)Utf8.Get();
        for (int32 b = 0; b < Utf8.Length(); ++b) { Fnv = (Fnv ^ P[b]) * FnvPrime; }
    }

    int64 ExtAt(const FKMove& Mv, int32 M) const
    {
        return Retracted + ((Mv.Ext - Retracted) * M) / (Mv.Startup + Mv.Active);
    }
};

static bool LoadJsonK(const FString& Path, TSharedPtr<FJsonObject>& OutRoot, FString& OutSha)
{
    TArray<uint8> Bytes;
    if (!FFileHelper::LoadFileToArray(Bytes, *Path)) { return false; }
    uint8 Sha[32];
    UppercutRenderSha256::Hash(Bytes.GetData(), Bytes.Num(), Sha);
    OutSha.Reset();
    for (int32 i = 0; i < 32; ++i) { OutSha += FString::Printf(TEXT("%02x"), Sha[i]); }
    FString Text;
    FFileHelper::BufferToString(Text, Bytes.GetData(), Bytes.Num());
    const TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(Text);
    return FJsonSerializer::Deserialize(Reader, OutRoot) && OutRoot.IsValid();
}

AUppercutBoutDirector::AUppercutBoutDirector()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AUppercutBoutDirector::BeginPlay()
{
    Super::BeginPlay();
    Impl = MakeShared<FImpl>();
    if (!LoadCanonAndParams())
    {
        UE_LOG(LogTemp, Error, TEXT("UppercutBoutDirector: canon/params failed; exiting"));
        FPlatformMisc::RequestExit(false);
        return;
    }
    BuildScene();
    bReady = true;
}
// [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 06:25 UTC | continued in this file ]

bool AUppercutBoutDirector::LoadCanonAndParams()
{
    const TCHAR* Cmd = FCommandLine::Get();
    FParse::Value(Cmd, TEXT("seed="), Seed);
    FParse::Value(Cmd, TEXT("ticks="), Ticks);
    FParse::Value(Cmd, TEXT("repo="), Repo);
    FParse::Value(Cmd, TEXT("out="), OutPath);
    FParse::Value(Cmd, TEXT("shots="), ShotDir);
    // [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 17:32 UTC | edit: marker view ]
    bShowMarkers = FParse::Param(Cmd, TEXT("markers"));
    // [ edit end ]
    if (Ticks <= 0 || Repo.IsEmpty() || OutPath.IsEmpty()) { return false; }

    const TCHAR* Rel[8] = { TEXT("data/movement_model.json"), TEXT("data/condition_model.json"),
                            TEXT("data/guard_evasion_model.json"), TEXT("data/cpu_decision_model.json"),
                            TEXT("data/moves/generic_sandbox_moves.json"), TEXT("data/animation_model.json"),
                            TEXT("data/collision_model.json"), TEXT("data/pose_geometry.json") };
    TSharedPtr<FJsonObject> Root[8];
    FImpl& S = *Impl;
    for (int32 i = 0; i < 8; ++i)
    {
        if (!LoadJsonK(Repo / Rel[i], Root[i], S.Sha[i])) { return false; }
    }
    const TSharedPtr<FJsonObject> RB = Root[0]->GetObjectField(TEXT("range_bands"));
    for (const TSharedPtr<FJsonValue>& V : RB->GetArrayField(TEXT("bands")))
    {
        const TSharedPtr<FJsonObject> B = V->AsObject();
        S.BMin.Add(Q(B->GetNumberField(TEXT("min_ru"))));
        S.BMax.Add(B->HasTypedField<EJson::Number>(TEXT("max_ru"))
                   ? Q(B->GetNumberField(TEXT("max_ru"))) : (int64)990000);
    }
    S.Hyst = Q(RB->GetNumberField(TEXT("hysteresis_ru")));
    const TSharedPtr<FJsonObject> Track =
        Root[0]->GetObjectField(TEXT("ring"))->GetObjectField(TEXT("track"));
    S.Axis = Q(Track->GetNumberField(TEXT("axis_length_ru")));
    S.Ropes = Q(Track->GetNumberField(TEXT("back_to_ropes_ru")));
    S.RopeRetreat = Q(Track->GetNumberField(TEXT("rope_retreat_multiplier")));
    S.MinSep = Q(Root[0]->GetObjectField(TEXT("separation"))
                 ->GetNumberField(TEXT("min_center_distance_ru")));
    const TSharedPtr<FJsonObject> Loco = Root[0]->GetObjectField(TEXT("locomotion"));
    for (const TSharedPtr<FJsonValue>& V : Loco->GetArrayField(TEXT("modes")))
    {
        const TSharedPtr<FJsonObject> M = V->AsObject();
        if (M->GetStringField(TEXT("posture_mode")) == TEXT("boxing_steps"))
        {
            S.Stride = Q(M->GetNumberField(TEXT("stride_length_ru")));
        }
    }
    const TSharedPtr<FJsonObject> Dir = Loco->GetObjectField(TEXT("directional"));
    S.DirAdvance = Q(Dir->GetNumberField(TEXT("advance_stride_multiplier")));
    S.DirRetreat = Q(Dir->GetNumberField(TEXT("retreat_stride_multiplier")));
    S.DirLateral = Q(Dir->GetNumberField(TEXT("lateral_stride_multiplier")));
    S.DirExhausted = Q(Dir->GetNumberField(TEXT("exhausted_stride_multiplier")));
    double RefSpanM = 1.3;
    Root[0]->GetObjectField(TEXT("spatial_units"))
        ->TryGetNumberField(TEXT("reference_reach_span_m"), RefSpanM);
    S.RuToCm = RefSpanM * 100.0;

    const TSharedPtr<FJsonObject> St = Root[1]->GetObjectField(TEXT("stamina"));
    S.StMax = Q(St->GetNumberField(TEXT("max")));
    S.Regen = Q(St->GetNumberField(TEXT("regen_per_tick_idle")));
    S.ExhaustedQ = (int64)FMath::RoundToDouble(
        (double)S.StMax * St->GetNumberField(TEXT("exhausted_threshold_fraction")));
    S.FMax = St->GetNumberField(TEXT("max"));
    S.FRegen = St->GetNumberField(TEXT("regen_per_tick_idle"));

    TSharedPtr<FJsonObject> HgExtents;
    for (const TSharedPtr<FJsonValue>& V : Root[2]->GetArrayField(TEXT("postures")))
    {
        const TSharedPtr<FJsonObject> P = V->AsObject();
        if (P->GetStringField(TEXT("id")) == TEXT("high_guard"))
        {
            S.Mobility = Q(P->GetNumberField(TEXT("mobility_multiplier")));
            S.Hold = Q(P->GetNumberField(TEXT("stamina_per_tick")));
            S.FHold = P->GetNumberField(TEXT("stamina_per_tick"));
            HgExtents = P->GetObjectField(TEXT("extents"));
        }
    }
    S.Interval = (int32)Root[3]->GetObjectField(TEXT("reaction"))
        ->GetNumberField(TEXT("decision_interval_ticks"));

    S.HalfDepth = Q(Root[7]->GetObjectField(TEXT("body"))->GetNumberField(TEXT("half_depth_ru")));
    const TSharedPtr<FJsonObject> G = Root[7]->GetObjectField(TEXT("guard"));
    S.PlaneOff = Q(G->GetNumberField(TEXT("plane_offset_ru")));
    const double Thr = G->GetNumberField(TEXT("plane_interception_min_extent"));
    S.Retracted = Q(Root[7]->GetObjectField(TEXT("fist"))->GetNumberField(TEXT("retracted_ru")));
    for (const TSharedPtr<FJsonValue>& V :
         Root[6]->GetObjectField(TEXT("volumes"))->GetArrayField(TEXT("guard_volumes")))
    {
        const TSharedPtr<FJsonObject> GV = V->AsObject();
        double ExtVal = 0.0;
        if (HgExtents.IsValid()
            && HgExtents->TryGetNumberField(GV->GetStringField(TEXT("id")), ExtVal)
            && ExtVal >= Thr)
        {
            S.Covered.Add(GV->GetStringField(TEXT("height_class")));
        }
    }
    TMap<FString, FString> HeightByInteraction;
    for (const TSharedPtr<FJsonValue>& V :
         Root[7]->GetArrayField(TEXT("height_by_guard_interaction")))
    {
        const TSharedPtr<FJsonObject> E = V->AsObject();
        HeightByInteraction.Add(E->GetStringField(TEXT("guard_interaction")),
                                E->GetStringField(TEXT("height_class")));
    }
    TMap<FString, int64> ExtByMove;
    for (const TSharedPtr<FJsonValue>& V :
         Root[7]->GetObjectField(TEXT("fist"))->GetArrayField(TEXT("extension_by_move")))
    {
        const TSharedPtr<FJsonObject> E = V->AsObject();
        ExtByMove.Add(E->GetStringField(TEXT("move_id")), Q(E->GetNumberField(TEXT("extended_ru"))));
    }
    TMap<FString, TSharedPtr<FJsonObject>> Anim;
    for (const TSharedPtr<FJsonValue>& V : Root[5]->GetArrayField(TEXT("move_animations")))
    {
        const TSharedPtr<FJsonObject> A = V->AsObject();
        Anim.Add(A->GetStringField(TEXT("move_id")), A);
    }
    const TCHAR* PunchIds[5] = { TEXT("jab_lead"), TEXT("cross_rear"), TEXT("hook_lead"),
                                 TEXT("uppercut_rear"), TEXT("body_straight_rear") };
    for (const TSharedPtr<FJsonValue>& V : Root[4]->GetArrayField(TEXT("moves")))
    {
        const TSharedPtr<FJsonObject> M = V->AsObject();
        const FString Id = M->GetStringField(TEXT("id"));
        bool bIsPunch = false;
        for (const TCHAR* P : PunchIds) { bIsPunch |= (Id == P); }
        const bool bIsStep = Id == TEXT("step_in") || Id == TEXT("step_out")
            || Id == TEXT("step_lateral");
        if (!bIsPunch && !bIsStep) { continue; }
        FKMove Mv;
        Mv.Cost = Q(M->GetNumberField(TEXT("stamina_cost")));
        if (bIsPunch)
        {
            const TSharedPtr<FJsonObject> A = Anim[Id];
            Mv.bPunch = true;
            Mv.Startup = (int32)A->GetNumberField(TEXT("startup_ticks"));
            Mv.Active = (int32)A->GetNumberField(TEXT("active_ticks"));
            Mv.Frames = Mv.Startup + Mv.Active + (int32)A->GetNumberField(TEXT("recovery_ticks"));
            Mv.Ext = ExtByMove[Id];
            Mv.Height = HeightByInteraction[M->GetStringField(TEXT("guard_interaction"))];
            Mv.Region = M->GetArrayField(TEXT("target_regions"))[0]->AsString();
            Mv.Hand = M->GetStringField(TEXT("hand"));
            if (Id == TEXT("jab_lead")) { S.FCost = M->GetNumberField(TEXT("stamina_cost")); }
        }
        else
        {
            Mv.Frames = (int32)M->GetNumberField(TEXT("startup_frames"))
                      + (int32)M->GetNumberField(TEXT("recovery_frames"));
        }
        S.Moves.Add(Id, Mv);
    }

    // headers + initial state
    S.Out += TEXT("H|phase=K\n");
    const TCHAR* ShaName[8] = { TEXT("movement"), TEXT("condition"), TEXT("guard"), TEXT("cpu"),
                                TEXT("moves"), TEXT("animation"), TEXT("collision"), TEXT("pose") };
    for (int32 i = 0; i < 8; ++i)
    {
        S.Out += FString::Printf(TEXT("H|canon_%s=%s\n"), ShaName[i], *S.Sha[i]);
    }
    S.Out += FString::Printf(TEXT("H|seed=%u\nH|ticks=%d\nH|interval=%d\n"),
                             Seed, Ticks, S.Interval);
    S.Pos[0] = S.Axis / 2 - 4500;
    S.Pos[1] = S.Axis / 2 + 4500;
    S.St[0] = S.St[1] = S.StMax;
    S.X = Seed;
    S.ShotTicks = { 240, 900, 1800, 3000, 4200 };
    return true;
}
// [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 06:25 UTC | continued ]

static AStaticMeshActor* SpawnShape(UWorld* World, const TCHAR* MeshPath,
                                    const FVector& Loc, const FVector& Scale,
                                    const FLinearColor& Color)
{
    UStaticMesh* Mesh = LoadObject<UStaticMesh>(nullptr, MeshPath);
    if (!Mesh) { return nullptr; }
    AStaticMeshActor* A = World->SpawnActor<AStaticMeshActor>(Loc, FRotator::ZeroRotator);
    if (!A) { return nullptr; }
    A->SetMobility(EComponentMobility::Movable);
    UStaticMeshComponent* Comp = A->GetStaticMeshComponent();
    Comp->SetStaticMesh(Mesh);
    Comp->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    A->SetActorScale3D(Scale);
    if (UMaterialInstanceDynamic* Mid = Comp->CreateAndSetMaterialInstanceDynamic(0))
    {
        Mid->SetVectorParameterValue(TEXT("Color"), Color);
    }
    return A;
}

void AUppercutBoutDirector::BuildScene()
{
    UWorld* World = GetWorld();
    const FImpl& S = *Impl;
    const double MidCm = (S.Axis / 2) / 10000.0 * S.RuToCm;

    // floor and the two rope-line posts marking the track's ends
    SpawnShape(World, TEXT("/Engine/BasicShapes/Cube.Cube"),
               FVector(MidCm, 0, -25), FVector(40, 40, 0.5), FLinearColor(0.16f, 0.28f, 0.42f));
    const double AxisCm = S.Axis / 10000.0 * S.RuToCm;
    for (int32 e = 0; e < 2; ++e)
    {
        SpawnShape(World, TEXT("/Engine/BasicShapes/Cylinder.Cylinder"),
                   FVector(e == 0 ? 0.0 : AxisCm, 0, 60), FVector(0.15, 0.15, 1.2),
                   FLinearColor(0.8f, 0.1f, 0.1f));
    }
    // fighters: torso capsule, head sphere, two glove spheres apiece
    const FLinearColor Cols[2] = { FLinearColor(0.85f, 0.25f, 0.1f),
                                   FLinearColor(0.1f, 0.35f, 0.9f) };
    for (int32 i = 0; i < 2; ++i)
    {
        // Cylinder, not Capsule: /Engine/BasicShapes/Capsule is absent from
        // runtime engine content in 5.8 (found by its Failed-to-find warning
        // on the first rendered run; Cube/Sphere/Cylinder all load).
        Torso[i] = SpawnShape(World, TEXT("/Engine/BasicShapes/Cylinder.Cylinder"),
                              FVector::ZeroVector, FVector(0.55, 0.55, 0.95), Cols[i]);
        Head[i] = SpawnShape(World, TEXT("/Engine/BasicShapes/Sphere.Sphere"),
                             FVector::ZeroVector, FVector(0.3, 0.3, 0.3), Cols[i]);
        GloveLead[i] = SpawnShape(World, TEXT("/Engine/BasicShapes/Sphere.Sphere"),
                                  FVector::ZeroVector, FVector(0.2, 0.2, 0.2),
                                  FLinearColor(0.9f, 0.8f, 0.1f));
        GloveRear[i] = SpawnShape(World, TEXT("/Engine/BasicShapes/Sphere.Sphere"),
                                  FVector::ZeroVector, FVector(0.2, 0.2, 0.2),
                                  FLinearColor(0.9f, 0.8f, 0.1f));
    }
    // key light and a soft fill from the far side
    if (ADirectionalLight* L = World->SpawnActor<ADirectionalLight>(
            FVector(0, 0, 500), FRotator(-50, 40, 0)))
    {
        L->SetMobility(EComponentMobility::Movable);
    }
    if (ADirectionalLight* L2 = World->SpawnActor<ADirectionalLight>(
            FVector(0, 0, 500), FRotator(-30, 220, 0)))
    {
        L2->SetMobility(EComponentMobility::Movable);
        L2->SetBrightness(1.2f);
    }
    // broadcast camera, side-on
    Camera = World->SpawnActor<ACameraActor>(
        FVector(MidCm, -620.0, 200.0), FRotator(-8.0, 90.0, 0));
    // [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 17:32 UTC | edit: mannequin visual pass ]
    BuildMannequins();
    if (bMannequins && !bShowMarkers)
    {
        // The primitives stop being the picture and become the instrument: still
        // spawned, still posed, still exactly where they were - just not drawn.
        // -markers brings the Phase K view back for anyone auditing the poses.
        for (int32 i = 0; i < 2; ++i)
        {
            if (Torso[i]) { Torso[i]->SetActorHiddenInGame(true); }
            if (Head[i]) { Head[i]->SetActorHiddenInGame(true); }
            if (GloveLead[i]) { GloveLead[i]->SetActorHiddenInGame(true); }
            if (GloveRear[i]) { GloveRear[i]->SetActorHiddenInGame(true); }
        }
    }
    // [ edit end ]
}

// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 17:32 UTC | START ]
// The mannequin visual pass. Two rules hold the truth boundary in place here:
//
//   1. Only In-Place clips are consumed. The pack ships root-motion variants of
//      every step; taking them would let an animation move a fighter, and a
//      fighter's position is the sim's to own. The rejection is on principle,
//      not preference - a root-motion step would be presentation writing to the
//      fight.
//   2. Clip time is a function of sim state, never of DeltaSeconds. Each clip is
//      SCRUBBED to the sim's own progress through the move (age / commit frames),
//      so the vendor's authored timing is stretched onto our timing. Our punch
//      frames are the design; theirs are a shape to borrow. A dropped frame moves
//      nothing, because nothing here integrates over wall clock.
//
// SOUTHPAW clips exist in the pack and are deliberately unused: stance is not in
// the sim's state model yet, and presentation does not get to invent a fact the
// fight does not have.
UAnimSequence* AUppercutBoutDirector::Clip(const TCHAR* Rel)
{
    const FString Path = FString(TEXT("/Game/BoxingAttacks/TRADITIONAL/")) + Rel;
    const FString Full = Path + TEXT(".") + FPaths::GetCleanFilename(Path);
    UAnimSequence* A = LoadObject<UAnimSequence>(nullptr, *Full);
    if (!A)
    {
        UE_LOG(LogTemp, Warning, TEXT("UppercutBoutDirector: clip missing: %s"), *Full);
        return nullptr;
    }
    A->AddToRoot();   // the map below is not a UPROPERTY; keep GC off the clips
    return A;
}

void AUppercutBoutDirector::BuildMannequins()
{
    UWorld* World = GetWorld();
    // Manny and Quinn: the two fighters must be told apart at a glance, and the
    // pack ships both on the one skeleton, so distinguishing them costs nothing.
    const TCHAR* MeshPath[2] = {
        TEXT("/Game/BoxingAttacks/Demo/Mannequins/Meshes/SKM_Manny.SKM_Manny"),
        TEXT("/Game/BoxingAttacks/Demo/Mannequins/Meshes/SKM_Quinn.SKM_Quinn") };

    // sim action (and lane-derived reaction) -> the clip that shows it
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
    for (int32 n = 0; n < UE_ARRAY_COUNT(Map); ++n)
    {
        UAnimSequence* A = Clip(Map[n][1]);
        if (!A)
        {
            // All or nothing: a half-clothed fighter is worse evidence than a
            // primitive one, and the primitives are still standing behind this.
            UE_LOG(LogTemp, Warning,
                   TEXT("UppercutBoutDirector: mannequins OFF (clip load failed)"));
            return;
        }
        Clips.Add(Map[n][0], A);
    }
    for (int32 i = 0; i < 2; ++i)
    {
        USkeletalMesh* Mesh = LoadObject<USkeletalMesh>(nullptr, MeshPath[i]);
        if (!Mesh)
        {
            UE_LOG(LogTemp, Warning,
                   TEXT("UppercutBoutDirector: mannequins OFF (mesh %s missing)"),
                   MeshPath[i]);
            return;
        }
        Mesh->AddToRoot();
        ASkeletalMeshActor* A = World->SpawnActor<ASkeletalMeshActor>(
            FVector::ZeroVector, FRotator::ZeroRotator);
        if (!A) { return; }
        USkeletalMeshComponent* C = A->GetSkeletalMeshComponent();
        // ASkeletalMeshActor has no SetMobility of its own (unlike AStaticMeshActor);
        // mobility lives on the component, which is also the actor's root here.
        C->SetMobility(EComponentMobility::Movable);
        C->SetSkeletalMeshAsset(Mesh);
        C->SetCollisionEnabled(ECollisionEnabled::NoCollision);
        C->VisibilityBasedAnimTickOption =
            EVisibilityBasedAnimTickOption::AlwaysTickPoseAndRefreshBones;
        C->SetAnimationMode(EAnimationMode::AnimationSingleNode);
        Fighter[i] = A;
    }
    bMannequins = true;
    UE_LOG(LogTemp, Display, TEXT("UppercutBoutDirector: mannequins ON (%d clips)"),
           Clips.Num());
}

void AUppercutBoutDirector::PoseMannequins()
{
    if (!bMannequins) { return; }
    const FImpl& S = *Impl;
    const int32 T = SimTick;
    const int32 ReactFrames = 20;   // how long a reaction reads for, in sim ticks
    for (int32 i = 0; i < 2; ++i)
    {
        if (!Fighter[i]) { continue; }
        const double Xcm = S.Pos[i] / 10000.0 * S.RuToCm;
        Fighter[i]->SetActorLocation(FVector(Xcm, 0.0, 0.0));
        Fighter[i]->SetActorRotation(FRotator(0.0, (i == 0) ? 0.0 : 180.0, 0.0));

        UAnimSequence* A = nullptr;
        double Alpha = 0.0;
        bool bLoop = false;

        // A reaction outranks the fighter's own last decision only if it is newer:
        // getting hit interrupts what you were doing, but throwing after you were
        // hit means you have recovered.
        const int32 ReactAge = T - S.ReactT0[i];
        if (!S.ReactClip[i].IsEmpty() && ReactAge >= 0 && ReactAge < ReactFrames
            && S.ReactT0[i] >= S.ActionT0[i])
        {
            A = Clips.FindRef(S.ReactClip[i]);
            Alpha = (double)ReactAge / (double)ReactFrames;
        }
        if (!A && !S.LastAction[i].IsEmpty())
        {
            const FKMove* Mv = S.Moves.Find(S.LastAction[i]);
            const int32 Age = T - S.ActionT0[i];
            if (Mv && Mv->Frames > 0 && Age >= 0 && Age <= Mv->Frames)
            {
                A = Clips.FindRef(S.LastAction[i]);   // "idle" has no clip: falls through
                Alpha = (double)Age / (double)Mv->Frames;
            }
        }
        if (!A) { A = Clips.FindRef(TEXT("guard")); bLoop = true; }
        if (!A) { continue; }

        USkeletalMeshComponent* C = Fighter[i]->GetSkeletalMeshComponent();
        const double Len = FMath::Max(0.0001, (double)A->GetPlayLength());
        // The idle offset is the fighter's INDEX, not a random number: two boxers
        // breathing in lockstep looks wrong, and nothing here may consume the RNG.
        const double Time = bLoop
            ? FMath::Fmod(T / 60.0 + i * 0.37, Len)
            : FMath::Clamp(Alpha, 0.0, 1.0) * Len;
        UAnimSingleNodeInstance* SN = C->GetSingleNodeInstance();
        if (!SN || SN->GetAnimationAsset() != A) { C->SetAnimation(A); }
        C->SetPosition((float)Time, false);
        C->TickAnimation(0.0f, false);
        C->RefreshBoneTransforms();
    }
}
// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 17:32 UTC | END ]

void AUppercutBoutDirector::StepSim()
{
    FImpl& S = *Impl;
    const int32 T = SimTick;
    for (int32 I = 0; I < 2; ++I)
    {
        if (!S.PunchMove[I].IsEmpty())
        {
            const FKMove& Mv = S.Moves[S.PunchMove[I]];
            const int32 Kk = T - S.PunchT0[I];
            if (Kk > Mv.Startup && Kk <= Mv.Startup + Mv.Active)
            {
                const int64 TipExt = S.ExtAt(Mv, Kk);
                int64 Tip, Plane, Surface;
                bool bPlaneX, bSurfaceX;
                if (I == 0)
                {
                    Tip = S.Pos[0] + TipExt;
                    Surface = S.Pos[1] - S.HalfDepth;
                    Plane = Surface - S.PlaneOff;
                    bPlaneX = Tip >= Plane;
                    bSurfaceX = Tip >= Surface;
                }
                else
                {
                    Tip = S.Pos[1] - TipExt;
                    Surface = S.Pos[0] + S.HalfDepth;
                    Plane = Surface + S.PlaneOff;
                    bPlaneX = Tip <= Plane;
                    bSurfaceX = Tip <= Surface;
                }
                const TCHAR* Result = nullptr;
                FString Region = TEXT("-");
                if (bPlaneX && S.Covered.Contains(Mv.Height))
                {
                    Result = TEXT("blocked"); ++S.Blocked;
                }
                else if (bSurfaceX)
                {
                    Result = TEXT("landed"); Region = Mv.Region; ++S.Landed;
                }
                else if (Kk == Mv.Startup + Mv.Active)
                {
                    Result = TEXT("whiffed"); ++S.Whiffed;
                }
                if (Result)
                {
                    ++S.Rows;
                    S.Emit(FString::Printf(TEXT("P|%d|%d|%s|%s|%s|%d|%lld|%lld|%lld\n"),
                        T, I, *S.PunchMove[I], Result, *Region, Kk, Tip, Plane, Surface));
                    // [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 17:32 UTC | edit: pose-only ]
                    // The DEFENDER reacts, and which reaction he plays is decided by the
                    // lane the punch arrived in - not by which punch it was. A blocked
                    // high punch is a high block; a landed body punch is a body hit. The
                    // guard model is what the audience sees.
                    const int32 D = 1 - I;
                    if (Result[0] != TEXT('w'))
                    {
                        const bool bLow = (Mv.Height == TEXT("low"));
                        S.ReactClip[D] = FString::Printf(TEXT("%s_%s"),
                            (Result[0] == TEXT('b')) ? TEXT("block") : TEXT("hit"),
                            bLow ? TEXT("body") : TEXT("high"));
                        S.ReactT0[D] = T;
                    }
                    // [ edit end ]
                    S.PunchMove[I].Reset();
                }
            }
            else if (Kk > Mv.Startup + Mv.Active)
            {
                S.PunchMove[I].Reset();
            }
        }
        bool bHeld = false;
        if (S.Committed[I] > 0)
        {
            --S.Committed[I];
            bHeld = true;
        }
        else
        {
            S.St[I] = FMath::Min(S.StMax, S.St[I] + S.Regen);
            S.St[I] = FMath::Max((int64)0, S.St[I] - S.Hold);
        }
        if (T % S.Interval != 0) { continue; }
        if (bHeld)
        {
            ++S.Held; ++S.Rows;
            S.Emit(FString::Printf(TEXT("D|%d|%d|held|0|%lld|%lld|%lld|%d|%lld|%lld|-\n"),
                T, I, S.Pos[0], S.Pos[1], S.Pos[1] - S.Pos[0], S.Band, S.St[0], S.St[1]));
            continue;
        }
        S.X = LcgA * S.X + LcgC;
        const int32 Choice = (int32)(S.X % 9u);
        static const TCHAR* ActionName[9] = { TEXT("step_in"), TEXT("step_out"),
            TEXT("step_lateral"), TEXT("jab_lead"), TEXT("cross_rear"), TEXT("hook_lead"),
            TEXT("uppercut_rear"), TEXT("body_straight_rear"), TEXT("idle") };
        FString Flags;
        if (Choice == 8)
        {
            ++S.Idles;
        }
        else if (Choice >= 3)
        {
            const FString Mid = ActionName[Choice];
            const FKMove& Mv = S.Moves[Mid];
            S.St[I] = FMath::Max((int64)0, S.St[I] - Mv.Cost);
            S.Committed[I] = Mv.Frames;
            S.PunchMove[I] = Mid;
            S.PunchT0[I] = T;
            ++S.Punches;
        }
        else
        {
            const FString Mid = ActionName[Choice];
            const FKMove& Mv = S.Moves[Mid];
            S.St[I] = FMath::Max((int64)0, S.St[I] - Mv.Cost);
            S.Committed[I] = Mv.Frames;
            ++S.Steps;
            int64 Mul = (Choice == 0) ? S.DirAdvance
                : (Choice == 1) ? S.DirRetreat : S.DirLateral;
            Mul = (Mul * S.Mobility) / 10000;
            if (S.St[I] < S.ExhaustedQ)
            {
                Mul = (Mul * S.DirExhausted) / 10000;
                Flags += TEXT("e");
            }
            if (Choice != 2)
            {
                const int32 Toward = (I == 0) ? 1 : -1;
                const int32 Sign = (Choice == 0) ? Toward : -Toward;
                const bool bOnRopes = FMath::Min(S.Pos[I], S.Axis - S.Pos[I]) <= S.Ropes;
                if (bOnRopes && Choice == 1)
                {
                    Mul = (Mul * S.RopeRetreat) / 10000;
                    Flags += TEXT("r");
                }
                const int64 Mag = (S.Stride * Mul) / 10000;
                S.Pos[I] = FMath::Clamp(S.Pos[I] + Sign * Mag, (int64)0, S.Axis);
                if (S.Pos[1] - S.Pos[0] < S.MinSep)
                {
                    if (I == 0) { S.Pos[0] = S.Pos[1] - S.MinSep; }
                    else { S.Pos[1] = S.Pos[0] + S.MinSep; }
                    S.Pos[0] = FMath::Max((int64)0, S.Pos[0]);
                    S.Pos[1] = FMath::Min(S.Axis, S.Pos[1]);
                    Flags += TEXT("m");
                }
                const int64 Sep = S.Pos[1] - S.Pos[0];
                const int64 Lo = S.BMin[S.Band] - S.Hyst;
                const int64 Hi = S.BMax[S.Band] + S.Hyst;
                int32 Next = S.Band + (Sep > Hi ? 1 : 0) - (Sep < Lo ? 1 : 0);
                Next = FMath::Clamp(Next, 0, S.BMin.Num() - 1);
                if (Next != S.Band) { ++S.Transitions; }
                S.Band = Next;
            }
        }
        ++S.Rows;
        S.Emit(FString::Printf(TEXT("D|%d|%d|%s|%u|%lld|%lld|%lld|%d|%lld|%lld|%s\n"),
            T, I, ActionName[Choice], S.X, S.Pos[0], S.Pos[1], S.Pos[1] - S.Pos[0], S.Band,
            S.St[0], S.St[1], Flags.IsEmpty() ? TEXT("-") : *Flags));
        // [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 17:32 UTC | edit: pose-only ]
        S.LastAction[I] = ActionName[Choice];
        S.ActionT0[I] = T;
        // [ edit end ]
    }
}
// [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 06:25 UTC | continued ]

void AUppercutBoutDirector::UpdatePoses()
{
    const FImpl& S = *Impl;
    for (int32 i = 0; i < 2; ++i)
    {
        if (!Torso[i]) { continue; }
        const double Xcm = S.Pos[i] / 10000.0 * S.RuToCm;
        const double Facing = (i == 0) ? 1.0 : -1.0;
        Torso[i]->SetActorLocation(FVector(Xcm, 0, 95));
        Head[i]->SetActorLocation(FVector(Xcm, 0, 195));
        // gloves ride at guard by default; the punching hand extends along
        // facing by the sim's own integer extension, at its lane's height -
        // the pose READS the authoritative state and adds nothing to it.
        double LeadExt = 0.0, RearExt = 0.0, PunchZ = 150.0;
        if (!S.PunchMove[i].IsEmpty())
        {
            const FKMove& Mv = S.Moves[S.PunchMove[i]];
            const int32 Kk = SimTick - S.PunchT0[i];
            const int32 Total = Mv.Startup + Mv.Active;
            const int32 Mm = FMath::Clamp(Kk, 0, Total);
            const double ExtCm = S.ExtAt(Mv, Mm) / 10000.0 * S.RuToCm;
            PunchZ = (Mv.Height == TEXT("low")) ? 110.0 : 160.0;
            if (Mv.Hand == TEXT("lead")) { LeadExt = ExtCm; }
            else { RearExt = ExtCm; }
        }
        GloveLead[i]->SetActorLocation(FVector(
            Xcm + Facing * (25.0 + LeadExt), -14.0, LeadExt > 0 ? PunchZ : 145.0));
        GloveRear[i]->SetActorLocation(FVector(
            Xcm + Facing * (18.0 + RearExt), 14.0, RearExt > 0 ? PunchZ : 140.0));
    }
    // [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 17:32 UTC | edit: mannequin visual pass ]
    PoseMannequins();
    // [ edit end ]
}

void AUppercutBoutDirector::FinishRun()
{
    FImpl& S = *Impl;
    // the float-conformance probe: reported, not judged
    double Sd = S.FMax;
    for (int32 Kk = 1; Kk <= 1000; ++Kk)
    {
        Sd = Sd - S.FCost / 4.0;
        Sd = Sd + S.FRegen * 3.0;
        Sd = Sd * 0.9995;
        Sd = Sd + S.FHold;
        if (Sd > S.FMax) { Sd = S.FMax; }
        if (Kk % 100 == 0)
        {
            uint64 Bits = 0;
            FMemory::Memcpy(&Bits, &Sd, sizeof(double));
            S.Out += FString::Printf(TEXT("F|%d|%016llx\n"), Kk, Bits);
        }
    }
    S.Out += FString::Printf(TEXT("S|rows=%lld|punches=%lld|blocked=%lld|landed=%lld")
        TEXT("|whiffed=%lld|steps=%lld|held=%lld|idles=%lld|transitions=%lld|fnv1a64=%016llx\n"),
        S.Rows, S.Punches, S.Blocked, S.Landed, S.Whiffed, S.Steps, S.Held, S.Idles,
        S.Transitions, S.Fnv);
    IFileManager::Get().MakeDirectory(*FPaths::GetPath(OutPath), true);
    FFileHelper::SaveStringToFile(S.Out, *OutPath,
        FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);
    UE_LOG(LogTemp, Display, TEXT("UppercutBoutDirector: %lld rows, %d shots -> %s"),
           S.Rows, S.ShotsTaken, *OutPath);
}

void AUppercutBoutDirector::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    if (!bReady || bDone) { return; }
    if (!bViewSet && Camera)
    {
        if (APlayerController* PC = UGameplayStatics::GetPlayerController(this, 0))
        {
            PC->SetViewTargetWithBlend(Camera, 0.0f);
            bViewSet = true;
        }
    }
    if (SimTick < Ticks)
    {
        ++SimTick;
        StepSim();
        UpdatePoses();
        if (!ShotDir.IsEmpty() && Impl->ShotTicks.Contains(SimTick))
        {
            IFileManager::Get().MakeDirectory(*ShotDir, true);
            FScreenshotRequest::RequestScreenshot(
                ShotDir / FString::Printf(TEXT("tick_%05d.png"), SimTick), false, false);
            ++Impl->ShotsTaken;
        }
        if (SimTick == Ticks)
        {
            FinishRun();
        }
        return;
    }
    // grace frames so pending screenshots flush before exit
    if (++GraceFrames > 90)
    {
        bDone = true;
        FPlatformMisc::RequestExit(false);
    }
}
// [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 06:25 UTC | END ]
