// [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 06:25 UTC | START ]
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "UppercutRenderGameMode.generated.h"

// Phase K: the game mode that hosts the first rendered slice. Spawns the
// bout director into any map (the scene is built from primitives at runtime,
// so /Engine/Maps/Entry suffices - no content assets, nothing to drift).
UCLASS()
class AUppercutRenderGameMode : public AGameModeBase
{
    GENERATED_BODY()

public:
    AUppercutRenderGameMode();

protected:
    virtual void BeginPlay() override;
};
// [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 06:25 UTC | END ]
