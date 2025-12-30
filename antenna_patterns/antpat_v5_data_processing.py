import calcdiagram_functions as calc
import logconfig as log
import numpy as np
from abc import ABC, abstractmethod
import copy

# Get logger instance
myLogger =log.antPatLogger.logger

class OutFormatTable(ABC):
    def __init__(self):
        self.antennaType=0
        self.chirp=0
        self.azElCombSetup=0
        self.dataTablesList=[]
        self.outputDict=0
        self.dataTablesDictList=[]

    # Reorder the data tables list by changing the antenna pattern index in the configured tables.
    @abstractmethod
    def reorderDataTablesList(self):
        pass

# JSON Table class. Contains parameters for the generated JSON files.
class JSON_Table(OutFormatTable):
    def __init__(self):
        super().__init__()
        self.jsonFileTitle = ''

    # Reorder the data tables list by changing the antenna pattern index in the configured tables.
    def reorderDataTablesList(self):
        myLogger.info("JSON file data tables list reordered, Antenna Type: "+str(self.antennaType) +" Diagram type and Angle setup comb.: " + self.azElCombSetup.string + ', Chirp' + str(self.chirp) + ':')

        for i in range(len(self.dataTablesList)):

            oldIdx=self.dataTablesList[i].configTable.antennaPatternIdx
            self.dataTablesList[i].configTable.antennaPatternIdx=i
            newIdx=self.dataTablesList[i].configTable.antennaPatternIdx

            myLogger.info('[ Table'+str(oldIdx)+' - "antenna_pattern_idx": '+str(oldIdx) +' ] - - - - > [ '+'Table'+str(newIdx)+' - "antenna_pattern_idx": '+str(newIdx)+' ]')

class YAML_Table(OutFormatTable):
    def __init__(self):
        super().__init__()
        self.yamlFileTitle = ''

    # Reorder the data tables list by changing the antenna pattern index in the configured tables.
    def reorderDataTablesList(self):
        myLogger.info("YAML file data tables list reordered, Antenna Type: "+str(self.antennaType) +" Diagram type and Angle setup comb.: " + self.azElCombSetup.string + ', Chirp' + str(self.chirp) + ':')

        for i in range(len(self.dataTablesList)):

            oldIdx=self.dataTablesList[i].configTable.antennaPatternIdx
            self.dataTablesList[i].configTable.antennaPatternIdx=i
            newIdx=self.dataTablesList[i].configTable.antennaPatternIdx

            myLogger.info('[ Table'+str(oldIdx)+' - "antenna_pattern_idx": '+str(oldIdx) +' ] - - - - > [ '+'Table'+str(newIdx)+' - "antenna_pattern_idx": '+str(newIdx)+' ]')


# Setup class. Contains the input parameters data for data tables.
class Setup():
    def __init__(self, setup, antPatHeader, ptu2InputConfDict, chirpConfig, parseDataList, MAX_NOF_DATA_TABLES,portData):
        self.setup=0
        self.antPatHeader=0
        self.ptu2InputConf=0
        self.antennaTypesList=[]
        self.angleSetupList=[]
        self.confChirpList=[]
        self.confTablesList=[]
        self.angleSetupAzElComb=[]
        self.jsonTablesList=[]
        self.yamlTablesList=[]
        self.string=""
        self.errorStatus=0
        self.setupValues(setup, antPatHeader, ptu2InputConfDict, chirpConfig, parseDataList, MAX_NOF_DATA_TABLES,portData)

    # Set the list of AZ-El combinations.
    def setAngleSetupAzElComb(self,angleSetupList):
        outputList = []
        azList = []
        elList = []
        noDiagTypeList=[]
        filteredList=[]

        if len(angleSetupList)==0:
           self.errorStatus=1
           myLogger.error("Empty angle setup list!")
        else:
            for i in range(len(angleSetupList)):
                if angleSetupList[i].diagType == 'NoDiagType':
                    noDiagTypeList.append(angleSetupList[i])

            if len(noDiagTypeList)!=0:
                for antIdx in range(len(self.antennaTypesList)):
                    filteredList=getAngSetupListPerAntennaType(self.antennaTypesList[antIdx], angleSetupList)
                    if len(filteredList)!=0:
                        if len(filteredList) == 1:
                            element = AzElComb(filteredList[0], filteredList[0], 0)
                            outputList.append(element)
                        else:
                            for i in range(len(filteredList)):
                                for j in range(len(filteredList)):
                                    if filteredList[i].nofAnglePoints !=filteredList[j].nofAnglePoints or \
                                            filteredList[i].refAnglePoint != filteredList[j].refAnglePoint or \
                                            filteredList[i].angleStepSize !=filteredList[j].angleStepSize:
                                        element = AzElComb(filteredList[i], filteredList[j], 0)
                                        outputList.append(element)


            else:
                for i in range(len(angleSetupList)):
                    if angleSetupList[i].diagType=='Az':
                        azList.append(angleSetupList[i])
                for i in range(len(angleSetupList)):
                    if angleSetupList[i].diagType == 'El':
                        elList.append(angleSetupList[i])

                if len(azList)==0 and len(elList)!=0:
                    for j in range(len(elList)):
                        element = AzElComb(0, elList[j],0)
                        outputList.append(element)
                elif len(elList)==0 and len(azList)!=0:
                    for i in range(len(azList)):
                        element=AzElComb(azList[i],0,0)
                        outputList.append(element)
                elif len(elList)!=0 and len(azList)!=0:
                    for i in range(len(azList)):
                        for j in range(len(elList)):
                            element = AzElComb(azList[i], elList[j],0)
                            outputList.append(element)

        return outputList

    # Set string.
    def setStr(self,ptu2InputConf):
        self.string=ptu2InputConf.getStr()

    # Set the list of angle setups.
    def setAngleSetupList(self, ptu2InputConf, parseDataList):
        angSetupCombDictList=getAppearingAngleSetupComb(parseDataList)
        angSetupCombDictList1=[]
        withDiagTypeList=[]
        withoutDiagTypeList=[]
        angSetupCombList = []

        for i in range(len(angSetupCombDictList)):
            if angSetupCombDictList[i]["diagType"]=='Az' or angSetupCombDictList[i]["diagType"]=='El':
                withDiagTypeList.append(angSetupCombDictList[i])

        for i in range(len(angSetupCombDictList)):
            if angSetupCombDictList[i]["diagType"] == 'NoDiagType':
                withoutDiagTypeList.append(angSetupCombDictList[i])

        if ptu2InputConf.diagTypeInfo == 1:
            angSetupCombDictList1=withDiagTypeList.copy()
        else:
            angSetupCombDictList1 = withoutDiagTypeList.copy()

        if len(angSetupCombDictList1)==0:
            myLogger.error('No data for ' + ptu2InputConf.getStr() + ' found.')
            self.errorStatus=1
        else:
            for angSetupIdx in range(len(angSetupCombDictList1)):
                myLogger.info('Angle setup comb. added: '+'AntType-'+ str(+angSetupCombDictList1[angSetupIdx]["antType"])+'_DiagType='+angSetupCombDictList1[angSetupIdx]["diagType"]+ '_NofPts=' + str(angSetupCombDictList1[angSetupIdx]["nofAnglePoints"]) + '_StepSize=' + str(angSetupCombDictList1[angSetupIdx]["angleStepSize"]) + '_RefPt=' + str(angSetupCombDictList1[angSetupIdx]["refAnglePoint"])+'.')

                angSetupComb = AngleSetup(angSetupCombDictList1[angSetupIdx])
                angSetupCombList.append(angSetupComb)

        return angSetupCombList

    # Set the configured tables list.
    def setConfTablesList(self,ptu2InputConf):

        outputList = []
        for confTabIdx in range(len(ptu2InputConf.tables)):
            configTable =ConfigTable(ptu2InputConf.tables[confTabIdx])
            if configTable.errorStatus==1:
                self.errorStatus=1
            outputList.append(configTable)
        return outputList

    # Seting the class members according to the input parameters.
    def setupValues(self, setup, antPatHeader, ptu2InputConf, chirpConfig, parseDataList, MAX_NOF_DATA_TABLES,portData):
        self.setup = setup
        self. antPatHeader=copy.deepcopy(antPatHeader)
        self.ptu2InputConf = ptu2InputConf

        if len(parseDataList) == 0:
            self.errorStatus = 1
            myLogger.error('No parsed PTU-2 files found!')

        self.antennaTypesList=getAntennaTypesList(parseDataList,self.ptu2InputConf)

        # Set error if Antenna Type list is empty.
        if len(self.antennaTypesList)==0:
            self.errorStatus=1
            myLogger.error('No antenna types found.')

        self.confChirpList = getConfChirpList(chirpConfig)

        # Set error if Chirp list is empty.
        if len(self.confChirpList)==0:
            self.errorStatus=1
            myLogger.error('Invalid chirp configuration.')

        self.angleSetupList = self.setAngleSetupList(self.ptu2InputConf, parseDataList)
        self.confTablesList = self.setConfTablesList(self.ptu2InputConf)
        self.angleSetupAzElComb=self.setAngleSetupAzElComb(self.angleSetupList)

        self.setStr(self.ptu2InputConf)

        myLogger.info("Initial number of data tables: "+str(self.antPatHeader["nofDataTables"])+'.')

        if self.ptu2InputConf.diagTypeInfo == 1:
            myLogger.info("Only PTU2 files WITH diagram type info considered.")
        else:
            myLogger.info("Only PTU2 files WITHOUT diagram type info considered.")

        if self.ptu2InputConf.upsideDownInfo == 1:
            myLogger.info("Only PTU2 files WITH upside down info considered.")
        else:
            myLogger.info("Only PTU2 files WITHOUT upside down info considered. Processing accordingly to the configured 'upsideDown': "+str(self.ptu2InputConf.upsideDown)+", value.")

        # Set error if the configured tables list surpasses the maximum data tables allowed.
        if len(self.confTablesList) > MAX_NOF_DATA_TABLES:
            self.errorStatus=1
            myLogger.error("The configured tables list surpasses the maximal number of data tables allowed: "+str(MAX_NOF_DATA_TABLES)+'.')

        # Adjust the nofDataTables field to the number of configured tables.
        elif self.antPatHeader["nofDataTables"] != len(self.confTablesList):
            self.antPatHeader["nofDataTables"]=len(self.confTablesList)
            myLogger.info("Nof. Data Tables adjusted to the number of configured tables: " + str(
                len(self.confTablesList)) + '.')

