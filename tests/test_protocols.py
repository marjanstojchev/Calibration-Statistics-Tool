"""Tests for shared/protocolsTest.py — ProtocolInfoClass.

Covers:
  PST-72 — getPreParseInfo, FilterProtocols, FilterNewProtocols,
            PreParseProtcols, GetAllProtocolsList,
            getfiltered_ptu2filelist, getfiltered_txantdiagramfilelist.

Fixture files in measurement_data/protocol_files/ (created in PST-73):
  - Protocol.txt              (Calibration, clean – no flags)
  - BurnIn_Protocol.txt       (BurnIn, clean)
  - Protocol_Error.txt        (bErrorOccured=True, bAbortCriterion=False)
  - Protocol_Abort.txt        (bErrorOccured=False, bAbortCriterion=True)
  - Protocol_Limits.txt       (bLimitExceeded=True)
  - Protocol_AllFlags.txt     (all three flags set)
  - BurnIn_Start_Protocol.txt (BurnIn + (12a) start marker + Gen26 tag)
  - Protocol_NewerSameSensor  (same rf/dsp/serial as Calibration, newer date)
"""
import os

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

import pytest
from calibration_statistics_tool.shared.protocolsTest import ProtocolInfoClass

# ---------------------------------------------------------------------------
# Absolute paths to fixture files
# ---------------------------------------------------------------------------
_PROT_DIR = os.path.join(_root, 'measurement_data', 'protocol_files')

_CAL_FILE    = os.path.join(_PROT_DIR, '2024-01-15_12-30-45_Tuner1_rf12345_dsp67890_Seq1_TxAnt1_Diagram1_Protocol.txt')
_BURNIN_FILE = os.path.join(_PROT_DIR, '2024-01-15_10-15-20_Tuner2_rf12346_dsp67891_Seq2_TxAnt2_Diagram2_BurnIn_Protocol.txt')
_ERROR_FILE  = os.path.join(_PROT_DIR, '2024-02-01_08-00-00_Tuner1_rf11111_dsp22222_Seq1_TxAnt0_Diagram0_Error_Protocol.txt')
_ABORT_FILE  = os.path.join(_PROT_DIR, '2024-02-01_09-00-00_Tuner1_rf11112_dsp22223_Seq1_TxAnt0_Diagram0_Abort_Protocol.txt')
_LIMITS_FILE = os.path.join(_PROT_DIR, '2024-02-01_10-00-00_Tuner1_rf11113_dsp22224_Seq1_TxAnt0_Diagram0_Limits_Protocol.txt')
_ALL_FLAGS   = os.path.join(_PROT_DIR, '2024-02-01_11-00-00_Tuner1_rf11114_dsp22225_Seq1_TxAnt0_Diagram0_AllFlags_Protocol.txt')
_BI_START    = os.path.join(_PROT_DIR, '2024-02-01_12-00-00_Tuner1_rf12345_dsp67890_Seq1_TxAnt0_Diagram0_BurnIn_Start_Protocol.txt')
_NEWER_FILE  = os.path.join(_PROT_DIR, '2024-02-02_08-00-00_Tuner1_rf12345_dsp67890_Seq1_TxAnt0_Diagram0_NewerSameSensor_Protocol.txt')


# ---------------------------------------------------------------------------
# Helper: build a ProtocolInfoClass with specified attributes
# ---------------------------------------------------------------------------

def _make_info(
    serial: str,
    rf: str,
    dsp: str,
    date_time: str,
    error: bool = False,
    abort: bool = False,
    limits: bool = False,
    empty: bool = False,
    path: str = 'fixture.txt',
) -> ProtocolInfoClass:
    p = ProtocolInfoClass()
    p.productSerial   = serial
    p.rf              = rf
    p.dsp             = dsp
    p.dateAndTime     = date_time
    p.bErrorOccured   = error
    p.bAbortCriterion = abort
    p.bLimitExceeded  = limits
    p.bFileEmpty      = empty
    p.PathName        = path
    return p


# ===========================================================================
# getPreParseInfo
# ===========================================================================

