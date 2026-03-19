"""Tests for ui/handlers handler modules (PST-65).

Each test builds a mock AppContext and calls the extracted handler function
directly — no real Qt required.  Handler modules are imported after the
minimal sys.modules patching needed for any top-level Qt imports.
"""
from __future__ import annotations

import os
import sys
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Path setup — mirrors conftest.py and main.py path initialisation
# ---------------------------------------------------------------------------
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _subdir in ["shared", "ui", "system_diagrams", "tx_diagrams", "antenna_patterns"]:
    _path = os.path.join(_root, _subdir)
    if _path not in sys.path:
        sys.path.insert(0, _path)

# parse_handlers imports ``from PySide6.QtWidgets import QTableWidgetItem`` at
# module level.  Mock PySide6 before importing it (no-op if already present).
_pyside_mock = MagicMock()
sys.modules.setdefault("PySide6", _pyside_mock)
sys.modules.setdefault("PySide6.QtWidgets", _pyside_mock.QtWidgets)
sys.modules.setdefault("PySide6.QtCore", _pyside_mock.QtCore)

# sys_diag_handlers / tx_ant_diag_handlers / ant_pat_handlers do NOT import Qt
# at module level (they use lazy imports inside functions), so they are safe to
# import here unconditionally.
from ui.handlers.sys_diag_handlers import (   # noqa: E402
    sys_diag_data_update_and_evaluation,
    sysDiagInputSetupAngleGroupClick,
    sysDiagInputSetupChirpClick,
    sysDiagInputSetupDiagConfigInputModeClick,
    sysDiagInputSetupDiagConfOddEvenClick,
    sysDiagInputSetupSensorOrientGroupClick,
    sysDiagPlotSetup3GraphLayoutImgClick,
    sysDiagPlotSetupGraphConfIdealCurveClick,
    sysDiagPlotSetupImgGenClick,
    sysDiagPlotSetupScalingAutoClick,
    sysDiagPlotSetupScalingYLimitsClick,
    sysDiagPlotSetupScriptModeGroupClick,
    sysDiagPlotWindowAllGraphsClick,
    sysDiagPlotWindowGraphTypeComboBoxClick,
    sysDiagPlotWindowInputModeClick,
    sysDiagSlideConfFourGraphComboBox1Click,
    sysDiagSlideConfFourGraphComboBox2Click,
    sysDiagSlideConfFourGraphComboBox3Click,
    sysDiagSlideConfGeneralAllGraphsSlideClick,
    sysDiagSlideConfGeneralAllSlidesComboBox1Click,
    sysDiagSlideConfGeneralAllSlidesComboBox2Click,
    sysDiagSlideConfGeneralAllSlidesComboBox3Click,
    sysDiagSlideConfThreeGraphComboBox1Click,
    sysDiagSlideConfThreeGraphComboBox2Click,
    sysDiagSlideConfThreeGraphComboBox3Click,
    sysDiagSlideConfTwoGraphComboBox11Click,
    sysDiagSlideConfTwoGraphComboBox12Click,
    sysDiagSlideConfTwoGraphComboBox21Click,
    sysDiagSlideConfTwoGraphComboBox22Click,
    sysDiagPlotWindowAllGraphsComboBox1Click,
    sysDiagPlotWindowAllGraphsComboBox2Click,
    sysDiagPlotWindowAllGraphsComboBox3Click,
)
from ui.handlers.tx_ant_diag_handlers import (  # noqa: E402
    txAntDiagInputSetupAngleGroupClick,
    txAntDiagInputSetupAzClick,
    txAntDiagInputSetupElClick,
    txAntDiagInputSetupSensorOrientGroupClick,
    txAntDiagPlotSetupScalingAutoClick,
    txAntDiagPlotSetupScalingNormGraphsClick,
    txAntDiagPlotSetupScalingOrigGraphsClick,
)
from ui.handlers.ant_pat_handlers import (  # noqa: E402
    antPatControl,
    antPatInputConfFileSearchClick,
    antPatInputNameIdentifierSelClick,
    antPatInputSetupAngleGroupClick,
    antPatInputSetupSensorOrientGroupClick,
    antPatInputSetupYAMLGroupClick,
    antPatTableDiagTypeInfoClick,
    antPatTableLEditParse,
    antPatTableUpsideDownInfoClick,
)

# ---------------------------------------------------------------------------
# Shared helper
# ---------------------------------------------------------------------------

def _make_ctx() -> MagicMock:
    """Return a minimal mock AppContext suitable for all handler tests."""
    ctx = MagicMock()
    # Give plc real dicts so handlers can mutate them and tests can assert
    ctx.plc.plotSetup = {}
    ctx.plc.chirpConfig = {}
    ctx.plc.diagramConfig = {}
    ctx.plc.graphConfig = {}
    ctx.plc.twoGraphConf1 = {}
    ctx.plc.twoGraphConf2 = {}
    ctx.plc.fourGraphConf1 = {}
    ctx.plc.fourGraphConf2 = {}
    ctx.plc.fourGraphConf3 = {}
    ctx.plc.threeGraphConf1 = {}
    ctx.plc.threeGraphConf2 = {}
    ctx.plc.threeGraphConf3 = {}
    ctx.plc.AllGraphsConf1 = {}
    ctx.plc.AllGraphsConf2 = {}
    ctx.plc.AllGraphsConf3 = {}
    ctx.plc.plotWindowConfig = {}
    return ctx


