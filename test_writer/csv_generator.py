"""CSV export for Jira Zephyr Scale manual test cases.

Generates a CSV file in the format expected by the Zephyr Scale (formerly
TM4J) **CSV import** wizard.  The file can be uploaded directly from the
*Test Cases* list view → *Import* → *CSV*.

Column layout (one row per step)::

    Name | Status | Priority | Component | Labels | Precondition
         | Objective | Folder
         | Test Script (Step) | Test Script (Step Data)
         | Test Script (Expected Result)

When a test case has more than one step the *Name*, *Status*, *Priority*,
*Component*, *Labels*, *Precondition*, *Objective*, and *Folder* columns are
populated only for the **first** step row; subsequent rows for the same test
case leave those columns empty (this matches the Zephyr Scale import
convention).
"""
from __future__ import annotations

import csv
import os
from typing import List

from test_writer.models import TestCase, TestStep


# ---------------------------------------------------------------------------
# Column header constants (kept as a single source of truth)
# ---------------------------------------------------------------------------

_HEADERS = [
    "Name",
    "Status",
    "Priority",
    "Component",
    "Labels",
    "Precondition",
    "Objective",
    "Folder",
    "Test Script (Step)",
    "Test Script (Step Data)",
    "Test Script (Expected Result)",
]


class ZephyrCSVGenerator:
    """Serialise a list of :class:`~test_writer.models.TestCase` objects to CSV.

    Parameters:
        test_cases: Test cases to export.
        output_path: Filesystem path for the generated CSV file.
    """

    def __init__(self, test_cases: List[TestCase], output_path: str) -> None:
        self.test_cases = test_cases
        self.output_path = output_path

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(self) -> str:
        """Write the CSV file and return the absolute path.

        Raises:
            OSError: If the output directory cannot be created or the file
                     cannot be written.
        """
        os.makedirs(os.path.dirname(os.path.abspath(self.output_path)), exist_ok=True)

        with open(self.output_path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh, quoting=csv.QUOTE_ALL)
            writer.writerow(_HEADERS)

            for tc in self.test_cases:
                self._write_test_case(writer, tc)

        return os.path.abspath(self.output_path)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _write_test_case(self, writer: csv.writer, tc: TestCase) -> None:  # type: ignore[type-arg]
        """Write one :class:`TestCase` as one or more CSV rows."""
        steps = tc.steps if tc.steps else [TestStep(action="Execute the test.", expected="Verify the outcome.")]

        for idx, step in enumerate(steps):
            if idx == 0:
                # First row carries all test-case metadata
                row = [
                    tc.name,
                    tc.status.value,
                    tc.priority.value,
                    tc.component,
                    tc.label_string,
                    tc.precondition,
                    tc.objective,
                    tc.folder,
                    step.action,
                    step.data,
                    step.expected,
                ]
            else:
                # Continuation rows: only step columns are filled
                row = [
                    "",  # Name
                    "",  # Status
                    "",  # Priority
                    "",  # Component
                    "",  # Labels
                    "",  # Precondition
                    "",  # Objective
                    "",  # Folder
                    step.action,
                    step.data,
                    step.expected,
                ]
            writer.writerow(row)
