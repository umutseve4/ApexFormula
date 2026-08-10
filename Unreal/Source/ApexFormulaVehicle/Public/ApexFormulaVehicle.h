// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

/**
 * ApexFormulaVehicle runtime module.
 *
 * Owns the vehicle pawn, its simulation components, setup application,
 * vehicle telemetry sources and input mapping.
 *
 * Depends on: ApexFormulaCore, and the engine vehicle plugin via
 * UAFVehicleCompatibilityLayer only.
 */
class FApexFormulaVehicleModule : public IModuleInterface
{
public:
	virtual void StartupModule() override;
	virtual void ShutdownModule() override;
};
