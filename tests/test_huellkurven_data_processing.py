"""
Tests for shared/huellkurven_data_processing.py

Covers:
- calcPatternLimits (pure math, no I/O)
- calcPhaseLimits (pure math, no I/O)
- LimitsData defaults
- LimitsHeader enum values
- RxAntPatternData initialization and setLimitsList
- RxChPhaseDiffData initialization, setLimitsList, applyToleranceAngRangePhaseDiff
- AngleSetup construction and setStr
- getConfChirpList filter logic
"""
import sys
import os
import pytest

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _subdir in ['shared']:
    _path = os.path.join(_root, _subdir)
    if _path not in sys.path:
        sys.path.insert(0, _path)

from shared.huellkurven_data_processing import (
    calcPatternLimits,
    calcPhaseLimits,
    LimitsData,
    LimitsHeader,
    RxAntPatternData,
    RxChPhaseDiffData,
    AngleSetup,
    getConfChirpList,
)


# ──────────────────────────────────────────────
# calcPatternLimits
# ──────────────────────────────────────────────

class TestCalcPatternLimits:
    def test_method0_returns_correct_limits(self):
        data = [1.0, 2.0, 3.0, 4.0, 5.0]
        min_l, max_l, median, std, mn, mx = calcPatternLimits(data, -3, 3, 0, 2.0)
        assert min_l < median < max_l
        assert mn == pytest.approx(min(data))
        assert mx == pytest.approx(max(data))

    def test_method1_uses_min_max(self):
        data = [1.0, 2.0, 3.0, 4.0, 5.0]
        min_l, max_l, _, _, _, _ = calcPatternLimits(data, -3, 3, 1, 2.0)
        # method=1: minLimit = minimum - std - 7, maxLimit = maximum + std + 3
        assert min_l < min(data)
        assert max_l > max(data)

    def test_single_element_list(self):
        data = [5.0]
        min_l, max_l, median, std, mn, mx = calcPatternLimits(data, -2, 2, 0, 1.0)
        # std=0, so min_l = median - reserve, max_l = median + reserve
        assert median == pytest.approx(5.0)
        assert std == pytest.approx(0.0)

    def test_identical_values(self):
        data = [3.0, 3.0, 3.0]
        min_l, max_l, median, _, _, _ = calcPatternLimits(data, -2, 2, 0, 1.0)
        assert median == pytest.approx(3.0)

    def test_reserve_applied(self):
        data = [0.0, 0.0, 0.0]
        min_l, max_l, _, _, _, _ = calcPatternLimits(data, 0, 0, 0, 2.0)
        assert min_l == pytest.approx(-2.0)
        assert max_l == pytest.approx(2.0)

    def test_returns_six_values(self):
        data = [1.0, 2.0, 3.0]
        result = calcPatternLimits(data, -2, 2, 0, 1.0)
        assert len(result) == 6

    def test_method0_minlimit_lt_maxlimit(self):
        data = [10.0, 20.0, 30.0, 40.0, 50.0]
        min_l, max_l, *_ = calcPatternLimits(data, -2, 2, 0, 1.0)
        assert min_l < max_l

    def test_method1_minlimit_lt_maxlimit(self):
        data = [10.0, 20.0, 30.0]
        min_l, max_l, *_ = calcPatternLimits(data, -2, 2, 1, 1.0)
        assert min_l < max_l


# ──────────────────────────────────────────────
# calcPhaseLimits
# ──────────────────────────────────────────────

class TestCalcPhaseLimits:
    def test_symmetric_factor(self):
        data = [0.0, 0.0, 0.0, 0.0]
        mn, mx, median = calcPhaseLimits(data, 3, 3)
        assert mn == pytest.approx(0.0)
        assert mx == pytest.approx(0.0)
        assert median == pytest.approx(0.0)

    def test_returns_three_values(self):
        data = [10.0, 20.0, 30.0]
        result = calcPhaseLimits(data, 2, 2)
        assert len(result) == 3

    def test_min_less_than_max(self):
        data = [5.0, 10.0, 15.0, 20.0]
        mn, mx, median = calcPhaseLimits(data, 1, 1)
        assert mn < mx

    def test_asymmetric_factors(self):
        data = [0.0, 10.0, 20.0]
        mn, mx, median = calcPhaseLimits(data, 1, 3)
        assert abs(mn - median) < abs(mx - median)

    def test_median_between_min_max(self):
        data = [5.0, 10.0, 15.0]
        mn, mx, median = calcPhaseLimits(data, 2, 2)
        assert mn <= median <= mx


