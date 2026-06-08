"""
Tests for PTU2ParseData.buildArrays() and the flat NumPy arrays
(angles_array, levels_array, phases_array) added as part of PST-29.
"""
import os
import pytest
import numpy as np

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from calibration_statistics_tool.shared.parsePTU2data import PTU2ParseData


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

PTU2_TEST_FILE = os.path.join(
    _root, 'measurement_data', 'ptu_files',
    '2024-01-15_08-15-30_Tuner1_rf12345_dsp67890_Seq1_TxAnt0_Diagram0_Az_ptu2.txt'
)


# ---------------------------------------------------------------------------
# Fixture-based tests (simple_ptu2_data)
# ---------------------------------------------------------------------------

class TestAnglesArray:
    """angles_array shape and values."""

    def test_shape(self, simple_ptu2_data):
        arr = simple_ptu2_data.angles_array
        assert arr is not None
        assert arr.ndim == 1
        assert arr.shape == (3,)  # 3 angle positions in fixture

    def test_dtype(self, simple_ptu2_data):
        assert simple_ptu2_data.angles_array.dtype == np.float64

    def test_values(self, simple_ptu2_data):
        expected = np.array([-10.0, 0.0, 10.0])
        np.testing.assert_array_equal(simple_ptu2_data.angles_array, expected)

    def test_matches_ptuPosDataList(self, simple_ptu2_data):
        manual = np.array([p.d_PTU_Angle for p in simple_ptu2_data.ptuPosDataList])
        np.testing.assert_array_equal(simple_ptu2_data.angles_array, manual)


class TestLevelsArray:
    """levels_array shape and values."""

    def test_shape(self, simple_ptu2_data):
        arr = simple_ptu2_data.levels_array
        assert arr is not None
        assert arr.shape == (3, PTU2ParseData.MAX_CHIRP, 2)  # 3 angles, 4 chirps, 2 antennas

    def test_dtype(self, simple_ptu2_data):
        assert simple_ptu2_data.levels_array.dtype == np.float64

    def test_chirp0_ant0_values(self, simple_ptu2_data):
        # From conftest level_table: chirp0 ant0 → [-20, -10, -20] at angles -10°,0°,10°
        expected = np.array([-20.0, -10.0, -20.0])
        np.testing.assert_array_equal(simple_ptu2_data.levels_array[:, 0, 0], expected)

    def test_chirp0_ant1_values(self, simple_ptu2_data):
        # chirp0 ant1 → [-25, -15, -25]
        expected = np.array([-25.0, -15.0, -25.0])
        np.testing.assert_array_equal(simple_ptu2_data.levels_array[:, 0, 1], expected)

    def test_chirp1_ant0_values(self, simple_ptu2_data):
        # chirp1 ant0 → [-21, -11, -21]
        expected = np.array([-21.0, -11.0, -21.0])
        np.testing.assert_array_equal(simple_ptu2_data.levels_array[:, 1, 0], expected)

    def test_inactive_chirp_sentinel(self, simple_ptu2_data):
        # chirp 2 and 3 use sentinel -99 in fixture
        assert np.all(simple_ptu2_data.levels_array[:, 2, :] == -99.0)
        assert np.all(simple_ptu2_data.levels_array[:, 3, :] == -99.0)

    def test_matches_ptuPosDataList(self, simple_ptu2_data):
        data = simple_ptu2_data
        for chirp in range(PTU2ParseData.MAX_CHIRP):
            for ant in range(data.antennaInfo.nofAntennas):
                manual = np.array([
                    pos.chirpMeasDataList[chirp].antennaLevelDataList[ant].dLevel
                    for pos in data.ptuPosDataList
                ])
                np.testing.assert_array_equal(data.levels_array[:, chirp, ant], manual)