# ===========================================================================
# sys_diag_handlers — controller-delegation (simple) handlers
# ===========================================================================

class TestSysDiagSimple:

    def test_angle_group_click_delegates_id(self):
        ctx = _make_ctx()
        ctx.qt.sysDiagInputSetupAngleGroup.checkedId.return_value = 2
        sysDiagInputSetupAngleGroupClick(ctx)
        ctx.plc.set_target_angle.assert_called_once_with(2)

    def test_sensor_orient_group_click_delegates_id(self):
        ctx = _make_ctx()
        ctx.qt.sysDiagInputSetupSensorOrientGroup.checkedId.return_value = 1
        sysDiagInputSetupSensorOrientGroupClick(ctx)
        ctx.plc.set_upside_down.assert_called_once_with(1)

    def test_chirp_click_delegates_key_and_state(self):
        ctx = _make_ctx()
        ctx.qt.sysDiagInputSetupChirpGroup.id.return_value = 3
        ctx.qt.sysDiagInputSetupChirpGroup.button.return_value.isChecked.return_value = True
        sysDiagInputSetupChirpClick(ctx, MagicMock())
        ctx.plc.set_chirp_key.assert_called_once_with("chirp3", True)

    def test_diag_config_input_mode_click(self):
        ctx = _make_ctx()
        ctx.qt.sysDiagInputSetupDiagConfGroup.checkedId.return_value = 1
        sysDiagInputSetupDiagConfigInputModeClick(ctx)
        ctx.plc.set_diagram_select_mode.assert_called_once_with(1)

    def test_diag_odd_even_click(self):
        ctx = _make_ctx()
        ctx.qt.sysDiagInputSetupDiagConfOddEvenGroup.checkedId.return_value = 2
        sysDiagInputSetupDiagConfOddEvenClick(ctx)
        ctx.plc.set_diagram_odd_even.assert_called_once_with(2)

    def test_scaling_auto_click(self):
        ctx = _make_ctx()
        ctx.qt.sysDiagPlotSetupScalingAutoCheckBox.isChecked.return_value = True
        sysDiagPlotSetupScalingAutoClick(ctx)
        ctx.plc.set_x_scale_auto.assert_called_once_with(True)

    def test_y_limits_click(self):
        ctx = _make_ctx()
        ctx.qt.sysDiagPlotSetupScalingYLimitsGroup.checkedId.return_value = 0
        sysDiagPlotSetupScalingYLimitsClick(ctx)
        ctx.plc.set_y_limits_mode.assert_called_once_with(0)

    def test_ideal_curve_click_on(self):
        ctx = _make_ctx()
        ctx.qt.sysDiagPlotSetupGraphConfIdealCurveCheckBox.isChecked.return_value = True
        sysDiagPlotSetupGraphConfIdealCurveClick(ctx)
        ctx.plc.set_ideal_phase_diff.assert_called_once_with(True)

    def test_ideal_curve_click_off(self):
        ctx = _make_ctx()
        ctx.qt.sysDiagPlotSetupGraphConfIdealCurveCheckBox.isChecked.return_value = False
        sysDiagPlotSetupGraphConfIdealCurveClick(ctx)
        ctx.plc.set_ideal_phase_diff.assert_called_once_with(False)


