"""
PlotController — owns all plot configuration state (no Qt).

main.py Qt event handlers delegate state changes here; widget updates
(setChecked, setEnabled, addItems, etc.) remain in main.py.
"""

from __future__ import annotations


class PlotController:
    """Holds all plot configuration state and provides Qt-free setters/getters."""

    def __init__(self) -> None:
        # ------------------------------------------------------------------ #
        # Plot setup — matches AntennaSystemDiagrams.plotSetup defaults
        # ------------------------------------------------------------------ #
        self.plotSetup: dict = {
            'targetAngle': 1,
            'upsideDown': 0,
            'xScaleSizeAuto': 0,
            'xScaleSizeAz': 90.0,
            'xScaleSizeEl': 45.0,
            'idealPhaseDiff': 1,
            'SeparateRxCh': 1,
            'threeGraphLayout': 1,
            'allOnOneSlide': 1,
            'diffPhaseDiffScalingFactor': 1.5,
            'yLimitsAntTypeSeparately': 1,
            'imageDpi': 220,
            'nofSensorMeasToShow': 32,
            'ShowCertainPlotWindow': 0,
            'sortByMeasAngle': 0,
            'sensorMusterList': ['rf', 'dsp', 'PT', 'MA'],
            'useSensorMuster': 0,
            'graphsPerSlide': 1,
        }

        # ------------------------------------------------------------------ #
        # Graph config — which graph types are active
        # ------------------------------------------------------------------ #
        self.graphConfig: dict = {
            'level':           1,
            'avgLevel':        0,
            'normLevel':       1,
            'avgNormLevel':    0,
            'phaseDiff':       1,
            'avgPhaseDiff':    0,
            'diffPhaseDiff':   0,
            'avgDiffPhaseDiff': 0,
            'corrPhaseDiff':   1,
        }

        # ------------------------------------------------------------------ #
        # Chirp config
        # ------------------------------------------------------------------ #
        self.chirpConfig: dict = {
            'chirp0': 1,
            'chirp1': 0,
            'chirp2': 0,
            'chirp3': 0,
        }

        # ------------------------------------------------------------------ #
        # Diagram selection config
        # ------------------------------------------------------------------ #
        self.diagramConfig: dict = {
            'selectDiagrams': 0,
            'oddOrEven': 0,
            'lowerNumber': 0,
            'higherNumber': 7,
        }
        self.diagramConfigList: list = [1, 2, 3, 4]

        # Runtime accumulation lists — rebuilt on each evaluation run
        self.twoGraphSetupList:      list = []
        self.threeGraphSetupList:    list = []
        self.fourGraphSetupList:     list = []
        self.allOnOneSlideGraphList: list = []

        # ------------------------------------------------------------------ #
        # Slide layout confs — two/three/four-graph and all-on-one-slide
        # ------------------------------------------------------------------ #
        self.twoGraphConf1: dict  = {'primGraph': 'level',        'secGraph':   'normLevel'}
        self.twoGraphConf2: dict  = {'primGraph': 'corrPhaseDiff', 'secGraph':   'diffPhaseDiff'}

        self.threeGraphConf1: dict = {'graphType': 'corrPhaseDiff'}
        self.threeGraphConf2: dict = {'graphType': 'diffPhaseDiff'}
        self.threeGraphConf3: dict = {'graphType': 'phaseDiff'}

        self.fourGraphConf1: dict  = {'graphType': 'level'}
        self.fourGraphConf2: dict  = {'graphType': 'corrPhaseDiff'}
        self.fourGraphConf3: dict  = {'graphType': 'diffPhaseDiff'}

        self.AllGraphsConf1: dict  = {'graphType': 'level'}
        self.AllGraphsConf2: dict  = {'graphType': 'corrPhaseDiff'}
        self.AllGraphsConf3: dict  = {'graphType': 'diffPhaseDiff'}

        # ------------------------------------------------------------------ #
        # Plot window config (interactive / single-window mode)
        # ------------------------------------------------------------------ #
        self.plotWindowConfig: dict = {
            'inputMode': 1,
            'showPlotAllMode': 0,
            'string': '',
            'graph': 'level',
            'antType': 0,
            'diagramNum': 0,
            'rxCh': 0,
        }

    # ====================================================================== #
    # Image generation mode (Separate vs. Combined Rx channels)
    # ====================================================================== #

    def set_img_gen_mode(self, btn_id: int) -> None:
        """btn_id 0 = separate Rx channels, 1 = combined Rx channels."""
        if btn_id == 0:
            self.plotSetup['SeparateRxCh'] = 1
            self.plotSetup['threeGraphLayout'] = 1
        else:
            self.plotSetup['SeparateRxCh'] = 0
            self.plotSetup['threeGraphLayout'] = 0

    def set_three_graph_layout(self, enabled: bool) -> None:
        self.plotSetup['threeGraphLayout'] = 1 if enabled else 0

    # ====================================================================== #
    # Image DPI / scaling
    # ====================================================================== #

    def set_image_dpi(self, dpi: int) -> None:
        self.plotSetup['imageDpi'] = dpi

    def set_x_scale_auto(self, auto: bool) -> None:
        self.plotSetup['xScaleSizeAuto'] = 1 if auto else 0

    def set_x_scale_az(self, size: float) -> None:
        self.plotSetup['xScaleSizeAz'] = size

    def set_x_scale_el(self, size: float) -> None:
        self.plotSetup['xScaleSizeEl'] = size

    def set_y_limits_mode(self, btn_id: int) -> None:
        """btn_id 0 = separate per antenna type, 1 = common for all."""
        self.plotSetup['yLimitsAntTypeSeparately'] = 1 if btn_id == 0 else 0

    def set_diff_phase_diff_scaling(self, factor: float) -> None:
        self.plotSetup['diffPhaseDiffScalingFactor'] = factor

    # ====================================================================== #
    # Ideal phase difference curve
    # ====================================================================== #

    def set_ideal_phase_diff(self, enabled: bool) -> None:
        self.plotSetup['idealPhaseDiff'] = 1 if enabled else 0

    # ====================================================================== #
    # Sensor / slide count
    # ====================================================================== #

    def set_n_sensor_meas_to_show(self, n: int) -> None:
        self.plotSetup['nofSensorMeasToShow'] = n

    def set_all_on_one_slide(self, enabled: bool) -> None:
        self.plotSetup['allOnOneSlide'] = 1 if enabled else 0

    # ====================================================================== #
    # Script mode (batch vs. interactive window)
    # ====================================================================== #

    def set_script_mode(self, btn_id: int) -> None:
        """btn_id 0 = script/batch (no plot window), 1 = show plot window."""
        self.plotSetup['ShowCertainPlotWindow'] = 0 if btn_id == 0 else 1

    # ====================================================================== #
    # Graph config
    # ====================================================================== #

    def set_graph_conf_key(self, key: str, enabled: bool) -> None:
        """Enable or disable a single graph type."""
        if key in self.graphConfig:
            self.graphConfig[key] = 1 if enabled else 0

    def get_active_graphs(self) -> list[str]:
        """Return list of currently enabled graph type keys."""
        return [k for k, v in self.graphConfig.items() if v == 1]

    def get_active_phase_graphs(self) -> list[str]:
        """Return list of currently enabled graph types that contain phase data."""
        return [k for k, v in self.graphConfig.items() if v == 1 and 'hase' in k]

    # ====================================================================== #
    # Two-graph slide configuration
    # ====================================================================== #

    def set_two_graph_conf1_prim(self, graph: str) -> None:
        self.twoGraphConf1['primGraph'] = graph

    def set_two_graph_conf1_sec(self, graph: str) -> None:
        self.twoGraphConf1['secGraph'] = graph

    def set_two_graph_conf2_prim(self, graph: str) -> None:
        self.twoGraphConf2['primGraph'] = graph

    def set_two_graph_conf2_sec(self, graph: str) -> None:
        self.twoGraphConf2['secGraph'] = graph

    # ====================================================================== #
    # Four-graph slide configuration
    # ====================================================================== #

    def set_four_graph_conf1(self, graph: str) -> None:
        self.fourGraphConf1['graphType'] = graph

    def set_four_graph_conf2(self, graph: str) -> None:
        self.fourGraphConf2['graphType'] = graph

    def set_four_graph_conf3(self, graph: str) -> None:
        self.fourGraphConf3['graphType'] = graph

    # ====================================================================== #
    # Three-graph slide configuration
    # ====================================================================== #

    def set_three_graph_conf1(self, graph: str) -> None:
        self.threeGraphConf1['graphType'] = graph

    def set_three_graph_conf2(self, graph: str) -> None:
        self.threeGraphConf2['graphType'] = graph

    def set_three_graph_conf3(self, graph: str) -> None:
        self.threeGraphConf3['graphType'] = graph

    # ====================================================================== #
    # All-on-one-slide graph configuration
    # ====================================================================== #

    def set_all_graphs_conf1(self, graph: str) -> None:
        self.AllGraphsConf1['graphType'] = graph

    def set_all_graphs_conf2(self, graph: str) -> None:
        self.AllGraphsConf2['graphType'] = graph

    def set_all_graphs_conf3(self, graph: str) -> None:
        self.AllGraphsConf3['graphType'] = graph

    # ====================================================================== #
    # Plot window (interactive selection)
    # ====================================================================== #

    def set_plot_window_input_mode(self, btn_id: int) -> None:
        """btn_id 0 = data input mode, 1 = string input mode."""
        self.plotWindowConfig['inputMode'] = 1 if btn_id == 0 else 0

    def set_plot_window_string(self, s: str) -> None:
        self.plotWindowConfig['string'] = s

    def set_plot_window_ant_type(self, ant_type: int) -> None:
        self.plotWindowConfig['antType'] = ant_type

    def set_plot_window_diag_num(self, diag_num: int) -> None:
        self.plotWindowConfig['diagramNum'] = diag_num

    def set_plot_window_rx_ch(self, rx_ch: int) -> None:
        self.plotWindowConfig['rxCh'] = rx_ch

    def set_plot_window_graph(self, graph: str) -> None:
        self.plotWindowConfig['graph'] = graph

    def set_plot_window_all_graphs_mode(self, enabled: bool) -> None:
        self.plotWindowConfig['showPlotAllMode'] = 1 if enabled else 0

    # ====================================================================== #
    # Slide setup list helpers (used to build combo-box items and slide lists)
    # ====================================================================== #

    def get_two_graph_setup_list(self) -> list[dict]:
        """Return active two-graph slide configurations."""
        return [self.twoGraphConf1]

    def get_four_graph_setup_list(self) -> list[dict]:
        return []

    def get_three_graph_setup_list(self) -> list[dict]:
        return [self.threeGraphConf1, self.threeGraphConf3]

    def get_all_on_one_slide_list(self) -> list[dict]:
        return [self.AllGraphsConf1, self.AllGraphsConf2, self.AllGraphsConf3]

    # ====================================================================== #
    # Input setup
    # ====================================================================== #

    def set_target_angle(self, btn_id: int) -> None:
        """btn_id 0 = use target angle, 1 = use measured angle."""
        self.plotSetup['targetAngle'] = 1 if btn_id == 0 else 0

    def set_upside_down(self, btn_id: int) -> None:
        """btn_id 0 = normal orientation, 1 = upside down."""
        self.plotSetup['upsideDown'] = 1 if btn_id == 1 else 0

    def set_chirp_key(self, key: str, enabled: bool) -> None:
        if key in self.chirpConfig:
            self.chirpConfig[key] = 1 if enabled else 0

    def set_diagram_select_mode(self, btn_id: int) -> None:
        """btn_id 0 = all, 1 = by list, 2 = by range."""
        self.diagramConfig['selectDiagrams'] = btn_id

    def set_diagram_odd_even(self, btn_id: int) -> None:
        self.diagramConfig['oddOrEven'] = btn_id

    def set_sensor_muster_enabled(self, enabled: bool) -> None:
        self.plotSetup['useSensorMuster'] = 1 if enabled else 0
