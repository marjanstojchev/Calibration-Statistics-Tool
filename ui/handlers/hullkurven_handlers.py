"""Hullkurven (Envelope Curves) tab signal handlers — Epic 2.

``init_widgets(ctx)`` performs widget initialisation.
``wire(ctx)``         connects all Qt signals to their handlers.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from shared import safeparse as sp
from shared import auxiliary as aux

if TYPE_CHECKING:  # pragma: no cover
    from ui.handlers.app_context import AppContext

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


# ---------------------------------------------------------------------------
# Widget initialisation
# ---------------------------------------------------------------------------

def init_widgets(ctx: "AppContext") -> None:
    """Initialise hullkurven tab widgets and sync defaults into plc."""
    plc = ctx.plc

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
