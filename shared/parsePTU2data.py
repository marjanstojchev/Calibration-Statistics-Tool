import os
from enum import Enum
import io
import safeparse as sp
import logconfig as log

## Parse data module ##

myLogger = log.mainLoadDataLogger.logger

# Power level [dB] and Power level variance [dB^2] per measurement point(angle) inside  one chirp
class AntennaLevelData:
    def __init__(self):
        self.dLevel = -10000  # [dB]
        self.dVarianzLevel = -10000  # [dB ^ 2]

# Phase difference [°] and phase difference variance [dB^2] between two antennas per measurement point(angle) inside one chirp
class DiffPhaseData:
    def __init__(self):
        self.dDiffPhase = -10000 # [°]
        self.dVarianzDiffPhase = -10000 # [° ^ 2]

# Lists of AntennaLevelData and DiffPhaseData for one chirp, regarding more antennas
class ChirpMeasData:
    def __init__(self, antennaLevelData, diffPhaseData):
       self.antennaLevelDataList = antennaLevelData[:]
       self.diffPhaseDataList = diffPhaseData[:]

# PTU angle and chirp measurement data per angle
class PtuPosMeasData:
    def __init__(self):
        self.d_PTU_Angle = -10000 # [°]
        self.chirpMeasDataList = []
    # Pass a list of chirps
    def setChirpMeasDataList(self, chirpMeasDataList):
        self.chirpMeasDataList = chirpMeasDataList[:]

# Meeta data about chirp
class ChirpInfo:
    def __init__(self):
        self.chirp  = 0
        self.active = 0 # Chirp
        self.centerFrequency = 0 # [Hz]
        self.diffPhaseOffsetList=[]
    # Pass a list of phase difference offsets
    def setDiffPhases(self, diffPhaseOffsetList):
        self.diffPhaseOffsetList = []
        self.diffPhaseOffsetList = diffPhaseOffsetList[:]

# Meta data about antenna
class AntennaInfo:
    def __init__(self):
        self.rfSerial = None
        self.antennaType = 0
        self.nofAntennas = 0
        self.nofAntennaDiffValues = 0
        self.antennaDistancesList = []
    # Pass a list of antenna distances
    def setAntennaDistances(self, antennaDistancesList):
        self.antennaDistancesList = []
        self.antennaDistancesList = antennaDistancesList[:]
    # Get the number of differences between antennas
    def getNofAntennaDiffValues(self):
        return len(self.antennaDistancesList)
    # Set number of differences between antennas
    def setNofAntennaDiffValues(self, nofAntennaDiffValues):
        self.nofAntennaDiffValues = nofAntennaDiffValues

class MeasSetupInfo:
    def __init__(self):
        self.phyDoppGenDist          = 0
        self.doppGenHeightPtuZero    = 0
        self.rfBoardMidHeightPtuZero = 0
        self.sensorUpsideDown        = 0
        self.antennaDiagramType      = ''
        self.oppositeToPanAngle      = 0

        self.phyDoppGenDistFound = 0
        self.doppGenHeightPtuZeroFound    = 0
        self.rfBoardMidHeightPtuZeroFound = 0
        self.sensorUpsideDownFound   = 0
        self.antennaDiagramTypeFound = 0
        self.oppositeToPanAngleFound = 0

# Data from the parsed PTU2 file, containing antenna info, chirp info list, and meaurements data for each ptu position
class PTU2ParseData:
    MAX_CHIRP = 4
    def __init__(self):
        self.bDataValid     = False
        self.fileNamePath   = ''
        self.errorList      = []
        self.antennaInfo    = AntennaInfo()
        self.chirpInfoList  = []
        self.ptuPosDataList = [] # Messdaten an der jeweiligen ptu position
        self.fileTitle      = FileTitle()
        self.measSetupInfo  = MeasSetupInfo()
    # Call parse data from the PTU2ParseData object (parseData wrapper)
    def parseFile(self, fileNamePath, useSensorMuster, sensorMusterList):
        self.errorList = []
        self.fileNamePath = fileNamePath
        parseFile(fileNamePath, self)
        self.fileTitle.parseFileTitle(self.fileNamePath, useSensorMuster, sensorMusterList)

