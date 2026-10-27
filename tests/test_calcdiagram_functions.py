"""
Tests for shared/calcdiagram_functions.py

Covers all public functions with known inputs and expected outputs.
Uses fixtures from conftest.py for realistic PTU2ParseData structures.

These tests serve as the regression baseline before Phase 2 vectorization.
Any optimisation must produce bit-identical results for all tests here.
"""
import sys
import os
import pytest
import numpy as np

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _subdir in ['shared']:
    _path = os.path.join(_root, _subdir)
    if _path not in sys.path:
        sys.path.insert(0, _path)

from calibration_statistics_tool.shared import calcdiagram_functions as calc

# Reuse parsePTU2data data classes for manual fixture building if needed
from calibration_statistics_tool.shared.parsePTU2data import PTU2ParseData, AntennaInfo, ChirpInfo

ANGLES = [-10.0, 0.0, 10.0]


# ──────────────────────────────────────────────
# getNofAngVals
# ──────────────────────────────────────────────

class TestGetNofAngVals:
    def test_returns_correct_count(self, simple_ptu2_data):
        assert calc.getNofAngVals(simple_ptu2_data) == 3

    def test_empty_data_returns_zero(self):
        data = PTU2ParseData()
        assert calc.getNofAngVals(data) == 0


# ──────────────────────────────────────────────
# getPtuAngVals
# ──────────────────────────────────────────────

class TestGetPtuAngVals:
    def test_returns_numpy_array(self, simple_ptu2_data):
        result = calc.getPtuAngVals(simple_ptu2_data)
        assert isinstance(result, np.ndarray)

    def test_correct_angles(self, simple_ptu2_data):
        result = calc.getPtuAngVals(simple_ptu2_data)
        np.testing.assert_array_equal(result, np.array([-10.0, 0.0, 10.0]))

    def test_length_matches_nof_ang_vals(self, simple_ptu2_data):
        result = calc.getPtuAngVals(simple_ptu2_data)
        assert len(result) == calc.getNofAngVals(simple_ptu2_data)


# ──────────────────────────────────────────────
# getTarAngVals
# ──────────────────────────────────────────────

class TestGetTarAngVals:
    def test_not_upside_down_inverts_angles(self, simple_ptu2_data):
        result = calc.getTarAngVals(simple_ptu2_data, upsideDown=0)
        np.testing.assert_array_equal(result, np.array([10.0, 0.0, -10.0]))

    def test_upside_down_keeps_ptu_angles(self, simple_ptu2_data):
        result = calc.getTarAngVals(simple_ptu2_data, upsideDown=1)
        np.testing.assert_array_equal(result, np.array([-10.0, 0.0, 10.0]))


# ──────────────────────────────────────────────
# getAntLevel
# ──────────────────────────────────────────────

class TestGetAntLevel:
    def test_returns_numpy_array(self, simple_ptu2_data):
        result = calc.getAntLevel(rxAnt=0, chirp=0, ptu2ParseData=simple_ptu2_data)
        assert isinstance(result, np.ndarray)

    def test_correct_levels_ant0_chirp0(self, simple_ptu2_data):
        # From fixture: ant0 chirp0 → [-20, -10, -20] for the 3 angles
        result = calc.getAntLevel(rxAnt=0, chirp=0, ptu2ParseData=simple_ptu2_data)
        np.testing.assert_array_equal(result, np.array([-20.0, -10.0, -20.0]))

    def test_correct_levels_ant1_chirp0(self, simple_ptu2_data):
        # From fixture: ant1 chirp0 → [-25, -15, -25] for the 3 angles
        result = calc.getAntLevel(rxAnt=1, chirp=0, ptu2ParseData=simple_ptu2_data)
        np.testing.assert_array_equal(result, np.array([-25.0, -15.0, -25.0]))

    def test_correct_levels_ant0_chirp1(self, simple_ptu2_data):
        # From fixture: ant0 chirp1 → [-21, -11, -21] for the 3 angles
        result = calc.getAntLevel(rxAnt=0, chirp=1, ptu2ParseData=simple_ptu2_data)
        np.testing.assert_array_equal(result, np.array([-21.0, -11.0, -21.0]))


# ──────────────────────────────────────────────
# getNormAntLevel
# ──────────────────────────────────────────────

class TestGetNormAntLevel:
    def test_max_is_zero_db(self, simple_ptu2_data):
        result = calc.getNormAntLevel(rxAnt=0, chirp=0, ptu2ParseData=simple_ptu2_data)
        assert np.max(result) == pytest.approx(0.0)

    def test_returns_numpy_array(self, simple_ptu2_data):
        result = calc.getNormAntLevel(rxAnt=0, chirp=0, ptu2ParseData=simple_ptu2_data)
        assert isinstance(result, np.ndarray)

    def test_relative_values_preserved(self, simple_ptu2_data):
        # ant0 chirp0 raw: [-20, -10, -20], max=-10 → norm: [-10, 0, -10]
        result = calc.getNormAntLevel(rxAnt=0, chirp=0, ptu2ParseData=simple_ptu2_data)
        np.testing.assert_array_almost_equal(result, np.array([-10.0, 0.0, -10.0]))


