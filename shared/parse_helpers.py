"""Pure helper functions for protocol-file filtering and parsed-data deduplication.

These contain no Qt dependencies and are extracted from main.py so they can be
unit-tested independently.
"""
from __future__ import annotations

import os
from typing import Callable


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


def deduplicate_protocol_list(
    protocol_files_list: list[str],
    existing_path_type_dict_list: list[dict],
) -> list[str]:
    """Return paths from *protocol_files_list* not already in *existing_path_type_dict_list*.

    Args:
        protocol_files_list: Candidate protocol file paths to import.
        existing_path_type_dict_list: Already-imported entries, each with a
            ``protocolPath`` key.

    Returns:
        Ordered list of paths that are not yet imported.
    """
    existing = {d['protocolPath'] for d in existing_path_type_dict_list}
    return [p for p in protocol_files_list if p not in existing]


def walk_protocol_files(
    accepted_protocols_list: list,
    search_ptu2_files: bool,
    search_txantdiag_files: bool,
    use_error: bool,
    use_abort: bool,
    use_limits_exceeded: bool,
    get_ptu2_files_fn: Callable[[str, str], list],
    get_txantdiag_files_fn: Callable[[str, str], list],
) -> tuple[list, list, list, list, list, list]:
    """Walk accepted protocols and collect PTU2 / TxAntDiag file associations.

    For each entry in *accepted_protocols_list* the function derives file-search
    parameters from the protocol path, invokes the supplied search callables,
    and accumulates results into six output lists.

    Args:
        accepted_protocols_list: Pre-parsed protocol info objects exposing
            ``.PathName``, ``.bErrorOccured``, ``.bAbortCriterion``,
            ``.bLimitExceeded``.
        search_ptu2_files: When ``True``, search for PTU2 files.
        search_txantdiag_files: When ``True``, search for TxAntDiag files.
        use_error: Include error-flagged protocols in ``acc_error_prot_list``.
        use_abort: Include abort-criterion protocols in ``acc_abort_crit_prot_list``.
        use_limits_exceeded: Include limit-exceeded protocols in
            ``acc_limit_exceeded_prot_list``.
        get_ptu2_files_fn: ``callable(dir_path, search_pattern) -> list``
        get_txantdiag_files_fn: ``callable(dir_path, file_stem) -> list``

    Returns:
        ``(ptu2_files_list, txantdiag_list, acc_prot_list,
           acc_error_prot_list, acc_abort_crit_prot_list,
           acc_limit_exceeded_prot_list)``
    """
    ptu2_files_list:           list = []
    txantdiag_list:            list = []
    acc_prot_list:             list = []
    acc_error_prot_list:       list = []
    acc_abort_crit_prot_list:  list = []
    acc_limit_exceeded_prot_list: list = []

    for pre_parse_info in accepted_protocols_list:
        ptu2_files_list_dict: dict = {'protocolPath': '', 'ptu2FilesList': []}
        txantdiag_list_dict:  dict = {'protocolPath': '', 'txAntDiagList': []}

        path_only, file_name_only = os.path.split(pre_parse_info.PathName)
        file_name_no_ptu = (
            file_name_only
            .replace('Protocol_Chip', '')
            .replace('Protocol', '')
            .replace('protocol', '')
        )
        stem, ext = os.path.splitext(file_name_no_ptu)

        if search_ptu2_files:
            search_pattern = stem + '*PTU2*' + ext
            ptu2_files_list_dict['ptu2FilesList'] = get_ptu2_files_fn(path_only, search_pattern)

        if search_txantdiag_files:
            txantdiag_list_dict['txAntDiagList'] = get_txantdiag_files_fn(path_only, stem)

        if search_ptu2_files:
            ptu2_files_list_dict['protocolPath'] = pre_parse_info.PathName
            ptu2_files_list.append(ptu2_files_list_dict)

        if search_txantdiag_files:
            txantdiag_list_dict['protocolPath'] = pre_parse_info.PathName
            txantdiag_list.append(txantdiag_list_dict)

        if use_error and pre_parse_info.bErrorOccured:
            acc_error_prot_list.append(pre_parse_info.PathName)

        if use_abort and pre_parse_info.bAbortCriterion:
            acc_abort_crit_prot_list.append(pre_parse_info.PathName)

        if use_limits_exceeded and pre_parse_info.bLimitExceeded:
            acc_limit_exceeded_prot_list.append(pre_parse_info.PathName)

        acc_prot_list.append(pre_parse_info.PathName)

    return (
        ptu2_files_list, txantdiag_list, acc_prot_list,
        acc_error_prot_list, acc_abort_crit_prot_list, acc_limit_exceeded_prot_list,
    )


def update_filtered_protocol_list(
    new_filtered_list: list[str],
    filtered_protocol_path_dict: dict,
    accepted_path_set: set[str],
) -> None:
    """Add new filtered paths then remove any that were subsequently accepted.

    Mutates *filtered_protocol_path_dict['protocolPathList']* in-place:
    1. Appends paths from *new_filtered_list* not already present.
    2. Removes any path that now appears in *accepted_path_set*.

    Args:
        new_filtered_list: Freshly filtered paths from the latest import.
        filtered_protocol_path_dict: Dict with ``protocolPathList`` key.
        accepted_path_set: Set of paths that were accepted (should not remain filtered).
    """
    existing = set(filtered_protocol_path_dict['protocolPathList'])
    for p in new_filtered_list:
        if p not in existing:
            filtered_protocol_path_dict['protocolPathList'].append(p)
            existing.add(p)

    filtered_protocol_path_dict['protocolPathList'] = [
        p for p in filtered_protocol_path_dict['protocolPathList']
        if p not in accepted_path_set
    ]


def collect_unparsed_protocols(
    accepted_prot_path_type_dict_list: list[dict],
    parsed_prot_dict: dict,
    prot_to_be_parsed_dict: dict,
) -> list[str]:
    """Append accepted protocols not yet parsed to *prot_to_be_parsed_dict*.

    Skips entries whose ``protocolPath`` already appears in
    *parsed_prot_dict['protocolPathTypeDictList']*.  Mutates
    *prot_to_be_parsed_dict* in-place.

    Args:
        accepted_prot_path_type_dict_list: Newly accepted protocol dicts, each
            with a ``protocolPath`` key.
        parsed_prot_dict: Dict with ``protocolPathTypeDictList`` of already-parsed entries.
        prot_to_be_parsed_dict: Dict with ``protocolPathTypeDictList`` to append to.

    Returns:
        List of protocol paths that were skipped (already parsed).
    """
    parsed_paths = {d['protocolPath'] for d in parsed_prot_dict['protocolPathTypeDictList']}
    already_parsed: list[str] = []
    for entry in accepted_prot_path_type_dict_list:
        if entry['protocolPath'] not in parsed_paths:
            prot_to_be_parsed_dict['protocolPathTypeDictList'].append(entry)
        else:
            already_parsed.append(entry['protocolPath'])
    return already_parsed
