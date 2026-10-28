"""Regression tests: parse handlers must work when the package is installed.

``_load_protocol_data`` used to do ``import TxAntDiagrams`` (a bare import that only
worked from the old flat layout).  The exception was swallowed inside a Qt slot, so the
Accepted Protocols table stayed empty.  Other tests patch ``_load_protocol_data`` out,
so nothing exercised that import.
"""
import ast
import pathlib
from unittest.mock import MagicMock

from calibration_statistics_tool.ui.handlers import parse_handlers

HANDLERS_DIR = pathlib.Path(parse_handlers.__file__).parent
PACKAGE_DIR = HANDLERS_DIR.parent.parent
# Bare imports of these modules work only through sys.path hacks in the UI package.
SYS_PATH_OK = {"ui_constants", "tabs", "widgets"}


def test_load_protocol_data_runs_real_imports():
    ctx = MagicMock()
    result = parse_handlers._load_protocol_data(ctx, [], [], "", 0)
    assert result == ([], [], [], [])


def test_handlers_have_no_bare_package_imports():
    internal = {p.stem for p in PACKAGE_DIR.rglob("*.py")} | {
        p.name for p in PACKAGE_DIR.rglob("*") if p.is_dir()
    }
    internal -= {PACKAGE_DIR.name}
    offenders = []
    for path in HANDLERS_DIR.glob("*.py"):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Import):
                names = [a.name.split(".")[0] for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                names = [node.module.split(".")[0]]
            else:
                continue
            offenders += [
                f"{path.name}:{node.lineno} {n}"
                for n in names
                if n in internal and n not in SYS_PATH_OK
            ]
    assert not offenders, offenders