class Setup_v2(Setup):
    def __init__(self, setup, antPatHeader, ptu2InputConf, chirpConfig, parseDataList, MAX_NOF_DATA_TABLES,portData):
        self.portData = portData
        super().__init__(setup, antPatHeader, ptu2InputConf, chirpConfig, parseDataList, MAX_NOF_DATA_TABLES,portData)


    # Seting the class members according to the input parameters.
    def setupValues(self, setup, antPatHeader, ptu2InputConf, chirpConfig, parseDataList, MAX_NOF_DATA_TABLES,portData):
        self.setup = setup
        self.antPatHeader = copy.deepcopy(antPatHeader)
        self.portData = copy.deepcopy(portData)
        self.ptu2InputConf = ptu2InputConf

        if len(parseDataList)==0:
            self.errorStatus=1
            myLogger.error('No parsed PTU-2 files found!')

        self.antennaTypesList = getAntennaTypesList(parseDataList, self.ptu2InputConf)

        # Set error if Antenna Type list is empty.
        if len(self.antennaTypesList) == 0:
            self.errorStatus = 1
            myLogger.error('No antenna types found.')

        self.confChirpList = getConfChirpList(chirpConfig)

        # Set error if Chirp list is empty.
        if len(self.confChirpList) == 0:
            self.errorStatus = 1
            myLogger.error('Invalid chirp configuration.')

        self.angleSetupList = self.setAngleSetupList(self.ptu2InputConf, parseDataList)
        self.confTablesList = self.setConfTablesList(self.ptu2InputConf)
        self.angleSetupAzElComb = self.setAngleSetupAzElComb(self.angleSetupList)

        self.setStr(self.ptu2InputConf)

        myLogger.info("Initial number of data tables: " + str(self.portData["nofDataTables"]) + '.')

        if self.ptu2InputConf.diagTypeInfo == 1:
            myLogger.info("Only PTU2 files WITH diagram type info considered.")
        else:
            myLogger.info("Only PTU2 files WITHOUT diagram type info considered.")

        if self.ptu2InputConf.upsideDownInfo == 1:
            myLogger.info("Only PTU2 files WITH upside down info considered.")
        else:
            myLogger.info("Only PTU2 files WITHOUT upside down info considered. Processing accordingly to the configured 'upsideDown': " + str(
                    self.ptu2InputConf.upsideDown) + ", value.")

        # Set error if the configured tables list surpasses the maximum data tables allowed.
        if len(self.confTablesList) > MAX_NOF_DATA_TABLES:
            self.errorStatus = 1
            myLogger.error("The configured tables list surpasses the maximal number of data tables allowed: " + str(
                MAX_NOF_DATA_TABLES) + '.')

        # Adjust the nofDataTables field to the number of configured tables.
        elif self.portData["nofDataTables"] != len(self.confTablesList):
            self.portData["nofDataTables"] = len(self.confTablesList)
            myLogger.info("Nof. Data Tables adjusted to the number of configured tables: " + str(
                len(self.confTablesList)) + '.')

class Setup_v3(Setup_v2):
    def __init__(self, setup, antPatHeader, ptu2InputConf, chirpConfig, parseDataList, MAX_NOF_DATA_TABLES,portData):
        super().__init__(setup, antPatHeader, ptu2InputConf, chirpConfig, parseDataList, MAX_NOF_DATA_TABLES,portData)

        # Set the list of angle setups.

    def setAngleSetupList(self, ptu2InputConf, parseDataList):
        angSetupCombDictList = getAppearingAngleSetupComb(parseDataList)
        withDiagTypeList = []
        angSetupCombList = []

        for i in range(len(angSetupCombDictList)):
            if angSetupCombDictList[i]["diagType"] == 'Az' or angSetupCombDictList[i]["diagType"] == 'El':
                withDiagTypeList.append(angSetupCombDictList[i])


        if len(withDiagTypeList) == 0:
            myLogger.error('No data for ' + ptu2InputConf.getStr() + ' found.')
            self.errorStatus = 1
        else:
            for angSetupIdx in range(len(withDiagTypeList)):
                myLogger.info('Angle setup comb. added: ' + 'AntType-' + str(
                    +withDiagTypeList[angSetupIdx]["antType"]) + '_DiagType=' + withDiagTypeList[angSetupIdx]["diagType"] + '_NofPts=' + str(withDiagTypeList[angSetupIdx]["nofAnglePoints"]) + '_StepSize=' + str(withDiagTypeList[angSetupIdx]["angleStepSize"]) + '_RefPt=' + str(withDiagTypeList[angSetupIdx]["refAnglePoint"]) + '.')

                angSetupComb = AngleSetup(withDiagTypeList[angSetupIdx])
                angSetupCombList.append(angSetupComb)

        return angSetupCombList

