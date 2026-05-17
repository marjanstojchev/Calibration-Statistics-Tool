"""System-Diagrams tab signal handlers  (PST-56).

All handler functions previously defined at module level in main.py under
the "##System Diagrams" section.

``wire(ctx)`` connects every Qt signal to its handler and performs the
same widget-initialisation that used to run at import time in main.py.
"""
from __future__ import annotations

import copy
import threading
from typing import TYPE_CHECKING

from shared import safeparse as sp

if TYPE_CHECKING:  # pragma: no cover
    from ui.handlers.app_context import AppContext

import logconfig

parseDataLog = logconfig.mainLoadDataLogger.logger


def _resolve_sys_diag_parsed_data(ctx: "AppContext") -> list:
    """Return the best available parsed PTU2 list for system-diagram workflows."""
    primary = ctx.pc.sysDiagParsedDataDict.get("parsedDataList", [])
    if primary:
        return list(primary)

    # Fallback for cases where PTU2 was parsed via the separate flow and
    # the primary sys-diag list was not synchronised yet.
    fallback = ctx.pc.separatePtu2ParsedDataDict.get("parsedDataList", [])
    if fallback:
        parseDataLog.warning(
            "sysDiagParsedDataDict is empty; using separatePtu2ParsedDataDict fallback (%d entries).",
            len(fallback),
        )
        return list(fallback)

    parseDataLog.warning("No parsed PTU2 data available for System Diagrams.")
    return []


# ---------------------------------------------------------------------------
# Input Setup — angle / orientation / chirp / diagram config
# ---------------------------------------------------------------------------

def sysDiagInputSetupAngleGroupClick(ctx: "AppContext") -> None:
    btnId = ctx.qt.sysDiagInputSetupAngleGroup.checkedId()
    ctx.plc.set_target_angle(btnId)
    parseDataLog.debug("plotSetup: " + str(ctx.plc.plotSetup))


def sysDiagInputSetupSensorOrientGroupClick(ctx: "AppContext") -> None:
    btnId = ctx.qt.sysDiagInputSetupSensorOrientGroup.checkedId()
    ctx.plc.set_upside_down(btnId)
    parseDataLog.debug("plotSetup: " + str(ctx.plc.plotSetup))


def sysDiagInputSetupChirpClick(ctx: "AppContext", btn) -> None:
    btnId   = ctx.qt.sysDiagInputSetupChirpGroup.id(btn)
    chBox   = ctx.qt.sysDiagInputSetupChirpGroup.button(btnId)
    state   = chBox.isChecked()
    dictKey = "chirp" + str(btnId)
    ctx.plc.set_chirp_key(dictKey, state)
    parseDataLog.debug("chirpConfig: " + str(ctx.plc.chirpConfig))


def sysDiagInputSetupDiagConfigInputModeClick(ctx: "AppContext") -> None:
    btnId = ctx.qt.sysDiagInputSetupDiagConfGroup.checkedId()
    ctx.plc.set_diagram_select_mode(btnId)
    parseDataLog.debug("diagramConfig: " + str(ctx.plc.diagramConfig))


def sysDiagInputSetupDiagConfOddEvenClick(ctx: "AppContext") -> None:
    btnId = ctx.qt.sysDiagInputSetupDiagConfOddEvenGroup.checkedId()
    ctx.plc.set_diagram_odd_even(btnId)
    parseDataLog.debug("diagramConfig: " + str(ctx.plc.diagramConfig))


# ---------------------------------------------------------------------------
# Plot Setup — image gen mode
# ---------------------------------------------------------------------------

def sysDiagPlotSetupImgGenClick(ctx: "AppContext") -> None:
    btnId = ctx.qt.sysDiagPlotSetupImgGenGroup.checkedId()
    ctx.plc.set_img_gen_mode(btnId)
    if btnId == 0:
        ctx.qt.sysDiagSlideConfTwoGraphCheckBox1.setChecked(False)
        ctx.qt.sysDiagSlideConfTwoGraphCheckBox2.setChecked(False)
        ctx.qt.sysDiagSlideConfFourGraphFrame.setEnabled(True)
        ctx.qt.sysDiagPlotSetup3GraphLayoutImgCheckBox.setChecked(True)
        ctx.qt.sysDiagPlotSetup3GraphLayoutImgCheckBox.setEnabled(True)
        ctx.qt.sysDiagSlideConfThreeGraphFrame.setEnabled(True)
        ctx.qt.sysDiagSlideConfThreeGraphCheckBox1.setChecked(True)
        ctx.qt.sysDiagSlideConfThreeGraphCheckBox2.setChecked(True)
        ctx.qt.sysDiagSlideConfThreeGraphCheckBox3.setChecked(False)
        ctx.qt.sysDiagSlideConfFourGraphCheckBox1.setChecked(True)
        ctx.qt.sysDiagSlideConfFourGraphCheckBox2.setChecked(False)
        ctx.qt.sysDiagSlideConfFourGraphCheckBox3.setChecked(False)
        parseDataLog.debug("plotSetup: " + str(ctx.plc.plotSetup))
    elif btnId == 1:
        ctx.qt.sysDiagSlideConfTwoGraphCheckBox1.setChecked(True)
        ctx.qt.sysDiagSlideConfTwoGraphCheckBox2.setChecked(True)
        ctx.qt.sysDiagSlideConfFourGraphFrame.setEnabled(False)
        ctx.qt.sysDiagPlotSetup3GraphLayoutImgCheckBox.setChecked(False)
        ctx.qt.sysDiagPlotSetup3GraphLayoutImgCheckBox.setEnabled(False)
        ctx.qt.sysDiagSlideConfThreeGraphFrame.setEnabled(False)
        ctx.qt.sysDiagSlideConfThreeGraphCheckBox1.setChecked(False)
        ctx.qt.sysDiagSlideConfThreeGraphCheckBox2.setChecked(False)
        ctx.qt.sysDiagSlideConfThreeGraphCheckBox3.setChecked(False)
        ctx.qt.sysDiagSlideConfFourGraphCheckBox1.setChecked(False)
        ctx.qt.sysDiagSlideConfFourGraphCheckBox2.setChecked(False)
        ctx.qt.sysDiagSlideConfFourGraphCheckBox3.setChecked(False)
        parseDataLog.debug("plotSetup: " + str(ctx.plc.plotSetup))


def sysDiagPlotSetup3GraphLayoutImgClick(ctx: "AppContext") -> None:
    state = ctx.qt.sysDiagPlotSetup3GraphLayoutImgCheckBox.isChecked()
    ctx.plc.set_three_graph_layout(state)
    if state == 1:
        ctx.qt.sysDiagSlideConfThreeGraphFrame.setEnabled(True)
        ctx.qt.sysDiagSlideConfThreeGraphCheckBox1.setChecked(True)
        ctx.qt.sysDiagSlideConfThreeGraphCheckBox2.setChecked(True)
        ctx.qt.sysDiagSlideConfThreeGraphCheckBox3.setChecked(False)
        ctx.qt.sysDiagSlideConfTwoGraphCheckBox2.setChecked(False)
    else:
        ctx.qt.sysDiagSlideConfThreeGraphFrame.setEnabled(False)
        ctx.qt.sysDiagSlideConfThreeGraphCheckBox1.setChecked(False)
        ctx.qt.sysDiagSlideConfThreeGraphCheckBox2.setChecked(False)
        ctx.qt.sysDiagSlideConfThreeGraphCheckBox3.setChecked(False)
        ctx.qt.sysDiagSlideConfTwoGraphCheckBox2.setChecked(True)
    parseDataLog.debug("plotSetup: " + str(ctx.plc.plotSetup))


