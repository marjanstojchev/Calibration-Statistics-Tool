from . import safeparse as sp
from logconfig import logAdapter_PP as log
import yaml
import enum
import codecs
import copy
import re

# log.error('Error')
# log.warning('Warning')
# log.info('info')

class ProtocolType(enum.Enum):
    BurnIn ='BurnIn'
    Calibration = 'Calibration'

class MeasResultEnum(enum.Enum):
    NotUsed = -2
    NotMeasured = -1
    MeasNotOK = 0
    MeasOk = 1
    Invalid = 2

class ProtocolCategoriesEnum(enum.Enum):
    ProtocolHead = 0
    MeasurementLimits = 1
    Measurements = 2
    AbbortCriterions = 3
    MeasurementDurations = 4
    MeasSettings = 5

class ProtocolCategoryNameEnum(enum.Enum):
    MeasurementLimits = 'MeasurmentLimit'
    AbbortCriterions  = 'AbbortCriterions'


class ErrorStatusEnum(enum.Enum):
    Ok = 0
    Error = 1
    Warning = 2
#
# class LimitCategory():
#     def __init__(self):
#         self.limitsList=[]


class ProtocolHeadEnum(enum.Enum):
    PtuOffsets_Az ='PtuOffset: AZ[°]:'
    PtuOffsets_El ='PtuOffset: EL[°]:'
    CalibrationDspSoftwareInfo = 'Calibration DSP softwareinfo:'
    CalibrationDspSoftwareCompileInfo = 'Calibration DSP software Compile Info:'
    ModularSoftware = 'Modular Software:'
    CalStart = 'CalStart:'
    CalEnd   = 'CalEnd:'
    MeasDuration   = 'Duration[s]: '
    MeasDurationV2 = 'DurationV2[s]:'
    RFSerial = 'RF-Serial:'
    BurnInSpeed = 'Burn16a_BurnInMeasSpeedList[km/h]'
    BurnInAzi   = 'Burn16c_BurnInMeasPtuPosAzimuthList[°]'
    BurnInEle   = 'Burn16d_BurnInPtuPosElevationList[°]'


class ProtocolHeadElement:
    def __init__(self,name):
        self.name   = name
        self.lineNr = 0
        self.nameFound = 0
        self.errorStatus = ErrorStatusEnum.Ok
        self.valuesList  = []

class ProtocolHeadElementValue:
    def __init__(self,name):
        self.name  = name
        self.value = ''

        self.nameFound  = 0
        self.valueFound = 0

class MeasurementEnum(enum.Enum):
    TxAntRawFrequencyTable_Measpoints = 0
    TxAntPowerCorrCurve = 2
    TxAntCtapRawFreqSelectSearch = 1

class MeasurementDurationsEnum(enum.Enum):
    TxAnt = 'TxAnt[1]'
    Frequency_MHz = 'Freq[MHz]'
    Level_dB = 'Level[dB]'
    Level_Powermeter_dB = 'Level-Powermeter[dB]'

class MeasurementDuration():
    def __init__(self):
        self.name = ''
        self.nameFound = 0

        self.value = 0
        self.valueFound = 0

        self.start = ''
        self.end   = ''
        self.startFound = 0
        self.endFound = 0

        self.errorStatus = ErrorStatusEnum.Ok

class MeasSetting():
    def __init__(self):
        self.name = ''
        self.nameFound = 0

        self.value = ''
        self.valueFound = 0

        self.comment = ''
        self.commentFound = 0

        self.errorStatus = ErrorStatusEnum.Ok

NOF_TX_ANT = 3
MeasurementType3aDict = dict()
MeasurementType3bDict = dict()
MeasurementType3eDict = dict()
TxAntPowerCorrCurveDict   = dict()
BasicMeasurementParamDict = dict()

for txAnt in range (NOF_TX_ANT):
    extraString = ''
    strAddString  = 'TxAnt' + str(txAnt)
    strAddString2 = 'Tx' + str(txAnt)

    basicString = '(3a) ' + strAddString + ' raw frequency table -  measpoints'
    possibleNames  = [ '(3a) ' + extraString + 'raw frequency table -  measpoints' ]
    possibleNames += ['(3a)' + strAddString]
    possibleNames += ['(3a)' + extraString]
    possibleNames += ['(3a' + strAddString2 + ')']
    MeasurementType3aDict[basicString] = possibleNames

    basicString = '(3e) ' + strAddString + ' TxPowerCorrCurve'
    possibleNames  = [ '(3e) ' + strAddString + 'TxPowerCorrCurve']
    possibleNames += ['(3e)' + strAddString]
    possibleNames += ['(3e)' + extraString]
    possibleNames += ['(3e' + strAddString2 + ')']
    MeasurementType3eDict[basicString] = possibleNames

    basicString = '(3b) ' + strAddString + ' ctap raw freq select search'
    possibleNames  = [ '(3b) ' + strAddString + 'ctap raw freq select search']
    possibleNames += ['(3b)' + strAddString]
    possibleNames += ['(3b)' + extraString]
    possibleNames += ['(3b' + strAddString2 + ')']
    MeasurementType3bDict[basicString] = possibleNames

class BasicMeasurementParamEnum(enum.Enum):
    TxAnt = 'TxAnt[1]'
    Frequency_MHz = 'Freq[MHz]'
    Level_dB = 'Level[dB]'
    Level_Powermeter_dB = 'Level-Powermeter[dB]'
    FreqSensorSetting   = 'FreqSensorSetting[MHz]'
    RawFreqSel = 'raw freq sel[1]'
    DAC = 'DAC[dac] '
    TIME_ms  = 'Time[ms] '
    TXPowVal = 'tx_pow_val'
    Number = 'Number [1]'
    CenterFrequency_MHz = 'Centerfreq [Mhz]'
    Span_MHz = 'Span [MHz]'
    LevelMeasSpec_dB = 'Level meas (Spec)[dB]'
    LevelMeasPowermeter_dB = 'Level meas (Powermeter)[dB]'

BasicMeasurementParamDict[BasicMeasurementParamEnum.TxAnt] = [BasicMeasurementParamEnum.TxAnt.value]
BasicMeasurementParamDict[BasicMeasurementParamEnum.Frequency_MHz] = [BasicMeasurementParamEnum.Frequency_MHz.value]
BasicMeasurementParamDict[BasicMeasurementParamEnum.Level_dB] = [BasicMeasurementParamEnum.Level_dB.value]
BasicMeasurementParamDict[BasicMeasurementParamEnum.Level_Powermeter_dB] = [BasicMeasurementParamEnum.Level_Powermeter_dB.value]

BasicMeasurementParamDict[BasicMeasurementParamEnum.FreqSensorSetting] = [BasicMeasurementParamEnum.FreqSensorSetting.value]

BasicMeasurementParamDict[BasicMeasurementParamEnum.RawFreqSel] = [BasicMeasurementParamEnum.RawFreqSel.value]
BasicMeasurementParamDict[BasicMeasurementParamEnum.DAC] = [BasicMeasurementParamEnum.DAC.value]

BasicMeasurementParamDict[BasicMeasurementParamEnum.TIME_ms]  = [BasicMeasurementParamEnum.TIME_ms.value]
BasicMeasurementParamDict[BasicMeasurementParamEnum.TXPowVal] = [BasicMeasurementParamEnum.TXPowVal.value,'tx_power_val[1]']

BasicMeasurementParamDict[BasicMeasurementParamEnum.Number] = [BasicMeasurementParamEnum.Number.value]
BasicMeasurementParamDict[BasicMeasurementParamEnum.CenterFrequency_MHz] = [BasicMeasurementParamEnum.CenterFrequency_MHz.value]
BasicMeasurementParamDict[BasicMeasurementParamEnum.Span_MHz] = [BasicMeasurementParamEnum.Span_MHz.value]
BasicMeasurementParamDict[BasicMeasurementParamEnum.LevelMeasSpec_dB] = [BasicMeasurementParamEnum.LevelMeasSpec_dB.value]
BasicMeasurementParamDict[BasicMeasurementParamEnum.LevelMeasPowermeter_dB] = [BasicMeasurementParamEnum.LevelMeasPowermeter_dB.value]

BasicMeasurementParamListBasicVariant = [BasicMeasurementParamEnum.TxAnt,BasicMeasurementParamEnum.Frequency_MHz,BasicMeasurementParamEnum.Level_dB,BasicMeasurementParamEnum.Level_Powermeter_dB,
                                       BasicMeasurementParamEnum.FreqSensorSetting,
                                       BasicMeasurementParamEnum.TIME_ms, BasicMeasurementParamEnum.TXPowVal,BasicMeasurementParamEnum.Number,
                                       BasicMeasurementParamEnum.CenterFrequency_MHz,BasicMeasurementParamEnum.Span_MHz, BasicMeasurementParamEnum.LevelMeasSpec_dB,BasicMeasurementParamEnum.LevelMeasPowermeter_dB]

BasicMeasurementParamListExtendedVariant = [BasicMeasurementParamEnum.TxAnt,BasicMeasurementParamEnum.Frequency_MHz,BasicMeasurementParamEnum.Level_dB,BasicMeasurementParamEnum.Level_Powermeter_dB,
                                       BasicMeasurementParamEnum.RawFreqSel,BasicMeasurementParamEnum.DAC,
                                       BasicMeasurementParamEnum.TIME_ms, BasicMeasurementParamEnum.TXPowVal,BasicMeasurementParamEnum.Number,
                                       BasicMeasurementParamEnum.CenterFrequency_MHz,BasicMeasurementParamEnum.Span_MHz, BasicMeasurementParamEnum.LevelMeasSpec_dB,BasicMeasurementParamEnum.LevelMeasPowermeter_dB]
