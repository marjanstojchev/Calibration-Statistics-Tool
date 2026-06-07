"""Hullkurven (Envelope Curves) tab signal handlers — Epic 2.

``init_widgets(ctx)`` performs widget initialisation.
``wire(ctx)``         connects all Qt signals to their handlers.
"""
from __future__ import annotations

import os
import threading
from typing import TYPE_CHECKING

from PySide6.QtCore import QTimer

from calibration_statistics_tool.shared import safeparse as sp
from calibration_statistics_tool.shared import auxiliary as aux
from calibration_statistics_tool.shared import huellkurven_data_processing as hdp

if TYPE_CHECKING:  # pragma: no cover
    from calibration_statistics_tool.ui.handlers.app_context import AppContext

import logging
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Input Setup — Az / El checkboxes
# ---------------------------------------------------------------------------

def hullkurvenInputSetupAzClick(ctx: "AppContext") -> None:
    state = ctx.qt.hullkurvenInputSetupAzCheckBox.isChecked()
    ctx.plc.hullkurvenDataConf['AzDiag'] = 1 if state else 0
    log.debug("hullkurvenDataConf: %s", ctx.plc.hullkurvenDataConf)


def hullkurvenInputSetupElClick(ctx: "AppContext") -> None:
    state = ctx.qt.hullkurvenInputSetupElCheckBox.isChecked()
    ctx.plc.hullkurvenDataConf['ElDiag'] = 1 if state else 0
    log.debug("hullkurvenDataConf: %s", ctx.plc.hullkurvenDataConf)


# ---------------------------------------------------------------------------
# Plot Setup — X-Scale auto checkbox
# ---------------------------------------------------------------------------

def hullkurvenPlotSetupXScaleAutoClick(ctx: "AppContext") -> None:
    state = ctx.qt.hullkurvenPlotSetupXScaleAutoCheckBox.isChecked()
    ctx.plc.hullkurvenPlotSetup['xScaleSizeAuto'] = 1 if state else 0
    log.debug("hullkurvenPlotSetup: %s", ctx.plc.hullkurvenPlotSetup)


# ---------------------------------------------------------------------------
# Evaluation orchestrator (wired to hullkurvenStartPushBtn)
# ---------------------------------------------------------------------------

