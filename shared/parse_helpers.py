"""Pure helper functions for protocol-file filtering and parsed-data deduplication.

These contain no Qt dependencies and are extracted from main.py so they can be
unit-tested independently.
"""
from __future__ import annotations


def filter_protocol_file_lists(
    protToBeParsedDict: dict,
    sysDiagFilePathDict: dict,
    txDiagfilePathDict: dict,
    parsedProtDict: dict,
) -> tuple[list, list]:
    """Match each protocol to its sys-diag and tx-ant-diag file entries.

    Iterates over every protocol entry in *protToBeParsedDict* and looks up a
    matching dict in the sys-diag and tx-ant-diag file-path lists (matched by
    ``protocolPath``).  Each entry is also appended to *parsedProtDict* to mark
    it as "attempted".

    Args:
        protToBeParsedDict: Dict containing ``protocolPathTypeDictList`` with
            entries that have a ``protocolPath`` key.
        sysDiagFilePathDict: Dict containing ``filePathList`` — each element has
            a ``protocolPath`` key and a ``ptu2FilesList`` value.
        txDiagfilePathDict: Dict containing ``filePathList`` — each element has
            a ``protocolPath`` key and a ``txAntDiagList`` value.
        parsedProtDict: Dict with ``protocolPathTypeDictList``; each matched
            entry is appended here.

    Returns:
        ``(filteredSysDiagList, filteredTxAntDiagList)`` — one entry per
        protocol in *protToBeParsedDict*, ``None``-entries are excluded.
    """
    filteredSysDiagList:  list = []
    filteredTxAntDiagList: list = []

    for entry in protToBeParsedDict['protocolPathTypeDictList']:
        protPath = entry['protocolPath']

        matched_sys = next(
            (d for d in sysDiagFilePathDict['filePathList'] if d['protocolPath'] == protPath),
            None,
        )
        if matched_sys is not None:
            filteredSysDiagList.append(matched_sys)

        matched_tx = next(
            (d for d in txDiagfilePathDict['filePathList'] if d['protocolPath'] == protPath),
            None,
        )
        if matched_tx is not None:
            filteredTxAntDiagList.append(matched_tx)

        parsedProtDict['protocolPathTypeDictList'].append(entry)

    return filteredSysDiagList, filteredTxAntDiagList


def merge_into_parsed_dicts(
    sysDiagParsedDataList: list,
    txAntDiagParsedDataList: list,
    sysDiagParsedDataDict: dict,
    txAntDiagParsedDataDict: dict,
) -> None:
    """Append newly parsed data items to the master dicts, skipping duplicates.

    Deduplication is done by ``fileTitle.fileNamePath``.  A set of already-known
    paths is built once per call (O(n)), so each membership test is O(1) rather
    than scanning the whole list.

    Args:
        sysDiagParsedDataList: Newly loaded sys-diag parsed-data objects.
        txAntDiagParsedDataList: Newly loaded tx-ant-diag parsed-data objects.
        sysDiagParsedDataDict: Master dict with ``parsedDataList`` for sys-diag.
        txAntDiagParsedDataDict: Master dict with ``parsedDataList`` for tx-ant-diag.
    """
    existing_sys_paths = {d.fileTitle.fileNamePath for d in sysDiagParsedDataDict['parsedDataList']}
    for item in sysDiagParsedDataList:
        if item.fileTitle.fileNamePath not in existing_sys_paths:
            sysDiagParsedDataDict['parsedDataList'].append(item)
            existing_sys_paths.add(item.fileTitle.fileNamePath)

    existing_tx_paths = {d.fileTitle.fileNamePath for d in txAntDiagParsedDataDict['parsedDataList']}
    for item in txAntDiagParsedDataList:
        if item.fileTitle.fileNamePath not in existing_tx_paths:
            txAntDiagParsedDataDict['parsedDataList'].append(item)
            existing_tx_paths.add(item.fileTitle.fileNamePath)
