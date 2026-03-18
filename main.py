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
from shared.parser_factory import ParserFactory
from shared.parse_controller import ParseController
from shared.plot_controller import PlotController
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

from ui.main_view import MainView as _MainView
view = _MainView()
qt = view  # backward-compatible alias: all qt.<widget> calls delegate to MainView
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


# Instantiate the ParseController — owns all parsing state and business logic
pc = ParseController()

# Instantiate the PlotController — owns all plot configuration state
plc = PlotController()

# Bind antSysDiag state dicts to plc's shared dict objects so that
# plc.set_*() mutations and antSysDiag reads/writes operate on the same data.
antSysDiag.plotSetup      = plc.plotSetup
antSysDiag.graphConfig    = plc.graphConfig
antSysDiag.chirpConfig    = plc.chirpConfig
antSysDiag.diagramConfig  = plc.diagramConfig
antSysDiag.twoGraphConf1   = plc.twoGraphConf1
antSysDiag.twoGraphConf2   = plc.twoGraphConf2
antSysDiag.threeGraphConf1 = plc.threeGraphConf1
antSysDiag.threeGraphConf2 = plc.threeGraphConf2
antSysDiag.threeGraphConf3 = plc.threeGraphConf3
antSysDiag.fourGraphConf1  = plc.fourGraphConf1
antSysDiag.fourGraphConf2  = plc.fourGraphConf2
antSysDiag.fourGraphConf3  = plc.fourGraphConf3
antSysDiag.AllGraphsConf1  = plc.AllGraphsConf1
antSysDiag.AllGraphsConf2  = plc.AllGraphsConf2
antSysDiag.AllGraphsConf3  = plc.AllGraphsConf3
antSysDiag.plotWindowConfig = plc.plotWindowConfig

# ParseController owns all parsing state — access via pc.*

##########

qt.parseProtSensorMusterCheckBox.setChecked(False)
view.set_sensor_muster_enabled(False)

antSysDiag.plotSetup['useSensorMuster'] = 0
antPat1.setup['useSensorMuster'] = 0
txAntDiag.plotSetup['useSensorMuster'] = 0


def parseProtSensorMusterClick():
    state = qt.parseProtSensorMusterCheckBox.isChecked()
    view.set_sensor_muster_enabled(state == 1)
    plc.set_sensor_muster_enabled(state == 1)
    antPat1.setup['useSensorMuster'] = 1 if state == 1 else 0
    txAntDiag.plotSetup['useSensorMuster'] = 1 if state == 1 else 0
    parseDataLog.debug('plotSetp: ' + str(plc.plotSetup))


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


view.set_burn_in_limits_file(aux.burnInLimitsFilePath)
view.set_cal_limits_file(aux.calLimitsFilePath)
view.set_burn_in_lim_groups_file(aux.burnInLimGroupsFilePath)
view.set_cal_lim_groups_file(aux.calLimGroupsFilePath)
view.set_stats_input_conf_path(aux.statsinputconffilepath)

qt.parseProtProtDataInFileBurnInPushBtn.clicked.connect(lambda: loadBurnInInputLimitsFile())
qt.parseProtProtDataInFileCalPushBtn.clicked.connect(lambda : loadCalInputLimitsFile())
qt.parseProtProtDataLimGroupsBurnInPushBtn.clicked.connect(lambda: loadBurnInLimitsGroupsFile())
qt.parseProtProtDataLimGroupsCalPushBtn.clicked.connect(lambda : loadCalLimitsGroupsFile())


def importProtocolsDirPath():
    protocolDirPath = ''
    if qt.parseProtImportProtDirPathFDialog.exec_():
        protocolDirPath = qt.parseProtImportProtDirPathFDialog.selectedFiles()[0]
    protocolFilesList = protocolFilter.ProtocolInfoClass.GetAllProtocolsList(protocolDirPath)

    for protFileIdx in range(len(protocolFilesList)):

        protocolFilesList[protFileIdx]=protocolFilesList[protFileIdx].replace('\\', '/')


    fillInProtocolData(protocolFilesList)


def importProtocolsFileList():

    protocolFilesList = []
    if qt.parseProtImportProtFListFDialog.exec_():
        protocolFilesList = qt.parseProtImportProtFListFDialog.selectedFiles()

    fillInProtocolData(protocolFilesList)


def getProtPathTypeDictList(protocolPathList):
    """Thin Qt-aware wrapper: reads UI state via view and delegates to ParseController."""
    return pc.build_prot_path_type_list(
        protocolPathList,
        burn_in_cal_mode=view.get_burn_in_cal_mode(),
        include_burn_in_start=view.get_include_burn_in_start(),
    )


