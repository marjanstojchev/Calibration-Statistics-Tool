"""PST-60: Tx-Antenna Diagrams tab widget declarations."""
from __future__ import annotations

import os
import sys

_ui_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ui_dir not in sys.path:
    sys.path.insert(0, _ui_dir)

from PySide6.QtWidgets import (
    QFrame, QLabel, QPushButton, QWidget, QGroupBox, QCheckBox,
    QHeaderView, QComboBox, QRadioButton, QLineEdit, QButtonGroup,
    QVBoxLayout, QHBoxLayout, QGridLayout, QSizePolicy,
)
from PySide6.QtGui import *
from PySide6.QtCore import *

from ui_constants import *

##
## TxAnt Diagrams Tab
txAntDiagTab = QWidget()
txAntDiagTab.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
txAntDiagTab.setMaximumHeight(400)
txAntDiagLayout = QGridLayout()
txAntDiagLayout.setHorizontalSpacing(H_LAYOUT_SPACING)
txAntDiagLayout.setVerticalSpacing(V_LAYOUT_SPACING)
txAntDiagLayout.setAlignment(Qt.AlignTop)
txAntDiagTab.setLayout(txAntDiagLayout)
# Note: mainTabWidget.insertTab(2, txAntDiagTab, ...) is called in pyside_qtgui.py

### Tx-Antenna Diagrams Start Script Button
txAntDiagRowIdx = 0
txAntDiagColIdx = 0

txAntDiagStartPushBtn = QPushButton('Start')
txAntDiagStartPushBtn.setMinimumSize(PUSH_BTN_H_SIZE, PUSH_BTN_V_SIZE)
txAntDiagStartPushBtn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
txAntDiagLayout.addWidget(txAntDiagStartPushBtn, txAntDiagRowIdx, txAntDiagColIdx)

#### Input Data Setup GroupBox
txAntDiagRowIdx += 1

txAntDiagInputSetupGroupBox = QGroupBox('Input Setup')
txAntDiagInputSetupGroupBox.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
txAntDiagInputSetupLayout = QHBoxLayout()

txAntDiagLayout.setRowStretch(0, 1)
txAntDiagLayout.setRowStretch(1, 1)
txAntDiagLayout.setColumnStretch(0, 1)
txAntDiagLayout.setColumnStretch(1, 3)

txAntDiagInputSetupLayout.setSpacing(H_LAYOUT_SPACING)
txAntDiagInputSetupLayout.setAlignment(Qt.AlignTop)

txAntDiagInputSetupGroupBox.setLayout(txAntDiagInputSetupLayout)
txAntDiagLayout.addWidget(txAntDiagInputSetupGroupBox, txAntDiagRowIdx, txAntDiagColIdx)

##### Input Data GroupBox Frame
txAntDiagSetupGroupBoxFrame = QFrame()
txAntDiagSetupGroupBoxFrame.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
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
txAntDiagInputSetupAngleGroup.addButton(txAntDiagInputSetupAngleSetupRadio1, 0)

txAntDiagInputSetupAngleSetupRadio2 = QRadioButton('PTU Angle')
txAntDiagInputSetupGroupBoxFrameLayout.addWidget(txAntDiagInputSetupAngleSetupRadio2)
txAntDiagInputSetupAngleGroup.addButton(txAntDiagInputSetupAngleSetupRadio2, 1)

#####
txAntDiagInputSetupHLine = QFrame()
txAntDiagInputSetupHLine.setMinimumHeight(H_LINE_HEIGHT)
txAntDiagInputSetupHLine.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
txAntDiagInputSetupHLine.setStyleSheet(lineStyle)
txAntDiagInputSetupGroupBoxFrameLayout.addWidget(txAntDiagInputSetupHLine)

#####
txAntDiagInputSetupSensorOrientGroup = QButtonGroup()

txAntDiagInputSetupAngleLabel = QLabel('Sensor Orientation')
txAntDiagInputSetupAngleLabel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
txAntDiagInputSetupGroupBoxFrameLayout.addWidget(txAntDiagInputSetupAngleLabel)

txAntDiagInputSetupSensorOrientRadio1 = QRadioButton('Normal')
txAntDiagInputSetupSensorOrientRadio1.setChecked(True)
txAntDiagInputSetupSensorOrientRadio1.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
txAntDiagInputSetupSensorOrientGroup.addButton(txAntDiagInputSetupSensorOrientRadio1)
txAntDiagInputSetupSensorOrientGroup.setId(txAntDiagInputSetupSensorOrientRadio1, 0)
txAntDiagInputSetupGroupBoxFrameLayout.addWidget(txAntDiagInputSetupSensorOrientRadio1)

