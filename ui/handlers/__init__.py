"""Handler sub-package.

Provides ``AppContext`` and the three handler modules created in PST-55/56/57:
  - parse_handlers       — Parse tab
  - sys_diag_handlers    — System-Diagrams tab
  - tx_ant_diag_handlers — Tx-Antenna-Diagrams tab
"""
from ui.handlers.app_context import AppContext

__all__ = ["AppContext"]