def _update_protocol_dicts(
    accepted_crit_prot_list: list,
    sys_diag_file_path_dict_temp: list,
    tx_diag_file_path_dict_temp: list,
    filtered_protocol_list: list,
    acc_error_prot_list: list,
    acc_abort_crit_prot_list: list,
    acc_limit_exceeded_prot_list: list,
) -> list:
    """Merge getprotcols results into the shared state dicts via ParseController.

    Updates accepted/filtered/parsed dicts and returns the list of protocol
    path-type dicts that still need to be parsed.
    """
    pc.acceptedProtocolPathDict['errorProtList']         += acc_error_prot_list
    pc.acceptedProtocolPathDict['abbortCritProtList']    += acc_abort_crit_prot_list
    pc.acceptedProtocolPathDict['limitExceededProtList'] += acc_limit_exceeded_prot_list

    accepted_prot_path_type_dict_list = getProtPathTypeDictList(accepted_crit_prot_list)

    pc.protocolPathDict['protocolPathTypeDictList'] += accepted_prot_path_type_dict_list

    accepted_path_set = {d['protocolPath'] for d in pc.protocolPathDict['protocolPathTypeDictList']}
    update_filtered_protocol_list(filtered_protocol_list, pc.filteredProtocolPathDict, accepted_path_set)

    parseDataLog.info('Filtered Protocol List:')
    for elem in pc.filteredProtocolPathDict['protocolPathList']:
        parseDataLog.info(elem)

    already_parsed = collect_unparsed_protocols(
        accepted_prot_path_type_dict_list, pc.parsedProtDict, pc.protToBeParsedDict
    )
    for path in already_parsed:
        parseDataLog.info('Protocol is already parsed: ' + path)

    parseDataLog.info('Num. of Total Accepted Protocols: ' + str(len(pc.protocolPathDict['protocolPathTypeDictList'])))
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


def fillInProtocolData(protocolFilesList: list) -> None:
    """Load and validate new protocol files; update all state dicts and the UI table."""
    qt.parseProtTableTabWidget.setCurrentIndex(0)

    if not protocolFilesList:
        return

    view.set_progress_label('Loading...')
    view.reset_progress_bar()

    if not pc.protocolPathDict['protocolPathTypeDictList']:
        qt.parseProtSelProtTable.setRowCount(0)

    protNonRepList = deduplicate_protocol_list(
        protocolFilesList, pc.protocolPathDict['protocolPathTypeDictList']
    )
    for p in set(protocolFilesList) - set(protNonRepList):
        parseDataLog.info('Protocol is already imported: ' + p)

    sysDiagFilePathDictTemp, txDiagfilePathDictTemp, acceptedCritProtList, accErrorProtList, accAbbortCritProtList, accLimitExceededProtList, filteredProtocolList = getprotcols(
        protNonRepList, qt.parseProtSysDiagCheckBox.isChecked(), qt.parseProtTxAntDiagCheckBox.isChecked()
    )

    if sysDiagFilePathDictTemp:
        pc.sysDiagFilePathDict['filePathList'] += sysDiagFilePathDictTemp
    if txDiagfilePathDictTemp:
        pc.txDiagfilePathDict['filePathList'] += txDiagfilePathDictTemp

    acceptedProtPathTypeDictList = _update_protocol_dicts(
        acceptedCritProtList,
        sysDiagFilePathDictTemp, txDiagfilePathDictTemp,
        filteredProtocolList,
        accErrorProtList, accAbbortCritProtList, accLimitExceededProtList,
    )

    _populate_sel_prot_table(acceptedProtPathTypeDictList, sysDiagFilePathDictTemp, txDiagfilePathDictTemp)

    if pc.protToBeParsedDict['protocolPathTypeDictList']:
        view.set_progress_bar_range(len(pc.protToBeParsedDict['protocolPathTypeDictList']))
        view.set_progress_bar(0)
        view.set_progress_bar_format(
            f'{view.get_progress_bar_value()} / {len(pc.protToBeParsedDict["protocolPathTypeDictList"])}'
        )
        progBarLabelStr = (
            f'Protocols to be parsed: {len(pc.protToBeParsedDict["protocolPathTypeDictList"])}'
            f' / {len(pc.protocolPathDict["protocolPathTypeDictList"])}. '
        )
        view.set_progress_label(progBarLabelStr)
    else:
        view.set_progress_label('No new protocols Loaded.')

    total = len(pc.protocolPathDict['protocolPathTypeDictList'])
    view.set_loaded_prot_ratio_label(total, len(pc.filteredProtocolPathDict['protocolPathList']))
    view.set_eol_error_label(len(pc.acceptedProtocolPathDict['errorProtList']), total)
    view.set_abort_crit_label(len(pc.acceptedProtocolPathDict['abbortCritProtList']), total)
    view.set_meas_limits_label(len(pc.acceptedProtocolPathDict['limitExceededProtList']), total)
    view.set_parsed_loaded_label(len(pc.parsedProtDict['protocolPathTypeDictList']), total)