# Meta data class from the PTU2 file title
class FileTitle:
    def __init__(self):
        self.dateAndTime = ''
        self.date = ''
        self.time = ''
        self.sensor  = ''
        self.tuner   = ''
        self.txAnt   = 0
        self.seqNum  = 0
        self.diagram = 0
        self.rf  = ''
        self.dsp = ''
        self.fileNamePath = ''
        self.fileName = ''
        self.sensorMusterList = []
        self.useSensorMuster  = 0
        self.sensorMusterValueDict = dict()

        self.dateAndTimeFound = 0
        self.tunerFound = 0
        self.rfFound  = 0
        self.dspFound = 0
        self.txAntFound   = 0
        self.seqNumFound  = 0
        self.diagramFound = 0
        self.sensorFound = 0
        self.sensorMusterFoundDict = dict()


    # Parse the PTU2 file title
    def parseFileTitle(self, fileNamePath,useSensorMuster,sensorMusterList):

        self.fileNamePath = fileNamePath
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

        fileNameParts = fileName.split('_')

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
                        a = part.replace('TxAnt','.')

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
                            self.sensor+=binder+ self.sensorMusterValueDict[key]
                            i += 1
                        else:
                            self.sensorFound = 0

            else:
                if self.rfFound == 1:
                    binder = '_' if self.dspFound == 1 else ''
                    self.sensor = self.rf + binder + self.dsp
                    self.sensorFound = 1

# PTU2 file parts procesing info
class searchParts(Enum):
    MeasSetupData = 0
    Header = 1
    AntennaData = 2
    ChirpData  = 3
    PtuPosData = 4


# Control wrapper for interpretData
def parseFile(fileNamePath,ptu2ParseData):
    myLogger.info('Parsing: ' + fileNamePath)
    ptu2ParseData.fileNamePath = fileNamePath
    interpretData(fileNamePath,ptu2ParseData)
    if len(ptu2ParseData.errorList) == 0:
        ptu2ParseData.bDataValid = True
    else:
        ptu2ParseData.bDataValid = False
    return ptu2ParseData

