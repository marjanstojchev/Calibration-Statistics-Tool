
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




color_list = ['b', 'r', 'g', 'm', 'k', 'c', 'orange', 'midnightblue',
                  'maroon', 'springgreen', 'purple', 'dimgrey', 'teal',
                  'yellow', 'thistle', 'lime', 'darkgoldenrod', 'rosybrown',
                  'lightcoral', 'darkred', 'teal', 'navy', 'mediumslateblue',
                  'khaki', 'indigo', 'palevioletred', 'yellowgreen',
                  'palegreen', 'olivedrab', 'tomato']

color_list_rev = []
for rev_ord in reversed(range(len(color_list))):
    color_list_rev.append(color_list[rev_ord])


# platPlugin='C:\ProgramData\Anaconda3\Lib\site-packages\PySide6\plugins\platforms'
# os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = platPlugin

QSS = '''

 QTabWidget{
 background-color: cyan;
}
.QPushButton{
    background-color: cyan;
    margin: 0px;
    padding: 0px;

}

'''
# qproperty-alignment: 'AlignVCenter | AlignRight';
# border - width: 2
# px;
# border - style: solid;
# border - color: darkblue;

antPatTableStyle='''
.QFrame#Frame {
    background-color: white;
    border-style: solid;
    border-color: grey;
    border-width: 2px;
    border-radius: 10px;


}
.QFrame#SubFrame1 {
    background-color: white;
    border-style: none;
    border-color: grey;
    border-width: 2px;
    border-radius: 10px;


}

.QFrame#SubFrame2 {
    background-color: lavender;
    border-style: none;
    border-color: grey;
    border-width: 2px;
    border-radius: 10px;


}
'''
slideSymbolStyle='''
.QFrame{
    background-color: lavender;
    border-style: solid;
    border-color: grey;
    border-width: 2px;
    border-radius: 10px;


}

'''

plotFrameStyle='''
.PlotFrame#PlotFrame{
    border-style: solid;
    border-color: grey;
    border-width: 2px;
    border-radius: 10px;

}

'''
lineStyle='''
.QFrame{
   /* background-color: silver; */
   background-color: lightgrey;

}
'''

# app = QApplication(sys.argv)
# loader = QUiLoader()
# file = QFile(r"C:\Arbeit\test.ui")
# file.open(QFile.ReadOnly)
# myWidget = loader.load(file)
# file.close()
# tab=myWidget.findChild(QTableWidget, 'tableWidget')



app = QApplication(sys.argv)
# app.setStyleSheet(QSS)
#Main Tab Widget
setCurvesInputConfPathLabel = QLabel()
mainWidget = QWidget()
# mainWidget.setStyleSheet(QSS)
# mainWidget.setGeometry(100,100,1200,1050)

PROGRESS_BAR_H_SIZE   = 250
PUSH_BTN_H_SIZE       = 120
PUSH_BTN_V_SIZE       = 30
LEDIT_BTN_H_SIZE      = 100
LEDIT_BTN_PATH_H_SIZE = 280
LABEL_PATH_H_SIZE     = 320
LEDIT_BTN_V_SIZE      = 20
H_LAYOUT_SPACING      = 12
V_LAYOUT_SPACING      = 12
GRID_LAYOUT_SPACING   = 12
PARSE_PROT_TABLE_ROWS = 20
STATS_TABLE_ROWS=7
LIM_GROUPS_TABLE_ROWS = 10
V_LINE_WIDTH  = 1
H_LINE_HEIGHT = 1
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

#
## Parse Protocols Tab
parseProtTab    = QWidget()
parseProtLayout = QGridLayout()
parseProtLayout.setHorizontalSpacing(H_LAYOUT_SPACING)
parseProtLayout.setVerticalSpacing(V_LAYOUT_SPACING)
# parseProtLayout.setRowStretch(0,1)
# parseProtLayout.setRowStretch(0,1)
# parseProtLayout.setRowStretch(0,1)

parseProtLayout.setColumnStretch(0, 1)
parseProtLayout.setColumnStretch(1, 1)
parseProtLayout.setColumnStretch(2, 2)

parseProtLayout.setAlignment(Qt.AlignTop)

parseProtTab.setLayout(parseProtLayout)
parseProtTab.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
mainTabWidget.insertTab(0, parseProtTab, 'Parse Protocols')

### Parse Protocols Frame
# parseProtFrame=QFrame()
# parseProtFrame.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding)
# parseProtLayout.addWidget(parseProtFrame,0,0)
# # parseProtFrameLayout=QVBoxLayout()
# # parseProtFrameLayout.setSpacing(V_LAYOUT_SPACING)
# parseProtFrame.setLayout(parseProtFrameLayout)

###### Parse Data Frame
parseProtParseDataFrame = QFrame()
parseProtParseDataFrame.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
parseProtParseDataFrameLayout=QHBoxLayout()
parseProtParseDataFrameLayout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
parseProtParseDataFrameLayout.setSpacing(H_LAYOUT_SPACING)
parseProtParseDataFrame.setLayout(parseProtParseDataFrameLayout)

parseProtLayout.addWidget(parseProtParseDataFrame, 0, 0, 1, 2, alignment=Qt.AlignLeft | Qt.AlignTop)

#### Parse Protocols - Parse Data PushButton
parseProtParseDataPushBtn = QPushButton('Parse Data')
parseProtParseDataPushBtn.setObjectName('1')
# parseProtParseDataPushBtn.setStyleSheet(QSS)
parseProtParseDataPushBtn.setFixedSize(PUSH_BTN_H_SIZE, PUSH_BTN_V_SIZE)
parseProtParseDataPushBtn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
parseProtParseDataFrameLayout.addWidget(parseProtParseDataPushBtn)

#### Parse Protocols - Clear Data PushButton
parseProtClearDataPushBtn = QPushButton('Clear Data')
parseProtClearDataPushBtn.setFixedSize(PUSH_BTN_H_SIZE, PUSH_BTN_V_SIZE)
parseProtClearDataPushBtn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
parseProtParseDataFrameLayout.addWidget(parseProtClearDataPushBtn)

###### Write Statistic Frame
parseProtParseDataFrame = QFrame()
parseProtParseDataFrame.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
parseProtParseDataFrameLayout=QHBoxLayout()
parseProtParseDataFrameLayout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
parseProtParseDataFrameLayout.setSpacing(H_LAYOUT_SPACING)
parseProtParseDataFrame.setLayout(parseProtParseDataFrameLayout)

parseProtLayout.addWidget(parseProtParseDataFrame, 1, 0, 1, 2, alignment=Qt.AlignLeft | Qt.AlignTop)
#####
parseProtWriteStatsPushBtn = QPushButton('Parse / Write Statistic')
parseProtWriteStatsPushBtn.setFixedSize(PUSH_BTN_H_SIZE, PUSH_BTN_V_SIZE)
parseProtWriteStatsPushBtn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
parseProtParseDataFrameLayout.addWidget(parseProtWriteStatsPushBtn)


#####
parseProtClearStatsDataBtn = QPushButton('Clear Statistic Data')
parseProtClearStatsDataBtn.setFixedSize(PUSH_BTN_H_SIZE, PUSH_BTN_V_SIZE)
parseProtClearStatsDataBtn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
parseProtParseDataFrameLayout.addWidget(parseProtClearStatsDataBtn)

# New
parseProtMergePPTXBtn = QPushButton('Merge PPTX')
parseProtMergePPTXBtn.setFixedSize(PUSH_BTN_H_SIZE, PUSH_BTN_V_SIZE)
parseProtMergePPTXBtn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
parseProtParseDataFrameLayout.addWidget(parseProtMergePPTXBtn)

#### Parse Protocols GroupBox
# parseProtLoadDataTablesFrame=QFrame()
# parseProtLoadDataTablesFrame.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding)
# parseProtLoadDataTablesFrameLayout=QHBoxLayout()
# parseProtLoadDataTablesFrameLayout.setAlignment(Qt.AlignTop)
# parseProtLoadDataTablesFrameLayout.setSpacing(H_LAYOUT_SPACING)
# parseProtLoadDataTablesFrame.setLayout(parseProtLoadDataTablesFrameLayout)

parseProtGroupBox = QGroupBox('Load Data')
parseProtGroupBox.setMinimumHeight(600)
# parseProtGroupBox.setFixedWidth(210)
parseProtGroupBox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
# parseProtLayout.addWidget(parseProtLoadDataTablesFrame,2,0,1,2,alignment=Qt.AlignTop)
parseProtLayout.addWidget(parseProtGroupBox, 2, 0, 2, 1, alignment=Qt.AlignTop)


parseProtGroupBoxLayout = QHBoxLayout()
parseProtGroupBoxLayout.setSpacing(H_LAYOUT_SPACING)
parseProtGroupBoxLayout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
parseProtGroupBox.setLayout(parseProtGroupBoxLayout)

# parseProtLoadDataTablesFrameLayout.addWidget(parseProtGroupBox)

parseProtGroupBoxFrame = QFrame()
parseProtGroupBoxFrame.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
parseProtGroupBoxFrameLayout = QVBoxLayout()
parseProtGroupBoxFrameLayout.setSpacing(V_LAYOUT_SPACING)
parseProtGroupBoxFrameLayout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

parseProtGroupBoxFrame.setLayout(parseProtGroupBoxFrameLayout)
parseProtGroupBoxLayout.addWidget(parseProtGroupBoxFrame)

##### Parse Protocols System Diag. CheckBox
parseProtSysDiagCheckBox = QCheckBox('Search PTU2 Files')
parseProtSysDiagCheckBox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
parseProtSysDiagCheckBox.setChecked(True)
parseProtGroupBoxFrameLayout.addWidget(parseProtSysDiagCheckBox,stretch=0)

##### Parse Protocols TxAnt Diag. CheckBox
parseProtTxAntDiagCheckBox = QCheckBox('Search for Tx-Ant. Diag. Files')
parseProtTxAntDiagCheckBox.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
parseProtTxAntDiagCheckBox.setChecked(True)
parseProtGroupBoxFrameLayout.addWidget(parseProtTxAntDiagCheckBox,stretch=0)

##### Parse Protocols Use Protocols With Label
parseProtUseProtWithLabel = QLabel('Use Protocols With:')
parseProtUseProtWithLabel.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
parseProtGroupBoxFrameLayout.addWidget(parseProtUseProtWithLabel, stretch=0)

#### Parse only newest protocol
parseProtnewProtCheckBox = QCheckBox('Latest Protocol')
parseProtnewProtCheckBox.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
parseProtnewProtCheckBox.setChecked(False)
parseProtGroupBoxFrameLayout.addWidget(parseProtnewProtCheckBox, stretch=1)

#### Ignore BurnIn At Start
parseProtBurnStartCheckBox = QCheckBox('BurnIn Start')
parseProtBurnStartCheckBox.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
parseProtBurnStartCheckBox.setChecked(False)
parseProtGroupBoxFrameLayout.addWidget(parseProtBurnStartCheckBox, stretch=1)

##### Parse Protocols EOL Error CheckBox
parseProtEolErrorCheckBox = QCheckBox('EOL Error(s)')
parseProtEolErrorCheckBox.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
parseProtEolErrorCheckBox.setChecked(False)
parseProtGroupBoxFrameLayout.addWidget(parseProtEolErrorCheckBox, stretch=0)

##### Parse Protocols EOL Abort Criterion CheckBox
parseProtEolAbortCheckBox = QCheckBox('EOL Abbort Criterion(s)')
parseProtEolAbortCheckBox.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
parseProtEolAbortCheckBox.setChecked(True)
parseProtGroupBoxFrameLayout.addWidget(parseProtEolAbortCheckBox, stretch=0)

##### Parse Protocols EOL Meas Limits exceeded CheckBox
parseProtEolMeasLimitsCheckBox = QCheckBox('EOL Meas. Limits Exceeded')
parseProtEolMeasLimitsCheckBox.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
parseProtEolMeasLimitsCheckBox.setChecked(True)
parseProtGroupBoxFrameLayout.addWidget(parseProtEolMeasLimitsCheckBox, stretch=0)


# #### Parse only End
# parseProtBurnInStartCheckBox = QCheckBox('BurnIn At Start')
# parseProtBurnInStartCheckBox.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Fixed)
# parseProtBurnInStartCheckBox.setChecked(True)
# parseProtGroupBoxFrameLayout.addWidget(parseProtBurnInStartCheckBox,stretch=0)
#####
parseProtAddAndParseSepLabel = QLabel('Protocol Type:')
parseProtAddAndParseSepLabel.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
parseProtGroupBoxFrameLayout.addWidget(parseProtAddAndParseSepLabel, stretch=0)
#####
parseProtBurnInCalGroup = QButtonGroup()
parseProtBurnInCalGroup.setExclusive(True)

parseProtBurnInCalGroupRadio1 = QRadioButton('Auto Recognition')
parseProtGroupBoxFrameLayout.addWidget(parseProtBurnInCalGroupRadio1)
parseProtBurnInCalGroup.addButton(parseProtBurnInCalGroupRadio1, 0)

#####
parseProtBurnInCalGroupRadio2 = QRadioButton('BurnIn')
parseProtGroupBoxFrameLayout.addWidget(parseProtBurnInCalGroupRadio2)
parseProtBurnInCalGroup.addButton(parseProtBurnInCalGroupRadio2, 1)

#####
parseProtBurnInCalGroupRadio3 = QRadioButton('Calibration')
parseProtGroupBoxFrameLayout.addWidget(parseProtBurnInCalGroupRadio3)
parseProtBurnInCalGroup.addButton(parseProtBurnInCalGroupRadio3, 2)


#### Parse Protocols - Import Protocols - File List PushButton
parseProtImportProtFListPushBtn = QPushButton('Protocol File List')
parseProtImportProtFListPushBtn.setFixedSize(PUSH_BTN_H_SIZE, PUSH_BTN_V_SIZE)
parseProtImportProtFListPushBtn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
parseProtGroupBoxFrameLayout.addWidget(parseProtImportProtFListPushBtn, stretch=0)

##### Parse Protocols - Import Protocols -File List FileDialog
parseProtImportProtFListFDialog = QFileDialog()
parseProtImportProtFListFDialog.setFileMode(QFileDialog.ExistingFiles)
parseProtImportProtFListFDialog.setNameFilter("Protocols (*_Protocol.txt)")
# parseProtImportProtFListFDialog.setFilter(QDir.Filter.Files)

##### Parse Protocols - Import Protocols -File Path FileDialog
parseProtImportProtDirPathFDialog = QFileDialog()
parseProtImportProtDirPathFDialog.setFileMode(QFileDialog.Directory)

# New
# parseProtImportProtDirPathFDialog.setFileMode(QFileDialog.DirectoryOnly)
# parseProtImportProtDirPathFDialog.setOption(QFileDialog.DontUseNativeDialog, True)
# file_view = parseProtImportProtDirPathFDialog.findChild(QListView, 'listView')

# # to make it possible to select multiple directories:
# if file_view:
#     file_view.setSelectionMode(QAbstractItemView.MultiSelection)
# f_tree_view = parseProtImportProtDirPathFDialog.findChild(QTreeView)
# if f_tree_view:
#     f_tree_view.setSelectionMode(QAbstractItemView.MultiSelection)


# parseProtImportProtDirPathFDialog.setNameFilter("Protocols (*_Protocol.txt)")
# parseProtImportProtFListFDialog.setFilter(QDir.Filter.Files)

# parseProtImportProtFListFDialog.setDirectory('C://')
# def fun():
#     if parseProtImportProtFListFDialog.exec_():
#         fileNames = parseProtImportProtFListFDialog.selectedFiles()
#
# parseProtImportProtFListPushBtn.clicked.connect(fun)

#### Parse Protocols - Import Protocols - File List PushButton
parseProtImportProtDirPathPushBtn = QPushButton('Protocol Directory')
parseProtImportProtDirPathPushBtn.setFixedSize(PUSH_BTN_H_SIZE, PUSH_BTN_V_SIZE)
parseProtImportProtDirPathPushBtn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
parseProtGroupBoxFrameLayout.addWidget(parseProtImportProtDirPathPushBtn, stretch=0)

####
parseProtHLine = QFrame()
parseProtHLine.setFixedHeight(H_LINE_HEIGHT)
parseProtHLine.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
parseProtHLine.setStyleSheet(lineStyle)
parseProtGroupBoxFrameLayout.addWidget(parseProtHLine)

##### Parse Protocols Use Protocols With Label
parseProtAddAndParseSepLabel = QLabel('Add and Parse Separately')
parseProtAddAndParseSepLabel.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
parseProtGroupBoxFrameLayout.addWidget(parseProtAddAndParseSepLabel, stretch=0)

#### Parse Protocols - Import PTU-2 Files PushButton
parseProtAddAndParsePtu2PushBtn = QPushButton('PTU-2 Files')
parseProtAddAndParsePtu2PushBtn.setFixedSize(PUSH_BTN_H_SIZE, PUSH_BTN_V_SIZE)
parseProtAddAndParsePtu2PushBtn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
parseProtGroupBoxFrameLayout.addWidget(parseProtAddAndParsePtu2PushBtn, stretch=0)

##### Parse Protocols - Import Protocols -File List FileDialog
parseProtAddAndParsePtu2FDialog = QFileDialog()
parseProtAddAndParsePtu2FDialog.setFileMode(QFileDialog.ExistingFiles)
parseProtAddAndParsePtu2FDialog.setNameFilter("PTU-2 Files (*ptu2.txt)")

#### Parse Protocols - Import PTU-2 Files PushButton
parseProtAddAndParseTxAntDiagPushBtn = QPushButton('Tx-Ant. Diag. Files')
parseProtAddAndParseTxAntDiagPushBtn.setFixedSize(PUSH_BTN_H_SIZE, PUSH_BTN_V_SIZE)
parseProtAddAndParseTxAntDiagPushBtn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
parseProtGroupBoxFrameLayout.addWidget(parseProtAddAndParseTxAntDiagPushBtn, stretch=0)

parseProtAddAndParseTxAntDiagFDialog = QFileDialog()
# parseProtAddAndParseTxAntSortFiltProxyModel=QSortFilterProxyModel()
# parseProtAddAndParseTxAntRegExp=QRegularExpression('^TxAnt\d_Diagram0.txt$')
# parseProtAddAndParseTxAntSortFiltProxyModel.setFilterRegExp(parseProtAddAndParseTxAntRegExp)
# parseProtAddAndParseTxAntDiagFDialog.setProxyModel(parseProtAddAndParseTxAntSortFiltProxyModel)
# parseProtAddAndParseTxAntDiagFDialog.setOption(QFileDialog.DontUseNativeDialog,True)
parseProtAddAndParseTxAntDiagFDialog.setFileMode(QFileDialog.ExistingFiles)
parseProtAddAndParseTxAntDiagFDialog.setNameFilter("Tx-Ant. Diag. Files (*Diagram0.txt)")


####
parseProtHLine = QFrame()
parseProtHLine.setFixedHeight(H_LINE_HEIGHT)
parseProtHLine.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
parseProtHLine.setStyleSheet(lineStyle)
parseProtGroupBoxFrameLayout.addWidget(parseProtHLine)

## Parse Protocols Sensor Muster
parseProtSensorMusterCheckBox = QCheckBox()
parseProtSensorMusterCheckBox.setText('Use Sensor Muster')
parseProtSensorMusterCheckBox.setChecked(False)
parseProtGroupBoxFrameLayout.addWidget(parseProtSensorMusterCheckBox)

# parseProtSensorMusterIntValidator=QIntValidator()
# parseProtSensorMusterIntValidator.setRange(0,200)

#####

parseProtSensorMusterLabel = QLabel('Sensor Muster Parts: \n(sep. by white space)')
parseProtGroupBoxFrameLayout.addWidget(parseProtSensorMusterLabel)

#####

parseProtSensorMusterLEdit = QLineEdit()
parseProtSensorMusterLEdit.setFixedSize(LEDIT_BTN_H_SIZE,LEDIT_BTN_V_SIZE)
# parseProtSensorMusterLEdit.setValidator(parseProtSensorMusterIntValidator)
parseProtGroupBoxFrameLayout.addWidget(parseProtSensorMusterLEdit)


### Parse Protocols Stats GroupBox

parseProtStatsGroupBox = QGroupBox('Data Stats')
parseProtStatsGroupBox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
parseProtStatsGroupBox.setFixedWidth(210)
parseProtStatsGroupBoxLayout = QHBoxLayout()
parseProtStatsGroupBoxLayout.setSpacing(V_LAYOUT_SPACING)
parseProtStatsGroupBoxLayout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
parseProtStatsGroupBox.setLayout(parseProtStatsGroupBoxLayout)
parseProtLayout.addWidget(parseProtStatsGroupBox, 2, 1, 1, 1, alignment=Qt.AlignTop)

#### Parse Protocols GroupBox Stats Frame

parseProtGroupBoxStatsFrame = QFrame()
parseProtGroupBoxStatsFrame.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
parseProtGroupBoxStatsFrameLayout = QVBoxLayout()
parseProtGroupBoxStatsFrameLayout.setSpacing(V_LAYOUT_SPACING)
parseProtGroupBoxStatsFrameLayout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

parseProtGroupBoxStatsFrame.setLayout(parseProtGroupBoxStatsFrameLayout)

parseProtStatsGroupBoxLayout.addWidget(parseProtGroupBoxStatsFrame)
#####
parseProtTextTab = '    '
parseProtLoadedProtStr   = 'Loaded Protocols: '
parseProtLoadedProtLabel = QLabel(parseProtLoadedProtStr+'0')
parseProtGroupBoxStatsFrameLayout.addWidget(parseProtLoadedProtLabel)

#####
parseProtEolErrorStr   = parseProtTextTab + 'EOL Error(s): '
parseProtEolErrorLabel = QLabel(parseProtEolErrorStr+'0')
# parseProtEolErrorLabel.setAlignment(Qt.AlignCenter)
parseProtGroupBoxStatsFrameLayout.addWidget(parseProtEolErrorLabel)
#####
parseProtAbbortCritStr   = parseProtTextTab +  'EOL Abbort Criterion(s): '
parseProtAbbortCritLabel = QLabel(parseProtAbbortCritStr+'0')
parseProtGroupBoxStatsFrameLayout.addWidget(parseProtAbbortCritLabel)
#####
parseProtMeasLimitsExcStr   = parseProtTextTab + 'EOL Meas. Limits Exceeded: '
parseProtMeasLimitsExcLabel = QLabel(parseProtMeasLimitsExcStr+'0')
parseProtGroupBoxStatsFrameLayout.addWidget(parseProtMeasLimitsExcLabel)

####
parseProtHLine = QFrame()
parseProtHLine.setFixedHeight(H_LINE_HEIGHT)
parseProtHLine.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
parseProtHLine.setStyleSheet(lineStyle)
parseProtGroupBoxStatsFrameLayout.addWidget(parseProtHLine)

#####
parseProtParsedLoadedProtStr   = 'Parsed / Loaded Protocols: '
parseProtParsedLoadedProtLabel = QLabel(parseProtParsedLoadedProtStr+'0')
parseProtGroupBoxStatsFrameLayout.addWidget(parseProtParsedLoadedProtLabel)
#####
parseProtPtu2FilesStr   = parseProtTextTab + 'PTU-2 Files: '
parseProtPtu2FilesLabel = QLabel(parseProtPtu2FilesStr +'0')
parseProtGroupBoxStatsFrameLayout.addWidget(parseProtPtu2FilesLabel)
#####
parseProtTxAntDiagFilesStr   = parseProtTextTab + 'Tx-Antenna Diag. Files: '
parseProtTxAntDiagFilesLabel = QLabel(parseProtTxAntDiagFilesStr +'0')
parseProtGroupBoxStatsFrameLayout.addWidget(parseProtTxAntDiagFilesLabel)

####
parseProtHLine = QFrame()
parseProtHLine.setFixedHeight(H_LINE_HEIGHT)
parseProtHLine.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
parseProtHLine.setStyleSheet(lineStyle)
parseProtGroupBoxStatsFrameLayout.addWidget(parseProtHLine)

#####
parseProtSepParPtu2FilesStr   = 'Separately Parsed Files: '
parseProtSepParPtu2FilesLabel = QLabel(parseProtSepParPtu2FilesStr)
parseProtGroupBoxStatsFrameLayout.addWidget(parseProtSepParPtu2FilesLabel)
#####

#####
parseProtSepParPtu2FilesStr   = parseProtTextTab+'PTU-2 Files: '
parseProtSepParPtu2FilesLabel = QLabel(parseProtSepParPtu2FilesStr+'0')
parseProtGroupBoxStatsFrameLayout.addWidget(parseProtSepParPtu2FilesLabel)
#####
parseProtSepParTxAntDiagFilesStr   = parseProtTextTab+'Tx-Antenna Diag. Files: '
parseProtSepParTxAntDiagFilesLabel = QLabel(parseProtSepParTxAntDiagFilesStr +'0')
parseProtGroupBoxStatsFrameLayout.addWidget(parseProtSepParTxAntDiagFilesLabel)

### Parse Protocols Data