def hullkurven_start(ctx: "AppContext") -> None:
    plc = ctx.plc

    if sp.checkInt(ctx.qt.hullkurvenInputSetupMinSigmaLEdit.text()):
        plc.hullkurvenDataConf['minSigma'] = int(ctx.qt.hullkurvenInputSetupMinSigmaLEdit.text())

    if sp.checkInt(ctx.qt.hullkurvenInputSetupMaxSigmaLEdit.text()):
        plc.hullkurvenDataConf['maxSigma'] = int(ctx.qt.hullkurvenInputSetupMaxSigmaLEdit.text())

    patternMethodId = ctx.qt.hullkurvenInputSetupPatternMethodGroup.checkedId()
    if patternMethodId >= 0:
        plc.hullkurvenDataConf['patternLimitsMethod'] = patternMethodId

    if sp.checkDecimal(ctx.qt.hullkurvenPlotSetupXScaleAzLEdit.text()):
        plc.hullkurvenPlotSetup['xScaleSizeAz'] = float(ctx.qt.hullkurvenPlotSetupXScaleAzLEdit.text())

    if sp.checkDecimal(ctx.qt.hullkurvenPlotSetupXScaleElLEdit.text()):
        plc.hullkurvenPlotSetup['xScaleSizeEl'] = float(ctx.qt.hullkurvenPlotSetupXScaleElLEdit.text())

    log.info("Hullkurven: start evaluation requested")

    VERSION = 1
    commentsDict = {
        'version': (
            ' // Pattern calc: Method 0 = Factor*StdDev diff from median + reserve dB;'
            ' Method 1 = StdDev diff from max/min.'
        ),
    }

    parseDataList = ctx.pc.separatePtu2ParsedDataDict['parsedDataList']
    if not parseDataList:
        log.error("Hullkurven: No parsed PTU2 files found. Load PTU2 files first.")
        return

    chirpConfig = plc.chirpConfig
    diagramConfig = plc.diagramConfig
    diagramConfigList = plc.diagramConfigList
    dataConf = plc.hullkurvenDataConf

    inputConfig = {
        'diagTypeInfo':   1,
        'targetAngle':    plc.plotSetup.get('targetAngle', 1),
        'upsideDown':     plc.plotSetup.get('upsideDown', 0),
        'upsideDownInfo': 1,
        'useSensorMuster': plc.plotSetup.get('useSensorMuster', 0),
        'sensorMusterList': plc.plotSetup.get('sensorMusterList', []),
    }

    # Prepare output directory
    createDirStatus, createDirString = aux.createDirectory(aux.huellKurvenOutputPath)
    if not createDirStatus:
        log.error("Hullkurven: %s", createDirString)
        return
    clearStatus, clearString = aux.clearAll(aux.huellKurvenOutputPath)
    if not clearStatus:
        log.warning("Hullkurven: %s", clearString)

    confChirpList = hdp.getConfChirpList(chirpConfig)
    if not confChirpList:
        log.error("Hullkurven: No active chirps configured.")
        return

    antennaTypesList = hdp.getAntennaTypesList(parseDataList)
    if not antennaTypesList:
        log.error("Hullkurven: Empty antenna types list.")
        return

    log.info("Hullkurven: antenna types: %s", antennaTypesList)

    ctx.qt.hullkurvenStartPushBtn.setEnabled(False)

    def _worker() -> None:
        try:
            for antennaType in antennaTypesList:
                antTypeOutputPath = os.path.join(aux.huellKurvenOutputPath, 'AntType' + str(antennaType))
                createDirStatus, createDirString = aux.createDirectory(antTypeOutputPath)
                if not createDirStatus:
                    log.error("Hullkurven: %s", createDirString)
                    return

                ptu2ListPerAntennaType = hdp.getPtu2ListPerAntennaType(antennaType, parseDataList)
                angleSetupList = hdp.setAngleSetupList(inputConfig, ptu2ListPerAntennaType)
                if not angleSetupList:
                    log.error("Hullkurven: Empty angle setup list for AntType %s.", antennaType)
                    continue

                for angleSetupIdx in range(len(angleSetupList)):
                    angleSetup = angleSetupList[angleSetupIdx]
                    angleSetupStr = (
                        'NofPts=' + str(angleSetup.nofAnglePoints)
                        + '_StepSize=' + str(angleSetup.angleStepSize)
                        + '_RefPt=' + str(angleSetup.refAnglePoint)
                    )
                    log.info("Hullkurven: AntType%s - %s - inputConfig: %s", antennaType, angleSetupStr, inputConfig)

                    angleOutputPath = os.path.join(antTypeOutputPath, angleSetupStr)
                    createDirStatus, createDirString = aux.createDirectory(angleOutputPath)
                    if not createDirStatus:
                        log.error("Hullkurven: %s", createDirString)
                        return

                    confPtu2List = hdp.getConfiguredPtu2Files(ptu2ListPerAntennaType, angleSetup, inputConfig)
                    if not confPtu2List:
                        log.warning("Hullkurven: No configured PTU2 files for %s.", angleSetupStr)
                        continue

                    desiredDiagramList = hdp.getDesiredDiagramsList(
                        diagramConfig, diagramConfigList, antennaType, confPtu2List
                    )
                    if not desiredDiagramList:
                        log.warning("Hullkurven: No desired diagrams for AntType%s.", antennaType)
                        continue

                    centFreqDictList: list = []

                    for diagListIdx in range(len(desiredDiagramList)):
                        for chirp in confChirpList:
                            diagNum = desiredDiagramList[diagListIdx]['diagramNum']
                            avgFreq = hdp.getAvgFreqPerDiagram(chirp, diagNum, confPtu2List)
                            minFreq = hdp.getMinFreqPerDiagram(chirp, diagNum, confPtu2List)
                            maxFreq = hdp.getMaxFreqPerDiagram(chirp, diagNum, confPtu2List)
                            centFreqDict = {
                                'avgFreqMHz':    format(round(avgFreq / 1e6, 4), '.2f'),
                                'avgFreqGHz':    format(round(avgFreq / 1e9, 4), '.2f'),
                                'posFreqDevMHz': format(round((maxFreq - avgFreq) / 1e6, 4), '.2f'),
                                'negFreqDevMHz': format(round((avgFreq - minFreq) / 1e6, 4), '.2f'),
                                'diagNum': diagNum,
                                'chirp':   chirp,
                            }
                            centFreqDictList.append(centFreqDict)

                            log.info(
                                "Hullkurven: Diagram%s Chirp%s - %s GHz",
                                diagNum, chirp, centFreqDict['avgFreqGHz'],
                            )

                            if angleSetup.diagType == 'Az':
                                if dataConf['AzDiag'] == 1:
                                    log.info("Hullkurven: Creating Az limits - Diagram%s Chirp%s", diagNum, chirp)
                                    limitsData = hdp.createLimitsData(
                                        VERSION, commentsDict, desiredDiagramList, diagListIdx, chirp,
                                        antennaType, confPtu2List, angleSetup, centFreqDictList,
                                        'Az', inputConfig, chirpConfig, dataConf, write_output=True,
                                    )
                                    if limitsData is not None:
                                        hdp.savePlotImage(limitsData, aux.huellKurvenOutputPath)
                            elif angleSetup.diagType == 'El':
                                if dataConf['ElDiag'] == 1:
                                    log.info("Hullkurven: Creating El limits - Diagram%s Chirp%s", diagNum, chirp)
                                    limitsData = hdp.createLimitsData(
                                        VERSION, commentsDict, desiredDiagramList, diagListIdx, chirp,
                                        antennaType, confPtu2List, angleSetup, centFreqDictList,
                                        'El', inputConfig, chirpConfig, dataConf, write_output=True,
                                    )
                                    if limitsData is not None:
                                        hdp.savePlotImage(limitsData, aux.huellKurvenOutputPath)
                            else:
                                if dataConf['AzDiag'] == 1:
                                    log.info("Hullkurven: Creating Az limits (no diagType) - Diagram%s Chirp%s", diagNum, chirp)
                                    limitsData = hdp.createLimitsData(
                                        VERSION, commentsDict, desiredDiagramList, diagListIdx, chirp,
                                        antennaType, confPtu2List, angleSetup, centFreqDictList,
                                        'Az', inputConfig, chirpConfig, dataConf, write_output=True,
                                    )
                                    if limitsData is not None:
                                        hdp.savePlotImage(limitsData, aux.huellKurvenOutputPath)
                                if dataConf['ElDiag'] == 1:
                                    log.info("Hullkurven: Creating El limits (no diagType) - Diagram%s Chirp%s", diagNum, chirp)
                                    limitsData = hdp.createLimitsData(
                                        VERSION, commentsDict, desiredDiagramList, diagListIdx, chirp,
                                        antennaType, confPtu2List, angleSetup, centFreqDictList,
                                        'El', inputConfig, chirpConfig, dataConf, write_output=True,
                                    )
                                    if limitsData is not None:
                                        hdp.savePlotImage(limitsData, aux.huellKurvenOutputPath)

            log.info("Hullkurven: evaluation complete.")
        except Exception:
            log.exception("Hullkurven: unhandled error in worker thread")
        finally:
            QTimer.singleShot(0, ctx.qt.hullkurvenStartPushBtn,
                              lambda: ctx.qt.hullkurvenStartPushBtn.setEnabled(True))

    threading.Thread(target=_worker, daemon=True).start()


