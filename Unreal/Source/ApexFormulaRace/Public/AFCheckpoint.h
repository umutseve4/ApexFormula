// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "AFCheckpoint.generated.h"

class UBoxComponent;

/**
 * Fired when a participant crosses a checkpoint.
 *
 * ParticipantId identifies the crosser through IAFRaceParticipant, never
 * through a vehicle type. That is what keeps ApexFormulaRace independent of
 * ApexFormulaVehicle, as required by TECHNICAL_ARCHITECTURE.md section 2.
 */
DECLARE_DYNAMIC_MULTICAST_DELEGATE_ThreeParams(
	FAFOnCheckpointPassed,
	FName, CheckpointId,
	int32, ParticipantId,
	double, SessionTime);

/**
 * AAFCheckpoint - a timing or ordering gate placed on a circuit.
 *
 * Architecture reference: TECHNICAL_ARCHITECTURE.md sections 3 and 11.
 *
 * The checkpoint knows nothing about vehicles. It resolves any overlapping
 * actor through the IAFRaceParticipant interface and rejects anything that
 * does not implement it. The trigger volume shape and placement are Blueprint
 * and level concerns; the identity, ordering and reporting rules live here.
 *
 * Status: statically inspected. requires local compilation.
 * requires Unreal Editor verification (volume placement and overlap response).
 */
UCLASS(BlueprintType, Blueprintable)
class APEXFORMULARACE_API AAFCheckpoint : public AActor
{
	GENERATED_BODY()

public:
	AAFCheckpoint();

	/** Stable id referenced by UAFTrackDefinition::CheckpointOrder. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Checkpoint")
	FName CheckpointId = NAME_None;

	/** True when this checkpoint is the start/finish timing line. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Checkpoint")
	bool bIsTimingLine = false;

	/**
	 * Index of this checkpoint within the circuit's checkpoint order.
	 * Authoring aid only; UAFTrackDefinition remains authoritative.
	 */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Checkpoint", meta = (ClampMin = "0"))
	int32 AuthoringOrderIndex = 0;

	/** Broadcast on every accepted crossing. */
	UPROPERTY(BlueprintAssignable, Category = "ApexFormula|Checkpoint")
	FAFOnCheckpointPassed OnCheckpointPassed;

	/** The trigger volume. Sized in the Blueprint or the level. */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "ApexFormula|Checkpoint")
	TObjectPtr<UBoxComponent> TriggerVolume;

	/**
	 * Reports a crossing by the given actor at SessionTime.
	 * Returns false and broadcasts nothing when the actor is null or does not
	 * implement IAFRaceParticipant.
	 */
	UFUNCTION(BlueprintCallable, Category = "ApexFormula|Checkpoint")
	bool ReportCrossing(AActor* CrossingActor, double SessionTime);

	/** Returns a list of human-readable problems. Empty means valid. */
	UFUNCTION(BlueprintCallable, Category = "ApexFormula|Validation")
	TArray<FString> ValidateSelf() const;

protected:
	virtual void BeginPlay() override;
};
