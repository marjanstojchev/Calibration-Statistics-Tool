"""Parse-tab signal handlers  (PST-55).

All handler functions that were previously defined at module level in main.py
under the "Parse protocols / PTU2 / TxAntDiag" section.

``wire(ctx, extra)`` connects every Qt signal to its handler.
"""
from __future__ import annotations

import os
from typing import TYPE_CHECKING

from calibration_statistics_tool.shared import auxiliary as aux
from calibration_statistics_tool.shared import data_processing as dp
from calibration_statistics_tool.shared import protocolsTest as protocolFilter
from PySide6.QtWidgets import QTableWidgetItem
from calibration_statistics_tool.shared.parse_helpers import (
    collect_unparsed_protocols,
    deduplicate_protocol_list,
    filter_protocol_file_lists,
    merge_into_parsed_dicts,
    update_filtered_protocol_list,
    walk_protocol_files,
)
from calibration_statistics_tool.ui.handlers.stats_handlers import clear_stats_ui, update_stats_nav_buttons

if TYPE_CHECKING:  # pragma: no cover
    from calibration_statistics_tool.ui.handlers.app_context import AppContext

from calibration_statistics_tool.shared import logconfig

parseDataLog = logconfig.mainLoadDataLogger.logger


# ---------------------------------------------------------------------------
# Sensor muster
# ---------------------------------------------------------------------------

def parseProtSensorMusterClick(ctx: "AppContext") -> None:
    from calibration_statistics_tool.antenna_patterns import antpat_v5_main_v3 as _antPat1  # noqa: PLC0415
    from calibration_statistics_tool.tx_diagrams import TxAntDiagrams as _txAntDiag    # noqa: PLC0415
    state = ctx.qt.parseProtSensorMusterCheckBox.isChecked()
    ctx.mv.set_sensor_muster_enabled(state == 1)
    ctx.plc.set_sensor_muster_enabled(state == 1)
    _antPat1.setup["useSensorMuster"] = 1 if state else 0
    _txAntDiag.plotSetup["useSensorMuster"] = 1 if state else 0
    parseDataLog.debug("plotSetup: " + str(ctx.plc.plotSetup))


# ---------------------------------------------------------------------------
# Import protocols
# ---------------------------------------------------------------------------

def importProtocolsDirPath(ctx: "AppContext") -> None:
    protocolDirPath = ""
    if aux.inputProtocolDir:
        ctx.qt.parseProtImportProtDirPathFDialog.setDirectory(aux.inputProtocolDir)
    if ctx.qt.parseProtImportProtDirPathFDialog.exec_():
        protocolDirPath = ctx.qt.parseProtImportProtDirPathFDialog.selectedFiles()[0]
    protocolFilesList = protocolFilter.ProtocolInfoClass.GetAllProtocolsList(protocolDirPath)
    for i in range(len(protocolFilesList)):
        protocolFilesList[i] = protocolFilesList[i].replace("\\", "/")
    fillInProtocolData(ctx, protocolFilesList)


def importProtocolsFileList(ctx: "AppContext") -> None:
    protocolFilesList = []
    if aux.inputProtocolDir:
        ctx.qt.parseProtImportProtFListFDialog.setDirectory(aux.inputProtocolDir)
    if ctx.qt.parseProtImportProtFListFDialog.exec_():
        protocolFilesList = ctx.qt.parseProtImportProtFListFDialog.selectedFiles()
    fillInProtocolData(ctx, protocolFilesList)


# ---------------------------------------------------------------------------
# Protocol helpers
# ---------------------------------------------------------------------------

def getProtPathTypeDictList(ctx: "AppContext", protocolPathList: list) -> list:
    """Thin Qt-aware wrapper: reads UI state via view and delegates to ParseController."""
    return ctx.pc.build_prot_path_type_list(
        protocolPathList,
        burn_in_cal_mode=ctx.mv.get_burn_in_cal_mode(),
        include_burn_in_start=ctx.mv.get_include_burn_in_start(),
    )


