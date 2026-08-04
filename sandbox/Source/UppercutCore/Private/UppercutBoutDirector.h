// [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 06:25 UTC | START ]
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "UppercutBoutDirector.generated.h"

class AStaticMeshActor;
class ACameraActor;

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

    // scene
    AStaticMeshActor* Torso[2] = { nullptr, nullptr };
    AStaticMeshActor* Head[2] = { nullptr, nullptr };
    AStaticMeshActor* GloveLead[2] = { nullptr, nullptr };
    AStaticMeshActor* GloveRear[2] = { nullptr, nullptr };
    ACameraActor* Camera = nullptr;
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