class TestGetPreParseInfo:
    """Tests directly exercising the static getPreParseInfo logic."""

    def _parse(self, lines: list[str]):
        return ProtocolInfoClass.getPreParseInfo(lines)

    # --- empty file ---------------------------------------------------------

    def test_empty_file_bFileEmpty_true(self):
        empty, err, abort, limits, *_ = self._parse([])
        assert empty is True

    def test_empty_file_flags_all_false(self):
        empty, err, abort, limits, *_ = self._parse([])
        assert err is False
        assert abort is False
        assert limits is False

    # --- clean protocol (E=0 and K=0 present, no M:) -----------------------

    def test_clean_no_error(self):
        lines = ['E=0;\n', 'K=0;\n', 'Measurment Durations:\n', 'M:ignored\n']
        _, err, abort, limits, *_ = self._parse(lines)
        assert err is False

    def test_clean_no_abort(self):
        lines = ['E=0;\n', 'K=0;\n']
        _, err, abort, limits, *_ = self._parse(lines)
        assert abort is False

    def test_clean_no_limits(self):
        lines = ['E=0;\n', 'K=0;\n']
        _, err, abort, limits, *_ = self._parse(lines)
        assert limits is False

    # --- error flag ---------------------------------------------------------

    def test_missing_eol_no_error_flag_means_error_occurred(self):
        # Only K=0 present, no E=0 → bErrorOccured stays True
        lines = ['K=0;\n']
        _, err, abort, limits, *_ = self._parse(lines)
        assert err is True

    def test_present_eol_no_error_flag_clears_error(self):
        lines = ['E=0;\n', 'K=0;\n']
        _, err, *_ = self._parse(lines)
        assert err is False

    # --- abort criterion flag -----------------------------------------------

    def test_missing_k0_means_abort_criterion(self):
        lines = ['E=0;\n']
        _, err, abort, limits, *_ = self._parse(lines)
        assert abort is True

    def test_present_k0_clears_abort(self):
        lines = ['E=0;\n', 'K=0;\n']
        _, err, abort, *_ = self._parse(lines)
        assert abort is False

    # --- limits exceeded ----------------------------------------------------

    def test_m_colon_line_sets_limits_exceeded(self):
        lines = ['E=0;\n', 'K=0;\n', 'M:SomeLimit;val;\n']
        _, err, abort, limits, *_ = self._parse(lines)
        assert limits is True

    def test_no_m_colon_line_leaves_limits_false(self):
        lines = ['E=0;\n', 'K=0;\n']
        _, err, abort, limits, *_ = self._parse(lines)
        assert limits is False

    # --- stops at 'Measurment Durations:' header ----------------------------

    def test_stops_before_header_m_colon_ignored(self):
        lines = ['E=0;\n', 'K=0;\n', 'Measurment Durations:\n', 'M:AfterHeader;\n']
        _, err, abort, limits, *_ = self._parse(lines)
        assert limits is False

    def test_e0_before_header_is_found(self):
        lines = ['E=0;\n', 'Measurment Durations:\n', 'K=0;\n']
        _, err, abort, *_ = self._parse(lines)
        assert err is False   # E=0 found before header
        assert abort is True  # K=0 was AFTER header, not found

    # --- metadata extraction ------------------------------------------------

    def test_date_time_parsed(self):
        # Use lines without \n (unit-test inputs; file-reading \n is tested in
        # TestPreParseProtocols via real fixture files).
        lines = ['Date:;2024-03-15', 'Time:;09:30:00']
        _, _, _, _, date_time, *_ = self._parse(lines)
        assert date_time == '2024-03-15-09:30:00'

    def test_product_serial_parsed(self):
        lines = ['Product-Serial:;UMRR-11.00.04-99999']
        _, _, _, _, _, serial, *_ = self._parse(lines)
        assert serial == 'UMRR-11.00.04-99999'

    def test_rf_dsp_parsed(self):
        lines = ['RF-Serial:;55555', 'Dsp-Serial:;66666']
        _, _, _, _, _, _, rf, dsp = self._parse(lines)
        assert rf  == '55555'
        assert dsp == '66666'

    def test_spaces_in_field_values_stripped(self):
        # replace(' ','') removes spaces from line before field split
        lines = ['RF-Serial:; 77777']
        _, _, _, _, _, _, rf, _ = self._parse(lines)
        assert rf == '77777'


