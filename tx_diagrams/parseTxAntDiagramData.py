import os
from enum import Enum
import io
import safeparse as sp
import logconfig as log

myLogger=log.mainLoadDataLogger.logger

## Parse data module ##

# PTU angle and chirp measurement data per angle
class PtuPosMeasData:
    def __init__(self):
        self.d_PTU_AzAngle = -10000 # [°]
        self.d_PTU_ElAngle = -10000 # [°]
        self.level_dBm = -10000 #[dBm]
        self.levelPowMet_dBm =-10000 #[dBm]
        self.frequenz_MHz = 0 #[MHz]
        self.time_ms = 0 #[ms]
        self.levelMeasSpec_dBm = -10000 #[dBm]
        self.levelMeasPowMet_dBm = -10000 #[dBm]


# Data from the parsed TxAnt diagram file, containing meaurements data for each ptu position
class TxAntDiagramParseData:

    def __init__(self):
        self.bDataValid = False
        self.fileNamePath = ''
        self.errorList = []
        self.ptuMaxSpecHeaderData = 0
        self.chirp = 0
        self.ptuPosDataList = [] # Messdaten an der jeweiligen ptu position
        self.fileTitle = FileTitle()
    # Call parse data from the PTU2ParseData object (parseData wrapper)
    def parseFile(self, fileNamePath, useSensorMuster, sensorMusterList):
        self.errorList = []
        self.fileNamePath = fileNamePath
        parseFile(fileNamePath, self)
        self.fileTitle.parseFileTitle(self.fileNamePath, useSensorMuster, sensorMusterList)


# Meta data class from the PTU2 file title
class FileTitle:
    def __init__(self):
        self.dateAndTime  = ''
        self.date    = ''
        self.time    = ''
        self.sensor  = ''
        self.tuner   = ''
        self.txAnt   = 0
        self.seqNum  = 0
        self.diagram = 0
        self.rf      = ''
        self.dsp     = ''
        self.fileNamePath = ''
        self.fileDirPath  = ''
        self.fileName = ''
        self.sensorMusterList = []
        self.useSensorMuster = 0
        self.sensorMusterValueDict = dict()

        self.dateAndTimeFound = 0
        self.tunerFound   = 0
        self.rfFound      = 0
        self.dspFound     = 0
        self.txAntFound   = 0
        self.seqNumFound  = 0
        self.diagramFound = 0
        self.sensorFound  = 0
        self.sensorMusterFoundDict=dict()

    # Parse the PTU2 file title
    def parseFileTitle(self, fileNamePath, useSensorMuster, sensorMusterList):

        self.fileNamePath     = fileNamePath
        self.useSensorMuster  = useSensorMuster
        self.sensorMusterList = sensorMusterList

        if useSensorMuster == 1:
            if len(sensorMusterList) != 0:
                for musterItem in sensorMusterList:
                    dictKey = str(musterItem)
                    self.sensorMusterFoundDict[dictKey] = 0

                    self.sensorMusterValueDict[dictKey] = ''
            else:
                myLogger.error('Empty sensor muster list!')

        pathParts = os.path.split(fileNamePath)

        fileName = pathParts[1]
        self.fileName = fileName

        fileDirPath = pathParts[0]
        self.fileDirPath = fileDirPath


        fileNameParts = os.path.splitext(fileName)
        fileNameParts = fileNameParts[0].split('_')

        for part in fileNameParts:
            if self.dateAndTimeFound == 0:
                if part.startswith('20') and part[4] == '-':
                    self.dateAndTime = part
                    self.dateAndTimeFound = 1
                    self.date = part[0:10]
                    self.time = part[11:19]
            if self.tunerFound == 0:
                if part.startswith('Tuner'):
                    self.tuner = part
                    self.tunerFound = 1
            if self.rfFound == 0:
                if part.startswith('rf'):
                    self.rf = part
                    self.rfFound = 1
            if self.dspFound == 0:
                if part.startswith('dsp'):
                    self.dsp = part
                    self.dspFound = 1
            if self.seqNumFound == 0:
                if 'Seq' in part:
                    # self.seqNumFound = 1
                    part = part.strip('Seq')
                    if 'TxAnt' not in part:
                        if (sp.checkInt(part)):
                            self.seqNum = int(part)
                    else:
                        a=part.replace('TxAnt','.')

                        if (sp.checkInt(a[0])):
                            self.seqNum = int(a[0])
                            self.seqNumFound = 1
                        else:
                            self.seqNumFound = 0
                        if (sp.checkInt(a[2])):
                            self.txAnt = int(a[2])
                            self.txAntFound = 1
                        else:
                            self.txAntFound = 0
            if self.txAntFound == 0:
                if part.startswith('TxAnt'):
                    part = part.strip('TxAnt')
                    if(sp.checkInt(part)):
                        self.txAnt = int(part)
                        self.txAntFound = 1
            if self.diagramFound == 0:
                if part.startswith('Diagram'):
                    part = part.strip('Diagram')
                    if (sp.checkInt(part)):
                        self.diagram = int(part)
                        self.diagramFound = 1

            if self.useSensorMuster == 1:
                if len(self.sensorMusterList) != 0:
                    for musterItem in self.sensorMusterList:
                        musterItem = str(musterItem)
                        if self.sensorMusterFoundDict[musterItem] == 0:
                            if part.startswith(musterItem):
                                self.sensorMusterValueDict[musterItem] = part
                                self.sensorMusterFoundDict[musterItem] = 1

        if self.sensorFound == 0:
            if self.useSensorMuster == 1:

                if len(self.sensorMusterList) != 0:
                    i = 0
                    self.sensorFound = 1
                    for key,val in self.sensorMusterFoundDict.items():
                        if self.sensorMusterFoundDict[key] == 1:
                            binder = '' if i == 0 else '_'
                            self.sensor += binder+ self.sensorMusterValueDict[key]
                            i += 1
                        else:
                            self.sensorFound = 0

            else:
                if self.rfFound == 1:
                    binder = '_' if self.dspFound == 1 else ''
                    self.sensor = self.rf + binder + self.dsp
                    self.sensorFound = 1

