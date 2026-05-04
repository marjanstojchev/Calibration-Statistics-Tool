"""MCP server for the Zephyr test-writer agent.

Exposes the test-writer capabilities as MCP tools so that cloud AI agents
(GitHub Copilot, Claude Desktop, Cursor, etc.) can call them directly via
the Model Context Protocol.

Start the server (stdio transport, used by most MCP clients)::

    python -m test_writer.mcp_server

Or register it in ``.mcp.json`` / ``.vscode/mcp.json`` and let your IDE
start it automatically.
"""
from __future__ import annotations

import json
import os
import sys
from typing import List, Optional

# ---------------------------------------------------------------------------
# Ensure the repo root is on sys.path when launched as __main__
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from mcp.server.fastmcp import FastMCP  # type: ignore[import-untyped]

from test_writer.agent import TestWriterAgent
from test_writer.code_analyzer import CodeAnalyzer
from test_writer.models import TestLevel

# ---------------------------------------------------------------------------
# Server instance
# ---------------------------------------------------------------------------

mcp = FastMCP(
    "zephyr-test-writer",
    instructions=(
        "Generate Jira Zephyr Scale manual test cases from Python source files. "
        "Use generate_test_csv to produce an importable CSV file, "
        "analyze_source to inspect discovered symbols, or "
        "list_test_levels to see available test levels."
    ),
)


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@mcp.tool(
    description=(
        "Analyse Python source files and generate a Jira Zephyr Scale CSV file "
        "containing manual test cases. Returns the path to the generated CSV."
    )
)
def generate_test_csv(
    source_paths: List[str],
    output_csv: str = "zephyr_tests.csv",
    levels: Optional[List[str]] = None,
    component_prefix: str = "Calibration-Statistics-Tool",
    skip_dirs: Optional[List[str]] = None,
) -> str:
    """Generate a Zephyr Scale CSV from Python source files.

    Args:
        source_paths:      List of directories or .py files to analyse.
        output_csv:        Output CSV file path.
        levels:            Test levels to generate (e.g. ["Unit", "Integration"]).
                           Defaults to ["Unit", "Integration"].
        component_prefix:  Jira component name prefix.
        skip_dirs:         Directory names to skip during source walking.

    Returns:
        Absolute path to the generated CSV file.
    """
    agent = TestWriterAgent(
        source_paths=source_paths,
        levels=levels or ["Unit", "Integration"],
        output_csv=output_csv,
        root=_ROOT,
        skip_dirs=skip_dirs,
        component_prefix=component_prefix,
    )
    return agent.run()


@mcp.tool(
    description=(
        "Analyse Python source files and return a JSON summary of all discovered "
        "public symbols (modules, classes, functions/methods)."
    )
)
def analyze_source(
    source_paths: List[str],
    skip_dirs: Optional[List[str]] = None,
) -> str:
    """Discover public symbols in Python source files.

    Args:
        source_paths: Directories or .py files to scan.
        skip_dirs:    Directory names to skip.

    Returns:
        JSON string — list of symbol objects with keys:
        kind, name, module, file_path, docstring, args, lineno.
    """
    analyzer = CodeAnalyzer(
        source_paths=source_paths,
        root=_ROOT,
        skip_dirs=skip_dirs,
    )
    symbols = analyzer.analyse()
    result = [
        {
            "kind": s.kind,
            "name": s.name,
            "module": s.module,
            "file_path": s.file_path,
            "docstring": s.docstring,
            "args": s.args,
            "lineno": s.lineno,
        }
        for s in symbols
    ]
    return json.dumps(result, indent=2)


@mcp.tool(
    description="List all supported Zephyr test levels that can be used with generate_test_csv."
)
def list_test_levels() -> str:
    """Return all available test levels.

    Returns:
        JSON list of valid level strings.
    """
    return json.dumps([lv.value for lv in TestLevel])


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="stdio")
