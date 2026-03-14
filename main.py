import os
import sys

_root = os.path.dirname(os.path.abspath(__file__))
for _subdir in ['shared', 'ui', 'system_diagrams', 'tx_diagrams', 'antenna_patterns']:
    _path = os.path.join(_root, _subdir)
    if _path not in sys.path:
        sys.path.insert(0, _path)

import loaddata as ld
import parsePTU2data as parsePtu2
import parseTxAntDiagramData as parseTxAntDiag
import logconfig
import data_processing as dp
from shared import safeparse as sp
from shared.parse_helpers import (
    filter_protocol_file_lists,
    merge_into_parsed_dicts,
    deduplicate_protocol_list,
    walk_protocol_files,
    update_filtered_protocol_list,
    collect_unparsed_protocols,
)
import load_TxAntData as ld_txantdiag
import auxiliary as aux
import protocolsTest as protocolFilter
import PySide6


dirname = os.path.dirname(PySide6.__file__)
print(dirname)
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
print(plugin_path)
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path

import pyside_qtgui as qt
from PySide6.QtWidgets import QTableWidgetItem
import AntennaSystemDiagrams as antSysDiag
import TxAntDiagrams as txAntDiag
import antpat_v5_main_v3 as antPat1

parseDataLogger = logconfig.mainLoadDataLogger
parseDataLog = logconfig.mainLoadDataLogger.logger
logconfig.mainLoadDataLogger.addTableHandler(qt.mainLogTableHandler)
errorStatus, errorSting = logconfig.mainLoadDataLogger.addFileHandler(logconfig.mainLoadDataLogFilePath, 'w+')
if errorStatus == 1:
    parseDataLog.warning(errorSting)


sysDiagLog = logconfig.antSysDiagLogger.logger
sysDiagLogger = logconfig.antSysDiagLogger
errorStatus, errorSting = logconfig.antSysDiagLogger.addFileHandler(logconfig.antSysDiagLogFilePath, 'w+')
if errorStatus == 1:
    sysDiagLog.warning(errorSting)
logconfig.antSysDiagLogger.addTableHandler(qt.mainLogTableHandler)


txAntDiagLogger = logconfig.txAntDiagLogger
txAntDiagLog = logconfig.txAntDiagLogger.logger
errorStatus, errorSting = logconfig.txAntDiagLogger.addFileHandler(logconfig.txAntDiagLogFilePath, 'w+')
if errorStatus == 1:
    txAntDiagLog.warning(errorSting)
logconfig.txAntDiagLogger.addTableHandler(qt.mainLogTableHandler)


antpatLogger = logconfig.antPatLogger
antpatLog = logconfig.antPatLogger.logger
errorStatus, errorSting = logconfig.antPatLogger.addFileHandler(logconfig.antPatLogFilePath, 'w+')
if errorStatus == 1:
    antpatLog.warning(errorSting)
logconfig.antPatLogger.addTableHandler(qt.mainLogTableHandler)


sysDiagFilePathDict = {
    'filePathList':[]
}
txDiagfilePathDict = {
    'filePathList': []
}


protocolPathDict={
    'protocolPathTypeDictList':[],
}
acceptedProtocolPathDict={
    'emptyProtList':[],
    'errorProtList':[],
    'abbortCritProtList':[],
    'limitExceededProtList':[]
}
filteredProtocolPathDict = {
    'protocolPathList': [],
}
parsedProtDict = {
    'protocolPathTypeDictList':[],
}
protToBeParsedDict = {
    'protocolPathTypeDictList':[],
}
sysDiagParsedDataDict={
    'parsedDataList':[]
}
separatePtu2ParsedDataDict={
    'parsedDataList': []
}
separatePtu2FailedDataDict={
    'parsedDataList': []
}
txAntDiagParsedDataDict={
    'parsedDataList': []
}
separateTxAntDiagParsedDataDict={
    'parsedDataList': []
}
separateTxAntDiagFailedDataDict={
    'parsedDataList': []
}


burnInProtocolPathDict={
    'protocolPathList':[]
}
calProtocolPathDict = {
    'protocolPathList': []
}

##########

qt.parseProtSensorMusterCheckBox.setChecked(False)
qt.parseProtSensorMusterLEdit.setEnabled(False)
qt.parseProtSensorMusterLabel.setEnabled(False)

antSysDiag.plotSetup['useSensorMuster'] = 0
antPat1.setup['useSensorMuster'] = 0
txAntDiag.plotSetup['useSensorMuster'] = 0


def parseProtSensorMusterClick():
    state = qt.parseProtSensorMusterCheckBox.isChecked()
    if state == 1:
        qt.parseProtSensorMusterLEdit.setEnabled(True)
        qt.parseProtSensorMusterLabel.setEnabled(True)
        antSysDiag.plotSetup['useSensorMuster'] = 1
        antPat1.setup['useSensorMuster'] = 1
        txAntDiag.plotSetup['useSensorMuster'] = 1
    else:
        qt.parseProtSensorMusterLEdit.setEnabled(False)
        qt.parseProtSensorMusterLabel.setEnabled(False)
        antSysDiag.plotSetup['useSensorMuster'] = 0
        antPat1.setup['useSensorMuster'] = 0
        txAntDiag.plotSetup['useSensorMuster'] = 0
    parseDataLog.debug('plotSetp: ' + str(antSysDiag.plotSetup))


qt.parseProtSensorMusterCheckBox.stateChanged.connect(parseProtSensorMusterClick)

###
qt.parseProtBurnInCalGroupRadio1.setChecked(True)
qt.parseProtBurnInCalGroupRadio2.setChecked(False)
qt.parseProtBurnInCalGroupRadio3.setChecked(False)


### Protocols Data
qt.parseProtProtDataBurnInInclCheckBox.setChecked(True)
qt.parseProtProtDataBurnInExtCheckBox.setChecked(False)


qt.parseProtProtDataCalInclCheckBox.setChecked(True)
qt.parseProtProtDataCalExtCheckBox.setChecked(False)


qt.parseProtProtDataInFileBurnInLabel.setToolTip(aux.burnInLimitsFilePath)
qt.parseProtProtDataInFileBurnInLabel.setText(aux.burnInLimitsFilePath)


qt.parseProtProtDataInFileCalLabel.setToolTip(aux.calLimitsFilePath)
qt.parseProtProtDataInFileCalLabel.setText(aux.calLimitsFilePath)


qt.parseProtProtDataLimGroupsBurnInLabel.setToolTip(aux.burnInLimGroupsFilePath)
qt.parseProtProtDataLimGroupsBurnInLabel.setText(aux.burnInLimGroupsFilePath)


qt.parseProtProtDataLimGroupsCalLabel.setToolTip(aux.calLimGroupsFilePath)
qt.parseProtProtDataLimGroupsCalLabel.setText(aux.calLimGroupsFilePath)


qt.statsInputConfPathLabel.setText(aux.statsinputconffilepath)
qt.statsInputConfPathLabel.setToolTip(aux.statsinputconffilepath)

qt.parseProtProtDataInFileBurnInPushBtn.clicked.connect(lambda: loadBurnInInputLimitsFile())
qt.parseProtProtDataInFileCalPushBtn.clicked.connect(lambda : loadCalInputLimitsFile())
qt.parseProtProtDataLimGroupsBurnInPushBtn.clicked.connect(lambda: loadBurnInLimitsGroupsFile())
qt.parseProtProtDataLimGroupsCalPushBtn.clicked.connect(lambda : loadCalLimitsGroupsFile())


def importProtocolsDirPath(protocolPathDict, acceptedProtocolPathDict, filteredProtocolPathDict, sysDiagFilePathDict, txDiagfilePathDict, parsedProtDict, protToBeParsedDict, parseProtSysDiagCheckBox, parseProtTxAntDiagCheckBox):
    protocolDirPath = ''
    if qt.parseProtImportProtDirPathFDialog.exec_():
        protocolDirPath = qt.parseProtImportProtDirPathFDialog.selectedFiles()[0]
    protocolFilesList = protocolFilter.ProtocolInfoClass.GetAllProtocolsList(protocolDirPath)

    for protFileIdx in range(len(protocolFilesList)):

        protocolFilesList[protFileIdx]=protocolFilesList[protFileIdx].replace('\\', '/')


    fillInProtocolData(protocolFilesList, acceptedProtocolPathDict, filteredProtocolPathDict, protocolPathDict, sysDiagFilePathDict, txDiagfilePathDict, parsedProtDict, protToBeParsedDict, parseProtSysDiagCheckBox, parseProtTxAntDiagCheckBox)


def importProtocolsFileList(protocolPathDict, acceptedProtocolPathDict, filteredProtocolPathDict, sysDiagFilePathDict, txDiagfilePathDict, parsedProtDict, protToBeParsedDict, parseProtSysDiagCheckBox, parseProtTxAntDiagCheckBox):

    protocolFilesList = []
    if qt.parseProtImportProtFListFDialog.exec_():
        protocolFilesList = qt.parseProtImportProtFListFDialog.selectedFiles()

    fillInProtocolData(protocolFilesList, acceptedProtocolPathDict, filteredProtocolPathDict, protocolPathDict, sysDiagFilePathDict, txDiagfilePathDict, parsedProtDict, protToBeParsedDict, parseProtSysDiagCheckBox, parseProtTxAntDiagCheckBox)


def getProtPathTypeDictList(protocolPathList):

    outputList = []

    for protocol in protocolPathList:
        if qt.parseProtBurnInCalGroup.checkedId() == 0:
            typeMuster   = 'Gen26_UseBurnInMeas[1]'
            filterMuster = '(12a) BurnIn Start Check results:'
            tempDict = dict()
            tempDict['protocolPath'] = protocol
            tempDict['type'] = 'Unclear'
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
                
                if not qt.parseProtBurnStartCheckBox.isChecked():
                    if tempDict['type'] == 'BurnIn':
                        if not filterProt:
                            outputList.append(tempDict)
                    else:
                        outputList.append(tempDict)
                else:
                    outputList.append(tempDict)

            except Exception as e:
                parseDataLog.error('Opening protocol file: ' + str(e) + '.')

        elif qt.parseProtBurnInCalGroup.checkedId() == 1:

            tempDict = dict()
            tempDict['protocolPath'] = protocol
            tempDict['type'] = 'BurnIn'
            outputList.append(tempDict)

        elif qt.parseProtBurnInCalGroup.checkedId() == 2:

            tempDict = dict()
            tempDict['protocolPath'] = protocol
            tempDict['type'] = 'Calibration'
            outputList.append(tempDict)

    return outputList


def _update_protocol_dicts(
    accepted_crit_prot_list: list,
    sys_diag_file_path_dict_temp: list,
    tx_diag_file_path_dict_temp: list,
    filtered_protocol_list: list,
    acc_error_prot_list: list,
    acc_abort_crit_prot_list: list,
    acc_limit_exceeded_prot_list: list,
    accepted_protocol_path_dict: dict,
    filtered_protocol_path_dict: dict,
    protocol_path_dict: dict,
    parsed_prot_dict: dict,
    prot_to_be_parsed_dict: dict,
) -> list:
    """Merge getprotcols results into the shared state dicts.

    Updates accepted/filtered/parsed dicts and returns the list of protocol
    path-type dicts that still need to be parsed.
    """
    accepted_protocol_path_dict['errorProtList']         += acc_error_prot_list
    accepted_protocol_path_dict['abbortCritProtList']    += acc_abort_crit_prot_list
    accepted_protocol_path_dict['limitExceededProtList'] += acc_limit_exceeded_prot_list

    accepted_prot_path_type_dict_list = getProtPathTypeDictList(accepted_crit_prot_list)

    protocol_path_dict['protocolPathTypeDictList'] += accepted_prot_path_type_dict_list

    accepted_path_set = {d['protocolPath'] for d in protocol_path_dict['protocolPathTypeDictList']}
    update_filtered_protocol_list(filtered_protocol_list, filtered_protocol_path_dict, accepted_path_set)

    parseDataLog.info('Filtered Protocol List:')
    for elem in filtered_protocol_path_dict['protocolPathList']:
        parseDataLog.info(elem)

    already_parsed = collect_unparsed_protocols(
        accepted_prot_path_type_dict_list, parsed_prot_dict, prot_to_be_parsed_dict
    )
    for path in already_parsed:
        parseDataLog.info('Protocol is already parsed: ' + path)

    parseDataLog.info('Num. of Total Accepted Protocols: ' + str(len(protocol_path_dict['protocolPathTypeDictList'])))
    parseDataLog.info('Num. of System Diagram Files: ' + str(len(sys_diag_file_path_dict_temp)))

    return accepted_prot_path_type_dict_list


def _populate_sel_prot_table(
    accepted_prot_path_type_dict_list: list,
    sys_diag_file_path_dict_temp: list,
    tx_diag_file_path_dict_temp: list,
) -> None:
    """Set up the selected-protocols table columns and insert one row-group per protocol."""
    header = qt.parseProtSelProtTable.horizontalHeader()
    header.setSectionResizeMode(0, qt.QHeaderView.ResizeMode.Interactive)
    qt.parseProtSelProtTable.setColumnWidth(0, 400)
    header.setSectionResizeMode(1, qt.QHeaderView.ResizeMode.Interactive)
    qt.parseProtSelProtTable.setColumnWidth(1, 110)
    header.setSectionResizeMode(2, qt.QHeaderView.ResizeMode.Interactive)
    header.setSectionResizeMode(3, qt.QHeaderView.ResizeMode.Stretch)

    ref_row_idx = qt.parseProtSelProtTable.rowCount()

    for prot_idx, entry in enumerate(accepted_prot_path_type_dict_list):
        protocol_path           = entry['protocolPath']
        protocol_type           = entry['type']
        sys_diag_per_prot       = sys_diag_file_path_dict_temp[prot_idx]['ptu2FilesList']
        tx_ant_diag_per_prot    = tx_diag_file_path_dict_temp[prot_idx]['txAntDiagList']
        prot_table_data         = dp.ProtocolsTableData(protocol_path, sys_diag_per_prot, tx_ant_diag_per_prot)

        if sys_diag_per_prot or tx_ant_diag_per_prot:
            for rel_row in range(prot_table_data.biggerListLength):
                row_idx = rel_row + ref_row_idx
                qt.parseProtSelProtTable.insertRow(row_idx)
                qt.parseProtSelProtTable.setItem(
                    row_idx, 0,
                    QTableWidgetItem(prot_table_data.protocolPath if rel_row == 0 else ''),
                )
                qt.parseProtSelProtTable.setItem(row_idx, 1, QTableWidgetItem(protocol_type))
                qt.parseProtSelProtTable.setItem(row_idx, 2, QTableWidgetItem(prot_table_data.sysDiagFilePathShapedList[rel_row]))
                qt.parseProtSelProtTable.setItem(row_idx, 3, QTableWidgetItem(prot_table_data.txAntDiagFilePathShapedList[rel_row]))

            for span_entry in prot_table_data.smallerListRowSpanList:
                qt.parseProtSelProtTable.setSpan(
                    span_entry['spanStart'] + ref_row_idx,
                    prot_table_data.smallerListColIdx,
                    span_entry['spanCount'],
                    1,
                )

            qt.parseProtSelProtTable.setSpan(ref_row_idx, 0, prot_table_data.biggerListLength, 1)
            qt.parseProtSelProtTable.setSpan(ref_row_idx, 1, prot_table_data.biggerListLength, 1)
            ref_row_idx += prot_table_data.biggerListLength
        else:
            row_idx = prot_idx + ref_row_idx
            qt.parseProtSelProtTable.insertRow(row_idx)
            qt.parseProtSelProtTable.setItem(row_idx, 0, QTableWidgetItem(protocol_path))
            qt.parseProtSelProtTable.setItem(row_idx, 1, QTableWidgetItem(protocol_type))