def setParDict(lineArray, nofMeasDataFields):

        parMappingDict = dict()
        dictEntry = {}

        for lineArrayElement in range(nofMeasDataFields):

            if 'PTU-AngleAz' in lineArray[lineArrayElement]:
                dictEntry = {lineArrayElement: 'ptuAngleAz'}

            elif 'PTU-AngleEl' in lineArray[lineArrayElement]:
                dictEntry = {lineArrayElement: 'ptuAngleEl'}

            elif 'Level[dBm]' == lineArray[lineArrayElement]:
                dictEntry = {lineArrayElement: 'level'}

            elif ('Powermeter' in lineArray[lineArrayElement]) and ('measured' not in lineArray[lineArrayElement]):
                dictEntry = {lineArrayElement: 'levelPowerMeter'}

            elif ('Spec' in lineArray[lineArrayElement]) and ('measured' in lineArray[lineArrayElement]):
                dictEntry = {lineArrayElement: 'levelSpecMeas'}

            elif ('Powermeter' in lineArray[lineArrayElement]) and ('measured' in lineArray[lineArrayElement]):
                dictEntry = {lineArrayElement: 'levelPowerMeterMeas'}

            elif 'Frequenz' in lineArray[lineArrayElement]:
                dictEntry = {lineArrayElement: 'frequency'}

            elif 'Time' in lineArray[lineArrayElement]:
                dictEntry = {lineArrayElement: 'time'}

            parMappingDict.update(dictEntry)

        return parMappingDict


# PTU2 file parts procesing info
class searchParts(Enum):
    MaxHeader     = 1
    MaxHeaderData = 2
    Header        = 3
    PtuPosData    = 4



# Control wrapper for interpretData
def parseFile(fileNamePath, txAntDiagParseData):
    myLogger.info("Parsing: " + fileNamePath)
    txAntDiagParseData.fileNamePath = fileNamePath
    interpretData(fileNamePath, txAntDiagParseData)
    if len(txAntDiagParseData.errorList) == 0:
        txAntDiagParseData.bDataValid = True
    else:
        txAntDiagParseData.bDataValid = False
    return txAntDiagParseData

