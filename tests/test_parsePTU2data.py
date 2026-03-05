"""
Tests for shared/parsePTU2data.py

Covers all public functions with known inputs and expected outputs.
Uses fixtures from conftest.py for realistic PTU2ParseData structures.

These tests serve as the regression baseline before Phase 2 vectorization.
Any optimisation must produce bit-identical results for all tests here.
"""
import sys
import os
import tempfile
import pytest
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

from shared.parsePTU2data import (
    AntennaLevelData, DiffPhaseData, ChirpMeasData, PtuPosMeasData,
    ChirpInfo, AntennaInfo, MeasSetupInfo, PTU2ParseData, FileTitle,
    parseFile, getAntennaData, getChirpData, getMeasData, interpretData,
)

SAMPLE_PTU_FILE = os.path.join(
    os.path.dirname(__file__), '..', 'measurement_data', 'ptu_files',
    '2024-01-15_08-15-30_Tuner1_rf12345_dsp67890_Seq1_TxAnt0_Diagram0_Az_ptu2.txt'
)


# ---------------------------------------------------------------------------
# Data model classes — one defaults check each
# ---------------------------------------------------------------------------

class TestAntennaLevelData:
    def test_defaults(self):
        obj = AntennaLevelData()
        assert obj.dLevel == -10000
        assert obj.dVarianzLevel == -10000


class TestDiffPhaseData:
    def test_defaults(self):
        obj = DiffPhaseData()
        assert obj.dDiffPhase == -10000
        assert obj.dVarianzDiffPhase == -10000


class TestChirpMeasData:
    def test_defaults(self):
        obj = ChirpMeasData([], [])
        assert obj.antennaLevelDataList == []
        assert obj.diffPhaseDataList == []


class TestPtuPosMeasData:
    def test_defaults(self):
        obj = PtuPosMeasData()
        assert obj.d_PTU_Angle == -10000
        assert obj.chirpMeasDataList == []


class TestChirpInfo:
    def test_defaults(self):
        obj = ChirpInfo()
        assert obj.chirp == 0
        assert obj.active == 0
        assert obj.centerFrequency == 0
        assert obj.diffPhaseOffsetList == []


class TestAntennaInfo:
    def test_defaults(self):
        obj = AntennaInfo()
        assert obj.rfSerial is None
        assert obj.antennaType == 0
        assert obj.nofAntennas == 0
        assert obj.nofAntennaDiffValues == 0
        assert obj.antennaDistancesList == []
        assert obj.getNofAntennaDiffValues() == 0


class TestMeasSetupInfo:
    def test_defaults(self):
        obj = MeasSetupInfo()
        assert obj.phyDoppGenDist == 0
        assert obj.doppGenHeightPtuZero == 0
        assert obj.rfBoardMidHeightPtuZero == 0
        assert obj.sensorUpsideDown == 0
        assert obj.antennaDiagramType == ''
        assert obj.oppositeToPanAngle == 0
        assert obj.phyDoppGenDistFound == 0
        assert obj.doppGenHeightPtuZeroFound == 0
        assert obj.rfBoardMidHeightPtuZeroFound == 0
        assert obj.sensorUpsideDownFound == 0
        assert obj.antennaDiagramTypeFound == 0
        assert obj.oppositeToPanAngleFound == 0


# ---------------------------------------------------------------------------
# PTU2ParseData
# ---------------------------------------------------------------------------

