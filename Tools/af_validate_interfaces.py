#!/usr/bin/env python3
# Copyright UludagFormula. Original work. Not affiliated with any real motorsport series.

"""UludagFormula interface override agreement checker.

Why this exists
---------------
Milestone 2 uncovered decision D-035: AAFVehiclePawn declared
GetParticipantDisplayName as returning FText, while IAFRaceParticipant declares
it as returning FString. Nothing in the repository caught it. Tools/
af_static_validate.py checks module boundaries, include resolution, originality,
backend isolation and test shape, but it had never compared an override against
the contract it claims to implement. That class of mistake stays invisible until
a compiler sees both translation units, and no compiler runs in CI here.

This script closes that gap. It reads every .h and .cpp under Unreal/Source,
collects the pure-virtual methods declared by IAF* interfaces, and compares the
return type of every override declaration and out-of-line definition against
them.

What it is not
--------------
Not a C++ parser. It matches declaration shapes with regular expressions, and it
only compares methods whose names appear in an IAF* interface. An unrelated
method that happens to share a name with an interface method is the single
false-positive shape, and it is accepted deliberately: a false positive costs a
rename, a false negative costs a broken build discovered on someone else's
machine.

Known blind spot, measured by the self-test: an out-of-line definition whose
return type is a pointer written as `FVector *Class::Method()` is not matched,
because the `*` binds to the name. The declaration in the header is still
checked, so the contract is not unguarded, only checked once instead of twice.
No UludagFormula interface currently returns a pointer.

Verification status
-------------------
This script IS executed, by CI and by --self-test. That makes it one of the few
things in this repository with genuine executed evidence behind it. It still
compiles nothing, so a pass says only that the text of the tree is internally
consistent on this one axis. Compilation, editor verification and playtesting
remain outstanding.

Kept separate from af_static_validate.py on purpose: this file carries its own
mutation suite (--self-test, decision D-030) and CI runs both, so the two can be
reviewed and changed independently.

Standard library only. Python 3.9 floor, same as af_static_validate.py.

Usage:
    python Tools/af_validate_interfaces.py --root .
    python Tools/af_validate_interfaces.py --self-test
"""

import argparse
import os
import re
import shutil
import sys
import tempfile
from typing import Dict, List, Sequence, Set, Tuple

UNREAL_DIR = "Unreal"
SOURCE_DIR = os.path.join(UNREAL_DIR, "Source")
SOURCE_EXTENSIONS = (".h", ".cpp")

#: virtual <return type> <Name>(<args>) [const] = 0;
PURE_VIRTUAL_RE = re.compile(
    r"virtual\s+([A-Za-z_][\w:<>,\s\*&]*?)\s+(\w+)\s*\(([^;()]*)\)\s*"
    r"(const\s*)?=\s*0\s*;"
)

#: virtual <return type> <Name>(<args>) [const] override
OVERRIDE_DECL_RE = re.compile(
    r"virtual\s+([A-Za-z_][\w:<>,\s\*&]*?)\s+(\w+)\s*\(([^;()]*)\)\s*"
    r"(const\s*)?override"
)

#: <return type> <Class>::<Name>(<args>) [const] {
OUT_OF_LINE_DEF_RE = re.compile(
    r"(?:^|\n)[ \t]*([A-Za-z_][\w:<>,\s\*&]*?)\s+(\w+)::(\w+)\s*\(([^;()]*)\)\s*"
    r"(const\s*)?\{"
)


