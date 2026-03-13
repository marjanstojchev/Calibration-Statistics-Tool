"""
Tests for shared/loaddata.py

Covers the error handling improvements added in this session:
- Empty/None/falsy path guard in loadData()
- OSError handling for os.listdir() failures in proceessPath()
"""
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

from shared.loaddata import LoadData


# ---------------------------------------------------------------------------
# loadData(): empty / None / falsy path guard
# ---------------------------------------------------------------------------

class TestLoadDataEmptyPath:

    def test_none_path_sets_invalidPath(self):
        ld = LoadData(None, False, [])
        assert ld.invalidPath == 1

    def test_empty_string_sets_invalidPath(self):
        ld = LoadData('', False, [])
        assert ld.invalidPath == 1

    def test_empty_list_sets_invalidPath(self):
        ld = LoadData([], False, [])
        assert ld.invalidPath == 1

    def test_no_files_parsed_on_none_path(self):
        ld = LoadData(None, False, [])
        assert ld.parseDataList == []

    def test_counter_zero_on_empty_string_path(self):
        ld = LoadData('', False, [])
        assert ld.counter == 0


# ---------------------------------------------------------------------------
# proceessPath(): os.listdir() OSError handling (protocol path branch)
#
# A path ending in _Protocol.txt whose parent directory does not exist
# triggers FileNotFoundError (subclass of OSError) from os.listdir.
# Before the fix this propagated as an unhandled exception; after the fix
# it is caught and invalidPath is set to 1.
# ---------------------------------------------------------------------------

class TestLoadDataProtocolDirOSError:

    @staticmethod
    def _fake_protocol_path(tmp_path):
        # tmp_path itself exists but 'nosuchdir' under it does not, so
        # os.listdir(str(tmp_path / 'nosuchdir')) raises FileNotFoundError.
        return str(tmp_path / 'nosuchdir' / 'measurement_Protocol.txt')

    def test_nonexistent_dir_does_not_raise(self, tmp_path):
        LoadData(self._fake_protocol_path(tmp_path), False, [])

    def test_nonexistent_dir_sets_invalidPath(self, tmp_path):
        ld = LoadData(self._fake_protocol_path(tmp_path), False, [])
        assert ld.invalidPath == 1

    def test_nonexistent_dir_no_files_parsed(self, tmp_path):
        ld = LoadData(self._fake_protocol_path(tmp_path), False, [])
        assert ld.parseDataList == []
