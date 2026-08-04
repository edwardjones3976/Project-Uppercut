// [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 06:25 UTC | START ]
#include "UppercutRenderGameMode.h"

#include "GameFramework/SpectatorPawn.h"
#include "UppercutBoutDirector.h"

AUppercutRenderGameMode::AUppercutRenderGameMode()
{
    DefaultPawnClass = ASpectatorPawn::StaticClass();
}

void AUppercutRenderGameMode::BeginPlay()
{
    Super::BeginPlay();
    GetWorld()->SpawnActor<AUppercutBoutDirector>(FVector::ZeroVector, FRotator::ZeroRotator);
}
// [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 06:25 UTC | END ]
