// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 21:50 UTC | START ]
#pragma once

#include "CoreMinimal.h"
#include "Commandlets/Commandlet.h"
#include "UppercutLiveArenaCommandlet.generated.h"

// PROVE THE LIVE PATH, not just the headless one.
//
// UppercutCoreRange proves that the C++ RULES reproduce the contract. It does
// not prove anything about the thing the Director actually presses Play on: the
// world subsystem, its start/step controls, and its stream writer. Those are new
// code, and new code between the proof and the screen is exactly where a
// "runtime version" quietly becomes a second implementation.
//
// So this builds a real UWorld, lets the real UUppercutFightSubsystem come up in
// it, drives it through its own single-step control, and asks it to dump. If
// that file is byte-identical to the contract's stream, then the fight in the
// arena is the fight in the evidence - not a fight that agrees with it.
//
// Deliberately single-stepped rather than run on a timer: wall-clock pacing is
// what a Director watches, and it must not be what a proof depends on.
//
// Usage:
//   UnrealEditor-Cmd <uproject> -run=UppercutLiveArena
//       -seed=4242 -ticks=5400 -repo=<project-uppercut root> -out=<file>
UCLASS()
class UUppercutLiveArenaCommandlet : public UCommandlet
{
    GENERATED_BODY()

public:
    virtual int32 Main(const FString& Params) override;
};
// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 21:50 UTC | END ]