def _update_protocol_dicts(
    ctx: "AppContext",
    accepted_crit_prot_list: list,
    sys_diag_file_path_dict_temp: list,
    tx_diag_file_path_dict_temp: list,
    filtered_protocol_list: list,
    acc_error_prot_list: list,
    acc_abort_crit_prot_list: list,
    acc_limit_exceeded_prot_list: list,
) -> list:
    ctx.pc.acceptedProtocolPathDict["errorProtList"]         += acc_error_prot_list
    ctx.pc.acceptedProtocolPathDict["abbortCritProtList"]    += acc_abort_crit_prot_list
    ctx.pc.acceptedProtocolPathDict["limitExceededProtList"] += acc_limit_exceeded_prot_list

    accepted_prot_path_type_dict_list = getProtPathTypeDictList(ctx, accepted_crit_prot_list)
    ctx.pc.protocolPathDict["protocolPathTypeDictList"] += accepted_prot_path_type_dict_list

    accepted_path_set = {d["protocolPath"] for d in ctx.pc.protocolPathDict["protocolPathTypeDictList"]}

    # Protocols dropped by type-filtering (e.g. BurnIn-start when checkbox is off) should
    # be surfaced in filteredProtocolPathDict so the ratio label reflects them, rather than
    # disappearing silently with "No new protocols Loaded."
    type_filtered = [p for p in accepted_crit_prot_list if p not in accepted_path_set]
    filtered_protocol_list.extend(type_filtered)

    update_filtered_protocol_list(filtered_protocol_list, ctx.pc.filteredProtocolPathDict, accepted_path_set)

    parseDataLog.info("Filtered Protocol List:")
    for elem in ctx.pc.filteredProtocolPathDict["protocolPathList"]:
        parseDataLog.info(elem)

    already_parsed = collect_unparsed_protocols(
        accepted_prot_path_type_dict_list, ctx.pc.parsedProtDict, ctx.pc.protToBeParsedDict
    )
    for path in already_parsed:
        parseDataLog.info("Protocol is already parsed: " + path)

    parseDataLog.info("Num. of Total Accepted Protocols: " + str(len(ctx.pc.protocolPathDict["protocolPathTypeDictList"])))
    parseDataLog.info("Num. of System Diagram Files: " + str(len(sys_diag_file_path_dict_temp)))

    return accepted_prot_path_type_dict_list


def _populate_sel_prot_table(
    ctx: "AppContext",
    accepted_prot_path_type_dict_list: list,
    sys_diag_file_path_dict_temp: list,
    tx_diag_file_path_dict_temp: list,
) -> None:
    header = ctx.qt.parseProtSelProtTable.horizontalHeader()
    header.setSectionResizeMode(0, ctx.qt.QHeaderView.ResizeMode.Interactive)
    ctx.qt.parseProtSelProtTable.setColumnWidth(0, 400)
    header.setSectionResizeMode(1, ctx.qt.QHeaderView.ResizeMode.Interactive)
    ctx.qt.parseProtSelProtTable.setColumnWidth(1, 110)
    header.setSectionResizeMode(2, ctx.qt.QHeaderView.ResizeMode.Interactive)
    header.setSectionResizeMode(3, ctx.qt.QHeaderView.ResizeMode.Stretch)

    ref_row_idx = ctx.qt.parseProtSelProtTable.rowCount()

    for prot_idx, entry in enumerate(accepted_prot_path_type_dict_list):
        protocol_path        = entry["protocolPath"]
        protocol_type        = entry["type"]
        # Either list may be empty when its checkbox was unchecked — fall back to [].
        sys_diag_per_prot = (
            sys_diag_file_path_dict_temp[prot_idx]["ptu2FilesList"]
            if prot_idx < len(sys_diag_file_path_dict_temp)
            else []
        )
        tx_ant_diag_per_prot = (
            tx_diag_file_path_dict_temp[prot_idx]["txAntDiagList"]
            if prot_idx < len(tx_diag_file_path_dict_temp)
            else []
        )
        prot_table_data      = dp.ProtocolsTableData(protocol_path, sys_diag_per_prot, tx_ant_diag_per_prot)

        if sys_diag_per_prot or tx_ant_diag_per_prot:
            for rel_row in range(prot_table_data.biggerListLength):
                row_idx = rel_row + ref_row_idx
                ctx.qt.parseProtSelProtTable.insertRow(row_idx)
                ctx.qt.parseProtSelProtTable.setItem(
                    row_idx, 0,
                    QTableWidgetItem(prot_table_data.protocolPath if rel_row == 0 else ""),
                )
                ctx.qt.parseProtSelProtTable.setItem(row_idx, 1, QTableWidgetItem(protocol_type))
                ctx.qt.parseProtSelProtTable.setItem(row_idx, 2, QTableWidgetItem(prot_table_data.sysDiagFilePathShapedList[rel_row]))
                ctx.qt.parseProtSelProtTable.setItem(row_idx, 3, QTableWidgetItem(prot_table_data.txAntDiagFilePathShapedList[rel_row]))

            for span_entry in prot_table_data.smallerListRowSpanList:
                ctx.qt.parseProtSelProtTable.setSpan(
                    span_entry["spanStart"] + ref_row_idx,
                    prot_table_data.smallerListColIdx,
                    span_entry["spanCount"],
                    1,
                )

            ctx.qt.parseProtSelProtTable.setSpan(ref_row_idx, 0, prot_table_data.biggerListLength, 1)
            ctx.qt.parseProtSelProtTable.setSpan(ref_row_idx, 1, prot_table_data.biggerListLength, 1)
            ref_row_idx += prot_table_data.biggerListLength
        else:
            row_idx = prot_idx + ref_row_idx
            ctx.qt.parseProtSelProtTable.insertRow(row_idx)
            ctx.qt.parseProtSelProtTable.setItem(row_idx, 0, QTableWidgetItem(protocol_path))
            ctx.qt.parseProtSelProtTable.setItem(row_idx, 1, QTableWidgetItem(protocol_type))