def addAndParsePtu2Files():
    qt.parseProtTableTabWidget.setCurrentIndex(2)

    ptu2FilesList = []
    if qt.parseProtAddAndParsePtu2FDialog.exec_():
        ptu2FilesList = qt.parseProtAddAndParsePtu2FDialog.selectedFiles()
        ptu2FilesList.sort()

    # Business logic delegated to controller
    parsed, failed = pc.parse_ptu2_files(
        ptu2FilesList,
        antSysDiag.plotSetup['useSensorMuster'],
        antSysDiag.plotSetup['sensorMusterList'],
    )
    pc.add_ptu2_to_state(parsed, failed)

    # Qt widget updates
    clearTable(qt.parseProtAddPtu2ParsedTable)
    for idx, item in enumerate(pc.separatePtu2ParsedDataDict['parsedDataList']):
        qt.parseProtAddPtu2ParsedTable.insertRow(idx)
        qt.parseProtAddPtu2ParsedTable.setItem(idx, 0, QTableWidgetItem(item.fileTitle.fileNamePath))
    view.set_sep_par_ptu2_files_label(pc.ptu2_parsed_count())

    clearTable(qt.parseProtAddPtu2FailedTable)
    for idx, item in enumerate(pc.separatePtu2FailedDataDict['parsedDataList']):
        qt.parseProtAddPtu2FailedTable.insertRow(idx)
        qt.parseProtAddPtu2FailedTable.setItem(idx, 0, QTableWidgetItem(item.fileTitle.fileNamePath))


def addAndParseTxAntDiagFiles():
    qt.parseProtTableTabWidget.setCurrentIndex(3)

    txAntDiagFilesList = []
    if qt.parseProtAddAndParseTxAntDiagFDialog.exec_():
        txAntDiagFilesList = qt.parseProtAddAndParseTxAntDiagFDialog.selectedFiles()

    # Business logic delegated to controller
    parsed, failed = pc.parse_tx_ant_diag_files(
        txAntDiagFilesList,
        antSysDiag.plotSetup['useSensorMuster'],
        antSysDiag.plotSetup['sensorMusterList'],
    )
    pc.add_tx_ant_diag_to_state(parsed, failed)

    # Qt widget updates
    clearTable(qt.parseProtAddTxAntDiagParsedTable)
    for idx, item in enumerate(pc.separateTxAntDiagParsedDataDict['parsedDataList']):
        qt.parseProtAddTxAntDiagParsedTable.insertRow(idx)
        qt.parseProtAddTxAntDiagParsedTable.setItem(idx, 0, QTableWidgetItem(item.fileTitle.fileNamePath))
    view.set_sep_par_tx_ant_diag_files_label(pc.tx_ant_diag_parsed_count())

    clearTable(qt.parseProtAddTxAntDiagFailedTable)
    for idx, item in enumerate(pc.separateTxAntDiagFailedDataDict['parsedDataList']):
        qt.parseProtAddTxAntDiagFailedTable.insertRow(idx)
        qt.parseProtAddTxAntDiagFailedTable.setItem(idx, 0, QTableWidgetItem(item.fileTitle.fileNamePath))



def loadCalInputLimitsFile():

    filePath = ''

    if qt.parseProtProtDataInFileCalFDialog.exec_():
        filePath = qt.parseProtProtDataInFileCalFDialog.selectedFiles()[0]

        filePath = filePath.replace('\\', '/')

    else:
        filePath=aux.calLimitsFilePath
    view.set_cal_limits_file(filePath)


def loadBurnInInputLimitsFile():

    filePath = ''

    if qt.parseProtProtDataInFileBurnInFDialog.exec_():
        filePath = qt.parseProtProtDataInFileBurnInFDialog.selectedFiles()[0]

        filePath = filePath.replace('\\', '/')
    else:
        filePath = aux.burnInLimitsFilePath
    view.set_burn_in_limits_file(filePath)


def loadBurnInLimitsGroupsFile():

    filePath = ''

    if qt.parseProtProtDataLimGroupsBurnInFDialog.exec_():
        filePath = qt.parseProtProtDataLimGroupsBurnInFDialog.selectedFiles()[0]

        filePath = filePath.replace('\\', '/')
    else:
        filePath = aux.burnInLimGroupsFilePath
    view.set_burn_in_lim_groups_file(filePath)


