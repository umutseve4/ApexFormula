// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Pawn.h"
#include "AFTypes.h"
#include "AFRaceParticipantInterface.h"
#include "AFVehiclePawn.generated.h"

class USkeletalMeshComponent;
class USpringArmComponent;
class UCameraComponent;
class UAFVehicleCompatibilityLayer;
class UAFVehicleDefinition;
class UAFVehicleComponentBase;

/**
 * AAFVehiclePawn - the single vehicle actor.
 *
 * Architecture reference: TECHNICAL_ARCHITECTURE.md sections 4 and 11.
 * Milestone reference: MILESTONE_2_IMPLEMENTATION.md sections 3 and 6.
 *
 * Deep pawn inheritance is prohibited. There is exactly one vehicle pawn
 * class; every behavioural difference comes from Data Assets and from
 * UAFVehicleComponentBase subclasses attached to it.
 *
 * It implements IAFRaceParticipant so the Race module can time it, position it
 * and classify it WITHOUT depending on ApexFormulaVehicle. That interface is
 * the entire reason the Race module compiles with no vehicle types in scope.
 *
 * D-031. This pawn does NOT derive from any engine wheeled-vehicle pawn. Doing
 * so would place an engine vehicle type in the base-class list, and therefore
 * in every translation unit that includes this header, defeating D-008. The
 * compatibility layer creates and owns the engine movement component and hands
 * this pawn back only an opaque UActorComponent pointer.
 *
 * D-035. GetParticipantDisplayName returns FString because that is what
 * IAFRaceParticipant declares. DriverDisplayName remains FText because it is
 * authored content that must be localisable; the override converts at the
 * boundary. A mismatched override return type is not an overload - it is a
 * compile error, and it survived Milestone 1 only because nothing in this
 * repository can compile C++.
 *
 * Milestone 2 scope. Physics backend bound, driver input consumed, chase camera
 * present, reset affordance present. No cockpit camera (Milestone 6), no
 * powertrain model (Milestone 10), no timing (Milestone 3).
 *
 * Status: statically inspected. requires local compilation.
 * requires Unreal Editor verification (spawning and component layout).
 * requires playtesting (handling, camera, reset behaviour).
 */
UCLASS(BlueprintType, Blueprintable)
class APEXFORMULAVEHICLE_API AAFVehiclePawn
	: public APawn
	, public IAFRaceParticipant
{
	GENERATED_BODY()

public:
	AAFVehiclePawn();

	/** Root visual representation. Bound to the pipeline skeletal mesh. */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "ApexFormula|Vehicle")
	TObjectPtr<USkeletalMeshComponent> VehicleMeshComponent;

	/** Chase camera boom. Configured per D-034. */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "ApexFormula|Camera")
	TObjectPtr<USpringArmComponent> ChaseCameraBoom;

	/** Chase camera. The only camera in Milestone 2. */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "ApexFormula|Camera")
	TObjectPtr<UCameraComponent> ChaseCamera;

	/** The vehicle this pawn was configured from. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Vehicle")
	TObjectPtr<UAFVehicleDefinition> VehicleDefinition;

	/**
	 * Applies VehicleDefinition and calls ApplyConfiguration on every attached
	 * UAFVehicleComponentBase, in a deterministic order.
	 * Milestone 2 additionally builds an FAFVehicleBackendSetup from the
	 * definition and hands it to the compatibility layer.
	 * Returns false and logs when VehicleDefinition is missing or invalid.
	 */
	UFUNCTION(BlueprintCallable, Category = "ApexFormula|Vehicle")
	bool ApplyVehicleDefinition();

	/**
	 * Hands a driver input frame to the compatibility layer.
	 * Shift flags are edges: the caller sets them true for exactly one frame.
	 */
	UFUNCTION(BlueprintCallable, Category = "ApexFormula|Vehicle")
	void SubmitInputFrame(const FAFVehicleInputFrame& InputFrame);

	/** Sets the handbrake. Separate from the input frame; see the layer header. */
	UFUNCTION(BlueprintCallable, Category = "ApexFormula|Vehicle")
	void SetHandbrake(bool bEngaged);

	/**
	 * Places the vehicle upright at the last known good transform, zeroes its
	 * velocities and increments the reset counter.
	 *
	 * Milestone 3 will observe this through EAFLapInvalidationReason::VehicleReset,
	 * which already exists in AFTypes.h. Wiring it now means Milestone 3 does
	 * not have to retrofit an invalidation source.
	 */
	UFUNCTION(BlueprintCallable, Category = "ApexFormula|Vehicle")
	void ResetVehicle();

	/** How many times ResetVehicle has run this session. */
	UFUNCTION(BlueprintPure, Category = "ApexFormula|Vehicle")
	int32 GetResetCount() const { return ResetCount; }

	/** The reason code a lap timer should use when this pawn was last reset. */
	UFUNCTION(BlueprintPure, Category = "ApexFormula|Vehicle")
	EAFLapInvalidationReason GetLastResetReason() const { return EAFLapInvalidationReason::VehicleReset; }

	/** The compatibility layer instance owned by this pawn. Never null after construction. */
	UFUNCTION(BlueprintPure, Category = "ApexFormula|Vehicle")
	UAFVehicleCompatibilityLayer* GetCompatibilityLayer() const { return CompatibilityLayer; }

	/** Numeric id assigned by the session. Also the IAFRaceParticipant id. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "ApexFormula|Race")
	int32 ParticipantId = INDEX_NONE;

	/** Fictional driver name shown in timing screens. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "ApexFormula|Race")
	FText DriverDisplayName;

	//~ Begin IAFRaceParticipant interface
	virtual int32 GetParticipantId() const override;
	virtual FString GetParticipantDisplayName() const override;
	virtual FVector GetParticipantLocation() const override;
	virtual FVector GetParticipantForward() const override;
	virtual double GetParticipantSpeedKph() const override;
	virtual bool IsParticipantActive() const override;
	//~ End IAFRaceParticipant interface

protected:
	virtual void BeginPlay() override;
	virtual void Tick(float DeltaSeconds) override;

	/**
	 * Records the current transform as safe to reset to, when the vehicle is
	 * upright, grounded and not moving backwards. Called from Tick.
	 */
	void UpdateLastGoodTransform();

private:
	/** Sole owner of engine vehicle API access. Created in the constructor. */
	UPROPERTY()
	TObjectPtr<UAFVehicleCompatibilityLayer> CompatibilityLayer;

	/**
	 * The opaque backend movement component. Held only for lifetime.
	 * Never cast; see D-031.
	 */
	UPROPERTY()
	TObjectPtr<UActorComponent> BackendMovement;

	/** Where ResetVehicle puts the car. Seeded from the spawn transform. */
	FTransform LastGoodTransform;

	/** How many times ResetVehicle has run. */
	int32 ResetCount = 0;

	/** Seconds since the last LastGoodTransform update, used to rate-limit it. */
	double SecondsSinceGoodTransform = 0.0;
};
