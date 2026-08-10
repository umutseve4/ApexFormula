// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

#pragma once

#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "AFTypes.h"
#include "AFSessionRules.generated.h"

/**
 * UAFSessionRules - the rule set governing one session.
 *
 * Architecture reference: TECHNICAL_ARCHITECTURE.md section 5.
 *
 * These are ApexFormula's own sporting rules, invented for this project. They
 * are not a reproduction of any real sporting regulation and must never be
 * presented as one.
 *
 * Status: statically inspected. requires local compilation.
 */
UCLASS(BlueprintType)
class APEXFORMULARACE_API UAFSessionRules : public UPrimaryDataAsset
{
	GENERATED_BODY()

public:
	/** Schema version for this asset type. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Meta")
	int32 DataVersion = 1;

	/** Stable internal id, lower case, no spaces. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Meta")
	FName RulesId = NAME_None;

	/** Player-facing rule set name. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Meta")
	FText DisplayName;

	/** Which kind of session these rules describe. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Session")
	EAFSessionType SessionType = EAFSessionType::Race;

	/**
	 * Race distance in laps. Ignored when SessionDurationSeconds is greater
	 * than zero, in which case the session is timed rather than lap-limited.
	 */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Session", meta = (ClampMin = "0"))
	int32 RaceLapCount = 20;

	/** Timed session length in seconds. Zero means lap-limited. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Session", meta = (ClampMin = "0.0"))
	double SessionDurationSeconds = 0.0;

	/** Maximum number of participants admitted to the session. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Session", meta = (ClampMin = "1"))
	int32 MaxParticipants = 20;

	//
	// Lap validation
	//

	/**
	 * Number of track-limit breaches tolerated before a penalty is issued.
	 * A breach also invalidates the lap it occurred on regardless of this value.
	 */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Rules", meta = (ClampMin = "0"))
	int32 TrackLimitWarningsBeforePenalty = 3;

	/** Time added per track-limit penalty, seconds. ApexFormula design value. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Rules", meta = (ClampMin = "0.0"))
	double TrackLimitPenaltySeconds = 5.0;

	/** When true, a lap on which the vehicle was reset can never be valid. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Rules")
	bool bVehicleResetInvalidatesLap = true;

	/** When true, driving the circuit backwards invalidates the lap. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Rules")
	bool bWrongDirectionInvalidatesLap = true;

	/** When true, a lap that includes a pit-lane transit is not a flying lap. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Rules")
	bool bPitLapInvalidatesFlyingLap = true;

	//
	// Pit rules
	//

	/** When true, at least one pit stop is required to be classified. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|PitLane")
	bool bMandatoryPitStop = false;

	/** Time added per pit-lane speeding penalty, seconds. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|PitLane", meta = (ClampMin = "0.0"))
	double PitSpeedingPenaltySeconds = 5.0;

	//
	// Classification
	//

	/**
	 * Fraction of the leader's distance a participant must cover to be
	 * classified as a finisher. 0.9 means ninety percent.
	 */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Classification", meta = (ClampMin = "0.0", ClampMax = "1.0"))
	double ClassificationDistanceFraction = 0.9;

	/** True when this rule set is timed rather than lap-limited. */
	UFUNCTION(BlueprintPure, Category = "ApexFormula|Session")
	bool IsTimedSession() const { return SessionDurationSeconds > 0.0; }

	/** Returns a list of human-readable problems. Empty means valid. */
	UFUNCTION(BlueprintCallable, Category = "ApexFormula|Validation")
	TArray<FString> ValidateSelf() const;
};
