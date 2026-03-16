from __future__ import annotations
import os
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
from matplotlib.widgets import Button
from matplotlib.ticker import (MaxNLocator, AutoMinorLocator)
import gc
import calcdiagram_functions as calc
import calculation_strategy as strat
import logconfig as log
import data_processing as dp
import auxiliary as aux
from shared.models import GraphData

myLogger = log.antSysDiagLogger.logger

# Basic directory path
basicDir = aux.basicDir

# Output directory path. Plotted graph images are saved here.
outputDir = os.path.join(basicDir,'output')

# legend name
legFigTitle = 'legend.png'


# Save the plotted graph figure with a given title.
def saveFig(fig, figureTitle: str, dpi: int) -> None:
    figTitle = figureTitle+'.png'
    fig.set_figheight(9)
    fig.set_figwidth(16)
    figurePath = os.path.join(outputDir, figTitle)
    try:
        fig.savefig(figurePath, dpi=dpi)
    except Exception as e:
        myLogger.error(e)
    # # fig.savefig('mat.png',bbox_inches='tight')
    plt.close(fig)
    gc.collect()

# Save the plotted graph figure with a given title.
def saveFigRx(fig, figureTitle: str, dpi: int, graph: str, isTrgLayout: int) -> None:
    figTitle = figureTitle+'.png'
    fig.set_figheight(9)
    fig.set_figwidth(16)
    figurePath = os.path.join(outputDir, figTitle)
    try:
        fig.savefig(figurePath, dpi=dpi)
    except Exception as e:
        myLogger.error(e)

    if 'iff' in graph and isTrgLayout == 1:
        figTitle = figureTitle + '_3graph.png'
        fig.set_figheight(9)
        fig.set_figwidth(9)

    figurePath = os.path.join(outputDir, figTitle)
    try:
        fig.savefig(figurePath, dpi=dpi)
        myLogger.info('Image saved: '+ figurePath)
    except Exception as e:
        myLogger.error(e)    
    # fig.savefig('mat.png',bbox_inches='tight')
    plt.close(fig)
    gc.collect()


#                             # ptuList.append(pdIdx)
#
#     return angleList

def getAngleData(parseDataList: list, desiredDiagList: list, plotSetup: dict) -> list:
    combDictList= []
    outputList  = []
    for pdIdx in range(len(parseDataList)):

        for diagIdx in range(len(desiredDiagList)):

            if desiredDiagList[diagIdx] == parseDataList[pdIdx].fileTitle.diagram:

                # Get the ptu angle for the specific PTU2 file
                angle = getAngle(parseDataList, pdIdx)

                # Get the ptu angle for the specific PTU2 file
                tarAngle = getTargetAngle(plotSetup, parseDataList, pdIdx)

                if plotSetup['targetAngle'] == 1:
                    angle = tarAngle

                combDict = dict()

                firstPoint = round(angle[0], 1)
                lastPoint = round(angle[1], 1)
                step = abs(firstPoint - lastPoint)

                # step=getAngleStep(parseDataList[pdIdx])
                nofAnglePoints=len(angle)

                # angle = calc.getPtuAngVals(parseDataList)
                refAnglePoint = round(angle[0], 1)

                combDict.update({'nofAnglePoints': nofAnglePoints, 'angleStepSize': step,'refAnglePoint':refAnglePoint, 'angle':angle,'ptuIdx':pdIdx})
                combDictList.append(combDict)

    # outputList=list(np.unique(np.array(combDictList)))

    for pdIdx in range(len(combDictList)):
        if pdIdx==0:
            # outputDict= dict()
            # outputDict.update({'angleArray':angle,'pdIdx':pdIdx})
            # outputList.append(outputDict)
            outputList.append(combDictList[pdIdx])
            # myLogger.debug('Angle setup comb. added: '+ 'AntTyp-'+str(combDictList[pdIdx]['antType']) + '_DiagType='+combDictList[pdIdx]['diagType']+ '_NofAngPts=' + str(combDictList[pdIdx]['nofAnglePoints']) + '_AngStepSize=' + \
            #               str(combDictList[pdIdx]['angleStepSize']) + '_RefAngPt=' + str(combDictList[pdIdx]['refAnglePoint']))
        isDifferentList = []
        for outputIdx in range(len(outputList)):
            isDifferent = 0
            if outputList[outputIdx]['nofAnglePoints']!=combDictList[pdIdx]['nofAnglePoints'] or outputList[outputIdx]['angleStepSize']!=combDictList[pdIdx]['angleStepSize']\
                    or outputList[outputIdx]['refAnglePoint']!=combDictList[pdIdx]['refAnglePoint']:
               isDifferent = 1
            isDifferentList.append(isDifferent)

        found=1
        for difIdx in range(len(isDifferentList)):
            if isDifferentList[difIdx] == 0:
                found=0
                break

        if found ==1:
            outputList.append(combDictList[pdIdx])
            # myLogger.debug('Angle setup comb. added: '+ 'AntTyp-'+str(combDictList[pdIdx]['antType']) + '_DiagType='+combDictList[pdIdx]['diagType']+  '_NofAngPts=' + str(combDictList[pdIdx]['nofAnglePoints']) + '_AngStepSize=' + str(combDictList[pdIdx]['angleStepSize']) + '_RefAngPt=' + str(combDictList[pdIdx]['refAnglePoint'])+'.')
                # outputList.append(combDictList[pdIdx])

    return outputList

# Get angle step from PTU2 parsed data, for angle setup configuration.
def getAngleStep(parseData) -> float:
    # if isTargetAngle ==1:
    #     angle=calc.getTarAngVals(parseData,upsideDown)
    # else:
    #     angle=calc.getPtuAngVals(parseData)
    angle = calc.getPtuAngVals(parseData)
    firstPoint= round(angle[0],1)
    lastPoint = round(angle[1],1)
    step = abs(firstPoint-lastPoint)
    return step

# Get number fo angle points from PTU2 parsed data, for angle setup configuration.
def getNofAnglePoints(parseData) -> int:
    # if isTargetAngle == 1:
    #     length=len(calc.getTarAngVals(parseData, upsideDown))
    # else:
    #     length=len(calc.getPtuAngVals(parseData))
    length = len(calc.getPtuAngVals(parseData))
    return length

# Get the reference angle point(the first point from the angle array) from PTU2 parsed data, for angle setup configuration.
def getRefAnglePoint(parseData) -> float:
    # if isTargetAngle ==1:
    #     angle=calc.getTarAngVals(parseData,upsideDown)
    # else:
    #     angle=calc.getPtuAngVals(parseData)
    angle = calc.getPtuAngVals(parseData)
    refAnglePoint = round(angle[0],1)
    return refAnglePoint


# Get the list of all configred graphs to be drawn.
def getGraphList(graphConfig: dict) -> list:
    graphList = []
    for graph, set in graphConfig.items():
        if set == 1:
            graphList.append(graph)
    return graphList

# Mapping string for the graph titles
def graphStringMapping(graphTitle: str) -> str:
    graphString     =''
    if graphTitle   == 'level':
        graphString ='Level [dB]'
    elif graphTitle == 'avgLevel':
        graphString ='Avg. Level [dB]'
    elif graphTitle == 'normLevel':
        graphString = 'Norm. Level [dB]'
    elif graphTitle == 'avgNormLevel':
        graphString = 'Avg. Norm. Level [dB]'
    elif graphTitle == 'phaseDiff':
        graphString = 'Phase Diff. [°]'
    elif graphTitle == 'avgPhaseDiff':
        graphString = 'Avg. Phase Diff. [°]'
    elif graphTitle == 'diffPhaseDiff':
        graphString = 'Diff. of Phase Diff. [°]'
    elif graphTitle == 'avgDiffPhaseDiff':
        graphString = 'Avg. Diff. of Phase Diff. [°]'
    elif graphTitle == 'corrPhaseDiff':
        graphString = 'Corr. Phase Diff. [°]'
    return graphString