# ──────────────────────────────────────────────
# LimitsData defaults
# ──────────────────────────────────────────────

class TestLimitsData:
    def test_default_init(self):
        ld = LimitsData()
        assert ld.antennaType == 153
        assert ld.nofAntennas == 4
        assert ld.nofDiffPhases == 3
        assert ld.nofChirps == 1
        assert ld.angle == []
        assert ld.rxAntPatternData == []
        assert ld.rxChPhaseDiffData == []
        assert ld.parseError == 0
        assert ld.parseErrorList == []

    def test_instances_independent(self):
        a = LimitsData()
        b = LimitsData()
        a.angle.append(1.0)
        assert b.angle == []

    def test_version_default(self):
        ld = LimitsData()
        assert ld.fileFormatVersion == '1'

    def test_pan_type_default(self):
        ld = LimitsData()
        assert ld.panType == 1


# ──────────────────────────────────────────────
# LimitsHeader enum
# ──────────────────────────────────────────────

class TestLimitsHeader:
    def test_enum_values(self):
        assert LimitsHeader.AntennaType.value == '#AntennaType'
        assert LimitsHeader.NofAntennas.value == '#NofAntennas'
        assert LimitsHeader.NofDiffPhases.value == '#NofDiffPhases'
        assert LimitsHeader.PanType.value == '#PanType'

    def test_nof_chirps_value(self):
        assert LimitsHeader.NofChirps.value == '#NofChirps:'

    def test_all_members_present(self):
        names = {m.name for m in LimitsHeader}
        assert 'AntennaType' in names
        assert 'NofAntennas' in names
        assert 'NofDiffPhases' in names
        assert 'NofChirps' in names
        assert 'PanType' in names


# ──────────────────────────────────────────────
# RxAntPatternData
# ──────────────────────────────────────────────

class TestRxAntPatternData:
    def test_default_init(self):
        rx = RxAntPatternData()
        assert rx.ptuLevelPerRxAntenna == []
        assert rx.minPatternLimits == []
        assert rx.maxPatternLimits == []
        assert rx.medianPatternLimits == []

    def test_setLimitsList_populates_limits(self):
        rx = RxAntPatternData()
        # 3 PTU measurements each with 5 angle points
        rx.ptuLevelPerRxAntenna = [
            [1.0, 2.0, 3.0, 4.0, 5.0],
            [1.5, 2.5, 3.5, 4.5, 5.5],
            [0.5, 1.5, 2.5, 3.5, 4.5],
        ]
        rx.setLimitsList(minSigma=-3, maxSigma=3, patternLimitsMethod=0, reserveDb=2.0)
        assert len(rx.minPatternLimits) == 5
        assert len(rx.maxPatternLimits) == 5
        assert len(rx.medianPatternLimits) == 5
        for i in range(5):
            assert rx.minPatternLimits[i] < rx.maxPatternLimits[i]

    def test_setLimitsList_clears_previous(self):
        rx = RxAntPatternData()
        rx.ptuLevelPerRxAntenna = [[1.0, 2.0], [3.0, 4.0]]
        rx.setLimitsList(-2, 2, 0, 1.0)
        prev_min = rx.minPatternLimits[:]
        rx.setLimitsList(-2, 2, 0, 1.0)
        assert rx.minPatternLimits == prev_min  # idempotent

    def test_median_limits_populated(self):
        rx = RxAntPatternData()
        rx.ptuLevelPerRxAntenna = [[10.0, 20.0], [12.0, 22.0], [8.0, 18.0]]
        rx.setLimitsList(-2, 2, 0, 1.0)
        assert len(rx.medianPatternLimits) == 2


# ──────────────────────────────────────────────
# RxChPhaseDiffData
# ──────────────────────────────────────────────

