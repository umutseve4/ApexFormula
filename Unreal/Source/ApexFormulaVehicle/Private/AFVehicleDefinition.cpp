// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

#include "AFVehicleDefinition.h"

TArray<FString> UAFVehicleDefinition::ValidateSelf() const
{
	TArray<FString> Problems;

	if (DataVersion < 1)
	{
		Problems.Add(FString::Printf(TEXT("DataVersion must be >= 1, is %d"), DataVersion));
	}

	if (VehicleId.IsNone())
	{
		Problems.Add(TEXT("VehicleId must be set"));
	}
	else
	{
		const FString AsString = VehicleId.ToString();

		if (AsString != AsString.ToLower())
		{
			Problems.Add(FString::Printf(TEXT("VehicleId '%s' must be lower case"), *AsString));
		}
		if (AsString.Contains(TEXT(" ")))
		{
			Problems.Add(FString::Printf(TEXT("VehicleId '%s' must not contain spaces"), *AsString));
		}
	}

	if (DisplayName.IsEmpty())
	{
		Problems.Add(TEXT("DisplayName must be set"));
	}

	if (ConstructorName.IsEmpty())
	{
		Problems.Add(TEXT("ConstructorName must be set"));
	}

	if (DryMassKg <= 0.0)
	{
		Problems.Add(FString::Printf(TEXT("DryMassKg must be > 0, is %f"), DryMassKg));
	}

	if (WheelbaseM <= 0.0)
	{
		Problems.Add(FString::Printf(TEXT("WheelbaseM must be > 0, is %f"), WheelbaseM));
	}

	if (FrontTrackM <= 0.0)
	{
		Problems.Add(FString::Printf(TEXT("FrontTrackM must be > 0, is %f"), FrontTrackM));
	}

	if (RearTrackM <= 0.0)
	{
		Problems.Add(FString::Printf(TEXT("RearTrackM must be > 0, is %f"), RearTrackM));
	}

	// A wheelbase longer than the whole car is geometrically impossible and is
	// the most likely consequence of mixing metres with centimetres.
	if (OverallLengthM > 0.0 && WheelbaseM >= OverallLengthM)
	{
		Problems.Add(FString::Printf(
			TEXT("WheelbaseM (%f) must be less than OverallLengthM (%f); check units"),
			WheelbaseM, OverallLengthM));
	}

	if (CentreOfMassBiasRear < 0.0 || CentreOfMassBiasRear > 1.0)
	{
		Problems.Add(FString::Printf(
			TEXT("CentreOfMassBiasRear must be within 0..1, is %f"), CentreOfMassBiasRear));
	}

	if (CentreOfMassHeightM < 0.0)
	{
		Problems.Add(FString::Printf(
			TEXT("CentreOfMassHeightM must be >= 0, is %f"), CentreOfMassHeightM));
	}

	if (BoneNameMap.IsNull())
	{
		Problems.Add(TEXT("BoneNameMap must be assigned so the skeleton can be validated"));
	}

	return Problems;
}
