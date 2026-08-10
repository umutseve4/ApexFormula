// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/SaveGame.h"
#include "AFSaveGame.generated.h"

/**
 * One stored best time for a track and session type combination.
 */
USTRUCT(BlueprintType)
struct APEXFORMULACORE_API FAFBestLapRecord
{
	GENERATED_BODY()

	/** Stable track id, matching UAFTrackDefinition::TrackId. */
	UPROPERTY(BlueprintReadWrite, Category = "ApexFormula|Save")
	FName TrackId = NAME_None;

	/** Stable vehicle id, matching UAFVehicleDefinition::VehicleId. */
	UPROPERTY(BlueprintReadWrite, Category = "ApexFormula|Save")
	FName VehicleId = NAME_None;

	/** Best valid lap, seconds. Negative means no time set. */
	UPROPERTY(BlueprintReadWrite, Category = "ApexFormula|Save")
	double BestLapSeconds = -1.0;

	/** Per-sector bests, seconds. May be shorter than the track sector count. */
	UPROPERTY(BlueprintReadWrite, Category = "ApexFormula|Save")
	TArray<double> BestSectorSeconds;
};

/**
 * UAFSaveGame - persistent player data.
 *
 * Architecture reference: TECHNICAL_ARCHITECTURE.md sections 2 and 11.
 *
 * Lives in Core because both Race (writes results) and UI (reads them) need
 * it, and neither may depend on the other.
 *
 * Versioning rule: SaveVersion is checked on load. An older save is migrated
 * or rejected explicitly. Silently reinterpreting old bytes is prohibited.
 *
 * Status: statically inspected. requires local compilation.
 */
UCLASS(BlueprintType)
class APEXFORMULACORE_API UAFSaveGame : public USaveGame
{
	GENERATED_BODY()

public:
	/** Current save schema version written by this build. */
	static constexpr int32 CurrentSaveVersion = 1;

	/** Schema version this instance was written with. */
	UPROPERTY(BlueprintReadWrite, Category = "ApexFormula|Save")
	int32 SaveVersion = CurrentSaveVersion;

	/** Slot name used by the default save path. */
	UPROPERTY(BlueprintReadWrite, Category = "ApexFormula|Save")
	FString SlotName;

	/** Player-chosen display name. Original fictional names only. */
	UPROPERTY(BlueprintReadWrite, Category = "ApexFormula|Save")
	FString PlayerDisplayName;

	/** Quality profile id the player last selected. */
	UPROPERTY(BlueprintReadWrite, Category = "ApexFormula|Save")
	FName SelectedQualityProfileId = NAME_None;

	/** Difficulty profile id the player last selected. */
	UPROPERTY(BlueprintReadWrite, Category = "ApexFormula|Save")
	FName SelectedDifficultyProfileId = NAME_None;

	/** All recorded personal bests. */
	UPROPERTY(BlueprintReadWrite, Category = "ApexFormula|Save")
	TArray<FAFBestLapRecord> BestLaps;

	/** Total distance driven across all sessions, metres. */
	UPROPERTY(BlueprintReadWrite, Category = "ApexFormula|Save")
	double TotalDistanceDrivenM = 0.0;

	/** Total valid laps completed across all sessions. */
	UPROPERTY(BlueprintReadWrite, Category = "ApexFormula|Save")
	int32 TotalValidLaps = 0;

	/** Finds an existing record, or nullptr. */
	const FAFBestLapRecord* FindBestLap(FName TrackId, FName VehicleId) const;

	/**
	 * Records a lap if it improves on the stored best, or if none exists.
	 * Returns true when the stored data changed.
	 * Non-positive lap times are rejected.
	 */
	UFUNCTION(BlueprintCallable, Category = "ApexFormula|Save")
	bool SubmitLapTime(FName TrackId, FName VehicleId, double LapSeconds);

	/** True when SaveVersion matches what this build writes. */
	UFUNCTION(BlueprintPure, Category = "ApexFormula|Save")
	bool IsCurrentVersion() const { return SaveVersion == CurrentSaveVersion; }
};
