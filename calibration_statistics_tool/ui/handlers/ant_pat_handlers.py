"""Antenna-Patterns tab signal handlers  (PST-58).

All handler functions previously defined at module level in main.py under
the "## Antenna Patterns" section.

``init_widgets(ctx)`` performs widget initialisation, including building
``antPatTableList`` and initialising ``antPatControl``.
``wire(ctx)``         connects all Qt signals to their handlers (including
the QSignalMapper plumbing for the per-table combos).
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from calibration_statistics_tool.shared import safeparse as sp

if TYPE_CHECKING:  # pragma: no cover
    from calibration_statistics_tool.ui.handlers.app_context import AppContext

from calibration_statistics_tool.shared import logconfig

parseDataLog = logconfig.mainLoadDataLogger.logger

# ---------------------------------------------------------------------------
# Module-level mutable state — populated / reset by init_widgets()
# ---------------------------------------------------------------------------

antPatTableList: list = []
antPatControl: dict = {"version": 0}

# QSignalMapper references — kept alive so the GC cannot collect them
_signal_mappers: dict = {}


# ---------------------------------------------------------------------------
# Internal helper — lazy import to avoid Qt init at module import time
# ---------------------------------------------------------------------------

def _antPat1():
    """Return the antpat_v5_main_v3 module (imported lazily)."""
    from calibration_statistics_tool.antenna_patterns import antpat_v5_main_v3 as _mod  # noqa: PLC0415
    return _mod


# ---------------------------------------------------------------------------
# Pure utility
# ---------------------------------------------------------------------------

def antPatTableLEditParse(inputString: str) -> list:
    """Parse a comma-separated integer string, returning a deduplicated list."""
    separatedList = []
    for char in inputString.split(","):
        if char != "" and sp.checkInt(char):
            separatedList.append(int(char))

    outputList: list = []
    for item in separatedList:
        if item not in outputList:
            outputList.append(item)
    return outputList


# ---------------------------------------------------------------------------
# Per-table combo handlers (dispatched via QSignalMapper in wire())
# ---------------------------------------------------------------------------

def antPatTablePatTypeClick(tabIdx: int, ctx: "AppContext") -> None:
    combo = ctx.qt.antPatTableWidgetsList[tabIdx]["patTypeComboBox"]
    antPatTableList[tabIdx]["patternType"] = combo.currentIndex()
    parseDataLog.debug("Table" + str(tabIdx) + ": " + str(antPatTableList[tabIdx]))


def antPatTableRotAxisClick(tabIdx: int, ctx: "AppContext") -> None:
    combo = ctx.qt.antPatTableWidgetsList[tabIdx]["rotAxisComboBox"]
    antPatTableList[tabIdx]["rotationAxis"] = combo.currentIndex()
    parseDataLog.debug("Table" + str(tabIdx) + ": " + str(antPatTableList[tabIdx]))


def antPatTableGainCalcMethodClick(tabIdx: int, ctx: "AppContext") -> None:
    combo = ctx.qt.antPatTableWidgetsList[tabIdx]["gainCalcMethodComboBox"]
    antPatTableList[tabIdx]["gainCalcMethod"] = combo.currentIndex()
    parseDataLog.debug("Table" + str(tabIdx) + ": " + str(antPatTableList[tabIdx]))


# ---------------------------------------------------------------------------
# Input config — angle / orientation / chirp
# ---------------------------------------------------------------------------

def antPatInputSetupAngleGroupClick(ctx: "AppContext") -> None:
    btnId = ctx.qt.antPatInputConfAngleGroup.checkedId()
    if btnId == 0:
        _antPat1().conf0["targetAngle"] = 1
    elif btnId == 1:
        _antPat1().conf0["targetAngle"] = 0
    parseDataLog.debug("conf0: " + str(_antPat1().conf0))


def antPatInputSetupSensorOrientGroupClick(ctx: "AppContext") -> None:
    btnId = ctx.qt.antPatInputConfSensorOrientGroup.checkedId()
    if btnId == 0:
        _antPat1().conf0["upsideDown"] = 0
    elif btnId == 1:
        _antPat1().conf0["upsideDown"] = 1
    parseDataLog.debug("conf0: " + str(_antPat1().conf0))


def antPatInputConfChirpClick(ctx: "AppContext", btn) -> None:
    btnId   = ctx.qt.antPatInputConfChirpGroup.id(btn)
    chBox   = ctx.qt.antPatInputConfChirpGroup.button(btnId)
    state   = chBox.isChecked()
    dictKey = "chirp" + str(btnId)
    _antPat1().chirpConfig[dictKey] = 1 if state else 0
    parseDataLog.debug("chirpConfig: " + str(_antPat1().chirpConfig))


# ---------------------------------------------------------------------------
# Input config — file-search / name-identifier checkboxes
# ---------------------------------------------------------------------------

def antPatInputConfFileSearchClick(ctx: "AppContext") -> None:
    state = ctx.qt.antPatInputConfFileSearchCheckBox.isChecked()
    enabled = bool(state)
    ctx.qt.antPatTableUpsideDownInfoCheckBox.setEnabled(enabled)
    ctx.qt.antPatTableDiagTypeInfoCheckBox.setEnabled(enabled)


def antPatInputNameIdentifierSelClick(ctx: "AppContext") -> None:
    state = ctx.qt.antPatInputNameIdentifierSelCheckBox.isChecked()
    enabled = bool(state)
    ctx.qt.antPatHeaderNameLEdit.setEnabled(enabled)
    ctx.qt.antPatHeaderIdentifierLEdit.setEnabled(enabled)
    ctx.qt.antPatHeaderIdentifierLabel.setEnabled(enabled)
    ctx.qt.antPatHeaderNameLabel.setEnabled(enabled)


# ---------------------------------------------------------------------------
# Table info checkboxes
# ---------------------------------------------------------------------------

def antPatTableDiagTypeInfoClick(ctx: "AppContext") -> None:
    state = ctx.qt.antPatTableDiagTypeInfoCheckBox.isChecked()
    _antPat1().conf0["diagTypeInfo"] = 1 if state else 0
    parseDataLog.debug("conf0: " + str(_antPat1().conf0))


def antPatTableUpsideDownInfoClick(ctx: "AppContext") -> None:
    state = ctx.qt.antPatTableUpsideDownInfoCheckBox.isChecked()
    _antPat1().conf0["upsideDownInfo"] = 1 if state else 0
    parseDataLog.debug("conf0: " + str(_antPat1().conf0))


# ---------------------------------------------------------------------------
# Output format (JSON / YAML version)
# ---------------------------------------------------------------------------

def antPatInputSetupYAMLGroupClick(ctx: "AppContext") -> None:
    btnId = ctx.qt.antPatInputConfYAMLGroup.checkedId()
    if btnId == 0:
        antPatControl["version"] = 0
        parseDataLog.info("json v1 has been selected")
    elif btnId == 1:
        antPatControl["version"] = 1
        parseDataLog.info("Yaml v1 has been selected")
    elif btnId == 2:
        antPatControl["version"] = 2
        parseDataLog.info("Yaml v2 has been selected")


# ---------------------------------------------------------------------------
# Evaluation orchestrator (wired to antPatStartPushBtn)
# ---------------------------------------------------------------------------

def antpat_data_update_and_evaluation(ctx: "AppContext") -> None:
    """Read widget state, build antPat1 config, then run the evaluation."""
    antPat1 = _antPat1()

    antPat1.conf0["tables"][:]   = []
    antPat1.ptu2InputConfList[:] = []
    antPat1.setup["sensorMusterList"][:] = []

    if ctx.plc.plotSetup["useSensorMuster"] == 1:
        sensorMusterInputList = ctx.qt.parseProtSensorMusterLEdit.text()
        for part in sensorMusterInputList.split(" "):
            if part != "":
                antPat1.setup["sensorMusterList"].append(part)

    antPat1.portData["nofDataTables"] = 0
    ctx.qt.antPatHeaderNameLEdit.setText("Antenna_Pattern_Tables")

    for tabIdx in range(len(ctx.qt.antPatTableWidgetsList)):
        widgets = ctx.qt.antPatTableWidgetsList[tabIdx]

        if sp.checkInt(widgets["nofAppTxAntIdxLEdit"].text()):
            antPatTableList[tabIdx]["nofApplicableTxAnt"] = int(widgets["nofAppTxAntIdxLEdit"].text())

        if sp.checkInt(widgets["nofAppRxAntIdxLEdit"].text()):
            antPatTableList[tabIdx]["nofApplicableRxAnt"] = int(widgets["nofAppRxAntIdxLEdit"].text())

        antPatTableList[tabIdx]["applTxAntInd"] = antPatTableLEditParse(widgets["appTxAntIdxLEdit"].text())
        antPatTableList[tabIdx]["applRxAntInd"] = antPatTableLEditParse(widgets["appRxAntIdxLEdit"].text())

        if widgets["tableCheckBox"].isChecked():
            antPat1.portData["nofDataTables"] += 1
            antPat1.conf0["tables"].append(antPatTableList[tabIdx])

    antPat1.ptu2InputConfList.append(antPat1.conf0)
    parseDataLog.debug("conf0: " + str(antPat1.conf0))
    parseDataLog.debug("ptu2InputConfList: " + str(antPat1.ptu2InputConfList))

    # Only antPat1 (YAML v1) is available — versions 0 and 2 were removed
    antPat1.start_data_evaluation(
        ctx.pc.sysDiagParsedDataDict["parsedDataList"],
        logconfig.antPatLogger,
    )


# ---------------------------------------------------------------------------
# Widget initialisation
# ---------------------------------------------------------------------------

def init_widgets(ctx: "AppContext") -> None:
    """Mirror the top-level antenna-patterns init code from main.py."""
    antPat1 = _antPat1()

    # Reset module-level state
    antPatTableList.clear()
    antPatControl["version"] = 0

    # --- Per-table initialisation ---
    for tabIdx in range(len(ctx.qt.antPatTableWidgetsList)):
        antPatTable: dict = {
            "antenna_pattern_idx": tabIdx,
            "patternType":         0,
            "rotationAxis":        0,
            "nofApplicableTxAnt": 0,
            "nofApplicableRxAnt": 0,
            "applTxAntInd":        [],
            "applRxAntInd":        [],
            "gainCalcMethod":      0,
        }

        widgets = ctx.qt.antPatTableWidgetsList[tabIdx]

        if tabIdx < 4:
            widgets["tableCheckBox"].setChecked(True)

        widgets["patTypeComboBox"].setCurrentIndex(1)
        antPatTable["patternType"] = widgets["patTypeComboBox"].currentIndex()

        widgets["rotAxisComboBox"].setCurrentIndex(1)
        antPatTable["rotationAxis"] = widgets["rotAxisComboBox"].currentIndex()

        widgets["gainCalcMethodComboBox"].setCurrentIndex(1)
        antPatTable["gainCalcMethod"] = widgets["gainCalcMethodComboBox"].currentIndex()

        widgets["nofAppTxAntIdxLEdit"].setText("1")
        if sp.checkInt(widgets["nofAppTxAntIdxLEdit"].text()):
            antPatTable["nofApplicableTxAnt"] = int(widgets["nofAppTxAntIdxLEdit"].text())

        widgets["nofAppRxAntIdxLEdit"].setText("4")
        if sp.checkInt(widgets["nofAppRxAntIdxLEdit"].text()):
            antPatTable["nofApplicableRxAnt"] = int(widgets["nofAppRxAntIdxLEdit"].text())

        widgets["appTxAntIdxLEdit"].setText("0")
        widgets["appRxAntIdxLEdit"].setText("0, 1, 2, 3")

        antPatTableList.append(antPatTable)

    # --- Header fields ---
    ctx.qt.antPatHeaderNameLEdit.setText("Antenna_Pattern_Tables")
    ctx.qt.antPatHeaderNameLEdit.setEnabled(False)
    ctx.qt.antPatHeaderIdentifierLEdit.setText("36")
    ctx.qt.antPatHeaderIdentifierLEdit.setEnabled(False)
    ctx.qt.antPatHeaderIdentifierLabel.setEnabled(False)
    ctx.qt.antPatHeaderNameLabel.setEnabled(False)

    ctx.qt.antPatHeaderMajVerLEdit.setText("2")
    ctx.qt.antPatHeaderMinVerLEdit.setText("0")
    ctx.qt.antPatHeaderYearLEdit.setText("2020")
    ctx.qt.antPatHeaderMonthLEdit.setText("1")
    ctx.qt.antPatHeaderDayLEdit.setText("28")
    ctx.qt.antPatHeaderRfeGenLEdit.setText("28")
    ctx.qt.antPatHeaderRfeModLEdit.setText("0")
    ctx.qt.antPatHeaderRfeRevLEdit.setText("0")

    # --- Input config defaults ---
    ctx.qt.antPatInputConfAngleSetupRadio1.setChecked(True)
    ctx.qt.antPatInputConfAngleSetupRadio2.setChecked(False)
    antPat1.conf0["targetAngle"] = 1

    ctx.qt.antPatInputConfSensorOrientRadio1.setChecked(True)
    ctx.qt.antPatInputConfSensorOrientRadio1.setChecked(False)  # preserve main.py typo
    antPat1.conf0["upsideDown"] = 0

    ctx.qt.antPatInputConfChirp0CheckBox.setChecked(True)
    ctx.qt.antPatInputConfChirp1CheckBox.setChecked(False)
    ctx.qt.antPatInputConfChirp2CheckBox.setChecked(False)
    ctx.qt.antPatInputConfChirp3CheckBox.setChecked(False)
    antPat1.chirpConfig["chirp0"] = 1
    antPat1.chirpConfig["chirp1"] = 0
    antPat1.chirpConfig["chirp2"] = 0
    antPat1.chirpConfig["chirp3"] = 0

    ctx.qt.antPatInputConfFileSearchCheckBox.setChecked(False)
    ctx.qt.antPatInputNameIdentifierSelCheckBox.setChecked(False)

    ctx.qt.antPatTableDiagTypeInfoCheckBox.setChecked(True)
    antPat1.conf0["diagTypeInfo"] = 1
    ctx.qt.antPatTableDiagTypeInfoCheckBox.setEnabled(False)

    ctx.qt.antPatTableUpsideDownInfoCheckBox.setChecked(True)
    antPat1.conf0["upsideDownInfo"] = 1
    ctx.qt.antPatTableUpsideDownInfoCheckBox.setEnabled(False)

    # --- Output format ---
    ctx.qt.antPatInputConfYAMLSetupRadio1.setChecked(True)
    ctx.qt.antPatInputConfYAMLSetupRadio2.setChecked(False)
    ctx.qt.antPatInputConfYAMLSetupRadio3.setChecked(False)


# ---------------------------------------------------------------------------
# Signal wiring
# ---------------------------------------------------------------------------

def wire(ctx: "AppContext") -> None:
    """Connect all antenna-patterns Qt signals to their handlers."""
    from PySide6.QtCore import QSignalMapper  # noqa: PLC0415

    # --- Per-table combo QSignalMappers ---
    patTypeMapper = QSignalMapper()
    patTypeMapper.mappedInt.connect(lambda idx: antPatTablePatTypeClick(idx, ctx))
    _signal_mappers["patTypeMapper"] = patTypeMapper

    rotAxisMapper = QSignalMapper()
    rotAxisMapper.mappedInt.connect(lambda idx: antPatTableRotAxisClick(idx, ctx))
    _signal_mappers["rotAxisMapper"] = rotAxisMapper

    gainCalcMapper = QSignalMapper()
    gainCalcMapper.mappedInt.connect(lambda idx: antPatTableGainCalcMethodClick(idx, ctx))
    _signal_mappers["gainCalcMapper"] = gainCalcMapper

    for tabIdx in range(len(ctx.qt.antPatTableWidgetsList)):
        widgets = ctx.qt.antPatTableWidgetsList[tabIdx]

        widgets["patTypeComboBox"].currentIndexChanged.connect(patTypeMapper.map)
        patTypeMapper.setMapping(widgets["patTypeComboBox"], tabIdx)

        widgets["rotAxisComboBox"].currentIndexChanged.connect(rotAxisMapper.map)
        rotAxisMapper.setMapping(widgets["rotAxisComboBox"], tabIdx)

        widgets["gainCalcMethodComboBox"].currentIndexChanged.connect(gainCalcMapper.map)
        gainCalcMapper.setMapping(widgets["gainCalcMethodComboBox"], tabIdx)

    # --- Config checkboxes & radio groups ---
    ctx.qt.antPatInputConfFileSearchCheckBox.stateChanged.connect(
        lambda: antPatInputConfFileSearchClick(ctx)
    )
    ctx.qt.antPatInputNameIdentifierSelCheckBox.stateChanged.connect(
        lambda: antPatInputNameIdentifierSelClick(ctx)
    )
    ctx.qt.antPatTableUpsideDownInfoCheckBox.stateChanged.connect(
        lambda: antPatTableUpsideDownInfoClick(ctx)
    )
    ctx.qt.antPatTableDiagTypeInfoCheckBox.stateChanged.connect(
        lambda: antPatTableDiagTypeInfoClick(ctx)
    )
    ctx.qt.antPatInputConfChirpGroup.buttonClicked.connect(
        lambda btn: antPatInputConfChirpClick(ctx, btn)
    )
    ctx.qt.antPatInputConfAngleGroup.buttonClicked.connect(
        lambda: antPatInputSetupAngleGroupClick(ctx)
    )
    ctx.qt.antPatInputConfSensorOrientGroup.buttonClicked.connect(
        lambda: antPatInputSetupSensorOrientGroupClick(ctx)
    )
    ctx.qt.antPatInputConfYAMLGroup.buttonClicked.connect(
        lambda: antPatInputSetupYAMLGroupClick(ctx)
    )

    # --- Start button ---
    ctx.qt.antPatStartPushBtn.clicked.connect(
        lambda: antpat_data_update_and_evaluation(ctx)
    )
