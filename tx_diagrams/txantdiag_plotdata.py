import os
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches
from matplotlib.ticker import (AutoMinorLocator)
import gc
import txantdiag_calc as calc
import logconfig as log
import auxiliary as aux

myLogger  = log.txAntDiagLogger.logger

# Basic directory path
basicDir  = aux.basicDir

# Output directory path. Plotted graph images are saved here.
outputDir = aux.txAntDiagOutputPath


# legend name
legFigTitle = 'legend.png'

# Graph meta data
class GraphData:
    def __init__(self):
        self.graphTitle        = ''
        self.txAnt             = 0
        self.sensorId          = ''
        self.figureTitle       = ''
        self.figureTitle3graph = ''
        self.dateAndTime       = ''
        self.diagType          = ''
        self.avgNormAngle      = 0
        self.normGraphs        = ''

# Save the plotted graph figure with a given title.
def saveFig(fig, figureTitle, dpi, graphsPerSlide):
    if graphsPerSlide == 3:
        fig.set_figheight(9)
        fig.set_figwidth(9)
    else:
        fig.set_figheight(9)
        fig.set_figwidth(16)
    figTitle = figureTitle+'.png'


    figurePath = os.path.join(outputDir, figTitle)
    try:
        fig.savefig(figurePath, dpi=dpi)
    except Exception as e:
        myLogger.error(e)
    plt.close(fig)
    # fig.savefig('mat.png',bbox_inches='tight')
    gc.collect()

# Mapping string for the graph titles
def graphStringMapping(graphTitle, normGraphs):
    if normGraphs == 0:
        normGraphStr = ''
    else:
        normGraphStr = 'Norm. '
    graphString = ''
    if graphTitle   == 'level':
        graphString = normGraphStr + 'Level [dBm]'
    elif graphTitle == 'levelPowMet':
        graphString = normGraphStr + 'Level Pow. Meter [dBm]'
    elif graphTitle == 'levelMeasSpec':
        graphString = normGraphStr + 'Level Meas. Spec. [dBm]'
    elif graphTitle == 'levelMeasPowMet':
        graphString = normGraphStr + 'Level Meas. Pow. Meter [dBm]'
    elif graphTitle == 'frequency':
        graphString = normGraphStr + 'Frequency [MHz]'
    elif graphTitle == 'time':
        graphString = normGraphStr + 'Time [ms]'

    return graphString

# Get PTU angle values
def getAzAngle(parseDataList, x):
    angle = calc.getAzPtuAngVals(parseDataList[x])
    return angle

# Get target angle values
def getAzTargetAngle( plotSetup, parseDataList, x):
    upsideDown = getUpsideDown(plotSetup)
    tarAngle = calc.getAzTarAngVals(parseDataList[x], upsideDown)
    return tarAngle

# Get PTU angle values
def getElAngle(parseDataList, x):
    angle = calc.getElPtuAngVals(parseDataList[x])
    return angle

# Get target angle values
def getElTargetAngle( plotSetup, parseDataList, x):
    upsideDown = getUpsideDown(plotSetup)
    tarAngle = calc.getElTarAngVals(parseDataList[x], upsideDown)
    return tarAngle

# Get the info for the upside down set up sensor, from the configuration.
def getUpsideDown( plotSetup):
    if plotSetup['upsideDown'] == 0:
        upsideDown = False
    else:
        upsideDown = True
    return upsideDown

