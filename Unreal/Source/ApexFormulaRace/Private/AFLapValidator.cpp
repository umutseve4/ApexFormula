// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

#include "AFLapValidator.h"
#include "AFLog.h"

bool UAFLapValidator::Configure(const TArray<FName>& InExpectedCheckpointOrder)
{
	if (InExpectedCheckpointOrder.Num() < 2)
	{
		UE_LOG(LogAFRace, Warning,
			TEXT("UAFLapValidator::Configure rejected an order with %d entries; at least 2 are required."),
			InExpectedCheckpointOrder.Num());
		return false;
	}

	TSet<FName> Unique;
	for (int32 Index = 0; Index < InExpectedCheckpointOrder.Num(); ++Index)
	{
		const FName CheckpointId = InExpectedCheckpointOrder[Index];

		if (CheckpointId.IsNone())
		{
			UE_LOG(LogAFRace, Warning,
				TEXT("UAFLapValidator::Configure rejected the order; entry %d is unset."), Index);
			return false;
		}

		bool bAlreadySeen = false;
		Unique.Add(CheckpointId, &bAlreadySeen);
		if (bAlreadySeen)
		{
			UE_LOG(LogAFRace, Warning,
				TEXT("UAFLapValidator::Configure rejected the order; checkpoint '%s' appears more than once."),
				*CheckpointId.ToString());
			return false;
		}
	}

	ExpectedCheckpointOrder = InExpectedCheckpointOrder;
	KnownCheckpoints = MoveTemp(Unique);
	ResetLap();
	return true;
}

void UAFLapValidator::BeginLap(const int32 InLapIndex, const double SessionTime)
{
	if (ExpectedCheckpointOrder.Num() < 2)
	{
		UE_LOG(LogAFRace, Warning,
			TEXT("UAFLapValidator::BeginLap called before Configure; ignoring."));
		return;
	}

	CurrentLapIndex = InLapIndex;
	CurrentLapStartTime = SessionTime;
	NextExpectedIndex = 1;
	CurrentReason = EAFLapInvalidationReason::NotInvalidated;
	bLapOpen = true;
}

bool UAFLapValidator::NotifyCheckpointPassed(const FName CheckpointId, const double SessionTime)
{
	if (!bLapOpen)
	{
		UE_LOG(LogAFRace, Verbose,
			TEXT("UAFLapValidator::NotifyCheckpointPassed('%s') with no lap open; ignoring."),
			*CheckpointId.ToString());
		return false;
	}

	if (!KnownCheckpoints.Contains(CheckpointId))
	{
		UE_LOG(LogAFRace, Warning,
			TEXT("Checkpoint '%s' is not part of the configured circuit; lap %d marked invalid."),
			*CheckpointId.ToString(), CurrentLapIndex);
		InvalidateLap(EAFLapInvalidationReason::MissedCheckpoint);
		return false;
	}

	// Every intermediate checkpoint has been passed; only the timing line
	// remains, and that arrives through CompleteLap rather than here.
	if (!ExpectedCheckpointOrder.IsValidIndex(NextExpectedIndex))
	{
		UE_LOG(LogAFRace, Warning,
			TEXT("Checkpoint '%s' passed after the lap's checkpoints were all consumed; lap %d marked invalid."),
			*CheckpointId.ToString(), CurrentLapIndex);
		InvalidateLap(EAFLapInvalidationReason::MissedCheckpoint);
		return false;
	}

	const FName Expected = ExpectedCheckpointOrder[NextExpectedIndex];
	if (CheckpointId != Expected)
	{
		UE_LOG(LogAFRace, Log,
			TEXT("Lap %d expected checkpoint '%s' but received '%s' at %f; lap marked invalid."),
			CurrentLapIndex, *Expected.ToString(), *CheckpointId.ToString(), SessionTime);
		InvalidateLap(EAFLapInvalidationReason::MissedCheckpoint);
		return false;
	}

	++NextExpectedIndex;
	return true;
}

void UAFLapValidator::InvalidateLap(const EAFLapInvalidationReason Reason)
{
	if (Reason == EAFLapInvalidationReason::NotInvalidated)
	{
		// Callers must not clear an invalidation through this entry point.
		return;
	}

	if (CurrentReason == EAFLapInvalidationReason::NotInvalidated)
	{
		// First cause wins. A spin caused by a track-limit excursion should be
		// reported as the excursion, not as the collision that followed it.
		CurrentReason = Reason;
	}
}

FAFLapResult UAFLapValidator::CompleteLap(const double SessionTime, bool& bOutHasResult)
{
	FAFLapResult Result;

	if (!bLapOpen)
	{
		bOutHasResult = false;
		return Result;
	}

	// The lap is only complete when every intermediate checkpoint was consumed.
	const bool bAllCheckpointsPassed = (NextExpectedIndex >= ExpectedCheckpointOrder.Num());
	if (!bAllCheckpointsPassed)
	{
		InvalidateLap(EAFLapInvalidationReason::MissedCheckpoint);
	}

	if (!(SessionTime > CurrentLapStartTime))
	{
		UE_LOG(LogAFRace, Warning,
			TEXT("UAFLapValidator::CompleteLap received time %f which is not after the lap start %f; lap %d marked invalid."),
			SessionTime, CurrentLapStartTime, CurrentLapIndex);
		InvalidateLap(EAFLapInvalidationReason::MissedCheckpoint);
	}

	Result.LapIndex = CurrentLapIndex;
	Result.StartTime = CurrentLapStartTime;
	Result.EndTime = SessionTime;
	Result.LapTimeSeconds = FMath::Max(0.0, SessionTime - CurrentLapStartTime);
	Result.InvalidationReason = CurrentReason;
	Result.bValid = (CurrentReason == EAFLapInvalidationReason::NotInvalidated)
		&& bAllCheckpointsPassed
		&& Result.LapTimeSeconds > 0.0;

	bLapOpen = false;
	bOutHasResult = true;
	return Result;
}

void UAFLapValidator::ResetLap()
{
	bLapOpen = false;
	CurrentLapIndex = 0;
	CurrentLapStartTime = 0.0;
	NextExpectedIndex = 1;
	CurrentReason = EAFLapInvalidationReason::NotInvalidated;
}
