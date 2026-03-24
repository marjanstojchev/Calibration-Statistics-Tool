"""PST-60: System Diagrams tab widget declarations."""
from __future__ import annotations

import os
import sys

_ui_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ui_dir not in sys.path:
    sys.path.insert(0, _ui_dir)

from PySide6.QtWidgets import (
    QFrame, QLabel, QPushButton, QWidget, QGroupBox, QCheckBox,
    QHeaderView, QComboBox, QRadioButton, QLineEdit, QButtonGroup,
    QVBoxLayout, QHBoxLayout, QGridLayout, QSizePolicy, QGraphicsDropShadowEffect,
)
from PySide6.QtGui import *
from PySide6.QtCore import *

from ui_constants import *

# ---------------------------------------------------------------------------
# Shadow effects (must be created after QApplication, i.e. during import)
# ---------------------------------------------------------------------------
shadowTwoGraphBig   = QGraphicsDropShadowEffect(blurRadius=8, xOffset=6, yOffset=6)
shadowTwoGraphSmall = QGraphicsDropShadowEffect(blurRadius=8, xOffset=6, yOffset=6)
shadowThreeGraph3   = QGraphicsDropShadowEffect(blurRadius=8, xOffset=6, yOffset=6)
shadowThreeGraph1   = QGraphicsDropShadowEffect(blurRadius=8, xOffset=6, yOffset=6)
shadowThreeGraph2   = QGraphicsDropShadowEffect(blurRadius=8, xOffset=6, yOffset=6)
shadowFourGraph00   = QGraphicsDropShadowEffect(blurRadius=8, xOffset=6, yOffset=6)
shadowFourGraph01   = QGraphicsDropShadowEffect(blurRadius=8, xOffset=6, yOffset=6)
shadowFourGraph10   = QGraphicsDropShadowEffect(blurRadius=8, xOffset=6, yOffset=6)
shadowFourGraph11   = QGraphicsDropShadowEffect(blurRadius=8, xOffset=6, yOffset=6)

##
## System Diagrams Tab
sysDiagTab    = QWidget()
sysDiagLayout = QGridLayout()
sysDiagLayout.setHorizontalSpacing(H_LAYOUT_SPACING)
sysDiagLayout.setVerticalSpacing(V_LAYOUT_SPACING)
sysDiagTab.setLayout(sysDiagLayout)
# Note: mainTabWidget.insertTab(1, sysDiagTab, ...) is called in pyside_qtgui.py

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
sysDiagInputSetupLayout.setHorizontalSpacing(H_LAYOUT_SPACING)
sysDiagInputSetupLayout.setVerticalSpacing(V_LAYOUT_SPACING)

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

sysDiagInputSetupDiagConfigDesRangeRegExp = QRegularExpression(r'^\d{0,3}(,\d{0,3})*$')
sysDiagInputSetupDiagConfigDesRangeRegExpValidator = QRegularExpressionValidator(sysDiagInputSetupDiagConfigDesRangeRegExp)

sysDiagInputSetupDiagConfigDesListLEdit = QLineEdit()
sysDiagInputSetupDiagConfigDesListLEdit.setValidator(sysDiagInputSetupDiagConfigDesRangeRegExpValidator)
sysDiagInputSetupDiagConfigLayout.addWidget(sysDiagInputSetupDiagConfigDesListLEdit, sysDiagInputSetupDiagConfigRowIdx, sysDiagInputSetupDiagConfigColIdx)

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
sysDiagInputSetupDiagConfigDesRangeHighLEdit.setFixedSize(LEDIT_BTN_H_SIZE, LEDIT_BTN_V_SIZE)
sysDiagInputSetupDiagConfigDesRangeHighLEdit.setValidator(sysDiagInputSetupDiagConfigDesRangeIntValidator)
sysDiagInputSetupDiagConfigDesRangeHighLEdit.setMaxLength(3)
sysDiagInputSetupDiagConfigLayout.addWidget(sysDiagInputSetupDiagConfigDesRangeHighLEdit, sysDiagInputSetupDiagConfigRowIdx, sysDiagInputSetupDiagConfigColIdx)

#####
sysDiagInputSetupDiagConfigRowIdx  = 1
sysDiagInputSetupDiagConfigColIdx += 1

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
sysDiagPlotSetupGropBox.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)

sysDiagPlotSetupLayout = QHBoxLayout()
sysDiagPlotSetupLayout.setSpacing(H_LAYOUT_SPACING)

sysDiagPlotSetupGropBox.setLayout(sysDiagPlotSetupLayout)

sysDiagLayout.addWidget(sysDiagPlotSetupGropBox, sysDiagRowIdx, sysDiagColIdx)

#### Plot Setup Frame

sysDiagPlotSetupFrame = QFrame()
sysDiagPlotSetupFrame.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
sysDiagPlotSetupLayout.addWidget(sysDiagPlotSetupFrame, stretch=1)

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
sysDiagPlotSetupScriptModeGroup.addButton(sysDiagPlotSetupScriptModeRadio1, 0)
sysDiagPlotSetupFrameLayout.addWidget(sysDiagPlotSetupScriptModeRadio1)

sysDiagPlotSetupScriptModeRadio2 = QRadioButton('Plot Window')
sysDiagPlotSetupScriptModeGroup.addButton(sysDiagPlotSetupScriptModeRadio2, 1)
sysDiagPlotSetupFrameLayout.addWidget(sysDiagPlotSetupScriptModeRadio2)

#####
sysDiagPlotSetupHLine = QFrame()
sysDiagPlotSetupHLine.setFixedHeight(H_LINE_HEIGHT)
sysDiagPlotSetupHLine.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
sysDiagPlotSetupHLine.setStyleSheet(lineStyle)
sysDiagPlotSetupFrameLayout.addWidget(sysDiagPlotSetupHLine)

#####
sysDiagPlotSetupImgGenGroup = QButtonGroup()

sysDiagPlotSetupImgGenLabel = QLabel('Image Generation mode')
sysDiagPlotSetupFrameLayout.addWidget(sysDiagPlotSetupImgGenLabel)

sysDiagPlotSetupImgGenRadio1 = QRadioButton('Rx-Channel')
sysDiagPlotSetupImgGenRadio1.setChecked(True)
sysDiagPlotSetupImgGenGroup.addButton(sysDiagPlotSetupImgGenRadio1, 0)
sysDiagPlotSetupFrameLayout.addWidget(sysDiagPlotSetupImgGenRadio1)

sysDiagPlotSetupImgGenRadio2 = QRadioButton('Diagram Number')
sysDiagPlotSetupImgGenGroup.addButton(sysDiagPlotSetupImgGenRadio2, 1)
sysDiagPlotSetupFrameLayout.addWidget(sysDiagPlotSetupImgGenRadio2)

#####
sysDiagPlotSetupHLine = QFrame()
sysDiagPlotSetupHLine.setFixedHeight(H_LINE_HEIGHT)
sysDiagPlotSetupHLine.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
sysDiagPlotSetupHLine.setStyleSheet(lineStyle)
sysDiagPlotSetupFrameLayout.addWidget(sysDiagPlotSetupHLine)

