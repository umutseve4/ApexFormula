#!/usr/bin/env python3
"""UludagFormula - track definition drift guard (D-045).

Mechanically compares the C++ validator ``UAFTrackDefinition::ValidateSelf()``
against its hand-maintained Python mirror ``validate_track_definition()`` in
``BlenderPipeline/scripts/af_circuit_generate.py``.

WHY A SEPARATE TOOL (and not an extension of af_drift_guard.py)
--------------------------------------------------------------
D-044 introduced ``Tools/af_drift_guard.py`` for the LAP RULES mirror. Its
check functions read the module-level ``CLASS_PAIRS`` / ``RULES`` tables as
globals rather than as parameters, and its whole shape assumes a C++ *class*
mirrored by a Python *class*. The track mirror is a free function in a
different file with a different failure mode (a list of diagnostic strings).
Extending that file in place would mean rewriting 38 KB of already-proven,
mutation-tested code. This guard is therefore additive and standalone: it
imports nothing from af_drift_guard.py, and its rule tables are passed in as
arguments so the self-test can exercise the checks with small fixtures.
Precedent for separate single-purpose validators: D-037.

WHAT THIS GUARD PROVES
----------------------
Check A - diagnostic parity.
    Every message template pushed into the C++ ``Problems`` array must appear
    in the Python mirror, byte for byte, in the same order. Adding, removing,
    reordering or rewording a check on one side only is a finding. Because
    every threshold in this validator is spelled out in its own message
    ("must be >= 1", "at least 2 entries", "checkpoint index 0"), a silent
    threshold change is caught by this check as well.

Check B - predicate parity.
    Each declared rule names one C++ source fragment and one Python source
    fragment. Both must be present in their respective function bodies. This
    catches drift where a check is rewritten but its message is left intact.

Check C - field parity.
    Each declared field pair (C++ member, Python dict key) must be read by
    both sides.

WHAT THIS GUARD DOES NOT PROVE
------------------------------
  * It does NOT compile the C++ and does NOT execute the Python mirror.
    Nothing here is evidence that either side runs.
  * It compares TEXT, not behaviour. Both sides can agree on every message
    and every fragment and still differ in control flow or in the values
    substituted into the format specifiers.
  * It cannot detect a missing invariant that neither side ever checked.
  * Only C++ literals reached through ``Problems.Add(...)`` and Python
    literals reached through ``problems.append(...)`` are compared. A
    diagnostic emitted by any other means is invisible to Check A.

USAGE
-----
    python3 Tools/af_track_drift_guard.py --self-test
    python3 Tools/af_track_drift_guard.py --root . [--verbose]

Exit codes: 0 clean, 1 drift found or self-test failed, 2 bad invocation.
"""

from __future__ import annotations

import argparse
import ast
import os
import re
import sys

EXIT_OK = 0
EXIT_DRIFT = 1
EXIT_USAGE = 2

BAR = "=" * 72

# --------------------------------------------------------------------------
# Repository wiring
# --------------------------------------------------------------------------

PATH_TRACK_CPP = os.path.join(
    "Unreal", "Source", "ApexFormulaRace", "Private", "AFTrackDefinition.cpp"
)
PATH_GENERATOR_PY = os.path.join(
    "BlenderPipeline", "scripts", "af_circuit_generate.py"
)

CPP_FUNCTION = "UAFTrackDefinition::ValidateSelf"
CPP_SINK = "Problems.Add"
PY_FUNCTION = "validate_track_definition"
PY_SINK = "problems"

# (C++ member name, Python dict key) - both sides must read every pair.
FIELD_PAIRS = (
    ("DataVersion", "data_version"),
    ("TrackId", "track_id"),
    ("DisplayName", "display_name"),
    ("LapLengthM", "lap_length_m"),
    ("GridSlotCount", "grid_slot_count"),
    ("CheckpointOrder", "checkpoint_order"),
    ("Sectors", "sectors"),
    ("SectorIndex", "sector_index"),
    ("ClosingCheckpointIndex", "closing_checkpoint_index"),
    ("bHasPitLane", "has_pit_lane"),
    ("PitLaneSpeedLimitKph", "pit_lane_speed_limit_kph"),
)

