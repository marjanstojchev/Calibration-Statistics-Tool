"""Tests for the test_writer package.

Covers:
- TestCase / TestStep model behaviour
- CodeAnalyzer symbol extraction
- ZephyrCSVGenerator CSV output
- TestWriterAgent end-to-end
"""
from __future__ import annotations

import csv
import os
import sys
import textwrap

# Ensure the repo root is on sys.path so test_writer is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_writer.models import (  # noqa: E402
    TestCase,
    TestStep,
    TestLevel,
    TestPriority,
    TestStatus,
)
from test_writer.code_analyzer import CodeAnalyzer, SourceSymbol, _module_name  # noqa: E402
from test_writer.csv_generator import ZephyrCSVGenerator  # noqa: E402
from test_writer.agent import TestWriterAgent  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_py(tmp_path, filename, source):
    """Write *source* to *tmp_path/filename* and return the full path."""
    p = tmp_path / filename
    p.write_text(textwrap.dedent(source), encoding="utf-8")
    return str(p)


# ---------------------------------------------------------------------------
# models.py
# ---------------------------------------------------------------------------

class TestTestCaseModel:
    def test_default_status_is_draft(self):
        tc = TestCase(name="TC-001")
        assert tc.status == TestStatus.DRAFT

    def test_add_step_chaining(self):
        tc = TestCase(name="TC-002")
        result = tc.add_step("Do something", "input", "expected")
        assert result is tc
        assert len(tc.steps) == 1
        step = tc.steps[0]
        assert step.action == "Do something"
        assert step.data == "input"
        assert step.expected == "expected"

    def test_label_string_empty(self):
        tc = TestCase(name="TC-003")
        assert tc.label_string == ""

    def test_label_string_multiple(self):
        tc = TestCase(name="TC-004", labels=["Unit", "Function", "shared"])
        assert tc.label_string == "Unit, Function, shared"

    def test_test_step_defaults(self):
        step = TestStep(action="Press the button.")
        assert step.data == ""
        assert step.expected == ""


# ---------------------------------------------------------------------------
# code_analyzer.py
# ---------------------------------------------------------------------------

class TestModuleName:
    def test_simple_file(self, tmp_path):
        root = str(tmp_path)
        file_path = str(tmp_path / "mymodule.py")
        assert _module_name(file_path, root) == "mymodule"

    def test_nested_file(self, tmp_path):
        root = str(tmp_path)
        file_path = str(tmp_path / "shared" / "parser.py")
        assert _module_name(file_path, root) == "shared.parser"