#####
sysDiagPlotSetup3GraphLayoutImgCheckBox = QCheckBox('3-Graph Layout Images')
sysDiagPlotSetup3GraphLayoutImgCheckBox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
sysDiagPlotSetup3GraphLayoutImgCheckBox.setChecked(True)
sysDiagPlotSetupFrameLayout.addWidget(sysDiagPlotSetup3GraphLayoutImgCheckBox)

#####
sysDiagPlotSetupHLine = QFrame()
sysDiagPlotSetupHLine.setFixedHeight(H_LINE_HEIGHT)
sysDiagPlotSetupHLine.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
sysDiagPlotSetupHLine.setStyleSheet(lineStyle)
sysDiagPlotSetupFrameLayout.addWidget(sysDiagPlotSetupHLine)

#####
sysDiagPlotSetupImageDpiIntValidator = QIntValidator()
sysDiagPlotSetupImageDpiIntValidator.setRange(0, 500)

sysDiagPlotSetupImageDpiLabel = QLabel('Image DPI:')
sysDiagPlotSetupFrameLayout.addWidget(sysDiagPlotSetupImageDpiLabel)

sysDiagPlotSetupImageDpiLEdit = QLineEdit()
sysDiagPlotSetupImageDpiLEdit.setValidator(sysDiagPlotSetupImageDpiIntValidator)
sysDiagPlotSetupImageDpiLEdit.setMaxLength(3)
sysDiagPlotSetupImageDpiLEdit.setFixedSize(LEDIT_BTN_H_SIZE, LEDIT_BTN_V_SIZE)
sysDiagPlotSetupImageDpiLEdit.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
sysDiagPlotSetupFrameLayout.addWidget(sysDiagPlotSetupImageDpiLEdit)

####
sysDiagPlotSetupVLine = QFrame()
sysDiagPlotSetupVLine.setFixedWidth(V_LINE_WIDTH)
sysDiagPlotSetupVLine.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.MinimumExpanding)
sysDiagPlotSetupVLine.setStyleSheet(lineStyle)
sysDiagPlotSetupLayout.addWidget(sysDiagPlotSetupVLine)

#### Plot Setup Scaling Frame
sysDiagPlotSetupScalingFrame = QFrame()
sysDiagPlotSetupScalingLayout = QVBoxLayout()
sysDiagPlotSetupScalingLayout.setSpacing(V_LAYOUT_SPACING)
sysDiagPlotSetupScalingLayout.setAlignment(Qt.AlignTop)
sysDiagPlotSetupScalingFrame.setLayout(sysDiagPlotSetupScalingLayout)
sysDiagPlotSetupLayout.addWidget(sysDiagPlotSetupScalingFrame, stretch=1)

#####
sysDiagPlotSetupScalingAutoCheckBox = QCheckBox('X-Scale Autoscale')
sysDiagPlotSetupScalingAutoCheckBox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
sysDiagPlotSetupScalingLayout.addWidget(sysDiagPlotSetupScalingAutoCheckBox)

#####
sysDiagPlotSetupScalingXScaleIntValidator = QIntValidator()
sysDiagPlotSetupScalingXScaleIntValidator.setRange(0, 150)

#####
sysDiagPlotSetupScalingXScaleAzLabel = QLabel('X-Scale Azimuth:')
sysDiagPlotSetupScalingLayout.addWidget(sysDiagPlotSetupScalingXScaleAzLabel)

sysDiagPlotSetupScalingXScaleAzLEdit = QLineEdit()
sysDiagPlotSetupScalingXScaleAzLEdit.setValidator(sysDiagPlotSetupScalingXScaleIntValidator)
sysDiagPlotSetupScalingXScaleAzLEdit.setMaxLength(3)
sysDiagPlotSetupScalingXScaleAzLEdit.setFixedSize(LEDIT_BTN_H_SIZE, LEDIT_BTN_V_SIZE)
sysDiagPlotSetupScalingXScaleAzLEdit.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
sysDiagPlotSetupScalingLayout.addWidget(sysDiagPlotSetupScalingXScaleAzLEdit)

#####
sysDiagPlotSetupScalingXScaleElLabel = QLabel('X-Scale Elevation:')
sysDiagPlotSetupScalingLayout.addWidget(sysDiagPlotSetupScalingXScaleElLabel)

sysDiagPlotSetupScalingXScaleElLEdit = QLineEdit()
sysDiagPlotSetupScalingXScaleElLEdit.setValidator(sysDiagPlotSetupScalingXScaleIntValidator)
sysDiagPlotSetupScalingXScaleElLEdit.setMaxLength(3)
sysDiagPlotSetupScalingXScaleElLEdit.setFixedSize(LEDIT_BTN_H_SIZE, LEDIT_BTN_V_SIZE)
sysDiagPlotSetupScalingXScaleElLEdit.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
sysDiagPlotSetupScalingLayout.addWidget(sysDiagPlotSetupScalingXScaleElLEdit)

#####
sysDiagPlotSetupHLine = QFrame()
sysDiagPlotSetupHLine.setFixedHeight(H_LINE_HEIGHT)
sysDiagPlotSetupHLine.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
sysDiagPlotSetupHLine.setStyleSheet(lineStyle)
sysDiagPlotSetupScalingLayout.addWidget(sysDiagPlotSetupHLine)

#####
sysDiagPlotSetupScalingYLimitsGroup = QButtonGroup()

sysDiagPlotSetupScalingYLimitsLabel = QLabel('Y-Limits Yield')
sysDiagPlotSetupScalingLayout.addWidget(sysDiagPlotSetupScalingYLimitsLabel)

sysDiagPlotSetupScalingYLimitRadio1 = QRadioButton('Per Antenna-Type')
sysDiagPlotSetupScalingYLimitRadio1.setChecked(True)
sysDiagPlotSetupScalingYLimitsGroup.addButton(sysDiagPlotSetupScalingYLimitRadio1, 0)
sysDiagPlotSetupScalingLayout.addWidget(sysDiagPlotSetupScalingYLimitRadio1)

sysDiagPlotSetupScalingYLimitRadio2 = QRadioButton('All Antenna-Types')
sysDiagPlotSetupScalingYLimitsGroup.addButton(sysDiagPlotSetupScalingYLimitRadio2, 1)
sysDiagPlotSetupScalingLayout.addWidget(sysDiagPlotSetupScalingYLimitRadio2)

#####
sysDiagPlotSetupHLine = QFrame()
sysDiagPlotSetupHLine.setFixedHeight(H_LINE_HEIGHT)
sysDiagPlotSetupHLine.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
sysDiagPlotSetupHLine.setStyleSheet(lineStyle)
sysDiagPlotSetupScalingLayout.addWidget(sysDiagPlotSetupHLine)

#####
sysDiagPlotSetupScalingDiffPhDiffDoubleValidator = QDoubleValidator()

#####
sysDiagPlotSetupScalingDiffPhDiffLabel = QLabel('Diff. Phase Diff. Scaling Factor:')
sysDiagPlotSetupScalingLayout.addWidget(sysDiagPlotSetupScalingDiffPhDiffLabel)

