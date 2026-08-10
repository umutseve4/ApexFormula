// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

#pragma once

#include "CoreMinimal.h"
#include "UObject/Object.h"
#include "AFViewModelBase.generated.h"

class UAFTelemetryBus;

/** Broadcast whenever a view model's published values have changed. */
DECLARE_DYNAMIC_MULTICAST_DELEGATE(FAFOnViewModelChanged);

/**
 * UAFViewModelBase - shared base for every ApexFormula view model.
 *
 * Architecture reference: TECHNICAL_ARCHITECTURE.md sections 2 and 11.
 *
 * A view model is a READ-ONLY projection. It subscribes to the telemetry bus,
 * stores display-ready values, and raises OnViewModelChanged. It must never
 * write to a vehicle, a race subsystem or a Data Asset.
 *
 * Widgets bind to this object rather than reading simulation state directly,
 * so the HUD can be rebuilt or replaced without touching gameplay code.
 *
 * Status: statically inspected. requires local compilation.
 */
UCLASS(Abstract, BlueprintType)
class APEXFORMULAUI_API UAFViewModelBase : public UObject
{
	GENERATED_BODY()

public:
	/** Raised after any published value changes. */
	UPROPERTY(BlueprintAssignable, Category = "ApexFormula|UI")
	FAFOnViewModelChanged OnViewModelChanged;

	/**
	 * Binds this view model to a telemetry bus.
	 * Unbinds from any previous bus first. Passing null unbinds only.
	 */
	UFUNCTION(BlueprintCallable, Category = "ApexFormula|UI")
	void BindToTelemetryBus(UAFTelemetryBus* InBus);

	/** True when a telemetry bus is currently bound. */
	UFUNCTION(BlueprintPure, Category = "ApexFormula|UI")
	bool IsBound() const;

	/** Clears every published value back to its default. */
	UFUNCTION(BlueprintCallable, Category = "ApexFormula|UI")
	virtual void ResetViewModel();

protected:
	/**
	 * Called after a bus is bound so subclasses can register their channel
	 * subscriptions. The base implementation does nothing.
	 */
	virtual void OnBusBound(UAFTelemetryBus* InBus);

	/**
	 * Called before a bus is unbound so subclasses can remove subscriptions.
	 * The base implementation does nothing.
	 */
	virtual void OnBusUnbound(UAFTelemetryBus* InBus);

	/** Raises OnViewModelChanged. Call after mutating published values. */
	void NotifyChanged();

	/** The bus this view model observes. Weak: the bus outlives nothing here. */
	UPROPERTY(Transient)
	TWeakObjectPtr<UAFTelemetryBus> TelemetryBus;
};
