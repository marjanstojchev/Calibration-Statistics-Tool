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


class _Geometry:
    def __init__(self, width=1920, height=1080):
        self._w, self._h = width, height

    def x(self):
        return 0

    def y(self):
        return 0

    def width(self):
        return self._w

    def height(self):
        return self._h


def _fake_figure(moves, screen=None):
    window = MagicMock()
    window.screen.return_value.availableGeometry.return_value = screen or _Geometry()
    window.move.side_effect = lambda x, y: moves.append((x, y))
    fig = MagicMock()
    fig.canvas.manager.window = window
    fig.dpi = 100
    fig.canvas.device_pixel_ratio = 1
    return fig


def test_show_plot_window_cascades_and_resets(monkeypatch):
    from calibration_statistics_tool.shared import plotdata

    moves = []
    fig = _fake_figure(moves)
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


def test_plot_window_is_sized_to_fit_a_small_screen(monkeypatch):
    from calibration_statistics_tool.shared import plotdata

    moves = []
    fig = _fake_figure(moves, _Geometry(1000, 600))
    monkeypatch.setattr(plotdata.plt, "show", lambda: None)
    plotdata.showPlotWindow(fig, plotdata._ALL_GRAPHS_WINDOW_SIZE)

    inches = fig.set_size_inches.call_args.args
    assert inches[0] * 100 <= 1000 * plotdata._MAX_SCREEN_FRACTION
    assert inches[1] * 100 <= 600 * plotdata._MAX_SCREEN_FRACTION
    assert fig.set_size_inches.call_args.kwargs == {"forward": True}


def test_show_plot_window_tolerates_non_qt_backend(monkeypatch):
    from calibration_statistics_tool.shared import plotdata

    shown = []
    monkeypatch.setattr(plotdata.plt, "show", lambda: shown.append(1))
    plotdata.showPlotWindow(object())
    assert shown == [1]


def test_legend_is_generated_once_per_sensor_list_and_closed_on_next_run():
    import matplotlib.pyplot as plt
    from calibration_statistics_tool.shared import plotdata

    plotdata.closePlotWindows()
    setup = {"ShowCertainPlotWindow": 1, "idealPhaseDiff": 0}
    combos = [{"dateAndTime": "2024-01-15", "sensor": "rf1_dsp1"}]
    before = set(plt.get_fignums())

    plotdata.generateLegend(setup, combos)
    plotdata.generateLegend(setup, combos)
    assert len(set(plt.get_fignums()) - before) == 1

    other = [{"dateAndTime": "2024-01-16", "sensor": "rf2_dsp2"}]
    plotdata.generateLegend(setup, other)
    assert len(set(plt.get_fignums()) - before) == 2

    plotdata.closePlotWindows()
    assert set(plt.get_fignums()) == before


def test_plot_window_enables_the_selected_graph_even_if_not_ticked():
    from calibration_statistics_tool.shared import plotdata

    config = {"level": 1, "phaseDiff": 0, "corrPhaseDiff": 0}
    window = {"showPlotAllMode": 0, "inputMode": 1, "graph": "phaseDiff"}
    assert plotdata.withPlotWindowGraphs(config, window, 0, [])["phaseDiff"] == 1
    assert config["phaseDiff"] == 0

    window = {"showPlotAllMode": 1, "inputMode": 1, "graph": "level"}
    all_graphs = [{"graphType": "level"}, {"graphType": "corrPhaseDiff"}]
    result = plotdata.withPlotWindowGraphs(config, window, 0, all_graphs)
    assert result["corrPhaseDiff"] == 1 and result["phaseDiff"] == 0

    window = {"showPlotAllMode": 0, "inputMode": 0, "graph": "level"}
    assert plotdata.withPlotWindowGraphs(config, window, {"graph": "phaseDiff"}, [])["phaseDiff"] == 1


def test_statistics_page_fits_the_visible_area(shared_main_view):
    """The plot must shrink to the tab area instead of overflowing it (cut off at the bottom)."""
    from PySide6.QtWidgets import QApplication

    view = shared_main_view
    view.mainWidget.resize(1210, 690)
    index = view.tab_index_of("Statistics")
    view.mainTabWidget.setCurrentIndex(index)
    QApplication.processEvents()
    scroll = view.mainTabWidget.widget(index)

    assert view.statsTab.minimumSizeHint().height() <= scroll.viewport().height()
    assert not scroll.verticalScrollBar().isVisible()
    plot_bottom = view.statsPlotFrame.geometry().bottom()
    assert plot_bottom <= view.statsTab.height()