parseProtProtDataGroupBox = QGroupBox('Protocols Data')
parseProtProtDataGroupBox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
parseProtProtDataGroupBox.setFixedWidth(210)
parseProtProtDataGroupBoxLayout = QVBoxLayout()
parseProtProtDataGroupBoxLayout.setSpacing(V_LAYOUT_SPACING)
parseProtProtDataGroupBoxLayout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
parseProtProtDataGroupBox.setLayout(parseProtProtDataGroupBoxLayout)
parseProtLayout.addWidget(parseProtProtDataGroupBox, 3, 1, 1, 1, alignment=Qt.AlignTop )

#### Parse Protocols GroupBox ProtData Frame
# parseProtProtDataFrame=QFrame()
# parseProtProtDataFrame.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
# parseProtProtDataFrameLayout = QVBoxLayout()
# parseProtProtDataFrameLayout.setSpacing(V_LAYOUT_SPACING)
# parseProtProtDataFrameLayout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
#
# parseProtProtDataFrame.setLayout(parseProtProtDataFrameLayout)
# parseProtProtDataGroupBoxLayout.addWidget(parseProtProtDataFrame)

### Parse Protocols Table Tab Widget
parseProtProtDataTabWidget = QTabWidget()

parseProtProtDataGroupBoxLayout.addWidget(parseProtProtDataTabWidget, alignment=Qt.AlignTop)
parseProtProtDataTabWidget.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)

parseProtProtDataBurnInTab    = QFrame()
parseProtProtDataBurnInLayout = QVBoxLayout()
parseProtProtDataBurnInLayout.setSpacing(V_LAYOUT_SPACING)
parseProtProtDataBurnInLayout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
parseProtProtDataBurnInTab.setLayout(parseProtProtDataBurnInLayout)
parseProtProtDataTabWidget.insertTab(0, parseProtProtDataBurnInTab, 'Burn-In')

parseProtProtDataCalTab    = QFrame()
parseProtProtDataCalLayout = QVBoxLayout()
parseProtProtDataCalLayout.setSpacing(V_LAYOUT_SPACING)
parseProtProtDataCalLayout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
parseProtProtDataCalTab.setLayout(parseProtProtDataCalLayout)
parseProtProtDataTabWidget.insertTab(1, parseProtProtDataCalTab, 'Calibration')

#####
#####
parseProtProtDataBurnInInclCheckBox = QCheckBox('Include for Parsing')
parseProtProtDataBurnInLayout.addWidget(parseProtProtDataBurnInInclCheckBox)

#####
parseProtProtDataBurnInHLine = QFrame()
parseProtProtDataBurnInHLine.setFixedHeight(H_LINE_HEIGHT)
parseProtProtDataBurnInHLine.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
parseProtProtDataBurnInHLine.setStyleSheet(lineStyle)
parseProtProtDataBurnInLayout.addWidget(parseProtProtDataBurnInHLine)

#####
parseProtProtDataInFileBurnInPushBtn = QPushButton('Load Input Limits File')
parseProtProtDataInFileBurnInPushBtn.setFixedSize(PUSH_BTN_H_SIZE, PUSH_BTN_V_SIZE)
parseProtProtDataInFileBurnInPushBtn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
parseProtProtDataBurnInLayout.addWidget(parseProtProtDataInFileBurnInPushBtn)

#####
parseProtProtDataInFileBurnInFDialog = QFileDialog()
parseProtProtDataInFileBurnInFDialog.setFileMode(QFileDialog.ExistingFile)
parseProtProtDataInFileBurnInFDialog.setNameFilter("BurnIn Limits Input (*.yaml)")
parseProtProtDataInFileBurnInFDialog.setFilter(QDir.Filter.Files)

parseProtProtDataInFileBurnInLabel = QLabel('No file set.')
parseProtProtDataInFileBurnInLabel.setToolTip('No file set.')
parseProtProtDataBurnInLayout.addWidget(parseProtProtDataInFileBurnInLabel)

#####
parseProtProtDataBurnInExtCheckBox = QCheckBox('Extend Input Limits File')
parseProtProtDataBurnInLayout.addWidget(parseProtProtDataBurnInExtCheckBox)
# parseProtProtDataBurnInCheckBox.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)

#####
parseProtProtDataBurnInHLine = QFrame()
parseProtProtDataBurnInHLine.setFixedHeight(H_LINE_HEIGHT)
parseProtProtDataBurnInHLine.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
parseProtProtDataBurnInHLine.setStyleSheet(lineStyle)
parseProtProtDataBurnInLayout.addWidget(parseProtProtDataBurnInHLine)

#####
parseProtProtDataLimGroupsBurnInPushBtn = QPushButton('Load Limits Groups File')
parseProtProtDataLimGroupsBurnInPushBtn.setFixedSize(PUSH_BTN_H_SIZE, PUSH_BTN_V_SIZE)
parseProtProtDataLimGroupsBurnInPushBtn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
parseProtProtDataBurnInLayout.addWidget(parseProtProtDataLimGroupsBurnInPushBtn)

#####
parseProtProtDataLimGroupsBurnInFDialog = QFileDialog()
parseProtProtDataLimGroupsBurnInFDialog.setFileMode(QFileDialog.ExistingFile)
parseProtProtDataLimGroupsBurnInFDialog.setNameFilter("BurnIn Limits Groups Input (*.yaml)")
parseProtProtDataLimGroupsBurnInFDialog.setFilter(QDir.Filter.Files)

parseProtProtDataLimGroupsBurnInLabel = QLabel('No file set.')
parseProtProtDataLimGroupsBurnInLabel.setToolTip('No file set.')
parseProtProtDataBurnInLayout.addWidget(parseProtProtDataLimGroupsBurnInLabel)

#####
parseProtProtDataBurnInLimGroupsExtCheckBox = QCheckBox('Extend Limits Groups File')
parseProtProtDataBurnInLayout.addWidget(parseProtProtDataBurnInLimGroupsExtCheckBox)
# parseProtProtDataBurnInCheckBox.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)

######
parseProtProtDataCalInclCheckBox = QCheckBox('Include for Parsing')
parseProtProtDataCalLayout.addWidget(parseProtProtDataCalInclCheckBox)

#####
parseProtProtDataCalHLine = QFrame()
parseProtProtDataCalHLine.setFixedHeight(H_LINE_HEIGHT)
parseProtProtDataCalHLine.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
parseProtProtDataCalHLine.setStyleSheet(lineStyle)
parseProtProtDataCalLayout.addWidget(parseProtProtDataCalHLine)

#####
parseProtProtDataInFileCalPushBtn = QPushButton('Load Input Limits File')
parseProtProtDataInFileCalPushBtn.setFixedSize(PUSH_BTN_H_SIZE, PUSH_BTN_V_SIZE)
parseProtProtDataInFileCalPushBtn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
parseProtProtDataCalLayout.addWidget(parseProtProtDataInFileCalPushBtn)

#####
parseProtProtDataInFileCalFDialog = QFileDialog()
parseProtProtDataInFileCalFDialog.setFileMode(QFileDialog.ExistingFile)
parseProtProtDataInFileCalFDialog.setNameFilter("Limits Input (*.yaml)")
parseProtProtDataInFileCalFDialog.setFilter(QDir.Filter.Files)

parseProtProtDataInFileCalLabel = QLabel('No file set.')
parseProtProtDataInFileCalLabel.setToolTip('No file set.')
parseProtProtDataCalLayout.addWidget(parseProtProtDataInFileCalLabel)

parseProtProtDataCalExtCheckBox = QCheckBox('Extend Input Limits File')
parseProtProtDataCalLayout.addWidget(parseProtProtDataCalExtCheckBox)

#####
parseProtProtDataCalHLine = QFrame()
parseProtProtDataCalHLine.setFixedHeight(H_LINE_HEIGHT)
parseProtProtDataCalHLine.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
parseProtProtDataCalHLine.setStyleSheet(lineStyle)
parseProtProtDataCalLayout.addWidget(parseProtProtDataCalHLine)

#####
parseProtProtDataLimGroupsCalPushBtn = QPushButton('Load Limits Groups File')
parseProtProtDataLimGroupsCalPushBtn.setFixedSize(PUSH_BTN_H_SIZE, PUSH_BTN_V_SIZE)
parseProtProtDataLimGroupsCalPushBtn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
parseProtProtDataCalLayout.addWidget(parseProtProtDataLimGroupsCalPushBtn)

#####
parseProtProtDataLimGroupsCalFDialog = QFileDialog()
parseProtProtDataLimGroupsCalFDialog.setFileMode(QFileDialog.ExistingFile)
parseProtProtDataLimGroupsCalFDialog.setNameFilter("Calibration Limits Groups Input (*.yaml)")
parseProtProtDataLimGroupsCalFDialog.setFilter(QDir.Filter.Files)

parseProtProtDataLimGroupsCalLabel = QLabel('No file set.')
parseProtProtDataLimGroupsCalLabel.setToolTip('No file set.')
parseProtProtDataCalLayout.addWidget(parseProtProtDataLimGroupsCalLabel)

parseProtProtDataCalLimGroupsExtCheckBox = QCheckBox('Extend Limits Groups File')
parseProtProtDataCalLayout.addWidget(parseProtProtDataCalLimGroupsExtCheckBox)



### Parse Protocols Status

#### Parse Protocols ProgresBar
parseProtProgresFrame = QFrame()
parseProtProgresFrame.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
parseProtLayout.addWidget(parseProtProgresFrame, 0, 2, 2, 2, alignment=Qt.AlignTop)

parseProtProgresFrameLayout = QHBoxLayout()
parseProtProgresFrameLayout.setSpacing(H_LAYOUT_SPACING)
parseProtProgresFrameLayout.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
parseProtProgresFrame.setLayout(parseProtProgresFrameLayout)
#
parseProtProgresLabel = QLabel()
parseProtProgresLabel.setText('No protocols loaded.')
parseProtProgresLabel.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
parseProtProgresFrameLayout.addWidget(parseProtProgresLabel, stretch=3)

parseProtProgresBar = QProgressBar()
progBarFormatStr    = ''
# parseProtProgresBar.setFixedSize()
parseProtProgresBar.setFixedWidth(PROGRESS_BAR_H_SIZE)
parseProtProgresBar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

# parseProtProgresBar.setRange(0,1000)
# parseProtProgresBar.setValue(560)
# parseProtProgresBar.setFormat(progBarFormatStr)
parseProtProgresBar.setTextVisible(True)


parseProtProgresFrameLayout.addWidget(parseProtProgresBar, stretch=1)

### Parse Protocols Table Tab Widget
parseProtTableTabWidget = QTabWidget()
parseProtTableTabWidget.setMinimumHeight(600)
# parseProtLoadDataTablesFrameLayout.addWidget(parseProtTableTabWidget)
parseProtLayout.addWidget(parseProtTableTabWidget, 2, 2, 2, 1, alignment=Qt.AlignTop)
# parseProtLayout.setAlignment()
parseProtTableTabWidget.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
parseProtSelProtTab = QWidget()
parseProtTableTabWidget.insertTab(0, parseProtSelProtTab, 'Selected Protocols')
parseProtSelProtLayout = QVBoxLayout()
parseProtSelProtTab.setLayout(parseProtSelProtLayout)

parseProtAccProtTab = QWidget()
parseProtAccProtTab.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
parseProtTableTabWidget.insertTab(1, parseProtAccProtTab, 'Accepted Protocols')
parseProtAccProtLayout = QVBoxLayout()
parseProtAccProtTab.setLayout(parseProtAccProtLayout)

parseProtAddPtu2Tab = QWidget()
parseProtTableTabWidget.insertTab(2, parseProtAddPtu2Tab, 'Additional PTU-2 Files')
parseProtAddPtu2Layout = QVBoxLayout()
parseProtAddPtu2Tab.setLayout(parseProtAddPtu2Layout)

parseProtAddTxAntDiagTab = QWidget()
parseProtTableTabWidget.insertTab(3, parseProtAddTxAntDiagTab, 'Additional Tx-Ant. Diag. Files')
parseProtAddTxAntDiagLayout = QVBoxLayout()
parseProtAddTxAntDiagTab.setLayout(parseProtAddTxAntDiagLayout)

# parseProtSelCertProtTab=QWidget()
# parseProtTableTabWidget.insertTab(4,parseProtSelCertProtTab,'Selected Certificate Protocols')
# parseProtSelCertProtLayout=QVBoxLayout()
# parseProtSelCertProtTab.setLayout(parseProtSelCertProtLayout)

parseProtStatsTab = QWidget()
parseProtTableTabWidget.insertTab(4, parseProtStatsTab, 'Statistics Protocols')
parseProtStatsLayout = QVBoxLayout()
parseProtStatsTab.setLayout(parseProtStatsLayout)

#### Parse Protocols Selected Protocols Table Widget
parseProtSelProtTable = QTableWidget(PARSE_PROT_TABLE_ROWS, 4)
# parseProtSelProtTable.setMinimumHeight(650)
parseProtSelProtTable.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
parseProtSelProtTable.setHorizontalHeaderLabels(['Protocol','Imported as (Type)', 'PTU2 File Path', 'Tx-Ant Diagram File Path'])
# parseProtSelProtTable.setEditTriggers(QTableWidget.DoubleClicked)
parseProtSelProtLayout.addWidget(parseProtSelProtTable, stretch=1)
parseProtSelProtTableHeader = parseProtSelProtTable.horizontalHeader()
parseProtSelProtTable.setColumnWidth(1,100)
parseProtSelProtTableHeader.setSectionResizeMode(QHeaderView.Stretch)


#### Parse Protocols Accepted Protocols Table Widget
parseProtAccProtTable = QTableWidget(PARSE_PROT_TABLE_ROWS, 4)
parseProtAccProtTable.setHorizontalHeaderLabels(['Protocol', 'Imported as (Type)', 'PTU2 File Path', 'Tx-Ant Diagram File Path'])
parseProtAccProtTable.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
# parseProtSelProtTable.setEditTriggers(QTableWidget.DoubleClicked)
parseProtAccProtLayout.addWidget(parseProtAccProtTable, stretch=2)
parseProtAccProtTableHeader = parseProtAccProtTable.horizontalHeader()
parseProtAccProtTable.setColumnWidth(1, 100)
parseProtAccProtTableHeader.setSectionResizeMode(QHeaderView.Stretch)

#### Parse Protocols PTU2 Files Table Widget
parseProtAddPtu2ParsedTable = QTableWidget(PARSE_PROT_TABLE_ROWS,1)
parseProtAddPtu2ParsedTable.setHorizontalHeaderLabels(['Parsed PTU-2 Files'])
parseProtAddPtu2ParsedTable.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred)
# parseProtSelProtTable.setEditTriggers(QTableWidget.DoubleClicked)
parseProtAddPtu2Layout.addWidget(parseProtAddPtu2ParsedTable, stretch=5)
parseProtAddPtu2ParsedTableHeader = parseProtAddPtu2ParsedTable.horizontalHeader()
parseProtAddPtu2ParsedTableHeader.setSectionResizeMode(QHeaderView.Stretch)

#### Parse Protocols Failed PTU2 Files Table Widget
parseProtAddPtu2FailedTable = QTableWidget(PARSE_PROT_TABLE_ROWS, 1)
parseProtAddPtu2FailedTable.setHorizontalHeaderLabels(['Failed PTU-2 Files'])
parseProtAddPtu2FailedTable.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred)
# parseProtSelProtTable.setEditTriggers(QTableWidget.DoubleClicked)
parseProtAddPtu2Layout.addWidget(parseProtAddPtu2FailedTable, stretch=2)
parseProtAddPtu2FailedTableHeader = parseProtAddPtu2FailedTable.horizontalHeader()
parseProtAddPtu2FailedTableHeader.setSectionResizeMode(QHeaderView.Stretch)


#### Parse Protocols Tx Ant Diag Files Table Widget
parseProtAddTxAntDiagParsedTable = QTableWidget(PARSE_PROT_TABLE_ROWS, 1)
parseProtAddTxAntDiagParsedTable.setHorizontalHeaderLabels(['Parsed Tx-Ant. Diag. Files'])
parseProtAddTxAntDiagParsedTable.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
# parseProtSelProtTable.setEditTriggers(QTableWidget.DoubleClicked)
parseProtAddTxAntDiagLayout.addWidget(parseProtAddTxAntDiagParsedTable, stretch=5)
parseProtAddTxAntDiagTableHeader = parseProtAddTxAntDiagParsedTable.horizontalHeader()
parseProtAddTxAntDiagTableHeader.setSectionResizeMode(QHeaderView.Stretch)

#### Parse Protocols Failed Tx Ant Diag Files Table Widget
parseProtAddTxAntDiagFailedTable = QTableWidget(PARSE_PROT_TABLE_ROWS, 1)
parseProtAddTxAntDiagFailedTable.setHorizontalHeaderLabels(['Failed Tx-Ant. Diag. Files'])
parseProtAddTxAntDiagFailedTable.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
# parseProtSelProtTable.setEditTriggers(QTableWidget.DoubleClicked)
parseProtAddTxAntDiagLayout.addWidget(parseProtAddTxAntDiagFailedTable, stretch=2)
parseProtAddTxAntDiagFailedTableHeader = parseProtAddTxAntDiagFailedTable.horizontalHeader()
parseProtAddTxAntDiagFailedTableHeader.setSectionResizeMode(QHeaderView.Stretch)


#### Certificates - Parsed Protocols Table Widget
parseProtStatsParsedTable = QTableWidget(PARSE_PROT_TABLE_ROWS, 3)
parseProtStatsParsedTable.setHorizontalHeaderLabels(['Accepted Protocols', 'Imported as (Type)', 'Parsed as (Type)'])
parseProtStatsParsedTable.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
# parseProtSelProtTable.setEditTriggers(QTableWidget.DoubleClicked)
parseProtStatsLayout.addWidget(parseProtStatsParsedTable, stretch=5)
parseProtStatsParsedTableHeader = parseProtStatsParsedTable.horizontalHeader()
parseProtStatsParsedTableHeader.setSectionResizeMode(QHeaderView.Stretch)
parseProtStatsParsedTable.resizeColumnToContents(0)


#### Certificates - Failed Protocols Table Widget
parseProtStatsFailedTable = QTableWidget(PARSE_PROT_TABLE_ROWS, 3)
parseProtStatsFailedTable.setHorizontalHeaderLabels(['Failed Protocols', 'Imported as (Type)', 'Parsed as (Type)'])
parseProtStatsFailedTable.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
# parseProtSelProtTable.setEditTriggers(QTableWidget.DoubleClicked)
parseProtStatsLayout.addWidget(parseProtStatsFailedTable, stretch=2)
parseProtStatsFailedTableHeader = parseProtStatsFailedTable.horizontalHeader()
parseProtStatsFailedTableHeader.setSectionResizeMode(QHeaderView.Stretch)
parseProtStatsFailedTable.resizeColumnsToContents()

#### Parse Protocols Certificates Selected Protocols Table Widget
# parseProtSelCertProtTable=QTableWidget(PARSE_PROT_TABLE_ROWS,2)
# parseProtSelCertProtTable.setHorizontalHeaderLabels(['Protocol','Type'])
# parseProtSelCertProtTable.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding)
# # parseProtSelProtTable.setEditTriggers(QTableWidget.DoubleClicked)
# parseProtSelCertProtLayout.addWidget(parseProtSelCertProtTable, stretch=2)
# parseProtSelCertProtTableHeader=parseProtSelCertProtTable.horizontalHeader()
# parseProtSelCertProtTableHeader.setSectionResizeMode(QHeaderView.Stretch)
# parseProtSelCertProtTable.resizeColumnToContents(0)
#

# #### Certificates - Parsed Protocols Table Widget
# parseProtCertParsedTable=QTableWidget(PARSE_PROT_TABLE_ROWS, 2)
# parseProtCertParsedTable.setHorizontalHeaderLabels(['Accepted Protocols','Type'])
# parseProtCertParsedTable.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
# # parseProtSelProtTable.setEditTriggers(QTableWidget.DoubleClicked)
# parseProtAccCertLayout.addWidget(parseProtCertParsedTable, stretch=5)
# parseProtCertParsedTableHeader=parseProtCertParsedTable.horizontalHeader()
# parseProtCertParsedTableHeader.setSectionResizeMode(QHeaderView.Stretch)
# parseProtCertParsedTable.resizeColumnToContents(0)
#
#
# #### Certificates - Failed Protocols Table Widget
# parseProtCertFailedTable=QTableWidget(PARSE_PROT_TABLE_ROWS,2)
# parseProtCertFailedTable.setHorizontalHeaderLabels(['Failed Protocols','Type'])
# parseProtCertFailedTable.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding)
# # parseProtSelProtTable.setEditTriggers(QTableWidget.DoubleClicked)
# parseProtAccCertLayout.addWidget(parseProtCertFailedTable, stretch=2)
# parseProtCertFailedTableHeader=parseProtCertFailedTable.horizontalHeader()
# parseProtCertFailedTableHeader.setSectionResizeMode(QHeaderView.Stretch)
# parseProtCertFailedTable.resizeColumnsToContents()


##########
##########

## System Diagrams Tab
sysDiagTab    = QWidget()
sysDiagLayout = QGridLayout()
sysDiagLayout.setHorizontalSpacing(H_LAYOUT_SPACING)
sysDiagLayout.setVerticalSpacing(V_LAYOUT_SPACING)
sysDiagTab.setLayout(sysDiagLayout)
mainTabWidget.insertTab(1, sysDiagTab, 'System Diagrams')

### System Diagrams Start Script Button
sysDiagRowIdx = 0
sysDiagColIdx = 0

sysDiagStartPushBtn = QPushButton('Start')
sysDiagStartPushBtn.setFixedSize(PUSH_BTN_H_SIZE, PUSH_BTN_V_SIZE)
sysDiagStartPushBtn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
sysDiagLayout.addWidget(sysDiagStartPushBtn, sysDiagRowIdx, sysDiagColIdx)

### Input Data Setup GroupBox
sysDiagRowIdx += 1

sysDiagInputSetupGroupBox = QGroupBox('Input Setup')
sysDiagInputSetupGroupBox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.MinimumExpanding)
sysDiagInputSetupLayout = QGridLayout()

sysDiagInputSetupLayout.setColumnStretch(0, 1)
sysDiagInputSetupLayout.setColumnStretch(1, 1)
# sysDiagInputSetupLayout.setColumnStretch(2, 1)
sysDiagInputSetupLayout.setHorizontalSpacing(H_LAYOUT_SPACING)
sysDiagInputSetupLayout.setVerticalSpacing(V_LAYOUT_SPACING)
# sysDiagInputSetupLayout.setAlignment(Qt.AlignTop)

sysDiagInputSetupGroupBox.setLayout(sysDiagInputSetupLayout)
sysDiagLayout.addWidget(sysDiagInputSetupGroupBox, sysDiagRowIdx, sysDiagColIdx)

sysDiagInputSetupFrame = QFrame()
sysDiagInputSetupDiagFrameLayout = QGridLayout()
sysDiagInputSetupDiagFrameLayout.setColumnStretch(0, 1)
sysDiagInputSetupDiagFrameLayout.setColumnStretch(1, 1)
sysDiagInputSetupDiagFrameLayout.setColumnStretch(2, 1)
sysDiagInputSetupDiagFrameLayout.setHorizontalSpacing(H_LAYOUT_SPACING)
sysDiagInputSetupDiagFrameLayout.setVerticalSpacing(V_LAYOUT_SPACING)
sysDiagInputSetupDiagFrameLayout.setAlignment(Qt.AlignTop)

sysDiagInputSetupFrame.setLayout(sysDiagInputSetupDiagFrameLayout)
# sysDiagInputSetupFrame.setSizePolicy()

sysDiagInputSetupRowIdx = 0
sysDiagInputSetupColIdx = 0
sysDiagInputSetupLayout.addWidget(sysDiagInputSetupFrame, sysDiagInputSetupRowIdx, sysDiagInputSetupColIdx)
####
sysDiagInputSetupFrameRowIdx = 0
sysDiagInputSetupFrameColIdx = 0

sysDiagInputSetupAngleLabel = QLabel('Angle Setup')
sysDiagInputSetupDiagFrameLayout.addWidget(sysDiagInputSetupAngleLabel, sysDiagInputSetupFrameRowIdx, sysDiagInputSetupFrameColIdx)

#####
sysDiagInputSetupAngleGroup = QButtonGroup()


sysDiagInputSetupFrameRowIdx += 1
sysDiagInputSetupAngleSetupRadio1 = QRadioButton('Target Angle')
sysDiagInputSetupDiagFrameLayout.addWidget(sysDiagInputSetupAngleSetupRadio1, sysDiagInputSetupFrameRowIdx, sysDiagInputSetupFrameColIdx)
# sysDiagInputSetupAngleSetupRadio1.setChecked(True)
sysDiagInputSetupAngleGroup.addButton(sysDiagInputSetupAngleSetupRadio1, 0)
#####
sysDiagInputSetupFrameRowIdx += 1
sysDiagInputSetupAngleSetupRadio2 = QRadioButton('PTU Angle')
sysDiagInputSetupDiagFrameLayout.addWidget(sysDiagInputSetupAngleSetupRadio2, sysDiagInputSetupFrameRowIdx, sysDiagInputSetupFrameColIdx)
sysDiagInputSetupAngleGroup.addButton(sysDiagInputSetupAngleSetupRadio2, 1)