#         rxChString='RxAnt'+ str(rxCh)
#     return rxChString

# Get PTU angle values
def getAngle(parseDataList: list, x: int) -> np.ndarray:
    angle = calc.getPtuAngVals(parseDataList[x])
    return angle

# Get target angle values
def getTargetAngle(plotSetup: dict, parseDataList: list, x: int) -> np.ndarray:
    upsideDown = getUpsideDown(plotSetup)
    tarAngle = calc.getTarAngVals(parseDataList[x], upsideDown)
    return tarAngle

# Get the info for the upside down set up sensor, from the configuration.
def getUpsideDown(plotSetup: dict) -> bool:
    if plotSetup['upsideDown'] == 0:
        upsideDown = False
    else:
        upsideDown = True
    return upsideDown



# Get the data for the actual graph for specific graph, chirp, rx channel, and PTU2 file
def getActualGraphData(graph: str, rxChannel: int, chirp: int, parseDataList: list, parseDataIdx: int) -> np.ndarray:
    strategy = strat.STRATEGY_REGISTRY.get(graph)
    if strategy is None:
        return 0
    context = strat.CalculationContext(strategy)
    return context.execute(rxChannel, chirp, parseDataList[parseDataIdx])

# Set plot collor for each sensor
def setColor(combIdx: int) -> str:
    colorList = ['b', 'r', 'g', 'm', 'k', 'c', 'orange', 'midnightblue',
                  'maroon', 'springgreen', 'purple', 'dimgrey', 'teal',
                  'yellow', 'thistle', 'lime', 'darkgoldenrod', 'rosybrown',
                  'lightcoral', 'darkred', 'teal', 'navy', 'mediumslateblue',
                  'khaki', 'indigo', 'palevioletred', 'yellowgreen',
                  'palegreen', 'olivedrab', 'tomato']

    if combIdx >= len(colorList):
        res   = combIdx%len(colorList)
        color = colorList[res]
    else:
        color = colorList[combIdx]
    return color

#  Check if diagram is calculation of average from the basic types.
def isAvgDiagram(graph: str) -> bool:
    isAvg = False
    if graph.startswith('avg'):
        isAvg = True
    return isAvg

def getAllOnOneSlideTitle(allOnOneSlideGraphList: list, diagramConfig: dict, desiredDiagramList: list) -> str:
    title = ''
    for i in range(len(allOnOneSlideGraphList)):
        if i==0:
            title = graphStringMapping(allOnOneSlideGraphList[0]['graphType'])
        else:
            title = title+' - '+graphStringMapping(allOnOneSlideGraphList[i]['graphType'])
    if diagramConfig['selectDiagrams'] == 0:
        title = title + ' - All diagrams'

        if diagramConfig['oddOrEven'] == 1:
            title = title + ' - Odd'
        elif diagramConfig['oddOrEven'] == 2:
            title = title + ' - Even'

    elif diagramConfig['selectDiagrams'] == 1:
        title = title + ' - Diag' + str(diagramConfig['lowerNumber']) + ' - Diag' + str(
            diagramConfig['higherNumber'])
        if diagramConfig['oddOrEven'] == 1:
            title = title + ' - Odd'
        elif diagramConfig['oddOrEven'] == 2:
            title = title + ' - Even'

    else:
        title = title + ' - Diag: '
        for i in range(len(desiredDiagramList)):
            title = title + str(desiredDiagramList[i]) + ','

    return title

def getAllOnOneSlideDbLabel(allOnOneSlideGraphList: list) -> str:
    title = ''
    levelList = []
    for i in range(len(allOnOneSlideGraphList)):
        if 'evel' in allOnOneSlideGraphList[i]['graphType']:
            levelList.append(allOnOneSlideGraphList[i]['graphType'])
    for i in range(len(levelList)):
        if i == 0:
            title = graphStringMapping(levelList[i])
        else:
            title = title+' - '+graphStringMapping(levelList[i])
    return title

def getAllOnOneSlideDegLabel(allOnOneSlideGraphList: list) -> str:
    title = ''
    phDiffList = []
    for i in range(len(allOnOneSlideGraphList)):
        if 'Diff' in allOnOneSlideGraphList[i]['graphType']:
            phDiffList.append(allOnOneSlideGraphList[i]['graphType'])
    for i in range(len(phDiffList)):
        if i == 0:
            title = graphStringMapping(phDiffList[i])
        else:
            title = title+' - '+graphStringMapping(phDiffList[i])
    return title

def useSecondAxis(allOnOneSlideGraphList: list) -> bool:
    ret = False
    phDiffFound = False
    levelFound  = False
    for graphIdx in range(len(allOnOneSlideGraphList)):
        if 'evel' in allOnOneSlideGraphList[graphIdx]['graphType']:
            levelFound = True
        elif 'Diff' in allOnOneSlideGraphList[graphIdx]['graphType']:
            phDiffFound = True
        else:
            myLogger.error('No valid graph type for all graphs at one slide configured.')
    ret=levelFound &  phDiffFound
    return ret
    # return [True for graph in allOnOneSlideGraphList if 'evel' in graph and 'Diff' in graph ]

def getPrimAxisTitle(allOnOneSlideGraphList: list) -> str:
    ret = ''
    for graphIdx in range(len(allOnOneSlideGraphList)):
        if 'evel' in allOnOneSlideGraphList[graphIdx]['graphType']:
            ret = getAllOnOneSlideDbLabel(allOnOneSlideGraphList)
        elif 'Diff' in allOnOneSlideGraphList[graphIdx]['graphType']:
            ret = getAllOnOneSlideDegLabel(allOnOneSlideGraphList)
        else :
            myLogger.error('No valid graph type for all graphs at one slide configured.')
    return ret


