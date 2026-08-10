// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

#include "AFTrackDefinition.h"

TArray<FString> UAFTrackDefinition::ValidateSelf() const
{
	TArray<FString> Problems;

	if (DataVersion < 1)
	{
		Problems.Add(FString::Printf(TEXT("DataVersion must be >= 1, is %d"), DataVersion));
	}

	if (TrackId.IsNone())
	{
		Problems.Add(TEXT("TrackId must be set"));
	}
	else
	{
		const FString AsString = TrackId.ToString();

		if (AsString != AsString.ToLower())
		{
			Problems.Add(FString::Printf(TEXT("TrackId '%s' must be lower case"), *AsString));
		}
		if (AsString.Contains(TEXT(" ")))
		{
			Problems.Add(FString::Printf(TEXT("TrackId '%s' must not contain spaces"), *AsString));
		}
	}

	if (DisplayName.IsEmpty())
	{
		Problems.Add(TEXT("DisplayName must be set"));
	}

	if (LapLengthM <= 0.0)
	{
		Problems.Add(FString::Printf(TEXT("LapLengthM must be > 0, is %f"), LapLengthM));
	}

	if (GridSlotCount < 1)
	{
		Problems.Add(FString::Printf(TEXT("GridSlotCount must be >= 1, is %d"), GridSlotCount));
	}

	// A lap needs at least the timing line plus one intermediate checkpoint,
	// otherwise cutting the entire circuit would still register a valid lap.
	if (CheckpointOrder.Num() < 2)
	{
		Problems.Add(FString::Printf(
			TEXT("CheckpointOrder must contain at least 2 entries, has %d"),
			CheckpointOrder.Num()));
	}

	TSet<FName> SeenCheckpoints;
	for (int32 Index = 0; Index < CheckpointOrder.Num(); ++Index)
	{
		const FName CheckpointId = CheckpointOrder[Index];

		if (CheckpointId.IsNone())
		{
			Problems.Add(FString::Printf(
				TEXT("CheckpointOrder[%d] is unset"), Index));
			continue;
		}

		bool bAlreadySeen = false;
		SeenCheckpoints.Add(CheckpointId, &bAlreadySeen);
		if (bAlreadySeen)
		{
			Problems.Add(FString::Printf(
				TEXT("CheckpointOrder[%d] duplicates checkpoint '%s'"),
				Index, *CheckpointId.ToString()));
		}
	}

	if (Sectors.Num() < 1)
	{
		Problems.Add(TEXT("At least one sector must be defined"));
	}

	TSet<int32> SeenSectorIndices;
	for (int32 Index = 0; Index < Sectors.Num(); ++Index)
	{
		const FAFSectorDefinition& Sector = Sectors[Index];

		if (Sector.SectorIndex != Index)
		{
			Problems.Add(FString::Printf(
				TEXT("Sectors[%d] has SectorIndex %d; sectors must be stored in ascending order starting at 0"),
				Index, Sector.SectorIndex));
		}

		bool bAlreadySeen = false;
		SeenSectorIndices.Add(Sector.SectorIndex, &bAlreadySeen);
		if (bAlreadySeen)
		{
			Problems.Add(FString::Printf(
				TEXT("Sector index %d is used more than once"), Sector.SectorIndex));
		}

		if (!CheckpointOrder.IsValidIndex(Sector.ClosingCheckpointIndex))
		{
			Problems.Add(FString::Printf(
				TEXT("Sectors[%d].ClosingCheckpointIndex %d is outside CheckpointOrder (0..%d)"),
				Index, Sector.ClosingCheckpointIndex, CheckpointOrder.Num() - 1));
		}
	}

	// The last sector must close the lap at the timing line, index 0.
	if (Sectors.Num() > 0 && CheckpointOrder.Num() > 0)
	{
		const FAFSectorDefinition& FinalSector = Sectors.Last();
		if (FinalSector.ClosingCheckpointIndex != 0)
		{
			Problems.Add(FString::Printf(
				TEXT("The final sector must close at the timing line (checkpoint index 0), closes at %d"),
				FinalSector.ClosingCheckpointIndex));
		}
	}

	if (bHasPitLane && PitLaneSpeedLimitKph <= 0.0)
	{
		Problems.Add(FString::Printf(
			TEXT("PitLaneSpeedLimitKph must be > 0 when bHasPitLane is true, is %f"),
			PitLaneSpeedLimitKph));
	}

	return Problems;
}
