"""PST-60: Parse Protocols tab widget declarations."""
from __future__ import annotations

import os
import sys

# Ensure ui/ is on sys.path so ui_constants is importable
_ui_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ui_dir not in sys.path:
    sys.path.insert(0, _ui_dir)

from PySide6.QtWidgets import (
    QApplication, QFrame, QLabel, QPushButton, QWidget, QProgressBar,
    QTableWidget, QTableWidgetItem, QTabWidget, QGroupBox, QCheckBox,
    QHeaderView, QFileDialog, QComboBox, QRadioButton, QLineEdit,
    QDialog, QDialogButtonBox, QGraphicsDropShadowEffect, QButtonGroup,
    QStyledItemDelegate, QCompleter, QVBoxLayout, QHBoxLayout, QGridLayout,
    QSizePolicy,
)
from PySide6.QtGui import *
from PySide6.QtCore import *

from ui_constants import *

##
## Parse Protocols Tab
parseProtTab    = QWidget()
parseProtLayout = QGridLayout()
parseProtLayout.setHorizontalSpacing(H_LAYOUT_SPACING)
parseProtLayout.setVerticalSpacing(V_LAYOUT_SPACING)

parseProtLayout.setColumnStretch(0, 1)
parseProtLayout.setColumnStretch(1, 1)
parseProtLayout.setColumnStretch(2, 2)

parseProtLayout.setAlignment(Qt.AlignTop)

parseProtTab.setLayout(parseProtLayout)
parseProtTab.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
# Note: mainTabWidget.insertTab(0, parseProtTab, ...) is called in pyside_qtgui.py

### Parse Protocols Frame
###### Parse Data Frame
parseProtParseDataFrame = QFrame()
parseProtParseDataFrame.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
parseProtParseDataFrameLayout = QHBoxLayout()
parseProtParseDataFrameLayout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
parseProtParseDataFrameLayout.setSpacing(H_LAYOUT_SPACING)
parseProtParseDataFrame.setLayout(parseProtParseDataFrameLayout)

parseProtLayout.addWidget(parseProtParseDataFrame, 0, 0, 1, 2, alignment=Qt.AlignLeft | Qt.AlignTop)

#### Parse Protocols - Parse Data PushButton
parseProtParseDataPushBtn = QPushButton('Parse Data')
parseProtParseDataPushBtn.setObjectName('1')
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
parseProtParseDataFrameLayout = QHBoxLayout()
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
parseProtGroupBox = QGroupBox('Load Data')
parseProtGroupBox.setMinimumHeight(600)
parseProtGroupBox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
parseProtLayout.addWidget(parseProtGroupBox, 2, 0, 2, 1, alignment=Qt.AlignTop)

parseProtGroupBoxLayout = QHBoxLayout()
parseProtGroupBoxLayout.setSpacing(H_LAYOUT_SPACING)
parseProtGroupBoxLayout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
parseProtGroupBox.setLayout(parseProtGroupBoxLayout)

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
parseProtGroupBoxFrameLayout.addWidget(parseProtSysDiagCheckBox, stretch=0)

##### Parse Protocols TxAnt Diag. CheckBox
parseProtTxAntDiagCheckBox = QCheckBox('Search for Tx-Ant. Diag. Files')
parseProtTxAntDiagCheckBox.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
parseProtTxAntDiagCheckBox.setChecked(True)
parseProtGroupBoxFrameLayout.addWidget(parseProtTxAntDiagCheckBox, stretch=0)

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

##### Parse Protocols - Import Protocols - File List FileDialog
parseProtImportProtFListFDialog = QFileDialog()
parseProtImportProtFListFDialog.setFileMode(QFileDialog.ExistingFiles)
parseProtImportProtFListFDialog.setNameFilter("Protocols (*_Protocol.txt)")

##### Parse Protocols - Import Protocols - File Path FileDialog
parseProtImportProtDirPathFDialog = QFileDialog()
parseProtImportProtDirPathFDialog.setFileMode(QFileDialog.Directory)

#### Parse Protocols - Import Protocols - Directory PushButton
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

##### Parse Protocols - Add and Parse Separately Label
parseProtAddAndParseSepLabel = QLabel('Add and Parse Separately')
parseProtAddAndParseSepLabel.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
parseProtGroupBoxFrameLayout.addWidget(parseProtAddAndParseSepLabel, stretch=0)