def fillInProtocolData(
    protocolFilesList: list,
    acceptedProtocolPathDict: dict,
    filteredProtocolPathDict: dict,
    protocolPathDict: dict,
    sysDiagFilePathDict: dict,
    txDiagfilePathDict: dict,
    parsedProtDict: dict,
    protToBeParsedDict: dict,
    parseProtSysDiagCheckBox,
    parseProtTxAntDiagCheckBox,
) -> None:
    """Load and validate new protocol files; update all state dicts and the UI table."""
    qt.parseProtTableTabWidget.setCurrentIndex(0)

    if not protocolFilesList:
        return

    qt.parseProtProgresLabel.setText('Loading...')
    qt.parseProtProgresBar.reset()

    if not protocolPathDict['protocolPathTypeDictList']:
        qt.parseProtSelProtTable.setRowCount(0)

    protNonRepList = deduplicate_protocol_list(
        protocolFilesList, protocolPathDict['protocolPathTypeDictList']
    )
    for p in set(protocolFilesList) - set(protNonRepList):
        parseDataLog.info('Protocol is already imported: ' + p)

    sysDiagFilePathDictTemp, txDiagfilePathDictTemp, acceptedCritProtList, accErrorProtList, accAbbortCritProtList, accLimitExceededProtList, filteredProtocolList = getprotcols(
        protNonRepList, parseProtSysDiagCheckBox.isChecked(), parseProtTxAntDiagCheckBox.isChecked()
    )

    if sysDiagFilePathDictTemp:
        sysDiagFilePathDict['filePathList'] += sysDiagFilePathDictTemp
    if txDiagfilePathDictTemp:
        txDiagfilePathDict['filePathList'] += txDiagfilePathDictTemp

    acceptedProtPathTypeDictList = _update_protocol_dicts(
        acceptedCritProtList,
        sysDiagFilePathDictTemp, txDiagfilePathDictTemp,
        filteredProtocolList,
        accErrorProtList, accAbbortCritProtList, accLimitExceededProtList,
        acceptedProtocolPathDict, filteredProtocolPathDict,
        protocolPathDict, parsedProtDict, protToBeParsedDict,
    )

    _populate_sel_prot_table(acceptedProtPathTypeDictList, sysDiagFilePathDictTemp, txDiagfilePathDictTemp)

    if protToBeParsedDict['protocolPathTypeDictList']:
        qt.parseProtProgresBar.setRange(0, len(protToBeParsedDict['protocolPathTypeDictList']))
        qt.parseProtProgresBar.setValue(0)
        qt.parseProtProgresBar.setFormat(
            f'{qt.parseProtProgresBar.value()} / {len(protToBeParsedDict["protocolPathTypeDictList"])}'
        )
        progBarLabelStr = (
            f'Protocols to be parsed: {len(protToBeParsedDict["protocolPathTypeDictList"])}'
            f' / {len(protocolPathDict["protocolPathTypeDictList"])}. '
        )
        qt.parseProtProgresLabel.setText(progBarLabelStr)
    else:
        qt.parseProtProgresLabel.setText('No new protocols Loaded.')

    total = len(protocolPathDict['protocolPathTypeDictList'])
    qt.parseProtLoadedProtLabel.setText(
        qt.parseProtLoadedProtStr
        + f'{total} / {len(filteredProtocolPathDict["protocolPathList"]) + total}'
    )
    qt.parseProtEolErrorLabel.setText(
        qt.parseProtEolErrorStr
        + f'{len(acceptedProtocolPathDict["errorProtList"])} / {total}'
    )
    qt.parseProtAbbortCritLabel.setText(
        qt.parseProtAbbortCritStr
        + f'{len(acceptedProtocolPathDict["abbortCritProtList"])} / {total}'
    )
    qt.parseProtMeasLimitsExcLabel.setText(
        qt.parseProtMeasLimitsExcStr
        + f'{len(acceptedProtocolPathDict["limitExceededProtList"])} / {total}'
    )
    qt.parseProtParsedLoadedProtLabel.setText(
        qt.parseProtParsedLoadedProtStr
        + f'{len(parsedProtDict["protocolPathTypeDictList"])} / {total}'
    )


def addAndParsePtu2Files(sysDiagParsedDataDict, separatePtu2ParsedDataDict, separatePtu2FailedDataDict):

    qt.parseProtTableTabWidget.setCurrentIndex(2)

    ptu2FilesList = []
    if qt.parseProtAddAndParsePtu2FDialog.exec_():
        ptu2FilesList = qt.parseProtAddAndParsePtu2FDialog.selectedFiles()
        ptu2FilesList.sort()

    for item in ptu2FilesList:
        parseDataLog.info(item)

    ptu2FailedDataList = []
    ptu2ParsedDataList = []
    for ptu2 in ptu2FilesList:
        parseData = parsePtu2.PTU2ParseData()
        parseData.parseFile(ptu2,antSysDiag.plotSetup['useSensorMuster'],antSysDiag.plotSetup['sensorMusterList'])
        if parseData.bDataValid == False:
            ptu2FailedDataList.append(parseData)
        else:
            ptu2ParsedDataList.append(parseData)


    for ptu2FromList in ptu2FailedDataList:
        notInDict=1

        for ptu2FromDict in separatePtu2FailedDataDict['parsedDataList']:
            if ptu2FromList.fileTitle.fileNamePath ==  ptu2FromDict.fileTitle.fileNamePath:
                notInDict = 0
        if notInDict == 1:
            separatePtu2FailedDataDict['parsedDataList'].append(ptu2FromList)

    for ptu2FromList in ptu2ParsedDataList:
        notInDict = 1

        for ptu2FromDict in separatePtu2ParsedDataDict['parsedDataList']:
            if ptu2FromList.fileTitle.fileNamePath == ptu2FromDict.fileTitle.fileNamePath:
                notInDict = 0
        if notInDict == 1:
            separatePtu2ParsedDataDict['parsedDataList'].append(ptu2FromList)

    for ptu2FromList in ptu2ParsedDataList:
        notInDict = 1

        for ptu2FromDict in sysDiagParsedDataDict['parsedDataList']:
            if ptu2FromList.fileTitle.fileNamePath == ptu2FromDict.fileTitle.fileNamePath:
                notInDict = 0
        if notInDict == 1:
            sysDiagParsedDataDict['parsedDataList'].append(ptu2FromList)

    clearTable(qt.parseProtAddPtu2ParsedTable)

    for ptu2FileIdx in range(len(separatePtu2ParsedDataDict['parsedDataList'])):

        qt.parseProtAddPtu2ParsedTable.insertRow(ptu2FileIdx)
        qt.parseProtAddPtu2ParsedTable.setItem(ptu2FileIdx, 0, QTableWidgetItem(separatePtu2ParsedDataDict['parsedDataList'][ptu2FileIdx].fileTitle.fileNamePath))

    qt.parseProtSepParPtu2FilesLabel.setText(qt.parseProtSepParPtu2FilesStr + str(len(separatePtu2ParsedDataDict['parsedDataList'])))

    clearTable(qt.parseProtAddPtu2FailedTable)

    for ptu2FileIdx in range(len(separatePtu2FailedDataDict['parsedDataList'])):
        qt.parseProtAddPtu2FailedTable.insertRow(ptu2FileIdx)
        qt.parseProtAddPtu2FailedTable.setItem(ptu2FileIdx, 0, QTableWidgetItem(separatePtu2FailedDataDict['parsedDataList'][ptu2FileIdx].fileTitle.fileNamePath))


def addAndParseTxAntDiagFiles(txAntDiagParsedDataDict, separateTxAntDiagParsedDataDict, separateTxAntDiagFailedDataDict):

    qt.parseProtTableTabWidget.setCurrentIndex(3)

    txAntDiagFilesList = []
    if qt.parseProtAddAndParseTxAntDiagFDialog.exec_():
        txAntDiagFilesList = qt.parseProtAddAndParseTxAntDiagFDialog.selectedFiles()

    for item in txAntDiagFilesList:
        parseDataLog.info(item)

    txAntDiagFailedDataList = []
    txAntDiagParsedDataList = []
    for txAntDiagPath in txAntDiagFilesList:
        parseData = parseTxAntDiag.TxAntDiagramParseData()
        parseData.parseFile(txAntDiagPath, antSysDiag.plotSetup['useSensorMuster'], antSysDiag.plotSetup['sensorMusterList'])
        if parseData.bDataValid == False:
            txAntDiagFailedDataList.append(parseData)
        else:
            txAntDiagParsedDataList.append(parseData)

    for txAntDiagFromList in txAntDiagFailedDataList:
        notInDict = 1

        for txAntDiagFromDict in separateTxAntDiagFailedDataDict['parsedDataList']:
            if txAntDiagFromList.fileTitle.fileNamePath == txAntDiagFromDict.fileTitle.fileNamePath:
                notInDict = 0
        if notInDict == 1:
            separateTxAntDiagFailedDataDict['parsedDataList'].append(txAntDiagFromList)

    for txAntDiagFromList in txAntDiagParsedDataList:
        notInDict = 1

        for txAntDiagFromDict in separateTxAntDiagParsedDataDict['parsedDataList']:
            if txAntDiagFromList.fileTitle.fileNamePath == txAntDiagFromDict.fileTitle.fileNamePath:
                notInDict = 0
        if notInDict == 1:
            separateTxAntDiagParsedDataDict['parsedDataList'].append(txAntDiagFromList)

    for txAntDiagFromList in txAntDiagParsedDataList:
        notInDict = 1

        for txAntDiagFromDict in txAntDiagParsedDataDict['parsedDataList']:
            if txAntDiagFromList.fileTitle.fileNamePath == txAntDiagFromDict.fileTitle.fileNamePath:
                notInDict = 0
        if notInDict == 1:
            txAntDiagParsedDataDict['parsedDataList'].append(txAntDiagFromList)

    clearTable(qt.parseProtAddTxAntDiagParsedTable)

    for txAntDiagFileIdx in range(len(separateTxAntDiagParsedDataDict['parsedDataList'])):
        qt.parseProtAddTxAntDiagParsedTable.insertRow(txAntDiagFileIdx)
        qt.parseProtAddTxAntDiagParsedTable.setItem(txAntDiagFileIdx, 0, QTableWidgetItem(
            separateTxAntDiagParsedDataDict['parsedDataList'][txAntDiagFileIdx].fileTitle.fileNamePath))

    qt.parseProtSepParTxAntDiagFilesLabel.setText(qt.parseProtSepParTxAntDiagFilesStr + str(len(separateTxAntDiagParsedDataDict['parsedDataList'])))

    clearTable(qt.parseProtAddTxAntDiagFailedTable)

    for txAntDiagFileIdx in range(len(separateTxAntDiagFailedDataDict['parsedDataList'])):
        qt.parseProtAddTxAntDiagFailedTable.insertRow(txAntDiagFileIdx)
        qt.parseProtAddTxAntDiagFailedTable.setItem(txAntDiagFileIdx, 0, QTableWidgetItem(
            separateTxAntDiagFailedDataDict['parsedDataList'][txAntDiagFileIdx].fileTitle.fileNamePath))



def loadCalInputLimitsFile():

    filePath = ''

    if qt.parseProtProtDataInFileCalFDialog.exec_():
        filePath = qt.parseProtProtDataInFileCalFDialog.selectedFiles()[0]

        filePath = filePath.replace('\\', '/')

    else:
        filePath=aux.calLimitsFilePath
    qt.parseProtProtDataInFileCalLabel.setText(filePath)
    qt.parseProtProtDataInFileCalLabel.setToolTip(filePath)


def loadBurnInInputLimitsFile():

    filePath = ''

    if qt.parseProtProtDataInFileBurnInFDialog.exec_():
        filePath = qt.parseProtProtDataInFileBurnInFDialog.selectedFiles()[0]

        filePath = filePath.replace('\\', '/')
    else:
        filePath = aux.burnInLimitsFilePath
    qt.parseProtProtDataInFileBurnInLabel.setText(filePath)
    qt.parseProtProtDataInFileBurnInLabel.setToolTip(filePath)


def loadBurnInLimitsGroupsFile():

    filePath = ''

    if qt.parseProtProtDataLimGroupsBurnInFDialog.exec_():
        filePath = qt.parseProtProtDataLimGroupsBurnInFDialog.selectedFiles()[0]

        filePath = filePath.replace('\\', '/')
    else:
        filePath = aux.burnInLimGroupsFilePath
    qt.parseProtProtDataLimGroupsBurnInLabel.setText(filePath)
    qt.parseProtProtDataLimGroupsBurnInLabel.setToolTip(filePath)


def loadCalLimitsGroupsFile():

    filePath = ''

    if qt.parseProtProtDataLimGroupsCalFDialog.exec_():
        filePath = qt.parseProtProtDataLimGroupsCalFDialog.selectedFiles()[0]

        filePath = filePath.replace('\\', '/')
    else:
        filePath = aux.calLimGroupsFilePath
    qt.parseProtProtDataLimGroupsCalLabel.setText(filePath)
    qt.parseProtProtDataLimGroupsCalLabel.setToolTip(filePath)


def setup_progress_bar(protToBeParsedDict: dict, protocolPathDict: dict) -> tuple[str, int]:
    """Setup the progress bar for protocol parsing."""
    qt.parseProtProgresBar.reset()
    protToBeParsedListLen = len(protToBeParsedDict['protocolPathTypeDictList'])
    progBarLabelStr = ''
    if len(protToBeParsedDict['protocolPathTypeDictList']) != 0:
        qt.parseProtProgresBar.setRange(0, len(protToBeParsedDict['protocolPathTypeDictList']))
        progBarLabelStr = f'Protocols to be parsed: {len(protToBeParsedDict["protocolPathTypeDictList"])} / {len(protocolPathDict["protocolPathTypeDictList"])}. '
        qt.parseProtProgresLabel.setText(progBarLabelStr)
        qt.parseProtProgresBar.setValue(0)
        qt.parseProtProgresBar.setFormat(f'{qt.parseProtProgresBar.value()} / {protToBeParsedListLen}')
    return progBarLabelStr, protToBeParsedListLen


def _load_protocol_data(
    filteredSysDiagList: list,
    filteredTxAntDiagList: list,
    protToBeParsedDict: dict,
    progBarLabelStr: str,
    protToBeParsedListLen: int,
) -> tuple[list, list, list, list]:
    """Load PTU2 and TxAntDiag files for every protocol; update the progress bar.

    Returns (sysDiagDataList, txAntDiagDataList,
             sysDiagParsedDataList, txAntDiagParsedDataList).
    """
    sysDiagDataList:        list = []
    txAntDiagDataList:      list = []
    sysDiagParsedDataList:  list = []
    txAntDiagParsedDataList: list = []

    twentyPercent = int(protToBeParsedListLen / 5)
    twentyPercRes = protToBeParsedListLen % 5
    idx      = 1
    final    = 0
    setFinal = False

    for protFileIdx in range(protToBeParsedListLen):
        # --- load sys-diag (PTU2) files ---
        sysDiagDataPerProt = filteredSysDiagList[protFileIdx]['ptu2FilesList']
        sysDiagLoadedData  = ld.LoadData(
            sysDiagDataPerProt,
            antSysDiag.plotSetup['useSensorMuster'],
            antSysDiag.plotSetup['sensorMusterList'],
        )
        if sysDiagLoadedData.invalidPath == 1:
            parseDataLog.info(sysDiagLoadedData.invalidPathString)
        else:
            sysDiagDataList.append(sysDiagDataPerProt)
            sysDiagParsedDataList += sysDiagLoadedData.parseDataList

        # --- load tx-ant-diag files ---
        txAntDiagDataPerProt = filteredTxAntDiagList[protFileIdx]['txAntDiagList']
        txAntDiagLoadedData  = ld_txantdiag.LoadData(
            txAntDiagDataPerProt,
            txAntDiag.plotSetup['useSensorMuster'],
            txAntDiag.plotSetup['sensorMusterList'],
        )
        if txAntDiagLoadedData.invalidPath == 1:
            parseDataLog.info(txAntDiagLoadedData.invalidPathString)
        else:
            txAntDiagDataList.append(txAntDiagDataPerProt)
            txAntDiagParsedDataList += txAntDiagLoadedData.parseDataList

        # --- update progress bar ---
        if setFinal:
            qt.parseProtProgresBar.setFormat(f'{final} / {protToBeParsedListLen}')
        else:
            qt.parseProtProgresBar.setFormat(f'{idx} / {protToBeParsedListLen}')

        if twentyPercent != 0:
            if idx % twentyPercent == 0:
                _, tail = os.path.split(
                    protToBeParsedDict['protocolPathTypeDictList'][protFileIdx]['protocolPath']
                )
                qt.parseProtProgresLabel.setText(progBarLabelStr + 'Protocol: ' + tail)
                if int(idx / twentyPercent) < 5:
                    qt.parseProtProgresBar.setValue(idx)
                else:
                    setFinal = True
                    final    = idx + twentyPercRes
                    qt.parseProtProgresBar.setValue(final)
        else:
            _, tail = os.path.split(
                protToBeParsedDict['protocolPathTypeDictList'][protFileIdx]['protocolPath']
            )
            qt.parseProtProgresLabel.setText(progBarLabelStr + 'Protocol: ' + tail)
            qt.parseProtProgresBar.setValue(idx)

        idx += 1

    return sysDiagDataList, txAntDiagDataList, sysDiagParsedDataList, txAntDiagParsedDataList


