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
    QSizePolicy, QScrollArea,
)
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtUiTools import *
import logging
import time
import enum
import numpy as np
from calibration_statistics_tool.shared import plotdata

from calibration_statistics_tool.ui.ui_constants import *
from calibration_statistics_tool.ui.widgets import (
    getGraphColor, show_datapoints, Match,
    dialogLEditErrorStyle, dialogLEditCorrectStyle,
    dialogLabelErrorStyle, dialogLabelCorrectStyle,
    LimitsGroupsSaveDialog, TableItemCompleter,
    PlotFrame, PlotFrameSysDia, QTableLogHandler,
)


class MainView:
    """PST-67: Qt View layer — all widget construction owned by this class."""

    def __init__(self) -> None:
        # ------------------------------------------------------------------ #
        # Application + top-level labels
        # ------------------------------------------------------------------ #
        self.app = QApplication.instance() or QApplication(sys.argv)
        self.setCurvesInputConfPathLabel = QLabel()

        # ------------------------------------------------------------------ #
        # Main window widget + layout
        # ------------------------------------------------------------------ #
        self.mainWidget = QWidget()
        mainWidgetLayout = QVBoxLayout()
        mainWidgetLayout.setAlignment(Qt.AlignTop)
        mainWidgetLayout.setSpacing(V_LAYOUT_SPACING)
        self.mainWidget.setLayout(mainWidgetLayout)

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
        self.mainTabWidget.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        mainWidgetLayout.addWidget(self.mainTabWidget)

        # ------------------------------------------------------------------ #
        # Tab modules — absorb all public names as instance attributes
        # ------------------------------------------------------------------ #
        import calibration_statistics_tool.ui.tabs.parse_prot_tab as _ppt
        self._absorb(vars(_ppt))
        self.mainTabWidget.insertTab(0, self.parseProtTab, 'Parse Protocols')

        import calibration_statistics_tool.ui.tabs.sys_diag_tab as _sdt
        self._absorb(vars(_sdt))
        self.mainTabWidget.insertTab(1, self.sysDiagTab, 'System Diagrams')

        import calibration_statistics_tool.ui.tabs.tx_ant_diag_tab as _tat
        self._absorb(vars(_tat))
        self.mainTabWidget.insertTab(2, self.txAntDiagTab, 'Tx-Antenna Diagrams')

        import calibration_statistics_tool.ui.tabs.hullkurven_tab as _hkt
        self._absorb(vars(_hkt))
        self.mainTabWidget.insertTab(3, self.hullkurvenTab, 'Hullkurven')

        import calibration_statistics_tool.ui.tabs.ant_pat_tab as _apt
        self._absorb(vars(_apt))
        self.mainTabWidget.insertTab(4, self.antPatTab, 'Antenna Patterns')

        import calibration_statistics_tool.ui.tabs.hullkurven_tab as _hkt
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
        self.statsClearBtn.setFixedSize(PUSH_BTN_H_SIZE, PUSH_BTN_V_SIZE)
        statsButtonFrameLayout.addWidget(self.statsClearBtn, stretch=1, alignment=Qt.AlignLeft)

        self.statsSeriesDistBtn = QPushButton('Statistical Series')
        self.statsSeriesDistBtn.setFixedSize(PUSH_BTN_H_SIZE, PUSH_BTN_V_SIZE)
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
        self.statsGroupBackBtn.setFixedSize(PUSH_BTN_H_SIZE, PUSH_BTN_V_SIZE)
        statsButtonFrameLayout.addWidget(self.statsGroupBackBtn, stretch=1, alignment=Qt.AlignLeft)

        self.statsGroupForwardBtn = QPushButton('Group >')
        self.statsGroupForwardBtn.setFixedSize(PUSH_BTN_H_SIZE, PUSH_BTN_V_SIZE)
        statsButtonFrameLayout.addWidget(self.statsGroupForwardBtn, stretch=1, alignment=Qt.AlignLeft)

        self.statsGroupSaveBtn = QPushButton('Save Group')
        self.statsGroupSaveBtn.setFixedSize(PUSH_BTN_H_SIZE, PUSH_BTN_V_SIZE)
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
        self.statsGroupPptxBtn.setFixedSize(PUSH_BTN_H_SIZE, PUSH_BTN_V_SIZE)
        statsGroupPptxFrameLayout.addWidget(self.statsGroupPptxBtn, stretch=1, alignment=Qt.AlignRight)

        statsInputConfFrame = QFrame()
        statsInputConfFrame.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Maximum)
        statsInputConfFrameLayout = QHBoxLayout()
        statsInputConfFrameLayout.setSpacing(H_LAYOUT_SPACING)
        statsInputConfFrameLayout.setAlignment(Qt.AlignRight)
        statsInputConfFrame.setLayout(statsInputConfFrameLayout)
        statsLayout.addWidget(statsInputConfFrame, 1, 1, 1, 1)

        self.statsInputConfBtn = QPushButton('Load Input Config File')
        self.statsInputConfBtn.setFixedSize(140, PUSH_BTN_V_SIZE)
        self.statsInputConfBtn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
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
        SysDiaInterLayout.setAlignment(Qt.AlignLeft)
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
        self.SysDiaInterStartBtn.setFixedSize(PUSH_BTN_H_SIZE, PUSH_BTN_V_SIZE)
        SysDiaInterStartFrameLayout.addWidget(self.SysDiaInterStartBtn, stretch=1, alignment=Qt.AlignLeft)

        self.SysDiaInterClrGrBtn = QPushButton('Clear')
        self.SysDiaInterClrGrBtn.setFixedSize(PUSH_BTN_H_SIZE, PUSH_BTN_V_SIZE)
        SysDiaInterStartFrameLayout.addWidget(self.SysDiaInterClrGrBtn, stretch=1, alignment=Qt.AlignRight)

        self.SysDiaInterSwitchBtn = QPushButton('On/Off')
        self.SysDiaInterSwitchBtn.setFixedSize(PUSH_BTN_H_SIZE, PUSH_BTN_V_SIZE)
        SysDiaInterStartFrameLayout.addWidget(self.SysDiaInterSwitchBtn, stretch=0, alignment=Qt.AlignRight)

        self.SysDiaInterPlotFrame = PlotFrameSysDia()
        self.SysDiaInterPlotFrame.setObjectName('PlotFrame')
        self.SysDiaInterPlotFrame.setStyleSheet(plotFrameStyle)
        SysDiaInterLayout.addWidget(self.SysDiaInterPlotFrame, 1, 0, 3, 2)

        self.mainTabWidget.insertTab(8, self.SysDiaInterTab, 'System Diagrams Interactive')

        # ------------------------------------------------------------------ #
        # Log table (below tab widget)
        # ------------------------------------------------------------------ #
        self.mainTabWidget.setCurrentIndex(0)

        mainLogTableFrame = QFrame()
        mainLogTableFrame.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        mainLogTableFrameLayout = QHBoxLayout()
        mainLogTableFrameLayout.setAlignment(Qt.AlignTop)
        mainLogTableFrameLayout.setSpacing(H_LAYOUT_SPACING)
        mainLogTableFrame.setLayout(mainLogTableFrameLayout)
        mainWidgetLayout.addWidget(mainLogTableFrame)

        self.mainLogTableClearBtn = QPushButton('Clear')
        self.mainLogTableClearBtn.setFixedSize(PUSH_BTN_H_SIZE, PUSH_BTN_V_SIZE)
        mainLogTableFrameLayout.addWidget(self.mainLogTableClearBtn, stretch=1)

        self.mainLogTableHandler = QTableLogHandler()
        self.mainLogTable = self.mainLogTableHandler.logTable
        self.mainLogTableHeader = self.mainLogTableHandler.logTable.horizontalHeader()
        self.mainLogTableHeader.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.mainLogTableHeader.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.mainLogTableHeader.setSectionResizeMode(2, QHeaderView.Stretch)
        self.mainLogTable.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        mainLogTableFrameLayout.addWidget(self.mainLogTable, stretch=3)

        self._wrap_tabs_in_scroll_areas()
        self.mainTabWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        mainWidgetLayout.setStretchFactor(self.mainTabWidget, 4)
        mainWidgetLayout.setStretchFactor(mainLogTableFrame, 1)
        self._fit_window_to_screen()

        self.mainWidget.show()

    # ------------------------------------------------------------------ #
    # Window sizing
    # ------------------------------------------------------------------ #

    def _wrap_tabs_in_scroll_areas(self) -> None:
        """Scroll each tab page so oversized pages cannot force the window past the screen."""
        for i in range(self.mainTabWidget.count()):
            page = self.mainTabWidget.widget(i)
            title = self.mainTabWidget.tabText(i)
            self.mainTabWidget.removeTab(i)
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QFrame.NoFrame)
            scroll.setWidget(page)
            self.mainTabWidget.insertTab(i, scroll, title)
        self.mainTabWidget.setCurrentIndex(0)

    def _fit_window_to_screen(self) -> None:
        """Open at 90 % of the primary screen's usable area, centred."""
        screen = QGuiApplication.primaryScreen().availableGeometry()
        self.mainWidget.resize(int(screen.width() * 0.9), int(screen.height() * 0.9))
        frame = self.mainWidget.frameGeometry()
        frame.moveCenter(screen.center())
        self.mainWidget.move(frame.topLeft())

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
        from calibration_statistics_tool.shared import safeparse as sp
        text = self.sysDiagPlotSetupImageDpiLEdit.text()
        if sp.checkInt(text):
            return int(text)
        return None

    def get_x_scale_auto(self) -> bool:
        return self.sysDiagPlotSetupScalingAutoCheckBox.isChecked()

    def get_x_scale_az(self) -> float | None:
        from calibration_statistics_tool.shared import safeparse as sp
        text = self.sysDiagPlotSetupScalingXScaleAzLEdit.text()
        if sp.checkDecimal(text):
            return float(text)
        return None

    def get_x_scale_el(self) -> float | None:
        from calibration_statistics_tool.shared import safeparse as sp
        text = self.sysDiagPlotSetupScalingXScaleElLEdit.text()
        if sp.checkDecimal(text):
            return float(text)
        return None

    def get_y_limits_mode(self) -> int:
        return self.sysDiagPlotSetupScalingYLimitsGroup.checkedId()

    def get_diff_phase_diff_scaling(self) -> float | None:
        from calibration_statistics_tool.shared import safeparse as sp
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