class Report:
    """Collects outcomes so one run reports every problem, not the first.

    Same shape as the Report in af_static_validate.py, kept independent so this
    script has no import dependency on it.
    """

    def __init__(self, verbose: bool = False) -> None:
        self.passes = 0
        self.failures: List[str] = []
        self.verbose = verbose

    def check(self, condition: bool, description: str, detail: str = "") -> bool:
        if condition:
            self.passes += 1
            if self.verbose:
                print("  PASS  %s" % description)
            return True
        message = description if not detail else "%s -- %s" % (description, detail)
        self.failures.append(message)
        print("  FAIL  %s" % message)
        return False

    def summarise(self) -> int:
        print("")
        print("=" * 72)
        print("checks passed : %d" % self.passes)
        print("failures      : %d" % len(self.failures))
        if self.failures:
            print("")
            print("FAILURES:")
            for item in self.failures:
                print("  - %s" % item)
            print("=" * 72)
            print("RESULT: FAIL")
            return 1
        print("=" * 72)
        print("RESULT: PASS  (return types agree - nothing was compiled)")
        return 0


def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def iter_source_files(root: str) -> List[str]:
    found: List[str] = []
    source_root = os.path.join(root, SOURCE_DIR)
    for dirpath, _dirnames, filenames in os.walk(source_root):
        for filename in sorted(filenames):
            if filename.endswith(SOURCE_EXTENSIONS):
                found.append(os.path.join(dirpath, filename))
    return sorted(found)


def strip_comments(text: str) -> str:
    """Remove /* */ and // comments.

    Required, or the doc comment that explains D-035 would itself trip the
    check that D-035 motivated.
    """
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    text = re.sub(r"//[^\n]*", " ", text)
    return text


def relpath(root: str, path: str) -> str:
    return os.path.relpath(path, root).replace(os.sep, "/")


def normalise_type(text: str) -> str:
    """Collapse a return type to a comparable form.

    Whitespace and storage decorations that do not change the type are removed.
    `const FString&` and `FString` deliberately stay distinct, because they are
    distinct and an override may not silently swap one for the other.
    """
    cleaned = re.sub(r"\bFORCEINLINE\b|\binline\b|\bstatic\b", " ", text)
    cleaned = re.sub(r"\s*([\*&:,<>])\s*", r"\1", cleaned)
    return re.sub(r"\s+", " ", cleaned).strip()


def collect_interface_contracts(root: str) -> Dict[str, Tuple[str, str]]:
    """Map method name -> (normalised return type, declaring file).

    Only IAF* interface headers contribute. If two interfaces declare the same
    method name with different return types the entry is dropped rather than
    guessed at: there is then no single contract to check against, and guessing
    would produce failures nobody can act on.
    """
    contracts: Dict[str, Tuple[str, str]] = {}
    ambiguous: Set[str] = set()

    for path in iter_source_files(root):
        if not path.endswith(".h"):
            continue
        text = strip_comments(read_text(path))
        if not re.search(r"\bclass\b[^\n{;]*\bIAF\w+", text):
            continue

        rel = relpath(root, path)
        for return_type, name, _args, _is_const in PURE_VIRTUAL_RE.findall(text):
            normalised = normalise_type(return_type)
            if not normalised:
                continue
            existing = contracts.get(name)
            if existing is not None and existing[0] != normalised:
                ambiguous.add(name)
                continue
            contracts[name] = (normalised, rel)

    for name in ambiguous:
        contracts.pop(name, None)

    return contracts


