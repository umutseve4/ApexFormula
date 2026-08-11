// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

#pragma once

#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "AFWheelSetup.h"
#include "AFVehicleDefinition.generated.h"

class UAFBoneNameMap;
class USkeletalMesh;

/**
 * UAFVehicleDefinition - the root Data Asset describing one vehicle.
 *
 * Architecture reference: TECHNICAL_ARCHITECTURE.md section 5.
 * Milestone reference: MILESTONE_2_IMPLEMENTATION.md section 4.
 *
 * Holds identity, mass, dimensions and references to the profile assets that
 * describe each subsystem. Per the no-magic-numbers rule, no vehicle constant
 * may live in C++; it lives here.
 *
 * Every dimension below is an ApexFormula design value. These are fictional
 * numbers chosen for this project. They are NOT official measurements from any
 * real motorsport series and must never be presented as such.
 *
 * Status: statically inspected. requires local compilation.
 * requires Unreal Editor verification (asset authoring and mesh binding).
 */
UCLASS(BlueprintType)
class APEXFORMULAVEHICLE_API UAFVehicleDefinition : public UPrimaryDataAsset
{
	GENERATED_BODY()

public:
	/** Schema version for this asset type. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Meta")
	int32 DataVersion = 2;

	/** Stable internal id, lower case, no spaces. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Meta")
	FName VehicleId = NAME_None;

	/** Player-facing name. Original fictional naming only. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Meta")
	FText DisplayName;

	/** Fictional constructor name. Must not resemble a real team. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Meta")
	FText ConstructorName;

	//
	// Geometry. ApexFormula design values, metres and kilograms.
	//
	// D-041. The defaults below are kept numerically identical to
	// BlenderPipeline/scripts/af_pipeline_config.py, section DESIGN. That file
	// is the single source of truth for vehicle geometry, because it is the
	// file that actually builds the mesh; this data asset only describes the
	// mesh that Blender produced. Where the two disagreed, Blender won.
	//
	//   DESIGN["wheelbase_m"]      3.600  ->  WheelbaseM
	//   DESIGN["track_front_m"]    1.600  ->  FrontTrackM
	//   DESIGN["track_rear_m"]     1.540  ->  RearTrackM
	//   DESIGN["overall_length_m"] 5.600  ->  OverallLengthM
	//
	// If a value here is edited, edit af_pipeline_config.py in the same commit
	// and re-run the Blender smoke test, or the exported mesh and the physics
	// body will describe two different cars.
	//

	/** Dry mass without driver or fuel, kilograms. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Mass", meta = (ClampMin = "1.0"))
	double DryMassKg = 740.0;

	/** Distance between front and rear axle centres, metres. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Geometry", meta = (ClampMin = "0.1"))
	double WheelbaseM = 3.60;

	/** Front track width, metres. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Geometry", meta = (ClampMin = "0.1"))
	double FrontTrackM = 1.60;

	/** Rear track width, metres. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Geometry", meta = (ClampMin = "0.1"))
	double RearTrackM = 1.54;

	/** Overall length, metres. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Geometry", meta = (ClampMin = "0.1"))
	double OverallLengthM = 5.60;

	/**
	 * Longitudinal centre of mass position as a fraction from the front axle.
	 * 0.5 is exactly midway; larger values move mass rearward.
	 */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Mass", meta = (ClampMin = "0.0", ClampMax = "1.0"))
	double CentreOfMassBiasRear = 0.55;

	/** Centre of mass height above the reference plane, metres. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Mass", meta = (ClampMin = "0.0"))
	double CentreOfMassHeightM = 0.28;

	//
	// Wheels. Added in Milestone 2.
	//
	// Exactly four entries are expected, and each BoneName must be one of the
	// four D-012 wheel bones. The order of the array does not matter; the
	// compatibility layer derives axle assignment from bAffectedBySteering
	// rather than from array position, so a reordered array produces an
	// identical car.
	//

	/** Per-corner wheel configuration. Exactly four entries. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Wheels")
	TArray<FAFWheelSetup> Wheels;

	//
	// Asset references
	//

	/** Skeletal mesh produced by the Blender pipeline. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Assets")
	TSoftObjectPtr<USkeletalMesh> VehicleMesh;

	/** Bone naming contract this vehicle's skeleton must satisfy. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ApexFormula|Assets")
	TSoftObjectPtr<UAFBoneNameMap> BoneNameMap;

	/** Returns a list of human-readable problems. Empty means valid. */
	UFUNCTION(BlueprintCallable, Category = "ApexFormula|Validation")
	TArray<FString> ValidateSelf() const;
};