# ===========================================================================
# FilterProtocols
# ===========================================================================

class TestFilterProtocols:
    """Test the six flag combinations exposed by the UI checkboxes."""

    # Helper: run filter and return (accepted_paths, filtered_paths)
    def _run(self, infos, use_error=False, use_abort=False, use_limits=False):
        accepted, filtered = ProtocolInfoClass.FilterProtocols(
            infos, use_error, use_abort, use_limits
        )
        return [i.PathName for i in accepted], [i.PathName for i in filtered]

    # --- empty protocol always rejected ------------------------------------

    def test_empty_file_always_rejected(self):
        info = _make_info('S1', 'rf1', 'dsp1', '2024-01-01-00:00:00', empty=True)
        accepted, filtered = self._run([info], True, True, True)
        # Empty files are never added to the accepted list
        assert info.PathName not in accepted
        # FilterProtocols silently drops empty files: they are NOT in filteredOut
        # either (the else branch only handles error/abort/limits rejections)
        assert info.PathName not in filtered

    # --- clean protocol (no flags) ----------------------------------------

    def test_clean_protocol_accepted_unconditionally(self):
        info = _make_info('S1', 'rf1', 'dsp1', '2024-01-01-00:00:00')
        accepted, _ = self._run([info])
        assert info.PathName in accepted

    # --- EOL Error flag ----------------------------------------------------

    def test_error_rejected_when_use_error_false(self):
        info = _make_info('S1', 'rf1', 'dsp1', '2024-01-01', error=True)
        accepted, filtered = self._run([info], use_error=False)
        assert info.PathName not in accepted
        assert info.PathName in filtered

    def test_error_accepted_when_use_error_true(self):
        info = _make_info('S1', 'rf1', 'dsp1', '2024-01-01', error=True)
        accepted, _ = self._run([info], use_error=True)
        assert info.PathName in accepted

    # --- EOL Abort Criterion flag -----------------------------------------

    def test_abort_rejected_when_use_abort_false(self):
        info = _make_info('S1', 'rf1', 'dsp1', '2024-01-01', abort=True)
        accepted, filtered = self._run([info], use_abort=False)
        assert info.PathName not in accepted
        assert info.PathName in filtered

    def test_abort_accepted_when_use_abort_true(self):
        info = _make_info('S1', 'rf1', 'dsp1', '2024-01-01', abort=True)
        accepted, _ = self._run([info], use_abort=True)
        assert info.PathName in accepted

    # --- EOL Meas Limits flag ---------------------------------------------

    def test_limits_rejected_when_use_limits_false(self):
        info = _make_info('S1', 'rf1', 'dsp1', '2024-01-01', limits=True)
        accepted, filtered = self._run([info], use_limits=False)
        assert info.PathName not in accepted
        assert info.PathName in filtered

    def test_limits_accepted_when_use_limits_true(self):
        info = _make_info('S1', 'rf1', 'dsp1', '2024-01-01', limits=True)
        accepted, _ = self._run([info], use_limits=True)
        assert info.PathName in accepted

    # --- All flags set -----------------------------------------------------

    def test_all_flags_rejected_when_all_use_false(self):
        info = _make_info('S1', 'rf1', 'dsp1', '2024-01-01', error=True, abort=True, limits=True)
        accepted, filtered = self._run([info])
        assert info.PathName not in accepted
        assert info.PathName in filtered

    def test_all_flags_accepted_when_all_use_true(self):
        info = _make_info('S1', 'rf1', 'dsp1', '2024-01-01', error=True, abort=True, limits=True)
        accepted, _ = self._run([info], use_error=True, use_abort=True, use_limits=True)
        assert info.PathName in accepted

    # --- Mixed batch -------------------------------------------------------

    def test_clean_accepted_while_error_rejected(self):
        clean = _make_info('S1', 'rf1', 'dsp1', '2024-01-01', path='clean.txt')
        err   = _make_info('S2', 'rf2', 'dsp2', '2024-01-02', error=True, path='err.txt')
        accepted, filtered = self._run([clean, err], use_error=False)
        assert 'clean.txt' in accepted
        assert 'err.txt'   in filtered

    # --- Sorting -----------------------------------------------------------

    def test_accepted_list_sorted_by_dsp(self):
        # dsp2 > dsp1 alphabetically → p2 should come after p1
        p1 = _make_info('S1', 'rf1', 'dsp1', '2024-01-02', path='/p1.txt')
        p2 = _make_info('S2', 'rf1', 'dsp2', '2024-01-01', path='/p2.txt')
        accepted, _ = self._run([p2, p1])   # deliberately reversed input
        paths = [i for i in accepted]
        assert paths.index('/p1.txt') < paths.index('/p2.txt')


