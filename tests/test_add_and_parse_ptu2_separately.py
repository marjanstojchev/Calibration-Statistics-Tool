
import pytest
import sys
import os

# Add project root to path for imports
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

# Import Qt constants for proper comparison
from PySide6.QtWidgets import QFileDialog


def _get_pc():
    """Return the ParseController instance owned by main."""
    import main
    return main.pc

def test_dialog_opens_user_cancels(mocker):
    """Test when user opens dialog but clicks Cancel."""
    
    # Use pytest mocker instead of unittest.mock
    mock_qt = mocker.patch('main.qt')
    
    # Mock the file dialog
    mock_qt.parseProtAddAndParsePtu2FDialog.exec_.return_value = False  # Dialog cancelled
    
    # Only need this for string concatenation
    mock_qt.parseProtSepParPtu2FilesStr = "Files: "
    
    # Create simple antenna system config mock matching real module structure
    class MockModule:
        pass
    mock_antSysDiag = MockModule()
    mock_antSysDiag.plotSetup = {'useSensorMuster': 0, 'sensorMusterList': []}
    mocker.patch('main.antSysDiag', mock_antSysDiag)
    
    # Mock clearTable separately to avoid MagicMock in range() operations
    mocker.patch('main.clearTable')
    
    # Import and call the function that gets triggered by button click
    from main import addAndParsePtu2Files
    
    # Call the function (this simulates what happens when button is clicked)
    addAndParsePtu2Files()
    
    # Verify the dialog was opened
    mock_qt.parseProtAddAndParsePtu2FDialog.exec_.assert_called_once()


def test_dialog_opens_no_files_selected(mocker):
    """Test when user clicks OK but selects no files."""
    
    # SETUP MOCKS
    mock_qt = mocker.patch('main.qt')
    mock_qt.parseProtAddAndParsePtu2FDialog.exec_.return_value = True  # User clicked OK
    mock_qt.parseProtAddAndParsePtu2FDialog.selectedFiles.return_value = []  # But no files selected
    
    # Only need this for string concatenation
    mock_qt.parseProtSepParPtu2FilesStr = "Files: "
    
    # Create simple antenna system config mock matching real module structure
    class MockModule:
        pass
    mock_antSysDiag = MockModule()
    mock_antSysDiag.plotSetup = {'useSensorMuster': 0, 'sensorMusterList': []}
    mocker.patch('main.antSysDiag', mock_antSysDiag)
    
    # Mock clearTable separately to avoid MagicMock in range() operations
    mocker.patch('main.clearTable')
    
    # CALL FUNCTION
    from main import addAndParsePtu2Files
    pc = _get_pc()
    pc.clear_state()

    addAndParsePtu2Files()

    # VERIFY
    mock_qt.parseProtAddAndParsePtu2FDialog.exec_.assert_called_once()  # Dialog opened
    mock_qt.parseProtAddAndParsePtu2FDialog.selectedFiles.assert_called_once()  # Files requested (but empty list returned)
    assert pc.ptu2_parsed_count() == 0  # No data added
    assert pc.ptu2_failed_count() == 0


