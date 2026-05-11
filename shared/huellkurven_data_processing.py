from __future__ import annotations
import os
import re
import enum
import sys
import errno
import logging
from operator import itemgetter

import numpy as np

from shared import loaddata as ld
from shared import calcdiagram_functions as calc
from shared import logconfig
from shared import auxiliary as aux
from shared import safeparse as sp

myLogger = logging.getLogger(__name__)


class LimitsHeader(enum.Enum):
    AntennaType = '#AntennaType'
    NofAntennas = '#NofAntennas'
    NofDiffPhases = '#NofDiffPhases'
    NofChirps = '#NofChirps:'
    PanType = '#PanType'


class LimitsData():
    def __init__(self):
        self.fileFormatVersion = '1'
        self.antennaType = 153
        self.nofAntennas = 4
        self.nofDiffPhases = 3
        self.nofChirps = 1
        self.usedChirpBitCoded = 1
        self.panType = 1  # 0-Azimut|1-Elevation
        self.activeTx = 0
        self.txFrequency = 0
        self.diagTypeInfo = 1
        self.upsideDownInfo = 1
        self.angleSetupStr = ''
        self.title = ''
        self.angle = []
        self.rxAntPatternData = []
        self.rxChPhaseDiffData = []
        self.parseDataList = []
        self.commentsDict = []
        self.patternMethod = 0
        self.version = ''

        self.parseError = 0
        self.parseErrorList = []

    def parseLimitsDataFileHeader(self, filePath):
        with open(filePath, 'r+') as limitsDataFile:
            content = limitsDataFile.readlines()

            found = 0
            for line in content:
                line = re.sub(r"\s\s+", " ", line)
                line = line.strip('\n')
                line.strip()
                if LimitsHeader.AntennaType.value in line:
                    found = 1
                    valList = line.split(':')
                    if sp.checkInt(valList[1]):
                        self.antennaType = int(valList[1])
                    else:
                        parseError = 1
                        self.parseErrorList.append('AntennaType parsing error, value: ' + valList[1])
                    break
            if not found:
                parseError = 1
                self.parseErrorList.append('AntennaType not found in limits .dat file.')

            found = 0
            for line in content:
                line = re.sub(r"\s\s+", " ", line)
                line = line.strip('\n')
                line.strip()
                if LimitsHeader.NofAntennas.value in line:
                    valList = line.split(':')
                    found = 1
                    if sp.checkInt(valList[1]):
                        self.nofAntennas = int(valList[1])
                    else:
                        parseError = 1
                        self.parseErrorList.append('NofAntennas parsing error, value: ' + valList[1])
                    break
            if not found:
                parseError = 1
                self.parseErrorList.append('NofAntennas not found in limits .dat file.')

            found = 0
            for line in content:
                line = re.sub(r"\s\s+", " ", line)
                line = line.strip('\n')
                line.strip()
                if LimitsHeader.NofDiffPhases.value in line:
                    valList = line.split(':')
                    found = 1
                    if sp.checkInt(valList[1]):
                        self.nofDiffPhases = int(valList[1])
                    else:
                        parseError = 1
                        self.parseErrorList.append('NofDiffPhases parsing error, value: ' + valList[1])
                    break
            if not found:
                parseError = 1
                self.parseErrorList.append('NofDiffPhases not found in limits .dat file.')

            found = 0
            for line in content:
                line = re.sub(r"\s\s+", " ", line)
                line = line.strip('\n')
                line.strip()
                if LimitsHeader.NofChirps.value in line:
                    valList = line.split(':')
                    found = 1
                    if sp.checkInt(valList[1]):
                        self.nofChirps = int(valList[1])
                    else:
                        parseError = 1
                        self.parseErrorList.append('NofChirps parsing error, value: ' + valList[1])
                    break
            if not found:
                parseError = 1
                self.parseErrorList.append('NofChirps not found in limits .dat file.')

            found = 0
            for line in content:
                line = re.sub(r"\s\s+", " ", line)
                line = line.strip('\n')
                line.strip()
                if LimitsHeader.PanType.value in line:
                    valList = line.split(':')
                    found = 1
                    if sp.checkInt(valList[1]):
                        self.panType = int(valList[1])
                    else:
                        parseError = 1
                        self.parseErrorList.append('PanType parsing error, value: ' + valList[1])
                    break
            if not found:
                parseError = 1
                self.parseErrorList.append('PanType not found in limits .dat file.')

    def parseLimitsDataFileValues(self, filePath, bParseSample=False):
        with open(filePath, 'r+') as limitsDataFile:
            content = limitsDataFile.readlines()

            lineArrayList = []

            for line in content:
                if '#' not in line and '//' not in line:
                    line = re.sub(r"\s\s+", " ", line)
                    line = line.strip('\n')
                    lineArray = line.split(' ')

                    for idx in range(len(lineArray)):
                        if sp.checkDecimal(lineArray[idx]):
                            lineArray[idx] = float(lineArray[idx])
                        else:
                            errorStr = 'Parsing error: ' + lineArray[idx]
                            self.parseErrorList.append(errorStr)
                            self.parseError = 1

                    lineArray = np.array(lineArray)

                    if lineArray.size != (self.nofAntennas + self.nofDiffPhases) * 2 + 1:
                        errorStr = 'Invalid number of elements, line: ' + line
                        self.parseErrorList.append(errorStr)
                        self.parseError = 1

                    lineArrayList.append(lineArray)

            lineMatrix = np.array(lineArrayList)

        if self.parseError == 0:
            if bParseSample:
                self.angle = list(lineMatrix[:, 0])
                for rxChIdx in range(self.nofAntennas):
                    self.rxAntPatternData.append(RxAntPatternData())
                for rxChIdx in range(self.nofAntennas - 1):
                    self.rxChPhaseDiffData.append(RxChPhaseDiffData())

                rxAnt = 0
                angleArrOff = 1
                minArrOff = 1
                for col in range(angleArrOff, (angleArrOff + (self.nofAntennas) * 2), 2):
                    self.rxAntPatternData[rxAnt].minPatternLimits = list(lineMatrix[:, col])
                    rxAnt += 1

                rxAnt = 0
                for col in range(angleArrOff + minArrOff, (angleArrOff + minArrOff + ((self.nofAntennas) * 2) - 1), 2):
                    self.rxAntPatternData[rxAnt].maxPatternLimits = list(lineMatrix[:, col])
                    rxAnt += 1

                rxAntOff = self.nofAntennas * 2

                rxAnt = 0
                for col in range(angleArrOff + rxAntOff, (angleArrOff + rxAntOff + (self.nofDiffPhases) * 2), 2):
                    self.rxChPhaseDiffData[rxAnt].minPhaseLimits = list(lineMatrix[:, col])
                    rxAnt += 1

                rxAnt = 0
                for col in range(angleArrOff + rxAntOff + minArrOff,
                                 (angleArrOff + rxAntOff + minArrOff + ((self.nofDiffPhases) * 2) - 1), 2):
                    self.rxChPhaseDiffData[rxAnt].maxPhaseLimits = list(lineMatrix[:, col])
                    rxAnt += 1
            else:
                rxAnt = 0
                angleArrOff = 1
                minArrOff = 1
                for col in range(angleArrOff, (angleArrOff + (self.nofAntennas) * 2), 2):
                    self.rxAntPatternData[rxAnt].minPatternLimits = list(lineMatrix[:, col])
                    rxAnt += 1

                rxAnt = 0
                for col in range(angleArrOff + minArrOff, (angleArrOff + minArrOff + ((self.nofAntennas) * 2) - 1), 2):
                    self.rxAntPatternData[rxAnt].maxPatternLimits = list(lineMatrix[:, col])
                    rxAnt += 1

                rxAntOff = self.nofAntennas * 2

                rxAnt = 0
                for col in range(angleArrOff + rxAntOff, (angleArrOff + rxAntOff + (self.nofDiffPhases) * 2), 2):
                    self.rxChPhaseDiffData[rxAnt].minPhaseLimits = list(lineMatrix[:, col])
                    rxAnt += 1

                rxAnt = 0
                for col in range(angleArrOff + rxAntOff + minArrOff,
                                 (angleArrOff + rxAntOff + minArrOff + ((self.nofDiffPhases) * 2) - 1), 2):
                    self.rxChPhaseDiffData[rxAnt].maxPhaseLimits = list(lineMatrix[:, col])
                    rxAnt += 1