class TestPTU2ParseData:
    def test_defaults(self):
        obj = PTU2ParseData()
        assert isinstance(obj.bDataValid, bool)
        assert obj.bDataValid == False
        assert obj.fileNamePath == ''
        assert obj.errorList == []
        assert isinstance(obj.antennaInfo, AntennaInfo)
        assert obj.chirpInfoList == []
        assert obj.ptuPosDataList == []
        assert isinstance(obj.fileTitle, FileTitle)
        assert isinstance(obj.measSetupInfo, MeasSetupInfo)

    def test_parse_file_sets_data_valid_true_on_good_file(self):
        # Integration test - uses real file
        obj = PTU2ParseData()
        obj.parseFile(SAMPLE_PTU_FILE, 0, [])
        assert obj.bDataValid == True
        assert len(obj.errorList) == 0
        assert obj.fileNamePath == SAMPLE_PTU_FILE
        assert len(obj.ptuPosDataList) > 0  # Should have parsed some data

    def test_parse_file_populates_ptu_pos_data_list(self):
        obj = PTU2ParseData()
        obj.parseFile(SAMPLE_PTU_FILE, 0, [])
        assert len(obj.ptuPosDataList) > 0
        # Check that first position has expected structure
        first_pos = obj.ptuPosDataList[0]
        assert isinstance(first_pos.d_PTU_Angle, float)
        assert len(first_pos.chirpMeasDataList) == PTU2ParseData.MAX_CHIRP

    def test_parse_file_sets_data_valid_false_on_missing_file(self):
        obj = PTU2ParseData()
        obj.parseFile("nonexistent_file.txt", 0, [])
        assert obj.bDataValid == False
        assert len(obj.errorList) > 0
        assert "File does not exist" in obj.errorList[0]

    def test_parse_file_appends_error_on_missing_file(self):
        obj = PTU2ParseData()
        obj.parseFile("nonexistent_file.txt", 0, [])
        assert len(obj.errorList) == 1
        assert obj.errorList[0].endswith("File does not exist! Insert a valid file path.")


# ---------------------------------------------------------------------------
# FileTitle.parseFileTitle
# ---------------------------------------------------------------------------

