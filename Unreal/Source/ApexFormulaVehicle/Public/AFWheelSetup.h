// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

#pragma once

#include "CoreMinimal.h"
#include "AFWheelSetup.generated.h"

/**
 * FAFWheelSetup - description of one wheel corner, in ApexFormula design units.
 *
 * Decision reference: DECISION_LOG.md D-012 (bone contract), D-013 (units),
 * D-032 (configuration crosses the compatibility boundary as plain data).
 * Milestone reference: MILESTONE_2_IMPLEMENTATION.md section 4.
 *
 * This struct contains NO engine vehicle types, by design. It is the data half
 * of the D-008 chokepoint: gameplay code and Data Assets author this, and
 * AFVehicleCompatibilityLayer.cpp is the only place that translates it into
 * whatever the engine's vehicle API actually wants.
 *
 * All lengths are METRES. The conversion to centimetres happens exactly once,
 * at the engine boundary, inside AFVehicleCompatibilityLayer.cpp. Never store a
 * converted value back into this struct.
 *
 * Every default below is a fictional ApexFormula design value chosen so that a
 * placeholder car sits on its wheels and can be driven. They are not
 * measurements of any real vehicle and must never be presented as such.
 *
 * Status: statically inspected. requires local compilation.
 */
USTRUCT(BlueprintType)
struct APEXFORMULAVEHICLE_API FAFWheelSetup
{
	GENERATED_BODY()

	/**
	 * Skeleton bone this wheel drives.
	 * Must be one of the four wheel bones in the D-012 contract:
	 * AF_Wheel_FL, AF_Wheel_FR, AF_Wheel_RL, AF_Wheel_RR.
	 * Validated against UAFBoneNameMap; a mismatch is a hard failure, not a
	 * warning, because a silently unbound wheel looks like a physics bug.
	 */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Wheel")
	FName BoneName = NAME_None;

	/** Rolling radius, metres. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Wheel", meta = (ClampMin = "0.01"))
	double RadiusM = 0.36;

	/** Tyre width, metres. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Wheel", meta = (ClampMin = "0.01"))
	double WidthM = 0.30;

	/** True when this wheel turns with steering input. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Wheel")
	bool bAffectedBySteering = false;

	/** True when this wheel locks under handbrake. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Wheel")
	bool bAffectedByHandbrake = false;

	/** True when this wheel receives drive torque. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Wheel")
	bool bDriven = false;

	/** Maximum steering angle at this corner, degrees. Zero when not steered. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Wheel", meta = (ClampMin = "0.0", ClampMax = "90.0"))
	double MaxSteerAngleDeg = 0.0;

	/** Suspension rest length, metres. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Suspension", meta = (ClampMin = "0.0"))
	double SuspensionRestLengthM = 0.12;

	/** Permitted travel above rest, metres. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Suspension", meta = (ClampMin = "0.0"))
	double SuspensionMaxRaiseM = 0.06;

	/** Permitted travel below rest, metres. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Suspension", meta = (ClampMin = "0.0"))
	double SuspensionMaxDropM = 0.06;

	/**
	 * Suspension natural frequency, hertz.
	 * Higher is stiffer. A placeholder value; not a real setup parameter.
	 */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Suspension", meta = (ClampMin = "0.1"))
	double SuspensionNaturalFrequencyHz = 7.0;

	/**
	 * Suspension damping ratio, dimensionless.
	 * 1.0 is critically damped. Values below 0.5 are the usual cause of the
	 * "car oscillates at rest" failure that Milestone 2 criterion A2 forbids.
	 */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Suspension", meta = (ClampMin = "0.0", ClampMax = "2.0"))
	double SuspensionDampingRatio = 1.0;

	/** Maximum braking torque at this corner, newton metres. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Brakes", meta = (ClampMin = "0.0"))
	double MaxBrakeTorqueNm = 4000.0;

	/** Maximum handbrake torque at this corner, newton metres. Zero when not affected. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Brakes", meta = (ClampMin = "0.0"))
	double MaxHandbrakeTorqueNm = 0.0;

	FAFWheelSetup() = default;

	/**
	 * Returns a list of human-readable problems. Empty means valid.
	 * Checks internal consistency only; bone-name agreement against
	 * UAFBoneNameMap is checked by the owning definition, which is the only
	 * thing that holds the map reference.
	 */
	TArray<FString> ValidateSelf() const
	{
		TArray<FString> Problems;

		if (BoneName.IsNone())
		{
			Problems.Add(TEXT("BoneName is unset."));
		}

		if (RadiusM <= 0.0)
		{
			Problems.Add(TEXT("RadiusM must be greater than zero."));
		}

		if (WidthM <= 0.0)
		{
			Problems.Add(TEXT("WidthM must be greater than zero."));
		}

		if (bAffectedBySteering && MaxSteerAngleDeg <= 0.0)
		{
			Problems.Add(TEXT("Wheel is steered but MaxSteerAngleDeg is zero."));
		}

		if (!bAffectedBySteering && MaxSteerAngleDeg > 0.0)
		{
			Problems.Add(TEXT("MaxSteerAngleDeg is set but wheel is not steered."));
		}

		if (bAffectedByHandbrake && MaxHandbrakeTorqueNm <= 0.0)
		{
			Problems.Add(TEXT("Wheel is handbraked but MaxHandbrakeTorqueNm is zero."));
		}

		if (SuspensionDampingRatio < 0.5)
		{
			Problems.Add(TEXT(
				"SuspensionDampingRatio below 0.5 is very likely to oscillate at rest, "
				"which Milestone 2 acceptance criterion A2 forbids."));
		}

		return Problems;
	}
};
