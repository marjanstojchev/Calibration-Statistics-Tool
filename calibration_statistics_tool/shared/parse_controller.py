"""
ParseController: Encapsulates all protocol, PTU, and TxAnt parsing logic and state.

All methods in this class are pure business logic — they do not call any Qt/GUI
code.  The GUI layer (main.py / PST-47) is responsible for reading UI state
(checkbox values, selected file paths) and for updating widgets after each
call.  This keeps the controller fully unit-testable without a running Qt app.

Part of MVC refactor (PST-45).
"""
from __future__ import annotations

from calibration_statistics_tool.shared.parser_factory import ParserFactory
from calibration_statistics_tool.shared import safeparse as sp
import re
import math

from calibration_statistics_tool.shared.parseProtocols import (
    ParseProtocols,
    ParseInputLimitsGroups,
    LimitsRow,
    LimitsGroup,
    ProtocolType,
    ProtocolCategoriesEnum,
    ErrorStatusEnum,
)
from calibration_statistics_tool.shared import logconfig


class ParseController:
    """Owns all parsing-related application state and business logic."""

    # ------------------------------------------------------------------
    # Construction / state
    # ------------------------------------------------------------------

    def __init__(self) -> None:
        # Application state dicts (formerly module-level globals in main.py)
        self.sysDiagFilePathDict: dict                   = {'filePathList': []}
        self.txDiagfilePathDict: dict                    = {'filePathList': []}
        self.protocolPathDict: dict                      = {'protocolPathTypeDictList': []}
        self.acceptedProtocolPathDict: dict              = {
            'emptyProtList': [],
            'errorProtList': [],
            'abbortCritProtList': [],
            'limitExceededProtList': [],
        }
        self.filteredProtocolPathDict: dict              = {'protocolPathList': []}
        self.parsedProtDict: dict                        = {'protocolPathTypeDictList': []}
        self.protToBeParsedDict: dict                    = {'protocolPathTypeDictList': []}
        self.sysDiagParsedDataDict: dict                 = {'parsedDataList': []}
        self.separatePtu2ParsedDataDict: dict            = {'parsedDataList': []}
        self.separatePtu2FailedDataDict: dict            = {'parsedDataList': []}
        self.txAntDiagParsedDataDict: dict               = {'parsedDataList': []}
        self.separateTxAntDiagParsedDataDict: dict       = {'parsedDataList': []}
        self.separateTxAntDiagFailedDataDict: dict       = {'parsedDataList': []}
        self.burnInProtocolPathDict: dict                = {'protocolPathList': []}
        self.calProtocolPathDict: dict                   = {'protocolPathList': []}

        # Protocol limits parsing results
        self.burnInParsedProtDict: dict  = {'protocolParsingDictList': []}
        self.burnInFailedProtDict: dict  = {'protocolParsingDictList': []}
        self.calParsedProtDict: dict     = {'protocolParsingDictList': []}
        self.calFailedProtDict: dict     = {'protocolParsingDictList': []}

        # Limit rows (one per unique limit name, per protocol type)
        self.limitsRowListDict: dict = {'limitsRowList': []}

        # Limit groups
        self.burnInLimitsGroupDict: dict = {
            'limitsGroupList':  [],
            'activeGroupIndex': -1,
            'savedGroupIndex':  0,
        }
        self.calLimitsGroupDict: dict = {
            'limitsGroupList':  [],
            'activeGroupIndex': -1,
            'savedGroupIndex':  0,
        }

        # Loggers
        self._log = logconfig.mainLoadDataLogger.logger

    # ------------------------------------------------------------------
    # Protocol-type detection
    # ------------------------------------------------------------------

    def get_protocol_type(
        self,
        protocol_path: str,
        burn_in_cal_mode: int,
        include_burn_in_start: bool,
    ) -> str:
        """Determine whether a single protocol file is BurnIn, Calibration, or Unclear.

        Args:
            protocol_path:       Absolute path of the protocol .txt file.
            burn_in_cal_mode:    0 = auto-detect, 1 = force BurnIn, 2 = force Calibration
                                 (mirrors the radio-button id in the GUI).
            include_burn_in_start: When True, include protocols that contain a
                                   BurnIn-start check result (i.e. do not filter them out).

        Returns:
            One of ``'BurnIn'``, ``'Calibration'``, or ``'Unclear'``.
        """
        if burn_in_cal_mode == 1:
            return 'BurnIn'
        if burn_in_cal_mode == 2:
            return 'Calibration'

        # Auto-detect (mode 0)
        TYPE_MUSTER   = 'Gen26_UseBurnInMeas[1]'
        FILTER_MUSTER = '(12a) BurnIn Start Check results:'
        prot_type     = 'Unclear'
        filter_prot   = False

        try:
            with open(protocol_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith(TYPE_MUSTER):
                        line = line.replace(' ', '')
                        parts = line.split(';')
                        if parts[0] == TYPE_MUSTER and len(parts) > 1:
                            if sp.checkInt(parts[1]):
                                val = int(parts[1])
                                if val == 0:
                                    prot_type = 'Calibration'
                                elif val == 3:
                                    prot_type = 'BurnIn'
                                else:
                                    prot_type = 'Unclear'
                            else:
                                self._log.error(
                                    f'Invalid BurnIn/Cal auto-detection value: {parts[1]}'
                                )
                    if line.startswith(FILTER_MUSTER):
                        filter_prot = True
                        break
        except Exception as exc:
            self._log.error(f'Opening protocol file: {exc}')
            return 'Unclear'

        # BurnIn-start filtering: drop BurnIn-start protocols unless explicitly included
        if not include_burn_in_start and prot_type == 'BurnIn' and filter_prot:
            return 'Filtered'

        return prot_type

    def build_prot_path_type_list(
        self,
        protocol_path_list: list[str],
        burn_in_cal_mode: int,
        include_burn_in_start: bool,
    ) -> list[dict]:
        """Return a list of ``{'protocolPath': ..., 'type': ...}`` dicts.

        Protocols whose type resolves to ``'Filtered'`` are silently dropped.
        """
        result = []
        for path in protocol_path_list:
            ptype = self.get_protocol_type(path, burn_in_cal_mode, include_burn_in_start)
            if ptype != 'Filtered':
                result.append({'protocolPath': path, 'type': ptype})
        return result

    # ------------------------------------------------------------------
    # PTU-2 file parsing
    # ------------------------------------------------------------------

    def parse_ptu2_files(
        self,
        ptu2_files_list: list[str],
        use_sensor_muster: int,
        sensor_muster_list: list,
    ) -> tuple[list, list]:
        """Parse a list of PTU-2 file paths.

        Returns:
            (parsed_list, failed_list) — both are lists of parser objects.
        """
        parsed: list = []
        failed: list = []
        for path in ptu2_files_list:
            self._log.info(path)
            parser = ParserFactory.create('ptu2')
            parser.parseFile(path, use_sensor_muster, sensor_muster_list)
            if parser.bDataValid:
                parsed.append(parser)
            else:
                failed.append(parser)
        return parsed, failed

    def add_ptu2_to_state(
        self,
        parsed_list: list,
        failed_list: list,
    ) -> None:
        """Merge parsed/failed PTU-2 results into the controller's state dicts.

        De-duplicates by ``fileTitle.fileNamePath`` before inserting.
        """
        for item in failed_list:
            if not any(
                item.fileTitle.fileNamePath == e.fileTitle.fileNamePath
                for e in self.separatePtu2FailedDataDict['parsedDataList']
            ):
                self.separatePtu2FailedDataDict['parsedDataList'].append(item)

        for item in parsed_list:
            if not any(
                item.fileTitle.fileNamePath == e.fileTitle.fileNamePath
                for e in self.separatePtu2ParsedDataDict['parsedDataList']
            ):
                self.separatePtu2ParsedDataDict['parsedDataList'].append(item)
            if not any(
                item.fileTitle.fileNamePath == e.fileTitle.fileNamePath
                for e in self.sysDiagParsedDataDict['parsedDataList']
            ):
                self.sysDiagParsedDataDict['parsedDataList'].append(item)

    # ------------------------------------------------------------------
    # TxAntDiag file parsing
    # ------------------------------------------------------------------

    def parse_tx_ant_diag_files(
        self,
        tx_ant_diag_files_list: list[str],
        use_sensor_muster: int,
        sensor_muster_list: list,
    ) -> tuple[list, list]:
        """Parse a list of TxAntDiag file paths.

        Returns:
            (parsed_list, failed_list) — both are lists of parser objects.
        """
        parsed: list = []
        failed: list = []
        for path in tx_ant_diag_files_list:
            self._log.info(path)
            parser = ParserFactory.create('txantdiag')
            parser.parseFile(path, use_sensor_muster, sensor_muster_list)
            if parser.bDataValid:
                parsed.append(parser)
            else:
                failed.append(parser)
        return parsed, failed

    def add_tx_ant_diag_to_state(
        self,
        parsed_list: list,
        failed_list: list,
    ) -> None:
        """Merge parsed/failed TxAntDiag results into the controller's state dicts.

        De-duplicates by ``fileTitle.fileNamePath`` before inserting.
        """
        for item in failed_list:
            if not any(
                item.fileTitle.fileNamePath == e.fileTitle.fileNamePath
                for e in self.separateTxAntDiagFailedDataDict['parsedDataList']
            ):
                self.separateTxAntDiagFailedDataDict['parsedDataList'].append(item)

        for item in parsed_list:
            if not any(
                item.fileTitle.fileNamePath == e.fileTitle.fileNamePath
                for e in self.separateTxAntDiagParsedDataDict['parsedDataList']
            ):
                self.separateTxAntDiagParsedDataDict['parsedDataList'].append(item)
            if not any(
                item.fileTitle.fileNamePath == e.fileTitle.fileNamePath
                for e in self.txAntDiagParsedDataDict['parsedDataList']
            ):
                self.txAntDiagParsedDataDict['parsedDataList'].append(item)

    # ------------------------------------------------------------------
    # State reset
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # Protocol limits parsing
    # ------------------------------------------------------------------

    def parse_protocol_limits(
        self,
        burn_in_limits_path: str,
        cal_limits_path: str,
        include_burn_in: bool,
        include_cal: bool,
        extend_burn_in: bool,
        extend_cal: bool,
    ) -> None:
        """Parse the MeasurementLimits section of each protocol and evaluate against
        the supplied YAML limit files.

        Ported from statistic.py ``parseStatsProtocols`` (PST original project).
        Populates burnInParsedProtDict / burnInFailedProtDict (BurnIn protocols)
        and calParsedProtDict / calFailedProtDict (Calibration protocols).
        Only protocols not already present in those dicts are processed.

        Args:
            burn_in_limits_path: Path to BurnInLimits.yaml.
            cal_limits_path:     Path to CalLimits.yaml.
            include_burn_in:     Process BurnIn-type protocols.
            include_cal:         Process Calibration-type protocols.
            extend_burn_in:      Extend the BurnIn limits dict and re-save the YAML.
            extend_cal:          Extend the Cal limits dict and re-save the YAML.
        """
        already_parsed = {
            d['protocolPath']
            for d in (
                self.burnInParsedProtDict['protocolParsingDictList']
                + self.burnInFailedProtDict['protocolParsingDictList']
                + self.calParsedProtDict['protocolParsingDictList']
                + self.calFailedProtDict['protocolParsingDictList']
            )
        }

        for prot_dict in self.protToBeParsedDict['protocolPathTypeDictList']:
            protocol_path = prot_dict['protocolPath']
            prot_type     = prot_dict['type']

            if protocol_path in already_parsed:
                continue

            if prot_type == 'BurnIn' and include_burn_in:
                if not burn_in_limits_path or burn_in_limits_path == 'No file set.':
                    self._log.error('BurnIn limits file path not set.')
                    continue

                pp = ParseProtocols(ProtocolType.BurnIn)
                pp.loadProtocolParseInputDictYAML(burn_in_limits_path)
                if pp.errorStatus in (ErrorStatusEnum.Error, 1):
                    self.burnInFailedProtDict['protocolParsingDictList'].append(
                        {'protocolPath': protocol_path, 'type': prot_type,
                         'parsing': 'BurnIn', 'parsedData': pp}
                    )
                    self._log.warning(f'BurnIn limits YAML load failed: {protocol_path}')
                    continue
                pp.rawParseProtocols([ProtocolCategoriesEnum.MeasurementLimits], protocol_path)
                pp.rawParseProtocols([ProtocolCategoriesEnum.ProtocolHead], protocol_path)

                if extend_burn_in:
                    pp.extendInputMeasurementLimitDict()
                    pp.generateInputFilteredMeasurementLimit(pp.extInputMeasurementLimitDict)
                    pp.inputFilteredMeasurementLimitDict, pp.inputFilteredMeasurementLimit = \
                        pp.generateMeasurmentLimitDict(pp.inputFilteredMeasurementLimit, pp.protocolParseInputDict)
                    pp.rawParsedProtocolHead = pp.generateMeasurmentLimitDictHeaders(
                        pp.rawParsedProtocolHead, pp.protocolParseInputDict)
                    pp.saveProtocolParseInputDictYAML(pp.extInputMeasurementLimitDict, burn_in_limits_path)
                else:
                    pp.generateInputFilteredMeasurementLimit(pp.protocolParseInputDict)
                    pp.inputFilteredMeasurementLimitDict, pp.inputFilteredMeasurementLimit = \
                        pp.generateMeasurmentLimitDict(pp.inputFilteredMeasurementLimit, pp.protocolParseInputDict)
                    pp.rawParsedProtocolHead = pp.generateMeasurmentLimitDictHeaders(
                        pp.rawParsedProtocolHead, pp.protocolParseInputDict)

                result = {'protocolPath': protocol_path, 'type': prot_type,
                          'parsing': 'BurnIn', 'parsedData': pp}
                is_error = pp.errorStatus in (ErrorStatusEnum.Error, 1)
                if is_error:
                    self.burnInFailedProtDict['protocolParsingDictList'].append(result)
                    self._log.warning(f'BurnIn limits parsing failed: {protocol_path}')
                else:
                    self.burnInParsedProtDict['protocolParsingDictList'].append(result)
                    self._log.info(f'BurnIn limits parsing succeeded: {protocol_path}')

            elif prot_type == 'Calibration' and include_cal:
                if not cal_limits_path or cal_limits_path == 'No file set.':
                    self._log.error('Calibration limits file path not set.')
                    continue

                pp = ParseProtocols(ProtocolType.Calibration)
                pp.loadProtocolParseInputDictYAML(cal_limits_path)
                if pp.errorStatus in (ErrorStatusEnum.Error, 1):
                    self.calFailedProtDict['protocolParsingDictList'].append(
                        {'protocolPath': protocol_path, 'type': prot_type,
                         'parsing': 'Calibration', 'parsedData': pp}
                    )
                    self._log.warning(f'Calibration limits YAML load failed: {protocol_path}')
                    continue
                pp.rawParseProtocols([ProtocolCategoriesEnum.MeasurementLimits], protocol_path)
                pp.rawParseProtocols([ProtocolCategoriesEnum.ProtocolHead], protocol_path)

                if extend_cal:
                    pp.extendInputMeasurementLimitDict()
                    pp.generateInputFilteredMeasurementLimit(pp.extInputMeasurementLimitDict)
                    pp.inputFilteredMeasurementLimitDict, pp.inputFilteredMeasurementLimit = \
                        pp.generateMeasurmentLimitDict(pp.inputFilteredMeasurementLimit, pp.protocolParseInputDict)
                    pp.rawParsedProtocolHead = pp.generateMeasurmentLimitDictHeaders(
                        pp.rawParsedProtocolHead, pp.protocolParseInputDict)
                    pp.saveProtocolParseInputDictYAML(pp.extInputMeasurementLimitDict, cal_limits_path)
                else:
                    pp.generateInputFilteredMeasurementLimit(pp.protocolParseInputDict)
                    pp.inputFilteredMeasurementLimitDict, pp.inputFilteredMeasurementLimit = \
                        pp.generateMeasurmentLimitDict(pp.inputFilteredMeasurementLimit, pp.protocolParseInputDict)
                    pp.rawParsedProtocolHead = pp.generateMeasurmentLimitDictHeaders(
                        pp.rawParsedProtocolHead, pp.protocolParseInputDict)

                result = {'protocolPath': protocol_path, 'type': prot_type,
                          'parsing': 'Calibration', 'parsedData': pp}
                is_error = pp.errorStatus in (ErrorStatusEnum.Error, 1)
                if is_error:
                    self.calFailedProtDict['protocolParsingDictList'].append(result)
                    self._log.warning(f'Calibration limits parsing failed: {protocol_path}')
                else:
                    self.calParsedProtDict['protocolParsingDictList'].append(result)
                    self._log.info(f'Calibration limits parsing succeeded: {protocol_path}')

    # ------------------------------------------------------------------
    # Limits row + group building
    # ------------------------------------------------------------------

    def build_limits_rows(self) -> None:
        """Build a flat list of LimitsRow objects from already-parsed protocol limits.

        Each unique limit name found in the parsed protocol data gets one
        LimitsRow entry (with only limitName and protType populated).
        Statistics fields (mean, Cg, stDev …) are left at their zero defaults
        and can be filled in by a dedicated statistics step later.

        The result is stored in ``self.limitsRowListDict['limitsRowList']``.
        This list is then consumed by ``build_limits_groups()``.
        """
        rows: list[LimitsRow] = []
        seen: set[tuple[str, str]] = set()   # (limitName, protType) de-dup

        for prot_type, parsed_dict in (
            ('BurnIn',      self.burnInParsedProtDict),
            ('Calibration', self.calParsedProtDict),
        ):
            for entry in parsed_dict['protocolParsingDictList']:
                pp = entry['parsedData']   # ParseProtocols instance

                names: list[str] = []

                # From rawParsedProtocolHead (dict of name → value list)
                if hasattr(pp, 'rawParsedProtocolHead') and pp.rawParsedProtocolHead:
                    for header_name in pp.rawParsedProtocolHead:
                        names.append(header_name)

                # From inputFilteredMeasurementLimit (has .limitsList)
                if (
                    hasattr(pp, 'inputFilteredMeasurementLimit')
                    and pp.inputFilteredMeasurementLimit is not None
                    and hasattr(pp.inputFilteredMeasurementLimit, 'limitsList')
                ):
                    for limit in pp.inputFilteredMeasurementLimit.limitsList:
                        if limit.name:
                            names.append(limit.name)

                for name in names:
                    key = (name, prot_type)
                    if key not in seen:
                        seen.add(key)
                        row = LimitsRow()
                        row.limitName = name
                        row.protType  = prot_type
                        rows.append(row)

        self.limitsRowListDict['limitsRowList'] = rows
        self._log.info(
            f'build_limits_rows: {len(rows)} limit rows '
            f'({sum(1 for r in rows if r.protType == "BurnIn")} BurnIn, '
            f'{sum(1 for r in rows if r.protType == "Calibration")} Cal)'
        )

    def build_limits_groups(
        self,
        burn_in_lim_groups_path: str,
        cal_lim_groups_path: str,
        include_burn_in: bool,
        include_cal: bool,
        extend_burn_in_groups: bool,
        extend_cal_groups: bool,
    ) -> None:
        """Build limits group lists from YAML config and the current limitsRowListDict.

        Must be called after ``build_limits_rows()`` (or after
        ``parse_protocol_limits()`` which is itself called first).

        Populates ``self.burnInLimitsGroupDict['limitsGroupList']``
        and ``self.calLimitsGroupDict['limitsGroupList']``.

        Args:
            burn_in_lim_groups_path: Path to BurnInLimGroups.yaml.
            cal_lim_groups_path:     Path to CalLimGroups.yaml.
            include_burn_in:         Process BurnIn groups.
            include_cal:             Process Calibration groups.
            extend_burn_in_groups:   Extend BurnIn groups YAML with auto-detected names.
            extend_cal_groups:       Extend Cal groups YAML with auto-detected names.
        """
        rows = self.limitsRowListDict['limitsRowList']

        burn_in_group_names: list[str] = []
        cal_group_names:     list[str] = []

        for row in rows:
            limit_name = row.limitName.split('[')[0]   # strip array index suffix

            if limit_name.lower().endswith('rs485'):
                group_name = limit_name
                suffix     = 'special'
            else:
                m = re.match(r'(.*\D)?(\d*)$', limit_name, re.I)
                group_name, suffix = m.groups() if m else (limit_name, '')
                group_name = group_name or limit_name

            if include_burn_in and row.protType == 'BurnIn':
                if group_name not in burn_in_group_names and suffix:
                    burn_in_group_names.append(group_name)

            if include_cal and row.protType == 'Calibration':
                if group_name not in cal_group_names and suffix:
                    cal_group_names.append(group_name)

        lim_groups_parser = ParseInputLimitsGroups()
        burn_in_groups_list: list[LimitsGroup] = []
        cal_groups_list:     list[LimitsGroup] = []

        # ---- BurnIn ----
        if include_burn_in and burn_in_group_names:
            if not burn_in_lim_groups_path or burn_in_lim_groups_path == 'No file set.':
                self._log.error('BurnIn limits groups file path not set.')
            else:
                burn_in_group_name_dicts = self._make_group_name_dicts(
                    burn_in_group_names, rows, 'BurnIn'
                )
                lim_groups_parser.loadBurnInInputLimitsGroupsDictYAML(burn_in_lim_groups_path)

                if lim_groups_parser.burnInErrorStatus != 1:
                    if extend_burn_in_groups:
                        lim_groups_parser.extendBurnInInputLimitsGroupsDict(burn_in_group_name_dicts)
                        if lim_groups_parser.burnInErrorStatus != 1:
                            lim_groups_parser.saveLimitsGroupsDictYAML(
                                lim_groups_parser.burnInExtInputLimitsGroupsDict,
                                burn_in_lim_groups_path,
                            )
                        input_dict = lim_groups_parser.burnInExtInputLimitsGroupsDict
                    else:
                        input_dict = lim_groups_parser.burnInInputLimitsGroupsDict

                    burn_in_groups_list = self._build_group_objects(
                        input_dict, rows, 'BurnIn'
                    )

        # ---- Calibration ----
        if include_cal and cal_group_names:
            if not cal_lim_groups_path or cal_lim_groups_path == 'No file set.':
                self._log.error('Calibration limits groups file path not set.')
            else:
                cal_group_name_dicts = self._make_group_name_dicts(
                    cal_group_names, rows, 'Calibration'
                )
                lim_groups_parser.loadCalInputLimitsGroupsDictYAML(cal_lim_groups_path)

                if lim_groups_parser.calErrorStatus != 1:
                    if extend_cal_groups:
                        lim_groups_parser.extendCalInputLimitsGroupsDict(cal_group_name_dicts)
                        if lim_groups_parser.calErrorStatus != 1:
                            lim_groups_parser.saveLimitsGroupsDictYAML(
                                lim_groups_parser.calExtInputLimitsGroupsDict,
                                cal_lim_groups_path,
                            )
                        input_dict = lim_groups_parser.calExtInputLimitsGroupsDict
                    else:
                        input_dict = lim_groups_parser.calInputLimitsGroupsDict

                    cal_groups_list = self._build_group_objects(
                        input_dict, rows, 'Calibration'
                    )

        self.burnInLimitsGroupDict['limitsGroupList']  = burn_in_groups_list
        self.calLimitsGroupDict['limitsGroupList']     = cal_groups_list
        # Reset navigation indices whenever the group list is rebuilt
        self.burnInLimitsGroupDict['activeGroupIndex'] = -1
        self.calLimitsGroupDict['activeGroupIndex']    = -1

        self._log.info(
            f'build_limits_groups: {len(burn_in_groups_list)} BurnIn groups, '
            f'{len(cal_groups_list)} Cal groups'
        )

    @staticmethod
    def _make_group_name_dicts(
        group_names: list[str],
        rows: list,
        prot_type: str,
    ) -> list[dict]:
        """Build the groupNameDictList needed by ParseInputLimitsGroups.extend*."""
        result = []
        for group_name in group_names:
            exact_matches = [
                r.limitName for r in rows
                if group_name in r.limitName and r.protType == prot_type
            ]
            result.append({
                'groupName': group_name,
                'Limits': {'ExactMatch': exact_matches, 'Contains': []},
            })
        return result

    @staticmethod
    def _build_group_objects(
        input_dict: dict,
        rows: list,
        prot_type: str,
    ) -> 'list[LimitsGroup]':
        """Convert a loaded/extended YAML group dict into LimitsGroup objects."""
        groups: list[LimitsGroup] = []
        if not input_dict:
            return groups

        for group_name, group_dict in input_dict.items():
            lim_dict       = group_dict.get('Limits', {})
            exact_matches  = lim_dict.get('ExactMatch', [])
            contains_items = lim_dict.get('Contains', [])

            group = LimitsGroup()
            group.name     = group_name
            group.protType = prot_type

            for exact in exact_matches:
                for row in rows:
                    if row.limitName == exact and row.protType == prot_type:
                        group.limitsRowMatchDictList.append({'row': row, 'match': 'ExactMatch'})

            for contains in contains_items:
                for row in rows:
                    if contains in row.limitName and row.protType == prot_type:
                        group.limitsRowMatchDictList.append({'row': row, 'match': 'Contains'})

            if group.limitsRowMatchDictList:
                groups.append(group)

        return groups

    # ------------------------------------------------------------------
    # Statistics computation
    # ------------------------------------------------------------------

    def compute_limits_stats(self) -> None:
        """Compute statistics for each LimitsRow in limitsRowListDict.

        Must be called after ``build_limits_rows()``.  Fills in:
        ``mean``, ``min``, ``max``, ``stDev``, ``maxDev``,
        ``upperLimit``, ``lowerLimit``, ``cg``, ``error``, ``index``
        on every :class:`LimitsRow`.
        """
        rows = self.limitsRowListDict['limitsRowList']

        for idx, row in enumerate(rows):
            row.index = idx

            parsed_dict = (
                self.burnInParsedProtDict
                if row.protType == 'BurnIn'
                else self.calParsedProtDict
            )
            parsed_list = [e['parsedData'] for e in parsed_dict['protocolParsingDictList']]

            if not parsed_list:
                row.error = {2: 'No actual values available.'}
                continue

            limit_name  = row.limitName
            error_dict: dict = {}

            # ---- collect actual measurement values -------------------------
            actual_vals: list[float] = []
            for pp in parsed_list:
                if (
                    hasattr(pp, 'inputFilteredMeasurementLimit')
                    and pp.inputFilteredMeasurementLimit is not None
                    and hasattr(pp.inputFilteredMeasurementLimit, 'limitsList')
                ):
                    for lim in pp.inputFilteredMeasurementLimit.limitsList:
                        if lim.name == limit_name and getattr(lim, 'valueFound', 0) == 1:
                            actual_vals.append(float(lim.value))

                if hasattr(pp, 'rawParsedProtocolHead') and pp.rawParsedProtocolHead:
                    for hdr, hvals in pp.rawParsedProtocolHead.items():
                        if hdr == limit_name:
                            for v in hvals:
                                if sp.checkInt(str(v)) or sp.checkDecimal(str(v)):
                                    actual_vals.append(float(v))
                            break

            if not actual_vals:
                row.error = {2: 'No actual values available.'}
                continue

            n          = len(actual_vals)
            row.mean   = round(sum(actual_vals) / n, 6)
            row.min    = round(min(actual_vals), 6)
            row.max    = round(max(actual_vals), 6)
            row.maxDev = round(max(abs(v - row.mean) for v in actual_vals), 6)

            if n >= 2:
                var      = sum((v - row.mean) ** 2 for v in actual_vals) / (n - 1)
                row.stDev = round(math.sqrt(var), 6)
            else:
                row.stDev = 0.0
                error_dict[13] = 'Insufficient values for StdDev.'

            # ---- collect limit bounds (min/max from limitsList) ------------
            lo_vals: list[float] = []
            hi_vals: list[float] = []
            for pp in parsed_list:
                if (
                    hasattr(pp, 'inputFilteredMeasurementLimit')
                    and pp.inputFilteredMeasurementLimit is not None
                    and hasattr(pp.inputFilteredMeasurementLimit, 'limitsList')
                ):
                    for lim in pp.inputFilteredMeasurementLimit.limitsList:
                        if lim.name == limit_name and getattr(lim, 'valueFound', 0) == 1:
                            lo_vals.append(float(lim.min))
                            hi_vals.append(float(lim.max))

            row.lowerLimit = round(min(lo_vals), 6) if lo_vals else 0.0
            row.upperLimit = round(max(hi_vals), 6) if hi_vals else 0.0

            # ---- Cg -------------------------------------------------------
            tol = abs(row.upperLimit - row.lowerLimit)
            if tol > 1e-12 and row.stDev > 1e-12:
                row.cg = round(min(tol / 20.0 / row.stDev, 1000.0), 6)
            else:
                row.cg = 0.0
                if tol <= 1e-12:
                    error_dict[14] = 'Cg calc error: zero tolerance span.'

            row.error = error_dict

        self._log.info(f'compute_limits_stats: processed {len(rows)} limit rows')

    # ------------------------------------------------------------------
    # State reset
    # ------------------------------------------------------------------

    def clear_state(self) -> None:
        """Reset all state dicts to their initial empty values.

        Does NOT touch any Qt widgets — the caller is responsible for
        updating the UI after this call.
        """
        self.protocolPathDict['protocolPathTypeDictList']      = []
        self.sysDiagFilePathDict['filePathList']               = []
        self.txDiagfilePathDict['filePathList']                = []
        self.parsedProtDict['protocolPathTypeDictList']        = []
        self.protToBeParsedDict['protocolPathTypeDictList']    = []
        self.filteredProtocolPathDict['protocolPathList']      = []

        self.sysDiagParsedDataDict['parsedDataList']           = []
        self.separatePtu2ParsedDataDict['parsedDataList']      = []
        self.separatePtu2FailedDataDict['parsedDataList']      = []

        self.txAntDiagParsedDataDict['parsedDataList']         = []
        self.separateTxAntDiagParsedDataDict['parsedDataList'] = []
        self.separateTxAntDiagFailedDataDict['parsedDataList'] = []

        self.acceptedProtocolPathDict['emptyProtList']         = []
        self.acceptedProtocolPathDict['errorProtList']         = []
        self.acceptedProtocolPathDict['abbortCritProtList']    = []
        self.acceptedProtocolPathDict['limitExceededProtList'] = []

        self.burnInParsedProtDict['protocolParsingDictList']   = []
        self.burnInFailedProtDict['protocolParsingDictList']   = []
        self.calParsedProtDict['protocolParsingDictList']      = []
        self.calFailedProtDict['protocolParsingDictList']      = []

        self.limitsRowListDict['limitsRowList']                 = []

        self.burnInLimitsGroupDict['limitsGroupList']           = []
        self.burnInLimitsGroupDict['activeGroupIndex']          = -1
        self.burnInLimitsGroupDict['savedGroupIndex']           = 0

        self.calLimitsGroupDict['limitsGroupList']              = []
        self.calLimitsGroupDict['activeGroupIndex']             = -1
        self.calLimitsGroupDict['savedGroupIndex']              = 0

        self._log.info('Loaded and Parsed Data cleared.')

    # ------------------------------------------------------------------
    # Convenience accessors (for View / main.py)
    # ------------------------------------------------------------------

    def ptu2_parsed_count(self) -> int:
        return len(self.separatePtu2ParsedDataDict['parsedDataList'])

    def ptu2_failed_count(self) -> int:
        return len(self.separatePtu2FailedDataDict['parsedDataList'])

    def tx_ant_diag_parsed_count(self) -> int:
        return len(self.separateTxAntDiagParsedDataDict['parsedDataList'])

    def tx_ant_diag_failed_count(self) -> int:
        return len(self.separateTxAntDiagFailedDataDict['parsedDataList'])

    def sys_diag_parsed_count(self) -> int:
        return len(self.sysDiagParsedDataDict['parsedDataList'])

    def protocol_count(self) -> int:
        return len(self.protocolPathDict['protocolPathTypeDictList'])

    def parsed_protocol_count(self) -> int:
        return len(self.parsedProtDict['protocolPathTypeDictList'])

    def to_be_parsed_count(self) -> int:
        return len(self.protToBeParsedDict['protocolPathTypeDictList'])