#####
sysDiagInputSetupFrameRowIdx  = 0
sysDiagInputSetupFrameColIdx += 1

sysDiagInputSetupVLine = QFrame()
sysDiagInputSetupVLine.setFixedWidth(V_LINE_WIDTH)
sysDiagInputSetupVLine.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.MinimumExpanding)
sysDiagInputSetupVLine.setStyleSheet(lineStyle)
sysDiagInputSetupDiagFrameLayout.addWidget(sysDiagInputSetupVLine, sysDiagInputSetupFrameRowIdx, sysDiagInputSetupFrameColIdx, 5, 1)

#####
sysDiagInputSetupFrameRowIdx  = 0
sysDiagInputSetupFrameColIdx += 1

sysDiagInputSetupSensorOrientGroup = QButtonGroup()

sysDiagInputSetupAngleLabel = QLabel('Sensor Orientation')
sysDiagInputSetupAngleLabel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
sysDiagInputSetupDiagFrameLayout.addWidget(sysDiagInputSetupAngleLabel, sysDiagInputSetupFrameRowIdx, sysDiagInputSetupFrameColIdx)

#####

sysDiagInputSetupFrameRowIdx += 1
sysDiagInputSetupSensorOrientRadio1 = QRadioButton('Normal')
sysDiagInputSetupSensorOrientRadio1.setChecked(True)
sysDiagInputSetupSensorOrientRadio1.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
sysDiagInputSetupSensorOrientGroup.addButton(sysDiagInputSetupSensorOrientRadio1)
sysDiagInputSetupSensorOrientGroup.setId(sysDiagInputSetupSensorOrientRadio1, 0)
sysDiagInputSetupDiagFrameLayout.addWidget(sysDiagInputSetupSensorOrientRadio1, sysDiagInputSetupFrameRowIdx, sysDiagInputSetupFrameColIdx)


####

sysDiagInputSetupFrameRowIdx += 1
sysDiagInputSetupSensorOrientRadio2 = QRadioButton('Upside-Down')
sysDiagInputSetupSensorOrientRadio2.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

sysDiagInputSetupDiagFrameLayout.addWidget(sysDiagInputSetupSensorOrientRadio2, sysDiagInputSetupFrameRowIdx, sysDiagInputSetupFrameColIdx)
sysDiagInputSetupSensorOrientGroup.addButton(sysDiagInputSetupSensorOrientRadio2)
sysDiagInputSetupSensorOrientGroup.setId(sysDiagInputSetupSensorOrientRadio2, 1)

#####
sysDiagInputSetupFrameRowIdx  = 0
sysDiagInputSetupFrameColIdx += 1

sysDiagInputSetupVLine = QFrame()
sysDiagInputSetupVLine.setFixedWidth(V_LINE_WIDTH)
sysDiagInputSetupVLine.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.MinimumExpanding)
sysDiagInputSetupVLine.setStyleSheet(lineStyle)
sysDiagInputSetupDiagFrameLayout.addWidget(sysDiagInputSetupVLine, sysDiagInputSetupFrameRowIdx, sysDiagInputSetupFrameColIdx, 5, 1)

####
sysDiagInputSetupFrameRowIdx  = 0
sysDiagInputSetupFrameColIdx += 1

sysDiagInputSetupChirpConfLabel = QLabel('Chirp Configuration')
sysDiagInputSetupDiagFrameLayout.addWidget(sysDiagInputSetupChirpConfLabel, sysDiagInputSetupFrameRowIdx, sysDiagInputSetupFrameColIdx)

sysDiagInputSetupChirpGroup = QButtonGroup()
sysDiagInputSetupChirpGroup.setExclusive(False)

#####
sysDiagInputSetupFrameRowIdx += 1

sysDiagInputSetupChirp0CheckBox = QCheckBox('Chirp 0')
sysDiagInputSetupChirpGroup.addButton(sysDiagInputSetupChirp0CheckBox, 0)
sysDiagInputSetupChirp0CheckBox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
# sysDiagInputSetupChirp0CheckBox.setChecked(True)

sysDiagInputSetupDiagFrameLayout.addWidget(sysDiagInputSetupChirp0CheckBox, sysDiagInputSetupFrameRowIdx, sysDiagInputSetupFrameColIdx)

#####
sysDiagInputSetupFrameRowIdx += 1

sysDiagInputSetupChirp1CheckBox = QCheckBox('Chirp 1')
sysDiagInputSetupChirpGroup.addButton(sysDiagInputSetupChirp1CheckBox, 1)

sysDiagInputSetupChirp1CheckBox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
sysDiagInputSetupChirp1CheckBox.setChecked(True)

sysDiagInputSetupDiagFrameLayout.addWidget(sysDiagInputSetupChirp1CheckBox, sysDiagInputSetupFrameRowIdx, sysDiagInputSetupFrameColIdx)


#####
sysDiagInputSetupFrameRowIdx += 1

sysDiagInputSetupChirp2CheckBox = QCheckBox('Chirp 2')
sysDiagInputSetupChirpGroup.addButton(sysDiagInputSetupChirp2CheckBox, 2)

sysDiagInputSetupChirp2CheckBox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
sysDiagInputSetupChirp2CheckBox.setChecked(True)

sysDiagInputSetupDiagFrameLayout.addWidget(sysDiagInputSetupChirp2CheckBox, sysDiagInputSetupFrameRowIdx, sysDiagInputSetupFrameColIdx)

#####
sysDiagInputSetupFrameRowIdx += 1

sysDiagInputSetupChirp3CheckBox = QCheckBox('Chirp 3')
sysDiagInputSetupChirpGroup.addButton(sysDiagInputSetupChirp3CheckBox, 3)

sysDiagInputSetupChirp3CheckBox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
sysDiagInputSetupChirp3CheckBox.setChecked(True)

sysDiagInputSetupDiagFrameLayout.addWidget(sysDiagInputSetupChirp3CheckBox, sysDiagInputSetupFrameRowIdx, sysDiagInputSetupFrameColIdx)

#### Input Data Diagram Config

sysDiagInputSetupFrameRowIdx += 1
sysDiagInputSetupFrameColIdx  = 0

sysDiagInputSetupDiagConfigFrame  = QFrame()
sysDiagInputSetupDiagConfigLayout = QGridLayout()
sysDiagInputSetupDiagConfigLayout.setAlignment(Qt.AlignTop)
sysDiagInputSetupDiagConfigFrame.setLayout(sysDiagInputSetupDiagConfigLayout)
sysDiagInputSetupDiagConfigFrame.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
sysDiagInputSetupLayout.addWidget(sysDiagInputSetupDiagConfigFrame, sysDiagInputSetupFrameRowIdx, sysDiagInputSetupFrameColIdx)

sysDiagInputSetupDiagConfigLayout.setColumnStretch(0, 1)
sysDiagInputSetupDiagConfigLayout.setColumnStretch(1, 1)
sysDiagInputSetupDiagConfigLayout.setColumnStretch(2, 1)
sysDiagInputSetupDiagConfigLayout.setHorizontalSpacing(H_LAYOUT_SPACING)
sysDiagInputSetupDiagConfigLayout.setVerticalSpacing(V_LAYOUT_SPACING)

sysDiagInputSetupDiagConfigRowIdx = 0
sysDiagInputSetupDiagConfigColIdx = 0

sysDiagInputSetupDiagConfigLabel = QLabel('Diagram Configuration')
sysDiagInputSetupDiagConfigLayout.addWidget(sysDiagInputSetupDiagConfigLabel, sysDiagInputSetupDiagConfigRowIdx, sysDiagInputSetupDiagConfigColIdx)

#####
sysDiagInputSetupDiagConfGroup = QButtonGroup()

sysDiagInputSetupDiagConfigRowIdx += 1

sysDiagInputSetupDiagConfigInputModeLabel = QLabel('Input Mode')
sysDiagInputSetupDiagConfigLayout.addWidget(sysDiagInputSetupDiagConfigInputModeLabel, sysDiagInputSetupDiagConfigRowIdx, sysDiagInputSetupDiagConfigColIdx)

#####
sysDiagInputSetupDiagConfigRowIdx += 1
sysDiagInputSetupDiagConfigInputModeRadio1 = QRadioButton('All')
sysDiagInputSetupDiagConfGroup.addButton(sysDiagInputSetupDiagConfigInputModeRadio1, 0)
sysDiagInputSetupDiagConfigLayout.addWidget(sysDiagInputSetupDiagConfigInputModeRadio1, sysDiagInputSetupDiagConfigRowIdx, sysDiagInputSetupDiagConfigColIdx)
#####
sysDiagInputSetupDiagConfigRowIdx += 1
sysDiagInputSetupDiagConfigInputModeRadio2 = QRadioButton('Desired range')
sysDiagInputSetupDiagConfGroup.addButton(sysDiagInputSetupDiagConfigInputModeRadio2, 1)
sysDiagInputSetupDiagConfigLayout.addWidget(sysDiagInputSetupDiagConfigInputModeRadio2, sysDiagInputSetupDiagConfigRowIdx, sysDiagInputSetupDiagConfigColIdx)
#####
sysDiagInputSetupDiagConfigRowIdx += 1
sysDiagInputSetupDiagConfigInputModeRadio3 = QRadioButton('Desired list')
sysDiagInputSetupDiagConfGroup.addButton(sysDiagInputSetupDiagConfigInputModeRadio3, 2)
sysDiagInputSetupDiagConfigLayout.addWidget(sysDiagInputSetupDiagConfigInputModeRadio3, sysDiagInputSetupDiagConfigRowIdx, sysDiagInputSetupDiagConfigColIdx)
#####

sysDiagInputSetupDiagConfigRowIdx += 1

sysDiagInputSetupDiagConfigDesRangeIntValidator = QIntValidator()
sysDiagInputSetupDiagConfigDesRangeIntValidator.setRange(0, 200)

sysDiagInputSetupDiagConfigDesRangeRegExp = QRegularExpression(r'^\d{0,3}(,\d{0,3})*$')
sysDiagInputSetupDiagConfigDesRangeRegExpValidator = QRegularExpressionValidator(sysDiagInputSetupDiagConfigDesRangeRegExp)

sysDiagInputSetupDiagConfigDesListLEdit = QLineEdit()
sysDiagInputSetupDiagConfigDesListLEdit.setValidator(sysDiagInputSetupDiagConfigDesRangeRegExpValidator)
# sysDiagInputSetupDiagConfigDesListLEdit.setMaxLength(3)
sysDiagInputSetupDiagConfigLayout.addWidget(sysDiagInputSetupDiagConfigDesListLEdit, sysDiagInputSetupDiagConfigRowIdx, sysDiagInputSetupDiagConfigColIdx)

#####


#####
sysDiagInputSetupDiagConfigRowIdx = 0
sysDiagInputSetupDiagConfigColIdx = 1

sysDiagInputSetupHLine = QFrame()
sysDiagInputSetupHLine.setFixedHeight(H_LINE_HEIGHT)
sysDiagInputSetupHLine.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
sysDiagInputSetupHLine.setStyleSheet(lineStyle)
sysDiagInputSetupDiagConfigLayout.addWidget(sysDiagInputSetupHLine, sysDiagInputSetupDiagConfigRowIdx, sysDiagInputSetupDiagConfigColIdx, 1, 2)

#####
sysDiagInputSetupDiagConfigRowIdx += 1

sysDiagInputSetupDiagConfigDesRangeLabel = QLabel('Desired Range')
sysDiagInputSetupDiagConfigLayout.addWidget(sysDiagInputSetupDiagConfigDesRangeLabel, sysDiagInputSetupDiagConfigRowIdx, sysDiagInputSetupDiagConfigColIdx)

sysDiagInputSetupDiagConfigDesRangeIntValidator = QIntValidator()
sysDiagInputSetupDiagConfigDesRangeIntValidator.setRange(0, 200)

#####
sysDiagInputSetupDiagConfigRowIdx += 1

sysDiagInputSetupDiagConfigDesRangeLowLabel = QLabel('Low:')
sysDiagInputSetupDiagConfigLayout.addWidget(sysDiagInputSetupDiagConfigDesRangeLowLabel, sysDiagInputSetupDiagConfigRowIdx, sysDiagInputSetupDiagConfigColIdx)

#####
sysDiagInputSetupDiagConfigRowIdx += 1

sysDiagInputSetupDiagConfigDesRangeLowLEdit = QLineEdit()
sysDiagInputSetupDiagConfigDesRangeLowLEdit.setValidator(sysDiagInputSetupDiagConfigDesRangeIntValidator)
sysDiagInputSetupDiagConfigDesRangeLowLEdit.setMaxLength(3)
sysDiagInputSetupDiagConfigLayout.addWidget(sysDiagInputSetupDiagConfigDesRangeLowLEdit, sysDiagInputSetupDiagConfigRowIdx, sysDiagInputSetupDiagConfigColIdx)

#####
sysDiagInputSetupDiagConfigRowIdx += 1

sysDiagInputSetupDiagConfigDesRangeHighLabel = QLabel('High:')
sysDiagInputSetupDiagConfigLayout.addWidget(sysDiagInputSetupDiagConfigDesRangeHighLabel, sysDiagInputSetupDiagConfigRowIdx, sysDiagInputSetupDiagConfigColIdx)

#####
sysDiagInputSetupDiagConfigRowIdx += 1

sysDiagInputSetupDiagConfigDesRangeHighLEdit = QLineEdit()
# s=sysDiagInputSetupDiagConfigDesRangeHighLEdit.size()
# sh=sysDiagInputSetupDiagConfigDesRangeHighLEdit.sizeHint()
sysDiagInputSetupDiagConfigDesRangeHighLEdit.setFixedSize(LEDIT_BTN_H_SIZE,LEDIT_BTN_V_SIZE)
sysDiagInputSetupDiagConfigDesRangeHighLEdit.setValidator(sysDiagInputSetupDiagConfigDesRangeIntValidator)
sysDiagInputSetupDiagConfigDesRangeHighLEdit.setMaxLength(3)
sysDiagInputSetupDiagConfigLayout.addWidget(sysDiagInputSetupDiagConfigDesRangeHighLEdit, sysDiagInputSetupDiagConfigRowIdx, sysDiagInputSetupDiagConfigColIdx)

#####
sysDiagInputSetupDiagConfigRowIdx  =1
sysDiagInputSetupDiagConfigColIdx +=1

sysDiagInputSetupDiagConfOddEvenGroup = QButtonGroup()

sysDiagInputSetupDiagConfigOddEvenLabel = QLabel('Odd / Even')
sysDiagInputSetupDiagConfigLayout.addWidget(sysDiagInputSetupDiagConfigOddEvenLabel, sysDiagInputSetupDiagConfigRowIdx, sysDiagInputSetupDiagConfigColIdx)

#####
sysDiagInputSetupDiagConfigRowIdx += 1
sysDiagInputSetupDiagConfigOddEvenRadio1 = QRadioButton('Both')
sysDiagInputSetupDiagConfOddEvenGroup.addButton(sysDiagInputSetupDiagConfigOddEvenRadio1, 0)
sysDiagInputSetupDiagConfigLayout.addWidget(sysDiagInputSetupDiagConfigOddEvenRadio1, sysDiagInputSetupDiagConfigRowIdx, sysDiagInputSetupDiagConfigColIdx)
#####
sysDiagInputSetupDiagConfigRowIdx += 1
sysDiagInputSetupDiagConfigOddEvenRadio2 = QRadioButton('Odd')
sysDiagInputSetupDiagConfOddEvenGroup.addButton(sysDiagInputSetupDiagConfigOddEvenRadio2, 1)
sysDiagInputSetupDiagConfigLayout.addWidget(sysDiagInputSetupDiagConfigOddEvenRadio2, sysDiagInputSetupDiagConfigRowIdx, sysDiagInputSetupDiagConfigColIdx)
#####
sysDiagInputSetupDiagConfigRowIdx += 1
sysDiagInputSetupDiagConfigOddEvenRadio3 = QRadioButton('Even')
sysDiagInputSetupDiagConfOddEvenGroup.addButton(sysDiagInputSetupDiagConfigOddEvenRadio3, 2)
sysDiagInputSetupDiagConfigLayout.addWidget(sysDiagInputSetupDiagConfigOddEvenRadio3, sysDiagInputSetupDiagConfigRowIdx, sysDiagInputSetupDiagConfigColIdx)

### Plot Setup GroupBox
sysDiagRowIdx = 1
sysDiagColIdx = 1

sysDiagPlotSetupGropBox = QGroupBox('Plot Setup')
sysDiagPlotSetupGropBox.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding)

sysDiagPlotSetupLayout = QHBoxLayout()
sysDiagPlotSetupLayout.setSpacing(H_LAYOUT_SPACING)

sysDiagPlotSetupGropBox.setLayout(sysDiagPlotSetupLayout)

sysDiagLayout.addWidget(sysDiagPlotSetupGropBox,sysDiagRowIdx,sysDiagColIdx)

#### Plot Setup Frame

sysDiagPlotSetupFrame = QFrame()
sysDiagPlotSetupFrame.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
sysDiagPlotSetupLayout.addWidget(sysDiagPlotSetupFrame,stretch=1)

sysDiagPlotSetupFrameLayout = QVBoxLayout()
sysDiagPlotSetupFrameLayout.setSpacing(V_LAYOUT_SPACING)
sysDiagPlotSetupFrameLayout.setAlignment(Qt.AlignTop)
sysDiagPlotSetupFrame.setLayout(sysDiagPlotSetupFrameLayout)


#####
sysDiagPlotSetupScriptModeGroup = QButtonGroup()

sysDiagPlotSetupScriptModeLabel = QLabel('Script mode')
sysDiagPlotSetupFrameLayout.addWidget(sysDiagPlotSetupScriptModeLabel)

sysDiagPlotSetupScriptModeRadio1 = QRadioButton('Presentation')
sysDiagPlotSetupScriptModeRadio1.setChecked(True)
sysDiagPlotSetupScriptModeGroup.addButton(sysDiagPlotSetupScriptModeRadio1,0)
sysDiagPlotSetupFrameLayout.addWidget(sysDiagPlotSetupScriptModeRadio1)

sysDiagPlotSetupScriptModeRadio2 = QRadioButton('Plot Window')
sysDiagPlotSetupScriptModeGroup.addButton(sysDiagPlotSetupScriptModeRadio2,1)
sysDiagPlotSetupFrameLayout.addWidget(sysDiagPlotSetupScriptModeRadio2)

#####
sysDiagPlotSetupHLine = QFrame()
sysDiagPlotSetupHLine.setFixedHeight(H_LINE_HEIGHT)
sysDiagPlotSetupHLine.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Fixed)
sysDiagPlotSetupHLine.setStyleSheet(lineStyle)
sysDiagPlotSetupFrameLayout.addWidget(sysDiagPlotSetupHLine)

#####
sysDiagPlotSetupImgGenGroup = QButtonGroup()

sysDiagPlotSetupImgGenLabel = QLabel('Image Generation mode')
sysDiagPlotSetupFrameLayout.addWidget(sysDiagPlotSetupImgGenLabel)

sysDiagPlotSetupImgGenRadio1 = QRadioButton('Rx-Channel')
sysDiagPlotSetupImgGenRadio1.setChecked(True)
sysDiagPlotSetupImgGenGroup.addButton(sysDiagPlotSetupImgGenRadio1,0)
sysDiagPlotSetupFrameLayout.addWidget(sysDiagPlotSetupImgGenRadio1)

sysDiagPlotSetupImgGenRadio2 = QRadioButton('Diagram Number')
sysDiagPlotSetupImgGenGroup.addButton(sysDiagPlotSetupImgGenRadio2,1)
sysDiagPlotSetupFrameLayout.addWidget(sysDiagPlotSetupImgGenRadio2)

#####
sysDiagPlotSetupHLine = QFrame()
sysDiagPlotSetupHLine.setFixedHeight(H_LINE_HEIGHT)
sysDiagPlotSetupHLine.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Fixed)
sysDiagPlotSetupHLine.setStyleSheet(lineStyle)
sysDiagPlotSetupFrameLayout.addWidget(sysDiagPlotSetupHLine)

#####
sysDiagPlotSetup3GraphLayoutImgCheckBox = QCheckBox('3-Graph Layout Images')
sysDiagPlotSetup3GraphLayoutImgCheckBox.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
sysDiagPlotSetup3GraphLayoutImgCheckBox.setChecked(True)

sysDiagPlotSetupFrameLayout.addWidget(sysDiagPlotSetup3GraphLayoutImgCheckBox)

#####
sysDiagPlotSetupHLine = QFrame()
sysDiagPlotSetupHLine.setFixedHeight(H_LINE_HEIGHT)
sysDiagPlotSetupHLine.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Fixed)
sysDiagPlotSetupHLine.setStyleSheet(lineStyle)
sysDiagPlotSetupFrameLayout.addWidget(sysDiagPlotSetupHLine)

#####
sysDiagPlotSetupImageDpiIntValidator = QIntValidator()
sysDiagPlotSetupImageDpiIntValidator.setRange(0,500)

sysDiagPlotSetupImageDpiLabel = QLabel('Image DPI:')
sysDiagPlotSetupFrameLayout.addWidget(sysDiagPlotSetupImageDpiLabel)

sysDiagPlotSetupImageDpiLEdit = QLineEdit()
sysDiagPlotSetupImageDpiLEdit.setValidator(sysDiagPlotSetupImageDpiIntValidator)
sysDiagPlotSetupImageDpiLEdit.setMaxLength(3)
sysDiagPlotSetupImageDpiLEdit.setFixedSize(LEDIT_BTN_H_SIZE,LEDIT_BTN_V_SIZE)
sysDiagPlotSetupImageDpiLEdit.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
sysDiagPlotSetupFrameLayout.addWidget(sysDiagPlotSetupImageDpiLEdit)

####
####
sysDiagPlotSetupVLine = QFrame()
sysDiagPlotSetupVLine.setFixedWidth(V_LINE_WIDTH)
sysDiagPlotSetupVLine.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.MinimumExpanding)
sysDiagPlotSetupVLine.setStyleSheet(lineStyle)
sysDiagPlotSetupLayout.addWidget(sysDiagPlotSetupVLine)

#### Plot Setup Scalling Frame
sysDiagPlotSetupScalingFrame = QFrame()

sysDiagPlotSetupScalingLayout = QVBoxLayout()
sysDiagPlotSetupScalingLayout.setSpacing(V_LAYOUT_SPACING)
sysDiagPlotSetupScalingLayout.setAlignment(Qt.AlignTop)
sysDiagPlotSetupScalingFrame.setLayout(sysDiagPlotSetupScalingLayout)

sysDiagPlotSetupLayout.addWidget(sysDiagPlotSetupScalingFrame,stretch=1)

#####
sysDiagPlotSetupScalingAutoCheckBox = QCheckBox('X-Scale Autoscale')
sysDiagPlotSetupScalingAutoCheckBox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

sysDiagPlotSetupScalingLayout.addWidget(sysDiagPlotSetupScalingAutoCheckBox)

#####
sysDiagPlotSetupScalingXScaleIntValidator = QIntValidator()
sysDiagPlotSetupScalingXScaleIntValidator.setRange(0,150)

#####
sysDiagPlotSetupScalingXScaleAzLabel = QLabel('X-Scale Azimuth:')
sysDiagPlotSetupScalingLayout.addWidget(sysDiagPlotSetupScalingXScaleAzLabel)

sysDiagPlotSetupScalingXScaleAzLEdit = QLineEdit()
sysDiagPlotSetupScalingXScaleAzLEdit.setValidator(sysDiagPlotSetupScalingXScaleIntValidator)
sysDiagPlotSetupScalingXScaleAzLEdit.setMaxLength(3)
sysDiagPlotSetupScalingXScaleAzLEdit.setFixedSize(LEDIT_BTN_H_SIZE,LEDIT_BTN_V_SIZE)
sysDiagPlotSetupScalingXScaleAzLEdit.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
sysDiagPlotSetupScalingLayout.addWidget(sysDiagPlotSetupScalingXScaleAzLEdit)

#####
sysDiagPlotSetupScalingXScaleElLabel = QLabel('X-Scale Elevation:')
sysDiagPlotSetupScalingLayout.addWidget(sysDiagPlotSetupScalingXScaleElLabel)

sysDiagPlotSetupScalingXScaleElLEdit = QLineEdit()
sysDiagPlotSetupScalingXScaleElLEdit.setValidator(sysDiagPlotSetupScalingXScaleIntValidator)
sysDiagPlotSetupScalingXScaleElLEdit.setMaxLength(3)
sysDiagPlotSetupScalingXScaleElLEdit.setFixedSize(LEDIT_BTN_H_SIZE,LEDIT_BTN_V_SIZE)
sysDiagPlotSetupScalingXScaleElLEdit.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
sysDiagPlotSetupScalingLayout.addWidget(sysDiagPlotSetupScalingXScaleElLEdit)

#####
sysDiagPlotSetupHLine = QFrame()
sysDiagPlotSetupHLine.setFixedHeight(H_LINE_HEIGHT)
sysDiagPlotSetupHLine.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Fixed)
sysDiagPlotSetupHLine.setStyleSheet(lineStyle)
sysDiagPlotSetupScalingLayout.addWidget(sysDiagPlotSetupHLine)