# Seting the class members according to the input parameters.
    def setupValues(self, setup, antPatHeader, ptu2InputConf, chirpConfig, parseDataList, MAX_NOF_DATA_TABLES,portData):
        self.setup = setup
        self.antPatHeader=copy.deepcopy(antPatHeader)
        self.portData = copy.deepcopy(portData)
        self.ptu2InputConf = ptu2InputConf

        if len(parseDataList) == 0:
            self.errorStatus = 1
            myLogger.error('No parsed PTU-2 files found!')

        self.antennaTypesList=getAntennaTypesList(parseDataList,self.ptu2InputConf)

        # Set error if Antenna Type list is empty.
        if len(self.antennaTypesList)==0:
            self.errorStatus=1
            myLogger.error('No antenna types found.')

        self.confChirpList = getConfChirpList(chirpConfig)

        # Set error if Chirp list is empty.
        if len(self.confChirpList)==0:
            self.errorStatus=1
            myLogger.error('Invalid chirp configuration.')

        self.angleSetupList = self.setAngleSetupList(self.ptu2InputConf, parseDataList)
        self.confTablesList = self.setConfTablesList(self.ptu2InputConf)
        self.angleSetupAzElComb=self.setAngleSetupAzElComb(self.angleSetupList)

        self.setStr(self.ptu2InputConf)

        myLogger.info("Initial number of data tables: "+str(self.portData["nofDataTables"])+'.')


        # Set error if the configured tables list surpasses the maximum data tables allowed.
        if len(self.confTablesList) > MAX_NOF_DATA_TABLES:
            self.errorStatus=1
            myLogger.error("The configured tables list surpasses the maximal number of data tables allowed: "+str(MAX_NOF_DATA_TABLES)+'.')

        # Adjust the nofDataTables field to the number of configured tables.
        elif self.portData["nofDataTables"] != len(self.confTablesList):
            self.portData["nofDataTables"]=len(self.confTablesList)
            myLogger.info("Nof. Data Tables adjusted to the number of configured tables: " + str(len(self.confTablesList)) + '.')



class Ptu2InputConf():
    def __init__(self,ptu2InputConf,confIdx):
        self.diagTypeInfo=0
        self.targetAngle=0
        self.upsideDown=0
        self.upsideDownInfo=0
        # self.elDiagCriteria=0
        self.confIdx=0
        self.tables=[]
        self.str=''
        self.setup(ptu2InputConf,confIdx)

    def setStr(self):
        diagTypeInfoStr=''
        targetAngleStr=''
        upsideDownStr=''
        upsideDownInfoStr=''
        if self.diagTypeInfo!=1:
            diagTypeInfoStr='NoDiagType'
        else:
            diagTypeInfoStr='DiagType'

        if self.upsideDown==1:
            upsideDownStr='_UpDown=1_'
        else:
            upsideDownStr='_UpDown=0_'

        if self.upsideDownInfo!=1:
            upsideDownInfoStr='NoUpDownInfo'
        else:
            upsideDownInfoStr='UpDownInfo'
            upsideDownStr='_'

        if self.targetAngle==0:
            targetAngleStr='PTU-Ang'
        else:
            targetAngleStr='Tar-Ang'

        self.str='Conf' +str(self.confIdx) +'_'+diagTypeInfoStr +'_'+ upsideDownInfoStr + upsideDownStr + targetAngleStr

    # Get string.
    def getStr(self):
        self.setStr()
        return self.str

    def setup(self,ptu2InputConf,confIdx):
        self.diagTypeInfo =ptu2InputConf["diagTypeInfo"]
        self.targetAngle = ptu2InputConf["targetAngle"]
        self.upsideDown = ptu2InputConf["upsideDown"]
        self.upsideDownInfo = ptu2InputConf["upsideDownInfo"]
        # self.elDiagCriteria=ptu2InputConf["elDiagCriteria"]
        self.confIdx=confIdx
        self.tables=ptu2InputConf["tables"]
        self.setStr()

class Ptu2InputConfV3():
    def __init__(self,ptu2InputConf):
        self.targetAngle=0
        self.upsideDown=0
        # self.elDiagCriteria=0
        self.tables=[]
        self.str=''
        self.setup(ptu2InputConf)

    def setStr(self):

        targetAngleStr=''
        upsideDownStr=''

        if self.upsideDown==1:
            upsideDownStr='UpDown=1'
        else:
            upsideDownStr='UpDown=0'

        if self.targetAngle==0:
            targetAngleStr='PTU-Ang'
        else:
            targetAngleStr='Tar-Ang'

        self.str='Conf' +str(self.confIdx)  +'_'+ upsideDownStr +'_'+ targetAngleStr

    # Get string.
    def getStr(self):
        self.setStr()
        return self.str

    def setup(self,ptu2InputConf,confIdx):

        self.targetAngle = ptu2InputConf["targetAngle"]
        self.upsideDown = ptu2InputConf["upsideDown"]
        self.confIdx=confIdx
        self.tables=ptu2InputConf["tables"]
        self.setStr()

# Class that contains a combination of Az and El angle setups or No diagram type info angle setup.
class AzElComb():
    def __init__(self,az,el,noDiagType):
        self.az=0
        self.el=0
        self.noDiagType=0
        self.string=''
        self.setup(az,el,noDiagType)

    # Set string.
    def setStr(self,az,el,noDiagType):
        str=''
        if noDiagType!=0:
            str=noDiagType.angleSetupStr
        else:
            if el==0:
                str=az.angleSetupStr
            elif az==0:
                str=el.angleSetupStr
            else:
                str=az.angleSetupStr +' - '+el.angleSetupStr
        return str

    # Set values according to input parameters.
    def setup(self,az,el,noDiagType):
        self.az=az
        self.el=el
        self.noDiagType=noDiagType
        self.string=self.setStr(az,el,noDiagType)