sysDiagPlotSetupScalingDiffPhDiffLEdit = QLineEdit()
sysDiagPlotSetupScalingDiffPhDiffLEdit.setValidator(sysDiagPlotSetupScalingDiffPhDiffDoubleValidator)
sysDiagPlotSetupScalingDiffPhDiffLEdit.setFixedSize(LEDIT_BTN_H_SIZE, LEDIT_BTN_V_SIZE)
sysDiagPlotSetupScalingDiffPhDiffLEdit.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
sysDiagPlotSetupScalingLayout.addWidget(sysDiagPlotSetupScalingDiffPhDiffLEdit)

####
sysDiagPlotSetupVLine = QFrame()
sysDiagPlotSetupVLine.setFixedWidth(V_LINE_WIDTH)
sysDiagPlotSetupVLine.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.MinimumExpanding)
sysDiagPlotSetupVLine.setStyleSheet(lineStyle)
sysDiagPlotSetupLayout.addWidget(sysDiagPlotSetupVLine)

#### Graph Configuration Frame
sysDiagPlotSetupGraphConfFrame = QFrame()
sysDiagPlotSetupLayout.addWidget(sysDiagPlotSetupGraphConfFrame, stretch=1)
sysDiagPlotSetupGraphConfLayout = QVBoxLayout()
sysDiagPlotSetupGraphConfLayout.setAlignment(Qt.AlignTop)
sysDiagPlotSetupGraphConfLayout.setSpacing(V_LAYOUT_SPACING)
sysDiagPlotSetupGraphConfFrame.setLayout(sysDiagPlotSetupGraphConfLayout)

#####
sysDiagPlotSetupGraphConfLabel = QLabel('Graph Configuration')
sysDiagPlotSetupGraphConfLayout.addWidget(sysDiagPlotSetupGraphConfLabel)

graphConfig = {
    "level": 0,
    "avgLevel": 0,
    "normLevel": 0,
    "avgNormLevel": 0,
    "phaseDiff": 0,
    "avgPhaseDiff": 0,
    "diffPhaseDiff": 1,
    "avgDiffPhaseDiff": 0,
    "corrPhaseDiff": 0,
}


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


def boolMapping(value):
    if isinstance(value, bool):
        return 1 if value else 0
    elif isinstance(value, int):
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

_id = 0
for _key, _val in graphConfig.items():
    sysDiagPlotSetupGraphConfCheckBox = QCheckBox(graphStringMapping(_key))
    sysDiagPlotSetupGraphConfLayout.addWidget(sysDiagPlotSetupGraphConfCheckBox)
    sysDiagPlotSetupGraphConfGroup.addButton(sysDiagPlotSetupGraphConfCheckBox, _id)
    _id += 1

#####
sysDiagPlotSetupHLine = QFrame()
sysDiagPlotSetupHLine.setFixedHeight(H_LINE_HEIGHT)
sysDiagPlotSetupHLine.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
sysDiagPlotSetupHLine.setStyleSheet(lineStyle)
sysDiagPlotSetupGraphConfLayout.addWidget(sysDiagPlotSetupHLine)

#####
sysDiagPlotSetupGraphConfIdealCurveCheckBox = QCheckBox('Diff. Ph. Diff. Ideal Curve')
sysDiagPlotSetupGraphConfLayout.addWidget(sysDiagPlotSetupGraphConfIdealCurveCheckBox)


### Plot Window Configuration GroupBox
plotWindowConfigGraphList = [
    "level", "avgLevel", "normLevel", "avgNormLevel",
    "phaseDiff", "avgPhaseDiff", "diffPhaseDiff", "avgDiffPhaseDiff", "corrPhaseDiff",
]
sysDiagColIdx += 1

sysDiagPlotWindowGroupBox = QGroupBox('Plot Window Configuration')
sysDiagPlotWindowGroupBox.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)
sysDiagPlotWindowLayout = QHBoxLayout()
sysDiagPlotWindowLayout.setSpacing(H_LAYOUT_SPACING)
sysDiagPlotWindowLayout.setAlignment(Qt.AlignTop)
sysDiagPlotWindowGroupBox.setLayout(sysDiagPlotWindowLayout)
sysDiagLayout.addWidget(sysDiagPlotWindowGroupBox, sysDiagRowIdx, sysDiagColIdx)

sysDiagPlotWindowGeneralFrame  = QFrame()
sysDiagPlotWindowGeneralLayout = QVBoxLayout()
sysDiagPlotWindowGeneralLayout.setSpacing(H_LAYOUT_SPACING)
sysDiagPlotWindowGeneralLayout.setAlignment(Qt.AlignTop)
sysDiagPlotWindowGeneralFrame.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
sysDiagPlotWindowGeneralFrame.setLayout(sysDiagPlotWindowGeneralLayout)
sysDiagPlotWindowLayout.addWidget(sysDiagPlotWindowGeneralFrame, stretch=1)

#####
sysDiagPlotWindowInputModeLabel = QLabel('Input Mode')
sysDiagPlotWindowInputModeLabel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
sysDiagPlotWindowGeneralLayout.addWidget(sysDiagPlotWindowInputModeLabel, stretch=1)

sysDiagPlotWindowInputModeGroup = QButtonGroup()

sysDiagPlotWindowInputModeRadio1 = QRadioButton('Data')
sysDiagPlotWindowGeneralLayout.addWidget(sysDiagPlotWindowInputModeRadio1)
sysDiagPlotWindowInputModeGroup.addButton(sysDiagPlotWindowInputModeRadio1, 0)

sysDiagPlotWindowInputModeRadio2 = QRadioButton('String')
sysDiagPlotWindowGeneralLayout.addWidget(sysDiagPlotWindowInputModeRadio2)
sysDiagPlotWindowInputModeGroup.addButton(sysDiagPlotWindowInputModeRadio2, 1)

sysDiagPlotWindowInputModeLEdit = QLineEdit()
sysDiagPlotWindowInputModeLEdit.setFixedSize(LEDIT_BTN_H_SIZE, LEDIT_BTN_V_SIZE)
sysDiagPlotWindowInputModeLEdit.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
sysDiagPlotWindowGeneralLayout.addWidget(sysDiagPlotWindowInputModeLEdit)

sysDiagPlotWindowHLine = QFrame()
sysDiagPlotWindowHLine.setFixedHeight(H_LINE_HEIGHT)
sysDiagPlotWindowHLine.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
sysDiagPlotWindowHLine.setStyleSheet(lineStyle)
sysDiagPlotWindowGeneralLayout.addWidget(sysDiagPlotWindowHLine)

#####
sysDiagPlotWindowGraphTypeLabel = QLabel('Graph Type')
sysDiagPlotWindowGraphTypeLabel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
sysDiagPlotWindowGeneralLayout.addWidget(sysDiagPlotWindowGraphTypeLabel, stretch=1)

sysDiagPlotWindowGraphTypeComboBox = QComboBox()
sysDiagPlotWindowGeneralLayout.addWidget(sysDiagPlotWindowGraphTypeComboBox)
sysDiagPlotWindowGraphTypeComboBox.setEditText(plotWindowConfigGraphList[0])
sysDiagPlotWindowGraphTypeComboBox.addItems(plotWindowConfigGraphList)
sysDiagPlotWindowGraphTypeComboBox.setCurrentIndex(0)