class TestSysDiagComboHandlers:

    def test_two_graph_combo11(self):
        ctx = _make_ctx()
        ctx.qt.sysDiagSlideConfTwoGraphComboBox11.itemText.return_value = "level"
        sysDiagSlideConfTwoGraphComboBox11Click(ctx, 0)
        ctx.plc.set_two_graph_conf1_prim.assert_called_once_with("level")

    def test_two_graph_combo12(self):
        ctx = _make_ctx()
        ctx.qt.sysDiagSlideConfTwoGraphComboBox12.itemText.return_value = "normLevel"
        sysDiagSlideConfTwoGraphComboBox12Click(ctx, 1)
        ctx.plc.set_two_graph_conf1_sec.assert_called_once_with("normLevel")

    def test_two_graph_combo21(self):
        ctx = _make_ctx()
        ctx.qt.sysDiagSlideConfTwoGraphComboBox21.itemText.return_value = "corrPhaseDiff"
        sysDiagSlideConfTwoGraphComboBox21Click(ctx, 0)
        ctx.plc.set_two_graph_conf2_prim.assert_called_once_with("corrPhaseDiff")

    def test_two_graph_combo22(self):
        ctx = _make_ctx()
        ctx.qt.sysDiagSlideConfTwoGraphComboBox22.itemText.return_value = "diffPhaseDiff"
        sysDiagSlideConfTwoGraphComboBox22Click(ctx, 0)
        ctx.plc.set_two_graph_conf2_sec.assert_called_once_with("diffPhaseDiff")

    def test_four_graph_combo1(self):
        ctx = _make_ctx()
        ctx.qt.sysDiagSlideConfFourGraphComboBox1.itemText.return_value = "level"
        sysDiagSlideConfFourGraphComboBox1Click(ctx, 0)
        ctx.plc.set_four_graph_conf1.assert_called_once_with("level")

    def test_four_graph_combo2(self):
        ctx = _make_ctx()
        ctx.qt.sysDiagSlideConfFourGraphComboBox2.itemText.return_value = "corrPhaseDiff"
        sysDiagSlideConfFourGraphComboBox2Click(ctx, 0)
        ctx.plc.set_four_graph_conf2.assert_called_once_with("corrPhaseDiff")

    def test_four_graph_combo3(self):
        ctx = _make_ctx()
        ctx.qt.sysDiagSlideConfFourGraphComboBox3.itemText.return_value = "diffPhaseDiff"
        sysDiagSlideConfFourGraphComboBox3Click(ctx, 0)
        ctx.plc.set_four_graph_conf3.assert_called_once_with("diffPhaseDiff")

    def test_three_graph_combo1(self):
        ctx = _make_ctx()
        ctx.qt.sysDiagSlideConfThreeGraphComboBox1.itemText.return_value = "corrPhaseDiff"
        sysDiagSlideConfThreeGraphComboBox1Click(ctx, 0)
        ctx.plc.set_three_graph_conf1.assert_called_once_with("corrPhaseDiff")

    def test_three_graph_combo2(self):
        ctx = _make_ctx()
        ctx.qt.sysDiagSlideConfThreeGraphComboBox2.itemText.return_value = "diffPhaseDiff"
        sysDiagSlideConfThreeGraphComboBox2Click(ctx, 0)
        ctx.plc.set_three_graph_conf2.assert_called_once_with("diffPhaseDiff")

    def test_three_graph_combo3(self):
        ctx = _make_ctx()
        ctx.qt.sysDiagSlideConfThreeGraphComboBox3.itemText.return_value = "phaseDiff"
        sysDiagSlideConfThreeGraphComboBox3Click(ctx, 0)
        ctx.plc.set_three_graph_conf3.assert_called_once_with("phaseDiff")

    def test_all_slides_combo1(self):
        ctx = _make_ctx()
        ctx.qt.sysDiagSlideConfGeneralAllSlidesComboBox1.itemText.return_value = "level"
        sysDiagSlideConfGeneralAllSlidesComboBox1Click(ctx, 0)
        ctx.plc.set_all_graphs_conf1.assert_called_once_with("level")

    def test_all_slides_combo2(self):
        ctx = _make_ctx()
        ctx.qt.sysDiagSlideConfGeneralAllSlidesComboBox2.itemText.return_value = "corrPhaseDiff"
        sysDiagSlideConfGeneralAllSlidesComboBox2Click(ctx, 0)
        ctx.plc.set_all_graphs_conf2.assert_called_once_with("corrPhaseDiff")

    def test_all_slides_combo3(self):
        ctx = _make_ctx()
        ctx.qt.sysDiagSlideConfGeneralAllSlidesComboBox3.itemText.return_value = "diffPhaseDiff"
        sysDiagSlideConfGeneralAllSlidesComboBox3Click(ctx, 0)
        ctx.plc.set_all_graphs_conf3.assert_called_once_with("diffPhaseDiff")

    def test_plot_window_combo1(self):
        ctx = _make_ctx()
        ctx.qt.sysDiagPlotWindowAllGraphsComboBox1.itemText.return_value = "level"
        sysDiagPlotWindowAllGraphsComboBox1Click(ctx, 0)
        ctx.plc.set_all_graphs_conf1.assert_called_once_with("level")

    def test_plot_window_combo2(self):
        ctx = _make_ctx()
        ctx.qt.sysDiagPlotWindowAllGraphsComboBox2.itemText.return_value = "corrPhaseDiff"
        sysDiagPlotWindowAllGraphsComboBox2Click(ctx, 0)
        ctx.plc.set_all_graphs_conf2.assert_called_once_with("corrPhaseDiff")

    def test_plot_window_combo3(self):
        ctx = _make_ctx()
        ctx.qt.sysDiagPlotWindowAllGraphsComboBox3.itemText.return_value = "diffPhaseDiff"
        sysDiagPlotWindowAllGraphsComboBox3Click(ctx, 0)
        ctx.plc.set_all_graphs_conf3.assert_called_once_with("diffPhaseDiff")

    def test_plot_window_graph_type_combo(self):
        ctx = _make_ctx()
        ctx.qt.sysDiagPlotWindowGraphTypeComboBox.itemText.return_value = "normLevel"
        sysDiagPlotWindowGraphTypeComboBoxClick(ctx, 2)
        ctx.plc.set_plot_window_graph.assert_called_once_with("normLevel")


