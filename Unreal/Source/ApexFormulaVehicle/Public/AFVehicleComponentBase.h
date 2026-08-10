// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "AFTelemetrySourceInterface.h"
#include "AFVehicleComponentBase.generated.h"

/**
 * UAFVehicleComponentBase - shared base for every vehicle subsystem component.
 *
 * Architecture reference: TECHNICAL_ARCHITECTURE.md section 4.
 *
 * Composition is mandatory and deep pawn inheritance is prohibited, so vehicle
 * behaviour lives in components attached to a single pawn. This base exists to
 * give those components one consistent lifecycle and one telemetry contract,
 * NOT to become a dumping ground for behaviour. It is intentionally thin:
 * exactly one level of inheritance is permitted below it.
 *
 * Subclasses planned for later milestones: tyre set, aero, energy system,
 * fuel, brake, drivetrain, vehicle setup, vehicle telemetry, race participant.
 *
 * Status: statically inspected. requires local compilation.
 */
UCLASS(Abstract, BlueprintType, ClassGroup = "ApexFormula", meta = (BlueprintSpawnableComponent))
class APEXFORMULAVEHICLE_API UAFVehicleComponentBase
	: public UActorComponent
	, public IAFTelemetrySource
{
	GENERATED_BODY()

public:
	UAFVehicleComponentBase();

	/**
	 * Stable identifier for this subsystem, e.g. "tyres".
	 * Used to prefix telemetry channels and log lines. Set by each subclass
	 * constructor; never left as NAME_None.
	 */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "ApexFormula|Vehicle")
	FName SubsystemId = NAME_None;

	/**
	 * When false the component performs no per-tick work and publishes no
	 * telemetry. Used by lower quality profiles and by the test harness.
	 */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "ApexFormula|Vehicle")
	bool bSubsystemEnabled = true;

	/**
	 * Applies configuration from Data Assets held by the owning pawn.
	 * Called once after all components exist, so ordering between components
	 * is explicit rather than dependent on construction order.
	 * Base implementation marks the component configured.
	 */
	UFUNCTION(BlueprintCallable, Category = "ApexFormula|Vehicle")
	virtual void ApplyConfiguration();

	/** True once ApplyConfiguration has completed. */
	UFUNCTION(BlueprintPure, Category = "ApexFormula|Vehicle")
	bool IsConfigured() const { return bConfigured; }

	/**
	 * Resets all runtime state to session start. Must be deterministic:
	 * the same reset followed by the same inputs must give the same result.
	 */
	UFUNCTION(BlueprintCallable, Category = "ApexFormula|Vehicle")
	virtual void ResetSubsystem();

	//~ Begin IAFTelemetrySource interface
	/** Base implementation appends nothing. Subclasses append their channels. */
	virtual void CollectTelemetry(double SessionTime, TArray<FAFTelemetrySample>& OutSamples) const override;

	/** Base implementation returns an empty list. */
	virtual TArray<FName> GetProvidedTelemetryChannels() const override;
	//~ End IAFTelemetrySource interface

protected:
	/** Set by ApplyConfiguration, cleared by ResetSubsystem. */
	bool bConfigured = false;
};