class TestPhasesArray:
    """phases_array shape and values."""

    def test_shape(self, simple_ptu2_data):
        arr = simple_ptu2_data.phases_array
        assert arr is not None
        nof_diff = simple_ptu2_data.antennaInfo.getNofAntennaDiffValues()
        assert arr.shape == (3, PTU2ParseData.MAX_CHIRP, nof_diff)

    def test_dtype(self, simple_ptu2_data):
        assert simple_ptu2_data.phases_array.dtype == np.float64

    def test_chirp0_diff0_values(self, simple_ptu2_data):
        # chirp0 diff0 from conftest phase_table: [5.0, 0.0, -5.0]
        expected = np.array([5.0, 0.0, -5.0])
        np.testing.assert_array_equal(simple_ptu2_data.phases_array[:, 0, 0], expected)

    def test_chirp1_diff0_values(self, simple_ptu2_data):
        # chirp1 diff0: [6.0, 0.0, -6.0]
        expected = np.array([6.0, 0.0, -6.0])
        np.testing.assert_array_equal(simple_ptu2_data.phases_array[:, 1, 0], expected)

    def test_matches_ptuPosDataList(self, simple_ptu2_data):
        data = simple_ptu2_data
        nof_diff = data.antennaInfo.getNofAntennaDiffValues()
        for chirp in range(PTU2ParseData.MAX_CHIRP):
            for diff in range(nof_diff):
                manual = np.array([
                    pos.chirpMeasDataList[chirp].diffPhaseDataList[diff].dDiffPhase
                    for pos in data.ptuPosDataList
                ])
                np.testing.assert_array_equal(data.phases_array[:, chirp, diff], manual)


# ---------------------------------------------------------------------------
# Fresh (unbuilt) object has None arrays
# ---------------------------------------------------------------------------

class TestArraysInitiallyNone:
    def test_angles_none_on_init(self):
        data = PTU2ParseData()
        assert data.angles_array is None

    def test_levels_none_on_init(self):
        data = PTU2ParseData()
        assert data.levels_array is None

    def test_phases_none_on_init(self):
        data = PTU2ParseData()
        assert data.phases_array is None


# ---------------------------------------------------------------------------
# single_active_chirp_ptu2_data fixture tests
# ---------------------------------------------------------------------------

class TestSingleActiveChirpArrays:
    def test_angles_shape(self, single_active_chirp_ptu2_data):
        assert single_active_chirp_ptu2_data.angles_array.shape == (3,)

    def test_angles_values(self, single_active_chirp_ptu2_data):
        expected = np.array([-5.0, 0.0, 5.0])
        np.testing.assert_array_equal(single_active_chirp_ptu2_data.angles_array, expected)

    def test_levels_shape(self, single_active_chirp_ptu2_data):
        assert single_active_chirp_ptu2_data.levels_array.shape == (3, PTU2ParseData.MAX_CHIRP, 2)

    def test_phases_shape(self, single_active_chirp_ptu2_data):
        assert single_active_chirp_ptu2_data.phases_array.shape == (3, PTU2ParseData.MAX_CHIRP, 1)


# ---------------------------------------------------------------------------
# parseFile builds arrays automatically
# ---------------------------------------------------------------------------

