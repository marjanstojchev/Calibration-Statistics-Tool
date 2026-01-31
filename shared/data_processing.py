import calcdiagram_functions as calc
import logconfig as log
from shared import safeparse as sp

myLogger = log.antSysDiagLogger.logger

class ImportedProtcolsData():
    def _init_(self):
        self.protocolDataList=[]

class ProtocolData():
    def _init_(self):
        self.protocolPath=''
        self.ptu2DataList=[]
        self.txAntDiagDataList=[]

class PTU2Data():
    def _init_(self):
        self.filesList=[]
        self.protocolPath=''


class TxAntDiagData():
    def _init_(self):
        self.filesList=[]
        self.protocolPath=''


class ProtocolsTableData():
    def __init__(self,protocolPath,sysDiagFilePathList,txAntDiagFilePathList):
        self.protocolPath=protocolPath
        self.sysDiagFilePathShapedList=[]
        self.txAntDiagFilePathShapedList=[]
        self.biggerListLength=0
        self.smallerListLength=0
        self.smallerListColIdx=0
        self.smallerListRowSpanList=[]


        if len(sysDiagFilePathList) >= len(txAntDiagFilePathList):
            if len(txAntDiagFilePathList)!=0:
                ratio = int(len(sysDiagFilePathList) / len(txAntDiagFilePathList))
                res=len(sysDiagFilePathList) % len(txAntDiagFilePathList)

                self.smallerListColIdx=3
                self.biggerListLength=len(sysDiagFilePathList)
                self.smallerListLength=len(txAntDiagFilePathList)

                self.sysDiagFilePathShapedList=sysDiagFilePathList

                for sysDiagIdx in range(len(sysDiagFilePathList)):


                    entry=''

                    for txAntDiagIdx in range(len(txAntDiagFilePathList)):

                        if ratio * txAntDiagIdx ==sysDiagIdx:
                            entry=txAntDiagFilePathList[txAntDiagIdx]

                    self.txAntDiagFilePathShapedList.append(entry)

                size=0

                for txAntDiagIdx in range(len(txAntDiagFilePathList)):

                    tempDict = {
                        'spanStart': 0,
                        'spanCount': 0
                    }

                    tempDict['spanStart']= txAntDiagIdx * ratio



                    if txAntDiagIdx ==len(txAntDiagFilePathList)-1:
                        if res != 0:
                            tempDict['spanCount']=self.biggerListLength - size
                        else:
                            tempDict['spanCount']=ratio

                    else:
                        tempDict['spanCount']=ratio
                        size=ratio* (txAntDiagIdx +1)

                    self.smallerListRowSpanList.append(tempDict)

            else:

                self.smallerListColIdx = 3
                self.biggerListLength = len(sysDiagFilePathList)

                self.sysDiagFilePathShapedList = sysDiagFilePathList

                for sysDiagIdx in range(len(sysDiagFilePathList)):

                    entry = ''

                    self.txAntDiagFilePathShapedList.append(entry)


                tempDict = {
                    'spanStart': 0,
                    'spanCount': self.biggerListLength
                }

                self.smallerListRowSpanList.append(tempDict)
        else:
            if len(sysDiagFilePathList)!=0:

                ratio = int(len(txAntDiagFilePathList) / len(sysDiagFilePathList))
                res=len(txAntDiagFilePathList) % len(sysDiagFilePathList)

                self.smallerListColIdx=2
                self.biggerListLength=len(txAntDiagFilePathList)
                self.smallerListLength = len(sysDiagFilePathList)

                self.txAntDiagFilePathShapedList=txAntDiagFilePathList

                for txAntDiagIdx in range(len(txAntDiagFilePathList)):

                    entry=''

                    for sysDiagIdx in range(len(sysDiagFilePathList)):

                        if ratio * sysDiagIdx ==txAntDiagIdx:
                            entry = sysDiagFilePathList[sysDiagIdx]

                    self.sysDiagFilePathShapedList.append(entry)

                size=0
                for sysDiagIdx in range(len(sysDiagFilePathList)):
                    tempDict={
                        'spanStart':0,
                        'spanCount':0
                    }

                    tempDict['spanStart']=sysDiagIdx * ratio

                    if sysDiagIdx ==len(sysDiagFilePathList)-1:
                        if res != 0:
                            tempDict['spanCount'] =self.biggerListLength - size
                        else:
                            tempDict['spanCount'] = ratio
                    else:
                        tempDict['spanCount']=ratio
                        size = ratio * (sysDiagIdx +1)

                    self.smallerListRowSpanList.append(tempDict)
            else:

                self.smallerListColIdx = 2
                self.biggerListLength = len(txAntDiagFilePathList)

                self.txAntDiagFilePathShapedList = txAntDiagFilePathList

                for txAntDiagIdx in range(len(txAntDiagFilePathList)):

                    entry = ''

                    self.sysDiagFilePathShapedList.append(entry)


                tempDict = {
                    'spanStart': 0,
                    'spanCount': self.biggerListLength
                }

                self.smallerListRowSpanList.append(tempDict)


