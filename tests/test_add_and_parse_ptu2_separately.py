
import pytest
import os
from unittest.mock import MagicMock

# Import Qt constants for proper comparison
from PySide6.QtWidgets import QFileDialog
from calibration_statistics_tool.ui.handlers.app_context import AppContext
from calibration_statistics_tool.ui.handlers.parse_handlers import addAndParsePtu2Files


def _get_pc():
    """Return the ParseController instance owned by main."""
    from calibration_statistics_tool import main
    return main.pc


def _make_ctx(mock_qt, pc=None):
    """Create a minimal AppContext for addAndParsePtu2Files tests."""
    if pc is None:
        pc = _get_pc()
    mock_mv = MagicMock()
    mock_plc = MagicMock()
    mock_plc.plotSetup = {'useSensorMuster': 0, 'sensorMusterList': []}
    return AppContext(qt=mock_qt, mv=mock_mv, plc=mock_plc, pc=pc)


def test_dialog_opens_user_cancels(mocker):
    """Test when user opens dialog but clicks Cancel."""

    mock_qt = MagicMock()
    mock_qt.parseProtAddAndParsePtu2FDialog.exec_.return_value = False  # Dialog cancelled

    mocker.patch('calibration_statistics_tool.ui.handlers.parse_handlers.clearTable')

    ctx = _make_ctx(mock_qt)
    addAndParsePtu2Files(ctx)

    mock_qt.parseProtAddAndParsePtu2FDialog.exec_.assert_called_once()


def test_dialog_opens_no_files_selected(mocker):
    """Test when user clicks OK but selects no files."""

    mock_qt = MagicMock()
    mock_qt.parseProtAddAndParsePtu2FDialog.exec_.return_value = True   # User clicked OK
    mock_qt.parseProtAddAndParsePtu2FDialog.selectedFiles.return_value = []

    mocker.patch('calibration_statistics_tool.ui.handlers.parse_handlers.clearTable')

    pc = _get_pc()
    pc.clear_state()
    ctx = _make_ctx(mock_qt, pc)
    addAndParsePtu2Files(ctx)

    mock_qt.parseProtAddAndParsePtu2FDialog.exec_.assert_called_once()
    mock_qt.parseProtAddAndParsePtu2FDialog.selectedFiles.assert_called_once()
    assert pc.ptu2_parsed_count() == 0
    assert pc.ptu2_failed_count() == 0


def test_files_selected_all_parse_successfully(mocker):
    """Test when user selects real PTU files and all parse without errors."""

    mock_qt = MagicMock()
    mock_qt.parseProtAddAndParsePtu2FDialog.exec_.return_value = True

    test_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    real_ptu_files = [
        os.path.join(test_dir, 'measurement_data', 'ptu_files', '2024-01-15_08-15-30_Tuner1_rf12345_dsp67890_Seq1_TxAnt0_Diagram0_Az_ptu2.txt'),
        os.path.join(test_dir, 'measurement_data', 'ptu_files', '2024-01-15_09-25-45_Tuner1_rf12345_dsp67890_Seq1_TxAnt1_Diagram2_Az_ptu2.txt'),
        os.path.join(test_dir, 'measurement_data', 'ptu_files', '2024-01-15_12-30-45_Tuner1_rf12345_dsp67890_Seq1_TxAnt0_Diagram1_El_ptu2.txt'),
        os.path.join(test_dir, 'measurement_data', 'ptu_files', '2024-01-15_14-45-10_Tuner1_rf12345_dsp67890_Seq1_TxAnt1_Diagram3_El_ptu2.txt')
    ]
    mock_qt.parseProtAddAndParsePtu2FDialog.selectedFiles.return_value = real_ptu_files

    mocker.patch('calibration_statistics_tool.ui.handlers.parse_handlers.parseDataLog')
    mock_clearTable = mocker.patch('calibration_statistics_tool.ui.handlers.parse_handlers.clearTable')
    mocker.patch('calibration_statistics_tool.ui.handlers.parse_handlers.QTableWidgetItem')

    pc = _get_pc()
    pc.clear_state()
    ctx = _make_ctx(mock_qt, pc)
    addAndParsePtu2Files(ctx)

    mock_qt.parseProtAddAndParsePtu2FDialog.exec_.assert_called_once()
    mock_qt.parseProtAddAndParsePtu2FDialog.selectedFiles.assert_called_once()
    assert pc.ptu2_parsed_count() == 4
    assert pc.sys_diag_parsed_count() == 4
    assert pc.ptu2_failed_count() == 0
    mock_clearTable.assert_called()

    file_paths = [data.fileTitle.fileNamePath for data in pc.sysDiagParsedDataDict['parsedDataList']]
    assert any('2024-01-15' in path for path in file_paths)


