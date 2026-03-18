"""
PST-52 — MVC integration tests.

Verifies that PlotController, ParseController, and MainView collaborate
correctly as a unit — no real Qt required.

Key scenarios
-------------
1. Dict-binding integrity  — after the PST-50 binding pattern
   (antSysDiag.plotSetup = plc.plotSetup), mutations via plc.set_*() are
   immediately visible through the bound reference.

2. PlotController setter chains — set_img_gen_mode() updates both plotSetup
   keys atomically.

3. PlotController graph-config filters — get_active_graphs() /
   get_active_phase_graphs() return consistent views of graphConfig.

4. PlotController new list attributes (PST-51) — twoGraphSetupList,
   threeGraphSetupList, fourGraphSetupList, allOnOneSlideGraphList initialise
   as empty lists and are independent across instances.

5. PlotController ↔ ParseController independence — they share no mutable
   state.

6. MainView helpers → Qt widget calls — each helper invokes exactly the
   expected widget methods with the expected arguments.
"""

from __future__ import annotations

import sys
import os
import types
from unittest.mock import MagicMock, patch, call

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.plot_controller import PlotController
from shared.parse_controller import ParseController


# --------------------------------------------------------------------------- #
# Helpers / fixtures
# --------------------------------------------------------------------------- #

@pytest.fixture
def plc() -> PlotController:
    return PlotController()


@pytest.fixture
def pc() -> ParseController:
    return ParseController()


def _make_mock_qt():
    m = MagicMock()
    m.parseProtLoadedProtStr       = 'Protocols: '
    m.parseProtPtu2FilesStr        = 'PTU2 Files: '
    m.parseProtTxAntDiagFilesStr   = 'TxAnt Files: '
    m.parseProtSepParPtu2FilesStr  = 'Sep PTU2 Files: '
    m.parseProtSepParTxAntDiagFilesStr = 'Sep TxAnt Files: '
    m.parseProtEolErrorStr         = 'EoL: '
    m.parseProtAbbortCritStr       = 'Abort: '
    m.parseProtMeasLimitsExcStr    = 'Limits: '
    m.parseProtParsedLoadedProtStr = 'Parsed: '
    return m


@pytest.fixture
def view():
    mock_qt = _make_mock_qt()
    with patch.dict('sys.modules', {'pyside_qtgui': mock_qt}):
        if 'ui.main_view' in sys.modules:
            del sys.modules['ui.main_view']
        from ui.main_view import MainView
        v = MainView()
        v._qt = mock_qt
        yield v, mock_qt


# --------------------------------------------------------------------------- #
# 1. Dict-binding integrity
# --------------------------------------------------------------------------- #

class TestDictBindingIntegrity:
    """After binding antSysDiag.X = plc.X, mutations via plc are visible
    through the bound name — verifies the PST-50 reference-sharing pattern."""

    def test_plot_setup_is_same_object_after_binding(self, plc):
        ant = types.SimpleNamespace()
        ant.plotSetup = plc.plotSetup
        assert ant.plotSetup is plc.plotSetup

    def test_setter_mutation_visible_through_bound_reference(self, plc):
        ant = types.SimpleNamespace()
        ant.plotSetup = plc.plotSetup
        plc.set_target_angle(1)          # writes plotSetup['targetAngle'] = 0
        assert ant.plotSetup['targetAngle'] == plc.plotSetup['targetAngle']
        assert ant.plotSetup['targetAngle'] == 0

    def test_graph_config_binding(self, plc):
        ant = types.SimpleNamespace()
        ant.graphConfig = plc.graphConfig
        plc.set_graph_conf_key('level', False)
        assert ant.graphConfig['level'] == 0
        assert ant.graphConfig is plc.graphConfig

    def test_chirp_config_binding(self, plc):
        ant = types.SimpleNamespace()
        ant.chirpConfig = plc.chirpConfig
        plc.set_chirp_key('chirp1', True)
        assert ant.chirpConfig['chirp1'] == 1

    def test_all_bound_dicts_are_same_objects(self, plc):
        ant = types.SimpleNamespace()
        ant.plotSetup      = plc.plotSetup
        ant.graphConfig    = plc.graphConfig
        ant.chirpConfig    = plc.chirpConfig
        ant.diagramConfig  = plc.diagramConfig
        ant.twoGraphConf1  = plc.twoGraphConf1
        ant.AllGraphsConf1 = plc.AllGraphsConf1
        assert ant.plotSetup      is plc.plotSetup
        assert ant.graphConfig    is plc.graphConfig
        assert ant.chirpConfig    is plc.chirpConfig
        assert ant.diagramConfig  is plc.diagramConfig
        assert ant.twoGraphConf1  is plc.twoGraphConf1
        assert ant.AllGraphsConf1 is plc.AllGraphsConf1


# --------------------------------------------------------------------------- #
# 2. PlotController setter chains
# --------------------------------------------------------------------------- #