# Read and interpret the data for every part of the PTU2 file
def interpretData(fileNamePath, txAntDiagParseData):
    strMeasName = txAntDiagParseData.fileNamePath

    headerLineIndicator0 = "% PTU-Angle"
    headerLineIndicator1 = "Time[ms]"

    headerFound = 0
    ptuPosDataFound = 0
    maxHeaderFound = 0

    nofMeasDataFields = 0
    nofActualMeasDataFields = 0

    parMappingDict = dict()

    endOfEmptyLines = 0
    emptyCharFound  = 0

    currentPart = searchParts.MaxHeader

    # Try to read the file
    try:
        f = io.open(fileNamePath)

    # Catch an exception
    except IOError as ioErr:

        # errorString="try reading: " +fileNamePath+ " Exception = " + str(ioErr)
        errorString = strMeasName + ' File does not exist! Insert a valid file path.'

        txAntDiagParseData.errorList.append(errorString)
    else:
        # Read the lines of the file and remove all white spaces
        with f:
            content = f.readlines()
        content = [line.strip() for line in content]

        # Traverse through every line of the content
        for line in content:
            # read file name from protocol
            if 'File' in line:
                rest = line.split(';')
                txAntDiagParseData.fileNamePath = rest[1]
            
            timeFound = 0

            # Header lookup
            lineArray = line.split(';')


            for idx in range(len(lineArray)):

                if headerLineIndicator1 in lineArray[idx]:
                    timeFound = 1

            if currentPart == searchParts.MaxHeader:
                if ((headerLineIndicator0 in lineArray[0]) and (timeFound != 1)):
                    maxHeaderFound += 1
                    lineArrayLength = len(lineArray)
                    if lineArray[lineArrayLength - 1] == '':

                        nofMeasDataFields = len(lineArray) - 1
                    else:

                        nofMeasDataFields = len(lineArray)

                    parMappingDict = setParDict(lineArray, nofMeasDataFields)

                    currentPart = searchParts.MaxHeaderData

            elif currentPart == searchParts.MaxHeaderData:
                if not ((len(lineArray) == 1) and (lineArray[0] == '')):
                    endOfEmptyLines = 1
                if endOfEmptyLines == 1:

                    lineArrayLength = len(lineArray)

                    if lineArray[lineArrayLength - 1] == '':

                        nofActualMeasDataFields = len(lineArray) - 1
                    else:
                        nofActualMeasDataFields = len(lineArray)

                    if nofActualMeasDataFields != nofMeasDataFields:
                        txAntDiagParseData.errorList.append(strMeasName + ' incomplete or invalid ptu MAXIMUM measurement data')
                        return
                    else:
                        if not readPosPtuData(lineArray, txAntDiagParseData, nofMeasDataFields, parMappingDict, currentPart):
                            return
                        else:
                            ptuPosDataFound += 1
                            currentPart = searchParts.Header

            if currentPart == searchParts.Header:
                if ((headerLineIndicator0 in lineArray[0]) and (timeFound==1)):
                    headerFound += 1
                    lineArrayLength=len(lineArray)
                    if lineArray[lineArrayLength -1] == '':

                        nofMeasDataFields = len(lineArray)-1
                    else:

                        nofMeasDataFields = len(lineArray)

                    parMappingDict = setParDict(lineArray,nofMeasDataFields)

                    currentPart = searchParts.PtuPosData

            # Header lookup

            # PTU position lookup
            elif currentPart == searchParts.PtuPosData:
                endOfEmptyLines = 0
                if not((len(lineArray) == 1) and (lineArray[0] == '')):
                    endOfEmptyLines = 1
                if endOfEmptyLines == 1:

                    lineArrayLength = len(lineArray)

                    if lineArray[lineArrayLength - 1] == '':

                        nofActualMeasDataFields = len(lineArray)-1
                    else:
                        nofActualMeasDataFields = len(lineArray)


                    if nofActualMeasDataFields != nofMeasDataFields :
                        txAntDiagParseData.errorList.append(strMeasName + ' incomplete or invalid ptu position measurement data')
                        return
                    else:
                        if not readPosPtuData(lineArray, txAntDiagParseData, nofMeasDataFields, parMappingDict, currentPart):
                            return
                        else:
                            ptuPosDataFound += 1

        if endOfEmptyLines == 0:
            txAntDiagParseData.errorList.append(strMeasName + ' could not find ptu position measurement data')
        # Setup error list
        if headerFound == 0:
            txAntDiagParseData.errorList.append(strMeasName + ' could not find measurement data header in file')
        if headerFound > 1:
            txAntDiagParseData.errorList.append(strMeasName + ' found header more than once in file, loaded meas. data probably incorrect')
        if maxHeaderFound == 0:
            txAntDiagParseData.errorList.append(strMeasName + ' could not find MAXIMUM(Spec) header in file')
        if maxHeaderFound > 1:
            txAntDiagParseData.errorList.append(strMeasName + '  MAXIMUM(Spec) found header more than once in file, loaded meas. data probably incorrect')