#####
sysDiagPlotSetupScalingYLimitsGroup = QButtonGroup()

sysDiagPlotSetupScalingYLimitsLabel = QLabel('Y-Limits Yield')
sysDiagPlotSetupScalingLayout.addWidget(sysDiagPlotSetupScalingYLimitsLabel)

sysDiagPlotSetupScalingYLimitRadio1 = QRadioButton('Per Antenna-Type')
sysDiagPlotSetupScalingYLimitRadio1.setChecked(True)
sysDiagPlotSetupScalingYLimitsGroup.addButton(sysDiagPlotSetupScalingYLimitRadio1,0)
sysDiagPlotSetupScalingLayout.addWidget(sysDiagPlotSetupScalingYLimitRadio1)

sysDiagPlotSetupScalingYLimitRadio2 = QRadioButton('All Antenna-Types')
sysDiagPlotSetupScalingYLimitsGroup.addButton(sysDiagPlotSetupScalingYLimitRadio2,1)
sysDiagPlotSetupScalingLayout.addWidget(sysDiagPlotSetupScalingYLimitRadio2)

#####
sysDiagPlotSetupHLine = QFrame()
sysDiagPlotSetupHLine.setFixedHeight(H_LINE_HEIGHT)
sysDiagPlotSetupHLine.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Fixed)
sysDiagPlotSetupHLine.setStyleSheet(lineStyle)
sysDiagPlotSetupScalingLayout.addWidget(sysDiagPlotSetupHLine)

#####
sysDiagPlotSetupScalingDiffPhDiffDoubleValidator = QDoubleValidator()
# sysDiagPlotSetupScalingXScaleIntValidator.setRange(0,150)

#####
sysDiagPlotSetupScalingDiffPhDiffLabel = QLabel('Diff. Phase Diff. Scaling Factor:')
sysDiagPlotSetupScalingLayout.addWidget(sysDiagPlotSetupScalingDiffPhDiffLabel)

sysDiagPlotSetupScalingDiffPhDiffLEdit = QLineEdit()
sysDiagPlotSetupScalingDiffPhDiffLEdit.setValidator(sysDiagPlotSetupScalingDiffPhDiffDoubleValidator)
# sysDiagPlotSetupScalingDiffPhDiffLEdit.setMaxLength(3)
sysDiagPlotSetupScalingDiffPhDiffLEdit.setFixedSize(LEDIT_BTN_H_SIZE,LEDIT_BTN_V_SIZE)
sysDiagPlotSetupScalingDiffPhDiffLEdit.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
sysDiagPlotSetupScalingLayout.addWidget(sysDiagPlotSetupScalingDiffPhDiffLEdit)

####
sysDiagPlotSetupVLine = QFrame()
sysDiagPlotSetupVLine.setFixedWidth(V_LINE_WIDTH)
sysDiagPlotSetupVLine.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.MinimumExpanding)
sysDiagPlotSetupVLine.setStyleSheet(lineStyle)
sysDiagPlotSetupLayout.addWidget(sysDiagPlotSetupVLine)

#### Graph Configuration Frame
sysDiagPlotSetupGraphConfFrame = QFrame()
sysDiagPlotSetupLayout.addWidget(sysDiagPlotSetupGraphConfFrame,stretch=1)
sysDiagPlotSetupGraphConfLayout = QVBoxLayout()
sysDiagPlotSetupGraphConfLayout.setAlignment(Qt.AlignTop)
sysDiagPlotSetupGraphConfLayout.setSpacing(V_LAYOUT_SPACING)

sysDiagPlotSetupGraphConfFrame.setLayout(sysDiagPlotSetupGraphConfLayout)

#####
sysDiagPlotSetupGraphConfLabel = QLabel('Graph Configuration')
sysDiagPlotSetupGraphConfLayout.addWidget(sysDiagPlotSetupGraphConfLabel)

graphConfig = {
    # Power level diagrams
    "level": 0,  # Power level [dB].
    "avgLevel": 0,  # Average power level of chirps [dB].

    "normLevel": 0,  # Normalised power level [dB].
    "avgNormLevel": 0,  # Average of normalised power levels of all chirps [dB].

    # Phase difference diagrams
    "phaseDiff": 0,  # Phase difference [°].
    "avgPhaseDiff": 0,  # Average of the corrected phase differences of all chirps[°].

    "diffPhaseDiff": 1,  # Difference between the corrected phase difference and the ideal one [°].
    "avgDiffPhaseDiff": 0,  # Average of the difference of the corrected phase difference and the ideal one of all chirps[°].

    "corrPhaseDiff": 0,  # Corrected phase difference by the correction factor [°].
}
sysDiagPlotSetupGraphConfigGroup = QButtonGroup()

# Mapping string for the graph titles
def graphStringMapping(graphTitle):
    graphString = ''
    if graphTitle == "level":
        graphString = "Level [dB]"
    elif graphTitle == "avgLevel":
        graphString = "Avg. Level [dB]"
    elif graphTitle == "normLevel":
        graphString = "Norm. Level [dB]"
    elif graphTitle == "avgNormLevel":
        graphString = "Avg. Norm. Level [dB]"
    elif graphTitle == "phaseDiff":
        graphString = "Phase Diff. [°]"
    elif graphTitle == "avgPhaseDiff":
        graphString = "Avg. Phase Diff. [°]"
    elif graphTitle == "diffPhaseDiff":
        graphString = "Diff. of Phase Diff. [°]"
    elif graphTitle == "avgDiffPhaseDiff":
        graphString = "Avg. Diff. of Phase Diff. [°]"
    elif graphTitle == "corrPhaseDiff":
        graphString = "Corr. Phase Diff. [°]"
    return graphString

# sysDiagPlotSetupGraphConfList=["level","avgLevel","normLevel","avgNormLevel","phaseDiff","avgPhaseDiff","diffPhaseDiff","avgDiffPhaseDiff","corrPhaseDiff"]
def boolMapping(value):
    if isinstance(value,bool):
        if value == True:
            return 1
        else:
            return 0
    elif isinstance(value,int):
        if value == 1:
            return True
        elif value == 0:
            return False
        else:
            raise ValueError('Input must be: int 1 or 0.')
    else:
        raise TypeError('Input must be: bool or int.')


sysDiagPlotSetupGraphConfGroup = QButtonGroup()
sysDiagPlotSetupGraphConfGroup.setExclusive(False)

id = 0
for key, val in graphConfig.items():

    sysDiagPlotSetupGraphConfCheckBox = QCheckBox(graphStringMapping(key))
    # sysDiagPlotSetupGraphConfCheckBox.setChecked(boolMapping(val))
    sysDiagPlotSetupGraphConfLayout.addWidget(sysDiagPlotSetupGraphConfCheckBox)

    sysDiagPlotSetupGraphConfGroup.addButton(sysDiagPlotSetupGraphConfCheckBox, id)

    id += 1

# sysDiagPlotSetupGraphConfGroup.buttonClicked.connect(sysDiagPlotSetupGraphConfClick)

#####
sysDiagPlotSetupHLine = QFrame()
sysDiagPlotSetupHLine.setFixedHeight(H_LINE_HEIGHT)
sysDiagPlotSetupHLine.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Fixed)
sysDiagPlotSetupHLine.setStyleSheet(lineStyle)
sysDiagPlotSetupGraphConfLayout.addWidget(sysDiagPlotSetupHLine)

#####
sysDiagPlotSetupGraphConfIdealCurveCheckBox = QCheckBox('Diff. Ph. Diff. Ideal Curve')
sysDiagPlotSetupGraphConfLayout.addWidget(sysDiagPlotSetupGraphConfIdealCurveCheckBox)



### Plot Window Configuration GroupBox
plotWindowConfigGraphList = [ "level","avgLevel","normLevel","avgNormLevel","phaseDiff","avgPhaseDiff","diffPhaseDiff","avgDiffPhaseDiff","corrPhaseDiff"]
sysDiagColIdx += 1

sysDiagPlotWindowGroupBox = QGroupBox('Plot Window Configuration')
sysDiagPlotWindowGroupBox.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.MinimumExpanding)
sysDiagPlotWindowLayout = QHBoxLayout()

sysDiagPlotWindowLayout.setSpacing(H_LAYOUT_SPACING)

sysDiagPlotWindowLayout.setAlignment(Qt.AlignTop)

sysDiagPlotWindowGroupBox.setLayout(sysDiagPlotWindowLayout)

sysDiagLayout.addWidget(sysDiagPlotWindowGroupBox,sysDiagRowIdx,sysDiagColIdx)


sysDiagPlotWindowGeneralFrame  = QFrame()
sysDiagPlotWindowGeneralLayout = QVBoxLayout()
sysDiagPlotWindowGeneralLayout.setSpacing(H_LAYOUT_SPACING)
sysDiagPlotWindowGeneralLayout.setAlignment(Qt.AlignTop)
sysDiagPlotWindowGeneralFrame.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
sysDiagPlotWindowGeneralFrame.setLayout(sysDiagPlotWindowGeneralLayout)


sysDiagPlotWindowLayout.addWidget(sysDiagPlotWindowGeneralFrame,stretch=1)

#####
sysDiagPlotWindowInputModeLabel = QLabel()
sysDiagPlotWindowInputModeLabel.setText('Input Mode')
sysDiagPlotWindowInputModeLabel.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
sysDiagPlotWindowGeneralLayout.addWidget(sysDiagPlotWindowInputModeLabel,stretch=1)
#####
sysDiagPlotWindowInputModeGroup = QButtonGroup()
#####

sysDiagPlotWindowInputModeRadio1 = QRadioButton('Data')
sysDiagPlotWindowGeneralLayout.addWidget(sysDiagPlotWindowInputModeRadio1)
# sysDiagInputSetupAngleSetupRadio1.setChecked(True)
sysDiagPlotWindowInputModeGroup.addButton(sysDiagPlotWindowInputModeRadio1,0)
#####
#####

sysDiagPlotWindowInputModeRadio2 = QRadioButton('String')
sysDiagPlotWindowGeneralLayout.addWidget(sysDiagPlotWindowInputModeRadio2)
# sysDiagInputSetupAngleSetupRadio1.setChecked(True)
sysDiagPlotWindowInputModeGroup.addButton(sysDiagPlotWindowInputModeRadio2,1)
#####

sysDiagPlotWindowInputModeLEdit = QLineEdit()
# sysDiagSlideConfGeneralSensorNumSlideLEdit.setValidator(sysDiagPlotSetupImageDpiIntValidator)
# sysDiagSlideConfGeneralSensorNumSlideLEdit.setMaxLength(3)
sysDiagPlotWindowInputModeLEdit.setFixedSize(LEDIT_BTN_H_SIZE,LEDIT_BTN_V_SIZE)
sysDiagPlotWindowInputModeLEdit.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
sysDiagPlotWindowGeneralLayout.addWidget(sysDiagPlotWindowInputModeLEdit)

sysDiagPlotWindowHLine = QFrame()
sysDiagPlotWindowHLine.setFixedHeight(H_LINE_HEIGHT)
sysDiagPlotWindowHLine.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Fixed)
sysDiagPlotWindowHLine.setStyleSheet(lineStyle)
sysDiagPlotWindowGeneralLayout.addWidget(sysDiagPlotWindowHLine)

#####
sysDiagPlotWindowGraphTypeLabel = QLabel()
sysDiagPlotWindowGraphTypeLabel.setText('Graph Type')
sysDiagPlotWindowGraphTypeLabel.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
sysDiagPlotWindowGeneralLayout.addWidget(sysDiagPlotWindowGraphTypeLabel,stretch=1)

#####
sysDiagPlotWindowGraphTypeComboBox = QComboBox()
sysDiagPlotWindowGeneralLayout.addWidget(sysDiagPlotWindowGraphTypeComboBox)
sysDiagPlotWindowGraphTypeComboBox.setEditText(plotWindowConfigGraphList[0])
sysDiagPlotWindowGraphTypeComboBox.addItems(plotWindowConfigGraphList)
sysDiagPlotWindowGraphTypeComboBox.setCurrentIndex(0)

#####

sysDiagPlotWindowAntTypLabel = QLabel()
sysDiagPlotWindowAntTypLabel.setText('Antenna Type')
sysDiagPlotWindowAntTypLabel.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
sysDiagPlotWindowGeneralLayout.addWidget(sysDiagPlotWindowAntTypLabel,stretch=1)
#####

sysDiagPlotWindowAntTypValidator = QIntValidator()
sysDiagPlotWindowAntTypValidator.setRange(0,999)
sysDiagPlotWindowAntTypLEdit = QLineEdit()
sysDiagPlotWindowAntTypLEdit.setValidator(sysDiagPlotWindowAntTypValidator)
sysDiagPlotWindowAntTypLEdit.setMaxLength(3)
sysDiagPlotWindowAntTypLEdit.setFixedSize(LEDIT_BTN_H_SIZE,LEDIT_BTN_V_SIZE)
sysDiagPlotWindowAntTypLEdit.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
sysDiagPlotWindowGeneralLayout.addWidget(sysDiagPlotWindowAntTypLEdit)


#####

sysDiagPlotWindowDiagNumLabel = QLabel()
sysDiagPlotWindowDiagNumLabel.setText('Diagram Number')
sysDiagPlotWindowDiagNumLabel.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
sysDiagPlotWindowGeneralLayout.addWidget(sysDiagPlotWindowDiagNumLabel,stretch=1)
#####

sysDiagPlotWindowDiagNumValidator = QIntValidator()
sysDiagPlotWindowDiagNumValidator.setRange(0,200)
sysDiagPlotWindowDiagNumLEdit = QLineEdit()
sysDiagPlotWindowDiagNumLEdit.setValidator(sysDiagPlotWindowDiagNumValidator)
sysDiagPlotWindowDiagNumLEdit.setMaxLength(3)
sysDiagPlotWindowDiagNumLEdit.setFixedSize(LEDIT_BTN_H_SIZE,LEDIT_BTN_V_SIZE)
sysDiagPlotWindowDiagNumLEdit.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
sysDiagPlotWindowGeneralLayout.addWidget(sysDiagPlotWindowDiagNumLEdit)

#####
sysDiagPlotWindowRxChLabel = QLabel()
sysDiagPlotWindowRxChLabel.setText('Rx-Channel')
sysDiagPlotWindowRxChLabel.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
sysDiagPlotWindowGeneralLayout.addWidget(sysDiagPlotWindowRxChLabel,stretch=1)
#####
sysDiagPlotWindowRxChValidator = QIntValidator()
sysDiagPlotWindowRxChValidator.setRange(0,11)
sysDiagPlotWindowRxChLEdit = QLineEdit()
sysDiagPlotWindowRxChLEdit.setValidator(sysDiagPlotSetupImageDpiIntValidator)
sysDiagPlotWindowRxChLEdit.setMaxLength(2)
sysDiagPlotWindowRxChLEdit.setFixedSize(LEDIT_BTN_H_SIZE,LEDIT_BTN_V_SIZE)
sysDiagPlotWindowRxChLEdit.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
sysDiagPlotWindowGeneralLayout.addWidget(sysDiagPlotWindowRxChLEdit)

#####
# sysDiagPlotWindowHLine=QFrame()
# sysDiagPlotWindowHLine.setFixedHeight(H_LINE_HEIGHT)
# sysDiagPlotWindowHLine.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Fixed)
# sysDiagPlotWindowHLine.setStyleSheet(lineStyle)
# sysDiagPlotWindowGeneralLayout.addWidget(sysDiagPlotWindowHLine)

# #####
# sysDiagPlotWindowAllGraphsCheckBox  =  QCheckBox('All Graphs Mode')
# sysDiagPlotWindowAllGraphsCheckBox.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
# sysDiagPlotWindowAllGraphsCheckBox.setChecked(False)
# sysDiagPlotWindowGeneralLayout.addWidget(sysDiagPlotWindowAllGraphsCheckBox,stretch = 0)
####
sysDiagPlotWindowVLine = QFrame()
sysDiagPlotWindowVLine.setFixedWidth(V_LINE_WIDTH)
sysDiagPlotWindowVLine.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.MinimumExpanding)
sysDiagPlotWindowVLine.setStyleSheet(lineStyle)
sysDiagPlotWindowLayout.addWidget(sysDiagPlotWindowVLine)

#####
sysDiagPlotWindowAllGraphsFrame  = QFrame()
sysDiagPlotWindowAllGraphsLayout = QVBoxLayout()
sysDiagPlotWindowAllGraphsLayout.setSpacing(V_LAYOUT_SPACING)
sysDiagPlotWindowAllGraphsLayout.setAlignment(Qt.AlignTop)
sysDiagPlotWindowAllGraphsFrame.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
sysDiagPlotWindowAllGraphsFrame.setLayout(sysDiagPlotWindowAllGraphsLayout)


sysDiagPlotWindowLayout.addWidget(sysDiagPlotWindowAllGraphsFrame,stretch=1)
#####
sysDiagPlotWindowAllGraphsCheckBox = QCheckBox('All Graphs Mode')
sysDiagPlotWindowAllGraphsCheckBox.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
sysDiagPlotWindowAllGraphsCheckBox.setChecked(False)
sysDiagPlotWindowAllGraphsLayout.addWidget(sysDiagPlotWindowAllGraphsCheckBox)

#####
sysDiagPlotWindowAllGraphsCheckBox1 = QCheckBox('Graph 1')
sysDiagPlotWindowAllGraphsCheckBox1.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
sysDiagPlotWindowAllGraphsCheckBox1.setChecked(True)
sysDiagPlotWindowAllGraphsLayout.addWidget(sysDiagPlotWindowAllGraphsCheckBox1)

#####
sysDiagPlotWindowAllGraphsComboBox1 = QComboBox()
# sysDiagPlotWindowGeneralAllSlidesComboBox1.setEditText(plotWindowConfigGraphList[0])
sysDiagPlotWindowAllGraphsComboBox1.addItems(plotWindowConfigGraphList)
sysDiagPlotWindowAllGraphsComboBox1.setCurrentIndex(0)
sysDiagPlotWindowAllGraphsLayout.addWidget(sysDiagPlotWindowAllGraphsComboBox1)


#####
sysDiagPlotWindowAllGraphsCheckBox2 = QCheckBox('Graph 2')
sysDiagPlotWindowAllGraphsCheckBox2.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
sysDiagPlotWindowAllGraphsCheckBox2.setChecked(True)
sysDiagPlotWindowAllGraphsLayout.addWidget(sysDiagPlotWindowAllGraphsCheckBox2)

#####
sysDiagPlotWindowAllGraphsComboBox2 = QComboBox()
# sysDiagPlotWindowGeneralAllSlidesComboBox2.setEditText(plotWindowConfigGraphList[8])
sysDiagPlotWindowAllGraphsComboBox2.addItems(plotWindowConfigGraphList)
sysDiagPlotWindowAllGraphsComboBox2.setCurrentIndex(8)
sysDiagPlotWindowAllGraphsLayout.addWidget(sysDiagPlotWindowAllGraphsComboBox2)

#####
sysDiagPlotWindowAllGraphsCheckBox3 = QCheckBox('Graph 3')
sysDiagPlotWindowAllGraphsCheckBox3.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
sysDiagPlotWindowAllGraphsCheckBox3.setChecked(True)
sysDiagPlotWindowAllGraphsLayout.addWidget(sysDiagPlotWindowAllGraphsCheckBox3)

#####
sysDiagPlotWindowAllGraphsComboBox3 = QComboBox()
# sysDiagPlotWindowGeneralAllSlidesComboBox3.setEditText(plotWindowConfigGraphList[6])
sysDiagPlotWindowAllGraphsComboBox3.addItems(plotWindowConfigGraphList)
sysDiagPlotWindowAllGraphsComboBox3.setCurrentIndex(6)
sysDiagPlotWindowAllGraphsLayout.addWidget(sysDiagPlotWindowAllGraphsComboBox3)




#### Slide Conf GroupBox
sysDiagRowIdx += 1
sysDiagColIdx  = 0

# sysDiagSlideConfPlotWindowFrame=QFrame()
# sysDiagSlideConfPlotWindowFrameLayout=QHBoxLayout()
# sysDiagSlideConfPlotWindowFrameLayout.setSpacing(H_LAYOUT_SPACING)
# sysDiagSlideConfPlotWindowFrameLayout.setAlignment(Qt.AlignTop)
# sysDiagSlideConfPlotWindowFrame.setLayout(sysDiagSlideConfPlotWindowFrameLayout)
#

### Slide Configuration GroupBox

sysDiagSlideConfGroupBox = QGroupBox('Slide Configuration')
sysDiagSlideConfGroupBox.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.MinimumExpanding)
sysDiagSlideConfLayout = QHBoxLayout()
sysDiagSlideConfLayout.setSpacing(H_LAYOUT_SPACING)
sysDiagSlideConfLayout.setAlignment(Qt.AlignTop)

sysDiagSlideConfGroupBox.setLayout(sysDiagSlideConfLayout)
sysDiagLayout.addWidget(sysDiagSlideConfGroupBox, sysDiagRowIdx, sysDiagColIdx,1,3)


#### Slide Configuration - Two-Graph Frame
sysDiagSlideConfTwoGraphFrame = QFrame()
sysDiagSlideConfLayout.addWidget(sysDiagSlideConfTwoGraphFrame)
sysDiagSlideConfTwoGraphLayout = QHBoxLayout()
sysDiagSlideConfTwoGraphLayout.setSpacing(H_LAYOUT_SPACING)
sysDiagSlideConfTwoGraphLayout.setAlignment(Qt.AlignTop)
sysDiagSlideConfTwoGraphFrame.setLayout(sysDiagSlideConfTwoGraphLayout)
sysDiagSlideConfTwoGraphFrame.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Preferred)



#####
sysDiagSlideConfTwoGraphGraphicFrame  = QFrame()
sysDiagSlideConfTwoGraphGraphicLayout = QGridLayout()

sysDiagSlideConfTwoGraphGraphicLayout.setVerticalSpacing(V_LAYOUT_SPACING)
sysDiagSlideConfTwoGraphGraphicLayout.setHorizontalSpacing(H_LAYOUT_SPACING)
sysDiagSlideConfTwoGraphGraphicLayout.setAlignment(Qt.AlignVCenter)
sysDiagSlideConfTwoGraphGraphicFrame.setLayout(sysDiagSlideConfTwoGraphGraphicLayout)
sysDiagSlideConfTwoGraphGraphicFrame.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Preferred)

#####
#####
sysDiagSlideConfTwoGraphLabel = QLabel('Two - Graph Layout')
sysDiagSlideConfTwoGraphLabel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
sysDiagSlideConfTwoGraphGraphicLayout.addWidget(sysDiagSlideConfTwoGraphLabel, 0, 0,1,2)


sysDiagSlideConfTwoGraphBigFrame = QFrame()
sysDiagSlideConfTwoGraphBigFrame.setObjectName('TwoGraphBig')
sysDiagSlideConfTwoGraphBigFrame.setStyleSheet(slideSymbolStyle)
sysDiagSlideConfTwoGraphBigFrame.setFixedSize(80,60)
sysDiagSlideConfTwoGraphBigFrame.setGraphicsEffect(shadowTwoGraphBig)
sysDiagSlideConfTwoGraphBigFrame.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
sysDiagSlideConfTwoGraphGraphicLayout.addWidget(sysDiagSlideConfTwoGraphBigFrame,1,0,1,1)

sysDiagSlideConfTwoGraphSmallFrame = QFrame()
sysDiagSlideConfTwoGraphSmallFrame.setObjectName('TwoGraphSmall')
sysDiagSlideConfTwoGraphSmallFrame.setStyleSheet(slideSymbolStyle)
sysDiagSlideConfTwoGraphSmallFrame.setFixedSize(60,45)
sysDiagSlideConfTwoGraphSmallFrame.setGraphicsEffect(shadowTwoGraphSmall)
sysDiagSlideConfTwoGraphSmallFrame.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
sysDiagSlideConfTwoGraphGraphicLayout.addWidget(sysDiagSlideConfTwoGraphSmallFrame,1,1,1,1)

sysDiagSlideConfTwoGraphLayout.addWidget(sysDiagSlideConfTwoGraphGraphicFrame,stretch=1)



##### Subframe1
sysDiagSlideConfTwoGraphSubFrame1 = QFrame()
sysDiagSlideConfTwoGraphSubFrame1Layout = QVBoxLayout()
sysDiagSlideConfTwoGraphSubFrame1Layout.setSpacing(V_LAYOUT_SPACING)
sysDiagSlideConfTwoGraphSubFrame1Layout.setAlignment(Qt.AlignTop)
sysDiagSlideConfTwoGraphSubFrame1.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Preferred)

sysDiagSlideConfTwoGraphSubFrame1.setLayout(sysDiagSlideConfTwoGraphSubFrame1Layout)
sysDiagSlideConfTwoGraphLayout.addWidget(sysDiagSlideConfTwoGraphSubFrame1)


