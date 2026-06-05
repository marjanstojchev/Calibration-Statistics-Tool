from __future__ import annotations
import os
import protocolsTest as protocolfilter
import pyside_qtgui as qt
from shared import safeparse as sp
import logconfig
import protocolsTest as protocolFilter
# loadDataLogger=logconfig.loadDataLogger
parseDataLogger=logconfig.mainLoadDataLogger
parseDataLog=logconfig.mainLoadDataLogger.logger

# In headless mode (API), qt.mainLogTableHandler won't exist.
# Catch the error and continue.
try:
    logconfig.mainLoadDataLogger.addTableHandler(qt.mainLogTableHandler)
except AttributeError:
    pass  # Running in headless mode (API), no GUI handlers available

errorStatus, errorSting = logconfig.mainLoadDataLogger.addFileHandler(logconfig.mainLoadDataLogFilePath, 'w+')
if errorStatus ==1:
    parseDataLog.warning(errorSting)



protocolpathdict = {
    'protocolPathTypeDictList': [],

}
acceptedprotocolpathdict = {
    'emptyProtList': [],
    'errorProtList': [],
    'abbortCritProtList': [],
    'limitExceededProtList': []

}
filteredprotocolpathdict = {
    'protocolpathlist': [],
}

parsedprotdict = {
    'protocolPathTypeDictList': [],
}

prottobeparseddict = {
    'protocolPathTypeDictList': [],
}


def getprotcols(abspath: str, LatestProtocol: bool, BurnInStart: bool, EOLError: bool, EOLAbbortCriterian: bool, EOLMeasLimitsExceeded: bool, allprotocolspathnameslist: list) -> tuple:
    busefileswitherror = EOLError
    busefilesabbortcriterion = EOLAbbortCriterian
    busefileswithlimitsexceeded = EOLMeasLimitsExceeded

    # erste infos ob fehler, abbruchkriterien, messgrenzen ueberschreitungen
    preparseinfoprotocolslist, emptyprotocolslist, errorprotocolslist, abbortcritprotocolslist, limitexceededprotocolslist = protocolfilter.ProtocolInfoClass.PreParseProtcols(
        allprotocolspathnameslist)
    # filtere liste, nur die gewuenschten protokolle in liste

    acceptedprotocolslist, filteredprotocolslist = protocolfilter.ProtocolInfoClass.FilterProtocols(
        preparseinfoprotocolslist, busefileswitherror, busefilesabbortcriterion, busefileswithlimitsexceeded)

    if LatestProtocol:
        acceptedprotocolslist = protocolFilter.ProtocolInfoClass.FilterNewProtocols(acceptedprotocolslist)


    accprotlist = []

    filteredprotocolslist = [
        filteredprotocolslist[i].PathName for i in range(len(filteredprotocolslist))]

    accerrorprotlist = []
    accabbortcritprotlist = []
    acclimitexceededprotlist = []

    for cpreparseinfo in acceptedprotocolslist:
        strpathonly, strfilenameonly = os.path.split(cpreparseinfo.PathName)
        parseDataLog.info(cpreparseinfo.PathName)


        # if len(ptu2FilesListDict['ptu2FilesList'])!=0 or len(txAntDiagListDict['txAntDiagList'])!=0:


        if busefileswitherror and cpreparseinfo.bErrorOccured:
            accerrorprotlist.append(cpreparseinfo.PathName)

        if busefilesabbortcriterion and cpreparseinfo.bAbortCriterion:
            accabbortcritprotlist.append(cpreparseinfo.PathName)

        if busefileswithlimitsexceeded and cpreparseinfo.bLimitExceeded:
            acclimitexceededprotlist.append(cpreparseinfo.PathName)

        accprotlist.append(cpreparseinfo.PathName)

        # elif len(ptu2FilesListDict['ptu2FilesList'])!=0 and:
    return accprotlist, accerrorprotlist, accabbortcritprotlist, acclimitexceededprotlist, filteredprotocolslist

def importprotocolsdirpath(abspath: str, LatestProtocol: bool, BurnInStart: bool, EOLError: bool, EOLAbbortCriterian: bool, EOLMeasLimitsExceeded: bool) -> None:
    protocoldirpath = abspath
    protocolfileslist = protocolfilter.ProtocolInfoClass.GetAllProtocolsList(
        protocoldirpath)

    for protFileIdx in range(len(protocolfileslist)):

        protocolfileslist[protFileIdx] = protocolfileslist[protFileIdx].replace("\\", "/")


    filterprotocoldata(abspath, LatestProtocol, BurnInStart, EOLError, EOLAbbortCriterian, EOLMeasLimitsExceeded, protocolfileslist)



