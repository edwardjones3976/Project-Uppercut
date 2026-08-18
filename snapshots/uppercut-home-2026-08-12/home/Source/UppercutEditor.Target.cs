// Copyright Project Uppercut. Clean UE 5.8 editor target.
using UnrealBuildTool;

public class UppercutEditorTarget : TargetRules
{
	public UppercutEditorTarget(TargetInfo Target) : base(Target)
	{
		Type = TargetType.Editor;
		DefaultBuildSettings = BuildSettingsVersion.Latest;
		IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
		ExtraModuleNames.Add("UppercutCore");
	}
}
