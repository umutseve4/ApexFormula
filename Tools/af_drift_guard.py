#!/usr/bin/env python3
# Copyright UludagFormula. Original work. Not affiliated with any real motorsport series.
"""
af_drift_guard.py - executable guard against C++/Python rule drift (Milestone 3).

WHY THIS FILE EXISTS
--------------------
Tools/af_lap_rules_model.py is a hand-written Python transcription of:

    Unreal/Source/ApexFormulaRace/Private/AFSectorTimer.cpp
    Unreal/Source/ApexFormulaRace/Private/AFLapValidator.cpp

Its own docstring admits the weakness that decision record D-042 recorded:

    "If someone edits one .cpp and not this file, this file will keep passing
     while describing code that no longer exists. The guard against that is
     review discipline, not automation."

Review discipline is not a control. It is a hope. This file converts D-042's
mitigation from process into automation, so a one-sided edit fails CI instead
of passing silently.

WHAT THIS PROVES
----------------
Three classes of parity between the C++ and its Python mirror:

  A. ENUM PARITY   - EAFLapInvalidationReason in AFTypes.h and
                     INVALIDATION_REASONS in the model declare the same
                     members, spelled the same way, in the same order.
  B. API PARITY    - every method defined in the two .cpp translation units
                     has a snake_case counterpart on the mirroring Python
                     class, and every Python method that has no .cpp
                     counterpart is on an explicit, reviewed allowlist.
  C. RULE PARITY   - every guard clause, bound and clamp in the RULES table
                     below is present on BOTH sides. Delete it from one side
                     only and this guard fails.

Verification label: `automatically validated`.

WHAT THIS DOES NOT PROVE
------------------------
Read this before quoting the green tick anywhere.

  - It does NOT prove the C++ compiles. Nothing in this repository has ever
    been compiled. This guard reads C++ as text; it is not a compiler.
  - It does NOT prove semantic equivalence. It proves that the specific
    invariants enumerated in RULES survive on both sides, and that the
    enum and the method surface match. A logic change that keeps every
    listed token intact can still slip through. The RULES table is the
    coverage boundary, and it is deliberately explicit so that boundary is
    reviewable rather than implied.
  - It does NOT replace `af_lap_rules_model.py --self-test`. That proves the
    rules are self-consistent; this proves the two artefacts still describe
    the same rules. Both steps are required.

Deliberately standard library only, and deliberately Python 3.9 compatible,
matching every other script in Tools/.

Exit codes:
    0  no drift detected / every self-test passed
    1  drift detected / at least one self-test failed
    2  bad invocation, or a required source file is missing

Usage:
    python3 Tools/af_drift_guard.py --root .
    python3 Tools/af_drift_guard.py --root . --verbose
    python3 Tools/af_drift_guard.py --self-test
"""

import argparse
import ast
import os
import re
import sys

# ---------------------------------------------------------------------------
# Source locations, relative to the repository root
# ---------------------------------------------------------------------------

PATH_TYPES_H = os.path.join(
    "Unreal", "Source", "ApexFormulaCore", "Public", "AFTypes.h"
)
PATH_SECTOR_CPP = os.path.join(
    "Unreal", "Source", "ApexFormulaRace", "Private", "AFSectorTimer.cpp"
)
PATH_VALIDATOR_CPP = os.path.join(
    "Unreal", "Source", "ApexFormulaRace", "Private", "AFLapValidator.cpp"
)
PATH_MODEL_PY = os.path.join("Tools", "af_lap_rules_model.py")

REQUIRED_SOURCES = (
    PATH_TYPES_H,
    PATH_SECTOR_CPP,
    PATH_VALIDATOR_CPP,
    PATH_MODEL_PY,
)

ENUM_NAME = "EAFLapInvalidationReason"
MODEL_ENUM_TUPLE = "INVALIDATION_REASONS"

# C++ class -> Python class in the mirror.
CLASS_PAIRS = (
    ("UAFSectorTimer", "SectorTimer", PATH_SECTOR_CPP),
    ("UAFLapValidator", "LapValidator", PATH_VALIDATOR_CPP),
)

# Python methods with no .cpp counterpart because the C++ declares them inline
# in the header. Listed explicitly so a NEW unmatched Python method is drift,
# not noise.
PYTHON_ONLY_ALLOWLIST = {
    "SectorTimer": frozenset(
        {"__init__", "is_lap_open", "get_splits", "get_sector_count"}
    ),
    "LapValidator": frozenset(
        {
            "__init__",
            "is_lap_open",
            "get_current_invalidation_reason",
            "get_passed_checkpoint_count",
            "get_expected_checkpoint_order",
        }
    ),
}

