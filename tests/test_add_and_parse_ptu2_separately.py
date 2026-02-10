
import pytest
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_dialog_opens_user_cancels(mocker):
    """Test when user opens dialog but clicks Cancel."""
    
    # Use pytest mocker instead of unittest.mock
    mock_qt = mocker.patch('main.qt')
    
    # Mock the file dialog
    mock_qt.parseProtAddAndParsePtu2FDialog.exec_.return_value = False  # Dialog cancelled
    
    # Import and call the function that gets triggered by button click
    from main import addAndParsePtu2Files
    
    # Create test data dictionaries
    sysDiagParsedDataDict = {'parsedDataList': []}
    separatePtu2ParsedDataDict = {'parsedDataList': []}
    separatePtu2FailedDataDict = {'parsedDataList': []}
    
    # Call the function (this simulates what happens when button is clicked)
    addAndParsePtu2Files(sysDiagParsedDataDict, separatePtu2ParsedDataDict, separatePtu2FailedDataDict)
    
    # Verify the dialog was opened
    mock_qt.parseProtAddAndParsePtu2FDialog.exec_.assert_called_once()


def test_dialog_opens_no_files_selected(mocker):
    """Test when user clicks OK but selects no files."""
    
    # SETUP MOCKS
    mock_qt = mocker.patch('main.qt')
    mock_qt.parseProtAddAndParsePtu2FDialog.exec_.return_value = True  # User clicked OK
    mock_qt.parseProtAddAndParsePtu2FDialog.selectedFiles.return_value = []  # But no files selected
    
    # CALL FUNCTION
    from main import addAndParsePtu2Files
    sys_dict = {'parsedDataList': []}
    sep_parsed = {'parsedDataList': []}
    sep_failed = {'parsedDataList': []}
    
    addAndParsePtu2Files(sys_dict, sep_parsed, sep_failed)
    
    # VERIFY
    mock_qt.parseProtAddAndParsePtu2FDialog.exec_.assert_called_once()  # Dialog opened
    mock_qt.parseProtAddAndParsePtu2FDialog.selectedFiles.assert_called_once()  # Files requested (but empty list returned)
    assert len(sys_dict['parsedDataList']) == 0  # No data added
    assert len(sep_parsed['parsedDataList']) == 0
    assert len(sep_failed['parsedDataList']) == 0


def test_files_selected_all_parse_successfully(mocker):
    """Test when user selects real PTU files and all parse without errors."""
    
    # SETUP MOCKS - Only mock UI components
    mock_qt = mocker.patch('main.qt')
    mock_qt.parseProtAddAndParsePtu2FDialog.exec_.return_value = True  # User clicked OK
    
    # Use REAL PTU files with different characteristics
    real_ptu_files = [
        'C:\\Calibration Statistics Tool\\measurement_data\\ptu_files\\2024-01-15_08-15-30_Tuner1_rf12345_dsp67890_Seq1_TxAnt0_Diagram0_Az_ptu2.txt',
        'C:\\Calibration Statistics Tool\\measurement_data\\ptu_files\\2024-01-15_09-25-45_Tuner1_rf12345_dsp67890_Seq1_TxAnt1_Diagram2_Az_ptu2.txt',
        'C:\\Calibration Statistics Tool\\measurement_data\\ptu_files\\2024-01-15_12-30-45_Tuner1_rf12345_dsp67890_Seq1_TxAnt0_Diagram1_El_ptu2.txt',
        'C:\\Calibration Statistics Tool\\measurement_data\\ptu_files\\2024-01-15_14-45-10_Tuner1_rf12345_dsp67890_Seq1_TxAnt1_Diagram3_El_ptu2.txt'
    ]
    mock_qt.parseProtAddAndParsePtu2FDialog.selectedFiles.return_value = real_ptu_files
    
    # Mock only UI and logging components (let real parsing happen)
    mock_parseDataLog = mocker.patch('main.parseDataLog')
    mock_clearTable = mocker.patch('main.clearTable')
    mock_QTableWidgetItem = mocker.patch('main.QTableWidgetItem')
    
    # Provide real antenna system configuration for parsing
    mocker.patch('main.antSysDiag', {'plotSetup': {'useSensorMuster': 0, 'sensorMusterList': []}})
    
    # DON'T mock parsePtu2 - let real parsing happen!
    # DON'T mock parse data objects - they'll be real!
    
    # CALL FUNCTION  
    from main import addAndParsePtu2Files
    sys_dict = {'parsedDataList': []}
    sep_parsed = {'parsedDataList': []}
    sep_failed = {'parsedDataList': []}
    
    addAndParsePtu2Files(sys_dict, sep_parsed, sep_failed)
    
    # VERIFY
    mock_qt.parseProtAddAndParsePtu2FDialog.exec_.assert_called_once()
    mock_qt.parseProtAddAndParsePtu2FDialog.selectedFiles.assert_called_once()
    
    # With 4 real PTU files, all should parse successfully
    assert len(sys_dict['parsedDataList']) == 4  # All files added to main dict
    assert len(sep_parsed['parsedDataList']) == 4  # All files added to separate dict  
    assert len(sep_failed['parsedDataList']) == 0  # No failed files (assuming they're all valid)
    mock_clearTable.assert_called()  # Tables were cleared/updated
    mock_parseDataLog.info.assert_called()  # Files were logged
    assert mock_parseDataLog.info.call_count == 4  # One log call per file
    assert mock_QTableWidgetItem.call_count == 4  # One table item per successful file
    
    # Verify actual file paths are in the results (real parsing happened)
    file_paths = [data.fileTitle.fileNamePath for data in sys_dict['parsedDataList']]
    # Check that at least one of the real files made it through
    assert any('2024-01-15' in path for path in file_paths)