# ──────────────────────────────────────────────
# getAvgAntLevel
# ──────────────────────────────────────────────

class TestGetAvgAntLevel:
    def test_returns_numpy_array(self, simple_ptu2_data):
        result = calc.getAvgAntLevel(rxAnt=0, ptu2ParseData=simple_ptu2_data)
        assert isinstance(result, np.ndarray)

    def test_length_equals_nof_angles(self, simple_ptu2_data):
        result = calc.getAvgAntLevel(rxAnt=0, ptu2ParseData=simple_ptu2_data)
        assert len(result) == 3

    def test_single_active_chirp_matches_that_chirp(self, single_active_chirp_ptu2_data):
        """With only chirp 0 active, the average equals chirp 0's level."""
        avg = calc.getAvgAntLevel(rxAnt=0, ptu2ParseData=single_active_chirp_ptu2_data)
        chirp0 = calc.getAntLevel(rxAnt=0, chirp=0, ptu2ParseData=single_active_chirp_ptu2_data)
        np.testing.assert_array_almost_equal(avg, chirp0)

    def test_two_equal_active_chirps_average_equals_either(self, simple_ptu2_data):
        """
        When two chirps have similar (but not identical) values, the average
        should be between them and close to each individually.
        chirp0 ant0: [-20,-10,-20], chirp1 ant0: [-21,-11,-21]
        Linear avg in watts then back to dB should be close to ~-20.5 dB at edges.
        """
        avg = calc.getAvgAntLevel(rxAnt=0, ptu2ParseData=simple_ptu2_data)
        chirp0 = calc.getAntLevel(rxAnt=0, chirp=0, ptu2ParseData=simple_ptu2_data)
        chirp1 = calc.getAntLevel(rxAnt=0, chirp=1, ptu2ParseData=simple_ptu2_data)
        # Average should lie between the two
        assert np.all(avg <= np.maximum(chirp0, chirp1) + 0.01)
        assert np.all(avg >= np.minimum(chirp0, chirp1) - 0.01)

    def test_result_in_db_range(self, simple_ptu2_data):
        """Result should be a reasonable dB value (not nan/inf)."""
        result = calc.getAvgAntLevel(rxAnt=0, ptu2ParseData=simple_ptu2_data)
        assert np.all(np.isfinite(result))


# ──────────────────────────────────────────────
# getPhaseDiff
# ──────────────────────────────────────────────

class TestGetPhaseDiff:
    def test_returns_numpy_array(self, simple_ptu2_data):
        result = calc.getPhaseDiff(phaseDiffIdx=0, chirp=0, ptu2ParseData=simple_ptu2_data)
        assert isinstance(result, np.ndarray)

    def test_correct_values_chirp0(self, simple_ptu2_data):
        # From fixture: chirp0 phase → [5.0, 0.0, -5.0] for the 3 angles
        result = calc.getPhaseDiff(phaseDiffIdx=0, chirp=0, ptu2ParseData=simple_ptu2_data)
        np.testing.assert_array_equal(result, np.array([5.0, 0.0, -5.0]))

    def test_correct_values_chirp1(self, simple_ptu2_data):
        # From fixture: chirp1 phase → [6.0, 0.0, -6.0] for the 3 angles
        result = calc.getPhaseDiff(phaseDiffIdx=0, chirp=1, ptu2ParseData=simple_ptu2_data)
        np.testing.assert_array_equal(result, np.array([6.0, 0.0, -6.0]))


# ──────────────────────────────────────────────
# getPhaseDiffOffCorr  (offset correction)
# ──────────────────────────────────────────────

class TestGetPhaseDiffOffCorr:
    def test_zero_offset_equals_raw_phase(self, simple_ptu2_data):
        """Fixture uses zero phase offsets - corrected should equal raw."""
        raw    = calc.getPhaseDiff(phaseDiffIdx=0, chirp=0, ptu2ParseData=simple_ptu2_data)
        corrected = calc.getPhaseDiffOffCorr(phaseDiffIdx=0, chirp=0, ptu2ParseData=simple_ptu2_data)
        np.testing.assert_array_almost_equal(raw, corrected)

    def test_nonzero_offset_shifts_values(self, simple_ptu2_data):
        """Manually set a phase offset and verify the correction is applied."""
        simple_ptu2_data.chirpInfoList[0].diffPhaseOffsetList[0] = 10.0
        raw       = calc.getPhaseDiff(phaseDiffIdx=0, chirp=0, ptu2ParseData=simple_ptu2_data)
        corrected = calc.getPhaseDiffOffCorr(phaseDiffIdx=0, chirp=0, ptu2ParseData=simple_ptu2_data)
        # corrected = raw + offset (before range wrapping)
        # At 0° angle: raw=0, offset=10 → corrected=10
        assert corrected[1] == pytest.approx(10.0)


