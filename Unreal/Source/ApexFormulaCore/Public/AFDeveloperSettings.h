// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

#pragma once

#include "CoreMinimal.h"
#include "Engine/DeveloperSettings.h"
#include "AFDeveloperSettings.generated.h"

class UAFQualityProfile;
class UAFBoneNameMap;

/**
 * UAFDeveloperSettings - project configuration surface.
 *
 * Architecture reference: TECHNICAL_ARCHITECTURE.md section 6.
 *
 * Backed by Config/DefaultApexFormula.ini. Holds pipeline paths, default Data
 * Asset references and telemetry toggles. This is the only sanctioned place
 * for project-wide tunables; components must not invent their own ini sections.
 *
 * Console variables for the same concepts use the "af." prefix and are for
 * debugging only. A cvar must never be the sole home of a shipping value.
 *
 * Status: statically inspected. requires local compilation.
 * requires Unreal Editor verification (settings panel appearance).
 */
UCLASS(Config = ApexFormula, DefaultConfig, meta = (DisplayName = "ApexFormula"))
class APEXFORMULACORE_API UAFDeveloperSettings : public UDeveloperSettings
{
	GENERATED_BODY()

public:
	UAFDeveloperSettings();

	/** Convenience accessor. Never returns null once the module is loaded. */
	static const UAFDeveloperSettings* Get();

	//
	// Pipeline paths
	//

	/**
	 * Project-relative directory the Blender pipeline writes FBX exports into.
	 * Relative so the repository stays machine independent; absolute paths in
	 * config are rejected by the static validator.
	 */
	UPROPERTY(Config, EditAnywhere, Category = "Pipeline")
	FString PipelineExportDirectory;

	/** Project-relative directory the Blender pipeline writes JSON reports into. */
	UPROPERTY(Config, EditAnywhere, Category = "Pipeline")
	FString PipelineReportDirectory;

	/** Content path imported vehicle assets are expected to land under. */
	UPROPERTY(Config, EditAnywhere, Category = "Pipeline")
	FString VehicleContentRoot;

	//
	// Default data assets
	//

	/** Quality profile applied when the player has made no choice. */
	UPROPERTY(Config, EditAnywhere, Category = "Defaults", meta = (AllowedClasses = "/Script/ApexFormulaCore.AFQualityProfile"))
	FSoftObjectPath DefaultQualityProfile;

	/** Bone name map every vehicle skeleton is validated against. */
	UPROPERTY(Config, EditAnywhere, Category = "Defaults", meta = (AllowedClasses = "/Script/ApexFormulaCore.AFBoneNameMap"))
	FSoftObjectPath DefaultBoneNameMap;

	//
	// Telemetry
	//

	/** Master switch for telemetry collection. */
	UPROPERTY(Config, EditAnywhere, Category = "Telemetry")
	bool bTelemetryEnabled = true;

	/** Write collected telemetry to disk at session end. */
	UPROPERTY(Config, EditAnywhere, Category = "Telemetry")
	bool bTelemetryWriteToDisk = false;

	/**
	 * Fallback pull rate in hertz, used when no quality profile is resolved.
	 * The quality profile value takes precedence when one is available.
	 */
	UPROPERTY(Config, EditAnywhere, Category = "Telemetry", meta = (ClampMin = "1.0"))
	double FallbackTelemetrySampleRateHz = 30.0;

	//
	// Diagnostics
	//

	/** Log every rule decision at Verbose rather than Log. Noisy. */
	UPROPERTY(Config, EditAnywhere, Category = "Diagnostics")
	bool bVerboseRuleLogging = false;

	/**
	 * Fail loudly instead of warning when a Data Asset fails validation at
	 * runtime. Recommended on for development configurations.
	 */
	UPROPERTY(Config, EditAnywhere, Category = "Diagnostics")
	bool bStrictDataValidation = true;

	//~ Begin UDeveloperSettings interface
	virtual FName GetCategoryName() const override;
	//~ End UDeveloperSettings interface

	/** Returns a list of human-readable configuration problems. Empty means valid. */
	TArray<FString> ValidateSelf() const;
};