# Class containing the data for Antenna Pattern WITH diagram type info, for certain Configured Table and certain Antenna Type, Angle setup, and Chirp.
class DataTable():
    def __init__(self,angleSetupData,configTable,chirp,parseDataList,ptu2InputConf):
        self.ptu2InputConf=0
        self.tableMeasDataList=[]
        self.angleSetup=0
        self.configTable=0
        self.antennaType=0
        self.chirp=0
        self.nofAngleValues=0
        self.angle=0
        self.errorStatus=0
        self.avgNormLevelDb=0
        self.dataTableString=''
        self.setup(angleSetupData,configTable,chirp,parseDataList,ptu2InputConf)

    # Set string.
    def setStr(self):

        if self.angleSetup.diagType =='NoDiagType':
            diagramTypeStr=''
        else:
            diagramTypeStr='_'+self.angleSetup.diagType

        self.dataTableString=self.ptu2InputConf.getStr()+str(diagramTypeStr)+' - AntType-'+str(self.angleSetup.antennaType)+'_NofPts='+str(self.angleSetup.nofAnglePoints)+'_StepSize='+str(self.angleSetup.angleStepSize)\
        +'_RefPt='+str(self.angleSetup.refAnglePoint)+' - Chirp'+str(self.chirp)+' - Tab'+str(self.configTable.antennaPatternIdx)

    # Get string.
    def getStr(self):
        self.setStr()
        return self.dataTableString

    # Set angle data
    def setAngle(self):
        if self.errorStatus==0:
            self.angle = calc.getPtuAngVals(self.tableMeasDataList[0].parseData)
            self.nofAngleValues=len(self.angle)
            if self.ptu2InputConf.targetAngle == 1:
                self.angle = calc.getTarAngVals(self.tableMeasDataList[0].parseData, getUpsideDown(self.tableMeasDataList[0].parseData,self.ptu2InputConf) )
                # self.angle=mapInputOutput(self.angle,
                #                self.angleSetup.nofAnglePoints,
                #                self.angleSetup.angleStepSize,
                #                self.angleSetup.refAnglePoint,MAX_ANGLE_POINTS, setup["targetAngle"], setup["upsideDown"])

        else:
            myLogger.debug("Angle data not available. Empty parsed data list: AntPatTable" +str(self.configTable.antennaPatternIdx)+' - '+ self.configTable.getStr())

    # Set the list of data for certain Antenna Type, Tx antennas and Rotation axis from the Configured tables, Angle setup, and Chirp.
    def setTableMeasDataList(self,parseDataList):

        upsideDownData = getUpsideDownData(parseDataList, self.ptu2InputConf.upsideDownInfo)

        if len(upsideDownData) != 0:

            if self.ptu2InputConf.diagTypeInfo==1:

                myLogger.debug('Getting PTU2 parsed data WITH dagram type info, AntPatTable' +str(self.configTable.antennaPatternIdx)+': '+ str(self.configTable.getStr()))

                applicableTxAntData = getApplicableTxAntIndData(self.configTable.applTxAntInd, self.configTable.nofApplicableTxAnt, upsideDownData)
                txAntDiagTypeCombData=[]

                if len(applicableTxAntData)==0:
                    myLogger.info('No PTU2 files with Tx Antenna info found. Looking for matching PTU2 without Tx Antenna info.')

                    noTxAntData = getNoTxAntData(upsideDownData)
                    if len(noTxAntData)!=0:
                        txAntDiagTypeCombData=getDesiredDiagTypeData(antennaDiagramTypeMapping(self.configTable.rotationAxis), noTxAntData)
                        myLogger.info('PTU2 files without Tx Antenna info found. Processng as configured Tx Antenna.')
                    else:
                        myLogger.error('No PTU2 files without Tx Antenna info found.')
                        self.errorStatus=1
                else:

                    txAntDiagTypeCombData = getDesiredDiagTypeData(antennaDiagramTypeMapping(self.configTable.rotationAxis), applicableTxAntData)

                if len(txAntDiagTypeCombData)!=0:

                    for txAntDiagTypeIdx in range(len(txAntDiagTypeCombData)):

                        fileNamePath=txAntDiagTypeCombData[txAntDiagTypeIdx].fileNamePath
                        myLogger.debug('LISTED: ' +fileNamePath )

                        nofAngPts=getNofAnglePoints(txAntDiagTypeCombData[txAntDiagTypeIdx])
                        nofAngPtsSelf=self.angleSetup.nofAnglePoints
                        # myLogger.debug('NofAngPts: ' + str(nofAngPts)+', NofAngPtsSelf: '+str(nofAngPtsSelf))

                        angleStep=getAngleStep(txAntDiagTypeCombData[txAntDiagTypeIdx])
                        angleStepSelf=self.angleSetup.angleStepSize
                        # myLogger.debug('AngleStep: ' + str(nofAngPts) + ', AngleStepSelf: ' + str(nofAngPtsSelf))

                        refAngPt=getRefAnglePoint(txAntDiagTypeCombData[txAntDiagTypeIdx])
                        refAngPtSelf=self.angleSetup.refAnglePoint
                        # myLogger.debug('RefAngPt: ' + str(nofAngPts) + ', RefAngPtSelf: ' + str(nofAngPtsSelf))

                        antennaType = txAntDiagTypeCombData[txAntDiagTypeIdx].antennaInfo.antennaType
                        antennaTypeSelf = self.angleSetup.antennaType

                        chirpActive=txAntDiagTypeCombData[txAntDiagTypeIdx].chirpInfoList[self.chirp].active
                        # myLogger.debug('ChirpSelf: ' + str(self.chirp)+', Active: '+str(chirpActive))

                        if (antennaType==antennaTypeSelf) and (nofAngPts ==nofAngPtsSelf ) and (angleStep == angleStepSelf) and (abs(refAngPt - refAngPtSelf)<0.1) and (chirpActive==1):
                            tableMeasData=TableMeasData()
                            tableMeasData.parseData=txAntDiagTypeCombData[txAntDiagTypeIdx]
                            self.tableMeasDataList.append(tableMeasData)
                            myLogger.info('PTU2 file added: ' + tableMeasData.parseData.fileNamePath)


                    if len(self.tableMeasDataList)==0:
                        self.errorStatus=1
                        myLogger.error('No PTU2 parsed data files WITH diagram type info found: Table'+str(self.configTable.antennaPatternIdx)+' - '+ self.configTable.getStr())
                    else:
                        maxNofAvailableTxAnt = getNofAvailableTxAnt(self.tableMeasDataList)
                        if self.configTable.nofApplicableTxAnt > maxNofAvailableTxAnt:
                            myLogger.error('Number of applicable Tx Antenna indices: '+str(self.configTable.nofApplicableTxAnt)+ ', surpasses the total number of available Tx Antenna: '+str(maxNofAvailableTxAnt)+'.')
                            self.errorStatus=1
                        else:
                            self.errorStatus=0
                else:
                    self.errorStatus=1
                    myLogger.error("No data for Diagram Type found: "+antennaDiagramTypeMapping(self.configTable.rotationAxis)+'.')
            else:

                myLogger.debug('Getting PTU2 parsed data WITHOUT dagram type info, Table' + str(self.configTable.antennaPatternIdx) + ': ' + str(self.configTable.getStr()))

                applicableTxAntData = getApplicableTxAntIndData(self.configTable.applTxAntInd,self.configTable.nofApplicableTxAnt, upsideDownData)

                if len(applicableTxAntData) == 0:
                    myLogger.info('No PTU2 files with Tx Antenna info found. Looking for matching PTU2 without Tx Antenna info.')

                    noTxAntData = getNoTxAntData(upsideDownData)
                    noDiagTypeList=[]

                    if len(noTxAntData) != 0:
                        noDiagTypeList = getNonDiagTypeFilesList(noTxAntData)
                        myLogger.info('PTU2 files without Tx Antenna info found. Processng as configured Tx Antenna.')
                    else:
                        myLogger.error('No PTU2 files without Tx Antenna info found.')
                        self.errorStatus=1
                else:

                    noDiagTypeList = getNonDiagTypeFilesList(applicableTxAntData)

                if len(noDiagTypeList) != 0:

                    for txAntDiagTypeIdx in range(len(noDiagTypeList)):
                        if getNofAnglePoints(noDiagTypeList[txAntDiagTypeIdx]) == self.angleSetup.nofAnglePoints and \
                                getAngleStep(noDiagTypeList[txAntDiagTypeIdx]) == self.angleSetup.angleStepSize and \
                                abs (getRefAnglePoint(noDiagTypeList[txAntDiagTypeIdx]) - self.angleSetup.refAnglePoint)<0.1 \
                                and noDiagTypeList[txAntDiagTypeIdx].antennaInfo.antennaType==self.angleSetup.antennaType \
                                and noDiagTypeList[txAntDiagTypeIdx].chirpInfoList[self.chirp].active == 1:
                            tableMeasData = TableMeasData()
                            tableMeasData.parseData = noDiagTypeList[txAntDiagTypeIdx]
                            self.tableMeasDataList.append(tableMeasData)
                            myLogger.info('PTU2 file added: ' + tableMeasData.parseData.fileNamePath)

                    if len(self.tableMeasDataList)==0:
                        self.errorStatus=1
                        myLogger.error('No PTU2 parsed data files WITHOUT diagram type info found: Table'+str(self.configTable.antennaPatternIdx)+' - '+ self.configTable.getStr())
                    else:
                        maxNofAvailableTxAnt = getNofAvailableTxAnt(self.tableMeasDataList)
                        if self.configTable.nofApplicableTxAnt > maxNofAvailableTxAnt:
                            myLogger.error('Number of applicable Tx Antenna indices: '+str(self.configTable.nofApplicableTxAnt)+ ', surpasses the total number of available Tx Antenna: '+str(maxNofAvailableTxAnt)+'.')
                            self.errorStatus=1
                        else:
                            self.errorStatus=0

                else:
                    self.errorStatus = 1
                    myLogger.error("No data for WITHOUT diagram type info found: " + antennaDiagramTypeMapping(self.configTable.rotationAxis) + '.')
        else:
            self.errorStatus = 1
            myLogger.error("No PTU2 parsed data files found, upsideDownInfo: " + str(self.ptu2InputConf.upsideDownInfo) + '.')


    # Set the Measuremenr Data list with normalised level values.
    def setTableMeasDataVals(self):
        if self.errorStatus==0:

            for tmDataIdx in range(len(self.tableMeasDataList)):

                self.tableMeasDataList[tmDataIdx].normLevelList=self.setNormLevelData(self.configTable, self.chirp, self.tableMeasDataList[tmDataIdx].parseData)
                #
                # for rxAnt in range(len(self.tableMeasDataList[tmDataIdx].normLevelList)):
                #
                #     self.tableMeasDataList[tmDataIdx].normLevelList[rxAnt] = mapInputOutput(self.tableMeasDataList[tmDataIdx].normLevelList[rxAnt],
                #                                           self.angleSetup.nofAnglePoints,
                #                                             self.angleSetup.angleStepSize,
                #                                         self.angleSetup.refAnglePoint,MAX_ANGLE_POINTS, setup["targetAngle"], setup["upsideDown"])
                self.setRxAntAvgNormLevel(self.tableMeasDataList[tmDataIdx])

    # Set normalised level data for the data table input parameters and a certain PTU2 parsed file from the Measurement Data list.
    def setNormLevelData(self,configTable,chirp,parseData):
        normLevelList = []
        if configTable.nofApplicableRxAnt <= parseData.antennaInfo.nofAntennas:
            for rxAntIdx in range(configTable.nofApplicableRxAnt):
                normLevel = calc.getNormAntLevel(configTable.applRxAntInd[rxAntIdx], chirp, parseData)
                normLevelList.append(normLevel)
        else:
            self.errorStatus=1
            myLogger.error("The number of the applicable Rx antennas surpasses the number of sensor antennas: Table"+str(configTable.antennaPatternIdx)+' - '+configTable.getStr()+' - PTU2 file - '+parseData.fileNamePath)
        return normLevelList

    # Set the average normalised level of the configured Rx antennas for a certain PTU2 parsed file from the Meas Data list.
    def setRxAntAvgNormLevel(self,tableMeasData):
        if self.errorStatus==0:
            normLevelSum=0
            for rxAnt in range(len(tableMeasData.normLevelList)):
                normLevelW = 10 ** (tableMeasData.normLevelList[rxAnt] / 10)
                normLevelSum += normLevelW
            avgNormLevel=normLevelSum/len(tableMeasData.normLevelList)
            tableMeasData.rxAntAvgNormLevelW=avgNormLevel
            tableMeasData.rxAntAvgNormLevelDb =10 * np.log10(tableMeasData.rxAntAvgNormLevelW)


    # Set the values for given input parameters.
    def setup(self,angleSetupData,configTable,chirp,parseDataList,ptu2InputConf):
        self.ptu2InputConf=ptu2InputConf
        # self.antennaType=antennaType
        self.angleSetup=angleSetupData
        self.configTable=configTable
        self.chirp=chirp
        self.avgNormLevelDb=0
        self.setTableMeasDataList(parseDataList)
        self.setTableMeasDataVals()
        self.setAngle()

