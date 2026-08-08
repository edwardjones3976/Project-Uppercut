// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 11:00 UTC | START ]
#pragma once

#include "CoreMinimal.h"
#include "Commandlets/Commandlet.h"
#include "UppercutStaminaVectorsCommandlet.generated.h"

// Decision 0021 runtime parity: the C++ two-tier economy against the contract's
// trajectories, in exact q10000 integers.
//
// Not "close enough at the end". Every declared checkpoint is compared, because
// an economy that drifts by one unit per tick reads correct at tick 1 and is a
// whole round wrong by the twelfth - and the end-of-run total can hide a
// cancelling pair of errors that a mid-run checkpoint cannot.
//
// Usage:
//   UnrealEditor-Cmd <uproject> -run=UppercutStaminaVectors
//       -repo=<project-uppercut root> -out=<file>
UCLASS()
class UUppercutStaminaVectorsCommandlet : public UCommandlet
{
    GENERATED_BODY()

public:
    virtual int32 Main(const FString& Params) override;
};
// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 11:00 UTC | END ]
