// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

#pragma once

#include "CoreMinimal.h"
#include "AFViewModelBase.h"
#include "AFHudViewModel.generated.h"

struct FAFTelemetrySample;

/**
 * UAFHudViewModel - values the in-car HUD displays.
 *
 * Architecture reference: TECHNICAL_ARCHITECTURE.md sections 2 and 11.
 *
 * Subscribes to a small, explicit set of telemetry channels and stores the
 * latest value of each. Nothing here is computed from world state, so the HUD
 * can be exercised in a test by publishing samples onto a bus with no vehicle,
 * no track and no frame, in line with the section 9 testing principle.
 *
 * Status: statically inspected. requires local compilation.
 */
UCLASS(BlueprintType)
class APEXFORMULAUI_API UAFHudViewModel : public UAFViewModelBase
{
	GENERATED_BODY()

public:
	/** Latest road speed, kilometres per hour. */
	UPROPERTY(BlueprintReadOnly, Category = "ApexFormula|UI")
	float SpeedKph = 0.0f;

	/** Latest gear. Zero is neutral; negative is reverse. */
	UPROPERTY(BlueprintReadOnly, Category = "ApexFormula|UI")
	int32 Gear = 0;

	/** Latest throttle demand, 0..1. */
	UPROPERTY(BlueprintReadOnly, Category = "ApexFormula|UI")
	float Throttle = 0.0f;

	/** Latest brake demand, 0..1. */
	UPROPERTY(BlueprintReadOnly, Category = "ApexFormula|UI")
	float Brake = 0.0f;

	/** Latest stored energy state of charge, 0..1. */
	UPROPERTY(BlueprintReadOnly, Category = "ApexFormula|UI")
	float StateOfCharge = 0.0f;

	/** Latest fuel mass, kilograms. */
	UPROPERTY(BlueprintReadOnly, Category = "ApexFormula|UI")
	float FuelMassKg = 0.0f;

	/** Most recent completed lap time, seconds. Zero when none yet. */
	UPROPERTY(BlueprintReadOnly, Category = "ApexFormula|UI")
	float LastLapTimeSeconds = 0.0f;

	/** Current classified position. Zero when unknown. */
	UPROPERTY(BlueprintReadOnly, Category = "ApexFormula|UI")
	int32 Position = 0;

	/** Session time of the most recent sample applied, seconds. */
	UPROPERTY(BlueprintReadOnly, Category = "ApexFormula|UI")
	float LastUpdateTimeSeconds = 0.0f;

	/** LastLapTimeSeconds formatted as m:ss.mmm. */
	UFUNCTION(BlueprintPure, Category = "ApexFormula|UI")
	FString GetFormattedLastLapTime() const;

	/**
	 * Applies one telemetry sample.
	 * Returns true when the sample was on a channel this view model displays.
	 * Public so tests can drive the view model without a bus.
	 */
	UFUNCTION(BlueprintCallable, Category = "ApexFormula|UI")
	bool ApplySample(const FAFTelemetrySample& Sample);

	/** Channels this view model reads. */
	UFUNCTION(BlueprintPure, Category = "ApexFormula|UI")
	static TArray<FName> GetConsumedChannels();

	virtual void ResetViewModel() override;

protected:
	virtual void OnBusBound(UAFTelemetryBus* InBus) override;
	virtual void OnBusUnbound(UAFTelemetryBus* InBus) override;

private:
	/** Handle for the all-channel subscription held while bound. */
	FDelegateHandle SampleHandle;
};