#####
sysDiagPlotWindowAntTypLabel = QLabel('Antenna Type')
sysDiagPlotWindowAntTypLabel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
sysDiagPlotWindowGeneralLayout.addWidget(sysDiagPlotWindowAntTypLabel, stretch=1)

sysDiagPlotWindowAntTypValidator = QIntValidator()
sysDiagPlotWindowAntTypValidator.setRange(0, 999)
sysDiagPlotWindowAntTypLEdit = QLineEdit()
sysDiagPlotWindowAntTypLEdit.setValidator(sysDiagPlotWindowAntTypValidator)
sysDiagPlotWindowAntTypLEdit.setMaxLength(3)
sysDiagPlotWindowAntTypLEdit.setFixedSize(LEDIT_BTN_H_SIZE, LEDIT_BTN_V_SIZE)
sysDiagPlotWindowAntTypLEdit.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
sysDiagPlotWindowGeneralLayout.addWidget(sysDiagPlotWindowAntTypLEdit)

#####
sysDiagPlotWindowDiagNumLabel = QLabel('Diagram Number')
sysDiagPlotWindowDiagNumLabel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
sysDiagPlotWindowGeneralLayout.addWidget(sysDiagPlotWindowDiagNumLabel, stretch=1)

sysDiagPlotWindowDiagNumValidator = QIntValidator()
sysDiagPlotWindowDiagNumValidator.setRange(0, 200)
sysDiagPlotWindowDiagNumLEdit = QLineEdit()
sysDiagPlotWindowDiagNumLEdit.setValidator(sysDiagPlotWindowDiagNumValidator)
sysDiagPlotWindowDiagNumLEdit.setMaxLength(3)
sysDiagPlotWindowDiagNumLEdit.setFixedSize(LEDIT_BTN_H_SIZE, LEDIT_BTN_V_SIZE)
sysDiagPlotWindowDiagNumLEdit.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
sysDiagPlotWindowGeneralLayout.addWidget(sysDiagPlotWindowDiagNumLEdit)

#####
sysDiagPlotWindowRxChLabel = QLabel('Rx-Channel')
sysDiagPlotWindowRxChLabel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
sysDiagPlotWindowGeneralLayout.addWidget(sysDiagPlotWindowRxChLabel, stretch=1)

sysDiagPlotWindowRxChValidator = QIntValidator()
sysDiagPlotWindowRxChValidator.setRange(0, 11)
sysDiagPlotWindowRxChLEdit = QLineEdit()
sysDiagPlotWindowRxChLEdit.setValidator(sysDiagPlotSetupImageDpiIntValidator)
sysDiagPlotWindowRxChLEdit.setMaxLength(2)
sysDiagPlotWindowRxChLEdit.setFixedSize(LEDIT_BTN_H_SIZE, LEDIT_BTN_V_SIZE)
sysDiagPlotWindowRxChLEdit.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
sysDiagPlotWindowGeneralLayout.addWidget(sysDiagPlotWindowRxChLEdit)

####
sysDiagPlotWindowVLine = QFrame()
sysDiagPlotWindowVLine.setFixedWidth(V_LINE_WIDTH)
sysDiagPlotWindowVLine.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.MinimumExpanding)
sysDiagPlotWindowVLine.setStyleSheet(lineStyle)
sysDiagPlotWindowLayout.addWidget(sysDiagPlotWindowVLine)

#####
sysDiagPlotWindowAllGraphsFrame  = QFrame()
sysDiagPlotWindowAllGraphsLayout = QVBoxLayout()
sysDiagPlotWindowAllGraphsLayout.setSpacing(V_LAYOUT_SPACING)
sysDiagPlotWindowAllGraphsLayout.setAlignment(Qt.AlignTop)
sysDiagPlotWindowAllGraphsFrame.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
sysDiagPlotWindowAllGraphsFrame.setLayout(sysDiagPlotWindowAllGraphsLayout)
sysDiagPlotWindowLayout.addWidget(sysDiagPlotWindowAllGraphsFrame, stretch=1)

#####
sysDiagPlotWindowAllGraphsCheckBox = QCheckBox('All Graphs Mode')
sysDiagPlotWindowAllGraphsCheckBox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
sysDiagPlotWindowAllGraphsCheckBox.setChecked(False)
sysDiagPlotWindowAllGraphsLayout.addWidget(sysDiagPlotWindowAllGraphsCheckBox)

sysDiagPlotWindowAllGraphsCheckBox1 = QCheckBox('Graph 1')
sysDiagPlotWindowAllGraphsCheckBox1.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
sysDiagPlotWindowAllGraphsCheckBox1.setChecked(True)
sysDiagPlotWindowAllGraphsLayout.addWidget(sysDiagPlotWindowAllGraphsCheckBox1)

sysDiagPlotWindowAllGraphsComboBox1 = QComboBox()
sysDiagPlotWindowAllGraphsComboBox1.addItems(plotWindowConfigGraphList)
sysDiagPlotWindowAllGraphsComboBox1.setCurrentIndex(0)
sysDiagPlotWindowAllGraphsLayout.addWidget(sysDiagPlotWindowAllGraphsComboBox1)

sysDiagPlotWindowAllGraphsCheckBox2 = QCheckBox('Graph 2')
sysDiagPlotWindowAllGraphsCheckBox2.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
sysDiagPlotWindowAllGraphsCheckBox2.setChecked(True)
sysDiagPlotWindowAllGraphsLayout.addWidget(sysDiagPlotWindowAllGraphsCheckBox2)

sysDiagPlotWindowAllGraphsComboBox2 = QComboBox()
sysDiagPlotWindowAllGraphsComboBox2.addItems(plotWindowConfigGraphList)
sysDiagPlotWindowAllGraphsComboBox2.setCurrentIndex(8)
sysDiagPlotWindowAllGraphsLayout.addWidget(sysDiagPlotWindowAllGraphsComboBox2)

sysDiagPlotWindowAllGraphsCheckBox3 = QCheckBox('Graph 3')
sysDiagPlotWindowAllGraphsCheckBox3.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
sysDiagPlotWindowAllGraphsCheckBox3.setChecked(True)
sysDiagPlotWindowAllGraphsLayout.addWidget(sysDiagPlotWindowAllGraphsCheckBox3)

sysDiagPlotWindowAllGraphsComboBox3 = QComboBox()
sysDiagPlotWindowAllGraphsComboBox3.addItems(plotWindowConfigGraphList)
sysDiagPlotWindowAllGraphsComboBox3.setCurrentIndex(6)
sysDiagPlotWindowAllGraphsLayout.addWidget(sysDiagPlotWindowAllGraphsComboBox3)


#### Slide Conf GroupBox
sysDiagRowIdx += 1
sysDiagColIdx  = 0

