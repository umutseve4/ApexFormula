// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

#include "UludagFormulaEditor.h"
#include "AFLog.h"

#define LOCTEXT_NAMESPACE "FUludagFormulaEditorModule"

void FUludagFormulaEditorModule::StartupModule()
{
	UE_LOG(LogAFCore, Log, TEXT("UludagFormulaEditor module started."));
}

void FUludagFormulaEditorModule::ShutdownModule()
{
	UE_LOG(LogAFCore, Log, TEXT("UludagFormulaEditor module shut down."));
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FUludagFormulaEditorModule, UludagFormulaEditor)
