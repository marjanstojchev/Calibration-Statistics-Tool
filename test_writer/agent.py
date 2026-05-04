"""Main orchestrator for the test-writer agent.

:class:`TestWriterAgent` ties together :mod:`test_writer.code_analyzer` and
:mod:`test_writer.csv_generator` to produce a Jira Zephyr-ready CSV file
from a set of Python source paths.

Typical usage::

    from test_writer import TestWriterAgent

    agent = TestWriterAgent(
        source_paths=["shared/", "ui/handlers/"],
        levels=["Unit", "Integration"],
        output_csv="zephyr_tests.csv",
    )
    path = agent.run()
    print(f"Generated: {path}")
"""
from __future__ import annotations

import os
from typing import List, Optional

from test_writer.code_analyzer import CodeAnalyzer, SourceSymbol
from test_writer.csv_generator import ZephyrCSVGenerator
from test_writer.models import (
    TestCase,
    TestLevel,
    TestPriority,
    TestStatus,
    TestStep,
)


# ---------------------------------------------------------------------------
# Priority heuristics
# ---------------------------------------------------------------------------

# Words in function/class names that suggest a higher priority
_HIGH_PRIORITY_KEYWORDS = frozenset({
    "parse", "load", "save", "export", "import", "validate",
    "calculate", "process", "run", "execute", "init", "connect",
    "auth", "login", "error", "exception",
})


def _infer_priority(symbol: SourceSymbol) -> TestPriority:
    """Return a priority based on the symbol name and kind."""
    lower = symbol.name.lower()
    if any(kw in lower for kw in _HIGH_PRIORITY_KEYWORDS):
        return TestPriority.HIGH
    if symbol.kind == "class":
        return TestPriority.MEDIUM
    return TestPriority.LOW


# ---------------------------------------------------------------------------
# Step builders — one builder per testing level
# ---------------------------------------------------------------------------

def _build_unit_steps(symbol: SourceSymbol) -> List[TestStep]:
    """Generate unit-test steps for a function/method symbol."""
    if symbol.kind == "module":
        return [
            TestStep(
                action=f"Import the ``{symbol.name}`` module.",
                data="",
                expected="Module imports without errors; no exceptions raised.",
            )
        ]
    if symbol.kind == "class":
        return [
            TestStep(
                action=f"Instantiate ``{symbol.name}`` with default arguments.",
                data="",
                expected="Object is created successfully; no exceptions raised.",
            ),
            TestStep(
                action="Inspect all public attributes of the instance.",
                data="",
                expected="All attributes have expected default types/values.",
            ),
        ]
    # function / method
    arg_desc = ", ".join(symbol.args) if symbol.args else "no arguments"
    return [
        TestStep(
            action=f"Call ``{symbol.name}({arg_desc})`` with valid inputs.",
            data=f"Parameters: {arg_desc}",
            expected="Function returns the expected result without raising exceptions.",
        ),
        TestStep(
            action=f"Call ``{symbol.name}`` with boundary / edge-case inputs.",
            data="e.g. empty strings, zero values, maximum values",
            expected="Function handles edge cases gracefully (returns a sensible value or raises the documented exception).",
        ),
    ]


def _build_integration_steps(symbol: SourceSymbol) -> List[TestStep]:
    """Generate integration-test steps for a class or function symbol."""
    if symbol.kind == "module":
        return [
            TestStep(
                action=f"Load the ``{symbol.name}`` module together with its direct dependencies.",
                data="",
                expected="All imports succeed; no circular-import errors.",
            )
        ]
    if symbol.kind == "class":
        return [
            TestStep(
                action=f"Instantiate ``{symbol.name}`` with real (non-mocked) dependencies.",
                data="Use the test fixture data from ``tests/conftest.py``.",
                expected="Instance integrates correctly with its dependencies.",
            ),
            TestStep(
                action="Invoke the primary workflow methods in sequence.",
                data="",
                expected="Each method produces the expected side-effects and return values.",
            ),
        ]
    return [
        TestStep(
            action=f"Call ``{symbol.name}`` inside a realistic end-to-end scenario.",
            data="Provide representative input data.",
            expected="Output data matches the expected format and values.",
        )
    ]


def _build_system_steps(symbol: SourceSymbol) -> List[TestStep]:
    """Generate high-level system / GUI test steps."""
    return [
        TestStep(
            action="Launch the Calibration Statistics Tool application.",
            data="",
            expected="Application starts without errors; main window is visible.",
        ),
        TestStep(
            action=f"Exercise the feature associated with ``{symbol.name}`` through the GUI.",
            data="Use a representative measurement data file.",
            expected="The feature behaves as documented; no errors are shown in the log panel.",
        ),
        TestStep(
            action="Close the application.",
            data="",
            expected="Application exits cleanly; no crash dialogs.",
        ),
    ]


