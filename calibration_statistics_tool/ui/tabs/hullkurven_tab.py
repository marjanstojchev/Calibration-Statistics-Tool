"""Hullkurven (Envelope Curves) tab widget declarations — Epic 2."""
from __future__ import annotations

import os
import sys

_ui_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ui_dir not in sys.path:
    sys.path.insert(0, _ui_dir)

from PySide6.QtWidgets import (
    QFrame, QLabel, QPushButton, QWidget, QGroupBox, QCheckBox,
    QRadioButton, QLineEdit, QButtonGroup,
    QVBoxLayout, QHBoxLayout, QGridLayout, QSizePolicy,
)
from PySide6.QtGui import *
from PySide6.QtCore import *

from calibration_statistics_tool.ui.ui_constants import *

##
## Hullkurven Tab
hullkurvenTab = QWidget()
hullkurvenTab.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
hullkurvenTab.setMaximumHeight(400)
hullkurvenLayout = QGridLayout()
hullkurvenLayout.setHorizontalSpacing(H_LAYOUT_SPACING)
hullkurvenLayout.setVerticalSpacing(V_LAYOUT_SPACING)
hullkurvenLayout.setAlignment(Qt.AlignTop)
hullkurvenTab.setLayout(hullkurvenLayout)

### Start Button
hullkurvenRowIdx = 0
hullkurvenColIdx = 0

hullkurvenStartPushBtn = QPushButton('Start')
hullkurvenStartPushBtn.setFixedSize(PUSH_BTN_H_SIZE, PUSH_BTN_V_SIZE)
hullkurvenStartPushBtn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
hullkurvenLayout.addWidget(hullkurvenStartPushBtn, hullkurvenRowIdx, hullkurvenColIdx)

#### Input Setup GroupBox
hullkurvenRowIdx += 1

hullkurvenLayout.setRowStretch(0, 1)
hullkurvenLayout.setRowStretch(1, 1)
hullkurvenLayout.setColumnStretch(0, 1)
hullkurvenLayout.setColumnStretch(1, 3)

hullkurvenInputSetupGroupBox = QGroupBox('Input Setup')
hullkurvenInputSetupGroupBox.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
hullkurvenInputSetupLayout = QHBoxLayout()
hullkurvenInputSetupLayout.setSpacing(H_LAYOUT_SPACING)
hullkurvenInputSetupLayout.setAlignment(Qt.AlignTop)
hullkurvenInputSetupGroupBox.setLayout(hullkurvenInputSetupLayout)
hullkurvenLayout.addWidget(hullkurvenInputSetupGroupBox, hullkurvenRowIdx, hullkurvenColIdx)

##### Input Setup Frame
hullkurvenInputSetupFrame = QFrame()
hullkurvenInputSetupFrame.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
hullkurvenInputSetupFrameLayout = QVBoxLayout()
hullkurvenInputSetupFrameLayout.setSpacing(V_LAYOUT_SPACING)
hullkurvenInputSetupFrameLayout.setAlignment(Qt.AlignTop)
hullkurvenInputSetupFrame.setLayout(hullkurvenInputSetupFrameLayout)
hullkurvenInputSetupLayout.addWidget(hullkurvenInputSetupFrame)

#####
hullkurvenInputSetupAzCheckBox = QCheckBox('Azimuth Diagrams')
hullkurvenInputSetupAzCheckBox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
hullkurvenInputSetupAzCheckBox.setChecked(True)
hullkurvenInputSetupFrameLayout.addWidget(hullkurvenInputSetupAzCheckBox)

hullkurvenInputSetupElCheckBox = QCheckBox('Elevation Diagrams')
hullkurvenInputSetupElCheckBox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
hullkurvenInputSetupElCheckBox.setChecked(False)
hullkurvenInputSetupFrameLayout.addWidget(hullkurvenInputSetupElCheckBox)

#####
hullkurvenInputSetupHLine1 = QFrame()
hullkurvenInputSetupHLine1.setFixedHeight(H_LINE_HEIGHT)
hullkurvenInputSetupHLine1.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
hullkurvenInputSetupHLine1.setStyleSheet(lineStyle)
hullkurvenInputSetupFrameLayout.addWidget(hullkurvenInputSetupHLine1)

#####
hullkurvenInputSetupSigmaIntValidator = QIntValidator()
hullkurvenInputSetupSigmaIntValidator.setRange(-100, 100)

hullkurvenInputSetupMinSigmaLabel = QLabel('Min Sigma:')
hullkurvenInputSetupMinSigmaLabel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
hullkurvenInputSetupFrameLayout.addWidget(hullkurvenInputSetupMinSigmaLabel)

hullkurvenInputSetupMinSigmaLEdit = QLineEdit()
hullkurvenInputSetupMinSigmaLEdit.setValidator(hullkurvenInputSetupSigmaIntValidator)
hullkurvenInputSetupMinSigmaLEdit.setMaxLength(4)
hullkurvenInputSetupMinSigmaLEdit.setFixedSize(LEDIT_BTN_H_SIZE, LEDIT_BTN_V_SIZE)
hullkurvenInputSetupMinSigmaLEdit.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
hullkurvenInputSetupFrameLayout.addWidget(hullkurvenInputSetupMinSigmaLEdit)

hullkurvenInputSetupMaxSigmaLabel = QLabel('Max Sigma:')
hullkurvenInputSetupMaxSigmaLabel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
hullkurvenInputSetupFrameLayout.addWidget(hullkurvenInputSetupMaxSigmaLabel)