def loadCalLimitsGroupsFile():

    filePath = ''

    if qt.parseProtProtDataLimGroupsCalFDialog.exec_():
        filePath = qt.parseProtProtDataLimGroupsCalFDialog.selectedFiles()[0]

        filePath = filePath.replace('\\', '/')
    else:
        filePath = aux.calLimGroupsFilePath
    view.set_cal_lim_groups_file(filePath)


def setup_progress_bar(protToBeParsedDict: dict, protocolPathDict: dict) -> tuple[str, int]:
    """Setup the progress bar for protocol parsing."""
    view.reset_progress_bar()
    protToBeParsedListLen = len(protToBeParsedDict['protocolPathTypeDictList'])
    progBarLabelStr = ''
    if len(protToBeParsedDict['protocolPathTypeDictList']) != 0:
        view.set_progress_bar_range(len(protToBeParsedDict['protocolPathTypeDictList']))
        progBarLabelStr = f'Protocols to be parsed: {len(protToBeParsedDict["protocolPathTypeDictList"])} / {len(protocolPathDict["protocolPathTypeDictList"])}. '
        view.set_progress_label(progBarLabelStr)
        view.set_progress_bar(0)
        view.set_progress_bar_format(f'{view.get_progress_bar_value()} / {protToBeParsedListLen}')
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
            view.set_progress_bar_format(f'{final} / {protToBeParsedListLen}')
        else:
            view.set_progress_bar_format(f'{idx} / {protToBeParsedListLen}')

        if twentyPercent != 0:
            if idx % twentyPercent == 0:
                _, tail = os.path.split(
                    protToBeParsedDict['protocolPathTypeDictList'][protFileIdx]['protocolPath']
                )
                view.set_progress_label(progBarLabelStr + 'Protocol: ' + tail)
                if int(idx / twentyPercent) < 5:
                    view.set_progress_bar(idx)
                else:
                    setFinal = True
                    final    = idx + twentyPercRes
                    view.set_progress_bar(final)
        else:
            _, tail = os.path.split(
                protToBeParsedDict['protocolPathTypeDictList'][protFileIdx]['protocolPath']
            )
            view.set_progress_label(progBarLabelStr + 'Protocol: ' + tail)
            view.set_progress_bar(idx)

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


def parseData() -> None:
    """Orchestrate protocol parsing: filter → load → merge → update UI."""
    qt.parseProtTableTabWidget.setCurrentIndex(1)

    if not pc.protToBeParsedDict['protocolPathTypeDictList']:
        view.set_progress_label('No protocols to be parsed.')
        return

    if not pc.parsedProtDict['protocolPathTypeDictList']:
        qt.parseProtAccProtTable.setRowCount(0)

    filteredSysDiagList, filteredTxAntDiagList = filter_protocol_file_lists(
        pc.protToBeParsedDict, pc.sysDiagFilePathDict, pc.txDiagfilePathDict, pc.parsedProtDict
    )

    progBarLabelStr, protToBeParsedListLen = setup_progress_bar(pc.protToBeParsedDict, pc.protocolPathDict)

    sysDiagDataList, txAntDiagDataList, sysDiagParsedDataList, txAntDiagParsedDataList = _load_protocol_data(
        filteredSysDiagList, filteredTxAntDiagList,
        pc.protToBeParsedDict, progBarLabelStr, protToBeParsedListLen,
    )

    merge_into_parsed_dicts(
        sysDiagParsedDataList, txAntDiagParsedDataList,
        pc.sysDiagParsedDataDict, pc.txAntDiagParsedDataDict,
    )

    view.set_parsed_loaded_label(
        len(pc.parsedProtDict['protocolPathTypeDictList']),
        len(pc.protocolPathDict['protocolPathTypeDictList']),
    )
    view.set_ptu2_files_label(len(pc.sysDiagParsedDataDict['parsedDataList']))
    view.set_tx_ant_diag_files_label(len(pc.txAntDiagParsedDataDict['parsedDataList']))

    _populate_accepted_protocols_table(pc.protToBeParsedDict, sysDiagDataList, txAntDiagDataList)

    view.set_progress_label(
        f'Parsing finished. Protocols parsed: {len(pc.protToBeParsedDict["protocolPathTypeDictList"])}.'
    )
    pc.protToBeParsedDict['protocolPathTypeDictList'][:] = []


def importDbProtocolsList():
    # cert module removed - function disabled
    parseDataLog.warning('Database protocol import not available - CT_DataCollector module removed')
    pass


def importBurnInProtocolsList():
    # cert module removed - using simplified version without cert.importData
    fillInCertProtocolData([], 'BurnIn')


def importCalProtocolsList():
    # cert module removed - using simplified version without cert.importData
    fillInCertProtocolData([], 'Calibration')


