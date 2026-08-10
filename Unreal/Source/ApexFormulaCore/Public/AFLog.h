// Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.

#pragma once

#include "CoreMinimal.h"
#include "Logging/LogMacros.h"

/**
 * ApexFormula logging categories.
 *
 * Architecture reference: TECHNICAL_ARCHITECTURE.md section 10.
 *
 * Rule: every rule decision that affects the player (lap invalidated, penalty
 * issued, pit stop judged) logs at Log level with participant id, session time
 * and the reason. Silent rule decisions are prohibited.
 *
 * Verbosity is configuration-driven (Config/DefaultApexFormula.ini), not
 * compile-time.
 *
 * Status: statically inspected. requires local compilation.
 */

APEXFORMULACORE_API DECLARE_LOG_CATEGORY_EXTERN(LogAFCore, Log, All);
APEXFORMULACORE_API DECLARE_LOG_CATEGORY_EXTERN(LogAFVehicle, Log, All);
APEXFORMULACORE_API DECLARE_LOG_CATEGORY_EXTERN(LogAFRace, Log, All);
APEXFORMULACORE_API DECLARE_LOG_CATEGORY_EXTERN(LogAFPipeline, Log, All);
APEXFORMULACORE_API DECLARE_LOG_CATEGORY_EXTERN(LogAFUI, Log, All);

/**
 * Helper macro for rule decisions that must never be silent.
 * ParticipantId and SessionTime are mandatory arguments by design.
 */
#define AF_LOG_RULE(Category, ParticipantId, SessionTime, Format, ...) \
	UE_LOG(Category, Log, TEXT("[participant=%d t=%.3f] ") Format, \
		(int32)(ParticipantId), (double)(SessionTime), ##__VA_ARGS__)