def test_files_selected_some_fail_parsing(mocker):
    """Test when user selects files but some fail to parse - using real good/bad files."""

    mock_qt = MagicMock()
    mock_qt.parseProtAddAndParsePtu2FDialog.exec_.return_value = True

    test_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    good_file = os.path.join(test_dir, 'measurement_data', 'ptu_files', '2024-01-15_08-15-30_Tuner1_rf12345_dsp67890_Seq1_TxAnt0_Diagram0_Az_ptu2.txt')
    bad_file  = os.path.join(test_dir, 'tests', 'bad_ptu2_test_file.txt')
    mock_qt.parseProtAddAndParsePtu2FDialog.selectedFiles.return_value = [good_file, bad_file]

    mocker.patch('calibration_statistics_tool.ui.handlers.parse_handlers.parseDataLog')
    mock_clearTable = mocker.patch('calibration_statistics_tool.ui.handlers.parse_handlers.clearTable')
    mocker.patch('calibration_statistics_tool.ui.handlers.parse_handlers.QTableWidgetItem')

    pc = _get_pc()
    pc.clear_state()
    ctx = _make_ctx(mock_qt, pc)
    addAndParsePtu2Files(ctx)

    assert pc.sys_diag_parsed_count() == 1
    assert pc.ptu2_parsed_count() == 1
    assert pc.ptu2_failed_count() == 1

    successful_path = pc.separatePtu2ParsedDataDict['parsedDataList'][0].fileTitle.fileNamePath
    failed_path     = pc.separatePtu2FailedDataDict['parsedDataList'][0].fileTitle.fileNamePath
    assert '2024-01-15_08-15-30' in successful_path
    assert 'bad_ptu2_test_file.txt' in failed_path


def test_duplicate_files_not_added_twice(mocker):
    """Test that duplicate files aren't added to dictionaries twice - using real file."""

    mock_qt = MagicMock()
    mock_qt.parseProtAddAndParsePtu2FDialog.exec_.return_value = True

    test_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    duplicate_file_path = os.path.join(test_dir, 'measurement_data', 'ptu_files', '2024-01-15_08-15-30_Tuner1_rf12345_dsp67890_Seq1_TxAnt0_Diagram0_Az_ptu2.txt')
    mock_qt.parseProtAddAndParsePtu2FDialog.selectedFiles.return_value = [duplicate_file_path]

    mocker.patch('calibration_statistics_tool.ui.handlers.parse_handlers.parseDataLog')
    mocker.patch('calibration_statistics_tool.ui.handlers.parse_handlers.clearTable')
    mocker.patch('calibration_statistics_tool.ui.handlers.parse_handlers.QTableWidgetItem')

    pc = _get_pc()
    pc.clear_state()
    ctx = _make_ctx(mock_qt, pc)

    # FIRST CALL
    addAndParsePtu2Files(ctx)
    assert pc.ptu2_parsed_count() == 1
    assert pc.sys_diag_parsed_count() == 1

    # SECOND CALL — same file should not be added again
    addAndParsePtu2Files(ctx)
    assert pc.ptu2_parsed_count() == 1
    assert pc.sys_diag_parsed_count() == 1
    assert pc.ptu2_failed_count() == 0

    file_path = pc.sysDiagParsedDataDict['parsedDataList'][0].fileTitle.fileNamePath
    assert '2024-01-15_08-15-30' in file_path


