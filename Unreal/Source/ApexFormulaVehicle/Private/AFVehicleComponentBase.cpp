// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

#include "AFVehicleComponentBase.h"
#include "AFLog.h"

UAFVehicleComponentBase::UAFVehicleComponentBase()
{
	// Milestone 1 has no per-tick vehicle behaviour. Subclasses that need a
	// tick enable it explicitly, so nothing ticks by accident.
	PrimaryComponentTick.bCanEverTick = false;
	PrimaryComponentTick.bStartWithTickEnabled = false;
}

void UAFVehicleComponentBase::ApplyConfiguration()
{
	if (SubsystemId.IsNone())
	{
		UE_LOG(LogAFVehicle, Warning,
			TEXT("%s: ApplyConfiguration called with SubsystemId unset. "
				 "Telemetry channels from this component will be unattributable."),
			*GetName());
	}

	bConfigured = true;

	UE_LOG(LogAFVehicle, Verbose,
		TEXT("Vehicle subsystem '%s' configured."),
		*SubsystemId.ToString());
}

void UAFVehicleComponentBase::ResetSubsystem()
{
	bConfigured = false;

	UE_LOG(LogAFVehicle, Verbose,
		TEXT("Vehicle subsystem '%s' reset."),
		*SubsystemId.ToString());
}

void UAFVehicleComponentBase::CollectTelemetry(double SessionTime, TArray<FAFTelemetrySample>& OutSamples) const
{
	// Contract: implementations append and never clear OutSamples.
	// The base class contributes no channels of its own.
	(void)SessionTime;
	(void)OutSamples;
}

TArray<FName> UAFVehicleComponentBase::GetProvidedTelemetryChannels() const
{
	return TArray<FName>();
}
