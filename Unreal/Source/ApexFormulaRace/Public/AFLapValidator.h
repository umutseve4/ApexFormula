// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

#pragma once

#include "CoreMinimal.h"
#include "UObject/Object.h"
#include "AFTypes.h"
#include "AFLapValidator.generated.h"

/**
 * Outcome of one attempted lap.
 */
USTRUCT(BlueprintType)
struct APEXFORMULARACE_API FAFLapResult
{
	GENERATED_BODY()

	/** Zero-based lap index within the session. */
	UPROPERTY(BlueprintReadOnly, Category = "ApexFormula|Timing")
	int32 LapIndex = 0;

	/** True only when every checkpoint was passed in order and nothing invalidated the lap. */
	UPROPERTY(BlueprintReadOnly, Category = "ApexFormula|Timing")
	bool bValid = false;

	/** Why the lap is not valid. NotInvalidated when bValid is true. */
	UPROPERTY(BlueprintReadOnly, Category = "ApexFormula|Timing")
	EAFLapInvalidationReason InvalidationReason = EAFLapInvalidationReason::NotInvalidated;

	/** Session time at the start of the lap, seconds. */
	UPROPERTY(BlueprintReadOnly, Category = "ApexFormula|Timing")
	double StartTime = 0.0;

	/** Session time at the end of the lap, seconds. */
	UPROPERTY(BlueprintReadOnly, Category = "ApexFormula|Timing")
	double EndTime = 0.0;

	/** EndTime minus StartTime, seconds. Zero for an abandoned lap. */
	UPROPERTY(BlueprintReadOnly, Category = "ApexFormula|Timing")
	double LapTimeSeconds = 0.0;
};

/**
 * UAFLapValidator - decides whether one lap counts.
 *
 * Architecture reference: TECHNICAL_ARCHITECTURE.md sections 9 and 11.
 *
 * Like UAFSectorTimer this class is PURE. It holds no world reference, never
 * ticks, and takes every input explicitly. It is driven entirely by:
 *   - an expected checkpoint order supplied by UAFTrackDefinition,
 *   - checkpoint pass notifications with a session time,
 *   - explicit invalidation notifications.
 *
 * The lap ends only when the timing line, index 0, is reached again after every
 * other checkpoint in the expected order has been passed exactly once.
 *
 * Deliberate design point: an out-of-order checkpoint does NOT abandon the lap.
 * It marks the lap invalid and keeps timing, because a driver who cuts a corner
 * still finishes the lap and still needs a recorded, clearly invalid result.
 *
 * Status: statically inspected. requires local compilation.
 */
UCLASS(BlueprintType)
class APEXFORMULARACE_API UAFLapValidator : public UObject
{
	GENERATED_BODY()

public:
	/**
	 * Sets the checkpoint order for the circuit. Index 0 must be the timing
	 * line. Clears all lap state.
	 * Returns false when the order has fewer than two entries or contains
	 * duplicates or unset names.
	 */
	UFUNCTION(BlueprintCallable, Category = "ApexFormula|Timing")
	bool Configure(const TArray<FName>& InExpectedCheckpointOrder);

	/** Starts a new lap at the timing line. Discards any lap in progress. */
	UFUNCTION(BlueprintCallable, Category = "ApexFormula|Timing")
	void BeginLap(int32 InLapIndex, double SessionTime);

	/**
	 * Reports that CheckpointId was passed at SessionTime.
	 * Returns true when the checkpoint was the expected next one.
	 * Returns false and marks the lap invalid with MissedCheckpoint when it
	 * was not, or when the checkpoint is unknown to this circuit.
	 */
	UFUNCTION(BlueprintCallable, Category = "ApexFormula|Timing")
	bool NotifyCheckpointPassed(FName CheckpointId, double SessionTime);

	/**
	 * Marks the current lap invalid. The first reason recorded wins, so the
	 * original cause is never overwritten by a later consequence.
	 */
	UFUNCTION(BlueprintCallable, Category = "ApexFormula|Timing")
	void InvalidateLap(EAFLapInvalidationReason Reason);

	/**
	 * Closes the lap at the timing line and returns the result.
	 * bOutHasResult is false when no lap was open.
	 * A lap that reaches the line without passing every checkpoint is returned
	 * with bValid false and reason MissedCheckpoint.
	 */
	UFUNCTION(BlueprintCallable, Category = "ApexFormula|Timing")
	FAFLapResult CompleteLap(double SessionTime, bool& bOutHasResult);

	/** True between BeginLap and CompleteLap. */
	UFUNCTION(BlueprintPure, Category = "ApexFormula|Timing")
	bool IsLapOpen() const { return bLapOpen; }

	/** Reason recorded so far for the current lap. */
	UFUNCTION(BlueprintPure, Category = "ApexFormula|Timing")
	EAFLapInvalidationReason GetCurrentInvalidationReason() const { return CurrentReason; }

	/** Number of checkpoints passed in order so far, excluding the timing line. */
	UFUNCTION(BlueprintPure, Category = "ApexFormula|Timing")
	int32 GetPassedCheckpointCount() const { return NextExpectedIndex - 1; }

	/** The checkpoint order this validator was configured with. */
	UFUNCTION(BlueprintPure, Category = "ApexFormula|Timing")
	const TArray<FName>& GetExpectedCheckpointOrder() const { return ExpectedCheckpointOrder; }

	/** Clears the current lap without changing the configured checkpoint order. */
	UFUNCTION(BlueprintCallable, Category = "ApexFormula|Timing")
	void ResetLap();

private:
	/** Circuit checkpoint order. Index 0 is the timing line. */
	TArray<FName> ExpectedCheckpointOrder;

	/** Fast membership test for unknown checkpoint detection. */
	TSet<FName> KnownCheckpoints;

	/** True between BeginLap and CompleteLap. */
	bool bLapOpen = false;

	/** Lap index supplied to BeginLap. */
	int32 CurrentLapIndex = 0;

	/** Session time at BeginLap. */
	double CurrentLapStartTime = 0.0;

	/**
	 * Index into ExpectedCheckpointOrder of the checkpoint expected next.
	 * Starts at 1 because index 0, the timing line, is consumed by BeginLap.
	 */
	int32 NextExpectedIndex = 1;

	/** First invalidation reason recorded for the current lap. */
	EAFLapInvalidationReason CurrentReason = EAFLapInvalidationReason::NotInvalidated;
};