def _populate_accepted_protocols_table(
    protToBeParsedDict: dict,
    sysDiagDataList: list,
    txAntDiagDataList: list,
) -> None:
    """Set up the accepted-protocols table columns and insert one row-group per protocol."""
    header = qt.parseProtAccProtTable.horizontalHeader()
    header.setSectionResizeMode(0, qt.QHeaderView.ResizeMode.Interactive)
    qt.parseProtAccProtTable.setColumnWidth(0, 400)
    header.setSectionResizeMode(1, qt.QHeaderView.ResizeMode.Interactive)
    qt.parseProtAccProtTable.setColumnWidth(1, 110)
    header.setSectionResizeMode(2, qt.QHeaderView.ResizeMode.Interactive)
    header.setSectionResizeMode(3, qt.QHeaderView.ResizeMode.Stretch)

    if not sysDiagDataList or not txAntDiagDataList:
        return

    refRowIdx = qt.parseProtAccProtTable.rowCount()

    for protocolFileIdx in range(len(protToBeParsedDict['protocolPathTypeDictList'])):
        protocolPath             = protToBeParsedDict['protocolPathTypeDictList'][protocolFileIdx]['protocolPath']
        protocolType             = protToBeParsedDict['protocolPathTypeDictList'][protocolFileIdx]['type']
        sysDiagListPerProtocol   = sysDiagDataList[protocolFileIdx]
        txAntDiagListPerProtocol = txAntDiagDataList[protocolFileIdx]
        protTableData            = dp.ProtocolsTableData(protocolPath, sysDiagListPerProtocol, txAntDiagListPerProtocol)

        if not sysDiagListPerProtocol and not txAntDiagListPerProtocol:
            continue

        for relRowIdx in range(protTableData.biggerListLength):
            rowIdx = relRowIdx + refRowIdx
            qt.parseProtAccProtTable.insertRow(rowIdx)
            qt.parseProtAccProtTable.setItem(
                rowIdx, 0,
                QTableWidgetItem(protTableData.protocolPath if relRowIdx == 0 else ''),
            )
            qt.parseProtAccProtTable.setItem(rowIdx, 1, QTableWidgetItem(protocolType))
            qt.parseProtAccProtTable.setItem(rowIdx, 2, QTableWidgetItem(protTableData.sysDiagFilePathShapedList[relRowIdx]))
            qt.parseProtAccProtTable.setItem(rowIdx, 3, QTableWidgetItem(protTableData.txAntDiagFilePathShapedList[relRowIdx]))

        for spanEntry in protTableData.smallerListRowSpanList:
            qt.parseProtAccProtTable.setSpan(
                spanEntry['spanStart'] + refRowIdx,
                protTableData.smallerListColIdx,
                spanEntry['spanCount'],
                1,
            )

        qt.parseProtAccProtTable.setSpan(refRowIdx, 0, protTableData.biggerListLength, 1)
        refRowIdx += protTableData.biggerListLength


def parseData(
    protocolPathDict: dict,
    protToBeParsedDict: dict,
    parsedProtDict: dict,
    sysDiagFilePathDict: dict,
    txDiagfilePathDict: dict,
    sysDiagParsedDataDict: dict,
    txAntDiagParsedDataDict: dict,
) -> None:
    """Orchestrate protocol parsing: filter → load → merge → update UI."""
    qt.parseProtTableTabWidget.setCurrentIndex(1)

    if not protToBeParsedDict['protocolPathTypeDictList']:
        qt.parseProtProgresLabel.setText('No protocols to be parsed.')
        return

    if not parsedProtDict['protocolPathTypeDictList']:
        qt.parseProtAccProtTable.setRowCount(0)

    filteredSysDiagList, filteredTxAntDiagList = filter_protocol_file_lists(
        protToBeParsedDict, sysDiagFilePathDict, txDiagfilePathDict, parsedProtDict
    )

    progBarLabelStr, protToBeParsedListLen = setup_progress_bar(protToBeParsedDict, protocolPathDict)

    sysDiagDataList, txAntDiagDataList, sysDiagParsedDataList, txAntDiagParsedDataList = _load_protocol_data(
        filteredSysDiagList, filteredTxAntDiagList,
        protToBeParsedDict, progBarLabelStr, protToBeParsedListLen,
    )

    merge_into_parsed_dicts(
        sysDiagParsedDataList, txAntDiagParsedDataList,
        sysDiagParsedDataDict, txAntDiagParsedDataDict,
    )

    qt.parseProtParsedLoadedProtLabel.setText(
        qt.parseProtParsedLoadedProtStr
        + f'{len(parsedProtDict["protocolPathTypeDictList"])} / {len(protocolPathDict["protocolPathTypeDictList"])}'
    )
    qt.parseProtPtu2FilesLabel.setText(qt.parseProtPtu2FilesStr + str(len(sysDiagParsedDataDict['parsedDataList'])))
    qt.parseProtTxAntDiagFilesLabel.setText(qt.parseProtTxAntDiagFilesStr + str(len(txAntDiagParsedDataDict['parsedDataList'])))

    _populate_accepted_protocols_table(protToBeParsedDict, sysDiagDataList, txAntDiagDataList)

    qt.parseProtProgresLabel.setText(
        f'Parsing finished. Protocols parsed: {len(protToBeParsedDict["protocolPathTypeDictList"])}.'
    )
    protToBeParsedDict['protocolPathTypeDictList'][:] = []


def importDbProtocolsList(burnInProtocolPathDict, burnInParsedProtDict, burnInProtToBeParsedDict, calProtocolPathDict, calParsedProtDict, calProtToBeParsedDict, allCertProtocolPathDict, downloadBurnIn, downloadCal):
    # cert module removed - function disabled
    parseDataLog.warning('Database protocol import not available - CT_DataCollector module removed')
    pass


def importBurnInProtocolsList(burnInProtocolPathDict, burnInParsedProtDict, burnInProtToBeParsedDict, allCertProtocolPathDict):
    # cert module removed - using simplified version without cert.importData
    burnInProtocolFilesList = []
    fillInCertProtocolData(burnInProtocolFilesList, burnInProtocolPathDict, burnInParsedProtDict, burnInProtToBeParsedDict, allCertProtocolPathDict, 'BurnIn')


def importCalProtocolsList(calProtocolPathDict, calParsedProtDict, calProtToBeParsedDict, allCertProtocolPathDict):
    # cert module removed - using simplified version without cert.importData
    calProtocolFilesList = []
    fillInCertProtocolData(calProtocolFilesList, calProtocolPathDict, calParsedProtDict, calProtToBeParsedDict, allCertProtocolPathDict, 'Calibration')


def fillInCertProtocolData(protocolFilesList, protocolPathDict, parsedProtDict, protToBeParsedDict, allCertProtocolPathDict, protType):

    qt.mainTabWidget.setCurrentIndex(0)
    qt.parseProtTableTabWidget.setCurrentIndex(4)

    if len(protocolFilesList) == 0:
        return


    protNonRepList = []
    for protocolFilePath in protocolFilesList:
        if protocolFilePath not in allCertProtocolPathDict['protocolPathList']:
            protNonRepList.append(protocolFilePath)
        else:
            parseDataLog.info('Protocol is already imported: ' + protocolFilePath)

    protocolPathDict['protocolPathList'] += protNonRepList
    allCertProtocolPathDict['protocolPathList'] += protNonRepList

    # check if loaded protocols are already parsed
    for protocolFilePathIdx in range(len(protNonRepList)):

        if protNonRepList[protocolFilePathIdx] not in parsedProtDict['protocolPathList']:
            protToBeParsedDict['protocolPathList'].append(protNonRepList[protocolFilePathIdx])
        else:
            parseDataLog.info('Protocol is already parsed: ' + protNonRepList[protocolFilePathIdx])


    # Removed: parseProtSelCertProtTable and related header setup (widget no longer exists)


    # refRowIdx=qt.parseProtSelCertProtTable.rowCount()  # Removed: widget no longer exists


    # parseDataLog.info('Num. of  Accepted Protocols: ' + str(len(protocolPathDict['protocolPathList'])))

    # insert into table


def clearData(protocolPathDict, acceptedProtocolPathDict, filteredProtocolPathDict, sysDiagFilePathDict, txDiagfilePathDict):
    protocolPathDict['protocolPathTypeDictList']   = []
    sysDiagFilePathDict['filePathList']            = []
    txDiagfilePathDict['filePathList']             = []
    parsedProtDict['protocolPathTypeDictList']     = []
    protToBeParsedDict['protocolPathTypeDictList'] = []
    filteredProtocolPathDict['protocolPathList']   = []

    sysDiagParsedDataDict['parsedDataList']      = []
    separatePtu2ParsedDataDict['parsedDataList'] = []
    separatePtu2FailedDataDict['parsedDataList'] = []

    txAntDiagParsedDataDict['parsedDataList']         = []
    separateTxAntDiagParsedDataDict['parsedDataList'] = []
    separateTxAntDiagFailedDataDict['parsedDataList'] = []

    acceptedProtocolPathDict['emptyProtList'] = []
    acceptedProtocolPathDict['errorProtList'] = []
    acceptedProtocolPathDict['abbortCritProtList']    = []
    acceptedProtocolPathDict['limitExceededProtList'] = []

    qt.parseProtParsedLoadedProtLabel.setText(qt.parseProtParsedLoadedProtStr + '0')
    qt.parseProtPtu2FilesLabel.setText(qt.parseProtPtu2FilesStr + '0')
    qt.parseProtTxAntDiagFilesLabel.setText(qt.parseProtTxAntDiagFilesStr + '0')

    qt.parseProtLoadedProtLabel.setText(qt.parseProtLoadedProtStr + '0')
    qt.parseProtEolErrorLabel.setText(qt.parseProtEolErrorStr + '0')
    qt.parseProtAbbortCritLabel.setText(qt.parseProtAbbortCritStr + '0')
    qt.parseProtMeasLimitsExcLabel.setText(qt.parseProtMeasLimitsExcStr + '0')

    qt.parseProtSepParPtu2FilesLabel.setText(qt.parseProtSepParPtu2FilesStr + '0')
    qt.parseProtSepParTxAntDiagFilesLabel.setText(qt.parseProtSepParTxAntDiagFilesStr + '0')

    # qt.parseProtProgresBar.setRange(0, len(protocolPathDict['protocolPathList']))
    # qt.parseProtProgresBar.setValue(0)
    qt.parseProtProgresBar.reset()
    qt.parseProtProgresBar.setFormat('')
    qt.parseProtProgresLabel.setText('No protocols loaded.')

    clearTable(qt.parseProtSelProtTable)
    clearTable(qt.parseProtAccProtTable)

    clearTable(qt.parseProtAddPtu2ParsedTable)
    clearTable(qt.parseProtAddPtu2FailedTable)

    clearTable(qt.parseProtAddTxAntDiagFailedTable)
    clearTable(qt.parseProtAddTxAntDiagParsedTable)

    parseDataLog.info('Loaded and Parsed Data cleared!')


def clearTable(tableWidget):

    while (tableWidget.rowCount() > 0):
        tableWidget.removeRow(0)
    # tableWidget.clearContents()
    tableWidget.setRowCount(qt.PARSE_PROT_TABLE_ROWS)
    tableWidgetHeader = tableWidget.horizontalHeader()
    tableWidgetHeader.setSectionResizeMode(qt.QHeaderView.ResizeMode.Stretch)


def getprotcols(
    allProtocolsPathNamesList: list,
    searchPtu2Files: bool,
    searchTxAntDiagFiles: bool,
) -> tuple[list, list, list, list, list, list, list]:
    """Pre-parse, filter and walk protocols; return file-association lists."""
    bUseFilesWithError          = qt.parseProtEolErrorCheckBox.isChecked()
    bUseFilesAbbortCriterion    = qt.parseProtEolAbortCheckBox.isChecked()
    bUseFilesWIthLimitsExceeded = qt.parseProtEolMeasLimitsCheckBox.isChecked()

    PreParseInfoProtocolsList, *_ = protocolFilter.ProtocolInfoClass.PreParseProtcols(allProtocolsPathNamesList)

    parseDataLog.info(
        f'Filter Protocols: UseFilesWithError = {bUseFilesWithError}, '
        f'UseFilesAbbortCriterion = {bUseFilesAbbortCriterion}, '
        f'UseFilesWIthLimitsExceeded = {bUseFilesWIthLimitsExceeded}'
    )

    acceptedProtocolsList, filteredProtocolsList = protocolFilter.ProtocolInfoClass.FilterProtocols(
        PreParseInfoProtocolsList, bUseFilesWithError, bUseFilesAbbortCriterion, bUseFilesWIthLimitsExceeded
    )
    parseDataLog.info(f'Accepted Protocols {len(acceptedProtocolsList)} of {len(allProtocolsPathNamesList)}')

    if qt.parseProtnewProtCheckBox.isChecked():
        parseDataLog.info('Only the latest protocol will be selected.')
        acceptedProtocolsList = protocolFilter.ProtocolInfoClass.FilterNewProtocols(acceptedProtocolsList)

    for cPreParseInfo in acceptedProtocolsList:
        parseDataLog.info(cPreParseInfo.PathName)

    filteredProtocolsList = [p.PathName for p in filteredProtocolsList]

    ptu2FilesList, txAntDiagList, accProtList, accErrorProtList, accAbbortCritProtList, accLimitExceededProtList = walk_protocol_files(
        acceptedProtocolsList,
        searchPtu2Files, searchTxAntDiagFiles,
        bUseFilesWithError, bUseFilesAbbortCriterion, bUseFilesWIthLimitsExceeded,
        protocolFilter.ProtocolInfoClass.getfiltered_ptu2filelist,
        protocolFilter.ProtocolInfoClass.getfiltered_txantdiagramfilelist,
    )

    return ptu2FilesList, txAntDiagList, accProtList, accErrorProtList, accAbbortCritProtList, accLimitExceededProtList, filteredProtocolsList

errmsg = 'Error!'



qt.parseProtImportProtFListPushBtn.clicked.connect(lambda: importProtocolsFileList(protocolPathDict, acceptedProtocolPathDict, filteredProtocolPathDict, sysDiagFilePathDict, txDiagfilePathDict, parsedProtDict, protToBeParsedDict, qt.parseProtSysDiagCheckBox, qt.parseProtTxAntDiagCheckBox))
qt.parseProtImportProtDirPathPushBtn.clicked.connect(lambda: importProtocolsDirPath(protocolPathDict, acceptedProtocolPathDict, filteredProtocolPathDict, sysDiagFilePathDict, txDiagfilePathDict, parsedProtDict, protToBeParsedDict, qt.parseProtSysDiagCheckBox, qt.parseProtTxAntDiagCheckBox))
qt.parseProtClearDataPushBtn.clicked.connect(lambda: clearData(protocolPathDict, acceptedProtocolPathDict, filteredProtocolPathDict, sysDiagFilePathDict, txDiagfilePathDict))
qt.parseProtParseDataPushBtn.clicked.connect(lambda: parseData(protocolPathDict, protToBeParsedDict, parsedProtDict, sysDiagFilePathDict, txDiagfilePathDict, sysDiagParsedDataDict, txAntDiagParsedDataDict))
qt.parseProtAddAndParsePtu2PushBtn.clicked.connect(lambda: addAndParsePtu2Files(sysDiagParsedDataDict, separatePtu2ParsedDataDict, separatePtu2FailedDataDict))
qt.parseProtAddAndParseTxAntDiagPushBtn.clicked.connect(lambda: addAndParseTxAntDiagFiles(txAntDiagParsedDataDict, separateTxAntDiagParsedDataDict, separateTxAntDiagFailedDataDict))


def clearLogTable():
    while (qt.mainLogTable.rowCount() > 0):
        qt.mainLogTable.removeRow(0)
    # qt.mainLogTable.clearContents()
    qt.mainLogTable.setRowCount(0)
    qt.mainLogTableHandler.logTableRow=0
    # qt.mainLogTableHeader.setSectionResizeMode(qt.QHeaderView.Stretch)


qt.mainLogTableClearBtn.clicked.connect(lambda: clearLogTable())


##System Diagrams
### Input Setup
qt.sysDiagInputSetupAngleSetupRadio1.setChecked(True)
qt.sysDiagInputSetupAngleSetupRadio2.setChecked(False)
antSysDiag.plotSetup['targetAngle'] = 1


