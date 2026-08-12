// [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 03:53 UTC | START ]
#pragma once

#include "CoreMinimal.h"

class UWorld;
class USkeletalMesh;
class UAnimSequence;

// PRESENTATION ONLY (Decision 0012). Spawns Fab ring meshes and loads
// mannequin assets for the live arena. Never touches FightSubsystem controls
// or the marker stream. Soft-fails when vendor content is missing so a clean
// checkout still Press-Plays with cylinders on a plane.

struct UPPERCUTCORE_API FUppercutArenaRingSpawn
{
    bool bSpawned = false;
    int32 PartCount = 0;
    double Scale = 1.0;
};

// AxisCm must match how AUppercutFighterBase places fighters
// (GetRingAxisRu() * WorldUnitsPerRingUnit, default 100 cm/ru).
UPPERCUTCORE_API FUppercutArenaRingSpawn UppercutSpawnFabRing(
    UWorld* World, double AxisCm);

UPPERCUTCORE_API USkeletalMesh* UppercutLoadFighterMannequinMesh(int32 FighterIndex);

// All-or-nothing: if any clip fails to load, OutClips is emptied and false is
// returned (same rule as BoutDirector — a half-clothed fighter is worse evidence).
UPPERCUTCORE_API bool UppercutLoadFighterActionClips(
    TMap<FString, UAnimSequence*>& OutClips);
// [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 03:53 UTC | END ]