# ===========================================================================
# FilterNewProtocols
# ===========================================================================

class TestFilterNewProtocols:
    """Test 'Latest Protocol' checkbox logic."""

    def _run(self, infos):
        return [i.PathName for i in ProtocolInfoClass.FilterNewProtocols(infos)]

    # --- edge cases --------------------------------------------------------

    def test_empty_list_returns_empty(self):
        result = ProtocolInfoClass.FilterNewProtocols([])
        assert result == []

    def test_single_protocol_is_kept(self):
        p = _make_info('S1', 'rf1', 'dsp1', '2024-01-01')
        result = self._run([p])
        assert p.PathName in result

    # --- different sensors ------------------------------------------------

    def test_all_different_sensors_kept(self):
        p1 = _make_info('S1', 'rf1', 'dsp1', '2024-01-01', path='/p1.txt')
        p2 = _make_info('S2', 'rf2', 'dsp2', '2024-01-02', path='/p2.txt')
        result = self._run([p1, p2])
        assert '/p1.txt' in result
        assert '/p2.txt' in result

    # --- same sensor, keep newer ------------------------------------------

    def test_older_removed_newer_kept(self):
        old = _make_info('S1', 'rf1', 'dsp1', '2024-01-01-08:00:00', path='old.txt')
        new = _make_info('S1', 'rf1', 'dsp1', '2024-01-02-08:00:00', path='new.txt')
        # FilterProtocols sorts by dsp then dateAndTime → [old, new]
        result = self._run([old, new])
        assert 'new.txt' in result
        assert 'old.txt' not in result

    # --- same serial but different rf/dsp → both kept ---------------------

    def test_same_serial_different_dsp_both_kept(self):
        p1 = _make_info('S1', 'rf1', 'dsp1', '2024-01-01', path='/p1.txt')
        p2 = _make_info('S1', 'rf1', 'dsp2', '2024-01-02', path='/p2.txt')
        result = self._run([p1, p2])
        assert '/p1.txt' in result
        assert '/p2.txt' in result

    # --- three protocols: two same-sensor (keep newer), one different -----

    def test_three_protocols_keeps_newer_plus_different(self):
        old = _make_info('S1', 'rf1', 'dsp1', '2024-01-01', path='old.txt')
        new = _make_info('S1', 'rf1', 'dsp1', '2024-01-02', path='new.txt')
        other = _make_info('S2', 'rf2', 'dsp2', '2024-01-01', path='other.txt')
        # list already sorted as FilterProtocols would produce [old, new, other]
        result = self._run([old, new, other])
        assert 'new.txt'   in result
        assert 'other.txt' in result
        assert 'old.txt'   not in result


# ===========================================================================
# PreParseProtcols — real fixture files
# ===========================================================================