txAntDiagInputSetupSensorOrientRadio2 = QRadioButton('Upside-Down')
txAntDiagInputSetupSensorOrientRadio2.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
txAntDiagInputSetupGroupBoxFrameLayout.addWidget(txAntDiagInputSetupSensorOrientRadio2)
txAntDiagInputSetupSensorOrientGroup.addButton(txAntDiagInputSetupSensorOrientRadio2)
txAntDiagInputSetupSensorOrientGroup.setId(txAntDiagInputSetupSensorOrientRadio2, 1)

#####
txAntDiagInputSetupHLine = QFrame()
txAntDiagInputSetupHLine.setMinimumHeight(H_LINE_HEIGHT)
txAntDiagInputSetupHLine.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
txAntDiagInputSetupHLine.setStyleSheet(lineStyle)
txAntDiagInputSetupGroupBoxFrameLayout.addWidget(txAntDiagInputSetupHLine)

#####
txAntDiagInputSetupAzCheckBox = QCheckBox('Azimuth Diagrams')
txAntDiagInputSetupAzCheckBox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
txAntDiagInputSetupAzCheckBox.setChecked(True)
txAntDiagInputSetupGroupBoxFrameLayout.addWidget(txAntDiagInputSetupAzCheckBox, stretch=1)

txAntDiagInputSetupElCheckBox = QCheckBox('Elevation Diagrams')
txAntDiagInputSetupElCheckBox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
txAntDiagInputSetupElCheckBox.setChecked(True)
txAntDiagInputSetupGroupBoxFrameLayout.addWidget(txAntDiagInputSetupElCheckBox, stretch=1)

#### Plot Setup GroupBox
txAntDiagColIdx += 1

txAntDiagPlotSetupGroupBox = QGroupBox('Plot Setup')
txAntDiagPlotSetupGroupBox.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
txAntDiagPlotSetupLayout = QHBoxLayout()
txAntDiagPlotSetupLayout.setSpacing(H_LAYOUT_SPACING)
txAntDiagPlotSetupLayout.setAlignment(Qt.AlignTop)
txAntDiagPlotSetupGroupBox.setLayout(txAntDiagPlotSetupLayout)
txAntDiagLayout.addWidget(txAntDiagPlotSetupGroupBox, txAntDiagRowIdx, txAntDiagColIdx)

##### Plot GroupBox Frame
txAntDiagSetupGroupBoxFrame = QFrame()
txAntDiagSetupGroupBoxFrame.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
txAntDiagPlotSetupGroupBoxFrameLayout = QVBoxLayout()
txAntDiagPlotSetupGroupBoxFrameLayout.setSpacing(V_LAYOUT_SPACING)
txAntDiagPlotSetupGroupBoxFrameLayout.setAlignment(Qt.AlignTop)
txAntDiagSetupGroupBoxFrame.setLayout(txAntDiagPlotSetupGroupBoxFrameLayout)
txAntDiagPlotSetupLayout.addWidget(txAntDiagSetupGroupBoxFrame)

#####
txAntDiagPlotSetupSensorNumSlideIntValidator = QIntValidator()
txAntDiagPlotSetupSensorNumSlideIntValidator.setRange(0, 500)

txAntDiagPlotSetupSensorNumSlideLabel = QLabel('Num. of Sensors - Sensor Slide:')
txAntDiagPlotSetupGroupBoxFrameLayout.addWidget(txAntDiagPlotSetupSensorNumSlideLabel)

txAntDiagPlotSetupSensorNumSlideLEdit = QLineEdit()
# FIX: use local validator instead of cross-tab sysDiagPlotSetupImageDpiIntValidator
txAntDiagPlotSetupSensorNumSlideLEdit.setValidator(txAntDiagPlotSetupSensorNumSlideIntValidator)
txAntDiagPlotSetupSensorNumSlideLEdit.setMaxLength(3)
txAntDiagPlotSetupSensorNumSlideLEdit.setMinimumSize(LEDIT_BTN_H_SIZE, LEDIT_BTN_V_SIZE)
txAntDiagPlotSetupSensorNumSlideLEdit.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
txAntDiagPlotSetupGroupBoxFrameLayout.addWidget(txAntDiagPlotSetupSensorNumSlideLEdit)

