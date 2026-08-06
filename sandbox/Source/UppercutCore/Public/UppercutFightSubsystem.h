// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 20:20 UTC | START ]
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "UppercutRangeCore.h"
#include "UppercutFightSubsystem.generated.h"

// THE LIVE FIGHT.
//
// This owns one FUppercutRangeSession and advances it on the authoritative
// clock. It is deliberately the ONLY thing in the runtime that may call Step():
// actors and widgets read snapshots and never touch the session, so no amount
// of presentation code can move a fighter.
//
// CRITERION E.19 - WALL-CLOCK TIME NEVER DRIVES THE SIMULATION. Real time
// decides WHEN a tick runs, never how big one is. Delta seconds accumulate and
// are spent in whole ticks; a frame that took four ticks' worth of time runs
// four identical ticks. The speed control multiplies how fast the accumulator
// fills - it does not scale the tick. This is why a fight watched at 0.25x
// speed and one watched at 4x produce the same marker stream, and it is the
// difference between a dev control and a lie.
//
// WHAT MAKES THIS WORTH WATCHING: the session, the canon reader and the stream
// format are the same code the Phase Q parity proof is taken against. `Dump()`
// writes a stream `tools/engine/prove_core_range` can check. So the arena is
// not "a runtime that agrees with the proof" - it is the proven artifact, run
// with a camera pointed at it.

UENUM(BlueprintType)
enum class EUppercutFightState : uint8
{
    NoCanon     UMETA(DisplayName = "No Canon"),
    Ready       UMETA(DisplayName = "Ready"),
    Running     UMETA(DisplayName = "Running"),
    Paused      UMETA(DisplayName = "Paused"),
    Finished    UMETA(DisplayName = "Finished")
};

// One fighter, as presentation is allowed to see him: everything readable,
// nothing writable.
USTRUCT(BlueprintType)
struct UPPERCUTCORE_API FUppercutFighterView
{
    GENERATED_BODY()

    // Ring units. The simulation holds these as q10000 integers; this is the
    // float a transform wants, produced at the boundary and nowhere else.
    UPROPERTY(BlueprintReadOnly, Category = "Uppercut|Fighter")
    float PositionRu = 0.f;

    UPROPERTY(BlueprintReadOnly, Category = "Uppercut|Fighter")
    int32 BandIndex = 0;

    UPROPERTY(BlueprintReadOnly, Category = "Uppercut|Fighter")
    FString BandKey;

    UPROPERTY(BlueprintReadOnly, Category = "Uppercut|Fighter")
    FString LastAction;

    // The tick that commitment was drawn on. Two identical actions in a row are
    // two commitments; without this an animation layer comparing strings would
    // play only the first.
    UPROPERTY(BlueprintReadOnly, Category = "Uppercut|Fighter")
    int32 LastActionTick = 0;

    // Frames of commitment left. A fighter who is busy cannot decide, which is
    // the whole reason a punch can be made to pay for itself.
    UPROPERTY(BlueprintReadOnly, Category = "Uppercut|Fighter")
    int32 BusyTicks = 0;

    UPROPERTY(BlueprintReadOnly, Category = "Uppercut|Fighter")
    bool bPunchInFlight = false;

    UPROPERTY(BlueprintReadOnly, Category = "Uppercut|Fighter")
    FString PunchMove;

    // Rule 12: the punch was thrown from a band that does not reach. It will
    // travel its full arc into empty air anyway.
    UPROPERTY(BlueprintReadOnly, Category = "Uppercut|Fighter")
    bool bPunchIsInRange = false;

    // Movement still owed, capped per tick so nobody teleports.
    UPROPERTY(BlueprintReadOnly, Category = "Uppercut|Fighter")
    float PendingRu = 0.f;
};

USTRUCT(BlueprintType)
struct UPPERCUTCORE_API FUppercutFightView
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadOnly, Category = "Uppercut|Fight")
    EUppercutFightState State = EUppercutFightState::NoCanon;

    UPROPERTY(BlueprintReadOnly, Category = "Uppercut|Fight")
    int32 Tick = 0;

    UPROPERTY(BlueprintReadOnly, Category = "Uppercut|Fight")
    int32 TickBudget = 0;          // 0 means "until stopped"

    UPROPERTY(BlueprintReadOnly, Category = "Uppercut|Fight")
    int32 Seed = 0;

    UPROPERTY(BlueprintReadOnly, Category = "Uppercut|Fight")
    float SpeedMultiplier = 1.f;

    UPROPERTY(BlueprintReadOnly, Category = "Uppercut|Fight")
    float SeparationRu = 0.f;

    UPROPERTY(BlueprintReadOnly, Category = "Uppercut|Fight")
    TArray<FUppercutFighterView> Fighters;

    // The trailer's counters, live. A HUD showing these is showing the same
    // numbers the marker stream ends with.
    UPROPERTY(BlueprintReadOnly, Category = "Uppercut|Fight")
    int32 Decisions = 0;

    UPROPERTY(BlueprintReadOnly, Category = "Uppercut|Fight")
    int32 Punches = 0;

    UPROPERTY(BlueprintReadOnly, Category = "Uppercut|Fight")
    int32 Landed = 0;

    // Thrown from the wrong band (Rule 12) versus thrown from the right band and
    // still short. Two different mistakes, and a fighter who only makes one of
    // them is a different fighter.
    UPROPERTY(BlueprintReadOnly, Category = "Uppercut|Fight")
    int32 WhiffFromWrongBand = 0;

    UPROPERTY(BlueprintReadOnly, Category = "Uppercut|Fight")
    int32 WhiffOutOfReach = 0;

    UPROPERTY(BlueprintReadOnly, Category = "Uppercut|Fight")
    int32 BandTransitions = 0;

    UPROPERTY(BlueprintReadOnly, Category = "Uppercut|Fight")
    int32 Steps = 0;

    UPROPERTY(BlueprintReadOnly, Category = "Uppercut|Fight")
    int32 RopeBlockedRetreats = 0;

    // FNV-1a 64 of every row so far, lowercase hex. Put this on screen and the
    // fight is auditable while it is still happening.
    UPROPERTY(BlueprintReadOnly, Category = "Uppercut|Evidence")
    FString MarkerHash;

    UPROPERTY(BlueprintReadOnly, Category = "Uppercut|Evidence")
    int32 RowCount = 0;
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FUppercutFightTick,
                                            const FUppercutFightView&, View);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FUppercutFightRow,
                                            const FString&, Row);

