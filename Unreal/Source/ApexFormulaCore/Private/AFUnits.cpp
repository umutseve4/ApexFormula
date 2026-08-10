// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

#include "AFUnits.h"

FString UAFUnitsHelper::FormatLapTime(double Seconds)
{
	const bool bNegative = Seconds < 0.0;
	double Abs = bNegative ? -Seconds : Seconds;

	const int32 Minutes = static_cast<int32>(Abs / 60.0);
	Abs -= static_cast<double>(Minutes) * 60.0;

	const int32 WholeSeconds = static_cast<int32>(Abs);
	// Round to milliseconds rather than truncate, so 12.9996 s reads 13.000.
	int32 Millis = static_cast<int32>(FMath::RoundToInt((Abs - static_cast<double>(WholeSeconds)) * 1000.0));

	int32 CarrySeconds = WholeSeconds;
	int32 CarryMinutes = Minutes;
	if (Millis >= 1000)
	{
		Millis -= 1000;
		++CarrySeconds;
	}
	if (CarrySeconds >= 60)
	{
		CarrySeconds -= 60;
		++CarryMinutes;
	}

	return FString::Printf(TEXT("%s%d:%02d.%03d"),
		bNegative ? TEXT("-") : TEXT(""),
		CarryMinutes, CarrySeconds, Millis);
}
