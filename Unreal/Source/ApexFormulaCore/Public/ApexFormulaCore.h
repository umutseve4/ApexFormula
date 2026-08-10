// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

/**
 * ApexFormulaCore module interface.
 *
 * Loading phase: PreDefault. Core must be available before any other
 * ApexFormula module initialises.
 *
 * Status: statically inspected. requires local compilation.
 */
class APEXFORMULACORE_API FApexFormulaCoreModule : public IModuleInterface
{
public:
	virtual void StartupModule() override;
	virtual void ShutdownModule() override;

	/** Convenience accessor. Returns nullptr if the module is not loaded. */
	static FApexFormulaCoreModule* GetPtr()
	{
		return FModuleManager::GetModulePtr<FApexFormulaCoreModule>(TEXT("ApexFormulaCore"));
	}
};