def parsePlotWindowString(plotWindowStr):
    plotWindowConfig = {

        "graph": "",
        "antType": 0,
        "diagramNum": 0,
        "rxCh": 0
    }

    graphConfig = [ "level","avgLevel","normLevel","avgNormLevel","phaseDiff","avgPhaseDiff","diffPhaseDiff","avgDiffPhaseDiff","corrPhaseDiff"]


    graphFound =0
    antTypeFound=0
    diagramNumFound = 0
    rxChFound = 0

    plotWindowStr = plotWindowStr.replace('.','_')
    nameParts = plotWindowStr.split('_')

    for part in nameParts:
        if graphFound == 0:
               if part in graphConfig:
                   plotWindowConfig["graph"]=part
                   graphFound = 1
        if antTypeFound == 0:
            if part.startswith('AntType'):
                part = part.strip('AntType')
                if (sp.checkInt(part)):
                    plotWindowConfig["antType"] = int(part)
                    antTypeFound = 1
        if diagramNumFound == 0:
            if part.startswith('Diagram'):
                part = part.strip('Diagram')
                if (sp.checkInt(part)):
                    plotWindowConfig["diagramNum"] = int(part)
                    diagramNumFound = 1
        if rxChFound == 0:
            if part.startswith('RxCh'):
                part = part.strip('RxCh')
                if (sp.checkInt(part)):
                    plotWindowConfig["rxCh"] = int(part)
                    rxChFound = 1

    return plotWindowConfig

def rxChStringMapping(graphTitle, rxCh):
    rxChString=''
    # Mapping string for the phase difference channels
    # phDiffRxComb = ['RxAnt1-RxAnt0', 'RxAnt2-RxAnt1', 'RxAnt3-RxAnt2']
    if 'haseDiff'  in graphTitle:
        lower=str(rxCh)
        upper=str(rxCh+1)
        rxChString='RxAnt'+upper+'-'+'RxAnt'+lower
    else:
        rxChString='RxAnt'+ str(rxCh)
    return rxChString

def graphTypeStringMapping(graphTitle):
    graphTypeString = ''
    if 'haseDiff' in graphTitle:
        graphTypeString = "all sensors, RxAnt comb.:"
    else:
        graphTypeString = "all sensors, RxAnt:"
    return graphTypeString

# Mapping string for the antenna diagram types
def getAntDiagType(inputString):
    if inputString == 'Az':
        antennaDiagType = 'Azimuth'
    else:
        antennaDiagType = 'Elevation'
    return antennaDiagType

# Get the num. of diagrams from the parsed data
def getNofDiagrams(antType,parseDataList):
    diagramIdxList=[]
    for pdIdx in range(len(parseDataList)):
        if parseDataList[pdIdx].antennaInfo.antennaType==antType:
            diagram=parseDataList[pdIdx].fileTitle.diagram
            diagramIdxList.append(diagram)
    if len(diagramIdxList)!=0:
        nofDiagrams=max(diagramIdxList)+1
    else:
        nofDiagrams=0
    return nofDiagrams