# ---------------------------------------------------------------------------
# Widget initialisation
# ---------------------------------------------------------------------------

def init_widgets(ctx: "AppContext") -> None:
    """Initialise hullkurven tab widgets and sync defaults into plc."""

    plc = ctx.plc

    # --- Patch: assign all hullkurven widgets to ctx.qt so handler code works ---

    # Az checked, El unchecked by default
    ctx.qt.hullkurvenInputSetupAzCheckBox.setChecked(True)
    ctx.qt.hullkurvenInputSetupElCheckBox.setChecked(False)
    plc.hullkurvenDataConf['AzDiag'] = 1
    plc.hullkurvenDataConf['ElDiag'] = 0

    # Sigma defaults
    ctx.qt.hullkurvenInputSetupMinSigmaLEdit.setText("-10")
    ctx.qt.hullkurvenInputSetupMaxSigmaLEdit.setText("10")
    if sp.checkInt(ctx.qt.hullkurvenInputSetupMinSigmaLEdit.text()):
        plc.hullkurvenDataConf['minSigma'] = int(ctx.qt.hullkurvenInputSetupMinSigmaLEdit.text())
    if sp.checkInt(ctx.qt.hullkurvenInputSetupMaxSigmaLEdit.text()):
        plc.hullkurvenDataConf['maxSigma'] = int(ctx.qt.hullkurvenInputSetupMaxSigmaLEdit.text())

    # Pattern method: Sigma-based (0) by default
    ctx.qt.hullkurvenInputSetupPatternMethodSigmaRadio.setChecked(True)
    ctx.qt.hullkurvenInputSetupPatternMethodMinMaxRadio.setChecked(False)
    plc.hullkurvenDataConf['patternLimitsMethod'] = 0

    # X-Scale auto off by default
    ctx.qt.hullkurvenPlotSetupXScaleAutoCheckBox.setChecked(False)
    plc.hullkurvenPlotSetup['xScaleSizeAuto'] = 0

    # X-Scale Az/El defaults
    ctx.qt.hullkurvenPlotSetupXScaleAzLEdit.setText("90")
    ctx.qt.hullkurvenPlotSetupXScaleElLEdit.setText("45")
    if sp.checkDecimal(ctx.qt.hullkurvenPlotSetupXScaleAzLEdit.text()):
        plc.hullkurvenPlotSetup['xScaleSizeAz'] = float(ctx.qt.hullkurvenPlotSetupXScaleAzLEdit.text())
    if sp.checkDecimal(ctx.qt.hullkurvenPlotSetupXScaleElLEdit.text()):
        plc.hullkurvenPlotSetup['xScaleSizeEl'] = float(ctx.qt.hullkurvenPlotSetupXScaleElLEdit.text())


