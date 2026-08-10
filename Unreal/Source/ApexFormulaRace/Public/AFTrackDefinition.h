// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

#pragma once

#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "AFTrackDefinition.generated.h"

/**
 * One timing sector of a circuit.
 */
USTRUCT(BlueprintType)
struct APEXFORMULARACE_API FAFSectorDefinition
{
	GENERATED_BODY()

	/** Zero-based sector index. Sector 0 starts at the timing line. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Track")
	int32 SectorIndex = 0;

	/** Player-facing sector label. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Track")
	FText DisplayName;

	/**
	 * Index into UAFTrackDefinition::CheckpointOrder of the checkpoint that
	 * CLOSES this sector. The final sector closes at the timing line.
	 */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Track")
	int32 ClosingCheckpointIndex = 0;
};

/**
 * UAFTrackDefinition - describes one original circuit.
 *
 * Architecture reference: TECHNICAL_ARCHITECTURE.md section 5.
 *
 * Every circuit in ApexFormula is an original fictional layout. No real
 * circuit may be reproduced, traced or named. All distances below are
 * ApexFormula design values, not official measurements of any real venue.
 *
 * Status: statically inspected. requires local compilation.
 * requires Unreal Editor verification (checkpoint placement).
 */
UCLASS(BlueprintType)
class APEXFORMULARACE_API UAFTrackDefinition : public UPrimaryDataAsset
{
	GENERATED_BODY()

public:
	/** Schema version for this asset type. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Meta")
	int32 DataVersion = 1;

	/** Stable internal id, lower case, no spaces. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Meta")
	FName TrackId = NAME_None;

	/** Player-facing circuit name. Original fictional naming only. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Meta")
	FText DisplayName;

	/** Fictional country or region label. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Meta")
	FText RegionName;

	/** Lap distance in metres. ApexFormula design value. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Layout", meta = (ClampMin = "1.0"))
	double LapLengthM = 5200.0;

	/** Number of racing grid slots this circuit supports. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Layout", meta = (ClampMin = "1"))
	int32 GridSlotCount = 20;

	/**
	 * Ordered checkpoint ids forming exactly one lap.
	 * Index 0 is the timing line. A lap is valid only when every id in this
	 * array was passed, in this order, exactly once.
	 */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Layout")
	TArray<FName> CheckpointOrder;

	/** Timing sectors, in ascending SectorIndex order. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Layout")
	TArray<FAFSectorDefinition> Sectors;

	/** True when this circuit has an authored pit lane. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|PitLane")
	bool bHasPitLane = true;

	/** Pit lane speed limit, kilometres per hour. ApexFormula design value. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|PitLane", meta = (ClampMin = "1.0"))
	double PitLaneSpeedLimitKph = 80.0;

	/** Number of checkpoints in one lap. */
	UFUNCTION(BlueprintPure, Category = "ApexFormula|Layout")
	int32 GetCheckpointCount() const { return CheckpointOrder.Num(); }

	/** Returns a list of human-readable problems. Empty means valid. */
	UFUNCTION(BlueprintCallable, Category = "ApexFormula|Validation")
	TArray<FString> ValidateSelf() const;
};