# Read and interpret the data for every part of the PTU2 file
def interpretData(fileNamePath,ptu2ParseData):
    strMeasName = ptu2ParseData.fileNamePath
    headerLineIndicator0 = 'PTU-Angle['

    measSetupLineIndicator0 = 'Gen21a_PhysicalDopplergenDistance[cm]:'
    measSetupLineIndicator1 = 'Gen21c_DopplerGenHeightToPtuZero[cm]:'
    measSetupLineIndicator2 = 'Gen21d_RFBoardMiddleHeightToPtuZero[cm]:'
    measSetupLineIndicator3 = 'Ptu02_PtuSensorUpsideDown'
    measSetupLineIndicator4 = 'AntennaDiagrammType[1]:'
    measSetupLineIndicator5 = 'OppositeToPanAngle[deg]:'

    # headerLineIndicator1 = 'Level-Ant0[dB]'

    currentPart = searchParts.MeasSetupData

    headerFound = 0
    antennaDataFound = 0
    chirpDataFound   = 0
    ptuPosDataFound  = 0
    chirpCounter = 0

    # Try to read the file
    try:
        f = io.open(fileNamePath)

    # Catch an exception
    except IOError as ioErr:

        # errorString='try reading: ' +fileNamePath+ ' Exception = ' + str(ioErr)
        errorString = strMeasName + ' File does not exist! Insert a valid file path.'

        ptu2ParseData.errorList.append(errorString)
    else:
        # Read the lines of the file and remove all white spaces
        with f:
            content = f.readlines()
        content = [line.strip() for line in content]

        # Traverse through every line of the content
        for line in content:
            if 'File' in line:
                rest = line.split(';')
                ptu2ParseData.fileNamePath = rest[1]
            # Measurement setup info lookup
            if measSetupLineIndicator0 in line:
                rest = line.strip(measSetupLineIndicator0)
                rest = rest.replace(',', '.')
                if sp.checkDecimal(rest):
                    ptu2ParseData.measSetupInfo.phyDoppGenDist = float(rest)
                    ptu2ParseData.measSetupInfo.phyDoppGenDistFound = 1
                else:
                    ptu2ParseData.measSetupInfo.phyDoppGenDistFound = 0
            elif measSetupLineIndicator1 in line:
                rest = line.strip(measSetupLineIndicator1)
                rest = rest.replace(',', '.')
                if sp.checkDecimal(rest):
                    ptu2ParseData.measSetupInfo.doppGenHeightPtuZero = float(rest)
                    ptu2ParseData.measSetupInfo.doppGenHeightPtuZeroFound = 1
                else:
                    ptu2ParseData.measSetupInfo.doppGenHeightPtuZeroFound = 0
            elif measSetupLineIndicator2 in line:
                rest = line.strip(measSetupLineIndicator2)
                rest = rest.replace(',', '.')
                if sp.checkDecimal(rest):
                    ptu2ParseData.measSetupInfo.rfBoardMidHeightPtuZero = float(rest)
                    ptu2ParseData.measSetupInfo.rfBoardMidHeightPtuZeroFound = 1
                else:
                    ptu2ParseData.measSetupInfo.rfBoardMidHeightPtuZeroFound = 0
            elif measSetupLineIndicator3 in line:
                l = len(line)
                c = line[l-1]
                if sp.checkInt(c):
                    ptu2ParseData.measSetupInfo.sensorUpsideDown = int(c)
                    ptu2ParseData.measSetupInfo.sensorUpsideDownFound = 1
                else:
                    ptu2ParseData.measSetupInfo.sensorUpsideDownFound = 0
            elif measSetupLineIndicator4 in line:
                rest = line.strip(measSetupLineIndicator4)
                rest = rest.strip(' ')
                if 'Az' or 'El' in rest:
                    ptu2ParseData.measSetupInfo.antennaDiagramType = rest
                    ptu2ParseData.measSetupInfo.antennaDiagramTypeFound = 1
                else:
                    ptu2ParseData.measSetupInfo.antennaDiagramTypeFound = 0
            elif measSetupLineIndicator5 in line:
                rest = line.strip(measSetupLineIndicator5)
                rest = rest.replace(',', '.')
                if sp.checkInt(rest):
                    ptu2ParseData.measSetupInfo.oppositeToPanAngle = int(rest)
                    ptu2ParseData.measSetupInfo.oppositeToPanAngleFound = 1
                else:
                    ptu2ParseData.measSetupInfo.oppositeToPanAngleFound = 0

            # Swich to header lookup
            else:
                lineArray = line.split(';')
                if (headerLineIndicator0 in lineArray[0]):
                    headerFound += 1
                    currentPart = searchParts.Header

            # Header lookup
            if currentPart == searchParts.Header:
                if headerFound == 1:
                    currentPart = searchParts.AntennaData

            # Antenna info lookup
            elif currentPart == searchParts.AntennaData:
                if antennaDataFound == 0:
                    if len(lineArray) > 3:
                        antennaDataFound += 1
                if antennaDataFound > 0:
                    if not getAntennaData(lineArray, ptu2ParseData):
                        return
                    currentPart = searchParts.ChirpData
                    ptu2ParseData.chirpInfoList = []

            # Chirp info lookup
            elif currentPart == searchParts.ChirpData:
                if chirpCounter < PTU2ParseData.MAX_CHIRP:
                    if len(lineArray) == 3 + ptu2ParseData.antennaInfo.getNofAntennaDiffValues():
                        if not readChirpData(lineArray,ptu2ParseData,chirpCounter):
                            return
                        chirpCounter += 1
                if  chirpCounter == PTU2ParseData.MAX_CHIRP:
                    currentPart = searchParts.PtuPosData
                    ptu2ParseData.ptuPosDataList = []

            # PTU position lookup
            elif currentPart == searchParts.PtuPosData:
                if not readPosPtuData(lineArray,ptu2ParseData):
                    return
                else:
                    ptuPosDataFound += 1

        # Setup error list
        if headerFound == 0:
            ptu2ParseData.errorList.append(strMeasName + ' could not find header in file, no meas. data loaded')
        if headerFound > 1:
            ptu2ParseData.errorList.append(strMeasName + ' found header more than once in file, loaded meas. data probably incorrect')
        if antennaDataFound == 0:
            ptu2ParseData.errorList.append(strMeasName + ' could not find antenna data in file, no measdata loaded')
        if antennaDataFound > 1:
            ptu2ParseData.errorList.append(strMeasName + ' found antenna data more than once in file, loaded measdata probably incorrect')
        if chirpCounter != ptu2ParseData.MAX_CHIRP:
            ptu2ParseData.errorList.append(strMeasName + ' found (only) ' + str(chirpCounter)+ ' Chirp data of ' + str(ptu2ParseData.MAX_CHIRP) + ' Chirps')

