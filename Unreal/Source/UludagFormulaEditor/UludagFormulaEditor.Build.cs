// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

using UnrealBuildTool;

/// <summary>
/// UludagFormulaEditor - Data Asset validation, naming-convention checks,
/// track authoring helpers, asset audit commandlets.
///
/// BOUNDARY RULE: editor-only code never leaks into runtime modules.
/// Nothing in a runtime module may depend on this module.
/// </summary>
public class UludagFormulaEditor : ModuleRules
{
	public UludagFormulaEditor(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

		PublicDependencyModuleNames.AddRange(new string[]
		{
			"Core",
			"CoreUObject",
			"Engine",
			"ApexFormulaCore",
			"ApexFormulaVehicle",
			"ApexFormulaRace"
		});

		PrivateDependencyModuleNames.AddRange(new string[]
		{
			"UnrealEd",
			"Slate",
			"SlateCore",
			"EditorSubsystem"
		});
	}
}