# Generate graph for specific graph type, specific diagram num., all Rx channels together, and all sensors.
def plotTxAntDiagram(plotSetup, graph, diagType, dateAndTimeSensorList, txAnt, parseDataList, lowerMarginDict, upperMarginDict, normGraphs):

    # Instantiation of meta data object
    graphData = GraphData()

    # Assigning graph title to the meta data
    graphData.graphTitle = graph

    # Create subplots and plot figure
    fig, ax1 = plt.subplots()

    # Invert axis for showing angle from right to left
    plt.gca().invert_xaxis()

    # Show plot grid
    plt.grid(True)

    # Set title to the graph figure
    ax1.set_title(graphStringMapping(graph, normGraphs), fontsize=18)

    # Set y-axis label for specific general graph types
    ax1.set_ylabel(graphStringMapping(graph, normGraphs), fontsize=18)

    angBiggerThan45 = 0

    # Traversing through all PTU2 files
    for pdIdx in range(len(parseDataList)):

    # Traversing through all sensors
        for dateTimeSensorIdx in range(len(dateAndTimeSensorList)):
            # Looking for PTU file for specific sensor and specific TxAnt
            if (txAnt == parseDataList[pdIdx].fileTitle.txAnt) and (dateAndTimeSensorList[dateTimeSensorIdx]['sensor'] == parseDataList[pdIdx].fileTitle.sensor) \
                    and dateAndTimeSensorList[dateTimeSensorIdx]['dateAndTime'] == parseDataList[pdIdx].fileTitle.dateAndTime:

                # Filling in the meta data from the PTU2 title
                if parseDataList[pdIdx].fileTitle.sensorFound == 1:
                    graphData.sensorId=parseDataList[pdIdx].fileTitle.sensor
                if parseDataList[pdIdx].fileTitle.txAntFound == 1:
                    graphData.txAnt=parseDataList[pdIdx].fileTitle.txAnt
                if parseDataList[pdIdx].fileTitle.dateAndTimeFound == 1:
                    graphData.dateAndTime = parseDataList[pdIdx].fileTitle.dateAndTime

                if diagType =='Az':
                    graphData.avgNormAngle = parseDataList[pdIdx].ptuMaxSpecHeaderData.d_PTU_ElAngle
                else:
                    graphData.avgNormAngle =parseDataList[pdIdx].ptuMaxSpecHeaderData.d_PTU_AzAngle

                if normGraphs == 1:
                    graphData.normGraphs = 'norm'
                else:
                    graphData.normGraphs = 'orig'

                # Get the ptu and target angle for the specific PTU2 file and diagram type
                if diagType  =='Az':
                    angle    = getAzAngle(parseDataList, pdIdx)
                    tarAngle = getAzTargetAngle(plotSetup, parseDataList, pdIdx)
                else:
                    angle    = getElAngle(parseDataList, pdIdx)
                    tarAngle = getElTargetAngle(plotSetup, parseDataList, pdIdx)

                # Set graph title to the figure
                ax1.set_title(graphStringMapping(graph, normGraphs)+ ' - ' +diagType+ ' - ' + 'TxAnt' + str(txAnt), fontsize=18)

                # Level and  phase difference specific graph notations
                ax1.set_ylabel(graphStringMapping(graph, normGraphs), fontsize=18)

                # Set xticks according to the angle values from files a plot contains
                if abs(angle[0]) > 45:
                    angBiggerThan45 = 1

                if angBiggerThan45 != 1:
                    ax1.set_xticks(np.arange(90, -91, -2.5), minor = True)
                    plt.xticks(np.arange(90, -91, -5))
                else:
                    ax1.set_xticks(np.arange(90, -91, -5), minor = True)
                    plt.xticks(np.arange(90, -91, -10))

                # Set the x-axis scale size
                if plotSetup['xScaleSizeAuto'] == 1:
                    # Streching the x axis data from end to end
                    ax1.autoscale(enable=True, axis='x', tight=True)
                else:

                    if diagType == 'Az':
                        ax1.set_xlim(plotSetup['xScaleSizeAz'], (-1) * plotSetup['xScaleSizeAz'])
                    else:
                        ax1.set_xlim(plotSetup['xScaleSizeEl'], (-1) * plotSetup['xScaleSizeEl'])


                # Set the x-axis label
                ax1.set_xlabel('PTU Angle [°]', fontsize=18)
                if plotSetup['targetAngle'] == 1:
                    angle = tarAngle
                    ax1.set_xlabel('Target Angle [°]', fontsize=18)

                # Set the color for the sensor specific plot lines
                color = setColor(dateTimeSensorIdx)

                # Get the actual graph data for specific Rx channel, chirp and a PTU2 file
                if normGraphs == 0:
                    actualGraphData = getActualGraphData(graph, parseDataList, pdIdx)

                    # Scale the y-axis according to the upper and lower margins of all graphs from one graph type
                    lowerMargin = lowerMarginDict[graph]
                    upperMargin = upperMarginDict[graph]
                    plt.ylim(lowerMargin, upperMargin)

                    # Plot data
                    ax1.plot(angle, actualGraphData, '.-', color=color)

                else:

                    if graph != 'frequency' and graph != 'time':

                        actualGraphData = getNormGraphData(graph, parseDataList, pdIdx)

                        # Scale the y-axis according to the upper and lower margins of all graphs from one graph type
                        lowerMargin = lowerMarginDict[graph]
                        upperMargin = upperMarginDict[graph]
                        plt.ylim(lowerMargin, upperMargin)

                        # Plot data
                        ax1.plot(angle, actualGraphData, '.-', color=color)

    # Assign figure title
    figureTitle = graphData.normGraphs+'_'+ graphData.graphTitle+'_'+diagType +'_TxAnt'+str(graphData.txAnt)
    graphData.figureTitle = figureTitle + '.png'
    # Save figure

    if normGraphs==0:
        ax1.yaxis.set_minor_locator(AutoMinorLocator())
        ax1.grid(visible=True, which = 'minor', color = '#999999', linestyle = 'dashed', alpha = 0.2)
        saveFig(fig, figureTitle, plotSetup['imageDpi'], plotSetup['graphsPerSlide'])
    else:

        if graphData.graphTitle != 'frequency' and graphData.graphTitle != 'time':
            ax1.yaxis.set_minor_locator(AutoMinorLocator())
            ax1.grid(visible=True, which = 'minor', color = '#999999', linestyle = 'dashed', alpha = 0.2)
            saveFig(fig, figureTitle, plotSetup['imageDpi'], plotSetup['graphsPerSlide'])

    #myLogger.info('Image saved')
    # Close all plots
    plt.close('all')
    # plt.show()

    #  Return graph data pbject
    return graphData