def sysDiagInputSetupAngleGroupClick():
    btnId = qt.sysDiagInputSetupAngleGroup.checkedId()
    if btnId == 0:
        antSysDiag.plotSetup['targetAngle'] = 1
        parseDataLog.debug('plotSetup: ' + str(antSysDiag.plotSetup))
    elif btnId == 1:
        antSysDiag.plotSetup['targetAngle'] = 0
        parseDataLog.debug('plotSetup: ' + str(antSysDiag.plotSetup))


qt.sysDiagInputSetupSensorOrientRadio1.setChecked(True)
qt.sysDiagInputSetupSensorOrientRadio2.setChecked(False)
antSysDiag.plotSetup['upsideDown'] = 0


def sysDiagInputSetupSensorOrientGroupClick():
    btnId = qt.sysDiagInputSetupSensorOrientGroup.checkedId()
    if btnId == 0:
        antSysDiag.plotSetup['upsideDown'] = 0
        parseDataLog.debug('plotSetup: ' + str(antSysDiag.plotSetup))
    elif btnId == 1:
        antSysDiag.plotSetup['upsideDown'] = 1
        parseDataLog.debug('plotSetup: ' + str(antSysDiag.plotSetup))


qt.sysDiagInputSetupChirp0CheckBox.setChecked(True)
qt.sysDiagInputSetupChirp1CheckBox.setChecked(False)
qt.sysDiagInputSetupChirp2CheckBox.setChecked(False)
qt.sysDiagInputSetupChirp3CheckBox.setChecked(False)
qt.sysDiagInputSetupChirp3CheckBox.isChecked()
antSysDiag.chirpConfig['chirp0'] = 1
antSysDiag.chirpConfig['chirp1'] = 0
antSysDiag.chirpConfig['chirp2'] = 0
antSysDiag.chirpConfig['chirp3'] = 0


def sysDiagInputSetupChirpClick(btn):
    btnId = qt.sysDiagInputSetupChirpGroup.id(btn)
    # if btnId==0:
    chBox = qt.sysDiagInputSetupChirpGroup.button(btnId)
    state = chBox.isChecked()
    dictKey = 'chirp'+str(btnId)
    if state == 1:
        antSysDiag.chirpConfig[dictKey] = 1
    else:
        antSysDiag.chirpConfig[dictKey] = 0
    parseDataLog.debug('chirpConfig: ' + str(antSysDiag.chirpConfig))


# 'allOnOneSlide': 1, #Genrate all on one slide: all diagrams, all sensors, all RxAnt, graphs by choice.
#
# 'nofSensorMeasToShow': 32,  # The max number of sensor measurements to show
# 'ShowCertainPlotWindow': 0,

qt.sysDiagInputSetupDiagConfigInputModeRadio1.setChecked(True)
qt.sysDiagInputSetupDiagConfigInputModeRadio2.setChecked(False)
qt.sysDiagInputSetupDiagConfigInputModeRadio3.setChecked(False)
antSysDiag.diagramConfig['selectDiagrams']=0


def sysDiagInputSetupDiagConfigInputModeClick():
    btnId = qt.sysDiagInputSetupDiagConfGroup.checkedId()
    if btnId == 0:
        antSysDiag.diagramConfig['selectDiagrams'] = 0
        parseDataLog.debug('diagramConfig: ' + str(antSysDiag.diagramConfig))
    elif btnId == 1:
        antSysDiag.diagramConfig['selectDiagrams'] = 1
        parseDataLog.debug('diagramConfig: ' + str(antSysDiag.diagramConfig))
    elif btnId == 2:
        antSysDiag.diagramConfig['selectDiagrams'] = 2
        parseDataLog.debug('diagramConfig: ' + str(antSysDiag.diagramConfig))

#
# desDiagListString = qt.sysDiagInputSetupDiagConfigDesListLEdit.text()
qt.sysDiagInputSetupDiagConfigDesListLEdit.setText('1,2,3,4')

qt.sysDiagInputSetupDiagConfigDesRangeLowLEdit.setText('0')

if sp.checkInt(qt.sysDiagInputSetupDiagConfigDesRangeLowLEdit.text()) == True:
    antSysDiag.diagramConfig['lowerNumber'] = int(qt.sysDiagInputSetupDiagConfigDesRangeLowLEdit.text())
antSysDiag.diagramConfig['lowerNumber'] = 0
qt.sysDiagInputSetupDiagConfigDesRangeHighLEdit.setText('4')
v = qt.sysDiagInputSetupDiagConfigDesRangeHighLEdit.text()

if sp.checkInt(qt.sysDiagInputSetupDiagConfigDesRangeHighLEdit.text()) == True:
    antSysDiag.diagramConfig['higherNumber'] = int(qt.sysDiagInputSetupDiagConfigDesRangeHighLEdit.text())
antSysDiag.diagramConfig['higherNumber'] = 4

qt.sysDiagInputSetupDiagConfigOddEvenRadio1.setChecked(True)
qt.sysDiagInputSetupDiagConfigOddEvenRadio2.setChecked(False)
qt.sysDiagInputSetupDiagConfigOddEvenRadio3.setChecked(False)
antSysDiag.diagramConfig['oddOrEven']=0


def sysDiagInputSetupDiagConfOddEvenClick():
    btnId = qt.sysDiagInputSetupDiagConfOddEvenGroup.checkedId()
    if btnId == 0:
        antSysDiag.diagramConfig['oddOrEven'] = 0
        parseDataLog.debug('diagramConfig: ' + str(antSysDiag.diagramConfig))
    elif btnId == 1:
        antSysDiag.diagramConfig['oddOrEven'] = 1
        parseDataLog.debug('diagramConfig: ' + str(antSysDiag.diagramConfig))
    elif btnId == 2:
        antSysDiag.diagramConfig['oddOrEven'] = 2
        parseDataLog.debug('diagramConfig: ' + str(antSysDiag.diagramConfig))


qt.sysDiagPlotSetupImgGenRadio1.setChecked(True)
qt.sysDiagPlotSetupImgGenRadio2.setChecked(False)
antSysDiag.plotSetup['SeparateRxCh'] = 1


def sysDiagPlotSetupImgGenClick():
    btnId = qt.sysDiagPlotSetupImgGenGroup.checkedId()
    if btnId == 0:
        antSysDiag.plotSetup['SeparateRxCh'] = 1

        qt.sysDiagSlideConfTwoGraphCheckBox1.setChecked(False)
        qt.sysDiagSlideConfTwoGraphCheckBox2.setChecked(False)
        qt.sysDiagSlideConfFourGraphFrame.setEnabled(True)

        qt.sysDiagPlotSetup3GraphLayoutImgCheckBox.setChecked(True)
        qt.sysDiagPlotSetup3GraphLayoutImgCheckBox.setEnabled(True)
        antSysDiag.plotSetup['threeGraphLayout'] = 1

        qt.sysDiagSlideConfThreeGraphFrame.setEnabled(True)

        qt.sysDiagSlideConfThreeGraphCheckBox1.setChecked(True)
        qt.sysDiagSlideConfThreeGraphCheckBox2.setChecked(True)
        qt.sysDiagSlideConfThreeGraphCheckBox3.setChecked(False)

        qt.sysDiagSlideConfFourGraphCheckBox1.setChecked(True)
        qt.sysDiagSlideConfFourGraphCheckBox2.setChecked(False)
        qt.sysDiagSlideConfFourGraphCheckBox3.setChecked(False)


        parseDataLog.debug('plotSetup: ' + str(antSysDiag.plotSetup))
    elif btnId == 1:
        antSysDiag.plotSetup['SeparateRxCh'] = 0

        qt.sysDiagSlideConfTwoGraphCheckBox1.setChecked(True)
        qt.sysDiagSlideConfTwoGraphCheckBox2.setChecked(True)
        qt.sysDiagSlideConfFourGraphFrame.setEnabled(False)

        qt.sysDiagPlotSetup3GraphLayoutImgCheckBox.setChecked(False)
        qt.sysDiagPlotSetup3GraphLayoutImgCheckBox.setEnabled(False)
        antSysDiag.plotSetup['threeGraphLayout'] = 0

        qt.sysDiagSlideConfThreeGraphFrame.setEnabled(False)

        qt.sysDiagSlideConfThreeGraphCheckBox1.setChecked(False)
        qt.sysDiagSlideConfThreeGraphCheckBox2.setChecked(False)
        qt.sysDiagSlideConfThreeGraphCheckBox3.setChecked(False)

        qt.sysDiagSlideConfFourGraphCheckBox1.setChecked(False)
        qt.sysDiagSlideConfFourGraphCheckBox2.setChecked(False)
        qt.sysDiagSlideConfFourGraphCheckBox3.setChecked(False)

        parseDataLog.debug('plotSetup: ' + str(antSysDiag.plotSetup))


qt.sysDiagPlotSetup3GraphLayoutImgCheckBox.setChecked(True)
antSysDiag.plotSetup['threeGraphLayout'] = 1


def sysDiagPlotSetup3GraphLayoutImgClick():
    state = qt.sysDiagPlotSetup3GraphLayoutImgCheckBox.isChecked()
    if state == 1:
        antSysDiag.plotSetup['threeGraphLayout'] = 1

        qt.sysDiagSlideConfThreeGraphFrame.setEnabled(True)

        qt.sysDiagSlideConfThreeGraphCheckBox1.setChecked(True)
        qt.sysDiagSlideConfThreeGraphCheckBox2.setChecked(True)
        qt.sysDiagSlideConfThreeGraphCheckBox3.setChecked(False)

        qt.sysDiagSlideConfTwoGraphCheckBox2.setChecked(False)
    else:
        antSysDiag.plotSetup['threeGraphLayout'] = 0

        qt.sysDiagSlideConfThreeGraphFrame.setEnabled(False)

        qt.sysDiagSlideConfThreeGraphCheckBox1.setChecked(False)
        qt.sysDiagSlideConfThreeGraphCheckBox2.setChecked(False)
        qt.sysDiagSlideConfThreeGraphCheckBox3.setChecked(False)

        qt.sysDiagSlideConfTwoGraphCheckBox2.setChecked(True)
    parseDataLog.debug('plotSetup: ' + str(antSysDiag.plotSetup))


qt.sysDiagPlotSetupImageDpiLEdit.setText('220')
if sp.checkInt(qt.sysDiagPlotSetupImageDpiLEdit.text()) == True:
    antSysDiag.plotSetup['imageDpi'] = int(qt.sysDiagPlotSetupImageDpiLEdit.text())

qt.sysDiagPlotSetupScalingAutoCheckBox.setChecked(False)
antSysDiag.plotSetup['xScaleSizeAuto'] = 0
def sysDiagPlotSetupScalingAutoClick():
    state = qt.sysDiagPlotSetupScalingAutoCheckBox.isChecked()
    if state == 1:
        antSysDiag.plotSetup['xScaleSizeAuto'] = 1
    else:
        antSysDiag.plotSetup['xScaleSizeAuto'] = 0
    parseDataLog.debug('plotSetup: ' + str(antSysDiag.plotSetup))

qt.sysDiagPlotSetupScalingXScaleAzLEdit.setText('90')
qt.sysDiagPlotSetupScalingXScaleElLEdit.setText('45')
if sp.checkDecimal(qt.sysDiagPlotSetupScalingXScaleAzLEdit.text()) == True:
    antSysDiag.plotSetup['xScaleSizeAz'] = float(qt.sysDiagPlotSetupScalingXScaleAzLEdit.text())

if sp.checkDecimal(qt.sysDiagPlotSetupScalingXScaleElLEdit.text()) == True:
    antSysDiag.plotSetup['xScaleSizeEl'] = float(qt.sysDiagPlotSetupScalingXScaleElLEdit.text())


qt.sysDiagPlotSetupScalingYLimitRadio1.setChecked(True)
qt.sysDiagPlotSetupScalingYLimitRadio2.setChecked(False)
antSysDiag.plotSetup['yLimitsAntTypeSeparately'] = 1


def sysDiagPlotSetupScalingYLimitsClick():
    btnId = qt.sysDiagPlotSetupScalingYLimitsGroup.checkedId()
    if btnId == 0:
        antSysDiag.plotSetup['yLimitsAntTypeSeparately'] = 1
        parseDataLog.debug('plotSetup: ' + str(antSysDiag.plotSetup))
    elif btnId == 1:
        antSysDiag.plotSetup['yLimitsAntTypeSeparately'] = 0
        parseDataLog.debug('plotSetup: ' + str(antSysDiag.plotSetup))

qt.sysDiagPlotSetupScalingDiffPhDiffLEdit.setText('1.5')

if sp.checkDecimal(qt.sysDiagPlotSetupScalingDiffPhDiffLEdit.text()) == True:
    antSysDiag.plotSetup['diffPhaseDiffScalingFactor']=float(qt.sysDiagPlotSetupScalingDiffPhDiffLEdit.text())


qt.sysDiagPlotSetupGraphConfIdealCurveCheckBox.setChecked(True)
antSysDiag.plotSetup['idealPhaseDiff'] = 1


def sysDiagPlotSetupGraphConfIdealCurveClick():
    state = qt.sysDiagPlotSetupGraphConfIdealCurveCheckBox.isChecked()
    if state == 1:
        antSysDiag.plotSetup['idealPhaseDiff'] = 1
    else:
        antSysDiag.plotSetup['idealPhaseDiff'] = 0
    parseDataLog.debug('plotSetup: ' + str(antSysDiag.plotSetup))

graphId = 0
for key,val in antSysDiag.graphConfig.items():
    antSysDiag.graphConfig[key] = 0

    button = qt.sysDiagPlotSetupGraphConfGroup.button(graphId)
    button.setChecked(False)
    antSysDiag.graphConfig[key] = 0

    if key == 'level' or key == 'normLevel' or key == 'diffPhaseDiff' or key == 'corrPhaseDiff':
        antSysDiag.graphConfig[key] = 1
        button.setChecked(True)

    graphId += 1


def sysDiagPlotSetupGraphConfClick(btn):

    i = 0
    setKey = ''
    state  = 0
    btnId  = qt.sysDiagPlotSetupGraphConfGroup.id(btn)
    for key, val in antSysDiag.graphConfig.items():

        if i == btnId:
            chBox  = qt.sysDiagPlotSetupGraphConfGroup.button(btnId)
            state  = chBox.isChecked()
            setKey = key


            break

        i = i + 1
    antSysDiag.graphConfig[setKey] = qt.boolMapping(state)

    sysDiagSlideConfComboAddItems(qt.sysDiagSlideConfTwoGraphComboBox11, antSysDiag.graphConfig)
    sysDiagSlideConfComboAddItems(qt.sysDiagSlideConfTwoGraphComboBox12, antSysDiag.graphConfig)
    sysDiagSlideConfComboAddItems(qt.sysDiagSlideConfTwoGraphComboBox21, antSysDiag.graphConfig)
    sysDiagSlideConfComboAddItems(qt.sysDiagSlideConfTwoGraphComboBox22, antSysDiag.graphConfig)

    sysDiagSlideConfComboAddItems(qt.sysDiagSlideConfFourGraphComboBox1, antSysDiag.graphConfig)
    sysDiagSlideConfComboAddItems(qt.sysDiagSlideConfFourGraphComboBox2, antSysDiag.graphConfig)
    sysDiagSlideConfComboAddItems(qt.sysDiagSlideConfFourGraphComboBox3, antSysDiag.graphConfig)

    sysDiagSlideConfThreeGraphComboAddItems(qt.sysDiagSlideConfThreeGraphComboBox1, antSysDiag.graphConfig)
    sysDiagSlideConfThreeGraphComboAddItems(qt.sysDiagSlideConfThreeGraphComboBox2, antSysDiag.graphConfig)
    sysDiagSlideConfThreeGraphComboAddItems(qt.sysDiagSlideConfThreeGraphComboBox3, antSysDiag.graphConfig)
    parseDataLog.debug('graphConfig: ' + str(antSysDiag.graphConfig))


def sysDiagSlideConfComboAddItems(comboBox, graphConfig):
    itemList = []
    comboBox.clear()
    for key,val in antSysDiag.graphConfig.items():
        if val == 1:
            itemList.append(key)
    comboBox.addItems(itemList)


def sysDiagSlideConfThreeGraphComboAddItems(comboBox, graphConfig):
    itemList = []
    comboBox.clear()
    for key,val in antSysDiag.graphConfig.items():
        if val == 1 and 'hase' in key:
            itemList.append(key)
    comboBox.addItems(itemList)