# Class containing the data for Antenna Pattern WITHOUT diagram type info, for certain Configured Table and certain Antenna Type, Angle setup, and Chirp.
# class DataTableNoDiagType(DataTable):
#     # Set the list of data for No Diagram Type info setup, certain Antenna Type, Tx antennas, Configured tables, Angle setup, and Chirp.
#     def setTableMeasDataList(self, parseDataList):
#         myLogger.debug('Getting PTU2 parsed data WITHOUT dagram type info, Table' + str(self.configTable.antennaPatternIdx) + ': ' + str(self.configTable.getStr()))
#
#         antennaTypeData = getAntennaTypeData(self.antennaType, parseDataList)
#
#         if len(antennaTypeData) != 0:
#
#             applicableTxAntData = getApplicableTxAntIndData(self.configTable.applTxAntInd,self.configTable.nofApplicableTxAnt, upsideDownData)
#
#             if len(applicableTxAntData)==0:
#                 myLogger.debug('No applicable Tx Antenna data found.')
#                 noTxAntData = getNoTxAntData(antennaTypeData)
#
#                 noDiagTypeList = getNonDiagTypeFilesList(noTxAntData)
#             else:
#
#                 noDiagTypeList = getNonDiagTypeFilesList(applicableTxAntData)
#
#             if len(noDiagTypeList)!=0:
#
#                 for txAntDiagTypeIdx in range(len(noDiagTypeList)):
#                     if getNofAnglePoints(noDiagTypeList[txAntDiagTypeIdx], self.ptu2InputConf.targetAngle,
#                                          self.ptu2InputConf.upsideDown) == self.angleSetup.nofAnglePoints and \
#                             getAngleStep(noDiagTypeList[txAntDiagTypeIdx], self.ptu2InputConf.targetAngle,
#                                          self.ptu2InputConf.upsideDown) == self.angleSetup.angleStepSize and \
#                             getRefAnglePoint(noDiagTypeList[txAntDiagTypeIdx], self.ptu2InputConf.targetAngle,
#                                              self.ptu2InputConf.upsideDown) == self.angleSetup.refAnglePoint \
#                             and noDiagTypeList[txAntDiagTypeIdx].chirpInfoList[self.chirp].active==1:
#                         tableMeasData = TableMeasData()
#                         tableMeasData.parseData = noDiagTypeList[txAntDiagTypeIdx]
#                         self.tableMeasDataList.append(tableMeasData)
#                         myLogger.info('PTU2 file added: ' + tableMeasData.parseData.fileNamePath)
#
#                 if len(self.tableMeasDataList) == 0:
#                     self.errorStatus = 1
#                     myLogger.debug('No PTU2 parsed data files WITHOUT diagram type info found: Table' + str(
#                         self.configTable.antennaPatternIdx) + '- ' + self.configTable.getStr())
#                 else:
#                     self.errorStatus = 0
#             else:
#                 self.errorStatus = 1
#                 myLogger.debug("No data for WITHOUT diagram type info found: " + antennaDiagramTypeMapping(self.configTable.rotationAxis) + '.')
#
#         else:
#             self.errorStatus=1
#             myLogger.debug("No PTU2 parsed data files WITHOUT diagram type info found: Antenna Type: " +str(self.antennaType)+'.')

# Class containing the norm level data and PTU2 parsed data for certain element of the list containing data for certain input.
class TableMeasData():
    def __init__(self):
        self.normLevelList = []
        self.rxAntAvgNormLevelW=0
        self.rxAntAvgNormLevelDb = 0
        self.parseData=0