class TestPreParseProtocols:
    """Integration: PreParseProtcols with real fixture files."""

    def _pre_parse(self, *paths):
        infos, empty, errors, aborts, limits = ProtocolInfoClass.PreParseProtcols(list(paths))
        return infos, empty, errors, aborts, limits

    def test_clean_calibration_no_flags(self):
        infos, empty, errors, aborts, limits = self._pre_parse(_CAL_FILE)
        assert len(infos) == 1
        info = infos[0]
        assert info.bErrorOccured   is False
        assert info.bAbortCriterion is False
        assert info.bLimitExceeded  is False
        assert info.bFileEmpty      is False

    def test_clean_burnin_no_flags(self):
        infos, *_ = self._pre_parse(_BURNIN_FILE)
        info = infos[0]
        assert info.bErrorOccured   is False
        assert info.bAbortCriterion is False

    def test_error_fixture_has_error_flag(self):
        infos, _, errors, *_ = self._pre_parse(_ERROR_FILE)
        assert infos[0].bErrorOccured   is True
        assert infos[0].bAbortCriterion is False
        assert _ERROR_FILE in errors

    def test_abort_fixture_has_abort_flag(self):
        infos, _, _, aborts, _ = self._pre_parse(_ABORT_FILE)
        assert infos[0].bAbortCriterion is True
        assert infos[0].bErrorOccured   is False
        assert _ABORT_FILE in aborts

    def test_limits_fixture_has_limits_flag(self):
        infos, _, _, _, limits = self._pre_parse(_LIMITS_FILE)
        assert infos[0].bLimitExceeded is True
        assert _LIMITS_FILE in limits

    def test_all_flags_fixture(self):
        infos, _, errors, aborts, limits = self._pre_parse(_ALL_FLAGS)
        info = infos[0]
        assert info.bErrorOccured   is True
        assert info.bAbortCriterion is True
        assert info.bLimitExceeded  is True

    def test_path_name_set_on_info(self):
        infos, *_ = self._pre_parse(_CAL_FILE)
        assert infos[0].PathName == _CAL_FILE

    def test_missing_file_skipped_from_info_list(self):
        infos, *_ = self._pre_parse('/nonexistent/path_Protocol.txt')
        # File not found → skipped (error printed), not appended to infos
        assert infos == []

    def test_multiple_files_all_parsed(self):
        infos, *_ = self._pre_parse(_CAL_FILE, _BURNIN_FILE, _ERROR_FILE)
        assert len(infos) == 3


# ===========================================================================
# GetAllProtocolsList
# ===========================================================================

class TestGetAllProtocolsList:
    """Verify directory walking and glob filtering."""

    def test_finds_all_protocol_files_in_measurement_dir(self):
        found = ProtocolInfoClass.GetAllProtocolsList(_PROT_DIR)
        assert len(found) >= 2  # at minimum the two original fixtures

    def test_all_found_have_proto_in_name(self):
        found = ProtocolInfoClass.GetAllProtocolsList(_PROT_DIR)
        for path in found:
            assert 'proto' in os.path.basename(path).lower()

    def test_all_found_end_with_txt(self):
        found = ProtocolInfoClass.GetAllProtocolsList(_PROT_DIR)
        for path in found:
            assert path.endswith('.txt')

    def test_recurse_subdirectories(self, tmp_path):
        subdir = tmp_path / 'sub'
        subdir.mkdir()
        # Protocol in subdirectory
        f = subdir / '2024-01-01_Protocol.txt'
        f.write_text('E=0;\nK=0;\n')
        found = ProtocolInfoClass.GetAllProtocolsList(str(tmp_path))
        assert any('2024-01-01_Protocol.txt' in p for p in found)

    def test_non_protocol_files_excluded(self, tmp_path):
        (tmp_path / 'notes.txt').write_text('some content')
        (tmp_path / 'README.md').write_text('readme')
        found = ProtocolInfoClass.GetAllProtocolsList(str(tmp_path))
        assert found == []


# ===========================================================================
# getfiltered_ptu2filelist
# ===========================================================================