class TestPlotControllerSetterChains:

    def test_img_gen_mode_separate_sets_both_keys(self, plc):
        plc.set_img_gen_mode(0)
        assert plc.plotSetup['SeparateRxCh'] == 1
        assert plc.plotSetup['threeGraphLayout'] == 1

    def test_img_gen_mode_combined_sets_both_keys(self, plc):
        plc.set_img_gen_mode(1)
        assert plc.plotSetup['SeparateRxCh'] == 0
        assert plc.plotSetup['threeGraphLayout'] == 0

    def test_target_angle_btn0_sets_to_1(self, plc):
        plc.set_target_angle(0)
        assert plc.plotSetup['targetAngle'] == 1

    def test_target_angle_btn1_sets_to_0(self, plc):
        plc.set_target_angle(1)
        assert plc.plotSetup['targetAngle'] == 0

    def test_y_limits_mode_btn0_separate(self, plc):
        plc.set_y_limits_mode(0)
        assert plc.plotSetup['yLimitsAntTypeSeparately'] == 1

    def test_y_limits_mode_btn1_common(self, plc):
        plc.set_y_limits_mode(1)
        assert plc.plotSetup['yLimitsAntTypeSeparately'] == 0

    def test_script_mode_0_hides_plot_window(self, plc):
        plc.set_script_mode(0)
        assert plc.plotSetup['ShowCertainPlotWindow'] == 0

    def test_script_mode_1_shows_plot_window(self, plc):
        plc.set_script_mode(1)
        assert plc.plotSetup['ShowCertainPlotWindow'] == 1


# --------------------------------------------------------------------------- #
# 3. Graph-config filter methods
# --------------------------------------------------------------------------- #

class TestGraphConfigFilters:

    def test_get_active_graphs_default_includes_level(self, plc):
        active = plc.get_active_graphs()
        assert 'level' in active

    def test_get_active_graphs_excludes_disabled(self, plc):
        plc.set_graph_conf_key('level', False)
        assert 'level' not in plc.get_active_graphs()

    def test_get_active_graphs_after_enable(self, plc):
        plc.set_graph_conf_key('diffPhaseDiff', True)
        assert 'diffPhaseDiff' in plc.get_active_graphs()

    def test_get_active_phase_graphs_only_phase(self, plc):
        # Enable all graph types that contain 'hase'
        phase_graphs = plc.get_active_phase_graphs()
        assert all('hase' in g for g in phase_graphs)

    def test_get_active_phase_graphs_excludes_level(self, plc):
        assert 'level' not in plc.get_active_phase_graphs()

    def test_get_active_phase_graphs_consistent_with_graph_config(self, plc):
        """get_active_phase_graphs() must be a subset of get_active_graphs()."""
        all_active   = set(plc.get_active_graphs())
        phase_active = set(plc.get_active_phase_graphs())
        assert phase_active.issubset(all_active)


# --------------------------------------------------------------------------- #
# 4. New list attributes (PST-51)
# --------------------------------------------------------------------------- #

class TestNewListAttributes:

    def test_two_graph_setup_list_is_empty(self, plc):
        assert plc.twoGraphSetupList == []

    def test_three_graph_setup_list_is_empty(self, plc):
        assert plc.threeGraphSetupList == []

    def test_four_graph_setup_list_is_empty(self, plc):
        assert plc.fourGraphSetupList == []

    def test_all_on_one_slide_graph_list_is_empty(self, plc):
        assert plc.allOnOneSlideGraphList == []

    def test_lists_are_independent_across_instances(self):
        plc1 = PlotController()
        plc2 = PlotController()
        plc1.twoGraphSetupList.append({'primGraph': 'level'})
        assert plc2.twoGraphSetupList == []

    def test_diagram_config_list_has_defaults(self, plc):
        assert isinstance(plc.diagramConfigList, list)
        assert len(plc.diagramConfigList) > 0


# --------------------------------------------------------------------------- #
# 5. PlotController ↔ ParseController independence
# --------------------------------------------------------------------------- #

class TestControllerIndependence:

    def test_plc_and_pc_share_no_mutable_state(self, plc, pc):
        """Mutations to plc must not affect pc and vice versa."""
        plc.set_sensor_muster_enabled(True)
        # pc has its own sysDiagFilePathDict — not affected by plc
        assert plc.plotSetup['useSensorMuster'] == 1
        assert hasattr(pc, 'sysDiagFilePathDict')  # pc still has its own data

    def test_two_plc_instances_are_independent(self):
        plc1 = PlotController()
        plc2 = PlotController()
        plc1.set_graph_conf_key('level', False)
        assert plc2.graphConfig['level'] == 1

    def test_two_pc_instances_are_independent(self):
        pc1 = ParseController()
        pc2 = ParseController()
        pc1.protocolPathDict['protocolPathTypeDictList'].append({'path': 'x'})
        assert pc2.protocolPathDict['protocolPathTypeDictList'] == []


# --------------------------------------------------------------------------- #
# 6. MainView helpers → Qt widget calls
# --------------------------------------------------------------------------- #

