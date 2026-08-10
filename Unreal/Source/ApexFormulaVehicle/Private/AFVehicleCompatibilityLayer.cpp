// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

#include "AFVehicleCompatibilityLayer.h"
#include "AFLog.h"

UAFVehicleCompatibilityLayer::UAFVehicleCompatibilityLayer()
{
	// Milestone 1 binds no backend on purpose. Vehicle physics is excluded
	// from this milestone, and claiming a working backend here would be a
	// false statement about untested code.
	BackendInfo.BackendId = FName(TEXT("none"));
	BackendInfo.bBackendAvailable = false;
	BackendInfo.StatusMessage = TEXT(
		"No vehicle backend bound. Milestone 1 provides the compatibility "
		"surface only; physics integration is scheduled for a later milestone.");
}

FAFVehicleBackendInfo UAFVehicleCompatibilityLayer::GetBackendInfo() const
{
	return BackendInfo;
}

bool UAFVehicleCompatibilityLayer::IsBackendAvailable() const
{
	return BackendInfo.bBackendAvailable;
}

bool UAFVehicleCompatibilityLayer::ApplyInputFrame(const FAFVehicleInputFrame& InputFrame)
{
	LastInputFrame = InputFrame;
	LastInputFrame.Sanitise();
	++AppliedFrameCount;

	if (!BackendInfo.bBackendAvailable)
	{
		// Verbose, not Warning: this is the expected state for Milestone 1 and
		// a warning per tick would drown the log.
		UE_LOG(LogAFVehicle, Verbose,
			TEXT("ApplyInputFrame received frame %d at t=%f with no backend bound."),
			AppliedFrameCount, LastInputFrame.SessionTime);
		return false;
	}

	// A future milestone forwards LastInputFrame to the engine backend here.
	// That call must stay inside this file.
	return true;
}

double UAFVehicleCompatibilityLayer::GetForwardSpeedKph() const
{
	if (!BackendInfo.bBackendAvailable)
	{
		return 0.0;
	}

	// A future milestone reads backend velocity here and converts with
	// UAFUnitsHelper::UnrealSpeedToKph. Returning 0 until then is honest.
	return 0.0;
}

int32 UAFVehicleCompatibilityLayer::GetCurrentGear() const
{
	if (!BackendInfo.bBackendAvailable)
	{
		return 0;
	}

	return 0;
}
