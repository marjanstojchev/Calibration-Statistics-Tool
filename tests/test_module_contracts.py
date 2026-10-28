"""Static checks that catch module wiring mismatches after the package refactor.

* ``alias.attr`` where ``alias`` is an internal module must name something that
  module really defines (e.g. the truncated AntennaSystemDiagrams had no
  ``start_data_evaluation``).
* Internal modules must be imported with their package path; a bare
  ``import powerpoint`` only works when run from the source folder.
"""
import ast
from pathlib import Path

PKG_NAME = "calibration_statistics_tool"
PKG_DIR = Path(__file__).resolve().parent.parent / PKG_NAME


def _py_files():
    return [p for p in PKG_DIR.rglob("*.py") if "__pycache__" not in p.parts]


def _module_name(path):
    rel = path.relative_to(PKG_DIR.parent).with_suffix("")
    parts = list(rel.parts)
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def _module_path(dotted):
    base = PKG_DIR.parent.joinpath(*dotted.split("."))
    if base.with_suffix(".py").is_file():
        return base.with_suffix(".py")
    if (base / "__init__.py").is_file():
        return base / "__init__.py"
    return None


_MODULES = {_module_name(p): p for p in _py_files()}
_TOP_LEVEL_NAMES = {n.rsplit(".", 1)[-1] for n in _MODULES} | {
    p.name for p in PKG_DIR.rglob("*") if p.is_dir() and (p / "__init__.py").exists()
}


def _defined_names(path):
    """Top-level names of a module, or None if it cannot be determined statically."""
    tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    names = set()
    dynamic = False

    def visit(body):
        nonlocal dynamic
        for node in body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                names.add(node.name)
                if node.name == "__getattr__":
                    dynamic = True
            elif isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                for t in targets:
                    for n in ast.walk(t):
                        if isinstance(n, ast.Name):
                            names.add(n.id)
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                for a in node.names:
                    if a.name == "*":
                        dynamic = True
                    else:
                        names.add((a.asname or a.name).split(".")[0])
            elif isinstance(node, (ast.For, ast.While, ast.If, ast.With, ast.Try)):
                for field in ("body", "orelse", "finalbody", "handlers"):
                    sub = getattr(node, field, None)
                    if sub:
                        visit([s for h in sub for s in (h.body if isinstance(h, ast.ExceptHandler) else [h])])
            if isinstance(node, (ast.For,)):
                for n in ast.walk(node.target):
                    if isinstance(n, ast.Name):
                        names.add(n.id)

    visit(tree.body)
    # Module-level setattr()/globals() writes make the name set open-ended.
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in ("setattr", "globals"):
            dynamic = True
        if isinstance(n, ast.Global):
            names.update(n.names)
    return None if dynamic else names


def _alias_map(tree):
    """alias -> dotted internal module name, for every import in the file.

    Also follows helpers like ``def _mod(): import pkg.m as x; return x`` and the
    assignments ``name = _mod()`` that bind their result.
    """
    aliases = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            for a in node.names:
                dotted = f"{node.module}.{a.name}"
                if dotted in _MODULES:
                    aliases[a.asname or a.name] = dotted
        elif isinstance(node, ast.Import):
            for a in node.names:
                if a.asname and a.name in _MODULES:
                    aliases[a.asname] = a.name

    returns_module = {}
    for fn in ast.walk(tree):
        if isinstance(fn, ast.FunctionDef):
            local = _alias_map_flat(fn)
            for r in ast.walk(fn):
                if isinstance(r, ast.Return) and isinstance(r.value, ast.Name) and r.value.id in local:
                    returns_module[fn.name] = local[r.value.id]
    bound = set()
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Assign)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Name)
            and node.value.func.id in returns_module
        ):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    aliases[t.id] = returns_module[node.value.func.id]
                    bound.add(t.id)
    return aliases, bound


def _alias_map_flat(fn):
    local = {}
    for node in ast.walk(fn):
        if isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            for a in node.names:
                if f"{node.module}.{a.name}" in _MODULES:
                    local[a.asname or a.name] = f"{node.module}.{a.name}"
        elif isinstance(node, ast.Import):
            for a in node.names:
                if a.asname and a.name in _MODULES:
                    local[a.asname] = a.name
    return local


def test_module_attribute_references_exist():
    cache = {}
    problems = []
    for path in _py_files():
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        aliases, bound = _alias_map(tree)
        if not aliases:
            continue
        shadowed = {
            n.id
            for n in ast.walk(tree)
            if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store) and n.id in aliases and n.id not in bound
        } | {a.arg for n in ast.walk(tree) if isinstance(n, ast.arguments)
             for a in n.args + n.kwonlyargs + n.posonlyargs if a.arg in aliases}
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Attribute)
                and isinstance(node.value, ast.Name)
                and node.value.id in aliases
                and node.value.id not in shadowed
            ):
                target = aliases[node.value.id]
                if target not in cache:
                    cache[target] = _defined_names(_MODULES[target])
                names = cache[target]
                if names is None:
                    continue
                if node.attr not in names and f"{target}.{node.attr}" not in _MODULES:
                    problems.append(
                        f"{_module_name(path)}:{node.lineno}: {node.value.id}.{node.attr} "
                        f"is not defined in {target}"
                    )
    assert not problems, "\n".join(sorted(set(problems)))


def test_from_imports_of_internal_modules_exist():
    cache = {}
    problems = []
    for path in _py_files():
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        for node in ast.walk(tree):
            if not (isinstance(node, ast.ImportFrom) and node.level == 0 and node.module in _MODULES):
                continue
            if node.module not in cache:
                cache[node.module] = _defined_names(_MODULES[node.module])
            names = cache[node.module]
            if names is None:
                continue
            for a in node.names:
                if a.name != "*" and a.name not in names and f"{node.module}.{a.name}" not in _MODULES:
                    problems.append(f"{_module_name(path)}:{node.lineno}: cannot import {a.name} from {node.module}")
    assert not problems, "\n".join(sorted(set(problems)))


def test_no_bare_imports_of_internal_modules():
    problems = []
    for path in _py_files():
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.Import):
                names = [a.name.split(".")[0] for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                names = [node.module.split(".")[0]]
            for n in names:
                if n != PKG_NAME and n in _TOP_LEVEL_NAMES:
                    problems.append(f"{_module_name(path)}:{node.lineno}: bare import of '{n}'")
    assert not problems, "\n".join(sorted(set(problems)))
