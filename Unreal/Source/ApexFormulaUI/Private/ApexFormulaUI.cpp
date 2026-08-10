// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

#include "ApexFormulaUI.h"
#include "AFLog.h"

#define LOCTEXT_NAMESPACE "FApexFormulaUIModule"

void FApexFormulaUIModule::StartupModule()
{
	UE_LOG(LogAFUI, Log, TEXT("ApexFormulaUI module started."));
}

void FApexFormulaUIModule::ShutdownModule()
{
	UE_LOG(LogAFUI, Log, TEXT("ApexFormulaUI module shut down."));
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FApexFormulaUIModule, ApexFormulaUI)
