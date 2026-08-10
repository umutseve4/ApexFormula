// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

#include "AFCheckpoint.h"
#include "AFLog.h"
#include "AFRaceParticipantInterface.h"
#include "Components/BoxComponent.h"

AAFCheckpoint::AAFCheckpoint()
{
	// A checkpoint is event driven. Ticking it would cost frame time for no
	// benefit, and every crossing already carries an explicit session time.
	PrimaryActorTick.bCanEverTick = false;

	TriggerVolume = CreateDefaultSubobject<UBoxComponent>(TEXT("TriggerVolume"));
	if (TriggerVolume)
	{
		SetRootComponent(TriggerVolume);
		TriggerVolume->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
		TriggerVolume->SetCollisionResponseToAllChannels(ECR_Overlap);
		TriggerVolume->SetGenerateOverlapEvents(true);
	}
}

void AAFCheckpoint::BeginPlay()
{
	Super::BeginPlay();

	const TArray<FString> Problems = ValidateSelf();
	for (const FString& Problem : Problems)
	{
		UE_LOG(LogAFRace, Error, TEXT("Checkpoint '%s': %s"), *GetName(), *Problem);
	}
}

bool AAFCheckpoint::ReportCrossing(AActor* CrossingActor, const double SessionTime)
{
	if (!CrossingActor)
	{
		return false;
	}

	// Race code never casts to a vehicle type. If an actor cannot describe
	// itself as a race participant it is scenery as far as timing is concerned.
	const IAFRaceParticipant* Participant = Cast<IAFRaceParticipant>(CrossingActor);
	if (!Participant)
	{
		UE_LOG(LogAFRace, Verbose,
			TEXT("Checkpoint '%s' ignored actor '%s'; it does not implement IAFRaceParticipant."),
			*CheckpointId.ToString(), *CrossingActor->GetName());
		return false;
	}

	if (!Participant->IsParticipantActive())
	{
		UE_LOG(LogAFRace, Verbose,
			TEXT("Checkpoint '%s' ignored inactive participant '%s'."),
			*CheckpointId.ToString(), *CrossingActor->GetName());
		return false;
	}

	const int32 ParticipantId = Participant->GetParticipantId();

	UE_LOG(LogAFRace, Verbose,
		TEXT("Checkpoint '%s' crossed by participant %d at %f."),
		*CheckpointId.ToString(), ParticipantId, SessionTime);

	OnCheckpointPassed.Broadcast(CheckpointId, ParticipantId, SessionTime);
	return true;
}

TArray<FString> AAFCheckpoint::ValidateSelf() const
{
	TArray<FString> Problems;

	if (CheckpointId.IsNone())
	{
		Problems.Add(TEXT("CheckpointId must be set"));
	}
	else
	{
		const FString AsString = CheckpointId.ToString();

		if (AsString != AsString.ToLower())
		{
			Problems.Add(FString::Printf(TEXT("CheckpointId '%s' must be lower case"), *AsString));
		}
		if (AsString.Contains(TEXT(" ")))
		{
			Problems.Add(FString::Printf(TEXT("CheckpointId '%s' must not contain spaces"), *AsString));
		}
	}

	if (AuthoringOrderIndex < 0)
	{
		Problems.Add(FString::Printf(
			TEXT("AuthoringOrderIndex must be >= 0, is %d"), AuthoringOrderIndex));
	}

	// The timing line opens and closes the lap, so it is always index 0.
	if (bIsTimingLine && AuthoringOrderIndex != 0)
	{
		Problems.Add(FString::Printf(
			TEXT("The timing line must have AuthoringOrderIndex 0, has %d"), AuthoringOrderIndex));
	}

	if (!TriggerVolume)
	{
		Problems.Add(TEXT("TriggerVolume is missing"));
	}

	return Problems;
}
