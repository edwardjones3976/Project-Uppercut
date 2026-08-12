// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 21:50 UTC | START ]
#include "UppercutLiveArenaCommandlet.h"

#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Misc/Paths.h"
#include "UppercutFightSubsystem.h"

int32 UUppercutLiveArenaCommandlet::Main(const FString& Params)
{
    uint32 Seed = 0; int32 Ticks = 0; FString Repo, OutPath;
    FParse::Value(*Params, TEXT("seed="), Seed);
    FParse::Value(*Params, TEXT("ticks="), Ticks);
    FParse::Value(*Params, TEXT("repo="), Repo);
    FParse::Value(*Params, TEXT("out="), OutPath);
    if (Ticks <= 0 || Repo.IsEmpty() || OutPath.IsEmpty())
    {
        UE_LOG(LogTemp, Error, TEXT("UppercutLiveArena: need -seed= -ticks= -repo= -out="));
        return 1;
    }

    // A real game world, because a subsystem that only works in a fake one has
    // proven nothing about the arena.
    UWorld* World = UWorld::CreateWorld(EWorldType::Game, false);
    if (!World)
    {
        UE_LOG(LogTemp, Error, TEXT("UppercutLiveArena: could not create a world"));
        return 1;
    }
    FWorldContext& Context = GEngine->CreateNewWorldContext(EWorldType::Game);
    Context.SetCurrentWorld(World);

    int32 Result = 1;
    if (UUppercutFightSubsystem* Fight = World->GetSubsystem<UUppercutFightSubsystem>())
    {
        // prove_live_arena compares against Phase Q expected_stream.
        // Integrated 1-round is the Press Play default; force Q before LoadCanon
        // so bIntegratedLoaded stays false and the parity dump is Phase Q.
        Fight->bIntegratedOneRound = false;

        // The subsystem loads canon from the project's parent on Initialize.
        // Loading again from an explicit repo makes the proof independent of
        // where the commandlet happened to be run from.
        FString Error;
        if (!Fight->LoadCanon(Repo, Error))
        {
            UE_LOG(LogTemp, Error, TEXT("UppercutLiveArena: %s"), *Error);
        }
        else
        {
            Fight->bCaptureRows = true;
            Fight->StartFight((int32)Seed, Ticks);

            // Through the single-step control, one tick at a time - the same
            // entry point the Director's period key uses. Calling Step()
            // directly would prove the core again and the arena not at all.
            for (int32 T = 0; T < Ticks; ++T)
            {
                Fight->SingleStep(1);
            }

            const FUppercutFightView V = Fight->GetView();
            if (V.Tick != Ticks)
            {
                UE_LOG(LogTemp, Error,
                       TEXT("UppercutLiveArena: asked for %d ticks, ran %d"),
                       Ticks, V.Tick);
            }
            else if (Fight->DumpStream(OutPath, Error))
            {
                UE_LOG(LogTemp, Display,
                       TEXT("UppercutLiveArena: %d ticks, marker %s -> %s"),
                       V.Tick, *V.MarkerHash, *OutPath);
                Result = 0;
            }
            else
            {
                UE_LOG(LogTemp, Error, TEXT("UppercutLiveArena: %s"), *Error);
            }
        }
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("UppercutLiveArena: no fight subsystem in the world"));
    }

    GEngine->DestroyWorldContext(World);
    World->DestroyWorld(false);
    return Result;
}
// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 21:50 UTC | END ]