def getDiagramList(antType,parseDataList):
    diagramIdxList=[]
    for pdIdx in range(len(parseDataList)):
        if parseDataList[pdIdx].antennaInfo.antennaType==antType:
            diagram=parseDataList[pdIdx].fileTitle.diagram
            diagramIdxList.append(diagram)

    # Preserve original order while removing duplicates
    outputList=[]
    for diagram in diagramIdxList:
        if diagram not in outputList:
            outputList.append(diagram)

    return outputList

def getDateAndTimeList(parseDataList):
    dateAndTime = ''
    dateAndTimeList = []
    for listIdx in range(len(parseDataList)):
        if parseDataList[listIdx].fileTitle.dateAndTimeFound != 0:
            if parseDataList[listIdx].fileTitle.sensor!= dateAndTime:
                dateAndTime = parseDataList[listIdx].fileTitle.dateAndTime
                dateAndTimeList.append(parseDataList[listIdx].fileTitle.dateAndTime)
    return dateAndTimeList

# Get the list of all sensors from the parsed data
def getSensorList(parseDataList):
    sensor = ''
    sensorList = []
    for listIdx in range(len(parseDataList)):
        if parseDataList[listIdx].fileTitle.sensorFound != 0:
            if parseDataList[listIdx].fileTitle.sensor!= sensor:
                sensor = parseDataList[listIdx].fileTitle.sensor
                sensorList.append(parseDataList[listIdx].fileTitle.sensor)
    return sensorList

def getDateTimeSensorCombList(antennaType,parseDataList):
    outputDictList=[]
    sensor=''
    dateAndTime=''
    for listIdx in range(len(parseDataList)):
        outputDict = dict()

        if parseDataList[listIdx].fileTitle.sensorFound != 0 and parseDataList[listIdx].fileTitle.dateAndTimeFound !=0:
            if parseDataList[listIdx].fileTitle.sensor != sensor or parseDataList[listIdx].fileTitle.dateAndTime != dateAndTime:
                dateAndTime= parseDataList[listIdx].fileTitle.dateAndTime
                sensor= parseDataList[listIdx].fileTitle.sensor
                outputDict.update({"dateAndTime":dateAndTime,"sensor":sensor})
                outputDictList.append(outputDict)
    return outputDictList

def getDateTimeSensorCombTable(dateTimeList,sensorList,dateAndTimeCombList):

    outputList=[]
    for k in range(len(dateAndTimeCombList)):
        for i in range(len(dateTimeList)):
            if dateAndTimeCombList[k]["dateAndTime"] == dateTimeList[i]:
                subList = []
                for j in range(len(sensorList)):
                    if dateAndTimeCombList[k]["sensor"]==sensorList[j]:
                        subList.append(sensorList[j])
            outputList.append(subList)

    return outputList

#



#Get number of RxAnt per sensor
def getNofRxAntPerSensor(sensor, parseDataList):
    actualNofRxAnt=0
    for pdIdx in range(len(parseDataList)):
        if parseDataList[pdIdx].antennaInfo.fileTitle.sensorFound==1:
            if sensor == parseDataList[pdIdx].fileTitle.sensor:
                actualNofRxAnt = parseDataList[pdIdx].antennaInfo.nofAntennas
                break
    return actualNofRxAnt

# Get the maximal number of Tx antenas of all sensors
def getMaxNofTxAnt(sensorList,parseDataList):
    maxNofTxAnt=0
    maxNofTxAntList=[]
    for sensorIdx in range(len(sensorList)):
        maxNofTxAnt=getNofTxAntPerSensor(sensorList[sensorIdx],parseDataList)
        maxNofTxAntList.append(maxNofTxAnt)
    return max(maxNofTxAntList)

# Get number of TxAnt per sensor
def getNofTxAntPerSensor(sensor, parseDataList):
    actualTxAnt=0
    txAntList=[]

    for pdIdx in range(len(parseDataList)):
        if parseDataList[pdIdx].antennaInfo.fileTitle.sensorFound==1:
            if sensor == parseDataList[pdIdx].fileTitle.sensor:
                if parseDataList[pdIdx].antennaInfo.fileTitle.txAntFound == 1:
                    actualTxAnt = parseDataList[pdIdx].fileTitle.txAnt
                    txAntList.append(actualTxAnt)
    return max(txAntList)

