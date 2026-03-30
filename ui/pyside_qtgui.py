"""PST-67: Backward-compatibility shim for pyside_qtgui.

AntennaSystemDiagrams does ``import pyside_qtgui as qt`` and uses:
  - ``qt.QTableWidgetItem``, ``qt.Qt``, ``qt.QHeaderView``  (Qt classes)
  - ``qt.SysDiaInterPlotFrame``, ``qt.mainTabWidget``, …    (widget attrs)

Keeping the PySide6 star-imports here satisfies the Qt-class references.
Widget attribute references are delegated to the registered MainView instance
via module-level ``__getattr__``.
"""
from PySide6.QtWidgets import *  # noqa: F401,F403
from PySide6.QtGui import *      # noqa: F401,F403
from PySide6.QtCore import *     # noqa: F401,F403
from PySide6.QtUiTools import *  # noqa: F401,F403

_view = None


def _register(view) -> None:
    """Register the MainView instance so widget attrs can be delegated."""
    global _view
    _view = view


def __getattr__(name: str):
    """Delegate unknown attribute lookups to the registered MainView."""
    if _view is not None:
        try:
            return getattr(_view, name)
        except AttributeError:
            pass
    raise AttributeError(f"pyside_qtgui: no attribute {name!r}")
