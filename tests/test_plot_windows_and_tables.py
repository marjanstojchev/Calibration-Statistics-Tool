"""Regression tests for the plot frames, plot-window placement and interactive table items."""
import ast
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from PySide6.QtWidgets import QSizePolicy, QTableWidget, QTableWidgetItem

PKG_DIR = Path(__file__).resolve().parent.parent / "calibration_statistics_tool"


def test_no_qt_item_copy_constructor_calls():
    """PySide6 items have no copy constructor: QTableWidgetItem(tableItem) raises TypeError."""
    problems = []
    for path in PKG_DIR.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or len(node.args) != 1:
                continue
            func = node.func
            name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", "")
            arg = node.args[0]
            if name == "QTableWidgetItem" and isinstance(arg, ast.Name) and arg.id.lower().endswith("item"):
                problems.append(f"{path.name}:{node.lineno}")
    assert not problems, "QTableWidgetItem copy-constructor used at " + ", ".join(problems)


def test_table_item_can_be_set_directly():
    table = QTableWidget(2, 2)
    item = QTableWidgetItem("x")
    table.setItem(0, 1, item)
    assert table.item(0, 1) is item


@pytest.mark.parametrize("frame_name", ["PlotFrame", "PlotFrameSysDia"])
def test_plot_frame_does_not_force_huge_minimum_size(frame_name):
    from calibration_statistics_tool.ui import widgets

    frame = getattr(widgets, frame_name)()
    assert frame.sizePolicy().verticalPolicy() == QSizePolicy.Expanding
    assert frame.canvas.sizePolicy().verticalPolicy() == QSizePolicy.Expanding
    assert frame.minimumSizeHint().height() < 700
    assert frame.minimumSizeHint().width() < 1000


@pytest.mark.parametrize("frame_name", ["PlotFrame", "PlotFrameSysDia"])
def test_embedded_figures_are_not_registered_in_pyplot(frame_name):
    import matplotlib.pyplot as plt
    from calibration_statistics_tool.ui import widgets

    before = set(plt.get_fignums())
    getattr(widgets, frame_name)()
    assert set(plt.get_fignums()) == before


def test_show_plot_window_cascades_and_resets(monkeypatch):
    from calibration_statistics_tool.shared import plotdata

    moves = []
    window = MagicMock()
    window.screen.return_value.availableGeometry.return_value = MagicMock(x=lambda: 0, y=lambda: 0)
    window.move.side_effect = lambda x, y: moves.append((x, y))
    fig = MagicMock()
    fig.canvas.manager.window = window
    shown = []
    monkeypatch.setattr(plotdata.plt, "show", lambda: shown.append(1))

    plotdata._windowCascade["count"] = 0
    for _ in range(3):
        plotdata.showPlotWindow(fig)

    assert len(shown) == 3
    assert len(set(moves)) == 3
    assert all(x >= plotdata._DIAGRAM_WINDOW_X for x, _ in moves)

    # More windows than the cascade length wrap around instead of walking off-screen.
    for _ in range(plotdata._CASCADE_LENGTH):
        plotdata.showPlotWindow(fig)
    assert max(x for x, _ in moves) <= plotdata._DIAGRAM_WINDOW_X + plotdata._CASCADE_LENGTH * plotdata._CASCADE_STEP


def test_show_plot_window_tolerates_non_qt_backend(monkeypatch):
    from calibration_statistics_tool.shared import plotdata

    shown = []
    monkeypatch.setattr(plotdata.plt, "show", lambda: shown.append(1))
    plotdata.showPlotWindow(object())
    assert shown == [1]
