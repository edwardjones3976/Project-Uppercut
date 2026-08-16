// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 20:50 UTC | START ]
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "UppercutFightSubsystem.h"
#include "UppercutMatchDirector.generated.h"

class AUppercutFighterBase;
class ACameraActor;

// THE THING YOU PRESS PLAY ON.
//
// Drop one of these in a map, press Play, and two fighters fight. It starts the
// round, binds the development controls to keys directly (no project input
// configuration, because a control that needs setup is a control that is not
// there when you need it), and owns nothing the simulation depends on.
//
// It is deliberately a director and not a referee: it decides when a round
// begins and ends and nothing about what happens inside one. The integrated
// 1-round session (FUppercutFightSession via FightSubsystem.bIntegratedOneRound)
// owns knockdown/count/decision. Phase O is no longer held on G7 —
// docs/decisions/OPEN_GATES.md has no open Director gates.

UCLASS(Blueprintable)
class UPPERCUTCORE_API AUppercutMatchDirector : public AActor
{
    GENERATED_BODY()

public:
    AUppercutMatchDirector();

    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;

    // --- what the round is -------------------------------------------------

    // The seed. Same seed, same fight, every time - which is what makes a
    // disagreement about what happened settleable.
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Uppercut|Round")
    int32 Seed = 4242;

    // Canon permits one, two or three minutes and nothing else
    // (clock_model.json, Rule 8). Set outside that set and this clamps to the
    // nearest authored length rather than inventing a round.
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Uppercut|Round")
    int32 RoundLengthSeconds = 180;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Uppercut|Round")
    bool bAutoStart = true;

    // [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-16 03:05 UTC |
    //   edit: how much wider the VISUAL ring is than the fight axis. 1.0 =
    //   ropes meet the axis (the old look); the Director asked for bigger.
    //   Presentation only - nothing about the fight moves with it. ]
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Uppercut|Presentation")
    float RingSpanMultiplier = 1.5f;

    // Keep every marker row so the round can be dumped and proven afterwards.
    // Costs memory and buys the only thing that makes this arena more than a
    // demo.
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Uppercut|Evidence")
    bool bCaptureRows = true;

    // --- development controls ----------------------------------------------

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Uppercut|Controls")
    bool bBindDefaultKeys = true;

    // [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-16 02:30 UTC | START ]
    // THE FIGHTER VITALS TELEMETRY PANEL (Director's name, 2026-08-16).
    //
    // Developer-only, and named apart from any future player-facing HUD on
    // purpose: this shows what the SIMULATION holds, including the marker hash
    // of the round in progress, so a fight can be read while it is still
    // happening rather than after it is dumped.
    //
    // It draws on the engine's on-screen debug channel - no UMG asset, no HUD
    // class, no game-mode override, no change to the map - which is also an
    // honest signal that it is instrumentation and not product.
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Uppercut|Telemetry")
    bool bShowVitalsPanel = true;
    // [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-16 02:30 UTC | END ]

    UFUNCTION(BlueprintCallable, Category = "Uppercut|Controls")
    void StartRound();

    UFUNCTION(BlueprintCallable, Category = "Uppercut|Controls")
    void TogglePause();

    UFUNCTION(BlueprintCallable, Category = "Uppercut|Controls")
    void StepOneTick();

    UFUNCTION(BlueprintCallable, Category = "Uppercut|Controls")
    void StepOneSecond();

    UFUNCTION(BlueprintCallable, Category = "Uppercut|Controls")
    void RestartSameSeed();

    UFUNCTION(BlueprintCallable, Category = "Uppercut|Controls")
    void NextSeed();

    UFUNCTION(BlueprintCallable, Category = "Uppercut|Controls")
    void Slower();

    UFUNCTION(BlueprintCallable, Category = "Uppercut|Controls")
    void Faster();

    UFUNCTION(BlueprintCallable, Category = "Uppercut|Controls")
    void NormalSpeed();

    // Writes the round so far to Saved/live/ and logs the path. Hand the file to
    // `python -m tools.engine.prove_core_range` and the fight that was watched
    // is the fight that gets checked.
    UFUNCTION(BlueprintCallable, Category = "Uppercut|Evidence")
    void DumpRound();

    // --- reading it ---------------------------------------------------------

    UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Uppercut")
    FUppercutFightView GetView() const;

    UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Uppercut")
    UUppercutFightSubsystem* GetFight() const { return Fight; }

    // Fired once when the tick budget runs out, so a HUD can say so without
    // polling for the transition.
    UFUNCTION(BlueprintImplementableEvent, Category = "Uppercut|Round")
    void OnRoundFinished(const FUppercutFightView& FinalView);

protected:
    UPROPERTY(BlueprintReadOnly, Category = "Uppercut")
    TObjectPtr<UUppercutFightSubsystem> Fight = nullptr;

private:
    void BindKeys();
    int32 AuthoredRoundLength(int32 Requested) const;

    // Pose studio (presentation-only): delay capture without TimerManager.h so
    // tools.engine.check_core_compiles stays on its observed UE whitelist.
    void ArmPoseStudioCapture(ACameraActor* Cam, const FString& ShotPath);
    void FirePoseStudioCapture();

    // [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-16 02:30 UTC | START ]
    void DrawVitalsPanel(const FUppercutFightView& View);
    // [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-16 02:30 UTC | END ]

    bool bAnnouncedFinish = false;
    float SpeedNow = 1.f;

    bool bPoseStudioActive = false;
    bool bPoseShotArmed = false;
    float PoseShotDelayRemaining = 0.f;
    TWeakObjectPtr<ACameraActor> PoseCamera;
    FString PoseShotPath;

    // [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-16 02:35 UTC | START ]
    // -UppercutShotAfter=12,60,178 : render-target captures of the LIVE fight
    // at those wall-clock seconds, to Saved/live_shots/. The same
    // FScreenshotRequest the pose studio uses, so it works headless-windowed
    // and does not care what is in front of the window. Presentation only.
    TArray<float> LiveShotTimes;
    float LiveShotClock = 0.f;
    int32 LiveShotsFired = 0;
    TWeakObjectPtr<ACameraActor> LiveCamera;
    // [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-16 02:35 UTC | END ]
};
// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 20:50 UTC | END ]
