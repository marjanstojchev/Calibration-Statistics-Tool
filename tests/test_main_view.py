"""
Unit tests for MainView (PST-47).
pyside_qtgui is mocked so no real QApplication is created.
"""
import sys
import os
import types
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _make_mock_qt():
    """Return a mock object simulating the pyside_qtgui module."""
    m = MagicMock()
    m.parseProtLoadedProtStr = 'Protocols: '
    m.parseProtPtu2FilesStr = 'PTU2 Files: '
    m.parseProtTxAntDiagFilesStr = 'TxAnt Files: '
    m.parseProtSepParPtu2FilesStr = 'Sep PTU2 Files: '
    m.parseProtSepParTxAntDiagFilesStr = 'Sep TxAnt Files: '
    return m


@pytest.fixture
def view():
    """MainView with pyside_qtgui fully mocked — no real Qt."""
    mock_qt = _make_mock_qt()
    # Patch the module-level _qt inside ui.main_view before importing
    with patch.dict('sys.modules', {'pyside_qtgui': mock_qt}):
        # Force re-import with the mock in place
        if 'ui.main_view' in sys.modules:
            del sys.modules['ui.main_view']
        from ui.main_view import MainView
        v = MainView()
        v._qt = mock_qt   # ensure instance uses our mock
        yield v, mock_qt


# --------------------------------------------------------------------------- #
# Instantiation
# --------------------------------------------------------------------------- #

class TestInstantiation:

    def test_main_view_creates(self, view):
        v, _ = view
        assert v is not None

    def test_qt_reference_set(self, view):
        v, mock_qt = view
        assert v._qt is mock_qt


# --------------------------------------------------------------------------- #
# __getattr__ delegation
# --------------------------------------------------------------------------- #

class TestAttrDelegation:

    def test_known_attr_delegated(self, view):
        v, mock_qt = view
        mock_qt.someWidget = 'widget_value'
        assert v.someWidget == 'widget_value'

    def test_unknown_attr_raises(self, view):
        v, _ = view
        # Use a spec-limited mock so accessing an unlisted attribute raises AttributeError
        v._qt = MagicMock(spec=['parseProtLoadedProtLabel'])
        with pytest.raises(AttributeError):
            _ = v.trulyMissingAttr

    def test_multiple_attrs_delegated(self, view):
        v, mock_qt = view
        mock_qt.labelA = 'a'
        mock_qt.labelB = 'b'
        assert v.labelA == 'a'
        assert v.labelB == 'b'


# --------------------------------------------------------------------------- #
# Application lifecycle
# --------------------------------------------------------------------------- #

class TestLifecycle:

    def test_show_calls_main_widget_show(self, view):
        v, mock_qt = view
        v.show()
        mock_qt.mainWidget.show.assert_called_once()

    def test_exec_calls_app_exec(self, view):
        v, mock_qt = view
        mock_qt.app.exec_.return_value = 0
        result = v.exec_()
        mock_qt.app.exec_.assert_called_once()
        assert result == 0


# --------------------------------------------------------------------------- #
# Label helpers
# --------------------------------------------------------------------------- #

