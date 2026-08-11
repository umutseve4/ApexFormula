#!/usr/bin/env python3
# Copyright ApexFormula. Original work. Not affiliated with any real motorsport series.
"""
af_lap_rules_model.py - executable reference model of the ApexFormula lap
timing and lap validity rules (Milestone 3).

WHAT THIS IS
------------
A line-for-line Python transcription of the decision logic in:

    Unreal/Source/ApexFormulaRace/Private/AFSectorTimer.cpp
    Unreal/Source/ApexFormulaRace/Private/AFLapValidator.cpp

and the contracts declared in the matching headers. It exists because no
compiler and no Unreal Editor exist in the environment this project is
currently developed in, so the C++ automation tests for those two classes
have never been executed. The *rules* they encode can still be executed,
and this file executes them.

WHAT THIS PROVES
----------------
That the lap timing and lap validity RULES are self-consistent and behave
as the Milestone 3 acceptance criteria require:

  - laps are timed reproducibly              (criterion 1)
  - sector times sum to the lap time         (criterion 2)
  - cutting the circuit invalidates the lap  (criterion 3)
  - reset behaves deterministically          (criterion 4)

Verification label: `automatically validated`.

WHAT THIS DOES NOT PROVE
------------------------
Read this part before quoting the green tick anywhere.

  - It does NOT prove the C++ compiles. Nothing in this repository has ever
    been compiled. This is a transcription, not the shipped translation unit.
  - It does NOT prove the C++ and this model cannot drift apart. They are
    two artefacts. If someone edits one .cpp and not this file, this file
    will keep passing while describing code that no longer exists. The
    guard against that is review discipline, not automation, and pretending
    otherwise would be exactly the kind of flattery this project bans.
  - It does NOT prove anything about geometry, volumes, overlap events,
    frame rate, or how track limits feel to drive. Those need an editor and
    a human, and carry `requires Unreal Editor verification` and
    `requires playtesting`.

Deliberately standard library only, and deliberately Python 3.9 compatible,
matching every other script in Tools/.

Exit codes:
    0  every self-test passed
    1  at least one self-test failed
    2  bad invocation

Usage:
    python3 Tools/af_lap_rules_model.py --self-test
    python3 Tools/af_lap_rules_model.py --self-test --verbose
"""

import argparse
import sys

# ---------------------------------------------------------------------------
# Enum mirror - EAFLapInvalidationReason, from AFTypes.h
# ---------------------------------------------------------------------------

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


class SectorSplit(object):
    """Mirror of FAFSectorSplit."""

    __slots__ = ("sector_index", "enter_time", "exit_time", "duration_seconds")

    def __init__(self, sector_index, enter_time, exit_time):
        self.sector_index = sector_index
        self.enter_time = enter_time
        self.exit_time = exit_time
        self.duration_seconds = exit_time - enter_time

    def as_tuple(self):
        return (
            self.sector_index,
            self.enter_time,
            self.exit_time,
            self.duration_seconds,
        )


class LapResult(object):
    """Mirror of FAFLapResult."""

    __slots__ = (
        "lap_index",
        "valid",
        "invalidation_reason",
        "start_time",
        "end_time",
        "lap_time_seconds",
    )

    def __init__(self):
        self.lap_index = 0
        self.valid = False
        self.invalidation_reason = NOT_INVALIDATED
        self.start_time = 0.0
        self.end_time = 0.0
        self.lap_time_seconds = 0.0

    def as_tuple(self):
        return (
            self.lap_index,
            self.valid,
            self.invalidation_reason,
            self.start_time,
            self.end_time,
            self.lap_time_seconds,
        )


# ---------------------------------------------------------------------------
# UAFSectorTimer mirror
# ---------------------------------------------------------------------------