def sysDiagSlideConfTwoGraphComboBox11Click(idx):
    antSysDiag.twoGraphConf1['primGraph'] = qt.sysDiagSlideConfTwoGraphComboBox11.itemText(idx)
    parseDataLog.debug('twoGraphConf1: ' + str(antSysDiag.twoGraphConf1))


def sysDiagSlideConfTwoGraphComboBox12Click(idx):
    antSysDiag.twoGraphConf1['secGraph'] = qt.sysDiagSlideConfTwoGraphComboBox12.itemText(idx)
    parseDataLog.debug('twoGraphConf1: ' + str(antSysDiag.twoGraphConf1))


def sysDiagSlideConfTwoGraphComboBox21Click(idx):
    antSysDiag.twoGraphConf2['primGraph'] = qt.sysDiagSlideConfTwoGraphComboBox21.itemText(idx)
    parseDataLog.debug('twoGraphConf2: ' + str(antSysDiag.twoGraphConf2))


def sysDiagSlideConfTwoGraphComboBox22Click(idx):
    antSysDiag.twoGraphConf2['secGraph'] = qt.sysDiagSlideConfTwoGraphComboBox22.itemText(idx)
    parseDataLog.debug('twoGraphConf2: ' + str(antSysDiag.twoGraphConf2))

# if qt.sysDiagPlotSetupImgGenRadio1.isChecked()==True:
    # twoGraphState='normal'
    # qt.sysDiagSlideConfTwoGraphCheckBox1.setChecked(False)
    # qt.sysDiagSlideConfTwoGraphCheckBox2.setChecked(False)

# else:
#     qt.sysDiagSlideConfTwoGraphCheckBox1.setChecked(True)
#     qt.sysDiagSlideConfTwoGraphCheckBox2.setChecked(True)

sysDiagSlideConfComboAddItems(qt.sysDiagSlideConfTwoGraphComboBox11, antSysDiag.graphConfig)
sysDiagSlideConfComboAddItems(qt.sysDiagSlideConfTwoGraphComboBox12, antSysDiag.graphConfig)
sysDiagSlideConfComboAddItems(qt.sysDiagSlideConfTwoGraphComboBox21, antSysDiag.graphConfig)
sysDiagSlideConfComboAddItems(qt.sysDiagSlideConfTwoGraphComboBox22, antSysDiag.graphConfig)


def sysDiagSlideConfTwoAndFourGraphComboSetCurrentItem(comboBox, textKey):
    for idx in range(comboBox.count()):
        text = comboBox.itemText(idx)
        if text == textKey:
            comboBox.setCurrentIndex(idx)

sysDiagSlideConfTwoAndFourGraphComboSetCurrentItem(qt.sysDiagSlideConfTwoGraphComboBox11, 'level')
antSysDiag.twoGraphConf1['primGraph'] = 'level'
sysDiagSlideConfTwoAndFourGraphComboSetCurrentItem(qt.sysDiagSlideConfTwoGraphComboBox12, 'normLevel')
antSysDiag.twoGraphConf1['secGraph']  = 'normLevel'
sysDiagSlideConfTwoAndFourGraphComboSetCurrentItem(qt.sysDiagSlideConfTwoGraphComboBox21, 'corrPhaseDiff')
antSysDiag.twoGraphConf2['primGraph'] = 'corrPhaseDiff'
sysDiagSlideConfTwoAndFourGraphComboSetCurrentItem(qt.sysDiagSlideConfTwoGraphComboBox22, 'diffPhaseDiff')
antSysDiag.twoGraphConf2['secGraph']  = 'diffPhaseDiff'


if qt.sysDiagPlotSetupImgGenRadio1.isChecked() == True:
    qt.sysDiagSlideConfFourGraphFrame.setEnabled(True)
    qt.sysDiagSlideConfFourGraphCheckBox1.setChecked(True)
    qt.sysDiagSlideConfFourGraphCheckBox2.setChecked(True)
    qt.sysDiagSlideConfFourGraphCheckBox3.setChecked(True)

    qt.sysDiagPlotSetup3GraphLayoutImgCheckBox.setChecked(True)
    qt.sysDiagPlotSetup3GraphLayoutImgCheckBox.setEnabled(True)
    antSysDiag.plotSetup['threeGraphLayout'] = 1

    qt.sysDiagSlideConfThreeGraphCheckBox1.setChecked(True)
    qt.sysDiagSlideConfThreeGraphCheckBox2.setChecked(True)
    qt.sysDiagSlideConfThreeGraphCheckBox3.setChecked(False)

    qt.sysDiagSlideConfThreeGraphFrame.setEnabled(True)

    qt.sysDiagSlideConfFourGraphCheckBox1.setChecked(True)
    qt.sysDiagSlideConfFourGraphCheckBox2.setChecked(False)
    qt.sysDiagSlideConfFourGraphCheckBox3.setChecked(False)

    qt.sysDiagSlideConfTwoGraphCheckBox1.setChecked(False)
    qt.sysDiagSlideConfTwoGraphCheckBox2.setChecked(False)
else:
    qt.sysDiagSlideConfFourGraphFrame.setEnabled(False)
    qt.sysDiagSlideConfFourGraphCheckBox1.setChecked(False)
    qt.sysDiagSlideConfFourGraphCheckBox2.setChecked(False)
    qt.sysDiagSlideConfFourGraphCheckBox3.setChecked(False)

    qt.sysDiagPlotSetup3GraphLayoutImgCheckBox.setChecked(False)
    qt.sysDiagPlotSetup3GraphLayoutImgCheckBox.setEnabled(False)
    antSysDiag.plotSetup['threeGraphLayout'] = 0

    qt.sysDiagSlideConfThreeGraphCheckBox1.setChecked(False)
    qt.sysDiagSlideConfThreeGraphCheckBox2.setChecked(False)
    qt.sysDiagSlideConfThreeGraphCheckBox3.setChecked(False)

    qt.sysDiagSlideConfThreeGraphFrame.setEnabled(False)

    qt.sysDiagSlideConfFourGraphCheckBox1.setChecked(False)
    qt.sysDiagSlideConfFourGraphCheckBox2.setChecked(False)
    qt.sysDiagSlideConfFourGraphCheckBox3.setChecked(False)

    qt.sysDiagSlideConfTwoGraphCheckBox1.setChecked(True)
    qt.sysDiagSlideConfTwoGraphCheckBox2.setChecked(True)


def sysDiagSlideConfFourGraphComboBox1Click(idx):
    antSysDiag.fourGraphConf1['graphType'] = qt.sysDiagSlideConfFourGraphComboBox1.itemText(idx)
    parseDataLog.debug('fourGraphConf1: ' + str(antSysDiag.fourGraphConf1))


def sysDiagSlideConfFourGraphComboBox2Click(idx):
    antSysDiag.fourGraphConf2['graphType'] = qt.sysDiagSlideConfFourGraphComboBox2.itemText(idx)
    parseDataLog.debug('fourGraphConf2: ' + str(antSysDiag.fourGraphConf2))


def sysDiagSlideConfFourGraphComboBox3Click(idx):
    antSysDiag.fourGraphConf3['graphType'] = qt.sysDiagSlideConfFourGraphComboBox3.itemText(idx)
    parseDataLog.debug('fourGraphConf3: ' + str(antSysDiag.fourGraphConf3))


sysDiagSlideConfComboAddItems(qt.sysDiagSlideConfFourGraphComboBox1, antSysDiag.graphConfig)
sysDiagSlideConfComboAddItems(qt.sysDiagSlideConfFourGraphComboBox2, antSysDiag.graphConfig)
sysDiagSlideConfComboAddItems(qt.sysDiagSlideConfFourGraphComboBox3, antSysDiag.graphConfig)

sysDiagSlideConfTwoAndFourGraphComboSetCurrentItem(qt.sysDiagSlideConfFourGraphComboBox1,'level')
antSysDiag.fourGraphConf1['graphType'] = 'level'
sysDiagSlideConfTwoAndFourGraphComboSetCurrentItem(qt.sysDiagSlideConfFourGraphComboBox2, 'corrPhaseDiff')
antSysDiag.fourGraphConf2['graphType'] = 'corrPhaseDiff'
sysDiagSlideConfTwoAndFourGraphComboSetCurrentItem(qt.sysDiagSlideConfFourGraphComboBox3, 'diffPhaseDiff')
antSysDiag.fourGraphConf3['graphType'] = 'diffPhaseDiff'


def sysDiagSlideConfThreeGraphComboBox1Click(idx):
    antSysDiag.threeGraphConf1['graphType'] = qt.sysDiagSlideConfThreeGraphComboBox1.itemText(idx)
    parseDataLog.debug('threeGraphConf1: ' + str(antSysDiag.threeGraphConf1))


def sysDiagSlideConfThreeGraphComboBox2Click(idx):
    antSysDiag.threeGraphConf2['graphType'] = qt.sysDiagSlideConfThreeGraphComboBox2.itemText(idx)
    parseDataLog.debug('threeGraphConf2: ' + str(antSysDiag.threeGraphConf2))


def sysDiagSlideConfThreeGraphComboBox3Click(idx):
    antSysDiag.threeGraphConf3['graphType'] = qt.sysDiagSlideConfThreeGraphComboBox3.itemText(idx)
    parseDataLog.debug('threeGraphConf3: ' + str(antSysDiag.threeGraphConf3))

sysDiagSlideConfThreeGraphComboAddItems(qt.sysDiagSlideConfThreeGraphComboBox1, antSysDiag.graphConfig)
sysDiagSlideConfThreeGraphComboAddItems(qt.sysDiagSlideConfThreeGraphComboBox2, antSysDiag.graphConfig)
sysDiagSlideConfThreeGraphComboAddItems(qt.sysDiagSlideConfThreeGraphComboBox3, antSysDiag.graphConfig)

sysDiagSlideConfTwoAndFourGraphComboSetCurrentItem(qt.sysDiagSlideConfThreeGraphComboBox1,'corrPhaseDiff')
antSysDiag.threeGraphConf1['graphType'] = 'corrPhaseDiff'
sysDiagSlideConfTwoAndFourGraphComboSetCurrentItem(qt.sysDiagSlideConfThreeGraphComboBox2, 'diffPhaseDiff')
antSysDiag.threeGraphConf2['graphType'] ='diffPhaseDiff'
# sysDiagSlideConfTwoAndFourGraphComboSetCurrentItem(qt.sysDiagSlideConfThreeGraphComboBox3, 'phaseDiff')

#####
qt.sysDiagSlideConfGeneralSensorNumSlideLEdit.setText('32')
if sp.checkInt(qt.sysDiagSlideConfGeneralSensorNumSlideLEdit.text()) == True:
    antSysDiag.plotSetup['nofSensorMeasToShow'] = int(qt.sysDiagSlideConfGeneralSensorNumSlideLEdit.text())

if qt.sysDiagSlideConfGeneralAllGraphsSlideCheckBox.isChecked()!=True:
    qt.sysDiagSlideConfGeneralAllSlidesCheckBox1.setChecked(False)
    qt.sysDiagSlideConfGeneralAllSlidesCheckBox1.setEnabled(False)

    qt.sysDiagSlideConfGeneralAllSlidesCheckBox2.setChecked(False)
    qt.sysDiagSlideConfGeneralAllSlidesCheckBox2.setEnabled(False)

    qt.sysDiagSlideConfGeneralAllSlidesCheckBox3.setChecked(False)
    qt.sysDiagSlideConfGeneralAllSlidesCheckBox3.setEnabled(False)

    qt.sysDiagSlideConfGeneralAllSlidesComboBox1.setEnabled(False)
    qt.sysDiagSlideConfGeneralAllSlidesComboBox2.setEnabled(False)
    qt.sysDiagSlideConfGeneralAllSlidesComboBox3.setEnabled(False)


    antSysDiag.plotSetup['allOnOneSlide'] = 0
else:
    antSysDiag.plotSetup['allOnOneSlide'] = 1


def sysDiagSlideConfGeneralAllGraphsSlideClick():
    state = qt.sysDiagSlideConfGeneralAllGraphsSlideCheckBox.isChecked()
    if state == True:
        antSysDiag.plotSetup['allOnOneSlide'] = 1

        qt.sysDiagSlideConfGeneralAllSlidesCheckBox1.setChecked(True)
        qt.sysDiagSlideConfGeneralAllSlidesCheckBox1.setEnabled(True)
        qt.sysDiagSlideConfGeneralAllSlidesCheckBox2.setChecked(True)
        qt.sysDiagSlideConfGeneralAllSlidesCheckBox2.setEnabled(True)
        qt.sysDiagSlideConfGeneralAllSlidesCheckBox3.setChecked(True)
        qt.sysDiagSlideConfGeneralAllSlidesCheckBox3.setEnabled(True)

        qt.sysDiagSlideConfGeneralAllSlidesComboBox1.setEnabled(True)
        qt.sysDiagSlideConfGeneralAllSlidesComboBox2.setEnabled(True)
        qt.sysDiagSlideConfGeneralAllSlidesComboBox3.setEnabled(True)

    else:
        antSysDiag.plotSetup['allOnOneSlide'] = 0
        qt.sysDiagSlideConfGeneralAllSlidesCheckBox1.setChecked(False)
        qt.sysDiagSlideConfGeneralAllSlidesCheckBox1.setEnabled(False)
        qt.sysDiagSlideConfGeneralAllSlidesCheckBox2.setChecked(False)
        qt.sysDiagSlideConfGeneralAllSlidesCheckBox2.setEnabled(False)
        qt.sysDiagSlideConfGeneralAllSlidesCheckBox3.setChecked(False)
        qt.sysDiagSlideConfGeneralAllSlidesCheckBox3.setEnabled(False)

        qt.sysDiagSlideConfGeneralAllSlidesComboBox1.setEnabled(False)
        qt.sysDiagSlideConfGeneralAllSlidesComboBox2.setEnabled(False)
        qt.sysDiagSlideConfGeneralAllSlidesComboBox3.setEnabled(False)

    parseDataLog.debug('plotSetup: ' + str(antSysDiag.plotSetup))


qt.sysDiagSlideConfGeneralAllSlidesComboBox1.setCurrentIndex(0)
qt.sysDiagSlideConfGeneralAllSlidesComboBox2.setCurrentIndex(8)
qt.sysDiagSlideConfGeneralAllSlidesComboBox3.setCurrentIndex(6)

antSysDiag.AllGraphsConf1['graphType'] = 'level'
antSysDiag.AllGraphsConf2['graphType'] = 'corrPhaseDiff'
antSysDiag.AllGraphsConf3['graphType'] = 'diffPhaseDiff'


def sysDiagSlideConfGeneralAllSlidesComboBox1Click(idx):
    antSysDiag.AllGraphsConf1['graphType'] = qt.sysDiagSlideConfGeneralAllSlidesComboBox1.itemText(idx)
    parseDataLog.debug('AllGraphsConf1: ' + str(antSysDiag.AllGraphsConf1))


def sysDiagSlideConfGeneralAllSlidesComboBox2Click(idx):
    antSysDiag.AllGraphsConf2['graphType'] = qt.sysDiagSlideConfGeneralAllSlidesComboBox2.itemText(idx)
    parseDataLog.debug('AllGraphsConf2: ' + str(antSysDiag.AllGraphsConf2))


def sysDiagSlideConfGeneralAllSlidesComboBox3Click(idx):
    antSysDiag.AllGraphsConf3['graphType'] = qt.sysDiagSlideConfGeneralAllSlidesComboBox3.itemText(idx)
    parseDataLog.debug('AllGraphsConf3: ' + str(antSysDiag.AllGraphsConf3))

qt.sysDiagPlotSetupScriptModeRadio1.setChecked(True)
qt.sysDiagPlotSetupScriptModeRadio2.setChecked(False)
antSysDiag.plotSetup['ShowCertainPlotWindow'] = 0
qt.sysDiagPlotWindowGroupBox.setEnabled(False)
qt.sysDiagSlideConfGroupBox.setEnabled(True)