def fillInCertProtocolData(protocolFilesList: list, protType: str) -> None:
    # cert module removed - no-op until cert support is restored
    qt.mainTabWidget.setCurrentIndex(0)
    qt.parseProtTableTabWidget.setCurrentIndex(4)


def clearData():
    # Business logic delegated to controller
    pc.clear_state()

    view.set_parsed_loaded_label(0)
    view.set_ptu2_files_label(0)
    view.set_tx_ant_diag_files_label(0)
    view.set_loaded_protocols_label(0)
    view.set_eol_error_label(0)
    view.set_abort_crit_label(0)
    view.set_meas_limits_label(0)
    view.set_sep_par_ptu2_files_label(0)
    view.set_sep_par_tx_ant_diag_files_label(0)

    # qt.parseProtProgresBar.setRange(0, len(protocolPathDict['protocolPathList']))
    # qt.parseProtProgresBar.setValue(0)
    view.reset_progress_bar()
    view.set_progress_bar_format('')
    view.set_progress_label('No protocols loaded.')

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



qt.parseProtImportProtFListPushBtn.clicked.connect(importProtocolsFileList)
qt.parseProtImportProtDirPathPushBtn.clicked.connect(importProtocolsDirPath)
qt.parseProtClearDataPushBtn.clicked.connect(clearData)
qt.parseProtParseDataPushBtn.clicked.connect(parseData)
qt.parseProtAddAndParsePtu2PushBtn.clicked.connect(addAndParsePtu2Files)
qt.parseProtAddAndParseTxAntDiagPushBtn.clicked.connect(addAndParseTxAntDiagFiles)


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
    plc.set_target_angle(btnId)
    parseDataLog.debug('plotSetup: ' + str(plc.plotSetup))


qt.sysDiagInputSetupSensorOrientRadio1.setChecked(True)
qt.sysDiagInputSetupSensorOrientRadio2.setChecked(False)
antSysDiag.plotSetup['upsideDown'] = 0


def sysDiagInputSetupSensorOrientGroupClick():
    btnId = qt.sysDiagInputSetupSensorOrientGroup.checkedId()
    plc.set_upside_down(btnId)
    parseDataLog.debug('plotSetup: ' + str(plc.plotSetup))


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
    chBox = qt.sysDiagInputSetupChirpGroup.button(btnId)
    state = chBox.isChecked()
    dictKey = 'chirp' + str(btnId)
    plc.set_chirp_key(dictKey, state)
    parseDataLog.debug('chirpConfig: ' + str(plc.chirpConfig))


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
    plc.set_diagram_select_mode(btnId)
    parseDataLog.debug('diagramConfig: ' + str(plc.diagramConfig))

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
    plc.set_diagram_odd_even(btnId)
    parseDataLog.debug('diagramConfig: ' + str(plc.diagramConfig))


qt.sysDiagPlotSetupImgGenRadio1.setChecked(True)
qt.sysDiagPlotSetupImgGenRadio2.setChecked(False)
antSysDiag.plotSetup['SeparateRxCh'] = 1


def sysDiagPlotSetupImgGenClick():
    btnId = qt.sysDiagPlotSetupImgGenGroup.checkedId()
    plc.set_img_gen_mode(btnId)
    if btnId == 0:
        qt.sysDiagSlideConfTwoGraphCheckBox1.setChecked(False)
        qt.sysDiagSlideConfTwoGraphCheckBox2.setChecked(False)
        qt.sysDiagSlideConfFourGraphFrame.setEnabled(True)

        qt.sysDiagPlotSetup3GraphLayoutImgCheckBox.setChecked(True)
        qt.sysDiagPlotSetup3GraphLayoutImgCheckBox.setEnabled(True)

        qt.sysDiagSlideConfThreeGraphFrame.setEnabled(True)

        qt.sysDiagSlideConfThreeGraphCheckBox1.setChecked(True)
        qt.sysDiagSlideConfThreeGraphCheckBox2.setChecked(True)
        qt.sysDiagSlideConfThreeGraphCheckBox3.setChecked(False)

        qt.sysDiagSlideConfFourGraphCheckBox1.setChecked(True)
        qt.sysDiagSlideConfFourGraphCheckBox2.setChecked(False)
        qt.sysDiagSlideConfFourGraphCheckBox3.setChecked(False)

        parseDataLog.debug('plotSetup: ' + str(plc.plotSetup))
    elif btnId == 1:
        qt.sysDiagSlideConfTwoGraphCheckBox1.setChecked(True)
        qt.sysDiagSlideConfTwoGraphCheckBox2.setChecked(True)
        qt.sysDiagSlideConfFourGraphFrame.setEnabled(False)

        qt.sysDiagPlotSetup3GraphLayoutImgCheckBox.setChecked(False)
        qt.sysDiagPlotSetup3GraphLayoutImgCheckBox.setEnabled(False)

        qt.sysDiagSlideConfThreeGraphFrame.setEnabled(False)

        qt.sysDiagSlideConfThreeGraphCheckBox1.setChecked(False)
        qt.sysDiagSlideConfThreeGraphCheckBox2.setChecked(False)
        qt.sysDiagSlideConfThreeGraphCheckBox3.setChecked(False)

        qt.sysDiagSlideConfFourGraphCheckBox1.setChecked(False)
        qt.sysDiagSlideConfFourGraphCheckBox2.setChecked(False)
        qt.sysDiagSlideConfFourGraphCheckBox3.setChecked(False)

        parseDataLog.debug('plotSetup: ' + str(plc.plotSetup))