class SectorTimer(object):
    """Mirror of UAFSectorTimer. Pure: no world, no tick, no frame."""

    def __init__(self):
        self.sector_count = 0
        self.lap_open = False
        self.current_sector_enter_time = 0.0
        self.splits = []

    def configure(self, in_sector_count):
        if in_sector_count < 1:
            return False
        self.sector_count = in_sector_count
        self.reset_lap()
        return True

    def begin_lap(self, session_time):
        if self.sector_count < 1:
            return
        self.splits = []
        self.current_sector_enter_time = session_time
        self.lap_open = True

    def record_sector_boundary(self, session_time):
        if not self.lap_open:
            return False
        if len(self.splits) >= self.sector_count:
            return False
        # Session time must move forward. A non-advancing time would produce a
        # zero or negative sector, which is never a real result.
        if not session_time > self.current_sector_enter_time:
            return False

        self.splits.append(
            SectorSplit(len(self.splits), self.current_sector_enter_time, session_time)
        )
        self.current_sector_enter_time = session_time

        if len(self.splits) >= self.sector_count:
            # A new lap requires an explicit begin_lap so that a missed timing
            # line can never be silently absorbed into the next lap.
            self.lap_open = False
        return True

    def is_lap_open(self):
        return self.lap_open

    def is_lap_complete(self):
        return self.sector_count > 0 and len(self.splits) >= self.sector_count

    def get_splits(self):
        return list(self.splits)

    def get_lap_time_seconds(self):
        total = 0.0
        for split in self.splits:
            total += split.duration_seconds
        return total

    def get_sector_count(self):
        return self.sector_count

    def reset_lap(self):
        self.splits = []
        self.lap_open = False
        self.current_sector_enter_time = 0.0


# ---------------------------------------------------------------------------
# UAFLapValidator mirror
# ---------------------------------------------------------------------------


class LapValidator(object):
    """Mirror of UAFLapValidator. Pure, explicit inputs only."""

    def __init__(self):
        self.expected_checkpoint_order = []
        self.known_checkpoints = set()
        self.lap_open = False
        self.current_lap_index = 0
        self.current_lap_start_time = 0.0
        self.next_expected_index = 1
        self.current_reason = NOT_INVALIDATED

    def configure(self, in_expected_checkpoint_order):
        if len(in_expected_checkpoint_order) < 2:
            return False

        unique = set()
        for checkpoint_id in in_expected_checkpoint_order:
            # FName::IsNone() mirror - unset names are rejected.
            if checkpoint_id is None or checkpoint_id == "" or checkpoint_id == "None":
                return False
            if checkpoint_id in unique:
                return False
            unique.add(checkpoint_id)

        self.expected_checkpoint_order = list(in_expected_checkpoint_order)
        self.known_checkpoints = unique
        self.reset_lap()
        return True

    def begin_lap(self, in_lap_index, session_time):
        if len(self.expected_checkpoint_order) < 2:
            return
        self.current_lap_index = in_lap_index
        self.current_lap_start_time = session_time
        self.next_expected_index = 1
        self.current_reason = NOT_INVALIDATED
        self.lap_open = True

    def notify_checkpoint_passed(self, checkpoint_id, session_time):
        if not self.lap_open:
            return False

        if checkpoint_id not in self.known_checkpoints:
            self.invalidate_lap(MISSED_CHECKPOINT)
            return False

        # Every intermediate checkpoint has been passed; only the timing line
        # remains, and that arrives through complete_lap rather than here.
        if not 0 <= self.next_expected_index < len(self.expected_checkpoint_order):
            self.invalidate_lap(MISSED_CHECKPOINT)
            return False

        expected = self.expected_checkpoint_order[self.next_expected_index]
        if checkpoint_id != expected:
            self.invalidate_lap(MISSED_CHECKPOINT)
            return False

        self.next_expected_index += 1
        return True

    def invalidate_lap(self, reason):
        if reason == NOT_INVALIDATED:
            # Callers must not clear an invalidation through this entry point.
            return
        if self.current_reason == NOT_INVALIDATED:
            # First cause wins. A spin caused by a track-limit excursion is
            # reported as the excursion, not as the collision that followed.
            self.current_reason = reason

    def complete_lap(self, session_time):
        """Returns (result, has_result)."""
        result = LapResult()

        if not self.lap_open:
            return result, False

        all_checkpoints_passed = self.next_expected_index >= len(
            self.expected_checkpoint_order
        )
        if not all_checkpoints_passed:
            self.invalidate_lap(MISSED_CHECKPOINT)

        if not session_time > self.current_lap_start_time:
            self.invalidate_lap(MISSED_CHECKPOINT)

        result.lap_index = self.current_lap_index
        result.start_time = self.current_lap_start_time
        result.end_time = session_time
        result.lap_time_seconds = max(0.0, session_time - self.current_lap_start_time)
        result.invalidation_reason = self.current_reason
        result.valid = (
            self.current_reason == NOT_INVALIDATED
            and all_checkpoints_passed
            and result.lap_time_seconds > 0.0
        )

        self.lap_open = False
        return result, True

    def is_lap_open(self):
        return self.lap_open

    def get_current_invalidation_reason(self):
        return self.current_reason

    def get_passed_checkpoint_count(self):
        return self.next_expected_index - 1

    def get_expected_checkpoint_order(self):
        return list(self.expected_checkpoint_order)

    def reset_lap(self):
        self.lap_open = False
        self.current_lap_index = 0
        self.current_lap_start_time = 0.0
        self.next_expected_index = 1
        self.current_reason = NOT_INVALIDATED


