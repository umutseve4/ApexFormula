// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

#include "AFPlayerController.h"
#include "AFVehiclePawn.h"
#include "AFLog.h"

#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystems.h"
#include "InputAction.h"
#include "InputActionValue.h"
#include "InputMappingContext.h"

AAFPlayerController::AAFPlayerController()
{
	// PlayerTick is where the frame is submitted, so this controller must tick.
	PrimaryActorTick.bCanEverTick = true;
}

void AAFPlayerController::BeginPlay()
{
	Super::BeginPlay();

	SessionTimeSeconds = 0.0;
	PendingFrame = FAFVehicleInputFrame();

	if (VehicleMappingContext == nullptr)
	{
		UE_LOG(LogAFVehicle, Warning,
			TEXT("%s: VehicleMappingContext is not assigned. ")
			TEXT("No driver input will reach the vehicle."),
			*GetName());
		return;
	}

	// ASSUMPTION REQUIRING VERIFICATION. The Enhanced Input local player
	// subsystem is the documented place to add a mapping context in UE 5.x.
	// The exact type name has not been verified against a UE 5.8 installation
	// because no engine is available in this environment.
	if (UEnhancedInputLocalPlayerSubsystem* Subsystem =
		ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(GetLocalPlayer()))
	{
		Subsystem->AddMappingContext(VehicleMappingContext, VehicleMappingPriority);

		UE_LOG(LogAFVehicle, Log,
			TEXT("%s added the vehicle mapping context at priority %d."),
			*GetName(), VehicleMappingPriority);
	}
	else
	{
		UE_LOG(LogAFVehicle, Error,
			TEXT("%s: no Enhanced Input local player subsystem. ")
			TEXT("The mapping context was not added."),
			*GetName());
	}
}

void AAFPlayerController::SetupInputComponent()
{
	Super::SetupInputComponent();

	// ASSUMPTION REQUIRING VERIFICATION. This requires the project's default
	// input component class to be UEnhancedInputComponent. If it is not, this
	// cast fails at runtime and every binding below is silently skipped, which
	// is why the failure is logged as an error rather than ignored.
	UEnhancedInputComponent* EnhancedInput = Cast<UEnhancedInputComponent>(InputComponent);
	if (EnhancedInput == nullptr)
	{
		UE_LOG(LogAFVehicle, Error,
			TEXT("%s: InputComponent is not a UEnhancedInputComponent. ")
			TEXT("Check DefaultInputComponentClass in the project input settings."),
			*GetName());
		return;
	}

	// Analogue axes are bound to Triggered so a held key keeps producing a
	// value. Binding them to Started would give a single-frame pulse and the
	// car would never hold throttle.
	if (ThrottleAction != nullptr)
	{
		EnhancedInput->BindAction(ThrottleAction, ETriggerEvent::Triggered, this, &AAFPlayerController::HandleThrottle);
		EnhancedInput->BindAction(ThrottleAction, ETriggerEvent::Completed, this, &AAFPlayerController::HandleThrottle);
	}

	if (BrakeAction != nullptr)
	{
		EnhancedInput->BindAction(BrakeAction, ETriggerEvent::Triggered, this, &AAFPlayerController::HandleBrake);
		EnhancedInput->BindAction(BrakeAction, ETriggerEvent::Completed, this, &AAFPlayerController::HandleBrake);
	}

	if (SteerAction != nullptr)
	{
		EnhancedInput->BindAction(SteerAction, ETriggerEvent::Triggered, this, &AAFPlayerController::HandleSteer);
		EnhancedInput->BindAction(SteerAction, ETriggerEvent::Completed, this, &AAFPlayerController::HandleSteer);
	}

	// Shifts are edges. Started fires once per press, which is exactly the
	// contract FAFVehicleInputFrame documents for bShiftUp and bShiftDown.
	if (ShiftUpAction != nullptr)
	{
		EnhancedInput->BindAction(ShiftUpAction, ETriggerEvent::Started, this, &AAFPlayerController::HandleShiftUp);
	}

	if (ShiftDownAction != nullptr)
	{
		EnhancedInput->BindAction(ShiftDownAction, ETriggerEvent::Started, this, &AAFPlayerController::HandleShiftDown);
	}

	// The handbrake is a held state, so both edges are needed.
	if (HandbrakeAction != nullptr)
	{
		EnhancedInput->BindAction(HandbrakeAction, ETriggerEvent::Started, this, &AAFPlayerController::HandleHandbrakeStarted);
		EnhancedInput->BindAction(HandbrakeAction, ETriggerEvent::Completed, this, &AAFPlayerController::HandleHandbrakeCompleted);
	}

	if (ResetVehicleAction != nullptr)
	{
		EnhancedInput->BindAction(ResetVehicleAction, ETriggerEvent::Started, this, &AAFPlayerController::HandleResetVehicle);
	}
}

