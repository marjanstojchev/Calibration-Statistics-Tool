
import loaddata as ld
import powerpoint as pp
import os
import numpy as np
import pptx
import logconfig
import data_processing as dp
import plotdata as plt
import sys
import auxiliary as aux
import matplotlib.pyplot as plot
import pyside_qtgui as qt
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

# fill in protocol lists
def fillInPTU(parseDataList, sysDiagLogger):
    ClearData()
    # log files
    myLogger = sysDiagLogger.logger
    errorStatus, errorSting = sysDiagLogger.addFileHandler(logconfig.antSysDiagLogFilePath, 'w+')
    if errorStatus == 1:
        myLogger.warning(errorSting)
    myLogger.info('Filling data in table.')
    
    if len(parseDataList) !=0:
        # clear the plot
        qt.SysDiaInterPlotFrame.clear()
        # data Prcoessing
        parseData['parseDataList'] = parseDataList
        antennaTypesList = dp.getAntennaTypesList(parseDataList)
        if len(antennaTypesList) == 0:
            myLogger.error('No antenna types found in parsed PTU2 data for interactive table fill.')
            return
        desiredDiagList  = dp.getDiagramList(antennaTypesList[0], parseDataList)
        qt.SysDiaInterTableProtocol.clearContents()
        qt.SysDiaInterTableParam.clearContents()
        qt.mainTabWidget.setCurrentIndex(qt.tab_index_of('System Diagrams Interactive'))

        for antTypeIdx in range(len(antennaTypesList)):
            ptu2ListPerAntennaType = dp.getPtu2ListPerAntennaType(antennaTypesList[antTypeIdx], parseDataList)
            rowIdx = 0
            seen_protocol_rows = set()
            # Number of protocol table
            for row in range(len(ptu2ListPerAntennaType)):
                protocol_key = (
                    str(ptu2ListPerAntennaType[row].fileTitle.dateAndTime),
                    str(ptu2ListPerAntennaType[row].fileTitle.tuner),
                    str(ptu2ListPerAntennaType[row].fileTitle.sensor),
                )
                if protocol_key in seen_protocol_rows:
                    continue
                seen_protocol_rows.add(protocol_key)

                qt.SysDiaInterTableProtocol.insertRow(rowIdx)

                # Graph
                tableItem = qt.QTableWidgetItem()
                tableItem.setData(qt.Qt.DisplayRole, 'True')
                tableItem.setData(qt.Qt.UserRole, -1)
                tableItem.setFlags(qt.Qt.ItemIsEnabled)
                tableItem.setBackground(qt.QBrush(qt.QColor('green')))
                tableItem.setForeground(qt.QBrush(qt.QColor('white')))
                qt.SysDiaInterTableProtocol.setItem(rowIdx, qt.SysDiaInterTableProtColMapping['graph'], qt.QTableWidgetItem(tableItem))

                # protocol
                tableItem = qt.QTableWidgetItem()
                tableItem.setData(0, protocol_key[0] + '_' + protocol_key[1] + '_' + protocol_key[2])
                tableItem.setData(qt.Qt.UserRole, protocol_key[2])  # sensor for line-matching
                qt.SysDiaInterTableProtocol.setItem(rowIdx, qt.SysDiaInterTableProtColMapping['Protocol'], tableItem)
                rowIdx += 1

            qt.SysDiaInterTableProtocolHeader.setSectionResizeMode(qt.QHeaderView.Interactive)
            qt.SysDiaInterTableProtocolHeader.setStretchLastSection(True)

            maxNofRxCh = parseDataList[0].antennaInfo.nofAntennas
            tablerow   = 0
            for graphname in graphInterList:
                for diagIdx in range(len(desiredDiagList)):
                    if 'evel' in graphname:
                        for rxch in range(maxNofRxCh):
                            qt.SysDiaInterTableParam.insertRow(tablerow)

                            # Graph
                            tableItem = qt.QTableWidgetItem()
                            tableItem.setData(qt.Qt.DisplayRole, 'Off')
                            tableItem.setData(qt.Qt.UserRole, -1)
                            tableItem.setFlags(qt.Qt.ItemIsEnabled)
                            qt.SysDiaInterTableParam.setItem(tablerow, qt.SysDiaInterTableParamColMapping['graph'], qt.QTableWidgetItem(tableItem))

                            # Axes
                            tableItem = qt.QTableWidgetItem()
                            tableItem.setData(qt.Qt.DisplayRole, 'ax1')
                            tableItem.setData(qt.Qt.UserRole, 1)
                            tableItem.setFlags(qt.Qt.ItemIsEnabled)
                            qt.SysDiaInterTableParam.setItem(tablerow, qt.SysDiaInterTableParamColMapping['axis'], qt.QTableWidgetItem(tableItem))

                            # Measurement Name
                            tableItem = qt.QTableWidgetItem()
                            tableItem.setData(0, str(graphname) + 'Ant' + str(rxch) + '_Diagram' + str(diagIdx))
                            qt.SysDiaInterTableParam.setItem(tablerow, qt.SysDiaInterTableParamColMapping['MeasurementName'], tableItem)
                        
                            # Add number of rows
                            tablerow += 1
                    else:
                        for rxch in range(maxNofRxCh - 1):
                            qt.SysDiaInterTableParam.insertRow(tablerow)

                            # Graph
                            tableItem = qt.QTableWidgetItem()
                            tableItem.setData(qt.Qt.DisplayRole, 'Off')
                            tableItem.setData(qt.Qt.UserRole, -1)
                            tableItem.setFlags(qt.Qt.ItemIsEnabled)
                            qt.SysDiaInterTableParam.setItem(tablerow, qt.SysDiaInterTableParamColMapping['graph'], qt.QTableWidgetItem(tableItem))

                            # Axes
                            tableItem = qt.QTableWidgetItem()
                            tableItem.setData(qt.Qt.DisplayRole, 'ax1')
                            tableItem.setData(qt.Qt.UserRole, 1)
                            tableItem.setFlags(qt.Qt.ItemIsEnabled)
                            qt.SysDiaInterTableParam.setItem(tablerow, qt.SysDiaInterTableParamColMapping['axis'], qt.QTableWidgetItem(tableItem))

                            # Measurement Name
                            tableItem = qt.QTableWidgetItem()
                            tableItem.setData(0, str(graphname)+ 'Ant' + str(rxch)+ '_Diagram' + str(diagIdx))
                            qt.SysDiaInterTableParam.setItem(tablerow, qt.SysDiaInterTableParamColMapping['MeasurementName'], tableItem)
                        
                            # Add number of rows
                            tablerow += 1

            qt.SysDiaInterTableParamHeader.setSectionResizeMode(qt.QHeaderView.Interactive)
            qt.SysDiaInterTableParamHeader.setStretchLastSection(True)
    else:
        myLogger.error('No parsed PTU2 files found!')