# Get TxAnt list
def getTxAntList(parseDataList):
    actualTxAnt=0
    txAntList=[]
    for pdIdx in range(len(parseDataList)):
        if parseDataList[pdIdx].antennaInfo.fileTitle.txAntFound == 1:
            actualTxAnt = parseDataList[pdIdx].fileTitle.txAnt
            txAntList.append(actualTxAnt)

    # Preserve original order while removing duplicates
    outputList=[]
    for txAnt in txAntList:
        if txAnt not in outputList:
            outputList.append(txAnt)

    return outputList



def getAngleStep(parseData,isTargetAngle,upsideDown):
    if isTargetAngle ==1:
        angle=calc.getTarAngVals(parseData,upsideDown)
    else:
        angle=calc.getPtuAngVals(parseData)
    firstPoint=round(angle[0],1)
    lastPoint=round(angle[1],1)
    step=abs(firstPoint-lastPoint)
    return step

def getNofAnglePoints(parseData,isTargetAngle,upsideDown):
    if isTargetAngle == 1:
        length=len(calc.getTarAngVals(parseData, upsideDown))
    else:
        length=len(calc.getPtuAngVals(parseData))
    return length

def getRefAnglePoint(parseData,isTargetAngle,upsideDown):
    if isTargetAngle ==1:
        angle=calc.getTarAngVals(parseData,upsideDown)
    else:
        angle=calc.getPtuAngVals(parseData)
    refAnglePoint=round(angle[0],1)
    return refAnglePoint


# Get the desired diagrams list, according to the diagram configuration.
def getDesiredDiagramsList(diagramConfig, diagramConfigList,antType, parseDataList):
    print(f"[DEBUG] getDesiredDiagramsList called with:")
    print(f"  - antType: {antType}")
    print(f"  - parseDataList length: {len(parseDataList)}")
    print(f"  - diagramConfig: {diagramConfig}")
    print(f"  - diagramConfigList: {diagramConfigList}")
    
    desiredDiagramList=[]
    diagramTempList=getDiagramList(antType,parseDataList)
    print(f"  - diagramTempList from getDiagramList: {diagramTempList}")
    
    # nofDiagrams = getNofDiagrams(antType,parseDataList)
    high = diagramConfig["higherNumber"]
    low = diagramConfig["lowerNumber"]

    if diagramConfig['selectDiagrams']==0:
        if diagramConfig['oddOrEven']==0:
            desiredDiagramList=diagramTempList
            # for diagramIdx in range(nofDiagrams):
            #     desiredDiagramList.append(diagramIdx)
        elif diagramConfig['oddOrEven'] == 1:
            for i in range(len(diagramTempList)):
                if diagramTempList[i] % 2 !=0:
                    desiredDiagramList.append(diagramTempList[i])

            # for i in range(1, nofDiagrams, 2):
            #     desiredDiagramList.append(i)
        else:
            for i in range(len(diagramTempList)):
                if diagramTempList[i] % 2 == 0:
                    desiredDiagramList.append(diagramTempList[i])

            # for i in range(0, nofDiagrams, 2):
            #     desiredDiagramList.append(i)

    elif diagramConfig['selectDiagrams']==1:
        if diagramConfig['oddOrEven']==0:
            for diagIdx in range (len(diagramTempList)):
                if diagramTempList[diagIdx]>=low and diagramTempList[diagIdx]<=high:
                    desiredDiagramList.append(diagramTempList[diagIdx])
            # for diagramIdx in range(low,high+1,1):
            #     desiredDiagramList.append(diagramIdx)
        elif diagramConfig['oddOrEven'] == 1:
            for diagIdx in range (len(diagramTempList)):
                if diagramTempList[diagIdx]>=low and diagramTempList[diagIdx]<=high and diagramTempList[diagIdx]%2!=0:
                    desiredDiagramList.append(diagramTempList[diagIdx])
            # if (low % 2) == 0:
            #     low=low+1
            # else:
            #     low=low
            # for i in range(low, high+1, 2):
            #     desiredDiagramList.append(i)
        else:


            for diagIdx in range (len(diagramTempList)):
                if diagramTempList[diagIdx]>=low and diagramTempList[diagIdx]<=high and diagramTempList[diagIdx]%2==0:
                    desiredDiagramList.append(diagramTempList[diagIdx])
            # if (low % 2) == 0:
            #     low = low
            # else:
            #     low = low+1
            # for i in range(low, high+1, 2):
            #     desiredDiagramList.append(i)
    else:
        # Preserve original order while removing duplicates
        filteredDiagList = []
        for diagram in diagramConfigList:
            if diagram not in filteredDiagList:
                filteredDiagList.append(diagram)

            for diagTempIdx in range(len(diagramTempList)):
                for filtDiagIdx in range(len(filteredDiagList)):
                    if diagramTempList[diagTempIdx] == filteredDiagList[filtDiagIdx]:
                        desiredDiagramList.append(diagramTempList[diagTempIdx])

    print(f"  - Final desiredDiagramList: {desiredDiagramList}")
    return desiredDiagramList