def plotAll(plotSetup: dict, chirpConfig: dict, allOnOneSlideGraphList: list, desiredDiagList: list, dateTimeSensorList: list, parseDataList: list, diagramConfig: dict, pickradius: int) -> None:
    # Create subplots and plot figure
    fig, ax1 = plt.subplots()
    ax1.grid(True)

    ## Horizontal axis setup
    # Invert axis for showing angle from right to left
    plt.gca().invert_xaxis()

    # Set the x-axis label
    ax1.set_xlabel('PTU Angle [°]', fontsize=20)

    if plotSetup['targetAngle'] == 1:
        # angle = tarAngle
        ax1.set_xlabel('Target Angle [°]', fontsize=20)


    # Set the x-axis scale size
    if plotSetup['xScaleSizeAuto'] == 1:
        # Streching the x axis data from end to end
        ax1.autoscale(enable=True, axis='x', tight=True)
    else:
        if dp.noDiagTypeDataFound(parseDataList)==True:
            # Streching the x axis data from end to end
            ax1.autoscale(enable=True, axis='x', tight=True)
        else:
            if dp.azDataFound(parseDataList) == True:
                ax1.set_xlim(plotSetup['xScaleSizeAz'], (-1) * plotSetup['xScaleSizeAz'])
            else:
                ax1.set_xlim(plotSetup['xScaleSizeEl'], (-1) * plotSetup['xScaleSizeEl'])


    ## Vertical axis setup
    # Check if there are both level [dB] and phase diff [°] like graphs
    if useSecondAxis(allOnOneSlideGraphList):
        # Create second axis
        ax2 = ax1.twinx()
        ax2.grid(True)

        # ax2.set_zorder(0.1)

        # Set the x-axis scale size
        if plotSetup['xScaleSizeAuto'] == 1:
            # Streching the x axis data from end to end
            ax2.autoscale(enable=True, axis='x', tight=True)
        else:
            if dp.noDiagTypeDataFound(parseDataList) == True:
                # Streching the x axis data from end to end
                ax2.autoscale(enable=True, axis='x', tight=True)
            else:
                if dp.azDataFound(parseDataList) == True:
                    ax2.set_xlim(plotSetup['xScaleSizeAz'], (-1) * plotSetup['xScaleSizeAz'])
                else:
                    ax2.set_xlim(plotSetup['xScaleSizeEl'], (-1) * plotSetup['xScaleSizeEl'])

        ax1.set_ylabel(getAllOnOneSlideDbLabel(allOnOneSlideGraphList), fontsize=20)
        ax2.set_ylabel(getAllOnOneSlideDegLabel(allOnOneSlideGraphList), fontsize=20)


    else:
        # Set primary axis label
        ax1.set_ylabel(getPrimAxisTitle(allOnOneSlideGraphList), fontsize=20)

    # Set title to the graph figure
    ax1.set_title(getAllOnOneSlideTitle(allOnOneSlideGraphList, diagramConfig, desiredDiagList), fontsize=20)

    angBiggerThan45=0

    def onclick(event):
        if isinstance(event.artist, Line2D):

            thisline = event.artist
            # order=thisline.get_zorder()
            # print('order: ' +str(order))
            lineLabel = thisline.get_label()
            LineLabelParts = lineLabel.split('_',2)
            ax = LineLabelParts[0]
            graph = LineLabelParts[1]
            lineLabel = LineLabelParts[2]

            xdata = thisline.get_xdata()
            ydata = thisline.get_ydata()
            ind = event.ind
            if ind.size > 1:
                ind = ind[0]

            horAlign = 'left'
            if xdata[ind] < 0:
                horAlign = 'right'

            if ('ideal' in graph):
                lineLabel = graph + ': ' + str(ydata[ind]) + ', angle[°]: ' + str(xdata[ind]) + '. '
            else:
                lineLabel = graphStringMapping(graph) + ': '  + str(ydata[ind]) + ', angle[°]: ' + str(xdata[ind]) + ', ' + lineLabel
            # lineLabel = graphStringMapping(graphName) + ': ' + str(ydata[ind]) +', angle[°]: '+str(xdata[ind])+', ' + lineLabel
            if(ax=='ax1'):
                txt = ax1.text(xdata[ind], ydata[ind], lineLabel, ha=horAlign, style='italic', bbox={'facecolor': 'white', 'alpha': 0.7, 'pad': 5})
                ax1.figure.canvas.draw()
                txt.remove()
            else:
                txt = ax2.text(xdata[ind], ydata[ind], lineLabel, ha=horAlign, style='italic',bbox={'facecolor': 'white', 'alpha': 0.7, 'pad': 5})
                ax2.figure.canvas.draw()
                txt.remove()


    def toggleAxis(event):
        # print('before')
        # a1 = ax1.get_zorder()
        # print(str(a1))
        # a2 = ax2.get_zorder()
        # print(str(a2))
        # ba = btnAxis.get_zorder()
        # print(str(ba))

        if ax1.get_zorder() ==0:

            ax1.set_zorder(0.1)
            ax1.patch.set_alpha(0.5)
            ax2.set_zorder(0)
        else:
            ax2.set_zorder(0.1)
            # ax2.patch.set_alpha(0.5)
            ax1.set_zorder(0)
        # print('after')
        # a1 = ax1.get_zorder()
        # print(str(a1))
        # a2 = ax2.get_zorder()
        # print(str(a2))
        # ba = btnAxis.get_zorder()
        # print(str(ba))

    # xlimAx1=ax1.get_xlim()
    # xlimMin=xlimAx1[0]
    # xlimMax=xlimAx1[1]
    # ylimAx1=ax1.get_ylim()
    # ylimAx2=ax2.get_ylim()
    # ylimMin = min(ylimAx1[0],ylimAx2[0])
    # ylimMax = min(ylimAx1[1], ylimAx2[1])

    if pickradius == 1:
        fig.canvas.mpl_connect('pick_event', onclick)


    # Connect pickradius event to callback
    if pickradius == 1:
        # ip = InsetPosition(ax1, [0.5, 0.5 , 0.20, 0.10])  # posx, posy, width, height
        # ax1.set_axes_locator(ip)
        btnAxis = plt.axes([0.7, 0.00, 0.07, 0.050])
        btnAxis.grid(False)
        bToggleAxis = Button(btnAxis, 'ToggleAxis')
        bToggleAxis.on_clicked(toggleAxis)

    angleList = []

    for pdIdx in range(len(parseDataList)):

        for diagIdx in range(len(desiredDiagList)):

            for dtsIdx in range(len(dateTimeSensorList)):

                for graphIdx in range(len(allOnOneSlideGraphList)):
                    if desiredDiagList[diagIdx]==parseDataList[pdIdx].fileTitle.diagram and dateTimeSensorList[dtsIdx]['sensor'] == parseDataList[pdIdx].fileTitle.sensor and \
                            dateTimeSensorList[dtsIdx]['dateAndTime'] == parseDataList[pdIdx].fileTitle.dateAndTime:

                        # Get the ptu angle for the specific PTU2 file
                        angle = getAngle(parseDataList, pdIdx)

                        # Get the ptu angle for the specific PTU2 file
                        tarAngle = getTargetAngle(plotSetup, parseDataList, pdIdx)

                        if plotSetup['targetAngle'] == 1:
                            angle = tarAngle

                        # Set xticks according to the angle values from files a plot contains
                        if abs(angle[0]) > 45:
                            angBiggerThan45=1

                        if angBiggerThan45 !=1:
                            ax1.set_xticks(np.arange(90, -91, -2.5), minor = True)
                            plt.xticks(np.arange(90, -91, -5))
                            
                        else:
                            ax1.set_xticks(np.arange(90, -91, -5), minor = True)
                            plt.xticks(np.arange(90, -91, -10))
                            

                        # Get the valid chirp list
                        validChirpList = dp.getValidChirp(chirpConfig, parseDataList, pdIdx)

                        # Get the num. of actual Rx channels for a given graph and a given PTU2 file
                        nofAcctualRxCh = dp.getNofActualRxChannels(allOnOneSlideGraphList[graphIdx]['graphType'], parseDataList, pdIdx)

                        # Set the color for the sensor specific plot lines
                        color = setColor(dtsIdx)

                        # Traverse through all rxChannels
                        for rxCh in range(nofAcctualRxCh):
                            plotLabel =allOnOneSlideGraphList[graphIdx]['graphType'] + '_' +dateTimeSensorList[dtsIdx]['dateAndTime'] + '_' + dateTimeSensorList[dtsIdx]['sensor']+ ', Diag' +str(desiredDiagList[diagIdx])+ ', ' + dp.rxChStringMapping(allOnOneSlideGraphList[graphIdx]['graphType'], rxCh)
                            # plotLabel = dp.rxChStringMapping(allOnOneSlideGraphList[graphIdx], rxCh)


                            # Processing for average function graphs
                            if isAvgDiagram(allOnOneSlideGraphList[graphIdx]['graphType']) == True:

                                # Get the actual graph data for specific Rx channel, chirp and a PTU2 file
                                actualGraphData = getActualGraphData(allOnOneSlideGraphList[graphIdx]['graphType'], rxCh, 0, parseDataList, pdIdx)
                                # Plot data
                                if useSecondAxis(allOnOneSlideGraphList):
                                    if 'evel' in allOnOneSlideGraphList[graphIdx]['graphType']:
                                        plotLabel = 'ax1_' + plotLabel
                                        ax1.plot(angle, actualGraphData, '.-',pickradius=2, color=color, label = plotLabel)
                                    else:
                                        plotLabel='ax2_'+plotLabel
                                        ax2.plot(angle, actualGraphData, '.-',pickradius=2, color=color, label=plotLabel)
                                else:
                                    plotLabel = 'ax1_' + plotLabel
                                    ax1.plot(angle, actualGraphData, '.-',pickradius=2, color=color, label = plotLabel)
                            else:
                                # Traverse through the valid chirps
                                for chirp in range(len(validChirpList)):

                                    # Get the actual graph data for specific Rx channel, chirp and a PTU2 file
                                    actualGraphData = getActualGraphData(allOnOneSlideGraphList[graphIdx]['graphType'], rxCh, chirp, parseDataList, pdIdx)

                                    # Plot data
                                    if useSecondAxis(allOnOneSlideGraphList):
                                        if 'evel' in allOnOneSlideGraphList[graphIdx]['graphType']:
                                            plotLabel = 'ax1_' + plotLabel
                                            ax1.plot(angle, actualGraphData, '.-',pickradius=2, color=color, label = plotLabel)
                                        else:
                                            plotLabel = 'ax2_' + plotLabel
                                            ax2.plot(angle, actualGraphData, '.-',pickradius=2, color=color, label = plotLabel)
                                    else:
                                        plotLabel = 'ax1_' + plotLabel
                                        ax1.plot(angle, actualGraphData, '.-', pickradius=2, color=color, label = plotLabel)


    if plotSetup['idealPhaseDiff'] == 1:

        angleList = getAngleData(parseDataList, desiredDiagList, plotSetup)
        # angleList=idealCurvesDataList['angleList']
        # ptuList = idealCurvesDataList['ptuList']

        for angIdx in range(len(angleList)):
            # for ptuIdx in range(len(ptuList)):
            #     if angIdx == ptuIdx:

            nofAcctualRxCh= parseDataList[angleList[angIdx]['ptuIdx']].antennaInfo.nofAntennaDiffValues
            for rxCh in range(nofAcctualRxCh):
                actualGraphData = getActualGraphData('idealPhaseDiff', rxCh, 0, parseDataList,angleList[angIdx]['ptuIdx'])

                label = 'Phase Diff. [°] - ideal' + '_'
                if useSecondAxis(allOnOneSlideGraphList):
                    label = 'ax2_' + label
                    ax2.plot(angleList[angIdx]['angle'], actualGraphData, '-', color='olive',linewidth=3.5, pickradius=2, label=label)
                else:
                    label = 'ax1_' + label
                    ax1.plot(angleList[angIdx]['angle'], actualGraphData, '-', color='olive',linewidth=3.5, pickradius=2, label=label)

                        # # # Insert the ideal phase difference lines
                        # if plotSetup['idealPhaseDiff'] == 1 and allOnOneSlideGraphList[graphIdx].endswith('Diff') and 'avgDiffPhase' not in allOnOneSlideGraphList[graphIdx] and 'diffPhase' not in allOnOneSlideGraphList[graphIdx]:
                        #     actualGraphData = getActualGraphData('idealPhaseDiff', rxCh, 0, parseDataList, pdIdx)
                        #     label= graphStringMapping(allOnOneSlideGraphList[graphIdx]) + ' - ideal'+'_'
                        #     if useSecondAxis(allOnOneSlideGraphList):
                        #         label = 'ax2_' + label
                        #         ax2.plot(angle, actualGraphData, '-', color='olive', pickradius=2, linewidth=3.5, label=label)
                        #     else:
                        #         label = 'ax1_' + label
                        #         ax1.plot(angle, actualGraphData, '-', color='olive', pickradius=2, linewidth=3.5, label = label)

    # Assign figure title
    figureTitle = 'all_on_one_slide'

    if pickradius == 0:
        ylimits = plt.ylim()
        ylimtick = (ylimits[0] + ylimits[1])*0.5 + np.array((-0.5, 0.5)) * (ylimits[1] - ylimits[0]) * (1 + 0.2)
        plt.ylim(min(ylimtick), max(ylimtick))
        ax1.yaxis.set_major_locator(MaxNLocator(nbins=10))
        ax1.yaxis.set_minor_locator(AutoMinorLocator())
        ax1.grid(visible=True, which = 'minor', color = '#999999', linestyle = 'dashed', alpha = 0.2)
        # Save figure
        saveFig(fig, figureTitle, plotSetup['imageDpi'])
        # Close all plots
        # plt.close('all')
    else:

        plt.show()