def fillInProtocolData(ctx: "AppContext", protocolFilesList: list) -> None:
    ctx.qt.parseProtTableTabWidget.setCurrentIndex(0)
    if not protocolFilesList:
        return

    ctx.mv.set_progress_label("Loading...")
    ctx.mv.reset_progress_bar()

    if not ctx.pc.protocolPathDict["protocolPathTypeDictList"]:
        ctx.qt.parseProtSelProtTable.setRowCount(0)

    protNonRepList = deduplicate_protocol_list(
        protocolFilesList, ctx.pc.protocolPathDict["protocolPathTypeDictList"]
    )
    for p in set(protocolFilesList) - set(protNonRepList):
        parseDataLog.info("Protocol is already imported: " + p)

    (
        sysDiagFilePathDictTemp,
        txDiagfilePathDictTemp,
        acceptedCritProtList,
        accErrorProtList,
        accAbbortCritProtList,
        accLimitExceededProtList,
        filteredProtocolList,
    ) = getprotcols(ctx, protNonRepList,
                    ctx.qt.parseProtSysDiagCheckBox.isChecked(),
                    ctx.qt.parseProtTxAntDiagCheckBox.isChecked())

    if sysDiagFilePathDictTemp:
        ctx.pc.sysDiagFilePathDict["filePathList"] += sysDiagFilePathDictTemp
    if txDiagfilePathDictTemp:
        ctx.pc.txDiagfilePathDict["filePathList"] += txDiagfilePathDictTemp

    acceptedProtPathTypeDictList = _update_protocol_dicts(
        ctx,
        acceptedCritProtList,
        sysDiagFilePathDictTemp, txDiagfilePathDictTemp,
        filteredProtocolList,
        accErrorProtList, accAbbortCritProtList, accLimitExceededProtList,
    )

    _populate_sel_prot_table(ctx, acceptedProtPathTypeDictList, sysDiagFilePathDictTemp, txDiagfilePathDictTemp)

    if ctx.pc.protToBeParsedDict["protocolPathTypeDictList"]:
        ctx.mv.set_progress_bar_range(len(ctx.pc.protToBeParsedDict["protocolPathTypeDictList"]))
        ctx.mv.set_progress_bar(0)
        ctx.mv.set_progress_bar_format(
            f'{ctx.mv.get_progress_bar_value()} / {len(ctx.pc.protToBeParsedDict["protocolPathTypeDictList"])}'
        )
        progBarLabelStr = (
            f'Protocols to be parsed: {len(ctx.pc.protToBeParsedDict["protocolPathTypeDictList"])}'
            f' / {len(ctx.pc.protocolPathDict["protocolPathTypeDictList"])}. '
        )
        ctx.mv.set_progress_label(progBarLabelStr)
    else:
        ctx.mv.set_progress_label("No new protocols Loaded.")

    total = len(ctx.pc.protocolPathDict["protocolPathTypeDictList"])
    ctx.mv.set_loaded_prot_ratio_label(total, len(ctx.pc.filteredProtocolPathDict["protocolPathList"]))
    ctx.mv.set_eol_error_label(len(ctx.pc.acceptedProtocolPathDict["errorProtList"]), total)
    ctx.mv.set_abort_crit_label(len(ctx.pc.acceptedProtocolPathDict["abbortCritProtList"]), total)
    ctx.mv.set_meas_limits_label(len(ctx.pc.acceptedProtocolPathDict["limitExceededProtList"]), total)
    ctx.mv.set_parsed_loaded_label(len(ctx.pc.parsedProtDict["protocolPathTypeDictList"]), total)


# ---------------------------------------------------------------------------
# PTU2 / TxAntDiag add-and-parse
# ---------------------------------------------------------------------------

def addAndParsePtu2Files(ctx: "AppContext") -> None:
    ctx.qt.parseProtTableTabWidget.setCurrentIndex(2)
    ptu2FilesList = []
    if aux.inputPtuDir:
        ctx.qt.parseProtAddAndParsePtu2FDialog.setDirectory(aux.inputPtuDir)
    if ctx.qt.parseProtAddAndParsePtu2FDialog.exec_():
        ptu2FilesList = ctx.qt.parseProtAddAndParsePtu2FDialog.selectedFiles()
        ptu2FilesList.sort()

    parsed, failed = ctx.pc.parse_ptu2_files(
        ptu2FilesList,
        ctx.plc.plotSetup["useSensorMuster"],
        ctx.plc.plotSetup["sensorMusterList"],
    )
    ctx.pc.add_ptu2_to_state(parsed, failed)

    clearTable(ctx, ctx.qt.parseProtAddPtu2ParsedTable)
    for idx, item in enumerate(ctx.pc.separatePtu2ParsedDataDict["parsedDataList"]):
        ctx.qt.parseProtAddPtu2ParsedTable.insertRow(idx)
        ctx.qt.parseProtAddPtu2ParsedTable.setItem(idx, 0, QTableWidgetItem(item.fileTitle.fileNamePath))
    ctx.mv.set_sep_par_ptu2_files_label(ctx.pc.ptu2_parsed_count())

    clearTable(ctx, ctx.qt.parseProtAddPtu2FailedTable)
    for idx, item in enumerate(ctx.pc.separatePtu2FailedDataDict["parsedDataList"]):
        ctx.qt.parseProtAddPtu2FailedTable.insertRow(idx)
        ctx.qt.parseProtAddPtu2FailedTable.setItem(idx, 0, QTableWidgetItem(item.fileTitle.fileNamePath))


