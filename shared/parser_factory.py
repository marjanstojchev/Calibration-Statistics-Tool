from shared.parser_base import ParseDataBase
from shared import parsePTU2data
from shared import parseTxAntDiagramData
from shared.parse_protocol_data import ProtocolParseData


_REGISTRY: dict[str, type[ParseDataBase]] = {
    'ptu2':      parsePTU2data.PTU2ParseData,
    'txantdiag': parseTxAntDiagramData.TxAntDiagramParseData,
    'protocol':  ProtocolParseData,
}


class ParserFactory:
    """Creates parser instances by file-type key.

    Usage:
        parser = ParserFactory.create('ptu2')
        parser.parseFile(path, useSensorMuster, sensorMusterList)

    Raises ValueError for unknown keys, keeping errors explicit at the
    point of construction rather than surfacing as AttributeError later.
    """

    @staticmethod
    def create(file_type: str) -> ParseDataBase:
        cls = _REGISTRY.get(file_type)
        if cls is None:
            raise ValueError(
                f"Unknown parser type '{file_type}'. "
                f"Valid types: {sorted(_REGISTRY)}"
            )
        return cls()

    @staticmethod
    def register(file_type: str, cls: type[ParseDataBase]) -> None:
        """Register a new parser type at runtime (e.g. for plugins or tests)."""
        if not issubclass(cls, ParseDataBase):
            raise TypeError(f"{cls.__name__} must extend ParseDataBase")
        _REGISTRY[file_type] = cls