# (rule id, description, C++ fragment, Python fragment)
PREDICATE_RULES = (
    ("P-01", "data version floor",
     "DataVersion < 1",
     'track["data_version"] < 1'),
    ("P-02", "track id must be set",
     "TrackId.IsNone()",
     "if not track_id:"),
    ("P-03", "track id must be lower case",
     "AsString != AsString.ToLower()",
     "track_id != track_id.lower()"),
    ("P-04", "track id must not contain spaces",
     'AsString.Contains(TEXT(" "))',
     'if " " in track_id:'),
    ("P-05", "display name must be set",
     "DisplayName.IsEmpty()",
     'not track["display_name"]'),
    ("P-06", "lap length must be positive",
     "LapLengthM <= 0.0",
     'track["lap_length_m"] <= 0.0'),
    ("P-07", "grid slot floor",
     "GridSlotCount < 1",
     'track["grid_slot_count"] < 1'),
    ("P-08", "checkpoint order minimum size",
     "CheckpointOrder.Num() < 2",
     "len(order) < 2"),
    ("P-09", "checkpoint entry must be set",
     "CheckpointId.IsNone()",
     "if not checkpoint_id:"),
    ("P-10", "checkpoint entries must be unique",
     "SeenCheckpoints.Add(CheckpointId, &bAlreadySeen)",
     "if checkpoint_id in seen:"),
    ("P-11", "at least one sector",
     "Sectors.Num() < 1",
     "len(sectors) < 1"),
    ("P-12", "sectors stored in ascending order from zero",
     "Sector.SectorIndex != Index",
     'sector["sector_index"] != index'),
    ("P-13", "sector index used at most once",
     "SeenSectorIndices.Add(Sector.SectorIndex, &bAlreadySeen)",
     'sector["sector_index"] in seen_indices'),
    ("P-14", "closing checkpoint index in range",
     "CheckpointOrder.IsValidIndex(Sector.ClosingCheckpointIndex)",
     "0 <= closing < len(order)"),
    ("P-15", "final sector closes at the timing line",
     "FinalSector.ClosingCheckpointIndex != 0",
     'sectors[-1]["closing_checkpoint_index"] != 0'),
    ("P-16", "pit lane speed limit positive when pit lane present",
     "bHasPitLane && PitLaneSpeedLimitKph <= 0.0",
     'track["has_pit_lane"] and track["pit_lane_speed_limit_kph"] <= 0.0'),
)

TEXT_LITERAL_RE = re.compile(r'TEXT\(\s*"((?:[^"\\]|\\.)*)"\s*\)')


# --------------------------------------------------------------------------
# Reporting
# --------------------------------------------------------------------------


class Report(object):
    """Collects findings and optional verbose notes."""

    def __init__(self, verbose=False):
        self.findings = []
        self.notes = []
        self.verbose = verbose

    def add(self, text):
        self.findings.append(text)

    def note(self, text):
        self.notes.append(text)

    def ok(self):
        return not self.findings

    def emit(self, stream=None):
        stream = stream or sys.stdout
        if self.verbose:
            for line in self.notes:
                stream.write("  . %s\n" % line)
        for line in self.findings:
            stream.write("  ! %s\n" % line)


# --------------------------------------------------------------------------
# C++ extraction (pure text; nothing is compiled or executed)
# --------------------------------------------------------------------------