# Parses the antenna info part
def getAntennaData(lineArray, ptu2ParseData):
    bRet = True
    if len(lineArray) >= 4:
        index = 0
        nofDiffValues=0

        temp = lineArray[index].replace(',', '.')
        if(sp.checkWholeNum(temp)):
            ptu2ParseData.antennaInfo.rfSerial = int(float(temp))
        else:
            bRet= False

        index += 1

        temp = lineArray[index].replace(',', '.')
        if(sp.checkWholeNum(temp)):
            ptu2ParseData.antennaInfo.antennaType = int(float(temp))
        else:
            bRet = False

        index += 1

        temp = lineArray[index].replace(',', '.')
        if(sp.checkWholeNum(temp)):
            ptu2ParseData.antennaInfo.nofAntennas = int(float(temp))
        else:
            bRet = False

        index += 1

        temp = lineArray[index].replace(',', '.')
        if(sp.checkWholeNum(temp)):
           nofDiffValues = int(float(temp))
        else:
            bRet = False

        index += 1

        ptu2ParseData.antennaInfo.setNofAntennaDiffValues(nofDiffValues)

        if len(lineArray) == (index + nofDiffValues):
            antennaDistList = []
            for antennaDistIndex in range(nofDiffValues):
                tempDistance = 0
                temp = lineArray[index+antennaDistIndex].replace(',','.')
                if (sp.checkDecimal(temp)):
                    tempDistance = float(temp)
                    tempDistance*= 0.01e-3 # [0, 01mm] = > [m]
                    antennaDistList.append(tempDistance)
                else:
                    bRet = False
            ptu2ParseData.antennaInfo.setAntennaDistances(antennaDistList)
        else:
            bRet = False
    else:
        bRet = False
    if bRet != True:
        errorString = ptu2ParseData.fileNamePath + ' Error 1 - Antennendaten einlesen'
        ptu2ParseData.errorList.append(errorString)
    return bRet

# Control wrapper for getChirpData
def readChirpData(lineArray,ptu2ParseData,chirpcounter):
    if not getChirpData(lineArray,ptu2ParseData):
        ptu2ParseData.errorList.append(str(ptu2ParseData.fileNamePath) + ' Error 2 - Chirp ' + str(chirpcounter) + ' daten einlesen')
        return False
    else:
        return True

# Parses the chirp info part
def getChirpData(lineArray, ptu2ParseDataClass):
    bRet = True
    if len(lineArray) != (3 + ptu2ParseDataClass.antennaInfo.getNofAntennaDiffValues()):
        return False
    chirpInfo = ChirpInfo()

    temp = lineArray[0].replace(',','.')
    if sp.checkDecimal(temp):
        chirpInfo.chirp = float(temp)
    else:
        bRet = False

    temp = lineArray[1].replace(',','.')
    if sp.checkDecimal(temp):
        chirpInfo.active = float(temp)
    else:
        bRet = False

    temp = lineArray[2].replace(',','.')
    if sp.checkDecimal(temp):
        chirpInfo.centerFrequency  = float(temp)
        chirpInfo.centerFrequency *= 1e4 # [10kHz] => [Hz]
    else:
        bRet = False

    diffPhaseOffsetList = []
    for index in range(ptu2ParseDataClass.antennaInfo.getNofAntennaDiffValues()):
        diffPhaseOffset = 0

        temp = lineArray[index + 3].replace(',','.')
        if sp.checkDecimal(temp):
            diffPhaseOffset = float(temp)
        else:
            bRet = False

        diffPhaseOffsetList.append(diffPhaseOffset)
    chirpInfo.setDiffPhases(diffPhaseOffsetList)
    ptu2ParseDataClass.chirpInfoList.append(chirpInfo)
    return bRet

