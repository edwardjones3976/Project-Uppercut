// [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 03:42 UTC | START ]
// Phase H staged editor target. The commandlet runs under UnrealEditor-Cmd,
// which is this target. Never compiled on this machine yet - see README.md.
using UnrealBuildTool;

public class UppercutSandboxEditorTarget : TargetRules
{
    public UppercutSandboxEditorTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Editor;
        DefaultBuildSettings = BuildSettingsVersion.Latest;
        IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
        ExtraModuleNames.Add("UppercutCore");
    }
}
// [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 03:42 UTC | END ]