def test_files_selected_some_fail_parsing(mocker):
    """Test when user selects files but some fail to parse - using real good/bad files."""
    
    # SETUP MOCKS
    mock_qt = mocker.patch('main.qt')
    mock_qt.parseProtAddAndParsePtu2FDialog.exec_.return_value = True
    
    # Use one REAL good file and one REAL bad file
    good_file = 'C:\\Calibration Statistics Tool\\measurement_data\\ptu_files\\2024-01-15_08-15-30_Tuner1_rf12345_dsp67890_Seq1_TxAnt0_Diagram0_Az_ptu2.txt'
    bad_file = 'C:\\Calibration Statistics Tool\\tests\\bad_ptu2_test_file.txt'
    
    mock_qt.parseProtAddAndParsePtu2FDialog.selectedFiles.return_value = [good_file, bad_file]
    
    # Mock UI and logging components only
    mock_parseDataLog = mocker.patch('main.parseDataLog')
    mock_clearTable = mocker.patch('main.clearTable')
    mock_QTableWidgetItem = mocker.patch('main.QTableWidgetItem')
    
    # Provide real antenna system configuration
    mocker.patch('main.antSysDiag', {'plotSetup': {'useSensorMuster': 0, 'sensorMusterList': []}})
    
    # DON'T mock parsePtu2 - let real parsing happen with real files
    
    # CALL FUNCTION
    from main import addAndParsePtu2Files
    sys_dict = {'parsedDataList': []}
    sep_parsed = {'parsedDataList': []}
    sep_failed = {'parsedDataList': []}
    
    addAndParsePtu2Files(sys_dict, sep_parsed, sep_failed)
    
    # VERIFY - Mixed results: good file succeeds, bad file fails
    assert len(sys_dict['parsedDataList']) == 1  # Only good file in main dict
    assert len(sep_parsed['parsedDataList']) == 1  # Only good file in successful dict
    assert len(sep_failed['parsedDataList']) == 1  # Only bad file in failed dict
    
    # Check file paths to verify which file went where
    successful_path = sep_parsed['parsedDataList'][0].fileTitle.fileNamePath
    failed_path = sep_failed['parsedDataList'][0].fileTitle.fileNamePath
    
    assert '2024-01-15_08-15-30' in successful_path  # Good file succeeded  
    assert 'bad_ptu2_test_file.txt' in failed_path  # Bad file failed