def sysDiagPlotSetupScalingAutoClick(ctx: "AppContext") -> None:
    state = ctx.qt.sysDiagPlotSetupScalingAutoCheckBox.isChecked()
    ctx.plc.set_x_scale_auto(state)
    parseDataLog.debug("plotSetup: " + str(ctx.plc.plotSetup))


def sysDiagPlotSetupScalingYLimitsClick(ctx: "AppContext") -> None:
    btnId = ctx.qt.sysDiagPlotSetupScalingYLimitsGroup.checkedId()
    ctx.plc.set_y_limits_mode(btnId)
    parseDataLog.debug("plotSetup: " + str(ctx.plc.plotSetup))


def sysDiagPlotSetupGraphConfIdealCurveClick(ctx: "AppContext") -> None:
    state = ctx.qt.sysDiagPlotSetupGraphConfIdealCurveCheckBox.isChecked()
    ctx.plc.set_ideal_phase_diff(state)
    parseDataLog.debug("plotSetup: " + str(ctx.plc.plotSetup))


def sysDiagPlotSetupGraphConfClick(ctx: "AppContext", btn) -> None:
    i      = 0
    setKey = ""
    state  = 0
    btnId  = ctx.qt.sysDiagPlotSetupGraphConfGroup.id(btn)
    for key in ctx.plc.graphConfig:
        if i == btnId:
            chBox  = ctx.qt.sysDiagPlotSetupGraphConfGroup.button(btnId)
            state  = chBox.isChecked()
            setKey = key
            break
        i += 1
    ctx.plc.set_graph_conf_key(setKey, state)

    sysDiagSlideConfComboAddItems(ctx, ctx.qt.sysDiagSlideConfTwoGraphComboBox11)
    sysDiagSlideConfComboAddItems(ctx, ctx.qt.sysDiagSlideConfTwoGraphComboBox12)
    sysDiagSlideConfComboAddItems(ctx, ctx.qt.sysDiagSlideConfTwoGraphComboBox21)
    sysDiagSlideConfComboAddItems(ctx, ctx.qt.sysDiagSlideConfTwoGraphComboBox22)
    sysDiagSlideConfComboAddItems(ctx, ctx.qt.sysDiagSlideConfFourGraphComboBox1)
    sysDiagSlideConfComboAddItems(ctx, ctx.qt.sysDiagSlideConfFourGraphComboBox2)
    sysDiagSlideConfComboAddItems(ctx, ctx.qt.sysDiagSlideConfFourGraphComboBox3)
    sysDiagSlideConfThreeGraphComboAddItems(ctx, ctx.qt.sysDiagSlideConfThreeGraphComboBox1)
    sysDiagSlideConfThreeGraphComboAddItems(ctx, ctx.qt.sysDiagSlideConfThreeGraphComboBox2)
    sysDiagSlideConfThreeGraphComboAddItems(ctx, ctx.qt.sysDiagSlideConfThreeGraphComboBox3)
    parseDataLog.debug("graphConfig: " + str(ctx.plc.graphConfig))


# ---------------------------------------------------------------------------
# Slide conf — combo helpers
# ---------------------------------------------------------------------------

def sysDiagSlideConfComboAddItems(ctx: "AppContext", comboBox) -> None:
    comboBox.clear()
    comboBox.addItems([k for k, v in ctx.plc.graphConfig.items() if v == 1])


def sysDiagSlideConfThreeGraphComboAddItems(ctx: "AppContext", comboBox) -> None:
    comboBox.clear()
    comboBox.addItems([k for k, v in ctx.plc.graphConfig.items() if v == 1 and "hase" in k])


def sysDiagSlideConfTwoAndFourGraphComboSetCurrentItem(comboBox, textKey: str) -> None:
    for idx in range(comboBox.count()):
        if comboBox.itemText(idx) == textKey:
            comboBox.setCurrentIndex(idx)
            return


# ---------------------------------------------------------------------------
# Slide conf — two-graph combos
# ---------------------------------------------------------------------------

def sysDiagSlideConfTwoGraphComboBox11Click(ctx: "AppContext", idx: int) -> None:
    ctx.plc.set_two_graph_conf1_prim(ctx.qt.sysDiagSlideConfTwoGraphComboBox11.itemText(idx))
    parseDataLog.debug("twoGraphConf1: " + str(ctx.plc.twoGraphConf1))


def sysDiagSlideConfTwoGraphComboBox12Click(ctx: "AppContext", idx: int) -> None:
    ctx.plc.set_two_graph_conf1_sec(ctx.qt.sysDiagSlideConfTwoGraphComboBox12.itemText(idx))
    parseDataLog.debug("twoGraphConf1: " + str(ctx.plc.twoGraphConf1))


def sysDiagSlideConfTwoGraphComboBox21Click(ctx: "AppContext", idx: int) -> None:
    ctx.plc.set_two_graph_conf2_prim(ctx.qt.sysDiagSlideConfTwoGraphComboBox21.itemText(idx))
    parseDataLog.debug("twoGraphConf2: " + str(ctx.plc.twoGraphConf2))


def sysDiagSlideConfTwoGraphComboBox22Click(ctx: "AppContext", idx: int) -> None:
    ctx.plc.set_two_graph_conf2_sec(ctx.qt.sysDiagSlideConfTwoGraphComboBox22.itemText(idx))
    parseDataLog.debug("twoGraphConf2: " + str(ctx.plc.twoGraphConf2))


# ---------------------------------------------------------------------------
# Slide conf — four-graph combos
# ---------------------------------------------------------------------------

def sysDiagSlideConfFourGraphComboBox1Click(ctx: "AppContext", idx: int) -> None:
    ctx.plc.set_four_graph_conf1(ctx.qt.sysDiagSlideConfFourGraphComboBox1.itemText(idx))
    parseDataLog.debug("fourGraphConf1: " + str(ctx.plc.fourGraphConf1))


def sysDiagSlideConfFourGraphComboBox2Click(ctx: "AppContext", idx: int) -> None:
    ctx.plc.set_four_graph_conf2(ctx.qt.sysDiagSlideConfFourGraphComboBox2.itemText(idx))
    parseDataLog.debug("fourGraphConf2: " + str(ctx.plc.fourGraphConf2))


def sysDiagSlideConfFourGraphComboBox3Click(ctx: "AppContext", idx: int) -> None:
    ctx.plc.set_four_graph_conf3(ctx.qt.sysDiagSlideConfFourGraphComboBox3.itemText(idx))
    parseDataLog.debug("fourGraphConf3: " + str(ctx.plc.fourGraphConf3))


