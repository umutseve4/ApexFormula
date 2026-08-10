// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

#include "ApexFormulaVehicle.h"
#include "AFLog.h"

#define LOCTEXT_NAMESPACE "FApexFormulaVehicleModule"

void FApexFormulaVehicleModule::StartupModule()
{
	UE_LOG(LogAFVehicle, Log, TEXT("ApexFormulaVehicle module started."));
}

void FApexFormulaVehicleModule::ShutdownModule()
{
	UE_LOG(LogAFVehicle, Log, TEXT("ApexFormulaVehicle module shut down."));
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FApexFormulaVehicleModule, ApexFormulaVehicle)
