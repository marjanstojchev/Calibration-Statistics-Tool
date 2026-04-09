"""
ParseController: Encapsulates all protocol, PTU, and TxAnt parsing logic and state.

All methods in this class are pure business logic — they do not call any Qt/GUI
code.  The GUI layer (main.py / PST-47) is responsible for reading UI state
(checkbox values, selected file paths) and for updating widgets after each
call.  This keeps the controller fully unit-testable without a running Qt app.

Part of MVC refactor (PST-45).
"""
from __future__ import annotations

from shared.parser_factory import ParserFactory
from shared import safeparse as sp
import logconfig


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
