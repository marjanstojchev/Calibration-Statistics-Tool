"""Tx-Antenna-Diagrams tab signal handlers  (PST-57).

All handler functions previously defined at module level in main.py under
the "##TxAnt Diagrams" section.

``init_widgets(ctx)`` performs widget initialisation.
``wire(ctx)``         connects all Qt signals to their handlers.
"""
from __future__ import annotations

import copy
import threading
from typing import TYPE_CHECKING

from shared import safeparse as sp
from shared import auxiliary as aux

if TYPE_CHECKING:  # pragma: no cover
    from ui.handlers.app_context import AppContext

import logconfig

parseDataLog = logconfig.mainLoadDataLogger.logger


# ---------------------------------------------------------------------------
# Input Setup — angle / orientation / Az / El
# ---------------------------------------------------------------------------

def txAntDiagInputSetupAngleGroupClick(ctx: "AppContext") -> None:
    btnId = ctx.qt.txAntDiagInputSetupAngleGroup.checkedId()
    if btnId == 0:
        _txAntDiag().plotSetup["targetAngle"] = 1
    elif btnId == 1:
        _txAntDiag().plotSetup["targetAngle"] = 0
    parseDataLog.debug("plotSetup: " + str(_txAntDiag().plotSetup))


def txAntDiagInputSetupSensorOrientGroupClick(ctx: "AppContext") -> None:
    btnId = ctx.qt.txAntDiagInputSetupSensorOrientGroup.checkedId()
    if btnId == 0:
        _txAntDiag().plotSetup["upsideDown"] = 0
    elif btnId == 1:
        _txAntDiag().plotSetup["upsideDown"] = 1
    parseDataLog.debug("plotSetup: " + str(_txAntDiag().plotSetup))


def txAntDiagInputSetupAzClick(ctx: "AppContext") -> None:
    state = ctx.qt.txAntDiagInputSetupAzCheckBox.isChecked()
    _txAntDiag().plotSetup["AzDiag"] = 1 if state else 0
    parseDataLog.debug("plotSetup: " + str(_txAntDiag().plotSetup))


def txAntDiagInputSetupElClick(ctx: "AppContext") -> None:
    state = ctx.qt.txAntDiagInputSetupElCheckBox.isChecked()
    _txAntDiag().plotSetup["ElDiag"] = 1 if state else 0
    parseDataLog.debug("plotSetup: " + str(_txAntDiag().plotSetup))


# ---------------------------------------------------------------------------
# Plot Setup — scaling
# ---------------------------------------------------------------------------

def txAntDiagPlotSetupScalingAutoClick(ctx: "AppContext") -> None:
    state = ctx.qt.txAntDiagPlotSetupScalingAutoCheckBox.isChecked()
    _txAntDiag().plotSetup["xScaleSizeAuto"] = 1 if state else 0
    parseDataLog.debug("plotSetup: " + str(_txAntDiag().plotSetup))


def txAntDiagPlotSetupScalingOrigGraphsClick(ctx: "AppContext") -> None:
    state = ctx.qt.txAntDiagPlotSetupScalingOrigGraphsCheckBox.isChecked()
    _txAntDiag().plotSetup["plotOrigGraphs"] = 1 if state else 0
    parseDataLog.debug("plotSetup: " + str(_txAntDiag().plotSetup))


def txAntDiagPlotSetupScalingNormGraphsClick(ctx: "AppContext") -> None:
    state = ctx.qt.txAntDiagPlotSetupScalingNormGraphsCheckBox.isChecked()
    _txAntDiag().plotSetup["plotNormGraphs"] = 1 if state else 0
    parseDataLog.debug("plotSetup: " + str(_txAntDiag().plotSetup))


# ---------------------------------------------------------------------------
# Plot Setup — graph config
# ---------------------------------------------------------------------------

def txAntDiagPlotSetupGraphConfClick(ctx: "AppContext", btn) -> None:
    i      = 0
    setKey = ""
    state  = 0
    btnId  = ctx.qt.txAntDiagPlotSetupGraphConfGroup.id(btn)
    for key in _txAntDiag().graphConfig:
        if i == btnId:
            chBox  = ctx.qt.txAntDiagPlotSetupGraphConfGroup.button(btnId)
            state  = chBox.isChecked()
            setKey = key
            break
        i += 1
    _txAntDiag().graphConfig[setKey] = ctx.qt.boolMapping(state)
    parseDataLog.debug("graphConfig: " + str(_txAntDiag().graphConfig))


# ---------------------------------------------------------------------------
# Evaluation orchestrator  (wired to txAntDiagStartPushBtn)
# ---------------------------------------------------------------------------