# Returns a list of all parsed PTU2 files for a certain diagram.
def getDataPerDiagram(desiredDiagram,loadedData):
    outputList=[]
    for pdIdx in range(len(loadedData.parseDataList)):
        if desiredDiagram==loadedData.parseDataList[pdIdx].fileTitle.diagram:
            outputList.append(loadedData.parseDataList[pdIdx])
    return outputList


# Get the configured chirps
def getChirpList(chirpSetup):
    chirpList = []
    for diagram, set in chirpSetup.items():
        if set == 1:
            chirpList.append(diagram)
    return chirpList

# Get the valid chirp according to the configuration and the active chirps info from the PTU2 files.
def getValidChirp( chirpSetup, parseDataList, pdIdx):
    chirpList = getChirpList(chirpSetup)
    validChirpList = []
    for chirpIdx in range(len(chirpList)):
        if parseDataList[pdIdx].chirpInfoList[chirpIdx].active == 1:
            validChirpList.append(chirpList[chirpIdx])
    return validChirpList


# Get the actual number of Rx channels, per specific graph and a PTU2 file.
def getNofActualRxChannels(graphList, graphIdx, parseDataList, parseDataIdx):
    if graphList[graphIdx].endswith('evel'):
        actualNofRxCh = parseDataList[parseDataIdx].antennaInfo.nofAntennas
    else:
        actualNofRxCh = parseDataList[parseDataIdx].antennaInfo.nofAntennaDiffValues
    return actualNofRxCh

# Get the actual number of Rx channels, per specific graph and a PTU2 file.
def getNofActualRxChannels(graph, parseDataList, pdIdx):
    if graph.endswith('evel'):
        actualNofRxCh =parseDataList[pdIdx].antennaInfo.nofAntennas
    else:
        actualNofRxCh = parseDataList[pdIdx].antennaInfo.nofAntennaDiffValues
    return actualNofRxCh

# Get the maximal number of Rx channels for specific graph, of all PTU2 files.
def getMaxNofRxCh(graph,parseDataList):
    nofRxChList = []
    for pdIdx in range(len(parseDataList)):

        nofRxCh = getNofActualRxChannels(graph, parseDataList, pdIdx)
        nofRxChList.append(nofRxCh)
    return max(nofRxChList)