# ---------------------------------------------------------------------------
# The rule table - the coverage boundary of check C
#
# (rule_id, description, cpp_path, cpp_pattern, py_class, py_pattern)
#
# Both patterns must match. One-sided presence is drift.
# ---------------------------------------------------------------------------

RULES = (
    (
        "R-01",
        "a sector count below one is rejected",
        PATH_SECTOR_CPP,
        r"InSectorCount\s*<\s*1",
        "SectorTimer",
        r"in_sector_count\s*<\s*1",
    ),
    (
        "R-02",
        "begin lap is ignored before configure",
        PATH_SECTOR_CPP,
        r"SectorCount\s*<\s*1",
        "SectorTimer",
        r"self\.sector_count\s*<\s*1",
    ),
    (
        "R-03",
        "no boundary is accepted once every sector is closed",
        PATH_SECTOR_CPP,
        r"Splits\.Num\(\)\s*>=\s*SectorCount",
        "SectorTimer",
        r"len\(self\.splits\)\s*>=\s*self\.sector_count",
    ),
    (
        "R-04",
        "sector boundary time must strictly advance",
        PATH_SECTOR_CPP,
        r"!\(\s*SessionTime\s*>\s*CurrentSectorEnterTime\s*\)",
        "SectorTimer",
        r"not\s+session_time\s*>\s*self\.current_sector_enter_time",
    ),
    (
        "R-05",
        "the lap closes after the final sector, requiring an explicit begin lap",
        PATH_SECTOR_CPP,
        r"bLapOpen\s*=\s*false\s*;",
        "SectorTimer",
        r"self\.lap_open\s*=\s*False",
    ),
    (
        "R-06",
        "lap time is the sum of the sector durations",
        PATH_SECTOR_CPP,
        r"\+=\s*Split\.DurationSeconds",
        "SectorTimer",
        r"\+=\s*split\.duration_seconds",
    ),
    (
        "R-07",
        "a checkpoint order shorter than two entries is rejected",
        PATH_VALIDATOR_CPP,
        r"InExpectedCheckpointOrder\.Num\(\)\s*<\s*2",
        "LapValidator",
        r"len\(in_expected_checkpoint_order\)\s*<\s*2",
    ),
    (
        "R-08",
        "the next expected checkpoint index starts at one, not zero",
        PATH_VALIDATOR_CPP,
        r"NextExpectedIndex\s*=\s*1\s*;",
        "LapValidator",
        r"self\.next_expected_index\s*=\s*1",
    ),
    (
        "R-09",
        "the first invalidation cause wins",
        PATH_VALIDATOR_CPP,
        r"CurrentReason\s*==\s*" + ENUM_NAME + r"::NotInvalidated",
        "LapValidator",
        r"self\.current_reason\s*==\s*NOT_INVALIDATED",
    ),
    (
        "R-10",
        "invalidate cannot clear an existing invalidation",
        PATH_VALIDATOR_CPP,
        r"\bReason\s*==\s*" + ENUM_NAME + r"::NotInvalidated",
        "LapValidator",
        r"\breason\s*==\s*NOT_INVALIDATED",
    ),
    (
        "R-11",
        "lap completion time must strictly advance past the lap start",
        PATH_VALIDATOR_CPP,
        r"!\(\s*SessionTime\s*>\s*CurrentLapStartTime\s*\)",
        "LapValidator",
        r"not\s+session_time\s*>\s*self\.current_lap_start_time",
    ),
    (
        "R-12",
        "lap time is clamped at zero and never reported negative",
        PATH_VALIDATOR_CPP,
        r"FMath::Max\(\s*0\.0\s*,",
        "LapValidator",
        r"\bmax\(\s*0\.0\s*,",
    ),
    (
        "R-13",
        "a lap is only complete when every checkpoint was consumed",
        PATH_VALIDATOR_CPP,
        r"NextExpectedIndex\s*>=\s*ExpectedCheckpointOrder\.Num\(\)",
        "LapValidator",
        r"self\.next_expected_index\s*>=\s*len\(",
    ),
    (
        "R-14",
        "validity requires a strictly positive lap time",
        PATH_VALIDATOR_CPP,
        r"LapTimeSeconds\s*>\s*0\.0",
        "LapValidator",
        r"lap_time_seconds\s*>\s*0\.0",
    ),
    (
        "R-15",
        "a checkpoint outside the configured circuit invalidates the lap",
        PATH_VALIDATOR_CPP,
        r"KnownCheckpoints\.Contains\(\s*CheckpointId\s*\)",
        "LapValidator",
        r"checkpoint_id\s+not\s+in\s+self\.known_checkpoints",
    ),
    (
        "R-16",
        "a duplicate checkpoint in the configured order is rejected",
        PATH_VALIDATOR_CPP,
        r"bAlreadySeen",
        "LapValidator",
        r"checkpoint_id\s+in\s+unique",
    ),
)