class TestSysDiagImgGenClick:

    def test_mode_0_enables_four_graph_frame(self):
        ctx = _make_ctx()
        ctx.qt.sysDiagPlotSetupImgGenGroup.checkedId.return_value = 0
        sysDiagPlotSetupImgGenClick(ctx)
        ctx.plc.set_img_gen_mode.assert_called_once_with(0)
        ctx.qt.sysDiagSlideConfFourGraphFrame.setEnabled.assert_called_with(True)

    def test_mode_1_disables_four_graph_frame(self):
        ctx = _make_ctx()
        ctx.qt.sysDiagPlotSetupImgGenGroup.checkedId.return_value = 1
        sysDiagPlotSetupImgGenClick(ctx)
        ctx.plc.set_img_gen_mode.assert_called_once_with(1)
        ctx.qt.sysDiagSlideConfFourGraphFrame.setEnabled.assert_called_with(False)


class TestSysDiag3GraphLayout:

    def test_enabled_sets_frame(self):
        ctx = _make_ctx()
        ctx.qt.sysDiagPlotSetup3GraphLayoutImgCheckBox.isChecked.return_value = 1
        sysDiagPlotSetup3GraphLayoutImgClick(ctx)
        ctx.plc.set_three_graph_layout.assert_called_once_with(1)
        ctx.qt.sysDiagSlideConfThreeGraphFrame.setEnabled.assert_called_with(True)

    def test_disabled_disables_frame(self):
        ctx = _make_ctx()
        ctx.qt.sysDiagPlotSetup3GraphLayoutImgCheckBox.isChecked.return_value = 0
        sysDiagPlotSetup3GraphLayoutImgClick(ctx)
        ctx.plc.set_three_graph_layout.assert_called_once_with(0)
        ctx.qt.sysDiagSlideConfThreeGraphFrame.setEnabled.assert_called_with(False)


class TestSysDiagAllOnOneSlide:

    def test_on_enables_all_combos(self):
        ctx = _make_ctx()
        ctx.qt.sysDiagSlideConfGeneralAllGraphsSlideCheckBox.isChecked.return_value = True
        sysDiagSlideConfGeneralAllGraphsSlideClick(ctx)
        ctx.plc.set_all_on_one_slide.assert_called_once_with(True)
        ctx.qt.sysDiagSlideConfGeneralAllSlidesComboBox1.setEnabled.assert_called_with(True)
        ctx.qt.sysDiagSlideConfGeneralAllSlidesComboBox2.setEnabled.assert_called_with(True)
        ctx.qt.sysDiagSlideConfGeneralAllSlidesComboBox3.setEnabled.assert_called_with(True)

    def test_off_disables_all_combos(self):
        ctx = _make_ctx()
        ctx.qt.sysDiagSlideConfGeneralAllGraphsSlideCheckBox.isChecked.return_value = False
        sysDiagSlideConfGeneralAllGraphsSlideClick(ctx)
        ctx.plc.set_all_on_one_slide.assert_called_once_with(False)
        ctx.qt.sysDiagSlideConfGeneralAllSlidesComboBox1.setEnabled.assert_called_with(False)


class TestSysDiagScriptMode:

    def test_mode_0_disables_plot_window(self):
        ctx = _make_ctx()
        ctx.qt.sysDiagPlotSetupScriptModeGroup.checkedId.return_value = 0
        sysDiagPlotSetupScriptModeGroupClick(ctx)
        ctx.plc.set_script_mode.assert_called_once_with(0)
        ctx.qt.sysDiagPlotWindowGroupBox.setEnabled.assert_called_with(False)
        ctx.qt.sysDiagSlideConfGroupBox.setEnabled.assert_called_with(True)

    def test_mode_1_enables_plot_window(self):
        ctx = _make_ctx()
        ctx.qt.sysDiagPlotSetupScriptModeGroup.checkedId.return_value = 1
        sysDiagPlotSetupScriptModeGroupClick(ctx)
        ctx.plc.set_script_mode.assert_called_once_with(1)
        ctx.qt.sysDiagPlotWindowGroupBox.setEnabled.assert_called_with(True)
        ctx.qt.sysDiagSlideConfGroupBox.setEnabled.assert_called_with(False)


class TestSysDiagPlotWindowInputMode:

    def test_mode_0_disables_ledit(self):
        ctx = _make_ctx()
        ctx.qt.sysDiagPlotWindowInputModeGroup.checkedId.return_value = 0
        sysDiagPlotWindowInputModeClick(ctx)
        ctx.qt.sysDiagPlotWindowInputModeLEdit.setEnabled.assert_called_with(False)

    def test_mode_1_enables_ledit(self):
        ctx = _make_ctx()
        ctx.qt.sysDiagPlotWindowInputModeGroup.checkedId.return_value = 1
        sysDiagPlotWindowInputModeClick(ctx)
        ctx.qt.sysDiagPlotWindowInputModeLEdit.setEnabled.assert_called_with(True)