void AAFPlayerController::OnPossess(APawn* InPawn)
{
	Super::OnPossess(InPawn);

	// Possessing a new pawn must not carry the previous pawn's intent across.
	PendingFrame = FAFVehicleInputFrame();
	bHandbrakeHeld = false;
	bHandbrakeDirty = true;

	if (GetVehiclePawn() == nullptr)
	{
		UE_LOG(LogAFVehicle, Warning,
			TEXT("%s possessed a pawn that is not an AAFVehiclePawn. ")
			TEXT("Driver input will be assembled but not delivered."),
			*GetName());
	}
}

void AAFPlayerController::PlayerTick(float DeltaTime)
{
	Super::PlayerTick(DeltaTime);

	SessionTimeSeconds += static_cast<double>(DeltaTime);

	AAFVehiclePawn* VehiclePawn = GetVehiclePawn();
	if (VehiclePawn == nullptr)
	{
		// Still clear the edges. Holding a stale shift edge across a
		// possession gap would fire a phantom gear change on the next pawn.
		PendingFrame.bShiftUp = false;
		PendingFrame.bShiftDown = false;
		return;
	}

	// The handbrake travels outside the input frame because it is a latched
	// state rather than a per-frame value; pushing it only on change keeps the
	// backend from being told the same thing every frame.
	if (bHandbrakeDirty)
	{
		VehiclePawn->SetHandbrake(bHandbrakeHeld);
		bHandbrakeDirty = false;
	}

	PendingFrame.SessionTime = SessionTimeSeconds;
	PendingFrame.Sanitise();

	VehiclePawn->SubmitInputFrame(PendingFrame);

	// Edges are consumed by submission. Analogue values persist because they
	// represent a held position, not an event.
	PendingFrame.bShiftUp = false;
	PendingFrame.bShiftDown = false;
}

AAFVehiclePawn* AAFPlayerController::GetVehiclePawn() const
{
	return Cast<AAFVehiclePawn>(GetPawn());
}

void AAFPlayerController::HandleThrottle(const FInputActionValue& Value)
{
	PendingFrame.Throttle = Value.Get<float>();
}

void AAFPlayerController::HandleBrake(const FInputActionValue& Value)
{
	PendingFrame.Brake = Value.Get<float>();
}

void AAFPlayerController::HandleSteer(const FInputActionValue& Value)
{
	// Positive is right. Any axis inversion belongs in the Input Mapping
	// Context as a Negate modifier, not in C++, so a player can rebind it.
	PendingFrame.Steer = Value.Get<float>();
}

void AAFPlayerController::HandleShiftUp(const FInputActionValue& Value)
{
	PendingFrame.bShiftUp = true;
}

void AAFPlayerController::HandleShiftDown(const FInputActionValue& Value)
{
	PendingFrame.bShiftDown = true;
}

void AAFPlayerController::HandleHandbrakeStarted(const FInputActionValue& Value)
{
	if (!bHandbrakeHeld)
	{
		bHandbrakeHeld = true;
		bHandbrakeDirty = true;
	}
}

void AAFPlayerController::HandleHandbrakeCompleted(const FInputActionValue& Value)
{
	if (bHandbrakeHeld)
	{
		bHandbrakeHeld = false;
		bHandbrakeDirty = true;
	}
}

void AAFPlayerController::HandleResetVehicle(const FInputActionValue& Value)
{
	if (AAFVehiclePawn* VehiclePawn = GetVehiclePawn())
	{
		VehiclePawn->ResetVehicle();
	}
}
