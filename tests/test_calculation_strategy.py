import sys
import os
import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from calibration_statistics_tool.shared import calculation_strategy
from calibration_statistics_tool.shared.calculation_strategy import (
    CalculationContext,
    AntLevelStrategy,
    AvgAntLevelStrategy,
    NormAntLevelStrategy,
    AvgNormAntLevelStrategy,
    PhaseDiffStrategy,
    AvgPhaseDiffStrategy,
    IdealPhaseDiffStrategy,
    PhaseDiffDiffStrategy,
    AvgPhaseDiffDiffStrategy,
    CorrPhaseDiffStrategy,
    STRATEGY_REGISTRY,
)


class DummyPTU2ParseData:
    MAX_CHIRP = 2

    def __init__(self):
        def make_chirp_data():
            return type('obj', (object,), {
                'antennaLevelDataList': [
                    type('obj', (object,), {'dLevel': -20.0})(),
                    type('obj', (object,), {'dLevel': -25.0})(),
                ],
                'diffPhaseDataList': [
                    type('obj', (object,), {'dDiffPhase': 10.0})(),
                ],
            })()

        self.chirpInfoList = [
            type('obj', (object,), {
                'active': 1,
                'centerFrequency': 1e9,
                'diffPhaseOffsetList': [0],
            })()
            for _ in range(self.MAX_CHIRP)
        ]
        self.ptuPosDataList = [
            type('obj', (object,), {
                'd_PTU_Angle': angle,
                'chirpMeasDataList': [make_chirp_data() for _ in range(self.MAX_CHIRP)],
            })()
            for angle in [-10.0, 0.0, 10.0]
        ]
        self.antennaInfo = type('obj', (object,), {'antennaDistancesList': [0.1]})()
        self.angles_array = None
        self.levels_array = None
        self.phases_array = None


ALL_GRAPH_TYPES = list(STRATEGY_REGISTRY.keys())


class TestEachStrategyViaRegistry:
    def test_all_graph_types_return_ndarray(self):
        data = DummyPTU2ParseData()
        for graph_type in ALL_GRAPH_TYPES:
            strategy = STRATEGY_REGISTRY[graph_type]
            context = CalculationContext(strategy)
            result = context.execute(0, 0, data)
            assert isinstance(result, np.ndarray), f"{graph_type} should return ndarray"
            assert result.shape[0] == 3, f"{graph_type} result should have 3 angle points"

    def test_unknown_graph_type_not_in_registry(self):
        assert STRATEGY_REGISTRY.get('unknownGraph') is None


class TestSwitchStrategy:
    def test_context_can_switch_strategy_at_runtime(self):
        data = DummyPTU2ParseData()
        context = CalculationContext(AntLevelStrategy())
        result_level = context.execute(0, 0, data)
        context.set_strategy(NormAntLevelStrategy())
        result_norm = context.execute(0, 0, data)
        assert isinstance(result_level, np.ndarray)
        assert isinstance(result_norm, np.ndarray)
        # Normalized level subtracts the max, so peak becomes 0 — always differs from raw level
        assert not np.allclose(result_level, result_norm)


class TestRegistryCoverage:
    def test_registry_contains_all_expected_types(self):
        expected = {
            'level', 'avgLevel', 'normLevel', 'avgNormLevel',
            'phaseDiff', 'avgPhaseDiff', 'idealPhaseDiff',
            'diffPhaseDiff', 'avgDiffPhaseDiff', 'corrPhaseDiff',
        }
        assert expected == set(STRATEGY_REGISTRY.keys())

