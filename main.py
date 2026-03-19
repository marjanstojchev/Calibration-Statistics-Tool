"""PST-66: main.py rewritten as a thin wiring file.

Responsibilities:
  1. sys.path setup
  2. Qt platform plugin env var + MainView creation
  3. Logger setup
  4. ParseController / PlotController instantiation
  5. antSysDiag dict bindings
  6. Misc startup tasks (setcurves label, merge output dir)
  7. AppContext creation + handler init_widgets / wire calls
  8. run() entry point

All handler logic lives in ui/handlers/*.py.
"""
import os
import sys

_root = os.path.dirname(os.path.abspath(__file__))
for _subdir in ['shared', 'ui', 'system_diagrams', 'tx_diagrams', 'antenna_patterns']:
    _path = os.path.join(_root, _subdir)
    if _path not in sys.path:
        sys.path.insert(0, _path)

import logconfig
from shared.parse_controller import ParseController
from shared.plot_controller import PlotController
import AntennaSystemDiagrams as antSysDiag
import auxiliary as aux
import PySide6

dirname = os.path.dirname(PySide6.__file__)
print(dirname)
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
print(plugin_path)
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path

from ui.main_view import MainView as _MainView
view = _MainView()
qt = view  # backward-compatible alias: all qt.<widget> calls delegate to MainView

# ---------------------------------------------------------------------------
# Loggers
# ---------------------------------------------------------------------------

parseDataLog = logconfig.mainLoadDataLogger.logger
logconfig.mainLoadDataLogger.addTableHandler(qt.mainLogTableHandler)
errorStatus, errorSting = logconfig.mainLoadDataLogger.addFileHandler(logconfig.mainLoadDataLogFilePath, 'w+')
if errorStatus == 1:
    parseDataLog.warning(errorSting)

sysDiagLog = logconfig.antSysDiagLogger.logger
errorStatus, errorSting = logconfig.antSysDiagLogger.addFileHandler(logconfig.antSysDiagLogFilePath, 'w+')
if errorStatus == 1:
    sysDiagLog.warning(errorSting)
logconfig.antSysDiagLogger.addTableHandler(qt.mainLogTableHandler)

txAntDiagLog = logconfig.txAntDiagLogger.logger
errorStatus, errorSting = logconfig.txAntDiagLogger.addFileHandler(logconfig.txAntDiagLogFilePath, 'w+')
if errorStatus == 1:
    txAntDiagLog.warning(errorSting)
logconfig.txAntDiagLogger.addTableHandler(qt.mainLogTableHandler)

antpatLog = logconfig.antPatLogger.logger
errorStatus, errorSting = logconfig.antPatLogger.addFileHandler(logconfig.antPatLogFilePath, 'w+')
if errorStatus == 1:
    antpatLog.warning(errorSting)
logconfig.antPatLogger.addTableHandler(qt.mainLogTableHandler)

# ---------------------------------------------------------------------------
# Controllers
# ---------------------------------------------------------------------------

pc = ParseController()
plc = PlotController()

# Bind antSysDiag state dicts to plc shared dict objects so that
# plc.set_*() mutations and antSysDiag reads/writes operate on the same data.
antSysDiag.plotSetup       = plc.plotSetup
antSysDiag.graphConfig     = plc.graphConfig
antSysDiag.chirpConfig     = plc.chirpConfig
antSysDiag.diagramConfig   = plc.diagramConfig
antSysDiag.twoGraphConf1   = plc.twoGraphConf1
antSysDiag.twoGraphConf2   = plc.twoGraphConf2
antSysDiag.threeGraphConf1 = plc.threeGraphConf1
antSysDiag.threeGraphConf2 = plc.threeGraphConf2
antSysDiag.threeGraphConf3 = plc.threeGraphConf3
antSysDiag.fourGraphConf1  = plc.fourGraphConf1
antSysDiag.fourGraphConf2  = plc.fourGraphConf2
antSysDiag.fourGraphConf3  = plc.fourGraphConf3
antSysDiag.AllGraphsConf1  = plc.AllGraphsConf1
antSysDiag.AllGraphsConf2  = plc.AllGraphsConf2
antSysDiag.AllGraphsConf3  = plc.AllGraphsConf3
antSysDiag.plotWindowConfig = plc.plotWindowConfig

# ---------------------------------------------------------------------------
# Misc startup tasks (setcurves label + merge output dir)
# ---------------------------------------------------------------------------

qt.setCurvesInputConfPathLabel.setToolTip(aux.setcurvesinputconffilepath)
qt.setCurvesInputConfPathLabel.setText(aux.setcurvesinputconffilepath)

aux.createDirectory(aux.mergeOutputPath)
aux.clearAll(aux.mergeOutputPath)
_merge_combine = os.path.join(aux.mergeOutputPath, 'combine.pptx')
aux.copyFile(_merge_combine, _merge_combine)

# ---------------------------------------------------------------------------
# Handler wiring
# ---------------------------------------------------------------------------

from ui.handlers.app_context import AppContext
import ui.handlers.parse_handlers       as parse_h
import ui.handlers.sys_diag_handlers    as sys_diag_h
import ui.handlers.tx_ant_diag_handlers as tx_h
import ui.handlers.ant_pat_handlers     as ant_h

ctx = AppContext(qt=qt, mv=view, plc=plc, pc=pc)

parse_h.init_widgets(ctx)
sys_diag_h.init_widgets(ctx)
tx_h.init_widgets(ctx)
ant_h.init_widgets(ctx)

parse_h.wire(ctx)
sys_diag_h.wire(ctx)
tx_h.wire(ctx)
ant_h.wire(ctx)

qt.parseProtMergePPTXBtn.clicked.connect(lambda: None)  # merge: stub (feature removed)

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def run() -> None:
    """Entry point for installed package."""
    sys.exit(qt.app.exec())

if __name__ == '__main__':
    run()