def addAndParseTxAntDiagFiles(ctx: "AppContext") -> None:
    ctx.qt.parseProtTableTabWidget.setCurrentIndex(3)
    txAntDiagFilesList = []
    if aux.inputTxAntDir:
        ctx.qt.parseProtAddAndParseTxAntDiagFDialog.setDirectory(aux.inputTxAntDir)
    if ctx.qt.parseProtAddAndParseTxAntDiagFDialog.exec_():
        txAntDiagFilesList = ctx.qt.parseProtAddAndParseTxAntDiagFDialog.selectedFiles()

    parsed, failed = ctx.pc.parse_tx_ant_diag_files(
        txAntDiagFilesList,
        ctx.plc.plotSetup["useSensorMuster"],
        ctx.plc.plotSetup["sensorMusterList"],
    )
    ctx.pc.add_tx_ant_diag_to_state(parsed, failed)

    clearTable(ctx, ctx.qt.parseProtAddTxAntDiagParsedTable)
    for idx, item in enumerate(ctx.pc.separateTxAntDiagParsedDataDict["parsedDataList"]):
        ctx.qt.parseProtAddTxAntDiagParsedTable.insertRow(idx)
        ctx.qt.parseProtAddTxAntDiagParsedTable.setItem(idx, 0, QTableWidgetItem(item.fileTitle.fileNamePath))
    ctx.mv.set_sep_par_tx_ant_diag_files_label(ctx.pc.tx_ant_diag_parsed_count())

    clearTable(ctx, ctx.qt.parseProtAddTxAntDiagFailedTable)
    for idx, item in enumerate(ctx.pc.separateTxAntDiagFailedDataDict["parsedDataList"]):
        ctx.qt.parseProtAddTxAntDiagFailedTable.insertRow(idx)
        ctx.qt.parseProtAddTxAntDiagFailedTable.setItem(idx, 0, QTableWidgetItem(item.fileTitle.fileNamePath))


# ---------------------------------------------------------------------------
# Limits file pickers
# ---------------------------------------------------------------------------

def loadCalInputLimitsFile(ctx: "AppContext") -> None:
    filePath = ""
    if ctx.qt.parseProtProtDataInFileCalFDialog.exec_():
        filePath = ctx.qt.parseProtProtDataInFileCalFDialog.selectedFiles()[0].replace("\\", "/")
    else:
        filePath = aux.calLimitsFilePath
    ctx.mv.set_cal_limits_file(filePath)


def loadBurnInInputLimitsFile(ctx: "AppContext") -> None:
    filePath = ""
    if ctx.qt.parseProtProtDataInFileBurnInFDialog.exec_():
        filePath = ctx.qt.parseProtProtDataInFileBurnInFDialog.selectedFiles()[0].replace("\\", "/")
    else:
        filePath = aux.burnInLimitsFilePath
    ctx.mv.set_burn_in_limits_file(filePath)


def loadBurnInLimitsGroupsFile(ctx: "AppContext") -> None:
    filePath = ""
    if ctx.qt.parseProtProtDataLimGroupsBurnInFDialog.exec_():
        filePath = ctx.qt.parseProtProtDataLimGroupsBurnInFDialog.selectedFiles()[0].replace("\\", "/")
    else:
        filePath = aux.burnInLimGroupsFilePath
    ctx.mv.set_burn_in_lim_groups_file(filePath)


def loadCalLimitsGroupsFile(ctx: "AppContext") -> None:
    filePath = ""
    if ctx.qt.parseProtProtDataLimGroupsCalFDialog.exec_():
        filePath = ctx.qt.parseProtProtDataLimGroupsCalFDialog.selectedFiles()[0].replace("\\", "/")
    else:
        filePath = aux.calLimGroupsFilePath
    ctx.mv.set_cal_lim_groups_file(filePath)


def _on_burn_in_group_changed(ctx: "AppContext", index: int) -> None:
    """Sync the BurnIn active group index in ParseController when the ComboBox changes."""
    ctx.pc.burnInLimitsGroupDict['activeGroupIndex'] = index


def _on_cal_group_changed(ctx: "AppContext", index: int) -> None:
    """Sync the Calibration active group index in ParseController when the ComboBox changes."""
    ctx.pc.calLimitsGroupDict['activeGroupIndex'] = index


# ---------------------------------------------------------------------------
# Parse orchestration
# ---------------------------------------------------------------------------

def setup_progress_bar(ctx: "AppContext") -> tuple[str, int]:
    ctx.mv.reset_progress_bar()
    protToBeParsedListLen = len(ctx.pc.protToBeParsedDict["protocolPathTypeDictList"])
    progBarLabelStr = ""
    if protToBeParsedListLen != 0:
        ctx.mv.set_progress_bar_range(protToBeParsedListLen)
        progBarLabelStr = (
            f'Protocols to be parsed: {protToBeParsedListLen}'
            f' / {len(ctx.pc.protocolPathDict["protocolPathTypeDictList"])}. '
        )
        ctx.mv.set_progress_label(progBarLabelStr)
        ctx.mv.set_progress_bar(0)
        ctx.mv.set_progress_bar_format(f"{ctx.mv.get_progress_bar_value()} / {protToBeParsedListLen}")
    return progBarLabelStr, protToBeParsedListLen


