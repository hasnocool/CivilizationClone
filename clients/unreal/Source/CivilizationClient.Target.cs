// clients/unreal/Source/CivilizationClient.Target.cs
using UnrealBuildTool;
using System.Collections.Generic;

public class CivilizationClientTarget : TargetRules
{
    public CivilizationClientTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Game;
        DefaultBuildSettings = BuildSettingsVersion.V6;
        IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
        ExtraModuleNames.Add("CivilizationClient");
    }
}