class BasicMeasurementParamSearchEnum(enum.Enum):
    RightAfterMeasTypeTitle = 0
    AfterOtherParams = 1
    NotAtAll = 2
    AfterOtherParamsNoHeader = 3

class TxAntPowerCorrCurveEnum(enum.Enum):
    PowermeterLevelValuesUsed   = 'PowermeterLevelValuesUsed:'
    PowermeterLevelRecalcActive = 'PowermeterLevelRecalcActive:'
    PowermeterLevelCorrMethod   = 'PowermeterLevelCorrMethod:'

TxAntPowerCorrCurvePLVU_PossibleNames = [TxAntPowerCorrCurveEnum.PowermeterLevelValuesUsed.value,'PLVU:']
TxAntPowerCorrCurveDict[TxAntPowerCorrCurveEnum.PowermeterLevelValuesUsed] = TxAntPowerCorrCurvePLVU_PossibleNames

TxAntPowerCorrCurvePLRA_PossibleNames = [TxAntPowerCorrCurveEnum.PowermeterLevelRecalcActive.value,'PLRA:']
TxAntPowerCorrCurveDict[TxAntPowerCorrCurveEnum.PowermeterLevelRecalcActive] = TxAntPowerCorrCurvePLRA_PossibleNames

TxAntPowerCorrCurvePLCM_PossibleNames = [TxAntPowerCorrCurveEnum.PowermeterLevelCorrMethod.value,'PLCM:']
TxAntPowerCorrCurveDict[TxAntPowerCorrCurveEnum.PowermeterLevelCorrMethod] = TxAntPowerCorrCurvePLCM_PossibleNames

class MeasurementType():
    def __init__(self,name,possibleNames,type):
        self.name = name
        self.nameFound = 0
        self.parameterMeasurementValueDict = dict()
        self.errorStatus = ErrorStatusEnum.Ok
        self.bassicParamNamesFound = 0
        self.noHeaderProcessed = 0
        self.type = type
        self.possibleNames = possibleNames

        for basicString, possibleNames in MeasurementType3aDict.items():
            if self.name==basicString or self.name in possibleNames:
                for parameter in BasicMeasurementParamEnum:
                    for  basicMeasurementParaBasicName,  basicMeasurementParaPossibleNames in BasicMeasurementParamDict.items():
                        if parameter==basicMeasurementParaBasicName:

                            self.parameterMeasurementValueDict[parameter] = MeasurementValue(parameter,basicMeasurementParaPossibleNames)

        for basicString, possibleNames in MeasurementType3bDict.items():
            if self.name==basicString or self.name in possibleNames:
                for parameter in BasicMeasurementParamEnum:
                    for  basicMeasurementParaBasicName,  basicMeasurementParaPossibleNames in BasicMeasurementParamDict.items():
                        if parameter==basicMeasurementParaBasicName:

                            self.parameterMeasurementValueDict[parameter] = MeasurementValue(parameter,basicMeasurementParaPossibleNames)

        for basicString, possibleNames in MeasurementType3eDict.items():
            if self.name==basicString or self.name in possibleNames:
                for parameter in BasicMeasurementParamEnum:
                    for  basicMeasurementParaBasicName,  basicMeasurementParaPossibleNames in BasicMeasurementParamDict.items():
                        if parameter==basicMeasurementParaBasicName:

                            self.parameterMeasurementValueDict[parameter] = MeasurementValue(parameter,basicMeasurementParaPossibleNames)

        if self.type==MeasurementEnum.TxAntPowerCorrCurve:
            for parameter in TxAntPowerCorrCurveEnum:
                for txAntPowerCorrCurveBasicName, txAntPowerCorrCurvePossibleNames in TxAntPowerCorrCurveDict.items():
                    if parameter==txAntPowerCorrCurveBasicName:
                        self.parameterMeasurementValueDict[parameter]=MeasurementValue(parameter,txAntPowerCorrCurvePossibleNames)


    def searchPatternInPossibleNames(self,pattern,possibleNames):
        status = False
        for item in possibleNames:
            if pattern in item:
                status = True
        return  status

    def searchBasicParamNamesWithoutHeader(self,lineNr):
        order = 0

        for listItem in BasicMeasurementParamListBasicVariant:
            for paramKey, paramValue in self.parameterMeasurementValueDict.items():
                if listItem.value in paramValue.possibleNames:

                    paramValue.nameFound = 1
                    paramValue.lineNr = lineNr
                    paramValue.order  = order

                    self.bassicParamNamesFound = 1
            order += 1


        for paramKey, paramValue in self.parameterMeasurementValueDict.items():
            if paramValue.nameFound!=1:
                if paramValue.name.value==BasicMeasurementParamEnum.TxAnt.value or paramValue.name.value==BasicMeasurementParamEnum.Frequency_MHz.value or paramValue.name.value==BasicMeasurementParamEnum.Level_dB.value:
                    log.error('XMeasurements, measurements type: ' + self.name + ', parameter name not found: ' + paramKey.value + ', line ' + str(lineNr))
                    paramValue.errorStatus = ErrorStatusEnum.Error
                else:
                    log.warning('XMeasurements, measurements type: ' + self.name + ', parameter name not found: ' + paramKey.value + ', line ' + str(lineNr))
                    paramValue.errorStatus = ErrorStatusEnum.Ok
    #
    # def checkPossibleNames(self, name):
    #     for listItem in BasicMeasurementParamDict.items():
    #

    def searchBasicParamNames(self,line,lineNr):

        lineList = line.split(';')

        order = 0
        for lineItem in lineList:
            for paramKey, paramValue in self.parameterMeasurementValueDict.items():
                # if paramKey.value==lineItem:
                if lineItem in paramValue.possibleNames:

                    paramValue.nameFound = 1
                    paramValue.lineNr = lineNr
                    paramValue.order = order

                    self.bassicParamNamesFound = 1
            order += 1

        for paramKey, paramValue in self.parameterMeasurementValueDict.items():
            if paramValue.nameFound!=1:
                if paramValue.name.value ==BasicMeasurementParamEnum.TxAnt.value or paramValue.name.value ==BasicMeasurementParamEnum.Frequency_MHz.value or paramValue.name.value== BasicMeasurementParamEnum.Level_dB.value:
                    log.error('Measurements, measurements type: ' + self.name + ', parameter name not found: ' + paramKey.value + ', line ' + str(lineNr))
                    paramValue.errorStatus = ErrorStatusEnum.Error
                else:
                    log.warning('Measurements, measurements type: ' + self.name+ ', parameter name not found: ' + paramKey.value + ', line ' + str(lineNr))
                    paramValue.errorStatus = ErrorStatusEnum.Ok

    def parseBasicParamNames(self,lineList,lineNr):

        for paramKey, paramValue in self.parameterMeasurementValueDict.items():
            for lineIdx in range(len(lineList)):
                if lineIdx==paramValue.order:

                    if paramValue.name==BasicMeasurementParamEnum.TxAnt:
                        if sp.checkInt(lineList[lineIdx]):
                            paramValue.values.append(int(lineList[lineIdx]))
                        else:
                            paramValue.valuesFound = 0
                            paramValue.errorStatus = ErrorStatusEnum.Error
                            log.warning('Measurements, parsing to int failed, measurements type: ' + self.name + ', parameter: ' + paramKey.value + ', line ' + str(lineNr))
                    else:
                        if sp.checkDecimal(lineList[lineIdx]):
                            paramValue.valuesFound = 1
                            paramValue.values.append(float(lineList[lineIdx]))
                        else:
                            paramValue.valuesFound = 0
                            paramValue.errorStatus = ErrorStatusEnum.Error
                            log.warning('Measurements, parsing to float failed, measurements type: ' + self.name + ', parameter: ' + paramKey.value + ', line ' + str(lineNr))

class MeasurementValue():
    def __init__(self,name,possibleNames = []):
        self.name = name
        self.nameFound = 0

        self.actualName = ''

        self.possibleNames = []
        self.possibleNames = possibleNames

        self.lineNr = 0
        self.order  = -1

        self.values = []
        self.valuesFound = 0

        self.errorStatus = ErrorStatusEnum.Ok

class Limit():
    def __init__(self):
        self.name  = ''
        self.value = 0.0
        self.min = 0.0
        self.max = 0.0
        self.measResult = MeasResultEnum.Invalid
        self.comment = ''

        self.possibleNamesList = []

        self.category = ''
        self.catFound = 0

        self.errorStatus = ErrorStatusEnum.Ok

        self.limitFound = 0
        self.minFound   = 0
        self.maxFound   = 0
        self.valueFound = 0
        self.measResultStringFound = 0
        self.measResultFound = 0
        self.commentFound = 0




class AbbortCriterion():
    def __init__(self):
        self.id = 0
        self.name = ''
        self.values = []
        self.statusCode = ''

        self.errorStatus = ErrorStatusEnum.Ok

        self.valuesFound = 0
        self.statusCodeFound = 0
        self.numberFound = 0
        self.nameFound = 0