# Generate graph for specific graph type, specific diagram num., all Rx channels together, and all sensors.
def plotDiagram(plotSetup: dict, chirpConfig: dict, graph: str, diagramNum: int, dateAndTimeSensorList: list, antType: int, parseDataList: list, dictScalingDict: dict, lowerMarginDict: dict, upperMarginDict: dict, pickradius: int) -> GraphData:
    if 'iff' in graph and plotSetup['threeGraphLayout']==1:
        font = 18
    else:
        font = 20
    # Instantiation of meta data object
    graphData = GraphData()

    # Assigning graph title to the meta data
    graphData.graphTitle=graph

    # Create subplots and plot figure
    fig, ax1 = plt.subplots()

    def onclick(event):
        if isinstance(event.artist, Line2D):

            thisline  = event.artist
            lineLabel = thisline.get_label()
            xdata = thisline.get_xdata()
            ydata = thisline.get_ydata()
            ind = event.ind
            if ind.size > 1 :
                ind =ind[0]
            # sign=''
            # if('evel' in graph):
            #     sign='dB'
            # else:
            #     sign ='°'

            horAlign='left'
            if xdata[ind] < 0:
                horAlign='right'

            lineLabel = graphStringMapping(graph) + ': ' + str(ydata[ind]) +', angle[°]: '+str(xdata[ind])+', ' + lineLabel

            txt = ax1.text(xdata[ind], ydata[ind], lineLabel, ha=horAlign, style='italic',bbox={'facecolor': 'white', 'alpha': 0.7, 'pad': 5})
            ax1.figure.canvas.draw()
            txt.remove()

    # Connect pickradius event to callback
    if pickradius == 1:
        fig.canvas.mpl_connect('pick_event', onclick)


    # Invert axis for showing angle from right to left
    plt.gca().invert_xaxis()

    # Show plot grid
    plt.grid(True)

    # Set title to the graph figure
    ax1.set_title(graphStringMapping(graph), fontsize=font)

    # Set y-axis label for specific general graph types
    ax1.set_ylabel(graphStringMapping(graph), fontsize=font)

    angBiggerThan45=0

    angleTemp=0

    angleTempPdIdxDict = {
        'angletemp': 0,
        'pdIdx': 0
    }

    angleTempList = []

    # Traversing through all PTU2 files
    for pdIdx in range(len(parseDataList)):

    # Traversing through all sensors
        for dateTimeSensorIdx in range(len(dateAndTimeSensorList)):
            # Looking for PTU file for specific sensor and specific diagram number
            if (diagramNum ==parseDataList[pdIdx].fileTitle.diagram) and (dateAndTimeSensorList[dateTimeSensorIdx]['sensor']==parseDataList[pdIdx].fileTitle.sensor) \
                    and dateAndTimeSensorList[dateTimeSensorIdx]['dateAndTime']==parseDataList[pdIdx].fileTitle.dateAndTime:

                # Filling in the meta data from the PTU2 title
                if parseDataList[pdIdx].fileTitle.sensorFound == 1:
                    graphData.sensorId = parseDataList[pdIdx].fileTitle.sensor
                if parseDataList[pdIdx].fileTitle.txAntFound == 1:
                    graphData.txAnt = parseDataList[pdIdx].fileTitle.txAnt
                if parseDataList[pdIdx].fileTitle.diagramFound == 1:
                    graphData.diagramNr = parseDataList[pdIdx].fileTitle.diagram
                if parseDataList[pdIdx].fileTitle.seqNumFound == 1:
                    graphData.seqNum = parseDataList[pdIdx].fileTitle.seqNum
                if parseDataList[pdIdx].fileTitle.dateAndTimeFound == 1:
                    graphData.dateAndTime = parseDataList[pdIdx].fileTitle.dateAndTime

                # Fill in the antenna type info
                graphData.antennaType = str(antType)

                # Filling in the meta data from the measurement setup inside the PTU2 file
                if parseDataList[pdIdx].measSetupInfo.antennaDiagramTypeFound == 1:
                    graphData.antennaDiagramType = parseDataList[pdIdx].measSetupInfo.antennaDiagramType
                if parseDataList[pdIdx].measSetupInfo.sensorUpsideDownFound == 1:
                    graphData.sensorUpsideDown = parseDataList[pdIdx].measSetupInfo.sensorUpsideDown
                if parseDataList[pdIdx].measSetupInfo.oppositeToPanAngleFound == 1:
                    graphData.oppositeToPanAngle = parseDataList[pdIdx].measSetupInfo.oppositeToPanAngle
                if parseDataList[pdIdx].measSetupInfo.phyDoppGenDistFound == 1:
                    graphData.phyDoppGenDist = parseDataList[pdIdx].measSetupInfo.phyDoppGenDist
                if parseDataList[pdIdx].measSetupInfo.rfBoardMidHeightPtuZeroFound == 1:
                    graphData.rfBoardMidHeightPtuZero = parseDataList[pdIdx].measSetupInfo.rfBoardMidHeightPtuZeroFound
                if parseDataList[pdIdx].measSetupInfo.doppGenHeightPtuZeroFound == 1:
                    graphData.doppGenHeightPtuZero = parseDataList[pdIdx].measSetupInfo.doppGenHeightPtuZeroFound

                # Get the ptu angle for the specific PTU2 file
                angle = getAngle(parseDataList, pdIdx)

                # Get the ptu angle for the specific PTU2 file
                tarAngle = getTargetAngle(plotSetup, parseDataList, pdIdx)

                # Set graph title to the figure
                ax1.set_title(graphStringMapping(graph)+ ' - ' + 'AntTyp' + str(graphData.antennaType)+ ' - ' + 'Diag' + str(graphData.diagramNr), fontsize=font)

                # Level and  phase difference specific graph notations
                ax1.set_ylabel(graphStringMapping(graph), fontsize=font)

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
                    if parseDataList[pdIdx].measSetupInfo.antennaDiagramTypeFound == 1:
                        if graphData.antennaDiagramType =='Az':
                            ax1.set_xlim(plotSetup['xScaleSizeAz'], (-1) * plotSetup['xScaleSizeAz'])
                        else:
                            ax1.set_xlim(plotSetup['xScaleSizeEl'], (-1) * plotSetup['xScaleSizeEl'])

                    else:
                        # Streching the x axis data from end to end
                        ax1.autoscale(enable=True, axis='x', tight=True)


                # Set the x-axis label
                ax1.set_xlabel('PTU Angle [°]', fontsize=font)
                if plotSetup['targetAngle'] == 1:
                    angle = tarAngle
                    ax1.set_xlabel('Target Angle [°]', fontsize=font)

                # Get the valid shirp list
                validChirpList = dp.getValidChirp(chirpConfig, parseDataList, pdIdx)

                # Get the num. of actual Rx channels for a given graph and a given PTU2 file
                nofAcctualRxCh = dp.getNofActualRxChannels(graph, parseDataList,pdIdx)

                # Set the color for the sensor specific plot lines
                color = setColor(dateTimeSensorIdx)

                # Traverse through all rxChannels
                for rxCh in range(nofAcctualRxCh):

                    # if nofAcctualRxCh <= getMaxNofRxCh(graphConfig,graphIdx, parseDataList):

                    plotLabel = graphData.dateAndTime + '_' + graphData.sensorId +', '+ dp.rxChStringMapping(graph, rxCh)

                    # Processing for average function graphs
                    if isAvgDiagram(graph) == True:
                        # # Get the actual graph for specific Rx channel, all chirps, and a specific PTU2 file
                        # actualGraphData = getActualGraphData(graph, rxCh, 0, parseDataList, pdIdx)
                        # # Plot data
                        # ax1.plot(angle, actualGraphData,'.-',color=color)
                        # Processing for diffPhaseDiff diagrams
                        if 'DiffPhaseDiff' in graph:

                            # Zoom the y-axis
                            scaleMax = dictScalingDict[diagramNum][graph]
                            # scaleMax = scaleMax[graph]

                            yAxisRange = scaleMax *  float(plotSetup['diffPhaseDiffScalingFactor'])

                            plt.ylim(-yAxisRange, yAxisRange)

                            # Get the actual graph data for specific Rx channel, chirp and a PTU2 file
                            actualGraphData = getActualGraphData(graph, rxCh, 0, parseDataList, pdIdx)
                            # Plot data
                            ax1.plot(angle, actualGraphData,  '.-',pickradius =2, color=color,label =plotLabel)

                        else:
                            # Get the actual graph data for specific Rx channel, chirp and a PTU2 file
                            actualGraphData = getActualGraphData(graph, rxCh, 0, parseDataList, pdIdx)

                            # Scale the y-axis according to the upper and lower margins of all graphs from one graph type
                            lowerMargin = lowerMarginDict[graph]
                            upperMargin = upperMarginDict[graph]
                            plt.ylim(lowerMargin, upperMargin)

                            # Plot data
                            ax1.plot(angle, actualGraphData, '.-', pickradius=2, color=color,label =plotLabel)
                    else:
                        # Traverse through the valid chirps
                        for chirp in range(len(validChirpList)):
                            # Processing for diffPhaseDiff diagrams
                            if graph.startswith('diff'):

                                # Zoom the y-axis
                                scaleMax = dictScalingDict[diagramNum][graph]

                                yAxisRange = scaleMax * float(plotSetup['diffPhaseDiffScalingFactor'])

                                plt.ylim(-yAxisRange, yAxisRange)

                                # Get the actual graph data for specific Rx channel, chirp and a PTU2 file
                                actualGraphData = getActualGraphData(graph, rxCh, chirp, parseDataList, pdIdx)
                                # Plot data
                                ax1.plot(angle, actualGraphData, '.-',pickradius=2, color=color, label=plotLabel)

                            else:

                                # Get the actual graph data for specific Rx channel, chirp and a PTU2 file
                                actualGraphData = getActualGraphData(graph, rxCh, chirp, parseDataList, pdIdx)

                                # Scale the y-axis according to the upper and lower margins of all graphs from one graph type
                                lowerMargin = lowerMarginDict[graph]
                                upperMargin = upperMarginDict[graph]
                                plt.ylim(lowerMargin, upperMargin)

                                # Plot data
                                ax1.plot(angle, actualGraphData, '.-', pickradius = 2, color=color, label =plotLabel)

                                # myLogger.info('Line plotted.')

                # Adding the ideal phase difference line to the phase difference graphs
                if graph.endswith('Diff') and 'avgDiffPhase' not in graph and 'diffPhase' not in graph and \
                        plotSetup['idealPhaseDiff'] == 1:

                    if np.array_equal(angleTemp, angle) == False:
                        angleTemp = angle
                        angleTempPdIdxDict['angletemp'] = angle
                        angleTempPdIdxDict['pdIdx'] = pdIdx

                        angleTempList.append(angleTempPdIdxDict)

    for angTempIdx in range(len(angleTempList)):
        for rxCh in range(nofAcctualRxCh):
            actualGraphData = getActualGraphData('idealPhaseDiff', rxCh, 0, parseDataList, angleTempList[angTempIdx]['pdIdx'])
            ax1.plot(angleTempList[angTempIdx]['angletemp'], actualGraphData, '-', color='olive', linewidth=3.5, pickradius=2, label='ideal curve')


                    # # Insert the ideal phase difference lines
                    # if graph.endswith('Diff') and 'avgDiffPhase' not in graph and 'diffPhase' not in graph and plotSetup['idealPhaseDiff'] == 1:
                    #     actualGraphData = getActualGraphData('idealPhaseDiff', rxCh, 0, parseDataList, pdIdx)
                    #     ax1.plot(angle, actualGraphData, '-', color='olive', pickradius = 2, linewidth=3.5,label ='ideal curve')

    # Assign figure title
    figureTitle = graphData.graphTitle  +'_AntTyp'+ str(antType)+'_TxAnt'+str(graphData.txAnt) +'_Diag'+str(graphData.diagramNr)
    graphData.figureTitle = figureTitle + '.png'

    if pickradius == 0:
        if 'iff' in graph:
            ylimits = plt.ylim()
            ylimtick = (ylimits[0] + ylimits[1])*0.5 + np.array((-0.5, 0.5)) * (ylimits[1] - ylimits[0]) * (1 + 0.2)
            plt.ylim(min(ylimtick), max(ylimtick))
            ax1.yaxis.set_major_locator(MaxNLocator(nbins=10))
        ax1.yaxis.set_minor_locator(AutoMinorLocator())
        ax1.grid(visible=True, which = 'minor', color = '#999999', linestyle = 'dashed', alpha = 0.2)
        # Save figure
        saveFig(fig, figureTitle, plotSetup['imageDpi'])

        #myLogger.info('Image saved')
        # Close all plots
        # plt.close('all')
    else:
        plt.show()

    #  Return graph data pbject
    return graphData

