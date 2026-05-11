---
name: pyside6-gui-patterns
description: Critical patterns, pitfalls and architectural constraints for the Calibration Statistics Tool PySide6 GUI. Use when adding tabs, workers, layouts, constants, or window management.
---

# PySide6 GUI Patterns — Calibration Statistics Tool

## Architecture Overview

- `ui/main_view.py` — owns all Qt widget instances as instance attrs on `MainView`
- `ui/ui_theme.py` — single source of truth: colors, QSS, spacing, HiDPI helpers, `MAX_LOG_ROWS`
- `ui/ui_constants.py` — **re-export shim only**; all tab files do `from ui_constants import *`
- `ui/widgets.py` — reusable widgets (`QTableLogHandler`, `PlotFrame`, dialogs)
- `ui/workers.py` — `QObject`-based workers for all blocking operations
- `ui/tabs/*.py` — module-level widget creation; absorbed into `MainView` via `_absorb(vars(module))`
- `ui/handlers/*.py` — signal handlers; `wire(ctx)` connects signals, `init_widgets(ctx)` sets defaults

## Pitfall: Re-export Chain

**Rule:** Any new constant added to `ui_theme.py` **must also** be added to the explicit re-export list in `ui_constants.py`.

All tab files use `from ui_constants import *` (star-import). If you add `FOO = 42` to `ui_theme.py` but forget `ui_constants.py`, every tab silently gets a `NameError` at runtime.

```python
# ui_constants.py — always keep in sync with ui_theme.py additions
from ui_theme import (
    ...,
    MAX_LOG_ROWS,      # ← must be here for tabs to see it
    configure_hidpi,
    dpi_scale,
)
```

## Pitfall: mainTabWidget Double-Add

`mainTabWidget` is added to `mainSplitter` — **never** also call `mainWidgetLayout.addWidget(self.mainTabWidget)`. That would add it to both, causing blank layout or rendering artifacts.

```python
# WRONG — do not do this:
mainWidgetLayout.addWidget(self.mainTabWidget)  # ← remove if splitter is used

# CORRECT — only via splitter:
self.mainSplitter.addWidget(self.mainTabWidget)
mainWidgetLayout.addWidget(self.mainSplitter)
```

## Pattern: HiDPI Setup

`configure_hidpi()` must be called with `QApplication` (the class) as argument **before** `QApplication()` is instantiated. Calling it after has no effect.

```python
configure_hidpi(QApplication)                          # before instantiation
self.app = QApplication.instance() or QApplication(sys.argv)
```

## Pattern: closeEvent on plain QWidget

`mainWidget` is a `QWidget`, not `QMainWindow`, so you cannot override `closeEvent` directly. Use an event filter:

```python
class _CloseEventFilter(QObject):
    def __init__(self, on_close_cb, parent=None):
        super().__init__(parent)
        self._on_close = on_close_cb

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Close:
            self._on_close()
        return False  # let event propagate

# Install in MainView.__init__:
self._close_filter = _CloseEventFilter(self._save_window_state, self.mainWidget)
self.mainWidget.installEventFilter(self._close_filter)
```

## Pattern: QThread Worker (non-blocking operations)

Use `QObject` subclass moved to `QThread` — **not** `QThread` subclass. This is safer for signal/slot cleanup.

```python
worker = ParseWorker(...)
thread = QThread()
worker.moveToThread(thread)

thread.started.connect(worker.run)
worker.finished.connect(thread.quit)
worker.finished.connect(worker.deleteLater)
thread.finished.connect(thread.deleteLater)

# Disable button, re-enable in finished/error slots
ctx.qt.parseProtParseDataPushBtn.setEnabled(False)
worker.finished.connect(lambda *_: ctx.qt.parseProtParseDataPushBtn.setEnabled(True))
worker.error.connect(lambda _: ctx.qt.parseProtParseDataPushBtn.setEnabled(True))

thread.start()
```

Workers live in `ui/workers.py`: `ParseWorker`, `SysDiagWorker`, `TxAntDiagWorker`, `AntPatWorker`.

**Workers must never touch Qt widgets directly** — only emit signals.

## Pattern: QScrollArea for Heavy Tabs

Wrap heavy tabs (SysDiag, TxAntDiag, AntPat) in a `QScrollArea` **before** passing to `insertTab`. The tab widget reference (`self.sysDiagTab`) stays accessible for signal wiring.

```python
import tabs.sys_diag_tab as _sdt
self._absorb(vars(_sdt))
_scroll = QScrollArea()
_scroll.setWidget(self.sysDiagTab)   # QScrollArea owns the widget
_scroll.setWidgetResizable(True)
self.mainTabWidget.insertTab(1, _scroll, 'System Diagrams')
# self.sysDiagTab is still accessible for wiring
```

## Pattern: Flexible Layouts

Use `setMinimumSize` / `setMinimumWidth` / `setMinimumHeight` instead of `setFixedSize` / `setFixedWidth` / `setFixedHeight` on buttons and tables so the layout can breathe as the window resizes.

```python
# WRONG:
btn.setFixedSize(PUSH_BTN_H_SIZE, PUSH_BTN_V_SIZE)
btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

# CORRECT:
btn.setMinimumSize(PUSH_BTN_H_SIZE, PUSH_BTN_V_SIZE)
btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
```

## Tab Index Map

```
0  Parse Protocols
1  System Diagrams         (QScrollArea-wrapped)
2  Tx-Antenna Diagrams     (QScrollArea-wrapped)
3  (set inside a tab module)
4  Antenna Patterns        (QScrollArea-wrapped)
6  Statistics
8  System Diagrams Interactive
```

## Log Table Cap

`QTableLogHandler.emit()` trims oldest rows when `MAX_LOG_ROWS` (500) is exceeded. Keep `MAX_LOG_ROWS` in `ui_theme.py` and re-export from `ui_constants.py`.
