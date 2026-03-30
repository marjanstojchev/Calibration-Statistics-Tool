
import os
import sys
# Ensure 'shared' is in sys.path for direct import
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_shared = os.path.join(_root, 'shared')
if _shared not in sys.path:
    sys.path.insert(0, _shared)

from PySide6.QtWidgets import (QApplication, QFrame, QLabel, QPushButton, QWidget, QProgressBar, QTableWidget,QTableWidgetItem, QTabWidget, QGroupBox, QCheckBox,QHeaderView,
                               QFileDialog,QComboBox, QRadioButton,QLineEdit, QDialog, QDialogButtonBox, QGraphicsDropShadowEffect, QButtonGroup, QStyledItemDelegate, QCompleter)
from PySide6.QtWidgets import (QVBoxLayout,QHBoxLayout,QGridLayout,QSizePolicy)
# from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtUiTools import*
import logging
import time
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import mplcursors
import enum
import plotdata
import numpy as np

from ui_constants import *
from widgets import (
    getGraphColor, show_datapoints, Match,
    dialogLEditErrorStyle, dialogLEditCorrectStyle,
    dialogLabelErrorStyle, dialogLabelCorrectStyle,
    LimitsGroupsSaveDialog, TableItemCompleter,
    PlotFrame, PlotFrameSysDia, QTableLogHandler,
)








# app = QApplication(sys.argv)
# loader = QUiLoader()
# file = QFile(r"C:\Arbeit\test.ui")
# file.open(QFile.ReadOnly)
# myWidget = loader.load(file)
# file.close()
# tab=myWidget.findChild(QTableWidget, 'tableWidget')



app = QApplication.instance() or QApplication(sys.argv)
# app.setStyleSheet(QSS)
#Main Tab Widget
setCurvesInputConfPathLabel = QLabel()
mainWidget = QWidget()
# mainWidget.setStyleSheet(QSS)
# mainWidget.setGeometry(100,100,1200,1050)

shadowTwoGraphBig   = QGraphicsDropShadowEffect(blurRadius=8, xOffset=6, yOffset=6)
shadowTwoGraphSmall = QGraphicsDropShadowEffect(blurRadius=8, xOffset=6, yOffset=6)
shadowThreeGraph3 = QGraphicsDropShadowEffect(blurRadius=8, xOffset=6, yOffset=6)
shadowThreeGraph1 = QGraphicsDropShadowEffect(blurRadius=8, xOffset=6, yOffset=6)
shadowThreeGraph2 = QGraphicsDropShadowEffect(blurRadius=8, xOffset=6, yOffset=6)

shadowFourGraph00 = QGraphicsDropShadowEffect(blurRadius=8, xOffset=6, yOffset=6)
shadowFourGraph01 = QGraphicsDropShadowEffect(blurRadius=8, xOffset=6, yOffset=6)
shadowFourGraph10 = QGraphicsDropShadowEffect(blurRadius=8, xOffset=6, yOffset=6)
shadowFourGraph11 = QGraphicsDropShadowEffect(blurRadius=8, xOffset=6, yOffset=6)
#
# mainSplitter=QSplitter()
# mainSplitter.setOrientation(Qt.Vertical)

mainWidgetLayout = QVBoxLayout()
mainWidgetLayout.setAlignment(Qt.AlignTop)
mainWidgetLayout.setSpacing(V_LAYOUT_SPACING)
mainWidget.setLayout(mainWidgetLayout)

# mainWidgetLayout.addWidget(mainSplitter)

# Main Tabs Widget
mainTabWidget = QTabWidget()

mainTabWidgetLayout = QHBoxLayout()
mainTabWidgetLayout.setAlignment(Qt.AlignTop)
mainTabWidgetLayout.setSpacing(H_LAYOUT_SPACING)

mainTabWidget.setLayout(mainTabWidgetLayout)
mainTabWidget.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Minimum)
mainWidgetLayout.addWidget(mainTabWidget)

