// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleInterface.h"

/**
 * ApexFormulaTests module. Developer tool, shipped in no cooked build.
 *
 * Architecture reference: TECHNICAL_ARCHITECTURE.md section 9.
 *
 * This is a leaf module. Nothing depends on it. Everything it tests must be
 * reachable without opening a level, because the section 9 principle is that
 * rules logic is testable without a car, a track or a frame.
 */
class FApexFormulaTestsModule : public IModuleInterface
{
public:
	virtual void StartupModule() override;
	virtual void ShutdownModule() override;
};
