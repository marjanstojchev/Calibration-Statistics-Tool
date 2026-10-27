"""
Unit tests for PlotController (PST-46).
No Qt required.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from calibration_statistics_tool.shared.plot_controller import PlotController


# --------------------------------------------------------------------------- #
# Fixtures
# --------------------------------------------------------------------------- #

@pytest.fixture
def pc() -> PlotController:
    return PlotController()


# --------------------------------------------------------------------------- #
# Initial state
# --------------------------------------------------------------------------- #

class TestInitialState:

    def test_plot_setup_defaults(self, pc):
        assert pc.plotSetup['SeparateRxCh'] == 1
        assert pc.plotSetup['threeGraphLayout'] == 1
        assert pc.plotSetup['imageDpi'] == 220
        assert pc.plotSetup['xScaleSizeAuto'] == 0
        assert pc.plotSetup['xScaleSizeAz'] == 90.0
        assert pc.plotSetup['xScaleSizeEl'] == 45.0
        assert pc.plotSetup['idealPhaseDiff'] == 1
        assert pc.plotSetup['diffPhaseDiffScalingFactor'] == 1.5
        assert pc.plotSetup['yLimitsAntTypeSeparately'] == 1
        assert pc.plotSetup['nofSensorMeasToShow'] == 32
        assert pc.plotSetup['allOnOneSlide'] == 1
        assert pc.plotSetup['ShowCertainPlotWindow'] == 0

    def test_graph_config_defaults(self, pc):
        assert pc.graphConfig['level'] == 1
        assert pc.graphConfig['normLevel'] == 1
        assert pc.graphConfig['corrPhaseDiff'] == 1
        assert pc.graphConfig['phaseDiff'] == 1
        assert pc.graphConfig['avgLevel'] == 0
        assert pc.graphConfig['diffPhaseDiff'] == 0

    def test_two_graph_conf_defaults(self, pc):
        assert pc.twoGraphConf1['primGraph'] == 'level'
        assert pc.twoGraphConf1['secGraph'] == 'normLevel'
        assert pc.twoGraphConf2['primGraph'] == 'corrPhaseDiff'
        assert pc.twoGraphConf2['secGraph'] == 'diffPhaseDiff'

    def test_four_graph_conf_defaults(self, pc):
        assert pc.fourGraphConf1['graphType'] == 'level'
        assert pc.fourGraphConf2['graphType'] == 'corrPhaseDiff'
        assert pc.fourGraphConf3['graphType'] == 'diffPhaseDiff'

    def test_three_graph_conf_defaults(self, pc):
        assert pc.threeGraphConf1['graphType'] == 'corrPhaseDiff'
        assert pc.threeGraphConf2['graphType'] == 'diffPhaseDiff'
        assert pc.threeGraphConf3['graphType'] == 'phaseDiff'

    def test_all_graphs_conf_defaults(self, pc):
        assert pc.AllGraphsConf1['graphType'] == 'level'
        assert pc.AllGraphsConf2['graphType'] == 'corrPhaseDiff'
        assert pc.AllGraphsConf3['graphType'] == 'diffPhaseDiff'

    def test_plot_window_config_defaults(self, pc):
        assert pc.plotWindowConfig['inputMode'] == 1
        assert pc.plotWindowConfig['showPlotAllMode'] == 0
        assert pc.plotWindowConfig['graph'] == 'level'
        assert pc.plotWindowConfig['antType'] == 0
        assert pc.plotWindowConfig['diagramNum'] == 0
        assert pc.plotWindowConfig['rxCh'] == 0

    def test_chirp_config_defaults(self, pc):
        assert pc.chirpConfig['chirp0'] == 1
        assert pc.chirpConfig['chirp1'] == 0


# --------------------------------------------------------------------------- #
# Image generation mode
# --------------------------------------------------------------------------- #

class TestImgGenMode:

    def test_set_img_gen_mode_separate(self, pc):
        pc.set_img_gen_mode(0)
        assert pc.plotSetup['SeparateRxCh'] == 1
        assert pc.plotSetup['threeGraphLayout'] == 1

    def test_set_img_gen_mode_combined(self, pc):
        pc.set_img_gen_mode(1)
        assert pc.plotSetup['SeparateRxCh'] == 0
        assert pc.plotSetup['threeGraphLayout'] == 0

    def test_set_three_graph_layout_enable(self, pc):
        pc.set_three_graph_layout(True)
        assert pc.plotSetup['threeGraphLayout'] == 1

    def test_set_three_graph_layout_disable(self, pc):
        pc.set_three_graph_layout(False)
        assert pc.plotSetup['threeGraphLayout'] == 0


# --------------------------------------------------------------------------- #
# Scaling / DPI
# --------------------------------------------------------------------------- #

class TestScaling:

    def test_set_image_dpi(self, pc):
        pc.set_image_dpi(300)
        assert pc.plotSetup['imageDpi'] == 300

    def test_set_x_scale_auto_on(self, pc):
        pc.set_x_scale_auto(True)
        assert pc.plotSetup['xScaleSizeAuto'] == 1

    def test_set_x_scale_auto_off(self, pc):
        pc.set_x_scale_auto(False)
        assert pc.plotSetup['xScaleSizeAuto'] == 0

    def test_set_x_scale_az(self, pc):
        pc.set_x_scale_az(60.0)
        assert pc.plotSetup['xScaleSizeAz'] == 60.0

    def test_set_x_scale_el(self, pc):
        pc.set_x_scale_el(30.0)
        assert pc.plotSetup['xScaleSizeEl'] == 30.0

    def test_set_y_limits_separate(self, pc):
        pc.set_y_limits_mode(0)
        assert pc.plotSetup['yLimitsAntTypeSeparately'] == 1

    def test_set_y_limits_combined(self, pc):
        pc.set_y_limits_mode(1)
        assert pc.plotSetup['yLimitsAntTypeSeparately'] == 0

    def test_set_diff_phase_diff_scaling(self, pc):
        pc.set_diff_phase_diff_scaling(2.0)
        assert pc.plotSetup['diffPhaseDiffScalingFactor'] == 2.0


# --------------------------------------------------------------------------- #
# Ideal phase diff / slide layout
# --------------------------------------------------------------------------- #

class TestSlideLayout:

    def test_set_ideal_phase_diff_on(self, pc):
        pc.set_ideal_phase_diff(True)
        assert pc.plotSetup['idealPhaseDiff'] == 1

    def test_set_ideal_phase_diff_off(self, pc):
        pc.set_ideal_phase_diff(False)
        assert pc.plotSetup['idealPhaseDiff'] == 0

    def test_set_n_sensor_meas_to_show(self, pc):
        pc.set_n_sensor_meas_to_show(16)
        assert pc.plotSetup['nofSensorMeasToShow'] == 16

    def test_set_all_on_one_slide_on(self, pc):
        pc.set_all_on_one_slide(True)
        assert pc.plotSetup['allOnOneSlide'] == 1

    def test_set_all_on_one_slide_off(self, pc):
        pc.set_all_on_one_slide(False)
        assert pc.plotSetup['allOnOneSlide'] == 0

    def test_set_script_mode_batch(self, pc):
        pc.set_script_mode(0)
        assert pc.plotSetup['ShowCertainPlotWindow'] == 0

    def test_set_script_mode_window(self, pc):
        pc.set_script_mode(1)
        assert pc.plotSetup['ShowCertainPlotWindow'] == 1


# --------------------------------------------------------------------------- #
# Graph config
# --------------------------------------------------------------------------- #

class TestGraphConfig:

    def test_set_graph_conf_key_enable(self, pc):
        pc.set_graph_conf_key('avgLevel', True)
        assert pc.graphConfig['avgLevel'] == 1

    def test_set_graph_conf_key_disable(self, pc):
        pc.set_graph_conf_key('level', False)
        assert pc.graphConfig['level'] == 0

    def test_set_graph_conf_key_unknown_key_ignored(self, pc):
        original = dict(pc.graphConfig)
        pc.set_graph_conf_key('nonExistentGraph', True)
        assert pc.graphConfig == original

    def test_get_active_graphs_default(self, pc):
        active = pc.get_active_graphs()
        assert 'level' in active
        assert 'normLevel' in active
        assert 'corrPhaseDiff' in active
        assert 'avgLevel' not in active

    def test_get_active_graphs_after_change(self, pc):
        pc.set_graph_conf_key('level', False)
        active = pc.get_active_graphs()
        assert 'level' not in active

    def test_get_active_phase_graphs_default(self, pc):
        phase = pc.get_active_phase_graphs()
        assert 'phaseDiff' in phase
        assert 'corrPhaseDiff' in phase
        assert 'level' not in phase

    def test_get_active_phase_graphs_empty_when_all_disabled(self, pc):
        for key in list(pc.graphConfig.keys()):
            if 'hase' in key:
                pc.set_graph_conf_key(key, False)
        assert pc.get_active_phase_graphs() == []


# --------------------------------------------------------------------------- #
# Slide graph selection
# --------------------------------------------------------------------------- #

class TestSlideGraphConf:

    def test_set_two_graph_conf1_prim(self, pc):
        pc.set_two_graph_conf1_prim('avgLevel')
        assert pc.twoGraphConf1['primGraph'] == 'avgLevel'

    def test_set_two_graph_conf1_sec(self, pc):
        pc.set_two_graph_conf1_sec('phaseDiff')
        assert pc.twoGraphConf1['secGraph'] == 'phaseDiff'

    def test_set_two_graph_conf2_prim(self, pc):
        pc.set_two_graph_conf2_prim('phaseDiff')
        assert pc.twoGraphConf2['primGraph'] == 'phaseDiff'

    def test_set_two_graph_conf2_sec(self, pc):
        pc.set_two_graph_conf2_sec('avgPhaseDiff')
        assert pc.twoGraphConf2['secGraph'] == 'avgPhaseDiff'

    def test_set_four_graph_confs(self, pc):
        pc.set_four_graph_conf1('normLevel')
        pc.set_four_graph_conf2('avgPhaseDiff')
        pc.set_four_graph_conf3('phaseDiff')
        assert pc.fourGraphConf1['graphType'] == 'normLevel'
        assert pc.fourGraphConf2['graphType'] == 'avgPhaseDiff'
        assert pc.fourGraphConf3['graphType'] == 'phaseDiff'

    def test_set_three_graph_confs(self, pc):
        pc.set_three_graph_conf1('phaseDiff')
        pc.set_three_graph_conf2('corrPhaseDiff')
        pc.set_three_graph_conf3('diffPhaseDiff')
        assert pc.threeGraphConf1['graphType'] == 'phaseDiff'
        assert pc.threeGraphConf2['graphType'] == 'corrPhaseDiff'
        assert pc.threeGraphConf3['graphType'] == 'diffPhaseDiff'

    def test_set_all_graphs_confs(self, pc):
        pc.set_all_graphs_conf1('normLevel')
        pc.set_all_graphs_conf2('phaseDiff')
        pc.set_all_graphs_conf3('avgPhaseDiff')
        assert pc.AllGraphsConf1['graphType'] == 'normLevel'
        assert pc.AllGraphsConf2['graphType'] == 'phaseDiff'
        assert pc.AllGraphsConf3['graphType'] == 'avgPhaseDiff'


# --------------------------------------------------------------------------- #
# Plot window config
# --------------------------------------------------------------------------- #

class TestPlotWindowConfig:

    def test_set_plot_window_input_mode_data(self, pc):
        pc.set_plot_window_input_mode(0)
        assert pc.plotWindowConfig['inputMode'] == 1

    def test_set_plot_window_input_mode_string(self, pc):
        pc.set_plot_window_input_mode(1)
        assert pc.plotWindowConfig['inputMode'] == 0

    def test_set_plot_window_string(self, pc):
        pc.set_plot_window_string('level_AntTyp0_TxAnt1')
        assert pc.plotWindowConfig['string'] == 'level_AntTyp0_TxAnt1'

    def test_set_plot_window_ant_type(self, pc):
        pc.set_plot_window_ant_type(158)
        assert pc.plotWindowConfig['antType'] == 158

    def test_set_plot_window_diag_num(self, pc):
        pc.set_plot_window_diag_num(7)
        assert pc.plotWindowConfig['diagramNum'] == 7

    def test_set_plot_window_rx_ch(self, pc):
        pc.set_plot_window_rx_ch(3)
        assert pc.plotWindowConfig['rxCh'] == 3

    def test_set_plot_window_graph(self, pc):
        pc.set_plot_window_graph('corrPhaseDiff')
        assert pc.plotWindowConfig['graph'] == 'corrPhaseDiff'

    def test_set_plot_window_all_graphs_mode_on(self, pc):
        pc.set_plot_window_all_graphs_mode(True)
        assert pc.plotWindowConfig['showPlotAllMode'] == 1

    def test_set_plot_window_all_graphs_mode_off(self, pc):
        pc.set_plot_window_all_graphs_mode(False)
        assert pc.plotWindowConfig['showPlotAllMode'] == 0


# --------------------------------------------------------------------------- #
# Slide list helpers
# --------------------------------------------------------------------------- #

class TestSlideListHelpers:

    def test_get_two_graph_setup_list(self, pc):
        lst = pc.get_two_graph_setup_list()
        assert len(lst) == 1
        assert lst[0] is pc.twoGraphConf1

    def test_get_three_graph_setup_list(self, pc):
        lst = pc.get_three_graph_setup_list()
        assert len(lst) == 2
        assert pc.threeGraphConf1 in lst

    def test_get_all_on_one_slide_list(self, pc):
        lst = pc.get_all_on_one_slide_list()
        assert len(lst) == 3
        assert lst[0] is pc.AllGraphsConf1
        assert lst[1] is pc.AllGraphsConf2
        assert lst[2] is pc.AllGraphsConf3


# --------------------------------------------------------------------------- #
# Hullkurven config
# --------------------------------------------------------------------------- #

class TestHullkurvenConfig:

    def test_hullkurven_data_conf_defaults(self, pc):
        assert pc.hullkurvenDataConf['AzDiag'] == 1
        assert pc.hullkurvenDataConf['ElDiag'] == 1
        assert pc.hullkurvenDataConf['minSigma'] == -10
        assert pc.hullkurvenDataConf['maxSigma'] == 10
        assert pc.hullkurvenDataConf['sigmaStep'] == 5
        assert pc.hullkurvenDataConf['reserveDb'] == 2
        assert pc.hullkurvenDataConf['patternLimitsMethod'] == 0
        assert pc.hullkurvenDataConf['minPhaseFactor'] == 5
        assert pc.hullkurvenDataConf['maxPhaseFactor'] == 5
        assert pc.hullkurvenDataConf['phaseFactorStep'] == 2

    def test_hullkurven_plot_setup_defaults(self, pc):
        assert pc.hullkurvenPlotSetup['xScaleSizeAuto'] == 0
        assert pc.hullkurvenPlotSetup['xScaleSizeAz'] == 90
        assert pc.hullkurvenPlotSetup['xScaleSizeEl'] == 45
        assert pc.hullkurvenPlotSetup['yLimitsAntTypeSeparately'] == 1

    def test_set_hullkurven_az_diag_true(self, pc):
        pc.set_hullkurven_az_diag(True)
        assert pc.hullkurvenDataConf['AzDiag'] == 1

    def test_set_hullkurven_az_diag_false(self, pc):
        pc.set_hullkurven_az_diag(False)
        assert pc.hullkurvenDataConf['AzDiag'] == 0

    def test_set_hullkurven_el_diag_true(self, pc):
        pc.set_hullkurven_el_diag(True)
        assert pc.hullkurvenDataConf['ElDiag'] == 1

    def test_set_hullkurven_el_diag_false(self, pc):
        pc.set_hullkurven_el_diag(False)
        assert pc.hullkurvenDataConf['ElDiag'] == 0

    def test_set_hullkurven_min_sigma(self, pc):
        pc.set_hullkurven_min_sigma(-5)
        assert pc.hullkurvenDataConf['minSigma'] == -5

    def test_set_hullkurven_max_sigma(self, pc):
        pc.set_hullkurven_max_sigma(15)
        assert pc.hullkurvenDataConf['maxSigma'] == 15

    def test_set_hullkurven_min_phase_factor(self, pc):
        pc.set_hullkurven_min_phase_factor(3)
        assert pc.hullkurvenDataConf['minPhaseFactor'] == 3

    def test_set_hullkurven_max_phase_factor(self, pc):
        pc.set_hullkurven_max_phase_factor(8)
        assert pc.hullkurvenDataConf['maxPhaseFactor'] == 8

    def test_set_hullkurven_pattern_method_sigma(self, pc):
        pc.set_hullkurven_pattern_method(0)
        assert pc.hullkurvenDataConf['patternLimitsMethod'] == 0

    def test_set_hullkurven_pattern_method_minmax(self, pc):
        pc.set_hullkurven_pattern_method(1)
        assert pc.hullkurvenDataConf['patternLimitsMethod'] == 1

    def test_set_hullkurven_x_scale_auto_on(self, pc):
        pc.set_hullkurven_x_scale_auto(True)
        assert pc.hullkurvenPlotSetup['xScaleSizeAuto'] == 1

    def test_set_hullkurven_x_scale_auto_off(self, pc):
        pc.set_hullkurven_x_scale_auto(False)
        assert pc.hullkurvenPlotSetup['xScaleSizeAuto'] == 0

    def test_set_hullkurven_x_scale_az(self, pc):
        pc.set_hullkurven_x_scale_az(60.0)
        assert pc.hullkurvenPlotSetup['xScaleSizeAz'] == 60.0

    def test_set_hullkurven_x_scale_el(self, pc):
        pc.set_hullkurven_x_scale_el(30.0)
        assert pc.hullkurvenPlotSetup['xScaleSizeEl'] == 30.0