class TestSysDiagPlotWindowAllGraphs:

    def test_on_enables_sub_checkboxes(self):
        ctx = _make_ctx()
        ctx.qt.sysDiagPlotWindowAllGraphsCheckBox.isChecked.return_value = True
        sysDiagPlotWindowAllGraphsClick(ctx)
        ctx.qt.sysDiagPlotWindowAllGraphsCheckBox1.setEnabled.assert_called_with(True)

    def test_off_disables_sub_checkboxes(self):
        ctx = _make_ctx()
        ctx.qt.sysDiagPlotWindowAllGraphsCheckBox.isChecked.return_value = False
        sysDiagPlotWindowAllGraphsClick(ctx)
        ctx.qt.sysDiagPlotWindowAllGraphsCheckBox1.setEnabled.assert_called_with(False)


# ---------------------------------------------------------------------------
# sysDiag evaluation orchestrator (PST-59)
# ---------------------------------------------------------------------------

def _eval_ctx() -> MagicMock:
    """Return a fully-configured ctx mock for the orchestrator."""
    ctx = _make_ctx()
    ctx.plc.plotSetup = {
        "useSensorMuster": 0,
        "sensorMusterList": [],
        "imageDpi": 220,
        "xScaleSizeAz": 90.0,
        "xScaleSizeEl": 45.0,
        "diffPhaseDiffScalingFactor": 1.5,
        "nofSensorMeasToShow": 32,
    }
    ctx.plc.diagramConfig = {"lowerNumber": 0, "higherNumber": 4}
    ctx.plc.plotWindowConfig = {"diagramNum": 0, "rxCh": 0, "antType": 0, "string": ""}
    ctx.pc.sysDiagParsedDataDict = {"parsedDataList": []}

    ctx.qt.sysDiagInputSetupDiagConfigDesListLEdit.text.return_value = "1,2"
    ctx.qt.sysDiagInputSetupDiagConfigDesRangeLowLEdit.text.return_value = "0"
    ctx.qt.sysDiagInputSetupDiagConfigDesRangeHighLEdit.text.return_value = "4"
    ctx.qt.sysDiagPlotSetupImageDpiLEdit.text.return_value = "220"
    ctx.qt.sysDiagPlotSetupScalingXScaleAzLEdit.text.return_value = "90"
    ctx.qt.sysDiagPlotSetupScalingXScaleElLEdit.text.return_value = "45"
    ctx.qt.sysDiagPlotSetupScalingDiffPhDiffLEdit.text.return_value = "1.5"
    ctx.qt.sysDiagPlotWindowDiagNumLEdit.text.return_value = "0"
    ctx.qt.sysDiagPlotWindowRxChLEdit.text.return_value = "0"
    ctx.qt.sysDiagPlotWindowAntTypLEdit.text.return_value = "0"
    ctx.qt.sysDiagPlotWindowInputModeLEdit.text.return_value = ""
    ctx.qt.sysDiagSlideConfGeneralSensorNumSlideLEdit.text.return_value = "32"
    ctx.qt.sysDiagPlotSetupScriptModeGroup.checkedId.return_value = 0

    for name in (
        "sysDiagSlideConfTwoGraphCheckBox1",
        "sysDiagSlideConfTwoGraphCheckBox2",
        "sysDiagSlideConfFourGraphCheckBox1",
        "sysDiagSlideConfFourGraphCheckBox2",
        "sysDiagSlideConfFourGraphCheckBox3",
        "sysDiagSlideConfThreeGraphCheckBox1",
        "sysDiagSlideConfThreeGraphCheckBox2",
        "sysDiagSlideConfThreeGraphCheckBox3",
        "sysDiagSlideConfGeneralAllSlidesCheckBox1",
        "sysDiagSlideConfGeneralAllSlidesCheckBox2",
        "sysDiagSlideConfGeneralAllSlidesCheckBox3",
    ):
        getattr(ctx.qt, name).isChecked.return_value = False

    return ctx