# ---------------------------------------------------------------------------
# Extraction helpers - all operate on TEXT, so the self-test can feed them
# mutated sources without touching the repository.
# ---------------------------------------------------------------------------


def to_snake_case(pascal_name):
    """RecordSectorBoundary -> record_sector_boundary."""
    stage = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", pascal_name)
    stage = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", stage)
    return stage.lower()


def extract_cpp_enum_members(header_text, enum_name):
    """Ordered member names of `enum class <enum_name>` in a UE header."""
    pattern = r"enum\s+class\s+" + re.escape(enum_name) + r"\s*:\s*\w+\s*\{(.*?)\}\s*;"
    match = re.search(pattern, header_text, re.DOTALL)
    if match is None:
        return None

    members = []
    for raw_line in match.group(1).splitlines():
        line = raw_line.strip()
        if not line or line.startswith("//") or line.startswith("/*"):
            continue
        if line.startswith("*"):
            continue
        member = re.match(r"([A-Za-z_]\w*)", line)
        if member is not None:
            members.append(member.group(1))
    return members


def extract_python_string_tuple(model_text, tuple_name):
    """Resolve `NAME = (CONST_A, CONST_B, ...)` to the string values, in order.

    Uses ast, never exec, so a broken model file cannot execute here.
    """
    tree = ast.parse(model_text)
    constants = {}
    target = None

    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for assign_target in node.targets:
            if not isinstance(assign_target, ast.Name):
                continue
            if isinstance(node.value, ast.Constant) and isinstance(
                node.value.value, str
            ):
                constants[assign_target.id] = node.value.value
            elif assign_target.id == tuple_name and isinstance(
                node.value, (ast.Tuple, ast.List)
            ):
                target = node.value

    if target is None:
        return None

    values = []
    for element in target.elts:
        if isinstance(element, ast.Name):
            if element.id not in constants:
                return None
            values.append(constants[element.id])
        elif isinstance(element, ast.Constant) and isinstance(element.value, str):
            values.append(element.value)
        else:
            return None
    return values


def extract_cpp_methods(cpp_text, cpp_class):
    """Method names defined as `<Ret> <Class>::<Method>(` in a translation unit."""
    pattern = re.escape(cpp_class) + r"::([A-Za-z_]\w*)\s*\("
    return sorted(set(re.findall(pattern, cpp_text)))


def extract_python_class(model_text, class_name):
    """Return (method_names, class_source_text) for a class in the model."""
    tree = ast.parse(model_text)
    lines = model_text.splitlines()
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            methods = sorted(
                child.name
                for child in node.body
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
            )
            end = getattr(node, "end_lineno", None) or len(lines)
            body = "\n".join(lines[node.lineno - 1 : end])
            return methods, body
    return None, None


# ---------------------------------------------------------------------------
# The three checks - each returns a list of drift findings (strings)
# ---------------------------------------------------------------------------


def check_enum_parity(header_text, model_text, report):
    findings = []
    cpp_members = extract_cpp_enum_members(header_text, ENUM_NAME)
    if cpp_members is None:
        findings.append(
            "A: could not locate `enum class %s` in AFTypes.h" % ENUM_NAME
        )
        return findings

    py_members = extract_python_string_tuple(model_text, MODEL_ENUM_TUPLE)
    if py_members is None:
        findings.append(
            "A: could not resolve `%s` in the model" % MODEL_ENUM_TUPLE
        )
        return findings

    if cpp_members != py_members:
        findings.append(
            "A: %s drifted.\n        C++    : %s\n        Python : %s"
            % (ENUM_NAME, cpp_members, py_members)
        )
    else:
        report("  OK  A  enum parity: %d members, same order" % len(cpp_members))
    return findings


