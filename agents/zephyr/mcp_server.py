"""MCP server for the Zephyr test-writer agent.

Exposes helper tools so that AI agents (GitHub Copilot, Claude Desktop,
Cursor, etc.) can read source files from the repo and write the generated
CSV — the AI itself does the test-case writing guided by
agents/zephyr/TEST_WRITER_AGENT.md.

Start the server (stdio transport)::

    python -m agents.zephyr.mcp_server

Or register it in ``.mcp.json`` / ``.vscode/mcp.json`` and let your IDE
start it automatically.
"""
from __future__ import annotations

import json
import os
import sys
from typing import List, Optional

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from mcp.server.fastmcp import FastMCP  # type: ignore[import-untyped]

mcp = FastMCP(
    "zephyr-test-writer",
    instructions=(
        "You are a QA engineer assistant for the Calibration Statistics Tool. "
        "Read source files with read_source_file and list_source_files, then "
        "write manual test cases as a Zephyr Scale CSV using write_csv. "
        "Follow the instructions in agents/zephyr/TEST_WRITER_AGENT.md for "
        "format and rules."
    ),
)


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@mcp.tool(description="List Python source files under a given directory path.")
def list_source_files(
    directory: str,
    skip_dirs: Optional[List[str]] = None,
) -> str:
    """Return a JSON list of .py file paths found under *directory*.

    Args:
        directory:  Directory to walk (relative to repo root or absolute).
        skip_dirs:  Directory names to skip (e.g. ["__pycache__", "tests"]).

    Returns:
        JSON list of relative file paths.
    """
    skip = set(skip_dirs or ["__pycache__", ".git", "test_writer"])
    base = directory if os.path.isabs(directory) else os.path.join(_ROOT, directory)
    found: List[str] = []
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if d not in skip]
        for fname in filenames:
            if fname.endswith(".py"):
                full = os.path.join(dirpath, fname)
                found.append(os.path.relpath(full, _ROOT))
    return json.dumps(found)


@mcp.tool(description="Read the contents of a source file.")
def read_source_file(file_path: str) -> str:
    """Return the text content of *file_path*.

    Args:
        file_path: Path relative to repo root or absolute.

    Returns:
        File contents as a plain string.
    """
    full = file_path if os.path.isabs(file_path) else os.path.join(_ROOT, file_path)
    with open(full, encoding="utf-8") as fh:
        return fh.read()


@mcp.tool(description="Write the AI-generated Zephyr CSV content to a file.")
def write_csv(content: str, output_path: str = "zephyr_tests.csv") -> str:
    """Save *content* (a complete Zephyr Scale CSV string) to *output_path*.

    Args:
        content:     Full CSV text to write (UTF-8, all fields quoted).
        output_path: Destination file path (default: zephyr_tests.csv).

    Returns:
        Absolute path of the written file.
    """
    full = output_path if os.path.isabs(output_path) else os.path.join(_ROOT, output_path)
    os.makedirs(os.path.dirname(full) or ".", exist_ok=True)
    with open(full, "w", encoding="utf-8") as fh:
        fh.write(content)
    return full


@mcp.tool(description="List all supported Zephyr test levels.")
def list_test_levels() -> str:
    """Return a JSON list of valid test level strings."""
    return json.dumps(["Unit", "Integration", "System", "Smoke", "Regression", "Acceptance"])


_DEFAULT_PROJECT_KEY = "PST"
_DEFAULT_BASE_URL = "https://api.zephyrscale.smartbear.com/v2"


@mcp.tool(description="Import a generated CSV file directly into Jira Zephyr Scale Cloud.")
def import_to_zephyr(
    csv_path: str,
    project_key: Optional[str] = None,
    token: Optional[str] = None,
    base_url: Optional[str] = None,
) -> str:
    """Upload *csv_path* to Zephyr Scale Cloud and start the import job.

    Credentials are resolved in this order:
      1. Explicit argument passed by the caller.
      2. Environment variables: ZEPHYR_TOKEN, ZEPHYR_PROJECT_KEY, ZEPHYR_BASE_URL.
      3. Hardcoded defaults: project_key='PST', base_url=Zephyr Scale Cloud API.

    Args:
        csv_path:    Path to the CSV file (absolute or relative to repo root).
        project_key: Jira project key. Defaults to ZEPHYR_PROJECT_KEY env var or 'PST'.
        token:       Zephyr Scale API token. Defaults to ZEPHYR_TOKEN env var.
        base_url:    API base URL. Defaults to ZEPHYR_BASE_URL env var or Cloud URL.

    Returns:
        JSON string with the API response (includes import job status URL).
    """
    from agents.zephyr.zephyr_client import import_csv

    resolved_token = token or os.environ.get("ZEPHYR_TOKEN")
    resolved_project = project_key or os.environ.get("ZEPHYR_PROJECT_KEY") or _DEFAULT_PROJECT_KEY
    resolved_url = base_url or os.environ.get("ZEPHYR_BASE_URL") or _DEFAULT_BASE_URL

    if not resolved_token:
        return json.dumps({"error": "No Zephyr token provided. Set the ZEPHYR_TOKEN environment variable or pass token explicitly."})

    full_path = csv_path if os.path.isabs(csv_path) else os.path.join(_ROOT, csv_path)
    result = import_csv(
        csv_path=full_path,
        project_key=resolved_project,
        token=resolved_token,
        base_url=resolved_url,
    )
    return json.dumps(result, indent=2)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def run_server() -> None:
    """Start the MCP server using stdio transport (used by most MCP clients)."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    run_server()