class TestSysDiagEvalOrchestrator:

    def test_calls_start_data_evaluation(self):
        ctx = _eval_ctx()
        mock_asd = MagicMock()
        with patch.dict(sys.modules, {"AntennaSystemDiagrams": mock_asd}):
            sys_diag_data_update_and_evaluation(ctx)
        mock_asd.start_data_evaluation.assert_called_once()

    def test_diagram_list_parsed_correctly(self):
        ctx = _eval_ctx()
        ctx.qt.sysDiagInputSetupDiagConfigDesListLEdit.text.return_value = "1,2,3"
        mock_asd = MagicMock()
        captured = []

        def _capture(*args, **kwargs):
            captured.append(args[9])  # diagramConfigList is 10th arg (index 9)

        mock_asd.start_data_evaluation.side_effect = _capture
        with patch.dict(sys.modules, {"AntennaSystemDiagrams": mock_asd}):
            sys_diag_data_update_and_evaluation(ctx)
        assert captured[0] == [1, 2, 3]

    def test_two_graph_conf_included_when_checkbox_checked(self):
        ctx = _eval_ctx()
        ctx.qt.sysDiagSlideConfTwoGraphCheckBox1.isChecked.return_value = True
        mock_asd = MagicMock()
        captured = []

        def _capture(*args, **kwargs):
            captured.append(args[5])  # twoGraphSetupList is 6th arg (index 5)

        mock_asd.start_data_evaluation.side_effect = _capture
        with patch.dict(sys.modules, {"AntennaSystemDiagrams": mock_asd}):
            sys_diag_data_update_and_evaluation(ctx)
        assert ctx.plc.twoGraphConf1 in captured[0]

    def test_sensor_muster_list_populated(self):
        ctx = _eval_ctx()
        ctx.plc.plotSetup["useSensorMuster"] = 1
        ctx.qt.parseProtSensorMusterLEdit.text.return_value = "A B C"
        mock_asd = MagicMock()
        with patch.dict(sys.modules, {"AntennaSystemDiagrams": mock_asd}):
            sys_diag_data_update_and_evaluation(ctx)
        assert ctx.plc.plotSetup["sensorMusterList"] == ["A", "B", "C"]


# ===========================================================================
# tx_ant_diag_handlers  (lazy-import: patch TxAntDiagrams in sys.modules)
# ===========================================================================

def _mock_tx() -> MagicMock:
    m = MagicMock()
    m.plotSetup = {
        "targetAngle": 1, "upsideDown": 0,
        "AzDiag": 1, "ElDiag": 0,
        "xScaleSizeAuto": 0, "plotOrigGraphs": 1, "plotNormGraphs": 1,
    }
    m.graphConfig = {}
    return m


class TestTxAntDiagHandlers:

    def test_angle_click_mode_0_sets_target_1(self):
        ctx = _make_ctx()
        ctx.qt.txAntDiagInputSetupAngleGroup.checkedId.return_value = 0
        mock_tx = _mock_tx()
        with patch.dict(sys.modules, {"TxAntDiagrams": mock_tx}):
            txAntDiagInputSetupAngleGroupClick(ctx)
        assert mock_tx.plotSetup["targetAngle"] == 1

    def test_angle_click_mode_1_sets_target_0(self):
        ctx = _make_ctx()
        ctx.qt.txAntDiagInputSetupAngleGroup.checkedId.return_value = 1
        mock_tx = _mock_tx()
        with patch.dict(sys.modules, {"TxAntDiagrams": mock_tx}):
            txAntDiagInputSetupAngleGroupClick(ctx)
        assert mock_tx.plotSetup["targetAngle"] == 0

    def test_sensor_orient_mode_0_sets_upside_down_0(self):
        ctx = _make_ctx()
        ctx.qt.txAntDiagInputSetupSensorOrientGroup.checkedId.return_value = 0
        mock_tx = _mock_tx()
        with patch.dict(sys.modules, {"TxAntDiagrams": mock_tx}):
            txAntDiagInputSetupSensorOrientGroupClick(ctx)
        assert mock_tx.plotSetup["upsideDown"] == 0

    def test_sensor_orient_mode_1_sets_upside_down_1(self):
        ctx = _make_ctx()
        ctx.qt.txAntDiagInputSetupSensorOrientGroup.checkedId.return_value = 1
        mock_tx = _mock_tx()
        with patch.dict(sys.modules, {"TxAntDiagrams": mock_tx}):
            txAntDiagInputSetupSensorOrientGroupClick(ctx)
        assert mock_tx.plotSetup["upsideDown"] == 1

    def test_az_click_checked_sets_1(self):
        ctx = _make_ctx()
        ctx.qt.txAntDiagInputSetupAzCheckBox.isChecked.return_value = True
        mock_tx = _mock_tx()
        with patch.dict(sys.modules, {"TxAntDiagrams": mock_tx}):
            txAntDiagInputSetupAzClick(ctx)
        assert mock_tx.plotSetup["AzDiag"] == 1

    def test_az_click_unchecked_sets_0(self):
        ctx = _make_ctx()
        ctx.qt.txAntDiagInputSetupAzCheckBox.isChecked.return_value = False
        mock_tx = _mock_tx()
        with patch.dict(sys.modules, {"TxAntDiagrams": mock_tx}):
            txAntDiagInputSetupAzClick(ctx)
        assert mock_tx.plotSetup["AzDiag"] == 0

    def test_el_click_checked_sets_1(self):
        ctx = _make_ctx()
        ctx.qt.txAntDiagInputSetupElCheckBox.isChecked.return_value = True
        mock_tx = _mock_tx()
        with patch.dict(sys.modules, {"TxAntDiagrams": mock_tx}):
            txAntDiagInputSetupElClick(ctx)
        assert mock_tx.plotSetup["ElDiag"] == 1

    def test_el_click_unchecked_sets_0(self):
        ctx = _make_ctx()
        ctx.qt.txAntDiagInputSetupElCheckBox.isChecked.return_value = False
        mock_tx = _mock_tx()
        with patch.dict(sys.modules, {"TxAntDiagrams": mock_tx}):
            txAntDiagInputSetupElClick(ctx)
        assert mock_tx.plotSetup["ElDiag"] == 0

    def test_scaling_auto_on(self):
        ctx = _make_ctx()
        ctx.qt.txAntDiagPlotSetupScalingAutoCheckBox.isChecked.return_value = True
        mock_tx = _mock_tx()
        with patch.dict(sys.modules, {"TxAntDiagrams": mock_tx}):
            txAntDiagPlotSetupScalingAutoClick(ctx)
        assert mock_tx.plotSetup["xScaleSizeAuto"] == 1

    def test_scaling_auto_off(self):
        ctx = _make_ctx()
        ctx.qt.txAntDiagPlotSetupScalingAutoCheckBox.isChecked.return_value = False
        mock_tx = _mock_tx()
        with patch.dict(sys.modules, {"TxAntDiagrams": mock_tx}):
            txAntDiagPlotSetupScalingAutoClick(ctx)
        assert mock_tx.plotSetup["xScaleSizeAuto"] == 0

    def test_orig_graphs_off(self):
        ctx = _make_ctx()
        ctx.qt.txAntDiagPlotSetupScalingOrigGraphsCheckBox.isChecked.return_value = False
        mock_tx = _mock_tx()
        with patch.dict(sys.modules, {"TxAntDiagrams": mock_tx}):
            txAntDiagPlotSetupScalingOrigGraphsClick(ctx)
        assert mock_tx.plotSetup["plotOrigGraphs"] == 0

    def test_norm_graphs_off(self):
        ctx = _make_ctx()
        ctx.qt.txAntDiagPlotSetupScalingNormGraphsCheckBox.isChecked.return_value = False
        mock_tx = _mock_tx()
        with patch.dict(sys.modules, {"TxAntDiagrams": mock_tx}):
            txAntDiagPlotSetupScalingNormGraphsClick(ctx)
        assert mock_tx.plotSetup["plotNormGraphs"] == 0