def sysDiagPlotSetupScriptModeGroupClick():
    btnId = qt.sysDiagPlotSetupScriptModeGroup.checkedId()
    if btnId == 0:
        antSysDiag.plotSetup['ShowCertainPlotWindow'] = 0
        qt.sysDiagPlotWindowGroupBox.setEnabled(False)
        qt.sysDiagSlideConfGroupBox.setEnabled(True)

        qt.sysDiagPlotWindowAllGraphsCheckBox.setChecked(False)

        qt.sysDiagPlotWindowAllGraphsCheckBox1.setChecked(False)
        qt.sysDiagPlotWindowAllGraphsCheckBox2.setChecked(False)
        qt.sysDiagPlotWindowAllGraphsCheckBox3.setChecked(False)
        qt.sysDiagPlotWindowAllGraphsComboBox1.setCurrentIndex(0)
        qt.sysDiagPlotWindowAllGraphsComboBox2.setCurrentIndex(8)
        qt.sysDiagPlotWindowAllGraphsComboBox3.setCurrentIndex(6)

        qt.sysDiagPlotWindowAllGraphsCheckBox1.setEnabled(False)
        qt.sysDiagPlotWindowAllGraphsCheckBox2.setEnabled(False)
        qt.sysDiagPlotWindowAllGraphsCheckBox3.setEnabled(False)

        qt.sysDiagPlotWindowAllGraphsComboBox1.setEnabled(False)
        qt.sysDiagPlotWindowAllGraphsComboBox2.setEnabled(False)
        qt.sysDiagPlotWindowAllGraphsComboBox3.setEnabled(False)

        parseDataLog.debug('plotSetup: ' + str(antSysDiag.plotSetup))
    elif btnId == 1:
        antSysDiag.plotSetup['ShowCertainPlotWindow'] = 1
        qt.sysDiagPlotWindowGroupBox.setEnabled(True)
        qt.sysDiagSlideConfGroupBox.setEnabled(False)

        qt.sysDiagPlotWindowAllGraphsCheckBox1.setChecked(False)
        qt.sysDiagPlotWindowAllGraphsCheckBox2.setChecked(False)
        qt.sysDiagPlotWindowAllGraphsCheckBox3.setChecked(False)
        qt.sysDiagPlotWindowAllGraphsComboBox1.setCurrentIndex(0)
        qt.sysDiagPlotWindowAllGraphsComboBox2.setCurrentIndex(8)
        qt.sysDiagPlotWindowAllGraphsComboBox3.setCurrentIndex(6)

        qt.sysDiagPlotWindowAllGraphsCheckBox1.setEnabled(False)
        qt.sysDiagPlotWindowAllGraphsCheckBox2.setEnabled(False)
        qt.sysDiagPlotWindowAllGraphsCheckBox3.setEnabled(False)

        qt.sysDiagPlotWindowAllGraphsComboBox1.setEnabled(False)
        qt.sysDiagPlotWindowAllGraphsComboBox2.setEnabled(False)
        qt.sysDiagPlotWindowAllGraphsComboBox3.setEnabled(False)

        parseDataLog.debug('plotSetup: ' + str(antSysDiag.plotSetup))

#####
qt.sysDiagPlotWindowInputModeRadio1.setChecked(True)
qt.sysDiagPlotWindowInputModeRadio2.setChecked(False)
antSysDiag.plotWindowConfig['inputMode'] = 1
qt.sysDiagPlotWindowInputModeLEdit.setEnabled(False)


def sysDiagPlotWindowInputModeClick():
    btnId = qt.sysDiagPlotWindowInputModeGroup.checkedId()
    if btnId == 0:
        antSysDiag.plotWindowConfig['inputMode']=1
        qt.sysDiagPlotWindowInputModeLEdit.setEnabled(False)

    elif btnId == 1:
        antSysDiag.plotWindowConfig['inputMode']=0
        qt.sysDiagPlotWindowInputModeLEdit.setEnabled(True)

    parseDataLog.debug('plotWindowConfig: ' + str(antSysDiag.plotWindowConfig))


antSysDiag.plotWindowConfig['string'] = ''

qt.sysDiagPlotWindowAntTypLEdit.setText('0')

if sp.checkInt(qt.sysDiagPlotWindowAntTypLEdit.text()) == True:
    antSysDiag.plotWindowConfig['antType'] = int(qt.sysDiagPlotWindowAntTypLEdit.text())
antSysDiag.plotWindowConfig['antType'] = 0

qt.sysDiagPlotWindowDiagNumLEdit.setText('0')

if sp.checkInt(qt.sysDiagPlotWindowDiagNumLEdit.text()) == True:
    antSysDiag.plotWindowConfig['diagramNum'] = int(qt.sysDiagPlotWindowDiagNumLEdit.text())
antSysDiag.plotWindowConfig['diagramNum'] = 0
qt.sysDiagPlotWindowRxChLEdit.setText('0')

if sp.checkInt(qt.sysDiagPlotWindowRxChLEdit.text()) == True:
    antSysDiag.plotWindowConfig['rxCh'] = int(qt.sysDiagPlotWindowRxChLEdit.text())
antSysDiag.plotWindowConfig['rxCh'] = 0


def sysDiagPlotWindowGraphTypeComboBoxClick(idx):
    antSysDiag.plotWindowConfig['graph'] = qt.sysDiagPlotWindowGraphTypeComboBox.itemText(idx)
    parseDataLog.debug('plotWindowConfig: ' + str(antSysDiag.plotWindowConfig))

antSysDiag.plotWindowConfig['graph'] = 'level'

qt.sysDiagPlotWindowAllGraphsCheckBox.setChecked(False)

qt.sysDiagPlotWindowAllGraphsCheckBox1.setChecked(False)
qt.sysDiagPlotWindowAllGraphsCheckBox2.setChecked(False)
qt.sysDiagPlotWindowAllGraphsCheckBox3.setChecked(False)
qt.sysDiagPlotWindowAllGraphsComboBox1.setCurrentIndex(0)
qt.sysDiagPlotWindowAllGraphsComboBox2.setCurrentIndex(8)
qt.sysDiagPlotWindowAllGraphsComboBox3.setCurrentIndex(6)


def sysDiagPlotWindowAllGraphsComboBox1Click(idx):
    antSysDiag.AllGraphsConf1['graphType'] = qt.sysDiagPlotWindowAllGraphsComboBox1.itemText(idx)
    parseDataLog.debug('AllGraphsConf1: ' + str(antSysDiag.AllGraphsConf1))


def sysDiagPlotWindowAllGraphsComboBox2Click(idx):
    antSysDiag.AllGraphsConf2['graphType'] = qt.sysDiagPlotWindowAllGraphsComboBox2.itemText(idx)
    parseDataLog.debug('AllGraphsConf2: ' + str(antSysDiag.AllGraphsConf2))


def sysDiagPlotWindowAllGraphsComboBox3Click(idx):
    antSysDiag.AllGraphsConf3['graphType'] = qt.sysDiagPlotWindowAllGraphsComboBox3.itemText(idx)
    parseDataLog.debug('AllGraphsConf3: ' + str(antSysDiag.AllGraphsConf3))


def sysDiagPlotWindowAllGraphsClick():
    state = qt.sysDiagPlotWindowAllGraphsCheckBox.isChecked()
    if state == 1:
        antSysDiag.plotWindowConfig['showPlotAllMode'] = 1
        qt.sysDiagPlotWindowAllGraphsCheckBox1.setEnabled(True)
        qt.sysDiagPlotWindowAllGraphsCheckBox2.setEnabled(True)
        qt.sysDiagPlotWindowAllGraphsCheckBox3.setEnabled(True)
        qt.sysDiagPlotWindowAllGraphsCheckBox1.setChecked(True)
        qt.sysDiagPlotWindowAllGraphsCheckBox2.setChecked(True)
        qt.sysDiagPlotWindowAllGraphsCheckBox3.setChecked(True)

        qt.sysDiagPlotWindowAllGraphsComboBox1.setEnabled(True)
        qt.sysDiagPlotWindowAllGraphsComboBox2.setEnabled(True)
        qt.sysDiagPlotWindowAllGraphsComboBox3.setEnabled(True)
        # qt.sysDiagSlideConfGroupBox.setEnabled(True)
    else:
        antSysDiag.plotWindowConfig['showPlotAllMode'] = 0
        qt.sysDiagPlotWindowAllGraphsCheckBox1.setEnabled(False)
        qt.sysDiagPlotWindowAllGraphsCheckBox2.setEnabled(False)
        qt.sysDiagPlotWindowAllGraphsCheckBox3.setEnabled(False)
        qt.sysDiagPlotWindowAllGraphsCheckBox1.setChecked(False)
        qt.sysDiagPlotWindowAllGraphsCheckBox2.setChecked(False)
        qt.sysDiagPlotWindowAllGraphsCheckBox3.setChecked(False)

        qt.sysDiagPlotWindowAllGraphsComboBox1.setEnabled(False)
        qt.sysDiagPlotWindowAllGraphsComboBox2.setEnabled(False)
        qt.sysDiagPlotWindowAllGraphsComboBox3.setEnabled(False)
        # qt.sysDiagSlideConfGroupBox.setEnabled(False)

qt.sysDiagInputSetupAngleGroup.buttonClicked.connect(sysDiagInputSetupAngleGroupClick)
qt.sysDiagInputSetupSensorOrientGroup.buttonClicked.connect(sysDiagInputSetupSensorOrientGroupClick)
qt.sysDiagInputSetupChirpGroup.buttonClicked.connect(sysDiagInputSetupChirpClick)
qt.sysDiagInputSetupDiagConfGroup.buttonClicked.connect(sysDiagInputSetupDiagConfigInputModeClick)
qt.sysDiagInputSetupDiagConfOddEvenGroup.buttonClicked.connect(sysDiagInputSetupDiagConfOddEvenClick)
qt.sysDiagPlotSetupImgGenGroup.buttonClicked.connect(sysDiagPlotSetupImgGenClick)
qt.sysDiagPlotSetupScalingYLimitsGroup.buttonClicked.connect(sysDiagPlotSetupScalingYLimitsClick)
qt.sysDiagPlotSetup3GraphLayoutImgCheckBox.stateChanged.connect(sysDiagPlotSetup3GraphLayoutImgClick)
qt.sysDiagPlotSetupScalingAutoCheckBox.stateChanged.connect(sysDiagPlotSetupScalingAutoClick)
qt.sysDiagPlotSetupGraphConfGroup.buttonClicked.connect(sysDiagPlotSetupGraphConfClick)
qt.sysDiagPlotSetupGraphConfIdealCurveCheckBox.stateChanged.connect(sysDiagPlotSetupGraphConfIdealCurveClick)

qt.sysDiagSlideConfGeneralAllGraphsSlideCheckBox.stateChanged.connect(sysDiagSlideConfGeneralAllGraphsSlideClick)
qt.sysDiagSlideConfGeneralAllSlidesComboBox1.currentIndexChanged.connect(sysDiagSlideConfGeneralAllSlidesComboBox1Click)
qt.sysDiagSlideConfGeneralAllSlidesComboBox2.currentIndexChanged.connect(sysDiagSlideConfGeneralAllSlidesComboBox2Click)
qt.sysDiagSlideConfGeneralAllSlidesComboBox3.currentIndexChanged.connect(sysDiagSlideConfGeneralAllSlidesComboBox3Click)

qt.sysDiagPlotSetupScriptModeGroup.buttonClicked.connect(sysDiagPlotSetupScriptModeGroupClick)
qt.sysDiagPlotWindowInputModeGroup.buttonClicked.connect(sysDiagPlotWindowInputModeClick)
qt.sysDiagPlotWindowGraphTypeComboBox.currentIndexChanged.connect(sysDiagPlotWindowGraphTypeComboBoxClick)
qt.sysDiagPlotWindowAllGraphsCheckBox.stateChanged.connect(sysDiagPlotWindowAllGraphsClick)


qt.sysDiagPlotWindowAllGraphsComboBox1.currentIndexChanged.connect(sysDiagPlotWindowAllGraphsComboBox1Click)
qt.sysDiagPlotWindowAllGraphsComboBox2.currentIndexChanged.connect(sysDiagPlotWindowAllGraphsComboBox2Click)
qt.sysDiagPlotWindowAllGraphsComboBox3.currentIndexChanged.connect(sysDiagPlotWindowAllGraphsComboBox3Click)


qt.sysDiagSlideConfTwoGraphComboBox11.currentIndexChanged.connect(sysDiagSlideConfTwoGraphComboBox11Click)
qt.sysDiagSlideConfTwoGraphComboBox12.currentIndexChanged.connect(sysDiagSlideConfTwoGraphComboBox12Click)
qt.sysDiagSlideConfTwoGraphComboBox21.currentIndexChanged.connect(sysDiagSlideConfTwoGraphComboBox21Click)
qt.sysDiagSlideConfTwoGraphComboBox22.currentIndexChanged.connect(sysDiagSlideConfTwoGraphComboBox22Click)

qt.sysDiagSlideConfFourGraphComboBox1.currentIndexChanged.connect(sysDiagSlideConfFourGraphComboBox1Click)
qt.sysDiagSlideConfFourGraphComboBox2.currentIndexChanged.connect(sysDiagSlideConfFourGraphComboBox2Click)
qt.sysDiagSlideConfFourGraphComboBox3.currentIndexChanged.connect(sysDiagSlideConfFourGraphComboBox3Click)

qt.sysDiagSlideConfThreeGraphComboBox1.currentIndexChanged.connect(sysDiagSlideConfThreeGraphComboBox1Click)
qt.sysDiagSlideConfThreeGraphComboBox2.currentIndexChanged.connect(sysDiagSlideConfThreeGraphComboBox2Click)
qt.sysDiagSlideConfThreeGraphComboBox3.currentIndexChanged.connect(sysDiagSlideConfThreeGraphComboBox3Click)


def data_update_and_evaluation(parsedDataList, twoGraphSetupList, fourGraphSetupList, threeGraphSetupList, allOnOneSlideGraphList, diagramConfigList, sysDiagLogger, output_pathpptx, pptxTitle, temp):

    twoGraphSetupList[:]      = []
    fourGraphSetupList[:]     = []
    threeGraphSetupList[:]    = []
    allOnOneSlideGraphList[:] = []
    diagramConfigList[:]      = []
    antSysDiag.plotSetup['sensorMusterList'][:] = []

    if antSysDiag.plotSetup['useSensorMuster'] == 1:

        sensorMusterInputList=qt.parseProtSensorMusterLEdit.text()
        sensorMusterList=sensorMusterInputList.split(' ')
        for part in sensorMusterList:
            if part != '':
                antSysDiag.plotSetup['sensorMusterList'].append(part)

    desDiagListString = qt.sysDiagInputSetupDiagConfigDesListLEdit.text()
    desDiagList = desDiagListString.split(',')
    for char in desDiagList:
        if char != '':
            if sp.checkInt(char) == True:
                diagramConfigList.append(int(char))




    if sp.checkInt(qt.sysDiagInputSetupDiagConfigDesRangeLowLEdit.text()) == True:
        antSysDiag.diagramConfig['lowerNumber'] = int(qt.sysDiagInputSetupDiagConfigDesRangeLowLEdit.text())

    if sp.checkInt(qt.sysDiagInputSetupDiagConfigDesRangeHighLEdit.text()) == True:
        antSysDiag.diagramConfig['higherNumber'] = int(qt.sysDiagInputSetupDiagConfigDesRangeHighLEdit.text())

    if sp.checkInt(qt.sysDiagPlotSetupImageDpiLEdit.text()) == True:
        antSysDiag.plotSetup['imageDpi'] = int(qt.sysDiagPlotSetupImageDpiLEdit.text())

    if sp.checkDecimal(qt.sysDiagPlotSetupScalingXScaleAzLEdit.text()) == True:
        antSysDiag.plotSetup['xScaleSizeAz'] = float(qt.sysDiagPlotSetupScalingXScaleAzLEdit.text())

    if sp.checkDecimal(qt.sysDiagPlotSetupScalingXScaleElLEdit.text()) == True:
        antSysDiag.plotSetup['xScaleSizeEl'] = float(qt.sysDiagPlotSetupScalingXScaleElLEdit.text())

    if sp.checkDecimal(qt.sysDiagPlotSetupScalingDiffPhDiffLEdit.text()) == True:
        antSysDiag.plotSetup['diffPhaseDiffScalingFactor'] = float(qt.sysDiagPlotSetupScalingDiffPhDiffLEdit.text())

    if sp.checkInt(qt.sysDiagPlotWindowDiagNumLEdit.text()) == True:
        antSysDiag.plotWindowConfig['diagramNum'] = int(qt.sysDiagPlotWindowDiagNumLEdit.text())

    if sp.checkInt(qt.sysDiagPlotWindowRxChLEdit.text()) == True:
        antSysDiag.plotWindowConfig['rxCh'] = int(qt.sysDiagPlotWindowRxChLEdit.text())

    if sp.checkInt(qt.sysDiagPlotWindowAntTypLEdit.text()) == True:
        antSysDiag.plotWindowConfig['antType'] = int(qt.sysDiagPlotWindowAntTypLEdit.text())

    antSysDiag.plotWindowConfig['string']=qt.sysDiagPlotWindowInputModeLEdit.text()

    if sp.checkInt(qt.sysDiagSlideConfGeneralSensorNumSlideLEdit.text()) == True:
        antSysDiag.plotSetup['nofSensorMeasToShow'] = int(qt.sysDiagSlideConfGeneralSensorNumSlideLEdit.text())

    if qt.sysDiagSlideConfTwoGraphCheckBox1.isChecked() == True:
        twoGraphSetupList.append(antSysDiag.twoGraphConf1)
    if qt.sysDiagSlideConfTwoGraphCheckBox2.isChecked() == True:
        twoGraphSetupList.append(antSysDiag.twoGraphConf2)

    if qt.sysDiagSlideConfFourGraphCheckBox1.isChecked() == True:
        fourGraphSetupList.append(antSysDiag.fourGraphConf1)

    if qt.sysDiagSlideConfFourGraphCheckBox2.isChecked() == True:
        fourGraphSetupList.append(antSysDiag.fourGraphConf2)

    if qt.sysDiagSlideConfFourGraphCheckBox3.isChecked() == True:
        fourGraphSetupList.append(antSysDiag.fourGraphConf3)

    if qt.sysDiagSlideConfThreeGraphCheckBox1.isChecked() == True:
        threeGraphSetupList.append(antSysDiag.threeGraphConf1)

    if qt.sysDiagSlideConfThreeGraphCheckBox2.isChecked() == True:
        threeGraphSetupList.append(antSysDiag.threeGraphConf2)

    if qt.sysDiagSlideConfThreeGraphCheckBox3.isChecked() == True:
        threeGraphSetupList.append(antSysDiag.threeGraphConf3)

    ####
    scriptMode = qt.sysDiagPlotSetupScriptModeGroup.checkedId()
    if scriptMode ==0:
        if qt.sysDiagSlideConfGeneralAllSlidesCheckBox1.isChecked() == True:
            allOnOneSlideGraphList.append(antSysDiag.AllGraphsConf1)
        if qt.sysDiagSlideConfGeneralAllSlidesCheckBox2.isChecked() == True:
            allOnOneSlideGraphList.append(antSysDiag.AllGraphsConf2)
        if qt.sysDiagSlideConfGeneralAllSlidesCheckBox3.isChecked() == True:
            allOnOneSlideGraphList.append(antSysDiag.AllGraphsConf3)
    else:
        if qt.sysDiagPlotWindowAllGraphsCheckBox1.isChecked() == True:
            allOnOneSlideGraphList.append(antSysDiag.AllGraphsConf1)
        if qt.sysDiagPlotWindowAllGraphsCheckBox2.isChecked() == True:
            allOnOneSlideGraphList.append(antSysDiag.AllGraphsConf2)
        if qt.sysDiagPlotWindowAllGraphsCheckBox3.isChecked() == True:
            allOnOneSlideGraphList.append(antSysDiag.AllGraphsConf3)

    antSysDiag.start_data_evaluation(parsedDataList, antSysDiag.plotSetup, antSysDiag.chirpConfig, antSysDiag.graphConfig, antSysDiag.diagramConfig,
    twoGraphSetupList, fourGraphSetupList, threeGraphSetupList, allOnOneSlideGraphList, diagramConfigList, sysDiagLogger, output_pathpptx, pptxTitle, temp)

