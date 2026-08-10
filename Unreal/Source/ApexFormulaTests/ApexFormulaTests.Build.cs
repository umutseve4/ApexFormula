// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

using UnrealBuildTool;

/// <summary>
/// ApexFormulaTests - automation tests and the deterministic replay harness.
///
/// BOUNDARY RULE: nothing depends on this module. It is a leaf.
/// Tests here must be pure-logic and must not require a rendered frame.
/// See Documentation/TECHNICAL_ARCHITECTURE.md section 9, tier 2.
/// </summary>
public class ApexFormulaTests : ModuleRules
{
	public ApexFormulaTests(ReadOnlyTargetRules Target) : base(Target)
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
		});
	}
}