def test_dialog_only_accepts_ptu2_files(mocker):
    """Test that file dialog is configured to filter for PTU2 .txt files."""

    mock_qt = MagicMock()
    mock_qt.parseProtAddAndParsePtu2FDialog.nameFilter.return_value = "PTU-2 Files (*_ptu2.txt)"
    mock_qt.parseProtAddAndParsePtu2FDialog.fileMode.return_value = QFileDialog.ExistingFiles
    mock_qt.parseProtAddAndParsePtu2FDialog.exec_.return_value = False  # User cancels

    mocker.patch('calibration_statistics_tool.ui.handlers.parse_handlers.clearTable')

    actual_filter = mock_qt.parseProtAddAndParsePtu2FDialog.nameFilter()
    assert "ptu2" in actual_filter.lower(), f"Expected PTU2 filter, got: {actual_filter}"
    assert ".txt" in actual_filter.lower(), f"Expected .txt extension, got: {actual_filter}"
    file_mode = mock_qt.parseProtAddAndParsePtu2FDialog.fileMode()
    assert file_mode == QFileDialog.ExistingFiles

    ctx = _make_ctx(mock_qt)
    addAndParsePtu2Files(ctx)

    actual_filter_after = mock_qt.parseProtAddAndParsePtu2FDialog.nameFilter()
    file_mode_after      = mock_qt.parseProtAddAndParsePtu2FDialog.fileMode()
    assert "ptu2" in actual_filter_after.lower()
    assert ".txt" in actual_filter_after.lower()
    assert file_mode_after == QFileDialog.ExistingFiles


def test_counters_update_correctly(mocker):
    """Test that UI counters reflect correct parsed/failed file counts."""

    mock_qt = MagicMock()
    mock_qt.parseProtAddAndParsePtu2FDialog.exec_.return_value = True

    test_dir  = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    good_file = os.path.join(test_dir, 'measurement_data', 'ptu_files', '2024-01-15_08-15-30_Tuner1_rf12345_dsp67890_Seq1_TxAnt0_Diagram0_Az_ptu2.txt')
    bad_file  = os.path.join(test_dir, 'tests', 'bad_ptu2_test_file.txt')
    mock_qt.parseProtAddAndParsePtu2FDialog.selectedFiles.return_value = [good_file, bad_file]

    mocker.patch('calibration_statistics_tool.ui.handlers.parse_handlers.parseDataLog')
    mocker.patch('calibration_statistics_tool.ui.handlers.parse_handlers.clearTable')
    mocker.patch('calibration_statistics_tool.ui.handlers.parse_handlers.QTableWidgetItem')

    pc = _get_pc()
    pc.clear_state()
    ctx = _make_ctx(mock_qt, pc)
    addAndParsePtu2Files(ctx)

    assert pc.ptu2_parsed_count() == 1
    assert pc.ptu2_failed_count() == 1


def test_log_entries_created_with_timestamps_and_status(mocker):
    """Test that log entries are created for each file with proper content."""

    mock_qt = MagicMock()
    mock_qt.parseProtAddAndParsePtu2FDialog.exec_.return_value = True

    test_dir   = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    test_files = [
        os.path.join(test_dir, 'measurement_data', 'ptu_files', '2024-01-15_08-15-30_Tuner1_rf12345_dsp67890_Seq1_TxAnt0_Diagram0_Az_ptu2.txt'),
        os.path.join(test_dir, 'measurement_data', 'ptu_files', '2024-01-15_09-25-45_Tuner1_rf12345_dsp67890_Seq1_TxAnt1_Diagram2_Az_ptu2.txt')
    ]
    mock_qt.parseProtAddAndParsePtu2FDialog.selectedFiles.return_value = test_files

    mocker.patch('calibration_statistics_tool.ui.handlers.parse_handlers.parseDataLog')
    mocker.patch('calibration_statistics_tool.ui.handlers.parse_handlers.clearTable')
    mocker.patch('calibration_statistics_tool.ui.handlers.parse_handlers.QTableWidgetItem')

    pc = _get_pc()
    pc.clear_state()
    ctx = _make_ctx(mock_qt, pc)

    mock_ctrl_log = mocker.patch('shared.parse_controller.logconfig.mainLoadDataLogger')
    mock_ctrl_log.logger.info = mocker.MagicMock()

    addAndParsePtu2Files(ctx)

    assert pc.ptu2_parsed_count() == 2
    file_paths = [d.fileTitle.fileNamePath for d in pc.sysDiagParsedDataDict['parsedDataList']]
    assert any('2024-01-15_08-15-30' in p for p in file_paths), "First file not found in results"
    assert any('2024-01-15_09-25-45' in p for p in file_paths), "Second file not found in results"
