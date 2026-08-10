// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

using UnrealBuildTool;

/// <summary>
/// ApexFormulaRace - checkpoints, sectors, lap validation, timing, session state,
/// race control, penalties, pit rules, AI driver logic.
///
/// BOUNDARY RULE: this module MUST NOT depend on ApexFormulaVehicle.
/// It talks to vehicles only through interfaces declared in ApexFormulaCore
/// (IAFRaceParticipant, IAFTelemetrySource). This is what allows AI cars,
/// player cars and future networked cars to be treated uniformly.
/// See Documentation/TECHNICAL_ARCHITECTURE.md section 2.
/// </summary>
public class ApexFormulaRace : ModuleRules
{
	public ApexFormulaRace(ReadOnlyTargetRules Target) : base(Target)
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
		});
	}
}