def SysDiaInterTableParamCellClicked(row, col):
    parseDataList          = parseData['parseDataList']
    antennaTypesList       = dp.getAntennaTypesList(parseDataList)
    ptu2ListPerAntennaType = dp.getPtu2ListPerAntennaType(antennaTypesList[0], parseDataList)
    dateTimeSensorList     = dp.getDateTimeSensorCombList(antennaTypesList[0], ptu2ListPerAntennaType)
    desiredDiagList        = dp.getDiagramList(antennaTypesList[0], parseDataList)
    ylimits0    = []
    ylimits1    = []
    ylimitssec0 = []
    ylimitssec1 = []
    if col == 0:
        # Table parameters
        item           = qt.SysDiaInterTableParam.item(row, col)
        graphIndex     = item.data(qt.Qt.UserRole)
        graphNameItem  = qt.SysDiaInterTableParam.item(row, 2)
        graphNameTable = graphNameItem.data(qt.Qt.DisplayRole)
        # Rx_Channel or Ant and parameter to plot
        rxCh      = re.findall(r'\d+', graphNameTable)
        diagIdx   = int(rxCh[1])
        rxCh      = int(rxCh[0])
        graphName = graphNameTable.replace('Ant', '').replace('_Diagram', '')
        graphType = re.sub(r'[0-9]+', '', graphName)
        AntChan   = graphType +'Ant'+ str(rxCh)
        Diag      = 'Diagram' + str(diagIdx)
 
        axisItem = qt.SysDiaInterTableParam.item(row, qt.SysDiaInterTableParamColMapping['axis'])
        ax = axisItem.data(qt.Qt.UserRole)

        if graphIndex != -1:
            for idx in reversed(range(0, len(RePlot['x']))):
                if AntChan in RePlot['label'][idx] and Diag in RePlot['label'][idx]:
                    del RePlot['x'][idx]
                    del RePlot['y'][idx]
                    del RePlot['label'][idx]
                    del RePlot['graphtype'][idx]
            for idx in reversed(range(0, len(RePlot['xsec']))):
                if AntChan in RePlot['labelsec'][idx] and Diag in RePlot['labelsec'][idx]:
                    del RePlot['xsec'][idx]
                    del RePlot['ysec'][idx]
                    del RePlot['labelsec'][idx]
                    del RePlot['graphtypesec'][idx]

            # parameter table
            item.setBackground(qt.QBrush(qt.QColor('white')))
            item.setForeground(qt.QBrush(qt.QColor('black')))
            axisItem.setForeground(qt.QBrush(qt.QColor('black')))


            strVal = 'Off'
            item.setText(strVal)
            if ax == 1:
                for lineIndex in reversed(range(len(qt.SysDiaInterPlotFrame.ax1.lines))):
                    if AntChan in qt.SysDiaInterPlotFrame.ax1.lines[lineIndex].get_label() \
                        and Diag in qt.SysDiaInterPlotFrame.ax1.lines[lineIndex].get_label():
                        qt.SysDiaInterPlotFrame.ax1.lines[lineIndex].remove()

            else:
                for lineIndex in reversed(range(len(qt.SysDiaInterPlotFrame.ax2.lines))):
                    if AntChan in qt.SysDiaInterPlotFrame.ax2.lines[lineIndex].get_label() \
                        and Diag in qt.SysDiaInterPlotFrame.ax2.lines[lineIndex].get_label():
                        qt.SysDiaInterPlotFrame.ax2.lines[lineIndex].remove()

            # rescaling
            for lineIndex in range(len(qt.SysDiaInterPlotFrame.ax1.lines)):
                ylimits0.append(min(qt.SysDiaInterPlotFrame.ax1.lines[lineIndex]._yorig))
                ylimits1.append(max(qt.SysDiaInterPlotFrame.ax1.lines[lineIndex]._yorig))
            if len(ylimits0) != 0:
                if min(ylimits0) >= 1:
                    ylimits0 = min(ylimits0) - 10
                elif min(ylimits0) < 1:
                    ylimits0 = min(ylimits0) - 5
                if max(ylimits1) >= 1:
                    ylimits1 = max(ylimits1) + 10
                elif max(ylimits1) < 1:
                    ylimits1 = max(ylimits1) + 5
                qt.SysDiaInterPlotFrame.ax1.set_ylim(ymin = ylimits0, ymax = ylimits1)

            # rescaling
            for lineIndex in range(len(qt.SysDiaInterPlotFrame.ax2.lines)):
                ylimitssec0.append(min(qt.SysDiaInterPlotFrame.ax2.lines[lineIndex]._yorig))
                ylimitssec1.append(max(qt.SysDiaInterPlotFrame.ax2.lines[lineIndex]._yorig))
            if len(ylimitssec0) != 0:
                if min(ylimitssec0) >= 1:
                    ylimitssec0 = min(ylimitssec0) - 10
                elif min(ylimitssec0) < 1:
                    ylimitssec0 = min(ylimitssec0) - 5
                if max(ylimitssec1) >= 1:
                    ylimitssec1 = max(ylimitssec1) + 10
                elif max(ylimitssec1) < 1:
                    ylimitssec1 = max(ylimitssec1) + 5
                qt.SysDiaInterPlotFrame.ax2.set_ylim(ymin = ylimitssec0, ymax = ylimitssec1)

            # scaling the axes
            qt.SysDiaInterPlotFrame.canvas.draw()
            item.setData(qt.Qt.DisplayRole, strVal)
            item.setData(qt.Qt.UserRole, -1)

        else:
            graphIndex = getGraphIndex()

            item.setBackground(qt.QBrush(qt.QColor('green')))
            item.setForeground(qt.QBrush(qt.QColor('black')))


            item.setText('On')
            item.setData(qt.Qt.UserRole, graphIndex)


            if ax == 1:
                axisItem.setForeground(qt.QBrush(qt.QColor('blue')))
            else:
                axisItem.setForeground(qt.QBrush(qt.QColor('red')))

            for pdIdx in range(len(parseDataList)):
                angBiggerThan45 = 0

                for dtsIdx in range(len(dateTimeSensorList)):
                    if desiredDiagList[diagIdx] == parseDataList[pdIdx].fileTitle.diagram and dateTimeSensorList[dtsIdx]['sensor'] == parseDataList[pdIdx].fileTitle.sensor and \
                            dateTimeSensorList[dtsIdx]['dateAndTime'] == parseDataList[pdIdx].fileTitle.dateAndTime:
                        
                        # lable for interactive modus
                        label = parseDataList[pdIdx].fileTitle.fileNamePath \
                            +'_'+ AntChan + '_Diagram' + str(diagIdx)
                        # Get the ptu angle for the specific PTU2 file
                        angle = plt.getAngle(parseDataList, pdIdx)

                        # Get the ptu angle for the specific PTU2 file
                        tarAngle = plt.getTargetAngle(plotSetup, parseDataList, pdIdx)

                        # Set xticks according to the angle values from files a plot contains
                        if abs(angle[0]) > 45:
                            angBiggerThan45 = 1

                        if angBiggerThan45 != 1:
                            plot.xticks(np.arange(90, -91, -5))
                        else:
                            plot.xticks(np.arange(90, -91, -10))

                        # Get the valid chirp list
                        validChirpList = dp.getValidChirp(chirpConfig, parseDataList, pdIdx)

                        # Processing for average function graphs
                        if plt.isAvgDiagram(graphType) == True:
                            # Get the actual graph data for specific Rx channel, chirp and a PTU2 file
                            actualGraphData = plt.getActualGraphData(graphType, rxCh, 0, parseDataList, pdIdx)
                        else:
                            # Traverse through the valid chirps
                            for chirp in range(len(validChirpList)):
                                # Get the actual graph data for specific Rx channel, chirp and a PTU2 file
                                actualGraphData = plt.getActualGraphData(graphType, rxCh, chirp, parseDataList, pdIdx)

                        # autoscale
                        qt.SysDiaInterPlotFrame.ax1.autoscale(enable = 'True')
                        # Set the x-axis label
                        qt.SysDiaInterPlotFrame.ax1.set_xlabel('PTU Angle [°]')

                        if plotSetup['targetAngle'] == 1:
                            angle = tarAngle
                            qt.SysDiaInterPlotFrame.ax1.set_xlabel('Target Angle [°]')
                        if ax == 1:
                            RePlot['x'].append(angle)
                            RePlot['y'].append(actualGraphData)
                            RePlot['label'].append(label)
                            RePlot['graphtype'].append(graphType)
                        else:
                            RePlot['xsec'].append(angle)
                            RePlot['ysec'].append(actualGraphData)
                            RePlot['labelsec'].append(label)
                            RePlot['graphtypesec'].append(graphType)
                        qt.SysDiaInterPlotFrame.plot(angle, actualGraphData, label, graphType, dtsIdx, ax)

    elif col == 1:
        graphNameItem  = qt.SysDiaInterTableParam.item(row,  qt.SysDiaInterTableParamColMapping['MeasurementName'])
        graphNameTable = graphNameItem.data(qt.Qt.DisplayRole)

        # Rx_Channel or Ant
        rxCh = re.findall(r'\d+', graphNameTable)
        diagIdx = int(rxCh[1])
        rxCh = int(rxCh[0])
        graphName = graphNameTable.replace('Ant', '').replace('_Diagram', '')
        graphType = re.sub(r'[0-9]+', '', graphName)
        AntChan = graphType +'Ant'+ str(rxCh)
        Diag = 'Diagram' + str(diagIdx)

        axisItem = qt.SysDiaInterTableParam.item(row, col)
        ax = axisItem.data(qt.Qt.UserRole)
        axLabel = axisItem.data(qt.Qt.DisplayRole)

        if ax == 1:
            axisItem.setData(qt.Qt.UserRole, 2)
            axisItem.setData(qt.Qt.DisplayRole, 'ax2')
            axisItem.setForeground(qt.QBrush(qt.QColor('red')))

            for lineIndex in reversed(range(len(qt.SysDiaInterPlotFrame.ax1.lines))):
                if AntChan in qt.SysDiaInterPlotFrame.ax1.lines[lineIndex].get_label() \
                    and Diag in qt.SysDiaInterPlotFrame.ax1.lines[lineIndex].get_label():
                    xData = qt.SysDiaInterPlotFrame.ax1.lines[lineIndex].get_xdata()
                    yData = qt.SysDiaInterPlotFrame.ax1.lines[lineIndex].get_ydata()
                    label = qt.SysDiaInterPlotFrame.ax1.lines[lineIndex].get_label()
                    qt.SysDiaInterPlotFrame.ax1.lines[lineIndex].remove()
                    qt.SysDiaInterPlotFrame.plot(xData, yData, label, graphType, lineIndex, 2)
        
        elif ax == 2:

            axisItem.setData(qt.Qt.UserRole, 1)
            axisItem.setData(qt.Qt.DisplayRole, 'ax1')
            axisItem.setForeground(qt.QBrush(qt.QColor('blue')))


            for lineIndex in reversed(range(len(qt.SysDiaInterPlotFrame.ax2.lines))):
                if AntChan in qt.SysDiaInterPlotFrame.ax2.lines[lineIndex].get_label() \
                    and Diag in qt.SysDiaInterPlotFrame.ax2.lines[lineIndex].get_label():
                    xData = qt.SysDiaInterPlotFrame.ax2.lines[lineIndex].get_xdata()
                    yData = qt.SysDiaInterPlotFrame.ax2.lines[lineIndex].get_ydata()
                    label = qt.SysDiaInterPlotFrame.ax2.lines[lineIndex].get_label()
                    qt.SysDiaInterPlotFrame.ax2.lines[lineIndex].remove()
                    qt.SysDiaInterPlotFrame.plot(xData, yData, label, graphType, lineIndex, 1)

def SysDiaInterTableProtCellClicked(row, col):
    if col == 0:
        # Table of protocols
        # True or false Check
        graphCheck = qt.SysDiaInterTableProtocol.item(row, col)
        graphNameCheck = graphCheck.data(qt.Qt.DisplayRole)
        # extract name of protocol
        item = qt.SysDiaInterTableProtocol.item(row, col)
        graphNameItem = qt.SysDiaInterTableProtocol.item(row, 1)
        graphNameTable = graphNameItem.data(qt.Qt.UserRole)  # sensor substring (e.g. 'rf12345_dsp67890')
        if graphNameCheck == 'False':
            # protocols table
            item.setBackground(qt.QBrush(qt.QColor('green')))
            item.setForeground(qt.QBrush(qt.QColor('white')))
            item.setText('True')
            # ax1
            for idx in range(0, len(RePlot['x'])):
                if graphNameTable in RePlot['label'][idx]:
                    qt.SysDiaInterPlotFrame.plot(RePlot['x'][idx], RePlot['y'][idx], RePlot['label'][idx], RePlot['graphtype'][idx], idx, 1, draw=False)
            # ax2
            for idx in range(0, len(RePlot['xsec'])):
                if graphNameTable in RePlot['labelsec'][idx]:
                    qt.SysDiaInterPlotFrame.plot(RePlot['xsec'][idx], RePlot['ysec'][idx], RePlot['labelsec'][idx], RePlot['graphtypesec'][idx], idx, 2, draw=False)
            # single draw after all lines added
            qt.SysDiaInterPlotFrame.canvas.draw()
        else:
            # remove ax1
            for lineIndex in reversed(range(len(qt.SysDiaInterPlotFrame.ax1.lines))):
                # removing lines
                if graphNameTable in qt.SysDiaInterPlotFrame.ax1.lines[lineIndex].get_label():
                    qt.SysDiaInterPlotFrame.ax1.lines[lineIndex].remove()
            # remove ax2
            for lineIndex in reversed(range(len(qt.SysDiaInterPlotFrame.ax2.lines))):
                # removing lines
                if graphNameTable in qt.SysDiaInterPlotFrame.ax2.lines[lineIndex].get_label():
                    qt.SysDiaInterPlotFrame.ax2.lines[lineIndex].remove()
            item.setBackground(qt.QBrush(qt.QColor('white')))
            item.setForeground(qt.QBrush(qt.QColor('black')))
            item.setText('False')
            qt.SysDiaInterPlotFrame.canvas.draw()

