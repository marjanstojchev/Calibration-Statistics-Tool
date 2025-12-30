import logconfig
import numpy as np
import os
import auxiliary as aux
import txantdiag_plotdata as plt

myLogger = logconfig.txAntDiagLogger.logger



# Get the list of all configred graphs to be drawn.
def getGraphList(graphConfig):
    graphList = []
    for graph, set in graphConfig.items():
        if set == 1:
            graphList.append(graph)
    return graphList

# Date time and sensor combination list
def getDateTimeSensorCombList(parseDataList):
    outputDictList = []
    sensor = ''
    dateAndTime = ''
    for listIdx in range(len(parseDataList)):
        outputDict = dict()

        if parseDataList[listIdx].fileTitle.sensorFound != 0 and parseDataList[listIdx].fileTitle.dateAndTimeFound != 0:
            if parseDataList[listIdx].fileTitle.sensor != sensor or parseDataList[listIdx].fileTitle.dateAndTime != dateAndTime:
                dateAndTime = parseDataList[listIdx].fileTitle.dateAndTime
                sensor = parseDataList[listIdx].fileTitle.sensor
                outputDict.update({"dateAndTime":dateAndTime,"sensor":sensor})
                outputDictList.append(outputDict)
    return outputDictList

def getTxAntList(parseDataList):
    txAntList = []

    for pdIdx in range(len(parseDataList)):
        if parseDataList[pdIdx].fileTitle.txAntFound == 1:
            txAnt = parseDataList[pdIdx].fileTitle.txAnt
            txAntList.append(txAnt)

    txAntSet  = set(txAntList)

    txAntList = list(txAntSet)

    return txAntList


# Mapping string for the antenna diagram types
def getAntDiagType(inputString):
    if inputString == 'Az':
        antennaDiagType = 'Azimuth'
    else:
        antennaDiagType = 'Elevation'
    return antennaDiagType

