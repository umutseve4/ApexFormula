// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

#pragma once

#include "CoreMinimal.h"
#include "UObject/Object.h"
#include "AFDataValidator.generated.h"

/** One problem found in one asset. */
USTRUCT(BlueprintType)
struct ULUDAGFORMULAEDITOR_API FAFValidationIssue
{
	GENERATED_BODY()

	/** Name of the asset the issue was found in. */
	UPROPERTY(BlueprintReadOnly, Category = "UludagFormula|Validation")
	FString AssetName;

	/** Class of the asset the issue was found in. */
	UPROPERTY(BlueprintReadOnly, Category = "UludagFormula|Validation")
	FString AssetClass;

	/** Human-readable description of the problem. */
	UPROPERTY(BlueprintReadOnly, Category = "UludagFormula|Validation")
	FString Message;
};

/**
 * UAFDataValidator - editor-side gate for Uludag Formula Data Assets.
 *
 * Architecture reference: TECHNICAL_ARCHITECTURE.md section 5.
 * Decision reference: DECISION_LOG.md D-017, validation is a gate.
 *
 * Every Uludag Formula Data Asset implements its own ValidateSelf returning a
 * list of problem strings. This class is the aggregator: it calls ValidateSelf
 * on each asset handed to it and collects the results into one report. The
 * rules themselves deliberately live next to the data they describe, not here,
 * so that runtime code and editor code can never disagree about what is valid.
 *
 * Status: statically inspected. requires local compilation.
 * requires Unreal Editor verification (asset discovery has not been run).
 */
UCLASS(BlueprintType)
class ULUDAGFORMULAEDITOR_API UAFDataValidator : public UObject
{
	GENERATED_BODY()

public:
	/**
	 * Validates one asset. Returns the issues found.
	 * Returns a single issue when Asset is null, and a single issue when the
	 * asset's class is not one this validator knows how to check, so an
	 * unrecognised asset can never silently pass.
	 */
	UFUNCTION(BlueprintCallable, Category = "UludagFormula|Validation")
	static TArray<FAFValidationIssue> ValidateAsset(const UObject* Asset);

	/** Validates many assets and concatenates the issues in input order. */
	UFUNCTION(BlueprintCallable, Category = "UludagFormula|Validation")
	static TArray<FAFValidationIssue> ValidateAssets(const TArray<UObject*>& Assets);

	/** Formats a report as one line per issue. Returns a summary when empty. */
	UFUNCTION(BlueprintCallable, Category = "UludagFormula|Validation")
	static FString FormatReport(const TArray<FAFValidationIssue>& Issues);

	/** Writes every issue to the log at Error level and returns the count. */
	UFUNCTION(BlueprintCallable, Category = "UludagFormula|Validation")
	static int32 LogIssues(const TArray<FAFValidationIssue>& Issues);
};