class RxAntPatternData():
    def __init__(self):
        self.ptuLevelPerRxAntenna = []
        self.minPatternLimits = []
        self.maxPatternLimits = []
        self.medianPatternLimits = []
        self.minSampleLimits = []
        self.maxSampleLimits = []

    def getLevelAllPtuFiles(self, parseDataList, diagramNum, chirp, rxCh, filterByTxAntenna, txAntenna):
        self.ptuLevelPerRxAntenna = []
        if filterByTxAntenna != 1:
            for pdIdx in range(len(parseDataList)):
                if parseDataList[pdIdx].fileTitle.diagram == diagramNum and parseDataList[pdIdx].chirpInfoList[chirp].active == 1:
                    level = calc.getNormAntLevel(rxCh, chirp, parseDataList[pdIdx])
                    self.ptuLevelPerRxAntenna.append(level)
        else:
            for pdIdx in range(len(parseDataList)):
                if parseDataList[pdIdx].fileTitle.diagram == diagramNum and parseDataList[pdIdx].chirpInfoList[chirp].active == 1 and parseDataList[pdIdx].fileTitle.txAnt == txAntenna:
                    level = calc.getNormAntLevel(rxCh, chirp, parseDataList[pdIdx])
                    self.ptuLevelPerRxAntenna.append(level)

    def setLimitsList(self, minSigma, maxSigma, patternLimitsMethod, reserveDb):
        self.minPatternLimits = []
        self.maxPatternLimits = []
        self.medianPatternLimits = []
        for levelIdx in range(len(self.ptuLevelPerRxAntenna[0])):
            auxList = []
            for ptuIdx in range(len(self.ptuLevelPerRxAntenna)):
                levelPerIdx = self.ptuLevelPerRxAntenna[ptuIdx][levelIdx]
                auxList.append(levelPerIdx)
            minVal, maxVal, median, stdDev, minimum, maximum = calcPatternLimits(auxList, minSigma, maxSigma, patternLimitsMethod, reserveDb)
            self.minPatternLimits.append(minVal)
            self.maxPatternLimits.append(maxVal)
            self.medianPatternLimits.append(median)