#####
sysDiagSlideConfTwoGraphCheckBox1 = QCheckBox('Configuration 1')
sysDiagSlideConfTwoGraphCheckBox1.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
sysDiagSlideConfTwoGraphCheckBox1.setChecked(True)
sysDiagSlideConfTwoGraphSubFrame1Layout.addWidget(sysDiagSlideConfTwoGraphCheckBox1,stretch=1)


#####
sysDiagSlideConfTwoGraphComboBox11 = QComboBox()
sysDiagSlideConfTwoGraphSubFrame1Layout.addWidget(sysDiagSlideConfTwoGraphComboBox11,stretch=1)

sysDiagSlideConfTwoGraphComboBox11.setEditText(plotWindowConfigGraphList[2])

# def react(s):
#    print( sysDiagSlideConfTwoGraphComboBox11.itemText(s))
# sysDiagSlideConfTwoGraphComboBox11.currentIndexChanged.connect(react)

#####
sysDiagSlideConfTwoGraphComboBox12 = QComboBox()
sysDiagSlideConfTwoGraphSubFrame1Layout.addWidget(sysDiagSlideConfTwoGraphComboBox12,stretch=1)
sysDiagSlideConfTwoGraphComboBox12.setEditText(plotWindowConfigGraphList[2])


#####
sysDiagSlideConfTwoGraphCheckBox2 = QCheckBox('Configuration 2')
sysDiagSlideConfTwoGraphCheckBox2.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
sysDiagSlideConfTwoGraphCheckBox2.setChecked(True)
sysDiagSlideConfTwoGraphSubFrame1Layout.addWidget(sysDiagSlideConfTwoGraphCheckBox2,stretch=1)

#####

sysDiagSlideConfTwoGraphComboBox21 = QComboBox()
sysDiagSlideConfTwoGraphSubFrame1Layout.addWidget(sysDiagSlideConfTwoGraphComboBox21)
sysDiagSlideConfTwoGraphComboBox21.setEditText(plotWindowConfigGraphList[2])

######
sysDiagSlideConfTwoGraphComboBox22 = QComboBox()
sysDiagSlideConfTwoGraphSubFrame1Layout.addWidget(sysDiagSlideConfTwoGraphComboBox22,stretch=1)
sysDiagSlideConfTwoGraphComboBox22.setEditText(plotWindowConfigGraphList[2])


####
sysDiagSlideConfVLine = QFrame()
sysDiagSlideConfVLine.setFixedWidth(V_LINE_WIDTH)
sysDiagSlideConfVLine.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.MinimumExpanding)
sysDiagSlideConfVLine.setStyleSheet(lineStyle)
sysDiagSlideConfLayout.addWidget(sysDiagSlideConfVLine)

#### Slide Configuration - Four-Graph Frame
sysDiagSlideConfFourGraphFrame = QFrame()
sysDiagSlideConfLayout.addWidget(sysDiagSlideConfFourGraphFrame)

sysDiagSlideConfFourGraphLayout = QHBoxLayout()
sysDiagSlideConfFourGraphLayout.setSpacing(H_LAYOUT_SPACING)
sysDiagSlideConfFourGraphLayout.setAlignment(Qt.AlignTop)
sysDiagSlideConfFourGraphFrame.setLayout(sysDiagSlideConfFourGraphLayout)
sysDiagSlideConfFourGraphFrame.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Preferred)


#####
sysDiagSlideConfFourGraphGraphicFrame = QFrame()
sysDiagSlideConfFourGraphGraphicFrame.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Preferred)
sysDiagSlideConfFourGraphGraphicLayout = QGridLayout()
sysDiagSlideConfFourGraphGraphicLayout.setVerticalSpacing(V_LAYOUT_SPACING)
sysDiagSlideConfFourGraphGraphicLayout.setHorizontalSpacing(H_LAYOUT_SPACING)
sysDiagSlideConfFourGraphGraphicLayout.setAlignment(Qt.AlignVCenter)
sysDiagSlideConfFourGraphGraphicFrame.setLayout(sysDiagSlideConfFourGraphGraphicLayout)


#####
sysDiagSlideConfFourGraphLabel = QLabel('Four-Graph Layout')
sysDiagSlideConfFourGraphLayout.addWidget(sysDiagSlideConfFourGraphLabel)
sysDiagSlideConfFourGraphGraphicLayout.addWidget(sysDiagSlideConfFourGraphLabel, 0, 0,1,2)


sysDiagSlideConfFourGraphFrame00 = QFrame()
sysDiagSlideConfFourGraphFrame00.setStyleSheet(slideSymbolStyle)
sysDiagSlideConfFourGraphFrame00.setFixedSize(60,45)
sysDiagSlideConfFourGraphFrame00.setGraphicsEffect(shadowFourGraph00)
sysDiagSlideConfFourGraphFrame00.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
sysDiagSlideConfFourGraphGraphicLayout.addWidget(sysDiagSlideConfFourGraphFrame00, 1, 0,1,1)

sysDiagSlideConfFourGraphFrame01 = QFrame()
# sysDiagSlideConfThreeGraphFrame1.setObjectName('TwoGraphBig')
sysDiagSlideConfFourGraphFrame01.setStyleSheet(slideSymbolStyle)
sysDiagSlideConfFourGraphFrame01.setFixedSize(60,45)
sysDiagSlideConfFourGraphFrame01.setGraphicsEffect(shadowFourGraph01)
sysDiagSlideConfFourGraphFrame01.setSizePolicy(QSizePolicy.Maximum,QSizePolicy.Maximum)
sysDiagSlideConfFourGraphGraphicLayout.addWidget(sysDiagSlideConfFourGraphFrame01, 1, 1,1,1, alignment=Qt.AlignLeft)

sysDiagSlideConfFourGraphFrame10 = QFrame()
sysDiagSlideConfFourGraphFrame10.setStyleSheet(slideSymbolStyle)
sysDiagSlideConfFourGraphFrame10.setFixedSize(60,45)
sysDiagSlideConfFourGraphFrame10.setGraphicsEffect(shadowFourGraph10)
sysDiagSlideConfFourGraphFrame10.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
sysDiagSlideConfFourGraphGraphicLayout.addWidget(sysDiagSlideConfFourGraphFrame10, 2, 0,1,1)

sysDiagSlideConfFourGraphFrame11 = QFrame()
# sysDiagSlideConfThreeGraphFrame1.setObjectName('TwoGraphBig')
sysDiagSlideConfFourGraphFrame11.setStyleSheet(slideSymbolStyle)
sysDiagSlideConfFourGraphFrame11.setFixedSize(60,45)
sysDiagSlideConfFourGraphFrame11.setGraphicsEffect(shadowFourGraph11)
sysDiagSlideConfFourGraphFrame11.setSizePolicy(QSizePolicy.Maximum,QSizePolicy.Maximum)
sysDiagSlideConfFourGraphGraphicLayout.addWidget(sysDiagSlideConfFourGraphFrame11, 2, 1,1,1, alignment=Qt.AlignLeft)

sysDiagSlideConfFourGraphLayout.addWidget(sysDiagSlideConfFourGraphGraphicFrame)



##### Subframe1
sysDiagSlideConfFourGraphSubFrame1 = QFrame()
sysDiagSlideConfFourGraphSubFrame1Layout = QVBoxLayout()
sysDiagSlideConfFourGraphSubFrame1Layout.setSpacing(V_LAYOUT_SPACING)
sysDiagSlideConfFourGraphSubFrame1Layout.setAlignment(Qt.AlignTop)
sysDiagSlideConfFourGraphSubFrame1.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Preferred)

sysDiagSlideConfFourGraphSubFrame1.setLayout(sysDiagSlideConfFourGraphSubFrame1Layout)
sysDiagSlideConfFourGraphLayout.addWidget(sysDiagSlideConfFourGraphSubFrame1)



#####
sysDiagSlideConfFourGraphCheckBox1 = QCheckBox('Configuration 1')
sysDiagSlideConfFourGraphCheckBox1.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
sysDiagSlideConfFourGraphCheckBox1.setChecked(True)
sysDiagSlideConfFourGraphSubFrame1Layout.addWidget(sysDiagSlideConfFourGraphCheckBox1)
#####

sysDiagSlideConfFourGraphComboBox1 = QComboBox()
sysDiagSlideConfFourGraphSubFrame1Layout.addWidget(sysDiagSlideConfFourGraphComboBox1)
sysDiagSlideConfFourGraphComboBox1.setEditText(plotWindowConfigGraphList[2])
sysDiagSlideConfFourGraphComboBox1.addItems(plotWindowConfigGraphList)
sysDiagSlideConfFourGraphComboBox1.setCurrentIndex(0)

#####

sysDiagSlideConfFourGraphCheckBox2 = QCheckBox('Configuration 2')
sysDiagSlideConfFourGraphCheckBox2.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
sysDiagSlideConfFourGraphCheckBox2.setChecked(True)
sysDiagSlideConfFourGraphSubFrame1Layout.addWidget(sysDiagSlideConfFourGraphCheckBox2)
#####

sysDiagSlideConfFourGraphComboBox2 = QComboBox()
sysDiagSlideConfFourGraphSubFrame1Layout.addWidget(sysDiagSlideConfFourGraphComboBox2)
sysDiagSlideConfFourGraphComboBox2.setEditText(plotWindowConfigGraphList[2])
sysDiagSlideConfFourGraphComboBox2.addItems(plotWindowConfigGraphList)
sysDiagSlideConfFourGraphComboBox2.setCurrentIndex(0)

#####
sysDiagSlideConfFourGraphCheckBox3 = QCheckBox('Configuration 3')
sysDiagSlideConfFourGraphCheckBox3.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
sysDiagSlideConfFourGraphCheckBox3.setChecked(True)
sysDiagSlideConfFourGraphSubFrame1Layout.addWidget(sysDiagSlideConfFourGraphCheckBox3)
#####

sysDiagSlideConfFourGraphComboBox3 = QComboBox()
sysDiagSlideConfFourGraphSubFrame1Layout.addWidget(sysDiagSlideConfFourGraphComboBox3)
sysDiagSlideConfFourGraphComboBox3.setEditText(plotWindowConfigGraphList[2])
sysDiagSlideConfFourGraphComboBox3.addItems(plotWindowConfigGraphList)
sysDiagSlideConfFourGraphComboBox3.setCurrentIndex(0)


#####
#####


####
sysDiagSlideConfVLine = QFrame()
sysDiagSlideConfVLine.setFixedWidth(V_LINE_WIDTH)
sysDiagSlideConfVLine.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.MinimumExpanding)
sysDiagSlideConfVLine.setStyleSheet(lineStyle)
sysDiagSlideConfLayout.addWidget(sysDiagSlideConfVLine)

#### Slide Configuration - Three-Graph Frame
sysDiagSlideConfThreeGraphFrame = QFrame()
sysDiagSlideConfLayout.addWidget(sysDiagSlideConfThreeGraphFrame)
# sysDagSlideConfLayout.addWidget(sysDiagSlideConfThreeGraphFrame)
sysDiagSlideConfThreeGraphLayout = QHBoxLayout()
sysDiagSlideConfThreeGraphLayout.setSpacing(H_LAYOUT_SPACING)
sysDiagSlideConfThreeGraphLayout.setAlignment(Qt.AlignTop)
sysDiagSlideConfThreeGraphFrame.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Preferred)
sysDiagSlideConfThreeGraphFrame.setLayout(sysDiagSlideConfThreeGraphLayout)


#####
sysDiagSlideConfThreeGraphGraphicFrame = QFrame()
sysDiagSlideConfThreeGraphGraphicFrame.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Preferred)
sysDiagSlideConfThreeGraphGraphicLayout = QGridLayout()
sysDiagSlideConfThreeGraphGraphicLayout.setVerticalSpacing(V_LAYOUT_SPACING)
sysDiagSlideConfThreeGraphGraphicLayout.setHorizontalSpacing(H_LAYOUT_SPACING)

sysDiagSlideConfThreeGraphGraphicLayout.setAlignment(Qt.AlignVCenter)
sysDiagSlideConfThreeGraphGraphicFrame.setLayout(sysDiagSlideConfThreeGraphGraphicLayout)

#####
sysDiagSlideConfThreeGraphLabel = QLabel('Three-Graph Layout')
sysDiagSlideConfThreeGraphGraphicLayout.addWidget(sysDiagSlideConfThreeGraphLabel,0,0,1,3)


sysDiagSlideConfThreeGraphFrame1 = QFrame()
sysDiagSlideConfThreeGraphFrame1.setStyleSheet(slideSymbolStyle)
sysDiagSlideConfThreeGraphFrame1.setFixedSize(45,45)
sysDiagSlideConfThreeGraphFrame1.setGraphicsEffect(shadowThreeGraph1)
sysDiagSlideConfThreeGraphFrame1.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
sysDiagSlideConfThreeGraphGraphicLayout.addWidget(sysDiagSlideConfThreeGraphFrame1,1,0,1,1, alignment=Qt.AlignLeft|Qt.AlignTop)

sysDiagSlideConfThreeGraphFrame2 = QFrame()
sysDiagSlideConfThreeGraphFrame2.setStyleSheet(slideSymbolStyle)
sysDiagSlideConfThreeGraphFrame2.setFixedSize(45,45)
sysDiagSlideConfThreeGraphFrame2.setGraphicsEffect(shadowThreeGraph2)
sysDiagSlideConfThreeGraphFrame2.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
sysDiagSlideConfThreeGraphGraphicLayout.addWidget(sysDiagSlideConfThreeGraphFrame2,1,1,1,1, alignment=Qt.AlignLeft|Qt.AlignTop)

sysDiagSlideConfThreeGraphFrame3 = QFrame()
sysDiagSlideConfThreeGraphFrame3.setStyleSheet(slideSymbolStyle)
sysDiagSlideConfThreeGraphFrame3.setFixedSize(45,45)
sysDiagSlideConfThreeGraphFrame3.setGraphicsEffect(shadowThreeGraph3)
sysDiagSlideConfThreeGraphFrame3.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
sysDiagSlideConfThreeGraphGraphicLayout.addWidget(sysDiagSlideConfThreeGraphFrame3,1,2,1,1, alignment=Qt.AlignLeft|Qt.AlignTop)

sysDiagSlideConfThreeGraphLayout.addWidget(sysDiagSlideConfThreeGraphGraphicFrame)

##### Subframe1
sysDiagSlideConfThreeGraphSubFrame1 = QFrame()
sysDiagSlideConfThreeGraphSubFrame1Layout = QVBoxLayout()
sysDiagSlideConfThreeGraphSubFrame1Layout.setSpacing(V_LAYOUT_SPACING)
sysDiagSlideConfThreeGraphSubFrame1Layout.setAlignment(Qt.AlignTop)
sysDiagSlideConfThreeGraphSubFrame1.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Preferred)

sysDiagSlideConfThreeGraphSubFrame1.setLayout(sysDiagSlideConfThreeGraphSubFrame1Layout)
sysDiagSlideConfThreeGraphLayout.addWidget(sysDiagSlideConfThreeGraphSubFrame1)


#####
sysDiagSlideConfThreeGraphCheckBox1 = QCheckBox('Configuration 1')
sysDiagSlideConfThreeGraphCheckBox1.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
sysDiagSlideConfThreeGraphCheckBox1.setChecked(True)
sysDiagSlideConfThreeGraphSubFrame1Layout.addWidget(sysDiagSlideConfThreeGraphCheckBox1)
#####

sysDiagSlideConfThreeGraphComboBox1 = QComboBox()
sysDiagSlideConfThreeGraphSubFrame1Layout.addWidget(sysDiagSlideConfThreeGraphComboBox1)
sysDiagSlideConfThreeGraphComboBox1.setEditText(plotWindowConfigGraphList[2])
sysDiagSlideConfThreeGraphComboBox1.addItems(plotWindowConfigGraphList)
sysDiagSlideConfThreeGraphComboBox1.setCurrentIndex(0)

#####

sysDiagSlideConfThreeGraphCheckBox2 = QCheckBox('Configuration 2')
sysDiagSlideConfThreeGraphCheckBox2.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
sysDiagSlideConfThreeGraphCheckBox2.setChecked(True)
sysDiagSlideConfThreeGraphSubFrame1Layout.addWidget(sysDiagSlideConfThreeGraphCheckBox2)
#####

sysDiagSlideConfThreeGraphComboBox2 = QComboBox()
sysDiagSlideConfThreeGraphSubFrame1Layout.addWidget(sysDiagSlideConfThreeGraphComboBox2)
sysDiagSlideConfThreeGraphComboBox2.setEditText(plotWindowConfigGraphList[2])
sysDiagSlideConfThreeGraphComboBox2.addItems(plotWindowConfigGraphList)
sysDiagSlideConfThreeGraphComboBox2.setCurrentIndex(0)

#####
sysDiagSlideConfThreeGraphCheckBox3 = QCheckBox('Configuration 3')
sysDiagSlideConfThreeGraphCheckBox3.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
sysDiagSlideConfThreeGraphCheckBox3.setChecked(True)
sysDiagSlideConfThreeGraphSubFrame1Layout.addWidget(sysDiagSlideConfThreeGraphCheckBox3)
#####

sysDiagSlideConfThreeGraphComboBox3 = QComboBox()
sysDiagSlideConfThreeGraphSubFrame1Layout.addWidget(sysDiagSlideConfThreeGraphComboBox3)
sysDiagSlideConfThreeGraphComboBox3.setEditText(plotWindowConfigGraphList[2])
sysDiagSlideConfThreeGraphComboBox3.addItems(plotWindowConfigGraphList)
sysDiagSlideConfThreeGraphComboBox3.setCurrentIndex(0)

####
sysDiagSlideConfVLine = QFrame()
sysDiagSlideConfVLine.setFixedWidth(V_LINE_WIDTH)
sysDiagSlideConfVLine.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.MinimumExpanding)
sysDiagSlideConfVLine.setStyleSheet(lineStyle)
sysDiagSlideConfLayout.addWidget(sysDiagSlideConfVLine)

#### All Graph Slide
sysDiagSlideConfGeneralFrame = QFrame()
sysDiagSlideConfGeneralFrame.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Preferred)
sysDiagSlideConfGeneralLayout = QHBoxLayout()
sysDiagSlideConfGeneralLayout.setAlignment(Qt.AlignTop)
sysDiagSlideConfGeneralLayout.setSpacing(H_LAYOUT_SPACING)
sysDiagSlideConfGeneralFrame.setLayout(sysDiagSlideConfGeneralLayout)

sysDiagSlideConfLayout.addWidget(sysDiagSlideConfGeneralFrame,stretch=1)

##### All Graphs Subframe1
sysDiagSlideConfGeneralSubFrame1 = QFrame()
sysDiagSlideConfGeneralSubFrame1.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Preferred)
sysDiagSlideConfGeneralSubFrame1Layout = QVBoxLayout()
sysDiagSlideConfGeneralSubFrame1Layout.setAlignment(Qt.AlignTop)
sysDiagSlideConfGeneralSubFrame1Layout.setSpacing(V_LAYOUT_SPACING)
sysDiagSlideConfGeneralSubFrame1.setLayout(sysDiagSlideConfGeneralSubFrame1Layout)

sysDiagSlideConfGeneralLayout.addWidget(sysDiagSlideConfGeneralSubFrame1,stretch=1)


#####
sysDiagSlideConfGeneralAllGraphsSlideCheckBox = QCheckBox('All-Graphs Slide')
sysDiagSlideConfGeneralAllGraphsSlideCheckBox.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
sysDiagSlideConfGeneralAllGraphsSlideCheckBox.setChecked(True)
sysDiagSlideConfGeneralSubFrame1Layout.addWidget(sysDiagSlideConfGeneralAllGraphsSlideCheckBox, alignment=Qt.AlignTop)

#####
sysDiagSlideConfHLine = QFrame()
sysDiagSlideConfHLine.setFixedHeight(H_LINE_HEIGHT)
sysDiagSlideConfHLine.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Fixed)
sysDiagSlideConfHLine.setStyleSheet(lineStyle)
sysDiagSlideConfGeneralSubFrame1Layout.addWidget(sysDiagSlideConfHLine)

####
sysDiagSlideConfGeneralSensorSlideLabel = QLabel('Sensor Slide:')
sysDiagSlideConfGeneralSubFrame1Layout.addWidget(sysDiagSlideConfGeneralSensorSlideLabel)

#####
sysDiagSlideConfGeneralSensorNumSlideIntValidator = QIntValidator()
sysDiagSlideConfGeneralSensorNumSlideIntValidator.setRange(0,500)

#####
sysDiagSlideConfGeneralSensorNumSlideLabel = QLabel('Num. of Sensors:')
sysDiagSlideConfGeneralSubFrame1Layout.addWidget(sysDiagSlideConfGeneralSensorNumSlideLabel)

sysDiagSlideConfGeneralSensorNumSlideLEdit = QLineEdit()
sysDiagSlideConfGeneralSensorNumSlideLEdit.setValidator(sysDiagPlotSetupImageDpiIntValidator)
sysDiagSlideConfGeneralSensorNumSlideLEdit.setMaxLength(3)
sysDiagSlideConfGeneralSensorNumSlideLEdit.setFixedSize(LEDIT_BTN_H_SIZE,LEDIT_BTN_V_SIZE)
sysDiagSlideConfGeneralSensorNumSlideLEdit.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
sysDiagSlideConfGeneralSubFrame1Layout.addWidget(sysDiagSlideConfGeneralSensorNumSlideLEdit)


##### All Graphs Subframe2
sysDiagSlideConfGeneralSubFrame2 = QFrame()
sysDiagSlideConfGeneralSubFrame2.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Preferred)
sysDiagSlideConfGeneralSubFrame2Layout = QVBoxLayout()
sysDiagSlideConfGeneralSubFrame2Layout.setAlignment(Qt.AlignTop)
sysDiagSlideConfGeneralSubFrame2Layout.setSpacing(V_LAYOUT_SPACING)
sysDiagSlideConfGeneralSubFrame2.setLayout(sysDiagSlideConfGeneralSubFrame2Layout)

sysDiagSlideConfGeneralLayout.addWidget(sysDiagSlideConfGeneralSubFrame2,stretch=1)


#####
sysDiagSlideConfGeneralAllSlidesCheckBox1 = QCheckBox('Graph 1')
sysDiagSlideConfGeneralAllSlidesCheckBox1.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
sysDiagSlideConfGeneralAllSlidesCheckBox1.setChecked(True)
sysDiagSlideConfGeneralSubFrame2Layout.addWidget(sysDiagSlideConfGeneralAllSlidesCheckBox1)

#####
sysDiagSlideConfGeneralAllSlidesComboBox1 = QComboBox()
# sysDiagSlideConfGeneralAllSlidesComboBox1.setEditText(plotWindowConfigGraphList[0])
sysDiagSlideConfGeneralAllSlidesComboBox1.addItems(plotWindowConfigGraphList)
sysDiagSlideConfGeneralAllSlidesComboBox1.setCurrentIndex(0)
sysDiagSlideConfGeneralSubFrame2Layout.addWidget(sysDiagSlideConfGeneralAllSlidesComboBox1)


#####
sysDiagSlideConfGeneralAllSlidesCheckBox2 = QCheckBox('Graph 2')
sysDiagSlideConfGeneralAllSlidesCheckBox2.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
sysDiagSlideConfGeneralAllSlidesCheckBox2.setChecked(True)
sysDiagSlideConfGeneralSubFrame2Layout.addWidget(sysDiagSlideConfGeneralAllSlidesCheckBox2)

#####
sysDiagSlideConfGeneralAllSlidesComboBox2 = QComboBox()
# sysDiagSlideConfGeneralAllSlidesComboBox2.setEditText(plotWindowConfigGraphList[8])
sysDiagSlideConfGeneralAllSlidesComboBox2.addItems(plotWindowConfigGraphList)
sysDiagSlideConfGeneralAllSlidesComboBox2.setCurrentIndex(8)
sysDiagSlideConfGeneralSubFrame2Layout.addWidget(sysDiagSlideConfGeneralAllSlidesComboBox2)

#####
sysDiagSlideConfGeneralAllSlidesCheckBox3 = QCheckBox('Graph 3')
sysDiagSlideConfGeneralAllSlidesCheckBox3.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
sysDiagSlideConfGeneralAllSlidesCheckBox3.setChecked(True)
sysDiagSlideConfGeneralSubFrame2Layout.addWidget(sysDiagSlideConfGeneralAllSlidesCheckBox3)

#####
sysDiagSlideConfGeneralAllSlidesComboBox3 = QComboBox()
# sysDiagSlideConfGeneralAllSlidesComboBox3.setEditText(plotWindowConfigGraphList[6])
sysDiagSlideConfGeneralAllSlidesComboBox3.addItems(plotWindowConfigGraphList)
sysDiagSlideConfGeneralAllSlidesComboBox3.setCurrentIndex(6)
sysDiagSlideConfGeneralSubFrame2Layout.addWidget(sysDiagSlideConfGeneralAllSlidesComboBox3)


##########
##########

## TxAnt Diagrams Tab
txAntDiagTab = QWidget()
txAntDiagTab.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding)
txAntDiagTab.setMaximumHeight(400)
txAntDiagLayout = QGridLayout()
txAntDiagLayout.setHorizontalSpacing(H_LAYOUT_SPACING)
txAntDiagLayout.setVerticalSpacing(V_LAYOUT_SPACING)
txAntDiagLayout.setAlignment(Qt.AlignTop)
txAntDiagTab.setLayout(txAntDiagLayout)
# txAntDiagTab.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
mainTabWidget.insertTab(2,txAntDiagTab,'Tx-Antenna Diagrams')