# ---------------------------------------------------------------------------
# Batch toggle-off helper (no dp.* calls needed, single canvas.draw)
# ---------------------------------------------------------------------------
def _batch_turn_off(on_rows):
    """Remove all currently-On rows from the plot in a single pass."""
    for row in on_rows:
        item          = qt.SysDiaInterTableParam.item(row, 0)
        axisItem      = qt.SysDiaInterTableParam.item(row, qt.SysDiaInterTableParamColMapping['axis'])
        graphNameItem = qt.SysDiaInterTableParam.item(row, 2)
        graphNameTable = graphNameItem.data(qt.Qt.DisplayRole)
        rxNums    = re.findall(r'\d+', graphNameTable)
        diagIdx   = int(rxNums[1])
        rxCh      = int(rxNums[0])
        graphName = graphNameTable.replace('Ant', '').replace('_Diagram', '')
        graphType = re.sub(r'[0-9]+', '', graphName)
        AntChan   = graphType + 'Ant' + str(rxCh)
        Diag      = 'Diagram' + str(diagIdx)
        ax        = axisItem.data(qt.Qt.UserRole) if axisItem else 1

        # Clear matching entries from the RePlot buffer
        for idx in reversed(range(len(RePlot['x']))):
            if AntChan in RePlot['label'][idx] and Diag in RePlot['label'][idx]:
                del RePlot['x'][idx]
                del RePlot['y'][idx]
                del RePlot['label'][idx]
                del RePlot['graphtype'][idx]
        for idx in reversed(range(len(RePlot['xsec']))):
            if AntChan in RePlot['labelsec'][idx] and Diag in RePlot['labelsec'][idx]:
                del RePlot['xsec'][idx]
                del RePlot['ysec'][idx]
                del RePlot['labelsec'][idx]
                del RePlot['graphtypesec'][idx]

        # Remove matching lines from the axes
        if ax == 1:
            for li in reversed(range(len(qt.SysDiaInterPlotFrame.ax1.lines))):
                if AntChan in qt.SysDiaInterPlotFrame.ax1.lines[li].get_label() \
                        and Diag in qt.SysDiaInterPlotFrame.ax1.lines[li].get_label():
                    qt.SysDiaInterPlotFrame.ax1.lines[li].remove()
        else:
            for li in reversed(range(len(qt.SysDiaInterPlotFrame.ax2.lines))):
                if AntChan in qt.SysDiaInterPlotFrame.ax2.lines[li].get_label() \
                        and Diag in qt.SysDiaInterPlotFrame.ax2.lines[li].get_label():
                    qt.SysDiaInterPlotFrame.ax2.lines[li].remove()

        # Update table item
        item.setBackground(qt.QBrush(qt.QColor('white')))
        item.setForeground(qt.QBrush(qt.QColor('black')))
        item.setText('Off')
        item.setData(qt.Qt.DisplayRole, 'Off')
        item.setData(qt.Qt.UserRole, -1)
        if axisItem:
            axisItem.setForeground(qt.QBrush(qt.QColor('black')))

    # Rescale axes once after all removals
    ylimits0    = [min(qt.SysDiaInterPlotFrame.ax1.lines[i]._yorig)
                   for i in range(len(qt.SysDiaInterPlotFrame.ax1.lines))]
    ylimits1    = [max(qt.SysDiaInterPlotFrame.ax1.lines[i]._yorig)
                   for i in range(len(qt.SysDiaInterPlotFrame.ax1.lines))]
    ylimitssec0 = [min(qt.SysDiaInterPlotFrame.ax2.lines[i]._yorig)
                   for i in range(len(qt.SysDiaInterPlotFrame.ax2.lines))]
    ylimitssec1 = [max(qt.SysDiaInterPlotFrame.ax2.lines[i]._yorig)
                   for i in range(len(qt.SysDiaInterPlotFrame.ax2.lines))]

    if ylimits0:
        qt.SysDiaInterPlotFrame.ax1.set_ylim(
            ymin=min(ylimits0) - (10 if min(ylimits0) >= 1 else 5),
            ymax=max(ylimits1) + (10 if max(ylimits1) >= 1 else 5))
    if ylimitssec0:
        qt.SysDiaInterPlotFrame.ax2.set_ylim(
            ymin=min(ylimitssec0) - (10 if min(ylimitssec0) >= 1 else 5),
            ymax=max(ylimitssec1) + (10 if max(ylimitssec1) >= 1 else 5))

    qt.SysDiaInterPlotFrame.canvas.draw()


# ---------------------------------------------------------------------------
# Background worker for TurnOnOff
# ---------------------------------------------------------------------------
class _TurnOnWorker(qt.QThread):
    """Computes plot data for all 'Off' rows; runs off the main thread."""
    batch_ready = qt.Signal(list)

    def __init__(self, row_params):
        super().__init__()
        self._row_params = row_params

    def run(self):
        parseDataList = list(parseData['parseDataList'])  # snapshot
        if not parseDataList:
            self.batch_ready.emit([])
            return

        antennaTypesList   = dp.getAntennaTypesList(parseDataList)
        ptu2List           = dp.getPtu2ListPerAntennaType(antennaTypesList[0], parseDataList)
        dateTimeSensorList = dp.getDateTimeSensorCombList(antennaTypesList[0], ptu2List)
        desiredDiagList    = dp.getDiagramList(antennaTypesList[0], parseDataList)

        batch = []
        for rp in self._row_params:
            row        = rp['row']
            graphIndex = rp['graphIndex']
            diagIdx    = rp['diagIdx']
            rxCh       = rp['rxCh']
            graphType  = rp['graphType']
            AntChan    = rp['AntChan']
            ax         = rp['ax']

            for pdIdx in range(len(parseDataList)):
                angBiggerThan45 = 0
                for dtsIdx in range(len(dateTimeSensorList)):
                    if (desiredDiagList[diagIdx] == parseDataList[pdIdx].fileTitle.diagram
                            and dateTimeSensorList[dtsIdx]['sensor'] == parseDataList[pdIdx].fileTitle.sensor
                            and dateTimeSensorList[dtsIdx]['dateAndTime'] == parseDataList[pdIdx].fileTitle.dateAndTime):

                        label    = (parseDataList[pdIdx].fileTitle.fileNamePath
                                    + '_' + AntChan + '_Diagram' + str(diagIdx))
                        angle    = plt.getAngle(parseDataList, pdIdx)
                        tarAngle = plt.getTargetAngle(plotSetup, parseDataList, pdIdx)

                        if abs(angle[0]) > 45:
                            angBiggerThan45 = 1

                        validChirpList = dp.getValidChirp(chirpConfig, parseDataList, pdIdx)

                        if plt.isAvgDiagram(graphType):
                            actualGraphData = plt.getActualGraphData(graphType, rxCh, 0, parseDataList, pdIdx)
                        else:
                            actualGraphData = None
                            for chirp in range(len(validChirpList)):
                                actualGraphData = plt.getActualGraphData(graphType, rxCh, chirp, parseDataList, pdIdx)

                        if plotSetup['targetAngle'] == 1:
                            angle = tarAngle

                        batch.append((row, graphIndex, ax, angle, actualGraphData,
                                      label, graphType, dtsIdx, angBiggerThan45))

        self.batch_ready.emit(batch)


_turn_on_thread = None  # module-level reference prevents GC while thread runs


def _apply_batch_turn_on(batch):
    """Main-thread slot: applies computed lines to the plot and updates the table."""
    global _turn_on_thread

    seen_rows = {}   # row → (graphIndex, ax)
    ang_big   = False

    for (row, graphIndex, ax, angle, actualGraphData,
         label, graphType, dtsIdx, angBiggerThan45) in batch:

        if actualGraphData is None:
            continue

        if angBiggerThan45:
            ang_big = True

        # Buffer for protocol-table redraw
        if ax == 1:
            RePlot['x'].append(angle)
            RePlot['y'].append(actualGraphData)
            RePlot['label'].append(label)
            RePlot['graphtype'].append(graphType)
        else:
            RePlot['xsec'].append(angle)
            RePlot['ysec'].append(actualGraphData)
            RePlot['labelsec'].append(label)
            RePlot['graphtypesec'].append(graphType)

        qt.SysDiaInterPlotFrame.ax1.autoscale(enable='True')
        qt.SysDiaInterPlotFrame.ax1.set_xlabel(
            'Target Angle [°]' if plotSetup['targetAngle'] == 1 else 'PTU Angle [°]')

        # draw=False defers canvas refresh until the entire batch is plotted
        qt.SysDiaInterPlotFrame.plot(angle, actualGraphData, label, graphType, dtsIdx, ax, draw=False)

        if row not in seen_rows:
            seen_rows[row] = (graphIndex, ax)

    # Apply x-ticks and do a single canvas refresh after all lines are added
    plot.xticks(np.arange(90, -91, -10) if ang_big else np.arange(90, -91, -5))
    qt.SysDiaInterPlotFrame.canvas.draw()

    # Update table items — Qt widget access must happen on the main thread
    for row, (graphIndex, ax) in seen_rows.items():
        item     = qt.SysDiaInterTableParam.item(row, 0)
        axisItem = qt.SysDiaInterTableParam.item(row, qt.SysDiaInterTableParamColMapping['axis'])
        if item:
            item.setBackground(qt.QBrush(qt.QColor('green')))
            item.setForeground(qt.QBrush(qt.QColor('black')))
            item.setText('On')
            item.setData(qt.Qt.UserRole, graphIndex)
        if axisItem:
            axisItem.setForeground(qt.QBrush(
                qt.QColor('blue') if ax == 1 else qt.QColor('red')))

    qt.SysDiaInterSwitchBtn.setEnabled(True)
    _turn_on_thread = None


# Turn on and off the plots
def TurnOnOff():
    global _turn_on_thread

    n_rows = qt.SysDiaInterTableParam.rowCount()
    if n_rows == 0:
        return

    on_rows  = []  # rows currently 'On' — toggle off in one batch
    off_rows = []  # rows currently 'Off' — toggle on via thread

    for row in range(n_rows):
        item = qt.SysDiaInterTableParam.item(row, 0)
        if item is None:
            continue
        if item.data(qt.Qt.UserRole) != -1:
            on_rows.append(row)
        else:
            # Collect all row params here; Qt widget reads must stay on the main thread
            graphNameItem  = qt.SysDiaInterTableParam.item(row, 2)
            graphNameTable = graphNameItem.data(qt.Qt.DisplayRole)
            rxNums    = re.findall(r'\d+', graphNameTable)
            diagIdx   = int(rxNums[1])
            rxCh      = int(rxNums[0])
            graphName = graphNameTable.replace('Ant', '').replace('_Diagram', '')
            graphType = re.sub(r'[0-9]+', '', graphName)
            AntChan   = graphType + 'Ant' + str(rxCh)
            axisItem  = qt.SysDiaInterTableParam.item(
                row, qt.SysDiaInterTableParamColMapping['axis'])
            ax = axisItem.data(qt.Qt.UserRole) if axisItem else 1
            off_rows.append({
                'row':        row,
                'graphIndex': getGraphIndex(),
                'diagIdx':    diagIdx,
                'rxCh':       rxCh,
                'graphType':  graphType,
                'AntChan':    AntChan,
                'ax':         ax,
            })

    # Batch all 'On'→'Off' removals with a single canvas.draw()
    if on_rows:
        _batch_turn_off(on_rows)

    # Toggle-On: run in background thread to avoid UI freeze
    if not off_rows:
        return

    # Disable the button to prevent re-entry while the thread runs
    qt.SysDiaInterSwitchBtn.setEnabled(False)
    _turn_on_thread = _TurnOnWorker(off_rows)
    _turn_on_thread.batch_ready.connect(_apply_batch_turn_on)
    _turn_on_thread.start()


def ClearData():
    RePlot['x']            = []
    RePlot['y']            = []
    RePlot['label']        = []
    RePlot['graphtype']    = []
    RePlot['xsec']         = []
    RePlot['ysec']         = []
    RePlot['labelsec']     = []
    RePlot['graphtypesec'] = []
    qt.SysDiaInterTableParam.clearContents()
    qt.SysDiaInterTableParam.setRowCount(0)
    qt.SysDiaInterTableProtocol.clearContents()
    qt.SysDiaInterTableProtocol.setRowCount(0)
    qt.SysDiaInterPlotFrame.clear()

