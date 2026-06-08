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
- getAntennaTypesList, getPtu2ListPerAntennaType
- getDiagramList, getDesiredDiagramsList
- getTxAntList
- getAvgFreqPerDiagram / getMinFreqPerDiagram / getMaxFreqPerDiagram
- createLimitsData returns None when no data matches
- writeLimitsDataToFile writes correct headers/data
- savePlotImage creates PNG files
"""
import os
import types
import pytest

from calibration_statistics_tool.shared.huellkurven_data_processing import (
    calcPatternLimits,
    calcPhaseLimits,
    LimitsData,
    LimitsHeader,
    RxAntPatternData,
    RxChPhaseDiffData,
    AngleSetup,
    getConfChirpList,
    getAntennaTypesList,
    getPtu2ListPerAntennaType,
    getDiagramList,
    getDesiredDiagramsList,
    getTxAntList,
    getAvgFreqPerDiagram,
    getMinFreqPerDiagram,
    getMaxFreqPerDiagram,
    writeLimitsDataToFile,
    createLimitsData,
    savePlotImage,
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


# ──────────────────────────────────────────────
# Shared mock factory for parse data objects
# ──────────────────────────────────────────────

def _ns(**kwargs):
    """Create a SimpleNamespace (used for building mock parse-data objects)."""
    return types.SimpleNamespace(**kwargs)


def _make_parse_data(
    antenna_type=1,
    diagram=0,
    tx_ant=0,
    chirp_active=1.0,
    freq=24e9,
    diag_type='Az',
    has_diag_type=True,
    upside_down_found=1,
):
    """Return a minimal mock parse-data object matching the real ParseData API."""
    return _ns(
        antennaInfo=_ns(antennaType=antenna_type),
        fileTitle=_ns(
            diagram=diagram,
            diagramFound=1,
            txAnt=tx_ant,
            txAntFound=1,
            sensorFound=1,
            dateAndTimeFound=1,
            dateAndTime='2024-01-01',
            sensor='sensor1',
        ),
        chirpInfoList={
            0: _ns(active=chirp_active, centerFrequency=freq),
        },
        measSetupInfo=_ns(
            antennaDiagramTypeFound=1 if has_diag_type else 0,
            antennaDiagramType=diag_type,
            sensorUpsideDown=0,
            sensorUpsideDownFound=upside_down_found,
        ),
    )


# ──────────────────────────────────────────────
# getAntennaTypesList
# ──────────────────────────────────────────────

class TestGetAntennaTypesList:
    def test_single_type(self):
        parse_list = [_make_parse_data(antenna_type=1)] * 3
        result = getAntennaTypesList(parse_list)
        assert result == [1]

    def test_multiple_types(self):
        parse_list = [
            _make_parse_data(antenna_type=1),
            _make_parse_data(antenna_type=2),
            _make_parse_data(antenna_type=1),
        ]
        result = getAntennaTypesList(parse_list)
        assert set(result) == {1, 2}

    def test_empty_list(self):
        result = getAntennaTypesList([])
        assert result == []


# ──────────────────────────────────────────────
# getPtu2ListPerAntennaType
# ──────────────────────────────────────────────

class TestGetPtu2ListPerAntennaType:
    def test_filters_by_type(self):
        parse_list = [
            _make_parse_data(antenna_type=1),
            _make_parse_data(antenna_type=2),
            _make_parse_data(antenna_type=1),
        ]
        result = getPtu2ListPerAntennaType(1, parse_list)
        assert len(result) == 2
        assert all(p.antennaInfo.antennaType == 1 for p in result)

    def test_no_match_returns_empty(self):
        parse_list = [_make_parse_data(antenna_type=2)]
        result = getPtu2ListPerAntennaType(99, parse_list)
        assert result == []

    def test_all_match(self):
        parse_list = [_make_parse_data(antenna_type=5)] * 4
        result = getPtu2ListPerAntennaType(5, parse_list)
        assert len(result) == 4


# ──────────────────────────────────────────────
# getDiagramList
# ──────────────────────────────────────────────

class TestGetDiagramList:
    def test_returns_sorted_unique_diagrams(self):
        parse_list = [
            _make_parse_data(antenna_type=1, diagram=4, tx_ant=0),
            _make_parse_data(antenna_type=1, diagram=0, tx_ant=0),
            _make_parse_data(antenna_type=1, diagram=2, tx_ant=1),
            _make_parse_data(antenna_type=1, diagram=0, tx_ant=0),  # duplicate
        ]
        result = getDiagramList(1, parse_list)
        diagram_nums = [d['diagramNum'] for d in result]
        assert diagram_nums == sorted(set(diagram_nums))
        assert len(result) == 3

    def test_anttype_filter(self):
        parse_list = [
            _make_parse_data(antenna_type=1, diagram=0),
            _make_parse_data(antenna_type=2, diagram=1),
        ]
        result = getDiagramList(2, parse_list)
        assert len(result) == 1
        assert result[0]['diagramNum'] == 1

    def test_empty_when_no_match(self):
        parse_list = [_make_parse_data(antenna_type=1, diagram=0)]
        result = getDiagramList(99, parse_list)
        assert result == []


# ──────────────────────────────────────────────
# getDesiredDiagramsList
# ──────────────────────────────────────────────

def _diag_config(select=0, odd_even=0, low=0, high=99):
    return {'selectDiagrams': select, 'oddOrEven': odd_even,
            'lowerNumber': low, 'higherNumber': high}


def _parse_list_for_diagrams(diagrams, ant_type=1):
    return [_make_parse_data(antenna_type=ant_type, diagram=d, tx_ant=i)
            for i, d in enumerate(diagrams)]


class TestGetDesiredDiagramsList:
    def test_select_all(self):
        parse_list = _parse_list_for_diagrams([0, 2, 4])
        result = getDesiredDiagramsList(_diag_config(select=0, odd_even=0), [], 1, parse_list)
        nums = [d['diagramNum'] for d in result]
        assert sorted(nums) == [0, 2, 4]

    def test_select_odd(self):
        parse_list = _parse_list_for_diagrams([1, 2, 3, 4, 5])
        result = getDesiredDiagramsList(_diag_config(select=0, odd_even=1), [], 1, parse_list)
        nums = [d['diagramNum'] for d in result]
        assert all(n % 2 != 0 for n in nums)
        assert set(nums) == {1, 3, 5}

    def test_select_even(self):
        parse_list = _parse_list_for_diagrams([1, 2, 3, 4, 5])
        result = getDesiredDiagramsList(_diag_config(select=0, odd_even=2), [], 1, parse_list)
        nums = [d['diagramNum'] for d in result]
        assert all(n % 2 == 0 for n in nums)
        assert set(nums) == {2, 4}

    def test_select_range(self):
        parse_list = _parse_list_for_diagrams([0, 1, 2, 3, 4, 5])
        result = getDesiredDiagramsList(_diag_config(select=1, odd_even=0, low=2, high=4), [], 1, parse_list)
        nums = [d['diagramNum'] for d in result]
        assert set(nums) == {2, 3, 4}

    def test_select_explicit_list(self):
        parse_list = _parse_list_for_diagrams([0, 1, 2, 3, 4])
        result = getDesiredDiagramsList(_diag_config(select=2), [1, 3], 1, parse_list)
        nums = [d['diagramNum'] for d in result]
        assert set(nums) == {1, 3}


# ──────────────────────────────────────────────
# getTxAntList
# ──────────────────────────────────────────────

class TestGetTxAntList:
    def test_returns_sorted_unique(self):
        parse_list = [
            _make_parse_data(tx_ant=2),
            _make_parse_data(tx_ant=0),
            _make_parse_data(tx_ant=1),
            _make_parse_data(tx_ant=0),  # duplicate
        ]
        result = getTxAntList(parse_list)
        assert sorted(result) == sorted(set(result))
        assert set(result) == {0, 1, 2}

    def test_txant_not_found_excluded(self):
        pd = _make_parse_data(tx_ant=5)
        pd.fileTitle.txAntFound = 0  # override to not-found
        result = getTxAntList([pd])
        assert result == []


# ──────────────────────────────────────────────
# getAvgFreqPerDiagram / getMin / getMax
# ──────────────────────────────────────────────

class TestFreqFunctions:
    def _make_freq_list(self):
        # 3 files for diagram=0, chirp=0, with frequencies 1, 2, 3 GHz
        return [
            _make_parse_data(diagram=0, freq=1e9),
            _make_parse_data(diagram=0, freq=2e9),
            _make_parse_data(diagram=0, freq=3e9),
        ]

    def test_avg_freq(self):
        parse_list = self._make_freq_list()
        avg = getAvgFreqPerDiagram(0, 0, parse_list)
        assert avg == pytest.approx(2e9)

    def test_min_freq(self):
        parse_list = self._make_freq_list()
        mn = getMinFreqPerDiagram(0, 0, parse_list)
        assert mn == pytest.approx(1e9)

    def test_max_freq(self):
        parse_list = self._make_freq_list()
        mx = getMaxFreqPerDiagram(0, 0, parse_list)
        assert mx == pytest.approx(3e9)

    def test_no_match_returns_zero(self):
        parse_list = [_make_parse_data(diagram=5, freq=9e9)]
        # chirp=0 active, but diagram=5 != diagram 0 requested
        avg = getAvgFreqPerDiagram(0, 99, parse_list)  # diagram 99 absent
        assert avg == 0


# ──────────────────────────────────────────────
# createLimitsData — returns None when no match
# ──────────────────────────────────────────────

class TestCreateLimitsDataNoMatch:
    def _angle_setup(self):
        return AngleSetup({
            'antType': 1, 'diagType': 'Az',
            'nofAnglePoints': 5, 'angleStepSize': 1.0, 'refAnglePoint': -2.0,
        })

    def _data_conf(self):
        return {
            'minSigma': -3, 'maxSigma': 3,
            'patternLimitsMethod': 0, 'reserveDb': 2.0,
            'minPhaseFactor': 2, 'maxPhaseFactor': 2,
        }

    def _input_config(self):
        return {
            'diagTypeInfo': 1, 'targetAngle': 0, 'upsideDown': 0,
            'upsideDownInfo': 1, 'useSensorMuster': 0, 'sensorMusterList': [],
        }

    def test_returns_none_when_diagram_not_in_list(self):
        # parse data has diagram=5 but desired diagram is 0 → no match
        pd = _make_parse_data(antenna_type=1, diagram=5)
        desired = [{'diagramNum': 0, 'txAnt': 0}]
        cent_freq = [{'avgFreqMHz': '24000.00', 'chirp': 0, 'diagNum': 0}]
        result = createLimitsData(
            version=1,
            commentsDict={'version': ''},
            desiredDiagramList=desired,
            diagListIdx=0,
            chirp=0,
            antennaType=1,
            parseDataList=[pd],
            angleSetup=self._angle_setup(),
            centFreqDictList=cent_freq,
            diagType='Az',
            inputConfig=self._input_config(),
            chirpConfig={'chirp0': 1},
            dataConf=self._data_conf(),
            write_output=False,
        )
        assert result is None

    def test_returns_none_when_chirp_inactive(self):
        # parse data has diagram=0 but chirp is inactive → no match
        pd = _make_parse_data(antenna_type=1, diagram=0, chirp_active=0.0)
        desired = [{'diagramNum': 0, 'txAnt': 0}]
        cent_freq = [{'avgFreqMHz': '24000.00', 'chirp': 0, 'diagNum': 0}]
        result = createLimitsData(
            version=1,
            commentsDict={'version': ''},
            desiredDiagramList=desired,
            diagListIdx=0,
            chirp=0,
            antennaType=1,
            parseDataList=[pd],
            angleSetup=self._angle_setup(),
            centFreqDictList=cent_freq,
            diagType='Az',
            inputConfig=self._input_config(),
            chirpConfig={'chirp0': 1},
            dataConf=self._data_conf(),
            write_output=False,
        )
        assert result is None


# ──────────────────────────────────────────────
# writeLimitsDataToFile
# ──────────────────────────────────────────────

class TestWriteLimitsDataToFile:
    def _make_limits_data(self):
        ld = LimitsData()
        ld.version = '1'
        ld.commentsDict = {'version': ' // test comment'}
        ld.antennaType = 1
        ld.nofAntennas = 2
        ld.nofDiffPhases = 1
        ld.nofChirps = 1
        ld.usedChirpBitCoded = 1
        ld.panType = 0
        ld.activeTx = 0
        ld.txFrequency = '24000.00'
        ld.diagTypeInfo = 1
        ld.upsideDownInfo = 1
        ld.outputPath = ''
        ld.title = 'test_output.dat'
        ld.angle = [0.0, 1.0, 2.0]

        rx1 = RxAntPatternData()
        rx1.minPatternLimits = [-1.0, -1.0, -1.0]
        rx1.maxPatternLimits = [1.0, 1.0, 1.0]
        rx2 = RxAntPatternData()
        rx2.minPatternLimits = [-2.0, -2.0, -2.0]
        rx2.maxPatternLimits = [2.0, 2.0, 2.0]
        ld.rxAntPatternData = [rx1, rx2]

        phase = RxChPhaseDiffData()
        phase.minPhaseLimits = [-10.0, -10.0, -10.0]
        phase.maxPhaseLimits = [10.0, 10.0, 10.0]
        ld.rxChPhaseDiffData = [phase]
        return ld

    def test_creates_file(self, tmp_path, monkeypatch):
        import calibration_statistics_tool.shared.huellkurven_data_processing as hdp
        monkeypatch.setattr(hdp.aux, 'huellKurvenOutputPath', str(tmp_path))
        writeLimitsDataToFile(self._make_limits_data())
        assert (tmp_path / 'test_output.dat').exists()

    def test_headers_in_output(self, tmp_path, monkeypatch):
        import calibration_statistics_tool.shared.huellkurven_data_processing as hdp
        monkeypatch.setattr(hdp.aux, 'huellKurvenOutputPath', str(tmp_path))
        writeLimitsDataToFile(self._make_limits_data())
        content = (tmp_path / 'test_output.dat').read_text()
        assert '#AntennaType: 1' in content
        assert '#NofAntennas: 2' in content
        assert '#NofDiffPhases: 1' in content
        assert '#PanType: 0' in content

    def test_angle_rows_count(self, tmp_path, monkeypatch):
        import calibration_statistics_tool.shared.huellkurven_data_processing as hdp
        monkeypatch.setattr(hdp.aux, 'huellKurvenOutputPath', str(tmp_path))
        writeLimitsDataToFile(self._make_limits_data())
        content = (tmp_path / 'test_output.dat').read_text()
        data_lines = [l for l in content.splitlines() if l and not l.startswith('#')]
        assert len(data_lines) == 3  # one row per angle point


# ──────────────────────────────────────────────
# savePlotImage
# ──────────────────────────────────────────────

class TestSavePlotImage:
    def _make_limits_data_for_plot(self, n_angles=11):
        ld = LimitsData()
        ld.antennaType = 1
        ld.activeTx = 0
        ld.panType = 0          # Az
        ld.usedChirpBitCoded = 1
        ld.outputPath = ''
        ld.title = 'Az_TxAnt0_Diagram0_Chirp0.dat'
        ld.angle = list(range(-5, -5 + n_angles))

        rx = RxAntPatternData()
        rx.ptuLevelPerRxAntenna = [list(range(n_angles)), list(range(n_angles))]
        rx.minPatternLimits = [float(x - 1) for x in range(n_angles)]
        rx.maxPatternLimits = [float(x + 1) for x in range(n_angles)]
        rx.medianPatternLimits = [float(x) for x in range(n_angles)]
        ld.rxAntPatternData = [rx]

        ph = RxChPhaseDiffData()
        ph.ptuPhaseDiffPerRxCh = [list(range(n_angles))]
        ph.minPhaseLimits = [float(x - 5) for x in range(n_angles)]
        ph.maxPhaseLimits = [float(x + 5) for x in range(n_angles)]
        ph.medianPhase = [float(x) for x in range(n_angles)]
        ld.rxChPhaseDiffData = [ph]
        return ld

    def test_creates_pattern_png(self, tmp_path):
        ld = self._make_limits_data_for_plot()
        savePlotImage(ld, str(tmp_path))
        expected = tmp_path / 'Az_TxAnt0_Diagram0_Chirp0_RxCh0_Pattern.png'
        assert expected.exists()

    def test_creates_phasediff_png(self, tmp_path):
        ld = self._make_limits_data_for_plot()
        savePlotImage(ld, str(tmp_path))
        expected = tmp_path / 'Az_TxAnt0_Diagram0_Chirp0_RxCh0_PhaseDiff.png'
        assert expected.exists()

    def test_elevation_pantype(self, tmp_path):
        ld = self._make_limits_data_for_plot()
        ld.panType = 1   # El
        ld.title = 'El_TxAnt0_Diagram1_Chirp0.dat'
        savePlotImage(ld, str(tmp_path))
        expected = tmp_path / 'El_TxAnt0_Diagram1_Chirp0_RxCh0_Pattern.png'
        assert expected.exists()

    def test_no_phasediff_channels_skips_phase_plot(self, tmp_path):
        ld = self._make_limits_data_for_plot()
        ld.rxChPhaseDiffData = []
        savePlotImage(ld, str(tmp_path))
        phase_files = list(tmp_path.glob('*PhaseDiff.png'))
        assert phase_files == []