#### Parse Protocols - Import PTU-2 Files PushButton
parseProtAddAndParsePtu2PushBtn = QPushButton('PTU-2 Files')
parseProtAddAndParsePtu2PushBtn.setFixedSize(PUSH_BTN_H_SIZE, PUSH_BTN_V_SIZE)
parseProtAddAndParsePtu2PushBtn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
parseProtGroupBoxFrameLayout.addWidget(parseProtAddAndParsePtu2PushBtn, stretch=0)

##### Parse Protocols - PTU-2 Files FileDialog
parseProtAddAndParsePtu2FDialog = QFileDialog()
parseProtAddAndParsePtu2FDialog.setFileMode(QFileDialog.ExistingFiles)
parseProtAddAndParsePtu2FDialog.setNameFilter("PTU-2 Files (*ptu2.txt)")

#### Parse Protocols - Import Tx-Ant. Diag. Files PushButton
parseProtAddAndParseTxAntDiagPushBtn = QPushButton('Tx-Ant. Diag. Files')
parseProtAddAndParseTxAntDiagPushBtn.setFixedSize(PUSH_BTN_H_SIZE, PUSH_BTN_V_SIZE)
parseProtAddAndParseTxAntDiagPushBtn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
parseProtGroupBoxFrameLayout.addWidget(parseProtAddAndParseTxAntDiagPushBtn, stretch=0)

parseProtAddAndParseTxAntDiagFDialog = QFileDialog()
parseProtAddAndParseTxAntDiagFDialog.setFileMode(QFileDialog.ExistingFiles)
parseProtAddAndParseTxAntDiagFDialog.setNameFilter("Tx-Ant. Diag. Files (*TxAnt*_Diagram*.txt)")

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

#####
parseProtSensorMusterLEdit = QLineEdit()
parseProtSensorMusterLEdit.setFixedSize(LEDIT_BTN_H_SIZE, LEDIT_BTN_V_SIZE)
parseProtSensorMusterLEdit.setPlaceholderText('(ex: rf dsp PT)')
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
parseProtLoadedProtLabel = QLabel(parseProtLoadedProtStr + '0')
parseProtGroupBoxStatsFrameLayout.addWidget(parseProtLoadedProtLabel)

#####
parseProtEolErrorStr   = parseProtTextTab + 'EOL Error(s): '
parseProtEolErrorLabel = QLabel(parseProtEolErrorStr + '0')
parseProtGroupBoxStatsFrameLayout.addWidget(parseProtEolErrorLabel)

#####
parseProtAbbortCritStr   = parseProtTextTab + 'EOL Abbort Criterion(s): '
parseProtAbbortCritLabel = QLabel(parseProtAbbortCritStr + '0')
parseProtGroupBoxStatsFrameLayout.addWidget(parseProtAbbortCritLabel)

#####
parseProtMeasLimitsExcStr   = parseProtTextTab + 'EOL Meas. Limits Exceeded: '
parseProtMeasLimitsExcLabel = QLabel(parseProtMeasLimitsExcStr + '0')
parseProtGroupBoxStatsFrameLayout.addWidget(parseProtMeasLimitsExcLabel)

####
parseProtHLine = QFrame()
parseProtHLine.setFixedHeight(H_LINE_HEIGHT)
parseProtHLine.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
parseProtHLine.setStyleSheet(lineStyle)
parseProtGroupBoxStatsFrameLayout.addWidget(parseProtHLine)

#####
parseProtParsedLoadedProtStr   = 'Parsed / Loaded Protocols: '
parseProtParsedLoadedProtLabel = QLabel(parseProtParsedLoadedProtStr + '0')
parseProtGroupBoxStatsFrameLayout.addWidget(parseProtParsedLoadedProtLabel)

#####
parseProtPtu2FilesStr   = parseProtTextTab + 'PTU-2 Files: '
parseProtPtu2FilesLabel = QLabel(parseProtPtu2FilesStr + '0')
parseProtGroupBoxStatsFrameLayout.addWidget(parseProtPtu2FilesLabel)

#####
parseProtTxAntDiagFilesStr   = parseProtTextTab + 'Tx-Antenna Diag. Files: '
parseProtTxAntDiagFilesLabel = QLabel(parseProtTxAntDiagFilesStr + '0')
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
parseProtSepParPtu2FilesStr   = parseProtTextTab + 'PTU-2 Files: '
parseProtSepParPtu2FilesLabel = QLabel(parseProtSepParPtu2FilesStr + '0')
parseProtGroupBoxStatsFrameLayout.addWidget(parseProtSepParPtu2FilesLabel)

#####
parseProtSepParTxAntDiagFilesStr   = parseProtTextTab + 'Tx-Antenna Diag. Files: '
parseProtSepParTxAntDiagFilesLabel = QLabel(parseProtSepParTxAntDiagFilesStr + '0')
parseProtGroupBoxStatsFrameLayout.addWidget(parseProtSepParTxAntDiagFilesLabel)


