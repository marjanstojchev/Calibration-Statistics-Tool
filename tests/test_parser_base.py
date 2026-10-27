import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

from calibration_statistics_tool.shared.parser_base import ParseDataBase


class ConcreteParser(ParseDataBase):
    """Minimal concrete implementation used only in these tests."""
    def parseFile(self, fileNamePath: str, useSensorMuster: int, sensorMusterList: list) -> None:
        self.fileNamePath = fileNamePath
        self.bDataValid = True


class IncompleteParser(ParseDataBase):
    """Subclass that deliberately omits parseFile — must not be instantiable."""
    pass


class TestParseDataBaseCannotBeInstantiated:
    def test_direct_instantiation_raises_type_error(self):
        with pytest.raises(TypeError):
            ParseDataBase()


class TestIncompleteSubclassCannotBeInstantiated:
    def test_missing_parseFile_raises_type_error(self):
        with pytest.raises(TypeError):
            IncompleteParser()


class TestConcreteSubclassDefaults:
    def test_bDataValid_starts_false(self):
        parser = ConcreteParser()
        assert parser.bDataValid is False

    def test_fileNamePath_starts_empty(self):
        parser = ConcreteParser()
        assert parser.fileNamePath == ''

    def test_errorList_starts_empty(self):
        parser = ConcreteParser()
        assert parser.errorList == []

    def test_instances_do_not_share_errorList(self):
        # mutable default — each instance must get its own list
        p1 = ConcreteParser()
        p2 = ConcreteParser()
        p1.errorList.append('err')
        assert p2.errorList == []


class TestConcreteSubclassBehaviour:
    def test_parseFile_sets_bDataValid(self):
        parser = ConcreteParser()
        parser.parseFile('some/path.txt', 0, [])
        assert parser.bDataValid is True

    def test_parseFile_sets_fileNamePath(self):
        parser = ConcreteParser()
        parser.parseFile('some/path.txt', 0, [])
        assert parser.fileNamePath == 'some/path.txt'

    def test_is_instance_of_ParseDataBase(self):
        parser = ConcreteParser()
        assert isinstance(parser, ParseDataBase)
