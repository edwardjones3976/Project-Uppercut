// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 20:50 UTC | START ]
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "UppercutFightSubsystem.h"
#include "UppercutMatchDirector.generated.h"

class AUppercutFighterBase;

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

    // Keep every marker row so the round can be dumped and proven afterwards.
    // Costs memory and buys the only thing that makes this arena more than a
    // demo.
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Uppercut|Evidence")
    bool bCaptureRows = true;

    // --- development controls ----------------------------------------------

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Uppercut|Controls")
    bool bBindDefaultKeys = true;

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

    bool bAnnouncedFinish = false;
    float SpeedNow = 1.f;
};
// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 20:50 UTC | END ]
