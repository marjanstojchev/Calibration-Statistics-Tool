"""
Unit tests for MainView (PST-67).

Uses real Qt widgets; QApplication is provided by the session-scoped qapp
fixture in conftest.py.  The old mock-based approach is replaced with
targeted patch.object calls and direct widget state assertions.
"""
import sys
import os
from unittest.mock import patch, MagicMock

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope='module')
def view(shared_main_view):
    """Alias for the session-scoped shared MainView."""
    return shared_main_view


# --------------------------------------------------------------------------- #
# Instantiation
# --------------------------------------------------------------------------- #

class TestInstantiation:

    def test_main_view_creates(self, view):
        assert view is not None

    def test_has_main_widget(self, view):
        assert view.mainWidget is not None

    def test_has_main_tab_widget(self, view):
        assert view.mainTabWidget is not None

    def test_no_qt_proxy_attr(self, view):
        """PST-67: MainView owns widgets directly — no _qt proxy."""
        assert not hasattr(view, '_qt')

    def test_tab_modules_absorbed(self, view):
        """Tab widget names should be accessible directly on the view."""
        assert hasattr(view, 'parseProtTab')
        assert hasattr(view, 'sysDiagTab')
        assert hasattr(view, 'txAntDiagTab')
        assert hasattr(view, 'antPatTab')


# --------------------------------------------------------------------------- #
# Application lifecycle
# --------------------------------------------------------------------------- #

class TestLifecycle:

    def test_show_displays_main_widget(self, view):
        view.show()
        assert view.mainWidget.isVisible()

    def test_exec_delegates_to_app(self, view):
        with patch.object(view.app, 'exec', return_value=42):
            result = view.exec_()
        assert result == 42


# --------------------------------------------------------------------------- #
# Label helpers
# --------------------------------------------------------------------------- #

class TestLabelHelpers:

    def test_set_loaded_protocols_label(self, view):
        view.set_loaded_protocols_label(42)
        assert view.parseProtLoadedProtLabel.text() == view.parseProtLoadedProtStr + '42'

    def test_set_ptu2_files_label(self, view):
        view.set_ptu2_files_label(7)
        assert view.parseProtPtu2FilesLabel.text() == view.parseProtPtu2FilesStr + '7'

    def test_set_tx_ant_diag_files_label(self, view):
        view.set_tx_ant_diag_files_label(3)
        assert view.parseProtTxAntDiagFilesLabel.text() == view.parseProtTxAntDiagFilesStr + '3'

    def test_set_sep_par_ptu2_files_label(self, view):
        view.set_sep_par_ptu2_files_label(5)
        assert view.parseProtSepParPtu2FilesLabel.text() == view.parseProtSepParPtu2FilesStr + '5'

    def test_set_sep_par_tx_ant_diag_files_label(self, view):
        view.set_sep_par_tx_ant_diag_files_label(2)
        assert view.parseProtSepParTxAntDiagFilesLabel.text() == (
            view.parseProtSepParTxAntDiagFilesStr + '2'
        )

    def test_set_progress_label(self, view):
        view.set_progress_label('Processing...')
        assert view.parseProtProgresLabel.text() == 'Processing...'

    def test_set_progress_bar(self, view):
        view.set_progress_bar(75)
        assert view.parseProtProgresBar.value() == 75

    def test_label_zero_count(self, view):
        view.set_loaded_protocols_label(0)
        assert view.parseProtLoadedProtLabel.text() == view.parseProtLoadedProtStr + '0'


# --------------------------------------------------------------------------- #
# Table helpers
# --------------------------------------------------------------------------- #

class TestTableHelpers:

    def test_clear_table_calls_set_row_count(self, view):
        table = MagicMock()
        view.clear_table(table)
        table.setRowCount.assert_called_once_with(0)

    def test_clear_all_parse_tables(self, view):
        tables = [
            view.parseProtSelProtTable,
            view.parseProtAccProtTable,
            view.parseProtAddPtu2ParsedTable,
            view.parseProtAddPtu2FailedTable,
            view.parseProtAddTxAntDiagParsedTable,
            view.parseProtAddTxAntDiagFailedTable,
            view.parseProtStatsParsedTable,
            view.parseProtStatsFailedTable,
        ]
        for t in tables:
            t.setRowCount(1)

        view.clear_all_parse_tables()

        for t in tables:
            assert t.rowCount() == 0


# --------------------------------------------------------------------------- #
# Read helpers (widget state getters)
# --------------------------------------------------------------------------- #

class TestReadHelpers:

    def test_get_burn_in_cal_mode(self, view):
        with patch.object(view.parseProtBurnInCalGroup, 'checkedId', return_value=1):
            assert view.get_burn_in_cal_mode() == 1

    def test_get_include_burn_in_start_checkbox_checked_returns_false(self, view):
        # Checked = "Ignore BurnIn At Start" = exclude → False
        with patch.object(view.parseProtBurnStartCheckBox, 'isChecked', return_value=True):
            assert view.get_include_burn_in_start() is False

    def test_get_include_burn_in_start_checkbox_unchecked_returns_true(self, view):
        # Unchecked (default) = don't ignore = include → True
        with patch.object(view.parseProtBurnStartCheckBox, 'isChecked', return_value=False):
            assert view.get_include_burn_in_start() is True

    def test_get_use_sensor_muster_checked(self, view):
        with patch.object(view.parseProtSensorMusterCheckBox, 'isChecked', return_value=True):
            assert view.get_use_sensor_muster() == 1

    def test_get_use_sensor_muster_unchecked(self, view):
        with patch.object(view.parseProtSensorMusterCheckBox, 'isChecked', return_value=False):
            assert view.get_use_sensor_muster() == 0

    def test_get_sensor_muster_list(self, view):
        with patch.object(view.parseProtSensorMusterLEdit, 'text', return_value='rf dsp PT'):
            assert view.get_sensor_muster_list() == ['rf', 'dsp', 'PT']

    def test_get_sensor_muster_list_empty(self, view):
        with patch.object(view.parseProtSensorMusterLEdit, 'text', return_value=''):
            assert view.get_sensor_muster_list() == []

    def test_get_img_gen_mode(self, view):
        with patch.object(view.sysDiagPlotSetupImgGenGroup, 'checkedId', return_value=0):
            assert view.get_img_gen_mode() == 0

    def test_get_script_mode(self, view):
        with patch.object(view.sysDiagPlotSetupScriptModeGroup, 'checkedId', return_value=1):
            assert view.get_script_mode() == 1

    def test_get_three_graph_layout_true(self, view):
        with patch.object(
            view.sysDiagPlotSetup3GraphLayoutImgCheckBox, 'isChecked', return_value=True
        ):
            assert view.get_three_graph_layout() is True
