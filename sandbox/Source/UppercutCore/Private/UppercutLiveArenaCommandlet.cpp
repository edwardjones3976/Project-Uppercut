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
    // [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-12 05:15 UTC | START edit ]
    // WHICH FIGHT TO PROVE. The subsystem defaults to the integrated one-round
    // session, so without this switch the arena can only ever emit an
    // INTEGRATED_1R stream - and prove_live_arena, which asserts the Phase Q
    // contract, had no way to ask for the fight it is the proof of. It failed
    // on the very first line, comparing "phase=INTEGRATED_1R" against
    // "phase=Q".
    //
    // Phase Q parity is a PINNED claim, not a superseded one, so the correct
    // repair is to let the caller choose rather than to retire the proof.
    // -integrated=0 selects the Phase Q range session; the default stays the
    // integrated round, so Play is unaffected.
    int32 Integrated = 1;
    FParse::Value(*Params, TEXT("integrated="), Integrated);
    // [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-12 05:15 UTC | END edit ]
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
        // The subsystem loads canon from the project's parent on Initialize.
        // Loading again from an explicit repo makes the proof independent of
        // where the commandlet happened to be run from.
        // [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-12 05:15 UTC | START edit ]
        // Set BEFORE LoadCanon: the subsystem decides there and then whether to
        // load the integrated pack, and flipping the flag afterwards would
        // leave a session that had already chosen.
        Fight->bIntegratedOneRound = (Integrated != 0);
        // [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-12 05:15 UTC | END edit ]
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