class TestCodeAnalyzer:
    def test_detects_class_and_method(self, tmp_path):
        src = """\
            class MyClass:
                \"\"\"A sample class.\"\"\"
                def my_method(self, x, y):
                    \"\"\"Return x + y.\"\"\"
                    return x + y
        """
        py = _write_py(tmp_path, "sample.py", src)
        analyzer = CodeAnalyzer(source_paths=[py], root=str(tmp_path))
        symbols = analyzer.analyse()

        kinds = {s.kind for s in symbols}
        names = {s.name for s in symbols}

        assert "class" in kinds
        assert "function" in kinds
        assert "MyClass" in names
        assert "MyClass.my_method" in names

    def test_method_args_exclude_self(self, tmp_path):
        src = """\
            class Foo:
                def bar(self, a, b):
                    pass
        """
        py = _write_py(tmp_path, "foo.py", src)
        analyzer = CodeAnalyzer(source_paths=[py], root=str(tmp_path))
        symbols = analyzer.analyse()

        method = next(s for s in symbols if s.name == "Foo.bar")
        assert method.args == ["a", "b"]

    def test_private_symbols_excluded(self, tmp_path):
        src = """\
            def _helper():
                pass
            class _Internal:
                pass
        """
        py = _write_py(tmp_path, "private_mod.py", src)
        analyzer = CodeAnalyzer(source_paths=[py], root=str(tmp_path))
        symbols = analyzer.analyse()

        names = {s.name for s in symbols}
        assert "_helper" not in names
        assert "_Internal" not in names

    def test_module_symbol_always_present(self, tmp_path):
        src = "x = 1\n"
        py = _write_py(tmp_path, "simple.py", src)
        analyzer = CodeAnalyzer(source_paths=[py], root=str(tmp_path))
        symbols = analyzer.analyse()

        assert any(s.kind == "module" for s in symbols)

    def test_skip_dirs(self, tmp_path):
        skip_dir = tmp_path / "skip_me"
        skip_dir.mkdir()
        _write_py(skip_dir, "skipped.py", "def public(): pass\n")

        keep_dir = tmp_path / "keep_me"
        keep_dir.mkdir()
        _write_py(keep_dir, "kept.py", "def kept_func(): pass\n")

        analyzer = CodeAnalyzer(
            source_paths=[str(tmp_path)],
            root=str(tmp_path),
            skip_dirs=["skip_me"],
        )
        symbols = analyzer.analyse()
        names = {s.name for s in symbols}
        assert "public" not in names
        assert "kept_func" in names

    def test_syntax_error_file_skipped(self, tmp_path):
        bad = tmp_path / "bad.py"
        bad.write_text("def (: pass\n", encoding="utf-8")
        analyzer = CodeAnalyzer(source_paths=[str(bad)], root=str(tmp_path))
        symbols = analyzer.analyse()
        # Should return empty list without raising
        assert symbols == []

    def test_directory_scan(self, tmp_path):
        src = """\
            def top_func():
                pass
        """
        _write_py(tmp_path, "scan_me.py", src)
        analyzer = CodeAnalyzer(source_paths=[str(tmp_path)], root=str(tmp_path))
        symbols = analyzer.analyse()
        assert any(s.name == "top_func" for s in symbols)


# ---------------------------------------------------------------------------
# csv_generator.py
# ---------------------------------------------------------------------------

class TestZephyrCSVGenerator:
    def _generate(self, test_cases, tmp_path):
        out = str(tmp_path / "output.csv")
        gen = ZephyrCSVGenerator(test_cases=test_cases, output_path=out)
        return gen.generate(), out

    def test_output_file_created(self, tmp_path):
        tc = TestCase(name="TC-001")
        tc.add_step("Step 1", "data", "expected")
        path, out = self._generate([tc], tmp_path)
        assert os.path.isfile(path)

    def test_header_row(self, tmp_path):
        path, _ = self._generate([], tmp_path)
        with open(path, newline="", encoding="utf-8") as fh:
            reader = csv.reader(fh)
            header = next(reader)
        assert "Name" in header
        assert "Test Script (Step)" in header
        assert "Test Script (Expected Result)" in header

    def test_single_step_row(self, tmp_path):
        tc = TestCase(
            name="My Test",
            objective="Verify X",
            priority=TestPriority.HIGH,
            status=TestStatus.DRAFT,
        )
        tc.add_step("Do X", "input_data", "result_ok")
        path, _ = self._generate([tc], tmp_path)

        with open(path, newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))

        assert len(rows) == 1
        assert rows[0]["Name"] == "My Test"
        assert rows[0]["Test Script (Step)"] == "Do X"
        assert rows[0]["Test Script (Expected Result)"] == "result_ok"

    def test_multi_step_continuation_rows(self, tmp_path):
        tc = TestCase(name="Multi-Step TC")
        tc.add_step("Step A", expected="Result A")
        tc.add_step("Step B", expected="Result B")
        tc.add_step("Step C", expected="Result C")
        path, _ = self._generate([tc], tmp_path)

        with open(path, newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))

        assert len(rows) == 3
        assert rows[0]["Name"] == "Multi-Step TC"
        # Continuation rows must have empty Name
        assert rows[1]["Name"] == ""
        assert rows[2]["Name"] == ""

    def test_empty_test_case_gets_default_step(self, tmp_path):
        tc = TestCase(name="No Steps TC")
        path, _ = self._generate([tc], tmp_path)

        with open(path, newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))

        assert len(rows) == 1
        assert rows[0]["Test Script (Step)"] != ""

    def test_multiple_test_cases(self, tmp_path):
        cases = [TestCase(name=f"TC-{i}") for i in range(5)]
        path, _ = self._generate(cases, tmp_path)

        with open(path, newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))

        assert len(rows) == 5