def getprotpathtypedictlist(protocolPathList: list, BurnInStart: bool) -> list:

    outputList = []

    for protocol in protocolPathList:
    # if qt.parseProtBurnInCalGroup.checkedId() == 0:
        typeMuster   = 'Gen26_UseBurnInMeas[1]'
        filterMuster = '(12a) BurnIn Start Check results:'
        tempDict = dict()
        tempDict['protocolPath'] = protocol
        tempDict['type'] = 'Unclear'
        # Filter the 'BurnIn At Start' protocols
        filterProt = False
        try:
            with open(protocol, 'r') as protocolFile:

                content = protocolFile.readlines()

                lineNr = 0

                for line in content:
                    lineNr += 1
                    line = line.strip()

                    if line.startswith(typeMuster):
                        line = line.replace(' ','')
                        linePartsList = line.split(';')
                        if linePartsList[0] == typeMuster:
                            tempVal = -1
                            
                            if sp.checkInt(linePartsList[1]):

                                tempVal = int(linePartsList[1])

                            else:
                                parseDataLog.error('Invalid value for protocol BurnIn/Calibration auto-recognition: '+linePartsList[1]+'.')

                            if tempVal == 0:

                                tempDict['type'] = 'Calibration'

                            elif tempVal == 3:

                                tempDict['type'] = 'BurnIn'

                            else:
                                tempDict['type'] = 'Unclear'

                        else:
                            tempDict['type'] = 'Unclear'
                    
                    if line == filterMuster:
                        filterProt = True
                        break
            
            # Do no add 'BurnIn At Start' protocols filter
            if not BurnInStart:
                if tempDict['type'] == 'BurnIn':
                    if not filterProt:
                        outputList.append(tempDict)
                else:
                    outputList.append(tempDict)
            # Add protocol files without any filter
            else:
                outputList.append(tempDict)

        except Exception as e:
            parseDataLog.error('Opening protocol file: ' + str(e) + '.')

    return outputList



def filterprotocoldata(abspath: str, LatestProtocol: bool, BurnInStart: bool, EOLError: bool, EOLAbbortCriterian: bool, EOLMeasLimitsExceeded: bool, protocolfileslist: list) -> None:


    if len(protocolfileslist) == 0:
        return

    auxprotpathlist = []

    for protdict in protocolpathdict['protocolPathTypeDictList']:
        auxprotpathlist.append(protdict['protocolPath'])

    # protNotPresent=0
    protnonreplist = []
    for protocolfilepath in protocolfileslist:
        if protocolfilepath not in auxprotpathlist:
            protnonreplist.append(protocolfilepath)

    acceptedcritprotlist, accerrorprotlist, accabbortcritprotlist, acclimitexceededprotlist, filteredprotocollist = getprotcols(
        abspath, LatestProtocol, BurnInStart, EOLError, EOLAbbortCriterian, EOLMeasLimitsExceeded, protnonreplist)

    acceptedprotocolpathdict['errorProtList'] += accerrorprotlist
    acceptedprotocolpathdict['abbortCritProtList'] += accabbortcritprotlist
    acceptedprotocolpathdict['limitExceededProtList'] += acclimitexceededprotlist

    acceptedprotpathtypedictlist = getprotpathtypedictlist(
        acceptedcritprotlist, BurnInStart)


    protocolpathdict['protocolPathTypeDictList'] += acceptedprotpathtypedictlist

    auxprotpathlist = []

    for protdict in protocolpathdict['protocolPathTypeDictList']:
        auxprotpathlist.append(protdict['protocolPath'])

    for protocolfilepath in filteredprotocollist:
        if protocolfilepath not in filteredprotocolpathdict['protocolpathlist']:

            filteredprotocolpathdict['protocolpathlist'].append(
                protocolfilepath)

    filteredprotocolpathdict['protocolpathlist'] = [
        protocolfilepath for protocolfilepath in filteredprotocolpathdict['protocolpathlist'] if protocolfilepath not in auxprotpathlist]

    auxparsedprotpathlist = []

    for protdict in parsedprotdict['protocolPathTypeDictList']:
        auxparsedprotpathlist.append(protdict['protocolPath'])


# Class containing the loaded data, including the parsed PTU2 files list, error status data, and meta data
class loadprotocol:
    def __init__(self, abspath: str, LatestProtocol: bool, BurnInStart: bool, EOLError: bool, EOLAbbortCriterian: bool, EOLMeasLimitsExceeded: bool) -> None:
        self.loaddata(abspath, LatestProtocol, BurnInStart, EOLError, EOLAbbortCriterian, EOLMeasLimitsExceeded)
        self.protocolpathdict = protocolpathdict

    # Load parsed data for a specific search path
    def loaddata(self, abspath: str, LatestProtocol: bool, BurnInStart: bool, EOLError: bool, EOLAbbortCriterian: bool, EOLMeasLimitsExceeded: bool) -> None:
        clear()
        importprotocolsdirpath(abspath, LatestProtocol, BurnInStart, EOLError, EOLAbbortCriterian, EOLMeasLimitsExceeded)

def clear() -> None:
    global protocolpathdict
    protocolpathdict = {
        'protocolPathTypeDictList': [],

    }
    global acceptedprotocolpathdict
    acceptedprotocolpathdict = {
        'emptyProtList': [],
        'errorProtList': [],
        'abbortCritProtList': [],
        'limitExceededProtList': []

    }
    global filteredprotocolpathdict
    filteredprotocolpathdict = {
        'protocolpathlist': [],
    }
    global parsedprotdict
    parsedprotdict = {
        'protocolPathTypeDictList': [],
    }
    global prottobeparseddict
    prottobeparseddict = {
        'protocolPathTypeDictList': [],
    }

