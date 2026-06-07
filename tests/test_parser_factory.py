import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from calibration_statistics_tool.shared.parser_factory import ParserFactory, _REGISTRY
from calibration_statistics_tool.shared.parser_base import ParseDataBase
from calibration_statistics_tool.shared.parsePTU2data import PTU2ParseData
from calibration_statistics_tool.shared.parseTxAntDiagramData import TxAntDiagramParseData


class TestParserFactoryKnownTypes:
    def test_ptu2_returns_ptu2parsedata(self):
        parser = ParserFactory.create('ptu2')
        assert isinstance(parser, PTU2ParseData)

    def test_txantdiag_returns_txantdiagramparsedata(self):
        parser = ParserFactory.create('txantdiag')
        assert isinstance(parser, TxAntDiagramParseData)

    def test_ptu2_is_instance_of_base(self):
        parser = ParserFactory.create('ptu2')
        assert isinstance(parser, ParseDataBase)

    def test_txantdiag_is_instance_of_base(self):
        parser = ParserFactory.create('txantdiag')
        assert isinstance(parser, ParseDataBase)

    def test_each_call_returns_new_instance(self):
        p1 = ParserFactory.create('ptu2')
        p2 = ParserFactory.create('ptu2')
        assert p1 is not p2

    def test_instances_do_not_share_errorList(self):
        p1 = ParserFactory.create('ptu2')
        p2 = ParserFactory.create('ptu2')
        p1.errorList.append('err')
        assert p2.errorList == []


class TestParserFactoryUnknownType:
    def test_unknown_key_raises_value_error(self):
        with pytest.raises(ValueError):
            ParserFactory.create('unknown_format')

    def test_error_message_contains_key(self):
        with pytest.raises(ValueError, match='unknown_format'):
            ParserFactory.create('unknown_format')

    def test_error_message_lists_valid_types(self):
        with pytest.raises(ValueError, match='ptu2'):
            ParserFactory.create('bad')


class TestParserFactoryRegister:
    def test_register_and_create_custom_type(self):
        class StubParser(ParseDataBase):
            def parseFile(self, fileNamePath, useSensorMuster, sensorMusterList):
                self.bDataValid = True

        ParserFactory.register('stub', StubParser)
        parser = ParserFactory.create('stub')
        assert isinstance(parser, StubParser)
        # cleanup
        del _REGISTRY['stub']

    def test_register_non_subclass_raises_type_error(self):
        class NotAParser:
            pass

        with pytest.raises(TypeError):
            ParserFactory.register('bad', NotAParser)
