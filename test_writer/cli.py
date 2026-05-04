"""Command-line interface for the test-writer agent.

Usage::

    python -m test_writer.cli [OPTIONS]

Options:
    --source      One or more source paths (directories or .py files).
                  May be specified multiple times. Default: current directory.
    --level       Testing level to generate: Unit, Integration, System,
                  Smoke, Regression, Acceptance.
                  May be specified multiple times.
                  Default: Unit, Integration.
    --output      Output CSV file path. Default: zephyr_tests.csv
    --root        Repository root for module-name resolution.
                  Default: current working directory.
    --prefix      Jira component prefix. Default: Calibration-Statistics-Tool
    --skip-dir    Directory name to skip (e.g. tests). May be repeated.

Example::

    python -m test_writer.cli \\
        --source shared/ \\
        --source ui/handlers/ \\
        --level Unit \\
        --level Integration \\
        --output output/zephyr_tests.csv
"""
from __future__ import annotations

import argparse
import sys
from typing import List

from test_writer.agent import TestWriterAgent
from test_writer.models import TestLevel


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="test-writer",
        description="Generate Jira Zephyr manual test cases from Python source files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--source",
        dest="sources",
        metavar="PATH",
        action="append",
        default=[],
        help="Source path (directory or .py file). May be repeated.",
    )
    parser.add_argument(
        "--level",
        dest="levels",
        metavar="LEVEL",
        action="append",
        default=[],
        choices=[lv.value for lv in TestLevel],
        help=(
            f"Testing level to generate. Choices: "
            f"{', '.join(lv.value for lv in TestLevel)}. May be repeated."
        ),
    )
    parser.add_argument(
        "--output",
        dest="output",
        metavar="FILE",
        default="zephyr_tests.csv",
        help="Output CSV file path (default: zephyr_tests.csv).",
    )
    parser.add_argument(
        "--root",
        dest="root",
        metavar="DIR",
        default=None,
        help="Repository root for module-name resolution (default: cwd).",
    )
    parser.add_argument(
        "--prefix",
        dest="prefix",
        metavar="PREFIX",
        default="Calibration-Statistics-Tool",
        help="Jira component prefix (default: Calibration-Statistics-Tool).",
    )
    parser.add_argument(
        "--skip-dir",
        dest="skip_dirs",
        metavar="NAME",
        action="append",
        default=[],
        help="Directory name to skip. May be repeated.",
    )
    return parser


def main(argv: List[str] | None = None) -> int:
    """Entry point; returns an exit code."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    sources = args.sources or ["."]
    levels = [TestLevel(lv) for lv in args.levels] if args.levels else None

    agent = TestWriterAgent(
        source_paths=sources,
        levels=levels,
        output_csv=args.output,
        root=args.root,
        skip_dirs=args.skip_dirs or None,
        component_prefix=args.prefix,
    )

    output_path = agent.run()
    print(f"✓ Generated {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
