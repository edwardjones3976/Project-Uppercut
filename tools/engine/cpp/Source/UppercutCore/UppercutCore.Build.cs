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
        PublicDependencyModuleNames.AddRange(new string[]
        {
            "Core", "CoreUObject", "Engine", "Json"
        });
    }
}
// [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 03:42 UTC | END ]