qt.sysDiagPlotSetup3GraphLayoutImgCheckBox.setChecked(True)
antSysDiag.plotSetup['threeGraphLayout'] = 1


def sysDiagPlotSetup3GraphLayoutImgClick():
    state = qt.sysDiagPlotSetup3GraphLayoutImgCheckBox.isChecked()
    plc.set_three_graph_layout(state)
    if state == 1:
        qt.sysDiagSlideConfThreeGraphFrame.setEnabled(True)

        qt.sysDiagSlideConfThreeGraphCheckBox1.setChecked(True)
        qt.sysDiagSlideConfThreeGraphCheckBox2.setChecked(True)
        qt.sysDiagSlideConfThreeGraphCheckBox3.setChecked(False)

        qt.sysDiagSlideConfTwoGraphCheckBox2.setChecked(False)
    else:
        qt.sysDiagSlideConfThreeGraphFrame.setEnabled(False)

        qt.sysDiagSlideConfThreeGraphCheckBox1.setChecked(False)
        qt.sysDiagSlideConfThreeGraphCheckBox2.setChecked(False)
        qt.sysDiagSlideConfThreeGraphCheckBox3.setChecked(False)

        qt.sysDiagSlideConfTwoGraphCheckBox2.setChecked(True)
    parseDataLog.debug('plotSetup: ' + str(plc.plotSetup))


qt.sysDiagPlotSetupImageDpiLEdit.setText('220')
if sp.checkInt(qt.sysDiagPlotSetupImageDpiLEdit.text()) == True:
    antSysDiag.plotSetup['imageDpi'] = int(qt.sysDiagPlotSetupImageDpiLEdit.text())

qt.sysDiagPlotSetupScalingAutoCheckBox.setChecked(False)
antSysDiag.plotSetup['xScaleSizeAuto'] = 0
def sysDiagPlotSetupScalingAutoClick():
    state = qt.sysDiagPlotSetupScalingAutoCheckBox.isChecked()
    plc.set_x_scale_auto(state)
    parseDataLog.debug('plotSetup: ' + str(plc.plotSetup))

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
    plc.set_y_limits_mode(btnId)
    parseDataLog.debug('plotSetup: ' + str(plc.plotSetup))

qt.sysDiagPlotSetupScalingDiffPhDiffLEdit.setText('1.5')

if sp.checkDecimal(qt.sysDiagPlotSetupScalingDiffPhDiffLEdit.text()) == True:
    antSysDiag.plotSetup['diffPhaseDiffScalingFactor']=float(qt.sysDiagPlotSetupScalingDiffPhDiffLEdit.text())


qt.sysDiagPlotSetupGraphConfIdealCurveCheckBox.setChecked(True)
antSysDiag.plotSetup['idealPhaseDiff'] = 1


def sysDiagPlotSetupGraphConfIdealCurveClick():
    state = qt.sysDiagPlotSetupGraphConfIdealCurveCheckBox.isChecked()
    plc.set_ideal_phase_diff(state)
    parseDataLog.debug('plotSetup: ' + str(plc.plotSetup))

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
    plc.set_graph_conf_key(setKey, state)

    sysDiagSlideConfComboAddItems(qt.sysDiagSlideConfTwoGraphComboBox11, plc.graphConfig)
    sysDiagSlideConfComboAddItems(qt.sysDiagSlideConfTwoGraphComboBox12, plc.graphConfig)
    sysDiagSlideConfComboAddItems(qt.sysDiagSlideConfTwoGraphComboBox21, plc.graphConfig)
    sysDiagSlideConfComboAddItems(qt.sysDiagSlideConfTwoGraphComboBox22, plc.graphConfig)

    sysDiagSlideConfComboAddItems(qt.sysDiagSlideConfFourGraphComboBox1, plc.graphConfig)
    sysDiagSlideConfComboAddItems(qt.sysDiagSlideConfFourGraphComboBox2, plc.graphConfig)
    sysDiagSlideConfComboAddItems(qt.sysDiagSlideConfFourGraphComboBox3, plc.graphConfig)

    sysDiagSlideConfThreeGraphComboAddItems(qt.sysDiagSlideConfThreeGraphComboBox1, plc.graphConfig)
    sysDiagSlideConfThreeGraphComboAddItems(qt.sysDiagSlideConfThreeGraphComboBox2, plc.graphConfig)
    sysDiagSlideConfThreeGraphComboAddItems(qt.sysDiagSlideConfThreeGraphComboBox3, plc.graphConfig)
    parseDataLog.debug('graphConfig: ' + str(plc.graphConfig))


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
    plc.set_two_graph_conf1_prim(qt.sysDiagSlideConfTwoGraphComboBox11.itemText(idx))
    parseDataLog.debug('twoGraphConf1: ' + str(plc.twoGraphConf1))