# Generate graphs for specific graph type, specific diagram num., all Rx channels separate, and all sensors.
def plotDiagramRxCh(plotSetup: dict, chirpConfig: dict, graph: str, diagramNum: int, rxCh: int, dateTimeSensorCombList: list, antType: int, parseDataList: list, dictScalingDict: dict, lowerMarginDict: dict, upperMarginDict: dict, pickradius: int) -> GraphData:
    if 'iff' in graph and plotSetup['threeGraphLayout'] == 1:
        font = 18
    else:
        font = 20
    # Instantiation of meta data object
    graphData = GraphData()

    # Assigning graph title to the meta data object
    graphData.graphTitle = graph

    # Create subplots and plot figure
    fig, ax1 = plt.subplots()

    def onclick(event):
        if isinstance(event.artist, Line2D):

            thisline  = event.artist
            lineLabel = thisline.get_label()
            xdata = thisline.get_xdata()
            ydata = thisline.get_ydata()
            ind   = event.ind
            if ind.size > 1 :
                ind =ind[0]

            horAlign='left'
            if xdata[ind] < 0:
                horAlign='right'

            lineLabel = graphStringMapping(graph) + ': ' + str(ydata[ind]) +', angle[°]: '+str(xdata[ind])+', ' + lineLabel
            txt = ax1.text(xdata[ind], ydata[ind], lineLabel, ha=horAlign, style='italic', bbox={'facecolor': 'white', 'alpha': 0.7, 'pad': 5})
            ax1.figure.canvas.draw()
            txt.remove()

    # Connect pickradius event to callback
    if pickradius == 1:
        fig.canvas.mpl_connect('pick_event', onclick)



    # Invert axis for showing angle from right to left
    plt.gca().invert_xaxis()
    # Show plot grid
    plt.grid(True)

    angBiggerThan45 = 0
    # ax1.grid(which='both', axis='both', linewidth=0.75, linestyle='-', color='0.75')
    angleTemp = 0

    angleTempList = []

    angleTempPdIdxDict = {
        'angletemp':0,
        'pdIdx':0
    }
    # Traversing through all PTU2 files
    for pdIdx in range(len(parseDataList)):

        # if parseDataList.parseDataList[pdIdx].antennaInfo.antennaType ==antType:
        # Traversing through all sensors
        for dateTimeSensorIdx in range(len(dateTimeSensorCombList)):
            # Looking for PTU file for specific sensor and specific diagram number
            if diagramNum == parseDataList[pdIdx].fileTitle.diagram and \
                    dateTimeSensorCombList[dateTimeSensorIdx]['sensor'] == parseDataList[pdIdx].fileTitle.sensor and \
                    dateTimeSensorCombList[dateTimeSensorIdx]['dateAndTime']==parseDataList[pdIdx].fileTitle.dateAndTime:

                # Filling in the meta data from the PTU2 title
                if parseDataList[pdIdx].fileTitle.sensorFound == 1:
                    graphData.sensorId = parseDataList[pdIdx].fileTitle.sensor
                if parseDataList[pdIdx].fileTitle.txAntFound == 1:
                    graphData.txAnt = parseDataList[pdIdx].fileTitle.txAnt
                if parseDataList[pdIdx].fileTitle.diagramFound == 1:
                    graphData.diagramNr = parseDataList[pdIdx].fileTitle.diagram
                if parseDataList[pdIdx].fileTitle.dateAndTimeFound == 1:
                    graphData.dateAndTime = parseDataList[pdIdx].fileTitle.dateAndTime

                if parseDataList[pdIdx].fileTitle.seqNumFound == 1:
                    graphData.seqNum = parseDataList[pdIdx].fileTitle.seqNum

                # Filling in the meta data from the measurement setup inside the PTU2 file
                if parseDataList[pdIdx].measSetupInfo.antennaDiagramTypeFound == 1:
                    graphData.antennaDiagramType = parseDataList[pdIdx].measSetupInfo.antennaDiagramType
                if parseDataList[pdIdx].measSetupInfo.sensorUpsideDownFound == 1:
                    graphData.sensorUpsideDown = parseDataList[pdIdx].measSetupInfo.sensorUpsideDown
                if parseDataList[pdIdx].measSetupInfo.oppositeToPanAngleFound == 1:
                    graphData.oppositeToPanAngle = parseDataList[pdIdx].measSetupInfo.oppositeToPanAngle
                if parseDataList[pdIdx].measSetupInfo.phyDoppGenDistFound == 1:
                    graphData.phyDoppGenDist = parseDataList[pdIdx].measSetupInfo.phyDoppGenDist
                if parseDataList[pdIdx].measSetupInfo.rfBoardMidHeightPtuZeroFound == 1:
                    graphData.rfBoardMidHeightPtuZero = parseDataList[pdIdx].measSetupInfo.rfBoardMidHeightPtuZeroFound
                if parseDataList[pdIdx].measSetupInfo.doppGenHeightPtuZeroFound == 1:
                    graphData.doppGenHeightPtuZero = parseDataList[pdIdx].measSetupInfo.doppGenHeightPtuZeroFound

                # Fill in antenna type
                graphData.antennaType = str(antType)

                # Fill in Rx channel number
                graphData.rxCh = rxCh

                # Get the PTU angle for the specific PTU2 file
                angle = getAngle(parseDataList, pdIdx)

                # Get the target angle for the specific PTU2 file
                tarAngle = getTargetAngle(plotSetup, parseDataList, pdIdx)

                # Set graph title to the figure
                # ax1.set_title(graphStringMapping(graph)+ ' - ' + 'AntTyp' + str(antType) + ' - ' + 'Diag' + str(graphData.diagramNr) + ' - ' + dp.rxChStringMapping(graph, rxCh), fontsize=font)
                ax1.set_title(graphStringMapping(graph)+ ' - ' + 'AntTyp' + str(antType) + ' - ' + 'Diag' + str(graphData.diagramNr) + ' - ' + r'$\bf{' + str(dp.rxChStringMapping(graph, rxCh)) + '}$', fontsize=font)

                # Level and  phase difference specific graph notations
                ax1.set_ylabel(graphStringMapping(graph), fontsize=font)

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
                    if parseDataList[pdIdx].measSetupInfo.antennaDiagramTypeFound == 1:
                        if graphData.antennaDiagramType == 'Az':
                            ax1.set_xlim(plotSetup['xScaleSizeAz'], (-1) * plotSetup['xScaleSizeAz'])
                        else:
                            ax1.set_xlim(plotSetup['xScaleSizeEl'], (-1) * plotSetup['xScaleSizeEl'])

                    else:
                        # Streching the x axis data from end to end
                        ax1.autoscale(enable=True, axis='x', tight=True)

                # Set x-axis label
                ax1.set_xlabel('PTU Angle [°]', fontsize=font)
                if plotSetup['targetAngle'] == 1:
                    angle = tarAngle
                    ax1.set_xlabel('Target Angle [°]', fontsize=font)

                # Get the list of valid chirps
                validChirpList = dp.getValidChirp(chirpConfig, parseDataList, pdIdx)

                # Get the num. of actual Rx channels for the diagram in question and the given PTU2 file (sensor).

                # Set color for the sensor specific plot lines
                color = setColor(dateTimeSensorIdx)

                # Set label for each plot line
                lineLabel = graphData.dateAndTime + '_' + graphData.sensorId

                # Processing for graphs that are NOT average function.
                if isAvgDiagram(graph) == True:
                    # Check if it is a diffPhaseDiff graph
                    if 'DiffPhaseDiff' in graph:

                        # Zoom the y-axis
                        scaleMax = dictScalingDict[diagramNum][graph]
                        # scaleMax=scaleMax[graph]
                        yAxisRange = scaleMax * float(plotSetup['diffPhaseDiffScalingFactor'])

                        plt.ylim(-yAxisRange, yAxisRange)

                        # Get the actual graph values
                        actualGraphData = getActualGraphData(graph, rxCh, 0, parseDataList, pdIdx)


                        # Plot the graph
                        ax1.plot(angle, actualGraphData, '.-', color=color, pickradius = 1, label=lineLabel)

                    else:
                        # Get the actual graph values
                        actualGraphData = getActualGraphData(graph, rxCh, 0, parseDataList, pdIdx)

                        # Set the y-axis margins accordingly to the margins of all diagrams for the specific graph type
                        lowerMargin = lowerMarginDict[graph]
                        upperMargin = upperMarginDict[graph]
                        plt.ylim(lowerMargin, upperMargin)

                        # Plot the graph
                        ax1.plot(angle, actualGraphData, '.-', color=color, pickradius = 2, label=lineLabel)

                else:
                    # Traverse through the valid chirps
                    for chirp in range(len(validChirpList)):

                        # Check if it is a diffPhaseDiff graph
                        if graph.startswith('diff'):

                            # Zoom the y-axis
                            scaleMax = dictScalingDict[diagramNum][graph]
                            # scaleMax = scaleMax[graph]

                            yAxisRange = scaleMax* float(plotSetup['diffPhaseDiffScalingFactor'])

                            plt.ylim(-yAxisRange,yAxisRange)


                            # Get the actual graph values
                            actualGraphData = getActualGraphData(graph, rxCh, chirp, parseDataList, pdIdx)

                            # Plot the graph
                            ax1.plot(angle, actualGraphData,'.-', color=color, pickradius = 2, label=lineLabel)

                        else:
                            # Get the actual graph values
                            actualGraphData = getActualGraphData(graph, rxCh, chirp, parseDataList, pdIdx)

                            # Set the y-axis margins accordingly to the margins of all diagrams for the specific graph type
                            lowerMargin = lowerMarginDict[graph]
                            upperMargin = upperMarginDict[graph]
                            plt.ylim(lowerMargin, upperMargin)

                            # Plot the graph
                            ax1.plot(angle, actualGraphData,  '.-', color=color, pickradius = 2, label=lineLabel)

                            # myLogger.info('line plotted.')

                # Adding the ideal phase difference line to the phase difference graphs
                if graph.endswith('Diff') and 'avgDiffPhase' not in graph and 'diffPhase' not in graph and plotSetup['idealPhaseDiff'] == 1:

                    if np.array_equal(angleTemp,angle) == False:

                        angleTemp = angle
                        angleTempPdIdxDict['angletemp'] = angle
                        angleTempPdIdxDict['pdIdx'] = pdIdx

                        angleTempList.append(angleTempPdIdxDict)

    for angTempIdx in range(len(angleTempList)):

        actualGraphData = getActualGraphData('idealPhaseDiff', rxCh, 0, parseDataList, angleTempList[angTempIdx]['pdIdx'])
        ax1.plot(angleTempList[angTempIdx]['angletemp'], actualGraphData, '-', color='olive', linewidth=3.5, pickradius=2, label='ideal curve')

    # Asigning figure title and puting it in the graph meta data object
    figureTitle = graphData.graphTitle +'_AntTyp'+ str(antType) +'_TxAnt'+str(graphData.txAnt) +'_Diag'+str(graphData.diagramNr) +'_RxCh'+str(graphData.rxCh)
    graphData.figureTitle = figureTitle + '.png'
    if 'iff' in graph and plotSetup['threeGraphLayout'] == 1:
        graphData.figureTitle3graph = figureTitle+'_3graph.png'

    if pickradius == 0:
        if 'iff' in graph:
            ylimits = plt.ylim()
            ylimtick = (ylimits[0] + ylimits[1])*0.5 + np.array((-0.5, 0.5)) * (ylimits[1] - ylimits[0]) * (1 + 0.2)
            plt.ylim(min(ylimtick), max(ylimtick))
            ax1.yaxis.set_major_locator(MaxNLocator(nbins=10))
        ax1.yaxis.set_minor_locator(AutoMinorLocator())
        ax1.grid(visible=True, which = 'minor', color = '#999999', linestyle = 'dashed', alpha = 0.2)
        # Save figure
        saveFigRx(fig, figureTitle, plotSetup['imageDpi'], graph, plotSetup['threeGraphLayout'])

        #myLogger.info('Image saved')
        # Close all plots
        # plt.close('all')


    else:
        plt.show()

    # Return the meta data object
    return graphData

