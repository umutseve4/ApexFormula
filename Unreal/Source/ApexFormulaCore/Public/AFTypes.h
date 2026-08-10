// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

#pragma once

#include "CoreMinimal.h"
#include "AFTypes.generated.h"

/**
 * Session kind. Drives which rules the session state machine applies.
 * Architecture reference: TECHNICAL_ARCHITECTURE.md section 2, Race module.
 */
UENUM(BlueprintType)
enum class EAFSessionType : uint8
{
	/** Free running. No classification, no penalties beyond track limits. */
	Practice    UMETA(DisplayName = "Practice"),

	/** Timed. Classification is by best single lap. */
	Qualifying  UMETA(DisplayName = "Qualifying"),

	/** Classification is by distance then time. Grid order applies. */
	Race        UMETA(DisplayName = "Race"),

	/** Single car, single lap, no opposition. Used by the test harness. */
	TimeTrial   UMETA(DisplayName = "Time Trial")
};

/**
 * The phase a session is currently in.
 * Deliberately explicit: silent state transitions are prohibited, so every
 * value here is something race control can name in a log line.
 */
UENUM(BlueprintType)
enum class EAFSessionPhase : uint8
{
	/** Created but not started. */
	NotStarted  UMETA(DisplayName = "Not Started"),

	/** Cars on the grid or in the pit lane, clock not running. */
	Forming     UMETA(DisplayName = "Forming"),

	/** Clock running, timing active. */
	Running     UMETA(DisplayName = "Running"),

	/** Clock stopped by race control, cars still on track. */
	Suspended   UMETA(DisplayName = "Suspended"),

	/** Leader has finished; others still completing their final lap. */
	Finishing   UMETA(DisplayName = "Finishing"),

	/** All classification final. */
	Complete    UMETA(DisplayName = "Complete")
};

/**
 * Why a lap was rejected. NotInvalidated means the lap counts.
 * Every rejection must be attributable to exactly one of these.
 */
UENUM(BlueprintType)
enum class EAFLapInvalidationReason : uint8
{
	NotInvalidated      UMETA(DisplayName = "Not Invalidated"),

	/** Left the track surface beyond the permitted limit. */
	TrackLimits         UMETA(DisplayName = "Track Limits"),

	/** Missed one or more checkpoints in sequence. */
	MissedCheckpoint    UMETA(DisplayName = "Missed Checkpoint"),

	/** Crossed a checkpoint in the wrong direction. */
	WrongDirection      UMETA(DisplayName = "Wrong Direction"),

	/** Contact judged to have gained an advantage. */
	Collision           UMETA(DisplayName = "Collision"),

	/** Vehicle was reset or teleported during the lap. */
	VehicleReset        UMETA(DisplayName = "Vehicle Reset"),

	/** Lap began or ended in the pit lane. */
	PitLane             UMETA(DisplayName = "Pit Lane")
};

/**
 * FAFVehicleInputFrame - one tick of driver intent.
 *
 * Architecture reference: TECHNICAL_ARCHITECTURE.md sections 4 and 11.
 *
 * This is the ONLY thing a controller hands to a vehicle. It is a plain value
 * type on purpose: a human controller, an AI controller and a replay playback
 * head all produce the same struct, so the vehicle cannot tell them apart and
 * deterministic replay stays possible.
 *
 * All axes are normalised and unitless. No centimetres, no radians, no
 * engine types. See AFUnits.h for the unit contract.
 */
USTRUCT(BlueprintType)
struct APEXFORMULACORE_API FAFVehicleInputFrame
{
	GENERATED_BODY()

	/** Throttle demand, 0..1. */
	UPROPERTY(BlueprintReadWrite, Category = "ApexFormula|Input")
	float Throttle = 0.0f;

	/** Brake demand, 0..1. */
	UPROPERTY(BlueprintReadWrite, Category = "ApexFormula|Input")
	float Brake = 0.0f;

	/** Steering demand, -1..1. Positive is right. */
	UPROPERTY(BlueprintReadWrite, Category = "ApexFormula|Input")
	float Steer = 0.0f;

	/** Clutch demand, 0..1. 0 is fully engaged. */
	UPROPERTY(BlueprintReadWrite, Category = "ApexFormula|Input")
	float Clutch = 0.0f;

	/** True on the tick the driver requested the next gear up. */
	UPROPERTY(BlueprintReadWrite, Category = "ApexFormula|Input")
	bool bShiftUp = false;

	/** True on the tick the driver requested the next gear down. */
	UPROPERTY(BlueprintReadWrite, Category = "ApexFormula|Input")
	bool bShiftDown = false;

	/** True while the driver is requesting stored-energy deployment. */
	UPROPERTY(BlueprintReadWrite, Category = "ApexFormula|Input")
	bool bDeployEnergy = false;

	/** True while the driver is requesting the drag-reduction device. */
	UPROPERTY(BlueprintReadWrite, Category = "ApexFormula|Input")
	bool bRequestDragReduction = false;

	/**
	 * Session time this frame was sampled at, seconds.
	 * Recorded so a replay can reproduce input at the correct instant rather
	 * than at whatever rate the replaying machine happens to tick.
	 */
	UPROPERTY(BlueprintReadWrite, Category = "ApexFormula|Input")
	double SessionTime = 0.0;

	FAFVehicleInputFrame() = default;

	/** Clamps every axis into its declared range. Call after any deserialise. */
	void Sanitise()
	{
		Throttle = FMath::Clamp(Throttle, 0.0f, 1.0f);
		Brake    = FMath::Clamp(Brake,    0.0f, 1.0f);
		Clutch   = FMath::Clamp(Clutch,   0.0f, 1.0f);
		Steer    = FMath::Clamp(Steer,   -1.0f, 1.0f);
	}

	/** True when no axis is applied and no button is held. */
	bool IsNeutral() const
	{
		return FMath::IsNearlyZero(Throttle)
			&& FMath::IsNearlyZero(Brake)
			&& FMath::IsNearlyZero(Steer)
			&& FMath::IsNearlyZero(Clutch)
			&& !bShiftUp
			&& !bShiftDown
			&& !bDeployEnergy
			&& !bRequestDragReduction;
	}
};
