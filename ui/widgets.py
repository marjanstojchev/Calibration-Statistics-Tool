"""PST-60: Shared Qt widget classes extracted from pyside_qtgui.py.

Contains: getGraphColor, show_datapoints, Match, dialog styles,
          TableItemCompleter, LimitsGroupsSaveDialog, PlotFrame,
          PlotFrameSysDia, QTableLogHandler.
"""
from __future__ import annotations

import enum
import logging
import time

from PySide6.QtWidgets import (
    QFrame, QLabel, QPushButton, QWidget, QTableWidget, QTableWidgetItem,
    QGroupBox, QHeaderView, QComboBox, QLineEdit, QDialog, QDialogButtonBox,
    QButtonGroup, QStyledItemDelegate, QCompleter, QVBoxLayout, QGridLayout,
    QHBoxLayout, QSizePolicy,
)
from PySide6.QtGui import QBrush, QColor
from PySide6.QtCore import Qt
import matplotlib.pyplot as plt
import mplcursors
import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar

import plotdata

from ui_constants import (
    V_LAYOUT_SPACING, H_LAYOUT_SPACING, LIM_GROUPS_TABLE_ROWS,
    PUSH_BTN_H_SIZE, PUSH_BTN_V_SIZE, LEDIT_BTN_PATH_H_SIZE, LEDIT_BTN_V_SIZE,
    plotFrameStyle, color_list, color_list_rev,
)
from ui_theme import (
    LOG_LEVEL_BG_COLORS, LOG_LEVEL_FG_COLORS,
    dialogLEditErrorStyle, dialogLEditCorrectStyle,
    dialogLabelErrorStyle, dialogLabelCorrectStyle,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def getGraphColor(combIdx: int) -> str:
    colorList = [
        'blue', 'red', 'green', 'magenta', 'black', 'cyan', 'orange',
        'midnightblue', 'maroon', 'springgreen', 'purple', 'dimgrey',
        'teal', 'yellow',
    ]
    if combIdx >= len(colorList):
        color = colorList[combIdx % len(colorList)]
    else:
        color = colorList[combIdx]
    return color


def show_datapoints(sel):
    """Tooltip callback for mplcursors — shows x/y values."""
    xi, yi = sel[0], sel[0]
    xi, yi = xi._xorig.tolist(), yi._yorig.tolist()
    sel.annotation.set_text(
        'x: ' + str(xi[round(sel.target.index)]) +
        '\n' + 'y: ' + str(yi[round(sel.target.index)])
    )


# ---------------------------------------------------------------------------
# Match enum  (used by LimitsGroupsSaveDialog)
# ---------------------------------------------------------------------------

class Match(enum.Enum):
    Contains   = 0
    ExactMatch = 0


# ---------------------------------------------------------------------------
# TableItemCompleter
# ---------------------------------------------------------------------------

class TableItemCompleter(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        userRoleDict  = index.data(Qt.UserRole)
        completion_ls = userRoleDict['completion_ls']
        completer = QCompleter(completion_ls, parent)
        editor.setCompleter(completer)
        return editor


# ---------------------------------------------------------------------------
# LimitsGroupsSaveDialog
# ---------------------------------------------------------------------------

class LimitsGroupsSaveDialog(QDialog):
    def __init__(self, parent=None):
        super(LimitsGroupsSaveDialog, self).__init__(parent)

        self.gridLayout = QGridLayout(self)
        self.gridLayout.setVerticalSpacing(V_LAYOUT_SPACING)
        self.gridLayout.setHorizontalSpacing(H_LAYOUT_SPACING)

        self.table = QTableWidget(LIM_GROUPS_TABLE_ROWS, 2)
        self.table.setMinimumHeight(400)
        self.table.setMinimumWidth(500)
        self.table.setHorizontalHeaderLabels(['Limit', 'Match'])
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.gridLayout.addWidget(self.table, 0, 0, 2, 1)

        self.tableHeader = self.table.horizontalHeader()
        self.tableHeader.setSectionResizeMode(0, QHeaderView.Interactive)
        self.table.setColumnWidth(0, 320)
        self.table.setColumnWidth(1, 60)

        self.groupNameFrame = QFrame()
        self.groupNameFrame.setMaximumHeight(100)
        self.groupNameFrameLayout = QVBoxLayout()
        self.groupNameFrameLayout.setSpacing(V_LAYOUT_SPACING)
        self.groupNameFrame.setLayout(self.groupNameFrameLayout)

        self.groupNameLabel = QLabel('Group Name:')
        self.groupNameFrameLayout.addWidget(self.groupNameLabel, alignment=Qt.AlignTop)

        self.groupNameLEdit = QLineEdit()
        self.groupNameLEdit.setFixedSize(LEDIT_BTN_PATH_H_SIZE, LEDIT_BTN_V_SIZE)
        self.groupNameFrameLayout.addWidget(self.groupNameLEdit, alignment=Qt.AlignTop)

        from PySide6.QtWidgets import QCheckBox
        self.saveToFileCheckBox = QCheckBox('Save to file')
        self.saveToFileCheckBox.setChecked(False)
        self.groupNameFrameLayout.addWidget(self.saveToFileCheckBox, alignment=Qt.AlignTop)

        self.gridLayout.addWidget(self.groupNameFrame, 0, 1, 1, 1)

        self.addLineFrame = QFrame()
        self.addLineFrame.setMaximumHeight(100)
        self.addLineFrameLayout = QVBoxLayout()
        self.addLineFrameLayout.setSpacing(V_LAYOUT_SPACING)
        self.addLineFrame.setLayout(self.addLineFrameLayout)

        self.addLineButton = QPushButton('Add Line')
        self.addLineButton.setFixedSize(PUSH_BTN_H_SIZE, PUSH_BTN_V_SIZE)
        self.addLineFrameLayout.addWidget(self.addLineButton, alignment=Qt.AlignBottom)

        self.gridLayout.addWidget(self.addLineFrame, 1, 1, 1, 1, alignment=Qt.AlignBottom)

        self.completionList = []
        self.compListRowDict = dict()
        self.compListRowDict['completion_ls'] = []
        self.compListRowDict['row'] = None

        self.statsTableHeader = self.table.horizontalHeader()
        self.statsTableHeader.setSectionResizeMode(QHeaderView.Stretch)
        self.table.resizeColumnsToContents()

        self.comboList = []
        self.initTable()

        self.tableCompleter = TableItemCompleter(self.table)
        self.table.setItemDelegateForColumn(0, self.tableCompleter)

        self.errorLabel = QLabel('')
        self.gridLayout.addWidget(self.errorLabel, 2, 0, 1, 1, alignment=Qt.AlignLeft)

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.buttonBox.button(QDialogButtonBox.Ok).setText('Save')
        self.buttonBox.button(QDialogButtonBox.Ok).setFixedSize(PUSH_BTN_H_SIZE, PUSH_BTN_V_SIZE)
        self.buttonBox.button(QDialogButtonBox.Cancel).setFixedSize(PUSH_BTN_H_SIZE, PUSH_BTN_V_SIZE)
        self.gridLayout.addWidget(self.buttonBox, 2, 1, 1, 1)

    def initTable(self):
        self.table.setRowCount(LIM_GROUPS_TABLE_ROWS)
        self.tableHeader.setSectionResizeMode(0, QHeaderView.Interactive)
        self.table.setColumnWidth(0, 320)
        self.table.setColumnWidth(1, 60)

        for i in range(LIM_GROUPS_TABLE_ROWS):
            comboBox = QComboBox()
            comboBox.addItems(['ExactMatch', 'Contains'])
            self.table.setCellWidget(i, 1, comboBox)
            self.comboList.append(comboBox)

            item = QTableWidgetItem()
            self.compListRowDict = dict()
            self.compListRowDict['completion_ls'] = self.completionList
            self.compListRowDict['row'] = None
            item.setData(Qt.UserRole, self.compListRowDict)
            self.table.setItem(i, 0, item)

    def addLine(self):
        nofRows = self.table.rowCount()
        row = nofRows
        self.table.insertRow(row)

        limitItem = QTableWidgetItem()
        comboBox = QComboBox()
        comboBox.addItems(['ExactMatch', 'Contains'])
        self.table.setCellWidget(row, 1, comboBox)
        self.comboList.append(comboBox)

        self.compListRowDict = dict()
        self.compListRowDict['completion_ls'] = self.completionList
        self.compListRowDict['row'] = None
        limitItem.setData(Qt.UserRole, self.compListRowDict)
        self.table.setItem(row, 0, limitItem)


# ---------------------------------------------------------------------------
# PlotFrame  — interactive statistics plot
# ---------------------------------------------------------------------------

class PlotFrame(QFrame):
    def __init__(self, on_cursor_select=None):
        super().__init__()
        self._on_cursor_select = on_cursor_select or (lambda name: print(name))
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)

        self.layout = QGridLayout(self)
        self.layout.setVerticalSpacing(V_LAYOUT_SPACING)
        self.layout.setAlignment(Qt.AlignRight)
        self.setLayout(self.layout)

        self.figure = plt.figure(tight_layout=True)
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas, 0, 0, 1, 1)

        self.ax1 = self.figure.add_subplot(111)
        self.figure.set_size_inches(10.5, 20.5)
        self.ax1.grid(visible=True, which='major', axis='both')
        self.ax1.set_xlabel('Protocol index')
        self.ax2 = self.ax1.twinx()
        self.ax2.grid(visible=True, which='major', axis='both', linestyle='--')

        self.toolbar = NavigationToolbar(self.canvas, self)
        self.layout.addWidget(self.toolbar, 1, 0, 1, 1)
        self.layout.setColumnStretch(0, 1)
        self.patchList = []

    def plot(self, protIndexList, plot_dat, graphIndex, limitName, protocol, ax):
        ylimits0 = []
        ylimits1 = []
        ylimitssec0 = []
        ylimitssec1 = []
        sensornameList = []
        for sensorlist in protocol:
            sensorname = sensorlist.replace('/', '\\')
            sensornameList.append(sensorname)
        color = getGraphColor(graphIndex)

        if ax == 1:
            if plot_dat:
                lineax1 = self.ax1.plot(protIndexList, plot_dat, 'o-', color=color, label=limitName)
                c1 = mplcursors.cursor(lineax1)
                @c1.connect("add")
                def on_add(sel):
                    sel.annotation.arrow_patch.set(arrowstyle="simple", alpha=.00000005)
                    sel.annotation.set_text('')
                    self._on_cursor_select(sensornameList[round(sel.target.index)])
                mplcursors.cursor(self.ax1).connect('add', show_datapoints)
        else:
            if plot_dat:
                lineax2 = self.ax2.plot(protIndexList, plot_dat, 'o-', color=color, label=limitName)
                self.ax2.legend(title='Legends', loc='upper right')
                c1 = mplcursors.cursor(lineax2)
                @c1.connect("add")
                def on_add(sel):
                    sel.annotation.arrow_patch.set(arrowstyle="simple", alpha=.00000005)
                    sel.annotation.set_text('')
                    self._on_cursor_select(sensornameList[round(sel.target.index)])
                mplcursors.cursor(self.ax2).connect('add', show_datapoints)

        for lineIndex in range(len(self.ax1.lines)):
            ylimits0.append(min(self.ax1.lines[lineIndex]._yorig))
            ylimits1.append(max(self.ax1.lines[lineIndex]._yorig))
        if len(ylimits0) != 0:
            ylimits0 = min(ylimits0) - 5 if min(ylimits0) >= 5 else min(ylimits0) - 0.1
            ylimits1 = max(ylimits1) + 5 if max(ylimits1) >= 5 else max(ylimits1) + 0.1
            self.ax1.set_ylim(ymin=ylimits0, ymax=ylimits1)

        for lineIndex in range(len(self.ax2.lines)):
            ylimitssec0.append(min(self.ax2.lines[lineIndex]._yorig))
            ylimitssec1.append(max(self.ax2.lines[lineIndex]._yorig))
        if len(ylimitssec0) != 0:
            ylimitssec0 = min(ylimitssec0) - 5 if min(ylimitssec0) >= 5 else min(ylimitssec0) - 0.1
            ylimitssec1 = max(ylimitssec1) + 5 if max(ylimitssec1) >= 5 else max(ylimitssec1) + 0.1
            self.ax2.set_ylim(ymin=ylimitssec0, ymax=ylimitssec1)

        if len(protIndexList) < 50:
            self.ax1.set_xticks(np.arange(min(protIndexList), max(protIndexList) + 1, 1.0))
        self.ax1.legend(title='Legends', loc='upper left')
        self.canvas.draw()

    def clear(self, ax=0):
        if ax == 0:
            self.ax1.clear()
            self.ax2.clear()
            self.ax1.grid(visible=True, which='major', axis='both')
            self.ax2.grid(visible=True, which='major', axis='both', linestyle='--')
            self.ax1.set_xlabel('Protocol index')
        elif ax == 1:
            self.ax1.clear()
            self.ax1.grid(visible=True, which='major', axis='both')
        else:
            self.ax2.clear()
            self.ax2.grid(visible=True, which='major', axis='both', linestyle='--')
        self.canvas.draw()