# ---------------------------------------------------------------------------
# agent.py
# ---------------------------------------------------------------------------

class TestTestWriterAgent:
    def test_run_produces_csv(self, tmp_path):
        src = """\
            def add(a, b):
                \"\"\"Return a + b.\"\"\"
                return a + b
        """
        _write_py(tmp_path, "math_utils.py", src)
        out = str(tmp_path / "out.csv")

        agent = TestWriterAgent(
            source_paths=[str(tmp_path)],
            levels=[TestLevel.UNIT],
            output_csv=out,
            root=str(tmp_path),
        )
        result = agent.run()
        assert os.path.isfile(result)

    def test_run_contains_function_name(self, tmp_path):
        src = "def greet(name): pass\n"
        _write_py(tmp_path, "greetings.py", src)
        out = str(tmp_path / "out.csv")

        agent = TestWriterAgent(
            source_paths=[str(tmp_path)],
            levels=[TestLevel.UNIT],
            output_csv=out,
            root=str(tmp_path),
        )
        agent.run()

        with open(out, encoding="utf-8") as fh:
            content = fh.read()
        assert "greet" in content

    def test_multiple_levels_generate_multiple_rows(self, tmp_path):
        src = "def fn(): pass\n"
        _write_py(tmp_path, "mod.py", src)
        out = str(tmp_path / "out.csv")

        agent = TestWriterAgent(
            source_paths=[str(tmp_path)],
            levels=[TestLevel.UNIT, TestLevel.INTEGRATION, TestLevel.SYSTEM],
            output_csv=out,
            root=str(tmp_path),
        )
        agent.run()

        with open(out, newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))

        # Each symbol × 3 levels → at least 3 name-bearing rows
        named = [r for r in rows if r["Name"]]
        assert len(named) >= 3

    def test_string_level_parsing(self, tmp_path):
        out = str(tmp_path / "out.csv")
        agent = TestWriterAgent(
            source_paths=[str(tmp_path)],
            levels=["Unit", "System"],
            output_csv=out,
            root=str(tmp_path),
        )
        assert agent.levels == [TestLevel.UNIT, TestLevel.SYSTEM]

    def test_string_level_parsing_case_insensitive(self, tmp_path):
        out = str(tmp_path / "out.csv")
        agent = TestWriterAgent(
            source_paths=[str(tmp_path)],
            levels=["unit", "INTEGRATION", "sYsTeM"],
            output_csv=out,
            root=str(tmp_path),
        )
        assert agent.levels == [TestLevel.UNIT, TestLevel.INTEGRATION, TestLevel.SYSTEM]

    def test_invalid_level_raises(self, tmp_path):
        import pytest
        with pytest.raises(ValueError, match="Unknown test level"):
            TestWriterAgent(
                source_paths=[str(tmp_path)],
                levels=["NotALevel"],
                output_csv=str(tmp_path / "out.csv"),
                root=str(tmp_path),
            )

    def test_build_test_cases_returns_list(self, tmp_path):
        agent = TestWriterAgent(
            source_paths=[str(tmp_path)],
            levels=[TestLevel.UNIT],
            output_csv=str(tmp_path / "out.csv"),
            root=str(tmp_path),
        )
        symbol = SourceSymbol(
            kind="function",
            name="my_func",
            module="mymod",
            file_path="mymod.py",
            docstring="Does something.",
            args=["x"],
        )
        cases = agent.build_test_cases([symbol])
        assert len(cases) == 1
        assert cases[0].level == TestLevel.UNIT
        assert "my_func" in cases[0].name
