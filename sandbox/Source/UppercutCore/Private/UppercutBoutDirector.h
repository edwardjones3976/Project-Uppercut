// [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 06:25 UTC | START ]
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "UppercutBoutDirector.generated.h"

class AStaticMeshActor;
class ACameraActor;
// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 17:32 UTC | edit: mannequin visual pass ]
class ASkeletalMeshActor;
class UAnimSequence;

// Phase K: the authoritative sim (Phase J's, widened to the slice's four
// named punches plus the body straight) advancing exactly one tick per
// rendered frame, with primitive-built fighters posed FROM sim state - the
// presentation reads, never writes. The marker stream this actor emits must
// be byte-identical to tools/engine/analyze_render_probe.py's recomputation:
// that identity IS the phase's claim that rendering holds zero authority.
//
// The sim code is deliberately a self-contained copy, like each evidence
// commandlet before it: these probes are frozen records, and the core's real
// shared API arrives when the reference simulator ports, not before.
UCLASS()
class AUppercutBoutDirector : public AActor
{
    GENERATED_BODY()

public:
    AUppercutBoutDirector();
    virtual void Tick(float DeltaSeconds) override;

protected:
    virtual void BeginPlay() override;

private:
    bool LoadCanonAndParams();
    void BuildScene();
    void StepSim();               // exactly one authoritative tick
    void UpdatePoses();
    void FinishRun();
    // [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 17:32 UTC | edit: mannequin visual pass ]
    // Skeletal fighters layered OVER the primitive markers. Both read sim
    // state; neither writes it. Animation is scrubbed to a sim-derived time -
    // never advanced by DeltaSeconds - so a dropped frame cannot desync the
    // picture from the fight.
    void BuildMannequins();
    void PoseMannequins();
    UAnimSequence* Clip(const TCHAR* Rel);
    // [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 19:30 UTC | edit: arena ]
    // -arena spawns the imported cartoon ring. Opt-in, because a ring the sim
    // does not know about is scenery, and scenery must never be load-bearing.
    void BuildArena();

    // scene
    AStaticMeshActor* Torso[2] = { nullptr, nullptr };
    AStaticMeshActor* Head[2] = { nullptr, nullptr };
    AStaticMeshActor* GloveLead[2] = { nullptr, nullptr };
    AStaticMeshActor* GloveRear[2] = { nullptr, nullptr };
    ACameraActor* Camera = nullptr;
    // [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 17:32 UTC | edit: mannequin visual pass ]
    ASkeletalMeshActor* Fighter[2] = { nullptr, nullptr };
    TMap<FString, UAnimSequence*> Clips;
    bool bMannequins = false;   // set once the pack's mesh and clips all load
    bool bShowMarkers = false;  // -markers restores the Phase K primitive view
    bool bArena = false;        // -arena spawns the imported ring
    bool bViewSet = false;
    bool bReady = false;
    bool bDone = false;

    // params
    uint32 Seed = 0;
    int32 Ticks = 0;
    FString Repo, OutPath, ShotDir;

    // sim state (contract types; see the analyzer for the arithmetic)
    struct FImpl;
    TSharedPtr<FImpl> Impl;

    int32 SimTick = 0;
    int32 GraceFrames = 0;
};
// [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 06:25 UTC | END ]