class AbbortCriterions():
    def __init__(self):
        self.abbortCriterionList = []

class MeasurementLimit():
    def __init__(self):
        self.limitsList = []

class ProtocolParseInput():
    def __init__(self):
        self.measurementLimit = MeasurementLimit()
        self.abbortCriterions = AbbortCriterions()

class ParseProtocols():
    def __init__(self,protocolType):
        # log.error('Error')
        # log.warning('Warning')
        # log.info('info')
        self.rawParsedMeasurements = dict()

        for basicString,possibleNames in MeasurementType3aDict.items():
            self.rawParsedMeasurements[basicString] = MeasurementType(basicString,possibleNames,MeasurementEnum.TxAntRawFrequencyTable_Measpoints)

        for basicString,possibleNames in MeasurementType3bDict.items():
            self.rawParsedMeasurements[basicString] = MeasurementType(basicString,possibleNames,MeasurementEnum.TxAntCtapRawFreqSelectSearch)

        for basicString,possibleNames in MeasurementType3eDict.items():
            self.rawParsedMeasurements[basicString] = MeasurementType(basicString,possibleNames, MeasurementEnum.TxAntPowerCorrCurve)

        self.rawParsedMeasurementLimit = MeasurementLimit()
        self.rawParsedAbbortCriterions = AbbortCriterions()
        self.rawParsedProtocolHead = dict()
        self.rawParsedMeasurementDurations = []
        self.rawParsedMeasSettings = []

        for element in ProtocolHeadEnum:
            self.rawParsedProtocolHead[element] = ProtocolHeadElement(element)

        self.protocolParseInputDict = dict()
        # self.rawParsedMeasurementLimitDict = dict()
        self.inputFilteredMeasurementLimitDict = dict()
        self.inputFilteredMeasurementLimit = MeasurementLimit()

        self.extInputMeasurementLimitDict = dict()

        self.protocolType = protocolType
        self.errorList    = []
        self.errorStatus  = ErrorStatusEnum.Ok

    def generateMeasurmentLimitDict(self, measurementLimit, protocolParseInputDict):

        outputDict = dict()

        if len(measurementLimit.limitsList)!=0:

            catList = []
            for limit in measurementLimit.limitsList:
                if limit.catFound==1:
                    catList.append(limit.category)

            tempMeasLimDict = dict()


            catSet   = set(catList)
            catList  = list(catSet)
            if len(catList)!=0:
                for cat in catList:
                    tempLimDict = dict()
                    for limit in measurementLimit.limitsList:
                        if limit.limitFound==1 and limit.catFound and limit.category==cat:

                            limitNameArray = limit.name.split('[')

                            limitName = limitNameArray[0]

                            unit = ''

                            basis  = ''
                            suffix =''

                            if limitName.endswith('rs485') or limitName.endswith('RS485'):
                                basis = limitName
                            else:
                                if len(limitNameArray)!=1:
                                    unit = '[' + limitNameArray[1]

                                match = re.match(r'(.*\D)?(\d*)$', limitName, re.I)

                                res = tuple()
                                if match:
                                    res = match.groups()

                                basis  = res[0]
                                suffix = res[1]


                            if cat in protocolParseInputDict['MeasurmentLimit']:

                                for inputLimitBasis,possibleLimBasisList in  protocolParseInputDict['MeasurmentLimit'][cat].items():

                                    if basis==inputLimitBasis:

                                        tempLimDict[inputLimitBasis] = possibleLimBasisList

                                    elif possibleLimBasisList is not None:
                                        if basis in possibleLimBasisList:
                                            tempLimDict[inputLimitBasis] = possibleLimBasisList
                                            newName = inputLimitBasis + suffix + unit
                                            limit.name = newName

                            else:
                                log.error('Generate MeasurementLimits dict: Limits category not found for inputMeasurmentLimitDict["MeasurmentLimit"], category: '+str(cat))
                                self.errorStatus = ErrorStatusEnum.Error

                    tempMeasLimDict[cat] = tempLimDict
            else:
                log.error('Generate MeasurementLimits dict: No limits category found for MeasurementLimit.')
                self.errorStatus = ErrorStatusEnum.Error

            outputDict = tempMeasLimDict

        else:
            log.error('Generate MeasurementLimits dict: Empty limits list for MeasurementLimit.')
            self.errorStatus = ErrorStatusEnum.Error

        return outputDict, measurementLimit

    def generateMeasurmentLimitDictHeaders(self, measurementLimit, protocolParseInputDict):

        outputDict = dict()
        for headobject,headvalue in measurementLimit.items():
            if len(headvalue.valuesList)!=0:
                for value in headvalue.valuesList:
                    if value.value != '':
                        if 'Burn16' in headobject.value:
                            val = value.value.replace(' ', '')
                            val = val.split('|')
                            for elemIdx in range(len(val)):
                                if sp.checkDecimal(val[elemIdx]):
                                    limitNameSplit = value.name.split('_')
                                    limitNameFilter = limitNameSplit[1].split('[')
                                    outputDict[str(limitNameFilter[0])+str(elemIdx)] = [float(val[elemIdx])]
                        else:
                            outputDict[headobject.value] = [value.value]

            else:
                log.error('Generate MeasurementLimits dict: Empty limits list for MeasurementLimit.')
                self.errorStatus = ErrorStatusEnum.Error

        return outputDict

    def extendInputMeasurementLimitDict(self):

        log.info('Extending '+str(self.protocolType)+' input MeasurementLimit dict.')

        if len(self.rawParsedMeasurementLimit.limitsList)==0:
            log.error('Extend input MeasurementLimit dict: Empty rawParsedMeasurementLimitDict.')
            self.errorStatus = 1
            return

        if len(self.protocolParseInputDict)==0:
            log.error('Extend input MeasurementLimit dict: Empty protocolParseInputDict.')
            self.errorStatus = ErrorStatusEnum.Error
            return

        elif ProtocolCategoryNameEnum.MeasurementLimits.value in self.protocolParseInputDict:
            if self.protocolParseInputDict[ProtocolCategoryNameEnum.MeasurementLimits.value] is None:
                log.error('Extend input MeasurementLimit dict: protocolParseInputDict["MeasurmentLimit"] is None.')
                self.errorStatus = ErrorStatusEnum.Error
                return
            else:

                if len(self.rawParsedMeasurementLimit.limitsList)!=0:
                    rawParsedMeasLimits = self.rawParsedMeasurementLimit
                    inputMeasLimCats    = self.protocolParseInputDict['MeasurmentLimit']

                    catList = []
                    for limit in rawParsedMeasLimits.limitsList:
                        if limit.catFound==1:
                            catList.append(limit.category)

                    # rawParsedMeasLimitsDict = dict()

                    catSet  = set(catList)
                    catList = list(catSet)

                    auxDict = dict()
                    # rawParsedMeasLimitsDict['MeasurmentLimit']=auxDict

                    for limCat in catList:

                        basisDict = dict()

                        for limit in rawParsedMeasLimits.limitsList:

                            if limit.limitFound==1 and limit.catFound==1 and limit.category==limCat:

                                limitNameArray = limit.name.split('[')
                                limitName = limitNameArray[0]

                                basis = ''

                                if limitName.endswith('rs485') or limitName.endswith('RS485'):
                                    basis = limitName
                                else:
                                    match = re.match(r'(.*\D)?(\d*)$', limitName, re.I)

                                    res = tuple()
                                    if match:
                                        res = match.groups()

                                    basis  = res[0]
                                    suffix = res[1]

                                basisDict[basis] = None

                                auxDict[limCat]  = basisDict

                    outputDict = dict()
                    outputTempDict = inputMeasLimCats
                    outputDict['MeasurmentLimit'] = outputTempDict

                    for rawCatKey, rawCatVal in auxDict.items():

                        outputLimDictPerCat = dict()


                        if rawCatKey not in inputMeasLimCats.keys():
                            outputTempDict[rawCatKey] = rawCatVal

                        else:
                            outputLimDictPerCat = inputMeasLimCats[rawCatKey]
                            inputLimDictPerCat  = copy.deepcopy(inputMeasLimCats[rawCatKey])
                            if len(rawCatVal)!=0:
                                for limit in rawCatVal:


                                    if inputLimDictPerCat is not None:

                                        if isinstance(inputLimDictPerCat, dict):

                                            if limit not in inputLimDictPerCat:


                                                found = 0

                                                for basicName, possibleNames in inputLimDictPerCat.items():

                                                    if limit!=basicName:

                                                        if isinstance(possibleNames,list):

                                                            if limit in possibleNames:
                                                                found = 1
                                                if found==0:
                                                    outputLimDictPerCat[limit] = None


                                            outputTempDict[rawCatKey] = outputLimDictPerCat

                                        else:
                                            log.error('Extend input MeasurementLimit dict :protocolParseInputDict["MeasurmentLimit"], category' + str(rawCatKey) + ', is not of a dict type.')
                                            self.errorStatus = ErrorStatusEnum.Error


                                    else:
                                        outputTempDict[rawCatKey] = auxDict[rawCatKey]
                            else:
                                log.warning('Extend input MeasurementLimit dict : rawParsedMeasurementLimitDict, category' + str(rawCatKey) + ', empty limits list.')
                                self.errorStatus =ErrorStatusEnum.Warning
                    self.extInputMeasurementLimitDict = outputDict
        else:
            log.error('Extend input MeasurementLimit dict: "MeasurmentLimit" key not found at protocolParseInputDict .')
            self.errorStatus = ErrorStatusEnum.Error
            return

    def saveProtocolParseInputDictYAML(self, measLimDict, outputPath):
        log.info('Saving '+str(self.protocolType)+' protocol parse input dict YAML.')

        try:

            with codecs.open(outputPath, 'w+', encoding='iso-8859-1')as yaml_file:

                yaml.dump(measLimDict, yaml_file, default_flow_style=False, sort_keys=False, allow_unicode=True, encoding='iso-8859-1')

        except Exception as exception:
            log.error('Save Protocol Parse Dict YAML, exception: ' + str(exception) + '.')
            self.errorStatus = ErrorStatusEnum.Error

    def loadProtocolParseInputDictYAML(self, filePath):
        try:
            # inputLimitDict=dict()

            log.info('Loading ' +str(self.protocolType)+' protocol prescriptions input file: '+filePath+'.' )
            with open(filePath,'r') as inputFile:
                inputDict = yaml.safe_load(inputFile)

                self.loadProtocolParseInputDict(inputDict)


        except Exception as exception:
            log.error('Load Protocol Parse Input YAML, exception: ' + str(exception) + '.')
            self.errorStatus = ErrorStatusEnum.Error

        pass

    def loadProtocolParseInputDict(self, protocolParseInputDict):

        log.info('Loading ' + str(self.protocolType) + ' protocol prescriptions input dict.')

        if protocolParseInputDict==None:
            protocolParseInputDict = dict()
            protocolParseInputDict[ProtocolCategoryNameEnum.MeasurementLimits.value] = dict()
            protocolParseInputDict[ProtocolCategoryNameEnum.AbbortCriterions.value]  = dict()
            self.protocolParseInputDict = protocolParseInputDict


        elif isinstance(protocolParseInputDict, dict):
            if ProtocolCategoryNameEnum.MeasurementLimits.value in protocolParseInputDict:

                if not isinstance(protocolParseInputDict[ProtocolCategoryNameEnum.MeasurementLimits.value], dict):
                    if protocolParseInputDict[ProtocolCategoryNameEnum.MeasurementLimits.value]==None:

                        protocolParseInputDict[ProtocolCategoryNameEnum.MeasurementLimits.value] = dict()
                        self.protocolParseInputDict[ProtocolCategoryNameEnum.MeasurementLimit.value] = protocolParseInputDict[ProtocolCategoryNameEnum.MeasurementLimits.value]
                        x = 0
                    else:

                        log.error('Load Protocol Parse Input dict, MeasurmentLimit is not of a dict type.')
                        self.errorStatus = ErrorStatusEnum.Error

                else:

                    self.protocolParseInputDict[ProtocolCategoryNameEnum.MeasurementLimits.value] = protocolParseInputDict[ProtocolCategoryNameEnum.MeasurementLimits.value]
            else:
                protocolParseInputDict[ProtocolCategoryNameEnum.MeasurementLimits.value] = dict()
                self.protocolParseInputDict[ProtocolCategoryNameEnum.MeasurementLimits.value] = protocolParseInputDict[ProtocolCategoryNameEnum.MeasurementLimits.value]

            ####
            if ProtocolCategoryNameEnum.AbbortCriterions.value in protocolParseInputDict:

                if not isinstance(protocolParseInputDict[ProtocolCategoryNameEnum.AbbortCriterions.value], dict):
                    if protocolParseInputDict[ProtocolCategoryNameEnum.AbbortCriterions.value]==None:

                        protocolParseInputDict[ProtocolCategoryNameEnum.AbbortCriterions.value] = dict()
                        self.protocolParseInputDict[ProtocolCategoryNameEnum, AbbortCriterions.value] = protocolParseInputDict[ProtocolCategoryNameEnum.AbbortCriterions.value]
                        x = 0
                    else:

                        log.error('Load Protocol Parse Input dict, AbbortCriterions is not of a dict type.')
                        self.errorStatus = ErrorStatusEnum.Error

                else:

                    self.protocolParseInputDict[ProtocolCategoryNameEnum.AbbortCriterions.value] = protocolParseInputDict[ProtocolCategoryNameEnum.AbbortCriterions.value]
            else:
                protocolParseInputDict[ProtocolCategoryNameEnum.AbbortCriterions.value] = dict()
                self.protocolParseInputDict[ProtocolCategoryNameEnum.AbbortCriterions.value] = protocolParseInputDict[ProtocolCategoryNameEnum.AbbortCriterions.value]


        else:
            log.error('Load Protocol Parse Input dict, no top-level dict availble.')
            self.errorStatus = ErrorStatusEnum.Error

    def generateInputFilteredMeasurementLimit(self,inputLimitDict):

        log.info('Generate '+str(self.protocolType)+' input-filtered MeasurementLimit.')

        if self.errorStatus==1:
            log.error('Generate input-filtered MeasurementLimit: Invalid input.')
            self.errorStatus = ErrorStatusEnum.Error
            return

        else:
            #
            # self.inputFilteredMeasurementLimitDict=dict()
            # tempDict = dict()
            #
            # self.inputFilteredMeasurementLimitDict['MeasurmentLimit'] = tempDict

            ###
            inputMeasurementLimitDict = inputLimitDict[ProtocolCategoryNameEnum.MeasurementLimits.value]

            validLimitObjList = []

            if len(self.rawParsedMeasurementLimit.limitsList)!=0:

                for limitObj in self.rawParsedMeasurementLimit.limitsList:

                    if limitObj.catFound==1 and limitObj.category in inputMeasurementLimitDict:

                        basisLimNamesDict = dict()
                        basisLimNamesDict = inputMeasurementLimitDict[limitObj.category]

                        if basisLimNamesDict is not None:
                            for key, val in basisLimNamesDict.items():

                                if limitObj.limitFound==1:

                                    limitNameArray = limitObj.name.split('[')

                                    limitName = limitNameArray[0]

                                    basis = ''

                                    if limitName.endswith('rs485') or limitName.endswith('RS485'):
                                        basis = limitName
                                    else:
                                        match = re.match(r'(.*\D)?(\d*)$', limitName, re.I)

                                        res = tuple()
                                        if match:
                                            res = match.groups()


                                        basis  = res[0]
                                        suffix = res[1]


                                    if key==basis :
                                        validLimitObjList.append(limitObj)

                                    else:
                                        possibleNamesList = basisLimNamesDict[key]

                                        if possibleNamesList is not None:
                                            if basis in possibleNamesList:
                                                validLimitObjList.append(limitObj)

                                else:
                                    log.warning('Generate input-filtered MeasurementLimit, limit not found in protocol: ' + str(limitObj.name) + ', category: ' + str(limitObj.category) + '.')
                                    self.errorStatus = ErrorStatusEnum.Warning

                    else:
                        log.warning('Generate input-filtered MeasurementLimit, limit not in input prescribtion data: ' + str(limitObj.name) + ', category: ' + str(limitObj.category) + '.')
                        self.errorStatus = ErrorStatusEnum.Warning

                self.inputFilteredMeasurementLimit.limitsList = validLimitObjList

            else:
                log.error('Generate input-filtered MeasurementLimit: Empty rawParsedMeasurementLimit limitsList.')
                self.errorStatus = ErrorStatusEnum.Error
                return

    def rawParseProtocols(self,protocolCategories, protocolPath):

        log.info('Parsing without prescribed input, ' + str(self.protocolType) + ' protocol file: ' + str(protocolPath))

        # try:
        with open(protocolPath,'r') as protocolFile:

            # log.info('Oppening '+str(self.protocolType)+' protocol file: ' +str(protocolPath))

            content = protocolFile.readlines()

            for protocolCategory in protocolCategories:

                if protocolCategory==ProtocolCategoriesEnum.ProtocolHead:

                    protocolHeadStartFound = 0

                    lineNr = 0
                    for line in content:
                        lineNr += 1
                        line = line.strip()

                        if '(1) protocol head:' in line:
                            protocolHeadStartFound = 1

                        if protocolHeadStartFound ==1 and 'Measurment Durations:' not in line :

                            for key,val in self.rawParsedProtocolHead.items():
                                if key.value in line :

                                    self.rawParsedProtocolHead[key].nameFound = 1
                                    self.rawParsedProtocolHead[key].lineNr = lineNr
                                    if ';' not in line:
                                        if ',' in line:
                                            lineList = line.split(',')

                                            for elem in lineList:
                                                if elem!='':
                                                    subList = elem.split(':',1)

                                                    elementValue = ProtocolHeadElementValue(subList[0])
                                                    elementValue.value = subList[1]
                                                    self.rawParsedProtocolHead[key].valuesList.append(elementValue)

                                        else:
                                            lineList = line.split(key.value)

                                            elementValue = ProtocolHeadElementValue(key)
                                            # elementValue.nameFound=1
                                            elementValue.value = lineList[1]
                                            # elementValue.valueFound = 1

                                            self.rawParsedProtocolHead[key].valuesList.append(elementValue)

                                    else:
                                        lineList = line.split(';')
                                        if key.value ==ProtocolHeadEnum.ModularSoftware.value:
                                            for elem in lineList:
                                                if ProtocolHeadEnum.ModularSoftware.value in elem:
                                                    subList = elem.split(':',1)
                                                    elementValue = ProtocolHeadElementValue(subList[0])
                                                    elementValue.value = subList[1]
                                                    self.rawParsedProtocolHead[key].valuesList.append(elementValue)

                                        else:

                                            for index in range(len(lineList)):
                                                if index %2==0:
                                                    if lineList[index]!='':
                                                        elementValue = ProtocolHeadElementValue(lineList[index])
                                                        self.rawParsedProtocolHead[key].valuesList.append(elementValue)
                                                else:
                                                    self.rawParsedProtocolHead[key].valuesList[len(self.rawParsedProtocolHead[key].valuesList)-1].value = lineList[index]

                    for key,val in self.rawParsedProtocolHead.items():

                        if self.rawParsedProtocolHead[key].nameFound==0:
                            self.rawParsedProtocolHead[key].errorStatus = ErrorStatusEnum.Warning

                            log.warning('Protocol Head, element not found: ' + str(self.rawParsedProtocolHead[key].name) + ', line ' + str(self.rawParsedProtocolHead[key].lineNr))

                        else:

                            # decimal check
                            if key==ProtocolHeadEnum.PtuOffsets_Az or key==ProtocolHeadEnum.PtuOffsets_El  or key==ProtocolHeadEnum.MeasDuration or key==ProtocolHeadEnum.MeasDurationV2:

                                for elementValue in self.rawParsedProtocolHead[key].valuesList:

                                    elementValue.nameFound = 1

                                    if sp.checkDecimal(elementValue.value):
                                        elementValue.valueFound = 1
                                        elementValue.value = float(elementValue.value)
                                    else:
                                        elementValue.valueFound = 0
                                        self.rawParsedProtocolHead[key].errorStatus = ErrorStatusEnum.Error

                                        log.warning('Protocol Head, value could not be parsed to float: ' + str(elementValue.name) +', value '+str(elementValue.value) +', line ' + str(self.rawParsedProtocolHead[key].lineNr))
                            elif key==ProtocolHeadEnum.RFSerial:
                                i = 0
                                for elementValue in self.rawParsedProtocolHead[key].valuesList:
                                    elementValue.nameFound = 1

                                    if i==0:
                                        elementValue.valueFound = 1

                                    elif i==1:
                                        if sp.checkDecimal(elementValue.value):
                                            elementValue.valueFound = 1
                                            elementValue.value = float(elementValue.value)
                                        else:
                                            elementValue.valueFound = 0
                                            self.rawParsedProtocolHead[key].errorStatus = ErrorStatusEnum.Error

                                            log.warning('Protocol Head, value could not be parsed to float: ' + str(elementValue.name) +', value '+str(elementValue.value) +', line ' + str(self.rawParsedProtocolHead[key].lineNr))

                            #string check
                            elif key==ProtocolHeadEnum.CalibrationDspSoftwareInfo or key==ProtocolHeadEnum.CalibrationDspSoftwareCompileInfo or key==ProtocolHeadEnum.CalStart or key==ProtocolHeadEnum.CalEnd:
                                for elementValue in self.rawParsedProtocolHead[key].valuesList:
                                    elementValue.nameFound  = 1
                                    elementValue.valueFound = 1

                            elif key==ProtocolHeadEnum.ModularSoftware:
                                for elementValue in self.rawParsedProtocolHead[key].valuesList:
                                    elementValue.nameFound = 1
                                    if elementValue.value!='':
                                        elementValue.valueFound = 1

                            elif key==ProtocolHeadEnum.BurnInAzi or key==ProtocolHeadEnum.BurnInEle or key==ProtocolHeadEnum.BurnInSpeed:
                                for elementValue in self.rawParsedProtocolHead[key].valuesList:
                                    elementValue.valueFound = 1
                                    elementValue.value = elementValue.value

                if protocolCategory==ProtocolCategoriesEnum.MeasurementDurations:

                    measDurationsStartFound  = 0
                    measDurationsStart1Found = 0
                    lineNr = 0
                    for line in content:
                        lineNr += 1
                        line = line.strip()
                        line = line.replace('\n','')

                        if 'Measurment Durations:' in line:
                            measDurationsStartFound = 1

                        if measDurationsStartFound and '-------' in line:
                            measDurationsStart1Found = 1

                        if measDurationsStartFound==1 and measDurationsStart1Found==1 and '-------' not in line :
                            if line!='':
                                line = line.replace(';','')
                                line = line.strip()
                                lineList = line.split(':',1)
                                measurementDuration = MeasurementDuration()


                                if lineList[0]!='':
                                    measurementDuration.name = lineList[0]
                                    measurementDuration.nameFound = 1
                                else:
                                    measurementDuration.errorStatus = ErrorStatusEnum.Warning
                                    log.warning('Measurement Duration:, Name not found: ' + str(lineList[0]) + ', line ' + str(lineNr))

                                subString = lineList[1]
                                subList   = subString.split('Start:')
                                value     = subList[0].strip()
                                if sp.checkDecimal(value):
                                    measurementDuration.value = float(value)
                                    measurementDuration.valueFound = 1

                                else:
                                    measurementDuration.valueFound  = 0
                                    measurementDuration.errorStatus = ErrorStatusEnum.Warning
                                    log.warning('Measurement Duration:, Value could not be parsed to float: ' + str(value) + ', line ' + str(lineNr))

                                subList1 = subList[1].split('End:')
                                start  = subList1[0].strip()
                                if subList1[0]!='':
                                    measurementDuration.start = start
                                    measurementDuration.startFound = 1

                                else:
                                    measurementDuration.startFound = 0
                                    measurementDuration.errorStatus = ErrorStatusEnum.Warning
                                    log.warning('Measurement Duration, Start not found: ' + str(start) + ', line ' + str(lineNr))

                                end = subList1[1].strip()
                                if end!='':
                                    measurementDuration.end = end
                                    measurementDuration.endFound = 1

                                else:
                                    measurementDuration.endFound = 0
                                    measurementDuration.errorStatus = ErrorStatusEnum.Warning
                                    log.warning('Measurement Duration, End not found: ' + str(end) + ', line ' + str(lineNr))


                                self.rawParsedMeasurementDurations.append(measurementDuration)
                            else:
                                break
                                x=0

                if protocolCategory==ProtocolCategoriesEnum.MeasSettings:

                    measSettingsStartFound  = 0
                    measSettingsStart1Found = 0
                    measSettingsStart2Found = 0
                    lineNr = 0
                    for line in content:
                        lineNr += 1
                        line = line.strip()
                        line = line.replace('\n', '')

                        if 'Meas Settings' in line:
                            measSettingsStartFound = 1

                        if measSettingsStartFound and '-------' in line:
                            measSettingsStart1Found = 1

                        if measSettingsStartFound and measSettingsStart1Found and line=='':
                            measSettingsStart2Found = 1

                        if measSettingsStartFound==1 and measSettingsStart1Found==1 and measSettingsStart2Found==1 and line!='':
                            if '-----' not in line:
                                line = line.strip()
                                lineList = line.split(';')
                                measSetting = MeasSetting()

                                name = lineList[0].strip()
                                if name !='':
                                    measSetting.name = name
                                    measSetting.nameFound =1
                                else:
                                    measurementDuration.errorStatus = ErrorStatusEnum.Warning
                                    log.warning('Measurement Settings, Name not found: ' + str(name) + ', line ' + str(lineNr))

                                value = lineList[1].strip()
                                if value!='':
                                    measSetting.value = value
                                    measSetting.valueFound = 1

                                else:
                                    measSetting.valueFound = 0
                                    measSetting.errorStatus = ErrorStatusEnum.Warning
                                    log.warning('Measurement Settings, Value not found: ' + str(value) + ', line ' + str(lineNr))

                                comment=lineList[2]
                                if comment!='':
                                    measSetting.comment = comment
                                    measSetting.commentFound = 1
                                else:
                                    measSetting.errorStatus = ErrorStatusEnum.Warning
                                    log.warning('Measurement Settings, Comment not found: ' + str(comment) + ', line ' + str(lineNr))

                                self.rawParsedMeasSettings.append(measSetting)
                            else:
                                break


                if  protocolCategory== ProtocolCategoriesEnum.MeasurementLimits:

                        # content=bytearray(protocolFile.read())
                        # charDet = chardet.detect(content)
                        # encoing = charDet['encoding']

                        measLimitsStartFound = 0

                        lineNr=0
                        measurementLimit=MeasurementLimit()
                        for line in content:
                            lineNr+=1
                            line = line.strip()
                            lineList = line.split(';')

                            # # New
                            # if 'Burn16a_BurnInMeasSpeedList[km/h]' in line:
                            #     lineListBurn = lineList[1].replace(' ', '')
                            #     lineListBurn = lineListBurn.split('|')
                            #     for elemIdx in range(len(lineListBurn)):
                            #         BurnIn= BurnInMeas()
                            #         if sp.checkDecimal(lineListBurn[elemIdx]):
                            #             lineList[0] = lineList[0].replace(' ', '')
                            #             BurnIn.name  = str(lineList[0])+str(elemIdx)
                            #             BurnIn.value = lineListBurn[elemIdx]
                            #         measurementLimit.limitsList.append(BurnIn)

                            if '(9) limit values results:' in line:
                                measLimitsStartFound=1

                            elif measLimitsStartFound==1 and len(lineList)!=1 and lineList[0]!='':

                                if len(lineList)<7:
                                    log.warning('Not sufficient elements found for MeasurmentLimit, line '+ str(lineNr))
                                    self.errorStatus=ErrorStatusEnum.Error
                                    break

                                limit = Limit()
                                for elemIdx in range(len(lineList)):
                                    if 'MeasurmentLimit' in lineList[elemIdx]:
                                        measLimitCatList=lineList[elemIdx].split(':')
                                        cat=measLimitCatList[1].strip(' ')
                                        limit.category=cat
                                        limit.catFound=1
                                    elif limit.catFound==1 and limit.limitFound!=1:
                                        limit.name=lineList[elemIdx].strip('=')
                                        limit.limitFound=1
                                    elif limit.catFound==1 and limit.limitFound==1:
                                        if limit.minFound!=1 and limit.maxFound!=1 and limit.valueFound!=1:
                                            lineList[elemIdx].replace(',','.')
                                            if sp.checkDecimal(lineList[elemIdx]):
                                                limit.value=float(lineList[elemIdx])
                                                limit.valueFound=1
                                            else:
                                                log.warning('Value could not be parsed to float: '+str(lineList[elemIdx])+', line '+str(lineNr))
                                                limit.errorStatus=ErrorStatusEnum.Error
                                                limit.value = str(lineList[elemIdx])
                                                break
                                        elif limit.maxFound!=1 and limit.minFound!=1 and limit.valueFound==1:
                                            lineList[elemIdx].replace(',','.')
                                            maxList = lineList[elemIdx].split(':')
                                            maxList[1] = maxList[1].replace(',','.').replace(' ', '')
                                            max = maxList[1]
                                            if sp.checkDecimal(max):

                                                limit.max = float(maxList[1])
                                                limit.maxFound = 1
                                            else:
                                                log.error('Max could not be parsed to float: ' + str(maxList[1]) + ', line ' + str(lineNr))
                                                limit.errorStatus = ErrorStatusEnum.Error
                                                limit.max = str(maxList[1])
                                                break

                                        elif limit.maxFound==1 and limit.minFound!=1 and limit.valueFound==1:
                                            
                                            minList = lineList[elemIdx].split(':')
                                            minList[1] = minList[1].replace(',','.').replace(' ', '')
                                            min = minList[1]
                                            if sp.checkDecimal(min):

                                                limit.min = float(minList[1])
                                                limit.minFound = 1
                                            else:
                                                log.warning('Min could not be parsed to float: ' + str(
                                                    minList[1]) + ', line ' + str(lineNr))
                                                limit.errorStatus = ErrorStatusEnum.Error
                                                limit.min = str(minList[1])
                                                break

                                        # elif limit.minFound==1 and limit.maxFound==1 and limit.valueFound==1 and 'MeasResult' in lineList[elemIdx]:
                                        elif limit.minFound==1 and limit.maxFound==1 and limit.valueFound==1 and 'MeasResultMeasOk' in lineList[elemIdx]:
                                            limit.measResultStringFound = 1
                                        elif limit.minFound==1 and limit.maxFound==1 and limit.valueFound==1 and limit.measResultStringFound==1 and limit.measResultFound!=1 and limit.commentFound!=1:
                                            lineList[elemIdx].replace(',','.')
                                            if sp.checkInt(lineList[elemIdx]):
                                                measResult=int(lineList[elemIdx])
                                                limit.measResult=MeasResultEnum(measResult)
                                                limit.measResultFound=1
                                            else:
                                                log.warning('MeasResult could not be parsed to int: ' + str(lineList[elemIdx]) + ', line ' + str(lineNr))
                                                limit.errorStatus = ErrorStatusEnum.Error
                                                limit.measResult=str(lineList[elemIdx])
                                                break
                                        elif limit.minFound==1 and limit.maxFound==1 and limit.valueFound==1 and limit.measResultStringFound==1 and limit.measResultFound==1 and limit.commentFound!=1:
                                            if lineList[elemIdx]!='':
                                                limit.commentFound=1
                                                limit.comment=lineList[elemIdx]
                                        elif  limit.minFound==1 and limit.maxFound==1 and limit.valueFound==1 and limit.measResultStringFound==1 and limit.measResultFound==1 and limit.commentFound==1:
                                            if lineList[elemIdx]!='':
                                                limit.errorStatus=ErrorStatusEnum.Warning
                                                log.warning('Extra argument found: ' + str(lineList[elemIdx]) + ', line ' + str(lineNr))
                                            break

                                measurementLimit.limitsList.append(limit)
                                self.rawParsedMeasurementLimit=measurementLimit

                            elif measLimitsStartFound==1 and len(lineList)==1 and lineList[0]=='':
                                break

                elif protocolCategory==ProtocolCategoriesEnum.Measurements:


                    bassicParamNamesFound = 0
                    basicParamNamesSearch = 0

                    for measTypeKey, measTypeVal in self.rawParsedMeasurements.items():

                        if measTypeVal.type==MeasurementEnum.TxAntPowerCorrCurve:
                            basicParamNamesSearch = BasicMeasurementParamSearchEnum.AfterOtherParams
                        elif measTypeVal.type==MeasurementEnum.TxAntRawFrequencyTable_Measpoints or measTypeKey==MeasurementEnum.TxAntCtapRawFreqSelectSearch:
                            basicParamNamesSearch = BasicMeasurementParamSearchEnum.RightAfterMeasTypeTitle

                        lineNr = 0
                        for line in content:
                            lineNr += 1
                            line = line.strip()

                            if measTypeVal.name==line or line in measTypeVal.possibleNames:
                                measTypeVal.actualName=line
                                measTypeVal.nameFound=1
                            elif measTypeVal.nameFound==1 and basicParamNamesSearch ==BasicMeasurementParamSearchEnum.AfterOtherParams:

                                if measTypeVal.type ==MeasurementEnum.TxAntPowerCorrCurve:

                                    lineList = line.split(';')

                                    if lineList[0]in TxAntPowerCorrCurvePLVU_PossibleNames:
                                        measTypeVal.parameterMeasurementValueDict[TxAntPowerCorrCurveEnum.PowermeterLevelValuesUsed].nameFound = 1
                                        if sp.checkInt(lineList[1]):
                                            measTypeVal.parameterMeasurementValueDict[TxAntPowerCorrCurveEnum.PowermeterLevelValuesUsed].valuesFound=1
                                            measTypeVal.parameterMeasurementValueDict[TxAntPowerCorrCurveEnum.PowermeterLevelValuesUsed].values.append(int(lineList[1]))
                                        else:
                                            measTypeVal.parameterMeasurementValueDict[TxAntPowerCorrCurveEnum.PowermeterLevelValuesUsed].errorStatus=ErrorStatusEnum.Error
                                            log.warning('Measurements, parsing to int failed, measurements type: ' + measTypeKey + ', parameter: ' + TxAntPowerCorrCurveEnum.PowermeterLevelValuesUsed.value + ', line ' + str(lineNr))

                                    elif lineList[0] in TxAntPowerCorrCurvePLRA_PossibleNames:
                                        measTypeVal.parameterMeasurementValueDict[TxAntPowerCorrCurveEnum.PowermeterLevelRecalcActive].nameFound =1
                                        if sp.checkInt(lineList[1]):
                                            measTypeVal.parameterMeasurementValueDict[TxAntPowerCorrCurveEnum.PowermeterLevelRecalcActive].valuesFound = 1
                                            measTypeVal.parameterMeasurementValueDict[TxAntPowerCorrCurveEnum.PowermeterLevelRecalcActive].values.append(int(lineList[1]))
                                        else:
                                            measTypeVal.parameterMeasurementValueDict[TxAntPowerCorrCurveEnum.PowermeterLevelRecalcActive].errorStatus = ErrorStatusEnum.Error
                                            log.warning('Measurements, parsing to int failed, measurements type: ' + measTypeKey + ', parameter: ' + TxAntPowerCorrCurveEnum.PowermeterLevelRecalcActive.value + ', line ' + str(lineNr))

                                    elif lineList[0] in  TxAntPowerCorrCurvePLCM_PossibleNames:
                                        measTypeVal.parameterMeasurementValueDict[TxAntPowerCorrCurveEnum.PowermeterLevelCorrMethod].nameFound=1
                                        if sp.checkInt(lineList[1]):
                                            measTypeVal.parameterMeasurementValueDict[TxAntPowerCorrCurveEnum.PowermeterLevelCorrMethod].valuesFound = 1
                                            measTypeVal.parameterMeasurementValueDict[TxAntPowerCorrCurveEnum.PowermeterLevelCorrMethod].values.append(int(lineList[1]))
                                        else:
                                            measTypeVal.parameterMeasurementValueDict[TxAntPowerCorrCurveEnum.PowermeterLevelCorrMethod].errorStatus = ErrorStatusEnum.Error
                                            log.warning('Measurements, parsing to int failed, measurements type: ' + measTypeKey + ', parameter: ' + TxAntPowerCorrCurveEnum.PowermeterLevelCorrMethod.value + ', line ' + str(lineNr))

                                        if lineList[2]!='':
                                            measTypeVal.parameterMeasurementValueDict[TxAntPowerCorrCurveEnum.PowermeterLevelCorrMethod].values.append(lineList[2])
                                        else:
                                            measTypeVal.parameterMeasurementValueDict[TxAntPowerCorrCurveEnum.PowermeterLevelCorrMethod].valuesFound = 0
                                            measTypeVal.parameterMeasurementValueDict[TxAntPowerCorrCurveEnum.PowermeterLevelCorrMethod].errorStatus = ErrorStatusEnum.Error
                                            log.warning('Measurements, measurements type: ' + measTypeKey + ', parameter value not found: ' + TxAntPowerCorrCurveEnum.PowermeterLevelCorrMethod.value + ', line ' + str(lineNr))

                                        if '3eTx' in measTypeVal.actualName:
                                            measTypeVal.searchBasicParamNamesWithoutHeader(lineNr)

                                    elif measTypeVal.bassicParamNamesFound==0:
                                        # if measTypeVal.searchPatternInPossibleNames('3eTx', measTypeVal.possibleNames):
                                        #     measTypeVal.searchBasicParamNamesWithoutHeader(lineNr)
                                        # else:
                                        measTypeVal.searchBasicParamNames(line,lineNr)

                                    elif measTypeVal.bassicParamNamesFound==1:

                                        lineList = line.split(';')

                                        if len(lineList)==1 and lineList[0]=='':
                                            break
                                        else:
                                           measTypeVal.parseBasicParamNames(lineList, lineNr)


                            elif measTypeVal.nameFound==1 and basicParamNamesSearch==BasicMeasurementParamSearchEnum.RightAfterMeasTypeTitle:
                                if '3aTx' in measTypeVal.actualName and measTypeVal.bassicParamNamesFound==0:
                                    measTypeVal.searchBasicParamNamesWithoutHeader(lineNr)
                                    # measTypeVal.noHeaderProcesed =1
                                if measTypeVal.bassicParamNamesFound==0:
                                    # if measTypeVal.searchPatternInPossibleNames('3aTx',measTypeVal.possibleNames):
                                    #     measTypeVal.searchBasicParamNamesWithoutHeader(lineNr)
                                    # else:
                                    measTypeVal.searchBasicParamNames(line, lineNr)

                                elif measTypeVal.bassicParamNamesFound==1:

                                    lineList = line.split(';')

                                    if len(lineList)==1 and lineList[0]=='':
                                        break
                                    else:
                                        measTypeVal.parseBasicParamNames(lineList, lineNr)

                            elif measTypeVal.nameFound==1 and basicParamNamesSearch==BasicMeasurementParamSearchEnum.NotAtAll:
                                break

                    for measTypeKey,measTypeObj in self.rawParsedMeasurements.items():

                        if measTypeObj.nameFound !=1:

                            measTypeObj.errorStatus=ErrorStatusEnum.Warning
                            log.warning('Measurements, name not found, measurements type: ' + measTypeKey + '.')

                        for paramKey, paramObj in measTypeObj.parameterMeasurementValueDict.items():

                            if paramObj.errorStatus==ErrorStatusEnum.Error:
                                measTypeObj.errorStatus = ErrorStatusEnum.Error

                elif protocolCategory ==ProtocolCategoriesEnum.AbbortCriterions:
                    abbortCriterionsStartFound = 0
                    abbortCriterionsString='(10) abort criterions - results:'

                    lineNr = 0
                    abbortCriterions = AbbortCriterions()
                    insufValsHeader = 0

                    for line in content:
                        lineNr += 1
                        line = line.strip()
                        lineList = line.split(';')

                        abbortCriterion = AbbortCriterion()

                        if abbortCriterionsString in line:
                            abbortCriterionsStartFound = 1

                        elif abbortCriterionsStartFound==1 and len(lineList)!=1 and lineList[0]!='':

                            headerLine=1
                            if lineList[0]=='measured values':
                                headerLine =0

                            if headerLine==1:
                                if len(lineList) < 4:
                                    log.warning('Not sufficient elements found for Abbort Criterion header, line '+ str(lineNr))
                                    self.errorStatus=ErrorStatusEnum.Warning
                                    insufValsHeader=1
                                    break
                                else:
                                    abbortCriterion = AbbortCriterion()
                                    if sp.checkInt(lineList[0]):
                                        abbortCriterion.id = int(lineList[0])
                                        abbortCriterion.numberFound=1
                                    else:
                                        log.warning('Abbort Criterion number could not be parsed to int: ' + str(lineList[0]) + ', line ' + str(lineNr))
                                        abbortCriterion.errorStatus=ErrorStatusEnum.Error
                                    if lineList[1]!='':
                                        abbortCriterion.name=lineList[1].strip()
                                        abbortCriterion.nameFound=1
                                    else:
                                        log.warning('Abbort Criterion name not found, line: '+ str(lineNr))
                                        abbortCriterion.errorStatus=ErrorStatusEnum.Error
                                    if lineList[2]!='':
                                        abbortCriterion.statusCode=lineList[2]
                                        abbortCriterion.statusCodeFound=1
                                    else:
                                        log.warning('Abbort Criterion status code not found, line: '+ str(lineNr))
                                        abbortCriterion.errorStatus=ErrorStatusEnum.Error

                                    insufValsHeader = 0
                                    abbortCriterions.abbortCriterionList.append(abbortCriterion)

                            else:
                                if insufValsHeader ==1:
                                    break
                                else:
                                    if len(lineList)<2:
                                        log.warning('Not sufficient elements found for Abbort Criterion measured values, line ' + str(lineNr))
                                        self.errorStatus = ErrorStatusEnum.Error
                                        break
                                    else:
                                        valueList=[]
                                        parseError=0
                                        for valueIdx in range(1, len(lineList)):
                                            if valueIdx !=len(lineList)-1:
                                                if sp.checkDecimal(lineList[valueIdx]):
                                                    value = float(lineList[valueIdx])
                                                    valueList.append(value)
                                                else:
                                                    parseError=1
                                            else:
                                                if lineList[valueIdx]!='':
                                                    self.errorStatus=ErrorStatusEnum.Error
                                                    log.warning('Abbort Criterion values could not be parsed, unexpected character at end: ' + str(lineList[0]) + ', line ' + str(lineNr))

                                        if parseError==1:
                                            log.warning('Abbort Criterion values could not be parsed to float: ' + str(lineList[0]) + ', line ' + str(lineNr))
                                            self.errorStatus = ErrorStatusEnum.Error
                                        else:
                                            abbortCriterions.abbortCriterionList[len(abbortCriterions.abbortCriterionList)-1].valuesFound=1
                                            abbortCriterions.abbortCriterionList[len(abbortCriterions.abbortCriterionList)-1].values=valueList

                    self.rawParsedAbbortCriterions = abbortCriterions

        # except Exception as exception:
        #     log.error('Opening protocol file error: '+str(exception)+'.')
        #     self.errorStatus = ErrorStatusEnum.Error

