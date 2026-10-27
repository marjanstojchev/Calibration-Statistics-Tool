
from calibration_statistics_tool.shared import loaddata as ld
from calibration_statistics_tool.shared import powerpoint as pp
import os
import numpy as np
import pptx
from calibration_statistics_tool.shared import logconfig
from calibration_statistics_tool.shared import data_processing as dp
from calibration_statistics_tool.shared import plotdata as plt
import sys
from calibration_statistics_tool.shared import auxiliary as aux
import matplotlib.pyplot as plot
from calibration_statistics_tool.ui import pyside_qtgui as qt
import re
from pptx import Presentation
import yaml


bUseGui = True

lenofargs = len(sys.argv)
if( lenofargs == 1): # ptu file / pfad hier vorgeben ( als erstes argument in sys.argv ist immer die script datei selbst enthalten)
    # absPath =r'C:\Arbeit\ProtokollBsp'
    # absPath=r'\\fileserver6\MDSMS0\Kalibrierung\Test_RR_Kalibrierung\2018-05-07_UMRR92_Type150\2018-08-13_Cal_Mobis_88Stueck'
    # absPath=r'C:\OpenAccess\vonAndreasA\FilesTemp1'
    absPath=r'C:\OpenAccess\von_Qi\umrr93_T150'
    absPath=r'C:\Arbeit\ALPSsampleMod'
    absPath=r'C:\OpenAccess\vonAndreasA\Typ132Daten'
    # absPath = r'C:\Arbeit\twoAntenna'
    # absPath=r'C:\Arbeit\axelAz'
    # absPath=r'C:\Arbeit\axelEl'
    # absPath=r'C:\Arbeit\AlpsAz'
    # absPath=r'C:\Arbeit\AlpsEl'
    # absPath=r'C:\Arbeit\qi_axel'
    # absPath=r'C:\Arbeit\ALPSsample\UMRR-98.00.00-0002E72A'
    absPath=r'C:\OpenAccess\Marjan\intern_300xUMRR-0C0204-2A2A02Dez2016\UMRR-0C.02.04-00029EED'
    # absPath=r'C:\Arbeit\ALPSsample\UMRR-98.00.00-0002E72A'
    # absPath=r'C:\Arbeit\antenna_patterns_ALPS'
    # absPath=r'C:\Arbeit\Alps_diag0'
    # absPath = r'C:\Arbeit\132'
    # absPath=r'\\ad.smartmicro.de\Data\Messdaten\MDSMS0\Kalibrierung\Test_TDAX_Kalibrierung\Umrr12T48_first3Wfs\UMRR-12.02.00-00030293'
    absPath=r'C:\Users\Raza\Desktop\StatisticToolPython_QtGUI_CT_Branch\intern_2xUMRR-110004-840100ohneJTAGLock'
    absPath=r'C:\StatisticToolPython_QtGUI_CT_Branch\Data\intern_300xUMRR-0C0204-2A2A02Dez2016'

elif(lenofargs == 2): # als argument einzelner pfad oder ptu file  ( als erstes argument in sys.argv ist immer die script datei selbst enthalten)
    absPath = sys.argv[1]
#else:  # liste von dateien
    absPath = list(sys.argv[1:])


