"""PST-67: MainView — proper class with all widget construction in __init__.

Replaces the module-proxy pattern (PST-47) with a true class that owns the
QApplication and all widget references as instance attributes.
pyside_qtgui.py is now a backward-compat shim for AntennaSystemDiagrams.
"""
from __future__ import annotations

import os
import sys

_ui_dir = os.path.dirname(os.path.abspath(__file__))
if _ui_dir not in sys.path:
    sys.path.insert(0, _ui_dir)

from PySide6.QtWidgets import (
    QApplication, QFrame, QLabel, QPushButton, QWidget, QProgressBar,
    QTableWidget, QTableWidgetItem, QTabWidget, QGroupBox, QCheckBox,
    QHeaderView, QFileDialog, QComboBox, QRadioButton, QLineEdit,
    QDialog, QDialogButtonBox, QGraphicsDropShadowEffect, QButtonGroup,
    QStyledItemDelegate, QCompleter, QVBoxLayout, QHBoxLayout, QGridLayout,
    QSizePolicy, QSplitter, QScrollArea,
)
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtUiTools import *
import logging
import time
import enum
import numpy as np
import plotdata

from ui_constants import *
from ui_theme import (
    apply_theme, configure_hidpi,
    WINDOW_TITLE, WINDOW_MIN_W, WINDOW_MIN_H,
    MARGINS_MAIN,
    ThemeManager, get_theme_manager,
    _build_ant_pat_table_style, _build_plot_frame_style,
)

_UI_DESIGN_CONFIG = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "config", "ui_design_config.json",
)
from widgets import (
    getGraphColor, show_datapoints, Match,
    dialogLEditErrorStyle, dialogLEditCorrectStyle,
    dialogLabelErrorStyle, dialogLabelCorrectStyle,
    LimitsGroupsSaveDialog, TableItemCompleter,
    PlotFrame, PlotFrameSysDia, QTableLogHandler,
)