class ParseInputLimitsGroups:
    def __init__(self):
        self.burnInErrorStatus = 0
        self.calErrorStatus = 0

        self.burnInInputLimitsGroupsDict=dict()
        self.calInputLimitsGroupsDict=dict()

        self.burnInExtInputLimitsGroupsDict = dict()
        self.calExtInputLimitsGroupsDict = dict()

    def loadBurnInInputLimitsGroupsDictYAML(self, filePath):

        self.burnInInputLimitsGroupsDict,self.burnInErrorStatus= self.loadInputLimitsGroupsDictYAML(filePath)

    def loadCalInputLimitsGroupsDictYAML(self, filePath):

        self.calInputLimitsGroupsDict,self.calErrorStatus= self.loadInputLimitsGroupsDictYAML(filePath)

    def loadInputLimitsGroupsDictYAML(self, filePath):
        errorStatus=0
        # try:
            # inputLimitDict=dict()
        with open(filePath,'r') as inputFile:
            inputLimitDict=yaml.safe_load(inputFile)

            if  inputLimitDict==None:
                inputLimitDict=dict()

                # inputLimitDict['BurnIn']=[]
                # inputLimitDict['Calibration'] = []
                # self.inputLimitsGroupsDict = inputLimitDict


            elif isinstance(inputLimitDict,dict):
                for key,val in inputLimitDict.items():
                    if not isinstance(val,dict):
                        log.error('Load Input Limits YAML, Group '+str(val)+' does not contain a nested dict.')
                        errorStatus = 1
                    else:
                        if 'Limits' in val:
                            if not isinstance(val['Limits'], dict):
                                log.error('Load Input Limits YAML, Group ' + str(val) + ', "Limit" key is not of a dict type.')
                                errorStatus = 1
                            else:
                                limitsDict = val['Limits']
                                if 'ExactMatch' not in limitsDict:
                                    limitsDict['ExactMatch']=[]
                                else:
                                    if not isinstance(limitsDict['ExactMatch'],list):
                                        log.error('Load Input Limits YAML, Group ' + str(val) + ', "ExactMatch" is not of a list type.')
                                        errorStatus = 1
                                    else:
                                        inputLimitDict[key]['Limits']['ExactMatch']= limitsDict['ExactMatch']

                                if 'Contains' not in limitsDict:
                                    limitsDict['Contains']=[]
                                else:
                                    if not isinstance(limitsDict['Contains'],list):
                                        log.error('Load Input Limits YAML, Group ' + str(val) + ', "Contains" is not of a list type.')
                                        errorStatus = 1
                                    else:
                                        inputLimitDict[key]['Limits']['Contains']= limitsDict['Contains']
                        else:
                            inputLimitDict[key]['Limits']=dict()
                            inputLimitDict[key]['Limits']['ExactMatch']=[]
                            inputLimitDict[key]['Limits']['Contains'] = []


                ##### ##### #####
                #     if 'BurnIn' in inputLimitDict:
                #
                #         if not isinstance(inputLimitDict['BurnIn'],list):
                #             if inputLimitDict['BurnIn']==None:
                #
                #                 inputLimitDict['BurnIn']=[]
                #
                #             else:
                #
                #                 log.error('Load Input Limits YAML, BurnIn Limits Group is not of a list type.')
                #                 errorStatus=1
                #
                #         else:
                #             self.inputLimitsGroupsDict = inputLimitDict['BurnIn']
                #     else:
                #         inputLimitDict['BurnIn']=[]
                #
                #     if 'Calibration' in inputLimitDict:
                #
                #         if not isinstance(inputLimitDict['Calibration'], list):
                #             if inputLimitDict['Calibration']==None:
                #
                #                 inputLimitDict['Calibration'] = []
                #
                #             else:
                #
                #                 log.error('Load Input Limits YAML, Caliibration Limits Group is not of a list type.')
                #                 errorStatus = 1
                #
                #         else:
                #             self.inputLimitsGroupsDict = inputLimitDict['Calibration']
                #     else:
                #         inputLimitDict['Calibration'] = []
                #
                #     if errorStatus !=1:
                #         self.inputLimitsGroupsDict = inputLimitDict
                #
                # else:
                #     log.error('Load Input Limits YAML, no top-level dict availble.')
                #     errorStatus = 1

        # except Exception as exception:
        #     log.error('Load Input Limits YAML, exception: ' + str(exception) + '.')
        #     errorStatus=1

        return inputLimitDict, errorStatus

    def extendBurnInInputLimitsGroupsDict(self, groupNamesList):
        protType='BurnIn'

        self.burnInExtInputLimitsGroupsDict, self.burnInErrorStatus =self.extendInputLimitsGroupsDict(groupNamesList, self.burnInInputLimitsGroupsDict, protType)

    def extendCalInputLimitsGroupsDict(self, groupNamesList):
        protType='Calibration'

        self.calExtInputLimitsGroupsDict, self.calErrorStatus =self.extendInputLimitsGroupsDict(groupNamesList, self.calInputLimitsGroupsDict, protType)

    def extendInputLimitsGroupsDict(self, groupNamesDictList, inputLimitsGroupsDict, protType):

        errorStatus=0
        protTypeStr='BurnIn'
        if protType !='BurnIn':
            protTypeStr='Calibration'

        if len(groupNamesDictList)==0:
            log.error('Extend input Limits Groups dict: Empty list of '+protTypeStr +' limits group names dicts.')
            errorStatus = 1

        # if len(inputLimitsGroupsDict)==0:
        #     log.error('Extend input Limits Groups dict: Empty '+protTypeStr+' extended input limits groups dict.')
        #     errorStatus=1

        if errorStatus!=1:

            outputDict=dict()
            for key, val in inputLimitsGroupsDict.items():
                outputDict[key] =inputLimitsGroupsDict[key]

            for groupNameDict in groupNamesDictList:

                groupName = groupNameDict['groupName']

                if groupName not in inputLimitsGroupsDict:
                    outputDict[groupName]=dict()

                    auxLimDict=groupNameDict['Limits']

                    outputDict[groupName]['Limits']=auxLimDict

                # else:
                #     outputDict[groupName] =inputLimitsGroupsDict[groupName]


                # outputDict['BurnIn']=inputLimitsGroupsDict['BurnIn']
                #
                # for burnInBasis in burnInBasisList:
                #     if burnInBasis not in self.inputLimitsGroupsDict['BurnIn']:
                #         outputDict['BurnIn'].append(burnInBasis)
                #
                # for calBasis in calBasisList:
                #     if calBasis not in self.inputLimitsGroupsDict['Calibration']:
                #         outputDict['Calibration'].append(calBasis)
                #
            return outputDict, errorStatus

    def saveToActualBurnInLimitsGroupsDict(self, limitsGroup, alreadyExtended):

        limNameDict= self.saveToActualLimitsGroupsDict(limitsGroup)

        if alreadyExtended ==0:
            self.burnInInputLimitsGroupsDict[limitsGroup.name] =limNameDict
        else:
            self.burnInExtInputLimitsGroupsDict[limitsGroup.name] =limNameDict

    def saveToActualCalLimitsGroupsDict(self, limitsGroup, alreadyExtended):

        limNameDict= self.saveToActualLimitsGroupsDict(limitsGroup)

        if alreadyExtended ==0:
            self.calInputLimitsGroupsDict[limitsGroup.name] =limNameDict
        else:
            self.calExtInputLimitsGroupsDict[limitsGroup.name] =limNameDict

    def saveToActualLimitsGroupsDict(self,limitsGroup):

        limNameDict=dict()
        limitsDict = dict()

        containsList = []
        exactMatchList=[]
        for limitRowMatchDict in limitsGroup.limitsRowMatchDictList:

            limitRow=limitRowMatchDict['row']

            if limitRowMatchDict['match']=='ExactMatch':
                exactMatchList.append(limitRow.limitName)
            else:
                containsList.append(limitRow.limitName)


        limitsDict['Contains']=containsList
        limitsDict['ExactMatch']=exactMatchList

        limNameDict['Limits']=limitsDict

        return limNameDict

    def saveLimitsGroupsDictYAML(self, limGroupsDict, outputPath):
        with codecs.open(outputPath, 'w+', encoding='iso-8859-1')as yaml_file:

            yaml.dump(limGroupsDict, yaml_file, default_flow_style=False, sort_keys=False, allow_unicode=True, encoding='iso-8859-1')