# ---------------------------------------------------------------------------
# Slide conf — three-graph combos
# ---------------------------------------------------------------------------

def sysDiagSlideConfThreeGraphComboBox1Click(ctx: "AppContext", idx: int) -> None:
    ctx.plc.set_three_graph_conf1(ctx.qt.sysDiagSlideConfThreeGraphComboBox1.itemText(idx))
    parseDataLog.debug("threeGraphConf1: " + str(ctx.plc.threeGraphConf1))


def sysDiagSlideConfThreeGraphComboBox2Click(ctx: "AppContext", idx: int) -> None:
    ctx.plc.set_three_graph_conf2(ctx.qt.sysDiagSlideConfThreeGraphComboBox2.itemText(idx))
    parseDataLog.debug("threeGraphConf2: " + str(ctx.plc.threeGraphConf2))


def sysDiagSlideConfThreeGraphComboBox3Click(ctx: "AppContext", idx: int) -> None:
    ctx.plc.set_three_graph_conf3(ctx.qt.sysDiagSlideConfThreeGraphComboBox3.itemText(idx))
    parseDataLog.debug("threeGraphConf3: " + str(ctx.plc.threeGraphConf3))


# ---------------------------------------------------------------------------
# Slide conf — all-on-one-slide
# ---------------------------------------------------------------------------

def sysDiagSlideConfGeneralAllGraphsSlideClick(ctx: "AppContext") -> None:
    state = ctx.qt.sysDiagSlideConfGeneralAllGraphsSlideCheckBox.isChecked()
    ctx.plc.set_all_on_one_slide(state)
    enabled = bool(state)
    ctx.qt.sysDiagSlideConfGeneralAllSlidesCheckBox1.setChecked(enabled)
    ctx.qt.sysDiagSlideConfGeneralAllSlidesCheckBox1.setEnabled(enabled)
    ctx.qt.sysDiagSlideConfGeneralAllSlidesCheckBox2.setChecked(enabled)
    ctx.qt.sysDiagSlideConfGeneralAllSlidesCheckBox2.setEnabled(enabled)
    ctx.qt.sysDiagSlideConfGeneralAllSlidesCheckBox3.setChecked(enabled)
    ctx.qt.sysDiagSlideConfGeneralAllSlidesCheckBox3.setEnabled(enabled)
    ctx.qt.sysDiagSlideConfGeneralAllSlidesComboBox1.setEnabled(enabled)
    ctx.qt.sysDiagSlideConfGeneralAllSlidesComboBox2.setEnabled(enabled)
    ctx.qt.sysDiagSlideConfGeneralAllSlidesComboBox3.setEnabled(enabled)
    parseDataLog.debug("plotSetup: " + str(ctx.plc.plotSetup))


def sysDiagSlideConfGeneralAllSlidesComboBox1Click(ctx: "AppContext", idx: int) -> None:
    ctx.plc.set_all_graphs_conf1(ctx.qt.sysDiagSlideConfGeneralAllSlidesComboBox1.itemText(idx))
    parseDataLog.debug("AllGraphsConf1: " + str(ctx.plc.AllGraphsConf1))


def sysDiagSlideConfGeneralAllSlidesComboBox2Click(ctx: "AppContext", idx: int) -> None:
    ctx.plc.set_all_graphs_conf2(ctx.qt.sysDiagSlideConfGeneralAllSlidesComboBox2.itemText(idx))
    parseDataLog.debug("AllGraphsConf2: " + str(ctx.plc.AllGraphsConf2))


def sysDiagSlideConfGeneralAllSlidesComboBox3Click(ctx: "AppContext", idx: int) -> None:
    ctx.plc.set_all_graphs_conf3(ctx.qt.sysDiagSlideConfGeneralAllSlidesComboBox3.itemText(idx))
    parseDataLog.debug("AllGraphsConf3: " + str(ctx.plc.AllGraphsConf3))


# ---------------------------------------------------------------------------
# Script mode / plot window
# ---------------------------------------------------------------------------

def sysDiagPlotSetupScriptModeGroupClick(ctx: "AppContext") -> None:
    btnId = ctx.qt.sysDiagPlotSetupScriptModeGroup.checkedId()
    ctx.plc.set_script_mode(btnId)
    if btnId == 0:
        ctx.qt.sysDiagPlotWindowGroupBox.setEnabled(False)
        ctx.qt.sysDiagSlideConfGroupBox.setEnabled(True)
        # Restore allOnOneSlide from the slide-conf checkbox state
        ctx.plc.plotSetup["allOnOneSlide"] = (
            1 if ctx.qt.sysDiagSlideConfGeneralAllGraphsSlideCheckBox.isChecked() else 0
        )
        ctx.qt.sysDiagPlotWindowAllGraphsCheckBox.setChecked(False)
        for cb in (ctx.qt.sysDiagPlotWindowAllGraphsCheckBox1,
                   ctx.qt.sysDiagPlotWindowAllGraphsCheckBox2,
                   ctx.qt.sysDiagPlotWindowAllGraphsCheckBox3):
            cb.setChecked(False)
            cb.setEnabled(False)
        ctx.qt.sysDiagPlotWindowAllGraphsComboBox1.setCurrentIndex(0)
        ctx.qt.sysDiagPlotWindowAllGraphsComboBox2.setCurrentIndex(8)
        ctx.qt.sysDiagPlotWindowAllGraphsComboBox3.setCurrentIndex(6)
        for cb in (ctx.qt.sysDiagPlotWindowAllGraphsComboBox1,
                   ctx.qt.sysDiagPlotWindowAllGraphsComboBox2,
                   ctx.qt.sysDiagPlotWindowAllGraphsComboBox3):
            cb.setEnabled(False)
        parseDataLog.debug("plotSetup: " + str(ctx.plc.plotSetup))
    elif btnId == 1:
        ctx.qt.sysDiagPlotWindowGroupBox.setEnabled(True)
        ctx.qt.sysDiagSlideConfGroupBox.setEnabled(False)
        ctx.plc.plotSetup["allOnOneSlide"] = 0
        for cb in (ctx.qt.sysDiagPlotWindowAllGraphsCheckBox1,
                   ctx.qt.sysDiagPlotWindowAllGraphsCheckBox2,
                   ctx.qt.sysDiagPlotWindowAllGraphsCheckBox3):
            cb.setChecked(False)
            cb.setEnabled(False)
        ctx.qt.sysDiagPlotWindowAllGraphsComboBox1.setCurrentIndex(0)
        ctx.qt.sysDiagPlotWindowAllGraphsComboBox2.setCurrentIndex(8)
        ctx.qt.sysDiagPlotWindowAllGraphsComboBox3.setCurrentIndex(6)
        for cb in (ctx.qt.sysDiagPlotWindowAllGraphsComboBox1,
                   ctx.qt.sysDiagPlotWindowAllGraphsComboBox2,
                   ctx.qt.sysDiagPlotWindowAllGraphsComboBox3):
            cb.setEnabled(False)
        parseDataLog.debug("plotSetup: " + str(ctx.plc.plotSetup))