def _load_protocol_data(
    ctx: "AppContext",
    filteredSysDiagList: list,
    filteredTxAntDiagList: list,
    progBarLabelStr: str,
    protToBeParsedListLen: int,
) -> tuple[list, list, list, list]:
    from calibration_statistics_tool.shared import loaddata as ld
    from calibration_statistics_tool.tx_diagrams import load_TxAntData as ld_txantdiag
    from calibration_statistics_tool.tx_diagrams import TxAntDiagrams as txAntDiag

    sysDiagDataList:         list = []
    txAntDiagDataList:       list = []
    sysDiagParsedDataList:   list = []
    txAntDiagParsedDataList: list = []

    twentyPercent = int(protToBeParsedListLen / 5)
    twentyPercRes = protToBeParsedListLen % 5
    idx      = 1
    final    = 0
    setFinal = False

    for protFileIdx in range(protToBeParsedListLen):
        sysDiagDataPerProt = filteredSysDiagList[protFileIdx]["ptu2FilesList"]
        sysDiagLoadedData  = ld.LoadData(
            sysDiagDataPerProt,
            ctx.plc.plotSetup["useSensorMuster"],
            ctx.plc.plotSetup["sensorMusterList"],
        )
        if sysDiagLoadedData.invalidPath == 1:
            parseDataLog.info(sysDiagLoadedData.invalidPathString)
            sysDiagDataList.append([])  # keep index aligned with protToBeParsedDict
        else:
            sysDiagDataList.append(sysDiagDataPerProt)
            sysDiagParsedDataList += sysDiagLoadedData.parseDataList

        txAntDiagDataPerProt = filteredTxAntDiagList[protFileIdx]["txAntDiagList"]
        txAntDiagLoadedData  = ld_txantdiag.LoadData(
            txAntDiagDataPerProt,
            txAntDiag.plotSetup["useSensorMuster"],
            txAntDiag.plotSetup["sensorMusterList"],
        )
        if txAntDiagLoadedData.invalidPath == 1:
            parseDataLog.info(txAntDiagLoadedData.invalidPathString)
            txAntDiagDataList.append([])  # keep index aligned with protToBeParsedDict
        else:
            txAntDiagDataList.append(txAntDiagDataPerProt)
            txAntDiagParsedDataList += txAntDiagLoadedData.parseDataList

        if setFinal:
            ctx.mv.set_progress_bar_format(f"{final} / {protToBeParsedListLen}")
        else:
            ctx.mv.set_progress_bar_format(f"{idx} / {protToBeParsedListLen}")

        if twentyPercent != 0:
            if idx % twentyPercent == 0:
                _, tail = os.path.split(
                    ctx.pc.protToBeParsedDict["protocolPathTypeDictList"][protFileIdx]["protocolPath"]
                )
                ctx.mv.set_progress_label(progBarLabelStr + "Protocol: " + tail)
                if int(idx / twentyPercent) < 5:
                    ctx.mv.set_progress_bar(idx)
                else:
                    setFinal = True
                    final    = idx + twentyPercRes
                    ctx.mv.set_progress_bar(final)
        else:
            _, tail = os.path.split(
                ctx.pc.protToBeParsedDict["protocolPathTypeDictList"][protFileIdx]["protocolPath"]
            )
            ctx.mv.set_progress_label(progBarLabelStr + "Protocol: " + tail)
            ctx.mv.set_progress_bar(idx)

        idx += 1

    return sysDiagDataList, txAntDiagDataList, sysDiagParsedDataList, txAntDiagParsedDataList