# Class containing the parameters for angle setup.
class AngleSetup():
    def __init__(self,angleSetupData):
        self.antennaType=0
        self.diagType = ''
        self.nofAnglePoints=0
        self.angleStepSize=0
        self.refAnglePoint=0
        self.angleSetupStr = ''
        self.setAngle(angleSetupData)
        self.setStr()

    # Set string.
    def setStr(self):
        self.angleSetupStr='AntType-'+str(self.antennaType)+'_'+str(self.diagType)+'_NofPts='+str(self.nofAnglePoints)+'_StepSize='+str(self.angleStepSize)+'_RefPt='+str(self.refAnglePoint)

    # Set values according to given input parameters.
    def setAngle(self,angleSetupData):
        self.antennaType=angleSetupData["antType"]
        self.diagType = angleSetupData["diagType"]
        self.nofAnglePoints = angleSetupData["nofAnglePoints"]
        self.angleStepSize =angleSetupData["angleStepSize"]
        self.refAnglePoint = angleSetupData["refAnglePoint"]

# Class containing the prarameters of a configured table.
class ConfigTable():
    def __init__(self,configDict):
        self.antennaPatternIdx=0
        self.patternType=0
        self.rotationAxis=0
        self.nofApplicableTxAnt=0
        self.nofApplicableRxAnt=0
        self.applTxAntInd=[]
        self.applRxAntInd=[]
        self.gainCalcMethod=0
        self.errorStatus=0
        self.errorStringList=[]
        self.rxErrorStringList = []
        self.txErrorStringList = []
        self.confTabStr=''
        self.setTable(configDict)

        # Check configuration errors for Tx antennas.
        if self.checkAppAntConf(self.nofApplicableTxAnt,self.applTxAntInd)==1:
            self.txErrorStringList=self.errorStringList
            myLogger.error("Invalid configuration for applicable Tx antennas: Table"+str(self.antennaPatternIdx)+' - '+self.getStr())
            for i in range(len(self.txErrorStringList)):
                errorString=self.txErrorStringList[i]
                myLogger.error(errorString)

        # Check configuration errors for Rx antennas.
        if self.checkAppAntConf(self.nofApplicableRxAnt, self.applRxAntInd)==1:
            self.rxErrorStringList = self.errorStringList
            myLogger.error("Invalid configuration for applicable Rx antennas: Table"+str(self.antennaPatternIdx)+' - '+self.getStr())
            for i in range(len(self.rxErrorStringList)):
                errorString=self.rxErrorStringList[i]
                myLogger.error(errorString)

        # Check congiguration for pattern type, and rotation axis.
        self.checkPatternType()
        self.checkRotationAxis()

    # Check congiguration for rotation axis.
    def checkRotationAxis(self):

        allowedVals = [0, 1, 2, 3]

        allowedValsStr = '0, 1 ,2, 3'

        if self.rotationAxis not in allowedVals:
            self.errorStatus = 1
            myLogger.error("Invalid rotation axis, Table" + str(self.antennaPatternIdx) + ' - ' + self.getStr() + '. It should be one of these values: ' + allowedValsStr + '.')

    # Check congiguration for pattern type.
    def checkPatternType(self):

        allowedVals=[0,1,2,3]

        allowedValsStr = '0, 1 ,2, 3'

        if self.patternType not in allowedVals:
            self.errorStatus=1
            myLogger.error("Invalid pattern type, Table"+str(self.antennaPatternIdx)+' - '+self.getStr()+'. It should be one of these values: '+allowedValsStr+'.')

    # Check applicable antenas configuration.
    def checkAppAntConf(self,nofAppAnt,appAntIndList):
        ret=0
        errorString=''
        checkNoInc=0
        checkNullAppAnt=0
        checkMaxNumAppAnt=0
        checkAppAntIndListLen=0
        checkNoMatch=0
        errorStringList=[]

        # if nofAppAnt>MAX_NUM_ANT:
        #     checkMaxNumAppAnt=1
        #     errorString='The number of applicable antennas is larger than the predefined maximum: ' + str(MAX_NUM_ANT)+'.'
        #     errorStringList.append(errorString)

        if nofAppAnt<=0:
            checkNullAppAnt=1
            errorString='The number of applicable antennas is zero or less.'
            errorStringList.append(errorString)

        # if len(appAntIndList)>MAX_NUM_ANT:
        #     checkAppAntIndListLen=1
        #     errorString='The length of the applicable antenna incices list is larger than the predefined maximal number of applicable antennas: ' + str(MAX_NUM_ANT)+'.'
        #     errorStringList.append(errorString)

        # nofNullInd=len(appAntIndList)-nofAppAnt
        # count=0
        # if nofAppAnt==1:
        #     stop=0
        # else:
        #     stop=-1
        # for i in range(len(appAntIndList)-1,stop,-1):
        #     if appAntIndList[i]==0:
        #         count=count+1
        #     else:
        #         break
        # if count!=nofNullInd:
        #     checkNoMatch=1
        #     errorString='Applicable antenna indices values do not match the number of applicable antennas.'
        #     errorStringList.append(errorString)

        if nofAppAnt>len(appAntIndList):
            stop=len(appAntIndList)
        else:
            stop=nofAppAnt
        temp = -1
        for i in range(stop):
            if appAntIndList[i] > temp:
                temp = appAntIndList[i]
            else:
                checkNoInc = 1
        if checkNoInc ==1:
            errorString='Applicable antenna indices are not in incremental order.'
            errorStringList.append(errorString)

        if len(appAntIndList)!=nofAppAnt:
            checkNoMatch=1
            errorString='Applicable antenna indices values do not match the number of applicable antennas.'
            errorStringList.append(errorString)

        self.errorStringList=errorStringList

        if checkNoInc==1 or checkNullAppAnt==1 or checkNoMatch==1:
            self.errorStatus=1
            ret=1
        return ret

    # Set string
    def setStr(self):
        confTableDict=dict()

        confTableDict.update({"antenna_pattern_idx":self.antennaPatternIdx,"patternType":self.patternType,"rotationAxis":self.rotationAxis,
                     "nofApplicableTxAnt":self.nofApplicableTxAnt,"nofApplicableRxAnt":self.nofApplicableRxAnt,
                     "applTxAntInd":self.applTxAntInd,"applRxAntInd":self.applRxAntInd,"gainCalcMethod":self.gainCalcMethod})

        self.confTabStr=str(confTableDict)

    # Get string
    def getStr(self):
        self.setStr()
        return self.confTabStr

    # Set values according to certain input.
    def setTable(self,configDict):
        self.antennaPatternIdx=configDict["antenna_pattern_idx"]
        self.patternType=configDict["patternType"]
        self.rotationAxis=configDict["rotationAxis"]
        self.nofApplicableTxAnt=configDict["nofApplicableTxAnt"]
        self.nofApplicableRxAnt=configDict["nofApplicableRxAnt"]
        self.applTxAntInd=configDict["applTxAntInd"]
        self.applRxAntInd=configDict["applRxAntInd"]
        self.gainCalcMethod=configDict["gainCalcMethod"]
        self.setStr()

# # Mapping string for the antenna diagram types
# def getAntDiagType(inputString):
#     if inputString == 'NVM_ANTPAT_ROT_AXIS_Z' or inputString ==1:
#         antennaDiagType = 'Az'
#     else:
#         antennaDiagType = 'El'
#     return antennaDiagType

# Get the PTU2 parsed data for desired diagram type.
def getDesiredDiagTypeData(diagramType, parseDataList):
    myLogger.debug("Looking for " +str(diagramType) +' PTU2 parsed data.')
    outputList = []
    for pdIdx in range(len(parseDataList)):
        if parseDataList[pdIdx].measSetupInfo.antennaDiagramTypeFound == 1:
            if parseDataList[pdIdx].measSetupInfo.antennaDiagramType == diagramType:
                outputData = parseDataList[pdIdx]
                outputList.append(outputData)

    # myLogger.debug('outputList#########')
    # for i in range(len(outputList)):
        # myLogger.debug('PTU#####outputLIST*******: ' + outputList[i].fileNamePath)
        # myLogger.debug('Chirp0: ' + str(outputList[i].chirpInfoList[0].active))
        # myLogger.debug('Chirp1: ' + str(outputList[i].chirpInfoList[1].active))
        # myLogger.debug('Chirp2: ' + str(outputList[i].chirpInfoList[2].active))
        # myLogger.debug('Chirp3: ' + str(outputList[i].chirpInfoList[3].active))
    return outputList