class TestRxChPhaseDiffData:
    def test_default_init(self):
        rx = RxChPhaseDiffData()
        assert rx.ptuPhaseDiffPerRxCh == []
        assert rx.minPhaseLimits == []
        assert rx.maxPhaseLimits == []
        assert rx.medianPhase == []

    def test_setLimitsList_populates(self):
        rx = RxChPhaseDiffData()
        rx.ptuPhaseDiffPerRxCh = [
            [0.0, 5.0, 10.0],
            [2.0, 7.0, 12.0],
            [-2.0, 3.0, 8.0],
        ]
        rx.setLimitsList(minPhaseFactor=2, maxPhaseFactor=2)
        assert len(rx.minPhaseLimits) == 3
        assert len(rx.maxPhaseLimits) == 3
        assert len(rx.medianPhase) == 3

    def test_applyToleranceAngRangePhaseDiff_large_spread(self):
        """Angles spanning more than 360° should be set to sentinel ±∞ values."""
        rx = RxChPhaseDiffData()
        # Create 5 angle points; upper ones have spread > 360
        rx.maxPhaseLimits = [50.0, 200.0, 400.0, 600.0, 800.0]
        rx.minPhaseLimits = [-50.0, -200.0, -400.0, -600.0, -800.0]
        rx.applyToleranceAngRangePhaseDiff()
        MAX = 10000 * 180 + 180
        # Points where diff > 360 should become sentinel values
        assert any(v == MAX for v in rx.maxPhaseLimits)

    def test_applyToleranceAngRangePhaseDiff_small_spread_unchanged(self):
        """Points with spread ≤ 360° must not be changed to sentinels."""
        rx = RxChPhaseDiffData()
        rx.maxPhaseLimits = [10.0, 10.0, 10.0]
        rx.minPhaseLimits = [-10.0, -10.0, -10.0]
        rx.applyToleranceAngRangePhaseDiff()
        assert rx.maxPhaseLimits == [10.0, 10.0, 10.0]
        assert rx.minPhaseLimits == [-10.0, -10.0, -10.0]


# ──────────────────────────────────────────────
# AngleSetup
# ──────────────────────────────────────────────

class TestAngleSetup:
    def _make_data(self):
        return {
            "antType": 153,
            "diagType": "Az",
            "nofAnglePoints": 181,
            "angleStepSize": 1.0,
            "refAnglePoint": -90.0,
        }

    def test_construction(self):
        setup = AngleSetup(self._make_data())
        assert setup.antennaType == 153
        assert setup.diagType == "Az"
        assert setup.nofAnglePoints == 181
        assert setup.angleStepSize == 1.0
        assert setup.refAnglePoint == -90.0

    def test_setStr(self):
        setup = AngleSetup(self._make_data())
        assert "NofPts=181" in setup.angleSetupStr
        assert "StepSize=1.0" in setup.angleSetupStr
        assert "RefPt=-90.0" in setup.angleSetupStr

    def test_str_format(self):
        setup = AngleSetup(self._make_data())
        assert setup.angleSetupStr == "NofPts=181_StepSize=1.0_RefPt=-90.0"

    def test_elevation_diag_type(self):
        data = self._make_data()
        data["diagType"] = "El"
        setup = AngleSetup(data)
        assert setup.diagType == "El"


# ──────────────────────────────────────────────
# getConfChirpList
# ──────────────────────────────────────────────

class TestGetConfChirpList:
    def test_single_chirp(self):
        cfg = {"chirp0": 1, "chirp1": 0, "chirp2": 0}
        result = getConfChirpList(cfg)
        assert result == [0]

    def test_multiple_chirps(self):
        cfg = {"chirp0": 1, "chirp1": 1, "chirp2": 0, "chirp3": 1}
        result = getConfChirpList(cfg)
        assert 0 in result
        assert 1 in result
        assert 3 in result
        assert 2 not in result

    def test_no_chirps(self):
        cfg = {"chirp0": 0, "chirp1": 0}
        result = getConfChirpList(cfg)
        assert result == []

    def test_all_chirps_active(self):
        cfg = {"chirp0": 1, "chirp1": 1, "chirp2": 1}
        result = getConfChirpList(cfg)
        assert sorted(result) == [0, 1, 2]

    def test_empty_config(self):
        result = getConfChirpList({})
        assert result == []
