// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

#pragma once

#include "CoreMinimal.h"
#include "UObject/Object.h"
#include "AFSectorTimer.generated.h"

/**
 * Timing result for one completed sector.
 */
USTRUCT(BlueprintType)
struct APEXFORMULARACE_API FAFSectorSplit
{
	GENERATED_BODY()

	/** Zero-based sector index. */
	UPROPERTY(BlueprintReadOnly, Category = "ApexFormula|Timing")
	int32 SectorIndex = 0;

	/** Session time at which this sector opened, seconds. */
	UPROPERTY(BlueprintReadOnly, Category = "ApexFormula|Timing")
	double EnterTime = 0.0;

	/** Session time at which this sector closed, seconds. */
	UPROPERTY(BlueprintReadOnly, Category = "ApexFormula|Timing")
	double ExitTime = 0.0;

	/** ExitTime minus EnterTime, seconds. */
	UPROPERTY(BlueprintReadOnly, Category = "ApexFormula|Timing")
	double DurationSeconds = 0.0;
};

/**
 * UAFSectorTimer - accumulates sector splits for one participant.
 *
 * Architecture reference: TECHNICAL_ARCHITECTURE.md sections 9 and 11.
 *
 * This class is deliberately PURE: it has no tick, no world, no actor and no
 * frame dependency. Every input arrives as an explicit session time, so the
 * same sequence of calls always produces the same splits. That is what makes
 * timing testable without a car, a track or a frame, which is the stated
 * testing principle for this project.
 *
 * Times are session-relative seconds as doubles. Float would lose enough
 * precision over a long session to move a lap time by milliseconds.
 *
 * Status: statically inspected. requires local compilation.
 */
UCLASS(BlueprintType)
class APEXFORMULARACE_API UAFSectorTimer : public UObject
{
	GENERATED_BODY()

public:
	/**
	 * Configures the timer for a circuit with SectorCount sectors.
	 * Clears all accumulated state. Returns false when SectorCount < 1.
	 */
	UFUNCTION(BlueprintCallable, Category = "ApexFormula|Timing")
	bool Configure(int32 InSectorCount);

	/**
	 * Begins timing at the timing line. Discards any partially timed lap.
	 * Must be called before the first RecordSectorBoundary of a lap.
	 */
	UFUNCTION(BlueprintCallable, Category = "ApexFormula|Timing")
	void BeginLap(double SessionTime);

	/**
	 * Closes the currently open sector at SessionTime and opens the next.
	 * Returns false, records nothing and logs when:
	 *  - no lap is open,
	 *  - SessionTime is not strictly greater than the sector's enter time,
	 *  - every sector of the lap has already been closed.
	 */
	UFUNCTION(BlueprintCallable, Category = "ApexFormula|Timing")
	bool RecordSectorBoundary(double SessionTime);

	/** True when BeginLap has been called and the lap is not yet complete. */
	UFUNCTION(BlueprintPure, Category = "ApexFormula|Timing")
	bool IsLapOpen() const { return bLapOpen; }

	/** True when every sector of the current lap has been closed. */
	UFUNCTION(BlueprintPure, Category = "ApexFormula|Timing")
	bool IsLapComplete() const;

	/** Splits closed so far on the current lap, in sector order. */
	UFUNCTION(BlueprintPure, Category = "ApexFormula|Timing")
	const TArray<FAFSectorSplit>& GetSplits() const { return Splits; }

	/**
	 * Total of every closed sector on the current lap, seconds.
	 * Returns 0 when no sector has been closed.
	 */
	UFUNCTION(BlueprintPure, Category = "ApexFormula|Timing")
	double GetLapTimeSeconds() const;

	/** Number of sectors this timer was configured for. */
	UFUNCTION(BlueprintPure, Category = "ApexFormula|Timing")
	int32 GetSectorCount() const { return SectorCount; }

	/** Clears the current lap without changing the configured sector count. */
	UFUNCTION(BlueprintCallable, Category = "ApexFormula|Timing")
	void ResetLap();

private:
	/** How many sectors form one lap. Set by Configure. */
	int32 SectorCount = 0;

	/** True between BeginLap and the final sector boundary. */
	bool bLapOpen = false;

	/** Session time at which the currently open sector began. */
	double CurrentSectorEnterTime = 0.0;

	/** Closed splits for the current lap. */
	TArray<FAFSectorSplit> Splits;
};