class RxChPhaseDiffData():
    def __init__(self):
        self.ptuPhaseDiffPerRxCh = []
        self.minPhaseLimits = []
        self.maxPhaseLimits = []
        self.medianPhase = []

    def getPhaseDiffAllPtuFiles(self, parseDataList, diagramNum, chirp, rxCh, filterByTxAntenna, txAntenna):
        self.ptuPhaseDiffPerRxCh = []
        if filterByTxAntenna != 1:
            for pdIdx in range(len(parseDataList)):
                if parseDataList[pdIdx].fileTitle.diagram == diagramNum and parseDataList[pdIdx].chirpInfoList[chirp].active == 1:
                    phaseDiff = calc.getPhaseDiffOffCorrCont(rxCh, chirp, parseDataList[pdIdx])
                    self.ptuPhaseDiffPerRxCh.append(phaseDiff)
        else:
            for pdIdx in range(len(parseDataList)):
                if parseDataList[pdIdx].fileTitle.diagram == diagramNum and parseDataList[pdIdx].chirpInfoList[chirp].active == 1 and parseDataList[pdIdx].fileTitle.txAnt == txAntenna:
                    phaseDiff = calc.getPhaseDiffOffCorrCont(rxCh, chirp, parseDataList[pdIdx])
                    self.ptuPhaseDiffPerRxCh.append(phaseDiff)

    def setLimitsList(self, minPhaseFactor, maxPhaseFactor):
        self.minPhaseLimits = []
        self.maxPhaseLimits = []
        self.medianPhase = []
        for levelIdx in range(len(self.ptuPhaseDiffPerRxCh[0])):
            auxList = []
            for ptuIdx in range(len(self.ptuPhaseDiffPerRxCh)):
                phaseDiffPerIdx = self.ptuPhaseDiffPerRxCh[ptuIdx][levelIdx]
                auxList.append(phaseDiffPerIdx)
            minVal, maxVal, median = calcPhaseLimits(auxList, minPhaseFactor, maxPhaseFactor)
            self.minPhaseLimits.append(minVal)
            self.maxPhaseLimits.append(maxVal)
            self.medianPhase.append(median)

        self.applyToleranceAngRangePhaseDiff()

    def applyToleranceAngRangePhaseDiff(self):
        MAX = 10000 * 180 + 180
        MIN = -10000 * 180 - 180
        zeroDegIdxOdd = 0
        zeroDegIdxUpper = 0
        zeroDegIdxLower = 0

        satisfied = 0
        WHOLE_TURN = 360
        lowerIndex = 0
        upperIndex = 0
        indexFeched = 0

        if len(self.maxPhaseLimits) % 2 == 0:
            zeroDegIdxLower = int(len(self.maxPhaseLimits) / 2) - 1
            zeroDegIdxUpper = int(len(self.maxPhaseLimits) / 2)
        else:
            zeroDegIdxOdd = int((len(self.maxPhaseLimits) - 1) / 2)
            zeroDegIdxLower = zeroDegIdxUpper = zeroDegIdxOdd

        for idx in range(zeroDegIdxUpper, len(self.maxPhaseLimits)):
            max_val = self.maxPhaseLimits[idx]
            min_val = self.minPhaseLimits[idx]
            diff = max_val - min_val
            if diff > WHOLE_TURN:
                satisfied = 1
                if indexFeched == 0:
                    upperIndex = idx
                    indexFeched = 1
            if satisfied == 1:
                self.maxPhaseLimits[idx] = MAX
                self.minPhaseLimits[idx] = MIN

        satisfied = 0
        indexFeched = 0
        for idx in range(zeroDegIdxLower, -1, -1):
            max_val = self.maxPhaseLimits[idx]
            min_val = self.minPhaseLimits[idx]
            diff = max_val - min_val
            if diff > WHOLE_TURN:
                satisfied = 1
                if indexFeched == 0:
                    lowerIndex = idx
                    indexFeched = 1
            if satisfied == 1:
                self.maxPhaseLimits[idx] = MAX
                self.minPhaseLimits[idx] = MIN


