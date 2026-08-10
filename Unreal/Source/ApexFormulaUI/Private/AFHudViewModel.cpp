// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

#include "AFHudViewModel.h"
#include "AFLog.h"
#include "AFTelemetryBus.h"
#include "AFTelemetryTypes.h"
#include "AFUnits.h"

TArray<FName> UAFHudViewModel::GetConsumedChannels()
{
	return TArray<FName>{
		AFTelemetryChannels::VehicleSpeedKph,
		AFTelemetryChannels::VehicleThrottle,
		AFTelemetryChannels::VehicleBrake,
		AFTelemetryChannels::VehicleGear,
		AFTelemetryChannels::EnergyStateOfCharge,
		AFTelemetryChannels::FuelMassKg,
		AFTelemetryChannels::RaceLapTimeSeconds,
		AFTelemetryChannels::RacePosition
	};
}

bool UAFHudViewModel::ApplySample(const FAFTelemetrySample& Sample)
{
	bool bHandled = true;

	if (Sample.Channel == AFTelemetryChannels::VehicleSpeedKph)
	{
		SpeedKph = static_cast<float>(Sample.Value);
	}
	else if (Sample.Channel == AFTelemetryChannels::VehicleThrottle)
	{
		Throttle = FMath::Clamp(static_cast<float>(Sample.Value), 0.0f, 1.0f);
	}
	else if (Sample.Channel == AFTelemetryChannels::VehicleBrake)
	{
		Brake = FMath::Clamp(static_cast<float>(Sample.Value), 0.0f, 1.0f);
	}
	else if (Sample.Channel == AFTelemetryChannels::VehicleGear)
	{
		Gear = FMath::RoundToInt(Sample.Value);
	}
	else if (Sample.Channel == AFTelemetryChannels::EnergyStateOfCharge)
	{
		StateOfCharge = FMath::Clamp(static_cast<float>(Sample.Value), 0.0f, 1.0f);
	}
	else if (Sample.Channel == AFTelemetryChannels::FuelMassKg)
	{
		FuelMassKg = FMath::Max(0.0f, static_cast<float>(Sample.Value));
	}
	else if (Sample.Channel == AFTelemetryChannels::RaceLapTimeSeconds)
	{
		LastLapTimeSeconds = FMath::Max(0.0f, static_cast<float>(Sample.Value));
	}
	else if (Sample.Channel == AFTelemetryChannels::RacePosition)
	{
		Position = FMath::Max(0, FMath::RoundToInt(Sample.Value));
	}
	else
	{
		bHandled = false;
	}

	if (bHandled)
	{
		LastUpdateTimeSeconds = static_cast<float>(Sample.SessionTime);
		NotifyChanged();
	}

	return bHandled;
}

FString UAFHudViewModel::GetFormattedLastLapTime() const
{
	return UAFUnitsHelper::FormatLapTime(LastLapTimeSeconds);
}

void UAFHudViewModel::ResetViewModel()
{
	SpeedKph = 0.0f;
	Gear = 0;
	Throttle = 0.0f;
	Brake = 0.0f;
	StateOfCharge = 0.0f;
	FuelMassKg = 0.0f;
	LastLapTimeSeconds = 0.0f;
	Position = 0;
	LastUpdateTimeSeconds = 0.0f;

	Super::ResetViewModel();
}

void UAFHudViewModel::OnBusBound(UAFTelemetryBus* InBus)
{
	if (!InBus)
	{
		return;
	}

	// One all-channel subscription is cheaper than eight per-channel ones and
	// keeps a single handle to release, which removes a whole class of leak.
	SampleHandle = InBus->SubscribeToAll(
		FAFOnTelemetrySample::FDelegate::CreateWeakLambda(this,
			[this](const FAFTelemetrySample& Sample)
			{
				ApplySample(Sample);
			}));
}

void UAFHudViewModel::OnBusUnbound(UAFTelemetryBus* InBus)
{
	if (InBus && SampleHandle.IsValid())
	{
		InBus->UnsubscribeFromAll(SampleHandle);
	}

	SampleHandle.Reset();
}