# Start data evaluation
def start_data_evaluation(parseDataList, plotSetup, chirpConfig, graphConfig, diagramConfig, twoGraphSetupList, fourGraphSetupList, threeGraphSetupList, allOnOneSlideGraphList, diagramConfigList, sysDiagLogger, output_pathpptx, pptxTitle, starttemp):
    # Output path
    outputPath = aux.antSysDiagOutputPath

    # Create directory if doesnt exist
    crDirStatus, crDirErrorString = aux.createDirectory(outputPath)
    # clear_output(wait=True)
    # if os.name=='nt':
    #     _=os.system('cls')
    # else:
    #     _=os.system('clear')

    myLogger = sysDiagLogger.logger

    errorStatus, errorSting = sysDiagLogger.addFileHandler(logconfig.antSysDiagLogFilePath, 'w+')
    if errorStatus == 1:
        myLogger.warning(errorSting)
    myLogger.info('Starting.')

    if not crDirStatus:
        myLogger.error(crDirErrorString)
        return

    # Clear the output folder
    clearDataStatus, clearDataString = aux.clearAll(aux.antSysDiagOutputPath)
    if not clearDataStatus:
        myLogger.error(clearDataString)
        return

    # Clear the output folder
    if plotSetup['ShowCertainPlotWindow'] == 0:
        clearDataStatus,clearDataString = aux.clearAll(aux.antSysDiagOutputPath)
        if not clearDataStatus:
            myLogger.error(clearDataString)
            return

    # Load Data by absolute path
    # myLogger.info('Loading data.')
    # if isinstance(absPath, dict):
    #     parseDataList = ld.LoadData(absPath['filePathList'])
    # else:
    #     parseDataList = ld.LoadData(absPath)

    if len(parseDataList) == 0:
        
        # Copying the LogFile to the output directory
        myLogger.error('No parsed PTU2 files found!')
        
        # generating presentation with separation sheet and log error
        pptxPath = os.path.join(output_pathpptx, pptxTitle)
        prs = pp.Presentation(starttemp)
        of_layout = pp.OneFieldLayout()
        ss_layout = pp.SeparationSheet()
        logFileOutputPath = os.path.join(aux.antSysDiagOutputPath, logconfig.LogFileNames.AntennaSystemDiagrams.value)
        status,errorSting = aux.copyFile(logconfig.antSysDiagLogFilePath, logFileOutputPath)
        if not  status:
            myLogger.warning(errorSting)
        loadDataLogFileOutputPath = os.path.join(aux.antSysDiagOutputPath, logconfig.LogFileNames.MainLoadData.value)
        status, errorSting = aux.copyFile(logconfig.mainLoadDataLogFilePath, loadDataLogFileOutputPath)
        if not  status:
            myLogger.warning(errorSting)
        
        # reading log files
        log_file = logconfig.antSysDiagLogFilePath
        with open(log_file, 'r') as logmessages:
            content = logmessages.readlines()
            error_mesg = 0
            warning_mesg = 0
            for line in content:
                if 'ERROR' in line:
                    error_mesg += 1
                if 'WARN' in line:
                    warning_mesg += 1
        
        # error messages
        of_layout = prs.add_slide(of_layout)
        of_layout.title.text = 'Antenna system diagrams'
        of_layout.titletext.text = 'Warnings and Errors'
        of_layout.text.text = 'Total Number of Warning messages: ' + str(warning_mesg) + '\n' + \
            'Total Number of Error messages: ' + str(error_mesg)
        
        # sepration sheet
        ss_layout = prs.add_slide(ss_layout)
        ss_layout.title.text = 'Antenna system diagrams'
        ss_layout.text.text  = 'Antenna system diagrams'
        prs.save(pptxPath)

        if os.path.exists(output_pathpptx):
            try:
                compptx  = os.path.join(output_pathpptx, 'combine.pptx')
                compptx1 = os.path.join(output_pathpptx, 'combine1.pptx')
                compptx2 = os.path.join(output_pathpptx, 'combine2.pptx')
                os.remove(compptx)
                os.remove(compptx1)
                os.remove(compptx2)
            except OSError:
                return
        return

    picker = 0
    plotAllPicker = 0
    parsedPlotWindowStringDict = 0
    graphData = 0

    if plotSetup['ShowCertainPlotWindow'] == 1:
        picker = 1
        if plotWindowConfig['inputMode'] == 0:
            parsedPlotWindowStringDict = dp.parsePlotWindowString(plotWindowConfig['string'])
        if plotWindowConfig['showPlotAllMode'] == 1:
            plotAllPicker = 1


    if plotSetup['ShowCertainPlotWindow'] == 0:
        # Title of the generated output .pptx file
        # pptxTitle = 'Antenna_diagrams.pptx'

        # pptx. save path
        pptxPath = os.path.join(output_pathpptx, pptxTitle)

        # Initialise PowerPoint presentation and specific layout objects
        prs = pp.Presentation(starttemp)
        if prs.openStatus == False:
            myLogger.error(prs.openStatusString)
            return
        else:
            myLogger.info('PPTX writing starts: ' +pptxTitle)
            legend_graph = pp.OneGraphLayout()
            ss_layout    = pp.SeparationSheet()
            tgLayout     = pp.TwoGraphLayout()
            fgLayout     = pp.FourGraphLayout()
            trgLayout    = pp.ThreeGraphLayout()
            llLayout     = pp.SensorListAndLegend()
            ot_layout    = pp.OnlyTableLayout()
            of_layout    = pp.OneFieldLayout()

    

    # List of all configured graph types
    graphList = plt.getGraphList(graphConfig)
    if len(graphList) == 0:
        
        # Copying the LogFile to the output directory
        myLogger.error('No graphs configured!')
        logFileOutputPath = os.path.join(aux.antSysDiagOutputPath, logconfig.LogFileNames.AntennaSystemDiagrams.value)
        status,errorSting = aux.copyFile(logconfig.antSysDiagLogFilePath, logFileOutputPath)
        if not  status:
            myLogger.warning(errorSting)
        loadDataLogFileOutputPath = os.path.join(aux.antSysDiagOutputPath, logconfig.LogFileNames.MainLoadData.value)
        status, errorSting = aux.copyFile(logconfig.mainLoadDataLogFilePath, loadDataLogFileOutputPath)
        if not  status:
            myLogger.warning(errorSting)

    # Antenna types list
    antennaTypesList = dp.getAntennaTypesList(parseDataList)
    if len(antennaTypesList) == 0:
        
        # Copying the LogFile to the output directory
        myLogger.error('Empty Antenna types list!')
        logFileOutputPath = os.path.join(aux.antSysDiagOutputPath, logconfig.LogFileNames.AntennaSystemDiagrams.value)
        status,errorSting = aux.copyFile(logconfig.antSysDiagLogFilePath, logFileOutputPath)
        if not  status:
            myLogger.warning(errorSting)
        loadDataLogFileOutputPath = os.path.join(aux.antSysDiagOutputPath, logconfig.LogFileNames.MainLoadData.value)
        status, errorSting = aux.copyFile(logconfig.mainLoadDataLogFilePath, loadDataLogFileOutputPath)
        if not  status:
            myLogger.warning(errorSting)

    # reading log files
    log_file = logconfig.antSysDiagLogFilePath
    with open(log_file, 'r') as logmessages:
        content = logmessages.readlines()
        error_mesg = 0
        warning_mesg = 0
        for line in content:
            if 'ERROR' in line:
                error_mesg += 1
            if 'WARN' in line:
                warning_mesg += 1


    for antTypeIdx in range(len(antennaTypesList)):

        ptu2ListPerAntennaType = dp.getPtu2ListPerAntennaType(antennaTypesList[antTypeIdx], parseDataList)
        
        myLogger.info('Antenna Type: '+ str(antennaTypesList[antTypeIdx])+' processing.')

        # Get the desired diagrams list
        desiredDiagramList = dp.getDesiredDiagramsList(diagramConfig, diagramConfigList, antennaTypesList[antTypeIdx], ptu2ListPerAntennaType)
        if len(desiredDiagramList) == 0:
            myLogger.error('Empty diagram list.')

        #list of date-time and sensor combination
        dateTimeSensorCombList = dp.getDateTimeSensorCombList(antennaTypesList[antTypeIdx], ptu2ListPerAntennaType)
        if len(dateTimeSensorCombList) != 0:
            myLogger.info('Num. of Sensor - Date and Time Comb. for Antenna Type ' + str(antennaTypesList[antTypeIdx]) + ': ' + str(len(dateTimeSensorCombList)) + '.')
        else:
            myLogger.error('Empty Date/Time - Sensor combination list for Antenna Type '+ str(antennaTypesList[antTypeIdx]) +'!')

        # Generate legend for sensor plot lines colors
        if len(dateTimeSensorCombList) != 0:
            plt.generateLegend(plotSetup, dateTimeSensorCombList)

        # List for cent. freq per diagram
        centFreqDictList = []

        # Get the scaling parameters for each graph
        lowerMarginDict = dict()
        # lowerMarginDictList=[]

        upperMarginDict = dict()
        # upperMarginDictList =[]

        if len(desiredDiagramList) != 0:
            for graphIdx in range(len(graphList)):
                if graphList[graphIdx] != 'diffPhaseDiff' and graphList[graphIdx] != 'avgDiffPhaseDiff':
                    if plotSetup['yLimitsAntTypeSeparately'] == 1:
                        lowerMargin = plt.scaleLowerMargin( graphList[graphIdx], chirpConfig, ptu2ListPerAntennaType)
                    else:
                        lowerMargin = plt.scaleLowerMargin( graphList[graphIdx], chirpConfig, parseDataList)

                    lowerMarginEntry = {graphList[graphIdx]:lowerMargin}
                    lowerMarginDict.update(lowerMarginEntry)

                    if plotSetup['yLimitsAntTypeSeparately'] == 1:
                        upperMargin = plt.scaleUpperMargin(graphList[graphIdx], chirpConfig,  ptu2ListPerAntennaType)
                    else:
                        upperMargin = plt.scaleUpperMargin(graphList[graphIdx], chirpConfig, parseDataList)

                    upperMarginEntry = {graphList[graphIdx]: upperMargin}
                    upperMarginDict.update(upperMarginEntry)
                    # scalingDict.update({graphList[graphIdx]:1})

                    # if graphList[graphIdx] == 'diffPhaseDiff' or graphList[graphIdx] =='avgDiffPhaseDiff':
        dictScalingDict = dict()

        if len(desiredDiagramList) != 0:
            for diagramIdx in range(len(desiredDiagramList)):
                centFreqDict = dict()
                scalingDict  = dict()
                for graphIdx in range(len(graphList)):
                    if graphList[graphIdx] == 'diffPhaseDiff':
                        # scaleDiffPhaseDiff=plt.scale('diffPhaseDiff',chirpConfig, plotSetup, parseDataList)
                        scaleDiffPhaseDiff = plt.scalePerDiagram('diffPhaseDiff', desiredDiagramList[diagramIdx], chirpConfig, plotSetup, ptu2ListPerAntennaType)
                        scalingEntry = {graphList[graphIdx]:scaleDiffPhaseDiff}
                        scalingDict.update(scalingEntry)

                        # lowerMarginDict.update({graphList[graphIdx]: -1})
                        # upperMarginDict.update({graphList[graphIdx]: 1})

                    if graphList[graphIdx] == 'avgDiffPhaseDiff':
                        # scaleAvgDiffPhaseDiff = plt.scale('avgDiffPhaseDiff', chirpConfig, plotSetup, parseDataList)
                        scaleAvgDiffPhaseDiff = plt.scalePerDiagram('avgDiffPhaseDiff', desiredDiagramList[diagramIdx], chirpConfig, plotSetup, ptu2ListPerAntennaType)
                        scalingEntry = {graphList[graphIdx]:scaleAvgDiffPhaseDiff}
                        scalingDict.update(scalingEntry)

                        # lowerMarginDict.update({graphList[graphIdx]: -1})
                        # upperMarginDict.update({graphList[graphIdx]: 1})
                diagramEntry = {desiredDiagramList[diagramIdx]:scalingDict}
                dictScalingDict.update(diagramEntry)

                # Get center frequency values
                avgFreq = dp.getAvgFreqPerDiagram(chirpConfig, desiredDiagramList[diagramIdx], ptu2ListPerAntennaType)
                minFreq = dp.getMinFreqPerDiagram(chirpConfig, desiredDiagramList[diagramIdx], ptu2ListPerAntennaType)
                maxFreq = dp.getMaxFreqPerDiagram(chirpConfig, desiredDiagramList[diagramIdx], ptu2ListPerAntennaType)
                posFreqDev = maxFreq - avgFreq
                negFreqDev = avgFreq - minFreq

                posFreqDevMHz = round((posFreqDev / 1e6), 4)
                negFreqDevMHz = round((negFreqDev / 1e6), 4)
                avgFreqGHz = round((avgFreq / 1e9), 4)

                posFreqDevMHz = format(posFreqDevMHz, '.2f')
                negFreqDevMHz = format(negFreqDevMHz, '.2f')
                avgFreqGHz = format(avgFreqGHz, '.2f')

                centFreqDict.update({'avgFreqGHz':avgFreqGHz, 'posFreqDevMHz':posFreqDevMHz, 'negFreqDevMHz':negFreqDevMHz})
                centFreqDictList.append(centFreqDict)

        # set parameter for three graph layout

        # if threeGraphSetupList!=0:
        #     plotSetup['threeGraphLayout']=1
        if len(dateTimeSensorCombList) != 0:
            if plotSetup['ShowCertainPlotWindow'] == 0:
                
                # error messages
                of_layout = prs.add_slide(of_layout)
                of_layout.title.text = 'Antenna system diagrams'
                of_layout.titletext.text = 'Warnings and Errors'
                of_layout.text.text = 'Total Number of Warning messages: ' + str(warning_mesg) + '\n' + \
                    'Total Number of Error messages: ' + str(error_mesg)
                
                # sepration sheet
                ss_layout = prs.add_slide(ss_layout)
                ss_layout.title.text = 'Antenna system diagrams'
                ss_layout.text.text  = 'Antenna system diagrams'
                if 'combine' not in starttemp:
                    
                    # Sensor List and Legend slide
                    alloneslide = prs.add_slide(legend_graph)
                    alloneslide.title.text = 'Antenna system diagrams - Type '+ str(antennaTypesList[antTypeIdx])

                    legendTitle = plt.legFigTitle
                    legendPath  = os.path.join(outputPath, legendTitle)
                    alloneslide.text.text  = 'Legends'
                    alloneslide.title.text = 'Antenna system diagrams'
                    alloneslide.image.insert_picture(legendPath)

                    # add total number of protocol tables
                    ot_slide = prs.add_slide(ot_layout)
                    ot_slide.title.text = 'Antenna system diagrams'
                    # Sensor list reshaping for listing in a table
                    dateTimeSensorCombTable = dateTimeSensorCombList.copy()
                    nofSensorMeas = len(dateTimeSensorCombTable)

                    if nofSensorMeas > plotSetup['nofSensorMeasToShow']:
                        dateTimeSensorCombTable = dateTimeSensorCombTable[:plotSetup['nofSensorMeasToShow']]
                        nofSensorMeas = len(dateTimeSensorCombTable)

                    maxNofRows = 16

                    nofColsFirstSlide = 2
                    maxNofSensorMeasFirstSlide = nofColsFirstSlide * maxNofRows

                    nofColsRestSlides = 3
                    maxNofSensorMeasRestSlides = nofColsRestSlides * maxNofRows

                    sensorMeasFirstSlideList = dateTimeSensorCombTable

                    nofRowsFirstSlide = maxNofRows
                    nofRowsRestSlides = maxNofRows
                    nofRestTables = 0

                    if nofSensorMeas <= maxNofSensorMeasFirstSlide:
                        if nofSensorMeas % nofColsFirstSlide == 0:
                            nofRowsFirstSlide = int(nofSensorMeas / nofColsFirstSlide)
                            sensorMeasFirstSlideList = np.reshape(sensorMeasFirstSlideList,
                                                                (nofRowsFirstSlide, nofColsFirstSlide))
                        else:
                            dateTimeSensorCombTable.append('')
                            nofRowsFirstSlide = int(nofSensorMeas / nofColsFirstSlide) + 1
                            sensorMeasFirstSlideList = np.reshape(sensorMeasFirstSlideList,
                                                                (nofRowsFirstSlide, nofColsFirstSlide))
                        # Table insertion
                        firstSlideTablePlaceholder = ot_slide.tablePlaceholder
                        firstSlideTablePlaceholder = firstSlideTablePlaceholder.insert_table(rows=nofRowsFirstSlide, cols=nofColsFirstSlide)
                        firstSlideTablePlaceholder = firstSlideTablePlaceholder.table

                        ot_slide.text.text = 'Sensor measurements list: 1 - ' + str(nofSensorMeas)

                        # Table filling
                        for row in range(nofRowsFirstSlide):
                            for col in range(nofColsFirstSlide):
                                cell = firstSlideTablePlaceholder.cell(row, col)
                                textFrame = cell.text_frame
                                paragraph = textFrame.paragraphs[0]
                                run = paragraph.add_run()
                                if sensorMeasFirstSlideList[row, col] != '':
                                    run.text = sensorMeasFirstSlideList[row, col]['dateAndTime'] + '_' + \
                                            sensorMeasFirstSlideList[row, col]['sensor']
                                    # run.text = sensorMeasFirstSlideList[row, col]
                                font = run.font
                                font.size = pptx.util.Pt(16)
                        myLogger.info('Sensors list table and legend slide inserted.')
                    else:

                        sensorMeasFirstSlideList = dateTimeSensorCombTable[:maxNofSensorMeasFirstSlide]
                        sensorMeasFirstSlideList = np.reshape(sensorMeasFirstSlideList, (nofRowsFirstSlide, nofColsFirstSlide))

                        # Table insertion
                        firstSlideTablePlaceholder = ot_slide.tablePlaceholder
                        firstSlideTablePlaceholder = firstSlideTablePlaceholder.insert_table(rows=nofRowsFirstSlide, cols=nofColsFirstSlide)
                        firstSlideTablePlaceholder = firstSlideTablePlaceholder.table

                        ot_slide.text.text = 'Sensor measurements list: 1 - ' + str(maxNofSensorMeasFirstSlide)

                        # Table filling
                        for row in range(nofRowsFirstSlide):
                            for col in range(nofColsFirstSlide):
                                cell = firstSlideTablePlaceholder.cell(row, col)
                                textFrame = cell.text_frame
                                paragraph = textFrame.paragraphs[0]
                                run = paragraph.add_run()
                                if sensorMeasFirstSlideList[row, col] != '':
                                    run.text = sensorMeasFirstSlideList[row, col]['dateAndTime'] + '_' + \
                                            sensorMeasFirstSlideList[row, col]['sensor']
                                    # run.text = sensorMeasFirstSlideList[row, col]
                                font = run.font
                                font.size = pptx.util.Pt(16)

                        nofRestTables = int(np.ceil((nofSensorMeas - maxNofSensorMeasFirstSlide) / maxNofSensorMeasRestSlides))

                        sensorMeasRestLists = []
                        sensorMeasRestWholeList = dateTimeSensorCombTable[maxNofSensorMeasFirstSlide:]

                        for i in range(nofRestTables):
                            # Rest Tables insertion
                            rtSlide = prs.add_slide(ot_layout)
                            rtSlide.title.text = 'Antenna system diagrams - Type ' + str(antennaTypesList[antTypeIdx])

                            start = i * maxNofSensorMeasRestSlides
                            stop  = start + maxNofSensorMeasRestSlides
                            sensorMeasRestList = sensorMeasRestWholeList[start:stop]

                            if i != (nofRestTables - 1):
                                rtSlide.text.text = 'Sensor measurements list: ' + str(
                                    start + maxNofSensorMeasFirstSlide + 1) + ' - ' + str(stop + maxNofSensorMeasFirstSlide)
                                sensorMeasRestList = np.reshape(sensorMeasRestList, (nofRowsRestSlides, nofColsRestSlides))

                            else:

                                rtSlide.text.text = 'Sensor measurements list: ' + str(
                                    start + maxNofSensorMeasFirstSlide + 1) + ' - ' + str(
                                    start + len(sensorMeasRestList) + maxNofSensorMeasFirstSlide)

                                residual = len(sensorMeasRestList) % nofColsRestSlides

                                if (residual) == 0:
                                    nofRowsRestSlides  = int(len(sensorMeasRestList) / nofColsRestSlides)
                                    sensorMeasRestList = np.reshape(sensorMeasRestList, (nofRowsRestSlides, nofColsRestSlides))
                                else:
                                    nofRowsRestSlides  = int(len(sensorMeasRestList) / nofColsRestSlides) + 1

                                    for j in range(nofColsRestSlides - residual):
                                        sensorMeasRestList.append('')

                                    sensorMeasRestList = np.reshape(sensorMeasRestList, (nofRowsRestSlides, nofColsRestSlides))


                            dim = np.shape(sensorMeasRestList)
                            nofRowsRestSlides = dim[0]

                            restSlidesTablePlaceholder = rtSlide.tablePlaceholder
                            restSlidesTablePlaceholder = restSlidesTablePlaceholder.insert_table(rows=nofRowsRestSlides, cols=nofColsRestSlides)
                            restSlidesTablePlaceholder = restSlidesTablePlaceholder.table
                            # Sensor List and Legend slide


                            # rtSlide.text.text = 'Sensor measurements list: ' +str(start+ maxNofSensorMeasFirstSlide +1) +' - '+str(stop + maxNofSensorMeasFirstSlide )

                            for row in range(nofRowsRestSlides):
                                for col in range(nofColsRestSlides):
                                    cell = restSlidesTablePlaceholder.cell(row, col)
                                    textFrame = cell.text_frame
                                    paragraph = textFrame.paragraphs[0]
                                    run = paragraph.add_run()
                                    if sensorMeasRestList[row, col] != '':
                                        run.text = sensorMeasRestList[row, col]['dateAndTime'] + '_' + \
                                                sensorMeasRestList[row, col]['sensor']
                                        # run.text = sensorMeasRestLists[slideIdx][row, col]
                                    font = run.font
                                    font.size = pptx.util.Pt(16)

            if len(desiredDiagramList) != 0:
                # Separate RxCh diagrams block
                if plotSetup['SeparateRxCh'] == 1:

                    # if plotSetup['ShowCertainPlotWindow'] == 1:
                    #
                    #     if plotWindowConfig['inputMode'] == 1:
                    #         plt.plotDiagramRxCh(plotSetup, chirpConfig, plotWindowConfig['graph'],
                    #                             plotWindowConfig['diagramNum'], plotWindowConfig['rxCh'],
                    #                             dateTimeSensorCombList,
                    #                             plotWindowConfig['antType'],
                    #                             ptu2ListPerAntennaType, dictScalingDict,
                    #                             lowerMarginDict, upperMarginDict, picker)
                    #     else:
                    #
                    #         plt.plotDiagramRxCh(plotSetup, chirpConfig,parsedPlotWindowStringDict['graph'],
                    #                             parsedPlotWindowStringDict['diagramNum'], parsedPlotWindowStringDict['rxCh'],
                    #                             dateTimeSensorCombList,
                    #                             parsedPlotWindowStringDict[ 'antType'],
                    #                             ptu2ListPerAntennaType, dictScalingDict,
                    #                             lowerMarginDict, upperMarginDict, picker)
                    # else:
                        # List containing all graph data
                    graphDiagramRxChList = []
                    for graphIdx in range(len(graphList)):

                        # List containing all the diagrams per each graph
                        diagramPerGraphList = []
                        for diagramIdx in range(len(desiredDiagramList)):

                            # List containing all Rx channel graph data per diagram number
                            rxChPerDiagramList = []

                            # Max. no. of Rx channels of all PTU2 files
                            maxNofRxCh = dp.getMaxNofRxCh(graphList[graphIdx], ptu2ListPerAntennaType)

                            # Generate graphs and graph data
                            for rxCh in range(maxNofRxCh):
                                # myLogger.info('Plot ordered')
                                if plotSetup['ShowCertainPlotWindow']==1:

                                    if  plotWindowConfig['showPlotAllMode']!=1:

                                        if plotWindowConfig['inputMode'] == 1:
                                            if (plotWindowConfig['graph'] == graphList[graphIdx] and (plotWindowConfig['antType'] == 0 or plotWindowConfig['antType'] == antennaTypesList[antTypeIdx]) and (plotWindowConfig['diagramNum'] == 0 or plotWindowConfig['diagramNum'] == desiredDiagramList[diagramIdx]) and (plotWindowConfig['rxCh'] == 0 or plotWindowConfig['rxCh'] == rxCh)):
                                                plt.plotDiagramRxCh(plotSetup, chirpConfig, graphList[graphIdx],
                                                                                desiredDiagramList[diagramIdx], rxCh,
                                                                                dateTimeSensorCombList,
                                                                                antennaTypesList[antTypeIdx],
                                                                                ptu2ListPerAntennaType, dictScalingDict,
                                                                                lowerMarginDict, upperMarginDict, picker)
                                        else:

                                            if (parsedPlotWindowStringDict['graph'] == graphList[graphIdx] and parsedPlotWindowStringDict['antType'] == antennaTypesList[antTypeIdx] and parsedPlotWindowStringDict['diagramNum'] == desiredDiagramList[diagramIdx] and parsedPlotWindowStringDict['rxCh'] == rxCh):
                                                plt.plotDiagramRxCh(plotSetup, chirpConfig, graphList[graphIdx],
                                                                                desiredDiagramList[diagramIdx], rxCh,
                                                                                dateTimeSensorCombList,
                                                                                antennaTypesList[antTypeIdx],
                                                                                ptu2ListPerAntennaType, dictScalingDict,
                                                                                lowerMarginDict, upperMarginDict, picker)

                                else:
                                    graphData = plt.plotDiagramRxCh(plotSetup, chirpConfig, graphList[graphIdx], desiredDiagramList[diagramIdx], rxCh, dateTimeSensorCombList, antennaTypesList[antTypeIdx], ptu2ListPerAntennaType, dictScalingDict, lowerMarginDict, upperMarginDict, picker)

                                if plotSetup['ShowCertainPlotWindow'] == 0:
                                    rxChPerDiagramList.append(graphData)
                            if plotSetup['ShowCertainPlotWindow'] == 0:
                                diagramPerGraphList.append(rxChPerDiagramList)
                        if plotSetup['ShowCertainPlotWindow'] == 0:
                            graphDiagramRxChList.append(diagramPerGraphList)

                    if plotSetup['ShowCertainPlotWindow'] == 0:
                        myLogger.info('Configured graphs generated.')

                    if plotSetup['ShowCertainPlotWindow'] == 0:
                        # Traverse through the graph setup list.
                        for fgSetupListIdx in range(len(fourGraphSetupList)):
                            # Check if the presentation-configured graph type is plot-configured.
                            if fourGraphSetupList[fgSetupListIdx]['graphType'] in graphList:
                                # Traverse through every diagramm
                                for diagramIdx in range(len(desiredDiagramList)):

                                    # Instantiate two-graph data class for level graphs
                                    fourGraphData = pp.FourGraphConfigRx(fourGraphSetupList[fgSetupListIdx], graphDiagramRxChList, desiredDiagramList[diagramIdx], graphList)

                                    actualNofRxCh = len(fourGraphData.graphList)
                                    nofImagePlaceholders = 4


                                    nofElements = actualNofRxCh
                                    nofSlides   = int(np.ceil(nofElements / nofImagePlaceholders))

                                    nofRows = nofSlides
                                    nofCols = nofImagePlaceholders

                                    if nofElements < (nofRows * nofCols):
                                        res = nofCols * nofRows - nofElements
                                        for i in range (res):
                                            fourGraphData.graphList.append(0)


                                    graphListReshaped = np.reshape(fourGraphData.graphList, [nofRows, nofCols])


                                    for slideIdx in range(nofRows):

                                        graphListPerSlide = graphListReshaped[slideIdx]

                                        # Adding a slide with four graphs layout
                                        prs.add_slide(fgLayout)

                                        imageList    = []
                                        captionsList = []

                                        # Inserting slide title.
                                        fgLayout.title.text = plt.graphStringMapping(fourGraphData.graphList[0].graphTitle) + ' - Antenna system diagrams - Type ' \
                                        + str(antennaTypesList[antTypeIdx]) + ' - ' + dp.getAntDiagType(fourGraphData.graphList[0].antennaDiagramType)


                                        # Filling the caption and image lists
                                        for i in range(len(graphListPerSlide)):
                                            if graphListPerSlide[i] != 0:
                                                img = fgLayout.imageList[i]
                                                cap = fgLayout.captionsList[i]
                                                imageList.append(img)
                                                captionsList.append(cap)

                                        # Inserting images and captions.
                                        for i in range(len(graphListPerSlide)):
                                            if graphListPerSlide[i] != 0:
                                                imgPath = os.path.join(outputPath, graphListPerSlide[i].figureTitle)
                                                imageList[i].insert_picture(imgPath)
                                                captionsList[i].text_frame.text = dp.rxChStringMapping(graphListPerSlide[i].graphTitle, i+ slideIdx*nofImagePlaceholders)

                                        # Inserting the description text
                                        # fgLayout.text.text_frame.text = plt.graphStringMapping(
                                        # fourGraphData.graphList[0].graphTitle) + fourGraphData.graphList[0].antennaDiagramType + ' - Diagram' \
                                        #                                 + str(fourGraphData.graphList[0].diagramNr) \
                                        #                                 + ' - Seq' + str(fourGraphData.graphList[0].seqNum) \
                                        #                                 + ' - TxAnt' + str(fourGraphData.graphList[0].txAnt) + ', ' \
                                        #                                 + ' CentFreq. = ' + str(centFreqDictList[diagramIdx]['avgFreqGHz']) +' GHz (+ ' + str(centFreqDictList[diagramIdx]['posFreqDevMHz']) + ' MHz - ' +str(centFreqDictList[diagramIdx]['negFreqDevMHz'])+' MHz) , ' \
                                        #                                 + dp.graphTypeStringMapping(fourGraphData.graphList[0].graphTitle)

                                        fgLayout.text.text_frame.text = 'Diag' \
                                                                        + str(fourGraphData.graphList[0].diagramNr) \
                                                                        + ' - Seq' + str(fourGraphData.graphList[0].seqNum) \
                                                                        + ' - TxAnt' + str(fourGraphData.graphList[0].txAnt) + ', ' \
                                                                        + ' CentFreq. = ' + str(centFreqDictList[diagramIdx]['avgFreqGHz']) +' GHz (+ ' + str(centFreqDictList[diagramIdx]['posFreqDevMHz']) + ' MHz - ' +str(centFreqDictList[diagramIdx]['negFreqDevMHz'])+' MHz) , ' \
                                                                        + dp.graphTypeStringMapping(fourGraphData.graphList[0].graphTitle)

                        if plotSetup['threeGraphLayout'] == 1:
                            # Traverse through the graph setup list.
                            for trgSetupListIdx in range(len(threeGraphSetupList)):
                                # Check if the presentation-configured graph type is plot-configured.
                                if threeGraphSetupList[trgSetupListIdx]['graphType'] in graphList:
                                    # Traverse through every diagramm
                                    for diagramIdx in range(len(desiredDiagramList)):


                                        # Instantiate two-graph data class for level graphs
                                        threeGraphData = pp.ThreeGraphConfigRx(threeGraphSetupList[trgSetupListIdx], graphDiagramRxChList, desiredDiagramList[diagramIdx], graphList)

                                        actualNofRxCh = len(threeGraphData.graphList)
                                        nofImagePlaceholders = 3

                                        nofElements = actualNofRxCh
                                        nofSlides   = int(np.ceil(nofElements / nofImagePlaceholders))

                                        nofRows = nofSlides
                                        nofCols = nofImagePlaceholders
                                        #
                                        if nofElements < (nofRows * nofCols):
                                            res = nofCols * nofRows - nofElements
                                            for i in range(res):
                                                threeGraphData.graphList.append(0)

                                        graphListReshaped = np.reshape(threeGraphData.graphList, [nofRows, nofCols])



                                        for slideIdx in range(nofRows):

                                            graphListPerSlide = graphListReshaped[slideIdx]

                                            # Adding a slide with four graphs layout
                                            prs.add_slide(trgLayout)

                                            # Inserting slide title.
                                            trgLayout.title.text = plt.graphStringMapping(threeGraphData.graphList[0].graphTitle) + ' - Antenna system diagrams - Type ' \
                                                                  + str(antennaTypesList[antTypeIdx]) + ' - ' + dp.getAntDiagType(threeGraphData.graphList[0].antennaDiagramType)


                                            imageList    = []
                                            captionsList = []

                                            # Filling the caption and image lists
                                            for i in range(len(graphListPerSlide)):
                                                if graphListPerSlide[i] != 0:
                                                    img = trgLayout.imageList[i]
                                                    cap = trgLayout.captionsList[i]
                                                    imageList.append(img)
                                                    captionsList.append(cap)

                                            # Inserting images and captions.
                                            for i in range(len(graphListPerSlide)):
                                                if graphListPerSlide[i] != 0:
                                                    imgPath = os.path.join(outputPath, graphListPerSlide[i].figureTitle3graph)
                                                    imageList[i].insert_picture(imgPath)
                                                    captionsList[i].text_frame.text = dp.rxChStringMapping(graphListPerSlide[i].graphTitle, i + slideIdx*nofImagePlaceholders)

                                            # Inserting the description text
                                            # trgLayout.text.text_frame.text = plt.graphStringMapping(
                                            #     threeGraphData.graphList[0].graphTitle) + \
                                            #                                 threeGraphData.graphList[0].antennaDiagramType + ' - Diagram' \
                                            #                                 + str(threeGraphData.graphList[0].diagramNr) \
                                            #                                 + ' - Seq' + str(threeGraphData.graphList[0].seqNum) \
                                            #                                 + ' - TxAnt' + str(threeGraphData.graphList[0].txAnt) + ', ' \
                                            #                                  + ' CentFreq. = ' + str(centFreqDictList[diagramIdx]['avgFreqGHz']) + ' GHz (+ ' + str(centFreqDictList[diagramIdx]['posFreqDevMHz']) + ' MHz - ' + str(centFreqDictList[diagramIdx]['negFreqDevMHz']) + ' MHz) , '  \
                                            #                                  + dp.graphTypeStringMapping(threeGraphData.graphList[0].graphTitle)

                                            trgLayout.text.text_frame.text = 'Diag' \
                                                                            + str(threeGraphData.graphList[0].diagramNr) \
                                                                            + ' - Seq' + str(threeGraphData.graphList[0].seqNum) \
                                                                            + ' - TxAnt' + str(threeGraphData.graphList[0].txAnt) + ', ' \
                                                                            + ' CentFreq. = ' + str(centFreqDictList[diagramIdx]['avgFreqGHz']) + ' GHz (+ ' + str(centFreqDictList[diagramIdx]['posFreqDevMHz']) + ' MHz - ' + str(centFreqDictList[diagramIdx]['negFreqDevMHz']) + ' MHz) , '  \
                                                                            + dp.graphTypeStringMapping(threeGraphData.graphList[0].graphTitle)

                        # Traverse through the graph setup list.
                        for tgSetupListIdx in range(len(twoGraphSetupList)):
                            # Check if at least one of the desired graphs is generated.
                            if twoGraphSetupList[tgSetupListIdx]['primGraph'] in graphList or \
                                    twoGraphSetupList[tgSetupListIdx]['secGraph'] in graphList:
                                # Insertion of slides for each diagram number and each Rx channel
                                for diagramIdx in range(len(desiredDiagramList)):

                                    # Instantiate two-graph data class for level graphs
                                    twoGraphData = pp.TwoGraphConfigRx(twoGraphSetupList[tgSetupListIdx],
                                                                       graphDiagramRxChList, desiredDiagramList[diagramIdx], graphList)

                                    # Check if there is only one graph
                                    if twoGraphData.onlyOneGraphList != 0:

                                        # Insertion of slides per Rx channel
                                        for rxCh in range(len(twoGraphData.onlyOneGraphList)):
                                            prs.add_slide(tgLayout)

                                            tgLayout.title.text = plt.graphStringMapping(twoGraphData.onlyOneGraphList[rxCh].graphTitle) + ' - Antenna system diagrams - Type ' + str(antennaTypesList[antTypeIdx]) + \
                                                                  ' - ' + dp.getAntDiagType(twoGraphData.onlyOneGraphList[rxCh].antennaDiagramType)

                                            # tgLayout.primText.text_frame.text = plt.graphStringMapping(
                                            #     twoGraphData.onlyOneGraphList[
                                            #         rxCh].graphTitle) + \
                                            #                                     twoGraphData.onlyOneGraphList[
                                            #                                         rxCh].antennaDiagramType + ' - Diagram' + str(twoGraphData.onlyOneGraphList[rxCh].diagramNr) + \
                                            #                                     ' - Seq' + str(twoGraphData.onlyOneGraphList[rxCh].seqNum)+ \
                                            #                                     ' - TxAnt' + str(twoGraphData.onlyOneGraphList[rxCh].txAnt) + ', ' \
                                            #                                     + ' CentFreq. = ' + str(centFreqDictList[diagramIdx]['avgFreqGHz']) + ' GHz (+ ' + str(centFreqDictList[diagramIdx]['posFreqDevMHz']) + ' MHz - ' + str(centFreqDictList[diagramIdx]['negFreqDevMHz']) + ' MHz) , ' \
                                            #                                     + dp.rxChStringMapping(twoGraphData.onlyOneGraphList[rxCh].graphTitle, rxCh) + ', all sensors.'

                                            tgLayout.primText.text_frame.text = 'Diag' + str(twoGraphData.onlyOneGraphList[rxCh].diagramNr) + \
                                                                                ' - Seq' + str(twoGraphData.onlyOneGraphList[rxCh].seqNum)+ \
                                                                                ' - TxAnt' + str(twoGraphData.onlyOneGraphList[rxCh].txAnt) + ', ' \
                                                                                + ' CentFreq. = ' + str(centFreqDictList[diagramIdx]['avgFreqGHz']) + ' GHz (+ ' + str(centFreqDictList[diagramIdx]['posFreqDevMHz']) + ' MHz - ' + str(centFreqDictList[diagramIdx]['negFreqDevMHz']) + ' MHz) , ' \
                                                                                + dp.rxChStringMapping(twoGraphData.onlyOneGraphList[rxCh].graphTitle, rxCh) + ', all sensors.'
                                                                                
                                            # tgLayout.primGraphCap.text_frame.text = plt.graphStringMapping(
                                            #     twoGraphData.onlyOneGraphList[rxCh].graphTitle)
                                            onlyOneImgPath = os.path.join(outputPath, twoGraphData.onlyOneGraphList[rxCh].figureTitle)
                                            tgLayout.primGraphImg.insert_picture(onlyOneImgPath)
                                            # tgLayout.secText.text_frame.text = 'Comments'
                                    else:

                                        for rxCh in range(len(twoGraphData.primGraphList)):
                                            prs.add_slide(tgLayout)
                                            tgLayout.title.text = plt.graphStringMapping(twoGraphData.primGraphList[rxCh].graphTitle) + ' - Antenna system diagrams - Type ' + str(
                                                antennaTypesList[antTypeIdx]) + ' - ' + dp.getAntDiagType(twoGraphData.primGraphList[rxCh].antennaDiagramType)
                                            # tgLayout.primText.text_frame.text = plt.graphStringMapping(twoGraphData.primGraphList[rxCh].graphTitle) + twoGraphData.primGraphList[rxCh].antennaDiagramType \
                                            #                                     + ' - Diagram' + str(twoGraphData.primGraphList[rxCh].diagramNr) + \
                                            #                                     ' - Seq' + str(twoGraphData.primGraphList[rxCh].seqNum) + \
                                            #                                     ' - TxAnt' + str(twoGraphData.primGraphList[rxCh].txAnt) + ', ' \
                                            #                                     + ' CentFreq. = ' + str(centFreqDictList[diagramIdx]['avgFreqGHz']) + ' GHz (+ ' + str(centFreqDictList[diagramIdx]['posFreqDevMHz']) + ' MHz - ' + str(centFreqDictList[diagramIdx]['negFreqDevMHz']) + ' MHz) , ' \
                                            #                                     + dp.rxChStringMapping(twoGraphData.primGraphList[rxCh].graphTitle, rxCh) + ', all sensors.'

                                            tgLayout.primText.text_frame.text = 'Diag' + str(twoGraphData.primGraphList[rxCh].diagramNr) + \
                                                                                ' - Seq' + str(twoGraphData.primGraphList[rxCh].seqNum) + \
                                                                                ' - TxAnt' + str(twoGraphData.primGraphList[rxCh].txAnt) + ', ' \
                                                                                + ' CentFreq. = ' + str(centFreqDictList[diagramIdx]['avgFreqGHz']) + ' GHz (+ ' + str(centFreqDictList[diagramIdx]['posFreqDevMHz']) + ' MHz - ' + str(centFreqDictList[diagramIdx]['negFreqDevMHz']) + ' MHz) , ' \
                                                                                + dp.rxChStringMapping(twoGraphData.primGraphList[rxCh].graphTitle, rxCh) + ', all sensors.'
                                            # tgLayout.primGraphCap.text_frame.text = plt.graphStringMapping(twoGraphData.primGraphList[rxCh].graphTitle)
                                            primImgPath = os.path.join(outputPath, twoGraphData.primGraphList[rxCh].figureTitle)
                                            tgLayout.primGraphImg.insert_picture(primImgPath)

                                            # tgLayout.secGraphCap.text_frame.text = plt.graphStringMapping(twoGraphData.secGraphList[rxCh].graphTitle)
                                            secImgPath = os.path.join(outputPath, twoGraphData.secGraphList[rxCh].figureTitle)
                                            tgLayout.secGraphImg.insert_picture(secImgPath)

                                            # tgLayout.secText.text_frame.text = 'Comments'

                                myLogger.info('Diagram slides inserted.')
                else:

                    # List of meta data per each graph-diagram combination
                    graphAndDiagramList = []

                    # Fill in the graph list
                    for graphIdx in range(len(graphList)):

                        # List of all diagrams per graph
                        diagramPerGraphList = []
                        for diagramIdx in range(len(desiredDiagramList)):
                            # myLogger.info('Plot ordered')
                            if plotSetup['ShowCertainPlotWindow'] == 1:

                                if plotWindowConfig['showPlotAllMode'] != 1:

                                    if plotWindowConfig['inputMode'] == 1:
                                        if (plotWindowConfig['graph'] == graphList[graphIdx] and (plotWindowConfig['antType'] == 0 or plotWindowConfig['antType'] == antennaTypesList[antTypeIdx]) and (plotWindowConfig['diagramNum'] == 0 or plotWindowConfig['diagramNum'] == desiredDiagramList[diagramIdx])):
                                            plt.plotDiagram(plotSetup, chirpConfig, graphList[graphIdx],
                                                                        desiredDiagramList[diagramIdx],
                                                                        dateTimeSensorCombList,
                                                                        antennaTypesList[antTypeIdx],
                                                                        ptu2ListPerAntennaType, dictScalingDict,
                                                                        lowerMarginDict, upperMarginDict, picker)
                                    else:
                                        if (parsedPlotWindowStringDict['graph'] == graphList[graphIdx] and parsedPlotWindowStringDict['antType'] == antennaTypesList[antTypeIdx] and parsedPlotWindowStringDict['diagramNum'] == desiredDiagramList[diagramIdx] ):
                                            plt.plotDiagram(plotSetup, chirpConfig, graphList[graphIdx],
                                                            desiredDiagramList[diagramIdx],
                                                            dateTimeSensorCombList,
                                                            antennaTypesList[antTypeIdx],
                                                            ptu2ListPerAntennaType, dictScalingDict,
                                                            lowerMarginDict, upperMarginDict, picker)

                            else:
                                graphData=plt.plotDiagram(plotSetup, chirpConfig, graphList[graphIdx], desiredDiagramList[diagramIdx], dateTimeSensorCombList,   antennaTypesList[antTypeIdx], ptu2ListPerAntennaType, dictScalingDict, lowerMarginDict, upperMarginDict, picker)

                            if plotSetup['ShowCertainPlotWindow'] == 0:
                                diagramPerGraphList.append(graphData)
                        if plotSetup['ShowCertainPlotWindow'] == 0:
                            graphAndDiagramList.append(diagramPerGraphList)
                    if plotSetup['ShowCertainPlotWindow'] == 0:
                        myLogger.info('Configured graphs generated.')

                    if plotSetup['ShowCertainPlotWindow'] == 0:
                        # Traverse through the graph setup list.
                        for tgSetupListIdx in range(len(twoGraphSetupList)):
                            # Check if at least one of the desired graphs is generated.
                            if twoGraphSetupList[tgSetupListIdx]['primGraph'] in graphList or twoGraphSetupList[tgSetupListIdx]['secGraph'] in graphList:
                                # Insertion of slides for each diagram number.
                                for diagramIdx in range(len(desiredDiagramList)):
                                    twoGraphData = pp.TwoGraphConfig(twoGraphSetupList[tgSetupListIdx], graphAndDiagramList, desiredDiagramList[diagramIdx], graphList)

                                    prs.add_slide(tgLayout)
                                    # Check if there is only one graph.
                                    if twoGraphData.onlyOneGraph!=0:
                                        
                                        tgLayout.title.text = plt.graphStringMapping(twoGraphData.onlyOneGraph.graphTitle)+' - Antenna system diagrams - Type ' + str(
                                            antennaTypesList[antTypeIdx]) + ' - ' + dp.getAntDiagType(twoGraphData.onlyOneGraph.antennaDiagramType)
                                        # tgLayout.primText.text_frame.text =  plt.graphStringMapping(twoGraphData.onlyOneGraph.graphTitle) + twoGraphData.onlyOneGraph.antennaDiagramType + ' - Diagram' + str(
                                        #     twoGraphData.onlyOneGraph.diagramNr) + \
                                        #     ' - Seq' + str(twoGraphData.onlyOneGraph.seqNum) +\
                                        #     ' - TxAnt' + str(twoGraphData.onlyOneGraph.txAnt) + ', ' \
                                        #     + ' CentFreq. = ' + str(centFreqDictList[diagramIdx]['avgFreqGHz']) + ' GHz (+ ' + str(centFreqDictList[diagramIdx]['posFreqDevMHz']) + ' MHz - ' + str(centFreqDictList[diagramIdx]['negFreqDevMHz']) + ' MHz) , ' \
                                        #     + dp.graphTypeStringMapping(twoGraphData.onlyOneGraph.graphTitle)

                                        tgLayout.primText.text_frame.text = 'Diag' + str(twoGraphData.onlyOneGraph.diagramNr) + \
                                            ' - Seq' + str(twoGraphData.onlyOneGraph.seqNum) +\
                                            ' - TxAnt' + str(twoGraphData.onlyOneGraph.txAnt) + ', ' \
                                            + ' CentFreq. = ' + str(centFreqDictList[diagramIdx]['avgFreqGHz']) + ' GHz (+ ' + str(centFreqDictList[diagramIdx]['posFreqDevMHz']) + ' MHz - ' + str(centFreqDictList[diagramIdx]['negFreqDevMHz']) + ' MHz) , ' \
                                            + dp.graphTypeStringMapping(twoGraphData.onlyOneGraph.graphTitle)

                                        # tgLayout.primGraphCap.text_frame.text = plt.graphStringMapping(twoGraphData.onlyOneGraph.graphTitle)
                                        onlyOneImgPath = os.path.join(outputPath, twoGraphData.onlyOneGraph.figureTitle)
                                        tgLayout.primGraphImg.insert_picture(onlyOneImgPath)

                                    else:
                                        tgLayout.title.text = plt.graphStringMapping(twoGraphData.primGraph.graphTitle)+' - Antenna system diagrams - Type ' + str(
                                            antennaTypesList[antTypeIdx]) + ' - ' + dp.getAntDiagType(twoGraphData.primGraph.antennaDiagramType)
                                        # tgLayout.primText.text_frame.text =  plt.graphStringMapping(twoGraphData.primGraph.graphTitle) + \
                                        #                                      twoGraphData.primGraph.antennaDiagramType + ' - Diagram' + str(twoGraphData.primGraph.diagramNr) + \
                                        #      ' - Seq' + str(twoGraphData.primGraph.seqNum) + \
                                        #      ' - TxAnt' + str(twoGraphData.primGraph.txAnt) + ', ' \
                                        #     + ' CentFreq. = ' + str(centFreqDictList[diagramIdx]['avgFreqGHz']) + ' GHz (+ ' + str(centFreqDictList[diagramIdx]['posFreqDevMHz']) + ' MHz - ' + str(centFreqDictList[diagramIdx]['negFreqDevMHz']) + ' MHz) , ' \
                                        #     + dp.graphTypeStringMapping(twoGraphData.primGraph.graphTitle)

                                        tgLayout.primText.text_frame.text =  'Diag' + str(twoGraphData.primGraph.diagramNr) + \
                                             ' - Seq' + str(twoGraphData.primGraph.seqNum) + \
                                             ' - TxAnt' + str(twoGraphData.primGraph.txAnt) + ', ' \
                                            + ' CentFreq. = ' + str(centFreqDictList[diagramIdx]['avgFreqGHz']) + ' GHz (+ ' + str(centFreqDictList[diagramIdx]['posFreqDevMHz']) + ' MHz - ' + str(centFreqDictList[diagramIdx]['negFreqDevMHz']) + ' MHz) , ' \
                                            + dp.graphTypeStringMapping(twoGraphData.primGraph.graphTitle)
                                        # tgLayout.primGraphCap.text_frame.text =  plt.graphStringMapping(twoGraphData.primGraph.graphTitle)
                                        primImgPath = os.path.join(outputPath, twoGraphData.primGraph.figureTitle)
                                        tgLayout.primGraphImg.insert_picture(primImgPath)

                                        # tgLayout.secGraphCap.text_frame.text =  plt.graphStringMapping(twoGraphData.secGraph.graphTitle)
                                        secImgPath = os.path.join(outputPath, twoGraphData.secGraph.figureTitle)
                                        tgLayout.secGraphImg.insert_picture(secImgPath)

                                    # tgLayout.secText.text_frame.text = 'Comments'

                                myLogger.info('Diagram slides inserted.')

                if plotSetup['allOnOneSlide'] == 1:

                    # Plot all graphs for all diagrams, all RxAnt, and all dateTimeSensor comb. on one slide.
                    if len(allOnOneSlideGraphList) == 0:
                        myLogger.error('Invalid configuraton for all graphs on one slide.')
                    else:
                        # Get center frequency values
                        avgFreq = dp.getAvgFreq(chirpConfig, desiredDiagramList, ptu2ListPerAntennaType)
                        minFreq = dp.getMinFreq(chirpConfig, desiredDiagramList, ptu2ListPerAntennaType)
                        maxFreq = dp.getMaxFreq(chirpConfig, desiredDiagramList, ptu2ListPerAntennaType)
                        posFreqDev = maxFreq - avgFreq
                        negFreqDev = avgFreq - minFreq

                        posFreqDevMHz = round((posFreqDev / 10e6), 4)
                        negFreqDevMHz = round((negFreqDev / 10e6), 4)
                        avgFreqGHz = round((avgFreq / 10e9), 4)

                        posFreqDevMHz = format(posFreqDevMHz, '.2f')
                        negFreqDevMHz = format(negFreqDevMHz, '.2f')
                        avgFreqGHz = format(avgFreqGHz, '.2f')

                        # plot all
                        plt.plotAll(plotSetup, chirpConfig, allOnOneSlideGraphList, desiredDiagramList, dateTimeSensorCombList, ptu2ListPerAntennaType, diagramConfig, plotAllPicker)

                        if plotSetup['ShowCertainPlotWindow'] == 0:

                            # All graphs on one slide, slide configuration.
                            aosLayout = pp.OneGraphLayout()
                            allOnOneSlide = prs.add_slide(aosLayout)
                            allOnOneSlide.title.text = 'Antenna system diagrams - Type ' + str(antennaTypesList[antTypeIdx])

                            graphListString=''

                            for graphIdx in range(len(allOnOneSlideGraphList)):
                                if graphIdx == 0:
                                    graphListString = plt.graphStringMapping(allOnOneSlideGraphList[0]['graphType'])
                                else:
                                    graphListString = graphListString + ' - ' +  plt.graphStringMapping(allOnOneSlideGraphList[graphIdx]['graphType'])

                            if diagramConfig['selectDiagrams'] == 0:
                                graphListString = graphListString + ' - All diagrams'

                                if diagramConfig['oddOrEven']   == 1:
                                    graphListString = graphListString + ' - Odd'
                                elif diagramConfig['oddOrEven'] == 2:
                                    graphListString = graphListString + ' - Even'

                            elif diagramConfig['selectDiagrams'] == 1:
                                graphListString = graphListString + ' - Diag' + str(diagramConfig['lowerNumber']) + ' - Diag'+ str(diagramConfig['higherNumber'])
                                if diagramConfig['oddOrEven'] == 1:
                                    graphListString = graphListString + ' - Odd'
                                elif diagramConfig['oddOrEven'] == 2:
                                    graphListString = graphListString + ' - Even'

                            else:
                                graphListString = graphListString + ' - Diag: '
                                for i in range (len(desiredDiagramList)):
                                    graphListString = graphListString + str(desiredDiagramList[i]) + ','

                            allOnOneSlide.text.text = str(graphListString) \
                            + ' -  CentFreq. = ' + str(avgFreqGHz) + ' GHz (+ ' + str(posFreqDevMHz) + ' MHz - ' + str(negFreqDevMHz) + ' MHz) ,' \
                            + ' all sensors, all diagrams, all TxAnt, all RxAnt.'
                            imagePath = os.path.join(outputPath, 'all_on_one_slide.png')
                            allOnOneSlide.image.insert_picture(imagePath)
                            allOnOneSlide.caption.text = graphListString



    if plotSetup['ShowCertainPlotWindow'] == 0:
        # Save presentation
        pathParts = os.path.split(pptxPath)
        if pathParts[1].endswith('.pptx') or pathParts[1].endswith('.ppt'):
            prs.save(pptxPath)
            # Delete extra placeholders in the presentation
            presPlace = Presentation(pptxPath)
            for slide in presPlace.slides:
                for placeholder in slide.shapes.placeholders:
                    if placeholder.has_text_frame and placeholder.text_frame.text == '':
                        rem_pc = placeholder._sp
                        rem_pc.getparent().remove(rem_pc)
            presPlace.save(pptxPath)

            if prs.saveStatus == False:
                myLogger.error(prs.saveStatusString)
            else:
                myLogger.info('PPTX file saved successfully: ' + pptxPath)
        else:
            myLogger.error('Invalid presentation file extension. Use .pptx or .ppt')


    # Copying the LogFile to the output directory
    logFileOutputPath  = os.path.join(aux.antSysDiagOutputPath, logconfig.LogFileNames.AntennaSystemDiagrams.value)
    status, errorSting = aux.copyFile(logconfig.antSysDiagLogFilePath, logFileOutputPath)
    if not status:
        myLogger.warning(errorSting)
    loadDataLogFileOutputPath = os.path.join(aux.antSysDiagOutputPath, logconfig.LogFileNames.MainLoadData.value)
    status, errorSting = aux.copyFile(logconfig.mainLoadDataLogFilePath, loadDataLogFileOutputPath)
    if not status:
        myLogger.warning(errorSting)

    if os.path.exists(output_pathpptx):
        try:
            compptx  = os.path.join(output_pathpptx, 'combine.pptx')
            compptx1 = os.path.join(output_pathpptx, 'combine1.pptx')
            compptx2 = os.path.join(output_pathpptx, 'combine2.pptx')
            os.remove(compptx)
            os.remove(compptx1)
            os.remove(compptx2)
        except OSError:
            return