class TestLabelHelpers:

    def test_set_loaded_protocols_label(self, view):
        v, mock_qt = view
        v.set_loaded_protocols_label(42)
        mock_qt.parseProtLoadedProtLabel.setText.assert_called_once_with('Protocols: 42')

    def test_set_ptu2_files_label(self, view):
        v, mock_qt = view
        v.set_ptu2_files_label(7)
        mock_qt.parseProtPtu2FilesLabel.setText.assert_called_once_with('PTU2 Files: 7')

    def test_set_tx_ant_diag_files_label(self, view):
        v, mock_qt = view
        v.set_tx_ant_diag_files_label(3)
        mock_qt.parseProtTxAntDiagFilesLabel.setText.assert_called_once_with('TxAnt Files: 3')

    def test_set_sep_par_ptu2_files_label(self, view):
        v, mock_qt = view
        v.set_sep_par_ptu2_files_label(5)
        mock_qt.parseProtSepParPtu2FilesLabel.setText.assert_called_once_with('Sep PTU2 Files: 5')

    def test_set_sep_par_tx_ant_diag_files_label(self, view):
        v, mock_qt = view
        v.set_sep_par_tx_ant_diag_files_label(2)
        mock_qt.parseProtSepParTxAntDiagFilesLabel.setText.assert_called_once_with('Sep TxAnt Files: 2')

    def test_set_progress_label(self, view):
        v, mock_qt = view
        v.set_progress_label('Processing...')
        mock_qt.parseProtProgresLabel.setText.assert_called_once_with('Processing...')

    def test_set_progress_bar(self, view):
        v, mock_qt = view
        v.set_progress_bar(75)
        mock_qt.parseProtProgresBar.setValue.assert_called_once_with(75)

    def test_label_zero_count(self, view):
        v, mock_qt = view
        v.set_loaded_protocols_label(0)
        mock_qt.parseProtLoadedProtLabel.setText.assert_called_once_with('Protocols: 0')


# --------------------------------------------------------------------------- #
# Table helpers
# --------------------------------------------------------------------------- #

class TestTableHelpers:

    def test_clear_table(self, view):
        v, _ = view
        table = MagicMock()
        v.clear_table(table)
        table.setRowCount.assert_called_once_with(0)

    def test_clear_all_parse_tables(self, view):
        v, mock_qt = view
        v.clear_all_parse_tables()
        # All 8 tables should have setRowCount(0) called
        assert mock_qt.parseProtSelProtTable.setRowCount.called
        assert mock_qt.parseProtAccProtTable.setRowCount.called
        assert mock_qt.parseProtAddPtu2ParsedTable.setRowCount.called
        assert mock_qt.parseProtAddPtu2FailedTable.setRowCount.called


# --------------------------------------------------------------------------- #
# Read helpers (widget state getters)
# --------------------------------------------------------------------------- #

class TestReadHelpers:

    def test_get_burn_in_cal_mode(self, view):
        v, mock_qt = view
        mock_qt.parseProtBurnInCalGroup.checkedId.return_value = 1
        assert v.get_burn_in_cal_mode() == 1

    def test_get_include_burn_in_start(self, view):
        v, mock_qt = view
        mock_qt.parseProtBurnStartCheckBox.isChecked.return_value = True
        assert v.get_include_burn_in_start() is True

    def test_get_use_sensor_muster_checked(self, view):
        v, mock_qt = view
        mock_qt.parseProtSensorMusterCheckBox.isChecked.return_value = True
        assert v.get_use_sensor_muster() == 1

    def test_get_use_sensor_muster_unchecked(self, view):
        v, mock_qt = view
        mock_qt.parseProtSensorMusterCheckBox.isChecked.return_value = False
        assert v.get_use_sensor_muster() == 0

    def test_get_sensor_muster_list(self, view):
        v, mock_qt = view
        mock_qt.parseProtSensorMusterLEdit.text.return_value = 'rf dsp PT'
        assert v.get_sensor_muster_list() == ['rf', 'dsp', 'PT']

    def test_get_sensor_muster_list_empty(self, view):
        v, mock_qt = view
        mock_qt.parseProtSensorMusterLEdit.text.return_value = ''
        assert v.get_sensor_muster_list() == []

    def test_get_img_gen_mode(self, view):
        v, mock_qt = view
        mock_qt.sysDiagPlotSetupImgGenGroup.checkedId.return_value = 0
        assert v.get_img_gen_mode() == 0

    def test_get_script_mode(self, view):
        v, mock_qt = view
        mock_qt.sysDiagPlotSetupScriptModeGroup.checkedId.return_value = 1
        assert v.get_script_mode() == 1

    def test_get_three_graph_layout(self, view):
        v, mock_qt = view
        mock_qt.sysDiagPlotSetup3GraphLayoutImgCheckBox.isChecked.return_value = True
        assert v.get_three_graph_layout() is True