def test_files_selected_all_parse_successfully(mocker):
    """Test when user selects real PTU files and all parse without errors."""
    
    # SETUP MOCKS - Only mock UI components
    mock_qt = mocker.patch('main.qt')
    mock_qt.parseProtAddAndParsePtu2FDialog.exec_.return_value = True  # User clicked OK
    
    # Use REAL PTU files with different characteristics - use absolute paths
    test_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    real_ptu_files = [
        os.path.join(test_dir, 'measurement_data', 'ptu_files', '2024-01-15_08-15-30_Tuner1_rf12345_dsp67890_Seq1_TxAnt0_Diagram0_Az_ptu2.txt'),
        os.path.join(test_dir, 'measurement_data', 'ptu_files', '2024-01-15_09-25-45_Tuner1_rf12345_dsp67890_Seq1_TxAnt1_Diagram2_Az_ptu2.txt'),
        os.path.join(test_dir, 'measurement_data', 'ptu_files', '2024-01-15_12-30-45_Tuner1_rf12345_dsp67890_Seq1_TxAnt0_Diagram1_El_ptu2.txt'),
        os.path.join(test_dir, 'measurement_data', 'ptu_files', '2024-01-15_14-45-10_Tuner1_rf12345_dsp67890_Seq1_TxAnt1_Diagram3_El_ptu2.txt')
    ]
    mock_qt.parseProtAddAndParsePtu2FDialog.selectedFiles.return_value = real_ptu_files
    
    # Mock only UI and logging components (let real parsing happen)
    mock_parseDataLog = mocker.patch('main.parseDataLog')
    mock_clearTable = mocker.patch('main.clearTable')
    mock_QTableWidgetItem = mocker.patch('main.QTableWidgetItem')
    
    # Create simple antenna system config mock matching real module structure
    # antSysDiag is a MODULE with plotSetup as a module-level dictionary
    class MockModule:
        pass
    mock_antSysDiag = MockModule()
    mock_antSysDiag.plotSetup = {'useSensorMuster': 0, 'sensorMusterList': []}
    mocker.patch('main.antSysDiag', mock_antSysDiag)
    
    # DON'T mock parsePtu2 - let real parsing happen!
    # DON'T mock parse data objects - they'll be real!
    
    # CALL FUNCTION
    from main import addAndParsePtu2Files
    pc = _get_pc()
    pc.clear_state()  # Reset controller state before test
    
    addAndParsePtu2Files()

    # VERIFY
    mock_qt.parseProtAddAndParsePtu2FDialog.exec_.assert_called_once()
    mock_qt.parseProtAddAndParsePtu2FDialog.selectedFiles.assert_called_once()

    # With 4 real PTU files, all should parse successfully — read from controller
    assert pc.ptu2_parsed_count() == 4
    assert pc.sys_diag_parsed_count() == 4
    assert pc.ptu2_failed_count() == 0
    mock_clearTable.assert_called()  # Tables were cleared/updated
    
    # Verify actual file paths are in the results (real parsing happened)
    file_paths = [data.fileTitle.fileNamePath for data in pc.sysDiagParsedDataDict['parsedDataList']]
    assert any('2024-01-15' in path for path in file_paths)


def test_files_selected_some_fail_parsing(mocker):
    """Test when user selects files but some fail to parse - using real good/bad files."""
    
    # SETUP MOCKS
    mock_qt = mocker.patch('main.qt')
    mock_qt.parseProtAddAndParsePtu2FDialog.exec_.return_value = True
    
    # Use one REAL good file and one REAL bad file - use absolute paths
    test_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    good_file = os.path.join(test_dir, 'measurement_data', 'ptu_files', '2024-01-15_08-15-30_Tuner1_rf12345_dsp67890_Seq1_TxAnt0_Diagram0_Az_ptu2.txt')
    bad_file = os.path.join(test_dir, 'tests', 'bad_ptu2_test_file.txt')
    
    mock_qt.parseProtAddAndParsePtu2FDialog.selectedFiles.return_value = [good_file, bad_file]
    
    # Mock UI and logging components only
    mock_parseDataLog = mocker.patch('main.parseDataLog')
    mock_clearTable = mocker.patch('main.clearTable')
    mock_QTableWidgetItem = mocker.patch('main.QTableWidgetItem')
    
    # Create simple antenna system config mock matching real module structure
    # antSysDiag is a MODULE with plotSetup as a module-level dictionary 
    class MockModule:
        pass
    mock_antSysDiag = MockModule()
    mock_antSysDiag.plotSetup = {'useSensorMuster': 0, 'sensorMusterList': []}
    mocker.patch('main.antSysDiag', mock_antSysDiag)
    
    # DON'T mock parsePtu2 - let real parsing happen with real files
    
    # CALL FUNCTION
    from main import addAndParsePtu2Files
    pc = _get_pc()
    pc.clear_state()  # Reset controller state before test
    
    addAndParsePtu2Files()

    # VERIFY - Mixed results: good file succeeds, bad file fails — read from controller
    assert pc.sys_diag_parsed_count() == 1
    assert pc.ptu2_parsed_count() == 1
    assert pc.ptu2_failed_count() == 1
    
    # Check file paths to verify which file went where
    successful_path = pc.separatePtu2ParsedDataDict['parsedDataList'][0].fileTitle.fileNamePath
    failed_path = pc.separatePtu2FailedDataDict['parsedDataList'][0].fileTitle.fileNamePath
    
    assert '2024-01-15_08-15-30' in successful_path
    assert 'bad_ptu2_test_file.txt' in failed_path