# Control wrapper for getMeasData
def readPosPtuData(lineArray, txAntDiagParseData, nofMeasDataFields, parMappingDict, currentPart):
    if not getMeasData(lineArray, txAntDiagParseData, nofMeasDataFields, parMappingDict, currentPart):
        if currentPart == searchParts.MaxHeaderData:
            txAntDiagParseData.errorList.append(str(txAntDiagParseData.fileNamePath) + ' Error - Reading MAXIMUM(SPEC) header measurement data')

        else:
            txAntDiagParseData.errorList.append(str(txAntDiagParseData.fileNamePath) + ' Error - Reading measurement data')
        return False
    return True

# Parses the measurements data part per one PTU position
def getMeasData(lineArray, txAntDiagParseData, nofMeasDataFields, parMappingDict, currentPart):
    bRet = True

    ptuPosMeasData = PtuPosMeasData()

    for key,par in parMappingDict.items():

        if par =='ptuAngleAz':
            temp = lineArray[key].replace(',', '.')

            if sp.checkDecimal(temp):
                ptuPosMeasData.d_PTU_AzAngle = float(temp)
            else:
                bRet = False

        elif par == 'ptuAngleEl':

            temp = lineArray[key].replace(',', '.')

            if sp.checkDecimal(temp):
                ptuPosMeasData.d_PTU_ElAngle = float(temp)
            else:
                bRet = False

        elif par == 'level':
            temp = lineArray[key]
            if sp.checkDecimal(temp):
                ptuPosMeasData.level_dBm = float(temp)
            else:
                bRet = False

        elif par == 'levelPowerMeter':
            temp = lineArray[key]
            if sp.checkDecimal(temp):
                ptuPosMeasData.levelPowMet_dBm = float(temp)
            else:
                bRet = False

        elif par == 'levelSpecMeas':

            temp = lineArray[key]
            if sp.checkDecimal(temp):
                ptuPosMeasData.levelMeasSpec_dBm = float(temp)
            else:
                bRet = False

        elif par == 'levelPowerMeterMeas':
            temp = lineArray[key]
            if sp.checkDecimal(temp):
                ptuPosMeasData.levelMeasPowMet_dBm = float(temp)
            else:
                bRet = False

        elif par == 'frequency':
            temp = lineArray[key]
            if sp.checkDecimal(temp):
                ptuPosMeasData.frequenz_MHz = float(temp)
            else:
                bRet = False

        elif par == 'time':
            temp = lineArray[key]
            if sp.checkDecimal(temp):
                ptuPosMeasData.time_ms = float(temp)
            else:
                bRet = False

    if not bRet:
        return False

    # Append the PTU position measurements per position to the ptuPosDataList
    if currentPart == searchParts.MaxHeaderData:
        txAntDiagParseData.ptuMaxSpecHeaderData = ptuPosMeasData
    else:
        txAntDiagParseData.ptuPosDataList.append(ptuPosMeasData)

    return bRet