# PST-60: Import tab modules (must be after QApplication exists)
from tabs.parse_prot_tab import *
mainTabWidget.insertTab(0, parseProtTab, 'Parse Protocols')
from tabs.sys_diag_tab import *
mainTabWidget.insertTab(1, sysDiagTab, 'System Diagrams')
from tabs.tx_ant_diag_tab import *
mainTabWidget.insertTab(2, txAntDiagTab, 'Tx-Antenna Diagrams')

# PST-68: Import antPatTab module (must be after QApplication exists)
from tabs.ant_pat_tab import *
mainTabWidget.insertTab(4, antPatTab, 'Antenna Patterns')

############
############

# NOTE: Removed tabs (code available in StatisticToolPython_New):
# - System Diagram Limits Tab (limSysDiagTab)
# - Certificates Tab (certTab)
# - Statistics Tab (statsTab)
# - Set Curves Tab (setCurvesTab)

############
############


## Statistics Tab
statsTab = QWidget()
statsTab.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding)
# statsTab.setFixedHeight(600)

statsLayout = QGridLayout()
statsLayout.setHorizontalSpacing(H_LAYOUT_SPACING)
# statsLayout.setVerticalSpacing(V_LAYOUT_SPACING)
statsLayout.setAlignment(Qt.AlignTop)

statsTab.setLayout(statsLayout)

#### Plot Setup Scalling Frame
statsTableColMapping = {
    'graph':0,
    'axis':1,
    'error':2,
    'protType':3,
    'limitName':4,
    'stDev':5,
    'mean':6,
    'min':7,
    'max':8,
    'maxDev':9,
    'upperLimit':10,
    'lowerLimit':11,
    'cg':12
}


statsTable = QTableWidget(0,13)
statsTable.setFixedHeight(220)
statsTable.setHorizontalHeaderLabels(['Graph','Axis','Error','Protocol Type','Limit Name','Standard Deviation','Mean','Min.','Max.','Max. Deviation','Upper Limit','Lower Limit','Cg'])
statsTable.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding)
# statsTable.setEditTriggers(QTableWidget.DoubleClicked)
statsLayout.addWidget(statsTable, 0,0,1,2)
statsTableHeader = statsTable.horizontalHeader()
statsTableHeader.setSectionResizeMode(QHeaderView.Stretch)
statsTable.resizeColumnsToContents()
statsTable.setSortingEnabled(False)



####
statsButtonFrame = QFrame()
statsButtonFrame.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Maximum)
statsButtonFrameLayout = QHBoxLayout()
statsButtonFrameLayout.setSpacing(H_LAYOUT_SPACING)
# statsButtonFrameLayout.setAlignment(Qt.AlignTop )
statsButtonFrame.setLayout(statsButtonFrameLayout)
####
statsLayout.addWidget(statsButtonFrame, 1,0,1,1)

statsClearBtn = QPushButton('Clear')
statsClearBtn.setFixedSize(PUSH_BTN_H_SIZE,PUSH_BTN_V_SIZE)
statsButtonFrameLayout.addWidget(statsClearBtn,stretch=1, alignment=Qt.AlignLeft )

statsSeriesDistBtn = QPushButton('Statistical Series')
statsSeriesDistBtn.setFixedSize(PUSH_BTN_H_SIZE,PUSH_BTN_V_SIZE)
statsButtonFrameLayout.addWidget(statsSeriesDistBtn,stretch=1, alignment=Qt.AlignLeft )

#####
statsGroupsTypeButtonGroup = QButtonGroup()
statsGroupsTypeButtonGroup.setExclusive(True)

#####
statsGroupNameString = 'Show Groups: '
statsGroupNameLabel  = QLabel(statsGroupNameString)
statsButtonFrameLayout.addWidget(statsGroupNameLabel, alignment=Qt.AlignLeft )

