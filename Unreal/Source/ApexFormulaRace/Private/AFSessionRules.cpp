// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

#include "AFSessionRules.h"

TArray<FString> UAFSessionRules::ValidateSelf() const
{
	TArray<FString> Problems;

	if (DataVersion < 1)
	{
		Problems.Add(FString::Printf(TEXT("DataVersion must be >= 1, is %d"), DataVersion));
	}

	if (RulesId.IsNone())
	{
		Problems.Add(TEXT("RulesId must be set"));
	}
	else
	{
		const FString AsString = RulesId.ToString();

		if (AsString != AsString.ToLower())
		{
			Problems.Add(FString::Printf(TEXT("RulesId '%s' must be lower case"), *AsString));
		}
		if (AsString.Contains(TEXT(" ")))
		{
			Problems.Add(FString::Printf(TEXT("RulesId '%s' must not contain spaces"), *AsString));
		}
	}

	if (DisplayName.IsEmpty())
	{
		Problems.Add(TEXT("DisplayName must be set"));
	}

	// A session must be bounded by something, otherwise it never ends.
	if (!IsTimedSession() && RaceLapCount < 1)
	{
		Problems.Add(TEXT(
			"Session is unbounded: set RaceLapCount >= 1 or SessionDurationSeconds > 0"));
	}

	if (MaxParticipants < 1)
	{
		Problems.Add(FString::Printf(
			TEXT("MaxParticipants must be >= 1, is %d"), MaxParticipants));
	}

	if (TrackLimitWarningsBeforePenalty < 0)
	{
		Problems.Add(FString::Printf(
			TEXT("TrackLimitWarningsBeforePenalty must be >= 0, is %d"),
			TrackLimitWarningsBeforePenalty));
	}

	if (TrackLimitPenaltySeconds < 0.0)
	{
		Problems.Add(FString::Printf(
			TEXT("TrackLimitPenaltySeconds must be >= 0, is %f"), TrackLimitPenaltySeconds));
	}

	if (PitSpeedingPenaltySeconds < 0.0)
	{
		Problems.Add(FString::Printf(
			TEXT("PitSpeedingPenaltySeconds must be >= 0, is %f"), PitSpeedingPenaltySeconds));
	}

	if (ClassificationDistanceFraction < 0.0 || ClassificationDistanceFraction > 1.0)
	{
		Problems.Add(FString::Printf(
			TEXT("ClassificationDistanceFraction must be within 0..1, is %f"),
			ClassificationDistanceFraction));
	}

	// Time trial has no field to race against, so a mandatory stop is a
	// configuration mistake rather than a rule.
	if (SessionType == EAFSessionType::TimeTrial && bMandatoryPitStop)
	{
		Problems.Add(TEXT("bMandatoryPitStop is not meaningful for a TimeTrial session"));
	}

	return Problems;
}