class _CloseEventFilter(QObject):
    """QObject event filter that intercepts QEvent.Close on mainWidget."""

    def __init__(self, on_close_cb, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._on_close = on_close_cb

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.Close:
            self._on_close()
        return False  # let the event propagate normally


class _LogDragHandle(QFrame):
    """Small grip widget that detaches and reattaches the log panel by drag."""

    def __init__(self, on_start, on_move, on_finish, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._on_start = on_start
        self._on_move = on_move
        self._on_finish = on_finish
        self._press_pos: QPoint | None = None
        self._drag_active = False
        self.setObjectName('LogDragHandle')
        self.setCursor(Qt.SizeAllCursor)
        self.setToolTip('Drag to detach the log window. Drop it back on the lower app area to attach.')
        self.setFixedSize(34, PUSH_BTN_V_SIZE)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self._press_pos = event.globalPosition().toPoint()
            self._drag_active = False
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if self._press_pos is None:
            super().mouseMoveEvent(event)
            return

        global_pos = event.globalPosition().toPoint()
        if not self._drag_active:
            distance = (global_pos - self._press_pos).manhattanLength()
            if distance < QApplication.startDragDistance():
                super().mouseMoveEvent(event)
                return
            self._drag_active = True
            self._on_start(global_pos)

        self._on_move(global_pos)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.LeftButton and self._press_pos is not None:
            global_pos = event.globalPosition().toPoint()
            if self._drag_active:
                self._on_finish(global_pos)
            self._press_pos = None
            self._drag_active = False
        super().mouseReleaseEvent(event)


class MainView:
    """PST-67: Qt View layer — all widget construction owned by this class."""

    def __init__(self) -> None:
        # ------------------------------------------------------------------ #
        # HiDPI — must happen before QApplication is created
        # ------------------------------------------------------------------ #
        configure_hidpi(QApplication)

        # ------------------------------------------------------------------ #
        # Application + top-level labels
        # ------------------------------------------------------------------ #
        self.app = QApplication.instance() or QApplication(sys.argv)
        self.setCurvesInputConfPathLabel = QLabel()

        # ------------------------------------------------------------------ #
        # Apply global theme  (must happen before any widgets are shown)
        # ------------------------------------------------------------------ #
        self._theme_manager = ThemeManager.create(self.app, _UI_DESIGN_CONFIG)
        self._theme_manager.apply()

        # ------------------------------------------------------------------ #
        # Main window widget + layout
        # ------------------------------------------------------------------ #
        self.mainWidget = QWidget()
        self.mainWidget.setWindowTitle(WINDOW_TITLE)
        self.mainWidget.setMinimumSize(WINDOW_MIN_W, WINDOW_MIN_H)
        _ml, _mt, _mr, _mb = MARGINS_MAIN
        mainWidgetLayout = QVBoxLayout()
        mainWidgetLayout.setAlignment(Qt.AlignTop)
        mainWidgetLayout.setSpacing(V_LAYOUT_SPACING)
        mainWidgetLayout.setContentsMargins(_ml, _mt, _mr, _mb)
        self.mainWidget.setLayout(mainWidgetLayout)

        # ------------------------------------------------------------------ #
        # Top bar — title label + theme toggle
        # ------------------------------------------------------------------ #
        _topBar = QFrame()
        _topBar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        _topBarLayout = QHBoxLayout(_topBar)
        _topBarLayout.setContentsMargins(0, 0, 0, 0)
        _topBarLayout.setSpacing(H_LAYOUT_SPACING)

        _titleLabel = QLabel(WINDOW_TITLE)
        _titleLabel.setStyleSheet("font-weight: bold; font-size: 10pt;")
        _topBarLayout.addWidget(_titleLabel, stretch=1)

        self.themeToggleBtn = QPushButton(self._theme_manager.next_mode_label())
        self.themeToggleBtn.setMinimumSize(90, PUSH_BTN_V_SIZE)
        self.themeToggleBtn.setMaximumWidth(110)
        self.themeToggleBtn.setToolTip("Cycle theme: Dark → Light → System")
        self.themeToggleBtn.clicked.connect(self._on_theme_toggle)
        _topBarLayout.addWidget(self.themeToggleBtn, stretch=0)

        mainWidgetLayout.addWidget(_topBar)

        # ------------------------------------------------------------------ #
        # Shadow effects
        # ------------------------------------------------------------------ #
        self.shadowTwoGraphBig   = QGraphicsDropShadowEffect(blurRadius=8, xOffset=6, yOffset=6)
        self.shadowTwoGraphSmall = QGraphicsDropShadowEffect(blurRadius=8, xOffset=6, yOffset=6)
        self.shadowThreeGraph3   = QGraphicsDropShadowEffect(blurRadius=8, xOffset=6, yOffset=6)
        self.shadowThreeGraph1   = QGraphicsDropShadowEffect(blurRadius=8, xOffset=6, yOffset=6)
        self.shadowThreeGraph2   = QGraphicsDropShadowEffect(blurRadius=8, xOffset=6, yOffset=6)
        self.shadowFourGraph00   = QGraphicsDropShadowEffect(blurRadius=8, xOffset=6, yOffset=6)
        self.shadowFourGraph01   = QGraphicsDropShadowEffect(blurRadius=8, xOffset=6, yOffset=6)
        self.shadowFourGraph10   = QGraphicsDropShadowEffect(blurRadius=8, xOffset=6, yOffset=6)
        self.shadowFourGraph11   = QGraphicsDropShadowEffect(blurRadius=8, xOffset=6, yOffset=6)

        # ------------------------------------------------------------------ #
        # Main tab widget
        # ------------------------------------------------------------------ #
        self.mainTabWidget = QTabWidget()
        mainTabWidgetLayout = QHBoxLayout()
        mainTabWidgetLayout.setAlignment(Qt.AlignTop)
        mainTabWidgetLayout.setSpacing(H_LAYOUT_SPACING)
        self.mainTabWidget.setLayout(mainTabWidgetLayout)
        self.mainTabWidget.setMinimumHeight(40)
        self.mainTabWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # Note: mainTabWidget is added to mainSplitter below, NOT directly to mainWidgetLayout

        # ------------------------------------------------------------------ #
        # Tab modules — absorb all public names as instance attributes
        # ------------------------------------------------------------------ #
        import tabs.parse_prot_tab as _ppt
        self._absorb(vars(_ppt))
        self.mainTabWidget.insertTab(0, self.parseProtTab, 'Parse Protocols')

        import tabs.sys_diag_tab as _sdt
        self._absorb(vars(_sdt))
        _sys_scroll = QScrollArea()
        _sys_scroll.setWidget(self.sysDiagTab)
        _sys_scroll.setWidgetResizable(True)
        self.mainTabWidget.insertTab(1, _sys_scroll, 'System Diagrams')

        import tabs.tx_ant_diag_tab as _tat
        self._absorb(vars(_tat))
        _tx_scroll = QScrollArea()
        _tx_scroll.setWidget(self.txAntDiagTab)
        _tx_scroll.setWidgetResizable(True)
        self.mainTabWidget.insertTab(2, _tx_scroll, 'Tx-Antenna Diagrams')

        import tabs.hullkurven_tab as _hkt
        self._absorb(vars(_hkt))
        self.mainTabWidget.insertTab(3, self.hullkurvenTab, 'Hullkurven')

        import tabs.ant_pat_tab as _apt
        self._absorb(vars(_apt))
        _ant_scroll = QScrollArea()
        _ant_scroll.setWidget(self.antPatTab)
        _ant_scroll.setWidgetResizable(True)
        self.mainTabWidget.insertTab(4, _ant_scroll, 'Antenna Patterns')

        import tabs.hullkurven_tab as _hkt
        self._absorb(vars(_hkt))
        self.mainTabWidget.insertTab(3, self.hullkurvenTab, 'Hullkurven')

        # ------------------------------------------------------------------ #
        # Statistics Tab
        # ------------------------------------------------------------------ #
        self.statsTab = QWidget()
        self.statsTab.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        statsLayout = QGridLayout()
        statsLayout.setHorizontalSpacing(H_LAYOUT_SPACING)
        statsLayout.setAlignment(Qt.AlignTop)
        self.statsTab.setLayout(statsLayout)

        self.statsTableColMapping = {
            'graph': 0, 'axis': 1, 'error': 2, 'protType': 3, 'limitName': 4,
            'stDev': 5, 'mean': 6, 'min': 7, 'max': 8, 'maxDev': 9,
            'upperLimit': 10, 'lowerLimit': 11, 'cg': 12,
        }

        self.statsTable = QTableWidget(0, 13)
        self.statsTable.setFixedHeight(220)
        self.statsTable.setHorizontalHeaderLabels([
            'Graph', 'Axis', 'Error', 'Protocol Type', 'Limit Name',
            'Standard Deviation', 'Mean', 'Min.', 'Max.', 'Max. Deviation',
            'Upper Limit', 'Lower Limit', 'Cg',
        ])
        self.statsTable.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        statsLayout.addWidget(self.statsTable, 0, 0, 1, 2)
        statsTableHeader = self.statsTable.horizontalHeader()
        statsTableHeader.setSectionResizeMode(QHeaderView.Stretch)
        self.statsTable.resizeColumnsToContents()
        self.statsTable.setSortingEnabled(False)

        statsButtonFrame = QFrame()
        statsButtonFrame.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Maximum)
        statsButtonFrameLayout = QHBoxLayout()
        statsButtonFrameLayout.setSpacing(H_LAYOUT_SPACING)
        statsButtonFrame.setLayout(statsButtonFrameLayout)
        statsLayout.addWidget(statsButtonFrame, 1, 0, 1, 1)

        self.statsClearBtn = QPushButton('Clear')
        self.statsClearBtn.setMinimumSize(PUSH_BTN_H_SIZE, PUSH_BTN_V_SIZE)
        statsButtonFrameLayout.addWidget(self.statsClearBtn, stretch=1, alignment=Qt.AlignLeft)

        self.statsSeriesDistBtn = QPushButton('Statistical Series')
        self.statsSeriesDistBtn.setMinimumSize(PUSH_BTN_H_SIZE, PUSH_BTN_V_SIZE)
        statsButtonFrameLayout.addWidget(self.statsSeriesDistBtn, stretch=1, alignment=Qt.AlignLeft)

        self.statsGroupsTypeButtonGroup = QButtonGroup()
        self.statsGroupsTypeButtonGroup.setExclusive(True)
        statsButtonFrameLayout.addWidget(QLabel('Show Groups: '), alignment=Qt.AlignLeft)

        self.statsGroupsTypeBurnInRadio = QRadioButton('BurnIn')
        statsButtonFrameLayout.addWidget(self.statsGroupsTypeBurnInRadio)
        self.statsGroupsTypeButtonGroup.addButton(self.statsGroupsTypeBurnInRadio, 0)

        self.statsGroupsTypeCalRadio = QRadioButton('Calibration')
        statsButtonFrameLayout.addWidget(self.statsGroupsTypeCalRadio)
        self.statsGroupsTypeButtonGroup.addButton(self.statsGroupsTypeCalRadio, 1)

        self.statsGroupBackBtn = QPushButton('< Group')
        self.statsGroupBackBtn.setMinimumSize(PUSH_BTN_H_SIZE, PUSH_BTN_V_SIZE)
        statsButtonFrameLayout.addWidget(self.statsGroupBackBtn, stretch=1, alignment=Qt.AlignLeft)

        self.statsGroupForwardBtn = QPushButton('Group >')
        self.statsGroupForwardBtn.setMinimumSize(PUSH_BTN_H_SIZE, PUSH_BTN_V_SIZE)
        statsButtonFrameLayout.addWidget(self.statsGroupForwardBtn, stretch=1, alignment=Qt.AlignLeft)

        self.statsGroupSaveBtn = QPushButton('Save Group')
        self.statsGroupSaveBtn.setMinimumSize(PUSH_BTN_H_SIZE, PUSH_BTN_V_SIZE)
        statsButtonFrameLayout.addWidget(self.statsGroupSaveBtn, stretch=1, alignment=Qt.AlignLeft)
        statsButtonFrameLayout.addWidget(QLabel('Group Name: '), alignment=Qt.AlignLeft)

        self.statsGroupNameString = ''
        self.statsGroupNameLabel = QLabel(self.statsGroupNameString)
        self.statsGroupNameLabel.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        statsButtonFrameLayout.addWidget(self.statsGroupNameLabel, alignment=Qt.AlignLeft)

        statsGroupPptxFrame = QFrame()
        statsGroupPptxFrame.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Maximum)
        statsGroupPptxFrameLayout = QHBoxLayout()
        statsGroupPptxFrameLayout.setSpacing(H_LAYOUT_SPACING)
        statsGroupPptxFrameLayout.setAlignment(Qt.AlignRight)
        statsGroupPptxFrame.setLayout(statsGroupPptxFrameLayout)
        statsLayout.addWidget(statsGroupPptxFrame, 1, 1, 1, 1)

        self.statsGroupPptxBtn = QPushButton('Export .pptx')
        self.statsGroupPptxBtn.setMinimumSize(PUSH_BTN_H_SIZE, PUSH_BTN_V_SIZE)
        statsGroupPptxFrameLayout.addWidget(self.statsGroupPptxBtn, stretch=1, alignment=Qt.AlignRight)

        statsInputConfFrame = QFrame()
        statsInputConfFrame.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Maximum)
        statsInputConfFrameLayout = QHBoxLayout()
        statsInputConfFrameLayout.setSpacing(H_LAYOUT_SPACING)
        statsInputConfFrameLayout.setAlignment(Qt.AlignRight)
        statsInputConfFrame.setLayout(statsInputConfFrameLayout)
        statsLayout.addWidget(statsInputConfFrame, 1, 1, 1, 1)

        self.statsInputConfBtn = QPushButton('Load Input Config File')
        self.statsInputConfBtn.setMinimumSize(140, PUSH_BTN_V_SIZE)
        self.statsInputConfBtn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        statsInputConfFrameLayout.addWidget(self.statsInputConfBtn, stretch=1, alignment=Qt.AlignRight)

        self.statsInputConfPathLabel = QLabel('Import input config ')
        self.statsInputConfPathLabel.setToolTip('Import input config ')
        self.statsInputConfPathLabel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        statsInputConfFrameLayout.addWidget(self.statsInputConfPathLabel, alignment=Qt.AlignRight)

        self.statsInputConfFDialog = QFileDialog()
        self.statsInputConfFDialog.setFileMode(QFileDialog.ExistingFile)
        self.statsInputConfFDialog.setNameFilter("Config File Input (*.json)")
        self.statsInputConfFDialog.setFilter(QDir.Filter.Files)

        self.statsGroupsSaveDialog = LimitsGroupsSaveDialog()

        self.statsPlotFrame = PlotFrame()
        self.statsPlotFrame.setObjectName('PlotFrame')
        self.statsPlotFrame.setStyleSheet(plotFrameStyle)
        statsLayout.addWidget(self.statsPlotFrame, 2, 0, 1, 2)

        self.mainTabWidget.insertTab(6, self.statsTab, 'Statistics')

        # ------------------------------------------------------------------ #
        # System Diagrams Interactive Tab
        # ------------------------------------------------------------------ #
        self.SysDiaInterTab = QWidget()
        self.SysDiaInterTab.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        SysDiaInterLayout = QGridLayout()
        SysDiaInterLayout.setHorizontalSpacing(H_LAYOUT_SPACING)
        SysDiaInterLayout.setAlignment(Qt.AlignTop)
        SysDiaInterLayout.setColumnStretch(0, 1)
        SysDiaInterLayout.setColumnStretch(1, 1)
        SysDiaInterLayout.setColumnStretch(2, 0)
        SysDiaInterLayout.setRowStretch(1, 1)
        self.SysDiaInterTab.setLayout(SysDiaInterLayout)

        self.SysDiaInterTableProtColMapping = {'graph': 0, 'Protocol': 1}
        self.SysDiaInterTableProtocol = QTableWidget(0, 2)
        self.SysDiaInterTableProtocol.setFixedHeight(200)
        self.SysDiaInterTableProtocol.setFixedWidth(600)
        self.SysDiaInterTableProtocol.setHorizontalHeaderLabels(['Graph', 'Protocol'])
        self.SysDiaInterTableProtocol.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        SysDiaInterLayout.addWidget(self.SysDiaInterTableProtocol, 1, 2, 1, 1)
        self.SysDiaInterTableProtocolHeader = self.SysDiaInterTableProtocol.horizontalHeader()
        self.SysDiaInterTableProtocolHeader.setSectionResizeMode(QHeaderView.Stretch)
        self.SysDiaInterTableProtocol.resizeColumnsToContents()
        self.SysDiaInterTableProtocol.setSortingEnabled(False)

        self.SysDiaInterTableParamColMapping = {'graph': 0, 'axis': 1, 'MeasurementName': 2}
        self.SysDiaInterTableParam = QTableWidget(0, 3)
        self.SysDiaInterTableParam.setFixedHeight(470)
        self.SysDiaInterTableParam.setFixedWidth(600)
        self.SysDiaInterTableParam.setHorizontalHeaderLabels(['Graph', 'Axis', 'Measurement Name'])
        self.SysDiaInterTableParam.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        SysDiaInterLayout.addWidget(self.SysDiaInterTableParam, 2, 2, 2, 1)
        self.SysDiaInterTableParamHeader = self.SysDiaInterTableParam.horizontalHeader()
        self.SysDiaInterTableParamHeader.setSectionResizeMode(QHeaderView.Stretch)
        self.SysDiaInterTableParam.resizeColumnsToContents()
        self.SysDiaInterTableParam.setSortingEnabled(False)

        SysDiaInterStartFrame = QFrame()
        SysDiaInterStartFrame.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Maximum)
        SysDiaInterStartFrameLayout = QHBoxLayout()
        SysDiaInterStartFrameLayout.setSpacing(H_LAYOUT_SPACING)
        SysDiaInterStartFrameLayout.setAlignment(Qt.AlignLeft)
        SysDiaInterStartFrame.setLayout(SysDiaInterStartFrameLayout)
        SysDiaInterLayout.addWidget(SysDiaInterStartFrame, 0, 0, 1, 1)

        self.SysDiaInterStartBtn = QPushButton('Start')
        self.SysDiaInterStartBtn.setMinimumSize(PUSH_BTN_H_SIZE, PUSH_BTN_V_SIZE)
        SysDiaInterStartFrameLayout.addWidget(self.SysDiaInterStartBtn, stretch=1, alignment=Qt.AlignLeft)

        self.SysDiaInterClrGrBtn = QPushButton('Clear')
        self.SysDiaInterClrGrBtn.setMinimumSize(PUSH_BTN_H_SIZE, PUSH_BTN_V_SIZE)
        SysDiaInterStartFrameLayout.addWidget(self.SysDiaInterClrGrBtn, stretch=1, alignment=Qt.AlignRight)

        self.SysDiaInterSwitchBtn = QPushButton('On/Off')
        self.SysDiaInterSwitchBtn.setMinimumSize(PUSH_BTN_H_SIZE, PUSH_BTN_V_SIZE)
        SysDiaInterStartFrameLayout.addWidget(self.SysDiaInterSwitchBtn, stretch=0, alignment=Qt.AlignRight)

        self.SysDiaInterPlotFrame = PlotFrameSysDia()
        self.SysDiaInterPlotFrame.setObjectName('PlotFrame')
        self.SysDiaInterPlotFrame.setStyleSheet(plotFrameStyle)
        SysDiaInterLayout.addWidget(self.SysDiaInterPlotFrame, 1, 0, 3, 2)

        self.mainTabWidget.insertTab(8, self.SysDiaInterTab, 'System Diagrams Interactive')

        # ------------------------------------------------------------------ #
        # Log table — in a vertical splitter below the tab widget
        # ------------------------------------------------------------------ #
        self.mainTabWidget.setCurrentIndex(0)

        self.mainLogTableFrame = QFrame()
        self.mainLogTableFrame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.mainLogTableFrame.setMinimumHeight(40)
        mainLogTableFrameLayout = QHBoxLayout()
        mainLogTableFrameLayout.setAlignment(Qt.AlignTop)
        mainLogTableFrameLayout.setSpacing(H_LAYOUT_SPACING)
        self.mainLogTableFrame.setLayout(mainLogTableFrameLayout)

        self.mainLogTableClearBtn = QPushButton('Clear Log')
        self.mainLogTableClearBtn.setMinimumSize(PUSH_BTN_H_SIZE, PUSH_BTN_V_SIZE)
        mainLogTableFrameLayout.addWidget(self.mainLogTableClearBtn, stretch=0)

        self.logDragHandle = _LogDragHandle(
            self._start_log_detach_drag,
            self._move_log_detach_drag,
            self._finish_log_detach_drag,
            self.mainLogTableFrame,
        )
        _dragGripLabel = QLabel('Log')
        _dragGripLabel.setAlignment(Qt.AlignCenter)
        _dragGripLabel.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        _dragGripLayout = QHBoxLayout(self.logDragHandle)
        _dragGripLayout.setContentsMargins(0, 0, 0, 0)
        _dragGripLayout.addWidget(_dragGripLabel)
        mainLogTableFrameLayout.addWidget(self.logDragHandle, stretch=0)

        self.mainLogTableHandler = QTableLogHandler()
        self.mainLogTable = self.mainLogTableHandler.logTable
        self.mainLogTableHeader = self.mainLogTableHandler.logTable.horizontalHeader()
        self.mainLogTableHeader.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.mainLogTableHeader.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.mainLogTableHeader.setSectionResizeMode(2, QHeaderView.Stretch)
        self.mainLogTable.setMinimumHeight(40)
        self.mainLogTable.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        mainLogTableFrameLayout.addWidget(self.mainLogTable, stretch=1)

        self._logPlaceholder = QWidget()
        self._logPlaceholder.setMinimumHeight(0)
        self._logPlaceholder.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self._logDialog = QDialog(self.mainWidget)
        self._logDialog.setWindowTitle(f"{WINDOW_TITLE} - Log")
        self._logDialog.setModal(False)
        self._logDialog.setWindowFlag(Qt.Window, True)
        self._logDialog.setWindowFlag(Qt.WindowMinMaxButtonsHint, True)
        self._logDialog.setWindowFlag(Qt.WindowCloseButtonHint, True)
        self._logDialog.resize(900, 280)
        _logDialogLayout = QVBoxLayout(self._logDialog)
        _logDialogLayout.setContentsMargins(0, 0, 0, 0)
        _logDialogLayout.setSpacing(0)
        self._logDialogCloseFilter = _CloseEventFilter(self._attach_log_panel, self._logDialog)
        self._logDialog.installEventFilter(self._logDialogCloseFilter)
        self._logDetached = False
        self._logVisible = True
        self._logDragOffset = QPoint(16, 10)
        self._default_splitter_sizes = [int(WINDOW_DEF_H * 0.78), int(WINDOW_DEF_H * 0.22)]
        self._last_attached_splitter_state = None

        # Vertical splitter: tab area (top, stretchy) + log table (bottom, collapsible)
        self.mainSplitter = QSplitter(Qt.Vertical)
        self.mainSplitter.addWidget(self.mainTabWidget)
        self.mainSplitter.addWidget(self.mainLogTableFrame)
        self.mainSplitter.setChildrenCollapsible(True)
        self.mainSplitter.setHandleWidth(8)
        self.mainSplitter.setStretchFactor(0, 4)   # tab area gets 4× the space
        self.mainSplitter.setStretchFactor(1, 1)   # log panel gets 1×
        self.mainSplitter.setCollapsible(0, False)
        self.mainSplitter.setCollapsible(1, False)
        self.mainSplitter.setSizes(self._default_splitter_sizes)
        self.mainSplitter.splitterMoved.connect(self._on_splitter_moved)
        self._last_attached_splitter_state = self.mainSplitter.saveState()
        mainWidgetLayout.addWidget(self.mainSplitter)

        # ------------------------------------------------------------------ #
        # Restore window geometry + splitter state from previous session
        # ------------------------------------------------------------------ #
        self._settings = QSettings("CalibrationStatsTool", "MainWindow")
        _geom = self._settings.value("geometry")
        if _geom:
            self.mainWidget.restoreGeometry(_geom)
        else:
            self.mainWidget.resize(WINDOW_DEF_W, WINDOW_DEF_H)

        _splitter_state = self._settings.value("splitterState")
        if _splitter_state:
            if not self.mainSplitter.restoreState(_splitter_state):
                self.mainSplitter.setSizes(self._default_splitter_sizes)
        self._sync_log_visibility_from_splitter()
        self._last_attached_splitter_state = self.mainSplitter.saveState()
        self._theme_manager.add_change_listener(self._refresh_inline_theme_styles)
        self._refresh_inline_theme_styles()

        # Install event filter on mainWidget to capture closeEvent for state save
        self._close_filter = _CloseEventFilter(self._save_window_state, self.mainWidget)
        self.mainWidget.installEventFilter(self._close_filter)

        self.mainWidget.show()

    def _save_window_state(self) -> None:
        """Persist geometry and splitter state to QSettings."""
        self._settings.setValue("geometry", self.mainWidget.saveGeometry())
        splitter_state = self._last_attached_splitter_state or self.mainSplitter.saveState()
        if not self._logDetached:
            splitter_state = self.mainSplitter.saveState()
        self._settings.setValue("splitterState", splitter_state)

    def _on_theme_toggle(self) -> None:
        """Cycle through dark → light → system themes."""
        self._theme_manager.cycle_mode()
        self.themeToggleBtn.setText(self._theme_manager.next_mode_label())

    def _refresh_inline_theme_styles(self) -> None:
        """Refresh widgets that still rely on inline styles outside global QSS."""
        theme_manager = get_theme_manager()
        if theme_manager is None:
            return

        palette = theme_manager.palette()
        ant_pat_style = _build_ant_pat_table_style(palette)
        plot_frame_style = _build_plot_frame_style(palette)

        for frame in self.mainWidget.findChildren(QFrame):
            object_name = frame.objectName()
            if object_name in {"Frame", "SubFrame1", "SubFrame2"}:
                frame.setStyleSheet(ant_pat_style)
            elif object_name == "PlotFrame":
                frame.setStyleSheet(plot_frame_style)

        if hasattr(self, "mainLogTableHandler") and self.mainLogTableHandler is not None:
            self.mainLogTableHandler.apply_theme_colors()

    def _on_splitter_moved(self, *_args) -> None:
        if self._logDetached:
            return
        self._last_attached_splitter_state = self.mainSplitter.saveState()
        self._sync_log_visibility_from_splitter()

    def _sync_log_visibility_from_splitter(self) -> None:
        if self._logDetached:
            self._logVisible = True
            return
        sizes = self.mainSplitter.sizes()
        self._logVisible = len(sizes) > 1 and sizes[1] > 0

    def _show_log_panel(self) -> None:
        if self._logDetached:
            self._logDialog.show()
            self._logDialog.raise_()
            self._logDialog.activateWindow()
            return
        sizes = self.mainSplitter.sizes()
        total = sum(sizes) if sizes else WINDOW_DEF_H
        log_size = max(int(total * 0.22), 96)
        self.mainSplitter.setSizes([max(total - log_size, 120), log_size])
        self._last_attached_splitter_state = self.mainSplitter.saveState()
        self._sync_log_visibility_from_splitter()

    def _hide_log_panel(self) -> None:
        if self._logDetached:
            self._logDialog.hide()
            return
        sizes = self.mainSplitter.sizes()
        total = sum(sizes) if sizes else WINDOW_DEF_H
        self.mainSplitter.setSizes([max(total, 200), 0])
        self._last_attached_splitter_state = self.mainSplitter.saveState()
        self._sync_log_visibility_from_splitter()

    def _toggle_log_panel(self) -> None:
        if self._logDetached:
            if self._logDialog.isVisible():
                self._logDialog.hide()
            else:
                self._show_log_panel()
            return
        if self._logVisible:
            self._hide_log_panel()
        else:
            self._show_log_panel()

    def _detach_log_panel(self) -> None:
        self._detach_log_panel_at()

    def _detach_log_panel_at(self, global_pos: QPoint | None = None) -> None:
        if self._logDetached:
            if global_pos is not None:
                self._move_detached_log_dialog(global_pos)
            self._show_log_panel()
            return
        self._last_attached_splitter_state = self.mainSplitter.saveState()
        self.mainSplitter.replaceWidget(1, self._logPlaceholder)
        self.mainLogTableFrame.setParent(self._logDialog)
        self._logDialog.layout().addWidget(self.mainLogTableFrame)
        self.mainSplitter.setSizes([sum(self.mainSplitter.sizes()) or WINDOW_DEF_H, 0])
        self._logDetached = True
        self._logDialog.show()
        if global_pos is not None:
            self._move_detached_log_dialog(global_pos)
        self._show_log_panel()

    def _attach_log_panel(self) -> None:
        if not self._logDetached:
            return
        self._logDialog.hide()
        self.mainLogTableFrame.setParent(None)
        self.mainSplitter.replaceWidget(1, self.mainLogTableFrame)
        if self._last_attached_splitter_state is not None:
            self.mainSplitter.restoreState(self._last_attached_splitter_state)
        else:
            self.mainSplitter.setSizes(self._default_splitter_sizes)
        self._logDetached = False
        self._sync_log_visibility_from_splitter()

    def _move_detached_log_dialog(self, global_pos: QPoint) -> None:
        self._logDialog.move(global_pos - self._logDragOffset)

    def _attach_drop_target_rect(self) -> QRect:
        top_left = self.mainWidget.mapToGlobal(QPoint(0, 0))
        size = self.mainWidget.size()
        attach_top = int(size.height() * 0.68)
        return QRect(
            QPoint(top_left.x(), top_left.y() + attach_top),
            QPoint(top_left.x() + size.width(), top_left.y() + size.height()),
        )

    def _start_log_detach_drag(self, global_pos: QPoint) -> None:
        if not self._logDetached:
            self._detach_log_panel_at(global_pos)
        else:
            self._logDialog.show()
            self._move_detached_log_dialog(global_pos)

    def _move_log_detach_drag(self, global_pos: QPoint) -> None:
        if self._logDetached:
            self._move_detached_log_dialog(global_pos)

    def _finish_log_detach_drag(self, global_pos: QPoint) -> None:
        if not self._logDetached:
            return
        if self._attach_drop_target_rect().contains(global_pos):
            self._attach_log_panel()
            return
        self._move_detached_log_dialog(global_pos)
        self._logDialog.show()
        self._logDialog.raise_()
        self._logDialog.activateWindow()

    # ------------------------------------------------------------------ #
    # Namespace absorb helper
    # ------------------------------------------------------------------ #

    def _absorb(self, ns: dict) -> None:
        """Copy public names from a module namespace dict into self."""
        for k, v in ns.items():
            if not k.startswith('_'):
                setattr(self, k, v)

    # ------------------------------------------------------------------ #
    # Tab helpers
    # ------------------------------------------------------------------ #

    def tab_index_of(self, title: str) -> int:
        """Return the actual tab index whose text equals *title*, or -1."""
        for i in range(self.mainTabWidget.count()):
            if self.mainTabWidget.tabText(i) == title:
                return i
        return -1

    # ------------------------------------------------------------------ #
    # Application lifecycle
    # ------------------------------------------------------------------ #

    def show(self) -> None:
        """Show the main application window."""
        self.mainWidget.show()

    def close_and_save_state(self) -> None:
        """Persist window geometry and splitter state, then close."""
        self._settings.setValue("geometry", self.mainWidget.saveGeometry())
        splitter_state = self._last_attached_splitter_state or self.mainSplitter.saveState()
        if not self._logDetached:
            splitter_state = self.mainSplitter.saveState()
        self._settings.setValue("splitterState", splitter_state)
        self.mainWidget.close()

    def exec_(self) -> int:
        """Start the Qt event loop and return exit code."""
        return self.app.exec()

    # ------------------------------------------------------------------ #
    # Parse-protocol stat label helpers
    # ------------------------------------------------------------------ #

    def set_loaded_protocols_label(self, count: int) -> None:
        self.parseProtLoadedProtLabel.setText(
            self.parseProtLoadedProtStr + str(count)
        )

    def set_ptu2_files_label(self, count: int) -> None:
        self.parseProtPtu2FilesLabel.setText(
            self.parseProtPtu2FilesStr + str(count)
        )

    def set_tx_ant_diag_files_label(self, count: int) -> None:
        self.parseProtTxAntDiagFilesLabel.setText(
            self.parseProtTxAntDiagFilesStr + str(count)
        )

    def set_sep_par_ptu2_files_label(self, count: int) -> None:
        self.parseProtSepParPtu2FilesLabel.setText(
            self.parseProtSepParPtu2FilesStr + str(count)
        )

    def set_sep_par_tx_ant_diag_files_label(self, count: int) -> None:
        self.parseProtSepParTxAntDiagFilesLabel.setText(
            self.parseProtSepParTxAntDiagFilesStr + str(count)
        )

    def set_progress_label(self, text: str) -> None:
        self.parseProtProgresLabel.setText(text)

    def set_progress_bar(self, value: int) -> None:
        self.parseProtProgresBar.setValue(value)

    # ------------------------------------------------------------------ #
    # Table helpers
    # ------------------------------------------------------------------ #

    def clear_table(self, table) -> None:
        """Remove all rows from a QTableWidget."""
        table.setRowCount(0)

    def clear_all_parse_tables(self) -> None:
        """Clear all parse-protocol tables."""
        for table in (
            self.parseProtSelProtTable,
            self.parseProtAccProtTable,
            self.parseProtAddPtu2ParsedTable,
            self.parseProtAddPtu2FailedTable,
            self.parseProtAddTxAntDiagParsedTable,
            self.parseProtAddTxAntDiagFailedTable,
            self.parseProtStatsParsedTable,
            self.parseProtStatsFailedTable,
        ):
            table.setRowCount(0)

    # ------------------------------------------------------------------ #
    # Read helpers for widget state (used by controllers to read UI values)
    # ------------------------------------------------------------------ #

    def get_burn_in_cal_mode(self) -> int:
        """Return checked button ID from the BurnIn/Cal radio group."""
        return self.parseProtBurnInCalGroup.checkedId()

    def get_include_burn_in_start(self) -> bool:
        # Checkbox means "Ignore BurnIn At Start": checked = exclude, unchecked = include.
        return not self.parseProtBurnStartCheckBox.isChecked()

    def get_use_sensor_muster(self) -> int:
        return 1 if self.parseProtSensorMusterCheckBox.isChecked() else 0

    def get_sensor_muster_list(self) -> list[str]:
        raw = self.parseProtSensorMusterLEdit.text().strip()
        return raw.split() if raw else []

    def get_img_gen_mode(self) -> int:
        return self.sysDiagPlotSetupImgGenGroup.checkedId()

    def get_script_mode(self) -> int:
        return self.sysDiagPlotSetupScriptModeGroup.checkedId()

    def get_three_graph_layout(self) -> bool:
        return self.sysDiagPlotSetup3GraphLayoutImgCheckBox.isChecked()

    def get_image_dpi(self) -> int | None:
        from shared import safeparse as sp
        text = self.sysDiagPlotSetupImageDpiLEdit.text()
        if sp.checkInt(text):
            return int(text)
        return None

    def get_x_scale_auto(self) -> bool:
        return self.sysDiagPlotSetupScalingAutoCheckBox.isChecked()

    def get_x_scale_az(self) -> float | None:
        from shared import safeparse as sp
        text = self.sysDiagPlotSetupScalingXScaleAzLEdit.text()
        if sp.checkDecimal(text):
            return float(text)
        return None

    def get_x_scale_el(self) -> float | None:
        from shared import safeparse as sp
        text = self.sysDiagPlotSetupScalingXScaleElLEdit.text()
        if sp.checkDecimal(text):
            return float(text)
        return None

    def get_y_limits_mode(self) -> int:
        return self.sysDiagPlotSetupScalingYLimitsGroup.checkedId()

    def get_diff_phase_diff_scaling(self) -> float | None:
        from shared import safeparse as sp
        text = self.sysDiagPlotSetupScalingDiffPhDiffLEdit.text()
        if sp.checkDecimal(text):
            return float(text)
        return None

    def get_ideal_phase_diff(self) -> bool:
        return self.sysDiagPlotSetupGraphConfIdealCurveCheckBox.isChecked()

    # ------------------------------------------------------------------ #
    # Sensor muster enable / disable
    # ------------------------------------------------------------------ #

    def set_sensor_muster_enabled(self, enabled: bool) -> None:
        self.parseProtSensorMusterLEdit.setEnabled(enabled)

    # ------------------------------------------------------------------ #
    # Parse-protocol stats counter labels (ratio format)
    # ------------------------------------------------------------------ #

    def set_loaded_prot_ratio_label(self, accepted: int, filtered: int) -> None:
        """Display accepted / (accepted + filtered) for the loaded protocols label."""
        self.parseProtLoadedProtLabel.setText(
            self.parseProtLoadedProtStr + f'{accepted} / {accepted + filtered}'
        )

    def set_eol_error_label(self, count, total=None) -> None:
        suffix = str(count) if total is None else f'{count} / {total}'
        self.parseProtEolErrorLabel.setText(self.parseProtEolErrorStr + suffix)

    def set_abort_crit_label(self, count, total=None) -> None:
        suffix = str(count) if total is None else f'{count} / {total}'
        self.parseProtAbbortCritLabel.setText(self.parseProtAbbortCritStr + suffix)

    def set_meas_limits_label(self, count, total=None) -> None:
        suffix = str(count) if total is None else f'{count} / {total}'
        self.parseProtMeasLimitsExcLabel.setText(self.parseProtMeasLimitsExcStr + suffix)

    def set_parsed_loaded_label(self, parsed, total=None) -> None:
        suffix = str(parsed) if total is None else f'{parsed} / {total}'
        self.parseProtParsedLoadedProtLabel.setText(
            self.parseProtParsedLoadedProtStr + suffix
        )

    # ------------------------------------------------------------------ #
    # Progress bar operations
    # ------------------------------------------------------------------ #

    def reset_progress_bar(self) -> None:
        self.parseProtProgresBar.reset()

    def set_progress_bar_range(self, max_val: int) -> None:
        self.parseProtProgresBar.setRange(0, max_val)

    def set_progress_bar_format(self, fmt: str) -> None:
        self.parseProtProgresBar.setFormat(fmt)

    def get_progress_bar_value(self) -> int:
        return self.parseProtProgresBar.value()

    # ------------------------------------------------------------------ #
    # File path label helpers (sets both text and tooltip)
    # ------------------------------------------------------------------ #

    def set_burn_in_limits_file(self, path: str) -> None:
        self.parseProtProtDataInFileBurnInLabel.setText(path)
        self.parseProtProtDataInFileBurnInLabel.setToolTip(path)

    def set_cal_limits_file(self, path: str) -> None:
        self.parseProtProtDataInFileCalLabel.setText(path)
        self.parseProtProtDataInFileCalLabel.setToolTip(path)

    def set_burn_in_lim_groups_file(self, path: str) -> None:
        self.parseProtProtDataLimGroupsBurnInLabel.setText(path)
        self.parseProtProtDataLimGroupsBurnInLabel.setToolTip(path)

    def set_cal_lim_groups_file(self, path: str) -> None:
        self.parseProtProtDataLimGroupsCalLabel.setText(path)
        self.parseProtProtDataLimGroupsCalLabel.setToolTip(path)

    def populate_burn_in_groups(self, group_names: list[str]) -> None:
        """Populate the BurnIn group selection ComboBox with ``group_names``.

        Clears any previous entries first and enables/disables the widget
        depending on whether any names were provided.
        """
        cb = self.parseProtProtDataBurnInGroupSelComboBox
        cb.blockSignals(True)
        cb.clear()
        if group_names:
            cb.addItems(group_names)
            cb.setEnabled(True)
        else:
            cb.setEnabled(False)
        cb.blockSignals(False)

    def populate_cal_groups(self, group_names: list[str]) -> None:
        """Populate the Calibration group selection ComboBox with ``group_names``."""
        cb = self.parseProtProtDataCalGroupSelComboBox
        cb.blockSignals(True)
        cb.clear()
        if group_names:
            cb.addItems(group_names)
            cb.setEnabled(True)
        else:
            cb.setEnabled(False)
        cb.blockSignals(False)

    def get_burn_in_active_group_index(self) -> int:
        return self.parseProtProtDataBurnInGroupSelComboBox.currentIndex()

    def get_cal_active_group_index(self) -> int:
        return self.parseProtProtDataCalGroupSelComboBox.currentIndex()

    def set_stats_input_conf_path(self, path: str) -> None:
        self.statsInputConfPathLabel.setText(path)
        self.statsInputConfPathLabel.setToolTip(path)
