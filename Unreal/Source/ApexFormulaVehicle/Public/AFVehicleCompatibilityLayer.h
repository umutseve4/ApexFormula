// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

#pragma once

#include "CoreMinimal.h"
#include "UObject/Object.h"
#include "AFTypes.h"
#include "AFWheelSetup.h"
#include "AFVehicleCompatibilityLayer.generated.h"

class APawn;
class UActorComponent;
class USkeletalMeshComponent;

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
 * FAFVehicleBackendSetup - everything the backend needs, as plain data.
 *
 * Decision reference: DECISION_LOG.md D-032.
 * Milestone reference: MILESTONE_2_IMPLEMENTATION.md section 3.2.
 *
 * This struct is the configuration half of the D-008 chokepoint. It uses only
 * double, int32, bool, FName, FVector and FAFWheelSetup. It names NO engine
 * vehicle type, which is what allows it to live in a public header that
 * gameplay code includes.
 *
 * All lengths are METRES and all masses KILOGRAMS. Conversion to engine units
 * happens once, inside AFVehicleCompatibilityLayer.cpp. See D-013.
 */
USTRUCT(BlueprintType)
struct APEXFORMULAVEHICLE_API FAFVehicleBackendSetup
{
	GENERATED_BODY()

	/** Dry mass, kilograms. */
	UPROPERTY(BlueprintReadWrite, Category = "ApexFormula|Vehicle")
	double DryMassKg = 740.0;

	/** Centre of mass offset from the mesh origin, metres. */
	UPROPERTY(BlueprintReadWrite, Category = "ApexFormula|Vehicle")
	FVector CentreOfMassOffsetM = FVector::ZeroVector;

	/** One entry per wheel corner, in the order the definition declares them. */
	UPROPERTY(BlueprintReadWrite, Category = "ApexFormula|Vehicle")
	TArray<FAFWheelSetup> Wheels;

	/**
	 * Peak drive torque at the wheels, newton metres.
	 * A placeholder figure so the car moves. Not a real engine curve; the
	 * powertrain model is Milestone 10.
	 */
	UPROPERTY(BlueprintReadWrite, Category = "ApexFormula|Vehicle")
	double PeakDriveTorqueNm = 720.0;

	/** Engine speed at which peak torque is produced, revolutions per minute. */
	UPROPERTY(BlueprintReadWrite, Category = "ApexFormula|Vehicle")
	double PeakTorqueRpm = 10500.0;

	/** Maximum engine speed, revolutions per minute. */
	UPROPERTY(BlueprintReadWrite, Category = "ApexFormula|Vehicle")
	double MaxRpm = 13000.0;

	/** Number of forward gears. */
	UPROPERTY(BlueprintReadWrite, Category = "ApexFormula|Vehicle")
	int32 ForwardGearCount = 8;

	/**
	 * True when the backend should change gear by itself.
	 * Milestone 2 uses automatic shifting so that the acceptance criteria can
	 * be assessed without a working manual shift model.
	 */
	UPROPERTY(BlueprintReadWrite, Category = "ApexFormula|Vehicle")
	bool bUseAutomaticGears = true;

	/** Aerodynamic drag coefficient. Placeholder; real aero is Milestone 10. */
	UPROPERTY(BlueprintReadWrite, Category = "ApexFormula|Vehicle")
	double DragCoefficient = 0.85;

	/** Frontal reference area, square metres. Placeholder. */
	UPROPERTY(BlueprintReadWrite, Category = "ApexFormula|Vehicle")
	double FrontalAreaM2 = 1.5;

	/** Returns a list of human-readable problems. Empty means valid. */
	TArray<FString> ValidateSelf() const;
};