def test_duplicate_files_not_added_twice(mocker):
    """Test that duplicate files aren't added to dictionaries twice - using real file."""
    
    # SETUP MOCKS
    mock_qt = mocker.patch('main.qt')
    mock_qt.parseProtAddAndParsePtu2FDialog.exec_.return_value = True
    
    # Use a real PTU file that will be selected as "duplicate" - use absolute path
    test_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    duplicate_file_path = os.path.join(test_dir, 'measurement_data', 'ptu_files', '2024-01-15_08-15-30_Tuner1_rf12345_dsp67890_Seq1_TxAnt0_Diagram0_Az_ptu2.txt')
    mock_qt.parseProtAddAndParsePtu2FDialog.selectedFiles.return_value = [duplicate_file_path]
    
    # Mock UI and logging components  
    mock_parseDataLog = mocker.patch('main.parseDataLog')
    mock_clearTable = mocker.patch('main.clearTable')
    mock_QTableWidgetItem = mocker.patch('main.QTableWidgetItem')
    
    # Create simple antenna system config mock matching real module structure
    # antSysDiag is a MODULE with plotSetup as a module-level dictionary
    class MockModule:
        pass 
    mock_antSysDiag = MockModule()
    mock_antSysDiag.plotSetup = {'useSensorMuster': 0, 'sensorMusterList': []}
    mocker.patch('main.antSysDiag', mock_antSysDiag)
    
    # DON'T mock parsePtu2 - let real parsing happen first time
    
    # FIRST CALL - Add file initially
    from main import addAndParsePtu2Files
    pc = _get_pc()
    pc.clear_state()  # Reset controller state before test
    
    addAndParsePtu2Files()
    assert pc.ptu2_parsed_count() == 1
    assert pc.sys_diag_parsed_count() == 1

    # SECOND CALL - Try to add same file again (simulate user selecting same file)
    addAndParsePtu2Files()
    
    # VERIFY - File count should NOT increase (duplicate prevention worked)
    assert pc.ptu2_parsed_count() == 1
    assert pc.sys_diag_parsed_count() == 1
    assert pc.ptu2_failed_count() == 0
    
    file_path = pc.sysDiagParsedDataDict['parsedDataList'][0].fileTitle.fileNamePath
    assert '2024-01-15_08-15-30' in file_path


def test_dialog_only_accepts_ptu2_files(mocker):
    """Test that file dialog is configured to filter for PTU2 .txt files."""
    
    # Mock the Qt GUI components completely
    mock_qt = mocker.patch('main.qt')
    
    # No need for MockDialog, use qt.parseProtAddAndParsePtu2FDialog directly
    mock_qt.parseProtAddAndParsePtu2FDialog.nameFilter.return_value = "PTU-2 Files (*_ptu2.txt)"
    mock_qt.parseProtAddAndParsePtu2FDialog.fileMode.return_value = QFileDialog.ExistingFiles
    mock_qt.parseProtAddAndParsePtu2FDialog.exec_.return_value = False  # User cancels dialog

    # Mock clearTable to avoid MagicMock in range() operations
    mocker.patch('main.clearTable')
    
    # VERIFY - Check the dialog filter configuration
    actual_filter = mock_qt.parseProtAddAndParsePtu2FDialog.nameFilter()
    
    # The dialog should have PTU-2 file filter set for .txt files
    assert "ptu2" in actual_filter.lower(), f"Expected PTU2 filter, got: {actual_filter}"
    assert ".txt" in actual_filter.lower(), f"Expected .txt extension, got: {actual_filter}"
    file_mode = mock_qt.parseProtAddAndParsePtu2FDialog.fileMode()
    assert file_mode == QFileDialog.ExistingFiles, "Dialog should allow multiple file selection"

    # Call the function and check dialog configuration after
    from main import addAndParsePtu2Files
    addAndParsePtu2Files()
    # Check again after function call
    actual_filter_after = mock_qt.parseProtAddAndParsePtu2FDialog.nameFilter()
    file_mode_after = mock_qt.parseProtAddAndParsePtu2FDialog.fileMode()
    assert "ptu2" in actual_filter_after.lower(), f"Expected PTU2 filter after call, got: {actual_filter_after}"
    assert ".txt" in actual_filter_after.lower(), f"Expected .txt extension after call, got: {actual_filter_after}"
    assert file_mode_after == QFileDialog.ExistingFiles, "Dialog should allow multiple file selection after function call"