hullkurvenInputSetupMaxSigmaLEdit = QLineEdit()
hullkurvenInputSetupMaxSigmaLEdit.setValidator(hullkurvenInputSetupSigmaIntValidator)
hullkurvenInputSetupMaxSigmaLEdit.setMaxLength(4)
hullkurvenInputSetupMaxSigmaLEdit.setFixedSize(LEDIT_BTN_H_SIZE, LEDIT_BTN_V_SIZE)
hullkurvenInputSetupMaxSigmaLEdit.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
hullkurvenInputSetupFrameLayout.addWidget(hullkurvenInputSetupMaxSigmaLEdit)

#####
hullkurvenInputSetupHLine2 = QFrame()
hullkurvenInputSetupHLine2.setFixedHeight(H_LINE_HEIGHT)
hullkurvenInputSetupHLine2.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
hullkurvenInputSetupHLine2.setStyleSheet(lineStyle)
hullkurvenInputSetupFrameLayout.addWidget(hullkurvenInputSetupHLine2)

#####
hullkurvenInputSetupPatternMethodLabel = QLabel('Pattern Limits Method:')
hullkurvenInputSetupPatternMethodLabel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
hullkurvenInputSetupFrameLayout.addWidget(hullkurvenInputSetupPatternMethodLabel)

hullkurvenInputSetupPatternMethodGroup = QButtonGroup()

hullkurvenInputSetupPatternMethodSigmaRadio = QRadioButton('Sigma-based')
hullkurvenInputSetupPatternMethodSigmaRadio.setChecked(True)
hullkurvenInputSetupPatternMethodSigmaRadio.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
hullkurvenInputSetupPatternMethodGroup.addButton(hullkurvenInputSetupPatternMethodSigmaRadio, 0)
hullkurvenInputSetupFrameLayout.addWidget(hullkurvenInputSetupPatternMethodSigmaRadio)

hullkurvenInputSetupPatternMethodMinMaxRadio = QRadioButton('Min/Max-based')
hullkurvenInputSetupPatternMethodMinMaxRadio.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
hullkurvenInputSetupPatternMethodGroup.addButton(hullkurvenInputSetupPatternMethodMinMaxRadio, 1)
hullkurvenInputSetupFrameLayout.addWidget(hullkurvenInputSetupPatternMethodMinMaxRadio)

#### Plot Setup GroupBox
hullkurvenColIdx += 1

hullkurvenPlotSetupGroupBox = QGroupBox('Plot Setup')
hullkurvenPlotSetupGroupBox.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
hullkurvenPlotSetupLayout = QHBoxLayout()
hullkurvenPlotSetupLayout.setSpacing(H_LAYOUT_SPACING)
hullkurvenPlotSetupLayout.setAlignment(Qt.AlignTop)
hullkurvenPlotSetupGroupBox.setLayout(hullkurvenPlotSetupLayout)
hullkurvenLayout.addWidget(hullkurvenPlotSetupGroupBox, hullkurvenRowIdx, hullkurvenColIdx)

##### Plot Setup Frame
hullkurvenPlotSetupFrame = QFrame()
hullkurvenPlotSetupFrame.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
hullkurvenPlotSetupFrameLayout = QVBoxLayout()
hullkurvenPlotSetupFrameLayout.setSpacing(V_LAYOUT_SPACING)
hullkurvenPlotSetupFrameLayout.setAlignment(Qt.AlignTop)
hullkurvenPlotSetupFrame.setLayout(hullkurvenPlotSetupFrameLayout)
hullkurvenPlotSetupLayout.addWidget(hullkurvenPlotSetupFrame)

#####
hullkurvenPlotSetupXScaleAutoCheckBox = QCheckBox('X-Scale Autoscale')
hullkurvenPlotSetupXScaleAutoCheckBox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
hullkurvenPlotSetupFrameLayout.addWidget(hullkurvenPlotSetupXScaleAutoCheckBox)

#####
hullkurvenPlotSetupXScaleIntValidator = QIntValidator()
hullkurvenPlotSetupXScaleIntValidator.setRange(0, 150)

hullkurvenPlotSetupXScaleAzLabel = QLabel('X-Scale Azimuth:')
hullkurvenPlotSetupFrameLayout.addWidget(hullkurvenPlotSetupXScaleAzLabel)

hullkurvenPlotSetupXScaleAzLEdit = QLineEdit()
hullkurvenPlotSetupXScaleAzLEdit.setValidator(hullkurvenPlotSetupXScaleIntValidator)
hullkurvenPlotSetupXScaleAzLEdit.setMaxLength(3)
hullkurvenPlotSetupXScaleAzLEdit.setFixedSize(LEDIT_BTN_H_SIZE, LEDIT_BTN_V_SIZE)
hullkurvenPlotSetupXScaleAzLEdit.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
hullkurvenPlotSetupFrameLayout.addWidget(hullkurvenPlotSetupXScaleAzLEdit)

hullkurvenPlotSetupXScaleElLabel = QLabel('X-Scale Elevation:')
hullkurvenPlotSetupFrameLayout.addWidget(hullkurvenPlotSetupXScaleElLabel)

hullkurvenPlotSetupXScaleElLEdit = QLineEdit()
hullkurvenPlotSetupXScaleElLEdit.setValidator(hullkurvenPlotSetupXScaleIntValidator)
hullkurvenPlotSetupXScaleElLEdit.setMaxLength(3)
hullkurvenPlotSetupXScaleElLEdit.setFixedSize(LEDIT_BTN_H_SIZE, LEDIT_BTN_V_SIZE)
hullkurvenPlotSetupXScaleElLEdit.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
hullkurvenPlotSetupFrameLayout.addWidget(hullkurvenPlotSetupXScaleElLEdit)