def _populate_accepted_protocols_table(
    ctx: "AppContext",
    sysDiagDataList: list,
    txAntDiagDataList: list,
) -> None:
    header = ctx.qt.parseProtAccProtTable.horizontalHeader()
    header.setSectionResizeMode(0, ctx.qt.QHeaderView.ResizeMode.Interactive)
    ctx.qt.parseProtAccProtTable.setColumnWidth(0, 400)
    header.setSectionResizeMode(1, ctx.qt.QHeaderView.ResizeMode.Interactive)
    ctx.qt.parseProtAccProtTable.setColumnWidth(1, 110)
    header.setSectionResizeMode(2, ctx.qt.QHeaderView.ResizeMode.Interactive)
    header.setSectionResizeMode(3, ctx.qt.QHeaderView.ResizeMode.Stretch)

    if not sysDiagDataList and not txAntDiagDataList:
        return

    refRowIdx = ctx.qt.parseProtAccProtTable.rowCount()

    for protocolFileIdx in range(len(ctx.pc.protToBeParsedDict["protocolPathTypeDictList"])):
        protocolPath             = ctx.pc.protToBeParsedDict["protocolPathTypeDictList"][protocolFileIdx]["protocolPath"]
        protocolType             = ctx.pc.protToBeParsedDict["protocolPathTypeDictList"][protocolFileIdx]["type"]
        sysDiagListPerProtocol   = sysDiagDataList[protocolFileIdx]
        txAntDiagListPerProtocol = txAntDiagDataList[protocolFileIdx]
        protTableData            = dp.ProtocolsTableData(protocolPath, sysDiagListPerProtocol, txAntDiagListPerProtocol)

        if not sysDiagListPerProtocol and not txAntDiagListPerProtocol:
            rowIdx = refRowIdx
            ctx.qt.parseProtAccProtTable.insertRow(rowIdx)
            ctx.qt.parseProtAccProtTable.setItem(rowIdx, 0, QTableWidgetItem(protocolPath))
            ctx.qt.parseProtAccProtTable.setItem(rowIdx, 1, QTableWidgetItem(protocolType))
            ctx.qt.parseProtAccProtTable.setItem(rowIdx, 2, QTableWidgetItem(''))
            ctx.qt.parseProtAccProtTable.setItem(rowIdx, 3, QTableWidgetItem(''))
            refRowIdx += 1
            continue

        for relRowIdx in range(protTableData.biggerListLength):
            rowIdx = relRowIdx + refRowIdx
            ctx.qt.parseProtAccProtTable.insertRow(rowIdx)
            ctx.qt.parseProtAccProtTable.setItem(
                rowIdx, 0,
                QTableWidgetItem(protTableData.protocolPath if relRowIdx == 0 else ""),
            )
            ctx.qt.parseProtAccProtTable.setItem(rowIdx, 1, QTableWidgetItem(protocolType))
            ctx.qt.parseProtAccProtTable.setItem(rowIdx, 2, QTableWidgetItem(protTableData.sysDiagFilePathShapedList[relRowIdx]))
            ctx.qt.parseProtAccProtTable.setItem(rowIdx, 3, QTableWidgetItem(protTableData.txAntDiagFilePathShapedList[relRowIdx]))

        for spanEntry in protTableData.smallerListRowSpanList:
            ctx.qt.parseProtAccProtTable.setSpan(
                spanEntry["spanStart"] + refRowIdx,
                protTableData.smallerListColIdx,
                spanEntry["spanCount"],
                1,
            )

        ctx.qt.parseProtAccProtTable.setSpan(refRowIdx, 0, protTableData.biggerListLength, 1)
        refRowIdx += protTableData.biggerListLength


def parseData(ctx: "AppContext") -> None:
    ctx.qt.parseProtTableTabWidget.setCurrentIndex(1)

    if not ctx.pc.protToBeParsedDict["protocolPathTypeDictList"]:
        ctx.mv.set_progress_label("No protocols to be parsed.")
        parseDataLog.info("No protocol files loaded. Please load protocol files before parsing.")
        return

    if not ctx.pc.parsedProtDict["protocolPathTypeDictList"]:
        ctx.qt.parseProtAccProtTable.setRowCount(0)

    filteredSysDiagList, filteredTxAntDiagList = filter_protocol_file_lists(
        ctx.pc.protToBeParsedDict, ctx.pc.sysDiagFilePathDict,
        ctx.pc.txDiagfilePathDict, ctx.pc.parsedProtDict,
    )

    progBarLabelStr, protToBeParsedListLen = setup_progress_bar(ctx)

    sysDiagDataList, txAntDiagDataList, sysDiagParsedDataList, txAntDiagParsedDataList = _load_protocol_data(
        ctx, filteredSysDiagList, filteredTxAntDiagList, progBarLabelStr, protToBeParsedListLen,
    )

    merge_into_parsed_dicts(
        sysDiagParsedDataList, txAntDiagParsedDataList,
        ctx.pc.sysDiagParsedDataDict, ctx.pc.txAntDiagParsedDataDict,
    )

    ctx.mv.set_parsed_loaded_label(
        len(ctx.pc.parsedProtDict["protocolPathTypeDictList"]),
        len(ctx.pc.protocolPathDict["protocolPathTypeDictList"]),
    )
    ctx.mv.set_ptu2_files_label(len(ctx.pc.sysDiagParsedDataDict["parsedDataList"]))
    ctx.mv.set_tx_ant_diag_files_label(len(ctx.pc.txAntDiagParsedDataDict["parsedDataList"]))

    _populate_accepted_protocols_table(ctx, sysDiagDataList, txAntDiagDataList)

    ctx.pc.parse_protocol_limits(
        burn_in_limits_path=ctx.qt.parseProtProtDataInFileBurnInLabel.text(),
        cal_limits_path=ctx.qt.parseProtProtDataInFileCalLabel.text(),
        include_burn_in=ctx.qt.parseProtProtDataBurnInInclCheckBox.isChecked(),
        include_cal=ctx.qt.parseProtProtDataCalInclCheckBox.isChecked(),
        extend_burn_in=ctx.qt.parseProtProtDataBurnInExtCheckBox.isChecked(),
        extend_cal=ctx.qt.parseProtProtDataCalExtCheckBox.isChecked(),
    )

    ctx.pc.build_limits_rows()
    ctx.pc.build_limits_groups(
        burn_in_lim_groups_path=ctx.qt.parseProtProtDataLimGroupsBurnInLabel.text(),
        cal_lim_groups_path=ctx.qt.parseProtProtDataLimGroupsCalLabel.text(),
        include_burn_in=ctx.qt.parseProtProtDataBurnInInclCheckBox.isChecked(),
        include_cal=ctx.qt.parseProtProtDataCalInclCheckBox.isChecked(),
        extend_burn_in_groups=ctx.qt.parseProtProtDataBurnInLimGroupsExtCheckBox.isChecked(),
        extend_cal_groups=ctx.qt.parseProtProtDataCalLimGroupsExtCheckBox.isChecked(),
    )

    burn_in_group_names = [
        g.name for g in ctx.pc.burnInLimitsGroupDict['limitsGroupList']
    ]
    cal_group_names = [
        g.name for g in ctx.pc.calLimitsGroupDict['limitsGroupList']
    ]
    ctx.mv.populate_burn_in_groups(burn_in_group_names)
    ctx.mv.populate_cal_groups(cal_group_names)

    update_stats_nav_buttons(ctx)

    ctx.mv.set_progress_label(
        f'Parsing finished. Protocols parsed: {len(ctx.pc.protToBeParsedDict["protocolPathTypeDictList"])}.'
    )
    ctx.pc.protToBeParsedDict["protocolPathTypeDictList"][:] = []