# Generate legend figure for all sensors
def generateLegend(plotSetup, dateTimeSensorCombList):

    # Create legend figure
    legFig = plt.figure(figsize=(2, 6))
    # plt.figure()

    # Num. of sensors
    nofComb = len(dateTimeSensorCombList)

    # Maximal possible number of sensors
    maxNofComb  = 17
    # Max num of lines
    maxNofLines = 18

    # Create pahtch list
    patchList  = []
    whiteBlank = 'white'

    if nofComb>maxNofComb:
        # Insert sensor list fith specific color patch
        for combIdx in range(maxNofComb):
            color = setColor(combIdx)
            patchList.append(mpatches.Patch(color=color, label=dateTimeSensorCombList[combIdx]['dateAndTime'] + '_' +dateTimeSensorCombList[combIdx]['sensor']))

    else:

        nofSensorLines = nofComb
        nofEmptyLines  = int((maxNofLines-nofSensorLines)/2)

        for i in range(nofEmptyLines):
            # Add empty space for better formating
            patchList.append(mpatches.Patch(color=whiteBlank, label=''))
        for combIdx in range(nofComb):
            color = setColor(combIdx)
            patchList.append(mpatches.Patch(color=color, label=dateTimeSensorCombList[combIdx]['dateAndTime'] + '_' +dateTimeSensorCombList[combIdx]['sensor']))

        for i in range(nofEmptyLines):
            # Add empty space for better formating
            patchList.append(mpatches.Patch(color=whiteBlank, label=''))

    # Attach patch list to a legend
    # legFig.legend(handles=patchList, loc='center')
    legFig.legend(handles=patchList, loc='center')
    # Figure title and save path
    legFigPath = os.path.join(outputDir, legFigTitle)
    # Save figure
    try:
        legFig.savefig(legFigPath, bbox_inches='tight', pad_inches=0, dpi=150)
    except Exception as e:
        myLogger.error(e)

# Set plot collor for each sensor
def setColor(combIdx):
    colorList = ['b', 'r', 'g', 'm', 'k', 'c', 'orange','midnightblue','maroon','springgreen','purple','dimgrey','teal','yellow']

    if combIdx >= len(colorList):
        res   = combIdx%len(colorList)
        color = colorList[res]
    else:
        color = colorList[combIdx]
    return color

