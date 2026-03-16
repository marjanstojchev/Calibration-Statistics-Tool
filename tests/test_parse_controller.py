"""
Tests for shared/parse_controller.py (PST-45).

All tests are pure-Python (no Qt required).  File-system interactions are
handled via pytest's tmp_path fixture so nothing modifies real project files.
"""
import sys
import os
import pytest

# Ensure shared/ is importable
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _sub in ['shared']:
    _p = os.path.join(_root, _sub)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from shared.parse_controller import ParseController


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_controller():
    return ParseController()


def _make_fake_parser(file_path: str, valid: bool):
    """Minimal stand-in for a parser object returned by ParserFactory."""
    class _FakeTitle:
        fileNamePath = file_path

    class _FakeParser:
        bDataValid = valid
        fileTitle  = _FakeTitle()

    return _FakeParser()


# ---------------------------------------------------------------------------
# __init__ — default state
# ---------------------------------------------------------------------------

class TestInitialState:
    def test_protocol_path_dict_empty(self):
        pc = _make_controller()
        assert pc.protocolPathDict['protocolPathTypeDictList'] == []

    def test_sys_diag_file_path_dict_empty(self):
        pc = _make_controller()
        assert pc.sysDiagFilePathDict['filePathList'] == []

    def test_tx_diag_file_path_dict_empty(self):
        pc = _make_controller()
        assert pc.txDiagfilePathDict['filePathList'] == []

    def test_accepted_protocol_keys(self):
        pc = _make_controller()
        assert set(pc.acceptedProtocolPathDict.keys()) == {
            'emptyProtList', 'errorProtList',
            'abbortCritProtList', 'limitExceededProtList',
        }

    def test_parsed_data_dicts_empty(self):
        pc = _make_controller()
        for d in [
            pc.sysDiagParsedDataDict,
            pc.separatePtu2ParsedDataDict,
            pc.separatePtu2FailedDataDict,
            pc.txAntDiagParsedDataDict,
            pc.separateTxAntDiagParsedDataDict,
            pc.separateTxAntDiagFailedDataDict,
        ]:
            assert d['parsedDataList'] == []

    def test_count_helpers_return_zero(self):
        pc = _make_controller()
        assert pc.ptu2_parsed_count()      == 0
        assert pc.ptu2_failed_count()      == 0
        assert pc.tx_ant_diag_parsed_count() == 0
        assert pc.tx_ant_diag_failed_count() == 0
        assert pc.sys_diag_parsed_count()  == 0
        assert pc.protocol_count()         == 0
        assert pc.parsed_protocol_count()  == 0
        assert pc.to_be_parsed_count()     == 0


# ---------------------------------------------------------------------------
# get_protocol_type — force mode
# ---------------------------------------------------------------------------

class TestGetProtocolTypeForceMode:
    def test_force_burn_in(self, tmp_path):
        # File content is irrelevant in force mode
        p = tmp_path / "prot.txt"
        p.write_text("anything")
        pc = _make_controller()
        assert pc.get_protocol_type(str(p), burn_in_cal_mode=1, include_burn_in_start=False) == 'BurnIn'

    def test_force_calibration(self, tmp_path):
        p = tmp_path / "prot.txt"
        p.write_text("anything")
        pc = _make_controller()
        assert pc.get_protocol_type(str(p), burn_in_cal_mode=2, include_burn_in_start=False) == 'Calibration'


# ---------------------------------------------------------------------------
# get_protocol_type — auto-detect mode (mode 0)
# ---------------------------------------------------------------------------

class TestGetProtocolTypeAutoDetect:
    def _write_prot(self, tmp_path, content: str):
        p = tmp_path / "prot.txt"
        p.write_text(content)
        return str(p)

    def test_auto_detect_calibration(self, tmp_path):
        content = "Gen26_UseBurnInMeas[1];0\n"
        path = self._write_prot(tmp_path, content)
        pc = _make_controller()
        assert pc.get_protocol_type(path, 0, False) == 'Calibration'

    def test_auto_detect_burn_in(self, tmp_path):
        content = "Gen26_UseBurnInMeas[1];3\n"
        path = self._write_prot(tmp_path, content)
        pc = _make_controller()
        assert pc.get_protocol_type(path, 0, True) == 'BurnIn'

    def test_auto_detect_unclear(self, tmp_path):
        content = "some other content\n"
        path = self._write_prot(tmp_path, content)
        pc = _make_controller()
        assert pc.get_protocol_type(path, 0, False) == 'Unclear'

    def test_burn_in_with_start_filter_excluded(self, tmp_path):
        # BurnIn protocol that also has a BurnIn-start marker → filtered out
        content = "Gen26_UseBurnInMeas[1];3\n(12a) BurnIn Start Check results:\n"
        path = self._write_prot(tmp_path, content)
        pc = _make_controller()
        result = pc.get_protocol_type(path, 0, include_burn_in_start=False)
        assert result == 'Filtered'

    def test_burn_in_with_start_filter_included(self, tmp_path):
        content = "Gen26_UseBurnInMeas[1];3\n(12a) BurnIn Start Check results:\n"
        path = self._write_prot(tmp_path, content)
        pc = _make_controller()
        result = pc.get_protocol_type(path, 0, include_burn_in_start=True)
        assert result == 'BurnIn'

    def test_missing_file_returns_unclear(self):
        pc = _make_controller()
        result = pc.get_protocol_type('/nonexistent/path.txt', 0, False)
        assert result == 'Unclear'