# Get antenna types list.
def getAntennaTypeData(antennaType,parseData):
    outputList=[]
    myLogger.debug("Looking for Antenna Type - " +str(antennaType) +' PTU2 parsed data.')
    for pdIdx in range(len(parseData)):
        if parseData[pdIdx].antennaInfo.antennaType==antennaType:
            outputList.append(parseData[pdIdx])
            myLogger.debug('File added: '+parseData[pdIdx].fileNamePath+'.')

    return outputList
# Get list of the parsed data with upsideDown info.
def getUpsideDownData(parseDataList,upsideDownInfo):
    outputList=[]
    if upsideDownInfo ==1:
        for pdIdx in range(len(parseDataList)):
            if parseDataList[pdIdx].measSetupInfo.sensorUpsideDownFound==1:
                outputList.append(parseDataList[pdIdx])
    else:
        for pdIdx in range(len(parseDataList)):
            if parseDataList[pdIdx].measSetupInfo.sensorUpsideDownFound!=1:
                outputList.append(parseDataList[pdIdx])
    return outputList

def getUpsideDown(parseData,ptu2InputConfig):
    if ptu2InputConfig.upsideDownInfo==0:
        upsideDown = ptu2InputConfig.upsideDown
    else:
        upsideDown = parseData.measSetupInfo.sensorUpsideDown
    return upsideDown

# Get PTU2 parsed data for PTU2 files without Tx antenna info.
def getNoTxAntData(parseDataList):
    outputList=[]
    myLogger.debug('Getting PTU2 parsed data without Tx antenna info.')
    for i in range(len(parseDataList)):
        if parseDataList[i].fileTitle.txAntFound==0:
            outputList.append(parseDataList[i])
            myLogger.debug('File added: '+parseDataList[i].fileNamePath+'.')

    return outputList

# Get PTU2 parsed data for PTU2 files without Tx antenna info.
def getDesiredTxAntFilesList(txAnt, parseDataList):
    outputList = []
    for pdIdx in range(len(parseDataList)):
        if parseDataList[pdIdx].fileTitle.txAntFound == 1 and parseDataList[pdIdx].fileTitle.txAnt == txAnt:
            actuaData = parseDataList[pdIdx]
            outputList.append(actuaData)
            # myLogger.debug('PTU#####: ' + parseDataList[pdIdx].fileNamePath)
            # myLogger.debug('Chirp0: '+str(parseDataList[pdIdx].chirpInfoList[0].active))
            # myLogger.debug('Chirp1: ' + str(parseDataList[pdIdx].chirpInfoList[1].active))
            # myLogger.debug('Chirp2: ' + str(parseDataList[pdIdx].chirpInfoList[2].active))
            # myLogger.debug('Chirp3: ' + str(parseDataList[pdIdx].chirpInfoList[3].active))

    return outputList

# Get the list of the lists containing PTU2 parsed data for given Tx antennas, according to applicable Tx antenna indices.
def getApplicableTxAntIndData(appTxAntIndArray, nofApplicableTxAnt, parseDataList):
    dataList = []
    arrayLen = len(appTxAntIndArray)
    if nofApplicableTxAnt <= arrayLen:
        for txAntInd in range(nofApplicableTxAnt):
            data = getDesiredTxAntFilesList(appTxAntIndArray[txAntInd], parseDataList)
            dataList += data
            myLogger.debug("Looking for TxAnt"+str(appTxAntIndArray[txAntInd]) +' PTU2 parsed data.')

    # myLogger.debug('DataList#########')
    # for i in range(len(dataList)):
        # myLogger.debug('PTU#####DATALIST: ' + dataList[i].fileNamePath)
        # myLogger.debug('Chirp0: ' + str(dataList[i].chirpInfoList[0].active))
        # myLogger.debug('Chirp1: ' + str(dataList[i].chirpInfoList[1].active))
        # myLogger.debug('Chirp2: ' + str(dataList[i].chirpInfoList[2].active))
        # myLogger.debug('Chirp3: ' + str(dataList[i].chirpInfoList[3].active))

    return dataList
# String mapping for diagram type.
def antennaDiagramTypeMapping(rotationAxis):
    if rotationAxis == 2:
        antDiagType = 'El'
    else:
        antDiagType = 'Az'
    return antDiagType


# Get the num. of diagrams from the parsed data
def getNofDiagrams(parseDataList):
    diagramIdxList=[]
    for pdIdx in range(len(parseDataList)):
        diagram=parseDataList[pdIdx].fileTitle.diagram
        diagramIdxList.append(diagram)
    if len(diagramIdxList)!=0:
        nofDiagrams=max(diagramIdxList)+1
    else:
        nofDiagrams=0
    return nofDiagrams

# Get the list of all sensors from the parsed data
def getSensorList(parseDataList):
    sensor = ''
    sensorList = []
    for listIdx in range(len(parseDataList)):
        if parseDataList[listIdx].fileTitle.sensorFound==1:
            if parseDataList[listIdx].fileTitle.sensor!= sensor:
                sensor = parseDataList[listIdx].fileTitle.sensor
                sensorList.append(parseDataList[listIdx].fileTitle.sensor)
    return sensorList

# Get the list of all antenna types from the parsed data
def getAntennaTypesList(parseDataList,ptu2InputConf):
    antennaType = 0
    antennaTypeList = []
    if ptu2InputConf.diagTypeInfo == 0:
        for listIdx in range(len(parseDataList)):
            if parseDataList[listIdx].measSetupInfo.antennaDiagramTypeFound != 1:
                if parseDataList[listIdx].antennaInfo.antennaType!= antennaType:
                    antennaType = parseDataList[listIdx].antennaInfo.antennaType
                    antennaTypeList.append(parseDataList[listIdx].antennaInfo.antennaType)
    else:
        for listIdx in range(len(parseDataList)):
            if parseDataList[listIdx].measSetupInfo.antennaDiagramTypeFound == 1:
                if parseDataList[listIdx].antennaInfo.antennaType!= antennaType:
                    antennaType = parseDataList[listIdx].antennaInfo.antennaType
                    antennaTypeList.append(parseDataList[listIdx].antennaInfo.antennaType)

    antTypeSet=set(antennaTypeList)
    outputList=list(antTypeSet)

    return outputList


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

# Get PTU2 parsed data for files without diagram type info.
def getNonDiagTypeFilesList(parseDataList):
    outputList = []
    for pdIdx in range(len(parseDataList)):
        if parseDataList[pdIdx].measSetupInfo.antennaDiagramTypeFound != 1:
                outputData = parseDataList[pdIdx]
                outputList.append(outputData)
    return outputList

# Get angle step from PTU2 parsed data, for angle setup configuration.
def getAngleStep(parseData):
    # if isTargetAngle ==1:
    #     angle=calc.getTarAngVals(parseData,upsideDown)
    # else:
    #     angle=calc.getPtuAngVals(parseData)
    angle = calc.getPtuAngVals(parseData)
    medianList=[]
    for i in range(1,5):
        firstPoint=round(angle[i-1],1)
        lastPoint=round(angle[i],1)
        step=abs(firstPoint-lastPoint)
        medianList.append(step)
    median=np.median(medianList)
    return median

