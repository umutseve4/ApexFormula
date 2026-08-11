// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/PlayerController.h"
#include "AFTypes.h"
#include "AFPlayerController.generated.h"

class AAFVehiclePawn;
class UInputAction;
class UInputMappingContext;
struct FInputActionValue;

/**
 * AAFPlayerController - assembles driver intent and submits it once per frame.
 *
 * Decision reference: DECISION_LOG.md D-033.
 * Milestone reference: MILESTONE_2_IMPLEMENTATION.md section 5.
 *
 * Design. Enhanced Input handlers do NOT talk to the vehicle. They only write
 * into a pending FAFVehicleInputFrame. PlayerTick stamps the session time,
 * sanitises the frame and submits it exactly once. This gives one input frame
 * per rendered frame with a single well-defined ordering, which is what a
 * future replay system needs; a design where each handler pokes the vehicle
 * directly cannot be recorded deterministically.
 *
 * Deliberately unbound: Clutch, bDeployEnergy, bRequestDragReduction. Those
 * fields exist in FAFVehicleInputFrame but the systems behind them are
 * Milestone 10. Binding a key to a field nothing reads would imply to a
 * playtester that the feature exists.
 *
 * Status: statically inspected. requires local compilation.
 * requires Unreal Editor verification (mapping context assignment).
 * requires playtesting (control feel).
 */
UCLASS(BlueprintType, Blueprintable)
class APEXFORMULAVEHICLE_API AAFPlayerController : public APlayerController
{
	GENERATED_BODY()

public:
	AAFPlayerController();

	/** The mapping context added on possession. Assign IMC_AFVehicleDefault. */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "ApexFormula|Input")
	TObjectPtr<UInputMappingContext> VehicleMappingContext;

	/** Priority of the vehicle mapping context. */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "ApexFormula|Input")
	int32 VehicleMappingPriority = 0;

	/** Analogue 0..1. W, or right trigger. */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "ApexFormula|Input")
	TObjectPtr<UInputAction> ThrottleAction;

	/** Analogue 0..1. S, or left trigger. */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "ApexFormula|Input")
	TObjectPtr<UInputAction> BrakeAction;

	/** Analogue -1..1, negative left. A and D, or left stick X. */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "ApexFormula|Input")
	TObjectPtr<UInputAction> SteerAction;

	/** Edge. E, or right shoulder. */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "ApexFormula|Input")
	TObjectPtr<UInputAction> ShiftUpAction;

	/** Edge. Q, or left shoulder. */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "ApexFormula|Input")
	TObjectPtr<UInputAction> ShiftDownAction;

	/** Held. Space, or the bottom face button. */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "ApexFormula|Input")
	TObjectPtr<UInputAction> HandbrakeAction;

	/** Edge. R, or the left face button. */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "ApexFormula|Input")
	TObjectPtr<UInputAction> ResetVehicleAction;

	/** The frame most recently submitted. Exposed for on-screen debug and tests. */
	UFUNCTION(BlueprintPure, Category = "ApexFormula|Input")
	const FAFVehicleInputFrame& GetPendingInputFrame() const { return PendingFrame; }

protected:
	virtual void BeginPlay() override;
	virtual void SetupInputComponent() override;
	virtual void OnPossess(APawn* InPawn) override;
	virtual void PlayerTick(float DeltaTime) override;

	/** The possessed vehicle, or nullptr when the controller possesses something else. */
	AAFVehiclePawn* GetVehiclePawn() const;

private:
	void HandleThrottle(const FInputActionValue& Value);
	void HandleBrake(const FInputActionValue& Value);
	void HandleSteer(const FInputActionValue& Value);
	void HandleShiftUp(const FInputActionValue& Value);
	void HandleShiftDown(const FInputActionValue& Value);
	void HandleHandbrakeStarted(const FInputActionValue& Value);
	void HandleHandbrakeCompleted(const FInputActionValue& Value);
	void HandleResetVehicle(const FInputActionValue& Value);

	/** Accumulated driver intent for the current frame. */
	FAFVehicleInputFrame PendingFrame;

	/** Seconds since BeginPlay, stamped into every submitted frame. */
	double SessionTimeSeconds = 0.0;

	/** True while the handbrake key is held. */
	bool bHandbrakeHeld = false;

	/** True when the handbrake state changed and needs pushing to the pawn. */
	bool bHandbrakeDirty = false;
};
