// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 18:40 UTC | START ]
#pragma once

#include "CoreMinimal.h"
#include "Commandlets/Commandlet.h"
#include "UppercutCoreConditionCommandlet.generated.h"

// Phase N: visible stamina and condition (Decision 0012 slice item 8) - where
// landing starts to matter. Phase L's guard-and-slip core gains the condition
// layer: per-region accumulation from delivered force (Rule 14, no generic
// pool), impact derived from what a punch cost to throw, torso damage slowing
// the tank, and arm damage from BLOCKED force eroding guard coverage - so
// coverage stops being a per-posture constant computable at load and becomes a
// per-punch evaluation against pose_geometry's one interception threshold.
//
// Contract: tools/engine/analyze_core_condition.py, mutation-proven with 15
// tests before this class existed. That contract also carries the finding this
// phase produced: at canon's authored coefficients the guard erosion needs
// ~216,000 ticks to reach the threshold, which is an hour of fighting.
//
// Usage:
//   UnrealEditor-Cmd <uproject> -run=UppercutCoreCondition
//       -seed=4242 -ticks=5400 -repo=<project-uppercut root> -out=<file>
UCLASS()
class UUppercutCoreConditionCommandlet : public UCommandlet
{
    GENERATED_BODY()

public:
    virtual int32 Main(const FString& Params) override;
};
// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 18:40 UTC | END ]
