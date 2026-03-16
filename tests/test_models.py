"""
Tests for shared/models.py — PST-44: Extract Models from shared.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

from shared.models import (
    ImportedProtcolsData,
    ProtocolData,
    PTU2Data,
    TxAntDiagData,
    ProtocolsTableData,
    GraphData,
)


# ---------------------------------------------------------------------------
# Simple container models
# ---------------------------------------------------------------------------

class TestImportedProtcolsData:
    def test_defaults(self):
        obj = ImportedProtcolsData()
        assert obj.protocolDataList == []

    def test_mutable_default_is_per_instance(self):
        a = ImportedProtcolsData()
        b = ImportedProtcolsData()
        a.protocolDataList.append('item')
        assert b.protocolDataList == []


class TestProtocolData:
    def test_defaults(self):
        obj = ProtocolData()
        assert obj.protocolPath == ''
        assert obj.ptu2DataList == []
        assert obj.txAntDiagDataList == []


class TestPTU2Data:
    def test_defaults(self):
        obj = PTU2Data()
        assert obj.filesList == []
        assert obj.protocolPath == ''


class TestTxAntDiagData:
    def test_defaults(self):
        obj = TxAntDiagData()
        assert obj.filesList == []
        assert obj.protocolPath == ''


class TestGraphData:
    def test_defaults(self):
        gd = GraphData()
        assert gd.graphTitle == ''
        assert gd.txAnt == 0
        assert gd.rxCh == 0
        assert gd.sensorId == ''
        assert gd.diagramNr == 0
        assert gd.figureTitle == ''
        assert gd.figureTitle3graph == ''
        assert gd.antennaType == ''
        assert gd.nofRxCh == 0
        assert gd.seqNum == 0
        assert gd.dateAndTime == ''
        assert gd.frequency == 0
        assert gd.phyDoppGenDist == 0
        assert gd.doppGenHeightPtuZero == 0
        assert gd.rfBoardMidHeightPtuZero == 0
        assert gd.sensorUpsideDown == 0
        assert gd.antennaDiagramType == ''
        assert gd.oppositeToPanAngle == 0

    def test_assignment(self):
        gd = GraphData()
        gd.graphTitle = 'level'
        gd.txAnt = 1
        assert gd.graphTitle == 'level'
        assert gd.txAnt == 1


# ---------------------------------------------------------------------------
# ProtocolsTableData — layout logic
# ---------------------------------------------------------------------------

class TestProtocolsTableData:
    def test_empty_both_lists(self):
        td = ProtocolsTableData('path', [], [])
        assert td.biggerListLength == 0
        assert td.sysDiagFilePathShapedList == []
        assert td.txAntDiagFilePathShapedList == []
        # When txAntDiag is empty, one span entry with spanCount=0 is added
        assert len(td.smallerListRowSpanList) == 1
        assert td.smallerListRowSpanList[0]['spanCount'] == 0

    def test_sys_diag_only(self):
        """Only sysDiag files, no txAntDiag files."""
        td = ProtocolsTableData('path', ['a', 'b', 'c'], [])
        assert td.biggerListLength == 3
        assert td.smallerListColIdx == 3
        assert len(td.sysDiagFilePathShapedList) == 3
        assert td.txAntDiagFilePathShapedList == ['', '', '']
        assert td.smallerListRowSpanList[0]['spanCount'] == 3

    def test_tx_ant_diag_only(self):
        """Only txAntDiag files, no sysDiag files."""
        td = ProtocolsTableData('path', [], ['x', 'y'])
        assert td.biggerListLength == 2
        assert td.smallerListColIdx == 2
        assert len(td.txAntDiagFilePathShapedList) == 2
        assert td.sysDiagFilePathShapedList == ['', '']
        assert td.smallerListRowSpanList[0]['spanCount'] == 2

    def test_equal_length_lists(self):
        """1:1 ratio — each sysDiag maps to one txAntDiag."""
        td = ProtocolsTableData('path', ['s0', 's1'], ['t0', 't1'])
        assert td.biggerListLength == 2
        assert td.smallerListColIdx == 3  # sysDiag is bigger-or-equal
        assert td.sysDiagFilePathShapedList == ['s0', 's1']
        # each txAntDiag entry maps to one row
        assert td.txAntDiagFilePathShapedList[0] == 't0'
        assert td.txAntDiagFilePathShapedList[1] == 't1'

    def test_more_sys_diag_than_tx_ant_diag(self):
        """2:1 ratio — 4 sysDiag, 2 txAntDiag."""
        td = ProtocolsTableData('path', ['s0', 's1', 's2', 's3'], ['t0', 't1'])
        assert td.biggerListLength == 4
        assert td.smallerListColIdx == 3
        assert len(td.smallerListRowSpanList) == 2
        assert td.smallerListRowSpanList[0]['spanCount'] == 2
        assert td.smallerListRowSpanList[1]['spanCount'] == 2

    def test_more_tx_ant_diag_than_sys_diag(self):
        """2:1 ratio — 4 txAntDiag, 2 sysDiag."""
        td = ProtocolsTableData('path', ['s0', 's1'], ['t0', 't1', 't2', 't3'])
        assert td.biggerListLength == 4
        assert td.smallerListColIdx == 2
        assert len(td.smallerListRowSpanList) == 2
        assert td.smallerListRowSpanList[0]['spanCount'] == 2

    def test_protocol_path_stored(self):
        td = ProtocolsTableData('/some/path', [], [])
        assert td.protocolPath == '/some/path'

    def test_re_export_from_data_processing(self):
        """Verify backward-compat re-export: dp.ProtocolsTableData still works."""
        import data_processing as dp
        td = dp.ProtocolsTableData('p', [], [])
        assert isinstance(td, ProtocolsTableData)
