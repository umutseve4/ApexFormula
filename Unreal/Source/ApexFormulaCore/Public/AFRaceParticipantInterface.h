// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

#pragma once

#include "CoreMinimal.h"
#include "UObject/Interface.h"
#include "AFRaceParticipantInterface.generated.h"

UINTERFACE(MinimalAPI, BlueprintType)
class UAFRaceParticipant : public UInterface
{
	GENERATED_BODY()
};

/**
 * IAFRaceParticipant - what the Race module is allowed to know about a car.
 *
 * Architecture reference: TECHNICAL_ARCHITECTURE.md section 2.
 *
 * This interface is the entire reason ApexFormulaRace does not depend on
 * ApexFormulaVehicle. Race code asks a participant for its id, its position and
 * whether it is currently controllable. It cannot reach a tyre model, an
 * aero surface or a Chaos body, because none of that is on this interface.
 *
 * Consequences that are deliberate:
 *  - Lap validation, sector timing and penalties can be unit tested against a
 *    trivial mock implementation, with no car, no track and no rendered frame.
 *  - An AI car, a player car and a future replay ghost are indistinguishable
 *    to race control.
 *
 * Status: statically inspected. requires local compilation.
 */
class APEXFORMULACORE_API IAFRaceParticipant
{
	GENERATED_BODY()

public:
	/** Stable, session-unique participant id. 1-based. INDEX_NONE if unassigned. */
	virtual int32 GetParticipantId() const = 0;

	/** Display name for this participant. Original fictional names only. */
	virtual FString GetParticipantDisplayName() const = 0;

	/** World-space location in runtime units (Unreal centimetres). */
	virtual FVector GetParticipantLocation() const = 0;

	/** World-space forward direction, normalised. */
	virtual FVector GetParticipantForward() const = 0;

	/** Ground speed in km/h. Convenience for standings and HUD. */
	virtual double GetParticipantSpeedKph() const = 0;

	/**
	 * True when this participant is currently under control and eligible to
	 * set a time. False while retired, in the pit lane under a stop penalty,
	 * or not yet released from the grid.
	 */
	virtual bool IsParticipantActive() const = 0;
};