def check_interface_overrides(root: str, report: Report) -> int:
    """Compare every override against its interface contract.

    Returns the number of comparisons made, so the caller can tell an empty
    tree apart from a clean one.
    """
    contracts = collect_interface_contracts(root)
    if not report.check(
        len(contracts) > 0, "at least one IAF* interface contract was parsed"
    ):
        return 0

    compared = 0

    for path in iter_source_files(root):
        text = strip_comments(read_text(path))
        rel = relpath(root, path)

        # Declarations carrying `override`. Checked in headers and .cpp files
        # alike, because test mocks declare their overrides inline in the .cpp
        # and a mock that drifts from the contract is the same bug.
        for return_type, name, _args, _is_const in OVERRIDE_DECL_RE.findall(text):
            contract = contracts.get(name)
            if contract is None:
                continue
            compared += 1
            expected, source = contract
            actual = normalise_type(return_type)
            report.check(
                actual == expected,
                "%s: override of %s returns the declared type" % (rel, name),
                "expected %s per %s, found %s" % (expected, source, actual),
            )

        # Out-of-line definitions carry no `override` keyword, so without this
        # pass a .cpp could disagree with its own header unnoticed.
        if path.endswith(".cpp"):
            for (
                return_type,
                _class_name,
                name,
                _args,
                _is_const,
            ) in OUT_OF_LINE_DEF_RE.findall(text):
                contract = contracts.get(name)
                if contract is None:
                    continue
                compared += 1
                expected, source = contract
                actual = normalise_type(return_type)
                report.check(
                    actual == expected,
                    "%s: definition of %s returns the declared type" % (rel, name),
                    "expected %s per %s, found %s" % (expected, source, actual),
                )

    print(
        "  note  %d interface method contracts, %d overrides compared"
        % (len(contracts), compared)
    )
    return compared


# ---------------------------------------------------------------------------
# Mutation self-test (decision D-030)
#
# A check nobody has seen fail is not a check. These cases build throwaway
# trees, break one thing at a time, and assert the checker notices exactly the
# mutations and nothing else. CI runs this, so the evidence is executed.
# ---------------------------------------------------------------------------

_IFACE = '''// Copyright UludagFormula. Original work. Not affiliated with any real motorsport series.

#pragma once

class ULUDAGFORMULACORE_API IAFRaceParticipant
{
public:
\tvirtual int32 GetParticipantId() const = 0;
\tvirtual FString GetParticipantDisplayName() const = 0;
\tvirtual FVector GetParticipantLocation() const = 0;
};
'''

_HEADER = '''// Copyright UludagFormula. Original work. Not affiliated with any real motorsport series.

#pragma once

class AAFVehiclePawn
{
public:
\tvirtual int32 GetParticipantId() const override;
\tvirtual FString GetParticipantDisplayName() const override;
\tvirtual FVector GetParticipantLocation() const override;
};
'''

_CPP = '''// Copyright UludagFormula. Original work. Not affiliated with any real motorsport series.

int32 AAFVehiclePawn::GetParticipantId() const
{
\treturn ParticipantId;
}

FString AAFVehiclePawn::GetParticipantDisplayName() const
{
\treturn DriverDisplayName.ToString();
}

FVector AAFVehiclePawn::GetParticipantLocation() const
{
\treturn GetActorLocation();
}
'''


def _build_tree(root: str, iface: str, header: str, cpp: str) -> None:
    public = os.path.join(root, SOURCE_DIR, "UludagFormulaCore", "Public")
    private = os.path.join(root, SOURCE_DIR, "UludagFormulaVehicle", "Private")
    os.makedirs(public)
    os.makedirs(private)
    with open(os.path.join(public, "AFRaceParticipantInterface.h"), "w") as handle:
        handle.write(iface)
    with open(os.path.join(public, "AFVehiclePawn.h"), "w") as handle:
        handle.write(header)
    with open(os.path.join(private, "AFVehiclePawn.cpp"), "w") as handle:
        handle.write(cpp)