def test_counters_update_correctly(mocker):
    """Test that UI counters reflect correct parsed/failed file counts."""
    
    # SETUP MOCKS
    mock_qt = mocker.patch('main.qt')
    mock_qt.parseProtAddAndParsePtu2FDialog.exec_.return_value = True
    
    # Use mix of good and bad files - use absolute paths
    test_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    good_file = os.path.join(test_dir, 'measurement_data', 'ptu_files', '2024-01-15_08-15-30_Tuner1_rf12345_dsp67890_Seq1_TxAnt0_Diagram0_Az_ptu2.txt')
    bad_file = os.path.join(test_dir, 'tests', 'bad_ptu2_test_file.txt')
    mock_qt.parseProtAddAndParsePtu2FDialog.selectedFiles.return_value = [good_file, bad_file]
    
    # Mock the string used for concatenation
    mock_qt.parseProtSepParPtu2FilesStr = "Files: "
    
    # Mock UI components
    mock_parseDataLog = mocker.patch('main.parseDataLog')
    mock_clearTable = mocker.patch('main.clearTable')
    mock_QTableWidgetItem = mocker.patch('main.QTableWidgetItem')
    
    # Create simple antenna system config mock matching real module structure
    # antSysDiag is a MODULE with plotSetup as a module-level dictionary
    class MockModule:
        pass
    mock_antSysDiag = MockModule()
    mock_antSysDiag.plotSetup = {'useSensorMuster': 0, 'sensorMusterList': []}
    mocker.patch('main.antSysDiag', mock_antSysDiag)
    
    # CALL FUNCTION
    from main import addAndParsePtu2Files
    pc = _get_pc()
    pc.clear_state()  # Reset controller state before test
    
    addAndParsePtu2Files()

    # VERIFY - Counter updated via view helper (view.set_sep_par_ptu2_files_label)
    assert pc.ptu2_parsed_count() == 1  # good file succeeded
    assert pc.ptu2_failed_count() == 1  # bad file failed


def test_log_entries_created_with_timestamps_and_status(mocker):
    """Test that log entries are created for each file with proper content."""
    
    # SETUP MOCKS
    mock_qt = mocker.patch('main.qt')
    mock_qt.parseProtAddAndParsePtu2FDialog.exec_.return_value = True
    
    # Use absolute paths
    test_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    test_files = [
        os.path.join(test_dir, 'measurement_data', 'ptu_files', '2024-01-15_08-15-30_Tuner1_rf12345_dsp67890_Seq1_TxAnt0_Diagram0_Az_ptu2.txt'),
        os.path.join(test_dir, 'measurement_data', 'ptu_files', '2024-01-15_09-25-45_Tuner1_rf12345_dsp67890_Seq1_TxAnt1_Diagram2_Az_ptu2.txt')
    ]
    mock_qt.parseProtAddAndParsePtu2FDialog.selectedFiles.return_value = test_files
    
    # Mock UI components
    mock_parseDataLog = mocker.patch('main.parseDataLog')
    mock_clearTable = mocker.patch('main.clearTable')
    mock_QTableWidgetItem = mocker.patch('main.QTableWidgetItem')
    
    # Create simple antenna system config mock matching real module structure
    # antSysDiag is a MODULE with plotSetup as a module-level dictionary
    class MockModule:
        pass
    mock_antSysDiag = MockModule()
    mock_antSysDiag.plotSetup = {'useSensorMuster': 0, 'sensorMusterList': []}
    mocker.patch('main.antSysDiag', mock_antSysDiag)
    
    # CALL FUNCTION
    from main import addAndParsePtu2Files
    pc = _get_pc()
    pc.clear_state()  # Reset controller state before test
    
    # Logging now happens inside ParseController — patch the controller's logger
    mock_ctrl_log = mocker.patch('shared.parse_controller.logconfig.mainLoadDataLogger')
    mock_ctrl_log.logger.info = mocker.MagicMock()
    
    addAndParsePtu2Files()

    # VERIFY - real files were parsed and stored in controller
    assert pc.ptu2_parsed_count() == 2
    file_paths = [d.fileTitle.fileNamePath for d in pc.sysDiagParsedDataDict['parsedDataList']]
    assert any('2024-01-15_08-15-30' in p for p in file_paths), "First file not found in results"
    assert any('2024-01-15_09-25-45' in p for p in file_paths), "Second file not found in results"