####
txAntDiagInputSetupHLine = QFrame()
txAntDiagInputSetupHLine.setMinimumHeight(H_LINE_HEIGHT)
txAntDiagInputSetupHLine.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
txAntDiagInputSetupHLine.setStyleSheet(lineStyle)
txAntDiagPlotSetupGroupBoxFrameLayout.addWidget(txAntDiagInputSetupHLine)

#####
txAntDiagPlotSetupGraphsPerSliideIntValidator = QIntValidator()
txAntDiagPlotSetupGraphsPerSliideIntValidator.setRange(1, 4)

txAntDiagPlotSetupGraphsPerSlideLabel = QLabel('Graphs per Slide:')
txAntDiagPlotSetupGroupBoxFrameLayout.addWidget(txAntDiagPlotSetupGraphsPerSlideLabel)

txAntDiagPlotSetupGraphsPerSlideLEdit = QLineEdit()
# FIX: use local validator instead of cross-tab sysDiagPlotSetupImageDpiIntValidator
txAntDiagPlotSetupGraphsPerSlideLEdit.setValidator(txAntDiagPlotSetupGraphsPerSliideIntValidator)
txAntDiagPlotSetupGraphsPerSlideLEdit.setMaxLength(1)
txAntDiagPlotSetupGraphsPerSlideLEdit.setMinimumSize(LEDIT_BTN_H_SIZE, LEDIT_BTN_V_SIZE)
txAntDiagPlotSetupGraphsPerSlideLEdit.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
txAntDiagPlotSetupGroupBoxFrameLayout.addWidget(txAntDiagPlotSetupGraphsPerSlideLEdit)

#####
txAntDiagInputSetupHLine = QFrame()
txAntDiagInputSetupHLine.setMinimumHeight(H_LINE_HEIGHT)
txAntDiagInputSetupHLine.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
txAntDiagInputSetupHLine.setStyleSheet(lineStyle)
txAntDiagPlotSetupGroupBoxFrameLayout.addWidget(txAntDiagInputSetupHLine)

#####
txAntDiagPlotSetupImageDpiIntValidator = QIntValidator()
txAntDiagPlotSetupImageDpiIntValidator.setRange(0, 500)

txAntDiagPlotSetupImageDpiLabel = QLabel('Image DPI:')
txAntDiagPlotSetupGroupBoxFrameLayout.addWidget(txAntDiagPlotSetupImageDpiLabel)

txAntDiagPlotSetupImageDpiLEdit = QLineEdit()
txAntDiagPlotSetupImageDpiLEdit.setValidator(txAntDiagPlotSetupImageDpiIntValidator)
txAntDiagPlotSetupImageDpiLEdit.setMaxLength(3)
txAntDiagPlotSetupImageDpiLEdit.setMinimumSize(LEDIT_BTN_H_SIZE, LEDIT_BTN_V_SIZE)
txAntDiagPlotSetupImageDpiLEdit.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
txAntDiagPlotSetupGroupBoxFrameLayout.addWidget(txAntDiagPlotSetupImageDpiLEdit)

#####
txAntDiagPlotSetupVLine = QFrame()
txAntDiagPlotSetupVLine.setMinimumWidth(V_LINE_WIDTH)
txAntDiagPlotSetupVLine.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.MinimumExpanding)
txAntDiagPlotSetupVLine.setStyleSheet(lineStyle)
txAntDiagPlotSetupLayout.addWidget(txAntDiagPlotSetupVLine)

##### Plot GroupBox Scaling Frame
txAntDiagPlotSetupGroupBoxScalingFrame = QFrame()
txAntDiagPlotSetupGroupBoxScalingFrame.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
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
txAntDiagPlotSetupScalingXScaleIntValidator.setRange(0, 150)

txAntDiagPlotSetupScalingXScaleAzLabel = QLabel('X-Scale Azimuth:')
txAntDiagPlotSetupGroupBoxScalingFrameLayout.addWidget(txAntDiagPlotSetupScalingXScaleAzLabel)

txAntDiagPlotSetupScalingXScaleAzLEdit = QLineEdit()
txAntDiagPlotSetupScalingXScaleAzLEdit.setValidator(txAntDiagPlotSetupScalingXScaleIntValidator)
txAntDiagPlotSetupScalingXScaleAzLEdit.setMaxLength(3)
txAntDiagPlotSetupScalingXScaleAzLEdit.setMinimumSize(LEDIT_BTN_H_SIZE, LEDIT_BTN_V_SIZE)
txAntDiagPlotSetupScalingXScaleAzLEdit.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
txAntDiagPlotSetupGroupBoxScalingFrameLayout.addWidget(txAntDiagPlotSetupScalingXScaleAzLEdit)