/**
 * UAFVehicleCompatibilityLayer - the ONLY place engine vehicle API may be used.
 *
 * Decision reference: DECISION_LOG.md D-008, D-031, D-032, D-036.
 * Architecture reference: TECHNICAL_ARCHITECTURE.md section 11.
 * Milestone reference: MILESTONE_2_IMPLEMENTATION.md section 3.
 *
 * Rationale. Chaos Vehicles is an engine subsystem whose API has changed
 * between Unreal releases. Every call into it is funnelled through this class
 * so that an engine upgrade touches one file rather than every component.
 * The static validator enforces this: engine vehicle symbols found in any
 * other file are a hard failure.
 *
 * Milestone 2 scope. This layer now BINDS a backend, where Milestone 1
 * deliberately bound none. Per D-031 the layer creates and owns the engine
 * movement component itself and hands the pawn back only an opaque
 * UActorComponent pointer. Consequently no engine vehicle type appears even in
 * THIS header - only in AFVehicleCompatibilityLayer.cpp, which nothing
 * includes. That is stricter than D-008 requires and is deliberate.
 *
 * Status: statically inspected. requires local compilation.
 * The backend binding itself is unverified: the Chaos Vehicles module and
 * plugin names for Unreal Engine 5.8 are assumptions recorded in
 * VERSION_MATRIX.md section 5.21, and every engine call site in the .cpp
 * carries an ASSUMPTION comment.
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
	 * Callers must handle false without crashing, so that rules and timing
	 * logic remain testable with no car.
	 */
	UFUNCTION(BlueprintPure, Category = "ApexFormula|Vehicle")
	bool IsBackendAvailable() const;

	//
	// Backend lifecycle. Milestone 2.
	//

	/**
	 * Creates the engine movement component on OwnerPawn and binds it to
	 * MeshComponent. Returns the created component as an opaque pointer, or
	 * nullptr on failure.
	 *
	 * The caller must NOT cast the returned pointer to an engine vehicle type.
	 * It is returned only so the pawn can hold a reference for lifetime and
	 * for the editor's component list.
	 *
	 * Safe to call once. A second call logs an error and returns the existing
	 * component.
	 */
	UFUNCTION(BlueprintCallable, Category = "ApexFormula|Vehicle")
	UActorComponent* CreateBackendMovement(APawn* OwnerPawn, USkeletalMeshComponent* MeshComponent);

	/**
	 * Applies Setup to the bound backend.
	 * Returns false and logs when no backend is bound or Setup is invalid.
	 * This is where metres become centimetres, exactly once.
	 */
	UFUNCTION(BlueprintCallable, Category = "ApexFormula|Vehicle")
	bool ConfigureBackend(const FAFVehicleBackendSetup& Setup);

	/**
	 * Applies a driver input frame to the bound backend.
	 * Returns true when the input was consumed by a backend.
	 * Records the frame and returns false when no backend is bound.
	 */
	UFUNCTION(BlueprintCallable, Category = "ApexFormula|Vehicle")
	bool ApplyInputFrame(const FAFVehicleInputFrame& InputFrame);

	/**
	 * Sets the handbrake state.
	 * Kept separate from FAFVehicleInputFrame because the handbrake is a test
	 * affordance for Milestone 2, not part of the replayable driver-intent
	 * contract. Promoting it into the input frame would change a struct that
	 * replay determinism depends on, for a feature that may not survive.
	 */
	UFUNCTION(BlueprintCallable, Category = "ApexFormula|Vehicle")
	bool SetHandbrake(bool bEngaged);

	/**
	 * Zeroes linear and angular velocity on the backend.
	 * Used by the reset affordance. Does not move the actor; the caller owns
	 * the transform change, because only the caller knows where "upright and
	 * safe" is.
	 */
	UFUNCTION(BlueprintCallable, Category = "ApexFormula|Vehicle")
	bool ZeroBackendVelocity();

	//
	// Backend state reads.
	//

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

	/** Reads engine speed from the bound backend, revolutions per minute. */
	UFUNCTION(BlueprintPure, Category = "ApexFormula|Vehicle")
	double GetEngineRpm() const;

	/** True when every wheel reports contact with a surface. */
	UFUNCTION(BlueprintPure, Category = "ApexFormula|Vehicle")
	bool AreAllWheelsGrounded() const;

	/** The most recent input frame handed to this layer. */
	UFUNCTION(BlueprintPure, Category = "ApexFormula|Vehicle")
	const FAFVehicleInputFrame& GetLastInputFrame() const { return LastInputFrame; }

	/** How many input frames this layer has received. Used by tests. */
	UFUNCTION(BlueprintPure, Category = "ApexFormula|Vehicle")
	int32 GetAppliedFrameCount() const { return AppliedFrameCount; }

	/** True once ConfigureBackend has succeeded. */
	UFUNCTION(BlueprintPure, Category = "ApexFormula|Vehicle")
	bool IsBackendConfigured() const { return bBackendConfigured; }

	/**
	 * True once the per-wheel numeric parameters have reached the backend's
	 * wheel objects. See D-036: those objects do not exist until the movement
	 * component registers, which is after ConfigureBackend runs.
	 */
	UFUNCTION(BlueprintPure, Category = "ApexFormula|Vehicle")
	bool AreWheelParametersApplied() const { return bWheelParametersApplied; }

	/**
	 * Attempts to push the retained wheel parameters into the backend's wheel
	 * objects. Returns true when they are applied, or were already applied.
	 * Cheap and idempotent; called from ApplyInputFrame until it succeeds.
	 */
	UFUNCTION(BlueprintCallable, Category = "ApexFormula|Vehicle")
	bool TryApplyWheelParameters();

private:
	/** Cached backend description, filled in the constructor. */
	FAFVehicleBackendInfo BackendInfo;

	/** Last input handed in, retained so tests can observe the plumbing. */
	FAFVehicleInputFrame LastInputFrame;

	/** Count of ApplyInputFrame calls. */
	int32 AppliedFrameCount = 0;

	/** True once ConfigureBackend has succeeded. */
	bool bBackendConfigured = false;

	/** Metric wheel data retained from ConfigureBackend. See D-036. */
	TArray<FAFWheelSetup> PendingWheels;

	/** True once PendingWheels has reached the backend's wheel objects. */
	bool bWheelParametersApplied = false;

	/**
	 * The engine movement component, held as the most-derived type this header
	 * is permitted to name. The .cpp casts it to the real engine vehicle type.
	 * Declaring it as UActorComponent is what keeps this header engine-vehicle
	 * free; see D-031.
	 */
	UPROPERTY()
	TObjectPtr<UActorComponent> BackendMovement;
};
