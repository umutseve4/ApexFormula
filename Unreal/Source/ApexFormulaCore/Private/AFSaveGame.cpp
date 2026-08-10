// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

#include "AFSaveGame.h"
#include "AFLog.h"

const FAFBestLapRecord* UAFSaveGame::FindBestLap(FName TrackId, FName VehicleId) const
{
	return BestLaps.FindByPredicate(
		[TrackId, VehicleId](const FAFBestLapRecord& Record)
		{
			return Record.TrackId == TrackId && Record.VehicleId == VehicleId;
		});
}

bool UAFSaveGame::SubmitLapTime(FName TrackId, FName VehicleId, double LapSeconds)
{
	if (TrackId.IsNone() || VehicleId.IsNone())
	{
		UE_LOG(LogAFCore, Warning,
			TEXT("SubmitLapTime rejected: TrackId or VehicleId is unset."));
		return false;
	}

	if (!(LapSeconds > 0.0))
	{
		// Covers zero, negatives and NaN.
		UE_LOG(LogAFCore, Warning,
			TEXT("SubmitLapTime rejected for track '%s': lap time %f is not positive."),
			*TrackId.ToString(), LapSeconds);
		return false;
	}

	for (FAFBestLapRecord& Record : BestLaps)
	{
		if (Record.TrackId == TrackId && Record.VehicleId == VehicleId)
		{
			const bool bNoTimeYet = !(Record.BestLapSeconds > 0.0);
			if (bNoTimeYet || LapSeconds < Record.BestLapSeconds)
			{
				UE_LOG(LogAFCore, Log,
					TEXT("New personal best on track '%s' with vehicle '%s': %f s (previous %f s)."),
					*TrackId.ToString(), *VehicleId.ToString(), LapSeconds, Record.BestLapSeconds);
				Record.BestLapSeconds = LapSeconds;
				return true;
			}
			return false;
		}
	}

	FAFBestLapRecord NewRecord;
	NewRecord.TrackId = TrackId;
	NewRecord.VehicleId = VehicleId;
	NewRecord.BestLapSeconds = LapSeconds;
	BestLaps.Add(MoveTemp(NewRecord));

	UE_LOG(LogAFCore, Log,
		TEXT("First recorded lap on track '%s' with vehicle '%s': %f s."),
		*TrackId.ToString(), *VehicleId.ToString(), LapSeconds);

	return true;
}
