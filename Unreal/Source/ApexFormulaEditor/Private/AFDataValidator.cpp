// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

#include "AFDataValidator.h"
#include "AFBoneNameMap.h"
#include "AFLog.h"
#include "AFQualityProfile.h"
#include "AFSessionRules.h"
#include "AFTrackDefinition.h"
#include "AFVehicleDefinition.h"

namespace
{
	/** Builds one issue record for an asset. */
	FAFValidationIssue MakeIssue(const UObject* Asset, const FString& Message)
	{
		FAFValidationIssue Issue;
		Issue.AssetName = Asset ? Asset->GetName() : TEXT("<null>");
		Issue.AssetClass = (Asset && Asset->GetClass()) ? Asset->GetClass()->GetName() : TEXT("<unknown>");
		Issue.Message = Message;
		return Issue;
	}

	/** Turns a ValidateSelf string list into issue records. */
	void AppendProblems(const UObject* Asset, const TArray<FString>& Problems, TArray<FAFValidationIssue>& OutIssues)
	{
		for (const FString& Problem : Problems)
		{
			OutIssues.Add(MakeIssue(Asset, Problem));
		}
	}
}

TArray<FAFValidationIssue> UAFDataValidator::ValidateAsset(const UObject* Asset)
{
	TArray<FAFValidationIssue> Issues;

	if (!Asset)
	{
		Issues.Add(MakeIssue(nullptr, TEXT("Asset reference is null")));
		return Issues;
	}

	if (const UAFBoneNameMap* BoneMap = Cast<UAFBoneNameMap>(Asset))
	{
		AppendProblems(Asset, BoneMap->ValidateSelf(), Issues);
	}
	else if (const UAFQualityProfile* Quality = Cast<UAFQualityProfile>(Asset))
	{
		AppendProblems(Asset, Quality->ValidateSelf(), Issues);
	}
	else if (const UAFVehicleDefinition* Vehicle = Cast<UAFVehicleDefinition>(Asset))
	{
		AppendProblems(Asset, Vehicle->ValidateSelf(), Issues);
	}
	else if (const UAFTrackDefinition* Track = Cast<UAFTrackDefinition>(Asset))
	{
		AppendProblems(Asset, Track->ValidateSelf(), Issues);
	}
	else if (const UAFSessionRules* Rules = Cast<UAFSessionRules>(Asset))
	{
		AppendProblems(Asset, Rules->ValidateSelf(), Issues);
	}
	else
	{
		// Reported rather than ignored. A silent pass on an unknown class is
		// how an unvalidated asset reaches a build.
		Issues.Add(MakeIssue(Asset,
			TEXT("No ApexFormula validation rule is registered for this asset class")));
	}

	return Issues;
}

TArray<FAFValidationIssue> UAFDataValidator::ValidateAssets(const TArray<UObject*>& Assets)
{
	TArray<FAFValidationIssue> Issues;

	for (const UObject* Asset : Assets)
	{
		Issues.Append(ValidateAsset(Asset));
	}

	return Issues;
}

FString UAFDataValidator::FormatReport(const TArray<FAFValidationIssue>& Issues)
{
	if (Issues.Num() == 0)
	{
		return TEXT("ApexFormula data validation: 0 issues.");
	}

	TStringBuilder<2048> Builder;
	Builder.Appendf(TEXT("ApexFormula data validation: %d issue(s)."), Issues.Num());

	for (const FAFValidationIssue& Issue : Issues)
	{
		Builder.Appendf(TEXT("\n  [%s] %s: %s"),
			*Issue.AssetClass, *Issue.AssetName, *Issue.Message);
	}

	return Builder.ToString();
}

int32 UAFDataValidator::LogIssues(const TArray<FAFValidationIssue>& Issues)
{
	for (const FAFValidationIssue& Issue : Issues)
	{
		UE_LOG(LogAFCore, Error, TEXT("[%s] %s: %s"),
			*Issue.AssetClass, *Issue.AssetName, *Issue.Message);
	}

	return Issues.Num();
}