# ---------------------------------------------------------------------------
# PlotFrameSysDia  — interactive system-diagrams plot
# ---------------------------------------------------------------------------

class PlotFrameSysDia(QFrame):
    def __init__(self, on_cursor_select=None):
        super().__init__()
        self._on_cursor_select = on_cursor_select or (lambda name: print(name))
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)

        self.layout = QGridLayout(self)
        self.layout.setVerticalSpacing(V_LAYOUT_SPACING)
        self.layout.setAlignment(Qt.AlignCenter)
        self.setLayout(self.layout)

        self.figure = plt.figure(tight_layout=True)
        self.figure.set_size_inches(18.5, 16.5)
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas, 0, 0, 1, 1)

        self.ax1 = self.figure.add_subplot(111)
        self.ax1.grid(visible=True, which='major', axis='both')
        self.ax2 = self.ax1.twinx()
        self.ax2.grid(visible=True, which='major', axis='both', linestyle='--')

        self.toolbar = NavigationToolbar(self.canvas, self)
        self.layout.addWidget(self.toolbar, 1, 0, 1, 1)
        self.layout.setColumnStretch(1, 1)
        self.layout.setRowStretch(1, 1)

    def plot(self, angleData, plot_dat, Prot_param, graphType, idx, ax):
        ylimits0 = []
        ylimits1 = []
        ylimitssec0 = []
        ylimitssec1 = []

        if ax == 1:
            self.ax1.set_ylabel(plotdata.graphStringMapping(graphType))
            if plot_dat.size != 0:
                if 'idealPhaseDiff' in graphType:
                    lineax1 = self.ax1.plot(angleData, plot_dat, 'o-', color='olive', label=Prot_param)
                else:
                    lineax1 = self.ax1.plot(angleData, plot_dat, 'o-', label=Prot_param)
                scatter1 = self.ax1.scatter(angleData, plot_dat, color='none', s=1.23E-7)
                c1 = mplcursors.cursor(lineax1)
                @c1.connect("add")
                def on_add(sel):
                    PTU = sel.artist.get_label().split('.txt')
                    PTUlabel = PTU[0]
                    sel.annotation.arrow_patch.set(arrowstyle='simple', alpha=.00000005)
                    sel.annotation.set_text('')
                    self._on_cursor_select(str(PTUlabel) + '.txt')
                c2 = mplcursors.cursor(scatter1)
                @c2.connect("add")
                def on_add(sel):
                    sel.annotation.set_text('x: ' + str(sel.target[0]) + '\ny: ' + str(sel.target[1]))
        else:
            self.ax2.set_ylabel(plotdata.graphStringMapping(graphType))
            if plot_dat.size != 0:
                if 'idealPhaseDiff' in graphType:
                    lineax2 = self.ax2.plot(angleData, plot_dat, 'o-', color='olive', label=Prot_param)
                else:
                    lineax2 = self.ax2.plot(angleData, plot_dat, 'o-', color=color_list_rev[(idx) % len(color_list)], label=Prot_param)
                scatter2 = self.ax2.scatter(angleData, plot_dat, color='none', s=1.23E-7)
                c1 = mplcursors.cursor(lineax2)
                @c1.connect("add")
                def on_add(sel):
                    PTU = sel.artist.get_label().split('.txt')
                    PTUlabel = PTU[0]
                    sel.annotation.arrow_patch.set(arrowstyle='simple', alpha=.00000005)
                    sel.annotation.set_text('')
                    self._on_cursor_select(str(PTUlabel) + '.txt')
                c2 = mplcursors.cursor(scatter2)
                @c2.connect("add")
                def on_add(sel):
                    sel.annotation.set_text('x: ' + str(sel.target[0]) + '\ny: ' + str(sel.target[1]))

        for lineIndex in range(len(self.ax1.lines)):
            ylimits0.append(min(self.ax1.lines[lineIndex]._yorig))
            ylimits1.append(max(self.ax1.lines[lineIndex]._yorig))
        if len(ylimits0) != 0:
            ylimits0 = min(ylimits0) - 10 if min(ylimits0) >= 1 else min(ylimits0) - 5
            ylimits1 = max(ylimits1) + 10 if max(ylimits1) >= 1 else max(ylimits1) + 5
            self.ax1.set_ylim(ymin=ylimits0, ymax=ylimits1)

        for lineIndex in range(len(self.ax2.lines)):
            ylimitssec0.append(min(self.ax2.lines[lineIndex]._yorig))
            ylimitssec1.append(max(self.ax2.lines[lineIndex]._yorig))
        if len(ylimitssec0) != 0:
            ylimitssec0 = min(ylimitssec0) - 10 if min(ylimitssec0) >= 1 else min(ylimitssec0) - 5
            ylimitssec1 = max(ylimitssec1) + 10 if max(ylimitssec1) >= 1 else max(ylimitssec1) + 5
            self.ax2.set_ylim(ymin=ylimitssec0, ymax=ylimitssec1)

        self.canvas.draw()

    def clear(self, ax=0):
        if ax == 0:
            self.ax1.clear()
            self.ax2.clear()
            self.ax1.grid(visible=True, which='major', axis='both')
            self.ax2.grid(visible=True, which='major', axis='both', linestyle='--')
        elif ax == 1:
            self.ax1.clear()
            self.ax1.grid(visible=True, which='major', axis='both')
        else:
            self.ax2.clear()
            self.ax2.grid(visible=True, which='major', axis='both', linestyle='--')
        self.canvas.draw()


