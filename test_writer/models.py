"""Data models for the test-writer agent.

Defines :class:`TestCase`, :class:`TestStep`, and the enumerations used to
categorise tests (:class:`TestLevel`, :class:`TestPriority`,
:class:`TestStatus`).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List


class TestLevel(str, Enum):
    """Testing level / layer the test case targets."""

    UNIT = "Unit"
    INTEGRATION = "Integration"
    SYSTEM = "System"
    SMOKE = "Smoke"
    REGRESSION = "Regression"
    ACCEPTANCE = "Acceptance"


class TestPriority(str, Enum):
    """Jira priority mapping."""

    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class TestStatus(str, Enum):
    """Zephyr Scale test-case status values."""

    DRAFT = "Draft"
    APPROVED = "Approved"
    DEPRECATED = "Deprecated"


@dataclass
class TestStep:
    """A single step inside a manual test case.

    Attributes:
        action:   What the tester should do.
        data:     Optional input data or test values.
        expected: The expected outcome / result.
    """

    action: str
    data: str = ""
    expected: str = ""


@dataclass
class TestCase:
    """A Jira Zephyr Scale manual test case.

    Attributes:
        name:         Unique, human-readable name shown in Jira.
        objective:    One-sentence description of what is being verified.
        precondition: State the system must be in before execution.
        level:        Testing layer this case belongs to.
        priority:     Triage priority.
        status:       Lifecycle status in Zephyr.
        component:    Jira component name (maps to a source module).
        labels:       Free-form Jira labels.
        folder:       Zephyr folder path, e.g. ``/Unit/shared``.
        steps:        Ordered list of :class:`TestStep` objects.
    """

    name: str
    objective: str = ""
    precondition: str = ""
    level: TestLevel = TestLevel.UNIT
    priority: TestPriority = TestPriority.MEDIUM
    status: TestStatus = TestStatus.DRAFT
    component: str = ""
    labels: List[str] = field(default_factory=list)
    folder: str = ""
    steps: List[TestStep] = field(default_factory=list)

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    def add_step(
        self,
        action: str,
        data: str = "",
        expected: str = "",
    ) -> "TestCase":
        """Append a step and return *self* for chaining."""
        self.steps.append(TestStep(action=action, data=data, expected=expected))
        return self

    @property
    def label_string(self) -> str:
        """Return labels joined with a comma, ready for CSV export."""
        return ", ".join(self.labels)