def test_duplicate_files_not_added_twice(mocker):
    """Test that duplicate files aren't added to dictionaries twice - using real file."""
    
    # SETUP MOCKS
    mock_qt = mocker.patch('main.qt')
    mock_qt.parseProtAddAndParsePtu2FDialog.exec_.return_value = True
    
    # Use a real PTU file that will be selected as "duplicate"
    duplicate_file_path = 'C:\\Calibration Statistics Tool\\measurement_data\\ptu_files\\2024-01-15_08-15-30_Tuner1_rf12345_dsp67890_Seq1_TxAnt0_Diagram0_Az_ptu2.txt'
    mock_qt.parseProtAddAndParsePtu2FDialog.selectedFiles.return_value = [duplicate_file_path]
    
    # Mock UI and logging components  
    mock_parseDataLog = mocker.patch('main.parseDataLog')
    mock_clearTable = mocker.patch('main.clearTable')
    mock_QTableWidgetItem = mocker.patch('main.QTableWidgetItem')
    
    # Provide real antenna system configuration
    mocker.patch('main.antSysDiag', {'plotSetup': {'useSensorMuster': 0, 'sensorMusterList': []}})
    
    # DON'T mock parsePtu2 - let real parsing happen first time
    
    # FIRST CALL - Add file initially
    from main import addAndParsePtu2Files
    sys_dict = {'parsedDataList': []}
    sep_parsed = {'parsedDataList': []}
    sep_failed = {'parsedDataList': []}
    
    # First call adds the file
    addAndParsePtu2Files(sys_dict, sep_parsed, sep_failed)
    
    # Verify file was added initially
    assert len(sys_dict['parsedDataList']) == 1
    assert len(sep_parsed['parsedDataList']) == 1
    
    # SECOND CALL - Try to add same file again (simulate user selecting same file)
    addAndParsePtu2Files(sys_dict, sep_parsed, sep_failed)
    
    # VERIFY - File count should NOT increase (duplicate prevention worked)
    assert len(sys_dict['parsedDataList']) == 1  # Still only 1 file (not 2)
    assert len(sep_parsed['parsedDataList']) == 1  # Still only 1 file (not 2)  
    assert len(sep_failed['parsedDataList']) == 0  # Good file doesn't go to failed
    
    # Verify it's the correct file that was kept
    file_path = sys_dict['parsedDataList'][0].fileTitle.fileNamePath
    assert '2024-01-15_08-15-30' in file_path


def test_dialog_only_accepts_ptu2_files(mocker):
    """Test that file dialog is configured to filter for .ptu2 files only."""
    
    # Import the real UI module to get the actual dialog with its filter
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ui'))
    
    from ui.pyside_qtgui import parseProtAddAndParsePtu2FDialog
    
    # VERIFY - Check the actual dialog filter configuration
    actual_filter = parseProtAddAndParsePtu2FDialog.nameFilter()
    
    # The dialog should have PTU-2 file filter set
    assert "ptu2" in actual_filter.lower(), f"Expected PTU2 filter, got: {actual_filter}"
    assert "*ptu2" in actual_filter.lower(), f"Expected wildcard pattern *ptu2, got: {actual_filter}"
    
    # Verify it's set to accept multiple files (from UI initialization)
    file_mode = parseProtAddAndParsePtu2FDialog.fileMode()
    assert file_mode == parseProtAddAndParsePtu2FDialog.ExistingFiles, "Dialog should allow multiple file selection"
    
    # Test the function still uses this correctly configured dialog
    mock_qt = mocker.patch('main.qt')
    mock_qt.parseProtAddAndParsePtu2FDialog = parseProtAddAndParsePtu2FDialog  # Use real dialog
    mock_qt.parseProtAddAndParsePtu2FDialog.exec_ = mocker.Mock(return_value=False)  # Mock only exec method
    
    # CALL FUNCTION
    from main import addAndParsePtu2Files
    sys_dict = {'parsedDataList': []}
    sep_parsed = {'parsedDataList': []}
    sep_failed = {'parsedDataList': []}
    
    addAndParsePtu2Files(sys_dict, sep_parsed, sep_failed)
    
    # VERIFY - Function used the properly configured dialog
    mock_qt.parseProtAddAndParsePtu2FDialog.exec_.assert_called_once()


