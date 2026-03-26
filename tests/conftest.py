"""
Shared pytest fixtures for Calibration Statistics Tool tests.
Provides reusable mock PTU2ParseData structures matching real parsed data.
"""
import sys
import os
import pytest
import numpy as np

# Must be set before PySide6 / Qt widgets are imported anywhere
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


@pytest.fixture(scope="session", autouse=True)
def _qapp_session():
    """Ensure a single QApplication exists for the entire test session.

    Session-scoped and autouse so it is created before any Qt widget is
    instantiated, including module-level widget creation in sys_diag_tab.py.
    """
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app

# Add project root and shared to path
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _subdir in ['shared', 'system_diagrams', 'tx_diagrams', 'antenna_patterns']:
    _path = os.path.join(_root, _subdir)
    if _path not in sys.path:
        sys.path.insert(0, _path)

from shared.parsePTU2data import (
    PTU2ParseData, AntennaInfo, ChirpInfo,
    PtuPosMeasData, ChirpMeasData, AntennaLevelData, DiffPhaseData,
    MeasSetupInfo, FileTitle
)


def make_antenna_level(level_db: float, variance: float = 0.01) -> AntennaLevelData:
    """Create an AntennaLevelData object with given values."""
    a = AntennaLevelData()
    a.dLevel = level_db
    a.dVarianzLevel = variance
    return a


def make_diff_phase(phase_deg: float, variance: float = 0.1) -> DiffPhaseData:
    """Create a DiffPhaseData object with given values."""
    d = DiffPhaseData()
    d.dDiffPhase = phase_deg
    d.dVarianzDiffPhase = variance
    return d


def make_chirp_meas(levels_db: list, phases_deg: list) -> ChirpMeasData:
    """Create a ChirpMeasData with given antenna levels and phase diffs."""
    level_objs = [make_antenna_level(l) for l in levels_db]
    phase_objs = [make_diff_phase(p) for p in phases_deg]
    return ChirpMeasData(level_objs, phase_objs)


def make_ptu_pos(angle_deg: float, chirp_data: list) -> PtuPosMeasData:
    """Create a PtuPosMeasData at the given angle with the given chirp data."""
    pos = PtuPosMeasData()
    pos.d_PTU_Angle = angle_deg
    pos.setChirpMeasDataList(chirp_data)
    return pos


@pytest.fixture
def simple_ptu2_data():
    """
    A minimal but realistic PTU2ParseData fixture:
    - 3 angles: -10°, 0°, 10°
    - 2 antennas
    - 1 antenna distance diff pair
    - 2 active chirps (chirp 0 and 1), 2 inactive (chirp 2 and 3)
    - Known level and phase values for easy assertion
    """
    data = PTU2ParseData()

    # Antenna info
    data.antennaInfo = AntennaInfo()
    data.antennaInfo.rfSerial = 12345
    data.antennaInfo.antennaType = 158
    data.antennaInfo.nofAntennas = 2
    data.antennaInfo.setAntennaDistances([0.006])  # 6mm in meters
    data.antennaInfo.setNofAntennaDiffValues(1)

    # Chirp info: chirp 0 and 1 active, 2 and 3 inactive
    for i in range(PTU2ParseData.MAX_CHIRP):
        ci = ChirpInfo()
        ci.chirp = i
        ci.active = 1 if i < 2 else 0
        ci.centerFrequency = 76.5e9  # 76.5 GHz
        ci.setDiffPhases([0.0])      # zero offset
        data.chirpInfoList.append(ci)

    # PTU positions at -10°, 0°, +10°
    angles = [-10.0, 0.0, 10.0]
    # Levels per chirp: chirp0=[-20,-25], chirp1=[-21,-26], chirp2/3 inactive
    # Phases per chirp: chirp0=[5.0], chirp1=[6.0]
    level_table = [
        [[-20.0, -25.0], [-21.0, -26.0], [-99.0, -99.0], [-99.0, -99.0]],  # angle -10
        [[-10.0, -15.0], [-11.0, -16.0], [-99.0, -99.0], [-99.0, -99.0]],  # angle  0
        [[-20.0, -25.0], [-21.0, -26.0], [-99.0, -99.0], [-99.0, -99.0]],  # angle +10
    ]
    phase_table = [
        [[5.0],  [6.0],  [0.0], [0.0]],  # angle -10
        [[0.0],  [0.0],  [0.0], [0.0]],  # angle  0
        [[-5.0], [-6.0], [0.0], [0.0]],  # angle +10
    ]

    for ang_idx, angle in enumerate(angles):
        chirp_list = []
        for chirp_idx in range(PTU2ParseData.MAX_CHIRP):
            cm = make_chirp_meas(
                level_table[ang_idx][chirp_idx],
                phase_table[ang_idx][chirp_idx]
            )
            chirp_list.append(cm)
        pos = make_ptu_pos(angle, chirp_list)
        data.ptuPosDataList.append(pos)

    data.bDataValid = True
    data.fileNamePath = 'test_fixture_file.txt'
    data.buildArrays()
    return data


@pytest.fixture
def single_active_chirp_ptu2_data():
    """
    PTU2ParseData with only chirp 0 active.
    Useful for testing averaging with a single chirp.
    """
    data = PTU2ParseData()

    data.antennaInfo = AntennaInfo()
    data.antennaInfo.nofAntennas = 2
    data.antennaInfo.setAntennaDistances([0.006])
    data.antennaInfo.setNofAntennaDiffValues(1)

    for i in range(PTU2ParseData.MAX_CHIRP):
        ci = ChirpInfo()
        ci.chirp = i
        ci.active = 1 if i == 0 else 0
        ci.centerFrequency = 76.5e9
        ci.setDiffPhases([0.0])
        data.chirpInfoList.append(ci)

    angles = [-5.0, 0.0, 5.0]
    for angle in angles:
        chirp_list = []
        for chirp_idx in range(PTU2ParseData.MAX_CHIRP):
            cm = make_chirp_meas([-10.0, -20.0], [3.0])
            chirp_list.append(cm)
        pos = make_ptu_pos(angle, chirp_list)
        data.ptuPosDataList.append(pos)

    data.bDataValid = True
    data.buildArrays()
    return data
