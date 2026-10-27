"""Domain model classes for the Calibration Statistics Tool.

Pure data containers extracted from data_processing.py and plotdata.py
as part of the MVC separation (PST-44).
"""
from __future__ import annotations


# ---------------------------------------------------------------------------
# Protocol / PTU data models (formerly in shared/data_processing.py)
# ---------------------------------------------------------------------------

class ImportedProtcolsData:
    def __init__(self) -> None:
        self.protocolDataList: list = []


class ProtocolData:
    def __init__(self) -> None:
        self.protocolPath: str = ''
        self.ptu2DataList: list = []
        self.txAntDiagDataList: list = []


class PTU2Data:
    def __init__(self) -> None:
        self.filesList: list = []
        self.protocolPath: str = ''


class TxAntDiagData:
    def __init__(self) -> None:
        self.filesList: list = []
        self.protocolPath: str = ''


class ProtocolsTableData:
    def __init__(self, protocolPath: str, sysDiagFilePathList: list, txAntDiagFilePathList: list) -> None:
        self.protocolPath = protocolPath
        self.sysDiagFilePathShapedList: list = []
        self.txAntDiagFilePathShapedList: list = []
        self.biggerListLength: int = 0
        self.smallerListLength: int = 0
        self.smallerListColIdx: int = 0
        self.smallerListRowSpanList: list = []

        if len(sysDiagFilePathList) >= len(txAntDiagFilePathList):
            if len(txAntDiagFilePathList) != 0:
                ratio = int(len(sysDiagFilePathList) / len(txAntDiagFilePathList))
                res = len(sysDiagFilePathList) % len(txAntDiagFilePathList)

                self.smallerListColIdx = 3
                self.biggerListLength = len(sysDiagFilePathList)
                self.smallerListLength = len(txAntDiagFilePathList)

                self.sysDiagFilePathShapedList = sysDiagFilePathList

                for sysDiagIdx in range(len(sysDiagFilePathList)):
                    entry = ''
                    for txAntDiagIdx in range(len(txAntDiagFilePathList)):
                        if ratio * txAntDiagIdx == sysDiagIdx:
                            entry = txAntDiagFilePathList[txAntDiagIdx]
                    self.txAntDiagFilePathShapedList.append(entry)

                size = 0
                for txAntDiagIdx in range(len(txAntDiagFilePathList)):
                    tempDict = {'spanStart': 0, 'spanCount': 0}
                    tempDict['spanStart'] = txAntDiagIdx * ratio
                    if txAntDiagIdx == len(txAntDiagFilePathList) - 1:
                        if res != 0:
                            tempDict['spanCount'] = self.biggerListLength - size
                        else:
                            tempDict['spanCount'] = ratio
                    else:
                        tempDict['spanCount'] = ratio
                        size = ratio * (txAntDiagIdx + 1)
                    self.smallerListRowSpanList.append(tempDict)
            else:
                self.smallerListColIdx = 3
                self.biggerListLength = len(sysDiagFilePathList)
                self.sysDiagFilePathShapedList = sysDiagFilePathList

                for _ in range(len(sysDiagFilePathList)):
                    self.txAntDiagFilePathShapedList.append('')

                self.smallerListRowSpanList.append({
                    'spanStart': 0,
                    'spanCount': self.biggerListLength,
                })
        else:
            if len(sysDiagFilePathList) != 0:
                ratio = int(len(txAntDiagFilePathList) / len(sysDiagFilePathList))
                res = len(txAntDiagFilePathList) % len(sysDiagFilePathList)

                self.smallerListColIdx = 2
                self.biggerListLength = len(txAntDiagFilePathList)
                self.smallerListLength = len(sysDiagFilePathList)

                self.txAntDiagFilePathShapedList = txAntDiagFilePathList

                for txAntDiagIdx in range(len(txAntDiagFilePathList)):
                    entry = ''
                    for sysDiagIdx in range(len(sysDiagFilePathList)):
                        if ratio * sysDiagIdx == txAntDiagIdx:
                            entry = sysDiagFilePathList[sysDiagIdx]
                    self.sysDiagFilePathShapedList.append(entry)

                size = 0
                for sysDiagIdx in range(len(sysDiagFilePathList)):
                    tempDict = {'spanStart': 0, 'spanCount': 0}
                    tempDict['spanStart'] = sysDiagIdx * ratio
                    if sysDiagIdx == len(sysDiagFilePathList) - 1:
                        if res != 0:
                            tempDict['spanCount'] = self.biggerListLength - size
                        else:
                            tempDict['spanCount'] = ratio
                    else:
                        tempDict['spanCount'] = ratio
                        size = ratio * (sysDiagIdx + 1)
                    self.smallerListRowSpanList.append(tempDict)
            else:
                self.smallerListColIdx = 2
                self.biggerListLength = len(txAntDiagFilePathList)
                self.txAntDiagFilePathShapedList = txAntDiagFilePathList

                for _ in range(len(txAntDiagFilePathList)):
                    self.sysDiagFilePathShapedList.append('')

                self.smallerListRowSpanList.append({
                    'spanStart': 0,
                    'spanCount': self.biggerListLength,
                })


# ---------------------------------------------------------------------------
# Graph / plot models (formerly in shared/plotdata.py)
# ---------------------------------------------------------------------------

class GraphData:
    def __init__(self) -> None:
        self.graphTitle:        str = ''
        self.txAnt:             int = 0
        self.rxCh:              int = 0
        self.sensorId:          str = ''
        self.diagramNr:         int = 0
        self.figureTitle:       str = ''
        self.figureTitle3graph: str = ''
        self.antennaType:       str = ''
        self.nofRxCh:           int = 0
        self.seqNum:            int = 0
        self.dateAndTime:       str = ''
        self.frequency:         int = 0

        self.phyDoppGenDist:          int = 0
        self.doppGenHeightPtuZero:    int = 0
        self.rfBoardMidHeightPtuZero: int = 0
        self.sensorUpsideDown:        int = 0
        self.antennaDiagramType:      str = ''
        self.oppositeToPanAngle:      int = 0