# ---------------------------------------------------------------------------
# build_prot_path_type_list
# ---------------------------------------------------------------------------

class TestBuildProtPathTypeList:
    def test_returns_correct_types(self, tmp_path):
        p1 = tmp_path / "cal.txt"
        p1.write_text("Gen26_UseBurnInMeas[1];0\n")
        p2 = tmp_path / "burn.txt"
        p2.write_text("Gen26_UseBurnInMeas[1];3\n")
        pc = _make_controller()
        result = pc.build_prot_path_type_list([str(p1), str(p2)], 0, True)
        assert len(result) == 2
        types = {r['protocolPath']: r['type'] for r in result}
        assert types[str(p1)] == 'Calibration'
        assert types[str(p2)] == 'BurnIn'

    def test_filtered_entries_excluded(self, tmp_path):
        p = tmp_path / "prot.txt"
        p.write_text("Gen26_UseBurnInMeas[1];3\n(12a) BurnIn Start Check results:\n")
        pc = _make_controller()
        result = pc.build_prot_path_type_list([str(p)], 0, include_burn_in_start=False)
        assert result == []

    def test_force_mode_all_burn_in(self, tmp_path):
        paths = []
        for i in range(3):
            p = tmp_path / f"p{i}.txt"
            p.write_text("anything")
            paths.append(str(p))
        pc = _make_controller()
        result = pc.build_prot_path_type_list(paths, burn_in_cal_mode=1, include_burn_in_start=False)
        assert all(r['type'] == 'BurnIn' for r in result)
        assert len(result) == 3


# ---------------------------------------------------------------------------
# add_ptu2_to_state — de-duplication and routing
# ---------------------------------------------------------------------------

class TestAddPtu2ToState:
    def test_valid_parser_goes_to_parsed_and_sys_diag(self):
        pc = _make_controller()
        parser = _make_fake_parser('/a/b/file.txt', valid=True)
        pc.add_ptu2_to_state([parser], [])
        assert pc.ptu2_parsed_count()     == 1
        assert pc.sys_diag_parsed_count() == 1
        assert pc.ptu2_failed_count()     == 0

    def test_invalid_parser_goes_to_failed_only(self):
        pc = _make_controller()
        parser = _make_fake_parser('/a/b/bad.txt', valid=False)
        pc.add_ptu2_to_state([], [parser])
        assert pc.ptu2_failed_count()     == 1
        assert pc.ptu2_parsed_count()     == 0
        assert pc.sys_diag_parsed_count() == 0

    def test_duplicate_not_added_twice(self):
        pc = _make_controller()
        p1 = _make_fake_parser('/dup.txt', valid=True)
        p2 = _make_fake_parser('/dup.txt', valid=True)
        pc.add_ptu2_to_state([p1], [])
        pc.add_ptu2_to_state([p2], [])
        assert pc.ptu2_parsed_count()     == 1
        assert pc.sys_diag_parsed_count() == 1

    def test_different_paths_both_added(self):
        pc = _make_controller()
        pc.add_ptu2_to_state([_make_fake_parser('/a.txt', True)], [])
        pc.add_ptu2_to_state([_make_fake_parser('/b.txt', True)], [])
        assert pc.ptu2_parsed_count()     == 2
        assert pc.sys_diag_parsed_count() == 2


# ---------------------------------------------------------------------------
# add_tx_ant_diag_to_state
# ---------------------------------------------------------------------------

class TestAddTxAntDiagToState:
    def test_valid_goes_to_parsed_and_main_dict(self):
        pc = _make_controller()
        parser = _make_fake_parser('/tx/file.txt', valid=True)
        pc.add_tx_ant_diag_to_state([parser], [])
        assert pc.tx_ant_diag_parsed_count() == 1
        assert len(pc.txAntDiagParsedDataDict['parsedDataList']) == 1

    def test_invalid_goes_to_failed_only(self):
        pc = _make_controller()
        parser = _make_fake_parser('/tx/bad.txt', valid=False)
        pc.add_tx_ant_diag_to_state([], [parser])
        assert pc.tx_ant_diag_failed_count()  == 1
        assert pc.tx_ant_diag_parsed_count()  == 0

    def test_no_duplicates(self):
        pc = _make_controller()
        p = _make_fake_parser('/tx/dup.txt', valid=True)
        pc.add_tx_ant_diag_to_state([p], [])
        pc.add_tx_ant_diag_to_state([p], [])
        assert pc.tx_ant_diag_parsed_count() == 1


# ---------------------------------------------------------------------------
# clear_state
# ---------------------------------------------------------------------------

class TestClearState:
    def test_clears_all_state_dicts(self):
        pc = _make_controller()
        # populate some state
        pc.sysDiagParsedDataDict['parsedDataList'].append('x')
        pc.protocolPathDict['protocolPathTypeDictList'].append({'protocolPath': 'a', 'type': 'BurnIn'})
        pc.acceptedProtocolPathDict['errorProtList'].append('err')
        pc.clear_state()
        assert pc.sysDiagParsedDataDict['parsedDataList']              == []
        assert pc.protocolPathDict['protocolPathTypeDictList']         == []
        assert pc.acceptedProtocolPathDict['errorProtList']            == []
        assert pc.filteredProtocolPathDict['protocolPathList']         == []

    def test_count_helpers_zero_after_clear(self):
        pc = _make_controller()
        pc.sysDiagParsedDataDict['parsedDataList'].append('x')
        pc.clear_state()
        assert pc.sys_diag_parsed_count() == 0