def generateInputLimitsFromFile(filePath,limExportPath):
    try:
        with open(filePath, 'r') as protocolFile:

            content = protocolFile.read().replace('\n', '')


            contentList = content.split(';MeasurmentLimit: ')
            del contentList[0]

            pairDictList=[]
            catList=[]
            limList=[]

            for entry in contentList:
                pairDict = dict()

                entryList = entry.split(';')

                category=entryList[0]
                limit =entryList[1]

                limitL = limit.split('[')

                limit = limitL[0]

                limit = limit.replace('=', '')

                basis = ''

                if limit.endswith('rs485') or limit.endswith('RS485'):
                    basis = limit
                else:
                    match = re.match(r'(.*\D)?(\d*)$', limit, re.I)

                    res = tuple()
                    if match:
                        res = match.groups()

                    basis = res[0]
                    suffix = res[1]

                pairDict['limit']=basis
                pairDict['category']=category

                catList.append(category)
                pairDictList.append(pairDict)

                a=0

            catList=set(catList)
            catList=list(catList)

            catDict = dict()
            for category in catList:

                limDict = dict()

                for pairDict in pairDictList:
                    cat = pairDict['category']
                    lim = pairDict['limit']

                    if cat==category and lim not in limDict.keys():

                        limDict[lim] = None

                catDict[category] = limDict


            measLimitDict = dict()
            measLimitDict['MeasurmentLimit'] = catDict


        with codecs.open(limExportPath, 'w+', encoding='iso-8859-1')as yaml_file:

            yaml.dump(measLimitDict, yaml_file, default_flow_style=False, sort_keys=False, allow_unicode=True, encoding='iso-8859-1')

    except Exception as exception:
        log.error('Opening protocol file: ' + str(exception) + '.')