qt.sysDiagStartPushBtn.clicked.connect(lambda:data_update_and_evaluation(sysDiagParsedDataDict['parsedDataList'], antSysDiag.twoGraphSetupList, antSysDiag.fourGraphSetupList, antSysDiag.threeGraphSetupList, antSysDiag.allOnOneSlideGraphList, antSysDiag.diagramConfigList, sysDiagLogger, aux.antSysDiagOutputPath, 'Antenna_diagrams.pptx', './assets/template.pptx') )

# fill up the table
# qt.SysDiaInterStartBtn.clicked.connect(lambda: addAndParsePtu2Files(sysDiagParsedDataDict,separatePtu2ParsedDataDict,separatePtu2FailedDataDict))
qt.SysDiaInterStartBtn.clicked.connect(lambda: antSysDiag.fillInPTU(sysDiagParsedDataDict['parsedDataList'], sysDiagLogger))

## Tx-Antenna Diagrams

### Input Setup

qt.txAntDiagInputSetupAngleSetupRadio1.setChecked(True)
qt.txAntDiagInputSetupAngleSetupRadio2.setChecked(False)
txAntDiag.plotSetup['targetAngle'] = 1


def txAntDiagInputSetupAngleGroupClick():
    btnId = qt.txAntDiagInputSetupAngleGroup.checkedId()
    if btnId == 0:
        txAntDiag.plotSetup['targetAngle'] = 1
        parseDataLog.debug('plotSetup: ' + str(txAntDiag.plotSetup))
    elif btnId == 1:
        txAntDiag.plotSetup['targetAngle'] = 0
        parseDataLog.debug('plotSetup: ' + str(txAntDiag.plotSetup))


qt.txAntDiagInputSetupSensorOrientRadio1.setChecked(True)
qt.txAntDiagInputSetupSensorOrientRadio2.setChecked(False)
txAntDiag.plotSetup['upsideDown'] = 0


def txAntDiagInputSetupSensorOrientGroupClick():
    btnId = qt.txAntDiagInputSetupSensorOrientGroup.checkedId()
    if btnId == 0:
        txAntDiag.plotSetup['upsideDown'] = 0
        parseDataLog.debug('plotSetup: ' + str(txAntDiag.plotSetup))
    elif btnId == 1:
        txAntDiag.plotSetup['upsideDown'] = 1
        parseDataLog.debug('plotSetup: ' + str(txAntDiag.plotSetup))


qt.txAntDiagInputSetupAzCheckBox.setChecked(True)
qt.txAntDiagInputSetupElCheckBox.setChecked(False)

txAntDiag.plotSetup['AzDiag'] = 1
txAntDiag.plotSetup['ElDiag'] = 0


def txAntDiagInputSetupAzClick():
    state = qt.txAntDiagInputSetupAzCheckBox.isChecked()
    if state == 1:
        txAntDiag.plotSetup['AzDiag'] = 1
    else:
        txAntDiag.plotSetup['AzDiag'] = 0
    parseDataLog.debug('plotSetup: ' + str(txAntDiag.plotSetup))


def txAntDiagInputSetupElClick():
    state = qt.txAntDiagInputSetupElCheckBox.isChecked()
    if state == 1:
        txAntDiag.plotSetup['ElDiag'] = 1
    else:
        txAntDiag.plotSetup['ElDiag'] = 0
    parseDataLog.debug('plotSetup: ' + str(txAntDiag.plotSetup))

#####
qt.txAntDiagPlotSetupSensorNumSlideLEdit.setText('32')
if sp.checkInt(qt.txAntDiagPlotSetupSensorNumSlideLEdit.text()) == True:
    txAntDiag.plotSetup['nofSensorMeasToShow'] = int(qt.txAntDiagPlotSetupSensorNumSlideLEdit.text())

qt.txAntDiagPlotSetupGraphsPerSlideLEdit.setText('1')
if sp.checkInt(qt.txAntDiagPlotSetupGraphsPerSlideLEdit.text()) == True:
    txAntDiag.plotSetup['graphsPerSlide'] = int(qt.txAntDiagPlotSetupGraphsPerSlideLEdit.text())

qt.txAntDiagPlotSetupImageDpiLEdit.setText('220')
if sp.checkInt(qt.txAntDiagPlotSetupImageDpiLEdit.text()) == True:
    txAntDiag.plotSetup['imageDpi'] = int(qt.txAntDiagPlotSetupImageDpiLEdit.text())

#####
qt.txAntDiagPlotSetupScalingAutoCheckBox.setChecked(False)
txAntDiag.plotSetup['xScaleSizeAuto'] = 0


def txAntDiagPlotSetupScalingAutoClick():
    state = qt.txAntDiagPlotSetupScalingAutoCheckBox.isChecked()
    if state == 1:
        txAntDiag.plotSetup['xScaleSizeAuto'] = 1
    else:
        txAntDiag.plotSetup['xScaleSizeAuto'] = 0
    parseDataLog.debug('plotSetup: ' + str(txAntDiag.plotSetup))

qt.txAntDiagPlotSetupScalingXScaleAzLEdit.setText('90')
qt.txAntDiagPlotSetupScalingXScaleElLEdit.setText('45')
if sp.checkDecimal(qt.txAntDiagPlotSetupScalingXScaleAzLEdit.text()) == True:
    txAntDiag.plotSetup['xScaleSizeAz'] = float(qt.txAntDiagPlotSetupScalingXScaleAzLEdit.text())

if sp.checkDecimal(qt.txAntDiagPlotSetupScalingXScaleElLEdit.text()) == True:
    txAntDiag.plotSetup['xScaleSizeEl'] = float(qt.txAntDiagPlotSetupScalingXScaleElLEdit.text())

qt.txAntDiagPlotSetupScalingOrigGraphsCheckBox.setChecked(True)
txAntDiag.plotSetup['plotOrigGraphs'] = 1

qt.txAntDiagPlotSetupScalingNormGraphsCheckBox.setChecked(True)
txAntDiag.plotSetup['plotNormGraphs'] = 1


def txAntDiagPlotSetupScalingOrigGraphsClick():
    state = qt.txAntDiagPlotSetupScalingOrigGraphsCheckBox.isChecked()
    if state == 1:
        txAntDiag.plotSetup['plotOrigGraphs'] = 1
    else:
        txAntDiag.plotSetup['plotOrigGraphs'] = 0
    parseDataLog.debug('plotSetup: ' + str(txAntDiag.plotSetup))


def txAntDiagPlotSetupScalingNormGraphsClick():
    state = qt.txAntDiagPlotSetupScalingNormGraphsCheckBox.isChecked()
    if state == 1:
        txAntDiag.plotSetup['plotNormGraphs'] = 1
    else:
        txAntDiag.plotSetup['plotNormGraphs'] = 0
    parseDataLog.debug('plotSetup: ' + str(txAntDiag.plotSetup))

#####
graphId = 0
for key, val in txAntDiag.graphConfig.items():
    button = qt.txAntDiagPlotSetupGraphConfGroup.button(graphId)

    txAntDiag.graphConfig[key] = 1
    button.setChecked(True)

    graphId += 1


def txAntDiagPlotSetupGraphConfClick(btn):

    i = 0
    setKey = ''
    state  = 0
    btnId  = qt.txAntDiagPlotSetupGraphConfGroup.id(btn)
    for key, val in txAntDiag.graphConfig.items():

        if i == btnId:
            chBox  = qt.txAntDiagPlotSetupGraphConfGroup.button(btnId)
            state  = chBox.isChecked()
            setKey = key

            break

        i = i + 1

    txAntDiag.graphConfig[setKey] = qt.boolMapping(state)

    parseDataLog.debug('graphConfig: ' + str(txAntDiag.graphConfig))


#####
qt.txAntDiagInputSetupAngleGroup.buttonClicked.connect(txAntDiagInputSetupAngleGroupClick)
qt.txAntDiagInputSetupSensorOrientGroup.buttonClicked.connect(txAntDiagInputSetupSensorOrientGroupClick)

qt.txAntDiagInputSetupAzCheckBox.stateChanged.connect(txAntDiagInputSetupAzClick)
qt.txAntDiagInputSetupElCheckBox.stateChanged.connect(txAntDiagInputSetupElClick)

qt.txAntDiagPlotSetupScalingAutoCheckBox.stateChanged.connect(txAntDiagPlotSetupScalingAutoClick)
qt.txAntDiagPlotSetupScalingOrigGraphsCheckBox.stateChanged.connect(txAntDiagPlotSetupScalingOrigGraphsClick)
qt.txAntDiagPlotSetupScalingNormGraphsCheckBox.stateChanged.connect(txAntDiagPlotSetupScalingNormGraphsClick)

qt.txAntDiagPlotSetupGraphConfGroup.buttonClicked.connect(txAntDiagPlotSetupGraphConfClick)


def txantdiag_data_update_and_evaluation(parsedDataList, txAntDiagLogger, output_pathpptx, pptxTitle, starttemp):

    txAntDiag.plotSetup['sensorMusterList'][:] = []

    if txAntDiag.plotSetup['useSensorMuster'] == 1:

        sensorMusterInputList = qt.parseProtSensorMusterLEdit.text()
        sensorMusterList = sensorMusterInputList.split(' ')
        for part in sensorMusterList:
            if part != '':
                txAntDiag.plotSetup['sensorMusterList'].append(part)

    if sp.checkInt(qt.txAntDiagPlotSetupImageDpiLEdit.text()) == True:
        txAntDiag.plotSetup['imageDpi'] = int(qt.txAntDiagPlotSetupImageDpiLEdit.text())

    if sp.checkDecimal(qt.txAntDiagPlotSetupScalingXScaleAzLEdit.text()) == True:
        txAntDiag.plotSetup['xScaleSizeAz'] = float(qt.txAntDiagPlotSetupScalingXScaleAzLEdit.text())

    if sp.checkDecimal(qt.txAntDiagPlotSetupScalingXScaleElLEdit.text()) == True:
        txAntDiag.plotSetup['xScaleSizeEl'] = float(qt.txAntDiagPlotSetupScalingXScaleElLEdit.text())

    if sp.checkInt(qt.txAntDiagPlotSetupSensorNumSlideLEdit.text()) == True:
        txAntDiag.plotSetup['nofSensorMeasToShow'] = int(qt.txAntDiagPlotSetupSensorNumSlideLEdit.text())

    if sp.checkInt(qt.txAntDiagPlotSetupGraphsPerSlideLEdit.text()) == True:
        txAntDiag.plotSetup['graphsPerSlide'] = int(qt.txAntDiagPlotSetupGraphsPerSlideLEdit.text())

    txAntDiag.start_data_evaluation(parsedDataList, txAntDiag.plotSetup, txAntDiag.graphConfig, txAntDiagLogger, output_pathpptx, pptxTitle, starttemp)

qt.txAntDiagStartPushBtn.clicked.connect(lambda:txantdiag_data_update_and_evaluation(txAntDiagParsedDataDict['parsedDataList'], txAntDiagLogger, aux.txAntDiagOutputPath, 'TxAnt_Diagrams.pptx', './assets/template.pptx' ))

## Antenna Patterns

### Table Configuration

from PySide6.QtCore import QSignalMapper

antPatTableList = []
antPatControl   = {
    'version': 0,
}
for tabIdx in range(len(qt.antPatTableWidgetsList)):

    antPatTable = {
        'antenna_pattern_idx': 0,
        'patternType': 0,
        'rotationAxis': 0,
        'nofApplicableTxAnt': 0,
        'nofApplicableRxAnt': 0,
        'applTxAntInd': [],
        'applRxAntInd': [],
        'gainCalcMethod': 0
    }

    antPatTable['antenna_pattern_idx'] = tabIdx

    if tabIdx < 4:
        qt.antPatTableWidgetsList[tabIdx]['tableCheckBox'].setChecked(True)

    qt.antPatTableWidgetsList[tabIdx]['patTypeComboBox'].setCurrentIndex(1)
    antPatTable['patternType'] = qt.antPatTableWidgetsList[tabIdx]['patTypeComboBox'].currentIndex()


    qt.antPatTableWidgetsList[tabIdx]['rotAxisComboBox'].setCurrentIndex(1)
    antPatTable['rotationAxis'] = qt.antPatTableWidgetsList[tabIdx]['rotAxisComboBox'].currentIndex()

    qt.antPatTableWidgetsList[tabIdx]['gainCalcMethodComboBox'].setCurrentIndex(1)
    antPatTable['gainCalcMethod'] = qt.antPatTableWidgetsList[tabIdx]['gainCalcMethodComboBox'].currentIndex()

    qt.antPatTableWidgetsList[tabIdx]['nofAppTxAntIdxLEdit'].setText('1')

    if sp.checkInt(qt.antPatTableWidgetsList[tabIdx]['nofAppTxAntIdxLEdit'].text()) == True:
        antPatTable['nofApplicableTxAnt'] = int(qt.antPatTableWidgetsList[tabIdx]['nofAppTxAntIdxLEdit'].text())

    qt.antPatTableWidgetsList[tabIdx]['nofAppRxAntIdxLEdit'].setText('4')
    if sp.checkInt(qt.antPatTableWidgetsList[tabIdx]['nofAppRxAntIdxLEdit'].text()) == True:
        antPatTable['nofApplicableRxAnt'] = int(qt.antPatTableWidgetsList[tabIdx]['nofAppRxAntIdxLEdit'].text())

    qt.antPatTableWidgetsList[tabIdx]['appTxAntIdxLEdit'].setText('0')
    # if sp.checkInt(qt.antPatTableAppTxAntIdxLEdit.text()) == True:
    #     antPatTable['applTxAntInd'] = int(qt.antPatTableAppTxAntIdxLEdit.text())
    qt.antPatTableWidgetsList[tabIdx]['appRxAntIdxLEdit'].setText('0, 1, 2, 3')
    # if sp.checkInt(qt.antPatTableAppRxAntIdxLEdit.text()) == True:
    #     antPatTable['applRxAntInd'] = int(qt.antPatTableAppRxAntIdxLEdit.text())

    antPatTableList.append(antPatTable)