### System Diagrams Start Script Button
txAntDiagRowIdx = 0
txAntDiagColIdx = 0

txAntDiagStartPushBtn = QPushButton('Start')
txAntDiagStartPushBtn.setFixedSize(PUSH_BTN_H_SIZE,PUSH_BTN_V_SIZE)
txAntDiagStartPushBtn.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
txAntDiagLayout.addWidget(txAntDiagStartPushBtn,txAntDiagRowIdx,txAntDiagColIdx)

#### Input Data Setup GroupBox
txAntDiagRowIdx += 1

txAntDiagInputSetupGroupBox = QGroupBox('Input Setup')
txAntDiagInputSetupGroupBox.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding)
txAntDiagInputSetupLayout = QHBoxLayout()

txAntDiagLayout.setRowStretch(0, 1)
txAntDiagLayout.setRowStretch(1, 1)

txAntDiagLayout.setColumnStretch(0, 1)
txAntDiagLayout.setColumnStretch(1, 3)


txAntDiagInputSetupLayout.setSpacing(H_LAYOUT_SPACING)
# txAntDiagInputSetupLayout.setVerticalSpacing(V_LAYOUT_SPACING)
txAntDiagInputSetupLayout.setAlignment(Qt.AlignTop)

txAntDiagInputSetupGroupBox.setLayout(txAntDiagInputSetupLayout)
txAntDiagLayout.addWidget(txAntDiagInputSetupGroupBox,txAntDiagRowIdx,txAntDiagColIdx)

##### Input Data GroupBox Frame
txAntDiagSetupGroupBoxFrame = QFrame()
txAntDiagSetupGroupBoxFrame.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding)
txAntDiagInputSetupGroupBoxFrameLayout = QVBoxLayout()
txAntDiagInputSetupGroupBoxFrameLayout.setSpacing(V_LAYOUT_SPACING)
txAntDiagInputSetupGroupBoxFrameLayout.setAlignment(Qt.AlignTop)

txAntDiagSetupGroupBoxFrame.setLayout(txAntDiagInputSetupGroupBoxFrameLayout)

txAntDiagInputSetupLayout.addWidget(txAntDiagSetupGroupBoxFrame)
#####
txAntDiagInputSetupAngleLabel = QLabel('Angle Setup')
txAntDiagInputSetupGroupBoxFrameLayout.addWidget(txAntDiagInputSetupAngleLabel)

#####
txAntDiagInputSetupAngleGroup = QButtonGroup()

txAntDiagInputSetupAngleSetupRadio1 = QRadioButton('Target Angle')
txAntDiagInputSetupGroupBoxFrameLayout.addWidget(txAntDiagInputSetupAngleSetupRadio1)
txAntDiagInputSetupAngleSetupRadio1.setChecked(True)
txAntDiagInputSetupAngleGroup.addButton(txAntDiagInputSetupAngleSetupRadio1,0)
#####

txAntDiagInputSetupAngleSetupRadio2 = QRadioButton('PTU Angle')
txAntDiagInputSetupGroupBoxFrameLayout.addWidget(txAntDiagInputSetupAngleSetupRadio2)
txAntDiagInputSetupAngleGroup.addButton(txAntDiagInputSetupAngleSetupRadio2,1)

#####


txAntDiagInputSetupHLine = QFrame()
txAntDiagInputSetupHLine.setFixedHeight(H_LINE_HEIGHT)
txAntDiagInputSetupHLine.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Fixed)
txAntDiagInputSetupHLine.setStyleSheet(lineStyle)
txAntDiagInputSetupGroupBoxFrameLayout.addWidget(txAntDiagInputSetupHLine)

#####


txAntDiagInputSetupSensorOrientGroup = QButtonGroup()

txAntDiagInputSetupAngleLabel = QLabel('Sensor Orientation')
txAntDiagInputSetupAngleLabel.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
txAntDiagInputSetupGroupBoxFrameLayout.addWidget(txAntDiagInputSetupAngleLabel)

#####

txAntDiagInputSetupSensorOrientRadio1 = QRadioButton('Normal')
txAntDiagInputSetupSensorOrientRadio1.setChecked(True)
txAntDiagInputSetupSensorOrientRadio1.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
txAntDiagInputSetupSensorOrientGroup.addButton(txAntDiagInputSetupSensorOrientRadio1)
txAntDiagInputSetupSensorOrientGroup.setId(txAntDiagInputSetupSensorOrientRadio1,0)
txAntDiagInputSetupGroupBoxFrameLayout.addWidget(txAntDiagInputSetupSensorOrientRadio1)


####
txAntDiagInputSetupSensorOrientRadio2 = QRadioButton('Upside-Down')
txAntDiagInputSetupSensorOrientRadio2.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
txAntDiagInputSetupGroupBoxFrameLayout.addWidget(txAntDiagInputSetupSensorOrientRadio2)
txAntDiagInputSetupSensorOrientGroup.addButton(txAntDiagInputSetupSensorOrientRadio2)
txAntDiagInputSetupSensorOrientGroup.setId(txAntDiagInputSetupSensorOrientRadio2,1)

#####
txAntDiagInputSetupHLine = QFrame()
txAntDiagInputSetupHLine.setFixedHeight(H_LINE_HEIGHT)
txAntDiagInputSetupHLine.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Fixed)
txAntDiagInputSetupHLine.setStyleSheet(lineStyle)
txAntDiagInputSetupGroupBoxFrameLayout.addWidget(txAntDiagInputSetupHLine)

#####
txAntDiagInputSetupAzCheckBox = QCheckBox('Azimuth Diagrams')
txAntDiagInputSetupAzCheckBox.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
txAntDiagInputSetupAzCheckBox.setChecked(True)
txAntDiagInputSetupGroupBoxFrameLayout.addWidget(txAntDiagInputSetupAzCheckBox,stretch=1)

#####
txAntDiagInputSetupElCheckBox = QCheckBox('Elevation Diagrams')
txAntDiagInputSetupElCheckBox.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
txAntDiagInputSetupElCheckBox.setChecked(True)
txAntDiagInputSetupGroupBoxFrameLayout.addWidget(txAntDiagInputSetupElCheckBox,stretch=1)

#### Plot Setup GroupBox
txAntDiagColIdx += 1

txAntDiagPlotSetupGroupBox = QGroupBox('Plot Setup')
# txAntDiagPlotSetupGroupBox.setMaximumHeight(300)
txAntDiagPlotSetupGroupBox.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding)
txAntDiagPlotSetupLayout = QHBoxLayout()


txAntDiagPlotSetupLayout.setSpacing(H_LAYOUT_SPACING)
# txAntDiagPlotSetupLayout.setVerticalSpacing(V_LAYOUT_SPACING)
txAntDiagPlotSetupLayout.setAlignment(Qt.AlignTop)

txAntDiagPlotSetupGroupBox.setLayout(txAntDiagPlotSetupLayout)
txAntDiagLayout.addWidget(txAntDiagPlotSetupGroupBox,txAntDiagRowIdx,txAntDiagColIdx)

##### Plot GroupBox Frame
txAntDiagSetupGroupBoxFrame = QFrame()
txAntDiagSetupGroupBoxFrame.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
txAntDiagPlotSetupGroupBoxFrameLayout = QVBoxLayout()
txAntDiagPlotSetupGroupBoxFrameLayout.setSpacing(V_LAYOUT_SPACING)
txAntDiagPlotSetupGroupBoxFrameLayout.setAlignment(Qt.AlignTop)

txAntDiagSetupGroupBoxFrame.setLayout(txAntDiagPlotSetupGroupBoxFrameLayout)
txAntDiagPlotSetupLayout.addWidget(txAntDiagSetupGroupBoxFrame)


#####
txAntDiagPlotSetupSensorNumSlideIntValidator = QIntValidator()
txAntDiagPlotSetupSensorNumSlideIntValidator.setRange(0,500)

txAntDiagPlotSetupSensorNumSlideLabel = QLabel('Num. of Sensors - Sensor Slide:')
txAntDiagPlotSetupGroupBoxFrameLayout.addWidget(txAntDiagPlotSetupSensorNumSlideLabel)

txAntDiagPlotSetupSensorNumSlideLEdit = QLineEdit()
txAntDiagPlotSetupSensorNumSlideLEdit.setValidator(sysDiagPlotSetupImageDpiIntValidator)
txAntDiagPlotSetupSensorNumSlideLEdit.setMaxLength(3)
txAntDiagPlotSetupSensorNumSlideLEdit.setFixedSize(LEDIT_BTN_H_SIZE,LEDIT_BTN_V_SIZE)
txAntDiagPlotSetupSensorNumSlideLEdit.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
txAntDiagPlotSetupGroupBoxFrameLayout.addWidget(txAntDiagPlotSetupSensorNumSlideLEdit)

####
txAntDiagInputSetupHLine = QFrame()
txAntDiagInputSetupHLine.setFixedHeight(H_LINE_HEIGHT)
txAntDiagInputSetupHLine.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding)
txAntDiagInputSetupHLine.setStyleSheet(lineStyle)
txAntDiagPlotSetupGroupBoxFrameLayout.addWidget(txAntDiagInputSetupHLine)

#####
txAntDiagPlotSetupGraphsPerSliideIntValidator = QIntValidator()
txAntDiagPlotSetupGraphsPerSliideIntValidator.setRange(1,4)

txAntDiagPlotSetupGraphsPerSlideLabel = QLabel('Graphs per Slide:')
txAntDiagPlotSetupGroupBoxFrameLayout.addWidget(txAntDiagPlotSetupGraphsPerSlideLabel)

txAntDiagPlotSetupGraphsPerSlideLEdit = QLineEdit()
txAntDiagPlotSetupGraphsPerSlideLEdit.setValidator(sysDiagPlotSetupImageDpiIntValidator)
txAntDiagPlotSetupGraphsPerSlideLEdit.setMaxLength(1)
txAntDiagPlotSetupGraphsPerSlideLEdit.setFixedSize(LEDIT_BTN_H_SIZE, LEDIT_BTN_V_SIZE)
txAntDiagPlotSetupGraphsPerSlideLEdit.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
txAntDiagPlotSetupGroupBoxFrameLayout.addWidget(txAntDiagPlotSetupGraphsPerSlideLEdit)

#####
txAntDiagInputSetupHLine = QFrame()
txAntDiagInputSetupHLine.setFixedHeight(H_LINE_HEIGHT)
txAntDiagInputSetupHLine.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Fixed)
txAntDiagInputSetupHLine.setStyleSheet(lineStyle)
txAntDiagPlotSetupGroupBoxFrameLayout.addWidget(txAntDiagInputSetupHLine)
#####
txAntDiagPlotSetupImageDpiIntValidator = QIntValidator()
txAntDiagPlotSetupImageDpiIntValidator.setRange(0,500)

txAntDiagPlotSetupImageDpiLabel = QLabel('Image DPI:')
txAntDiagPlotSetupGroupBoxFrameLayout.addWidget(txAntDiagPlotSetupImageDpiLabel)

txAntDiagPlotSetupImageDpiLEdit = QLineEdit()
txAntDiagPlotSetupImageDpiLEdit.setValidator(txAntDiagPlotSetupImageDpiIntValidator)
txAntDiagPlotSetupImageDpiLEdit.setMaxLength(3)
txAntDiagPlotSetupImageDpiLEdit.setFixedSize(LEDIT_BTN_H_SIZE,LEDIT_BTN_V_SIZE)
txAntDiagPlotSetupImageDpiLEdit.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
txAntDiagPlotSetupGroupBoxFrameLayout.addWidget(txAntDiagPlotSetupImageDpiLEdit)

#####
txAntDiagPlotSetupVLine = QFrame()
txAntDiagPlotSetupVLine.setFixedWidth(V_LINE_WIDTH)
txAntDiagPlotSetupVLine.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.MinimumExpanding)
txAntDiagPlotSetupVLine.setStyleSheet(lineStyle)
txAntDiagPlotSetupLayout.addWidget(txAntDiagPlotSetupVLine)

#####
##### Plot GroupBox Scaling Frame
txAntDiagPlotSetupGroupBoxScalingFrame = QFrame()
txAntDiagPlotSetupGroupBoxScalingFrame.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding)
txAntDiagPlotSetupGroupBoxScalingFrameLayout = QVBoxLayout()
txAntDiagPlotSetupGroupBoxScalingFrameLayout.setSpacing(V_LAYOUT_SPACING)
txAntDiagPlotSetupGroupBoxScalingFrameLayout.setAlignment(Qt.AlignTop)

txAntDiagPlotSetupGroupBoxScalingFrame.setLayout(txAntDiagPlotSetupGroupBoxScalingFrameLayout)
txAntDiagPlotSetupLayout.addWidget(txAntDiagPlotSetupGroupBoxScalingFrame)

#####
txAntDiagPlotSetupScalingAutoCheckBox = QCheckBox('X-Scale Autoscale')
txAntDiagPlotSetupScalingAutoCheckBox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

txAntDiagPlotSetupGroupBoxScalingFrameLayout.addWidget(txAntDiagPlotSetupScalingAutoCheckBox)

#####
txAntDiagPlotSetupScalingXScaleIntValidator = QIntValidator()
txAntDiagPlotSetupScalingXScaleIntValidator.setRange(0,150)

#####
txAntDiagPlotSetupScalingXScaleAzLabel = QLabel('X-Scale Azimuth:')
txAntDiagPlotSetupGroupBoxScalingFrameLayout.addWidget(txAntDiagPlotSetupScalingXScaleAzLabel)

txAntDiagPlotSetupScalingXScaleAzLEdit = QLineEdit()
txAntDiagPlotSetupScalingXScaleAzLEdit.setValidator(txAntDiagPlotSetupScalingXScaleIntValidator)
txAntDiagPlotSetupScalingXScaleAzLEdit.setMaxLength(3)
txAntDiagPlotSetupScalingXScaleAzLEdit.setFixedSize(LEDIT_BTN_H_SIZE,LEDIT_BTN_V_SIZE)
txAntDiagPlotSetupScalingXScaleAzLEdit.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
txAntDiagPlotSetupGroupBoxScalingFrameLayout.addWidget(txAntDiagPlotSetupScalingXScaleAzLEdit)

#####
txAntDiagPlotSetupScalingXScaleElLabel = QLabel('X-Scale Elevation:')
txAntDiagPlotSetupGroupBoxScalingFrameLayout.addWidget(txAntDiagPlotSetupScalingXScaleElLabel)

txAntDiagPlotSetupScalingXScaleElLEdit = QLineEdit()
txAntDiagPlotSetupScalingXScaleElLEdit.setValidator(txAntDiagPlotSetupScalingXScaleIntValidator)
txAntDiagPlotSetupScalingXScaleElLEdit.setMaxLength(3)
txAntDiagPlotSetupScalingXScaleElLEdit.setFixedSize(LEDIT_BTN_H_SIZE,LEDIT_BTN_V_SIZE)
txAntDiagPlotSetupScalingXScaleElLEdit.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
txAntDiagPlotSetupGroupBoxScalingFrameLayout.addWidget(txAntDiagPlotSetupScalingXScaleElLEdit)

#####


txAntDiagPlotSetupScalingHLine = QFrame()
txAntDiagPlotSetupScalingHLine.setFixedHeight(H_LINE_HEIGHT)
txAntDiagPlotSetupScalingHLine.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Fixed)
txAntDiagPlotSetupScalingHLine.setStyleSheet(lineStyle)
txAntDiagPlotSetupGroupBoxScalingFrameLayout.addWidget(txAntDiagPlotSetupScalingHLine)

#####
txAntDiagPlotSetupScalingOrigGraphsCheckBox = QCheckBox('Plot Original Graphs')
txAntDiagPlotSetupScalingOrigGraphsCheckBox.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
txAntDiagPlotSetupScalingOrigGraphsCheckBox.setChecked(True)
txAntDiagPlotSetupGroupBoxScalingFrameLayout.addWidget(txAntDiagPlotSetupScalingOrigGraphsCheckBox,stretch=1)

#####
txAntDiagPlotSetupScalingNormGraphsCheckBox = QCheckBox('Plot Normalised Graphs')
txAntDiagPlotSetupScalingNormGraphsCheckBox.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
txAntDiagPlotSetupScalingNormGraphsCheckBox.setChecked(True)
txAntDiagPlotSetupGroupBoxScalingFrameLayout.addWidget(txAntDiagPlotSetupScalingNormGraphsCheckBox,stretch=1)


#####
txAntDiagPlotSetupVLine = QFrame()
txAntDiagPlotSetupVLine.setFixedWidth(V_LINE_WIDTH)
txAntDiagPlotSetupVLine.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.MinimumExpanding)
txAntDiagPlotSetupVLine.setStyleSheet(lineStyle)
txAntDiagPlotSetupLayout.addWidget(txAntDiagPlotSetupVLine)

##### Plot Setup Graph Configuration Frame
txAntDiagPlotSetupGraphConfFrame = QFrame()
txAntDiagPlotSetupLayout.addWidget(txAntDiagPlotSetupGraphConfFrame)
txAntDiagPlotSetupGraphConfFrame.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
txAntDiagPlotSetupGraphConfLayout = QVBoxLayout()
txAntDiagPlotSetupGraphConfLayout.setAlignment(Qt.AlignTop)
txAntDiagPlotSetupGraphConfLayout.setSpacing(V_LAYOUT_SPACING)

txAntDiagPlotSetupGraphConfFrame.setLayout(txAntDiagPlotSetupGraphConfLayout)

#####
txAntDiagPlotSetupGraphConfLabel = QLabel('Graph Configuration')
txAntDiagPlotSetupGraphConfLayout.addWidget(txAntDiagPlotSetupGraphConfLabel)

txAntDiagGraphConfig = {
    # Power level diagrams
    "level": 1,  # Corrected transmited Power level using spectrum analyser [dBm].
    "levelPowMet": 1,  # Corrected transmited Power level using powermeter [dBm].

    "levelMeasSpec": 1,  # Measured transmited Power level using spectrum analyser [dBm].
    "levelMeasPowMet": 1, # Measured transmited Power level using spectrum analyser [dBm].

    # Phase difference diagrams
    "frequency": 1,  # Actual frequency [MHz].
    "time": 1,  # Time [ms].
}


# Mapping string for the graph titles
def txAntDiagGraphStringMapping(graphTitle):
    graphString = ''
    if graphTitle == "level":
        graphString = "Level [dBm]"
    elif graphTitle == "levelPowMet":
        graphString = "Level Pow. Meter [dBm]"
    elif graphTitle == "levelMeasSpec":
        graphString = "Level Meas. Spec. [dBm]"
    elif graphTitle == "levelMeasPowMet":
        graphString = "Level Meas. Pow. Meter [dBm]"
    elif graphTitle == "frequency":
        graphString = "Frequency [MHz]"
    elif graphTitle == "time":
        graphString = "Time [ms]"

    return graphString


# sysDiagPlotSetupGraphConfList=["level","avgLevel","normLevel","avgNormLevel","phaseDiff","avgPhaseDiff","diffPhaseDiff","avgDiffPhaseDiff","corrPhaseDiff"]
# def boolMapping(value):
#     if isinstance(value,bool):
#         if value==True:
#             return 1
#         else:
#             return 0
#     elif isinstance(value,int):
#         if value==1:
#             return True
#         elif value ==0:
#             return False
#         else:
#             raise ValueError('Input must be: int 1 or 0.')
#     else:
#         raise TypeError('Input must be: bool or int.')


txAntDiagPlotSetupGraphConfGroup = QButtonGroup()
txAntDiagPlotSetupGraphConfGroup.setExclusive(False)

id = 0
for key, val in txAntDiagGraphConfig.items():
    txAntDiagPlotSetupGraphConfCheckBox = QCheckBox(txAntDiagGraphStringMapping(key))
    # sysDiagPlotSetupGraphConfCheckBox.setChecked(boolMapping(val))
    txAntDiagPlotSetupGraphConfLayout.addWidget(txAntDiagPlotSetupGraphConfCheckBox)

    txAntDiagPlotSetupGraphConfGroup.addButton(txAntDiagPlotSetupGraphConfCheckBox, id)

    id += 1

# sysDiagPlotSetupGraphConfGroup.buttonClicked.connect(sysDiagPlotSetupGraphConfClick)

# #####
# sysDiagPlotSetupHLine=QFrame()
# sysDiagPlotSetupHLine.setFixedHeight(H_LINE_HEIGHT)
# sysDiagPlotSetupHLine.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Fixed)
# sysDiagPlotSetupHLine.setStyleSheet(lineStyle)
# sysDiagPlotSetupGraphConfLayout.addWidget(sysDiagPlotSetupHLine)

############
############

## Anttenna Pttterns Tab
antPatTab = QWidget()
antPatTab.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding)
# txAntDiagTab.setFixedSize(1000,400)

antPatLayout = QGridLayout()
antPatLayout.setHorizontalSpacing(H_LAYOUT_SPACING)
antPatLayout.setVerticalSpacing(V_LAYOUT_SPACING)
antPatLayout.setAlignment(Qt.AlignTop)

# antPatLayout.setColumnStretch(0,1)
# antPatLayout.setColumnStretch(1,1)

antPatTab.setLayout(antPatLayout)

mainTabWidget.insertTab(4,antPatTab,'Antenna Patterns')

### System Diagrams Start Script Button
antPatRowIdx = 0
antPatColIdx = 0

antPatStartPushBtn = QPushButton('Start')
antPatStartPushBtn.setFixedSize(PUSH_BTN_H_SIZE,PUSH_BTN_V_SIZE)
antPatStartPushBtn.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
antPatLayout.addWidget(antPatStartPushBtn,antPatRowIdx,antPatColIdx)

### Antenna Patterns Header
chirpConfig = {
    "chirp0": 1,
    "chirp1": 0,
    "chirp2": 0,
    "chirp3": 0,
}

antPatHeader = {

    # Name
    "name": "Antenna_Pattern_Tables",

    # Port identifier
    "identifier": 36,

    # Version
    "majorVersion": 2,
    "minorVersion": 0,

    # Date
    "year": 2019,
    "month": 12,
    "day": 19,

    # Antenna information
    "rfeGeneration": 48,
    "rfeModification": 0,
    "rfeRevision": 0,


}

antPatHeaderGroupBox = QGroupBox('Antenna Patterns Header')
antPatHeaderGroupBox.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding)
antPatHeaderLayout = QHBoxLayout()
antPatHeaderLayout.setSpacing(H_LAYOUT_SPACING)
antPatHeaderLayout.setAlignment(Qt.AlignTop)

antPatHeaderGroupBox.setLayout(antPatHeaderLayout)
antPatLayout.addWidget(antPatHeaderGroupBox,1,0)

antPatHeaderFrame = QFrame()
antPatHeaderFrameLayout = QVBoxLayout()
antPatHeaderFrameLayout.setSpacing(H_LAYOUT_SPACING)
antPatHeaderFrameLayout.setAlignment(Qt.AlignTop)
antPatHeaderFrame.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
antPatHeaderFrame.setLayout(antPatHeaderFrameLayout)

antPatHeaderLayout.addWidget(antPatHeaderFrame,stretch=1)

#####
antPatInputNameIdentifierSelCheckBox = QCheckBox('Name and Identifier Selection')
antPatInputNameIdentifierSelCheckBox.setChecked(False)
antPatInputNameIdentifierSelCheckBox.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
antPatHeaderFrameLayout.addWidget(antPatInputNameIdentifierSelCheckBox)
#####
antPatHeaderNameLabel = QLabel()
antPatHeaderNameLabel.setText('Name:')
antPatHeaderNameLabel.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
antPatHeaderFrameLayout.addWidget(antPatHeaderNameLabel,stretch=1)

antPatHeaderNameLEdit = QLineEdit()
# sysDiagSlideConfGeneralSensorNumSlideLEdit.setValidator(sysDiagPlotSetupImageDpiIntValidator)
# sysDiagSlideConfGeneralSensorNumSlideLEdit.setMaxLength(3)
antPatHeaderNameLEdit.setFixedSize(LEDIT_BTN_H_SIZE,LEDIT_BTN_V_SIZE)
antPatHeaderNameLEdit.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
antPatHeaderFrameLayout.addWidget(antPatHeaderNameLEdit)

#####
antPatHeaderIdentifierLabel = QLabel()
antPatHeaderIdentifierLabel.setText('Identifier:')
antPatHeaderIdentifierLabel.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
antPatHeaderFrameLayout.addWidget(antPatHeaderIdentifierLabel,stretch=1)

antPatHeaderIdentifierIntValidator = QIntValidator()
antPatHeaderIdentifierIntValidator.setRange(0,999)

antPatHeaderIdentifierLEdit = QLineEdit()
antPatHeaderIdentifierLEdit.setValidator(antPatHeaderIdentifierIntValidator)
antPatHeaderIdentifierLEdit.setMaxLength(3)
antPatHeaderIdentifierLEdit.setFixedSize(LEDIT_BTN_H_SIZE,LEDIT_BTN_V_SIZE)
antPatHeaderIdentifierLEdit.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
antPatHeaderFrameLayout.addWidget(antPatHeaderIdentifierLEdit)