sysDiagSlideConfGroupBox = QGroupBox('Slide Configuration')
sysDiagSlideConfGroupBox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.MinimumExpanding)
sysDiagSlideConfLayout = QHBoxLayout()
sysDiagSlideConfLayout.setSpacing(H_LAYOUT_SPACING)
sysDiagSlideConfLayout.setAlignment(Qt.AlignTop)
sysDiagSlideConfGroupBox.setLayout(sysDiagSlideConfLayout)
sysDiagLayout.addWidget(sysDiagSlideConfGroupBox, sysDiagRowIdx, sysDiagColIdx, 1, 3)


#### Slide Configuration - Two-Graph Frame
sysDiagSlideConfTwoGraphFrame = QFrame()
sysDiagSlideConfLayout.addWidget(sysDiagSlideConfTwoGraphFrame)
sysDiagSlideConfTwoGraphLayout = QHBoxLayout()
sysDiagSlideConfTwoGraphLayout.setSpacing(H_LAYOUT_SPACING)
sysDiagSlideConfTwoGraphLayout.setAlignment(Qt.AlignTop)
sysDiagSlideConfTwoGraphFrame.setLayout(sysDiagSlideConfTwoGraphLayout)
sysDiagSlideConfTwoGraphFrame.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)

#####
sysDiagSlideConfTwoGraphGraphicFrame  = QFrame()
sysDiagSlideConfTwoGraphGraphicLayout = QGridLayout()
sysDiagSlideConfTwoGraphGraphicLayout.setVerticalSpacing(V_LAYOUT_SPACING)
sysDiagSlideConfTwoGraphGraphicLayout.setHorizontalSpacing(H_LAYOUT_SPACING)
sysDiagSlideConfTwoGraphGraphicLayout.setAlignment(Qt.AlignVCenter)
sysDiagSlideConfTwoGraphGraphicFrame.setLayout(sysDiagSlideConfTwoGraphGraphicLayout)
sysDiagSlideConfTwoGraphGraphicFrame.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)

sysDiagSlideConfTwoGraphLabel = QLabel('Two - Graph Layout')
sysDiagSlideConfTwoGraphLabel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
sysDiagSlideConfTwoGraphGraphicLayout.addWidget(sysDiagSlideConfTwoGraphLabel, 0, 0, 1, 2)

sysDiagSlideConfTwoGraphBigFrame = QFrame()
sysDiagSlideConfTwoGraphBigFrame.setObjectName('TwoGraphBig')
sysDiagSlideConfTwoGraphBigFrame.setStyleSheet(slideSymbolStyle)
sysDiagSlideConfTwoGraphBigFrame.setFixedSize(80, 60)
sysDiagSlideConfTwoGraphBigFrame.setGraphicsEffect(shadowTwoGraphBig)
sysDiagSlideConfTwoGraphBigFrame.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
sysDiagSlideConfTwoGraphGraphicLayout.addWidget(sysDiagSlideConfTwoGraphBigFrame, 1, 0, 1, 1)

sysDiagSlideConfTwoGraphSmallFrame = QFrame()
sysDiagSlideConfTwoGraphSmallFrame.setObjectName('TwoGraphSmall')
sysDiagSlideConfTwoGraphSmallFrame.setStyleSheet(slideSymbolStyle)
sysDiagSlideConfTwoGraphSmallFrame.setFixedSize(60, 45)
sysDiagSlideConfTwoGraphSmallFrame.setGraphicsEffect(shadowTwoGraphSmall)
sysDiagSlideConfTwoGraphSmallFrame.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
sysDiagSlideConfTwoGraphGraphicLayout.addWidget(sysDiagSlideConfTwoGraphSmallFrame, 1, 1, 1, 1)

sysDiagSlideConfTwoGraphLayout.addWidget(sysDiagSlideConfTwoGraphGraphicFrame, stretch=1)

##### Subframe1
sysDiagSlideConfTwoGraphSubFrame1 = QFrame()
sysDiagSlideConfTwoGraphSubFrame1Layout = QVBoxLayout()
sysDiagSlideConfTwoGraphSubFrame1Layout.setSpacing(V_LAYOUT_SPACING)
sysDiagSlideConfTwoGraphSubFrame1Layout.setAlignment(Qt.AlignTop)
sysDiagSlideConfTwoGraphSubFrame1.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
sysDiagSlideConfTwoGraphSubFrame1.setLayout(sysDiagSlideConfTwoGraphSubFrame1Layout)
sysDiagSlideConfTwoGraphLayout.addWidget(sysDiagSlideConfTwoGraphSubFrame1)

#####
sysDiagSlideConfTwoGraphCheckBox1 = QCheckBox('Configuration 1')
sysDiagSlideConfTwoGraphCheckBox1.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
sysDiagSlideConfTwoGraphCheckBox1.setChecked(True)
sysDiagSlideConfTwoGraphSubFrame1Layout.addWidget(sysDiagSlideConfTwoGraphCheckBox1, stretch=1)

sysDiagSlideConfTwoGraphComboBox11 = QComboBox()
sysDiagSlideConfTwoGraphSubFrame1Layout.addWidget(sysDiagSlideConfTwoGraphComboBox11, stretch=1)
sysDiagSlideConfTwoGraphComboBox11.setEditText(plotWindowConfigGraphList[2])

sysDiagSlideConfTwoGraphComboBox12 = QComboBox()
sysDiagSlideConfTwoGraphSubFrame1Layout.addWidget(sysDiagSlideConfTwoGraphComboBox12, stretch=1)
sysDiagSlideConfTwoGraphComboBox12.setEditText(plotWindowConfigGraphList[2])

sysDiagSlideConfTwoGraphCheckBox2 = QCheckBox('Configuration 2')
sysDiagSlideConfTwoGraphCheckBox2.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
sysDiagSlideConfTwoGraphCheckBox2.setChecked(True)
sysDiagSlideConfTwoGraphSubFrame1Layout.addWidget(sysDiagSlideConfTwoGraphCheckBox2, stretch=1)

sysDiagSlideConfTwoGraphComboBox21 = QComboBox()
sysDiagSlideConfTwoGraphSubFrame1Layout.addWidget(sysDiagSlideConfTwoGraphComboBox21)
sysDiagSlideConfTwoGraphComboBox21.setEditText(plotWindowConfigGraphList[2])

sysDiagSlideConfTwoGraphComboBox22 = QComboBox()
sysDiagSlideConfTwoGraphSubFrame1Layout.addWidget(sysDiagSlideConfTwoGraphComboBox22, stretch=1)
sysDiagSlideConfTwoGraphComboBox22.setEditText(plotWindowConfigGraphList[2])


####
sysDiagSlideConfVLine = QFrame()
sysDiagSlideConfVLine.setFixedWidth(V_LINE_WIDTH)
sysDiagSlideConfVLine.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.MinimumExpanding)
sysDiagSlideConfVLine.setStyleSheet(lineStyle)
sysDiagSlideConfLayout.addWidget(sysDiagSlideConfVLine)

#### Slide Configuration - Four-Graph Frame
sysDiagSlideConfFourGraphFrame = QFrame()
sysDiagSlideConfLayout.addWidget(sysDiagSlideConfFourGraphFrame)
sysDiagSlideConfFourGraphLayout = QHBoxLayout()
sysDiagSlideConfFourGraphLayout.setSpacing(H_LAYOUT_SPACING)
sysDiagSlideConfFourGraphLayout.setAlignment(Qt.AlignTop)
sysDiagSlideConfFourGraphFrame.setLayout(sysDiagSlideConfFourGraphLayout)
sysDiagSlideConfFourGraphFrame.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)

