"""AST-based Python code analyser for the test-writer agent.

Walks a set of source paths, parses every ``*.py`` file, and returns a list
of :class:`SourceSymbol` objects describing the public API (modules, classes,
and functions/methods) found.  These symbols are later consumed by
:mod:`test_writer.agent` to generate :class:`~test_writer.models.TestCase`
templates.
"""
from __future__ import annotations

import ast
import os
from dataclasses import dataclass, field
from typing import List, Optional


# ---------------------------------------------------------------------------
# Data structures produced by the analyser
# ---------------------------------------------------------------------------

@dataclass
class SourceSymbol:
    """Represents a public symbol discovered in the Python source tree.

    Attributes:
        kind:        ``"module"``, ``"class"``, or ``"function"``.
        name:        Fully-qualified name within its module, e.g.
                     ``ParseController.load_protocol``.
        module:      Dotted module path, e.g. ``shared.parse_controller``.
        file_path:   Absolute (or relative) filesystem path to the source file.
        docstring:   First docstring paragraph, if present; otherwise ``""``.
        args:        Parameter names for functions/methods (excluding *self*).
        lineno:      Line number where the symbol is defined.
        parent_class: Name of the enclosing class, or ``None`` for top-level.
    """

    kind: str
    name: str
    module: str
    file_path: str
    docstring: str = ""
    args: List[str] = field(default_factory=list)
    lineno: int = 0
    parent_class: Optional[str] = None


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _first_docstring(node: ast.AST) -> str:
    """Return the first paragraph of the docstring of *node*, or ``""``."""
    doc = ast.get_docstring(node)
    if not doc:
        return ""
    return doc.splitlines()[0].strip()


def _is_public(name: str) -> bool:
    """Return ``True`` if *name* does not start with an underscore."""
    return not name.startswith("_")


def _module_name(file_path: str, root: str) -> str:
    """Convert a file path to a dotted module name relative to *root*."""
    rel = os.path.relpath(file_path, root)
    # Strip .py suffix and replace separators
    parts = rel.replace("\\", "/").replace("/", ".").rstrip(".")
    if parts.endswith(".py"):
        parts = parts[:-3]
    return parts


# ---------------------------------------------------------------------------
# Public analyser
# ---------------------------------------------------------------------------

class CodeAnalyzer:
    """Walk source paths and extract public symbols.

    Parameters:
        source_paths: Directories or individual ``.py`` files to scan.
        root:         Repository root used to build dotted module names.
                      Defaults to ``os.getcwd()``.
        skip_dirs:    Directory names to ignore (e.g. ``tests``, ``docs``).
    """

    _DEFAULT_SKIP: tuple = (
        ".git", ".venv", "venv", "__pycache__", "node_modules",
        "dist", "build", ".eggs",
    )

    def __init__(
        self,
        source_paths: List[str],
        root: Optional[str] = None,
        skip_dirs: Optional[List[str]] = None,
    ) -> None:
        self.source_paths = [os.path.abspath(p) for p in source_paths]
        self.root = os.path.abspath(root) if root else os.getcwd()
        self.skip_dirs: tuple = self._DEFAULT_SKIP + tuple(skip_dirs or [])

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def analyse(self) -> List[SourceSymbol]:
        """Return all public symbols found in :attr:`source_paths`."""
        symbols: List[SourceSymbol] = []
        for path in self.source_paths:
            if os.path.isfile(path):
                symbols.extend(self._analyse_file(path))
            elif os.path.isdir(path):
                for py_file in self._iter_python_files(path):
                    symbols.extend(self._analyse_file(py_file))
        return symbols

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _iter_python_files(self, directory: str):
        """Yield ``*.py`` paths under *directory*, skipping :attr:`skip_dirs`."""
        for dirpath, dirnames, filenames in os.walk(directory):
            # Prune unwanted directories in-place
            dirnames[:] = [
                d for d in dirnames
                if d not in self.skip_dirs and not d.startswith(".")
            ]
            for fname in filenames:
                if fname.endswith(".py"):
                    yield os.path.join(dirpath, fname)

    def _analyse_file(self, file_path: str) -> List[SourceSymbol]:
        """Parse one ``.py`` file and return its public symbols."""
        try:
            with open(file_path, encoding="utf-8", errors="replace") as fh:
                source = fh.read()
            tree = ast.parse(source, filename=file_path)
        except SyntaxError:
            return []

        module_name = _module_name(file_path, self.root)
        symbols: List[SourceSymbol] = []

        # Module-level symbol
        symbols.append(
            SourceSymbol(
                kind="module",
                name=module_name,
                module=module_name,
                file_path=file_path,
                docstring=_first_docstring(tree),
            )
        )

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and _is_public(node.name):
                symbols.append(
                    SourceSymbol(
                        kind="class",
                        name=node.name,
                        module=module_name,
                        file_path=file_path,
                        docstring=_first_docstring(node),
                        lineno=node.lineno,
                    )
                )
                # Methods inside the class
                for item in node.body:
                    if (
                        isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                        and _is_public(item.name)
                    ):
                        args = self._extract_args(item)
                        symbols.append(
                            SourceSymbol(
                                kind="function",
                                name=f"{node.name}.{item.name}",
                                module=module_name,
                                file_path=file_path,
                                docstring=_first_docstring(item),
                                args=args,
                                lineno=item.lineno,
                                parent_class=node.name,
                            )
                        )

            elif (
                isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                and _is_public(node.name)
            ):
                # Only include top-level functions (not inside a class)
                # Check parent is the module, not a class
                args = self._extract_args(node)
                symbols.append(
                    SourceSymbol(
                        kind="function",
                        name=node.name,
                        module=module_name,
                        file_path=file_path,
                        docstring=_first_docstring(node),
                        args=args,
                        lineno=node.lineno,
                        parent_class=None,
                    )
                )

        return symbols

    @staticmethod
    def _extract_args(func_node: "ast.FunctionDef | ast.AsyncFunctionDef") -> List[str]:
        """Return parameter names for *func_node*, excluding *self* / *cls*."""
        skip = {"self", "cls"}
        return [
            arg.arg
            for arg in func_node.args.args
            if arg.arg not in skip
        ]