def _run_case(iface: str, header: str, cpp: str) -> int:
    root = tempfile.mkdtemp()
    try:
        _build_tree(root, iface, header, cpp)
        report = Report(verbose=False)
        check_interface_overrides(root, report)
        return len(report.failures)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def _cases() -> List[Tuple[str, str, str, str, bool]]:
    return [
        ("baseline, everything agrees", _IFACE, _HEADER, _CPP, False),
        (
            "D-035 exactly: header returns FText",
            _IFACE,
            _HEADER.replace(
                "virtual FString GetParticipantDisplayName",
                "virtual FText GetParticipantDisplayName",
            ),
            _CPP,
            True,
        ),
        (
            "definition returns FText, header correct",
            _IFACE,
            _HEADER,
            _CPP.replace(
                "FString AAFVehiclePawn::GetParticipantDisplayName",
                "FText AAFVehiclePawn::GetParticipantDisplayName",
            ),
            True,
        ),
        (
            "integer width narrowed in the override",
            _IFACE,
            _HEADER.replace(
                "virtual int32 GetParticipantId", "virtual uint8 GetParticipantId"
            ),
            _CPP,
            True,
        ),
        (
            "reference snuck into the return type",
            _IFACE,
            _HEADER,
            _CPP.replace(
                "FVector AAFVehiclePawn::GetParticipantLocation",
                "const FVector& AAFVehiclePawn::GetParticipantLocation",
            ),
            True,
        ),
        (
            "whitespace-only difference must NOT fail",
            _IFACE,
            _HEADER.replace(
                "virtual FVector GetParticipantLocation",
                "virtual  FVector   GetParticipantLocation",
            ),
            _CPP,
            False,
        ),
        (
            "pointer spacing must NOT fail",
            _IFACE.replace(
                "virtual FVector GetParticipantLocation",
                "virtual FVector* GetParticipantLocation",
            ),
            _HEADER.replace(
                "virtual FVector GetParticipantLocation",
                "virtual FVector * GetParticipantLocation",
            ),
            _CPP.replace(
                "FVector AAFVehiclePawn::GetParticipantLocation",
                "FVector *AAFVehiclePawn::GetParticipantLocation",
            ),
            False,
        ),
        (
            "a comment naming the wrong type must NOT fail",
            _IFACE,
            _HEADER.replace(
                "public:",
                "public:\n\t// virtual FText GetParticipantDisplayName() const override;",
            ),
            _CPP,
            False,
        ),
        (
            "method absent from any interface is ignored",
            _IFACE,
            _HEADER.replace(
                "};",
                "\tvirtual double GetSomethingUnrelated() const override;\n};",
            ),
            _CPP,
            False,
        ),
    ]


def self_test() -> int:
    print("Mutation self-test: interface override agreement (D-030)")
    print("")
    all_ok = True
    for label, iface, header, cpp, expect_failure in _cases():
        failures = _run_case(iface, header, cpp)
        detected = failures > 0
        case_ok = detected == expect_failure
        all_ok = all_ok and case_ok
        print(
            "  %-4s %-44s expect_fail=%-5s failures=%d"
            % ("OK" if case_ok else "BAD", label, expect_failure, failures)
        )

    print("")
    print("=" * 72)
    if all_ok:
        print("RESULT: PASS  the checker fails on every mutation and only on mutations")
        return 0
    print("RESULT: FAIL  the checker did not behave as specified")
    return 1


def main(argv: Sequence[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Check that UludagFormula interface overrides agree with their contracts."
    )
    parser.add_argument(
        "--root",
        default=None,
        help="Repository root. Defaults to the parent of this script's directory.",
    )
    parser.add_argument("--verbose", action="store_true", help="Print passing checks.")
    parser.add_argument(
        "--self-test",
        action="store_true",
        dest="self_test",
        help="Run the mutation suite instead of checking the repository.",
    )
    args = parser.parse_args(list(argv))

    if args.self_test:
        return self_test()

    root = args.root or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    root = os.path.abspath(root)

    print("UludagFormula interface override agreement")
    print("repository root: %s" % root)
    print("")
    print("This script does NOT compile anything. A pass means every override")
    print("returns what its interface declares. Compilation, editor verification")
    print("and playtesting remain outstanding.")
    print("")

    if not os.path.isdir(os.path.join(root, SOURCE_DIR)):
        print("ERROR: %s not found under %s" % (SOURCE_DIR, root))
        return 2

    report = Report(verbose=args.verbose)
    compared = check_interface_overrides(root, report)
    report.check(compared > 0, "at least one interface override was compared")
    return report.summarise()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
