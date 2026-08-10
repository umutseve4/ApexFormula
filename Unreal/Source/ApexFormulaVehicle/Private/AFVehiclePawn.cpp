// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

#include "AFVehiclePawn.h"
#include "AFVehicleCompatibilityLayer.h"
#include "AFVehicleComponentBase.h"
#include "AFVehicleDefinition.h"
#include "AFLog.h"
#include "Components/SkeletalMeshComponent.h"

AAFVehiclePawn::AAFVehiclePawn()
{
	// Milestone 1 has no per-frame vehicle behaviour.
	PrimaryActorTick.bCanEverTick = false;

	VehicleMeshComponent = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("VehicleMesh"));
	SetRootComponent(VehicleMeshComponent);

	CompatibilityLayer = CreateDefaultSubobject<UAFVehicleCompatibilityLayer>(TEXT("CompatibilityLayer"));
}

void AAFVehiclePawn::BeginPlay()
{
	Super::BeginPlay();

	if (VehicleDefinition != nullptr)
	{
		ApplyVehicleDefinition();
	}
	else
	{
		UE_LOG(LogAFVehicle, Warning,
			TEXT("%s spawned with no VehicleDefinition assigned."), *GetName());
	}
}

bool AAFVehiclePawn::ApplyVehicleDefinition()
{
	if (VehicleDefinition == nullptr)
	{
		UE_LOG(LogAFVehicle, Warning,
			TEXT("%s: ApplyVehicleDefinition called with no definition assigned."),
			*GetName());
		return false;
	}

	const TArray<FString> Problems = VehicleDefinition->ValidateSelf();
	for (const FString& Problem : Problems)
	{
		UE_LOG(LogAFVehicle, Error,
			TEXT("%s: vehicle definition '%s' is invalid: %s"),
			*GetName(), *VehicleDefinition->VehicleId.ToString(), *Problem);
	}

	if (Problems.Num() > 0)
	{
		return false;
	}

	// Deterministic ordering. GetComponents does not guarantee a stable order,
	// so sort by SubsystemId before configuring. Configuration order must not
	// depend on how the components happened to be registered.
	TArray<UAFVehicleComponentBase*> Subsystems;
	GetComponents<UAFVehicleComponentBase>(Subsystems);

	Subsystems.Sort(
		[](const UAFVehicleComponentBase& A, const UAFVehicleComponentBase& B)
		{
			return A.SubsystemId.LexicalLess(B.SubsystemId);
		});

	for (UAFVehicleComponentBase* Subsystem : Subsystems)
	{
		if (Subsystem != nullptr)
		{
			Subsystem->ApplyConfiguration();
		}
	}

	UE_LOG(LogAFVehicle, Log,
		TEXT("%s configured from vehicle definition '%s' with %d subsystem component(s)."),
		*GetName(), *VehicleDefinition->VehicleId.ToString(), Subsystems.Num());

	return true;
}

void AAFVehiclePawn::SubmitInputFrame(const FAFVehicleInputFrame& InputFrame)
{
	if (CompatibilityLayer != nullptr)
	{
		CompatibilityLayer->ApplyInputFrame(InputFrame);
	}
}

int32 AAFVehiclePawn::GetParticipantId() const
{
	return ParticipantId;
}

FText AAFVehiclePawn::GetParticipantDisplayName() const
{
	return DriverDisplayName;
}

FVector AAFVehiclePawn::GetParticipantLocation() const
{
	return GetActorLocation();
}

FVector AAFVehiclePawn::GetParticipantForward() const
{
	return GetActorForwardVector();
}

double AAFVehiclePawn::GetParticipantSpeedKph() const
{
	return (CompatibilityLayer != nullptr)
		? CompatibilityLayer->GetForwardSpeedKph()
		: 0.0;
}

bool AAFVehiclePawn::IsParticipantActive() const
{
	return ParticipantId != INDEX_NONE && !IsActorBeingDestroyed();
}