statsGroupsTypeBurnInRadio = QRadioButton('BurnIn')
statsButtonFrameLayout.addWidget(statsGroupsTypeBurnInRadio)
statsGroupsTypeButtonGroup.addButton(statsGroupsTypeBurnInRadio,0)

#####
statsGroupsTypeCalRadio = QRadioButton('Calibration')
statsButtonFrameLayout.addWidget(statsGroupsTypeCalRadio)
statsGroupsTypeButtonGroup.addButton(statsGroupsTypeCalRadio,1)

statsGroupBackBtn = QPushButton('< Group')
statsGroupBackBtn.setFixedSize(PUSH_BTN_H_SIZE,PUSH_BTN_V_SIZE)
statsButtonFrameLayout.addWidget(statsGroupBackBtn,stretch=1, alignment=Qt.AlignLeft )

statsGroupForwardBtn = QPushButton('Group >')
statsGroupForwardBtn.setFixedSize(PUSH_BTN_H_SIZE,PUSH_BTN_V_SIZE)
statsButtonFrameLayout.addWidget(statsGroupForwardBtn,stretch=1, alignment=Qt.AlignLeft)

statsGroupSaveBtn = QPushButton('Save Group')
statsGroupSaveBtn.setFixedSize(PUSH_BTN_H_SIZE,PUSH_BTN_V_SIZE)
statsButtonFrameLayout.addWidget(statsGroupSaveBtn,stretch=1, alignment=Qt.AlignLeft )

####
statsGroupNameString = 'Group Name: '
statsGroupNameLabel  = QLabel(statsGroupNameString)
statsButtonFrameLayout.addWidget(statsGroupNameLabel, alignment=Qt.AlignLeft )



# ##search Tab ##new
# statsSearchTabFrame = QFrame()
# statsSearchTabFrame.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Maximum)
# statsSearchTabFrameLayout = QHBoxLayout()
# statsSearchTabFrameLayout.setSpacing(H_LAYOUT_SPACING)
# statsSearchTabFrameLayout.setAlignment(Qt.AlignRight)
# statsSearchTabFrame.setLayout(statsSearchTabFrameLayout)
# statsLayout.addWidget(statsSearchTabFrame,0,1,1,1)



# statsSearchTab = QLabel('Search Tab')
# statsSearchTabFrameLayout.addWidget(statsSearchTab)
# statsSearchTabFrameLayoutEdit=QLineEdit()
# statsSearchTabFrameLayoutEdit.setFixedSize(120, LEDIT_BTN_V_SIZE)
# statsSearchTabFrameLayoutEdit.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
# statsSearchTabFrameLayout.addWidget(statsSearchTabFrameLayoutEdit)


####
statsGroupPptxFrame = QFrame()
statsGroupPptxFrame.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Maximum)
statsGroupPptxFrameLayout = QHBoxLayout()
statsGroupPptxFrameLayout.setSpacing(H_LAYOUT_SPACING)
statsGroupPptxFrameLayout.setAlignment(Qt.AlignRight )
statsGroupPptxFrame.setLayout(statsGroupPptxFrameLayout)
statsLayout.addWidget(statsGroupPptxFrame, 1,1,1,1)

statsGroupPptxBtn = QPushButton('Export .pptx')
statsGroupPptxBtn.setFixedSize(PUSH_BTN_H_SIZE,PUSH_BTN_V_SIZE)
statsGroupPptxFrameLayout.addWidget(statsGroupPptxBtn,stretch=1, alignment=Qt.AlignRight )

####
statsInputConfFrame = QFrame()
statsInputConfFrame.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Maximum)
statsInputConfFrameLayout = QHBoxLayout()
statsInputConfFrameLayout.setSpacing(H_LAYOUT_SPACING)
statsInputConfFrameLayout.setAlignment(Qt.AlignRight )
statsInputConfFrame.setLayout(statsInputConfFrameLayout)
statsLayout.addWidget(statsInputConfFrame, 1,1,1,1)

