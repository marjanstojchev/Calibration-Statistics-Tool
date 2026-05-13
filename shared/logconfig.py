from __future__ import annotations
import logging as log
import os
import enum
import sys
import errno


def createDirectory(outputPath: str) -> tuple[bool, str]:
    errorStr = 'Creating directory OK, path: '+ outputPath +'.'
    status=True
    if not os.path.isdir(outputPath):
        try:
            os.makedirs(outputPath)
            # myLogger.info(errorStr)
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                errorStr = str(exc.errno)
                status=False
                # myLogger.error(errorStr)
    return status, errorStr


class LoggerNames(enum.Enum):
    MainLoadData = 'main_loaddata_logger'
    AntennaSystemDiagrams = '0_ant_system_diagrams_logger'
    TxAntDiagrams   = 'tx_ant_diagrams_logger'
    AntennaPatterns = 'antpat_logger'

class LogFileNames(enum.Enum):
    MainLoadData =  '0_main_loaddata.log'
    AntennaSystemDiagrams = '0_ant_system_diagrams.log'
    TxAntDiagrams   = '0_tx_ant_diagrams.log'
    AntennaPatterns = '0_antenna_patterns.log'


mainLoggerName = 'main_logger'
mainLoggerFileName = '0_main_logger.log'

class CustomLogLevel(enum.Enum):
    Errors   = '0'
    Warnings = '1'
    WarningsAndInfos = '2'

class ConsoleOutput(enum.Enum):
    On  = '0'
    Off = '1'


consoleOutput  = ConsoleOutput.On
customLogLevel = CustomLogLevel.Errors

customLogFormatter = log.Formatter("%(asctime)s [%(custom_module_name)s] [%(levelname)-5.5s] %(message)s")
logFormatter = log.Formatter("%(asctime)s [%(module)s] [%(levelname)-5.5s] %(message)s")


class Logger():
    def __init__(self, loggerName: str) -> None:
        self.loggerName = loggerName
        self.logger = log.getLogger(self.loggerName)
        self.fileHandlerDict = dict()
        self.consoleHandler = 0
        self.tableHandler = 0
        self.logFormatter = 0
        # self.consoleHandler.setFormatter(self.logFormatter)
        # self.logger.addHandler(self.consoleHandler)
        self.logger.setLevel(log.DEBUG)

    def setLevel(self, logLevel: int) -> None:
        self.logger.setLevel(logLevel)

    # def info(self,message):
    #     self.logger.info(message)
    # def warning(self,message):
    #     self.logger.warning(message)
    # def error(self, message):
    #     self.logger.error(message)
    # def debug(self, message):
    #     self.logger.debug(message)

    def setFormatter(self, formatter: log.Formatter) -> None:
        self.logFormatter = formatter
    def addFileHandler(self, filePath: str, mode: str) -> tuple[int, str]:
        errorStatus = 0
        errorString = 'Logger: Status OK.'
        try:
            fileHandler = log.FileHandler(filePath, mode=mode)
            fileHandler.setFormatter(self.logFormatter)
            self.logger.addHandler(fileHandler)

            self.fileHandlerDict[filePath] = fileHandler
        except Exception as e:
            errorString = str(e)
            errorStatus = 1
        return errorStatus, errorString

    def removeConsoleHandler(self) -> None:
        self.logger.removeHandler(self.consoleHandler)

    def addConsoleHandler(self) -> None:
        for h in self.logger.handlers:
            if isinstance(h, log.StreamHandler) and not isinstance(h, log.FileHandler):
                return
        consoleHandler = log.StreamHandler()
        consoleHandler.setFormatter(self.logFormatter)
        self.logger.addHandler(consoleHandler)
        self.consoleHandler = consoleHandler

    def addTableHandler(self, handler: log.Handler) -> None:
        self.logger.addHandler(handler)
        self.tableHandler = handler


# basicDir = os.path.dirname(os.path.abspath(__file__))
basicDir = os.path.dirname(sys.argv[0])
basicDir = os.path.join(basicDir, '0_logFiles')
createDirectory(basicDir)


antSysDiagLogFilePath = os.path.join(basicDir, LogFileNames.AntennaSystemDiagrams.value)
antSysDiagLogger = Logger(LoggerNames.AntennaSystemDiagrams.value)
antSysDiagLogger.setLevel(log.DEBUG)
antSysDiagLogger.setFormatter(logFormatter)
antSysDiagLogger.addConsoleHandler()
antSysDiagLogger.customLogLevel=CustomLogLevel.WarningsAndInfos
# errorStatus,errorSting=  mainLogger.addFileHandler(mainLogFilePath,'w')

antPatLogFilePath = os.path.join(basicDir, LogFileNames.AntennaPatterns.value)
antPatLogger = Logger(LoggerNames.AntennaPatterns.value)
antPatLogger.setFormatter(logFormatter)
antPatLogger.addConsoleHandler()
antPatLogger.setLevel(log.INFO)
antPatLogger.customLogLevel=CustomLogLevel.WarningsAndInfos

txAntDiagLogFilePath = os.path.join(basicDir, LogFileNames.TxAntDiagrams.value)
txAntDiagLogger = Logger(LoggerNames.TxAntDiagrams.value)
txAntDiagLogger.setFormatter(logFormatter)
txAntDiagLogger.addConsoleHandler()
txAntDiagLogger.setLevel(log.INFO)
txAntDiagLogger.customLogLevel=CustomLogLevel.WarningsAndInfos

mainLoadDataLogFilePath = os.path.join(basicDir, LogFileNames.MainLoadData.value)
mainLoadDataLogger = Logger(LoggerNames.MainLoadData.value)
mainLoadDataLogger.setFormatter(logFormatter)
mainLoadDataLogger.addConsoleHandler()
mainLoadDataLogger.setLevel(log.DEBUG)
mainLoadDataLogger.customLogLevel=CustomLogLevel.WarningsAndInfos

# Adapter for parseProtocols — exposes the standard logging.Logger interface
# (log.error / log.info / log.warning) expected by that module
logAdapter_PP = mainLoadDataLogger.logger

 ######   ###
  #######   ##
 ######   ###