def createLimitsData(version, commentsDict, desiredDiagramList, diagListIdx, chirp, antennaType, parseDataList,
                     angleSetup, centFreqDictList, diagType, inputConfig, chirpConfig, dataConf,
                     write_output: bool = False):

    limitsData = LimitsData()
    limitsData.version = version
    limitsData.patternMethod = dataConf['patternLimitsMethod']
    limitsData.commentsDict = commentsDict

    parseDataFilteredList = []

    for pdIdx in range(len(parseDataList)):
        if desiredDiagramList[diagListIdx]['diagramNum'] == parseDataList[pdIdx].fileTitle.diagram and parseDataList[pdIdx].chirpInfoList[chirp].active == 1:

            limitsData.nofChirps = len(getValidChirpList(chirpConfig, parseDataList, pdIdx))
            limitsData.usedChirpBitCoded = pow(2, chirp)
            limitsData.panType = 0 if diagType == 'Az' else 1  # 0-Azimut|1-Elevation
            limitsData.activeTx = parseDataList[pdIdx].fileTitle.txAnt
            limitsData.angleSetupStr = angleSetup.angleSetupStr
            limitsData.diagTypeInfo = inputConfig['diagTypeInfo']
            limitsData.upsideDownInfo = inputConfig['upsideDownInfo']
            limitsData.diagType = diagType

            parseDataFilteredList.append(parseDataList[pdIdx])

            if centFreqDictList[diagListIdx]['chirp'] == chirp:
                limitsData.txFrequency = centFreqDictList[diagListIdx]['avgFreqMHz']

            limitsData.angle = calc.getPtuAngVals(parseDataList[0])

            if inputConfig['targetAngle'] == 1:
                limitsData.angle = calc.getTarAngVals(parseDataList[0], getUpsideDown(parseDataList[0], inputConfig))

    limitsData.antennaType = antennaType
    limitsData.nofAntennas = getMaxNofRxAntennas(parseDataFilteredList)
    limitsData.nofDiffPhases = getMaxNofRxAntennas(parseDataFilteredList) - 1

    for rxChIdx in range(limitsData.nofAntennas):
        rxAntPatternData = RxAntPatternData()
        rxAntPatternData.getLevelAllPtuFiles(parseDataFilteredList, desiredDiagramList[diagListIdx]['diagramNum'], chirp, rxChIdx, 0, 0)
        rxAntPatternData.setLimitsList(dataConf['minSigma'], dataConf['maxSigma'], dataConf['patternLimitsMethod'], dataConf['reserveDb'])
        limitsData.rxAntPatternData.append(rxAntPatternData)

    for rxChIdx in range(limitsData.nofDiffPhases):
        rxChPhaseDiffData = RxChPhaseDiffData()
        rxChPhaseDiffData.getPhaseDiffAllPtuFiles(parseDataFilteredList, desiredDiagramList[diagListIdx]['diagramNum'], chirp, rxChIdx, 0, 0)
        rxChPhaseDiffData.setLimitsList(dataConf['minPhaseFactor'], dataConf['maxPhaseFactor'])
        limitsData.rxChPhaseDiffData.append(rxChPhaseDiffData)

    angleSetupStr = 'NofPts=' + str(angleSetup.nofAnglePoints) + '_StepSize=' + str(angleSetup.angleStepSize) + '_RefPt=' + str(angleSetup.refAnglePoint)
    antTypeStr = 'AntType' + str(limitsData.antennaType)

    limitsData.outputPath = os.path.join(antTypeStr, angleSetupStr)

    limitsData.title = ''
    limitsData.title += diagType + '_TxAnt' + str(limitsData.activeTx) + '_Diagram' + str(desiredDiagramList[diagListIdx]['diagramNum']) + '_Chirp' + str(chirp) + '.dat'

    if write_output:
        writeLimitsDataToFile(limitsData)

    return limitsData


def writeLimitsDataToFile(limitsData):
    limitsDataFileStr = ''
    limitsDataFileStr += '#FileFormatVersion: ' + str(limitsData.version) + limitsData.commentsDict['version'] + '\n'
    limitsDataFileStr += '#AntennaType: ' + str(limitsData.antennaType) + '\n'
    limitsDataFileStr += '#NofAntennas: ' + str(limitsData.nofAntennas) + '\n'
    limitsDataFileStr += '#NofDiffPhases: ' + str(limitsData.nofDiffPhases) + '\n'
    limitsDataFileStr += '#NofChirps: ' + str(limitsData.nofChirps) + '\n'
    limitsDataFileStr += '#UsedChirpBitCoded: ' + str(limitsData.usedChirpBitCoded) + '\n'
    limitsDataFileStr += '#PanType: ' + str(limitsData.panType) + '\n'
    limitsDataFileStr += '#ActiveTx: ' + str(limitsData.activeTx) + '\n'
    limitsDataFileStr += '#TxFrequency: ' + str(limitsData.txFrequency) + '\n'
    limitsDataFileStr += '#diagTypeInfo: ' + str(limitsData.diagTypeInfo) + '\n'
    limitsDataFileStr += '#upsideDownInfo: ' + str(limitsData.upsideDownInfo) + '\n'

    for angleIdx in range(len(limitsData.angle)):
        limitsDataFileStr += str(limitsData.angle[angleIdx])

        for rxAntIdx in range(len(limitsData.rxAntPatternData)):
            limitsDataFileStr += ' ' + str(limitsData.rxAntPatternData[rxAntIdx].minPatternLimits[angleIdx])
            limitsDataFileStr += ' ' + str(limitsData.rxAntPatternData[rxAntIdx].maxPatternLimits[angleIdx])

        for rxAntIdx in range(len(limitsData.rxChPhaseDiffData)):
            limitsDataFileStr += ' ' + str(limitsData.rxChPhaseDiffData[rxAntIdx].minPhaseLimits[angleIdx])
            limitsDataFileStr += ' ' + str(limitsData.rxChPhaseDiffData[rxAntIdx].maxPhaseLimits[angleIdx])

        limitsDataFileStr += '\n'

    outputPath = os.path.join(aux.huellKurvenOutputPath, limitsData.outputPath)
    outputPath = os.path.join(outputPath, limitsData.title)

    with open(outputPath, 'w+') as dat_file:
        dat_file.truncate(0)
        dat_file.write(limitsDataFileStr)
        myLogger.info('Limits data saved: ' + outputPath)