statsInputConfBtn = QPushButton('Load Input Config File')
statsInputConfBtn.setFixedSize(140,PUSH_BTN_V_SIZE)
statsInputConfBtn.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
statsInputConfFrameLayout.addWidget(statsInputConfBtn, stretch=1, alignment=Qt.AlignRight)


statsInputConfPathString = 'Import input config '
statsInputConfPathLabel  = QLabel(statsInputConfPathString)
statsInputConfPathLabel.setToolTip(statsInputConfPathString)
statsInputConfPathLabel.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)


statsInputConfFrameLayout.addWidget(statsInputConfPathLabel, alignment=Qt.AlignRight)


statsInputConfFDialog = QFileDialog()
statsInputConfFDialog.setFileMode(QFileDialog.ExistingFile)
statsInputConfFDialog.setNameFilter("Config File Input (*.json)")
statsInputConfFDialog.setFilter(QDir.Filter.Files)



statsGroupsSaveDialog = LimitsGroupsSaveDialog()


###

# Label function
def show_datapoints(sel):
    xi, yi = sel[0], sel[0]
    xi, yi = xi._xorig.tolist(), yi._yorig.tolist()
    sel.annotation.set_text('x: '+ str(xi[round(sel.target.index)])+\
            '\n'+'y: '+ str(yi[round(sel.target.index)]))

statsPlotFrame = PlotFrame()
statsPlotFrame.setObjectName('PlotFrame')
statsPlotFrame.setStyleSheet(plotFrameStyle)

statsLayout.addWidget(statsPlotFrame, 2,0,1,2)

mainTabWidget.insertTab(6,statsTab,'Statistics')

#############################################################
# SystemDiagrams Inetractive Mode Tab
SysDiaInterTab = QWidget()
SysDiaInterTab.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding)

SysDiaInterLayout = QGridLayout()
SysDiaInterLayout.setHorizontalSpacing(H_LAYOUT_SPACING)
# SysDiaInterLayout.setVerticalSpacing(V_LAYOUT_SPACING)
SysDiaInterLayout.setAlignment(Qt.AlignLeft)
SysDiaInterTab.setLayout(SysDiaInterLayout)


# protocolList Table
SysDiaInterTableProtColMapping = {
    'graph':0,
    'Protocol':1,
}
SysDiaInterTableProtocol = QTableWidget(0,2)
SysDiaInterTableProtocol.setFixedHeight(200)
SysDiaInterTableProtocol.setFixedWidth(600)
SysDiaInterTableProtocol.setHorizontalHeaderLabels(['Graph', 'Protocol'])
SysDiaInterTableProtocol.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding)
# SysDiaInterLayout.addWidget(SysDiaInterTableProtocol, 1,2,1,1)
SysDiaInterLayout.addWidget(SysDiaInterTableProtocol, 1,2,1,1)
SysDiaInterTableProtocolHeader = SysDiaInterTableProtocol.horizontalHeader()
SysDiaInterTableProtocolHeader.setSectionResizeMode(QHeaderView.Stretch)
SysDiaInterTableProtocol.resizeColumnsToContents()
SysDiaInterTableProtocol.setSortingEnabled(False)

# Parameters list table
SysDiaInterTableParamColMapping = {
    'graph':0,
    'axis':1,
    'MeasurementName': 2
}
SysDiaInterTableParam = QTableWidget(0,3)
SysDiaInterTableParam.setFixedHeight(470)
SysDiaInterTableParam.setFixedWidth(600)
SysDiaInterTableParam.setHorizontalHeaderLabels(['Graph','Axis','Measurement Name'])
SysDiaInterTableParam.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding)
# SysDiaInterLayout.addWidget(SysDiaInterTableParam, 2,2,1,1)
SysDiaInterLayout.addWidget(SysDiaInterTableParam, 2,2,2,1)
SysDiaInterTableParamHeader = SysDiaInterTableParam.horizontalHeader()
SysDiaInterTableParamHeader.setSectionResizeMode(QHeaderView.Stretch)
SysDiaInterTableParam.resizeColumnsToContents()
SysDiaInterTableParam.setSortingEnabled(False)