class TestFileTitle:


    fileTitleFull= "2024-01-15_08-15-30_Tuner1_rf12345_dsp67890_Seq1_TxAnt0_Diagram0_Az_ptu2.txt"
    fileTitleNoTuner= "2024-01-15_08-15-30_rf12345_dsp67890_Seq1_TxAnt0_Diagram0_Az_ptu2.txt"
    fileTitleNoRf= "2024-01-15_08-15-30_Tuner1_dsp67890_Seq1_TxAnt0_Diagram0_Az_ptu2.txt"
    fileTitleNoDsp= "2024-01-15_08-15-30_Tuner1_rf12345_Seq1_TxAnt0_Diagram0_Az_ptu2.txt"
    fileTitleNoSeq= "2024-01-15_08-15-30_Tuner1_rf12345_dsp67890_TxAnt0_Diagram0_Az_ptu2.txt"
    fileTitleNoTxAnt= "2024-01-15_08-15-30_Tuner1_rf12345_dsp67890_Seq1_Diagram0_Az_ptu2.txt"
    fileTitleNoDiagram= "2024-01-15_08-15-30_Tuner1_rf12345_dsp67890_Seq1_TxAnt0_Az_ptu2.txt"
    fileTitleNoDateAndTime= "Tuner1_rf12345_dsp67890_Seq1_TxAnt0_Diagram0_Az_ptu2.txt"

    def test_not_use_sensor_muster(self):
        obj = FileTitle()
        useSensorMuster = 0
        sensorMusterList=[]
        obj.parseFileTitle(self.fileTitleFull, useSensorMuster, sensorMusterList)
        assert obj.useSensorMuster == 0
        assert obj.dateAndTimeFound == 1
        assert obj.tunerFound == 1
        assert obj.rfFound  == 1
        assert obj.dspFound == 1
        assert obj.txAntFound   == 1
        assert obj.seqNumFound  == 1
        assert obj.diagramFound == 1
        assert obj.sensorFound == 1
        

    def test_sensor_muster_list_empty(self):
        obj = FileTitle()
        useSensorMuster = 1
        sensorMusterList=[]
        obj.parseFileTitle(self.fileTitleFull, useSensorMuster, sensorMusterList)
        assert obj.sensorMusterFoundDict == {}

    def test_default_fields_are_empty_or_zero(self):
        obj = FileTitle()
        assert obj.dateAndTime == ''
        assert obj.sensor == ''
        assert obj.tuner == ''
        assert obj.txAnt == 0
        assert obj.seqNum == 0
        assert obj.diagram == 0
        assert obj.rf == ''
        assert obj.dsp == ''
        assert obj.dateAndTimeFound == 0
        assert obj.tunerFound == 0
        assert obj.rfFound == 0
        assert obj.dspFound == 0
        assert obj.txAntFound == 0
        assert obj.seqNumFound == 0
        assert obj.diagramFound == 0
        assert obj.sensorFound == 0

    def test_sensor_muster_with_valid_list(self):
        obj = FileTitle()
        sensorMusterList = ['rf', 'dsp']
        obj.parseFileTitle(self.fileTitleFull, 1, sensorMusterList)
        assert obj.useSensorMuster == 1
        assert obj.sensorMusterFoundDict == {'rf': 1, 'dsp': 1}
        assert obj.sensorMusterValueDict == {'rf': 'rf12345', 'dsp': 'dsp67890'}
        assert obj.sensorFound == 1
        assert obj.sensor == 'rf12345_dsp67890'

    def test_sensor_muster_partial_match(self):
        obj = FileTitle()
        sensorMusterList = ['rf', 'dsp', 'PT']
        obj.parseFileTitle(self.fileTitleFull, 1, sensorMusterList)
        assert obj.sensorMusterFoundDict == {'rf': 1, 'dsp': 1, 'PT': 0}
        assert obj.sensorFound == 0

    def test_parses_date_and_time_from_filename(self):
        obj = FileTitle()
        useSensorMuster = 0
        sensorMusterList=[]
        obj.parseFileTitle(self.fileTitleNoDateAndTime, useSensorMuster, sensorMusterList)
        assert obj.dateAndTimeFound == 0    
        assert obj.useSensorMuster == 0
        assert obj.tunerFound == 1
        assert obj.rfFound  == 1
        assert obj.dspFound == 1
        assert obj.txAntFound   == 1
        assert obj.seqNumFound  == 1
        assert obj.diagramFound == 1
        assert obj.sensorFound == 1

    def test_parses_tuner_from_filename(self):
        obj = FileTitle()
        useSensorMuster = 0
        sensorMusterList=[]
        obj.parseFileTitle(self.fileTitleNoTuner, useSensorMuster, sensorMusterList)
        assert obj.dateAndTimeFound == 1    
        assert obj.useSensorMuster == 0
        assert obj.tunerFound == 0
        assert obj.rfFound  == 1
        assert obj.dspFound == 1
        assert obj.txAntFound   == 1
        assert obj.seqNumFound  == 1
        assert obj.diagramFound == 1
        assert obj.sensorFound == 1

    def test_parses_rf_from_filename(self):
        obj = FileTitle()
        obj.parseFileTitle(self.fileTitleNoRf, 0, [])
        assert obj.dateAndTimeFound == 1
        assert obj.tunerFound == 1
        assert obj.rfFound == 0
        assert obj.dspFound == 1
        assert obj.txAntFound == 1
        assert obj.seqNumFound == 1
        assert obj.diagramFound == 1
        assert obj.sensorFound == 0

    def test_parses_dsp_from_filename(self):
        obj = FileTitle()
        obj.parseFileTitle(self.fileTitleNoDsp, 0, [])
        assert obj.dateAndTimeFound == 1
        assert obj.tunerFound == 1
        assert obj.rfFound == 1
        assert obj.dspFound == 0
        assert obj.txAntFound == 1
        assert obj.seqNumFound == 1
        assert obj.diagramFound == 1
        assert obj.sensorFound == 1
        assert obj.sensor == 'rf12345'

    def test_parses_tx_ant_from_filename(self):
        obj = FileTitle()
        obj.parseFileTitle(self.fileTitleNoTxAnt, 0, [])
        assert obj.dateAndTimeFound == 1
        assert obj.tunerFound == 1
        assert obj.rfFound == 1
        assert obj.dspFound == 1
        assert obj.txAntFound == 0
        assert obj.seqNumFound == 1
        assert obj.diagramFound == 1
        assert obj.sensorFound == 1

    def test_parses_seq_num_from_filename(self):
        obj = FileTitle()
        obj.parseFileTitle(self.fileTitleNoSeq, 0, [])
        assert obj.dateAndTimeFound == 1
        assert obj.tunerFound == 1
        assert obj.rfFound == 1
        assert obj.dspFound == 1
        assert obj.txAntFound == 1
        assert obj.seqNumFound == 0
        assert obj.diagramFound == 1
        assert obj.sensorFound == 1

    def test_parses_diagram_from_filename(self):
        obj = FileTitle()
        obj.parseFileTitle(self.fileTitleNoDiagram, 0, [])
        assert obj.dateAndTimeFound == 1
        assert obj.tunerFound == 1
        assert obj.rfFound == 1
        assert obj.dspFound == 1
        assert obj.txAntFound == 1
        assert obj.seqNumFound == 1
        assert obj.diagramFound == 0
        assert obj.sensorFound == 1

    def test_sensor_built_from_rf_and_dsp(self):
        obj = FileTitle()
        obj.parseFileTitle(self.fileTitleFull, 0, [])
        assert obj.sensor == 'rf12345_dsp67890'
        assert obj.sensorFound == 1

    def test_filename_without_tuner_leaves_tuner_empty(self):
        obj = FileTitle()
        obj.parseFileTitle(self.fileTitleNoTuner, 0, [])
        assert obj.tuner == ''
        assert obj.tunerFound == 0


