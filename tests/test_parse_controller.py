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

    def test_burn_in_with_start_filter_excluded_with_ok_suffix(self, tmp_path):
        # Real-world files append ';ok' to the marker line — must still be filtered
        content = "Gen26_UseBurnInMeas[1];3\n(12a) BurnIn Start Check results:;ok\n"
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


# ---------------------------------------------------------------------------
# PST-74 — count helpers for protocol dicts
# ---------------------------------------------------------------------------

class TestProtocolCountHelpers:
    """protocol_count / parsed_protocol_count / to_be_parsed_count."""

    def test_protocol_count_reflects_path_type_list(self):
        pc = _make_controller()
        pc.protocolPathDict['protocolPathTypeDictList'].append(
            {'protocolPath': '/a.txt', 'type': 'Calibration'}
        )
        assert pc.protocol_count() == 1

    def test_protocol_count_multiple(self):
        pc = _make_controller()
        for i in range(5):
            pc.protocolPathDict['protocolPathTypeDictList'].append(
                {'protocolPath': f'/p{i}.txt', 'type': 'BurnIn'}
            )
        assert pc.protocol_count() == 5

    def test_parsed_protocol_count(self):
        pc = _make_controller()
        pc.parsedProtDict['protocolPathTypeDictList'].append({'protocolPath': '/b.txt'})
        assert pc.parsed_protocol_count() == 1

    def test_to_be_parsed_count(self):
        pc = _make_controller()
        pc.protToBeParsedDict['protocolPathTypeDictList'].append({'protocolPath': '/c.txt'})
        assert pc.to_be_parsed_count() == 1

    def test_all_counts_zero_after_clear(self):
        pc = _make_controller()
        pc.protocolPathDict['protocolPathTypeDictList'].append({'protocolPath': '/a.txt', 'type': 'BurnIn'})
        pc.parsedProtDict['protocolPathTypeDictList'].append({'protocolPath': '/b.txt'})
        pc.protToBeParsedDict['protocolPathTypeDictList'].append({'protocolPath': '/c.txt'})
        pc.clear_state()
        assert pc.protocol_count()        == 0
        assert pc.parsed_protocol_count() == 0
        assert pc.to_be_parsed_count()    == 0


# ---------------------------------------------------------------------------
# PST-74 — build_prot_path_type_list populates burnIn / cal split dicts
# ---------------------------------------------------------------------------

class TestProtocolTypeSplitDicts:
    """Verify that build_prot_path_type_list correctly assigns types and that
    the returned list separates BurnIn vs Calibration by type field."""

    def test_auto_mode_produces_correct_types(self, tmp_path):
        cal = tmp_path / 'cal.txt'
        cal.write_text('Gen26_UseBurnInMeas[1];0\n')
        burn = tmp_path / 'burn.txt'
        burn.write_text('Gen26_UseBurnInMeas[1];3\n')
        pc = _make_controller()
        result = pc.build_prot_path_type_list([str(cal), str(burn)], 0, True)
        type_map = {r['protocolPath']: r['type'] for r in result}
        assert type_map[str(cal)]  == 'Calibration'
        assert type_map[str(burn)] == 'BurnIn'

    def test_force_calibration_mode_overrides_content(self, tmp_path):
        p = tmp_path / 'burn_content.txt'
        p.write_text('Gen26_UseBurnInMeas[1];3\n')  # BurnIn content
        pc = _make_controller()
        result = pc.build_prot_path_type_list([str(p)], burn_in_cal_mode=2, include_burn_in_start=False)
        assert result[0]['type'] == 'Calibration'

    def test_force_burn_in_mode_overrides_content(self, tmp_path):
        p = tmp_path / 'cal_content.txt'
        p.write_text('Gen26_UseBurnInMeas[1];0\n')  # Calibration content
        pc = _make_controller()
        result = pc.build_prot_path_type_list([str(p)], burn_in_cal_mode=1, include_burn_in_start=False)
        assert result[0]['type'] == 'BurnIn'

    def test_empty_path_list_returns_empty(self):
        pc = _make_controller()
        result = pc.build_prot_path_type_list([], 0, False)
        assert result == []

    def test_unclear_type_still_included(self, tmp_path):
        p = tmp_path / 'unclear.txt'
        p.write_text('no recognizable marker\n')
        pc = _make_controller()
        result = pc.build_prot_path_type_list([str(p)], 0, False)
        assert len(result) == 1
        assert result[0]['type'] == 'Unclear'


# ---------------------------------------------------------------------------
# PST-74 — accepted / filtered protocol path dicts
# ---------------------------------------------------------------------------

class TestAcceptedFilteredProtocolDicts:
    """Verify structure and direct manipulation of acceptedProtocolPathDict
    and filteredProtocolPathDict."""

    def test_accepted_dict_has_all_required_keys(self):
        pc = _make_controller()
        assert 'emptyProtList'       in pc.acceptedProtocolPathDict
        assert 'errorProtList'       in pc.acceptedProtocolPathDict
        assert 'abbortCritProtList'  in pc.acceptedProtocolPathDict
        assert 'limitExceededProtList' in pc.acceptedProtocolPathDict

    def test_filtered_dict_has_protocol_path_list_key(self):
        pc = _make_controller()
        assert 'protocolPathList' in pc.filteredProtocolPathDict

    def test_error_list_accumulates(self):
        pc = _make_controller()
        pc.acceptedProtocolPathDict['errorProtList'].extend(['/a.txt', '/b.txt'])
        assert len(pc.acceptedProtocolPathDict['errorProtList']) == 2

    def test_clear_resets_all_accepted_sub_lists(self):
        pc = _make_controller()
        pc.acceptedProtocolPathDict['errorProtList'].append('/x.txt')
        pc.acceptedProtocolPathDict['abbortCritProtList'].append('/y.txt')
        pc.acceptedProtocolPathDict['limitExceededProtList'].append('/z.txt')
        pc.acceptedProtocolPathDict['emptyProtList'].append('/e.txt')
        pc.clear_state()
        for key in pc.acceptedProtocolPathDict:
            assert pc.acceptedProtocolPathDict[key] == []