def sysDiagSlideConfTwoGraphComboBox12Click(idx):
    plc.set_two_graph_conf1_sec(qt.sysDiagSlideConfTwoGraphComboBox12.itemText(idx))
    parseDataLog.debug('twoGraphConf1: ' + str(plc.twoGraphConf1))


def sysDiagSlideConfTwoGraphComboBox21Click(idx):
    plc.set_two_graph_conf2_prim(qt.sysDiagSlideConfTwoGraphComboBox21.itemText(idx))
    parseDataLog.debug('twoGraphConf2: ' + str(plc.twoGraphConf2))


def sysDiagSlideConfTwoGraphComboBox22Click(idx):
    plc.set_two_graph_conf2_sec(qt.sysDiagSlideConfTwoGraphComboBox22.itemText(idx))
    parseDataLog.debug('twoGraphConf2: ' + str(plc.twoGraphConf2))

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
    plc.set_four_graph_conf1(qt.sysDiagSlideConfFourGraphComboBox1.itemText(idx))
    parseDataLog.debug('fourGraphConf1: ' + str(plc.fourGraphConf1))


def sysDiagSlideConfFourGraphComboBox2Click(idx):
    plc.set_four_graph_conf2(qt.sysDiagSlideConfFourGraphComboBox2.itemText(idx))
    parseDataLog.debug('fourGraphConf2: ' + str(plc.fourGraphConf2))


def sysDiagSlideConfFourGraphComboBox3Click(idx):
    plc.set_four_graph_conf3(qt.sysDiagSlideConfFourGraphComboBox3.itemText(idx))
    parseDataLog.debug('fourGraphConf3: ' + str(plc.fourGraphConf3))


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
    plc.set_three_graph_conf1(qt.sysDiagSlideConfThreeGraphComboBox1.itemText(idx))
    parseDataLog.debug('threeGraphConf1: ' + str(plc.threeGraphConf1))


def sysDiagSlideConfThreeGraphComboBox2Click(idx):
    plc.set_three_graph_conf2(qt.sysDiagSlideConfThreeGraphComboBox2.itemText(idx))
    parseDataLog.debug('threeGraphConf2: ' + str(plc.threeGraphConf2))


def sysDiagSlideConfThreeGraphComboBox3Click(idx):
    plc.set_three_graph_conf3(qt.sysDiagSlideConfThreeGraphComboBox3.itemText(idx))
    parseDataLog.debug('threeGraphConf3: ' + str(plc.threeGraphConf3))

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
    plc.set_all_on_one_slide(state)
    if state == True:
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
        qt.sysDiagSlideConfGeneralAllSlidesCheckBox1.setChecked(False)
        qt.sysDiagSlideConfGeneralAllSlidesCheckBox1.setEnabled(False)
        qt.sysDiagSlideConfGeneralAllSlidesCheckBox2.setChecked(False)
        qt.sysDiagSlideConfGeneralAllSlidesCheckBox2.setEnabled(False)
        qt.sysDiagSlideConfGeneralAllSlidesCheckBox3.setChecked(False)
        qt.sysDiagSlideConfGeneralAllSlidesCheckBox3.setEnabled(False)

        qt.sysDiagSlideConfGeneralAllSlidesComboBox1.setEnabled(False)
        qt.sysDiagSlideConfGeneralAllSlidesComboBox2.setEnabled(False)
        qt.sysDiagSlideConfGeneralAllSlidesComboBox3.setEnabled(False)

    parseDataLog.debug('plotSetup: ' + str(plc.plotSetup))


qt.sysDiagSlideConfGeneralAllSlidesComboBox1.setCurrentIndex(0)
qt.sysDiagSlideConfGeneralAllSlidesComboBox2.setCurrentIndex(8)
qt.sysDiagSlideConfGeneralAllSlidesComboBox3.setCurrentIndex(6)

