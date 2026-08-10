// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleInterface.h"

/**
 * ApexFormulaUI runtime module.
 *
 * Architecture reference: TECHNICAL_ARCHITECTURE.md section 2.
 *
 * Boundary rule: this module READS. View models observe telemetry and race
 * state and expose display-ready values. UI code must never mutate vehicle or
 * race state, and must never be a dependency of a simulation module.
 */
class FApexFormulaUIModule : public IModuleInterface
{
public:
	virtual void StartupModule() override;
	virtual void ShutdownModule() override;
};
