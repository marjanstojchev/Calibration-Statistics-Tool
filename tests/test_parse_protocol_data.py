import pytest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

from calibration_statistics_tool.shared.parse_protocol_data import ProtocolParseData, _detect_protocol_type
from calibration_statistics_tool.shared.parseProtocols import ProtocolType
from calibration_statistics_tool.shared.parser_base import ParseDataBase
from calibration_statistics_tool.shared.parser_factory import ParserFactory


_BURNIN_FILE = os.path.join(
    os.path.dirname(__file__), '..',
    'measurement_data', 'protocol_files',
    '2024-01-15_10-15-20_Tuner2_rf12346_dsp67891_Seq2_TxAnt2_Diagram2_BurnIn_Protocol.txt',
)
_CAL_FILE = os.path.join(
    os.path.dirname(__file__), '..',
    'measurement_data', 'protocol_files',
    '2024-01-15_12-30-45_Tuner1_rf12345_dsp67890_Seq1_TxAnt1_Diagram1_Protocol.txt',
)


class TestProtocolTypeDetection:
    def test_burnin_filename_detected(self):
        assert _detect_protocol_type('some/path/BurnIn_Protocol.txt') == ProtocolType.BurnIn

    def test_calibration_filename_detected(self):
        assert _detect_protocol_type('some/path/Calibration_Protocol.txt') == ProtocolType.Calibration

    def test_default_is_calibration(self):
        assert _detect_protocol_type('some/path/Protocol.txt') == ProtocolType.Calibration


class TestProtocolParseDataDefaults:
    def test_bDataValid_starts_false(self):
        p = ProtocolParseData()
        assert p.bDataValid is False

    def test_errorList_starts_empty(self):
        p = ProtocolParseData()
        assert p.errorList == []

    def test_is_instance_of_base(self):
        p = ProtocolParseData()
        assert isinstance(p, ParseDataBase)

    def test_instances_do_not_share_errorList(self):
        p1 = ProtocolParseData()
        p2 = ProtocolParseData()
        p1.errorList.append('x')
        assert p2.errorList == []


class TestProtocolParseDataMissingFile:
    def test_missing_file_bDataValid_false(self):
        p = ProtocolParseData()
        p.parseFile('nonexistent/path.txt', 0, [])
        assert p.bDataValid is False

    def test_missing_file_appends_error(self):
        p = ProtocolParseData()
        p.parseFile('nonexistent/path.txt', 0, [])
        assert len(p.errorList) > 0


class TestProtocolParseDataRealFiles:
    def test_burnin_file_bDataValid_true(self):
        p = ProtocolParseData()
        p.parseFile(_BURNIN_FILE, 0, [])
        assert p.bDataValid is True

    def test_burnin_protocol_type_detected(self):
        p = ProtocolParseData()
        p.parseFile(_BURNIN_FILE, 0, [])
        assert p.protocolType == ProtocolType.BurnIn

    def test_burnin_head_populated(self):
        p = ProtocolParseData()
        p.parseFile(_BURNIN_FILE, 0, [])
        assert isinstance(p.rawParsedProtocolHead, dict)
        assert len(p.rawParsedProtocolHead) > 0

    def test_calibration_file_bDataValid_true(self):
        p = ProtocolParseData()
        p.parseFile(_CAL_FILE, 0, [])
        assert p.bDataValid is True

    def test_calibration_protocol_type_detected(self):
        p = ProtocolParseData()
        p.parseFile(_CAL_FILE, 0, [])
        assert p.protocolType == ProtocolType.Calibration


class TestFactoryProtocolIntegration:
    def test_factory_creates_protocol_parser(self):
        p = ParserFactory.create('protocol')
        assert isinstance(p, ProtocolParseData)

    def test_factory_protocol_is_parse_data_base(self):
        p = ParserFactory.create('protocol')
        assert isinstance(p, ParseDataBase)

    def test_factory_protocol_parses_real_file(self):
        p = ParserFactory.create('protocol')
        p.parseFile(_CAL_FILE, 0, [])
        assert p.bDataValid is True