class TestGetFilteredPtu2FileList:
    """Verify PTU2 file search (fnmatch glob)."""

    def test_finds_matching_ptu2_files(self, tmp_path):
        stem = '2024-01-15_12-30-45_Tuner1_rf12345_dsp67890_Seq1_'
        for name in [
            f'{stem}TxAnt0_Diagram1_Az_ptu2.txt',
            f'{stem}TxAnt1_Diagram2_El_ptu2.txt',
        ]:
            (tmp_path / name).write_text('data')

        pattern = stem + '*PTU2*'  # note: PTU2 all-caps in fnmatch
        # getfiltered_ptu2filelist uses fnmatch which is case-sensitive on Linux
        # but the test files use lowercase; use lowercase match pattern:
        pattern_lower = stem + '*ptu2*.txt'
        found = ProtocolInfoClass.getfiltered_ptu2filelist(str(tmp_path), pattern_lower)
        assert len(found) == 2

    def test_no_matches_returns_empty_list(self, tmp_path):
        (tmp_path / 'other_file.txt').write_text('data')
        found = ProtocolInfoClass.getfiltered_ptu2filelist(str(tmp_path), '*ptu2*.txt')
        assert found == []

    def test_non_matching_files_excluded(self, tmp_path):
        (tmp_path / '2024_ptu2.txt').write_text('data')
        (tmp_path / '2024_other.txt').write_text('data')
        found = ProtocolInfoClass.getfiltered_ptu2filelist(str(tmp_path), '*ptu2*.txt')
        assert len(found) == 1
        assert 'ptu2' in found[0]

    def test_recurse_into_subdirectories(self, tmp_path):
        subdir = tmp_path / 'nested'
        subdir.mkdir()
        (subdir / 'deep_ptu2.txt').write_text('data')
        found = ProtocolInfoClass.getfiltered_ptu2filelist(str(tmp_path), '*ptu2*.txt')
        assert len(found) == 1


# ===========================================================================
# getfiltered_txantdiagramfilelist
# ===========================================================================

class TestGetFilteredTxAntDiagramFileList:
    """Verify TxAntDiag file search logic (identifier + TxAnt + Diagram, no PTU2)."""

    def test_finds_matching_txantdiag_files(self, tmp_path):
        stem = '2024-01-15_12-30-45_Tuner1_rf12345_dsp67890_'
        (tmp_path / f'{stem}TxAnt0_Diagram0.txt').write_text('data')
        (tmp_path / f'{stem}TxAnt1_Diagram1.txt').write_text('data')
        found = ProtocolInfoClass.getfiltered_txantdiagramfilelist(str(tmp_path), stem)
        assert len(found) == 2

    def test_excludes_ptu2_files(self, tmp_path):
        stem = '2024-01-15_stem_'
        (tmp_path / f'{stem}TxAnt0_Diagram0_Az_ptu2.txt').write_text('ptu2 data')
        (tmp_path / f'{stem}TxAnt0_Diagram0.txt').write_text('tx data')
        found = ProtocolInfoClass.getfiltered_txantdiagramfilelist(str(tmp_path), stem)
        assert len(found) == 1
        # Check only the filename (not the full path which may contain 'ptu2' in tmp dir name)
        assert 'ptu2' not in os.path.basename(found[0]).lower()

    def test_requires_txant_and_diagram_in_name(self, tmp_path):
        stem = '2024-_stem_'
        (tmp_path / f'{stem}TxAnt0_other.txt').write_text('no diagram')
        (tmp_path / f'{stem}Diagram0_other.txt').write_text('no txant')
        (tmp_path / f'{stem}TxAnt0_Diagram0.txt').write_text('both')
        found = ProtocolInfoClass.getfiltered_txantdiagramfilelist(str(tmp_path), stem)
        assert len(found) == 1
        assert 'TxAnt0_Diagram0' in found[0]

    def test_excludes_protocol_files(self, tmp_path):
        stem = '2024-01-15_10-15-20_Tuner2_rf12346_dsp67891_Seq2_TxAnt2_Diagram2_BurnIn_'
        (tmp_path / f'{stem}Protocol.txt').write_text('protocol data')
        (tmp_path / f'{stem}TxAnt2_Diagram2.txt').write_text('tx diag data')
        found = ProtocolInfoClass.getfiltered_txantdiagramfilelist(str(tmp_path), stem)
        assert len(found) == 1
        assert 'Protocol' not in os.path.basename(found[0])

    def test_no_match_returns_empty(self, tmp_path):
        (tmp_path / 'unrelated.txt').write_text('data')
        found = ProtocolInfoClass.getfiltered_txantdiagramfilelist(str(tmp_path), 'myidentifier_')
        assert found == []


# ===========================================================================
# End-to-end: getprotcols-like flow using ProtocolInfoClass primitives
# ===========================================================================

