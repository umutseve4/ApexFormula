// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

#include "AFTelemetryBus.h"
#include "AFLog.h"

void UAFTelemetryBus::Publish(const FAFTelemetrySample& Sample)
{
	if (Sample.Channel.IsNone())
	{
		UE_LOG(LogAFCore, Warning,
			TEXT("UAFTelemetryBus::Publish called with an empty channel name. Sample dropped."));
		return;
	}

	++PublishedSampleCount;

	if (FAFOnTelemetrySample* Found = ChannelSubscribers.Find(Sample.Channel))
	{
		Found->Broadcast(Sample);
	}

	AllChannelSubscribers.Broadcast(Sample);
}

void UAFTelemetryBus::PublishVector(const FAFTelemetryVectorSample& Sample)
{
	if (Sample.Channel.IsNone())
	{
		UE_LOG(LogAFCore, Warning,
			TEXT("UAFTelemetryBus::PublishVector called with an empty channel name. Sample dropped."));
		return;
	}

	++PublishedVectorSampleCount;

	AllVectorSubscribers.Broadcast(Sample);
}

void UAFTelemetryBus::PublishValue(FName Channel, double SessionTime, int32 ParticipantId, double Value)
{
	Publish(FAFTelemetrySample(Channel, SessionTime, ParticipantId, Value));
}

FDelegateHandle UAFTelemetryBus::SubscribeToChannel(FName Channel, const FAFOnTelemetrySample::FDelegate& Delegate)
{
	if (Channel.IsNone())
	{
		UE_LOG(LogAFCore, Warning,
			TEXT("UAFTelemetryBus::SubscribeToChannel called with an empty channel name. Ignored."));
		return FDelegateHandle();
	}

	FAFOnTelemetrySample& Multicast = ChannelSubscribers.FindOrAdd(Channel);
	return Multicast.Add(Delegate);
}

FDelegateHandle UAFTelemetryBus::SubscribeToAll(const FAFOnTelemetrySample::FDelegate& Delegate)
{
	return AllChannelSubscribers.Add(Delegate);
}

FDelegateHandle UAFTelemetryBus::SubscribeToAllVectors(const FAFOnTelemetryVectorSample::FDelegate& Delegate)
{
	return AllVectorSubscribers.Add(Delegate);
}

void UAFTelemetryBus::UnsubscribeFromChannel(FName Channel, FDelegateHandle Handle)
{
	if (FAFOnTelemetrySample* Found = ChannelSubscribers.Find(Channel))
	{
		Found->Remove(Handle);

		// Keep the map free of empty entries so GetSubscribedChannelCount()
		// reports live channels only.
		if (!Found->IsBound())
		{
			ChannelSubscribers.Remove(Channel);
		}
	}
}

void UAFTelemetryBus::UnsubscribeFromAll(FDelegateHandle Handle)
{
	AllChannelSubscribers.Remove(Handle);
}

void UAFTelemetryBus::UnsubscribeFromAllVectors(FDelegateHandle Handle)
{
	AllVectorSubscribers.Remove(Handle);
}

void UAFTelemetryBus::Reset()
{
	ChannelSubscribers.Empty();
	AllChannelSubscribers.Clear();
	AllVectorSubscribers.Clear();
	PublishedSampleCount = 0;
	PublishedVectorSampleCount = 0;
}
