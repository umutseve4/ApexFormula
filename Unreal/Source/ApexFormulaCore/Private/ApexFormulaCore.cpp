// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

#include "ApexFormulaCore.h"
#include "AFLog.h"

#define LOCTEXT_NAMESPACE "FApexFormulaCoreModule"

void FApexFormulaCoreModule::StartupModule()
{
	UE_LOG(LogAFCore, Log, TEXT("ApexFormulaCore started."));
}

void FApexFormulaCoreModule::ShutdownModule()
{
	UE_LOG(LogAFCore, Log, TEXT("ApexFormulaCore shut down."));
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FApexFormulaCoreModule, ApexFormulaCore)