#####
sysDiagSlideConfFourGraphGraphicFrame = QFrame()
sysDiagSlideConfFourGraphGraphicFrame.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
sysDiagSlideConfFourGraphGraphicLayout = QGridLayout()
sysDiagSlideConfFourGraphGraphicLayout.setVerticalSpacing(V_LAYOUT_SPACING)
sysDiagSlideConfFourGraphGraphicLayout.setHorizontalSpacing(H_LAYOUT_SPACING)
sysDiagSlideConfFourGraphGraphicLayout.setAlignment(Qt.AlignVCenter)
sysDiagSlideConfFourGraphGraphicFrame.setLayout(sysDiagSlideConfFourGraphGraphicLayout)

#####
sysDiagSlideConfFourGraphLabel = QLabel('Four-Graph Layout')
sysDiagSlideConfFourGraphGraphicLayout.addWidget(sysDiagSlideConfFourGraphLabel, 0, 0, 1, 2)

sysDiagSlideConfFourGraphFrame00 = QFrame()
sysDiagSlideConfFourGraphFrame00.setStyleSheet(slideSymbolStyle)
sysDiagSlideConfFourGraphFrame00.setFixedSize(60, 45)
sysDiagSlideConfFourGraphFrame00.setGraphicsEffect(shadowFourGraph00)
sysDiagSlideConfFourGraphFrame00.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
sysDiagSlideConfFourGraphGraphicLayout.addWidget(sysDiagSlideConfFourGraphFrame00, 1, 0, 1, 1)

sysDiagSlideConfFourGraphFrame01 = QFrame()
sysDiagSlideConfFourGraphFrame01.setStyleSheet(slideSymbolStyle)
sysDiagSlideConfFourGraphFrame01.setFixedSize(60, 45)
sysDiagSlideConfFourGraphFrame01.setGraphicsEffect(shadowFourGraph01)
sysDiagSlideConfFourGraphFrame01.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
sysDiagSlideConfFourGraphGraphicLayout.addWidget(sysDiagSlideConfFourGraphFrame01, 1, 1, 1, 1, alignment=Qt.AlignLeft)

sysDiagSlideConfFourGraphFrame10 = QFrame()
sysDiagSlideConfFourGraphFrame10.setStyleSheet(slideSymbolStyle)
sysDiagSlideConfFourGraphFrame10.setFixedSize(60, 45)
sysDiagSlideConfFourGraphFrame10.setGraphicsEffect(shadowFourGraph10)
sysDiagSlideConfFourGraphFrame10.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
sysDiagSlideConfFourGraphGraphicLayout.addWidget(sysDiagSlideConfFourGraphFrame10, 2, 0, 1, 1)

sysDiagSlideConfFourGraphFrame11 = QFrame()
sysDiagSlideConfFourGraphFrame11.setStyleSheet(slideSymbolStyle)
sysDiagSlideConfFourGraphFrame11.setFixedSize(60, 45)
sysDiagSlideConfFourGraphFrame11.setGraphicsEffect(shadowFourGraph11)
sysDiagSlideConfFourGraphFrame11.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
sysDiagSlideConfFourGraphGraphicLayout.addWidget(sysDiagSlideConfFourGraphFrame11, 2, 1, 1, 1, alignment=Qt.AlignLeft)

sysDiagSlideConfFourGraphLayout.addWidget(sysDiagSlideConfFourGraphGraphicFrame)

##### Subframe1
sysDiagSlideConfFourGraphSubFrame1 = QFrame()
sysDiagSlideConfFourGraphSubFrame1Layout = QVBoxLayout()
sysDiagSlideConfFourGraphSubFrame1Layout.setSpacing(V_LAYOUT_SPACING)
sysDiagSlideConfFourGraphSubFrame1Layout.setAlignment(Qt.AlignTop)
sysDiagSlideConfFourGraphSubFrame1.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
sysDiagSlideConfFourGraphSubFrame1.setLayout(sysDiagSlideConfFourGraphSubFrame1Layout)
sysDiagSlideConfFourGraphLayout.addWidget(sysDiagSlideConfFourGraphSubFrame1)

#####
sysDiagSlideConfFourGraphCheckBox1 = QCheckBox('Configuration 1')
sysDiagSlideConfFourGraphCheckBox1.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
sysDiagSlideConfFourGraphCheckBox1.setChecked(True)
sysDiagSlideConfFourGraphSubFrame1Layout.addWidget(sysDiagSlideConfFourGraphCheckBox1)

sysDiagSlideConfFourGraphComboBox1 = QComboBox()
sysDiagSlideConfFourGraphSubFrame1Layout.addWidget(sysDiagSlideConfFourGraphComboBox1)
sysDiagSlideConfFourGraphComboBox1.setEditText(plotWindowConfigGraphList[2])
sysDiagSlideConfFourGraphComboBox1.addItems(plotWindowConfigGraphList)
sysDiagSlideConfFourGraphComboBox1.setCurrentIndex(0)

sysDiagSlideConfFourGraphCheckBox2 = QCheckBox('Configuration 2')
sysDiagSlideConfFourGraphCheckBox2.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
sysDiagSlideConfFourGraphCheckBox2.setChecked(True)
sysDiagSlideConfFourGraphSubFrame1Layout.addWidget(sysDiagSlideConfFourGraphCheckBox2)

sysDiagSlideConfFourGraphComboBox2 = QComboBox()
sysDiagSlideConfFourGraphSubFrame1Layout.addWidget(sysDiagSlideConfFourGraphComboBox2)
sysDiagSlideConfFourGraphComboBox2.setEditText(plotWindowConfigGraphList[2])
sysDiagSlideConfFourGraphComboBox2.addItems(plotWindowConfigGraphList)
sysDiagSlideConfFourGraphComboBox2.setCurrentIndex(0)

sysDiagSlideConfFourGraphCheckBox3 = QCheckBox('Configuration 3')
sysDiagSlideConfFourGraphCheckBox3.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
sysDiagSlideConfFourGraphCheckBox3.setChecked(True)
sysDiagSlideConfFourGraphSubFrame1Layout.addWidget(sysDiagSlideConfFourGraphCheckBox3)

sysDiagSlideConfFourGraphComboBox3 = QComboBox()
sysDiagSlideConfFourGraphSubFrame1Layout.addWidget(sysDiagSlideConfFourGraphComboBox3)
sysDiagSlideConfFourGraphComboBox3.setEditText(plotWindowConfigGraphList[2])
sysDiagSlideConfFourGraphComboBox3.addItems(plotWindowConfigGraphList)
sysDiagSlideConfFourGraphComboBox3.setCurrentIndex(0)

####
sysDiagSlideConfVLine = QFrame()
sysDiagSlideConfVLine.setFixedWidth(V_LINE_WIDTH)
sysDiagSlideConfVLine.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.MinimumExpanding)
sysDiagSlideConfVLine.setStyleSheet(lineStyle)
sysDiagSlideConfLayout.addWidget(sysDiagSlideConfVLine)