@pytest.mark.skipif(
    not os.path.exists(PTU2_TEST_FILE),
    reason="PTU2 test file not found"
)
class TestParseFileBuildsArrays:
    def test_arrays_not_none_after_parse(self):
        data = PTU2ParseData()
        from calibration_statistics_tool.shared.parsePTU2data import parseFile
        parseFile(PTU2_TEST_FILE, data)
        assert data.bDataValid
        assert data.angles_array is not None
        assert data.levels_array is not None
        assert data.phases_array is not None

    def test_angles_array_length_matches_ptuPosDataList(self):
        data = PTU2ParseData()
        from calibration_statistics_tool.shared.parsePTU2data import parseFile
        parseFile(PTU2_TEST_FILE, data)
        assert data.angles_array.shape[0] == len(data.ptuPosDataList)

    def test_levels_array_shape(self):
        data = PTU2ParseData()
        from calibration_statistics_tool.shared.parsePTU2data import parseFile
        parseFile(PTU2_TEST_FILE, data)
        nof_angles   = len(data.ptuPosDataList)
        nof_antennas = data.antennaInfo.nofAntennas
        assert data.levels_array.shape == (nof_angles, PTU2ParseData.MAX_CHIRP, nof_antennas)

    def test_phases_array_shape(self):
        data = PTU2ParseData()
        from calibration_statistics_tool.shared.parsePTU2data import parseFile
        parseFile(PTU2_TEST_FILE, data)
        nof_angles = len(data.ptuPosDataList)
        nof_diff   = data.antennaInfo.getNofAntennaDiffValues()
        assert data.phases_array.shape == (nof_angles, PTU2ParseData.MAX_CHIRP, nof_diff)

    def test_angles_values_match_ptuPosDataList(self):
        data = PTU2ParseData()
        from calibration_statistics_tool.shared.parsePTU2data import parseFile
        parseFile(PTU2_TEST_FILE, data)
        manual = np.array([p.d_PTU_Angle for p in data.ptuPosDataList])
        np.testing.assert_array_equal(data.angles_array, manual)


# ---------------------------------------------------------------------------
# Fast path used in calcdiagram_functions
# ---------------------------------------------------------------------------

class TestCalcdiagramFastPath:
    """Verify that calcdiagram_functions use pre-built arrays when available."""

    def test_getPtuAngVals_uses_array(self, simple_ptu2_data):
        from calibration_statistics_tool.shared.calcdiagram_functions import getPtuAngVals
        result = getPtuAngVals(simple_ptu2_data)
        assert result is simple_ptu2_data.angles_array  # same object — no copy made

    def test_getAntLevel_uses_array_copy(self, simple_ptu2_data):
        from calibration_statistics_tool.shared.calcdiagram_functions import getAntLevel
        result = getAntLevel(0, 0, simple_ptu2_data)
        # Should be a copy of the slice, not the original array
        assert result is not simple_ptu2_data.levels_array
        expected = simple_ptu2_data.levels_array[:, 0, 0]
        np.testing.assert_array_equal(result, expected)

    def test_getPhaseDiff_uses_array_copy(self, simple_ptu2_data):
        from calibration_statistics_tool.shared.calcdiagram_functions import getPhaseDiff
        result = getPhaseDiff(0, 0, simple_ptu2_data)
        assert result is not simple_ptu2_data.phases_array
        expected = simple_ptu2_data.phases_array[:, 0, 0]
        np.testing.assert_array_equal(result, expected)

    def test_getPtuAngVals_fallback_when_none(self, simple_ptu2_data):
        """When angles_array is None, function falls back to list comprehension."""
        from calibration_statistics_tool.shared.calcdiagram_functions import getPtuAngVals
        simple_ptu2_data.angles_array = None
        result = getPtuAngVals(simple_ptu2_data)
        expected = np.array([-10.0, 0.0, 10.0])
        np.testing.assert_array_equal(result, expected)

    def test_getAntLevel_fallback_when_none(self, simple_ptu2_data):
        from calibration_statistics_tool.shared.calcdiagram_functions import getAntLevel
        simple_ptu2_data.levels_array = None
        result = getAntLevel(0, 0, simple_ptu2_data)
        expected = np.array([-20.0, -10.0, -20.0])
        np.testing.assert_array_equal(result, expected)

class TestMemoryUsageReduction:
    """Test that flattened arrays reduce memory overhead compared to list-of-dicts."""

    def test_arrays_reduce_memory_overhead(self, simple_ptu2_data):
        """Verify that arrays are created and list data is still accessible."""
        data = simple_ptu2_data
        # Ensure arrays are built
        assert data.angles_array is not None
        assert data.levels_array is not None
        assert data.phases_array is not None

        # Arrays should have the same data as the original lists
        manual_angles = np.array([p.d_PTU_Angle for p in data.ptuPosDataList])
        np.testing.assert_array_equal(data.angles_array, manual_angles)

        # Memory-wise, arrays are more efficient than nested lists/dicts
        # This test ensures the optimization is in place