# ──────────────────────────────────────────────
# getAvgPhaseDiff
# ──────────────────────────────────────────────

class TestGetAvgPhaseDiff:
    def test_returns_numpy_array(self, simple_ptu2_data):
        result = calc.getAvgPhaseDiff(phaseDiffIdx=0, ptu2ParseData=simple_ptu2_data)
        assert isinstance(result, np.ndarray)

    def test_length_equals_nof_angles(self, simple_ptu2_data):
        result = calc.getAvgPhaseDiff(phaseDiffIdx=0, ptu2ParseData=simple_ptu2_data)
        assert len(result) == 3

    def test_single_active_chirp_matches_that_chirp(self, single_active_chirp_ptu2_data):
        avg    = calc.getAvgPhaseDiff(phaseDiffIdx=0, ptu2ParseData=single_active_chirp_ptu2_data)
        chirp0 = calc.getPhaseDiffOffCorr(phaseDiffIdx=0, chirp=0, ptu2ParseData=single_active_chirp_ptu2_data)
        np.testing.assert_array_almost_equal(avg, chirp0)

    def test_finite_values(self, simple_ptu2_data):
        result = calc.getAvgPhaseDiff(phaseDiffIdx=0, ptu2ParseData=simple_ptu2_data)
        assert np.all(np.isfinite(result))


# ──────────────────────────────────────────────
# getPhaseInRange  [-180, 180] wrapping
# ──────────────────────────────────────────────

class TestGetPhaseInRange:
    def test_values_within_range_unchanged(self):
        arr = np.array([-180.0, -90.0, 0.0, 90.0, 180.0])
        result = calc.getPhaseInRange(arr.copy())
        np.testing.assert_array_equal(result, arr)

    def test_values_above_180_wrapped_down(self):
        arr = np.array([181.0, 270.0, 360.0])
        result = calc.getPhaseInRange(arr.copy())
        assert result[0] == pytest.approx(-179.0)
        assert result[1] == pytest.approx(-90.0)
        assert result[2] == pytest.approx(0.0)

    def test_values_below_minus_180_wrapped_up(self):
        arr = np.array([-181.0, -270.0, -360.0])
        result = calc.getPhaseInRange(arr.copy())
        assert result[0] == pytest.approx(179.0)
        assert result[1] == pytest.approx(90.0)
        assert result[2] == pytest.approx(0.0)

    def test_zero_unchanged(self):
        arr = np.array([0.0])
        result = calc.getPhaseInRange(arr.copy())
        assert result[0] == pytest.approx(0.0)

    def test_exactly_180_unchanged(self):
        arr = np.array([180.0])
        result = calc.getPhaseInRange(arr.copy())
        assert result[0] == pytest.approx(180.0)

    def test_exactly_minus_180_unchanged(self):
        arr = np.array([-180.0])
        result = calc.getPhaseInRange(arr.copy())
        assert result[0] == pytest.approx(-180.0)


# ──────────────────────────────────────────────
# getIdealPhaseDiff  (physics formula check)
# ──────────────────────────────────────────────

class TestGetIdealPhaseDiff:
    def test_returns_numpy_array(self, simple_ptu2_data):
        result = calc.getIdealPhaseDiff(phaseDiffIdx=0, chirp=0, ptu2ParseData=simple_ptu2_data)
        assert isinstance(result, np.ndarray)

    def test_zero_angle_gives_zero_phase(self, simple_ptu2_data):
        """At 0° PTU angle the ideal phase difference should be 0."""
        result = calc.getIdealPhaseDiff(phaseDiffIdx=0, chirp=0, ptu2ParseData=simple_ptu2_data)
        # Angle 0° is at index 1 in our fixture
        assert result[1] == pytest.approx(0.0, abs=1e-6)

    def test_symmetric_around_zero(self, simple_ptu2_data):
        """Ideal phase diff should be antisymmetric: value at +θ == -value at -θ."""
        result = calc.getIdealPhaseDiff(phaseDiffIdx=0, chirp=0, ptu2ParseData=simple_ptu2_data)
        # index 0 = -10°, index 2 = +10°  (target angles are inverted PTU angles)
        assert result[0] == pytest.approx(-result[2], abs=1e-6)

    def test_result_within_phase_range(self, simple_ptu2_data):
        """Ideal phase diff should always be within [-180, 180]."""
        result = calc.getIdealPhaseDiff(phaseDiffIdx=0, chirp=0, ptu2ParseData=simple_ptu2_data)
        assert np.all(result >= -180.0)
        assert np.all(result <= 180.0)

    def test_finite_values(self, simple_ptu2_data):
        result = calc.getIdealPhaseDiff(phaseDiffIdx=0, chirp=0, ptu2ParseData=simple_ptu2_data)
        assert np.all(np.isfinite(result))
