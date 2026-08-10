// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

#include "ApexFormulaRace.h"
#include "AFLog.h"

#define LOCTEXT_NAMESPACE "FApexFormulaRaceModule"

void FApexFormulaRaceModule::StartupModule()
{
	UE_LOG(LogAFRace, Log, TEXT("ApexFormulaRace module started."));
}

void FApexFormulaRaceModule::ShutdownModule()
{
	UE_LOG(LogAFRace, Log, TEXT("ApexFormulaRace module shut down."));
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FApexFormulaRaceModule, ApexFormulaRace)