def importDbProtocolsList(ctx: "AppContext") -> None:
    parseDataLog.warning("Database protocol import not available - CT_DataCollector module removed")


def importBurnInProtocolsList(ctx: "AppContext") -> None:
    fillInCertProtocolData(ctx, [], "BurnIn")


def importCalProtocolsList(ctx: "AppContext") -> None:
    fillInCertProtocolData(ctx, [], "Calibration")


def fillInCertProtocolData(ctx: "AppContext", protocolFilesList: list, protType: str) -> None:
    ctx.qt.mainTabWidget.setCurrentIndex(0)
    ctx.qt.parseProtTableTabWidget.setCurrentIndex(4)


def clearData(ctx: "AppContext") -> None:
    ctx.pc.clear_state()

    ctx.mv.set_parsed_loaded_label(0)
    ctx.mv.set_ptu2_files_label(0)
    ctx.mv.set_tx_ant_diag_files_label(0)
    ctx.mv.set_loaded_protocols_label(0)
    ctx.mv.set_eol_error_label(0)
    ctx.mv.set_abort_crit_label(0)
    ctx.mv.set_meas_limits_label(0)
    ctx.mv.set_sep_par_ptu2_files_label(0)
    ctx.mv.set_sep_par_tx_ant_diag_files_label(0)
    ctx.mv.reset_progress_bar()
    ctx.mv.set_progress_bar_format("")
    ctx.mv.set_progress_label("No protocols loaded.")
    ctx.mv.populate_burn_in_groups([])
    ctx.mv.populate_cal_groups([])

    clearTable(ctx, ctx.qt.parseProtSelProtTable)
    clearTable(ctx, ctx.qt.parseProtAccProtTable)
    clearTable(ctx, ctx.qt.parseProtAddPtu2ParsedTable)
    clearTable(ctx, ctx.qt.parseProtAddPtu2FailedTable)
    clearTable(ctx, ctx.qt.parseProtAddTxAntDiagFailedTable)
    clearTable(ctx, ctx.qt.parseProtAddTxAntDiagParsedTable)
    clearTable(ctx, ctx.qt.parseProtStatsParsedTable)
    clearTable(ctx, ctx.qt.parseProtStatsFailedTable)

    clear_stats_ui(ctx)
    parseDataLog.info("Loaded and Parsed Data cleared!")


def clearTable(ctx: "AppContext", tableWidget) -> None:
    while tableWidget.rowCount() > 0:
        tableWidget.removeRow(0)
    tableWidget.setRowCount(ctx.qt.PARSE_PROT_TABLE_ROWS)
    tableWidgetHeader = tableWidget.horizontalHeader()
    tableWidgetHeader.setSectionResizeMode(ctx.qt.QHeaderView.ResizeMode.Stretch)


def clearLogTable(ctx: "AppContext") -> None:
    while ctx.qt.mainLogTable.rowCount() > 0:
        ctx.qt.mainLogTable.removeRow(0)
    ctx.qt.mainLogTable.setRowCount(0)
    ctx.qt.mainLogTableHandler.logTableRow = 0


def getprotcols(
    ctx: "AppContext",
    allProtocolsPathNamesList: list,
    searchPtu2Files: bool,
    searchTxAntDiagFiles: bool,
) -> tuple[list, list, list, list, list, list, list]:
    bUseFilesWithError          = ctx.qt.parseProtEolErrorCheckBox.isChecked()
    bUseFilesAbbortCriterion    = ctx.qt.parseProtEolAbortCheckBox.isChecked()
    bUseFilesWIthLimitsExceeded = ctx.qt.parseProtEolMeasLimitsCheckBox.isChecked()

    PreParseInfoProtocolsList, *_ = protocolFilter.ProtocolInfoClass.PreParseProtcols(allProtocolsPathNamesList)

    parseDataLog.info(
        f"Filter Protocols: UseFilesWithError = {bUseFilesWithError}, "
        f"UseFilesAbbortCriterion = {bUseFilesAbbortCriterion}, "
        f"UseFilesWIthLimitsExceeded = {bUseFilesWIthLimitsExceeded}"
    )

    acceptedProtocolsList, filteredProtocolsList = protocolFilter.ProtocolInfoClass.FilterProtocols(
        PreParseInfoProtocolsList, bUseFilesWithError, bUseFilesAbbortCriterion, bUseFilesWIthLimitsExceeded
    )
    parseDataLog.info(f"Accepted Protocols {len(acceptedProtocolsList)} of {len(allProtocolsPathNamesList)}")

    if ctx.qt.parseProtnewProtCheckBox.isChecked():
        parseDataLog.info("Only the latest protocol will be selected.")
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