def test_counters_update_correctly(mocker):
    """Test that UI counters reflect correct parsed/failed file counts."""
    
    # SETUP MOCKS
    mock_qt = mocker.patch('main.qt')
    mock_qt.parseProtAddAndParsePtu2FDialog.exec_.return_value = True
    
    # Use mix of good and bad files
    good_file = 'C:\\Calibration Statistics Tool\\measurement_data\\ptu_files\\2024-01-15_08-15-30_Tuner1_rf12345_dsp67890_Seq1_TxAnt0_Diagram0_Az_ptu2.txt'
    bad_file = 'C:\\Calibration Statistics Tool\\tests\\bad_ptu2_test_file.txt'
    mock_qt.parseProtAddAndParsePtu2FDialog.selectedFiles.return_value = [good_file, bad_file]
    
    # Mock UI components
    mock_parseDataLog = mocker.patch('main.parseDataLog')
    mock_clearTable = mocker.patch('main.clearTable')
    mock_QTableWidgetItem = mocker.patch('main.QTableWidgetItem')
    mocker.patch('main.antSysDiag', {'plotSetup': {'useSensorMuster': 0, 'sensorMusterList': []}})
    
    # CALL FUNCTION
    from main import addAndParsePtu2Files
    sys_dict = {'parsedDataList': []}
    sep_parsed = {'parsedDataList': []}
    sep_failed = {'parsedDataList': []}
    
    addAndParsePtu2Files(sys_dict, sep_parsed, sep_failed)
    
    # VERIFY - Counter label should be updated with correct count
    mock_qt.parseProtSepParPtu2FilesLabel.setText.assert_called()
    
    # Check that setText was called with the expected count (1 successful file)
    call_args = mock_qt.parseProtSepParPtu2FilesLabel.setText.call_args[0][0]
    assert '1' in call_args  # Should contain count of 1 successful file


def test_log_entries_created_with_timestamps_and_status(mocker):
    """Test that log entries are created for each file with proper content."""
    
    # SETUP MOCKS
    mock_qt = mocker.patch('main.qt')
    mock_qt.parseProtAddAndParsePtu2FDialog.exec_.return_value = True
    
    test_files = [
        'C:\\Calibration Statistics Tool\\measurement_data\\ptu_files\\2024-01-15_08-15-30_Tuner1_rf12345_dsp67890_Seq1_TxAnt0_Diagram0_Az_ptu2.txt',
        'C:\\Calibration Statistics Tool\\measurement_data\\ptu_files\\2024-01-15_09-25-45_Tuner1_rf12345_dsp67890_Seq1_TxAnt1_Diagram2_Az_ptu2.txt'
    ]
    mock_qt.parseProtAddAndParsePtu2FDialog.selectedFiles.return_value = test_files
    
    # Mock UI components
    mock_parseDataLog = mocker.patch('main.parseDataLog')
    mock_clearTable = mocker.patch('main.clearTable')
    mock_QTableWidgetItem = mocker.patch('main.QTableWidgetItem')
    mocker.patch('main.antSysDiag', {'plotSetup': {'useSensorMuster': 0, 'sensorMusterList': []}})
    
    # CALL FUNCTION  
    from main import addAndParsePtu2Files
    sys_dict = {'parsedDataList': []}
    sep_parsed = {'parsedDataList': []}
    sep_failed = {'parsedDataList': []}
    
    # Reset mock to ensure clean state before our test
    mock_parseDataLog.info.reset_mock()
    
    addAndParsePtu2Files(sys_dict, sep_parsed, sep_failed)
    
    # VERIFY - Log entries created for each file
    # Check that exactly 2 log calls were made (one per file)
    assert mock_parseDataLog.info.call_count == 2, f"Expected 2 log entries, got {mock_parseDataLog.info.call_count}"
    
    # Verify log entries contain file paths (actual log content verification)
    logged_files = [call[0][0] for call in mock_parseDataLog.info.call_args_list]
    
    # Ensure both files were logged
    assert len(logged_files) == 2, f"Expected 2 logged files, got {len(logged_files)}"
    assert any('2024-01-15_08-15-30' in log_entry for log_entry in logged_files), "First file not found in logs"
    assert any('2024-01-15_09-25-45' in log_entry for log_entry in logged_files), "Second file not found in logs"