# ---------------------------------------------------------------------------
# getAntennaData
# ---------------------------------------------------------------------------

class TestGetAntennaData:
    # From the sample file:  12345;1;3;3;5000;10000;5000
    # rfSerial=12345, antennaType=1, nofAntennas=3, nofDiff=3
    # distances [0.01mm → m]: 5000*0.01e-3=0.05, 10000*0.01e-3=0.1, 5000*0.01e-3=0.05

    @staticmethod
    def _make_antenna_line():
        return ['12345', '1', '3', '3', '5000', '10000', '5000']

    def test_returns_true_on_valid_input(self):
        result = getAntennaData(self._make_antenna_line(), PTU2ParseData())
        assert result == True

    def test_populates_rf_serial(self):
        ptu2ParseData = PTU2ParseData()
        getAntennaData(self._make_antenna_line(), ptu2ParseData)
        assert ptu2ParseData.antennaInfo.rfSerial == 12345

    def test_populates_antenna_type(self):
        ptu2ParseData = PTU2ParseData()
        getAntennaData(self._make_antenna_line(), ptu2ParseData)
        assert ptu2ParseData.antennaInfo.antennaType == 1

    def test_populates_nof_antennas(self):
        ptu2ParseData = PTU2ParseData()
        getAntennaData(self._make_antenna_line(), ptu2ParseData)
        assert ptu2ParseData.antennaInfo.nofAntennas == 3

    def test_antenna_distances_unit_conversion(self):
        # distances are stored as [m], input is in [0.01 mm]
        ptu2ParseData = PTU2ParseData()
        getAntennaData(self._make_antenna_line(), ptu2ParseData)
        dists = ptu2ParseData.antennaInfo.antennaDistancesList
        assert dists[0] == pytest.approx(0.05)
        assert dists[1] == pytest.approx(0.1)
        assert dists[2] == pytest.approx(0.05)

    def test_returns_false_on_too_few_columns(self):
        ptu2ParseData = PTU2ParseData()
        result = getAntennaData(['1', '2', '3'], ptu2ParseData)  # < 4 required
        assert result == False

    def test_appends_error_on_failure(self):
        ptu2ParseData = PTU2ParseData()
        ptu2ParseData.fileNamePath = 'testfile.txt'
        getAntennaData(['X', 'X', 'X'], ptu2ParseData)
        assert len(ptu2ParseData.errorList) > 0
        assert 'Error 1' in ptu2ParseData.errorList[0]

    def test_returns_false_on_non_numeric_values(self):
        ptu2ParseData = PTU2ParseData()
        result = getAntennaData(['X', 'X', 'X', 'X'], ptu2ParseData)
        assert result == False


