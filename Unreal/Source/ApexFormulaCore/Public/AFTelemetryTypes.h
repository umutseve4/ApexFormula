// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

#pragma once

#include "CoreMinimal.h"
#include "AFTelemetryTypes.generated.h"

/**
 * Telemetry sample schema.
 *
 * Architecture reference: TECHNICAL_ARCHITECTURE.md section 10.
 *
 * Deliberately narrow. A sample is a named channel, a session time, an owning
 * participant and a value. Producers do not know who consumes them.
 *
 * Status: statically inspected. requires local compilation.
 */
USTRUCT(BlueprintType)
struct APEXFORMULACORE_API FAFTelemetrySample
{
	GENERATED_BODY()

	/**
	 * Channel name. Lower case, dot separated, in the form <domain>.<measure>.
	 * Use the named constants in AFTelemetryChannels rather than composing a
	 * name here; the literals live in AFTelemetryTypes.cpp and nowhere else, so
	 * that a rename cannot leave a stale copy behind. An earlier doc comment in
	 * this project spelled out a channel by hand and became a drift risk for
	 * exactly that reason.
	 */
	UPROPERTY(BlueprintReadWrite, Category = "ApexFormula|Telemetry")
	FName Channel = NAME_None;

	/** Seconds since the session clock started. Double, not float: laps are long. */
	UPROPERTY(BlueprintReadWrite, Category = "ApexFormula|Telemetry")
	double SessionTime = 0.0;

	/** Participant this sample belongs to. INDEX_NONE for session-wide samples. */
	UPROPERTY(BlueprintReadWrite, Category = "ApexFormula|Telemetry")
	int32 ParticipantId = INDEX_NONE;

	/** The scalar value. */
	UPROPERTY(BlueprintReadWrite, Category = "ApexFormula|Telemetry")
	double Value = 0.0;

	FAFTelemetrySample() = default;

	FAFTelemetrySample(FName InChannel, double InSessionTime, int32 InParticipantId, double InValue)
		: Channel(InChannel)
		, SessionTime(InSessionTime)
		, ParticipantId(InParticipantId)
		, Value(InValue)
	{
	}
};

/**
 * Vector variant of FAFTelemetrySample, for channels that are inherently
 * three-dimensional (velocity, acceleration, force). Kept as a parallel type
 * rather than widening the scalar sample, so the common case stays small.
 */
USTRUCT(BlueprintType)
struct APEXFORMULACORE_API FAFTelemetryVectorSample
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadWrite, Category = "ApexFormula|Telemetry")
	FName Channel = NAME_None;

	UPROPERTY(BlueprintReadWrite, Category = "ApexFormula|Telemetry")
	double SessionTime = 0.0;

	UPROPERTY(BlueprintReadWrite, Category = "ApexFormula|Telemetry")
	int32 ParticipantId = INDEX_NONE;

	/** Runtime space: Unreal centimetres and derived units. See AFUnits.h. */
	UPROPERTY(BlueprintReadWrite, Category = "ApexFormula|Telemetry")
	FVector Value = FVector::ZeroVector;

	FAFTelemetryVectorSample() = default;

	FAFTelemetryVectorSample(FName InChannel, double InSessionTime, int32 InParticipantId, const FVector& InValue)
		: Channel(InChannel)
		, SessionTime(InSessionTime)
		, ParticipantId(InParticipantId)
		, Value(InValue)
	{
	}
};

/**
 * Canonical telemetry channel names.
 *
 * Rule: no telemetry channel name may be written as a bare string literal at
 * a call site. Every channel is declared here once, so that renaming a channel
 * is a one-file change and so the static validator can enumerate the whole
 * channel vocabulary.
 */
namespace AFTelemetryChannels
{
	/** Vehicle speed, km/h. */
	APEXFORMULACORE_API extern const FName VehicleSpeedKph;

	/** Engine or MGU output, normalised 0..1. */
	APEXFORMULACORE_API extern const FName VehicleThrottle;

	/** Brake application, normalised 0..1. */
	APEXFORMULACORE_API extern const FName VehicleBrake;

	/** Steering, normalised -1..1, positive is right. */
	APEXFORMULACORE_API extern const FName VehicleSteer;

	/** Selected gear as an integer value. */
	APEXFORMULACORE_API extern const FName VehicleGear;

	/** Stored energy remaining, normalised 0..1. */
	APEXFORMULACORE_API extern const FName EnergyStateOfCharge;

	/** Fuel mass remaining, kilograms. */
	APEXFORMULACORE_API extern const FName FuelMassKg;

	/** Last completed lap time, seconds. */
	APEXFORMULACORE_API extern const FName RaceLapTimeSeconds;

	/** Last completed sector time, seconds. */
	APEXFORMULACORE_API extern const FName RaceSectorTimeSeconds;

	/** Current position in the classification, 1-based. */
	APEXFORMULACORE_API extern const FName RacePosition;

	/** Returns every declared channel name. Used by tests and the validator. */
	APEXFORMULACORE_API TArray<FName> GetAllChannels();
}