def sysDiagPlotWindowInputModeClick(ctx: "AppContext") -> None:
    btnId = ctx.qt.sysDiagPlotWindowInputModeGroup.checkedId()
    ctx.plc.set_plot_window_input_mode(btnId)
    ctx.qt.sysDiagPlotWindowInputModeLEdit.setEnabled(btnId == 1)
    parseDataLog.debug("plotWindowConfig: " + str(ctx.plc.plotWindowConfig))


def sysDiagPlotWindowGraphTypeComboBoxClick(ctx: "AppContext", idx: int) -> None:
    ctx.plc.set_plot_window_graph(ctx.qt.sysDiagPlotWindowGraphTypeComboBox.itemText(idx))
    parseDataLog.debug("plotWindowConfig: " + str(ctx.plc.plotWindowConfig))


def sysDiagPlotWindowAllGraphsComboBox1Click(ctx: "AppContext", idx: int) -> None:
    ctx.plc.set_all_graphs_conf1(ctx.qt.sysDiagPlotWindowAllGraphsComboBox1.itemText(idx))
    parseDataLog.debug("AllGraphsConf1: " + str(ctx.plc.AllGraphsConf1))


def sysDiagPlotWindowAllGraphsComboBox2Click(ctx: "AppContext", idx: int) -> None:
    ctx.plc.set_all_graphs_conf2(ctx.qt.sysDiagPlotWindowAllGraphsComboBox2.itemText(idx))
    parseDataLog.debug("AllGraphsConf2: " + str(ctx.plc.AllGraphsConf2))


def sysDiagPlotWindowAllGraphsComboBox3Click(ctx: "AppContext", idx: int) -> None:
    ctx.plc.set_all_graphs_conf3(ctx.qt.sysDiagPlotWindowAllGraphsComboBox3.itemText(idx))
    parseDataLog.debug("AllGraphsConf3: " + str(ctx.plc.AllGraphsConf3))


def sysDiagPlotWindowAllGraphsClick(ctx: "AppContext") -> None:
    state = ctx.qt.sysDiagPlotWindowAllGraphsCheckBox.isChecked()
    ctx.plc.set_plot_window_all_graphs_mode(state)
    ctx.plc.plotSetup["allOnOneSlide"] = 1 if state else 0
    enabled = bool(state)
    for cb in (ctx.qt.sysDiagPlotWindowAllGraphsCheckBox1,
               ctx.qt.sysDiagPlotWindowAllGraphsCheckBox2,
               ctx.qt.sysDiagPlotWindowAllGraphsCheckBox3):
        cb.setEnabled(enabled)
        cb.setChecked(enabled)
    for combo in (ctx.qt.sysDiagPlotWindowAllGraphsComboBox1,
                  ctx.qt.sysDiagPlotWindowAllGraphsComboBox2,
                  ctx.qt.sysDiagPlotWindowAllGraphsComboBox3):
        combo.setEnabled(enabled)


# ---------------------------------------------------------------------------
# Initialisation + signal wiring
# ---------------------------------------------------------------------------

