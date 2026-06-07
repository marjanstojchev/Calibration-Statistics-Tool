"""AppContext — lightweight dependency-injection container.

Holds references to the three shared service objects that every handler
module needs.  Instantiated once in main.py and passed into each handler
module's ``wire()`` function.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from calibration_statistics_tool.shared.parse_controller import ParseController
    from calibration_statistics_tool.shared.plot_controller import PlotController
    from calibration_statistics_tool.ui.main_view import MainView


@dataclass
class AppContext:
    """Dependency container passed to all handler modules."""

    qt:  object          # MainView / pyside_qtgui proxy (any attribute access delegated)
    mv:  "MainView"      # typed MainView for set_*/get_* helpers
    plc: "PlotController"
    pc:  "ParseController"
