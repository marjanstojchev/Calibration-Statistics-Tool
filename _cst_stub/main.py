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
# Installed layout:  site-packages/calibration_statistics_tool/{shared,ui,...}
# Source layout:     repo/{shared,ui,...}  (CWD on sys.path handles package imports)
_cst = os.path.join(_root, 'calibration_statistics_tool')
_base = _cst if os.path.isdir(os.path.join(_cst, 'shared')) else _root
if _base != _root and _base not in sys.path:
    sys.path.insert(0, _base)   # lets 'from shared.X import Y' resolve
for _subdir in ['shared', 'ui', 'system_diagrams', 'tx_diagrams', 'antenna_patterns']:
    _path = os.path.join(_base, _subdir)
    if _path not in sys.path:
        sys.path.insert(0, _path)

import logconfig
from shared.parse_controller import ParseController
from shared.plot_controller import PlotController
import auxiliary as aux
import user_paths as _up

# ── Startup: config file location + onboarding notice ───────────────────────
print(f"\n{'─' * 60}")
print(f"  Calibration Statistics Tool")
print(f"{'─' * 60}")
print(f"  Config file : {_up.PATHS_FILE}")
print(f"  Output dir  : {_up.output_base}")
_unconfigured = {
    'input_protocol_dir': _up.input_protocol_dir,
    'input_ptu_dir':      _up.input_ptu_dir,
    'input_tx_ant_dir':   _up.input_tx_ant_dir,
}
_missing = [k for k, v in _unconfigured.items() if not v]
if _missing:
    print(f"\n  NOTE: The following input directories are not set in paths.json.")
    print(f"  File dialogs will open at your home folder until you configure them:")
    for _k in _missing:
        print(f"    - {_k}")
    print(f"\n  Edit the config file above to set them.")
else:
    print(f"\n  All input directories are configured.")
print(f"{'─' * 60}\n")
del _unconfigured, _missing
# ────────────────────────────────────────────────────────────────────────────

import PySide6

dirname = os.path.dirname(PySide6.__file__)
print(dirname)
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
print(plugin_path)
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path

from ui.main_view import MainView as _MainView
import pyside_qtgui as _pqg
view = _MainView()
_pqg._register(view)   # PST-67: must happen BEFORE AntennaSystemDiagrams is imported
                       # (AntennaSystemDiagrams.py accesses qt.SysDiaInterTableParam at module level)
import AntennaSystemDiagrams as antSysDiag
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
aux.createDirectory(aux.huellKurvenOutputPath)
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
import ui.handlers.stats_handlers       as stats_h
import ui.handlers.hullkurven_handlers  as hull_h

ctx = AppContext(qt=qt, mv=view, plc=plc, pc=pc)

parse_h.init_widgets(ctx)
sys_diag_h.init_widgets(ctx)
tx_h.init_widgets(ctx)
ant_h.init_widgets(ctx)
stats_h.init_widgets(ctx)
hull_h.init_widgets(ctx)

parse_h.wire(ctx)
sys_diag_h.wire(ctx)
tx_h.wire(ctx)
ant_h.wire(ctx)
stats_h.wire(ctx)
hull_h.wire(ctx)

qt.parseProtMergePPTXBtn.clicked.connect(lambda: None)  # merge: stub (feature removed)

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def run() -> None:
    """Entry point for installed package."""
    sys.exit(qt.app.exec())

if __name__ == '__main__':
    run()
