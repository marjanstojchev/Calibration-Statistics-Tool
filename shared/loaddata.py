import os
import parsePTU2data as pd
import enum
import logconfig as log


myLogger = log.mainLoadDataLogger.logger


# absPath=r'C:\Arbeit\ProtokollBsp\UMRR-11.00.04-0002B4ED'
absPath=r'C:\Arbeit\ProtokollBsp'

# Search path meta data
class SearchPath(enum.Enum):
    Invalid=0
    Folder=1
    Protocol=2
    File=3
    RootFolder=4
class AbsPathType(enum.Enum):
    Path=0
    List=1
    Tuple=2

# Class containing the loaded data, including the parsed PTU2 files list, error status data, and meta data
class LoadData:
    def __init__(self,absPath,useSensorMuster,sensorMusterList):
        self.searchPath = SearchPath.Invalid
        self.parseDataList = []
        self.sensorMusterList=sensorMusterList
        self.useSensorMuster=useSensorMuster
        self.errorString=''
        self.errorStringList=[]
        self.invalidPath=0
        self.invalidPathString = '\n Invalid path given! Use files with "_Protocol.text", "_PTU2.txt" endings, and make sure the path is valid.'
        self.counter = 0
        self.validFilesCounter=0
        self.loadData(absPath)
        self.parseLogging()

    # Logging for the parsing errors
    def parseLogging(self):
        errorString=''
        if self.counter >0:
            for i in range(len(self.errorStringList)):
                errorString+=self.errorStringList[i]
            myLogger.error('Parsing errors: '+errorString)

   # Formating function for the parsing errors
    def addParseDataError(self,parseData):
        logStr = ""
        for errStrIdx in range(len(parseData.errorList)):
            logStr = logStr + "\n" + parseData.errorList[errStrIdx]
        return logStr


    def proceessPath(self,absPath):
        ptu2PathEnd = "_PTU2.txt"
        protocolPathEnd = '_Protocol.txt'

        pathParts = os.path.split(absPath)

        if pathParts[1].endswith(ptu2PathEnd):
            if 'Diff' not in pathParts[1] and 'NotOk' not in pathParts[1]:
                parseData = pd.PTU2ParseData()
                parseData.parseFile(absPath,self.useSensorMuster,self.sensorMusterList)
                self.searchPath = SearchPath.File
                if parseData.bDataValid == False:
                    self.counter += 1
                    self.errorString = self.addParseDataError(parseData)
                    self.errorStringList.append(self.errorString)
                    # myLogger.error(self.errorString)
                else:
                    self.parseDataList.append(parseData)
                    self.validFilesCounter += 1

        elif pathParts[1].endswith(protocolPathEnd):
            pathError = 0
            lookFurther = 0
            self.searchPath = SearchPath.Protocol
            for item in os.listdir(pathParts[0]):
                if item.endswith(pathParts[1]):
                    lookFurther = 1

            if lookFurther == 1:
                for item in os.listdir(pathParts[0]):
                    if item.endswith(ptu2PathEnd):
                        if 'Diff' not in item and 'NotOk' not in item:
                            # Set path to current file
                            # pathToFile = pathParts[0] + "\\" + item
                            pathToFile = os.path.join(pathParts[0], item)
                            parseData = pd.PTU2ParseData()
                            # obj=parseFile(pathToFile,obj)
                            parseData.parseFile(pathToFile,self.useSensorMuster,self.sensorMusterList)
                            if parseData.bDataValid == False:
                                self.counter += 1
                                self.errorString = self.addParseDataError(parseData)
                                self.errorStringList.append(self.errorString)
                                # myLogger.error(self.errorString)
                            else:
                                self.validFilesCounter +=1
                                self.parseDataList.append(parseData)
            else:
                pathError = 1

            if pathError == 1:
                self.invalidPath = 1
                self.invalidPathString = absPath + self.invalidPathString
                # myLogger.error(self.errorString)
        else:

            if os.path.isdir(absPath):
                self.searchPath = SearchPath.Folder
                containsPtu2 = 0

                for dirName, subdirList, fileList in os.walk(absPath):
                    subdirList[:] = [d for d in subdirList if 'NotOk' not in d]
                    # Sort fileList to ensure consistent order (preserves alphabetical/chronological order)
                    fileList.sort()
                    for fileName in fileList:
                        if fileName.endswith(ptu2PathEnd):
                            if 'Diff' not in fileName and 'NotOk' not in fileName:

                                containsPtu2 = 1
                                # Set path to current file
                                # pathToFile = subPath + "\\" + file

                                pathToFile = os.path.join(dirName, fileName)

                                parseData = pd.PTU2ParseData()
                                parseData.parseFile(pathToFile,self.useSensorMuster,self.sensorMusterList)
                                if parseData.bDataValid == False:
                                    self.counter += 1
                                    self.errorString = self.addParseDataError(parseData)
                                    self.errorStringList.append(self.errorString)
                                    # myLogger.error(self.errorString)
                                else:
                                    self.validFilesCounter += 1
                                    self.parseDataList.append(parseData)

                if containsPtu2 == 0:
                    self.invalidPath = 1
                    self.invalidPathString = absPath + self.invalidPathString
                    # myLogger.error(self.errorString)
            else:
                self.invalidPath = 1
                self.invalidPathString = absPath + self.invalidPathString
            # myLogger.error(self.errorString)

    # Load parsed data for a specific search path
    def loadData(self,absPath):

        absPathType=AbsPathType.Path

        if isinstance(absPath, tuple):
            absPathType=AbsPathType.Tuple

        elif isinstance(absPath, list):
            absPathType=AbsPathType.List

        if absPathType==AbsPathType.Path:
            self.proceessPath(absPath)

        elif absPathType == AbsPathType.List:
              #absPath=str(absPath[0])
            absPathLen = len(absPath)
            for fileIdx in range (absPathLen):
                absPathInstance = str(absPath[fileIdx])
                self.proceessPath(absPathInstance)


        elif absPathType==AbsPathType.Tuple:
            absPathLen = len(absPath)
            for fileIdx in range (absPathLen):
                absPathInstance = str(absPath[fileIdx])
                self.proceessPath(absPathInstance)



# l=LoadData(absPath)
# a=getNofDiagrams(l)
# sensorList=getSensorList(l)
# y=6