# ---------------------------------------------------------------------------
# getChirpData
# ---------------------------------------------------------------------------

class TestGetChirpData:
    # From sample file chirp line:  0;1;770;0.5;1.0;1.5
    # chirp=0, active=1, centerFreq=770*1e4=7_700_000 Hz, diffPhaseOffsets=[0.5,1.0,1.5]

    @staticmethod
    def _make_chirp_input():
        ptu2ParseData = PTU2ParseData()
        ptu2ParseData.antennaInfo.antennaDistancesList = [0.0, 0.0, 0.0]  # nofDiff=3
        lineArray = ['0', '1', '770', '0.5', '1.0', '1.5']
        return ptu2ParseData, lineArray

    def test_returns_true_on_valid_input(self):
        ptu2ParseData, lineArray = self._make_chirp_input()
        assert getChirpData(lineArray, ptu2ParseData) == True

    def test_center_frequency_scaled_to_hz(self):
        # input is in [10 kHz], stored as [Hz]
        ptu2ParseData, lineArray = self._make_chirp_input()
        getChirpData(lineArray, ptu2ParseData)
        assert ptu2ParseData.chirpInfoList[0].centerFrequency == pytest.approx(7_700_000)

    def test_active_flag_stored(self):
        ptu2ParseData, lineArray = self._make_chirp_input()
        getChirpData(lineArray, ptu2ParseData)
        assert ptu2ParseData.chirpInfoList[0].active == 1.0

    def test_diff_phase_offsets_stored(self):
        ptu2ParseData, lineArray = self._make_chirp_input()
        getChirpData(lineArray, ptu2ParseData)
        assert ptu2ParseData.chirpInfoList[0].diffPhaseOffsetList == [0.5, 1.0, 1.5]

    def test_chirp_appended_to_chirp_info_list(self):
        ptu2ParseData, lineArray = self._make_chirp_input()
        assert len(ptu2ParseData.chirpInfoList) == 0
        getChirpData(lineArray, ptu2ParseData)
        assert len(ptu2ParseData.chirpInfoList) == 1

    def test_returns_false_on_wrong_column_count(self):
        ptu2ParseData, lineArray = self._make_chirp_input()
        assert getChirpData(lineArray[:-1], ptu2ParseData) == False

    def test_returns_false_on_non_numeric_frequency(self):
        ptu2ParseData, lineArray = self._make_chirp_input()
        lineArray[2] = 'X'
        assert getChirpData(lineArray, ptu2ParseData) == False


# ---------------------------------------------------------------------------
# getMeasData
# ---------------------------------------------------------------------------