# ---------------------------------------------------------------------------
# QTableLogHandler
# ---------------------------------------------------------------------------

class QTableLogHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.logTable = QTableWidget(0, 3)
        self.logTable.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.logTable.setHorizontalHeaderLabels(['Time', 'Level', 'Message'])
        self.logTableHeader = self.logTable.horizontalHeader()
        self.logTableHeader.setSectionResizeMode(QHeaderView.Stretch)
        self.logTableRow = 0

    def emit(self, record):
        msgStr       = str(record.msg)
        levelnameStr = str(record.levelname)
        timeStr      = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        timeMsStr    = "%s,%03d" % (timeStr, record.msecs)

        levelItem = QTableWidgetItem(levelnameStr)

        # Background colour — semantic dark-theme tints
        bg_hex = LOG_LEVEL_BG_COLORS.get(levelnameStr)
        if bg_hex:
            levelItem.setBackground(QBrush(QColor(bg_hex)))

        # Foreground (text) colour — readable on the dark background
        fg_hex = LOG_LEVEL_FG_COLORS.get(levelnameStr)
        if fg_hex:
            levelItem.setForeground(QBrush(QColor(fg_hex)))

        time_item  = QTableWidgetItem(timeMsStr)
        msg_item   = QTableWidgetItem(msgStr)

        # Propagate the same row colouring to all three cells for visual unity
        if bg_hex:
            time_item.setBackground(QBrush(QColor(bg_hex)))
            msg_item.setBackground(QBrush(QColor(bg_hex)))
        if fg_hex:
            time_item.setForeground(QBrush(QColor(fg_hex)))
            msg_item.setForeground(QBrush(QColor(fg_hex)))

        self.logTable.insertRow(self.logTableRow)
        self.logTable.setItem(self.logTableRow, 0, time_item)
        self.logTable.setItem(self.logTableRow, 1, levelItem)
        self.logTable.setItem(self.logTableRow, 2, msg_item)
        self.logTableRow += 1

        # Auto-scroll to the latest row
        self.logTable.scrollToBottom()

    def clearTable(self):
        self.logTable.clearContents()
        self.logTable.setRowCount(0)
        self.logTableRow = 0
        # Restore headers lost by clearContents()
        self.logTable.setHorizontalHeaderLabels(['Time', 'Level', 'Message'])
