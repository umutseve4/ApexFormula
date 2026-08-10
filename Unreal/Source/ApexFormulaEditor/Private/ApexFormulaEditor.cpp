// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

#include "ApexFormulaEditor.h"
#include "AFLog.h"

#define LOCTEXT_NAMESPACE "FApexFormulaEditorModule"

void FApexFormulaEditorModule::StartupModule()
{
	UE_LOG(LogAFCore, Log, TEXT("ApexFormulaEditor module started."));
}

void FApexFormulaEditorModule::ShutdownModule()
{
	UE_LOG(LogAFCore, Log, TEXT("ApexFormulaEditor module shut down."));
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FApexFormulaEditorModule, ApexFormulaEditor)