def noDiagTypeDataFound(parseDataList):
    val = False
    for pdIdx in range(len(parseDataList)):
        if parseDataList[pdIdx].measSetupInfo.antennaDiagramTypeFound == 0:
            val = True
            break
    return val


def azDataFound(parseDataList):
    val = False
    for pdIdx in range(len(parseDataList)):
        if (parseDataList[pdIdx].measSetupInfo.antennaDiagramTypeFound == 1) and (parseDataList[pdIdx].measSetupInfo.antennaDiagramType == 'Az'):
            val = True
            break
    return val


def getUpsideDown(parseData, ptu2InputConfig):
    if ptu2InputConfig['upsideDownInfo'] == 0:
        upsideDown = ptu2InputConfig['upsideDown']
    else:
        upsideDown = parseData.measSetupInfo.sensorUpsideDown
    return upsideDown


def getDateTimeSensorCombList(antennaType, parseDataList):
    outputDictList = []
    sensor = ''
    dateAndTime = ''
    for listIdx in range(len(parseDataList)):
        outputDict = dict()
        if parseDataList[listIdx].fileTitle.sensorFound != 0 and parseDataList[listIdx].fileTitle.dateAndTimeFound != 0:
            if parseDataList[listIdx].fileTitle.sensor != sensor or parseDataList[listIdx].fileTitle.dateAndTime != dateAndTime:
                dateAndTime = parseDataList[listIdx].fileTitle.dateAndTime
                sensor = parseDataList[listIdx].fileTitle.sensor
                outputDict.update({"dateAndTime": dateAndTime, "sensor": sensor})
                outputDictList.append(outputDict)
    return outputDictList


def getNofActualRxAntennas(parseDataList, pdIdx):
    actualNofRxCh = parseDataList[pdIdx].antennaInfo.nofAntennas
    return actualNofRxCh


def getMaxNofRxAntennas(parseDataList):
    nofRxChList = []
    for pdIdx in range(len(parseDataList)):
        nofRxCh = getNofActualRxAntennas(parseDataList, pdIdx)
        nofRxChList.append(nofRxCh)
    return max(nofRxChList)


def getPtu2ListPerAngleSetup(parseDataList, angleSetup, diagType):
    outputList = []
    if diagType != 1:
        for parseDataIdx in range(len(parseDataList)):
            angleStep = getAngleStep(parseDataList[parseDataIdx])
            nofAngPts = getNofAnglePoints(parseDataList[parseDataIdx])
            refAngPt = getRefAnglePoint(parseDataList[parseDataIdx])
            if (nofAngPts == angleSetup.nofAnglePoints) and (angleStep == angleSetup.angleStepSize) and (abs(angleSetup.refAnglePoint - refAngPt) < 0.1) and ('NoDiagType' == angleSetup.diagType):
                outputList.append(parseDataList[parseDataIdx])
    else:
        for parseDataIdx in range(len(parseDataList)):
            angleStep = getAngleStep(parseDataList[parseDataIdx])
            nofAngPts = getNofAnglePoints(parseDataList[parseDataIdx])
            refAngPt = getRefAnglePoint(parseDataList[parseDataIdx])
            if (nofAngPts == angleSetup.nofAnglePoints) and (angleStep == angleSetup.angleStepSize) and (abs(angleSetup.refAnglePoint - refAngPt) < 0.1) and ('NoDiagType' != angleSetup.diagType):
                outputList.append(parseDataList[parseDataIdx])
    return outputList


def getPtu2PerUpsideDownInfo(parseDataList, upsideDownInfo):
    outputList = []
    if upsideDownInfo == 1:
        for pdIdx in range(len(parseDataList)):
            if parseDataList[pdIdx].measSetupInfo.sensorUpsideDownFound == 1:
                outputList.append(parseDataList[pdIdx])
    else:
        for pdIdx in range(len(parseDataList)):
            if parseDataList[pdIdx].measSetupInfo.sensorUpsideDownFound != 1:
                outputList.append(parseDataList[pdIdx])
    return outputList


def ptu2PerDiagType(parseDataList):
    azList = []
    elList = []
    noDiagTypeList = []
    for pdIdx in range(len(parseDataList)):
        if parseDataList[pdIdx].measSetupInfo.antennaDiagramTypeFound == 1:
            if parseDataList[pdIdx].measSetupInfo.antennaDiagramType == 'Az':
                azList.append(parseDataList[pdIdx])
            else:
                elList.append(parseDataList[pdIdx])
        else:
            noDiagTypeList.append(parseDataList[pdIdx])
    return azList, elList, noDiagTypeList


