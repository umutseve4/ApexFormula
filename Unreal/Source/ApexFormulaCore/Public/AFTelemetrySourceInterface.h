// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

#pragma once

#include "CoreMinimal.h"
#include "UObject/Interface.h"
#include "AFTelemetryTypes.h"
#include "AFTelemetrySourceInterface.generated.h"

UINTERFACE(MinimalAPI, BlueprintType)
class UAFTelemetrySource : public UInterface
{
	GENERATED_BODY()
};

/**
 * IAFTelemetrySource - implemented by anything that can be polled for samples.
 *
 * Architecture reference: TECHNICAL_ARCHITECTURE.md sections 2 and 10.
 *
 * There are two ways telemetry reaches the bus:
 *  1. Push. A producer calls UAFTelemetryBus::Publish when it has news.
 *  2. Pull. A sampler walks every IAFTelemetrySource at a fixed rate and
 *     publishes what it collects.
 *
 * The pull path exists so that recording rate is a session decision rather than
 * something each component invents for itself, which is what keeps replay
 * snapshots evenly spaced.
 *
 * Status: statically inspected. requires local compilation.
 */
class APEXFORMULACORE_API IAFTelemetrySource
{
	GENERATED_BODY()

public:
	/**
	 * Append this source's current samples to OutSamples.
	 * Implementations must not clear OutSamples.
	 * SessionTime is supplied by the caller so every source in one tick shares
	 * an identical timestamp.
	 */
	virtual void CollectTelemetry(double SessionTime, TArray<FAFTelemetrySample>& OutSamples) const = 0;

	/**
	 * The channels this source can ever emit. Used to build the recording
	 * schema up front, and by tests to assert a source never emits a channel
	 * it did not declare.
	 */
	virtual TArray<FName> GetProvidedTelemetryChannels() const = 0;
};