# Get the data for the actual graph for specific graph, chirp, rx channel, and PTU2 file
def getActualGraphData(graph, rxChannel, chirp, parseDataList, pdIdx):
    actualDiagramData = 0
    if graph == "level":
        actualDiagramData = calc.getAntLevel(rxChannel, chirp, parseDataList[pdIdx])

    elif graph == "avgLevel":  # Average power level of chirps [dB].
        actualDiagramData = calc.getAvgAntLevel(rxChannel, parseDataList[pdIdx])

    elif graph == "normLevel":  # Normalised power level [dB].
        actualDiagramData = calc.getNormAntLevel(rxChannel, chirp, parseDataList[pdIdx])

    elif graph == "avgNormLevel":  # Average of normalised power levels of all chirps [dB].
        actualDiagramData = calc.getAvgNormAntLevel(rxChannel, parseDataList[pdIdx])

    # Phase difference diagrams
    elif graph == "phaseDiff":  # Phase difference [°].
        actualDiagramData = calc.getPhaseDiff(rxChannel, chirp, parseDataList[pdIdx])

    elif graph == "avgPhaseDiff":  # Average of the phase differences of all chirps[°].
        actualDiagramData = calc.getAvgPhaseDiff(rxChannel, parseDataList[pdIdx])

    elif graph == "idealPhaseDiff":  # Ideal phase difference [°].
        actualDiagramData = calc.getIdealPhaseDiff(rxChannel, chirp, parseDataList[pdIdx])

    elif graph == "diffPhaseDiff":  # Difference between one phase difference and the ideal one [°].
        actualDiagramData = calc.getPhaseDiffDiff(rxChannel, chirp, parseDataList[pdIdx])

    elif graph == "avgDiffPhaseDiff":  # Average difference of between the phase differences and the ideal one of all chirps[°].
        actualDiagramData = calc.getAvgPhaseDiffDiff(rxChannel, parseDataList[pdIdx])

    elif graph == "corrPhaseDiff":
        actualDiagramData = calc.getPhaseDiffOffCorr(rxChannel, chirp, parseDataList[pdIdx])
    return actualDiagramData


# def scaleLowerMargin(graph, chirpSetup, parseDataList):
#     actualGraph = 0
#     lowerMarginList = []
#     for pdIdx in range(len(parseDataList)):
#         validChirpList = getValidChirp(chirpSetup, parseDataList[pdIdx])
#         nofRxCh = getMaxNofRxCh(graph, parseDataList)
#         for chirp in range(len(validChirpList)):
#             for rxCh in range(nofRxCh):
#                 actualGraph = getActualGraphData(graph, rxCh, chirp, parseDataList[pdIdx])
#                 minValue = actualGraph.min()
#                 lowerMarginList.append(minValue)
#
#     lowerMargin = min(lowerMarginList)
#     whole = int(abs(lowerMargin) / 10)
#     rest = abs(lowerMargin) % 10
#
#     if lowerMargin >= 0:
#         if rest > 5:
#             lowerMargin = whole * 10
#         else:
#             lowerMargin = whole * 10 - 10
#     else:
#         if rest < 5:
#             lowerMargin = whole * (-10) - 10
#         else:
#             lowerMargin = whole * (-10) - 20
#     return lowerMargin
#
#     # Upper margin of all drawn sensor diagrams for a specific graph
#
#
# def scaleUpperMargin(graph, chirpSetup, parseDataList):
#     actualGraph = 0
#     upperMarginList = []
#     for pdIdx in range(len(parseDataList)):
#         validChirpList = getValidChirp(chirpSetup, parseDataList[pdIdx])
#         nofRxCh = getMaxNofRxCh(graph, parseDataList)
#         for chirp in range(len(validChirpList)):
#             for rxCh in range(nofRxCh):
#                 actualGraph = getActualGraphData(graph, rxCh, chirp,parseDataList[pdIdx])
#                 maxValue = actualGraph.max()
#                 upperMarginList.append(maxValue)
#     upperMargin = max(upperMarginList)
#     whole = int(abs(upperMargin) / 10)
#     rest = abs(upperMargin) % 10
#
#     if upperMargin >= 0:
#         if rest > 5:
#             upperMargin = whole * 10 + 20
#         else:
#             upperMargin = whole * 10 + 10
#     else:
#         if rest < 5:
#             upperMargin = whole * (-10) + 10
#         else:
#             upperMargin = whole * (-10)
#     return upperMargin

def azDataFound(parseDataList):
    val=False
    for pdIdx in range(len(parseDataList)):
        if (parseDataList[pdIdx].measSetupInfo.antennaDiagramTypeFound == 1) and (parseDataList[pdIdx].measSetupInfo.antennaDiagramType == 'Az'):
            val=True
            break
    return val