# ===========================================================================
# ant_pat_handlers — pure logic + mock antpat_v5_main_v3
# ===========================================================================

class TestAntPatTableLEditParse:

    def test_simple_ints(self):
        assert antPatTableLEditParse("0,1,2,3") == [0, 1, 2, 3]

    def test_deduplicates_preserving_order(self):
        assert antPatTableLEditParse("3,1,2,1") == [3, 1, 2]

    def test_ignores_non_integer_tokens(self):
        assert antPatTableLEditParse("0,abc,2") == [0, 2]

    def test_empty_string(self):
        assert antPatTableLEditParse("") == []

    def test_strips_empty_chunks_from_trailing_commas(self):
        assert antPatTableLEditParse(",0,1,") == [0, 1]

    def test_single_value(self):
        assert antPatTableLEditParse("5") == [5]


def _mock_ap() -> MagicMock:
    m = MagicMock()
    m.conf0 = {
        "targetAngle": 1,
        "upsideDown": 0,
        "diagTypeInfo": 1,
        "upsideDownInfo": 1,
    }
    m.chirpConfig = {"chirp0": 1, "chirp1": 0, "chirp2": 0, "chirp3": 0}
    return m


class TestAntPatAngleOrient:

    def test_angle_mode_0_sets_target_1(self):
        ctx = _make_ctx()
        ctx.qt.antPatInputConfAngleGroup.checkedId.return_value = 0
        mock_ap = _mock_ap()
        with patch.dict(sys.modules, {"antpat_v5_main_v3": mock_ap}):
            antPatInputSetupAngleGroupClick(ctx)
        assert mock_ap.conf0["targetAngle"] == 1

    def test_angle_mode_1_sets_target_0(self):
        ctx = _make_ctx()
        ctx.qt.antPatInputConfAngleGroup.checkedId.return_value = 1
        mock_ap = _mock_ap()
        with patch.dict(sys.modules, {"antpat_v5_main_v3": mock_ap}):
            antPatInputSetupAngleGroupClick(ctx)
        assert mock_ap.conf0["targetAngle"] == 0

    def test_orient_mode_0_sets_upside_down_0(self):
        ctx = _make_ctx()
        ctx.qt.antPatInputConfSensorOrientGroup.checkedId.return_value = 0
        mock_ap = _mock_ap()
        with patch.dict(sys.modules, {"antpat_v5_main_v3": mock_ap}):
            antPatInputSetupSensorOrientGroupClick(ctx)
        assert mock_ap.conf0["upsideDown"] == 0

    def test_orient_mode_1_sets_upside_down_1(self):
        ctx = _make_ctx()
        ctx.qt.antPatInputConfSensorOrientGroup.checkedId.return_value = 1
        mock_ap = _mock_ap()
        with patch.dict(sys.modules, {"antpat_v5_main_v3": mock_ap}):
            antPatInputSetupSensorOrientGroupClick(ctx)
        assert mock_ap.conf0["upsideDown"] == 1


