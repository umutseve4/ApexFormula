// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

#pragma once

#include "CoreMinimal.h"
#include "UObject/Object.h"
#include "AFTelemetryTypes.h"
#include "AFTelemetryBus.generated.h"

/** Native subscriber signature for scalar telemetry samples. */
DECLARE_MULTICAST_DELEGATE_OneParam(FAFOnTelemetrySample, const FAFTelemetrySample&);

/** Native subscriber signature for vector telemetry samples. */
DECLARE_MULTICAST_DELEGATE_OneParam(FAFOnTelemetryVectorSample, const FAFTelemetryVectorSample&);

/**
 * UAFTelemetryBus - the single telemetry hub.
 *
 * Architecture reference: TECHNICAL_ARCHITECTURE.md section 10.
 *
 * Design rules, enforced by the shape of this class:
 *  - Producers push named channels. They never look up consumers.
 *  - Consumers subscribe by channel, or subscribe to everything.
 *  - There is exactly one bus. UI, replay recording and debug overlays are all
 *    just consumers, which is what stops the HUD becoming a second source of
 *    truth for race state.
 *
 * Threading: this skeleton is game-thread only. Any future off-thread producer
 * must marshal onto the game thread before calling Publish.
 *
 * Status: statically inspected. requires local compilation.
 */
UCLASS(BlueprintType)
class APEXFORMULACORE_API UAFTelemetryBus : public UObject
{
	GENERATED_BODY()

public:
	/** Publish a scalar sample to all matching subscribers. */
	void Publish(const FAFTelemetrySample& Sample);

	/** Publish a vector sample to all matching subscribers. */
	void PublishVector(const FAFTelemetryVectorSample& Sample);

	/** Convenience overload for the common scalar case. */
	UFUNCTION(BlueprintCallable, Category = "ApexFormula|Telemetry")
	void PublishValue(FName Channel, double SessionTime, int32 ParticipantId, double Value);

	/**
	 * Subscribe to a single named channel.
	 * Returns a handle; pass it to Unsubscribe.
	 */
	FDelegateHandle SubscribeToChannel(FName Channel, const FAFOnTelemetrySample::FDelegate& Delegate);

	/** Subscribe to every scalar channel. */
	FDelegateHandle SubscribeToAll(const FAFOnTelemetrySample::FDelegate& Delegate);

	/** Subscribe to every vector channel. */
	FDelegateHandle SubscribeToAllVectors(const FAFOnTelemetryVectorSample::FDelegate& Delegate);

	/** Remove a channel subscription previously returned by SubscribeToChannel. */
	void UnsubscribeFromChannel(FName Channel, FDelegateHandle Handle);

	/** Remove an all-channel scalar subscription. */
	void UnsubscribeFromAll(FDelegateHandle Handle);

	/** Remove an all-channel vector subscription. */
	void UnsubscribeFromAllVectors(FDelegateHandle Handle);

	/** Drop every subscriber. Called on session teardown. */
	UFUNCTION(BlueprintCallable, Category = "ApexFormula|Telemetry")
	void Reset();

	/** Number of scalar samples published since the last Reset. Diagnostics only. */
	UFUNCTION(BlueprintPure, Category = "ApexFormula|Telemetry")
	int64 GetPublishedSampleCount() const { return PublishedSampleCount; }

	/** Number of vector samples published since the last Reset. Diagnostics only. */
	UFUNCTION(BlueprintPure, Category = "ApexFormula|Telemetry")
	int64 GetPublishedVectorSampleCount() const { return PublishedVectorSampleCount; }

	/** Number of distinct channels that currently have at least one subscriber. */
	UFUNCTION(BlueprintPure, Category = "ApexFormula|Telemetry")
	int32 GetSubscribedChannelCount() const { return ChannelSubscribers.Num(); }

private:
	/** Per-channel scalar subscribers. */
	TMap<FName, FAFOnTelemetrySample> ChannelSubscribers;

	/** Scalar subscribers that want every channel. */
	FAFOnTelemetrySample AllChannelSubscribers;

	/** Vector subscribers that want every channel. */
	FAFOnTelemetryVectorSample AllVectorSubscribers;

	int64 PublishedSampleCount = 0;
	int64 PublishedVectorSampleCount = 0;
};
