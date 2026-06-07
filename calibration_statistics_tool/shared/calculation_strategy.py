import numpy as np
from abc import ABC, abstractmethod
from calibration_statistics_tool.shared import calcdiagram_functions as calc


class CalculationStrategy(ABC):
    @abstractmethod
    def calculate(self, channelOrIdx: int, chirp: int, data) -> np.ndarray:
        pass


class AntLevelStrategy(CalculationStrategy):
    def calculate(self, channelOrIdx: int, chirp: int, data) -> np.ndarray:
        return calc.getAntLevel(channelOrIdx, chirp, data)


class AvgAntLevelStrategy(CalculationStrategy):
    def calculate(self, channelOrIdx: int, chirp: int, data) -> np.ndarray:
        return calc.getAvgAntLevel(channelOrIdx, data)


class NormAntLevelStrategy(CalculationStrategy):
    def calculate(self, channelOrIdx: int, chirp: int, data) -> np.ndarray:
        return calc.getNormAntLevel(channelOrIdx, chirp, data)


class AvgNormAntLevelStrategy(CalculationStrategy):
    def calculate(self, channelOrIdx: int, chirp: int, data) -> np.ndarray:
        return calc.getAvgNormAntLevel(channelOrIdx, data)


class PhaseDiffStrategy(CalculationStrategy):
    def calculate(self, channelOrIdx: int, chirp: int, data) -> np.ndarray:
        return calc.getPhaseDiff(channelOrIdx, chirp, data)


class AvgPhaseDiffStrategy(CalculationStrategy):
    def calculate(self, channelOrIdx: int, chirp: int, data) -> np.ndarray:
        return calc.getAvgPhaseDiff(channelOrIdx, data)


class IdealPhaseDiffStrategy(CalculationStrategy):
    def calculate(self, channelOrIdx: int, chirp: int, data) -> np.ndarray:
        return calc.getIdealPhaseDiff(channelOrIdx, chirp, data)


class PhaseDiffDiffStrategy(CalculationStrategy):
    def calculate(self, channelOrIdx: int, chirp: int, data) -> np.ndarray:
        return calc.getPhaseDiffDiff(channelOrIdx, chirp, data)


class AvgPhaseDiffDiffStrategy(CalculationStrategy):
    def calculate(self, channelOrIdx: int, chirp: int, data) -> np.ndarray:
        return calc.getAvgPhaseDiffDiff(channelOrIdx, data)


class CorrPhaseDiffStrategy(CalculationStrategy):
    def calculate(self, channelOrIdx: int, chirp: int, data) -> np.ndarray:
        return calc.getPhaseDiffOffCorr(channelOrIdx, chirp, data)


class CalculationContext:
    def __init__(self, strategy: CalculationStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: CalculationStrategy):
        self._strategy = strategy

    def execute(self, channelOrIdx: int, chirp: int, data) -> np.ndarray:
        return self._strategy.calculate(channelOrIdx, chirp, data)


STRATEGY_REGISTRY: dict[str, CalculationStrategy] = {
    "level":           AntLevelStrategy(),
    "avgLevel":        AvgAntLevelStrategy(),
    "normLevel":       NormAntLevelStrategy(),
    "avgNormLevel":    AvgNormAntLevelStrategy(),
    "phaseDiff":       PhaseDiffStrategy(),
    "avgPhaseDiff":    AvgPhaseDiffStrategy(),
    "idealPhaseDiff":  IdealPhaseDiffStrategy(),
    "diffPhaseDiff":   PhaseDiffDiffStrategy(),
    "avgDiffPhaseDiff": AvgPhaseDiffDiffStrategy(),
    "corrPhaseDiff":   CorrPhaseDiffStrategy(),
}