def init_widgets(ctx: "AppContext") -> None:
    """Set default widget states — mirrors the top-level init code from main.py."""
    # Angle / orientation
    ctx.qt.sysDiagInputSetupAngleSetupRadio1.setChecked(True)
    ctx.qt.sysDiagInputSetupAngleSetupRadio2.setChecked(False)
    ctx.plc.plotSetup["targetAngle"] = 1

    ctx.qt.sysDiagInputSetupSensorOrientRadio1.setChecked(True)
    ctx.qt.sysDiagInputSetupSensorOrientRadio2.setChecked(False)
    ctx.plc.plotSetup["upsideDown"] = 0

    # Chirp
    ctx.qt.sysDiagInputSetupChirp0CheckBox.setChecked(True)
    ctx.qt.sysDiagInputSetupChirp1CheckBox.setChecked(False)
    ctx.qt.sysDiagInputSetupChirp2CheckBox.setChecked(False)
    ctx.qt.sysDiagInputSetupChirp3CheckBox.setChecked(False)
    ctx.plc.chirpConfig["chirp0"] = 1
    ctx.plc.chirpConfig["chirp1"] = 0
    ctx.plc.chirpConfig["chirp2"] = 0
    ctx.plc.chirpConfig["chirp3"] = 0

    # Diagram config input mode
    ctx.qt.sysDiagInputSetupDiagConfigInputModeRadio1.setChecked(True)
    ctx.qt.sysDiagInputSetupDiagConfigInputModeRadio2.setChecked(False)
    ctx.qt.sysDiagInputSetupDiagConfigInputModeRadio3.setChecked(False)
    ctx.plc.diagramConfig["selectDiagrams"] = 0

    ctx.qt.sysDiagInputSetupDiagConfigDesListLEdit.setText("1,2,3,4")
    ctx.qt.sysDiagInputSetupDiagConfigDesRangeLowLEdit.setText("0")
    ctx.plc.diagramConfig["lowerNumber"] = 0
    ctx.qt.sysDiagInputSetupDiagConfigDesRangeHighLEdit.setText("4")
    ctx.plc.diagramConfig["higherNumber"] = 4

    ctx.qt.sysDiagInputSetupDiagConfigOddEvenRadio1.setChecked(True)
    ctx.qt.sysDiagInputSetupDiagConfigOddEvenRadio2.setChecked(False)
    ctx.qt.sysDiagInputSetupDiagConfigOddEvenRadio3.setChecked(False)
    ctx.plc.diagramConfig["oddOrEven"] = 0

    # Image gen mode
    ctx.qt.sysDiagPlotSetupImgGenRadio1.setChecked(True)
    ctx.qt.sysDiagPlotSetupImgGenRadio2.setChecked(False)
    ctx.plc.plotSetup["SeparateRxCh"] = 1

    # 3-graph layout
    ctx.qt.sysDiagPlotSetup3GraphLayoutImgCheckBox.setChecked(True)
    ctx.plc.plotSetup["threeGraphLayout"] = 1

    # DPI
    ctx.qt.sysDiagPlotSetupImageDpiLEdit.setText("220")
    if sp.checkInt(ctx.qt.sysDiagPlotSetupImageDpiLEdit.text()):
        ctx.plc.plotSetup["imageDpi"] = int(ctx.qt.sysDiagPlotSetupImageDpiLEdit.text())

    # X-scale auto
    ctx.qt.sysDiagPlotSetupScalingAutoCheckBox.setChecked(False)
    ctx.plc.plotSetup["xScaleSizeAuto"] = 0
    ctx.qt.sysDiagPlotSetupScalingXScaleAzLEdit.setText("90")
    ctx.qt.sysDiagPlotSetupScalingXScaleElLEdit.setText("45")
    if sp.checkDecimal(ctx.qt.sysDiagPlotSetupScalingXScaleAzLEdit.text()):
        ctx.plc.plotSetup["xScaleSizeAz"] = float(ctx.qt.sysDiagPlotSetupScalingXScaleAzLEdit.text())
    if sp.checkDecimal(ctx.qt.sysDiagPlotSetupScalingXScaleElLEdit.text()):
        ctx.plc.plotSetup["xScaleSizeEl"] = float(ctx.qt.sysDiagPlotSetupScalingXScaleElLEdit.text())

    # Y-limits
    ctx.qt.sysDiagPlotSetupScalingYLimitRadio1.setChecked(True)
    ctx.qt.sysDiagPlotSetupScalingYLimitRadio2.setChecked(False)
    ctx.plc.plotSetup["yLimitsAntTypeSeparately"] = 1

    ctx.qt.sysDiagPlotSetupScalingDiffPhDiffLEdit.setText("1.5")
    if sp.checkDecimal(ctx.qt.sysDiagPlotSetupScalingDiffPhDiffLEdit.text()):
        ctx.plc.plotSetup["diffPhaseDiffScalingFactor"] = float(ctx.qt.sysDiagPlotSetupScalingDiffPhDiffLEdit.text())

    # Ideal curve
    ctx.qt.sysDiagPlotSetupGraphConfIdealCurveCheckBox.setChecked(True)
    ctx.plc.plotSetup["idealPhaseDiff"] = 1

    # Graph config checkboxes
    graphId = 0
    for key in ctx.plc.graphConfig:
        ctx.plc.graphConfig[key] = 0
        button = ctx.qt.sysDiagPlotSetupGraphConfGroup.button(graphId)
        button.setChecked(False)
        if key in ("level", "normLevel", "diffPhaseDiff", "corrPhaseDiff"):
            ctx.plc.graphConfig[key] = 1
            button.setChecked(True)
        graphId += 1

    # Populate two-graph combos
    for combo in (ctx.qt.sysDiagSlideConfTwoGraphComboBox11,
                  ctx.qt.sysDiagSlideConfTwoGraphComboBox12,
                  ctx.qt.sysDiagSlideConfTwoGraphComboBox21,
                  ctx.qt.sysDiagSlideConfTwoGraphComboBox22):
        sysDiagSlideConfComboAddItems(ctx, combo)

    sysDiagSlideConfTwoAndFourGraphComboSetCurrentItem(ctx.qt.sysDiagSlideConfTwoGraphComboBox11, "level")
    ctx.plc.twoGraphConf1["primGraph"] = "level"
    sysDiagSlideConfTwoAndFourGraphComboSetCurrentItem(ctx.qt.sysDiagSlideConfTwoGraphComboBox12, "normLevel")
    ctx.plc.twoGraphConf1["secGraph"] = "normLevel"
    sysDiagSlideConfTwoAndFourGraphComboSetCurrentItem(ctx.qt.sysDiagSlideConfTwoGraphComboBox21, "corrPhaseDiff")
    ctx.plc.twoGraphConf2["primGraph"] = "corrPhaseDiff"
    sysDiagSlideConfTwoAndFourGraphComboSetCurrentItem(ctx.qt.sysDiagSlideConfTwoGraphComboBox22, "diffPhaseDiff")
    ctx.plc.twoGraphConf2["secGraph"] = "diffPhaseDiff"

    # Four/three-graph initial state (mirrors the if/else block from main.py)
    if ctx.qt.sysDiagPlotSetupImgGenRadio1.isChecked():
        ctx.qt.sysDiagSlideConfFourGraphFrame.setEnabled(True)
        ctx.qt.sysDiagSlideConfFourGraphCheckBox1.setChecked(True)
        ctx.qt.sysDiagSlideConfFourGraphCheckBox2.setChecked(True)
        ctx.qt.sysDiagSlideConfFourGraphCheckBox3.setChecked(True)
        ctx.qt.sysDiagPlotSetup3GraphLayoutImgCheckBox.setChecked(True)
        ctx.qt.sysDiagPlotSetup3GraphLayoutImgCheckBox.setEnabled(True)
        ctx.plc.plotSetup["threeGraphLayout"] = 1
        ctx.qt.sysDiagSlideConfThreeGraphCheckBox1.setChecked(True)
        ctx.qt.sysDiagSlideConfThreeGraphCheckBox2.setChecked(True)
        ctx.qt.sysDiagSlideConfThreeGraphCheckBox3.setChecked(False)
        ctx.qt.sysDiagSlideConfThreeGraphFrame.setEnabled(True)
        ctx.qt.sysDiagSlideConfFourGraphCheckBox1.setChecked(True)
        ctx.qt.sysDiagSlideConfFourGraphCheckBox2.setChecked(False)
        ctx.qt.sysDiagSlideConfFourGraphCheckBox3.setChecked(False)
        ctx.qt.sysDiagSlideConfTwoGraphCheckBox1.setChecked(False)
        ctx.qt.sysDiagSlideConfTwoGraphCheckBox2.setChecked(False)
    else:
        ctx.qt.sysDiagSlideConfFourGraphFrame.setEnabled(False)
        ctx.qt.sysDiagSlideConfFourGraphCheckBox1.setChecked(False)
        ctx.qt.sysDiagSlideConfFourGraphCheckBox2.setChecked(False)
        ctx.qt.sysDiagSlideConfFourGraphCheckBox3.setChecked(False)
        ctx.qt.sysDiagPlotSetup3GraphLayoutImgCheckBox.setChecked(False)
        ctx.qt.sysDiagPlotSetup3GraphLayoutImgCheckBox.setEnabled(False)
        ctx.plc.plotSetup["threeGraphLayout"] = 0
        ctx.qt.sysDiagSlideConfThreeGraphCheckBox1.setChecked(False)
        ctx.qt.sysDiagSlideConfThreeGraphCheckBox2.setChecked(False)
        ctx.qt.sysDiagSlideConfThreeGraphCheckBox3.setChecked(False)
        ctx.qt.sysDiagSlideConfThreeGraphFrame.setEnabled(False)
        ctx.qt.sysDiagSlideConfTwoGraphCheckBox1.setChecked(True)
        ctx.qt.sysDiagSlideConfTwoGraphCheckBox2.setChecked(True)

    # Four-graph combos
    for combo in (ctx.qt.sysDiagSlideConfFourGraphComboBox1,
                  ctx.qt.sysDiagSlideConfFourGraphComboBox2,
                  ctx.qt.sysDiagSlideConfFourGraphComboBox3):
        sysDiagSlideConfComboAddItems(ctx, combo)

    sysDiagSlideConfTwoAndFourGraphComboSetCurrentItem(ctx.qt.sysDiagSlideConfFourGraphComboBox1, "level")
    ctx.plc.fourGraphConf1["graphType"] = "level"
    sysDiagSlideConfTwoAndFourGraphComboSetCurrentItem(ctx.qt.sysDiagSlideConfFourGraphComboBox2, "corrPhaseDiff")
    ctx.plc.fourGraphConf2["graphType"] = "corrPhaseDiff"
    sysDiagSlideConfTwoAndFourGraphComboSetCurrentItem(ctx.qt.sysDiagSlideConfFourGraphComboBox3, "diffPhaseDiff")
    ctx.plc.fourGraphConf3["graphType"] = "diffPhaseDiff"

    # Three-graph combos
    for combo in (ctx.qt.sysDiagSlideConfThreeGraphComboBox1,
                  ctx.qt.sysDiagSlideConfThreeGraphComboBox2,
                  ctx.qt.sysDiagSlideConfThreeGraphComboBox3):
        sysDiagSlideConfThreeGraphComboAddItems(ctx, combo)

    sysDiagSlideConfTwoAndFourGraphComboSetCurrentItem(ctx.qt.sysDiagSlideConfThreeGraphComboBox1, "corrPhaseDiff")
    ctx.plc.threeGraphConf1["graphType"] = "corrPhaseDiff"
    sysDiagSlideConfTwoAndFourGraphComboSetCurrentItem(ctx.qt.sysDiagSlideConfThreeGraphComboBox2, "diffPhaseDiff")
    ctx.plc.threeGraphConf2["graphType"] = "diffPhaseDiff"

    # Sensor num
    ctx.qt.sysDiagSlideConfGeneralSensorNumSlideLEdit.setText("32")
    if sp.checkInt(ctx.qt.sysDiagSlideConfGeneralSensorNumSlideLEdit.text()):
        ctx.plc.plotSetup["nofSensorMeasToShow"] = int(ctx.qt.sysDiagSlideConfGeneralSensorNumSlideLEdit.text())

    # All-on-one-slide initial state
    if not ctx.qt.sysDiagSlideConfGeneralAllGraphsSlideCheckBox.isChecked():
        for w in (ctx.qt.sysDiagSlideConfGeneralAllSlidesCheckBox1,
                  ctx.qt.sysDiagSlideConfGeneralAllSlidesCheckBox2,
                  ctx.qt.sysDiagSlideConfGeneralAllSlidesCheckBox3,
                  ctx.qt.sysDiagSlideConfGeneralAllSlidesComboBox1,
                  ctx.qt.sysDiagSlideConfGeneralAllSlidesComboBox2,
                  ctx.qt.sysDiagSlideConfGeneralAllSlidesComboBox3):
            w.setChecked(False) if hasattr(w, "setChecked") else None
            w.setEnabled(False)
        ctx.plc.plotSetup["allOnOneSlide"] = 0
    else:
        ctx.plc.plotSetup["allOnOneSlide"] = 1

    ctx.qt.sysDiagSlideConfGeneralAllSlidesComboBox1.setCurrentIndex(0)
    ctx.qt.sysDiagSlideConfGeneralAllSlidesComboBox2.setCurrentIndex(8)
    ctx.qt.sysDiagSlideConfGeneralAllSlidesComboBox3.setCurrentIndex(6)
    ctx.plc.AllGraphsConf1["graphType"] = "level"
    ctx.plc.AllGraphsConf2["graphType"] = "corrPhaseDiff"
    ctx.plc.AllGraphsConf3["graphType"] = "diffPhaseDiff"

    # Script mode
    ctx.qt.sysDiagPlotSetupScriptModeRadio1.setChecked(True)
    ctx.qt.sysDiagPlotSetupScriptModeRadio2.setChecked(False)
    ctx.plc.plotSetup["ShowCertainPlotWindow"] = 0
    ctx.qt.sysDiagPlotWindowGroupBox.setEnabled(False)
    ctx.qt.sysDiagSlideConfGroupBox.setEnabled(True)

    # Plot window
    ctx.qt.sysDiagPlotWindowInputModeRadio1.setChecked(True)
    ctx.qt.sysDiagPlotWindowInputModeRadio2.setChecked(False)
    ctx.plc.plotWindowConfig["inputMode"] = 1
    ctx.qt.sysDiagPlotWindowInputModeLEdit.setEnabled(False)
    ctx.plc.plotWindowConfig["string"] = ""

    ctx.qt.sysDiagPlotWindowAntTypLEdit.setText("0")
    ctx.plc.plotWindowConfig["antType"] = 0
    ctx.qt.sysDiagPlotWindowDiagNumLEdit.setText("0")
    ctx.plc.plotWindowConfig["diagramNum"] = 0
    ctx.qt.sysDiagPlotWindowRxChLEdit.setText("0")
    ctx.plc.plotWindowConfig["rxCh"] = 0
    ctx.plc.plotWindowConfig["graph"] = "level"

    ctx.qt.sysDiagPlotWindowAllGraphsCheckBox.setChecked(False)
    for cb in (ctx.qt.sysDiagPlotWindowAllGraphsCheckBox1,
               ctx.qt.sysDiagPlotWindowAllGraphsCheckBox2,
               ctx.qt.sysDiagPlotWindowAllGraphsCheckBox3):
        cb.setChecked(False)
    ctx.qt.sysDiagPlotWindowAllGraphsComboBox1.setCurrentIndex(0)
    ctx.qt.sysDiagPlotWindowAllGraphsComboBox2.setCurrentIndex(8)
    ctx.qt.sysDiagPlotWindowAllGraphsComboBox3.setCurrentIndex(6)