# o=ParseProtocols()

# # o.loadInputLimitsDictYAML('C:\Projects\StatisticToolPythonQtGUI\CalLimits.yaml')
# o.loadInputLimitsDictYAML('C:\Projects\StatisticToolPythonQtGUI\CalLimits.yaml')
#
# o.loadInputLimitsDictYAML('C:\Arbeit\BurnInLimits.yaml')

# catList=[ProtocolCategoriesEnum.ProtocolHead, ProtocolCategoriesEnum.MeasurementLimits,ProtocolCategoriesEnum.Measurements, ProtocolCategoriesEnum.AbbortCriterions]
#
# o.rawParseProtocols(catList,r'C:\Projects\StatisticToolPythonQtGUI\output_certificates\0x0002EA1A\Calibration\2019-03-12-10-23-27_Tuner0_rf0x0002E125_dsp0x0002AFC9_Protocol.txt')

# o.rawParsedProtocolHead[ProtocolHead.CalEnd]='2'
# o.rawParsedProtocolHead['CalStart:']='2'
# o.generateInputFilteredMeasurementLimit(o.inputLimitDict)
# o.extendInputMeasurementLimitDict()
# o.generateInputFilteredMeasurementLimit(o.extInputMeasurementLimitDict)
# o.inputFilteredMeasurementLimitDict=o.generateMeasurementLimitDict(o.inputFilteredMeasurementLimit,o.inputLimitDict)
#
#
#
# # o.inputFilteredMeasurementLimitDict=o.generateMeasurementLimitDict(o.inputFilteredMeasurementLimit)
#
# o.saveMeasurementLimitsDictYAML(o.extInputMeasurementLimitDict, 'C:\Arbeit\limoutput.yaml')
#
#
# # o.saveMeasurementLimitsDictYAML(o.extInputMeasurementLimitDict, 'C:\Arbeit\extInputLimits.yaml')
# a=0

# generateInputLimitsFromFile('C:\Arbeit\CalWriteLimitsTest.txt','C:\Projects\StatisticToolPythonQtGUI\CalLimits.yaml')