#####
antPatHeaderHLine = QFrame()
antPatHeaderHLine.setFixedHeight(H_LINE_HEIGHT)
antPatHeaderHLine.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Fixed)
antPatHeaderHLine.setStyleSheet(lineStyle)
antPatHeaderFrameLayout.addWidget(antPatHeaderHLine)

#####
antPatHeaderMajVerLabel = QLabel()
antPatHeaderMajVerLabel.setText('Major Version:')
antPatHeaderMajVerLabel.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
antPatHeaderFrameLayout.addWidget(antPatHeaderMajVerLabel,stretch=1)

antPatHeaderMajVerIntValidator = QIntValidator()
antPatHeaderMajVerIntValidator.setRange(0,9)

antPatHeaderMajVerLEdit = QLineEdit()
antPatHeaderMajVerLEdit.setValidator(antPatHeaderMajVerIntValidator)
antPatHeaderMajVerLEdit.setMaxLength(1)
antPatHeaderMajVerLEdit.setFixedSize(LEDIT_BTN_H_SIZE,LEDIT_BTN_V_SIZE)
antPatHeaderMajVerLEdit.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
antPatHeaderFrameLayout.addWidget(antPatHeaderMajVerLEdit)

#####
antPatHeaderMinVerLabel = QLabel()
antPatHeaderMinVerLabel.setText('Minor Version:')
antPatHeaderMinVerLabel.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
antPatHeaderFrameLayout.addWidget(antPatHeaderMinVerLabel,stretch=1)

antPatHeaderMinVerIntValidator = QIntValidator()
antPatHeaderMinVerIntValidator.setRange(0,9)

antPatHeaderMinVerLEdit = QLineEdit()
antPatHeaderMinVerLEdit.setValidator(antPatHeaderMinVerIntValidator)
antPatHeaderMinVerLEdit.setMaxLength(1)
antPatHeaderMinVerLEdit.setFixedSize(LEDIT_BTN_H_SIZE,LEDIT_BTN_V_SIZE)
antPatHeaderMajVerLEdit.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
antPatHeaderFrameLayout.addWidget(antPatHeaderMinVerLEdit)

#####
antPatHeaderHLine = QFrame()
antPatHeaderHLine.setFixedHeight(H_LINE_HEIGHT)
antPatHeaderHLine.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Fixed)
antPatHeaderHLine.setStyleSheet(lineStyle)
antPatHeaderFrameLayout.addWidget(antPatHeaderHLine)
antPatInputConfSensorOrientGroup = QButtonGroup()
#####
antPatHeaderYearLabel = QLabel()
antPatHeaderYearLabel.setText('Year:')
antPatHeaderYearLabel.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
antPatHeaderFrameLayout.addWidget(antPatHeaderYearLabel,stretch=1)

antPatHeaderYearIntValidator = QIntValidator()
antPatHeaderMinVerIntValidator.setRange(0,2099)

antPatHeaderYearLEdit = QLineEdit()
antPatHeaderYearLEdit.setValidator(antPatHeaderYearIntValidator)
antPatHeaderYearLEdit.setMaxLength(4)
antPatHeaderYearLEdit.setFixedSize(LEDIT_BTN_H_SIZE,LEDIT_BTN_V_SIZE)
antPatHeaderMajVerLEdit.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
antPatHeaderFrameLayout.addWidget(antPatHeaderYearLEdit)

#####
antPatHeaderMonthLabel = QLabel()
antPatHeaderMonthLabel.setText('Month:')
antPatHeaderMonthLabel.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
antPatHeaderFrameLayout.addWidget(antPatHeaderMonthLabel,stretch=1)

antPatHeaderMonthIntValidator = QIntValidator()
antPatHeaderMinVerIntValidator.setRange(1,12)

antPatHeaderMonthLEdit = QLineEdit()
antPatHeaderMonthLEdit.setValidator(antPatHeaderMonthIntValidator)
antPatHeaderMonthLEdit.setMaxLength(2)
antPatHeaderMonthLEdit.setFixedSize(LEDIT_BTN_H_SIZE,LEDIT_BTN_V_SIZE)
antPatHeaderMajVerLEdit.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
antPatHeaderFrameLayout.addWidget(antPatHeaderMonthLEdit)

#####
antPatHeaderDayLabel = QLabel()
antPatHeaderDayLabel.setText('Day:')
antPatHeaderDayLabel.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
antPatHeaderFrameLayout.addWidget(antPatHeaderDayLabel,stretch=1)

antPatHeaderDayIntValidator = QIntValidator()
antPatHeaderMinVerIntValidator.setRange(1,31)

antPatHeaderDayLEdit = QLineEdit()
antPatHeaderDayLEdit.setValidator(antPatHeaderDayIntValidator)
antPatHeaderDayLEdit.setMaxLength(2)
antPatHeaderDayLEdit.setFixedSize(LEDIT_BTN_H_SIZE,LEDIT_BTN_V_SIZE)
antPatHeaderMajVerLEdit.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
antPatHeaderFrameLayout.addWidget(antPatHeaderDayLEdit)

#####
antPatHeaderHLine = QFrame()
antPatHeaderHLine.setFixedHeight(H_LINE_HEIGHT)
antPatHeaderHLine.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Fixed)
antPatHeaderHLine.setStyleSheet(lineStyle)
antPatHeaderFrameLayout.addWidget(antPatHeaderHLine)
antPatInputConfSensorOrientGroup=QButtonGroup()
#####
antPatHeaderRfeGenLabel = QLabel()
antPatHeaderRfeGenLabel.setText('rfeGeneration:')
antPatHeaderRfeGenLabel.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
antPatHeaderFrameLayout.addWidget(antPatHeaderRfeGenLabel,stretch=1)

antPatHeaderRfeGenIntValidator = QIntValidator()
antPatHeaderMinVerIntValidator.setRange(0,9)

antPatHeaderRfeGenLEdit = QLineEdit()
antPatHeaderRfeGenLEdit.setValidator(antPatHeaderRfeGenIntValidator)
antPatHeaderRfeGenLEdit.setMaxLength(1)
antPatHeaderRfeGenLEdit.setFixedSize(LEDIT_BTN_H_SIZE,LEDIT_BTN_V_SIZE)
antPatHeaderMajVerLEdit.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
antPatHeaderFrameLayout.addWidget(antPatHeaderRfeGenLEdit)

#####
antPatHeaderRfeModLabel = QLabel()
antPatHeaderRfeModLabel.setText('rfeModification:')
antPatHeaderRfeModLabel.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
antPatHeaderFrameLayout.addWidget(antPatHeaderRfeModLabel,stretch=1)

antPatHeaderRfeModIntValidator = QIntValidator()
antPatHeaderMinVerIntValidator.setRange(0,9)

antPatHeaderRfeModLEdit = QLineEdit()
antPatHeaderRfeModLEdit.setValidator(antPatHeaderRfeModIntValidator)
antPatHeaderRfeModLEdit.setMaxLength(1)
antPatHeaderRfeModLEdit.setFixedSize(LEDIT_BTN_H_SIZE,LEDIT_BTN_V_SIZE)
antPatHeaderMajVerLEdit.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
antPatHeaderFrameLayout.addWidget(antPatHeaderRfeModLEdit)

#####
antPatHeaderRfeRevLabel = QLabel()
antPatHeaderRfeRevLabel.setText('rfeRevision:')
antPatHeaderRfeRevLabel.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
antPatHeaderFrameLayout.addWidget(antPatHeaderRfeRevLabel,stretch=1)

antPatHeaderRfeRevIntValidator = QIntValidator()
antPatHeaderMinVerIntValidator.setRange(0,9)

antPatHeaderRfeRevLEdit = QLineEdit()
antPatHeaderRfeRevLEdit.setValidator(antPatHeaderRfeRevIntValidator)
antPatHeaderRfeRevLEdit.setMaxLength(1)
antPatHeaderRfeRevLEdit.setFixedSize(LEDIT_BTN_H_SIZE,LEDIT_BTN_V_SIZE)
antPatHeaderMajVerLEdit.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
antPatHeaderFrameLayout.addWidget(antPatHeaderRfeRevLEdit)

##### Antenna Patterns Table GroupBox

antPatTableConfGroupBox = QGroupBox('Table Configuration')
antPatTableConfGroupBox.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.MinimumExpanding)
antPatTableConfLayout = QHBoxLayout()
antPatTableConfLayout.setSpacing(H_LAYOUT_SPACING)
antPatTableConfLayout.setAlignment(Qt.AlignTop)

antPatTableConfGroupBox.setLayout(antPatTableConfLayout)
antPatLayout.addWidget(antPatTableConfGroupBox,1,1)


antPatTableConfFrame = QFrame()
antPatTableConfFrameLayout = QGridLayout()

antPatTableConfFrameLayout.setHorizontalSpacing(H_LAYOUT_SPACING)
antPatTableConfFrameLayout.setVerticalSpacing(V_LAYOUT_SPACING)

antPatTableConfFrameLayout.setAlignment(Qt.AlignTop)
antPatTableConfFrame.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
antPatTableConfFrame.setLayout(antPatTableConfFrameLayout)

antPatTableConfLayout.addWidget(antPatTableConfFrame,stretch=1)

antPatTableRotAxisList = ['Invalid','Azimuth','Elevation','Polarisation']
antPatTablePatTypeList = ['Invalid','Tx - Rx','Tx','Rx']
antPatTableGainCalcMethodList = ['Invalid','Step-wise','Interpolation']

antPatTableWidgetsList = []


antPatTableCheckBoxGroup = QButtonGroup()
antPatTableCheckBoxGroup.setExclusive(False)

# antPatTablePatTypeComboGroup = QButtonGroup()
# antPatTablePatTypeComboGroup.setExclusive(False)
# antPatTablePatTypeComboGroup

antPatTableRotAxisComboGroup = QButtonGroup()
antPatTableRotAxisComboGroup.setExclusive(False)

antPatTableGainCalcMethodComboGroup = QButtonGroup()
antPatTableGainCalcMethodComboGroup.setExclusive(False)

signalMapper = QSignalMapper()

for rowIdx in range(2):
    for colIdx in range(4):

        tableIdx = 4*rowIdx + colIdx

        antPatTableWidgetsDict = {
            'tableCheckBox': 0,
            'patTypeComboBox': 0,
            'rotAxisComboBox': 0,
            'nofAppTxAntIdxLEdit': 0,
            'nofAppRxAntIdxLEdit': 0,
            'appTxAntIdxLEdit': 0,
            'appRxAntIdxLEdit': 0,
            'gainCalcMethodComboBox': 0

        }

        ##### Antenna Patterns Frame1
        antPatTable = QFrame()
        antPatTable.setObjectName('Frame')
        antPatTableLayout = QHBoxLayout()
        antPatTableLayout.setSpacing(V_LAYOUT_SPACING)
        antPatTableLayout.setAlignment(Qt.AlignTop)
        antPatTable.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.MinimumExpanding)
        antPatTable.setLayout(antPatTableLayout)
        antPatTable.setStyleSheet(antPatTableStyle)

        antPatTableConfFrameLayout.addWidget(antPatTable,rowIdx,colIdx)


        ###### Subframe
        antPatTableSubFrame1 = QFrame()
        antPatTableSubFrame1.setObjectName('SubFrame1')
        antPatTableSubFrame1Layout = QVBoxLayout()
        antPatTableSubFrame1Layout.setSpacing(V_LAYOUT_SPACING)
        antPatTableSubFrame1Layout.setAlignment(Qt.AlignTop)
        antPatTableSubFrame1.setStyleSheet(antPatTableStyle)
        antPatTableSubFrame1.setLayout(antPatTableSubFrame1Layout)

        antPatTableLayout.addWidget(antPatTableSubFrame1)


        ######
        tableName = 'Table ' +str(tableIdx)
        antPatTableCheckBox = QCheckBox(tableName)
        antPatTableCheckBox.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)

        antPatTableSubFrame1Layout.addWidget(antPatTableCheckBox,stretch=1)

        antPatTableWidgetsDict['tableCheckBox'] = antPatTableCheckBox

        ######

        antPatTablePatTypeLabel = QLabel()
        antPatTablePatTypeLabel.setText('Pattern Type')
        antPatTablePatTypeLabel.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        antPatTableSubFrame1Layout.addWidget(antPatTablePatTypeLabel,stretch=1)

        antPatTablePatTypeComboBox = QComboBox()
        antPatTablePatTypeComboBox.addItems(antPatTablePatTypeList)
        antPatTableWidgetsDict['patTypeComboBox'] = antPatTablePatTypeComboBox
        antPatTableSubFrame1Layout.addWidget(antPatTablePatTypeComboBox,stretch=1)

        ######
        antPatTableRotAxisLabel = QLabel()
        antPatTableRotAxisLabel.setText('Rotation Axis')
        antPatTableRotAxisLabel.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        antPatTableSubFrame1Layout.addWidget(antPatTableRotAxisLabel,stretch=1)

        antPatTableRotAxisComboBox = QComboBox()
        antPatTableRotAxisComboBox.addItems(antPatTableRotAxisList)
        antPatTableRotAxisComboBox.setEditText(antPatTableRotAxisList[1])
        antPatTableSubFrame1Layout.addWidget(antPatTableRotAxisComboBox, stretch=1)
        antPatTableWidgetsDict['rotAxisComboBox'] = antPatTableRotAxisComboBox
        # antPatTableRotAxisComboGroup.addButton(antPatTableRotAxisComboBox, tableIdx)


        ######
        antPatTableGainCalcMethodLabel = QLabel()
        antPatTableGainCalcMethodLabel.setText('Gain Calculation Mehtod')
        antPatTableGainCalcMethodLabel.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        antPatTableSubFrame1Layout.addWidget(antPatTableGainCalcMethodLabel,stretch=1)

        antPatTableGainCalcMethodComboBox = QComboBox()
        antPatTableGainCalcMethodComboBox.addItems(antPatTableGainCalcMethodList)
        # antPatTableGainCalcMethodComboBox.setEditText(antPatTableGainCalcMethodList[1])
        antPatTableSubFrame1Layout.addWidget(antPatTableGainCalcMethodComboBox,stretch=1)
        antPatTableWidgetsDict['gainCalcMethodComboBox'] = antPatTableGainCalcMethodComboBox
        # antPatTableGainCalcMethodComboGroup.addButton(antPatTableGainCalcMethodComboBox, tableIdx)


        ###### Subframe2
        antPatTableSubFrame2 = QFrame()
        antPatTableSubFrame2.setObjectName('SubFrame2')
        antPatTableSubFrame2Layout = QVBoxLayout()
        antPatTableSubFrame2Layout.setSpacing(V_LAYOUT_SPACING)
        antPatTableSubFrame2Layout.setAlignment(Qt.AlignTop)
        antPatTableSubFrame2.setLayout(antPatTableSubFrame2Layout)
        antPatTableSubFrame2.setStyleSheet(antPatTableStyle)

        antPatTableLayout.addWidget(antPatTableSubFrame2)
        ######
        antPatTableNofAppTxAntIdxLabel = QLabel()
        antPatTableNofAppTxAntIdxLabel.setText('Num. of App. Tx-Ant. Ind.:')
        antPatTableNofAppTxAntIdxLabel.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        antPatTableSubFrame2Layout.addWidget(antPatTableNofAppTxAntIdxLabel,stretch=1)

        antPatTableNofAppTxAntIdxIntValidator = QIntValidator()
        antPatHeaderMinVerIntValidator.setRange(0,9)

        antPatTableNofAppTxAntIdxLEdit = QLineEdit()
        antPatTableNofAppTxAntIdxLEdit.setValidator(antPatTableNofAppTxAntIdxIntValidator)
        antPatTableNofAppTxAntIdxLEdit.setMaxLength(1)
        antPatTableNofAppTxAntIdxLEdit.setFixedSize(LEDIT_BTN_H_SIZE,LEDIT_BTN_V_SIZE)

        antPatHeaderMajVerLEdit.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        antPatTableSubFrame2Layout.addWidget(antPatTableNofAppTxAntIdxLEdit)

        antPatTableWidgetsDict['nofAppTxAntIdxLEdit'] = antPatTableNofAppTxAntIdxLEdit
        #####
        antPatTableNofAppRxAntIdxLabel = QLabel()
        antPatTableNofAppRxAntIdxLabel.setText('Num. of App. Rx-Ant. Ind.:')
        antPatTableNofAppRxAntIdxLabel.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        antPatTableSubFrame2Layout.addWidget(antPatTableNofAppRxAntIdxLabel,stretch=1)

        antPatTableNofAppRxAntIdxIntValidator = QIntValidator()
        antPatHeaderMinVerIntValidator.setRange(0,9)

        antPatTableNofAppRxAntIdxLEdit = QLineEdit()
        antPatTableNofAppRxAntIdxLEdit.setValidator(antPatTableNofAppRxAntIdxIntValidator)
        antPatTableNofAppRxAntIdxLEdit.setMaxLength(1)
        antPatTableNofAppRxAntIdxLEdit.setFixedSize(LEDIT_BTN_H_SIZE,LEDIT_BTN_V_SIZE)
        antPatHeaderMajVerLEdit.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        antPatTableSubFrame2Layout.addWidget(antPatTableNofAppRxAntIdxLEdit)

        antPatTableWidgetsDict['nofAppRxAntIdxLEdit'] = antPatTableNofAppRxAntIdxLEdit
        #####
        antPatTableAppTxAntIdxLabel = QLabel()
        antPatTableAppTxAntIdxLabel.setText('App. Tx-Antenna Indices:')
        antPatTableAppTxAntIdxLabel.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        antPatTableSubFrame2Layout.addWidget(antPatTableAppTxAntIdxLabel,stretch=1)

        antPatTableAppTxAntIdxRegExp = QRegularExpression(r'^\d(,\d)*$')

        antPatTableAppTxAntIdxRegexValidator = QRegularExpressionValidator(antPatTableAppTxAntIdxRegExp)
        # antPatTableAppTxAntIdxRegexValidator.setRange(0,9)

        antPatTableAppTxAntIdxLEdit = QLineEdit()
        antPatTableAppTxAntIdxLEdit.setValidator(antPatTableAppTxAntIdxRegexValidator)
        # antPatTableAppTxAntIdxLEdit.setMaxLength(1)
        antPatTableAppTxAntIdxLEdit.setFixedSize(LEDIT_BTN_H_SIZE,LEDIT_BTN_V_SIZE)
        antPatHeaderMajVerLEdit.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        antPatTableSubFrame2Layout.addWidget(antPatTableAppTxAntIdxLEdit)

        antPatTableWidgetsDict['appTxAntIdxLEdit'] = antPatTableAppTxAntIdxLEdit
        #####
        antPatTableAppRxAntIdxLabel = QLabel()
        antPatTableAppRxAntIdxLabel.setText('App. Rx-Antenna Indices:')
        antPatTableAppRxAntIdxLabel.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        antPatTableSubFrame2Layout.addWidget(antPatTableAppRxAntIdxLabel,stretch=1)

        antPatTableAppRxAntIdxRegExp = QRegularExpression(r'^\d(,\d)*$')

        antPatTableAppRxAntIdxRegexValidator = QRegularExpressionValidator(antPatTableAppRxAntIdxRegExp)
        # antPatTableAppRxAntIdxRegexValidator.setRange(0,9)

        antPatTableAppRxAntIdxLEdit = QLineEdit()
        antPatTableAppRxAntIdxLEdit.setValidator(antPatTableAppRxAntIdxRegexValidator)
        # antPatTableAppRxAntIdxLEdit.setMaxLength(1)
        antPatTableAppRxAntIdxLEdit.setFixedSize(LEDIT_BTN_H_SIZE,LEDIT_BTN_V_SIZE)
        antPatHeaderMajVerLEdit.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        antPatTableSubFrame2Layout.addWidget(antPatTableAppRxAntIdxLEdit)

        antPatTableWidgetsDict['appRxAntIdxLEdit'] = antPatTableAppRxAntIdxLEdit

        antPatTableWidgetsList.append(antPatTableWidgetsDict)

###### Antenna Patterns YAML Config GroupBox
antPatInputYAMLGroupBox = QGroupBox('Output Format')
antPatInputYAMLGroupBox.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding)
antPatInputYAMLLayout = QHBoxLayout()
antPatInputYAMLLayout.setSpacing(H_LAYOUT_SPACING)
antPatInputYAMLLayout.setAlignment(Qt.AlignTop)

antPatInputYAMLGroupBox.setLayout(antPatInputYAMLLayout)
antPatLayout.addWidget(antPatInputYAMLGroupBox,1,5)

antPatInputYAMLFrame = QFrame()
antPatInputYAMLFrameLayout = QVBoxLayout()

antPatInputYAMLFrameLayout.setSpacing(V_LAYOUT_SPACING)

antPatInputYAMLFrameLayout.setAlignment(Qt.AlignTop)
antPatInputYAMLFrame.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
antPatInputYAMLFrame.setLayout(antPatInputYAMLFrameLayout)

antPatInputYAMLLayout.addWidget(antPatInputYAMLFrame,stretch=1)

#####################antenna pattern Yaml file information########################################
antPatInputConfAntYamlConfLabel = QLabel('version')
antPatInputYAMLFrameLayout.addWidget(antPatInputConfAntYamlConfLabel)

antPatInputConfAntYamlGroup = QButtonGroup()
antPatInputConfAntYamlGroup.setExclusive(False)

#####

antPatInputConfYAMLGroup = QButtonGroup()

antPatInputConfYAMLSetupRadio1 = QRadioButton('json v1')
antPatInputYAMLFrameLayout.addWidget(antPatInputConfYAMLSetupRadio1)
antPatInputConfYAMLSetupRadio1.setChecked(True)
antPatInputConfYAMLGroup.addButton(antPatInputConfYAMLSetupRadio1,0)
#####

antPatInputConfYAMLSetupRadio2 = QRadioButton('yaml v1')
antPatInputYAMLFrameLayout.addWidget(antPatInputConfYAMLSetupRadio2)
antPatInputConfYAMLGroup.addButton(antPatInputConfYAMLSetupRadio2,1)

#####

antPatInputConfYAMLSetupRadio3 = QRadioButton('yaml v2')
antPatInputYAMLFrameLayout.addWidget(antPatInputConfYAMLSetupRadio3)
antPatInputConfYAMLGroup.addButton(antPatInputConfYAMLSetupRadio3,2)



###### Antenna Patterns Input Config GroupBox
antPatInputConfGroupBox = QGroupBox('Input Configuration')
antPatInputConfGroupBox.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding)
antPatInputConfLayout = QHBoxLayout()
antPatInputConfLayout.setSpacing(H_LAYOUT_SPACING)
antPatInputConfLayout.setAlignment(Qt.AlignTop)

antPatInputConfGroupBox.setLayout(antPatInputConfLayout)
antPatLayout.addWidget(antPatInputConfGroupBox,1,2)

antPatInputConfFrame = QFrame()
antPatInputConfFrameLayout = QVBoxLayout()

antPatInputConfFrameLayout.setSpacing(V_LAYOUT_SPACING)

antPatInputConfFrameLayout.setAlignment(Qt.AlignTop)
antPatInputConfFrame.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
antPatInputConfFrame.setLayout(antPatInputConfFrameLayout)

antPatInputConfLayout.addWidget(antPatInputConfFrame,stretch=1)

#####
antPatInputConfAngleLabel = QLabel('Angle Setup')
antPatInputConfFrameLayout.addWidget(antPatInputConfAngleLabel)

#####
antPatInputConfAngleGroup = QButtonGroup()

antPatInputConfAngleSetupRadio1 = QRadioButton('Target Angle')
antPatInputConfFrameLayout.addWidget(antPatInputConfAngleSetupRadio1)
antPatInputConfAngleSetupRadio1.setChecked(True)
antPatInputConfAngleGroup.addButton(antPatInputConfAngleSetupRadio1,0)
#####

antPatInputConfAngleSetupRadio2 = QRadioButton('PTU Angle')
antPatInputConfFrameLayout.addWidget(antPatInputConfAngleSetupRadio2)
antPatInputConfAngleGroup.addButton(antPatInputConfAngleSetupRadio2,1)

#####
antPatInputConfHLine = QFrame()
antPatInputConfHLine.setFixedHeight(H_LINE_HEIGHT)
antPatInputConfHLine.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Fixed)
antPatInputConfHLine.setStyleSheet(lineStyle)
antPatInputConfFrameLayout.addWidget(antPatInputConfHLine)
antPatInputConfSensorOrientGroup = QButtonGroup()

######
antPatInputConfAngleLabel = QLabel('Sensor Orientation')
antPatInputConfAngleLabel.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
antPatInputConfFrameLayout.addWidget(antPatInputConfAngleLabel)

#####

antPatInputConfSensorOrientRadio1 = QRadioButton('Normal')
antPatInputConfSensorOrientRadio1.setChecked(True)
antPatInputConfSensorOrientRadio1.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
antPatInputConfSensorOrientGroup.addButton(antPatInputConfSensorOrientRadio1)
antPatInputConfSensorOrientGroup.setId(antPatInputConfSensorOrientRadio1,0)
antPatInputConfFrameLayout.addWidget(antPatInputConfSensorOrientRadio1)