# ---------------------------------------------------------------------------
# Signal wiring
# ---------------------------------------------------------------------------

def wire(ctx: "AppContext") -> None:
    """Connect all hullkurven Qt signals to their handlers."""
    ctx.qt.hullkurvenInputSetupAzCheckBox.stateChanged.connect(
        lambda: hullkurvenInputSetupAzClick(ctx)
    )
    ctx.qt.hullkurvenInputSetupElCheckBox.stateChanged.connect(
        lambda: hullkurvenInputSetupElClick(ctx)
    )
    ctx.qt.hullkurvenPlotSetupXScaleAutoCheckBox.stateChanged.connect(
        lambda: hullkurvenPlotSetupXScaleAutoClick(ctx)
    )
    ctx.qt.hullkurvenInputSetupPatternMethodGroup.buttonClicked.connect(
        lambda: _hullkurvenPatternMethodClick(ctx)
    )
    ctx.qt.hullkurvenStartPushBtn.clicked.connect(
        lambda: hullkurven_start(ctx)
    )


def _hullkurvenPatternMethodClick(ctx: "AppContext") -> None:
    btn_id = ctx.qt.hullkurvenInputSetupPatternMethodGroup.checkedId()
    if btn_id >= 0:
        ctx.plc.hullkurvenDataConf['patternLimitsMethod'] = btn_id
    log.debug("hullkurvenDataConf: %s", ctx.plc.hullkurvenDataConf)