def check_api_parity(cpp_texts, model_text, report):
    findings = []
    for cpp_class, py_class, cpp_path in CLASS_PAIRS:
        cpp_methods = extract_cpp_methods(cpp_texts[cpp_path], cpp_class)
        py_methods, _ = extract_python_class(model_text, py_class)

        if py_methods is None:
            findings.append("B: class %s is missing from the model" % py_class)
            continue
        if not cpp_methods:
            findings.append(
                "B: no %s:: method definitions found in %s" % (cpp_class, cpp_path)
            )
            continue

        expected = [to_snake_case(name) for name in cpp_methods]
        missing = [name for name in expected if name not in py_methods]
        if missing:
            findings.append(
                "B: %s defines %s in C++ with no counterpart on %s"
                % (cpp_class, missing, py_class)
            )

        allowed = PYTHON_ONLY_ALLOWLIST.get(py_class, frozenset())
        unmatched = [
            name
            for name in py_methods
            if name not in expected and name not in allowed
        ]
        if unmatched:
            findings.append(
                "B: %s defines %s with no %s:: counterpart and no allowlist entry"
                % (py_class, unmatched, cpp_class)
            )

        if not missing and not unmatched:
            report(
                "  OK  B  api parity: %s <-> %s, %d mapped methods"
                % (cpp_class, py_class, len(expected))
            )
    return findings


def check_rule_parity(cpp_texts, model_text, report):
    findings = []
    bodies = {}
    for _, py_class, _ in CLASS_PAIRS:
        _, body = extract_python_class(model_text, py_class)
        bodies[py_class] = body

    seen = set()
    for rule_id, description, cpp_path, cpp_pattern, py_class, py_pattern in RULES:
        if rule_id in seen:
            raise AssertionError("duplicate rule id in RULES: %s" % rule_id)
        seen.add(rule_id)

        body = bodies.get(py_class)
        if body is None:
            findings.append(
                "C: %s - Python class %s is missing" % (rule_id, py_class)
            )
            continue

        in_cpp = re.search(cpp_pattern, cpp_texts[cpp_path]) is not None
        in_py = re.search(py_pattern, body) is not None

        if in_cpp and in_py:
            report("  OK  C  %s  %s" % (rule_id, description))
        elif in_cpp and not in_py:
            findings.append(
                "C: %s - %s\n        present in C++, ABSENT from %s"
                % (rule_id, description, py_class)
            )
        elif in_py and not in_cpp:
            findings.append(
                "C: %s - %s\n        present in %s, ABSENT from C++ (%s)"
                % (rule_id, description, py_class, os.path.basename(cpp_path))
            )
        else:
            findings.append(
                "C: %s - %s\n        ABSENT from BOTH sides; the rule was dropped"
                % (rule_id, description)
            )
    return findings


def run_all_checks(header_text, cpp_texts, model_text, report):
    findings = []
    findings.extend(check_enum_parity(header_text, model_text, report))
    findings.extend(check_api_parity(cpp_texts, model_text, report))
    findings.extend(check_rule_parity(cpp_texts, model_text, report))
    return findings


# ---------------------------------------------------------------------------
# Self-test - proves the guard DETECTS drift, not merely that it passes today
# ---------------------------------------------------------------------------

FIXTURE_HEADER = """
UENUM(BlueprintType)
enum class EAFLapInvalidationReason : uint8
{
	NotInvalidated      UMETA(DisplayName = "Not Invalidated"),
	/** comment line */
	TrackLimits         UMETA(DisplayName = "Track Limits"),
	MissedCheckpoint    UMETA(DisplayName = "Missed Checkpoint"),
	WrongDirection      UMETA(DisplayName = "Wrong Direction"),
	Collision           UMETA(DisplayName = "Collision"),
	VehicleReset        UMETA(DisplayName = "Vehicle Reset"),
	PitLane             UMETA(DisplayName = "Pit Lane")
};
"""

FIXTURE_SECTOR_CPP = """
bool UAFSectorTimer::Configure(const int32 InSectorCount)
{
	if (InSectorCount < 1) { return false; }
	SectorCount = InSectorCount;
	ResetLap();
	return true;
}
void UAFSectorTimer::BeginLap(const double SessionTime)
{
	if (SectorCount < 1) { return; }
	bLapOpen = true;
}
bool UAFSectorTimer::RecordSectorBoundary(const double SessionTime)
{
	if (Splits.Num() >= SectorCount) { return false; }
	if (!(SessionTime > CurrentSectorEnterTime)) { return false; }
	if (Splits.Num() >= SectorCount) { bLapOpen = false; }
	return true;
}
bool UAFSectorTimer::IsLapComplete() const { return true; }
double UAFSectorTimer::GetLapTimeSeconds() const
{
	double Total = 0.0;
	Total += Split.DurationSeconds;
	return Total;
}
void UAFSectorTimer::ResetLap() { bLapOpen = false; }
"""