# Generate legend figure for all sensors
def generateLegend(plotSetup: dict, dateTimeSensorCombList: list) -> None:

    # Create legend figure
    legFig = plt.figure(figsize=(2, 6))

    # plt.figure()

    # Num. of sensors
    nofComb = len(dateTimeSensorCombList)
    # Maximal possible number of sensors
    if plotSetup['idealPhaseDiff'] == 1:
        maxNofComb = 16

    else:
        maxNofComb = 17

    # Max num of lines
    maxNofLines = 18

    # Create pahtch list
    patchList  = []
    whiteBlank ='white'

    if nofComb>maxNofComb:
        # Insert sensor list fith specific color patch
        for combIdx in range(maxNofComb):
            color = setColor(combIdx)
            patchList.append(mpatches.Patch(color=color, label=dateTimeSensorCombList[combIdx]['dateAndTime'] + '_' +dateTimeSensorCombList[combIdx]['sensor']))
        # Add the ideal phase difference line
        if plotSetup['idealPhaseDiff'] == 1:
            patchList.append(mpatches.Patch(color='olive', label='Ideal phase-diff'))
    else:
        if plotSetup['idealPhaseDiff'] == 1:
            nofSensorLines = nofComb+1
        else:
            nofSensorLines = nofComb
        nofEmptyLines = int((maxNofLines-nofSensorLines)/2)
        for i in range(nofEmptyLines):
            # Add empty space for better formating
            patchList.append(mpatches.Patch(color=whiteBlank, label=''))
        for combIdx in range(nofComb):
            color = setColor(combIdx)
            patchList.append(mpatches.Patch(color=color, label=dateTimeSensorCombList[combIdx]['dateAndTime'] + '_' +dateTimeSensorCombList[combIdx]['sensor']))

        # Add the ideal phase difference line
        if plotSetup['idealPhaseDiff'] == 1:
            patchList.append(mpatches.Patch(color='olive', label='Ideal phase-diff'))
        for i in range(nofEmptyLines):
            # Add empty space for better formating
            patchList.append(mpatches.Patch(color=whiteBlank, label=''))

    # Attach patch list to a legend
    legFig.legend(handles=patchList, loc='center')


    # Figure title and save path
    legFigPath = os.path.join(outputDir, legFigTitle)
    # Save figure
    try:
        legFig.savefig(legFigPath, bbox_inches='tight', pad_inches=0, dpi=150)
    except Exception as e:
        myLogger.error(e)
    #
    # if plotSetup['ShowCertainPlotWindow']==1:
    #     plt.show()