# Control wrapper for getMeasData
def readPosPtuData(lineArray,ptu2ParseData):
    if not getMeasData(lineArray,ptu2ParseData):
        ptu2ParseData.errorList.append(str(ptu2ParseData.fileNamePath) + ' Error 3 - Messdaten einlesen')
        return False
    return True

# Parses the measurements data part per one PTU position
def getMeasData(lineArray,ptu2ParseData):
    bRet  =  True
    nofChirpValues = 2*(ptu2ParseData.antennaInfo.nofAntennas + ptu2ParseData.antennaInfo.getNofAntennaDiffValues())

    if len(lineArray) != (1+ ptu2ParseData.MAX_CHIRP * nofChirpValues):
        return False

    chirpMeasDataList = []

    ptuPosMeasData = PtuPosMeasData()
    # Traverse through each chirp and parse the PTU angle
    for chirpIndex in range(PTU2ParseData.MAX_CHIRP):

        temp = lineArray[0].replace(',','.')
        if sp.checkDecimal(temp):
            ptuPosMeasData.d_PTU_Angle = float(temp)
        else:
            bRet = False

        levelDataList = []
        # Parses the antenna level and variance for each antenna
        for antennaIndex in range(ptu2ParseData.antennaInfo.nofAntennas):
            levelData = AntennaLevelData()

            temp = lineArray[1+(nofChirpValues*chirpIndex) +2*antennaIndex].replace(',', '.')
            if sp.checkDecimal(temp):
                levelData.dLevel = float(temp)
            else:
                bRet = False

            temp = lineArray[2 + (nofChirpValues * chirpIndex) + 2 * antennaIndex].replace(',', '.')
            if sp.checkDecimal(temp):
                levelData.dVarianzLevel = float(temp)
            else:
                bRet = False
            levelDataList.append(levelData)

        diffPhaseDataList = []
        # Parses the phase difference and variance for each antenna
        for phaseIndex in range(ptu2ParseData.antennaInfo.getNofAntennaDiffValues()):
            diffPhaseData = DiffPhaseData()

            temp = lineArray[1+ (2*ptu2ParseData.antennaInfo.nofAntennas) + (chirpIndex*nofChirpValues) +(2*phaseIndex)].replace(',', '.')
            if sp.checkDecimal(temp):
                diffPhaseData.dDiffPhase = float(temp)
            else:
                bRet = False

            temp = lineArray[2+(2*ptu2ParseData.antennaInfo.nofAntennas) + (chirpIndex*nofChirpValues) +(2*phaseIndex)].replace(',', '.')
            if sp.checkDecimal(temp):
                diffPhaseData.dVarianzDiffPhase = float(temp)
            else:
                bRet = False
            diffPhaseDataList.append(diffPhaseData)
        if not bRet:
            return False
        # Packing the level and phase difference values to chirp measurements data (ChirpMeasData)
        chirpMeasData = ChirpMeasData(levelDataList,diffPhaseDataList)
        # Appending the chirp measurements data to a chirp list
        chirpMeasDataList.append(chirpMeasData)
    # Set the chirp measurements list to the PTU position data class (PtuPosMeasData)
    ptuPosMeasData.setChirpMeasDataList(chirpMeasDataList)
    # Append the PTU position measurements per position to the ptuPosDataList
    ptu2ParseData.ptuPosDataList.append(ptuPosMeasData)
    return bRet