# ---------------------------------------------------------------------------
# Evaluation orchestrator (PST-59) — wired to sysDiagStartPushBtn
# ---------------------------------------------------------------------------

def sys_diag_data_update_and_evaluation(ctx: "AppContext") -> None:
    """Read widget state, build graph lists, then start the sysDiag evaluation."""
    import AntennaSystemDiagrams as antSysDiag  # noqa: PLC0415
    from shared import auxiliary as aux           # noqa: PLC0415

    twoGraphSetupList:      list = []
    fourGraphSetupList:     list = []
    threeGraphSetupList:    list = []
    allOnOneSlideGraphList: list = []
    diagramConfigList:      list = []
    ctx.plc.plotSetup["sensorMusterList"][:] = []

    if ctx.plc.plotSetup["useSensorMuster"] == 1:
        for part in ctx.qt.parseProtSensorMusterLEdit.text().split(" "):
            if part != "":
                ctx.plc.plotSetup["sensorMusterList"].append(part)

    for char in ctx.qt.sysDiagInputSetupDiagConfigDesListLEdit.text().split(","):
        if char != "" and sp.checkInt(char):
            diagramConfigList.append(int(char))

    if sp.checkInt(ctx.qt.sysDiagInputSetupDiagConfigDesRangeLowLEdit.text()):
        ctx.plc.diagramConfig["lowerNumber"] = int(ctx.qt.sysDiagInputSetupDiagConfigDesRangeLowLEdit.text())

    if sp.checkInt(ctx.qt.sysDiagInputSetupDiagConfigDesRangeHighLEdit.text()):
        ctx.plc.diagramConfig["higherNumber"] = int(ctx.qt.sysDiagInputSetupDiagConfigDesRangeHighLEdit.text())

    if sp.checkInt(ctx.qt.sysDiagPlotSetupImageDpiLEdit.text()):
        ctx.plc.plotSetup["imageDpi"] = int(ctx.qt.sysDiagPlotSetupImageDpiLEdit.text())

    if sp.checkDecimal(ctx.qt.sysDiagPlotSetupScalingXScaleAzLEdit.text()):
        ctx.plc.plotSetup["xScaleSizeAz"] = float(ctx.qt.sysDiagPlotSetupScalingXScaleAzLEdit.text())

    if sp.checkDecimal(ctx.qt.sysDiagPlotSetupScalingXScaleElLEdit.text()):
        ctx.plc.plotSetup["xScaleSizeEl"] = float(ctx.qt.sysDiagPlotSetupScalingXScaleElLEdit.text())

    if sp.checkDecimal(ctx.qt.sysDiagPlotSetupScalingDiffPhDiffLEdit.text()):
        ctx.plc.plotSetup["diffPhaseDiffScalingFactor"] = float(ctx.qt.sysDiagPlotSetupScalingDiffPhDiffLEdit.text())

    if sp.checkInt(ctx.qt.sysDiagPlotWindowDiagNumLEdit.text()):
        ctx.plc.plotWindowConfig["diagramNum"] = int(ctx.qt.sysDiagPlotWindowDiagNumLEdit.text())

    if sp.checkInt(ctx.qt.sysDiagPlotWindowRxChLEdit.text()):
        ctx.plc.plotWindowConfig["rxCh"] = int(ctx.qt.sysDiagPlotWindowRxChLEdit.text())

    if sp.checkInt(ctx.qt.sysDiagPlotWindowAntTypLEdit.text()):
        ctx.plc.plotWindowConfig["antType"] = int(ctx.qt.sysDiagPlotWindowAntTypLEdit.text())

    ctx.plc.plotWindowConfig["string"] = ctx.qt.sysDiagPlotWindowInputModeLEdit.text()

    if sp.checkInt(ctx.qt.sysDiagSlideConfGeneralSensorNumSlideLEdit.text()):
        ctx.plc.plotSetup["nofSensorMeasToShow"] = int(ctx.qt.sysDiagSlideConfGeneralSensorNumSlideLEdit.text())

    if ctx.qt.sysDiagSlideConfTwoGraphCheckBox1.isChecked():
        twoGraphSetupList.append(ctx.plc.twoGraphConf1)
    if ctx.qt.sysDiagSlideConfTwoGraphCheckBox2.isChecked():
        twoGraphSetupList.append(ctx.plc.twoGraphConf2)

    if ctx.qt.sysDiagSlideConfFourGraphCheckBox1.isChecked():
        fourGraphSetupList.append(ctx.plc.fourGraphConf1)
    if ctx.qt.sysDiagSlideConfFourGraphCheckBox2.isChecked():
        fourGraphSetupList.append(ctx.plc.fourGraphConf2)
    if ctx.qt.sysDiagSlideConfFourGraphCheckBox3.isChecked():
        fourGraphSetupList.append(ctx.plc.fourGraphConf3)

    if ctx.qt.sysDiagSlideConfThreeGraphCheckBox1.isChecked():
        threeGraphSetupList.append(ctx.plc.threeGraphConf1)
    if ctx.qt.sysDiagSlideConfThreeGraphCheckBox2.isChecked():
        threeGraphSetupList.append(ctx.plc.threeGraphConf2)
    if ctx.qt.sysDiagSlideConfThreeGraphCheckBox3.isChecked():
        threeGraphSetupList.append(ctx.plc.threeGraphConf3)

    scriptMode = ctx.qt.sysDiagPlotSetupScriptModeGroup.checkedId()
    if scriptMode == 0:
        if ctx.qt.sysDiagSlideConfGeneralAllSlidesCheckBox1.isChecked():
            allOnOneSlideGraphList.append(ctx.plc.AllGraphsConf1)
        if ctx.qt.sysDiagSlideConfGeneralAllSlidesCheckBox2.isChecked():
            allOnOneSlideGraphList.append(ctx.plc.AllGraphsConf2)
        if ctx.qt.sysDiagSlideConfGeneralAllSlidesCheckBox3.isChecked():
            allOnOneSlideGraphList.append(ctx.plc.AllGraphsConf3)
    else:
        if ctx.qt.sysDiagPlotWindowAllGraphsCheckBox1.isChecked():
            allOnOneSlideGraphList.append(ctx.plc.AllGraphsConf1)
        if ctx.qt.sysDiagPlotWindowAllGraphsCheckBox2.isChecked():
            allOnOneSlideGraphList.append(ctx.plc.AllGraphsConf2)
        if ctx.qt.sysDiagPlotWindowAllGraphsCheckBox3.isChecked():
            allOnOneSlideGraphList.append(ctx.plc.AllGraphsConf3)

    # Safety clamp: in plot-window mode, allOnOneSlide must match the actual list.
    # If the list is empty (no checkboxes selected), disable allOnOneSlide so
    # start_data_evaluation does not error on an empty graph list.
    if scriptMode == 1 and len(allOnOneSlideGraphList) == 0:
        ctx.plc.plotSetup["allOnOneSlide"] = 0

    parsed_data_list = _resolve_sys_diag_parsed_data(ctx)
    plot_setup = copy.deepcopy(ctx.plc.plotSetup)
    chirp_config = copy.deepcopy(ctx.plc.chirpConfig)
    graph_config = copy.deepcopy(ctx.plc.graphConfig)
    diagram_config = copy.deepcopy(ctx.plc.diagramConfig)

    ctx.qt.sysDiagStartPushBtn.setEnabled(False)
    worker_done = {"done": False}

    def _run_eval() -> None:
        try:
            antSysDiag.start_data_evaluation(
                parsed_data_list,
                plot_setup,
                chirp_config,
                graph_config,
                diagram_config,
                copy.deepcopy(twoGraphSetupList),
                copy.deepcopy(fourGraphSetupList),
                copy.deepcopy(threeGraphSetupList),
                copy.deepcopy(allOnOneSlideGraphList),
                list(diagramConfigList),
                logconfig.antSysDiagLogger,
                aux.antSysDiagOutputPath,
                "Antenna_diagrams.pptx",
                "./assets/template.pptx",
            )
        except Exception as exc:
            parseDataLog.exception("System diagrams evaluation failed: %s", exc)
        finally:
            worker_done["done"] = True

    # Sync the module-level plotWindowConfig in AntennaSystemDiagrams so
    # start_data_evaluation uses current UI values instead of hardcoded defaults.
    antSysDiag.plotWindowConfig.update(ctx.plc.plotWindowConfig)

    if plot_setup.get("ShowCertainPlotWindow", 0) == 1:
        # Matplotlib GUI (plt.subplots / plt.show) must run on the main thread.
        # In plot-window mode run synchronously so the figures appear correctly.
        _run_eval()
        ctx.qt.sysDiagStartPushBtn.setEnabled(True)
    else:
        worker = threading.Thread(target=_run_eval, name="sys-diag-eval", daemon=True)
        worker.start()

        def _reenable_start_button() -> None:
            if worker_done["done"]:
                ctx.qt.sysDiagStartPushBtn.setEnabled(True)
                return
            ctx.qt.QTimer.singleShot(100, _reenable_start_button)

        ctx.qt.QTimer.singleShot(100, _reenable_start_button)


