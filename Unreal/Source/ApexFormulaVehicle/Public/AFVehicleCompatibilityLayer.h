// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

#pragma once

#include "CoreMinimal.h"
#include "UObject/Object.h"
#include "AFTypes.h"
#include "AFVehicleCompatibilityLayer.generated.h"

/**
 * Describes the engine vehicle backend this build was compiled against.
 */
USTRUCT(BlueprintType)
struct APEXFORMULAVEHICLE_API FAFVehicleBackendInfo
{
	GENERATED_BODY()

	/** Backend identifier, e.g. "chaos". Never a marketing name. */
	UPROPERTY(BlueprintReadOnly, Category = "ApexFormula|Vehicle")
	FName BackendId = NAME_None;

	/** True when a real engine vehicle backend was resolved at startup. */
	UPROPERTY(BlueprintReadOnly, Category = "ApexFormula|Vehicle")
	bool bBackendAvailable = false;

	/** Human-readable note explaining the current state. */
	UPROPERTY(BlueprintReadOnly, Category = "ApexFormula|Vehicle")
	FString StatusMessage;
};

/**
 * UAFVehicleCompatibilityLayer - the ONLY place engine vehicle API may be used.
 *
 * Decision reference: DECISION_LOG.md D-008.
 * Architecture reference: TECHNICAL_ARCHITECTURE.md section 11.
 *
 * Rationale. Chaos Vehicles is an engine subsystem whose API has changed
 * between Unreal releases. Every call into it is funnelled through this class
 * so that an engine upgrade touches one file rather than every component.
 * The static validator enforces this: engine vehicle symbols found in any
 * other file are a hard failure.
 *
 * Milestone 1 scope. This layer is deliberately a STUB. It declares the
 * surface and reports that no backend is bound. No physics is wired, because
 * Milestone 1 explicitly excludes vehicle physics.
 *
 * Status: statically inspected. requires local compilation.
 * The backend binding itself is unverified: the Chaos Vehicles module and
 * plugin names for Unreal Engine 5.8 are assumptions recorded in
 * VERSION_MATRIX.md section 5.21.
 */
UCLASS(BlueprintType)
class APEXFORMULAVEHICLE_API UAFVehicleCompatibilityLayer : public UObject
{
	GENERATED_BODY()

public:
	UAFVehicleCompatibilityLayer();

	/** Describes what backend, if any, this build resolved. */
	UFUNCTION(BlueprintPure, Category = "ApexFormula|Vehicle")
	FAFVehicleBackendInfo GetBackendInfo() const;

	/**
	 * True when a real engine vehicle backend is bound and usable.
	 * Milestone 1 always returns false. Callers must handle false without
	 * crashing, so that rules and timing logic remain testable with no car.
	 */
	UFUNCTION(BlueprintPure, Category = "ApexFormula|Vehicle")
	bool IsBackendAvailable() const;

	/**
	 * Applies a driver input frame to the bound backend.
	 * Returns true when the input was consumed by a backend.
	 * Milestone 1 records the frame and returns false.
	 */
	UFUNCTION(BlueprintCallable, Category = "ApexFormula|Vehicle")
	bool ApplyInputFrame(const FAFVehicleInputFrame& InputFrame);

	/**
	 * Reads forward speed from the bound backend, kilometres per hour.
	 * Returns 0 when no backend is bound.
	 */
	UFUNCTION(BlueprintPure, Category = "ApexFormula|Vehicle")
	double GetForwardSpeedKph() const;

	/**
	 * Reads the currently engaged gear from the bound backend.
	 * Returns 0 (neutral) when no backend is bound.
	 */
	UFUNCTION(BlueprintPure, Category = "ApexFormula|Vehicle")
	int32 GetCurrentGear() const;

	/** The most recent input frame handed to this layer. */
	UFUNCTION(BlueprintPure, Category = "ApexFormula|Vehicle")
	const FAFVehicleInputFrame& GetLastInputFrame() const { return LastInputFrame; }

	/** How many input frames this layer has received. Used by tests. */
	UFUNCTION(BlueprintPure, Category = "ApexFormula|Vehicle")
	int32 GetAppliedFrameCount() const { return AppliedFrameCount; }

private:
	/** Cached backend description, filled in the constructor. */
	FAFVehicleBackendInfo BackendInfo;

	/** Last input handed in, retained so tests can observe the plumbing. */
	FAFVehicleInputFrame LastInputFrame;

	/** Count of ApplyInputFrame calls. */
	int32 AppliedFrameCount = 0;
};