def fillGraphSlides(presentation, slideLayout, graphTxAntList, centFreqDictList, diagType, normAxisAvgAngleList, plotSetup):

    shapeCols=slideLayout.getNofGraphs()

    for graphTxAntIdx in range(len(graphTxAntList)):

        graphTxAntDict = graphTxAntList[graphTxAntIdx]

        txAntPerGraphList = graphTxAntDict['orig']
        txAntPerNormGraphList = graphTxAntDict['norm']

        if len(txAntPerGraphList) != 0 or len(txAntPerNormGraphList) != 0:

            nofTxAnt = len(txAntPerNormGraphList)
            if len(txAntPerGraphList) != 0:
                nofTxAnt = len(txAntPerGraphList)

            if plotSetup['plotOrigGraphs'] == 1:
                normGraphs = 0

                txAntGraphData = txAntPerGraphList

                res = nofTxAnt % shapeCols

                if nofTxAnt < shapeCols:
                    nofShapeElements = shapeCols
                    fillNum = shapeCols - nofTxAnt
                    for i in range(fillNum):
                        txAntGraphData.append('')
                elif res == 0:
                    nofShapeElements = nofTxAnt
                else:
                    fillNum = shapeCols -res
                    nofShapeElements = nofTxAnt + fillNum
                    for i in range(fillNum):
                        txAntGraphData.append('')

                shapeRows = int(nofShapeElements / shapeCols)

                txAntGraphData = np.reshape(txAntGraphData, (shapeRows, shapeCols))

                for txAntGraphDataRow in range(shapeRows):
                    # Adding a slide with one graph layout
                    presentation.add_slide(slideLayout)

                    textTxAntString = ''

                    imageList = []
                    captionsList = []
                    freqString = ''

                    # Filling the caption and image lists
                    for txAntGraphDataCol in range(shapeCols):
                        if txAntGraphData[txAntGraphDataRow][txAntGraphDataCol] != '':
                            img = slideLayout.imageList[txAntGraphDataCol]
                            cap = slideLayout.captionsList[txAntGraphDataCol]
                            imageList.append(img)
                            captionsList.append(cap)


                    newLineStr = '\n'

                    for txAntGraphDataCol in range(shapeCols):

                        graphData = txAntGraphData[txAntGraphDataRow][txAntGraphDataCol]

                        if graphData != '':

                            if diagType == 'Az':
                                normAxis = 'El'
                            else:
                                normAxis = 'Az'

                            textTxAntString += newLineStr + ' - TxAnt' + str(graphData.txAnt) + ': Freq. = ' + str(centFreqDictList[txAntGraphDataCol]["avgFreqGHz"]) + ' GHz (+ ' + str(centFreqDictList[txAntGraphDataCol]["posFreqDevMHz"]) + ' MHz - ' + str(centFreqDictList[txAntGraphDataCol]["negFreqDevMHz"]) + ' MHz), '
                            textTxAntString += normAxis+'= '+normAxisAvgAngleList[txAntGraphDataCol][diagType]+'°'
                            imgPath = os.path.join(aux.txAntDiagOutputPath, graphData.figureTitle)
                            imageList[txAntGraphDataCol].insert_picture(imgPath)

                            captionsList[txAntGraphDataCol].text_frame.text = 'TxAnt' + str(graphData.txAnt)

                    # Inserting slide title.
                    slideLayout.title.text = plt.graphStringMapping(txAntGraphData[txAntGraphDataRow][0].graphTitle,normGraphs) + ' - Tx Antenna Diagrams - Type ' \
                                             + ' - ' + getAntDiagType(diagType)

                    # Inserting the description text
                    slideLayout.text.text_frame.text = plt.graphStringMapping(txAntGraphData[txAntGraphDataRow][0].graphTitle,normGraphs) + ' - Tx Antenna Diagrams - ' + \
                                                    getAntDiagType(diagType) + textTxAntString  \
                                                    + newLineStr +' - All sensors.'

            # Insert normalised Graph Slides
            if plotSetup['plotNormGraphs'] == 1:
                normGraphs = 1

                txAntGraphData = txAntPerNormGraphList

                insertSlides = 1
                for i in range(len(txAntGraphData)):
                    if txAntGraphData[i].graphTitle == 'frequency' or txAntGraphData[i].graphTitle =='time':
                        insertSlides = 0

                if insertSlides == 1:

                    res = nofTxAnt % shapeCols

                    if nofTxAnt < shapeCols:
                        nofShapeElements = shapeCols
                        fillNum = shapeCols - nofTxAnt
                        for i in range(fillNum):
                            txAntGraphData.append('')
                    elif res == 0:
                        nofShapeElements = nofTxAnt
                    else:
                        fillNum = shapeCols - res
                        nofShapeElements = nofTxAnt + fillNum
                        for i in range(fillNum):
                            txAntGraphData.append('')

                    shapeRows = int(nofShapeElements / shapeCols)

                    txAntGraphData = np.reshape(txAntGraphData, (shapeRows, shapeCols))

                    for txAntGraphDataRow in range(shapeRows):

                        # Adding a slide with one graph layout
                        presentation.add_slide(slideLayout)

                        textTxAntString = ''

                        imageList = []
                        captionsList = []
                        freqString = ''

                        # Filling the caption and image lists
                        for txAntGraphDataCol in range(shapeCols):
                            if txAntGraphData[txAntGraphDataRow][txAntGraphDataCol] != '':
                                img = slideLayout.imageList[txAntGraphDataCol]
                                cap = slideLayout.captionsList[txAntGraphDataCol]
                                imageList.append(img)
                                captionsList.append(cap)

                        newLineStr = '\n'



                        for txAntGraphDataCol in range(shapeCols):

                            graphData = txAntGraphData[txAntGraphDataRow][txAntGraphDataCol]



                            if graphData != '':

                                if diagType == 'Az':
                                    normAxis = 'El'
                                else:
                                    normAxis = 'Az'

                                textTxAntString += newLineStr + ' - TxAnt' + str(graphData.txAnt) + ': Freq. = ' + str(
                                    centFreqDictList[txAntGraphDataCol]["avgFreqGHz"]) + ' GHz (+ ' + str(
                                    centFreqDictList[txAntGraphDataCol]["posFreqDevMHz"]) + ' MHz - ' + str(
                                    centFreqDictList[txAntGraphDataCol]["negFreqDevMHz"]) + ' MHz), '
                                textTxAntString += normAxis + '= ' + normAxisAvgAngleList[txAntGraphDataCol][diagType] + '°'
                                imgPath = os.path.join(aux.txAntDiagOutputPath, graphData.figureTitle)
                                imageList[txAntGraphDataCol].insert_picture(imgPath)

                                captionsList[txAntGraphDataCol].text_frame.text = 'TxAnt' + str(graphData.txAnt)

                        # Inserting slide title.
                        slideLayout.title.text = plt.graphStringMapping(txAntGraphData[txAntGraphDataRow][0].graphTitle,normGraphs) + ' - Tx Antenna Diagrams - Type ' \
                                                 + ' - ' + getAntDiagType(diagType)

                        # Inserting the description text
                        slideLayout.text.text_frame.text = plt.graphStringMapping(txAntGraphData[txAntGraphDataRow][0].graphTitle,normGraphs) + ' - Tx Antenna Diagrams - ' + \
                                                           getAntDiagType(diagType) + textTxAntString \
                                                           + newLineStr + ' - All sensors.'


