// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "AFUnits.generated.h"

/**
 * ApexFormula unit contract.
 *
 * Mirrors BlenderPipeline/scripts/af_pipeline_config.py section 1 exactly.
 * Decision reference: DECISION_LOG.md D-013 (unit and axis contract).
 *
 * Authoring space (Blender): metres. +X forward, +Y left, +Z up.
 * Runtime space (Unreal):    centimetres. +X forward, +Y RIGHT, +Z up.
 *
 * The Y axis flips at the boundary. That flip lives in exactly one place in
 * each language: blender_point_to_unreal_cm() in Python, and
 * FAFUnits::BlenderPointToUnrealCm() here.
 *
 * Status: statically inspected. requires local compilation.
 */
UCLASS()
class APEXFORMULACORE_API UAFUnitsHelper : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:
	/** Centimetres per authoring metre. Must equal af_pipeline_config.CM_PER_UNIT. */
	static constexpr double CmPerMetre = 100.0;

	/** Metres to Unreal centimetres. */
	UFUNCTION(BlueprintPure, Category = "ApexFormula|Units")
	static double MetresToCm(double Metres) { return Metres * CmPerMetre; }

	/** Unreal centimetres to authoring metres. */
	UFUNCTION(BlueprintPure, Category = "ApexFormula|Units")
	static double CmToMetres(double Centimetres) { return Centimetres / CmPerMetre; }

	/**
	 * Convert an authoring-space point (Blender, metres) to runtime space
	 * (Unreal, centimetres).
	 *
	 * Contract: (x, y, z) metres -> (x * 100, -y * 100, z * 100) centimetres.
	 * The negation of Y is the handedness flip and is deliberate.
	 */
	UFUNCTION(BlueprintPure, Category = "ApexFormula|Units")
	static FVector BlenderPointToUnrealCm(const FVector& BlenderMetres)
	{
		return FVector(
			BlenderMetres.X * CmPerMetre,
			-BlenderMetres.Y * CmPerMetre,
			BlenderMetres.Z * CmPerMetre);
	}

	/** Inverse of BlenderPointToUnrealCm. */
	UFUNCTION(BlueprintPure, Category = "ApexFormula|Units")
	static FVector UnrealCmToBlenderPoint(const FVector& UnrealCm)
	{
		return FVector(
			UnrealCm.X / CmPerMetre,
			-UnrealCm.Y / CmPerMetre,
			UnrealCm.Z / CmPerMetre);
	}

	/** Metres per second to kilometres per hour. */
	UFUNCTION(BlueprintPure, Category = "ApexFormula|Units")
	static double MpsToKph(double MetresPerSecond) { return MetresPerSecond * 3.6; }

	/** Kilometres per hour to metres per second. */
	UFUNCTION(BlueprintPure, Category = "ApexFormula|Units")
	static double KphToMps(double KilometresPerHour) { return KilometresPerHour / 3.6; }

	/** Unreal cm/s to km/h. Convenience for HUD speed readouts. */
	UFUNCTION(BlueprintPure, Category = "ApexFormula|Units")
	static double UnrealSpeedToKph(double CentimetresPerSecond)
	{
		return (CentimetresPerSecond / CmPerMetre) * 3.6;
	}

	/** Degrees Celsius to Kelvin. Tyre and brake thermal models use Celsius. */
	UFUNCTION(BlueprintPure, Category = "ApexFormula|Units")
	static double CelsiusToKelvin(double Celsius) { return Celsius + 273.15; }

	/**
	 * Format a lap or sector time in seconds as m:ss.mmm.
	 * Negative values are formatted with a leading minus (used for deltas).
	 */
	UFUNCTION(BlueprintPure, Category = "ApexFormula|Units")
	static FString FormatLapTime(double Seconds);
};