# Lower margin of all drawn sensor diagrams for a specific graph
def scaleLowerMargin(graph: str, chirpSetup: dict, parseDataList: list) -> float | None:
    actualGraph = 0
    lowerMarginList = []
    for pdIdx in range(len(parseDataList)):

        validChirpList = dp.getValidChirp(chirpSetup, parseDataList,pdIdx)
        nofRxCh = dp.getMaxNofRxCh(graph, parseDataList)
        for chirp in range(len(validChirpList)):
            for rxCh in range(nofRxCh):
                actualGraph = getActualGraphData(graph,rxCh,chirp,parseDataList,pdIdx)
                minValue = actualGraph.min()
                lowerMarginList.append(minValue)

    if len(lowerMarginList) !=0:
        lowerMargin = min(lowerMarginList)
        whole = int(abs(lowerMargin) / 10)
        rest = abs(lowerMargin) % 10

        if lowerMargin >= 0:
            if rest>5:
                lowerMargin = whole*10
            else:
                lowerMargin = whole*10-10
        else:
            if rest <5:
                lowerMargin = whole*(-10)-10
            else:
                lowerMargin = whole*(-10)-20
        return lowerMargin

# Upper margin of all drawn sensor diagrams for a specific graph
def scaleUpperMargin(graph: str, chirpSetup: dict, parseDataList: list) -> float | None:
    actualGraph = 0
    upperMarginList = []
    for pdIdx in range(len(parseDataList)):

        validChirpList = dp.getValidChirp(chirpSetup, parseDataList,pdIdx)
        nofRxCh = dp.getMaxNofRxCh(graph, parseDataList)
        for chirp in range(len(validChirpList)):
            for rxCh in range(nofRxCh):
                actualGraph = getActualGraphData(graph,rxCh,chirp,parseDataList,pdIdx)
                maxValue = actualGraph.max()
                upperMarginList.append(maxValue)

    if len(upperMarginList) !=0:
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