UCLASS()
class UPPERCUTCORE_API UUppercutFightSubsystem : public UTickableWorldSubsystem
{
    GENERATED_BODY()

public:
    // --- UWorldSubsystem ---------------------------------------------------
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;
    virtual void Tick(float DeltaSeconds) override;
    virtual TStatId GetStatId() const override;
    virtual bool DoesSupportWorldType(const EWorldType::Type Type) const override;

    // --- canon -------------------------------------------------------------

    // Reads the repository's canon. Called automatically on Initialize with the
    // repo inferred from the project directory; call it again with an explicit
    // path to point the arena at a different checkout.
    UFUNCTION(BlueprintCallable, Category = "Uppercut|Canon")
    bool LoadCanon(const FString& RepoDir, FString& OutError);

    // "What is this fight running on" - the four files and their hashes.
    UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Uppercut|Canon")
    void GetCanonSources(TArray<FString>& OutLabels, TArray<FString>& OutHashes,
                         TArray<FString>& OutPaths) const;

    // --- the controls the Director asked for --------------------------------

    UFUNCTION(BlueprintCallable, Category = "Uppercut|Control")
    void StartFight(int32 Seed, int32 InTickBudget);

    UFUNCTION(BlueprintCallable, Category = "Uppercut|Control")
    void Pause();

    UFUNCTION(BlueprintCallable, Category = "Uppercut|Control")
    void Resume();

    UFUNCTION(BlueprintCallable, Category = "Uppercut|Control")
    void TogglePause();

    // Advances exactly N ticks and leaves the fight paused. The only way to
    // watch one decision at a time.
    UFUNCTION(BlueprintCallable, Category = "Uppercut|Control")
    void SingleStep(int32 NumTicks);

    // Same seed, tick zero. A fight you can run again is a fight you can argue
    // about.
    UFUNCTION(BlueprintCallable, Category = "Uppercut|Control")
    void Restart();

    UFUNCTION(BlueprintCallable, Category = "Uppercut|Control")
    void Reseed(int32 NewSeed);

    // Clamped to [0.05, 8]. Changes how fast the accumulator fills and nothing
    // else - see the note on Criterion E.19 above.
    UFUNCTION(BlueprintCallable, Category = "Uppercut|Control")
    void SetSpeed(float Multiplier);

    // --- reading it ---------------------------------------------------------

    UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Uppercut|Read")
    FUppercutFightView GetView() const;

    UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Uppercut|Read")
    bool IsRunning() const { return State == EUppercutFightState::Running; }

    // The authoritative clock, read from canon. Anything that needs to convert
    // seconds to ticks asks here rather than assuming 60, because Rule 9 says
    // one clock and an assumption is a second one.
    UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Uppercut|Read")
    int32 GetTickRateHz() const { return TickRateHz; }

    // The ring's length in ring units, so presentation can lay out a floor that
    // matches the space the fight actually has.
    UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Uppercut|Read")
    float GetRingAxisRu() const { return (float)((double)Canon.Axis / 10000.0); }

    // --- evidence -----------------------------------------------------------

    // Write the fight so far as a marker stream. With `bCaptureRows` on since
    // tick zero and the tick budget reached, this file is byte-identical to what
    // the commandlet writes for the same seed - which is the point.
    UFUNCTION(BlueprintCallable, Category = "Uppercut|Evidence")
    bool DumpStream(const FString& Path, FString& OutError);

    // Off by default: a five-minute round is a few hundred thousand rows and a
    // HUD does not need them. Turn it on before StartFight to make the fight
    // dumpable.
    UPROPERTY(BlueprintReadWrite, EditAnywhere, Category = "Uppercut|Evidence")
    bool bCaptureRows = false;

    // --- presentation hooks (read-only by construction) ---------------------

    UPROPERTY(BlueprintAssignable, Category = "Uppercut|Events")
    FUppercutFightTick OnFightTick;

    // Every marker row as it is emitted. This is how a debug overlay narrates a
    // fight without a second opinion about what happened.
    UPROPERTY(BlueprintAssignable, Category = "Uppercut|Events")
    FUppercutFightRow OnMarkerRow;

private:
    void AdvanceOneTick();
    void ResetSession(uint32 InSeed);

    FUppercutRangeCanon Canon;
    TArray<FUppercutCanonSource> Sources;
    FUppercutRangeSession Session;

    EUppercutFightState State = EUppercutFightState::NoCanon;

    uint32 Seed = 4242;
    int32 TickBudget = 0;
    int32 TickRateHz = 60;
    float Speed = 1.f;
    double Accumulator = 0.0;

    uint64 Fnv = 0;
    int64 RowCount = 0;
    TArray<FString> CapturedRows;
    TArray<FString> Scratch;
};
// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 20:20 UTC | END ]