def getConfiguredPtu2Files(parseDataList, angleSetup, inputConfig):
    ptu2PerAngleSetupList = getPtu2ListPerAngleSetup(parseDataList, angleSetup, inputConfig['diagTypeInfo'])
    ptu2PerUpsideDownInfo = getPtu2PerUpsideDownInfo(ptu2PerAngleSetupList, inputConfig['upsideDownInfo'])
    if inputConfig['upsideDownInfo'] == 1 and len(ptu2PerUpsideDownInfo) == 0:
        myLogger.error('No PTU2 files WITH Upside-Down Info found!')
    if inputConfig['upsideDownInfo'] == 0 and len(ptu2PerUpsideDownInfo) == 0:
        myLogger.error('No PTU2 files WITHOUT Upside-Down Info found!')
    return ptu2PerUpsideDownInfo


def calcPatternLimits(data, min_sigma, max_sigma, method, reserveDb):
    median = np.median(data)
    stdDev = np.std(data)
    minimum = min(data)
    maximum = max(data)
    if method == 0:
        minLimit = median + min_sigma * stdDev - reserveDb
        maxLimit = median + max_sigma * stdDev + reserveDb
    else:
        minLimit = minimum - stdDev - 7
        maxLimit = maximum + stdDev + 3
    return minLimit, maxLimit, median, stdDev, minimum, maximum


def calcPhaseLimits(data, min_phase_factor, max_phase_factor):
    median = np.median(data)
    minLimit = median - min_phase_factor * np.std(data)
    maxLimit = median + max_phase_factor * np.std(data)
    return minLimit, maxLimit, median


def getTxAntList(parseDataList):
    actualTxAnt = 0
    txAntList = []
    for pdIdx in range(len(parseDataList)):
        if parseDataList[pdIdx].fileTitle.txAntFound == 1:
            actualTxAnt = parseDataList[pdIdx].fileTitle.txAnt
            txAntList.append(actualTxAnt)

    txAntList.sort()
    txAntSet = set(txAntList)
    outputList = list(txAntSet)
    return outputList


def getConfChirpList(chirpSetup):
    chirpList = []
    for chirp, set in chirpSetup.items():
        if set == 1:
            parts = chirp.split('chirp')
            chirpNum = parts[1]
            chirpNum = int(chirpNum)
            chirpList.append(chirpNum)
    return chirpList


def getDesiredDiagramsList(diagramConfig, diagramConfigList, antType, parseDataList):
    desiredDiagramList = []
    diagramTempList = getDiagramList(antType, parseDataList)
    high = diagramConfig["higherNumber"]
    low = diagramConfig["lowerNumber"]

    if diagramConfig['selectDiagrams'] == 0:
        if diagramConfig['oddOrEven'] == 0:
            desiredDiagramList = diagramTempList
        elif diagramConfig['oddOrEven'] == 1:
            for i in range(len(diagramTempList)):
                if diagramTempList[i]['diagramNum'] % 2 != 0:
                    desiredDiagramList.append(diagramTempList[i])
        else:
            for i in range(len(diagramTempList)):
                if diagramTempList[i]['diagramNum'] % 2 == 0:
                    desiredDiagramList.append(diagramTempList[i])

    elif diagramConfig['selectDiagrams'] == 1:
        if diagramConfig['oddOrEven'] == 0:
            for diagIdx in range(len(diagramTempList)):
                if diagramTempList[diagIdx]['diagramNum'] >= low and diagramTempList[diagIdx]['diagramNum'] <= high:
                    desiredDiagramList.append(diagramTempList[diagIdx])
        elif diagramConfig['oddOrEven'] == 1:
            for diagIdx in range(len(diagramTempList)):
                if diagramTempList[diagIdx]['diagramNum'] >= low and diagramTempList[diagIdx]['diagramNum'] <= high and diagramTempList[diagIdx]['diagramNum'] % 2 != 0:
                    desiredDiagramList.append(diagramTempList[diagIdx])
        else:
            for diagIdx in range(len(diagramTempList)):
                if diagramTempList[diagIdx]['diagramNum'] >= low and diagramTempList[diagIdx]['diagramNum'] <= high and diagramTempList[diagIdx]['diagramNum'] % 2 == 0:
                    desiredDiagramList.append(diagramTempList[diagIdx])
    else:
        diagramConfigList.sort()
        diagramTxAntList = []
        for i in range(len(diagramConfigList)):
            for j in range(len(diagramTempList)):
                if diagramConfigList[i] == diagramTempList[j]['diagramNum']:
                    diagramTxAntList.append(diagramTempList[j])
        desiredDiagramList = diagramTxAntList

    return desiredDiagramList