# Scaling factor for the diffPhaseDiff and avgDifPhaseDiff diagrams
def scale(graph: str, chirpSetup: dict, plotSetup: dict, parseDataList: list) -> float:
    absMaxList = []
    maxValue = 0
    minValue = 0
    upperXMarginIdx = 0
    lowerXMarginIdx = 0
    # if graph=='diffPhaseDiff' or graph=='avgDiffPhaseDiff':
    for pdIdx in range(len(parseDataList)):
        # Get the PTU angle for the specific PTU2 file
        angle = getAngle(parseDataList, pdIdx)
        # Get the target angle for the specific PTU2 file
        tarAngle = getTargetAngle(plotSetup, parseDataList, pdIdx)
        # Set the angle according to the configuration
        if plotSetup['targetAngle'] == 1:
            angle=tarAngle
        validChirpList = dp.getValidChirp(chirpSetup, parseDataList,pdIdx)
        nofRxCh = dp.getMaxNofRxCh(graph, parseDataList)
        for chirp in range(len(validChirpList)):
            for rxCh in range(nofRxCh):
                actualGraphData = getActualGraphData(graph, rxCh, chirp, parseDataList, pdIdx)
                arrayLen = len(angle)
                for i in range(arrayLen):
                    if angle[i] <= 10 + 0.1 and angle[i] >= 10 - 0.1:
                        if plotSetup['targetAngle'] == 1:
                            if getUpsideDown(plotSetup) == False:
                                lowerXMarginIdx = i
                            else:
                                upperXMarginIdx = i
                        else:
                            if getUpsideDown(plotSetup) == False:
                                upperXMarginIdx = i
                            else:
                                lowerXMarginIdx = i
                    if angle[i] <= -10 + 0.1 and angle[i] >= -10 - 0.1:
                        if plotSetup['targetAngle'] == 1:
                            if getUpsideDown(plotSetup) == False:
                                upperXMarginIdx = i
                            else:
                                lowerXMarginIdx = i
                        else:
                            if getUpsideDown(plotSetup) == False:
                                lowerXMarginIdx = i
                            else:
                                upperXMarginIdx = i
                maxValue = actualGraphData[lowerXMarginIdx:upperXMarginIdx].max()
                minValue = actualGraphData[lowerXMarginIdx:upperXMarginIdx].min()
                if abs(maxValue) >= abs(minValue):
                    absMax = abs(maxValue)
                else:
                    absMax = abs(minValue)
                absMaxList.append(absMax)
    return max(absMaxList)

# Scaling factor for the diffPhaseDiff and avgDifPhaseDiff diagrams
def scalePerDiagram(graph: str, diagramNr: int, chirpSetup: dict, plotSetup: dict, parseDataList: list) -> float | None:
    absMaxList = []
    maxValue = 0
    minValue = 0
    upperXMarginIdx = 0
    lowerXMarginIdx = 0
    # if graph=='diffPhaseDiff' or graph=='avgDiffPhaseDiff':
    for pdIdx in range(len(parseDataList)):

        # for diagramIdx in range(len(desiredDiagramList)):
        if parseDataList[pdIdx].fileTitle.diagram == diagramNr:
            # Get the PTU angle for the specific PTU2 file
            angle = getAngle(parseDataList, pdIdx)
            # Get the target angle for the specific PTU2 file
            tarAngle = getTargetAngle(plotSetup, parseDataList, pdIdx)
            # Set the angle according to the configuration
            if plotSetup['targetAngle'] == 1:
                angle = tarAngle
            validChirpList = dp.getValidChirp(chirpSetup, parseDataList, pdIdx)
            nofRxCh = dp.getMaxNofRxCh(graph, parseDataList)
            for chirp in range(len(validChirpList)):
                for rxCh in range(nofRxCh):

                    actualGraphData = getActualGraphData(graph, rxCh, chirp, parseDataList, pdIdx)
                    arrayLen = len(angle)

                    for i in range(arrayLen):
                        if plotSetup['targetAngle'] == 1:
                            if getUpsideDown(plotSetup) == False:
                                if angle[i] <= 10 + 0.1:
                                    lowerXMarginIdx=i
                                    break
                            else:
                                if angle[i] >= -10 - 0.1:
                                    lowerXMarginIdx = i
                                    break
                        else:
                            if angle[i] >= -10 - 0.1:
                                lowerXMarginIdx = i
                                break

                    for i in range(arrayLen):
                        if plotSetup['targetAngle'] == 1:
                            if getUpsideDown(plotSetup) == False:
                                if angle[i] < -10 - 0.1:
                                    upperXMarginIdx = i
                                    break
                                elif i == (len(angle)-1):
                                    upperXMarginIdx=i
                            else:
                                if angle[i] > 10 + 0.1:
                                    upperXMarginIdx =i
                                    break
                                elif i == (len(angle) - 1):
                                    upperXMarginIdx = i
                        else:
                            if angle[i] > 10 + 0.1:
                                upperXMarginIdx =i
                                break
                            elif i == (len(angle) - 1):
                                upperXMarginIdx = i

                    maxValue = actualGraphData[lowerXMarginIdx:upperXMarginIdx].max()
                    minValue = actualGraphData[lowerXMarginIdx:upperXMarginIdx].min()
                    if abs(maxValue) >= abs(minValue):
                        absMax = abs(maxValue)
                    else:
                        absMax = abs(minValue)
                    absMaxList.append(absMax)
    if len(absMaxList) !=0:
        maximum=max(absMaxList)
        return maximum
