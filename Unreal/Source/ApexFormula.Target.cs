// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

using UnrealBuildTool;
using System.Collections.Generic;

/// <summary>
/// Game target for ApexFormula.
///
/// Status: requires local compilation. This file has never been executed by
/// UnrealBuildTool in the authoring environment.
/// </summary>
public class ApexFormulaTarget : TargetRules
{
	public ApexFormulaTarget(TargetInfo Target) : base(Target)
	{
		Type = TargetType.Game;
		DefaultBuildSettings = BuildSettingsVersion.Latest;
		IncludeOrderVersion = EngineIncludeOrderVersion.Latest;

		// ApexFormula rule: warnings are not tolerated in project code.
		bUseUnityBuild = false;
		bUseAdaptiveUnityBuild = false;

		ExtraModuleNames.AddRange(new string[]
		{
			"ApexFormulaCore",
			"ApexFormulaVehicle",
			"ApexFormulaRace",
			"ApexFormulaUI",
			"ApexFormulaTests"
		});
	}
}