class TestGetMeasData:
    # nofAntennas=2, nofDiff=1  →  nofChirpValues=6  →  line length=25
    # chirp k, antenna a:  level=[1 + 6k + 2a],  variance=[2 + 6k + 2a]
    # chirp k, diff d:     phase=[5 + 6k + 2d],  variance=[6 + 6k + 2d]

    @staticmethod
    def _make_valid_input(nof_antennas=2, nof_diff=1):
        """Return (ptu2ParseData, lineArray, nofChirpValues) for a valid getMeasData call."""
        ptu2ParseData = PTU2ParseData()
        ptu2ParseData.antennaInfo.nofAntennas = nof_antennas
        ptu2ParseData.antennaInfo.antennaDistancesList = [0.0] * nof_diff
        nofChirpValues = 2 * (nof_antennas + ptu2ParseData.antennaInfo.getNofAntennaDiffValues())
        length = 1 + PTU2ParseData.MAX_CHIRP * nofChirpValues
        lineArray = ['0.0'] * length
        return ptu2ParseData, lineArray, nofChirpValues

    def test_wrong_line_length(self):
        ptu2ParseData, lineArray, _ = self._make_valid_input()
        short_array = lineArray[:-2]  # two elements too short
        result = getMeasData(short_array, ptu2ParseData)
        assert result == False

    def test_returns_true_on_valid_input(self):
        ptu2ParseData, lineArray, _ = self._make_valid_input()
        result = getMeasData(lineArray, ptu2ParseData)
        assert result == True

    def test_ptu_angle_parsed_correctly(self):
        ptu2ParseData, lineArray, _ = self._make_valid_input()
        lineArray[0] = '45.5'
        getMeasData(lineArray, ptu2ParseData)
        assert ptu2ParseData.ptuPosDataList[0].d_PTU_Angle == 45.5

    def test_antenna_level_parsed_for_each_antenna(self):
        ptu2ParseData, lineArray, nofChirpValues = self._make_valid_input(nof_antennas=2, nof_diff=1)
        # chirp 0, ant 0 level at index 1; ant 1 level at index 3
        lineArray[1] = '10.0'
        lineArray[3] = '20.0'
        getMeasData(lineArray, ptu2ParseData)
        chirp0 = ptu2ParseData.ptuPosDataList[0].chirpMeasDataList[0]
        assert chirp0.antennaLevelDataList[0].dLevel == 10.0
        assert chirp0.antennaLevelDataList[1].dLevel == 20.0

    def test_antenna_level_variance_parsed(self):
        ptu2ParseData, lineArray, nofChirpValues = self._make_valid_input(nof_antennas=2, nof_diff=1)
        # chirp 0, ant 0 variance at index 2; ant 1 variance at index 4
        lineArray[2] = '1.5'
        lineArray[4] = '2.5'
        getMeasData(lineArray, ptu2ParseData)
        chirp0 = ptu2ParseData.ptuPosDataList[0].chirpMeasDataList[0]
        assert chirp0.antennaLevelDataList[0].dVarianzLevel == 1.5
        assert chirp0.antennaLevelDataList[1].dVarianzLevel == 2.5

    def test_diff_phase_parsed_for_each_diff_pair(self):
        ptu2ParseData, lineArray, nofChirpValues = self._make_valid_input(nof_antennas=2, nof_diff=1)
        # chirp 0, diff 0 phase at index 1 + 2*2 + 0 = 5
        lineArray[5] = '33.3'
        getMeasData(lineArray, ptu2ParseData)
        chirp0 = ptu2ParseData.ptuPosDataList[0].chirpMeasDataList[0]
        assert chirp0.diffPhaseDataList[0].dDiffPhase == 33.3

    def test_diff_phase_variance_parsed(self):
        ptu2ParseData, lineArray, nofChirpValues = self._make_valid_input(nof_antennas=2, nof_diff=1)
        # chirp 0, diff 0 variance at index 2 + 2*2 + 0 = 6
        lineArray[6] = '4.4'
        getMeasData(lineArray, ptu2ParseData)
        chirp0 = ptu2ParseData.ptuPosDataList[0].chirpMeasDataList[0]
        assert chirp0.diffPhaseDataList[0].dVarianzDiffPhase == 4.4

    def test_appends_one_entry_to_ptu_pos_data_list(self):
        ptu2ParseData, lineArray, _ = self._make_valid_input()
        assert len(ptu2ParseData.ptuPosDataList) == 0
        getMeasData(lineArray, ptu2ParseData)
        assert len(ptu2ParseData.ptuPosDataList) == 1

    def test_returns_false_on_wrong_column_count(self):
        ptu2ParseData, lineArray, _ = self._make_valid_input()
        result = getMeasData(lineArray[:-1], ptu2ParseData)  # one element short
        assert result == False

    def test_returns_false_on_non_numeric_angle(self):
        ptu2ParseData, lineArray, _ = self._make_valid_input()
        lineArray[0] = 'X'
        result = getMeasData(lineArray, ptu2ParseData)
        assert result == False


# ---------------------------------------------------------------------------
# interpretData / parseFile  (integration-style)
# ---------------------------------------------------------------------------