class TestAntPatCheckboxHandlers:

    def test_file_search_checked_enables_info_boxes(self):
        ctx = _make_ctx()
        ctx.qt.antPatInputConfFileSearchCheckBox.isChecked.return_value = True
        antPatInputConfFileSearchClick(ctx)
        ctx.qt.antPatTableUpsideDownInfoCheckBox.setEnabled.assert_called_with(True)
        ctx.qt.antPatTableDiagTypeInfoCheckBox.setEnabled.assert_called_with(True)

    def test_file_search_unchecked_disables_info_boxes(self):
        ctx = _make_ctx()
        ctx.qt.antPatInputConfFileSearchCheckBox.isChecked.return_value = False
        antPatInputConfFileSearchClick(ctx)
        ctx.qt.antPatTableUpsideDownInfoCheckBox.setEnabled.assert_called_with(False)
        ctx.qt.antPatTableDiagTypeInfoCheckBox.setEnabled.assert_called_with(False)

    def test_name_id_sel_checked_enables_header_fields(self):
        ctx = _make_ctx()
        ctx.qt.antPatInputNameIdentifierSelCheckBox.isChecked.return_value = True
        antPatInputNameIdentifierSelClick(ctx)
        ctx.qt.antPatHeaderNameLEdit.setEnabled.assert_called_with(True)
        ctx.qt.antPatHeaderIdentifierLEdit.setEnabled.assert_called_with(True)

    def test_name_id_sel_unchecked_disables_header_fields(self):
        ctx = _make_ctx()
        ctx.qt.antPatInputNameIdentifierSelCheckBox.isChecked.return_value = False
        antPatInputNameIdentifierSelClick(ctx)
        ctx.qt.antPatHeaderNameLEdit.setEnabled.assert_called_with(False)
        ctx.qt.antPatHeaderIdentifierLEdit.setEnabled.assert_called_with(False)

    def test_diag_type_info_on(self):
        ctx = _make_ctx()
        ctx.qt.antPatTableDiagTypeInfoCheckBox.isChecked.return_value = True
        mock_ap = _mock_ap()
        with patch.dict(sys.modules, {"antpat_v5_main_v3": mock_ap}):
            antPatTableDiagTypeInfoClick(ctx)
        assert mock_ap.conf0["diagTypeInfo"] == 1

    def test_diag_type_info_off(self):
        ctx = _make_ctx()
        ctx.qt.antPatTableDiagTypeInfoCheckBox.isChecked.return_value = False
        mock_ap = _mock_ap()
        with patch.dict(sys.modules, {"antpat_v5_main_v3": mock_ap}):
            antPatTableDiagTypeInfoClick(ctx)
        assert mock_ap.conf0["diagTypeInfo"] == 0

    def test_upside_down_info_on(self):
        ctx = _make_ctx()
        ctx.qt.antPatTableUpsideDownInfoCheckBox.isChecked.return_value = True
        mock_ap = _mock_ap()
        with patch.dict(sys.modules, {"antpat_v5_main_v3": mock_ap}):
            antPatTableUpsideDownInfoClick(ctx)
        assert mock_ap.conf0["upsideDownInfo"] == 1

    def test_upside_down_info_off(self):
        ctx = _make_ctx()
        ctx.qt.antPatTableUpsideDownInfoCheckBox.isChecked.return_value = False
        mock_ap = _mock_ap()
        with patch.dict(sys.modules, {"antpat_v5_main_v3": mock_ap}):
            antPatTableUpsideDownInfoClick(ctx)
        assert mock_ap.conf0["upsideDownInfo"] == 0


class TestAntPatYAMLGroupClick:

    def test_version_0_json(self):
        ctx = _make_ctx()
        ctx.qt.antPatInputConfYAMLGroup.checkedId.return_value = 0
        antPatInputSetupYAMLGroupClick(ctx)
        assert antPatControl["version"] == 0

    def test_version_1_yaml_v1(self):
        ctx = _make_ctx()
        ctx.qt.antPatInputConfYAMLGroup.checkedId.return_value = 1
        antPatInputSetupYAMLGroupClick(ctx)
        assert antPatControl["version"] == 1

    def test_version_2_yaml_v2(self):
        ctx = _make_ctx()
        ctx.qt.antPatInputConfYAMLGroup.checkedId.return_value = 2
        antPatInputSetupYAMLGroupClick(ctx)
        assert antPatControl["version"] == 2