def getDiagramList(antType, parseDataList):
    diagramtxAntList = []

    for pdIdx in range(len(parseDataList)):
        diagramTxAntDict = {
            'diagramNum': 0,
            'txAnt': 0
        }
        if parseDataList[pdIdx].antennaInfo.antennaType == antType:
            if parseDataList[pdIdx].fileTitle.diagramFound == 1:
                diagram = parseDataList[pdIdx].fileTitle.diagram
                diagramTxAntDict['diagramNum'] = diagram
            if parseDataList[pdIdx].fileTitle.txAntFound == 1:
                diagramTxAntDict['txAnt'] = parseDataList[pdIdx].fileTitle.txAnt
                diagramtxAntList.append(diagramTxAntDict)

    newList = sorted(diagramtxAntList, key=itemgetter('diagramNum'))

    outputList = []

    if len(newList) != 0:
        temp = newList[0]
        outputList.append(temp)
        for i in range(len(newList)):
            if newList[i]['diagramNum'] != temp['diagramNum']:
                temp = newList[i]
                outputList.append(temp)

    return outputList


class AngleSetup():
    def __init__(self, angleSetupData):
        self.antennaType = 0
        self.diagType = ''
        self.nofAnglePoints = 0
        self.angleStepSize = 0
        self.refAnglePoint = 0
        self.angleSetupStr = ''
        self.setAngle(angleSetupData)
        self.setStr()

    def setStr(self):
        self.angleSetupStr = 'NofPts=' + str(self.nofAnglePoints) + '_StepSize=' + str(self.angleStepSize) + '_RefPt=' + str(self.refAnglePoint)

    def setAngle(self, angleSetupData):
        self.antennaType = angleSetupData["antType"]
        self.diagType = angleSetupData["diagType"]
        self.nofAnglePoints = angleSetupData["nofAnglePoints"]
        self.angleStepSize = angleSetupData["angleStepSize"]
        self.refAnglePoint = angleSetupData["refAnglePoint"]


def setAngleSetupList(ptu2InputConf, parseDataList):
    angSetupCombDictList = getAppearingAngleSetupComb(parseDataList)
    angSetupCombDictList1 = []
    withDiagTypeList = []
    withoutDiagTypeList = []
    angSetupCombList = []

    for i in range(len(angSetupCombDictList)):
        if angSetupCombDictList[i]["diagType"] == 'Az' or angSetupCombDictList[i]["diagType"] == 'El':
            withDiagTypeList.append(angSetupCombDictList[i])

    for i in range(len(angSetupCombDictList)):
        if angSetupCombDictList[i]["diagType"] == 'NoDiagType':
            withoutDiagTypeList.append(angSetupCombDictList[i])

    dtInfoStr = ''
    if ptu2InputConf['diagTypeInfo'] == 1:
        angSetupCombDictList1 = withDiagTypeList.copy()
        dtInfoStr = 'WITH Diagram Type Info'
    else:
        angSetupCombDictList1 = withoutDiagTypeList.copy()
        dtInfoStr = 'WITHOUT Diagram Type Info'

    if len(angSetupCombDictList1) == 0:
        myLogger.error('No data for ' + dtInfoStr + ' found.')
    else:
        for angSetupIdx in range(len(angSetupCombDictList1)):
            myLogger.info('Angle setup comb. added: ' + 'AntType-' + str(angSetupCombDictList1[angSetupIdx]["antType"]) + '_DiagType=' + angSetupCombDictList1[angSetupIdx]["diagType"] + '_NofPts=' + str(angSetupCombDictList1[angSetupIdx]["nofAnglePoints"]) + '_StepSize=' + str(angSetupCombDictList1[angSetupIdx]["angleStepSize"]) + '_RefPt=' + str(angSetupCombDictList1[angSetupIdx]["refAnglePoint"]) + '.')
            angSetupComb = AngleSetup(angSetupCombDictList1[angSetupIdx])
            angSetupCombList.append(angSetupComb)

    return angSetupCombList


def getAngleStep(parseData):
    angle = calc.getPtuAngVals(parseData)
    medianList = []
    for i in range(1, 5):
        firstPoint = round(angle[i - 1], 1)
        lastPoint = round(angle[i], 1)
        step = abs(firstPoint - lastPoint)
        medianList.append(step)
    median = np.median(medianList)
    return median


def getNofAnglePoints(parseData):
    length = len(calc.getPtuAngVals(parseData))
    return length


def getRefAnglePoint(parseData):
    angle = calc.getPtuAngVals(parseData)
    refAnglePoint = round(angle[0], 1)
    return refAnglePoint