# ---------------------------------------------------------------------------
# Widget initialisation
# ---------------------------------------------------------------------------

def init_widgets(ctx: "AppContext") -> None:
    """Set default widget states for the parse tab (PST-66)."""
    from calibration_statistics_tool.antenna_patterns import antpat_v5_main_v3 as _antPat1  # noqa: PLC0415
    from calibration_statistics_tool.tx_diagrams import TxAntDiagrams as _txAntDiag    # noqa: PLC0415

    # Sensor muster
    ctx.qt.parseProtSensorMusterCheckBox.setChecked(False)
    ctx.mv.set_sensor_muster_enabled(False)
    ctx.plc.plotSetup["useSensorMuster"] = 0
    _antPat1.setup["useSensorMuster"] = 0
    _txAntDiag.plotSetup["useSensorMuster"] = 0

    # Burn-in / calibration radio buttons
    ctx.qt.parseProtBurnInCalGroupRadio1.setChecked(True)
    ctx.qt.parseProtBurnInCalGroupRadio2.setChecked(False)
    ctx.qt.parseProtBurnInCalGroupRadio3.setChecked(False)

    # Protocol data include/exclude checkboxes
    ctx.qt.parseProtProtDataBurnInInclCheckBox.setChecked(True)
    ctx.qt.parseProtProtDataBurnInExtCheckBox.setChecked(False)
    ctx.qt.parseProtProtDataCalInclCheckBox.setChecked(True)
    ctx.qt.parseProtProtDataCalExtCheckBox.setChecked(False)

    # Limits-file path labels
    ctx.mv.set_burn_in_limits_file(aux.burnInLimitsFilePath)
    ctx.mv.set_cal_limits_file(aux.calLimitsFilePath)
    ctx.mv.set_burn_in_lim_groups_file(aux.burnInLimGroupsFilePath)
    ctx.mv.set_cal_lim_groups_file(aux.calLimGroupsFilePath)
    ctx.mv.set_stats_input_conf_path(aux.statsinputconffilepath)


# ---------------------------------------------------------------------------
# Wire all signals
# ---------------------------------------------------------------------------

def wire(ctx: "AppContext") -> None:
    """Connect all parse-tab Qt signals to their handlers."""
    ctx.qt.parseProtSensorMusterCheckBox.stateChanged.connect(
        lambda: parseProtSensorMusterClick(ctx)
    )
    ctx.qt.parseProtImportProtFListPushBtn.clicked.connect(
        lambda: importProtocolsFileList(ctx)
    )
    ctx.qt.parseProtImportProtDirPathPushBtn.clicked.connect(
        lambda: importProtocolsDirPath(ctx)
    )
    ctx.qt.parseProtClearDataPushBtn.clicked.connect(
        lambda: clearData(ctx)
    )
    ctx.qt.parseProtParseDataPushBtn.clicked.connect(
        lambda: parseData(ctx)
    )
    ctx.qt.parseProtAddAndParsePtu2PushBtn.clicked.connect(
        lambda: addAndParsePtu2Files(ctx)
    )
    ctx.qt.parseProtAddAndParseTxAntDiagPushBtn.clicked.connect(
        lambda: addAndParseTxAntDiagFiles(ctx)
    )
    ctx.qt.parseProtProtDataInFileBurnInPushBtn.clicked.connect(
        lambda: loadBurnInInputLimitsFile(ctx)
    )
    ctx.qt.parseProtProtDataInFileCalPushBtn.clicked.connect(
        lambda: loadCalInputLimitsFile(ctx)
    )
    ctx.qt.parseProtProtDataLimGroupsBurnInPushBtn.clicked.connect(
        lambda: loadBurnInLimitsGroupsFile(ctx)
    )
    ctx.qt.parseProtProtDataLimGroupsCalPushBtn.clicked.connect(
        lambda: loadCalLimitsGroupsFile(ctx)
    )
    ctx.qt.parseProtProtDataBurnInGroupSelComboBox.currentIndexChanged.connect(
        lambda idx: _on_burn_in_group_changed(ctx, idx)
    )
    ctx.qt.parseProtProtDataCalGroupSelComboBox.currentIndexChanged.connect(
        lambda idx: _on_cal_group_changed(ctx, idx)
    )
    ctx.qt.mainLogTableClearBtn.clicked.connect(
        lambda: clearLogTable(ctx)
    )