def getFreqListPerTxAnt(txAnt, parseDataList):
    freqList = []

    for pdIdx in range(len(parseDataList)):
        if parseDataList[pdIdx].fileTitle.txAntFound==1:
            if txAnt == parseDataList[pdIdx].fileTitle.txAnt:
                freq = parseDataList[pdIdx].ptuMaxSpecHeaderData.frequenz_MHz
                freqList.append(freq)
    return freqList


def getAvgFreqPerTxAnt(txAnt, parseDataList):
    freqList = getFreqListPerTxAnt(txAnt, parseDataList)

    avgFreq = 0
    if len(freqList) != 0:
        avgFreq = sum(freqList)/len(freqList)
    else:
        myLogger.error("Empty frequency list.")
    return avgFreq


def getMaxFreqPerTxAnt(txAnt, parseDataList):
    freqList = getFreqListPerTxAnt(txAnt,parseDataList)
    maxFreq  = 0
    if len(freqList) != 0:
        maxFreq = max(freqList)
    else:
        myLogger.error("Empty frequency list.")
    return maxFreq

def getMinFreqPerTxAnt(txAnt, parseDataList):
    freqList = getFreqListPerTxAnt(txAnt, parseDataList)
    minFreq  = 0
    if len(freqList) != 0:
        minFreq = min(freqList)
    else:
        myLogger.error("Empty frequency list.")
    return minFreq

# Freq functions, all parsed tx ant diagrams
def getFreqListAll(parseDataList):
    freqList = []

    for pdIdx in range(len(parseDataList)):
        freq = parseDataList[pdIdx].ptuMaxSpecHeaderData.frequenz_MHz
        freqList.append(freq)
    return freqList


def getAvgFreqAll(parseDataList):
    freqList = getFreqListAll(parseDataList)

    avgFreq  = 0
    if len(freqList) != 0:
        avgFreq = sum(freqList)/len(freqList)
    else:
        myLogger.error("Empty frequency list.")
    return avgFreq


def getMaxFreqAll(parseDataList):
    freqList = getFreqListAll(parseDataList)

    maxFreq = 0
    if len(freqList) != 0:
        maxFreq = max(freqList)
    else:
        myLogger.error("Empty frequency list.")
    return maxFreq

def getMinFreqAll(parseDataList):
    freqList = getFreqListAll(parseDataList)
    minFreq  = 0
    if len(freqList) != 0:
        minFreq = min(freqList)
    else:
        myLogger.error("Empty frequency list.")
    return minFreq

# Normal axis average angle per tx antenna
def getNormAxisAvgAngPerTxAnt(txAnt, parseDataList, diagType):
    normAxisAngList = []
    for pdIdx in range(len(parseDataList)):
        if parseDataList[pdIdx].fileTitle.txAntFound == 1:
            if txAnt == parseDataList[pdIdx].fileTitle.txAnt:

                if diagType == 'Az':
                    normAxisAng = parseDataList[pdIdx].ptuMaxSpecHeaderData.d_PTU_ElAngle
                else:
                    normAxisAng = parseDataList[pdIdx].ptuMaxSpecHeaderData.d_PTU_AzAngle

                normAxisAngList.append(normAxisAng)

    avgAng = 0
    if len(normAxisAngList) != 0:
        avgAng = sum(normAxisAngList) / len(normAxisAngList)
    else:
        myLogger.error("Empty frequency list.")

    return avgAng

