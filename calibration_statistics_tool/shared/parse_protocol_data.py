from __future__ import annotations

from calibration_statistics_tool.shared.parser_base import ParseDataBase
from calibration_statistics_tool.shared.parseProtocols import (
    ParseProtocols,
    ProtocolType,
    ProtocolCategoriesEnum,
)


def _detect_protocol_type(fileNamePath: str) -> ProtocolType:
    """Infer BurnIn vs Calibration from the filename, defaulting to Calibration."""
    return ProtocolType.BurnIn if 'BurnIn' in fileNamePath else ProtocolType.Calibration


class ProtocolParseData(ParseDataBase):
    """ParseDataBase adapter for calibration/burn-in protocol text files.

    Wraps ParseProtocols.rawParseProtocols so that protocol files can be
    created and parsed through ParserFactory like any other format:

        parser = ParserFactory.create('protocol')
        parser.parseFile(path, 0, [])

    The protocol type (BurnIn / Calibration) is inferred from the filename.
    After a successful parse, rawParsedProtocolHead is populated and
    bDataValid is True.  On any exception, the message is appended to
    errorList and bDataValid remains False.
    """

    def __init__(self) -> None:
        super().__init__()
        self.protocolType: ProtocolType | None = None
        self.rawParsedProtocolHead: dict = {}

    def parseFile(self, fileNamePath: str, useSensorMuster: int, sensorMusterList: list) -> None:
        self.fileNamePath = fileNamePath
        self.errorList = []
        self.protocolType = _detect_protocol_type(fileNamePath)

        inner = ParseProtocols(self.protocolType)
        try:
            inner.rawParseProtocols(
                [ProtocolCategoriesEnum.ProtocolHead],
                fileNamePath,
            )
            self.rawParsedProtocolHead = inner.rawParsedProtocolHead
            self.errorList = inner.errorList
            self.bDataValid = len(self.errorList) == 0
        except Exception as exc:
            self.errorList.append(str(exc))
            self.bDataValid = False