#####
antPatInputConfSensorOrientRadio2 = QRadioButton('Upside-Down')
antPatInputConfSensorOrientRadio2.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

antPatInputConfFrameLayout.addWidget(antPatInputConfSensorOrientRadio2)
antPatInputConfSensorOrientGroup.addButton(antPatInputConfSensorOrientRadio2)
antPatInputConfSensorOrientGroup.setId(antPatInputConfSensorOrientRadio2,1)

#####
antPatInputConfHLine = QFrame()
antPatInputConfHLine.setFixedHeight(H_LINE_HEIGHT)
antPatInputConfHLine.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Fixed)
antPatInputConfHLine.setStyleSheet(lineStyle)
antPatInputConfFrameLayout.addWidget(antPatInputConfHLine)

######
antPatInputConfFileSearchCheckBox = QCheckBox('Input Files Include Selection')
antPatInputConfFileSearchCheckBox.setChecked(False)
antPatInputConfFileSearchCheckBox.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
antPatInputConfFrameLayout.addWidget(antPatInputConfFileSearchCheckBox)

# antPatInputConfFileSearchLabel = QLabel('Input Files Include')
# antPatInputConfFileSearchLabel.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
# antPatInputConfFrameLayout.addWidget(antPatInputConfFileSearchLabel)

######
antPatTableDiagTypeInfoCheckBox = QCheckBox('With Diag. Type (Az/El) Info')
antPatTableDiagTypeInfoCheckBox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
antPatTableDiagTypeInfoCheckBox.setChecked(True)
antPatInputConfFrameLayout.addWidget(antPatTableDiagTypeInfoCheckBox)

######
antPatTableUpsideDownInfoCheckBox = QCheckBox('With Upside-Down Info')
antPatTableUpsideDownInfoCheckBox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
antPatTableUpsideDownInfoCheckBox.setChecked(True)
antPatInputConfFrameLayout.addWidget(antPatTableUpsideDownInfoCheckBox)

#####
antPatInputConfHLine = QFrame()
antPatInputConfHLine.setFixedHeight(H_LINE_HEIGHT)
antPatInputConfHLine.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Fixed)
antPatInputConfHLine.setStyleSheet(lineStyle)
antPatInputConfFrameLayout.addWidget(antPatInputConfHLine)

##### Antenna Patterns Chirp Config
antPatInputConfChirpConfLabel = QLabel('Chirp Configuration')
antPatInputConfFrameLayout.addWidget(antPatInputConfChirpConfLabel)

antPatInputConfChirpGroup = QButtonGroup()
antPatInputConfChirpGroup.setExclusive(False)

#####

antPatInputConfChirp0CheckBox = QCheckBox('Chirp 0')
antPatInputConfChirpGroup.addButton(antPatInputConfChirp0CheckBox,0)
antPatInputConfChirp0CheckBox.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
antPatInputConfChirp0CheckBox.setChecked(True)

antPatInputConfFrameLayout.addWidget(antPatInputConfChirp0CheckBox)

#####

antPatInputConfChirp1CheckBox = QCheckBox('Chirp 1')
antPatInputConfChirpGroup.addButton(antPatInputConfChirp1CheckBox,1)

antPatInputConfChirp1CheckBox.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
antPatInputConfChirp1CheckBox.setChecked(False)

antPatInputConfFrameLayout.addWidget(antPatInputConfChirp1CheckBox)


#####


antPatInputConfChirp2CheckBox = QCheckBox('Chirp 2')
antPatInputConfChirpGroup.addButton(antPatInputConfChirp2CheckBox,2)

antPatInputConfChirp2CheckBox.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
antPatInputConfChirp2CheckBox.setChecked(False)

antPatInputConfFrameLayout.addWidget(antPatInputConfChirp2CheckBox)

#####


antPatInputConfChirp3CheckBox = QCheckBox('Chirp 3')
antPatInputConfChirpGroup.addButton(antPatInputConfChirp3CheckBox,3)

antPatInputConfChirp3CheckBox.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
antPatInputConfChirp3CheckBox.setChecked(False)

antPatInputConfFrameLayout.addWidget(antPatInputConfChirp3CheckBox)



# antPatHeaderHLine=QFrame()
# antPatHeaderHLine.setFixedHeight(H_LINE_HEIGHT)
# antPatHeaderHLine.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Fixed)
# antPatHeaderHLine.setStyleSheet(lineStyle)
# antPatHeaderGeneralLayout.addWidget(antPatHeaderHLine)

#####
# #####
# antPatHeaderInputModeGroup=QButtonGroup()
# #####
#
# antPatHeaderInputModeRadio1=QRadioButton('Data')
# antPatHeaderGeneralLayout.addWidget(antPatHeaderInputModeRadio1)
# # sysDiagInputSetupAngleSetupRadio1.setChecked(True)
# antPatHeaderInputModeGroup.addButton(antPatHeaderInputModeRadio1,0)
# #####
# #####
#
# antPatHeaderInputModeRadio2=QRadioButton('String')
# antPatHeaderGeneralLayout.addWidget(antPatHeaderInputModeRadio2)
# # sysDiagInputSetupAngleSetupRadio1.setChecked(True)
# antPatHeaderInputModeGroup.addButton(antPatHeaderInputModeRadio2,1)
# #####
#



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

# Set plot collor for each sensor
def getGraphColor(combIdx):
    colorList = ['blue', 'red', 'green', 'magenta', 'black', 'cyan', 'orange','midnightblue','maroon','springgreen','purple','dimgrey','teal','yellow']

    if combIdx >= len(colorList):
        res = combIdx%len(colorList)
        color = colorList[res]
    else:
        color = colorList[combIdx]
    return color

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

#####
class Match(enum.Enum):
    Contains   = 0
    ExactMatch = 0


dialogLEditErrorStyle = '''
.QLineEdit{
    border: 1px solid red
}
'''

dialogLEditCorrectStyle = '''
.QLineEdit{
    border: 1px solid grey
}
'''
dialogLabelErrorStyle = '''
.QLabel{
    color: red
}
'''
dialogLabelCorrectStyle = '''
.QLabel{
    color: black
}
'''
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
        self.gridLayout.addWidget(self.table,0,0,2,1)

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
        self.groupNameFrameLayout.addWidget(self.groupNameLabel,alignment=Qt.AlignTop)

        self.groupNameLEdit = QLineEdit()
        self.groupNameLEdit.setFixedSize(LEDIT_BTN_PATH_H_SIZE, LEDIT_BTN_V_SIZE)
        self.groupNameFrameLayout.addWidget(self.groupNameLEdit,alignment=Qt.AlignTop)

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
        self.addLineButton.setFixedSize(PUSH_BTN_H_SIZE,PUSH_BTN_V_SIZE)
        self.addLineFrameLayout.addWidget(self.addLineButton,alignment=Qt.AlignBottom)

        self.gridLayout.addWidget(self.addLineFrame,1,1,1,1,alignment=Qt.AlignBottom)

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
        self.table.setItemDelegateForColumn(0,self.tableCompleter)

        self.errorLabel = QLabel('')

        self.gridLayout.addWidget(self.errorLabel,2,0,1,1,alignment=Qt.AlignLeft)

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.buttonBox.button(QDialogButtonBox.Ok).setText('Save')
        self.buttonBox.button(QDialogButtonBox.Ok).setFixedSize(PUSH_BTN_H_SIZE,PUSH_BTN_V_SIZE)
        self.buttonBox.button(QDialogButtonBox.Cancel).setFixedSize(PUSH_BTN_H_SIZE, PUSH_BTN_V_SIZE)
        self.gridLayout.addWidget(self.buttonBox,2,1,1,1)


    def initTable(self):

        self.table.setRowCount(LIM_GROUPS_TABLE_ROWS)

        self.tableHeader.setSectionResizeMode(0, QHeaderView.Interactive)
        self.table.setColumnWidth(0, 320)
        self.table.setColumnWidth(1, 60)

        for i in range(LIM_GROUPS_TABLE_ROWS):
            comboBox = QComboBox()

            comboBox.addItems(['ExactMatch','Contains'])

            self.table.setCellWidget(i, 1, comboBox)
            self.comboList.append(comboBox)

            item = QTableWidgetItem()

            self.compListRowDict=dict()
            self.compListRowDict['completion_ls'] = self.completionList
            self.compListRowDict['row'] = None

            item.setData(Qt.UserRole,self.compListRowDict)  # set list

            self.table.setItem(i, 0, item)

    def addLine(self):
        nofRows = self.table.rowCount()

        row = nofRows

        self.table.insertRow(row)

        limitItem = QTableWidgetItem()
        matchItem = QTableWidgetItem()

        comboBox = QComboBox()

        comboBox.addItems(['ExactMatch','Contains'])

        self.table.setCellWidget(row, 1, comboBox)
        self.comboList.append(comboBox)

        self.compListRowDict = dict()
        self.compListRowDict['completion_ls'] = self.completionList
        self.compListRowDict['row'] = None

        limitItem.setData(Qt.UserRole, self.compListRowDict)  # set list
        self.table.setItem(row, 0, limitItem)

class TableItemCompleter(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        userRoleDict  = index.data(Qt.UserRole) # get list
        completion_ls = userRoleDict['completion_ls']
        completer = QCompleter(completion_ls, parent)
        editor.setCompleter(completer)
        return editor


statsGroupsSaveDialog = LimitsGroupsSaveDialog()


###

# Label function
def show_datapoints(sel):
    xi, yi = sel[0], sel[0]
    xi, yi = xi._xorig.tolist(), yi._yorig.tolist()
    sel.annotation.set_text('x: '+ str(xi[round(sel.target.index)])+\
            '\n'+'y: '+ str(yi[round(sel.target.index)]))

# interactive plot for statistics limits
class PlotFrame(QFrame):
    def __init__(self):
        super().__init__()
        self.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding)
        # self.setMaximumWidth(800)

        # self.layout = QVBoxLayout(self)
        self.layout = QGridLayout(self)
        self.layout.setVerticalSpacing(V_LAYOUT_SPACING)
        self.layout.setAlignment(Qt.AlignRight)
        self.setLayout(self.layout)

        self.figure = plt.figure(tight_layout=True)
        # self.figure = fig.Figure(figsize=(9,9))

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)

        self.layout.addWidget(self.canvas,0,0,1,1)

        # create an axis
        self.ax1 = self.figure.add_subplot(111)
        # control the size of the figure
        # self.figure.set_size_inches(12.5, 8.5)
        self.figure.set_size_inches(10.5, 20.5)

        self.ax1.grid(visible=True, which='major', axis='both')
        # self.ax1.grid(visible=True, color='black')

        # self.ax1 = self.figure.add_axes([0.1,0.1,0.8,0.8])
        # Set the x-axis label
        self.ax1.set_xlabel('Protocol index')
        # self.ax1.set_ylabel('Limit - ax1', color='blue')

        # # create an axis
        self.ax2 = self.ax1.twinx()
        self.ax2.grid(visible=True, which='major', axis='both', linestyle='--')
        # self.ax2.grid(b = True, color='red', linestyle='--')
        # # Set the x-axis label
        # self.ax2.set_xlabel('Protocol index')
        # self.ax2.set_ylabel('Limit - ax2', color ='red')
        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(self.canvas,self)
        # print(self.toolbar.edit_parameters.
        # self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.toolbar,1,0,1,1)

        # self.legendFigure = plt.figure()
        # self.legendCanvas = FigureCanvas(self.legendFigure)
        # self.layout.addWidget(self.legendCanvas, 0, 1, 2, 1)

        # self.layout.setColumnStretch(1,1)
        self.layout.setColumnStretch(0,1)

        self.patchList = []

        # self.patchList.append(mpatches.Patch(color='red', label='curveNamecurveName1212212'))
        # self.patchList.append(mpatches.Patch(color='blue', label='curveNamecurveName1212212'))
        # self.legendFigure.legend(handles=self.patchList, loc='upper left', ncol=2)

    def plot(self,protIndexList,plot_dat,graphIndex,limitName,protocol,ax):
        ylimits0 = []
        ylimits1 = []
        ylimitssec0 = []
        ylimitssec1 = []
        sensornameList = []
        for sensorlist in protocol:
            sensorname = sensorlist.replace('/','\\')
            sensornameList.append(sensorname)
        # sensornameList = protocol
        color = getGraphColor(graphIndex)

        # plot plot_dat
        if ax == 1:
            if plot_dat:
                lineax1 = self.ax1.plot(protIndexList, plot_dat, 'o-', color=color, label=limitName)
                c1 = mplcursors.cursor(lineax1)
                @c1.connect("add")
                def on_add(sel):
                    # sel.annotation.set_text(os.path.basename(sensornameList[round(sel.target.index)]).replace('_Protocol.txt', ''))
                    sel.annotation.arrow_patch.set(arrowstyle="simple", alpha=.00000005)
                    sel.annotation.set_text('')
                    print(sensornameList[round(sel.target.index)])
                mplcursors.cursor(self.ax1).connect('add',show_datapoints)
        else:
            if plot_dat:
                lineax2 = self.ax2.plot(protIndexList, plot_dat, 'o-', color=color, label=limitName)
                # self.ax2.legend(title='Legends', bbox_to_anchor=(0.5, 1.05), loc='upper center')
                self.ax2.legend(title='Legends', loc='upper right')
                c1 = mplcursors.cursor(lineax2)
                @c1.connect("add")
                def on_add(sel):
                    # label on interactive mode
                    # sel.annotation.set_text(os.path.basename(sensornameList[round(sel.target.index)]).replace('_Protocol.txt', ''))
                    sel.annotation.arrow_patch.set(arrowstyle="simple", alpha=.00000005)
                    sel.annotation.set_text('')
                    # Print the path of protocol file
                    print(sensornameList[round(sel.target.index)])
                mplcursors.cursor(self.ax2).connect('add',show_datapoints)

        # rescaling ax1
        for lineIndex in range(len(self.ax1.lines)):
            ylimits0.append(min(self.ax1.lines[lineIndex]._yorig))
            ylimits1.append(max(self.ax1.lines[lineIndex]._yorig))
        if len(ylimits0) !=0:
            if min(ylimits0) >= 5:
                ylimits0 = min(ylimits0) - 5
            elif min(ylimits0) < 5:
                ylimits0 = min(ylimits0) - 0.1
            if max(ylimits1) >= 5:
                ylimits1 = max(ylimits1) + 5
            elif max(ylimits1) < 5:
                ylimits1 = max(ylimits1) + 0.1
            self.ax1.set_ylim(ymin=ylimits0, ymax=ylimits1)

        # rescaling ax2
        for lineIndex in range(len(self.ax2.lines)):
            ylimitssec0.append(min(self.ax2.lines[lineIndex]._yorig))
            ylimitssec1.append(max(self.ax2.lines[lineIndex]._yorig))
        if len(ylimitssec0) != 0:
            if min(ylimitssec0) >= 5:
                ylimitssec0 = min(ylimitssec0) - 5
            elif min(ylimitssec0) < 5:
                ylimitssec0 = min(ylimitssec0) - 0.1
            if max(ylimitssec1) >= 5:
                ylimitssec1 = max(ylimitssec1) + 5
            elif max(ylimitssec1) < 5:
                ylimitssec1 = max(ylimitssec1) + 0.1
            self.ax2.set_ylim(ymin=ylimitssec0, ymax=ylimitssec1)
        
        # refresh canvas
        # self.ax1.legend(title='Legends', bbox_to_anchor=(1.1, 1), loc='upper left')
        if len(protIndexList) < 50:
            self.ax1.set_xticks(np.arange(min(protIndexList), max(protIndexList)+1, 1.0))
        self.ax1.legend(title='Legends', loc='upper left')
        self.canvas.draw()

    def clear(self, ax=0):

        if ax == 0:
            self.ax1.clear()
            self.ax2.clear()

            self.ax1.grid(visible=True, which='major', axis='both')
            self.ax2.grid(visible=True, which='major', axis='both', linestyle='--')

            self.ax1.set_xlabel('Protocol index')
            # self.ax1.set_ylabel('Limit - ax1', color ='blue')
            # self.ax2.set_ylabel('Limit - ax2',color ='red')
            # self.figure.clear()

        elif ax == 1:
            self.ax1.clear()
            # self.ax1.grid(visible=True, color='blue', linestyle=':')
            self.ax1.grid(visible=True, which = 'major', axis ='both')
        else:
            self.ax2.clear()
            # self.ax2.grid(b = True, color='red', linestyle=':')
            self.ax2.grid(visible=True, which='major', axis='both', linestyle='--')


        # self.ax1 = self.figure.add_subplot(111)
        # # Set the x-axis label
        # self.ax1.set_xlabel('Protocol index')
        # self.ax1.set_ylabel('Limit')

        # refresh canvas
        self.canvas.draw()


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

# interactive plot for Antenna System Diagrams
class PlotFrameSysDia(QFrame):
    def __init__(self):
        super().__init__()
        self.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding)

        self.layout = QGridLayout(self)
        self.layout.setVerticalSpacing(V_LAYOUT_SPACING)
        self.layout.setAlignment(Qt.AlignCenter)
        self.setLayout(self.layout)

        self.figure = plt.figure(tight_layout=True)
        self.figure.set_size_inches(18.5,16.5)
        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)

        # self.layout.addWidget(self.canvas,0,0,1,1)
        self.layout.addWidget(self.canvas,0,0,1,1)
        # create an axis
        self.ax1 = self.figure.add_subplot(111)

        self.ax1.grid(visible=True, which='major', axis='both')
        # self.ax1.grid(visible=True, color='black')

        # Set the x-axis label
        # self.ax1.set_xlabel('Protocol index')
        # self.ax1.set_ylabel('Limit - ax1', color='blue')

        # # create an axis
        self.ax2 = self.ax1.twinx()
        self.ax2.grid(visible=True, which='major', axis='both', linestyle='--')
        # self.ax2.grid(b = True, color='red', linestyle='--')
        # # Set the x-axis label
        # self.ax2.set_xlabel('Protocol index')
        # self.ax2.set_ylabel('Limit - ax2', color ='red')
        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(self.canvas,self)
        # self.layout.addWidget(self.toolbar,1,0,1,1)
        self.layout.addWidget(self.toolbar,1,0,1,1)

        # self.legendFigure = plt.figure()
        # self.legendCanvas = FigureCanvas(self.legendFigure)
        # self.layout.addWidget(self.legendCanvas, 0, 1, 2, 1)

        # self.layout.setColumnStretch(0,1.35)
        self.layout.setColumnStretch(1,1)
        self.layout.setRowStretch(1,1)


    def plot(self, angleData, plot_dat, Prot_param, graphType, idx, ax):
        ylimits0 = []
        ylimits1 = []
        ylimitssec0 = []
        ylimitssec1 = []
        # plot plot_dat
        if ax == 1:
            # label
            self.ax1.set_ylabel(plotdata.graphStringMapping(graphType))
            if plot_dat.size != 0:
                if 'idealPhaseDiff' in graphType:
                    lineax1 = self.ax1.plot(angleData, plot_dat, 'o-', color='olive', label=Prot_param)
                else:
                    lineax1 = self.ax1.plot(angleData, plot_dat, 'o-', label=Prot_param)
                scatter1 = self.ax1.scatter(angleData, plot_dat, color='none', s = 1.23E-7)
                c1 = mplcursors.cursor(lineax1)
                @c1.connect("add")
                def on_add(sel):
                    PTU = sel.artist.get_label().split('.txt')
                    PTUlabel = PTU[0]
                    # label on interactive mode
                    # sel.annotation.set_text(os.path.basename(sel.artist.get_label().replace('_PTU2.txt', '')))
                    sel.annotation.arrow_patch.set(arrowstyle='simple', alpha=.00000005)
                    sel.annotation.set_text('')
                    # Print the path of protocol file
                    print(str(PTUlabel) + '.txt')
                # exact data points will be shown in text box
                c2 = mplcursors.cursor(scatter1)
                @c2.connect("add")
                def on_add(sel):
                    # sel.annotation.set_text('{:.1f} {:.6f}'.format(sel.target[0], sel.target[1]))
                    sel.annotation.set_text('x: '+str(sel.target[0]) \
                        +'\ny: '+ str(sel.target[1]))
                # mplcursors.cursor(scatter1)
        else:
            # Label
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
                    # label on interactive mode
                    # sel.annotation.set_text(os.path.basename(sel.artist.get_label().replace('_PTU2.txt', '')))
                    sel.annotation.arrow_patch.set(arrowstyle='simple', alpha=.00000005)
                    sel.annotation.set_text('')
                    # Print the path of protocol file
                    print(str(PTUlabel) + '.txt')
                # exact data points will be shown in text box
                c2 = mplcursors.cursor(scatter2)
                @c2.connect("add")
                def on_add(sel):
                    sel.annotation.set_text('x: '+str(sel.target[0]) \
                        +'\ny: '+ str(sel.target[1]))

        # rescaling
        for lineIndex in range(len(self.ax1.lines)):
            ylimits0.append(min(self.ax1.lines[lineIndex]._yorig))
            ylimits1.append(max(self.ax1.lines[lineIndex]._yorig))
        if len(ylimits0) != 0:
            if min(ylimits0) >= 1:
                ylimits0 = min(ylimits0) - 10
            elif min(ylimits0) < 1:
                ylimits0 = min(ylimits0) - 5
            if max(ylimits1) >= 1:
                ylimits1 = max(ylimits1) + 10
            elif max(ylimits1) < 1:
                ylimits1 = max(ylimits1) + 5
            self.ax1.set_ylim(ymin=ylimits0, ymax=ylimits1)

        # rescaling
        for lineIndex in range(len(self.ax2.lines)):
            ylimitssec0.append(min(self.ax2.lines[lineIndex]._yorig))
            ylimitssec1.append(max(self.ax2.lines[lineIndex]._yorig))
        if len(ylimitssec0) != 0:
            if min(ylimitssec0) >= 1:
                ylimitssec0 = min(ylimitssec0) - 10
            elif min(ylimitssec0) < 1:
                ylimitssec0 = min(ylimitssec0) - 5
            if max(ylimitssec1) >= 1:
                ylimitssec1 = max(ylimitssec1) + 10
            elif max(ylimitssec1) < 1:
                ylimitssec1 = max(ylimitssec1) + 5
            self.ax2.set_ylim(ymin=ylimitssec0, ymax=ylimitssec1)
        # # refresh canvas
        self.canvas.draw()


    def clear(self, ax=0):

        if ax == 0:
            self.ax1.clear()
            self.ax2.clear()
            self.ax1.grid(visible=True, which='major', axis='both')
            self.ax2.grid(visible=True, which='major', axis='both', linestyle='--')

            # self.figure.clear()

        elif ax == 1:
            self.ax1.clear()
            self.ax1.grid(visible=True, which='major', axis='both')
        else:
            self.ax2.clear()
            self.ax2.grid(visible=True, which='major', axis='both', linestyle='--')


        # refresh canvas
        self.canvas.draw()

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
# Main Table Log Handler
class QTableLogHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.logTable = QTableWidget(0,3)
        # self.logTable.setReadOnly(True)

        # parseProtSelProtTable.setMinimumHeight(650)
        self.logTable.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.logTable.setHorizontalHeaderLabels(['Time', 'Level', 'Message'])
        # parseProtSelProtTable.setEditTriggers(QTableWidget.DoubleClicked)

        self.logTableHeader = self.logTable.horizontalHeader()
        self.logTableHeader.setSectionResizeMode(QHeaderView.Stretch)

        self.logTableRow = 0

    def emit(self, record):
        msgStr = str(record.msg)
        levelnameStr = str(record.levelname)

        timeStr   = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        timeMsStr = "%s,%03d" % (timeStr, record.msecs)
        # print(timeMsStr)

        levelItem = QTableWidgetItem(levelnameStr)
        if levelnameStr == 'NOTSET':
            levelItem.setBackground(QBrush(QColor('lightgrey')))
        elif levelnameStr == 'INFO':
            levelItem.setBackground(QBrush(QColor('lavender')))
        elif levelnameStr == 'DEBUG':
            levelItem.setBackground(QBrush(QColor('cyan')))
        elif levelnameStr == 'WARNING':
            levelItem.setBackground(QBrush(QColor('yellow')))
        elif levelnameStr == 'ERROR':
            levelItem.setBackground(QBrush(QColor('red')))
        elif levelnameStr == 'CRITICAL':
            levelItem.setBackground(QBrush(QColor('black')))
            levelItem.setForeground(QBrush(QColor('white')))

        # levelItem.setBackground(QColor(100, 100, 150))

        self.logTable.insertRow(self.logTableRow)
        self.logTable.setItem(self.logTableRow, 0, QTableWidgetItem(timeMsStr))
        self.logTable.setItem(self.logTableRow, 1, levelItem)
        self.logTable.setItem(self.logTableRow, 2, QTableWidgetItem(msgStr))

        self.logTableRow += 1

        # msg = self.format(record)

    def clearTable(self):

        self.logTable.clear()
        self.logTable.setRowCount(10)
        self.logTableRow = 0

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

