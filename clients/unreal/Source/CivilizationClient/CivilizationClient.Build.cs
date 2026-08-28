// clients/unreal/Source/CivilizationClient/CivilizationClient.Build.cs
using UnrealBuildTool;

public class CivilizationClient : ModuleRules
{
    public CivilizationClient(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        PublicDependencyModuleNames.AddRange(new[] { "Core", "CoreUObject", "Engine" });
        PrivateDependencyModuleNames.AddRange(new[] { "Slate", "SlateCore", "InputCore", "HTTP", "Json", "JsonUtilities" });
    }
}
