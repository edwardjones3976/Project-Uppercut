// [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 03:42 UTC | START ]
// Phase H staged target (Decision 0012 slice item 3). Never compiled on this
// machine yet - see tools/engine/cpp/README.md before trusting it.
using UnrealBuildTool;

public class UppercutSandboxTarget : TargetRules
{
    public UppercutSandboxTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Game;
        DefaultBuildSettings = BuildSettingsVersion.Latest;
        IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
        ExtraModuleNames.Add("UppercutCore");
    }
}
// [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 03:42 UTC | END ]
