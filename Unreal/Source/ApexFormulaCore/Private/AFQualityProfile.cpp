// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

#include "AFQualityProfile.h"

UAFQualityProfile::UAFQualityProfile()
{
	// Defaults describe the "Balanced" profile. Concrete assets override.
	DisplayName = NSLOCTEXT("ApexFormula", "QualityProfileBalanced", "Balanced");
	ProfileId = FName(TEXT("balanced"));
}

TArray<FString> UAFQualityProfile::ValidateSelf() const
{
	TArray<FString> Problems;

	if (DataVersion < 1)
	{
		Problems.Add(FString::Printf(TEXT("DataVersion must be >= 1, is %d"), DataVersion));
	}

	if (ProfileId.IsNone())
	{
		Problems.Add(TEXT("ProfileId must be set"));
	}
	else
	{
		const FString AsString = ProfileId.ToString();

		if (AsString != AsString.ToLower())
		{
			Problems.Add(FString::Printf(
				TEXT("ProfileId '%s' must be lower case"), *AsString));
		}
		if (AsString.Contains(TEXT(" ")))
		{
			Problems.Add(FString::Printf(
				TEXT("ProfileId '%s' must not contain spaces"), *AsString));
		}
	}

	if (DisplayName.IsEmpty())
	{
		Problems.Add(TEXT("DisplayName must be set"));
	}

	if (MaxFullDetailVehicles < 0)
	{
		Problems.Add(FString::Printf(
			TEXT("MaxFullDetailVehicles must be >= 0, is %d"), MaxFullDetailVehicles));
	}

	if (VehicleCullDistanceM <= 0.0)
	{
		Problems.Add(FString::Printf(
			TEXT("VehicleCullDistanceM must be > 0, is %f"), VehicleCullDistanceM));
	}

	if (TelemetrySampleRateHz <= 0.0)
	{
		Problems.Add(FString::Printf(
			TEXT("TelemetrySampleRateHz must be > 0, is %f"), TelemetrySampleRateHz));
	}

	if (ScreenPercentage < 25 || ScreenPercentage > 200)
	{
		Problems.Add(FString::Printf(
			TEXT("ScreenPercentage must be within 25..200, is %d"), ScreenPercentage));
	}

	return Problems;
}
