"""Smoke tests for the limits UI pipeline.

Covers:
  - File loading paths resolved from auxiliary.py (config/ subfolder)
  - Correct button-press behaviour: parseData, clearData, group navigation
  - Stats tab behaviour: write_statistic, clear_sel_stats_data, group active state

These tests wire real ParseController + real (or mock) MainView through the
AppContext, calling handler functions directly — no real Qt event loop needed.
"""
from __future__ import annotations

import os
import pathlib
import pytest
from unittest.mock import MagicMock, patch, call

import calibration_statistics_tool.shared.auxiliary as aux

# Derive the config dir from auxiliary.py's location (shared/ -> shared/config/).
# Do NOT use aux.burnInLimitsFilePath etc. directly in tests: those paths depend
# on sys.argv[0] (= the pytest executable) when run via pytest.
_PROJECT_ROOT = pathlib.Path(aux.__file__).resolve().parent.parent
_CONFIG_DIR = pathlib.Path(aux.__file__).resolve().parent / 'config'
from calibration_statistics_tool.shared.parse_controller import ParseController
from calibration_statistics_tool.ui.handlers.app_context import AppContext
from calibration_statistics_tool.ui.handlers.parse_handlers import parseData, clearData
from calibration_statistics_tool.ui.handlers.stats_handlers import (
    write_statistic,
    clear_sel_stats_data,
    _on_group_forward,
    _on_group_back,
    set_limits_group_active,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_qt(
    burn_in_limits_path: str = '',
    cal_limits_path: str = '',
    burn_in_groups_path: str = '',
    cal_groups_path: str = '',
    include_burn_in: bool = False,
    include_cal: bool = False,
    extend_burn_in: bool = False,
    extend_cal: bool = False,
    extend_burn_in_groups: bool = False,
    extend_cal_groups: bool = False,
) -> MagicMock:
    """Return a MagicMock that mimics the qt widget layer for limits-related widgets."""
    qt = MagicMock()
    # parse-tab limits path labels
    qt.parseProtProtDataInFileBurnInLabel.text.return_value = burn_in_limits_path
    qt.parseProtProtDataInFileCalLabel.text.return_value = cal_limits_path
    qt.parseProtProtDataLimGroupsBurnInLabel.text.return_value = burn_in_groups_path
    qt.parseProtProtDataLimGroupsCalLabel.text.return_value = cal_groups_path
    # include / extend checkboxes
    qt.parseProtProtDataBurnInInclCheckBox.isChecked.return_value = include_burn_in
    qt.parseProtProtDataCalInclCheckBox.isChecked.return_value = include_cal
    qt.parseProtProtDataBurnInExtCheckBox.isChecked.return_value = extend_burn_in
    qt.parseProtProtDataCalExtCheckBox.isChecked.return_value = extend_cal
    qt.parseProtProtDataBurnInLimGroupsExtCheckBox.isChecked.return_value = extend_burn_in_groups
    qt.parseProtProtDataCalLimGroupsExtCheckBox.isChecked.return_value = extend_cal_groups
    # protocol list (no protocols selected → empty parse)
    qt.parseProtSelProtTable.rowCount.return_value = 0
    # stats tab buttons
    qt.statsGroupsTypeBurnInRadio.isChecked.return_value = True
    qt.statsGroupsTypeButtonGroup.checkedId.return_value = 0  # 0 = BurnIn
    # statsTable
    qt.statsTable.rowCount.return_value = 0
    return qt


def _make_mv() -> MagicMock:
    mv = MagicMock()
    mv.statsGroupNameLabel = MagicMock()
    mv.statsGroupNameString = ''
    mv.get_burn_in_active_group_index.return_value = 0
    mv.get_cal_active_group_index.return_value = 0
    return mv


def _make_ctx(qt=None, mv=None, pc=None) -> AppContext:
    qt = qt or _make_qt()
    mv = mv or _make_mv()
    pc = pc or ParseController()
    plc = MagicMock()
    plc.plotSetup = {'useSensorMuster': 0, 'sensorMusterList': []}
    return AppContext(qt=qt, mv=mv, plc=plc, pc=pc)


# ---------------------------------------------------------------------------
# 1. File loading — config paths exist on disk
# ---------------------------------------------------------------------------

class TestConfigFilePaths:
    """Smoke: the 5 limits config files exist in the project config/ folder."""

    def test_burn_in_limits_yaml_exists(self):
        p = _CONFIG_DIR / aux.burnInLimitsFileName
        assert p.is_file(), f"BurnInLimits.yaml not found at: {p}"

    def test_cal_limits_yaml_exists(self):
        p = _CONFIG_DIR / aux.calLimitsFileName
        assert p.is_file(), f"CalLimits.yaml not found at: {p}"

    def test_burn_in_groups_yaml_exists(self):
        p = _CONFIG_DIR / aux.burnInLimGroupsFileName
        assert p.is_file(), f"BurnInLimGroups.yaml not found at: {p}"

    def test_cal_groups_yaml_exists(self):
        p = _CONFIG_DIR / aux.calLimGroupsFileName
        assert p.is_file(), f"CalLimGroups.yaml not found at: {p}"

    def test_stats_input_conf_json_exists(self):
        p = _CONFIG_DIR / aux.statsinputconffilename
        assert p.is_file(), f"StatisticsLimitsConfig.json not found at: {p}"

    def test_config_dir_is_config_subfolder(self):
        """The resolved config directory must be the project-level config/ folder."""
        assert _CONFIG_DIR.is_dir(), f"config/ folder not found at: {_CONFIG_DIR}"
        assert _CONFIG_DIR.name == 'config'


# ---------------------------------------------------------------------------
# 2. Button press — parseData with no paths (no crash)
# ---------------------------------------------------------------------------

class TestParseDataButton:
    """Smoke: calling parseData handler does not raise even with missing paths."""

    # parseData calls several internal helpers before the limits section.
    # Patch them so the test focuses only on limits behaviour.
    _PARSE_DATA_PATCHES = (
        'calibration_statistics_tool.ui.handlers.parse_handlers.filter_protocol_file_lists',
        'calibration_statistics_tool.ui.handlers.parse_handlers.setup_progress_bar',
        'calibration_statistics_tool.ui.handlers.parse_handlers._load_protocol_data',
        'calibration_statistics_tool.ui.handlers.parse_handlers.merge_into_parsed_dicts',
        'calibration_statistics_tool.ui.handlers.parse_handlers._populate_accepted_protocols_table',
    )

    def _run_parseData(self, ctx) -> None:
        """Run parseData with all non-limits internals patched out."""
        with patch(self._PARSE_DATA_PATCHES[0], return_value=([], [])), \
             patch(self._PARSE_DATA_PATCHES[1], return_value=('', 0)), \
             patch(self._PARSE_DATA_PATCHES[2], return_value=([], [], [], [])), \
             patch(self._PARSE_DATA_PATCHES[3]), \
             patch(self._PARSE_DATA_PATCHES[4]):
            parseData(ctx)

    def _make_pc_with_protocols(self) -> MagicMock:
        """Return a MagicMock that passes the early-return guard in parseData.

        Not using spec= because Python evaluates all arguments before calling
        a patched function, and spec= would block attrs that are only passed
        through to patched helpers (e.g. sysDiagFilePathDict).
        """
        pc = MagicMock()
        # protToBeParsedDict must be non-empty so parseData doesn't early-return.
        pc.protToBeParsedDict = {'protocolPathTypeDictList': [{'dummy': True}]}
        pc.parsedProtDict = {'protocolPathTypeDictList': []}
        pc.burnInLimitsGroupDict = {'limitsGroupList': [], 'activeGroupIndex': -1}
        pc.calLimitsGroupDict = {'limitsGroupList': [], 'activeGroupIndex': -1}
        pc.limitsRowListDict = {'limitsRowList': []}
        return pc

    def test_parse_data_no_limits_paths_no_crash(self):
        """Empty path labels → limits skipped, no exception raised."""
        pc = self._make_pc_with_protocols()
        ctx = _make_ctx(
            qt=_make_qt(burn_in_limits_path='', cal_limits_path=''),
            pc=pc,
        )
        self._run_parseData(ctx)   # must not raise

    def test_parse_data_with_real_config_paths_no_crash(self):
        """Real YAML paths provided → limits pipeline runs without crash."""
        pc = self._make_pc_with_protocols()
        ctx = _make_ctx(
            qt=_make_qt(
                burn_in_limits_path=str(_CONFIG_DIR / aux.burnInLimitsFileName),
                cal_limits_path=str(_CONFIG_DIR / aux.calLimitsFileName),
                burn_in_groups_path=str(_CONFIG_DIR / aux.burnInLimGroupsFileName),
                cal_groups_path=str(_CONFIG_DIR / aux.calLimGroupsFileName),
                include_burn_in=True,
                include_cal=True,
            ),
            pc=pc,
        )
        self._run_parseData(ctx)

    def test_parse_data_no_file_set_label_no_crash(self):
        """'No file set.' sentinel label → treated as missing, no crash."""
        pc = self._make_pc_with_protocols()
        ctx = _make_ctx(
            qt=_make_qt(
                burn_in_limits_path='No file set.',
                cal_limits_path='No file set.',
            ),
            pc=pc,
        )
        self._run_parseData(ctx)

    def test_parse_data_calls_parse_protocol_limits(self):
        """parseData must call ctx.pc.parse_protocol_limits at least once."""
        pc = self._make_pc_with_protocols()
        ctx = _make_ctx(pc=pc)
        self._run_parseData(ctx)
        pc.parse_protocol_limits.assert_called_once()

    def test_parse_data_calls_build_limits_groups(self):
        """parseData must call ctx.pc.build_limits_groups after parse_protocol_limits."""
        pc = self._make_pc_with_protocols()
        ctx = _make_ctx(pc=pc)
        self._run_parseData(ctx)
        pc.build_limits_groups.assert_called_once()


# ---------------------------------------------------------------------------
# 3. Button press — clearData resets limits state
# ---------------------------------------------------------------------------

class TestClearDataButton:
    """Smoke: clearData properly resets the limits-related UI and state."""

    def test_clear_data_no_crash(self):
        ctx = _make_ctx()
        with patch('calibration_statistics_tool.ui.handlers.parse_handlers.clearTable'):
            clearData(ctx)

    def test_clear_data_calls_pc_clear_state(self):
        """clearData must call ctx.pc.clear_state()."""
        pc = MagicMock(spec=ParseController)
        ctx = _make_ctx(pc=pc)
        with patch('calibration_statistics_tool.ui.handlers.parse_handlers.clearTable'), \
             patch('calibration_statistics_tool.ui.handlers.parse_handlers.clear_stats_ui'):
            clearData(ctx)
        pc.clear_state.assert_called_once()

    def test_clear_data_populates_empty_burn_in_groups(self):
        """clearData must call mv.populate_burn_in_groups([])."""
        mv = _make_mv()
        ctx = _make_ctx(mv=mv)
        with patch('calibration_statistics_tool.ui.handlers.parse_handlers.clearTable'):
            clearData(ctx)
        mv.populate_burn_in_groups.assert_called_with([])

    def test_clear_data_populates_empty_cal_groups(self):
        """clearData must call mv.populate_cal_groups([])."""
        mv = _make_mv()
        ctx = _make_ctx(mv=mv)
        with patch('calibration_statistics_tool.ui.handlers.parse_handlers.clearTable'):
            clearData(ctx)
        mv.populate_cal_groups.assert_called_with([])


# ---------------------------------------------------------------------------
# 4. Stats tab — write_statistic button
# ---------------------------------------------------------------------------

class TestWriteStatisticButton:
    """Smoke: write_statistic handler does not crash with empty state."""

    def test_write_statistic_empty_state_no_crash(self):
        ctx = _make_ctx()
        write_statistic(ctx)  # must not raise

    def test_write_statistic_with_real_pc_no_crash(self):
        pc = ParseController()
        ctx = _make_ctx(pc=pc)
        write_statistic(ctx)

    def test_write_statistic_calls_fill_stats_table(self):
        """write_statistic must invoke fill_stats_table to refresh the UI."""
        with patch('calibration_statistics_tool.ui.handlers.stats_handlers.fill_stats_table') as mock_fill:
            ctx = _make_ctx()
            write_statistic(ctx)
            mock_fill.assert_called_once_with(ctx)


# ---------------------------------------------------------------------------
# 5. Stats tab — clear_sel_stats_data button
# ---------------------------------------------------------------------------

class TestClearSelStatsDataButton:
    """Smoke: clear_sel_stats_data clears active group index and resets label."""

    def test_clear_sel_stats_data_no_crash(self):
        ctx = _make_ctx()
        clear_sel_stats_data(ctx)

    def test_clear_sel_stats_data_calls_plot_frame_clear(self):
        """clear_sel_stats_data must clear the stats plot frame."""
        mv = _make_mv()
        ctx = _make_ctx(mv=mv)
        clear_sel_stats_data(ctx)
        mv.statsPlotFrame.clear.assert_called_once()

    def test_clear_sel_stats_data_resets_stats_group_name_label(self):
        """clear_sel_stats_data must reset statsGroupNameLabel to statsGroupNameString."""
        mv = _make_mv()
        mv.statsGroupNameString = 'BurnIn'
        ctx = _make_ctx(mv=mv)
        clear_sel_stats_data(ctx)
        mv.statsGroupNameLabel.setText.assert_called_with('BurnIn')

    def test_clear_sel_stats_data_clears_group_name_label(self):
        """After clear, statsGroupNameLabel text is reset (empty or default)."""
        mv = _make_mv()
        ctx = _make_ctx(mv=mv)
        clear_sel_stats_data(ctx)
        mv.statsGroupNameLabel.setText.assert_called()


# ---------------------------------------------------------------------------
# 6. Stats tab — group navigation (Forward / Back buttons)
# ---------------------------------------------------------------------------

class TestGroupNavigationButtons:
    """Smoke: Forward/Back buttons navigate active group index."""

    def _pc_with_groups(self) -> ParseController:
        """Return a ParseController seeded with 3 fake BurnIn groups."""
        pc = ParseController()
        fake_group = MagicMock()
        fake_group.name = 'TestGroup'
        fake_group.protType = 'BurnIn'
        fake_group.limitsRowMatchDictList = []
        pc.burnInLimitsGroupDict['limitsGroupList'] = [fake_group, fake_group, fake_group]
        pc.burnInLimitsGroupDict['activeGroupIndex'] = -1
        return pc

    def test_forward_advances_active_index(self):
        pc = self._pc_with_groups()
        qt = _make_qt()
        qt.statsGroupsTypeButtonGroup.checkedId.return_value = 0  # BurnIn
        ctx = _make_ctx(qt=qt, pc=pc)
        with patch('calibration_statistics_tool.ui.handlers.stats_handlers.set_limits_group_active'):
            _on_group_forward(ctx)
        assert pc.burnInLimitsGroupDict['activeGroupIndex'] == 0

    def test_forward_wraps_at_end(self):
        pc = self._pc_with_groups()
        pc.burnInLimitsGroupDict['activeGroupIndex'] = 2  # at last
        qt = _make_qt()
        qt.statsGroupsTypeButtonGroup.checkedId.return_value = 0
        ctx = _make_ctx(qt=qt, pc=pc)
        with patch('calibration_statistics_tool.ui.handlers.stats_handlers.set_limits_group_active'):
            _on_group_forward(ctx)
        assert pc.burnInLimitsGroupDict['activeGroupIndex'] == 0

    def test_back_decrements_active_index(self):
        pc = self._pc_with_groups()
        pc.burnInLimitsGroupDict['activeGroupIndex'] = 2
        qt = _make_qt()
        qt.statsGroupsTypeButtonGroup.checkedId.return_value = 0
        ctx = _make_ctx(qt=qt, pc=pc)
        with patch('calibration_statistics_tool.ui.handlers.stats_handlers.set_limits_group_active'):
            _on_group_back(ctx)
        assert pc.burnInLimitsGroupDict['activeGroupIndex'] == 1

    def test_back_wraps_at_start(self):
        pc = self._pc_with_groups()
        pc.burnInLimitsGroupDict['activeGroupIndex'] = 0  # at first
        qt = _make_qt()
        qt.statsGroupsTypeButtonGroup.checkedId.return_value = 0
        ctx = _make_ctx(qt=qt, pc=pc)
        with patch('calibration_statistics_tool.ui.handlers.stats_handlers.set_limits_group_active'):
            _on_group_back(ctx)
        assert pc.burnInLimitsGroupDict['activeGroupIndex'] == 2

    def test_forward_no_crash_when_no_groups(self):
        pc = ParseController()  # empty groups
        qt = _make_qt()
        qt.statsGroupsTypeButtonGroup.checkedId.return_value = 0
        ctx = _make_ctx(qt=qt, pc=pc)
        _on_group_forward(ctx)  # must not raise

    def test_back_no_crash_when_no_groups(self):
        pc = ParseController()
        qt = _make_qt()
        qt.statsGroupsTypeButtonGroup.checkedId.return_value = 0
        ctx = _make_ctx(qt=qt, pc=pc)
        _on_group_back(ctx)  # must not raise

    def test_forward_cal_branch_advances_cal_index(self):
        pc = ParseController()
        fake_group = MagicMock()
        fake_group.name = 'CalGroup'
        fake_group.protType = 'Calibration'
        fake_group.limitsRowMatchDictList = []
        pc.calLimitsGroupDict['limitsGroupList'] = [fake_group, fake_group]
        pc.calLimitsGroupDict['activeGroupIndex'] = -1
        qt = _make_qt()
        qt.statsGroupsTypeButtonGroup.checkedId.return_value = 1  # Cal
        ctx = _make_ctx(qt=qt, pc=pc)
        with patch('calibration_statistics_tool.ui.handlers.stats_handlers.set_limits_group_active'):
            _on_group_forward(ctx)
        assert pc.calLimitsGroupDict['activeGroupIndex'] == 0


# ---------------------------------------------------------------------------
# 7. Tab behaviour — populate_burn_in_groups / populate_cal_groups
# ---------------------------------------------------------------------------

class TestTabGroupPopulation:
    """Smoke: mv group-population helpers called correctly after parseData."""

    def _make_pc_for_parse(self) -> MagicMock:
        pc = MagicMock()  # no spec — see TestParseDataButton._make_pc_with_protocols
        pc.protToBeParsedDict = {'protocolPathTypeDictList': [{'dummy': True}]}
        pc.parsedProtDict = {'protocolPathTypeDictList': []}
        pc.burnInLimitsGroupDict = {'limitsGroupList': [], 'activeGroupIndex': -1}
        pc.calLimitsGroupDict = {'limitsGroupList': [], 'activeGroupIndex': -1}
        pc.limitsRowListDict = {'limitsRowList': []}
        return pc

    def _run_parseData(self, ctx) -> None:
        with patch('calibration_statistics_tool.ui.handlers.parse_handlers.filter_protocol_file_lists', return_value=([], [])), \
             patch('calibration_statistics_tool.ui.handlers.parse_handlers.setup_progress_bar', return_value=('', 0)), \
             patch('calibration_statistics_tool.ui.handlers.parse_handlers._load_protocol_data', return_value=([], [], [], [])), \
             patch('calibration_statistics_tool.ui.handlers.parse_handlers.merge_into_parsed_dicts'), \
             patch('calibration_statistics_tool.ui.handlers.parse_handlers._populate_accepted_protocols_table'):
            parseData(ctx)

    def test_populate_burn_in_groups_called_after_parse(self):
        mv = _make_mv()
        pc = self._make_pc_for_parse()
        ctx = _make_ctx(mv=mv, pc=pc)
        self._run_parseData(ctx)
        mv.populate_burn_in_groups.assert_called()

    def test_populate_cal_groups_called_after_parse(self):
        mv = _make_mv()
        pc = self._make_pc_for_parse()
        ctx = _make_ctx(mv=mv, pc=pc)
        self._run_parseData(ctx)
        mv.populate_cal_groups.assert_called()

    def test_groups_combobox_disabled_when_no_groups(self, shared_main_view):
        """With empty group list, BurnIn combobox should be disabled."""
        shared_main_view.populate_burn_in_groups([])
        assert not shared_main_view.parseProtProtDataBurnInGroupSelComboBox.isEnabled()

    def test_groups_combobox_enabled_when_groups_present(self, shared_main_view):
        """With non-empty group list, BurnIn combobox should be enabled."""
        shared_main_view.populate_burn_in_groups(['Group A', 'Group B'])
        assert shared_main_view.parseProtProtDataBurnInGroupSelComboBox.isEnabled()

    def test_cal_combobox_disabled_when_no_groups(self, shared_main_view):
        shared_main_view.populate_cal_groups([])
        assert not shared_main_view.parseProtProtDataCalGroupSelComboBox.isEnabled()

    def test_cal_combobox_enabled_when_groups_present(self, shared_main_view):
        shared_main_view.populate_cal_groups(['CalGroup 1'])
        assert shared_main_view.parseProtProtDataCalGroupSelComboBox.isEnabled()

    def test_group_name_label_updates_on_set_active(self):
        """set_limits_group_active must update statsGroupNameLabel."""
        mv = _make_mv()
        pc = ParseController()
        fake_group = MagicMock()
        fake_group.name = 'MyGroup'
        fake_group.protType = 'BurnIn'
        fake_group.limitsRowMatchDictList = []
        pc.burnInLimitsGroupDict['limitsGroupList'] = [fake_group]
        ctx = _make_ctx(mv=mv, pc=pc)
        set_limits_group_active(ctx, fake_group)
        mv.statsGroupNameLabel.setText.assert_called()
        label_text = mv.statsGroupNameLabel.setText.call_args[0][0]
        assert 'MyGroup' in label_text