def txantdiag_data_update_and_evaluation(ctx: "AppContext") -> None:
    txAntDiag = _txAntDiag()
    txAntDiag.plotSetup["sensorMusterList"][:] = []

    if txAntDiag.plotSetup["useSensorMuster"] == 1:
        sensorMusterInputList = ctx.qt.parseProtSensorMusterLEdit.text()
        sensorMusterList = sensorMusterInputList.split(" ")
        for part in sensorMusterList:
            if part != "":
                txAntDiag.plotSetup["sensorMusterList"].append(part)

    if sp.checkInt(ctx.qt.txAntDiagPlotSetupImageDpiLEdit.text()):
        txAntDiag.plotSetup["imageDpi"] = int(ctx.qt.txAntDiagPlotSetupImageDpiLEdit.text())

    if sp.checkDecimal(ctx.qt.txAntDiagPlotSetupScalingXScaleAzLEdit.text()):
        txAntDiag.plotSetup["xScaleSizeAz"] = float(ctx.qt.txAntDiagPlotSetupScalingXScaleAzLEdit.text())

    if sp.checkDecimal(ctx.qt.txAntDiagPlotSetupScalingXScaleElLEdit.text()):
        txAntDiag.plotSetup["xScaleSizeEl"] = float(ctx.qt.txAntDiagPlotSetupScalingXScaleElLEdit.text())

    if sp.checkInt(ctx.qt.txAntDiagPlotSetupSensorNumSlideLEdit.text()):
        txAntDiag.plotSetup["nofSensorMeasToShow"] = int(ctx.qt.txAntDiagPlotSetupSensorNumSlideLEdit.text())

    if sp.checkInt(ctx.qt.txAntDiagPlotSetupGraphsPerSlideLEdit.text()):
        txAntDiag.plotSetup["graphsPerSlide"] = int(ctx.qt.txAntDiagPlotSetupGraphsPerSlideLEdit.text())

    txAntDiagLogger = logconfig.txAntDiagLogger
    parsedDataList  = list(ctx.pc.txAntDiagParsedDataDict.get("parsedDataList", []))
    plotSetup = copy.deepcopy(txAntDiag.plotSetup)
    graphConfig = copy.deepcopy(txAntDiag.graphConfig)

    ctx.qt.txAntDiagStartPushBtn.setEnabled(False)
    worker_done = {"done": False}

    def _run_eval() -> None:
        try:
            txAntDiag.start_data_evaluation(
                parsedDataList,
                plotSetup,
                graphConfig,
                txAntDiagLogger,
                aux.txAntDiagOutputPath,
                "TxAnt_Diagrams.pptx",
                "./assets/template.pptx",
            )
        except Exception as exc:
            parseDataLog.exception("Tx antenna diagram evaluation failed: %s", exc)
        finally:
            worker_done["done"] = True

    worker = threading.Thread(target=_run_eval, name="tx-ant-eval", daemon=True)
    worker.start()

    def _reenable_start_button() -> None:
        if worker_done["done"]:
            ctx.qt.txAntDiagStartPushBtn.setEnabled(True)
            return
        ctx.qt.QTimer.singleShot(100, _reenable_start_button)

    ctx.qt.QTimer.singleShot(100, _reenable_start_button)


# ---------------------------------------------------------------------------
# Internal helper — lazy-import to avoid Qt init at module import time
# ---------------------------------------------------------------------------

def _txAntDiag():
    """Return the TxAntDiagrams module (imported lazily).

    ``tx_diagrams`` is on sys.path (added by main.py before any handler
    module is imported), so the bare-module name is correct here.
    """
    import TxAntDiagrams as _mod  # noqa: PLC0415
    return _mod


# ---------------------------------------------------------------------------
# Widget initialisation
# ---------------------------------------------------------------------------

