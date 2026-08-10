// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

#pragma once

#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "AFQualityProfile.generated.h"

/**
 * UAFQualityProfile - a named bundle of scalability settings.
 *
 * Architecture reference: TECHNICAL_ARCHITECTURE.md section 5.
 *
 * Exists so that "Low" is a piece of data an artist can edit, not a switch
 * statement buried in C++. Per the no-magic-numbers rule, nothing in code may
 * hardcode a quality threshold; it reads one of these instead.
 *
 * Status: statically inspected. requires local compilation.
 * requires Unreal Editor verification (asset authoring).
 */
UCLASS(BlueprintType)
class APEXFORMULACORE_API UAFQualityProfile : public UPrimaryDataAsset
{
	GENERATED_BODY()

public:
	UAFQualityProfile();

	/** Schema version for this asset type. Bump when fields change meaning. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Meta")
	int32 DataVersion = 1;

	/** Player-facing name, e.g. "Balanced". Original wording only. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Meta")
	FText DisplayName;

	/** Stable internal id, e.g. "balanced". Lower case, no spaces. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Meta")
	FName ProfileId = NAME_None;

	/** Maximum number of opponent vehicles rendered at full detail. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Detail", meta = (ClampMin = "0"))
	int32 MaxFullDetailVehicles = 8;

	/** Distance in metres beyond which vehicles drop to their lowest LOD. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Detail", meta = (ClampMin = "0.0"))
	double VehicleCullDistanceM = 400.0;

	/** Shadow quality index, 0 lowest. Mapped to engine scalability at apply time. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Detail", meta = (ClampMin = "0", ClampMax = "4"))
	int32 ShadowQuality = 2;

	/** Post-process quality index, 0 lowest. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Detail", meta = (ClampMin = "0", ClampMax = "4"))
	int32 PostProcessQuality = 2;

	/** Texture quality index, 0 lowest. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Detail", meta = (ClampMin = "0", ClampMax = "4"))
	int32 TextureQuality = 2;

	/** Screen percentage, 100 is native. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Detail", meta = (ClampMin = "25", ClampMax = "200"))
	int32 ScreenPercentage = 100;

	/**
	 * Telemetry sample rate in hertz for this profile.
	 * Lower profiles record less so that recording never becomes the reason a
	 * machine drops frames.
	 */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Telemetry", meta = (ClampMin = "1.0"))
	double TelemetrySampleRateHz = 30.0;

	/** Returns a list of human-readable problems. Empty means valid. */
	UFUNCTION(BlueprintCallable, Category = "ApexFormula|Validation")
	TArray<FString> ValidateSelf() const;
};