# ---------------------------------------------------------------------------
# Self-test harness
# ---------------------------------------------------------------------------

# A four-checkpoint closed circuit. Index 0 is the timing line, by contract.
# Entirely invented; no real circuit is described or reproduced anywhere in
# this project (Milestone 3 acceptance criterion 5).
TEST_CIRCUIT = ["AF_CP_Line", "AF_CP_Alpha", "AF_CP_Bravo", "AF_CP_Charlie"]


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

    # -- sector timer ------------------------------------------------------

    def test_sector_timer(self):
        t = SectorTimer()
        self.check(
            "timer rejects a sector count below one",
            t.configure(0) is False and t.configure(-3) is False,
        )
        self.check("timer accepts three sectors", t.configure(3) is True)
        self.check(
            "timer starts closed and empty",
            t.is_lap_open() is False and t.get_lap_time_seconds() == 0.0,
        )

        # Criterion 2: sector times sum to the lap time.
        t.begin_lap(10.0)
        self.check("timer reports an open lap after begin_lap", t.is_lap_open() is True)
        ok1 = t.record_sector_boundary(38.5)
        ok2 = t.record_sector_boundary(70.25)
        ok3 = t.record_sector_boundary(101.75)
        self.check(
            "timer accepts three advancing boundaries", ok1 and ok2 and ok3
        )
        splits = t.get_splits()
        self.check("timer recorded exactly three splits", len(splits) == 3)
        self.check(
            "split indices are zero-based and in order",
            [s.sector_index for s in splits] == [0, 1, 2],
        )
        self.check(
            "each split duration equals exit minus enter",
            all(
                s.duration_seconds == s.exit_time - s.enter_time for s in splits
            ),
        )
        self.check(
            "each split enters where the previous one exited",
            splits[0].exit_time == splits[1].enter_time
            and splits[1].exit_time == splits[2].enter_time,
        )
        summed = sum(s.duration_seconds for s in splits)
        self.check(
            "sector times sum to the lap time (criterion 2)",
            t.get_lap_time_seconds() == summed,
            "lap=%r sum=%r" % (t.get_lap_time_seconds(), summed),
        )
        self.check(
            "lap time equals last exit minus first enter",
            abs(t.get_lap_time_seconds() - (101.75 - 10.0)) < 1e-12,
            "got %r" % t.get_lap_time_seconds(),
        )
        self.check("timer reports the lap complete", t.is_lap_complete() is True)
        self.check(
            "timer closes the lap after the final sector, requiring an explicit begin_lap",
            t.is_lap_open() is False,
        )
        self.check(
            "timer rejects a boundary after every sector is closed",
            t.record_sector_boundary(120.0) is False,
        )

        # Non-advancing time.
        t2 = SectorTimer()
        t2.configure(3)
        t2.begin_lap(5.0)
        self.check(
            "timer rejects a boundary at the sector enter time",
            t2.record_sector_boundary(5.0) is False,
        )
        self.check(
            "timer rejects a boundary before the sector enter time",
            t2.record_sector_boundary(4.0) is False,
        )
        self.check(
            "a rejected boundary records nothing", len(t2.get_splits()) == 0
        )

        # No lap open.
        t3 = SectorTimer()
        t3.configure(2)
        self.check(
            "timer rejects a boundary with no lap open",
            t3.record_sector_boundary(1.0) is False,
        )
        self.check(
            "begin_lap before configure is ignored",
            SectorTimer().record_sector_boundary(1.0) is False,
        )

        # Reset keeps configuration, clears the lap.
        t.reset_lap()
        self.check(
            "reset_lap clears splits but keeps the sector count",
            t.get_lap_time_seconds() == 0.0
            and len(t.get_splits()) == 0
            and t.get_sector_count() == 3
            and t.is_lap_open() is False,
        )

    # -- lap validator -----------------------------------------------------

    def _clean_lap(self):
        v = LapValidator()
        v.configure(TEST_CIRCUIT)
        v.begin_lap(0, 10.0)
        v.notify_checkpoint_passed("AF_CP_Alpha", 40.0)
        v.notify_checkpoint_passed("AF_CP_Bravo", 70.0)
        v.notify_checkpoint_passed("AF_CP_Charlie", 90.0)
        return v

    def test_validator_configure(self):
        v = LapValidator()
        self.check(
            "validator rejects an order with fewer than two entries",
            v.configure([]) is False and v.configure(["AF_CP_Line"]) is False,
        )
        self.check(
            "validator rejects duplicate checkpoints",
            v.configure(["AF_CP_Line", "AF_CP_Alpha", "AF_CP_Alpha"]) is False,
        )
        self.check(
            "validator rejects an unset checkpoint name",
            v.configure(["AF_CP_Line", ""]) is False
            and v.configure(["AF_CP_Line", None]) is False
            and v.configure(["AF_CP_Line", "None"]) is False,
        )
        self.check(
            "validator accepts a well-formed circuit", v.configure(TEST_CIRCUIT) is True
        )
        self.check(
            "validator reports the configured order back unchanged",
            v.get_expected_checkpoint_order() == TEST_CIRCUIT,
        )

    def test_validator_clean_lap(self):
        v = self._clean_lap()
        self.check(
            "validator counts three passed checkpoints",
            v.get_passed_checkpoint_count() == 3,
        )
        self.check(
            "a clean lap is not invalidated before the line",
            v.get_current_invalidation_reason() == NOT_INVALIDATED,
        )
        result, has = v.complete_lap(100.0)
        self.check("complete_lap returns a result", has is True)
        self.check("a clean lap is valid", result.valid is True)
        self.check(
            "a valid lap carries no invalidation reason",
            result.invalidation_reason == NOT_INVALIDATED,
        )
        self.check(
            "lap time is end minus start",
            result.lap_time_seconds == 90.0,
            "got %r" % result.lap_time_seconds,
        )
        self.check("validator closes the lap", v.is_lap_open() is False)
        _, has_again = v.complete_lap(110.0)
        self.check("completing twice yields no second result", has_again is False)

    def test_validator_cutting(self):
        # Criterion 3: cutting the circuit invalidates the lap.
        v = LapValidator()
        v.configure(TEST_CIRCUIT)
        v.begin_lap(1, 0.0)
        v.notify_checkpoint_passed("AF_CP_Alpha", 30.0)
        skipped = v.notify_checkpoint_passed("AF_CP_Charlie", 55.0)
        self.check("an out-of-order checkpoint is rejected", skipped is False)
        self.check(
            "cutting the circuit invalidates the lap (criterion 3)",
            v.get_current_invalidation_reason() == MISSED_CHECKPOINT,
        )
        result, has = v.complete_lap(80.0)
        self.check("a cut lap still produces a result", has is True)
        self.check("a cut lap is not valid", result.valid is False)
        self.check(
            "a cut lap is attributed to MissedCheckpoint",
            result.invalidation_reason == MISSED_CHECKPOINT,
        )
        self.check(
            "a cut lap still records a time, so the driver sees why it did not count",
            result.lap_time_seconds == 80.0,
            "got %r" % result.lap_time_seconds,
        )

        # Reaching the line early.
        v2 = LapValidator()
        v2.configure(TEST_CIRCUIT)
        v2.begin_lap(2, 0.0)
        v2.notify_checkpoint_passed("AF_CP_Alpha", 30.0)
        r2, _ = v2.complete_lap(60.0)
        self.check(
            "reaching the line with checkpoints outstanding invalidates the lap",
            r2.valid is False and r2.invalidation_reason == MISSED_CHECKPOINT,
        )

        # Unknown checkpoint.
        v3 = self._clean_lap()
        unknown = v3.notify_checkpoint_passed("AF_CP_NotOnThisCircuit", 95.0)
        self.check("an unknown checkpoint is rejected", unknown is False)
        self.check(
            "an unknown checkpoint invalidates the lap",
            v3.get_current_invalidation_reason() == MISSED_CHECKPOINT,
        )

        # Extra checkpoint after all were consumed.
        v4 = self._clean_lap()
        extra = v4.notify_checkpoint_passed("AF_CP_Alpha", 95.0)
        self.check(
            "a checkpoint passed after all were consumed is rejected and invalidates",
            extra is False
            and v4.get_current_invalidation_reason() == MISSED_CHECKPOINT,
        )

    def test_validator_invalidation_precedence(self):
        v = self._clean_lap()
        v.invalidate_lap(TRACK_LIMITS)
        v.invalidate_lap(COLLISION)
        v.invalidate_lap(VEHICLE_RESET)
        self.check(
            "the first invalidation cause wins",
            v.get_current_invalidation_reason() == TRACK_LIMITS,
            "got %s" % v.get_current_invalidation_reason(),
        )
        v.invalidate_lap(NOT_INVALIDATED)
        self.check(
            "invalidate_lap cannot clear an existing invalidation",
            v.get_current_invalidation_reason() == TRACK_LIMITS,
        )
        result, _ = v.complete_lap(100.0)
        self.check(
            "a track-limits lap is invalid and attributed to TrackLimits",
            result.valid is False and result.invalidation_reason == TRACK_LIMITS,
        )

        # Every reason is a legitimate, distinguishable invalidation.
        for reason in INVALIDATION_REASONS:
            if reason == NOT_INVALIDATED:
                continue
            probe = self._clean_lap()
            probe.invalidate_lap(reason)
            r, _ = probe.complete_lap(100.0)
            self.check(
                "invalidation reason %s is carried through to the result" % reason,
                r.valid is False and r.invalidation_reason == reason,
            )

    def test_validator_time_guards(self):
        v = self._clean_lap()
        result, has = v.complete_lap(10.0)  # equal to the start time
        self.check(
            "a lap that does not advance in time is invalid",
            has is True and result.valid is False,
        )
        self.check(
            "a non-advancing lap time is clamped to zero, never negative",
            result.lap_time_seconds == 0.0,
            "got %r" % result.lap_time_seconds,
        )

        v2 = self._clean_lap()
        r2, _ = v2.complete_lap(5.0)  # before the start time
        self.check(
            "a lap ending before it started is invalid and clamped to zero",
            r2.valid is False and r2.lap_time_seconds == 0.0,
        )

        v3 = LapValidator()
        v3.configure(TEST_CIRCUIT)
        _, has3 = v3.complete_lap(10.0)
        self.check("completing with no lap open yields no result", has3 is False)
        self.check(
            "a checkpoint with no lap open is ignored",
            v3.notify_checkpoint_passed("AF_CP_Alpha", 1.0) is False,
        )

    # -- determinism -------------------------------------------------------

    def _drive(self, times):
        """Runs one identical scripted lap and returns a comparable snapshot."""
        timer = SectorTimer()
        timer.configure(3)
        validator = LapValidator()
        validator.configure(TEST_CIRCUIT)

        timer.begin_lap(times[0])
        validator.begin_lap(7, times[0])
        for index, checkpoint in enumerate(TEST_CIRCUIT[1:]):
            timer.record_sector_boundary(times[index + 1])
            validator.notify_checkpoint_passed(checkpoint, times[index + 1])
        result, has = validator.complete_lap(times[-1])
        return (
            tuple(s.as_tuple() for s in timer.get_splits()),
            timer.get_lap_time_seconds(),
            result.as_tuple(),
            has,
        )

    def test_determinism_and_reset(self):
        # Criterion 1 and 4: reproducible timing, deterministic reset.
        times = [12.5, 41.0, 73.25, 104.5]
        first = self._drive(times)
        second = self._drive(times)
        third = self._drive(times)
        self.check(
            "identical input produces identical output, three times over (criteria 1 and 4)",
            first == second == third,
        )

        # Reuse after reset must equal a fresh instance.
        timer = SectorTimer()
        timer.configure(3)
        timer.begin_lap(0.0)
        timer.record_sector_boundary(10.0)
        timer.reset_lap()
        timer.begin_lap(times[0])
        for t in times[1:]:
            timer.record_sector_boundary(t)

        fresh = SectorTimer()
        fresh.configure(3)
        fresh.begin_lap(times[0])
        for t in times[1:]:
            fresh.record_sector_boundary(t)

        self.check(
            "a reset timer behaves exactly like a fresh one",
            [s.as_tuple() for s in timer.get_splits()]
            == [s.as_tuple() for s in fresh.get_splits()],
        )

        validator = LapValidator()
        validator.configure(TEST_CIRCUIT)
        validator.begin_lap(0, 0.0)
        validator.invalidate_lap(COLLISION)
        validator.reset_lap()
        self.check(
            "reset_lap clears the invalidation reason",
            validator.get_current_invalidation_reason() == NOT_INVALIDATED
            and validator.is_lap_open() is False,
        )
        self.check(
            "reset_lap keeps the configured circuit",
            validator.get_expected_checkpoint_order() == TEST_CIRCUIT,
        )

        # A second lap on the same objects must not inherit the first.
        v = self._clean_lap()
        v.invalidate_lap(TRACK_LIMITS)
        v.complete_lap(100.0)
        v.begin_lap(1, 100.0)
        v.notify_checkpoint_passed("AF_CP_Alpha", 130.0)
        v.notify_checkpoint_passed("AF_CP_Bravo", 160.0)
        v.notify_checkpoint_passed("AF_CP_Charlie", 180.0)
        second_result, _ = v.complete_lap(190.0)
        self.check(
            "an invalid lap does not contaminate the lap that follows it",
            second_result.valid is True
            and second_result.invalidation_reason == NOT_INVALIDATED
            and second_result.lap_index == 1,
        )

    # -- cross-check -------------------------------------------------------

    def test_timer_validator_agreement(self):
        """The two classes are independent; their arithmetic must still agree."""
        times = [30.0, 61.5, 92.25, 121.0]
        timer = SectorTimer()
        timer.configure(3)
        validator = LapValidator()
        validator.configure(TEST_CIRCUIT)

        timer.begin_lap(times[0])
        validator.begin_lap(0, times[0])
        for index, checkpoint in enumerate(TEST_CIRCUIT[1:]):
            timer.record_sector_boundary(times[index + 1])
            validator.notify_checkpoint_passed(checkpoint, times[index + 1])
        result, _ = validator.complete_lap(times[-1])

        self.check(
            "the summed sector time equals the validator's lap time (criterion 2)",
            abs(timer.get_lap_time_seconds() - result.lap_time_seconds) < 1e-12,
            "timer=%r validator=%r"
            % (timer.get_lap_time_seconds(), result.lap_time_seconds),
        )
        self.check(
            "the cross-checked lap is valid and complete",
            result.valid is True and timer.is_lap_complete() is True,
        )

    def test_originality_guard(self):
        """Milestone 3 criterion 5: no real-world circuit is reproduced."""
        for name in TEST_CIRCUIT:
            self.check(
                "test circuit checkpoint '%s' uses the neutral AF_CP_ prefix" % name,
                name.startswith("AF_CP_"),
            )

    # -- driver ------------------------------------------------------------

    def run(self):
        self.test_sector_timer()
        self.test_validator_configure()
        self.test_validator_clean_lap()
        self.test_validator_cutting()
        self.test_validator_invalidation_precedence()
        self.test_validator_time_guards()
        self.test_determinism_and_reset()
        self.test_timer_validator_agreement()
        self.test_originality_guard()
        return len(self.failures) == 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=(
            "Executable reference model of the ApexFormula lap timing and lap "
            "validity rules. Transcribes AFSectorTimer.cpp and "
            "AFLapValidator.cpp; does not compile or replace them."
        )
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run the embedded self-test suite and report pass/fail",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="print every passing case, not only failures",
    )
    args = parser.parse_args(argv)

    if not args.self_test:
        parser.print_help()
        return 2

    print("ApexFormula lap rules reference model - self-test")
    print("  mirrors : AFSectorTimer.cpp, AFLapValidator.cpp")
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
    print("  Proven here : lap timing and lap validity RULES are self-consistent")
    print("                and satisfy Milestone 3 criteria 1, 2, 3 and 4 at the")
    print("                arithmetic level.  Label: automatically validated.")
    print("  NOT proven  : that the C++ compiles, that this model has not drifted")
    print("                from it, or anything about geometry, volumes, frame")
    print("                rate or how track limits feel.  Those still carry")
    print("                requires local compilation, requires Unreal Editor")
    print("                verification and requires playtesting.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