FIXTURE_VALIDATOR_CPP = """
bool UAFLapValidator::Configure(const TArray<FName>& InExpectedCheckpointOrder)
{
	if (InExpectedCheckpointOrder.Num() < 2) { return false; }
	bool bAlreadySeen = false;
	return true;
}
void UAFLapValidator::BeginLap(const int32 InLapIndex, const double SessionTime)
{
	NextExpectedIndex = 1;
}
bool UAFLapValidator::NotifyCheckpointPassed(const FName CheckpointId, const double SessionTime)
{
	if (!KnownCheckpoints.Contains(CheckpointId)) { return false; }
	return true;
}
void UAFLapValidator::InvalidateLap(const EAFLapInvalidationReason Reason)
{
	if (Reason == EAFLapInvalidationReason::NotInvalidated) { return; }
	if (CurrentReason == EAFLapInvalidationReason::NotInvalidated) { CurrentReason = Reason; }
}
FAFLapResult UAFLapValidator::CompleteLap(const double SessionTime, bool& bOutHasResult)
{
	const bool bAll = (NextExpectedIndex >= ExpectedCheckpointOrder.Num());
	if (!(SessionTime > CurrentLapStartTime)) { }
	Result.LapTimeSeconds = FMath::Max(0.0, SessionTime - CurrentLapStartTime);
	Result.bValid = bAll && Result.LapTimeSeconds > 0.0;
	return Result;
}
void UAFLapValidator::ResetLap() { NextExpectedIndex = 1; }
"""

FIXTURE_MODEL_PY = '''
NOT_INVALIDATED = "NotInvalidated"
TRACK_LIMITS = "TrackLimits"
MISSED_CHECKPOINT = "MissedCheckpoint"
WRONG_DIRECTION = "WrongDirection"
COLLISION = "Collision"
VEHICLE_RESET = "VehicleReset"
PIT_LANE = "PitLane"

INVALIDATION_REASONS = (
    NOT_INVALIDATED,
    TRACK_LIMITS,
    MISSED_CHECKPOINT,
    WRONG_DIRECTION,
    COLLISION,
    VEHICLE_RESET,
    PIT_LANE,
)


class SectorTimer(object):
    def __init__(self):
        self.sector_count = 0

    def configure(self, in_sector_count):
        if in_sector_count < 1:
            return False
        return True

    def begin_lap(self, session_time):
        if self.sector_count < 1:
            return
        self.lap_open = True

    def record_sector_boundary(self, session_time):
        if len(self.splits) >= self.sector_count:
            return False
        if not session_time > self.current_sector_enter_time:
            return False
        if len(self.splits) >= self.sector_count:
            self.lap_open = False
        return True

    def is_lap_open(self):
        return self.lap_open

    def is_lap_complete(self):
        return True

    def get_splits(self):
        return []

    def get_lap_time_seconds(self):
        total = 0.0
        total += split.duration_seconds
        return total

    def get_sector_count(self):
        return self.sector_count

    def reset_lap(self):
        self.lap_open = False


class LapValidator(object):
    def __init__(self):
        self.next_expected_index = 1

    def configure(self, in_expected_checkpoint_order):
        if len(in_expected_checkpoint_order) < 2:
            return False
        if checkpoint_id in unique:
            return False
        return True

    def begin_lap(self, in_lap_index, session_time):
        self.next_expected_index = 1

    def notify_checkpoint_passed(self, checkpoint_id, session_time):
        if checkpoint_id not in self.known_checkpoints:
            return False
        return True

    def invalidate_lap(self, reason):
        if reason == NOT_INVALIDATED:
            return
        if self.current_reason == NOT_INVALIDATED:
            self.current_reason = reason

    def complete_lap(self, session_time):
        all_checkpoints_passed = self.next_expected_index >= len(self.order)
        if not session_time > self.current_lap_start_time:
            pass
        result.lap_time_seconds = max(0.0, session_time - self.current_lap_start_time)
        result.valid = all_checkpoints_passed and result.lap_time_seconds > 0.0
        return result, True

    def is_lap_open(self):
        return self.lap_open

    def get_current_invalidation_reason(self):
        return self.current_reason

    def get_passed_checkpoint_count(self):
        return self.next_expected_index - 1

    def get_expected_checkpoint_order(self):
        return []

    def reset_lap(self):
        self.next_expected_index = 1
'''