#### Slide Configuration - Three-Graph Frame
sysDiagSlideConfThreeGraphFrame = QFrame()
sysDiagSlideConfLayout.addWidget(sysDiagSlideConfThreeGraphFrame)
sysDiagSlideConfThreeGraphLayout = QHBoxLayout()
sysDiagSlideConfThreeGraphLayout.setSpacing(H_LAYOUT_SPACING)
sysDiagSlideConfThreeGraphLayout.setAlignment(Qt.AlignTop)
sysDiagSlideConfThreeGraphFrame.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
sysDiagSlideConfThreeGraphFrame.setLayout(sysDiagSlideConfThreeGraphLayout)

#####
sysDiagSlideConfThreeGraphGraphicFrame = QFrame()
sysDiagSlideConfThreeGraphGraphicFrame.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
sysDiagSlideConfThreeGraphGraphicLayout = QGridLayout()
sysDiagSlideConfThreeGraphGraphicLayout.setVerticalSpacing(V_LAYOUT_SPACING)
sysDiagSlideConfThreeGraphGraphicLayout.setHorizontalSpacing(H_LAYOUT_SPACING)
sysDiagSlideConfThreeGraphGraphicLayout.setAlignment(Qt.AlignVCenter)
sysDiagSlideConfThreeGraphGraphicFrame.setLayout(sysDiagSlideConfThreeGraphGraphicLayout)

sysDiagSlideConfThreeGraphLabel = QLabel('Three-Graph Layout')
sysDiagSlideConfThreeGraphGraphicLayout.addWidget(sysDiagSlideConfThreeGraphLabel, 0, 0, 1, 3)

sysDiagSlideConfThreeGraphFrame1 = QFrame()
sysDiagSlideConfThreeGraphFrame1.setStyleSheet(slideSymbolStyle)
sysDiagSlideConfThreeGraphFrame1.setFixedSize(45, 45)
sysDiagSlideConfThreeGraphFrame1.setGraphicsEffect(shadowThreeGraph1)
sysDiagSlideConfThreeGraphFrame1.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
sysDiagSlideConfThreeGraphGraphicLayout.addWidget(sysDiagSlideConfThreeGraphFrame1, 1, 0, 1, 1, alignment=Qt.AlignLeft | Qt.AlignTop)

sysDiagSlideConfThreeGraphFrame2 = QFrame()
sysDiagSlideConfThreeGraphFrame2.setStyleSheet(slideSymbolStyle)
sysDiagSlideConfThreeGraphFrame2.setFixedSize(45, 45)
sysDiagSlideConfThreeGraphFrame2.setGraphicsEffect(shadowThreeGraph2)
sysDiagSlideConfThreeGraphFrame2.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
sysDiagSlideConfThreeGraphGraphicLayout.addWidget(sysDiagSlideConfThreeGraphFrame2, 1, 1, 1, 1, alignment=Qt.AlignLeft | Qt.AlignTop)

sysDiagSlideConfThreeGraphFrame3 = QFrame()
sysDiagSlideConfThreeGraphFrame3.setStyleSheet(slideSymbolStyle)
sysDiagSlideConfThreeGraphFrame3.setFixedSize(45, 45)
sysDiagSlideConfThreeGraphFrame3.setGraphicsEffect(shadowThreeGraph3)
sysDiagSlideConfThreeGraphFrame3.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
sysDiagSlideConfThreeGraphGraphicLayout.addWidget(sysDiagSlideConfThreeGraphFrame3, 1, 2, 1, 1, alignment=Qt.AlignLeft | Qt.AlignTop)

sysDiagSlideConfThreeGraphLayout.addWidget(sysDiagSlideConfThreeGraphGraphicFrame)

##### Subframe1
sysDiagSlideConfThreeGraphSubFrame1 = QFrame()
sysDiagSlideConfThreeGraphSubFrame1Layout = QVBoxLayout()
sysDiagSlideConfThreeGraphSubFrame1Layout.setSpacing(V_LAYOUT_SPACING)
sysDiagSlideConfThreeGraphSubFrame1Layout.setAlignment(Qt.AlignTop)
sysDiagSlideConfThreeGraphSubFrame1.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
sysDiagSlideConfThreeGraphSubFrame1.setLayout(sysDiagSlideConfThreeGraphSubFrame1Layout)
sysDiagSlideConfThreeGraphLayout.addWidget(sysDiagSlideConfThreeGraphSubFrame1)

#####
sysDiagSlideConfThreeGraphCheckBox1 = QCheckBox('Configuration 1')
sysDiagSlideConfThreeGraphCheckBox1.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
sysDiagSlideConfThreeGraphCheckBox1.setChecked(True)
sysDiagSlideConfThreeGraphSubFrame1Layout.addWidget(sysDiagSlideConfThreeGraphCheckBox1)

sysDiagSlideConfThreeGraphComboBox1 = QComboBox()
sysDiagSlideConfThreeGraphSubFrame1Layout.addWidget(sysDiagSlideConfThreeGraphComboBox1)
sysDiagSlideConfThreeGraphComboBox1.setEditText(plotWindowConfigGraphList[2])
sysDiagSlideConfThreeGraphComboBox1.addItems(plotWindowConfigGraphList)
sysDiagSlideConfThreeGraphComboBox1.setCurrentIndex(0)

sysDiagSlideConfThreeGraphCheckBox2 = QCheckBox('Configuration 2')
sysDiagSlideConfThreeGraphCheckBox2.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
sysDiagSlideConfThreeGraphCheckBox2.setChecked(True)
sysDiagSlideConfThreeGraphSubFrame1Layout.addWidget(sysDiagSlideConfThreeGraphCheckBox2)

sysDiagSlideConfThreeGraphComboBox2 = QComboBox()
sysDiagSlideConfThreeGraphSubFrame1Layout.addWidget(sysDiagSlideConfThreeGraphComboBox2)
sysDiagSlideConfThreeGraphComboBox2.setEditText(plotWindowConfigGraphList[2])
sysDiagSlideConfThreeGraphComboBox2.addItems(plotWindowConfigGraphList)
sysDiagSlideConfThreeGraphComboBox2.setCurrentIndex(0)

sysDiagSlideConfThreeGraphCheckBox3 = QCheckBox('Configuration 3')
sysDiagSlideConfThreeGraphCheckBox3.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
sysDiagSlideConfThreeGraphCheckBox3.setChecked(True)
sysDiagSlideConfThreeGraphSubFrame1Layout.addWidget(sysDiagSlideConfThreeGraphCheckBox3)

sysDiagSlideConfThreeGraphComboBox3 = QComboBox()
sysDiagSlideConfThreeGraphSubFrame1Layout.addWidget(sysDiagSlideConfThreeGraphComboBox3)
sysDiagSlideConfThreeGraphComboBox3.setEditText(plotWindowConfigGraphList[2])
sysDiagSlideConfThreeGraphComboBox3.addItems(plotWindowConfigGraphList)
sysDiagSlideConfThreeGraphComboBox3.setCurrentIndex(0)