def wire(ctx: "AppContext") -> None:
    """Connect all sys-diag Qt signals to their handlers."""
    ctx.qt.sysDiagInputSetupAngleGroup.buttonClicked.connect(
        lambda: sysDiagInputSetupAngleGroupClick(ctx)
    )
    ctx.qt.sysDiagInputSetupSensorOrientGroup.buttonClicked.connect(
        lambda: sysDiagInputSetupSensorOrientGroupClick(ctx)
    )
    ctx.qt.sysDiagInputSetupChirpGroup.buttonClicked.connect(
        lambda btn: sysDiagInputSetupChirpClick(ctx, btn)
    )
    ctx.qt.sysDiagInputSetupDiagConfGroup.buttonClicked.connect(
        lambda: sysDiagInputSetupDiagConfigInputModeClick(ctx)
    )
    ctx.qt.sysDiagInputSetupDiagConfOddEvenGroup.buttonClicked.connect(
        lambda: sysDiagInputSetupDiagConfOddEvenClick(ctx)
    )
    ctx.qt.sysDiagPlotSetupImgGenGroup.buttonClicked.connect(
        lambda: sysDiagPlotSetupImgGenClick(ctx)
    )
    ctx.qt.sysDiagPlotSetupScalingYLimitsGroup.buttonClicked.connect(
        lambda: sysDiagPlotSetupScalingYLimitsClick(ctx)
    )
    ctx.qt.sysDiagPlotSetup3GraphLayoutImgCheckBox.stateChanged.connect(
        lambda: sysDiagPlotSetup3GraphLayoutImgClick(ctx)
    )
    ctx.qt.sysDiagPlotSetupScalingAutoCheckBox.stateChanged.connect(
        lambda: sysDiagPlotSetupScalingAutoClick(ctx)
    )
    ctx.qt.sysDiagPlotSetupGraphConfGroup.buttonClicked.connect(
        lambda btn: sysDiagPlotSetupGraphConfClick(ctx, btn)
    )
    ctx.qt.sysDiagPlotSetupGraphConfIdealCurveCheckBox.stateChanged.connect(
        lambda: sysDiagPlotSetupGraphConfIdealCurveClick(ctx)
    )
    ctx.qt.sysDiagSlideConfGeneralAllGraphsSlideCheckBox.stateChanged.connect(
        lambda: sysDiagSlideConfGeneralAllGraphsSlideClick(ctx)
    )
    ctx.qt.sysDiagSlideConfGeneralAllSlidesComboBox1.currentIndexChanged.connect(
        lambda idx: sysDiagSlideConfGeneralAllSlidesComboBox1Click(ctx, idx)
    )
    ctx.qt.sysDiagSlideConfGeneralAllSlidesComboBox2.currentIndexChanged.connect(
        lambda idx: sysDiagSlideConfGeneralAllSlidesComboBox2Click(ctx, idx)
    )
    ctx.qt.sysDiagSlideConfGeneralAllSlidesComboBox3.currentIndexChanged.connect(
        lambda idx: sysDiagSlideConfGeneralAllSlidesComboBox3Click(ctx, idx)
    )
    ctx.qt.sysDiagPlotSetupScriptModeGroup.buttonClicked.connect(
        lambda: sysDiagPlotSetupScriptModeGroupClick(ctx)
    )
    ctx.qt.sysDiagPlotWindowInputModeGroup.buttonClicked.connect(
        lambda: sysDiagPlotWindowInputModeClick(ctx)
    )
    ctx.qt.sysDiagPlotWindowGraphTypeComboBox.currentIndexChanged.connect(
        lambda idx: sysDiagPlotWindowGraphTypeComboBoxClick(ctx, idx)
    )
    ctx.qt.sysDiagPlotWindowAllGraphsCheckBox.stateChanged.connect(
        lambda: sysDiagPlotWindowAllGraphsClick(ctx)
    )
    ctx.qt.sysDiagPlotWindowAllGraphsComboBox1.currentIndexChanged.connect(
        lambda idx: sysDiagPlotWindowAllGraphsComboBox1Click(ctx, idx)
    )
    ctx.qt.sysDiagPlotWindowAllGraphsComboBox2.currentIndexChanged.connect(
        lambda idx: sysDiagPlotWindowAllGraphsComboBox2Click(ctx, idx)
    )
    ctx.qt.sysDiagPlotWindowAllGraphsComboBox3.currentIndexChanged.connect(
        lambda idx: sysDiagPlotWindowAllGraphsComboBox3Click(ctx, idx)
    )
    ctx.qt.sysDiagSlideConfTwoGraphComboBox11.currentIndexChanged.connect(
        lambda idx: sysDiagSlideConfTwoGraphComboBox11Click(ctx, idx)
    )
    ctx.qt.sysDiagSlideConfTwoGraphComboBox12.currentIndexChanged.connect(
        lambda idx: sysDiagSlideConfTwoGraphComboBox12Click(ctx, idx)
    )
    ctx.qt.sysDiagSlideConfTwoGraphComboBox21.currentIndexChanged.connect(
        lambda idx: sysDiagSlideConfTwoGraphComboBox21Click(ctx, idx)
    )
    ctx.qt.sysDiagSlideConfTwoGraphComboBox22.currentIndexChanged.connect(
        lambda idx: sysDiagSlideConfTwoGraphComboBox22Click(ctx, idx)
    )
    ctx.qt.sysDiagSlideConfFourGraphComboBox1.currentIndexChanged.connect(
        lambda idx: sysDiagSlideConfFourGraphComboBox1Click(ctx, idx)
    )
    ctx.qt.sysDiagSlideConfFourGraphComboBox2.currentIndexChanged.connect(
        lambda idx: sysDiagSlideConfFourGraphComboBox2Click(ctx, idx)
    )
    ctx.qt.sysDiagSlideConfFourGraphComboBox3.currentIndexChanged.connect(
        lambda idx: sysDiagSlideConfFourGraphComboBox3Click(ctx, idx)
    )
    ctx.qt.sysDiagSlideConfThreeGraphComboBox1.currentIndexChanged.connect(
        lambda idx: sysDiagSlideConfThreeGraphComboBox1Click(ctx, idx)
    )
    ctx.qt.sysDiagSlideConfThreeGraphComboBox2.currentIndexChanged.connect(
        lambda idx: sysDiagSlideConfThreeGraphComboBox2Click(ctx, idx)
    )
    ctx.qt.sysDiagSlideConfThreeGraphComboBox3.currentIndexChanged.connect(
        lambda idx: sysDiagSlideConfThreeGraphComboBox3Click(ctx, idx)
    )
    # Start button — evaluation orchestrator (PST-59)
    ctx.qt.sysDiagStartPushBtn.clicked.connect(
        lambda: sys_diag_data_update_and_evaluation(ctx)
    )
    # Fill-in PTU table button
    ctx.qt.SysDiaInterStartBtn.clicked.connect(
        lambda: _fill_in_ptu(ctx)
    )


def _fill_in_ptu(ctx: "AppContext") -> None:
    """Delegate the fill-PTU-table action to AntennaSystemDiagrams."""
    import AntennaSystemDiagrams as antSysDiag  # noqa: PLC0415
    antSysDiag.fillInPTU(
        _resolve_sys_diag_parsed_data(ctx),
        logconfig.antSysDiagLogger,
    )
