// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleInterface.h"

/**
 * ApexFormulaRace runtime module.
 *
 * Owns checkpoints, sectors, lap validation, timing, standings, session state,
 * grid, race control, penalties, pit rules and AI.
 *
 * Boundary rule: this module MUST NOT depend on ApexFormulaVehicle. It reaches
 * vehicles only through IAFRaceParticipant and IAFTelemetrySource, both of
 * which live in ApexFormulaCore.
 */
class FApexFormulaRaceModule : public IModuleInterface
{
public:
	virtual void StartupModule() override;
	virtual void ShutdownModule() override;
};
