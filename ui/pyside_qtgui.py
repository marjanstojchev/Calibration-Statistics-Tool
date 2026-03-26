
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