txAntDiagPlotSetupScalingXScaleElLabel = QLabel('X-Scale Elevation:')
txAntDiagPlotSetupGroupBoxScalingFrameLayout.addWidget(txAntDiagPlotSetupScalingXScaleElLabel)

txAntDiagPlotSetupScalingXScaleElLEdit = QLineEdit()
txAntDiagPlotSetupScalingXScaleElLEdit.setValidator(txAntDiagPlotSetupScalingXScaleIntValidator)
txAntDiagPlotSetupScalingXScaleElLEdit.setMaxLength(3)
txAntDiagPlotSetupScalingXScaleElLEdit.setMinimumSize(LEDIT_BTN_H_SIZE, LEDIT_BTN_V_SIZE)
txAntDiagPlotSetupScalingXScaleElLEdit.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
txAntDiagPlotSetupGroupBoxScalingFrameLayout.addWidget(txAntDiagPlotSetupScalingXScaleElLEdit)

#####
txAntDiagPlotSetupScalingHLine = QFrame()
txAntDiagPlotSetupScalingHLine.setMinimumHeight(H_LINE_HEIGHT)
txAntDiagPlotSetupScalingHLine.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
txAntDiagPlotSetupScalingHLine.setStyleSheet(lineStyle)
txAntDiagPlotSetupGroupBoxScalingFrameLayout.addWidget(txAntDiagPlotSetupScalingHLine)

#####
txAntDiagPlotSetupScalingOrigGraphsCheckBox = QCheckBox('Plot Original Graphs')
txAntDiagPlotSetupScalingOrigGraphsCheckBox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
txAntDiagPlotSetupScalingOrigGraphsCheckBox.setChecked(True)
txAntDiagPlotSetupGroupBoxScalingFrameLayout.addWidget(txAntDiagPlotSetupScalingOrigGraphsCheckBox, stretch=1)

txAntDiagPlotSetupScalingNormGraphsCheckBox = QCheckBox('Plot Normalised Graphs')
txAntDiagPlotSetupScalingNormGraphsCheckBox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
txAntDiagPlotSetupScalingNormGraphsCheckBox.setChecked(True)
txAntDiagPlotSetupGroupBoxScalingFrameLayout.addWidget(txAntDiagPlotSetupScalingNormGraphsCheckBox, stretch=1)

#####
txAntDiagPlotSetupVLine = QFrame()
txAntDiagPlotSetupVLine.setMinimumWidth(V_LINE_WIDTH)
txAntDiagPlotSetupVLine.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.MinimumExpanding)
txAntDiagPlotSetupVLine.setStyleSheet(lineStyle)
txAntDiagPlotSetupLayout.addWidget(txAntDiagPlotSetupVLine)

##### Plot Setup Graph Configuration Frame
txAntDiagPlotSetupGraphConfFrame = QFrame()
txAntDiagPlotSetupLayout.addWidget(txAntDiagPlotSetupGraphConfFrame)
txAntDiagPlotSetupGraphConfFrame.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
txAntDiagPlotSetupGraphConfLayout = QVBoxLayout()
txAntDiagPlotSetupGraphConfLayout.setAlignment(Qt.AlignTop)
txAntDiagPlotSetupGraphConfLayout.setSpacing(V_LAYOUT_SPACING)
txAntDiagPlotSetupGraphConfFrame.setLayout(txAntDiagPlotSetupGraphConfLayout)

#####
txAntDiagPlotSetupGraphConfLabel = QLabel('Graph Configuration')
txAntDiagPlotSetupGraphConfLayout.addWidget(txAntDiagPlotSetupGraphConfLabel)

txAntDiagGraphConfig = {
    "level": 1,
    "levelPowMet": 1,
    "levelMeasSpec": 1,
    "levelMeasPowMet": 1,
    "frequency": 1,
    "time": 1,
}


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


txAntDiagPlotSetupGraphConfGroup = QButtonGroup()
txAntDiagPlotSetupGraphConfGroup.setExclusive(False)

_id = 0
for _key, _val in txAntDiagGraphConfig.items():
    txAntDiagPlotSetupGraphConfCheckBox = QCheckBox(txAntDiagGraphStringMapping(_key))
    txAntDiagPlotSetupGraphConfLayout.addWidget(txAntDiagPlotSetupGraphConfCheckBox)
    txAntDiagPlotSetupGraphConfGroup.addButton(txAntDiagPlotSetupGraphConfCheckBox, _id)
    _id += 1