# Get number fo angle points from PTU2 parsed data, for angle setup configuration.
def getNofAnglePoints(parseData):
    # if isTargetAngle == 1:
    #     length=len(calc.getTarAngVals(parseData, upsideDown))
    # else:
    #     length=len(calc.getPtuAngVals(parseData))
    length=len(calc.getPtuAngVals(parseData))
    return length

# Get the reference angle point(the first point from the angle array) from PTU2 parsed data, for angle setup configuration.
def getRefAnglePoint(parseData):
    # if isTargetAngle ==1:
    #     angle=calc.getTarAngVals(parseData,upsideDown)
    # else:
    #     angle=calc.getPtuAngVals(parseData)
    angle = calc.getPtuAngVals(parseData)
    refAnglePoint=round(angle[0],1)
    return refAnglePoint

# Get a list of the appearing angle setup (nof. angle points, angle step size, ref. angle point) and diagram type info (respectively Non diagram type info) combintains.
def getAppearingAngleSetupComb(parseDataList):

    combDictList=[]
    outputList=[]
    myLogger.info('Getting angle setup list:')


    for pdIdx in range(len(parseDataList)):

        combDict = dict()
        # step=getAngleStep(parseDataList[pdIdx],isTargetAngle,upsideDown)
        # nofAnglePoints=getNofAnglePoints(parseDataList[pdIdx],isTargetAngle,upsideDown)
        # refAnglePoint=getRefAnglePoint(parseDataList[pdIdx],isTargetAngle,upsideDown)

        step=getAngleStep(parseDataList[pdIdx])
        nofAnglePoints=getNofAnglePoints(parseDataList[pdIdx])
        refAnglePoint=getRefAnglePoint(parseDataList[pdIdx])

        antennaType=parseDataList[pdIdx].antennaInfo.antennaType

        if parseDataList[pdIdx].measSetupInfo.antennaDiagramTypeFound==1:
            diagType=parseDataList[pdIdx].measSetupInfo.antennaDiagramType
        else:
            diagType ='NoDiagType'

        combDict.update({"antType":antennaType,"diagType":diagType,"nofAnglePoints": nofAnglePoints, "angleStepSize": step,"refAnglePoint":refAnglePoint})
        combDictList.append(combDict)

    # outputList=list(np.unique(np.array(combDictList)))

    for pdIdx in range(len(combDictList)):
        if pdIdx==0:
            outputList.append(combDictList[pdIdx])
            myLogger.debug('Angle setup comb. added: '+ 'AntType-'+str(combDictList[pdIdx]["antType"]) + '_DiagType='+combDictList[pdIdx]["diagType"]+ '_NofAngPts=' + str(combDictList[pdIdx]["nofAnglePoints"]) + '_AngStepSize=' + \
                          str(combDictList[pdIdx]["angleStepSize"]) + '_RefAngPt=' + str(combDictList[pdIdx]["refAnglePoint"]))
        isDifferentList=[]
        for outputIdx in range(len(outputList)):
            isDifferent=0
            if outputList[outputIdx]["antType"]!=combDictList[pdIdx]["antType"]\
                    or outputList[outputIdx]["diagType"]!=combDictList[pdIdx]["diagType"]\
                    or outputList[outputIdx]["nofAnglePoints"]!=combDictList[pdIdx]["nofAnglePoints"]\
                    or outputList[outputIdx]["angleStepSize"]!=combDictList[pdIdx]["angleStepSize"]\
                    or abs(outputList[outputIdx]["refAnglePoint"]- combDictList[pdIdx]["refAnglePoint"])>=0.1:
               isDifferent=1
            isDifferentList.append(isDifferent)

        found=1
        for difIdx in range(len(isDifferentList)):
            if isDifferentList[difIdx] ==0:
                found=0
                break

        if found ==1:
            outputList.append(combDictList[pdIdx])
            myLogger.debug('Angle setup comb. added: '+ 'AntType-'+str(combDictList[pdIdx]["antType"]) + '_DiagType='+combDictList[pdIdx]["diagType"]+  '_NofAngPts=' + str(combDictList[pdIdx]["nofAnglePoints"]) + '_AngStepSize=' + str(combDictList[pdIdx]["angleStepSize"]) + '_RefAngPt=' + str(combDictList[pdIdx]["refAnglePoint"])+'.')
                # outputList.append(combDictList[pdIdx])

    return outputList

# Map the input measurement data array to the maximal number of allowed angle points.
def mapInputOutput(inputArr,nofAngPts, stepSize, refPoint,maxAnglePoints,isTargetAngle,upsideDown):
    if isTargetAngle==1 and upsideDown==0:
        stepSize=-stepSize
    firstPoint=refPoint
    lastPoint=refPoint +((nofAngPts-1)*stepSize)
    valuesRange = abs(firstPoint - lastPoint)
    nofSlices=nofAngPts-1

    # outputDict=dict()
    if nofAngPts > maxAnglePoints:

        n = 1
        outputStepSize=n*stepSize
        outputNofSlices=int(valuesRange / abs(outputStepSize))
        outputAngPts = 1+ outputNofSlices
        outputLastPoint = refPoint + ((outputAngPts - 1) * outputStepSize)
        # div=nofSlices/outputNofSlices

        while outputAngPts>91:
            n = n + 1
            outputStepSize = n * stepSize
            outputNofSlices = int(valuesRange / abs(outputStepSize))
            outputAngPts = 1 + outputNofSlices
            outputLastPoint = refPoint + ((outputAngPts - 1) * outputStepSize)
            # div = nofSlices / outputNofSlices

        outputArray=inputArr[0::n]
        myLogger.debug("Angle points reduced to: MAX_ANGLE_POINTS: " + str(maxAnglePoints) + ", StepSize: "+str(n)+'.')
        # outputDataArr=inputDataArr[0::n]

        # outputDict.update({"angleArray":outputArray,"normLevelArray":outputDataArr})
    else:
        outputArray = inputArr
    return outputArray

# Get the configured chirps
def getConfChirpList(chirpSetup):
    chirpList = []
    for chirp, set in chirpSetup.items():
        if set == 1:
            parts=chirp.split('chirp')
            chirpNum=parts[1]
            chirpNum=int(chirpNum)
            chirpList.append(chirpNum)
    return chirpList

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
        actualNofRxCh = parseDataList[pdIdx].antennaInfo.nofAntennas
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

# Get diagram type info string
def getDiagTypeInfoString(ptu2InputConf):
    if ptu2InputConf['diagTypeInfo']==1:
        ret='WITH diagram type info'
    else:
        ret ='WITHOUT diagram type info'
    return ret

def getNofAvailableTxAnt(tableMeasDataList):
    txAntList=[]
    for pdIdx in range(len(tableMeasDataList)):
        if tableMeasDataList[pdIdx].parseData.fileTitle.txAntFound == 1:
            actualTxAnt =tableMeasDataList[pdIdx].parseData.fileTitle.txAnt
            txAntList.append(actualTxAnt)
    txAntSet=set(txAntList)
    if len(txAntSet)==0:
        ret=1
    else:
        ret=len(txAntSet)
    return ret

def getElCritDataList(ptu2InputSetup,antennaList,angleSetupList,confTablesList):
    if ptu2InputSetup['elDiagCriteria']==1:
        angleSetupData=[]
        for antIdx in range(len(antennaList)):
            for angleSetupIdx in range(len(angleSetupList)):
                if angleSetupList[angleSetupIdx]["antennaType"]==antennaList[antIdx]:
                    angleSetupData.append(angleSetupList[angleSetupIdx])
    # To be continued on Monday ;D
    return  angleSetupData

def getAngSetupListPerAntennaType(antennaType,angleSetupList):
    outputList=[]
    for i in range(len(angleSetupList)):
        if angleSetupList[i].antennaType == antennaType:
            outputList.append(angleSetupList[i])
    return outputList
