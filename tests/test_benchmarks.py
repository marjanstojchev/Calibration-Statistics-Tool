"""
Performance benchmarks for vectorised hot paths in calcdiagram_functions.

Run locally with:   pytest --benchmark-only
Skip in CI with:    pytest --benchmark-disable
Not enforced as pass/fail — informational only.
"""
import copy
import pytest
from calibration_statistics_tool.shared.calcdiagram_functions import getAntLevel, getPhaseDiff, getPtuAngVals


# ---------------------------------------------------------------------------
# getPtuAngVals — angle extraction
# ---------------------------------------------------------------------------

def test_getPtuAngVals_fast_path(benchmark, simple_ptu2_data):
    """Fast path: angles_array pre-built — single array return."""
    benchmark(getPtuAngVals, simple_ptu2_data)


def test_getPtuAngVals_slow_path(benchmark, simple_ptu2_data):
    """Slow path: angles_array=None — loop over ptuPosDataList."""
    data = copy.copy(simple_ptu2_data)
    data.angles_array = None
    benchmark(getPtuAngVals, data)


# ---------------------------------------------------------------------------
# getAntLevel — level slice for one antenna / chirp combination
# ---------------------------------------------------------------------------

def test_getAntLevel_fast_path(benchmark, simple_ptu2_data):
    """Fast path: levels_array pre-built — NumPy column slice."""
    benchmark(getAntLevel, 0, 0, simple_ptu2_data)


def test_getAntLevel_slow_path(benchmark, simple_ptu2_data):
    """Slow path: levels_array=None — loop over ptuPosDataList."""
    data = copy.copy(simple_ptu2_data)
    data.levels_array = None
    benchmark(getAntLevel, 0, 0, data)


# ---------------------------------------------------------------------------
# getPhaseDiff — phase-difference slice for one diff-pair / chirp combination
# ---------------------------------------------------------------------------

def test_getPhaseDiff_fast_path(benchmark, simple_ptu2_data):
    """Fast path: phases_array pre-built — NumPy column slice."""
    benchmark(getPhaseDiff, 0, 0, simple_ptu2_data)


def test_getPhaseDiff_slow_path(benchmark, simple_ptu2_data):
    """Slow path: phases_array=None — loop over ptuPosDataList."""
    data = copy.copy(simple_ptu2_data)
    data.phases_array = None
    benchmark(getPhaseDiff, 0, 0, data)


# ---------------------------------------------------------------------------
# buildArrays — one-time array construction cost (called once per file load)
# ---------------------------------------------------------------------------

def test_buildArrays(benchmark, simple_ptu2_data):
    """Cost of constructing all three NumPy arrays from ptuPosDataList."""
    def _run():
        simple_ptu2_data.angles_array = None
        simple_ptu2_data.levels_array = None
        simple_ptu2_data.phases_array = None
        simple_ptu2_data.buildArrays()

    benchmark(_run)
