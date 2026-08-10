// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

using UnrealBuildTool;

/// <summary>
/// ApexFormulaUI - HUD view models, setup screen view models, telemetry display models.
///
/// BOUNDARY RULE: the UI module READS; it does not DECIDE.
/// No race rule, penalty or lap validity may be computed here.
/// It depends on ApexFormulaCore only (of the ApexFormula modules).
/// </summary>
public class ApexFormulaUI : ModuleRules
{
	public ApexFormulaUI(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

		PublicDependencyModuleNames.AddRange(new string[]
		{
			"Core",
			"CoreUObject",
			"Engine",
			"ApexFormulaCore"
		});

		PrivateDependencyModuleNames.AddRange(new string[]
		{
			"UMG",
			"Slate",
			"SlateCore"
		});
	}
}