def antPatTablePatTypeClick(tabIdx):
    combo = qt.antPatTableWidgetsList[tabIdx]['patTypeComboBox']
    idx = combo.currentIndex()
    if idx == 0:
        antPatTableList[tabIdx]['patternType'] = 0
    elif idx == 1:
        antPatTableList[tabIdx]['patternType'] = 1
    elif idx == 2:
        antPatTableList[tabIdx]['patternType'] = 2
    elif idx == 3:
        antPatTableList[tabIdx]['patternType'] = 3

    parseDataLog.debug('Table' + str(tabIdx) + ': ' + str(antPatTableList[tabIdx]))


def antPatTableRotAxisClick(tabIdx):
    combo = qt.antPatTableWidgetsList[tabIdx]['rotAxisComboBox']
    idx = combo.currentIndex()
    if idx == 0:
        antPatTableList[tabIdx]['rotationAxis'] = 0
    elif idx == 1:
        antPatTableList[tabIdx]['rotationAxis'] = 1
    elif idx == 2:
        antPatTableList[tabIdx]['rotationAxis'] = 2
    elif idx == 3:
        antPatTableList[tabIdx]['rotationAxis'] = 3

    parseDataLog.debug('Table' + str(tabIdx) + ': ' + str(antPatTableList[tabIdx]))


def antPatTableGainCalcMethodClick(tabIdx):
    combo = qt.antPatTableWidgetsList[tabIdx]['gainCalcMethodComboBox']
    idx = combo.currentIndex()
    if idx == 0:
        antPatTableList[tabIdx]['gainCalcMethod'] = 0
    elif idx == 1:
        antPatTableList[tabIdx]['gainCalcMethod'] = 1
    elif idx == 2:
        antPatTableList[tabIdx]['gainCalcMethod'] = 2


    parseDataLog.debug('Table' + str(tabIdx) + ': ' + str(antPatTableList[tabIdx]))

######
#######
##
antPatPatTypeSignalMapper = QSignalMapper()
antPatPatTypeSignalMapper.mappedInt.connect(antPatTablePatTypeClick)

antPatRotAxisSignalMapper = QSignalMapper()
antPatRotAxisSignalMapper.mappedInt.connect(antPatTableRotAxisClick)

antPatGainCalcMethodSignalMapper = QSignalMapper()
antPatGainCalcMethodSignalMapper.mappedInt.connect(antPatTableGainCalcMethodClick)

for tabIdx in range(len(qt.antPatTableWidgetsList)):
    qt.antPatTableWidgetsList[tabIdx]['patTypeComboBox'].currentIndexChanged.connect(antPatPatTypeSignalMapper.map)
    antPatPatTypeSignalMapper.setMapping(qt.antPatTableWidgetsList[tabIdx]['patTypeComboBox'], tabIdx)

    qt.antPatTableWidgetsList[tabIdx]['rotAxisComboBox'].currentIndexChanged.connect(antPatRotAxisSignalMapper.map)
    antPatRotAxisSignalMapper.setMapping(qt.antPatTableWidgetsList[tabIdx]['rotAxisComboBox'], tabIdx)

    qt.antPatTableWidgetsList[tabIdx]['gainCalcMethodComboBox'].currentIndexChanged.connect(antPatGainCalcMethodSignalMapper.map)
    antPatGainCalcMethodSignalMapper.setMapping(qt.antPatTableWidgetsList[tabIdx]['gainCalcMethodComboBox'], tabIdx)


def antPatTableLEditParse(inputString):
    separatedList=[]

    inputList = inputString.split(',')
    for char in inputList:
        if char != '':
            if sp.checkInt(char) == True:
                separatedList.append(int(char))
    
    # Preserve original order while removing duplicates
    outputList = []
    for item in separatedList:
        if item not in outputList:
            outputList.append(item)
    return outputList


qt.antPatHeaderNameLEdit.setText('Antenna_Pattern_Tables')
qt.antPatHeaderNameLEdit.setEnabled(False)
qt.antPatHeaderIdentifierLEdit.setText('36')
qt.antPatHeaderIdentifierLEdit.setEnabled(False)

qt.antPatHeaderIdentifierLabel.setEnabled(False)
qt.antPatHeaderNameLabel.setEnabled(False)

qt.antPatHeaderMajVerLEdit.setText('2')

qt.antPatHeaderMinVerLEdit.setText('0')

qt.antPatHeaderYearLEdit.setText('2020')

qt.antPatHeaderMonthLEdit.setText('1')

qt.antPatHeaderDayLEdit.setText('28')

qt.antPatHeaderRfeGenLEdit.setText('28')

qt.antPatHeaderRfeModLEdit.setText('0')

qt.antPatHeaderRfeRevLEdit.setText('0')

####
qt.antPatInputConfAngleSetupRadio1.setChecked(True)
qt.antPatInputConfAngleSetupRadio2.setChecked(False)
antPat1.conf0['targetAngle'] = 1


def antPatInputSetupAngleGroupClick():
    btnId = qt.antPatInputConfAngleGroup.checkedId()
    if btnId == 0:
        antPat1.conf0['targetAngle'] = 1
    elif btnId == 1:
        antPat1.conf0['targetAngle'] = 0
    parseDataLog.debug('conf0: ' + str(antPat1.conf0))


qt.antPatInputConfSensorOrientRadio1.setChecked(True)
qt.antPatInputConfSensorOrientRadio1.setChecked(False)
antPat1.conf0['upsideDown'] = 0


def antPatInputSetupSensorOrientGroupClick():
    btnId = qt.antPatInputConfSensorOrientGroup.checkedId()
    if btnId == 0:
        antPat1.conf0['upsideDown'] = 0
    elif btnId == 1:
        antPat1.conf0['upsideDown'] = 1
    parseDataLog.debug('conf0: ' + str(antPat1.conf0))

qt.antPatInputConfChirp0CheckBox.setChecked(True)
qt.antPatInputConfChirp1CheckBox.setChecked(False)
qt.antPatInputConfChirp2CheckBox.setChecked(False)
qt.antPatInputConfChirp3CheckBox.setChecked(False)
antPat1.chirpConfig['chirp0'] = 1
antPat1.chirpConfig['chirp1'] = 0
antPat1.chirpConfig['chirp2'] = 0
antPat1.chirpConfig['chirp3'] = 0


def antPatInputConfChirpClick(btn):
    btnId = qt.antPatInputConfChirpGroup.id(btn)
    # if btnId==0:
    chBox = qt.antPatInputConfChirpGroup.button(btnId)
    state = chBox.isChecked()
    dictKey = 'chirp' + str(btnId)
    if state == 1:
        antPat1.chirpConfig[dictKey] = 1
    else:
        antPat1.chirpConfig[dictKey] = 0
    parseDataLog.debug('chirpConfig: ' + str(antPat1.chirpConfig))

#####

qt.antPatInputConfFileSearchCheckBox.setChecked(False)
qt.antPatInputNameIdentifierSelCheckBox.setChecked(False)

qt.antPatTableDiagTypeInfoCheckBox.setChecked(True)
antPat1.conf0['diagTypeInfo'] = 1
qt.antPatTableDiagTypeInfoCheckBox.setEnabled(False)

qt.antPatTableUpsideDownInfoCheckBox.setChecked(True)
antPat1.conf0['upsideDownInfo'] = 1
qt.antPatTableUpsideDownInfoCheckBox.setEnabled(False)


def antPatTableDiagTypeInfoClick():
    state = qt.antPatTableDiagTypeInfoCheckBox.isChecked()
    if state == 1:
        antPat1.conf0['diagTypeInfo'] = 1
    else:
        antPat1.conf0['diagTypeInfo'] = 0
    parseDataLog.debug('conf0: ' + str(antPat1.conf0))


def antPatTableUpsideDownInfoClick():
    state = qt.antPatTableUpsideDownInfoCheckBox.isChecked()
    if state == 1:
        antPat1.conf0['upsideDownInfo'] = 1
    else:
        antPat1.conf0['upsideDownInfo'] = 0
    parseDataLog.debug('conf0: ' + str(antPat1.conf0))


def antPatInputConfFileSearchClick():
    state = qt.antPatInputConfFileSearchCheckBox.isChecked()
    if state == 1:
        qt.antPatTableUpsideDownInfoCheckBox.setEnabled(True)
        qt.antPatTableDiagTypeInfoCheckBox.setEnabled(True)
    else:
        qt.antPatTableUpsideDownInfoCheckBox.setEnabled(False)
        qt.antPatTableDiagTypeInfoCheckBox.setEnabled(False)


def antPatInputNameIdentifierSelClick():
    state = qt.antPatInputNameIdentifierSelCheckBox.isChecked()
    if state == 1:
        qt.antPatHeaderNameLEdit.setEnabled(True)
        qt.antPatHeaderIdentifierLEdit.setEnabled(True)
        qt.antPatHeaderIdentifierLabel.setEnabled(True)
        qt.antPatHeaderNameLabel.setEnabled(True)
    else:
        qt.antPatHeaderNameLEdit.setEnabled(False)
        qt.antPatHeaderIdentifierLEdit.setEnabled(False)
        qt.antPatHeaderIdentifierLabel.setEnabled(False)
        qt.antPatHeaderNameLabel.setEnabled(False)

#### output Format Yaml or json
qt.antPatInputConfYAMLSetupRadio1.setChecked(True)
qt.antPatInputConfYAMLSetupRadio2.setChecked(False)
qt.antPatInputConfYAMLSetupRadio3.setChecked(False)


def antPatInputSetupYAMLGroupClick():
    btnId = qt.antPatInputConfYAMLGroup.checkedId()
    if btnId == 0:
        antPatControl['version'] = 0
        parseDataLog.info('json v1 has been selected')
    elif btnId == 1:
        antPatControl['version'] = 1
        parseDataLog.info('Yaml v1 has been selected')
    elif btnId == 2:
        antPatControl['version'] = 2
        parseDataLog.info('Yaml v2 has been selected')


qt.antPatInputConfFileSearchCheckBox.stateChanged.connect(antPatInputConfFileSearchClick)
qt.antPatInputNameIdentifierSelCheckBox.stateChanged.connect(antPatInputNameIdentifierSelClick)
qt.antPatTableUpsideDownInfoCheckBox.stateChanged.connect(antPatTableUpsideDownInfoClick)
qt.antPatTableDiagTypeInfoCheckBox.stateChanged.connect(antPatTableDiagTypeInfoClick)
qt.antPatInputConfChirpGroup.buttonClicked.connect(antPatInputConfChirpClick)
qt.antPatInputConfAngleGroup.buttonClicked.connect(antPatInputSetupAngleGroupClick)
qt.antPatInputConfSensorOrientGroup.buttonClicked.connect(antPatInputSetupSensorOrientGroupClick)
qt.antPatInputConfYAMLGroup.buttonClicked.connect(antPatInputSetupYAMLGroupClick)


def antpat_data_update_and_evaluation(parsedDataList, antPatLogger):

    antPat1.conf0['tables'][:]   = []
    antPat1.ptu2InputConfList[:] = []
    antPat1.setup['sensorMusterList'][:] = []

    if txAntDiag.plotSetup['useSensorMuster'] == 1:

        sensorMusterInputList = qt.parseProtSensorMusterLEdit.text()
        sensorMusterList = sensorMusterInputList.split(' ')
        for part in sensorMusterList:
            if part != '':
                antPat1.setup['sensorMusterList'].append(part)

    antPat1.portData['nofDataTables'] = 0

    qt.antPatHeaderNameLEdit.setText('Antenna_Pattern_Tables')

    for tabIdx in range(len(qt.antPatTableWidgetsList)):

        # qt.antPatTableWidgetsList[tabIdx]['nofAppTxAntIdxLEdit'].setText('1')
        if sp.checkInt(qt.antPatTableWidgetsList[tabIdx]['nofAppTxAntIdxLEdit'].text()) == True:
            antPatTableList[tabIdx]['nofApplicableTxAnt'] = int(qt.antPatTableWidgetsList[tabIdx]['nofAppTxAntIdxLEdit'].text())

        # qt.antPatTableWidgetsList[tabIdx]['nofAppRxAntIdxLEdit'].setText('4')
        if sp.checkInt(qt.antPatTableWidgetsList[tabIdx]['nofAppRxAntIdxLEdit'].text()) == True:
            antPatTableList[tabIdx]['nofApplicableRxAnt'] = int(qt.antPatTableWidgetsList[tabIdx]['nofAppRxAntIdxLEdit'].text())

        lEditString = qt.antPatTableWidgetsList[tabIdx]['appTxAntIdxLEdit'].text()
        antPatTableList[tabIdx]['applTxAntInd'] = antPatTableLEditParse(lEditString)

        lEditString = qt.antPatTableWidgetsList[tabIdx]['appRxAntIdxLEdit'].text()
        antPatTableList[tabIdx]['applRxAntInd'] = antPatTableLEditParse(lEditString)

        if qt.antPatTableWidgetsList[tabIdx]['tableCheckBox'].isChecked():
            antPat1.portData['nofDataTables'] += 1
            antPat1.conf0['tables'].append(antPatTableList[tabIdx])

    antPat1.ptu2InputConfList.append(antPat1.conf0)
    parseDataLog.debug('conf0: ' + str(antPat1.conf0))
    parseDataLog.debug('ptu2InputConfList: ' + str(antPat1.ptu2InputConfList))

    # Only antPat1 (YAML v1) is available - versions 0 and 2 removed
    antPat1.start_data_evaluation(parsedDataList, antPatLogger)

qt.antPatStartPushBtn.clicked.connect(lambda:antpat_data_update_and_evaluation(sysDiagParsedDataDict['parsedDataList'], antpatLogger ))


# setcurves - module removed, stub connections
qt.setCurvesInputConfPathLabel.setToolTip(aux.setcurvesinputconffilepath)
qt.setCurvesInputConfPathLabel.setText(aux.setcurvesinputconffilepath)
## Removed: setCurvesCustInputConfPathLabel (widget no longer exists)

def setcurves_stub():
    pass  # setcurves module removed

## Removed: setCurvesStartBtn and setCurvesPptxBtn (widgets no longer exist)


# merge the presentations
# copy combine pptx to ouput_merge
aux.createDirectory(aux.mergeOutputPath)
aux.clearAll(aux.mergeOutputPath)
mergeOutputPath = os.path.join(aux.mergeOutputPath, 'combine.pptx')
mergeInputPath = os.path.join(aux.mergeOutputPath, 'combine.pptx')
status, errorSting = aux.copyFile(mergeInputPath, mergeOutputPath)

def merge_stub():
    pass  # setcurves/stats modules removed

qt.parseProtMergePPTXBtn.clicked.connect(lambda: merge_stub())
qt.parseProtMergePPTXBtn.clicked.connect(lambda: merge_stub())
qt.parseProtMergePPTXBtn.clicked.connect(lambda:txantdiag_data_update_and_evaluation(txAntDiagParsedDataDict['parsedDataList'], txAntDiagLogger, aux.mergeOutputPath, 'combine2.pptx', aux.mergeOutputPath+ './combine1.pptx' ))
qt.parseProtMergePPTXBtn.clicked.connect(lambda:data_update_and_evaluation(sysDiagParsedDataDict['parsedDataList'], antSysDiag.twoGraphSetupList, antSysDiag.fourGraphSetupList, antSysDiag.threeGraphSetupList, antSysDiag.allOnOneSlideGraphList, antSysDiag.diagramConfigList, sysDiagLogger, aux.mergeOutputPath, 'merged_presentation.pptx', str(aux.mergeOutputPath) +'./combine2.pptx') )

#####  ####  ###  ##  #

def run() -> None:
    """Entry point for installed package."""
    sys.exit(qt.app.exec())

if __name__ == "__main__":
    run()