####
sysDiagSlideConfVLine = QFrame()
sysDiagSlideConfVLine.setFixedWidth(V_LINE_WIDTH)
sysDiagSlideConfVLine.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.MinimumExpanding)
sysDiagSlideConfVLine.setStyleSheet(lineStyle)
sysDiagSlideConfLayout.addWidget(sysDiagSlideConfVLine)

#### All Graph Slide
sysDiagSlideConfGeneralFrame = QFrame()
sysDiagSlideConfGeneralFrame.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
sysDiagSlideConfGeneralLayout = QHBoxLayout()
sysDiagSlideConfGeneralLayout.setAlignment(Qt.AlignTop)
sysDiagSlideConfGeneralLayout.setSpacing(H_LAYOUT_SPACING)
sysDiagSlideConfGeneralFrame.setLayout(sysDiagSlideConfGeneralLayout)
sysDiagSlideConfLayout.addWidget(sysDiagSlideConfGeneralFrame, stretch=1)

##### All Graphs Subframe1
sysDiagSlideConfGeneralSubFrame1 = QFrame()
sysDiagSlideConfGeneralSubFrame1.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
sysDiagSlideConfGeneralSubFrame1Layout = QVBoxLayout()
sysDiagSlideConfGeneralSubFrame1Layout.setAlignment(Qt.AlignTop)
sysDiagSlideConfGeneralSubFrame1Layout.setSpacing(V_LAYOUT_SPACING)
sysDiagSlideConfGeneralSubFrame1.setLayout(sysDiagSlideConfGeneralSubFrame1Layout)
sysDiagSlideConfGeneralLayout.addWidget(sysDiagSlideConfGeneralSubFrame1, stretch=1)

#####
sysDiagSlideConfGeneralAllGraphsSlideCheckBox = QCheckBox('All-Graphs Slide')
sysDiagSlideConfGeneralAllGraphsSlideCheckBox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
sysDiagSlideConfGeneralAllGraphsSlideCheckBox.setChecked(True)
sysDiagSlideConfGeneralSubFrame1Layout.addWidget(sysDiagSlideConfGeneralAllGraphsSlideCheckBox, alignment=Qt.AlignTop)

#####
sysDiagSlideConfHLine = QFrame()
sysDiagSlideConfHLine.setFixedHeight(H_LINE_HEIGHT)
sysDiagSlideConfHLine.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
sysDiagSlideConfHLine.setStyleSheet(lineStyle)
sysDiagSlideConfGeneralSubFrame1Layout.addWidget(sysDiagSlideConfHLine)

####
sysDiagSlideConfGeneralSensorSlideLabel = QLabel('Sensor Slide:')
sysDiagSlideConfGeneralSubFrame1Layout.addWidget(sysDiagSlideConfGeneralSensorSlideLabel)

#####
sysDiagSlideConfGeneralSensorNumSlideIntValidator = QIntValidator()
sysDiagSlideConfGeneralSensorNumSlideIntValidator.setRange(0, 500)

#####
sysDiagSlideConfGeneralSensorNumSlideLabel = QLabel('Num. of Sensors:')
sysDiagSlideConfGeneralSubFrame1Layout.addWidget(sysDiagSlideConfGeneralSensorNumSlideLabel)

sysDiagSlideConfGeneralSensorNumSlideLEdit = QLineEdit()
sysDiagSlideConfGeneralSensorNumSlideLEdit.setValidator(sysDiagPlotSetupImageDpiIntValidator)
sysDiagSlideConfGeneralSensorNumSlideLEdit.setMaxLength(3)
sysDiagSlideConfGeneralSensorNumSlideLEdit.setFixedSize(LEDIT_BTN_H_SIZE, LEDIT_BTN_V_SIZE)
sysDiagSlideConfGeneralSensorNumSlideLEdit.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
sysDiagSlideConfGeneralSubFrame1Layout.addWidget(sysDiagSlideConfGeneralSensorNumSlideLEdit)

##### All Graphs Subframe2
sysDiagSlideConfGeneralSubFrame2 = QFrame()
sysDiagSlideConfGeneralSubFrame2.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
sysDiagSlideConfGeneralSubFrame2Layout = QVBoxLayout()
sysDiagSlideConfGeneralSubFrame2Layout.setAlignment(Qt.AlignTop)
sysDiagSlideConfGeneralSubFrame2Layout.setSpacing(V_LAYOUT_SPACING)
sysDiagSlideConfGeneralSubFrame2.setLayout(sysDiagSlideConfGeneralSubFrame2Layout)
sysDiagSlideConfGeneralLayout.addWidget(sysDiagSlideConfGeneralSubFrame2, stretch=1)

#####
sysDiagSlideConfGeneralAllSlidesCheckBox1 = QCheckBox('Graph 1')
sysDiagSlideConfGeneralAllSlidesCheckBox1.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
sysDiagSlideConfGeneralAllSlidesCheckBox1.setChecked(True)
sysDiagSlideConfGeneralSubFrame2Layout.addWidget(sysDiagSlideConfGeneralAllSlidesCheckBox1)

sysDiagSlideConfGeneralAllSlidesComboBox1 = QComboBox()
sysDiagSlideConfGeneralAllSlidesComboBox1.addItems(plotWindowConfigGraphList)
sysDiagSlideConfGeneralAllSlidesComboBox1.setCurrentIndex(0)
sysDiagSlideConfGeneralSubFrame2Layout.addWidget(sysDiagSlideConfGeneralAllSlidesComboBox1)

sysDiagSlideConfGeneralAllSlidesCheckBox2 = QCheckBox('Graph 2')
sysDiagSlideConfGeneralAllSlidesCheckBox2.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
sysDiagSlideConfGeneralAllSlidesCheckBox2.setChecked(True)
sysDiagSlideConfGeneralSubFrame2Layout.addWidget(sysDiagSlideConfGeneralAllSlidesCheckBox2)

sysDiagSlideConfGeneralAllSlidesComboBox2 = QComboBox()
sysDiagSlideConfGeneralAllSlidesComboBox2.addItems(plotWindowConfigGraphList)
sysDiagSlideConfGeneralAllSlidesComboBox2.setCurrentIndex(8)
sysDiagSlideConfGeneralSubFrame2Layout.addWidget(sysDiagSlideConfGeneralAllSlidesComboBox2)

sysDiagSlideConfGeneralAllSlidesCheckBox3 = QCheckBox('Graph 3')
sysDiagSlideConfGeneralAllSlidesCheckBox3.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
sysDiagSlideConfGeneralAllSlidesCheckBox3.setChecked(True)
sysDiagSlideConfGeneralSubFrame2Layout.addWidget(sysDiagSlideConfGeneralAllSlidesCheckBox3)

sysDiagSlideConfGeneralAllSlidesComboBox3 = QComboBox()
sysDiagSlideConfGeneralAllSlidesComboBox3.addItems(plotWindowConfigGraphList)
sysDiagSlideConfGeneralAllSlidesComboBox3.setCurrentIndex(6)
sysDiagSlideConfGeneralSubFrame2Layout.addWidget(sysDiagSlideConfGeneralAllSlidesComboBox3)
