// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Pawn.h"
#include "AFTypes.h"
#include "AFRaceParticipantInterface.h"
#include "AFVehiclePawn.generated.h"

class USkeletalMeshComponent;
class UAFVehicleCompatibilityLayer;
class UAFVehicleDefinition;
class UAFVehicleComponentBase;

/**
 * AAFVehiclePawn - the single vehicle actor.
 *
 * Architecture reference: TECHNICAL_ARCHITECTURE.md sections 4 and 11.
 *
 * Deep pawn inheritance is prohibited. There is exactly one vehicle pawn
 * class; every behavioural difference comes from Data Assets and from
 * UAFVehicleComponentBase subclasses attached to it.
 *
 * It implements IAFRaceParticipant so the Race module can time it, position it
 * and classify it WITHOUT depending on ApexFormulaVehicle. That interface is
 * the entire reason the Race module compiles with no vehicle types in scope.
 *
 * Milestone 1 scope. No physics, no input binding, no movement. The pawn
 * exists so the architecture is expressible as code.
 *
 * Status: statically inspected. requires local compilation.
 * requires Unreal Editor verification (spawning and component layout).
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

	/** The vehicle this pawn was configured from. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Vehicle")
	TObjectPtr<UAFVehicleDefinition> VehicleDefinition;

	/**
	 * Applies VehicleDefinition and calls ApplyConfiguration on every attached
	 * UAFVehicleComponentBase, in a deterministic order.
	 * Returns false and logs when VehicleDefinition is missing.
	 */
	UFUNCTION(BlueprintCallable, Category = "ApexFormula|Vehicle")
	bool ApplyVehicleDefinition();

	/** Hands a driver input frame to the compatibility layer. */
	UFUNCTION(BlueprintCallable, Category = "ApexFormula|Vehicle")
	void SubmitInputFrame(const FAFVehicleInputFrame& InputFrame);

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
	virtual FText GetParticipantDisplayName() const override;
	virtual FVector GetParticipantLocation() const override;
	virtual FVector GetParticipantForward() const override;
	virtual double GetParticipantSpeedKph() const override;
	virtual bool IsParticipantActive() const override;
	//~ End IAFRaceParticipant interface

protected:
	virtual void BeginPlay() override;

private:
	/** Sole owner of engine vehicle API access. Created in the constructor. */
	UPROPERTY()
	TObjectPtr<UAFVehicleCompatibilityLayer> CompatibilityLayer;
};
