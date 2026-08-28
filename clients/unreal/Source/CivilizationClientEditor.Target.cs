// clients/unreal/Source/CivilizationClientEditor.Target.cs
using UnrealBuildTool;
using System.Collections.Generic;

public class CivilizationClientEditorTarget : TargetRules
{
    public CivilizationClientEditorTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Editor;
        DefaultBuildSettings = BuildSettingsVersion.V6;
        IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
        ExtraModuleNames.Add("CivilizationClient");
    }
}
