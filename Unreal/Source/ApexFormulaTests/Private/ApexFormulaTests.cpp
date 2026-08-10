// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

#include "ApexFormulaTests.h"
#include "AFLog.h"

#define LOCTEXT_NAMESPACE "FApexFormulaTestsModule"

void FApexFormulaTestsModule::StartupModule()
{
	UE_LOG(LogAFCore, Log, TEXT("ApexFormulaTests module started."));
}

void FApexFormulaTestsModule::ShutdownModule()
{
	UE_LOG(LogAFCore, Log, TEXT("ApexFormulaTests module shut down."));
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FApexFormulaTestsModule, ApexFormulaTests)