def noDiagTypeDataFound(parseDataList):
    val=False
    for pdIdx in range(len(parseDataList)):
        if (parseDataList[pdIdx].measSetupInfo.antennaDiagramTypeFound == 0):
            val=True
            break
    return val

# Get the list of all antenna types from the parsed data
def getAntennaTypesList(parseDataList):
    antennaType = 0
    antennaTypeList = []

    for listIdx in range(len(parseDataList)):

        if parseDataList[listIdx].antennaInfo.antennaType!= antennaType:
            antennaType = parseDataList[listIdx].antennaInfo.antennaType
            antennaTypeList.append(parseDataList[listIdx].antennaInfo.antennaType)

    antTypeSet=set(antennaTypeList)
    outputList=list(antTypeSet)
    return outputList

def getPtu2ListPerAntennaType(antType,parseDataList):
    outputList=[]
    for listIdx in range(len(parseDataList)):
        if parseDataList[listIdx].antennaInfo.antennaType == antType:
            outputList.append(parseDataList[listIdx])
    return outputList

def getFreqListPerDiagram(chirpConfig,diagNum,parseDataList):
    freqList=[]
    for pdIdx in range(len(parseDataList)):
        if parseDataList[pdIdx].fileTitle.diagramFound==1:
            if parseDataList[pdIdx].fileTitle.diagram == diagNum:
                validChirpList = getValidChirp(chirpConfig, parseDataList, pdIdx)
                for chirp in range(len(validChirpList)):
                    freqList.append(parseDataList[pdIdx].chirpInfoList[chirp].centerFrequency)

    return  freqList

def getFreqList(chirpConfig, diagramList,parseDataList):
    freqList=[]
    for pdIdx in range(len(parseDataList)):
        for diagIdx in range(len(diagramList)):
            if parseDataList[pdIdx].fileTitle.diagramFound==1:
                validChirpList = getValidChirp(chirpConfig, parseDataList, pdIdx)
                for chirp in range(len(validChirpList)):
                    freqList.append(parseDataList[pdIdx].chirpInfoList[chirp].centerFrequency)

    return  freqList

def getAvgFreqPerDiagram (chirpConfig,diagNum,parseDataList):
    freqList=getFreqListPerDiagram(chirpConfig,diagNum,parseDataList)

    avgFreq = 0
    if len(freqList)!=0:
        avgFreq=sum(freqList)/len(freqList)
    else:
        myLogger.error("Empty frequency list.")
    return avgFreq


def getMaxFreqPerDiagram (chirpConfig,diagNum,parseDataList):
    freqList=getFreqListPerDiagram(chirpConfig,diagNum,parseDataList)
    maxFreq = 0
    if len(freqList)!=0:
        maxFreq=max(freqList)
    else:
        myLogger.error("Empty frequency list.")
    return maxFreq

def getMinFreqPerDiagram (chirpConfig,diagNum,parseDataList):
    freqList=getFreqListPerDiagram(chirpConfig,diagNum,parseDataList)

    minFreq = 0
    if len(freqList)!=0:
        minFreq=min(freqList)
    else:
        myLogger.error("Empty frequency list.")
    return minFreq

def getAvgFreq (chirpConfig,diagramList,parseDataList):
    freqList=getFreqList(chirpConfig,diagramList,parseDataList)

    avgFreq = 0
    if len(freqList)!=0:
        avgFreq=sum(freqList)/len(freqList)
    else:
        myLogger.error("Empty frequency list.")
    return avgFreq


def getMaxFreq(chirpConfig,diagramList,parseDataList):
    freqList=getFreqList(chirpConfig,diagramList,parseDataList)
    maxFreq = 0
    if len(freqList)!=0:
        maxFreq=max(freqList)
    else:
        myLogger.error("Empty frequency list.")
    return maxFreq

def getMinFreq (chirpConfig,diagramList,parseDataList):
    freqList=getFreqList(chirpConfig,diagramList,parseDataList)

    minFreq = 0
    if len(freqList)!=0:
        minFreq=min(freqList)
    else:
        myLogger.error("Empty frequency list.")
    return minFreq