# Lower margin of all drawn sensor diagrams for a specific graph
def scaleLowerMargin(graph, parseDataList, normGraphs):
    actualGraph     = 0
    lowerMarginList = []
    for pdIdx in range(len(parseDataList)):

        if normGraphs == 0:
            actualGraph = getActualGraphData(graph,parseDataList,pdIdx)
        else:
            actualGraph = getNormGraphData(graph,parseDataList,pdIdx)
        minValue = actualGraph.min()
        lowerMarginList.append(minValue)

    lowerMargin= min(lowerMarginList)
    whole = int(abs(lowerMargin) / 10)
    rest = abs(lowerMargin) % 10

    if lowerMargin >= 0:
        if rest>5:
            lowerMargin = whole*10
        else:
            lowerMargin = whole*10-10
    else:
        if rest<5:
            lowerMargin = whole*(-10)-10
        else:
            lowerMargin = whole*(-10)-20
    return lowerMargin

# Upper margin of all drawn sensor diagrams for a specific graph
def scaleUpperMargin(graph, parseDataList, normGraphs):
    actualGraph = 0
    upperMarginList = []
    for pdIdx in range(len(parseDataList)):

        if normGraphs == 0:
            actualGraph = getActualGraphData(graph, parseDataList, pdIdx)
        else:
            actualGraph = getNormGraphData(graph, parseDataList, pdIdx)

        maxValue = actualGraph.max()
        upperMarginList.append(maxValue)

    upperMargin = max(upperMarginList)
    whole = int(abs(upperMargin) / 10)
    rest = abs(upperMargin) % 10

    if upperMargin >= 0:
        if rest > 5:
            upperMargin = whole * 10 + 20
        else:
            upperMargin = whole * 10 + 10
    else:
        if rest < 5:
            upperMargin = whole * (-10) + 10
        else:
            upperMargin = whole *(-10)
    return upperMargin


# Get the data for the actual graph for specific graph, chirp, rx channel, and PTU2 file
def getActualGraphData(graph, parseDataList, parseDataIdx):
    actualDiagramData = 0
    if graph == 'level':
        actualDiagramData = calc.getLevel(parseDataList[parseDataIdx])

    elif graph == 'levelPowMet':  # Average power level of chirps [dB].
        actualDiagramData = calc.getLevelPowMet( parseDataList[parseDataIdx])

    elif graph == 'levelMeasSpec':  # Normalised power level [dB].
        actualDiagramData = calc.getLevelMeasSpec( parseDataList[parseDataIdx])

    elif graph == 'levelMeasPowMet':  # Average of normalised power levels of all chirps [dB].
        actualDiagramData = calc.getLevelMeasPowMet(parseDataList[parseDataIdx])

    # Phase difference diagrams
    elif graph == 'frequency':  # Phase difference [°].
        actualDiagramData = calc.getFrequency( parseDataList[parseDataIdx])

    elif graph == 'time':  # Average of the phase differences of all chirps[°].
        actualDiagramData = calc.getTime( parseDataList[parseDataIdx])

    return actualDiagramData

def getNormGraphData(graph, parseDataList, parseDataIdx):
    actualDiagramData = 0
    if graph == 'level':
        actualDiagramData = calc.getLevel(parseDataList[parseDataIdx])

    elif graph == 'levelPowMet':  # Average power level of chirps [dB].
        actualDiagramData = calc.getLevelPowMet( parseDataList[parseDataIdx])

    elif graph == 'levelMeasSpec':  # Normalised power level [dB].
        actualDiagramData = calc.getLevelMeasSpec( parseDataList[parseDataIdx])

    elif graph == 'levelMeasPowMet':  # Average of normalised power levels of all chirps [dB].
        actualDiagramData = calc.getLevelMeasPowMet(parseDataList[parseDataIdx])
    #
    # # Phase difference diagrams
    # elif graph == 'frequency':  # Phase difference [°].
    #     actualDiagramData = calc.getFrequency( parseDataList[parseDataIdx])
    #
    # elif graph == 'time':  # Average of the phase differences of all chirps[°].
    #     actualDiagramData = calc.getTime( parseDataList[parseDataIdx])


    normLevel = actualDiagramData - np.max(actualDiagramData)
    return normLevel
