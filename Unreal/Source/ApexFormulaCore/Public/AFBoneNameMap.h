// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

#pragma once

#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "AFBoneNameMap.generated.h"

/**
 * The four ApexFormula wheel corners.
 * Order matches af_pipeline_config.CORNERS exactly: FL, FR, RL, RR.
 */
UENUM(BlueprintType)
enum class EAFCorner : uint8
{
	FL		UMETA(DisplayName = "Front Left"),
	FR		UMETA(DisplayName = "Front Right"),
	RL		UMETA(DisplayName = "Rear Left"),
	RR		UMETA(DisplayName = "Rear Right")
};

/**
 * UAFBoneNameMap - the single central location for all ApexFormula skeletal
 * bone names.
 *
 * Architecture reference: TECHNICAL_ARCHITECTURE.md section 5,
 * "Central bone-name convention".
 * Decision reference: DECISION_LOG.md D-012 (eleven-bone convention).
 *
 * This is an ApexFormula convention. It is NOT assumed to be any Chaos
 * Vehicles default, and it is NOT derived from any real motorsport standard.
 *
 * The default values below mirror af_pipeline_config.BONE_ORDER exactly, in
 * the same order. That equivalence is enforced by the static validator
 * Tools/af_static_validate.py, which parses both files and compares the lists.
 *
 * Changing a bone name must be a one-file change here plus the matching
 * one-line change in af_pipeline_config.py plus a re-export - never a code hunt.
 *
 * Status: statically inspected. requires Unreal Editor verification (that
 * Unreal Engine 5.8's vehicle setup accepts a fully data-driven bone mapping
 * with these names).
 */
UCLASS(BlueprintType)
class APEXFORMULACORE_API UAFBoneNameMap : public UPrimaryDataAsset
{
	GENERATED_BODY()

public:
	UAFBoneNameMap();

	/** Data Asset schema version. Migration code in Core keys off this. */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "ApexFormula|Versioning")
	int32 DataVersion = 1;

	/** Skeleton root. Not a deform bone. */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "ApexFormula|Bones")
	FName RootBone;

	/** Chassis / body deform bone. */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "ApexFormula|Bones")
	FName ChassisBone;

	/** Steering wheel bone. CONTROL bone, not a deform bone. */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "ApexFormula|Bones")
	FName SteeringBone;

	/** Wheel bones, indexed by EAFCorner. Exactly four entries. */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "ApexFormula|Bones")
	TMap<EAFCorner, FName> WheelBones;

	/** Suspension bones, indexed by EAFCorner. Exactly four entries. */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "ApexFormula|Bones")
	TMap<EAFCorner, FName> SuspensionBones;

	/** Returns the wheel bone name for a corner, or NAME_None if unmapped. */
	UFUNCTION(BlueprintPure, Category = "ApexFormula|Bones")
	FName GetWheelBone(EAFCorner Corner) const;

	/** Returns the suspension bone name for a corner, or NAME_None if unmapped. */
	UFUNCTION(BlueprintPure, Category = "ApexFormula|Bones")
	FName GetSuspensionBone(EAFCorner Corner) const;

	/**
	 * Returns all eleven bone names in the canonical BONE_ORDER, which is
	 * HIERARCHY-INTERLEAVED, not grouped by kind:
	 *
	 *   Root, Chassis, Steering,
	 *   Suspension_FL, Wheel_FL,
	 *   Suspension_FR, Wheel_FR,
	 *   Suspension_RL, Wheel_RL,
	 *   Suspension_RR, Wheel_RR
	 *
	 * Each suspension bone immediately precedes the wheel bone it parents.
	 * This exact sequence is asserted against af_pipeline_config.BONE_ORDER
	 * by Tools/af_static_validate.py.
	 */
	UFUNCTION(BlueprintPure, Category = "ApexFormula|Bones")
	TArray<FName> GetAllBoneNamesInOrder() const;

	/**
	 * Returns the nine deform bone names, mirroring
	 * af_pipeline_config.DEFORM_BONES in its exact order:
	 *
	 *   Chassis,
	 *   Suspension_FL, Suspension_FR, Suspension_RL, Suspension_RR,
	 *   Wheel_FL, Wheel_FR, Wheel_RL, Wheel_RR
	 *
	 * AF_Root and AF_Steering are CONTROL bones: they carry no vertex weights
	 * in the placeholder vehicle. Note this differs in both membership and
	 * ordering from GetAllBoneNamesInOrder().
	 */
	UFUNCTION(BlueprintPure, Category = "ApexFormula|Bones")
	TArray<FName> GetDeformBoneNames() const;

	/**
	 * Returns the parent bone name for a given bone, mirroring
	 * af_pipeline_config.BONE_PARENTS. Returns NAME_None for the root bone
	 * and for any name not in this map.
	 */
	UFUNCTION(BlueprintPure, Category = "ApexFormula|Bones")
	FName GetParentBone(FName BoneName) const;

	/**
	 * Self-validation. Returns an empty array when the asset is well formed.
	 * Each returned string is a human-readable problem description.
	 *
	 * Checks: no empty names, no duplicates, all four corners present in both
	 * maps, and no prohibited name token appears in any bone name.
	 */
	UFUNCTION(BlueprintCallable, Category = "ApexFormula|Bones")
	TArray<FString> ValidateSelf() const;

	/** The four corners in canonical order. */
	static const TArray<EAFCorner>& GetCornersInOrder();

	/** Human-readable two-letter corner suffix, e.g. EAFCorner::FL -> "FL". */
	UFUNCTION(BlueprintPure, Category = "ApexFormula|Bones")
	static FString CornerToSuffix(EAFCorner Corner);
};