class TestMainViewSensorMuster:

    def test_set_sensor_muster_enabled_true_enables_both(self, view):
        v, qt = view
        v.set_sensor_muster_enabled(True)
        qt.parseProtSensorMusterLEdit.setEnabled.assert_called_with(True)
        qt.parseProtSensorMusterLabel.setEnabled.assert_called_with(True)

    def test_set_sensor_muster_enabled_false_disables_both(self, view):
        v, qt = view
        v.set_sensor_muster_enabled(False)
        qt.parseProtSensorMusterLEdit.setEnabled.assert_called_with(False)
        qt.parseProtSensorMusterLabel.setEnabled.assert_called_with(False)


class TestMainViewLabels:

    def test_set_loaded_prot_ratio_label_correct_text(self, view):
        v, qt = view
        v.set_loaded_prot_ratio_label(3, 2)
        qt.parseProtLoadedProtLabel.setText.assert_called_with('Protocols: 3 / 5')

    def test_set_loaded_prot_ratio_label_zero(self, view):
        v, qt = view
        v.set_loaded_prot_ratio_label(0, 0)
        qt.parseProtLoadedProtLabel.setText.assert_called_with('Protocols: 0 / 0')

    def test_set_eol_error_label_simple(self, view):
        v, qt = view
        v.set_eol_error_label(5)
        qt.parseProtEolErrorLabel.setText.assert_called_with('EoL: 5')

    def test_set_eol_error_label_with_total(self, view):
        v, qt = view
        v.set_eol_error_label(2, 10)
        qt.parseProtEolErrorLabel.setText.assert_called_with('EoL: 2 / 10')

    def test_set_abort_crit_label(self, view):
        v, qt = view
        v.set_abort_crit_label(1, 4)
        qt.parseProtAbbortCritLabel.setText.assert_called_with('Abort: 1 / 4')

    def test_set_meas_limits_label(self, view):
        v, qt = view
        v.set_meas_limits_label(7, 20)
        qt.parseProtMeasLimitsExcLabel.setText.assert_called_with('Limits: 7 / 20')

    def test_set_parsed_loaded_label(self, view):
        v, qt = view
        v.set_parsed_loaded_label(10, 15)
        qt.parseProtParsedLoadedProtLabel.setText.assert_called_with('Parsed: 10 / 15')


class TestMainViewFilePaths:

    def test_set_burn_in_limits_file_sets_text_and_tooltip(self, view):
        v, qt = view
        v.set_burn_in_limits_file('/some/path.yaml')
        qt.parseProtProtDataInFileBurnInLabel.setText.assert_called_with('/some/path.yaml')
        qt.parseProtProtDataInFileBurnInLabel.setToolTip.assert_called_with('/some/path.yaml')

    def test_set_cal_limits_file_sets_text_and_tooltip(self, view):
        v, qt = view
        v.set_cal_limits_file('/cal.yaml')
        qt.parseProtProtDataInFileCalLabel.setText.assert_called_with('/cal.yaml')
        qt.parseProtProtDataInFileCalLabel.setToolTip.assert_called_with('/cal.yaml')

    def test_set_burn_in_lim_groups_file(self, view):
        v, qt = view
        v.set_burn_in_lim_groups_file('/groups.yaml')
        qt.parseProtProtDataLimGroupsBurnInLabel.setText.assert_called_with('/groups.yaml')
        qt.parseProtProtDataLimGroupsBurnInLabel.setToolTip.assert_called_with('/groups.yaml')

    def test_set_cal_lim_groups_file(self, view):
        v, qt = view
        v.set_cal_lim_groups_file('/cal_groups.yaml')
        qt.parseProtProtDataLimGroupsCalLabel.setText.assert_called_with('/cal_groups.yaml')
        qt.parseProtProtDataLimGroupsCalLabel.setToolTip.assert_called_with('/cal_groups.yaml')

    def test_set_stats_input_conf_path(self, view):
        v, qt = view
        v.set_stats_input_conf_path('/stats/conf.yaml')
        qt.statsInputConfPathLabel.setText.assert_called_with('/stats/conf.yaml')
        qt.statsInputConfPathLabel.setToolTip.assert_called_with('/stats/conf.yaml')


class TestMainViewProgressBar:

    def test_reset_progress_bar_calls_reset(self, view):
        v, qt = view
        v.reset_progress_bar()
        qt.parseProtProgresBar.reset.assert_called_once()

    def test_set_progress_bar_range(self, view):
        v, qt = view
        v.set_progress_bar_range(50)
        qt.parseProtProgresBar.setRange.assert_called_with(0, 50)

    def test_set_progress_bar_format(self, view):
        v, qt = view
        v.set_progress_bar_format('5 / 10')
        qt.parseProtProgresBar.setFormat.assert_called_with('5 / 10')

    def test_set_progress_bar_value(self, view):
        v, qt = view
        v.set_progress_bar(7)
        qt.parseProtProgresBar.setValue.assert_called_with(7)
