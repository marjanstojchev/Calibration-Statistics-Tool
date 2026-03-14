from abc import ABC, abstractmethod


class ParseDataBase(ABC):
    """Abstract base class for all file parsers.

    Enforces a common interface across PTU2, TxAntDiagram, and any future
    parser types. Subclasses must implement parseFile(); the shared state
    fields (bDataValid, fileNamePath, errorList) are initialised here so
    concrete classes do not need to repeat them.
    """

    def __init__(self) -> None:
        self.bDataValid: bool = False
        self.fileNamePath: str = ''
        self.errorList: list = []

    @abstractmethod
    def parseFile(self, fileNamePath: str, useSensorMuster: int, sensorMusterList: list) -> None:
        """Parse the file at fileNamePath and populate this object's fields.

        Must set self.bDataValid = True on success, or append to
        self.errorList and leave self.bDataValid = False on failure.
        """