def init_widgets(ctx: "AppContext") -> None:
    """Mirror the top-level init code from main.py for the txAntDiag tab."""
    txAntDiag = _txAntDiag()

    # Angle
    ctx.qt.txAntDiagInputSetupAngleSetupRadio1.setChecked(True)
    ctx.qt.txAntDiagInputSetupAngleSetupRadio2.setChecked(False)
    txAntDiag.plotSetup["targetAngle"] = 1

    # Orientation
    ctx.qt.txAntDiagInputSetupSensorOrientRadio1.setChecked(True)
    ctx.qt.txAntDiagInputSetupSensorOrientRadio2.setChecked(False)
    txAntDiag.plotSetup["upsideDown"] = 0

    # Az / El
    ctx.qt.txAntDiagInputSetupAzCheckBox.setChecked(True)
    ctx.qt.txAntDiagInputSetupElCheckBox.setChecked(False)
    txAntDiag.plotSetup["AzDiag"] = 1
    txAntDiag.plotSetup["ElDiag"] = 0

    # Sensor num / graphs-per-slide / DPI
    ctx.qt.txAntDiagPlotSetupSensorNumSlideLEdit.setText("32")
    if sp.checkInt(ctx.qt.txAntDiagPlotSetupSensorNumSlideLEdit.text()):
        txAntDiag.plotSetup["nofSensorMeasToShow"] = int(ctx.qt.txAntDiagPlotSetupSensorNumSlideLEdit.text())

    ctx.qt.txAntDiagPlotSetupGraphsPerSlideLEdit.setText("1")
    if sp.checkInt(ctx.qt.txAntDiagPlotSetupGraphsPerSlideLEdit.text()):
        txAntDiag.plotSetup["graphsPerSlide"] = int(ctx.qt.txAntDiagPlotSetupGraphsPerSlideLEdit.text())

    ctx.qt.txAntDiagPlotSetupImageDpiLEdit.setText("220")
    if sp.checkInt(ctx.qt.txAntDiagPlotSetupImageDpiLEdit.text()):
        txAntDiag.plotSetup["imageDpi"] = int(ctx.qt.txAntDiagPlotSetupImageDpiLEdit.text())

    # X-scale auto
    ctx.qt.txAntDiagPlotSetupScalingAutoCheckBox.setChecked(False)
    txAntDiag.plotSetup["xScaleSizeAuto"] = 0

    ctx.qt.txAntDiagPlotSetupScalingXScaleAzLEdit.setText("90")
    ctx.qt.txAntDiagPlotSetupScalingXScaleElLEdit.setText("45")
    if sp.checkDecimal(ctx.qt.txAntDiagPlotSetupScalingXScaleAzLEdit.text()):
        txAntDiag.plotSetup["xScaleSizeAz"] = float(ctx.qt.txAntDiagPlotSetupScalingXScaleAzLEdit.text())
    if sp.checkDecimal(ctx.qt.txAntDiagPlotSetupScalingXScaleElLEdit.text()):
        txAntDiag.plotSetup["xScaleSizeEl"] = float(ctx.qt.txAntDiagPlotSetupScalingXScaleElLEdit.text())

    # Orig/norm graphs
    ctx.qt.txAntDiagPlotSetupScalingOrigGraphsCheckBox.setChecked(True)
    txAntDiag.plotSetup["plotOrigGraphs"] = 1

    ctx.qt.txAntDiagPlotSetupScalingNormGraphsCheckBox.setChecked(True)
    txAntDiag.plotSetup["plotNormGraphs"] = 1

    # Graph config — all on by default
    graphId = 0
    for key in txAntDiag.graphConfig:
        button = ctx.qt.txAntDiagPlotSetupGraphConfGroup.button(graphId)
        txAntDiag.graphConfig[key] = 1
        button.setChecked(True)
        graphId += 1


# ---------------------------------------------------------------------------
# Signal wiring
# ---------------------------------------------------------------------------

def wire(ctx: "AppContext") -> None:
    """Connect all txAntDiag Qt signals to their handlers."""
    ctx.qt.txAntDiagInputSetupAngleGroup.buttonClicked.connect(
        lambda: txAntDiagInputSetupAngleGroupClick(ctx)
    )
    ctx.qt.txAntDiagInputSetupSensorOrientGroup.buttonClicked.connect(
        lambda: txAntDiagInputSetupSensorOrientGroupClick(ctx)
    )
    ctx.qt.txAntDiagInputSetupAzCheckBox.stateChanged.connect(
        lambda: txAntDiagInputSetupAzClick(ctx)
    )
    ctx.qt.txAntDiagInputSetupElCheckBox.stateChanged.connect(
        lambda: txAntDiagInputSetupElClick(ctx)
    )
    ctx.qt.txAntDiagPlotSetupScalingAutoCheckBox.stateChanged.connect(
        lambda: txAntDiagPlotSetupScalingAutoClick(ctx)
    )
    ctx.qt.txAntDiagPlotSetupScalingOrigGraphsCheckBox.stateChanged.connect(
        lambda: txAntDiagPlotSetupScalingOrigGraphsClick(ctx)
    )
    ctx.qt.txAntDiagPlotSetupScalingNormGraphsCheckBox.stateChanged.connect(
        lambda: txAntDiagPlotSetupScalingNormGraphsClick(ctx)
    )
    ctx.qt.txAntDiagPlotSetupGraphConfGroup.buttonClicked.connect(
        lambda btn: txAntDiagPlotSetupGraphConfClick(ctx, btn)
    )
    ctx.qt.txAntDiagStartPushBtn.clicked.connect(
        lambda: txantdiag_data_update_and_evaluation(ctx)
    )