_STEP_BUILDERS = {
    TestLevel.UNIT: _build_unit_steps,
    TestLevel.INTEGRATION: _build_integration_steps,
    TestLevel.SYSTEM: _build_system_steps,
}


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class TestWriterAgent:
    """Generate Jira Zephyr manual test cases from Python source files.

    Parameters:
        source_paths:
            Directories or individual ``.py`` files to analyse.
        levels:
            Which testing levels to generate test cases for.
            Accepts :class:`~test_writer.models.TestLevel` values **or**
            their string equivalents (e.g. ``"Unit"``, ``"integration"``).
            Defaults to ``[TestLevel.UNIT, TestLevel.INTEGRATION]``.
        output_csv:
            Path for the generated CSV file.
            Defaults to ``"zephyr_tests.csv"`` in the current directory.
        root:
            Repository root used to build relative module names.
            Defaults to ``os.getcwd()``.
        skip_dirs:
            Extra directory names to skip when walking source paths.
        component_prefix:
            Jira component name prefix applied to each test case.
    """

    _DEFAULT_LEVELS = [TestLevel.UNIT, TestLevel.INTEGRATION]

    def __init__(
        self,
        source_paths: Optional[List[str]] = None,
        levels: Optional[List] = None,
        output_csv: str = "zephyr_tests.csv",
        root: Optional[str] = None,
        skip_dirs: Optional[List[str]] = None,
        component_prefix: str = "Calibration-Statistics-Tool",
    ) -> None:
        self.source_paths: List[str] = source_paths or [os.getcwd()]
        self.levels: List[TestLevel] = self._parse_levels(levels or self._DEFAULT_LEVELS)
        self.output_csv = output_csv
        self.root = root or os.getcwd()
        self.skip_dirs = skip_dirs or []
        self.component_prefix = component_prefix

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self) -> str:
        """Analyse sources, build test cases, and write the CSV file.

        Returns:
            Absolute path to the generated CSV file.
        """
        analyzer = CodeAnalyzer(
            source_paths=self.source_paths,
            root=self.root,
            skip_dirs=self.skip_dirs,
        )
        symbols = analyzer.analyse()
        test_cases = self._build_test_cases(symbols)
        generator = ZephyrCSVGenerator(test_cases=test_cases, output_path=self.output_csv)
        return generator.generate()

    def build_test_cases(self, symbols: List[SourceSymbol]) -> List[TestCase]:
        """Public wrapper around the internal builder (useful for testing)."""
        return self._build_test_cases(symbols)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_levels(raw: List) -> List[TestLevel]:
        result: List[TestLevel] = []
        for item in raw:
            if isinstance(item, TestLevel):
                result.append(item)
            else:
                # Case-insensitive match: find the enum member whose value
                # equals the supplied string (ignoring case).
                raw_str = str(item)
                matched = next(
                    (lv for lv in TestLevel if lv.value.lower() == raw_str.lower()),
                    None,
                )
                if matched is None:
                    raise ValueError(
                        f"Unknown test level {raw_str!r}. "
                        f"Valid values: {[lv.value for lv in TestLevel]}"
                    )
                result.append(matched)
        return result

    def _build_test_cases(self, symbols: List[SourceSymbol]) -> List[TestCase]:
        test_cases: List[TestCase] = []
        for symbol in symbols:
            for level in self.levels:
                tc = self._symbol_to_test_case(symbol, level)
                test_cases.append(tc)
        return test_cases

    def _symbol_to_test_case(self, symbol: SourceSymbol, level: TestLevel) -> TestCase:
        """Convert one :class:`SourceSymbol` + level into a :class:`TestCase`."""
        component = self._component_name(symbol)
        folder = f"/{level.value}/{symbol.module.replace('.', '/')}"

        objective = symbol.docstring or f"Verify that ``{symbol.name}`` works correctly."
        precondition = (
            "The Calibration Statistics Tool is installed and all dependencies are available."
        )

        tc = TestCase(
            name=f"[{level.value}] {symbol.module} — {symbol.name}",
            objective=objective,
            precondition=precondition,
            level=level,
            priority=_infer_priority(symbol),
            status=TestStatus.DRAFT,
            component=component,
            labels=[level.value, symbol.kind.capitalize(), symbol.module.split(".")[0]],
            folder=folder,
        )

        builder = _STEP_BUILDERS.get(level, _build_unit_steps)
        tc.steps = builder(symbol)
        return tc

    def _component_name(self, symbol: SourceSymbol) -> str:
        top_level = symbol.module.split(".")[0]
        return f"{self.component_prefix}/{top_level}"