antSysDiag.AllGraphsConf1['graphType'] = 'level'
antSysDiag.AllGraphsConf2['graphType'] = 'corrPhaseDiff'
antSysDiag.AllGraphsConf3['graphType'] = 'diffPhaseDiff'


def sysDiagSlideConfGeneralAllSlidesComboBox1Click(idx):
    plc.set_all_graphs_conf1(qt.sysDiagSlideConfGeneralAllSlidesComboBox1.itemText(idx))
    parseDataLog.debug('AllGraphsConf1: ' + str(plc.AllGraphsConf1))


def sysDiagSlideConfGeneralAllSlidesComboBox2Click(idx):
    plc.set_all_graphs_conf2(qt.sysDiagSlideConfGeneralAllSlidesComboBox2.itemText(idx))
    parseDataLog.debug('AllGraphsConf2: ' + str(plc.AllGraphsConf2))


def sysDiagSlideConfGeneralAllSlidesComboBox3Click(idx):
    plc.set_all_graphs_conf3(qt.sysDiagSlideConfGeneralAllSlidesComboBox3.itemText(idx))
    parseDataLog.debug('AllGraphsConf3: ' + str(plc.AllGraphsConf3))

qt.sysDiagPlotSetupScriptModeRadio1.setChecked(True)
qt.sysDiagPlotSetupScriptModeRadio2.setChecked(False)
antSysDiag.plotSetup['ShowCertainPlotWindow'] = 0
qt.sysDiagPlotWindowGroupBox.setEnabled(False)
qt.sysDiagSlideConfGroupBox.setEnabled(True)


def sysDiagPlotSetupScriptModeGroupClick():
    btnId = qt.sysDiagPlotSetupScriptModeGroup.checkedId()
    plc.set_script_mode(btnId)
    if btnId == 0:
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

        parseDataLog.debug('plotSetup: ' + str(plc.plotSetup))
    elif btnId == 1:
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

        parseDataLog.debug('plotSetup: ' + str(plc.plotSetup))

#####
qt.sysDiagPlotWindowInputModeRadio1.setChecked(True)
qt.sysDiagPlotWindowInputModeRadio2.setChecked(False)
antSysDiag.plotWindowConfig['inputMode'] = 1
qt.sysDiagPlotWindowInputModeLEdit.setEnabled(False)


def sysDiagPlotWindowInputModeClick():
    btnId = qt.sysDiagPlotWindowInputModeGroup.checkedId()
    plc.set_plot_window_input_mode(btnId)
    qt.sysDiagPlotWindowInputModeLEdit.setEnabled(btnId == 1)
    parseDataLog.debug('plotWindowConfig: ' + str(plc.plotWindowConfig))


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
    plc.set_plot_window_graph(qt.sysDiagPlotWindowGraphTypeComboBox.itemText(idx))
    parseDataLog.debug('plotWindowConfig: ' + str(plc.plotWindowConfig))

antSysDiag.plotWindowConfig['graph'] = 'level'

qt.sysDiagPlotWindowAllGraphsCheckBox.setChecked(False)

qt.sysDiagPlotWindowAllGraphsCheckBox1.setChecked(False)
qt.sysDiagPlotWindowAllGraphsCheckBox2.setChecked(False)
qt.sysDiagPlotWindowAllGraphsCheckBox3.setChecked(False)
qt.sysDiagPlotWindowAllGraphsComboBox1.setCurrentIndex(0)
qt.sysDiagPlotWindowAllGraphsComboBox2.setCurrentIndex(8)
qt.sysDiagPlotWindowAllGraphsComboBox3.setCurrentIndex(6)


def sysDiagPlotWindowAllGraphsComboBox1Click(idx):
    plc.set_all_graphs_conf1(qt.sysDiagPlotWindowAllGraphsComboBox1.itemText(idx))
    parseDataLog.debug('AllGraphsConf1: ' + str(plc.AllGraphsConf1))


def sysDiagPlotWindowAllGraphsComboBox2Click(idx):
    plc.set_all_graphs_conf2(qt.sysDiagPlotWindowAllGraphsComboBox2.itemText(idx))
    parseDataLog.debug('AllGraphsConf2: ' + str(plc.AllGraphsConf2))


def sysDiagPlotWindowAllGraphsComboBox3Click(idx):
    plc.set_all_graphs_conf3(qt.sysDiagPlotWindowAllGraphsComboBox3.itemText(idx))
    parseDataLog.debug('AllGraphsConf3: ' + str(plc.AllGraphsConf3))


def sysDiagPlotWindowAllGraphsClick():
    state = qt.sysDiagPlotWindowAllGraphsCheckBox.isChecked()
    plc.set_plot_window_all_graphs_mode(state)
    if state == 1:
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