class TestProtocolFilterFlowEndToEnd:
    """Full pipeline: PreParseProtcols → FilterProtocols → FilterNewProtocols."""

    def test_full_flow_default_ui_settings(self):
        """Simulate default UI: useError=False, useAbort=True, useLimits=True.

        clean protocol     → accepted
        error protocol     → filtered out  (useError=False)
        abort protocol     → accepted      (useAbort=True)
        limits protocol    → accepted      (useLimits=True)
        all-flags protocol → filtered out  (useError=False is blocking)
        """
        files = [_CAL_FILE, _ERROR_FILE, _ABORT_FILE, _LIMITS_FILE, _ALL_FLAGS]
        infos, *_ = ProtocolInfoClass.PreParseProtcols(files)
        accepted, filtered = ProtocolInfoClass.FilterProtocols(
            infos,
            bUseFilesWithError=False,
            bUseFilesAbbortCriterion=True,
            bUseFilesWIthLimitsExceeded=True,
        )
        accepted_paths = [i.PathName for i in accepted]
        filtered_paths = [i.PathName for i in filtered]

        assert _CAL_FILE    in accepted_paths
        assert _ABORT_FILE  in accepted_paths
        assert _LIMITS_FILE in accepted_paths
        assert _ERROR_FILE  in filtered_paths
        assert _ALL_FLAGS   in filtered_paths

    def test_full_flow_all_use_false(self):
        """All use-flags False → only completely-clean protocols accepted."""
        files = [_CAL_FILE, _ERROR_FILE, _ABORT_FILE, _LIMITS_FILE]
        infos, *_ = ProtocolInfoClass.PreParseProtcols(files)
        accepted, filtered = ProtocolInfoClass.FilterProtocols(
            infos, False, False, False
        )
        accepted_paths = [i.PathName for i in accepted]
        assert _CAL_FILE   in accepted_paths
        assert _ERROR_FILE not in accepted_paths
        assert _ABORT_FILE not in accepted_paths

    def test_latest_protocol_keeps_newer_same_sensor(self):
        """FilterNewProtocols retains only the newest protocol per sensor.

        _CAL_FILE  (2024-01-15, rf12345, dsp67890) → older
        _NEWER_FILE (2024-02-02, rf12345, dsp67890) → newer
        Both accepted first, then FilterNewProtocols keeps only _NEWER_FILE.
        """
        files = [_CAL_FILE, _NEWER_FILE]
        infos, *_ = ProtocolInfoClass.PreParseProtcols(files)
        accepted, _ = ProtocolInfoClass.FilterProtocols(infos, False, False, False)
        # Sort as FilterProtocols does: by dsp then dateAndTime
        # Both have dsp67890 → stable → older (_CAL_FILE) first
        latest = ProtocolInfoClass.FilterNewProtocols(accepted)
        latest_paths = [i.PathName for i in latest]
        assert _NEWER_FILE in latest_paths
        assert _CAL_FILE   not in latest_paths

    def test_burnin_start_detection(self):
        """BurnIn_Start protocol contains Gen26_UseBurnInMeas[1];3 and (12a) marker."""
        infos, *_ = ProtocolInfoClass.PreParseProtcols([_BI_START])
        assert len(infos) == 1
        info = infos[0]
        # Pre-parse checks flags only — bErrorOccured/Abort/Limits should be clean
        assert info.bErrorOccured   is False
        assert info.bAbortCriterion is False

    def test_burnin_start_filtered_by_build_prot_path_type_list(self):
        """BurnIn_Start protocol is dropped by build_prot_path_type_list when
        include_burn_in_start=False because the file contains both
        Gen26_UseBurnInMeas[1];3 and the '(12a) BurnIn Start Check results:;ok'
        line (with ';ok' suffix — real-world format)."""
        from calibration_statistics_tool.shared.parse_controller import ParseController
        pc = ParseController()
        result = pc.build_prot_path_type_list([_BI_START], 0, include_burn_in_start=False)
        assert result == [], (
            "BurnIn_Start_Protocol should be filtered out (type='Filtered') "
            "when include_burn_in_start=False"
        )

    def test_burnin_start_included_when_flag_true(self):
        """Same protocol is kept when include_burn_in_start=True."""
        from calibration_statistics_tool.shared.parse_controller import ParseController
        pc = ParseController()
        result = pc.build_prot_path_type_list([_BI_START], 0, include_burn_in_start=True)
        assert len(result) == 1
        assert result[0]['type'] == 'BurnIn'
