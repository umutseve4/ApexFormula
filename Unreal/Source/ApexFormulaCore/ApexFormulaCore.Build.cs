// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

using UnrealBuildTool;

/// <summary>
/// ApexFormulaCore - data models, units, telemetry bus, logging, shared interfaces.
///
/// BOUNDARY RULE: this module depends on NO other ApexFormula module.
/// It must remain free of vehicle-specific and race-specific types.
/// See Documentation/TECHNICAL_ARCHITECTURE.md section 2.
/// </summary>
public class ApexFormulaCore : ModuleRules
{
	public ApexFormulaCore(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

		PublicDependencyModuleNames.AddRange(new string[]
		{
			"Core",
			"CoreUObject",
			"Engine",
			"DeveloperSettings"
		});

		PrivateDependencyModuleNames.AddRange(new string[]
		{
			"Projects"
		});
	}
}
