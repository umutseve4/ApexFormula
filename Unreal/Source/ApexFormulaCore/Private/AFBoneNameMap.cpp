// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

#include "AFBoneNameMap.h"

namespace
{
	/**
	 * The ApexFormula bone-name prefix. Every bone in the convention starts
	 * with this. Kept in one place so a rename is a one-line change.
	 * Mirrors af_pipeline_config.AF_PREFIX usage.
	 */
	const TCHAR* const AFBonePrefix = TEXT("AF_");
}

const TArray<EAFCorner>& UAFBoneNameMap::GetCornersInOrder()
{
	// Order matches af_pipeline_config.CORNERS = ("FL", "FR", "RL", "RR").
	static const TArray<EAFCorner> Corners = {
		EAFCorner::FL,
		EAFCorner::FR,
		EAFCorner::RL,
		EAFCorner::RR
	};
	return Corners;
}

FString UAFBoneNameMap::CornerToSuffix(EAFCorner Corner)
{
	switch (Corner)
	{
	case EAFCorner::FL: return TEXT("FL");
	case EAFCorner::FR: return TEXT("FR");
	case EAFCorner::RL: return TEXT("RL");
	case EAFCorner::RR: return TEXT("RR");
	default:            return TEXT("??");
	}
}

UAFBoneNameMap::UAFBoneNameMap()
{
	// Defaults mirror af_pipeline_config.py section 3 exactly.
	RootBone     = FName(TEXT("AF_Root"));
	ChassisBone  = FName(TEXT("AF_Chassis"));
	SteeringBone = FName(TEXT("AF_Steering"));

	for (const EAFCorner Corner : GetCornersInOrder())
	{
		const FString Suffix = CornerToSuffix(Corner);
		WheelBones.Add(Corner, FName(*FString::Printf(TEXT("%sWheel_%s"), AFBonePrefix, *Suffix)));
		SuspensionBones.Add(Corner, FName(*FString::Printf(TEXT("%sSuspension_%s"), AFBonePrefix, *Suffix)));
	}
}

FName UAFBoneNameMap::GetWheelBone(EAFCorner Corner) const
{
	const FName* Found = WheelBones.Find(Corner);
	return Found ? *Found : NAME_None;
}

FName UAFBoneNameMap::GetSuspensionBone(EAFCorner Corner) const
{
	const FName* Found = SuspensionBones.Find(Corner);
	return Found ? *Found : NAME_None;
}

TArray<FName> UAFBoneNameMap::GetAllBoneNamesInOrder() const
{
	// HIERARCHY-INTERLEAVED order. Each suspension bone immediately precedes
	// the wheel bone it parents. Mirrors af_pipeline_config.BONE_ORDER.
	TArray<FName> Result;
	Result.Reserve(11);

	Result.Add(RootBone);
	Result.Add(ChassisBone);
	Result.Add(SteeringBone);

	for (const EAFCorner Corner : GetCornersInOrder())
	{
		Result.Add(GetSuspensionBone(Corner));
		Result.Add(GetWheelBone(Corner));
	}

	return Result;
}

TArray<FName> UAFBoneNameMap::GetDeformBoneNames() const
{
	// Mirrors af_pipeline_config.DEFORM_BONES:
	//   (BONE_CHASSIS,) + BONE_SUSPENSIONS + BONE_WHEELS
	// i.e. GROUPED by kind, unlike GetAllBoneNamesInOrder().
	TArray<FName> Result;
	Result.Reserve(9);

	Result.Add(ChassisBone);

	for (const EAFCorner Corner : GetCornersInOrder())
	{
		Result.Add(GetSuspensionBone(Corner));
	}
	for (const EAFCorner Corner : GetCornersInOrder())
	{
		Result.Add(GetWheelBone(Corner));
	}

	return Result;
}

FName UAFBoneNameMap::GetParentBone(FName BoneName) const
{
	// Mirrors af_pipeline_config.BONE_PARENTS.
	if (BoneName == RootBone)
	{
		return NAME_None;
	}
	if (BoneName == ChassisBone)
	{
		return RootBone;
	}
	if (BoneName == SteeringBone)
	{
		return ChassisBone;
	}

	for (const EAFCorner Corner : GetCornersInOrder())
	{
		if (BoneName == GetSuspensionBone(Corner))
		{
			return ChassisBone;
		}
		if (BoneName == GetWheelBone(Corner))
		{
			return GetSuspensionBone(Corner);
		}
	}

	return NAME_None;
}

TArray<FString> UAFBoneNameMap::ValidateSelf() const
{
	TArray<FString> Problems;

	const TArray<FName> All = GetAllBoneNamesInOrder();

	if (All.Num() != 11)
	{
		Problems.Add(FString::Printf(
			TEXT("Bone map must produce exactly 11 bones, produced %d"), All.Num()));
	}

	if (WheelBones.Num() != 4)
	{
		Problems.Add(FString::Printf(
			TEXT("WheelBones must contain exactly 4 entries, contains %d"), WheelBones.Num()));
	}
	if (SuspensionBones.Num() != 4)
	{
		Problems.Add(FString::Printf(
			TEXT("SuspensionBones must contain exactly 4 entries, contains %d"), SuspensionBones.Num()));
	}

	for (const EAFCorner Corner : GetCornersInOrder())
	{
		if (!WheelBones.Contains(Corner))
		{
			Problems.Add(FString::Printf(
				TEXT("WheelBones is missing corner %s"), *CornerToSuffix(Corner)));
		}
		if (!SuspensionBones.Contains(Corner))
		{
			Problems.Add(FString::Printf(
				TEXT("SuspensionBones is missing corner %s"), *CornerToSuffix(Corner)));
		}
	}

	TSet<FName> Seen;
	for (const FName& Bone : All)
	{
		if (Bone.IsNone() || Bone.ToString().IsEmpty())
		{
			Problems.Add(TEXT("Bone map contains an empty bone name"));
			continue;
		}

		const FString AsString = Bone.ToString();

		if (!AsString.StartsWith(AFBonePrefix, ESearchCase::CaseSensitive))
		{
			Problems.Add(FString::Printf(
				TEXT("Bone name '%s' does not start with the required prefix '%s'"),
				*AsString, AFBonePrefix));
		}

		if (AsString.Contains(TEXT(" ")))
		{
			Problems.Add(FString::Printf(
				TEXT("Bone name '%s' contains a space"), *AsString));
		}

		bool bAlreadySeen = false;
		Seen.Add(Bone, &bAlreadySeen);
		if (bAlreadySeen)
		{
			Problems.Add(FString::Printf(
				TEXT("Bone name '%s' is duplicated"), *AsString));
		}
	}

	if (DataVersion < 1)
	{
		Problems.Add(FString::Printf(
			TEXT("DataVersion must be >= 1, is %d"), DataVersion));
	}

	return Problems;
}