def getAppearingAngleSetupComb(parseDataList):
    combDictList = []
    outputList = []
    myLogger.info('Getting angle setup list:')

    for pdIdx in range(len(parseDataList)):
        combDict = dict()
        step = getAngleStep(parseDataList[pdIdx])
        nofAnglePoints = getNofAnglePoints(parseDataList[pdIdx])
        refAnglePoint = getRefAnglePoint(parseDataList[pdIdx])
        antennaType = parseDataList[pdIdx].antennaInfo.antennaType

        if parseDataList[pdIdx].measSetupInfo.antennaDiagramTypeFound == 1:
            diagType = parseDataList[pdIdx].measSetupInfo.antennaDiagramType
        else:
            diagType = 'NoDiagType'

        combDict.update({"antType": antennaType, "diagType": diagType, "nofAnglePoints": nofAnglePoints, "angleStepSize": step, "refAnglePoint": refAnglePoint})
        combDictList.append(combDict)

    for pdIdx in range(len(combDictList)):
        if pdIdx == 0:
            outputList.append(combDictList[pdIdx])
        isDifferentList = []
        for outputIdx in range(len(outputList)):
            isDifferent = 0
            if outputList[outputIdx]["antType"] != combDictList[pdIdx]["antType"] \
                    or outputList[outputIdx]["diagType"] != combDictList[pdIdx]["diagType"] \
                    or outputList[outputIdx]["nofAnglePoints"] != combDictList[pdIdx]["nofAnglePoints"] \
                    or outputList[outputIdx]["angleStepSize"] != combDictList[pdIdx]["angleStepSize"] \
                    or abs(outputList[outputIdx]["refAnglePoint"] - combDictList[pdIdx]["refAnglePoint"]) >= 0.1:
                isDifferent = 1
            isDifferentList.append(isDifferent)

        found = 1
        for difIdx in range(len(isDifferentList)):
            if isDifferentList[difIdx] == 0:
                found = 0
                break

        if found == 1:
            outputList.append(combDictList[pdIdx])

    return outputList


def getAntennaTypesList(parseDataList):
    antennaType = 0
    antennaTypeList = []

    for listIdx in range(len(parseDataList)):
        if parseDataList[listIdx].antennaInfo.antennaType != antennaType:
            antennaType = parseDataList[listIdx].antennaInfo.antennaType
            antennaTypeList.append(parseDataList[listIdx].antennaInfo.antennaType)

    antTypeSet = set(antennaTypeList)
    outputList = list(antTypeSet)
    return outputList


def getPtu2ListPerAntennaType(antType, parseDataList):
    outputList = []
    for listIdx in range(len(parseDataList)):
        if parseDataList[listIdx].antennaInfo.antennaType == antType:
            outputList.append(parseDataList[listIdx])
    return outputList


def getValidChirpList(chirpSetup, parseDataList, pdIdx):
    chirpList = getConfChirpList(chirpSetup)
    validChirpList = []
    for chirpIdx in range(len(chirpList)):
        if parseDataList[pdIdx].chirpInfoList[chirpIdx].active == 1:
            validChirpList.append(chirpList[chirpIdx])
    return validChirpList


def getFreqListPerDiagram(chirp, diagNum, parseDataList):
    freqList = []
    for pdIdx in range(len(parseDataList)):
        if parseDataList[pdIdx].fileTitle.diagramFound == 1:
            if parseDataList[pdIdx].fileTitle.diagram == diagNum:
                if parseDataList[pdIdx].chirpInfoList[chirp].active == 1:
                    freqList.append(parseDataList[pdIdx].chirpInfoList[chirp].centerFrequency)
    return freqList


def getFreqList(chirp, diagramList, parseDataList):
    freqList = []
    for pdIdx in range(len(parseDataList)):
        for diagIdx in range(len(diagramList)):
            if parseDataList[pdIdx].fileTitle.diagramFound == 1:
                if parseDataList[pdIdx].chirpInfoList[chirp].active == 1:
                    freqList.append(parseDataList[pdIdx].chirpInfoList[chirp].centerFrequency)
    return freqList


def getAvgFreqPerDiagram(chirp, diagNum, parseDataList):
    freqList = getFreqListPerDiagram(chirp, diagNum, parseDataList)
    avgFreq = 0
    if len(freqList) != 0:
        avgFreq = sum(freqList) / len(freqList)
    else:
        myLogger.error("Empty frequency list.")
    return avgFreq


def getMaxFreqPerDiagram(chirp, diagNum, parseDataList):
    freqList = getFreqListPerDiagram(chirp, diagNum, parseDataList)
    maxFreq = 0
    if len(freqList) != 0:
        maxFreq = max(freqList)
    else:
        myLogger.error("Empty frequency list.")
    return maxFreq


def getMinFreqPerDiagram(chirp, diagNum, parseDataList):
    freqList = getFreqListPerDiagram(chirp, diagNum, parseDataList)
    minFreq = 0
    if len(freqList) != 0:
        minFreq = min(freqList)
    else:
        myLogger.error("Empty frequency list.")
    return minFreq


def getAvgFreq(chirp, diagramList, parseDataList):
    freqList = getFreqList(chirp, diagramList, parseDataList)
    avgFreq = 0
    if len(freqList) != 0:
        avgFreq = sum(freqList) / len(freqList)
    else:
        myLogger.error("Empty frequency list.")
    return avgFreq


def getMaxFreq(chirp, diagramList, parseDataList):
    freqList = getFreqList(chirp, diagramList, parseDataList)
    maxFreq = 0
    if len(freqList) != 0:
        maxFreq = max(freqList)
    else:
        myLogger.error("Empty frequency list.")
    return maxFreq


def getMinFreq(chirp, diagramList, parseDataList):
    freqList = getFreqList(chirp, diagramList, parseDataList)
    minFreq = 0
    if len(freqList) != 0:
        minFreq = min(freqList)
    else:
        myLogger.error("Empty frequency list.")
    return minFreq