# start button
SysDiaInterStartFrame = QFrame()
SysDiaInterStartFrame.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Maximum)
SysDiaInterStartFrameLayout = QHBoxLayout()
SysDiaInterStartFrameLayout.setSpacing(H_LAYOUT_SPACING)
SysDiaInterStartFrameLayout.setAlignment(Qt.AlignLeft)
SysDiaInterStartFrame.setLayout(SysDiaInterStartFrameLayout)
# SysDiaInterLayout.addWidget(SysDiaInterStartFrame, 0,0,1,1)
SysDiaInterLayout.addWidget(SysDiaInterStartFrame, 0,0,1,1)

SysDiaInterStartBtn = QPushButton('Start')
SysDiaInterStartBtn.setFixedSize(PUSH_BTN_H_SIZE,PUSH_BTN_V_SIZE)
SysDiaInterStartFrameLayout.addWidget(SysDiaInterStartBtn, stretch=1, alignment=Qt.AlignLeft )


SysDiaInterClrGrBtn = QPushButton('Clear')
SysDiaInterClrGrBtn.setFixedSize(PUSH_BTN_H_SIZE,PUSH_BTN_V_SIZE)
SysDiaInterStartFrameLayout.addWidget(SysDiaInterClrGrBtn, stretch=1, alignment=Qt.AlignRight)

# On/Off button
SysDiaInterSwitchBtn = QPushButton('On/Off')
SysDiaInterSwitchBtn.setFixedSize(PUSH_BTN_H_SIZE,PUSH_BTN_V_SIZE)
SysDiaInterStartFrameLayout.addWidget(SysDiaInterSwitchBtn,stretch=0.5, alignment=Qt.AlignRight)

SysDiaInterPlotFrame = PlotFrameSysDia()
SysDiaInterPlotFrame.setObjectName('PlotFrame')
SysDiaInterPlotFrame.setStyleSheet(plotFrameStyle)

SysDiaInterLayout.maximumSize()
SysDiaInterLayout.minimumSize()
# SysDiaInterLayout.addWidget(SysDiaInterPlotFrame, 1,0,3,2)
SysDiaInterLayout.addWidget(SysDiaInterPlotFrame, 1,0,3,2)


#
mainTabWidget.insertTab(8,SysDiaInterTab,'System Diagrams Interactive')


##
mainTabWidget.setCurrentIndex(0)
#

mainLogTableFrame = QFrame()
mainLogTableFrame.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding)
mainLogTableFrameLayout = QHBoxLayout()
mainLogTableFrameLayout.setAlignment(Qt.AlignTop)
mainLogTableFrameLayout.setSpacing(H_LAYOUT_SPACING)
mainLogTableFrame.setLayout(mainLogTableFrameLayout)

mainWidgetLayout.addWidget(mainLogTableFrame)

mainLogTableClearBtn = QPushButton('Clear')
mainLogTableClearBtn.setFixedSize(PUSH_BTN_H_SIZE,PUSH_BTN_V_SIZE)
mainLogTableFrameLayout.addWidget(mainLogTableClearBtn,stretch=1)

mainLogTableHandler = QTableLogHandler()
mainLogTable = mainLogTableHandler.logTable
mainLogTableHeader = mainLogTableHandler.logTable.horizontalHeader()
mainLogTableHeader.setSectionResizeMode(0,QHeaderView.ResizeToContents)
mainLogTableHeader.setSectionResizeMode(1,QHeaderView.ResizeToContents)
mainLogTableHeader.setSectionResizeMode(2,QHeaderView.Stretch)

mainLogTable.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding)
mainLogTableFrameLayout.addWidget(mainLogTable,stretch=3)

# index = mainSplitter.indexOf(mainLogTable.logTable)
# mainSplitter.setCollapsible(index, False)

##
mainWidget.show()
# sys.exit(app.exec_())

