// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleInterface.h"

/**
 * ApexFormulaEditor module. Editor-only.
 *
 * Architecture reference: TECHNICAL_ARCHITECTURE.md section 2.
 *
 * Boundary rule: nothing in this module may be referenced by a runtime module.
 * It exists to validate Data Assets, enforce naming, help author tracks and run
 * audit commandlets. If a check here is needed at runtime, the check belongs in
 * ApexFormulaCore instead.
 */
class FApexFormulaEditorModule : public IModuleInterface
{
public:
	virtual void StartupModule() override;
	virtual void ShutdownModule() override;
};
