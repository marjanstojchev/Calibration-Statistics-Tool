"""
Tests for shared/data_processing.py

Covers:
- Class initialization correctness (post __init__ fix)
- ProtocolsTableData list shaping logic (sysDiag > txAntDiag, sysDiag < txAntDiag, equal, empty)
"""
import os
import pytest

from calibration_statistics_tool.shared.data_processing import (
    ImportedProtcolsData,
    ProtocolData,
    PTU2Data,
    TxAntDiagData,
    ProtocolsTableData,
)


# ──────────────────────────────────────────────
# Class Initialization Tests
# ──────────────────────────────────────────────

class TestImportedProtcolsData:
    def test_init_creates_empty_list(self):
        obj = ImportedProtcolsData()
        assert hasattr(obj, 'protocolDataList')
        assert isinstance(obj.protocolDataList, list)
        assert len(obj.protocolDataList) == 0

    def test_instances_do_not_share_list(self):
        """Ensure separate instances have independent lists."""
        a = ImportedProtcolsData()
        b = ImportedProtcolsData()
        a.protocolDataList.append('item')
        assert len(b.protocolDataList) == 0


class TestProtocolData:
    def test_init_defaults(self):
        obj = ProtocolData()
        assert obj.protocolPath == ''
        assert isinstance(obj.ptu2DataList, list)
        assert isinstance(obj.txAntDiagDataList, list)
        assert len(obj.ptu2DataList) == 0
        assert len(obj.txAntDiagDataList) == 0

    def test_instances_do_not_share_lists(self):
        a = ProtocolData()
        b = ProtocolData()
        a.ptu2DataList.append('x')
        assert len(b.ptu2DataList) == 0


class TestPTU2Data:
    def test_init_defaults(self):
        obj = PTU2Data()
        assert isinstance(obj.filesList, list)
        assert len(obj.filesList) == 0
        assert obj.protocolPath == ''


class TestTxAntDiagData:
    def test_init_defaults(self):
        obj = TxAntDiagData()
        assert isinstance(obj.filesList, list)
        assert len(obj.filesList) == 0
        assert obj.protocolPath == ''


# ──────────────────────────────────────────────
# ProtocolsTableData Tests
# ──────────────────────────────────────────────

class TestProtocolsTableData:
    """
    ProtocolsTableData shapes two lists (sysDiag and txAntDiag) for table display.
    The shorter list gets row spans, the longer list gets one entry per row.
    """

    def test_equal_lists(self):
        """1:1 mapping - both lists same length."""
        sys_list  = ['s1', 's2', 's3']
        tx_list   = ['t1', 't2', 't3']
        td = ProtocolsTableData('proto.txt', sys_list, tx_list)

        assert td.biggerListLength == 3
        assert len(td.sysDiagFilePathShapedList) == 3
        assert len(td.txAntDiagFilePathShapedList) == 3

    def test_more_sys_diag_than_tx(self):
        """sysDiag list is longer - txAntDiag gets row spans."""
        sys_list = ['s1', 's2', 's3', 's4']
        tx_list  = ['t1', 't2']
        td = ProtocolsTableData('proto.txt', sys_list, tx_list)

        assert td.biggerListLength == 4
        assert td.smallerListLength == 2
        assert td.smallerListColIdx == 3          # txAntDiag is smaller → col 3
        assert len(td.sysDiagFilePathShapedList) == 4
        assert len(td.txAntDiagFilePathShapedList) == 4
        assert len(td.smallerListRowSpanList) == 2
        assert td.smallerListRowSpanList[0]['spanStart'] == 0
        assert td.smallerListRowSpanList[0]['spanCount'] == 2

    def test_more_tx_than_sys_diag(self):
        """txAntDiag list is longer - sysDiag gets row spans."""
        sys_list = ['s1', 's2']
        tx_list  = ['t1', 't2', 't3', 't4']
        td = ProtocolsTableData('proto.txt', sys_list, tx_list)

        assert td.biggerListLength == 4
        assert td.smallerListLength == 2
        assert td.smallerListColIdx == 2          # sysDiag is smaller → col 2
        assert len(td.txAntDiagFilePathShapedList) == 4
        assert len(td.sysDiagFilePathShapedList) == 4

    def test_empty_tx_list(self):
        """txAntDiag is empty - sysDiag fills the table, tx side is all empty strings."""
        sys_list = ['s1', 's2', 's3']
        tx_list  = []
        td = ProtocolsTableData('proto.txt', sys_list, tx_list)

        assert td.biggerListLength == 3
        assert len(td.sysDiagFilePathShapedList) == 3
        assert all(e == '' for e in td.txAntDiagFilePathShapedList)

    def test_empty_sys_list(self):
        """sysDiag is empty - txAntDiag fills the table, sys side is all empty strings."""
        sys_list = []
        tx_list  = ['t1', 't2']
        td = ProtocolsTableData('proto.txt', sys_list, tx_list)

        assert td.biggerListLength == 2
        assert len(td.txAntDiagFilePathShapedList) == 2
        assert all(e == '' for e in td.sysDiagFilePathShapedList)

    def test_both_empty(self):
        """Both lists empty - everything stays at zero."""
        td = ProtocolsTableData('proto.txt', [], [])
        assert td.biggerListLength == 0
        assert len(td.sysDiagFilePathShapedList) == 0
        assert len(td.txAntDiagFilePathShapedList) == 0

    def test_protocol_path_stored(self):
        td = ProtocolsTableData('my_protocol.txt', ['s1'], ['t1'])
        assert td.protocolPath == 'my_protocol.txt'

    def test_span_covers_full_range_with_remainder(self):
        """Last span should absorb remainder when lists don't divide evenly."""
        sys_list = ['s1', 's2', 's3', 's4', 's5']  # 5 items
        tx_list  = ['t1', 't2']                      # 2 items, ratio=2, remainder=1
        td = ProtocolsTableData('proto.txt', sys_list, tx_list)

        total_span = sum(s['spanCount'] for s in td.smallerListRowSpanList)
        assert total_span == td.biggerListLength