### Parse Protocols Data
parseProtProtDataGroupBox = QGroupBox('Protocols Data')
parseProtProtDataGroupBox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
parseProtProtDataGroupBox.setFixedWidth(210)
parseProtProtDataGroupBoxLayout = QVBoxLayout()
parseProtProtDataGroupBoxLayout.setSpacing(V_LAYOUT_SPACING)
parseProtProtDataGroupBoxLayout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
parseProtProtDataGroupBox.setLayout(parseProtProtDataGroupBoxLayout)
parseProtLayout.addWidget(parseProtProtDataGroupBox, 3, 1, 1, 1, alignment=Qt.AlignTop)

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

#####
parseProtProtDataBurnInGroupSelLabel = QLabel('Active Limits Group:')
parseProtProtDataBurnInLayout.addWidget(parseProtProtDataBurnInGroupSelLabel)

parseProtProtDataBurnInGroupSelComboBox = QComboBox()
parseProtProtDataBurnInGroupSelComboBox.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
parseProtProtDataBurnInGroupSelComboBox.setEnabled(False)
parseProtProtDataBurnInLayout.addWidget(parseProtProtDataBurnInGroupSelComboBox)

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

#####
parseProtProtDataCalGroupSelLabel = QLabel('Active Limits Group:')
parseProtProtDataCalLayout.addWidget(parseProtProtDataCalGroupSelLabel)

parseProtProtDataCalGroupSelComboBox = QComboBox()
parseProtProtDataCalGroupSelComboBox.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
parseProtProtDataCalGroupSelComboBox.setEnabled(False)
parseProtProtDataCalLayout.addWidget(parseProtProtDataCalGroupSelComboBox)


### Parse Protocols Status

#### Parse Protocols ProgresBar
parseProtProgresFrame = QFrame()
parseProtProgresFrame.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
parseProtLayout.addWidget(parseProtProgresFrame, 0, 2, 2, 2, alignment=Qt.AlignTop)

parseProtProgresFrameLayout = QHBoxLayout()
parseProtProgresFrameLayout.setSpacing(H_LAYOUT_SPACING)
parseProtProgresFrameLayout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
parseProtProgresFrame.setLayout(parseProtProgresFrameLayout)

parseProtProgresLabel = QLabel()
parseProtProgresLabel.setText('No protocols loaded.')
parseProtProgresLabel.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
parseProtProgresFrameLayout.addWidget(parseProtProgresLabel, stretch=3)

parseProtProgresBar = QProgressBar()
progBarFormatStr    = ''
parseProtProgresBar.setFixedWidth(PROGRESS_BAR_H_SIZE)
parseProtProgresBar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
parseProtProgresBar.setTextVisible(True)
parseProtProgresFrameLayout.addWidget(parseProtProgresBar, stretch=1)

### Parse Protocols Table Tab Widget
parseProtTableTabWidget = QTabWidget()
parseProtTableTabWidget.setMinimumHeight(600)
parseProtLayout.addWidget(parseProtTableTabWidget, 2, 2, 2, 1, alignment=Qt.AlignTop)
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

parseProtStatsTab = QWidget()
parseProtTableTabWidget.insertTab(4, parseProtStatsTab, 'Statistics Protocols')
parseProtStatsLayout = QVBoxLayout()
parseProtStatsTab.setLayout(parseProtStatsLayout)

#### Parse Protocols Selected Protocols Table Widget
parseProtSelProtTable = QTableWidget(PARSE_PROT_TABLE_ROWS, 4)
parseProtSelProtTable.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
parseProtSelProtTable.setHorizontalHeaderLabels(['Protocol', 'Imported as (Type)', 'PTU2 File Path', 'Tx-Ant Diagram File Path'])
parseProtSelProtLayout.addWidget(parseProtSelProtTable, stretch=1)
parseProtSelProtTableHeader = parseProtSelProtTable.horizontalHeader()
parseProtSelProtTable.setColumnWidth(1, 100)
parseProtSelProtTableHeader.setSectionResizeMode(QHeaderView.Stretch)

