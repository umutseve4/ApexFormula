// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

using UnrealBuildTool;
using System.Collections.Generic;

/// <summary>
/// Editor target for ApexFormula.
///
/// Status: requires local compilation. This file has never been executed by
/// UnrealBuildTool in the authoring environment.
/// </summary>
public class ApexFormulaEditorTarget : TargetRules
{
	public ApexFormulaEditorTarget(TargetInfo Target) : base(Target)
	{
		Type = TargetType.Editor;
		DefaultBuildSettings = BuildSettingsVersion.Latest;
		IncludeOrderVersion = EngineIncludeOrderVersion.Latest;

		bUseUnityBuild = false;
		bUseAdaptiveUnityBuild = false;

		ExtraModuleNames.AddRange(new string[]
		{
			"ApexFormulaCore",
			"ApexFormulaVehicle",
			"ApexFormulaRace",
			"ApexFormulaUI",
			"ApexFormulaEditor",
			"ApexFormulaTests"
		});
	}
}
