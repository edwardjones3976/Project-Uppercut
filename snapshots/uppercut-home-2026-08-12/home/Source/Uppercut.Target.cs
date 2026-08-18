// Copyright Project Uppercut. Clean UE 5.8 game target.
using UnrealBuildTool;

public class UppercutTarget : TargetRules
{
	public UppercutTarget(TargetInfo Target) : base(Target)
	{
		Type = TargetType.Game;
		DefaultBuildSettings = BuildSettingsVersion.Latest;
		IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
		ExtraModuleNames.Add("UppercutCore");
	}
}
