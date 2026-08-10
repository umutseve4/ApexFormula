// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

#include "AFViewModelBase.h"
#include "AFLog.h"
#include "AFTelemetryBus.h"

void UAFViewModelBase::BindToTelemetryBus(UAFTelemetryBus* InBus)
{
	if (UAFTelemetryBus* Previous = TelemetryBus.Get())
	{
		if (Previous == InBus)
		{
			// Already bound to this bus. Rebinding would duplicate every
			// subscription and double-count each sample.
			return;
		}

		OnBusUnbound(Previous);
	}

	TelemetryBus = InBus;

	if (InBus)
	{
		OnBusBound(InBus);
		UE_LOG(LogAFUI, Verbose, TEXT("%s bound to a telemetry bus."), *GetName());
	}
	else
	{
		UE_LOG(LogAFUI, Verbose, TEXT("%s unbound from its telemetry bus."), *GetName());
	}
}

bool UAFViewModelBase::IsBound() const
{
	return TelemetryBus.IsValid();
}

void UAFViewModelBase::ResetViewModel()
{
	// The base view model publishes nothing of its own; subclasses override
	// this and call Super to keep the change notification consistent.
	NotifyChanged();
}

void UAFViewModelBase::OnBusBound(UAFTelemetryBus* InBus)
{
	// Intentionally empty.
}

void UAFViewModelBase::OnBusUnbound(UAFTelemetryBus* InBus)
{
	// Intentionally empty.
}

void UAFViewModelBase::NotifyChanged()
{
	OnViewModelChanged.Broadcast();
}