def _scan_forward(text, start, open_ch, close_ch):
    """Return index just past the balanced close, or -1.

    String literals are skipped so that parentheses inside a diagnostic
    message such as "(0..%d)" do not unbalance the scan.
    """
    depth = 1
    i = start
    in_str = False
    esc = False
    n = len(text)
    while i < n:
        ch = text[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
        else:
            if ch == '"':
                in_str = True
            elif ch == open_ch:
                depth += 1
            elif ch == close_ch:
                depth -= 1
                if depth == 0:
                    return i + 1
        i += 1
    return -1


def extract_cpp_function_body(text, qualified_name):
    """Return the brace-matched body of a C++ function, or None."""
    anchor = text.find(qualified_name)
    if anchor < 0:
        return None
    brace = text.find("{", anchor)
    if brace < 0:
        return None
    end = _scan_forward(text, brace + 1, "{", "}")
    if end < 0:
        return None
    return text[brace + 1:end - 1]


def extract_cpp_sink_templates(body, sink):
    """Return message templates passed to ``sink(...)``, in source order.

    An entry is None when a sink call carries no ``TEXT("...")`` literal,
    which is itself reported as a finding by the caller.
    """
    out = []
    needle = sink + "("
    i = 0
    while True:
        j = body.find(needle, i)
        if j < 0:
            break
        start = j + len(needle)
        end = _scan_forward(body, start, "(", ")")
        if end < 0:
            out.append(None)
            break
        arg = body[start:end - 1]
        match = TEXT_LITERAL_RE.search(arg)
        out.append(match.group(1) if match else None)
        i = end
    return out


# --------------------------------------------------------------------------
# Python extraction (ast only; never exec, never import)
# --------------------------------------------------------------------------


def extract_python_function(module_text, name):
    """Return the ast.FunctionDef for ``name`` at module level, or None.

    Raises SyntaxError if the module does not parse; callers convert that
    into a finding rather than a traceback.
    """
    tree = ast.parse(module_text)
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    return None


def python_function_source(module_text, node):
    lines = module_text.splitlines()
    end = getattr(node, "end_lineno", None) or node.lineno
    return "\n".join(lines[node.lineno - 1:end])


def extract_python_sink_templates(node, sink_name):
    """Return templates passed to ``sink_name.append(...)`` in source order.

    Handles the plain literal form and the ``"template" % args`` form.
    Adjacent string literals are already merged by the parser, so a message
    split across source lines is compared as one string.
    """
    found = []
    for sub in ast.walk(node):
        if not isinstance(sub, ast.Call):
            continue
        func = sub.func
        if not isinstance(func, ast.Attribute) or func.attr != "append":
            continue
        if not isinstance(func.value, ast.Name) or func.value.id != sink_name:
            continue
        if not sub.args:
            found.append((sub.lineno, sub.col_offset, None))
            continue
        arg = sub.args[0]
        template = None
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            template = arg.value
        elif (
            isinstance(arg, ast.BinOp)
            and isinstance(arg.op, ast.Mod)
            and isinstance(arg.left, ast.Constant)
            and isinstance(arg.left.value, str)
        ):
            template = arg.left.value
        found.append((sub.lineno, sub.col_offset, template))
    found.sort()
    return [t for _, _, t in found]


# --------------------------------------------------------------------------
# Checks
# --------------------------------------------------------------------------


def check_message_parity(cpp_templates, py_templates, report):
    """Check A - ordered, byte-exact diagnostic parity."""
    for index, template in enumerate(cpp_templates):
        if template is None:
            report.add(
                "A: C++ diagnostic #%d carries no TEXT literal; it cannot be "
                "compared" % index
            )
    for index, template in enumerate(py_templates):
        if template is None:
            report.add(
                "A: Python diagnostic #%d is not a plain template; it cannot "
                "be compared" % index
            )

    cpp_clean = [t for t in cpp_templates if t is not None]
    py_clean = [t for t in py_templates if t is not None]

    if len(cpp_clean) != len(py_clean):
        report.add(
            "A: diagnostic count differs - C++ emits %d, Python emits %d"
            % (len(cpp_clean), len(py_clean))
        )

    only_cpp = [t for t in cpp_clean if t not in py_clean]
    only_py = [t for t in py_clean if t not in cpp_clean]
    for text in only_cpp:
        report.add("A: message present in C++ but missing in Python: %r" % text)
    for text in only_py:
        report.add("A: message present in Python but missing in C++: %r" % text)

    if not only_cpp and not only_py:
        for index, (left, right) in enumerate(zip(cpp_clean, py_clean)):
            if left != right:
                report.add(
                    "A: diagnostic #%d is out of order - C++ %r, Python %r"
                    % (index, left, right)
                )

    report.note(
        "Check A compared %d C++ and %d Python diagnostics"
        % (len(cpp_clean), len(py_clean))
    )


def check_predicate_parity(cpp_body, py_source, rules, report):
    """Check B - both sides still contain each declared source fragment."""
    seen_ids = set()
    for rule_id, description, cpp_fragment, py_fragment in rules:
        if rule_id in seen_ids:
            raise AssertionError("duplicate predicate rule id %s" % rule_id)
        seen_ids.add(rule_id)
        if cpp_fragment not in cpp_body:
            report.add(
                "B: %s (%s) - C++ fragment not found: %s"
                % (rule_id, description, cpp_fragment)
            )
        if py_fragment not in py_source:
            report.add(
                "B: %s (%s) - Python fragment not found: %s"
                % (rule_id, description, py_fragment)
            )
    report.note("Check B evaluated %d predicate rules" % len(rules))


def check_field_parity(cpp_body, py_source, pairs, report):
    """Check C - both sides still read each declared field."""
    seen = set()
    for cpp_name, py_key in pairs:
        if cpp_name in seen:
            raise AssertionError("duplicate field name %s" % cpp_name)
        seen.add(cpp_name)
        if cpp_name not in cpp_body:
            report.add("C: C++ never reads member %s" % cpp_name)
        if ('"%s"' % py_key) not in py_source:
            report.add("C: Python never reads key %s" % py_key)
    report.note("Check C evaluated %d field pairs" % len(pairs))


# --------------------------------------------------------------------------
# Orchestration
# --------------------------------------------------------------------------


def analyse(cpp_text, py_text, rules, pairs, report):
    """Run all three checks over already-loaded source text."""
    cpp_body = extract_cpp_function_body(cpp_text, CPP_FUNCTION)
    if cpp_body is None:
        report.add("C++ function %s was not found" % CPP_FUNCTION)

    py_node = None
    py_source = None
    try:
        py_node = extract_python_function(py_text, PY_FUNCTION)
    except SyntaxError as error:
        report.add("Python mirror does not parse: %s" % error)
    if py_node is None and not report.findings:
        report.add("Python function %s was not found" % PY_FUNCTION)
    elif py_node is None and py_text and "def %s" % PY_FUNCTION not in py_text:
        report.add("Python function %s was not found" % PY_FUNCTION)

    if cpp_body is None or py_node is None:
        return

    py_source = python_function_source(py_text, py_node)
    check_message_parity(
        extract_cpp_sink_templates(cpp_body, CPP_SINK),
        extract_python_sink_templates(py_node, PY_SINK),
        report,
    )
    check_predicate_parity(cpp_body, py_source, rules, report)
    check_field_parity(cpp_body, py_source, pairs, report)


def read_text(path):
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def run_against_root(root, verbose):
    cpp_path = os.path.join(root, PATH_TRACK_CPP)
    py_path = os.path.join(root, PATH_GENERATOR_PY)

    missing = [p for p in (cpp_path, py_path) if not os.path.isfile(p)]
    if missing:
        for path in missing:
            sys.stderr.write("error: required source not found: %s\n" % path)
        return EXIT_DRIFT

    report = Report(verbose=verbose)
    analyse(
        read_text(cpp_path),
        read_text(py_path),
        PREDICATE_RULES,
        FIELD_PAIRS,
        report,
    )

    print(BAR)
    print("UludagFormula track definition drift guard (D-045)")
    print(BAR)
    print("C++    : %s" % cpp_path)
    print("Python : %s" % py_path)
    report.emit()
    if report.ok():
        print("RESULT : clean - %d predicate rules, %d field pairs, "
              "ordered message parity holds"
              % (len(PREDICATE_RULES), len(FIELD_PAIRS)))
        print(BAR)
        return EXIT_OK
    print("RESULT : DRIFT - %d finding(s)" % len(report.findings))
    print(BAR)
    return EXIT_DRIFT


# --------------------------------------------------------------------------
# Self-test
# --------------------------------------------------------------------------

FIXTURE_CPP = '''
TArray<FString> UAFTrackDefinition::ValidateSelf() const
{
    TArray<FString> Problems;

    if (DataVersion < 1)
    {
        Problems.Add(FString::Printf(TEXT("DataVersion low, is %d"), DataVersion));
    }

    const FString AsString = TrackId.ToString();
    if (AsString.Contains(TEXT(" ")))
    {
        Problems.Add(TEXT("TrackId has a space"));
    }

    if (CheckpointOrder.Num() < 2)
    {
        Problems.Add(FString::Printf(
            TEXT("CheckpointOrder needs 2 entries (min), has %d"),
            CheckpointOrder.Num()));
    }

    return Problems;
}
'''

FIXTURE_PY = '''
def validate_track_definition(track):
    problems = []
    if track["data_version"] < 1:
        problems.append("DataVersion low, is %d" % track["data_version"])
    track_id = track["track_id"]
    if " " in track_id:
        problems.append("TrackId has a space")
    order = track["checkpoint_order"]
    if len(order) < 2:
        problems.append(
            "CheckpointOrder needs 2 entries "
            "(min), has %d" % len(order))
    return problems
'''

FIXTURE_RULES = (
    ("F-01", "data version floor",
     "DataVersion < 1", 'track["data_version"] < 1'),
    ("F-02", "no spaces in track id",
     'AsString.Contains(TEXT(" "))', 'if " " in track_id:'),
)

FIXTURE_PAIRS = (
    ("DataVersion", "data_version"),
    ("CheckpointOrder", "checkpoint_order"),
)


class SelfTest(object):
    def __init__(self):
        self.cases = []
        self.names = set()

    def check(self, name, condition, detail=""):
        if name in self.names:
            raise AssertionError("duplicate self-test case name %s" % name)
        self.names.add(name)
        self.cases.append((name, bool(condition), detail))

    def _findings(self, cpp=None, py=None, rules=None, pairs=None):
        report = Report()
        analyse(
            FIXTURE_CPP if cpp is None else cpp,
            FIXTURE_PY if py is None else py,
            FIXTURE_RULES if rules is None else rules,
            FIXTURE_PAIRS if pairs is None else pairs,
            report,
        )
        return report.findings

    # -- extraction primitives ---------------------------------------

    def test_cpp_body_extracted(self):
        body = extract_cpp_function_body(FIXTURE_CPP, CPP_FUNCTION)
        self.check("cpp-body-found", body is not None)
        self.check("cpp-body-has-return", body and "return Problems;" in body)

    def test_cpp_body_missing(self):
        self.check(
            "cpp-body-absent",
            extract_cpp_function_body("int main() { return 0; }",
                                      CPP_FUNCTION) is None,
        )

    def test_cpp_literal_scan_skips_non_sink(self):
        body = extract_cpp_function_body(FIXTURE_CPP, CPP_FUNCTION)
        templates = extract_cpp_sink_templates(body, CPP_SINK)
        self.check("cpp-three-diagnostics", len(templates) == 3,
                   "got %d" % len(templates))
        self.check("cpp-space-literal-excluded", " " not in templates)

    def test_cpp_literal_with_parentheses(self):
        body = extract_cpp_function_body(FIXTURE_CPP, CPP_FUNCTION)
        templates = extract_cpp_sink_templates(body, CPP_SINK)
        self.check(
            "cpp-paren-inside-string",
            templates[2] == "CheckpointOrder needs 2 entries (min), has %d",
            repr(templates[2]),
        )

    def test_python_implicit_concat_merged(self):
        node = extract_python_function(FIXTURE_PY, PY_FUNCTION)
        templates = extract_python_sink_templates(node, PY_SINK)
        self.check(
            "py-concat-merged",
            templates[2] == "CheckpointOrder needs 2 entries (min), has %d",
            repr(templates[2]),
        )

    def test_python_function_missing(self):
        node = extract_python_function("def other():\n    pass\n", PY_FUNCTION)
        self.check("py-function-absent", node is None)

    # -- positive control --------------------------------------------

    def test_fixtures_are_in_parity(self):
        findings = self._findings()
        self.check("fixtures-clean", not findings, "; ".join(findings))

    # -- mutation: check A -------------------------------------------

    def test_removed_cpp_check_is_caught(self):
        mutated = FIXTURE_CPP.replace(
            '        Problems.Add(TEXT("TrackId has a space"));\n', "")
        findings = self._findings(cpp=mutated)
        self.check("mut-cpp-removed-check",
                   any(f.startswith("A:") for f in findings),
                   "; ".join(findings))

    def test_removed_python_check_is_caught(self):
        mutated = FIXTURE_PY.replace(
            '        problems.append("TrackId has a space")\n',
            "        pass\n")
        findings = self._findings(py=mutated)
        self.check("mut-py-removed-check",
                   any(f.startswith("A:") for f in findings),
                   "; ".join(findings))

    def test_reworded_python_message_is_caught(self):
        mutated = FIXTURE_PY.replace("TrackId has a space",
                                     "TrackId contains a space")
        findings = self._findings(py=mutated)
        self.check("mut-py-reworded",
                   any(f.startswith("A:") for f in findings),
                   "; ".join(findings))

    def test_changed_threshold_text_is_caught(self):
        mutated = FIXTURE_CPP.replace("needs 2 entries", "needs 3 entries")
        findings = self._findings(cpp=mutated)
        self.check("mut-cpp-threshold-text",
                   any(f.startswith("A:") for f in findings),
                   "; ".join(findings))

    def test_reordered_python_checks_are_caught(self):
        # Swap two message texts: the multiset of diagnostics is unchanged,
        # only their order differs, which must still be reported.
        mutated = FIXTURE_PY.replace('"DataVersion low, is %d"', '"__TMP__"')
        mutated = mutated.replace('"TrackId has a space"',
                                  '"DataVersion low, is %d"')
        mutated = mutated.replace('"__TMP__"', '"TrackId has a space"')
        findings = self._findings(py=mutated)
        self.check("mut-py-reordered",
                   any("out of order" in f for f in findings),
                   "; ".join(findings))

    # -- mutation: check B -------------------------------------------

    def test_rewritten_cpp_predicate_is_caught(self):
        mutated = FIXTURE_CPP.replace("DataVersion < 1", "DataVersion <= 0")
        findings = self._findings(cpp=mutated)
        self.check("mut-cpp-predicate",
                   any(f.startswith("B:") for f in findings),
                   "; ".join(findings))

    def test_rewritten_python_predicate_is_caught(self):
        mutated = FIXTURE_PY.replace('track["data_version"] < 1',
                                     'track["data_version"] <= 0')
        findings = self._findings(py=mutated)
        self.check("mut-py-predicate",
                   any(f.startswith("B:") for f in findings),
                   "; ".join(findings))

    # -- mutation: check C -------------------------------------------

    def test_dropped_python_field_is_caught(self):
        mutated = FIXTURE_PY.replace('track["checkpoint_order"]',
                                     "track_order_placeholder")
        findings = self._findings(py=mutated)
        self.check("mut-py-field",
                   any(f.startswith("C:") for f in findings),
                   "; ".join(findings))

    def test_dropped_cpp_field_is_caught(self):
        mutated = FIXTURE_CPP.replace("CheckpointOrder", "CpOrder")
        findings = self._findings(cpp=mutated)
        self.check("mut-cpp-field",
                   any(f.startswith("C:") for f in findings),
                   "; ".join(findings))

    # -- robustness ---------------------------------------------------

    def test_broken_python_is_reported_not_raised(self):
        findings = self._findings(py="def validate_track_definition(:\n")
        self.check("broken-python-reported",
                   any("does not parse" in f for f in findings),
                   "; ".join(findings))

    def test_missing_cpp_function_is_reported(self):
        findings = self._findings(cpp="// nothing here\n")
        self.check("missing-cpp-reported",
                   any("was not found" in f for f in findings),
                   "; ".join(findings))

    def test_missing_python_function_is_reported(self):
        findings = self._findings(py="def unrelated():\n    return []\n")
        self.check("missing-python-reported",
                   any("was not found" in f for f in findings),
                   "; ".join(findings))

    # -- table hygiene ------------------------------------------------

    def test_real_tables_are_well_formed(self):
        ids = [r[0] for r in PREDICATE_RULES]
        self.check("rule-ids-unique", len(ids) == len(set(ids)))
        self.check(
            "rule-fields-non-empty",
            all(all(str(part).strip() for part in rule)
                for rule in PREDICATE_RULES),
        )
        cpp_names = [p[0] for p in FIELD_PAIRS]
        py_keys = [p[1] for p in FIELD_PAIRS]
        self.check("field-cpp-unique", len(cpp_names) == len(set(cpp_names)))
        self.check("field-py-unique", len(py_keys) == len(set(py_keys)))
        self.check("rule-count-16", len(PREDICATE_RULES) == 16,
                   "got %d" % len(PREDICATE_RULES))

    def test_duplicate_rule_id_raises(self):
        bad = (
            ("F-01", "a", "DataVersion < 1", 'track["data_version"] < 1'),
            ("F-01", "b", "DataVersion < 1", 'track["data_version"] < 1'),
        )
        raised = False
        try:
            check_predicate_parity(FIXTURE_CPP, FIXTURE_PY, bad, Report())
        except AssertionError:
            raised = True
        self.check("duplicate-rule-id-raises", raised)

    def run(self):
        methods = [
            self.test_cpp_body_extracted,
            self.test_cpp_body_missing,
            self.test_cpp_literal_scan_skips_non_sink,
            self.test_cpp_literal_with_parentheses,
            self.test_python_implicit_concat_merged,
            self.test_python_function_missing,
            self.test_fixtures_are_in_parity,
            self.test_removed_cpp_check_is_caught,
            self.test_removed_python_check_is_caught,
            self.test_reworded_python_message_is_caught,
            self.test_changed_threshold_text_is_caught,
            self.test_reordered_python_checks_are_caught,
            self.test_rewritten_cpp_predicate_is_caught,
            self.test_rewritten_python_predicate_is_caught,
            self.test_dropped_python_field_is_caught,
            self.test_dropped_cpp_field_is_caught,
            self.test_broken_python_is_reported_not_raised,
            self.test_missing_cpp_function_is_reported,
            self.test_missing_python_function_is_reported,
            self.test_real_tables_are_well_formed,
            self.test_duplicate_rule_id_raises,
        ]
        for method in methods:
            method()
        return self.cases


def run_self_test(verbose):
    suite = SelfTest()
    cases = suite.run()
    failed = [c for c in cases if not c[1]]

    print(BAR)
    print("UludagFormula track drift guard - self-test (D-045)")
    print(BAR)
    if verbose:
        for name, passed, detail in cases:
            print("  %-4s %s%s" % ("PASS" if passed else "FAIL", name,
                                   (" - %s" % detail) if detail else ""))
    else:
        for name, passed, detail in failed:
            print("  FAIL %s%s" % (name, (" - %s" % detail) if detail else ""))
    print("cases : %d" % len(cases))
    print("failed: %d" % len(failed))
    print(BAR)
    return EXIT_OK if not failed else EXIT_DRIFT


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = argparse.ArgumentParser(
        description="UludagFormula track definition drift guard (D-045).",
        add_help=True,
    )
    parser.add_argument("--root", help="repository root to check")
    parser.add_argument("--self-test", action="store_true",
                        dest="self_test", help="run the built-in test suite")
    parser.add_argument("--verbose", action="store_true",
                        help="print per-check detail")
    args = parser.parse_args(argv)

    if args.self_test and args.root:
        sys.stderr.write("error: --self-test and --root are mutually "
                         "exclusive\n")
        return EXIT_USAGE
    if args.self_test:
        return run_self_test(args.verbose)
    if args.root:
        return run_against_root(args.root, args.verbose)

    parser.print_help()
    return EXIT_USAGE


if __name__ == "__main__":
    sys.exit(main())