class SelfTest(object):
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.passed = 0
        self.failures = []
        self.case_names = []

    def check(self, name, condition, detail=""):
        if name in self.case_names:
            raise AssertionError("duplicate self-test case name: %s" % name)
        self.case_names.append(name)
        if condition:
            self.passed += 1
            if self.verbose:
                print("  PASS  %s" % name)
        else:
            self.failures.append((name, detail))
            print("  FAIL  %s%s" % (name, ("  -- " + detail) if detail else ""))

    # -- helpers -----------------------------------------------------------

    @staticmethod
    def _silent(_message):
        return None

    def _findings(self, header=None, sector=None, validator=None, model=None):
        cpp_texts = {
            PATH_SECTOR_CPP: FIXTURE_SECTOR_CPP if sector is None else sector,
            PATH_VALIDATOR_CPP: (
                FIXTURE_VALIDATOR_CPP if validator is None else validator
            ),
        }
        return run_all_checks(
            FIXTURE_HEADER if header is None else header,
            cpp_texts,
            FIXTURE_MODEL_PY if model is None else model,
            self._silent,
        )

    # -- extraction --------------------------------------------------------

    def test_snake_case(self):
        cases = (
            ("Configure", "configure"),
            ("BeginLap", "begin_lap"),
            ("RecordSectorBoundary", "record_sector_boundary"),
            ("IsLapComplete", "is_lap_complete"),
            ("GetLapTimeSeconds", "get_lap_time_seconds"),
            ("NotifyCheckpointPassed", "notify_checkpoint_passed"),
        )
        for pascal, expected in cases:
            self.check(
                "snake_case maps %s to %s" % (pascal, expected),
                to_snake_case(pascal) == expected,
                "got %s" % to_snake_case(pascal),
            )

    def test_enum_extraction(self):
        members = extract_cpp_enum_members(FIXTURE_HEADER, ENUM_NAME)
        self.check(
            "the C++ enum extractor finds all seven members in order",
            members
            == [
                "NotInvalidated",
                "TrackLimits",
                "MissedCheckpoint",
                "WrongDirection",
                "Collision",
                "VehicleReset",
                "PitLane",
            ],
            "got %r" % members,
        )
        self.check(
            "the C++ enum extractor skips comment lines",
            members is not None and "comment" not in " ".join(members),
        )
        self.check(
            "the C++ enum extractor returns None for an absent enum",
            extract_cpp_enum_members(FIXTURE_HEADER, "EAFNoSuchEnum") is None,
        )
        values = extract_python_string_tuple(FIXTURE_MODEL_PY, MODEL_ENUM_TUPLE)
        self.check(
            "the Python tuple extractor resolves constants to their values",
            values == members,
            "got %r" % values,
        )
        self.check(
            "the Python tuple extractor returns None for an absent tuple",
            extract_python_string_tuple(FIXTURE_MODEL_PY, "NO_SUCH_TUPLE") is None,
        )

    def test_method_extraction(self):
        methods = extract_cpp_methods(FIXTURE_SECTOR_CPP, "UAFSectorTimer")
        self.check(
            "the C++ method extractor finds the sector timer definitions",
            methods
            == [
                "BeginLap",
                "Configure",
                "GetLapTimeSeconds",
                "IsLapComplete",
                "RecordSectorBoundary",
                "ResetLap",
            ],
            "got %r" % methods,
        )
        py_methods, body = extract_python_class(FIXTURE_MODEL_PY, "SectorTimer")
        self.check(
            "the Python class extractor finds the mirror methods",
            py_methods is not None and "record_sector_boundary" in py_methods,
        )
        self.check(
            "the Python class extractor returns only that class's body",
            body is not None
            and "class SectorTimer" in body
            and "class LapValidator" not in body,
        )
        self.check(
            "the Python class extractor returns None for an absent class",
            extract_python_class(FIXTURE_MODEL_PY, "NoSuchClass")[0] is None,
        )

    # -- the baseline must be clean ----------------------------------------

    def test_clean_fixture_reports_no_drift(self):
        findings = self._findings()
        self.check(
            "the aligned fixture pair reports no drift",
            findings == [],
            "got %r" % findings,
        )

    # -- and every mutation must be caught ---------------------------------

    def test_detects_enum_reorder(self):
        mutated = FIXTURE_MODEL_PY.replace(
            "    TRACK_LIMITS,\n    MISSED_CHECKPOINT,",
            "    MISSED_CHECKPOINT,\n    TRACK_LIMITS,",
        )
        findings = self._findings(model=mutated)
        self.check(
            "reordering the Python enum tuple is detected",
            any(f.startswith("A:") for f in findings),
            "got %r" % findings,
        )

    def test_detects_enum_member_added_to_cpp_only(self):
        mutated = FIXTURE_HEADER.replace(
            '\tPitLane             UMETA(DisplayName = "Pit Lane")',
            '\tPitLane             UMETA(DisplayName = "Pit Lane"),\n'
            '\tJumpStart           UMETA(DisplayName = "Jump Start")',
        )
        findings = self._findings(header=mutated)
        self.check(
            "adding an enum member to C++ only is detected",
            any(f.startswith("A:") for f in findings),
            "got %r" % findings,
        )

    def test_detects_enum_rename(self):
        mutated = FIXTURE_MODEL_PY.replace(
            'TRACK_LIMITS = "TrackLimits"', 'TRACK_LIMITS = "TrackLimit"'
        )
        findings = self._findings(model=mutated)
        self.check(
            "renaming a single enum member on one side is detected",
            any(f.startswith("A:") for f in findings),
            "got %r" % findings,
        )

    def test_detects_new_cpp_method(self):
        mutated = FIXTURE_SECTOR_CPP + (
            "\nbool UAFSectorTimer::AbortLap(const double SessionTime) { return true; }\n"
        )
        findings = self._findings(sector=mutated)
        self.check(
            "a new C++ method with no Python counterpart is detected",
            any(f.startswith("B:") for f in findings),
            "got %r" % findings,
        )

    def test_detects_new_python_method(self):
        mutated = FIXTURE_MODEL_PY.replace(
            "    def is_lap_open(self):\n        return self.lap_open\n\n"
            "    def is_lap_complete(self):",
            "    def abort_lap(self):\n        return True\n\n"
            "    def is_lap_open(self):\n        return self.lap_open\n\n"
            "    def is_lap_complete(self):",
            1,
        )
        findings = self._findings(model=mutated)
        self.check(
            "a new Python method with no C++ counterpart and no allowlist entry is detected",
            any(f.startswith("B:") for f in findings),
            "got %r" % findings,
        )

    def test_detects_removed_python_class(self):
        mutated = FIXTURE_MODEL_PY.replace("class LapValidator(object):", "class Renamed(object):")
        findings = self._findings(model=mutated)
        self.check(
            "renaming a mirrored Python class is detected",
            any(f.startswith("B:") for f in findings),
            "got %r" % findings,
        )

    def test_detects_dropped_rule_python_side(self):
        mutated = FIXTURE_MODEL_PY.replace(
            "        if not session_time > self.current_sector_enter_time:\n"
            "            return False\n",
            "",
        )
        findings = self._findings(model=mutated)
        self.check(
            "dropping the strict sector time guard from Python only is detected",
            any(f.startswith("C: R-04") for f in findings),
            "got %r" % findings,
        )

    def test_detects_dropped_rule_cpp_side(self):
        mutated = FIXTURE_VALIDATOR_CPP.replace(
            "\tResult.LapTimeSeconds = FMath::Max(0.0, SessionTime - CurrentLapStartTime);",
            "\tResult.LapTimeSeconds = SessionTime - CurrentLapStartTime;",
        )
        findings = self._findings(validator=mutated)
        self.check(
            "dropping the negative-lap-time clamp from C++ only is detected",
            any(f.startswith("C: R-12") for f in findings),
            "got %r" % findings,
        )

    def test_detects_relaxed_bound(self):
        mutated = FIXTURE_VALIDATOR_CPP.replace(
            "InExpectedCheckpointOrder.Num() < 2", "InExpectedCheckpointOrder.Num() < 1"
        )
        findings = self._findings(validator=mutated)
        self.check(
            "relaxing the minimum checkpoint count on the C++ side is detected",
            any(f.startswith("C: R-07") for f in findings),
            "got %r" % findings,
        )

    def test_detects_index_base_change(self):
        mutated = FIXTURE_MODEL_PY.replace(
            "        self.next_expected_index = 1", "        self.next_expected_index = 0"
        )
        findings = self._findings(model=mutated)
        self.check(
            "changing the checkpoint index base on the Python side is detected",
            any(f.startswith("C: R-08") for f in findings),
            "got %r" % findings,
        )

    def test_detects_first_cause_wins_removal(self):
        mutated = FIXTURE_VALIDATOR_CPP.replace(
            "\tif (CurrentReason == EAFLapInvalidationReason::NotInvalidated) { CurrentReason = Reason; }",
            "\tCurrentReason = Reason;",
        )
        findings = self._findings(validator=mutated)
        self.check(
            "removing first-cause-wins from C++ only is detected",
            any(f.startswith("C: R-09") for f in findings),
            "got %r" % findings,
        )

    def test_rule_ids_are_unique_and_paths_are_known(self):
        ids = [rule[0] for rule in RULES]
        self.check("every rule id is unique", len(ids) == len(set(ids)))
        self.check(
            "every rule targets a known C++ translation unit",
            all(rule[2] in (PATH_SECTOR_CPP, PATH_VALIDATOR_CPP) for rule in RULES),
        )
        self.check(
            "every rule targets a mirrored Python class",
            all(
                rule[4] in {pair[1] for pair in CLASS_PAIRS} for rule in RULES
            ),
        )
        self.check(
            "every rule pattern compiles as a regular expression",
            all(
                re.compile(rule[3]) is not None and re.compile(rule[5]) is not None
                for rule in RULES
            ),
        )

    def run(self):
        self.test_snake_case()
        self.test_enum_extraction()
        self.test_method_extraction()
        self.test_clean_fixture_reports_no_drift()
        self.test_detects_enum_reorder()
        self.test_detects_enum_member_added_to_cpp_only()
        self.test_detects_enum_rename()
        self.test_detects_new_cpp_method()
        self.test_detects_new_python_method()
        self.test_detects_removed_python_class()
        self.test_detects_dropped_rule_python_side()
        self.test_detects_dropped_rule_cpp_side()
        self.test_detects_relaxed_bound()
        self.test_detects_index_base_change()
        self.test_detects_first_cause_wins_removal()
        self.test_rule_ids_are_unique_and_paths_are_known()
        return len(self.failures) == 0


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def read_text(path):
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def run_against_repository(root, verbose):
    missing = [rel for rel in REQUIRED_SOURCES if not os.path.isfile(os.path.join(root, rel))]
    if missing:
        print("UludagFormula drift guard - CANNOT RUN")
        for rel in missing:
            print("  missing source: %s" % rel)
        return 2

    header_text = read_text(os.path.join(root, PATH_TYPES_H))
    model_text = read_text(os.path.join(root, PATH_MODEL_PY))
    cpp_texts = {
        PATH_SECTOR_CPP: read_text(os.path.join(root, PATH_SECTOR_CPP)),
        PATH_VALIDATOR_CPP: read_text(os.path.join(root, PATH_VALIDATOR_CPP)),
    }

    def report(message):
        if verbose:
            print(message)

    print("UludagFormula C++/Python drift guard")
    print("  root    : %s" % os.path.abspath(root))
    print("  python  : %d.%d.%d" % sys.version_info[:3])
    print("  rules   : %d" % len(RULES))
    print("")

    findings = run_all_checks(header_text, cpp_texts, model_text, report)

    if findings:
        print("")
        print("  DRIFT DETECTED - %d finding(s):" % len(findings))
        print("")
        for finding in findings:
            print("    %s" % finding)
        print("")
        print("DRIFT GUARD FAIL")
        print("")
        print("  The C++ and Tools/af_lap_rules_model.py no longer describe the")
        print("  same rules. Fix BOTH sides, then record the change in")
        print("  Documentation/DECISION_LOG.md. Do not silence this guard.")
        return 1

    print("")
    print("DRIFT GUARD PASS")
    print("")
    print("  Proven here : the lap enum, the mirrored method surface and the %d" % len(RULES))
    print("                invariants in RULES are present and identical on both")
    print("                sides.  Label: automatically validated.")
    print("  NOT proven  : that the C++ compiles, or that any rule outside the")
    print("                RULES table survived.  Those still carry requires")
    print("                local compilation and requires Unreal Editor")
    print("                verification.")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=(
            "Fails when Tools/af_lap_rules_model.py and the C++ it mirrors "
            "stop describing the same lap timing and lap validity rules."
        )
    )
    parser.add_argument(
        "--root",
        default=None,
        help="repository root to check (mutually exclusive with --self-test)",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run the embedded self-test suite, which proves this guard detects drift",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="print every passing check, not only failures",
    )
    args = parser.parse_args(argv)

    if args.self_test and args.root is not None:
        parser.error("--self-test and --root are mutually exclusive")

    if args.self_test:
        print("UludagFormula drift guard - self-test")
        print("  python  : %d.%d.%d" % sys.version_info[:3])
        print("")
        suite = SelfTest(verbose=args.verbose)
        ok = suite.run()
        print("")
        print("  cases passed : %d" % suite.passed)
        print("  cases failed : %d" % len(suite.failures))
        if not ok:
            print("")
            for name, detail in suite.failures:
                print("  FAILED: %s%s" % (name, ("  -- " + detail) if detail else ""))
            print("")
            print("SELF-TEST FAIL")
            return 1
        print("")
        print("SELF-TEST PASS")
        print("")
        print("  Proven here : this guard reports no drift on an aligned pair and")
        print("                DOES report drift for enum reordering, enum renaming,")
        print("                one-sided enum members, one-sided methods, renamed")
        print("                classes, dropped guards, relaxed bounds and changed")
        print("                index bases.  Label: automatically validated.")
        return 0

    if args.root is None:
        parser.print_help()
        return 2

    return run_against_repository(args.root, args.verbose)


if __name__ == "__main__":
    sys.exit(main())