if bUseGui:
    qt.SysDiaInterTableParam.cellClicked.connect(SysDiaInterTableParamCellClicked)
    qt.SysDiaInterTableProtocol.cellClicked.connect(SysDiaInterTableProtCellClicked)
    qt.SysDiaInterSwitchBtn.clicked.connect(TurnOnOff)
    qt.SysDiaInterClrGrBtn.clicked.connect(ClearData)
else:
    # configuration file if the GUI is not used
    with open(os.path.join(aux.configDir, 'AntennaSystemDiagramsConf.yaml'), 'r', encoding='utf8') as yamlfile:
        config = yaml.safe_load(yamlfile)
        plotSetup              = config['plotSetup']
        chirpConfig            = config['chirpConfig'] 
        graphConfig            = config['graphConfig']
        diagramConfig          = config['diagramConfig']
        diagramConfigList      = config['diagramConfigList']
        twoGraphSetupList      = config['twoGraphSetupList']
        threeGraphSetupList    = config['threeGraphSetupList']
        fourGraphSetupList     = config['fourGraphSetupList']
        allOnOneSlideGraphList = config['allOnOneSlideGraphList']
    # Parse Data
    parseDataLogger = logconfig.mainLoadDataLogger.logger
    parseDataLogger.info('Starting.')

    errorStatus, errorSting = logconfig.mainLoadDataLogger.addFileHandler(logconfig.mainLoadDataLogFilePath, 'w+')
    if errorStatus == 1:
        parseDataLogger.warning(errorSting)
    # Load Data by absolute path
    parseDataLogger.info('Loading data.')
    loadData = ld.LoadData(absPath, plotSetup['useSensorMuster'], plotSetup['sensorMusterList'])

    sysDiagLogger=logconfig.antSysDiagLogger

    if loadData.invalidPath != 1:
        parseDataLogger.info('Num. of valid files parsed: ' + str(loadData.validFilesCounter) + '.')
        parseDataList=loadData.parseDataList
        start_data_evaluation(parseDataList, plotSetup, chirpConfig, graphConfig, diagramConfig, twoGraphSetupList, fourGraphSetupList, threeGraphSetupList, allOnOneSlideGraphList, diagramConfigList, sysDiagLogger, aux.antSysDiagOutputPath, 'Antenna_diagrams.pptx', './template.pptx')
    else:
        parseDataLogger.error(loadData.invalidPathString)
