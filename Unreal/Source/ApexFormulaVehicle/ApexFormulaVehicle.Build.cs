// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

using UnrealBuildTool;

/// <summary>
/// ApexFormulaVehicle - vehicle pawn, simulation components, setup application.
///
/// BOUNDARY RULE: may depend on ApexFormulaCore only (of the ApexFormula modules).
/// It must never depend on ApexFormulaRace or ApexFormulaUI.
///
/// UNCERTAINTY: the module name "ChaosVehicles" and its availability in
/// Unreal Engine 5.8 is an ASSUMPTION REQUIRING VERIFICATION.
/// See Documentation/VERSION_MATRIX.md section 5.21 and
/// Documentation/VEHICLE_SYSTEM_DECISION.md section 7.
/// All engine vehicle API usage is isolated behind UAFVehicleCompatibilityLayer.
///
/// Milestone 2 additions:
///   InputCore  - key and axis identifiers referenced by input mapping assets.
/// EnhancedInput was already listed before any input code existed; Milestone 2
/// is the first milestone that actually consumes it, in AFPlayerController.cpp.
/// </summary>
public class ApexFormulaVehicle : ModuleRules
{
	public ApexFormulaVehicle(ReadOnlyTargetRules Target) : base(Target)
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
			"PhysicsCore",
			"ChaosVehicles",
			"EnhancedInput",
			"InputCore"
		});
	}
}