plotSetup = {
    'targetAngle': 1,  # Show in target angle.
    'upsideDown': 0,  # Sensor is upside down mounted: 1, otherwise: 0.
    'xScaleSizeAuto': 0,  # Automatic size of the xScale: 1, manual setup with xScaleSizeAz and xScaleSizeEl: 0.
    'xScaleSizeAz': 90, # (+-°) Size of the xScaleSizeAz, when xAxisAuto = 0.
    'xScaleSizeEl': 45, # (+-°) Size of the xScaleSizeEl, when xAxisAuto = 0.
    'idealPhaseDiff':1,  #Show ideal phase difference
    'SeparateRxCh':1, # Plot each Rx channel separately
    'threeGraphLayout':1, #Generate images for slides with three images in one line.
    'allOnOneSlide': 1, #Genrate all on one slide: all diagrams, all sensors, all RxAnt, graphs by choice.
    'diffPhaseDiffScalingFactor':1.5, # Y axis zoom factor for diffPhaseDiffDiagrams
    'yLimitsAntTypeSeparately':1, #Determine Y axis upper and lower margines separately for each Antenna Type: 1, for all Antenna Types together: 0.
    'imageDpi': 220, # Set plot image resolution
    'nofSensorMeasToShow': 32,  # The max number of sensor measurements to show
    'ShowCertainPlotWindow': 0, # Show certain plot window mode: 1, otherwise: 0.
    'sortByMeasAngle': 0, # Sort data from same antenna type by measurement angle setup: 1, process data together 0.
    'sensorMusterList':['rf', 'dsp', 'PT','MA'],  # Include rf and dsp patterns for actual sensor names
    'useSensorMuster':0
}
plotWindowConfig = {
    'inputMode': 1, # Data: 1, String: 0
    'showPlotAllMode': 0, # Show all graphs on one plot: 1, show certain configured plot: 0
    'string': 'level_AntType158_TxAnt0', # generated image name
    'graph': 'corrPhaseDiff',
    'antType': 158,
    'diagramNum': 7,
    'rxCh': 2
}
# Chirp configuration
chirpConfig = {
    'chirp0': 1,
    'chirp1': 0,
    'chirp2': 0,
    'chirp3': 0,
}
# Generate graph setup
graphConfig = {
    # Power level diagrams
    'level': 1,  # Power level [dB].
    'avgLevel': 0,  # Average power level of chirps [dB].

    'normLevel': 1,  # Normalised power level [dB].
    'avgNormLevel': 0,  # Average of normalised power levels of all chirps [dB].

    # Phase difference diagrams
    'phaseDiff': 1,  # Phase difference [°].
    'avgPhaseDiff': 0,  # Average of the corrected phase differences of all chirps[°].

    'diffPhaseDiff': 0,  # Difference between the corrected phase difference and the ideal one [°].
    'avgDiffPhaseDiff': 0,  # Average of the difference of the corrected phase difference and the ideal one of all chirps[°].

    'corrPhaseDiff': 1,  # Corrected phase difference by the correction factor [°].
}
# interactive modus dict
graphInterList = {
    # Power level diagrams
    'level': 0,  # Power level [dB].
    'avgLevel': 0,  # Average power level of chirps [dB].

    'normLevel': 0,  # Normalised power level [dB].
    'avgNormLevel': 0,  # Average of normalised power levels of all chirps [dB].

    # Phase difference diagrams
    'phaseDiff': 0,  # Phase difference [°].
    'avgPhaseDiff': 0,  # Average of the corrected phase differences of all chirps[°].

    'diffPhaseDiff': 0,  # Difference between the corrected phase difference and the ideal one [°].
    'avgDiffPhaseDiff': 0,  # Average of the difference of the corrected phase difference and the ideal one of all chirps[°].

    'corrPhaseDiff': 0,  # Corrected phase difference by the correction factor [°].
    'idealPhaseDiff': 0,  # Ideal phase difference [°].
}
diagramConfig = {
    'selectDiagrams':0 , # Set 0 for all diagrams. 1 for diagrams in desired range. 2 for diagrams from an arbitrary list.

    #Set even or odd diagram numbers
    'oddOrEven': 0, # Set 0 for both. 1 for odd. 2 for even.

    # Set from a desired range
    'lowerNumber': 0, # Present diagrams in a specific range. Chose lower number.
    'higherNumber':7, # Present diagrams in a specific range. Chose higher number.
}
# List of desired Diagram numbers
diagramConfigList = [1, 2, 3, 4]
# Level slide comb.
twoGraphConf1 = {
    'primGraph': 'level',
    'secGraph': 'normLevel'
}
# Phase difference slide comb.
twoGraphConf2 = {
    'primGraph': 'corrPhaseDiff',
    'secGraph': 'diffPhaseDiff'
}
# Phase difference slide comb.
threeGraphConf1 = {
    'graphType': 'corrPhaseDiff'
}
threeGraphConf2 = {
    'graphType': 'diffPhaseDiff'
}
threeGraphConf3 = {
    'graphType': 'phaseDiff'
}
fourGraphConf1 = {
    'graphType': 'level'
}
fourGraphConf2 = {
    'graphType': 'corrPhaseDiff'
}
fourGraphConf3 = {
    'graphType': 'diffPhaseDiff'
}
AllGraphsConf1 = {
    'graphType': 'level'
}
AllGraphsConf2 = {
    'graphType': 'corrPhaseDiff'
}
AllGraphsConf3 = {
    'graphType': 'diffPhaseDiff'
}
# Two-graph slides configuration list
twoGraphSetupList = [twoGraphConf1]
# Four-graph slides configuration list
fourGraphSetupList = []
# Three-graph slides configuration list
threeGraphSetupList = [threeGraphConf1, threeGraphConf3]
# All on one slide graphs list
allOnOneSlideGraphList = [AllGraphsConf1, AllGraphsConf2, AllGraphsConf3]
# interactive dicts
actualCheckedGraphsDict = {
    -1: 'default'
}
SysDiaInterTableParamGraphsDict = {
    'actualRemovedGraphsList': [],
    'actualCheckedGraphsDict': actualCheckedGraphsDict
}
# Protocol interctive table 
RePlot = {
    'x': [],
    'y': [],
    'label': [],
    'graphtype': [],
    'xsec': [],
    'ysec': [],
    'labelsec': [],
    'graphtypesec': [],
}
parseData = {
    'parseDataList' : [],
}

def getGraphIndex():
    graphIdx = -1

    if len(SysDiaInterTableParamGraphsDict['actualRemovedGraphsList']) == 0:
        keys = SysDiaInterTableParamGraphsDict['actualCheckedGraphsDict'].keys()
        graphIdx = max(keys) +1
    else:
        graphIdx = min(SysDiaInterTableParamGraphsDict['actualRemovedGraphsList'])
        idxOfgraphIdx = SysDiaInterTableParamGraphsDict['actualRemovedGraphsList'].index(graphIdx)
        del SysDiaInterTableParamGraphsDict['actualRemovedGraphsList'][idxOfgraphIdx]
    return graphIdx

# [rest of the file continues unchanged - truncated for length but would be identical to source]