class TestInterpretData:
    # Sample file values:
    #   Gen21a_PhysicalDopplergenDistance[cm]:150.0
    #   Gen21c_DopplerGenHeightToPtuZero[cm]:85.0
    #   Gen21d_RFBoardMiddleHeightToPtuZero[cm]:45.0
    #   Ptu02_PtuSensorUpsideDown0
    #   AntennaDiagrammType[1]:Az
    #   OppositeToPanAngle[deg]:0

    @staticmethod
    def _parsed_sample():
        obj = PTU2ParseData()
        interpretData(SAMPLE_PTU_FILE, obj)
        return obj

    @staticmethod
    def _write_temp(content):
        f = tempfile.NamedTemporaryFile(
            mode='w', suffix='.txt', delete=False, encoding='utf-8'
        )
        f.write(content)
        f.close()
        return f.name

    def test_meas_setup_phy_dopp_gen_dist_parsed(self):
        obj = self._parsed_sample()
        assert obj.measSetupInfo.phyDoppGenDistFound == 1
        assert obj.measSetupInfo.phyDoppGenDist == pytest.approx(150.0)

    def test_meas_setup_dopp_gen_height_parsed(self):
        obj = self._parsed_sample()
        assert obj.measSetupInfo.doppGenHeightPtuZeroFound == 1
        assert obj.measSetupInfo.doppGenHeightPtuZero == pytest.approx(85.0)

    def test_meas_setup_rf_board_height_parsed(self):
        obj = self._parsed_sample()
        assert obj.measSetupInfo.rfBoardMidHeightPtuZeroFound == 1
        assert obj.measSetupInfo.rfBoardMidHeightPtuZero == pytest.approx(45.0)

    def test_meas_setup_sensor_upside_down_parsed(self):
        obj = self._parsed_sample()
        assert obj.measSetupInfo.sensorUpsideDownFound == 1
        assert obj.measSetupInfo.sensorUpsideDown == 0

    def test_meas_setup_antenna_diagram_type_parsed(self):
        obj = self._parsed_sample()
        assert obj.measSetupInfo.antennaDiagramTypeFound == 1
        assert obj.measSetupInfo.antennaDiagramType == 'Az'

    def test_meas_setup_opposite_to_pan_angle_parsed(self):
        obj = self._parsed_sample()
        assert obj.measSetupInfo.oppositeToPanAngleFound == 1
        assert obj.measSetupInfo.oppositeToPanAngle == 0

    def test_error_added_when_header_missing(self):
        path = self._write_temp('Gen21a_PhysicalDopplergenDistance[cm]:150.0\nno header line\n')
        try:
            obj = PTU2ParseData()
            interpretData(path, obj)
            assert any('could not find header' in e for e in obj.errorList)
        finally:
            os.unlink(path)

    def test_error_added_when_antenna_data_missing(self):
        # Header present, but the only subsequent line has < 4 columns
        content = 'PTU-Angle[°];Level-Ant0[dB]\nonly one col\n'
        path = self._write_temp(content)
        try:
            obj = PTU2ParseData()
            interpretData(path, obj)
            assert any('could not find antenna data' in e for e in obj.errorList)
        finally:
            os.unlink(path)

    def test_error_added_when_fewer_than_max_chirps(self):
        # Antenna data (nofAntennas=2, nofDiff=1) + only 2 chirp lines
        content = (
            'PTU-Angle[°];Level-Ant0[dB]\n'
            '12345;1;2;1;5000\n'
            '0;1;770;0.5\n'
            '1;1;770;0.5\n'
        )
        path = self._write_temp(content)
        try:
            obj = PTU2ParseData()
            interpretData(path, obj)
            assert any('Chirp data' in e for e in obj.errorList)
        finally:
            os.unlink(path)

    def test_full_file_produces_no_errors(self):
        obj = self._parsed_sample()
        assert obj.errorList == []

    def test_full_file_correct_number_of_ptu_positions(self):
        obj = self._parsed_sample()
        assert len(obj.ptuPosDataList) > 0
        # First angle in sample file is -90.0
        assert obj.ptuPosDataList[0].d_PTU_Angle == pytest.approx(-90.0)

    def test_full_file_all_four_chirps_parsed(self):
        obj = self._parsed_sample()
        for pos in obj.ptuPosDataList:
            assert len(pos.chirpMeasDataList) == PTU2ParseData.MAX_CHIRP


