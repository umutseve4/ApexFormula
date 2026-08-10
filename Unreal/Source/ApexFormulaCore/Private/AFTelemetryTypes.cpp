// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

#include "AFTelemetryTypes.h"

namespace AFTelemetryChannels
{
	const FName VehicleSpeedKph        = FName(TEXT("vehicle.speed_kph"));
	const FName VehicleThrottle        = FName(TEXT("vehicle.throttle"));
	const FName VehicleBrake           = FName(TEXT("vehicle.brake"));
	const FName VehicleSteer           = FName(TEXT("vehicle.steer"));
	const FName VehicleGear            = FName(TEXT("vehicle.gear"));
	const FName EnergyStateOfCharge    = FName(TEXT("energy.state_of_charge"));
	const FName FuelMassKg             = FName(TEXT("fuel.mass_kg"));
	const FName RaceLapTimeSeconds     = FName(TEXT("race.lap_time_s"));
	const FName RaceSectorTimeSeconds  = FName(TEXT("race.sector_time_s"));
	const FName RacePosition           = FName(TEXT("race.position"));

	TArray<FName> GetAllChannels()
	{
		return TArray<FName>{
			VehicleSpeedKph,
			VehicleThrottle,
			VehicleBrake,
			VehicleSteer,
			VehicleGear,
			EnergyStateOfCharge,
			FuelMassKg,
			RaceLapTimeSeconds,
			RaceSectorTimeSeconds,
			RacePosition
		};
	}
}
