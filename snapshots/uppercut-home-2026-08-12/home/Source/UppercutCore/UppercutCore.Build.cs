// [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 03:42 UTC | START ]
// The authoritative fight core's module (Decision 0012): C++ simulation,
// Blueprints presentation, Python tooling. This scaffold's only job is the
// Phase H probe - canon in, deterministic integers, self-hashing markers out.
using UnrealBuildTool;

public class UppercutCore : ModuleRules
{
    public UppercutCore(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

        // [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 21:05 UTC | no unity start ]
        // NO UNITY BUILD, on purpose.
        //
        // Every phase's commandlet keeps its constants (LcgA, Q, FnvPrime) in an
        // anonymous namespace, which is correct per file and collides the moment
        // two of them land in the same unity blob. Which files share a blob
        // depends on the ADAPTIVE build's working set - that is, on `git status`.
        // So the module compiled or failed depending on which files happened to
        // be uncommitted, and it failed for the first time on a commit that
        // changed no commandlet at all.
        //
        // A build whose success depends on the state of the working tree is not
        // something an evidence pipeline should tolerate. The module is a dozen
        // small files; the seconds this costs are worth the failure mode it
        // removes.
        bUseUnity = false;
        // [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 21:05 UTC | no unity end ]
        PublicDependencyModuleNames.AddRange(new string[]
        {
            // [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 20:50 UTC | +InputCore start ]
            // InputCore is here for the dev arena's controls only. The
            // simulation reads no input at all - a fight that could be nudged by
            // a keypress would not be reproducible from its seed.
            // [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 20:50 UTC | +InputCore end ]
            "Core", "CoreUObject", "Engine", "Json", "InputCore", "UMG", "Slate", "SlateCore"
        });
    }
}
// [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 03:42 UTC | END ]