#### Parse Protocols Accepted Protocols Table Widget
parseProtAccProtTable = QTableWidget(PARSE_PROT_TABLE_ROWS, 4)
parseProtAccProtTable.setHorizontalHeaderLabels(['Protocol', 'Imported as (Type)', 'PTU2 File Path', 'Tx-Ant Diagram File Path'])
parseProtAccProtTable.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
parseProtAccProtLayout.addWidget(parseProtAccProtTable, stretch=2)
parseProtAccProtTableHeader = parseProtAccProtTable.horizontalHeader()
parseProtAccProtTable.setColumnWidth(1, 100)
parseProtAccProtTableHeader.setSectionResizeMode(QHeaderView.Stretch)

#### Parse Protocols PTU2 Files Table Widget
parseProtAddPtu2ParsedTable = QTableWidget(PARSE_PROT_TABLE_ROWS, 1)
parseProtAddPtu2ParsedTable.setHorizontalHeaderLabels(['Parsed PTU-2 Files'])
parseProtAddPtu2ParsedTable.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred)
parseProtAddPtu2Layout.addWidget(parseProtAddPtu2ParsedTable, stretch=5)
parseProtAddPtu2ParsedTableHeader = parseProtAddPtu2ParsedTable.horizontalHeader()
parseProtAddPtu2ParsedTableHeader.setSectionResizeMode(QHeaderView.Stretch)

#### Parse Protocols Failed PTU2 Files Table Widget
parseProtAddPtu2FailedTable = QTableWidget(PARSE_PROT_TABLE_ROWS, 1)
parseProtAddPtu2FailedTable.setHorizontalHeaderLabels(['Failed PTU-2 Files'])
parseProtAddPtu2FailedTable.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred)
parseProtAddPtu2Layout.addWidget(parseProtAddPtu2FailedTable, stretch=2)
parseProtAddPtu2FailedTableHeader = parseProtAddPtu2FailedTable.horizontalHeader()
parseProtAddPtu2FailedTableHeader.setSectionResizeMode(QHeaderView.Stretch)

#### Parse Protocols Tx Ant Diag Files Table Widget
parseProtAddTxAntDiagParsedTable = QTableWidget(PARSE_PROT_TABLE_ROWS, 1)
parseProtAddTxAntDiagParsedTable.setHorizontalHeaderLabels(['Parsed Tx-Ant. Diag. Files'])
parseProtAddTxAntDiagParsedTable.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
parseProtAddTxAntDiagLayout.addWidget(parseProtAddTxAntDiagParsedTable, stretch=5)
parseProtAddTxAntDiagTableHeader = parseProtAddTxAntDiagParsedTable.horizontalHeader()
parseProtAddTxAntDiagTableHeader.setSectionResizeMode(QHeaderView.Stretch)

#### Parse Protocols Failed Tx Ant Diag Files Table Widget
parseProtAddTxAntDiagFailedTable = QTableWidget(PARSE_PROT_TABLE_ROWS, 1)
parseProtAddTxAntDiagFailedTable.setHorizontalHeaderLabels(['Failed Tx-Ant. Diag. Files'])
parseProtAddTxAntDiagFailedTable.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
parseProtAddTxAntDiagLayout.addWidget(parseProtAddTxAntDiagFailedTable, stretch=2)
parseProtAddTxAntDiagFailedTableHeader = parseProtAddTxAntDiagFailedTable.horizontalHeader()
parseProtAddTxAntDiagFailedTableHeader.setSectionResizeMode(QHeaderView.Stretch)

#### Statistics - Parsed Protocols Table Widget
parseProtStatsParsedTable = QTableWidget(PARSE_PROT_TABLE_ROWS, 3)
parseProtStatsParsedTable.setHorizontalHeaderLabels(['Accepted Protocols', 'Imported as (Type)', 'Parsed as (Type)'])
parseProtStatsParsedTable.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
parseProtStatsLayout.addWidget(parseProtStatsParsedTable, stretch=5)
parseProtStatsParsedTableHeader = parseProtStatsParsedTable.horizontalHeader()
parseProtStatsParsedTableHeader.setSectionResizeMode(QHeaderView.Stretch)
parseProtStatsParsedTable.resizeColumnToContents(0)

#### Statistics - Failed Protocols Table Widget
parseProtStatsFailedTable = QTableWidget(PARSE_PROT_TABLE_ROWS, 3)
parseProtStatsFailedTable.setHorizontalHeaderLabels(['Failed Protocols', 'Imported as (Type)', 'Parsed as (Type)'])
parseProtStatsFailedTable.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
parseProtStatsLayout.addWidget(parseProtStatsFailedTable, stretch=2)
parseProtStatsFailedTableHeader = parseProtStatsFailedTable.horizontalHeader()
parseProtStatsFailedTableHeader.setSectionResizeMode(QHeaderView.Stretch)
parseProtStatsFailedTable.resizeColumnsToContents()
