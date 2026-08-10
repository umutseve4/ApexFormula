// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

#include "AFDeveloperSettings.h"

UAFDeveloperSettings::UAFDeveloperSettings()
{
	// Defaults mirror the repository layout produced by Milestone 0B.
	// All project relative. Absolute paths are a validator failure.
	PipelineExportDirectory = TEXT("BlenderPipeline/exports");
	PipelineReportDirectory = TEXT("BlenderPipeline/reports");
	VehicleContentRoot      = TEXT("/Game/ApexFormula/Vehicles");
}

const UAFDeveloperSettings* UAFDeveloperSettings::Get()
{
	return GetDefault<UAFDeveloperSettings>();
}

FName UAFDeveloperSettings::GetCategoryName() const
{
	return FName(TEXT("Game"));
}

TArray<FString> UAFDeveloperSettings::ValidateSelf() const
{
	TArray<FString> Problems;

	// Helper lambda: reject anything that looks like a machine-specific path.
	auto CheckRelative = [&Problems](const FString& Value, const TCHAR* FieldName)
	{
		if (Value.IsEmpty())
		{
			Problems.Add(FString::Printf(TEXT("%s must not be empty"), FieldName));
			return;
		}

		// Windows drive letter, e.g. C:/
		if (Value.Len() >= 2 && Value[1] == TEXT(':'))
		{
			Problems.Add(FString::Printf(
				TEXT("%s ('%s') looks like an absolute Windows path"), FieldName, *Value));
		}

		// UNC share.
		if (Value.StartsWith(TEXT("\\\\")))
		{
			Problems.Add(FString::Printf(
				TEXT("%s ('%s') looks like a UNC network path"), FieldName, *Value));
		}
	};

	CheckRelative(PipelineExportDirectory, TEXT("PipelineExportDirectory"));
	CheckRelative(PipelineReportDirectory, TEXT("PipelineReportDirectory"));

	if (!VehicleContentRoot.StartsWith(TEXT("/Game/")))
	{
		Problems.Add(FString::Printf(
			TEXT("VehicleContentRoot ('%s') must begin with /Game/"), *VehicleContentRoot));
	}

	if (FallbackTelemetrySampleRateHz <= 0.0)
	{
		Problems.Add(FString::Printf(
			TEXT("FallbackTelemetrySampleRateHz must be > 0, is %f"),
			FallbackTelemetrySampleRateHz));
	}

	if (bTelemetryWriteToDisk && !bTelemetryEnabled)
	{
		Problems.Add(TEXT("bTelemetryWriteToDisk is true but bTelemetryEnabled is false; nothing would be written"));
	}

	return Problems;
}
