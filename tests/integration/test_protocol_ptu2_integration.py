"""PST-75: Integration tests — Protocol ↔ PTU2 ↔ TxAntDiag search.

Covers the end-to-end search flow that the UI triggers when the user presses
"Import Protocol Directory":

  1.  GetAllProtocolsList  — finds all *proto*.txt files under a directory
  2.  PreParseProtcols     — reads each file to extract flags / metadata
  3.  FilterProtocols      — keeps / rejects based on EOL flags
  4.  walk_protocol_files  — derives file-search stems and calls callbacks to
                             find associated PTU2 / TxAntDiag files
  5.  The resulting ptu2_files_list / txantdiag_list link each protocol to
      its measurement files, ready for deduplication and parsing.

All file I/O is done inside pytest's tmp_path fixture so nothing touches
real project files.  The real ProtocolInfoClass text-based callbacks are
used for getfiltered_ptu2filelist and getfiltered_txantdiagramfilelist.
"""
import os
import sys

_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _root not in sys.path:
    sys.path.insert(0, _root)
for _sub in ['shared']:
    _p = os.path.join(_root, _sub)
    if _p not in sys.path:
        sys.path.insert(0, _p)

import pytest

from shared.protocolsTest import ProtocolInfoClass
from shared.parse_helpers import walk_protocol_files

# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------

_PROTOCOL_CONTENT = """\
Date:;{date}
Time:;{time}
Product-Serial:;{serial}
RF-Serial:;{rf}
Dsp-Serial:;{dsp}
E=0;
K=0;

Measurment Durations:

##### Measurements #####
"""

_PROTOCOL_BURNIN_CONTENT = """\
Date:;{date}
Time:;{time}
Product-Serial:;{serial}
RF-Serial:;{rf}
Dsp-Serial:;{dsp}
Gen26_UseBurnInMeas[1];3
E=0;
K=0;

Measurment Durations:
"""

_PROTOCOL_ERROR_CONTENT = """\
Date:;{date}
Time:;{time}
Product-Serial:;{serial}
RF-Serial:;{rf}
Dsp-Serial:;{dsp}
K=0;

Measurment Durations:
"""


def _write_protocol(directory, stem: str, serial: str, rf: str, dsp: str,
                     date: str = '2024-01-15', time_: str = '08:00:00',
                     suffix: str = 'Protocol', content_override: str | None = None):
    """Create a minimal protocol file; return its path as str."""
    filename = f'{stem}_{suffix}.txt'
    content = content_override or _PROTOCOL_CONTENT.format(
        date=date, time=time_, serial=serial, rf=rf, dsp=dsp
    )
    path = os.path.join(str(directory), filename)
    with open(path, 'w') as f:
        f.write(content)
    return path


def _write_ptu2(directory, stem: str, txant: int = 0, diagram: int = 0,
                direction: str = 'Az'):
    """Create a minimal PTU2 file that matches the given stem."""
    filename = f'{stem}_TxAnt{txant}_Diagram{diagram}_{direction}_ptu2.txt'
    path = os.path.join(str(directory), filename)
    with open(path, 'w') as f:
        f.write('PTU2 data placeholder\n')
    return path


def _write_tx_diag(directory, stem: str, txant: int = 0, diagram: int = 0):
    """Create a minimal TxAntDiag file that matches the given stem."""
    filename = f'{stem}_TxAnt{txant}_Diagram{diagram}.txt'
    path = os.path.join(str(directory), filename)
    with open(path, 'w') as f:
        f.write('TxAnt diagram data placeholder\n')
    return path


# ---------------------------------------------------------------------------
# Helper: run the full pipeline
# ---------------------------------------------------------------------------

def _run_pipeline(
    protocol_dir: str,
    search_ptu2: bool = True,
    search_txantdiag: bool = True,
    use_error: bool = False,
    use_abort: bool = True,
    use_limits: bool = True,
):
    all_protocols = ProtocolInfoClass.GetAllProtocolsList(protocol_dir)
    infos, *_ = ProtocolInfoClass.PreParseProtcols(all_protocols)
    accepted, _filtered = ProtocolInfoClass.FilterProtocols(
        infos,
        bUseFilesWithError=use_error,
        bUseFilesAbbortCriterion=use_abort,
        bUseFilesWIthLimitsExceeded=use_limits,
    )
    return walk_protocol_files(
        accepted,
        search_ptu2_files=search_ptu2,
        search_txantdiag_files=search_txantdiag,
        use_error=use_error,
        use_abort=use_abort,
        use_limits_exceeded=use_limits,
        get_ptu2_files_fn=ProtocolInfoClass.getfiltered_ptu2filelist,
        get_txantdiag_files_fn=ProtocolInfoClass.getfiltered_txantdiagramfilelist,
    )


# ===========================================================================
# 1. GetAllProtocolsList – directory scanning
# ===========================================================================

class TestGetAllProtocolsListIntegration:

    def test_empty_dir_returns_empty(self, tmp_path):
        found = ProtocolInfoClass.GetAllProtocolsList(str(tmp_path))
        assert found == []

    def test_finds_single_protocol(self, tmp_path):
        _write_protocol(tmp_path, '2024-01-15_stem', 'S1', 'rf1', 'dsp1')
        found = ProtocolInfoClass.GetAllProtocolsList(str(tmp_path))
        assert len(found) == 1

    def test_finds_multiple_protocols(self, tmp_path):
        _write_protocol(tmp_path, '2024-01-15_A', 'S1', 'rf1', 'dsp1')
        _write_protocol(tmp_path, '2024-01-16_B', 'S2', 'rf2', 'dsp2')
        _write_protocol(tmp_path, '2024-01-17_C', 'S3', 'rf3', 'dsp3')
        found = ProtocolInfoClass.GetAllProtocolsList(str(tmp_path))
        assert len(found) == 3

    def test_non_protocol_txt_not_found(self, tmp_path):
        (tmp_path / 'notes.txt').write_text('not a protocol')
        (tmp_path / 'readme.md').write_text('readme')
        found = ProtocolInfoClass.GetAllProtocolsList(str(tmp_path))
        assert found == []

    def test_subdirectory_protocols_found(self, tmp_path):
        subdir = tmp_path / 'sub'
        subdir.mkdir()
        _write_protocol(subdir, '2024-01-15_sub', 'S1', 'rf1', 'dsp1')
        found = ProtocolInfoClass.GetAllProtocolsList(str(tmp_path))
        assert len(found) == 1


# ===========================================================================
# 2. Protocol flag filtering in full pipeline
# ===========================================================================

class TestProtocolFlagFilteringIntegration:

    def test_clean_protocol_accepted_with_default_settings(self, tmp_path):
        _write_protocol(tmp_path, '2024-01-15_clean', 'S1', 'rf1', 'dsp1')
        ptu2_list, tx_list, acc, err, abort, limits = _run_pipeline(str(tmp_path))
        assert len(acc) == 1

    def test_error_protocol_rejected_when_use_error_false(self, tmp_path):
        content = _PROTOCOL_ERROR_CONTENT.format(
            date='2024-01-15', time='08:00:00', serial='S1', rf='rf1', dsp='dsp1'
        )
        _write_protocol(tmp_path, '2024-01-15_err', 'S1', 'rf1', 'dsp1',
                         content_override=content)
        ptu2_list, tx_list, acc, *_ = _run_pipeline(str(tmp_path), use_error=False)
        assert len(acc) == 0

    def test_error_protocol_accepted_when_use_error_true(self, tmp_path):
        content = _PROTOCOL_ERROR_CONTENT.format(
            date='2024-01-15', time='08:00:00', serial='S1', rf='rf1', dsp='dsp1'
        )
        _write_protocol(tmp_path, '2024-01-15_err', 'S1', 'rf1', 'dsp1',
                         content_override=content)
        ptu2_list, tx_list, acc, err_list, *_ = _run_pipeline(
            str(tmp_path), use_error=True
        )
        assert len(acc) == 1

    def test_user_error_list_populated(self, tmp_path):
        """acc_error_prot_list includes protocol path when use_error=True."""
        content = _PROTOCOL_ERROR_CONTENT.format(
            date='2024-01-15', time='08:00:00', serial='S1', rf='rf1', dsp='dsp1'
        )
        path = _write_protocol(tmp_path, '2024-01-15_err', 'S1', 'rf1', 'dsp1',
                                 content_override=content)
        _, _, _, err_list, *_ = _run_pipeline(str(tmp_path), use_error=True)
        norm = [os.path.normpath(p) for p in err_list]
        assert os.path.normpath(path) in norm

    def test_mixed_clean_and_error_only_clean_accepted(self, tmp_path):
        _write_protocol(tmp_path, '2024-01-15_clean', 'S1', 'rf1', 'dsp1')
        content = _PROTOCOL_ERROR_CONTENT.format(
            date='2024-01-16', time='09:00:00', serial='S2', rf='rf2', dsp='dsp2'
        )
        _write_protocol(tmp_path, '2024-01-16_err', 'S2', 'rf2', 'dsp2',
                         content_override=content)
        _, _, acc, *_ = _run_pipeline(str(tmp_path), use_error=False)
        assert len(acc) == 1


# ===========================================================================
# 3. PTU2 file discovery via walk_protocol_files
# ===========================================================================

class TestPtu2FileDiscoveryIntegration:

    def _stem(self, date='2024-01-15', time_='08-00-00', rf='rf12345', dsp='dsp67890'):
        return f'{date}_{time_}_Tuner1_{rf}_{dsp}_Seq1'

    def test_search_ptu2_finds_matching_files(self, tmp_path):
        stem = self._stem()
        prot = _write_protocol(tmp_path, stem, 'S1', 'rf12345', 'dsp67890')
        _write_ptu2(tmp_path, stem, txant=0, diagram=0, direction='Az')
        _write_ptu2(tmp_path, stem, txant=1, diagram=2, direction='El')

        ptu2_list, *_ = _run_pipeline(str(tmp_path), search_ptu2=True, search_txantdiag=False)
        assert len(ptu2_list) == 1
        assert ptu2_list[0]['protocolPath'] == prot.replace('\\', '/')  or \
               os.path.normpath(ptu2_list[0]['protocolPath']) == os.path.normpath(prot)
        assert len(ptu2_list[0]['ptu2FilesList']) == 2

    def test_search_ptu2_false_returns_empty_ptu2_list(self, tmp_path):
        stem = self._stem()
        _write_protocol(tmp_path, stem, 'S1', 'rf12345', 'dsp67890')
        _write_ptu2(tmp_path, stem)

        ptu2_list, *_ = _run_pipeline(str(tmp_path), search_ptu2=False, search_txantdiag=False)
        assert ptu2_list == []

    def test_no_matching_ptu2_yields_empty_files_list(self, tmp_path):
        stem = self._stem()
        _write_protocol(tmp_path, stem, 'S1', 'rf12345', 'dsp67890')
        # No PTU2 files created

        ptu2_list, *_ = _run_pipeline(str(tmp_path), search_ptu2=True, search_txantdiag=False)
        assert len(ptu2_list) == 1
        assert ptu2_list[0]['ptu2FilesList'] == []

    def test_ptu2_files_linked_to_correct_protocol(self, tmp_path):
        """Two protocols: each should link only to its own PTU2 files."""
        stem_a = self._stem(dsp='dsp11111')
        stem_b = self._stem(dsp='dsp22222')
        prot_a = _write_protocol(tmp_path, stem_a, 'SA', 'rfA', 'dsp11111')
        prot_b = _write_protocol(tmp_path, stem_b, 'SB', 'rfB', 'dsp22222')
        _write_ptu2(tmp_path, stem_a)        # belongs to prot_a
        _write_ptu2(tmp_path, stem_b)        # belongs to prot_b

        ptu2_list, tx_list, acc, *_ = _run_pipeline(
            str(tmp_path), search_ptu2=True, search_txantdiag=False
        )
        # Build a map protocol_path → ptu2 files
        path_map = {
            os.path.normpath(e['protocolPath']): e['ptu2FilesList']
            for e in ptu2_list
        }
        a_norm = os.path.normpath(prot_a)
        b_norm = os.path.normpath(prot_b)
        assert a_norm in path_map and len(path_map[a_norm]) == 1
        assert b_norm in path_map and len(path_map[b_norm]) == 1
        # Verify cross-contamination does not occur
        assert not any(stem_b in p for p in path_map[a_norm])
        assert not any(stem_a in p for p in path_map[b_norm])


# ===========================================================================
# 4. TxAntDiag file discovery via walk_protocol_files
# ===========================================================================

class TestTxAntDiagDiscoveryIntegration:

    def _stem(self, dsp='dsp67890'):
        return f'2024-01-15_08-00-00_Tuner1_rf12345_{dsp}_Seq1'

    def test_search_txantdiag_finds_matching_files(self, tmp_path):
        stem = self._stem()
        prot = _write_protocol(tmp_path, stem, 'S1', 'rf12345', 'dsp67890')
        _write_tx_diag(tmp_path, stem, txant=0, diagram=0)
        _write_tx_diag(tmp_path, stem, txant=1, diagram=1)

        _, tx_list, *_ = _run_pipeline(str(tmp_path), search_ptu2=False, search_txantdiag=True)
        assert len(tx_list) == 1
        assert len(tx_list[0]['txAntDiagList']) == 2

    def test_search_txantdiag_false_returns_empty(self, tmp_path):
        stem = self._stem()
        _write_protocol(tmp_path, stem, 'S1', 'rf12345', 'dsp67890')
        _write_tx_diag(tmp_path, stem)

        _, tx_list, *_ = _run_pipeline(str(tmp_path), search_ptu2=False, search_txantdiag=False)
        assert tx_list == []

    def test_txantdiag_ptu2_files_excluded(self, tmp_path):
        """getfiltered_txantdiagramfilelist must not return _ptu2.txt files."""
        stem = self._stem()
        _write_protocol(tmp_path, stem, 'S1', 'rf12345', 'dsp67890')
        _write_tx_diag(tmp_path, stem)        # real TxDiag file
        _write_ptu2(tmp_path, stem)            # PTU2 (should be excluded)

        _, tx_list, *_ = _run_pipeline(str(tmp_path), search_ptu2=False, search_txantdiag=True)
        # Check only the filename (not the full path whose tmp dir name may contain 'ptu2')
        for f in tx_list[0]['txAntDiagList']:
            assert '_ptu2' not in os.path.basename(f).lower()

    def test_no_matching_txantdiag_yields_empty_list(self, tmp_path):
        stem = self._stem()
        _write_protocol(tmp_path, stem, 'S1', 'rf12345', 'dsp67890')
        # No TxAntDiag files

        _, tx_list, *_ = _run_pipeline(str(tmp_path), search_ptu2=False, search_txantdiag=True)
        assert len(tx_list) == 1
        assert tx_list[0]['txAntDiagList'] == []


# ===========================================================================
# 5. Combined PTU2 + TxAntDiag search
# ===========================================================================

class TestCombinedPtu2TxAntDiagIntegration:

    def test_both_searches_return_independent_results(self, tmp_path):
        stem = '2024-01-15_09-00-00_Tuner1_rfX_dspY_Seq1'
        _write_protocol(tmp_path, stem, 'S1', 'rfX', 'dspY')
        _write_ptu2(tmp_path, stem, txant=0)
        _write_ptu2(tmp_path, stem, txant=1)
        _write_tx_diag(tmp_path, stem, txant=0)

        ptu2_list, tx_list, acc, *_ = _run_pipeline(
            str(tmp_path), search_ptu2=True, search_txantdiag=True
        )
        assert len(acc) == 1
        assert len(ptu2_list) == 1
        assert len(ptu2_list[0]['ptu2FilesList']) == 2
        assert len(tx_list) == 1
        assert len(tx_list[0]['txAntDiagList']) == 1

    def test_acc_prot_list_contains_protocol_path(self, tmp_path):
        stem = '2024-01-15_stem'
        prot = _write_protocol(tmp_path, stem, 'S1', 'rfX', 'dspY')
        _, _, acc, *_ = _run_pipeline(str(tmp_path))
        norm_acc = [os.path.normpath(p) for p in acc]
        assert os.path.normpath(prot) in norm_acc

    def test_multiple_protocols_multiple_file_sets(self, tmp_path):
        for i in range(3):
            stem = f'2024-0{i+1}-01_08-00-00_Tuner1_rfS{i}_dspD{i}_Seq1'
            _write_protocol(tmp_path, stem, f'S{i}', f'rfS{i}', f'dspD{i}',
                             date=f'2024-0{i+1}-01')
            _write_ptu2(tmp_path, stem)
            _write_tx_diag(tmp_path, stem)

        ptu2_list, tx_list, acc, *_ = _run_pipeline(str(tmp_path))
        assert len(acc) == 3
        assert len(ptu2_list) == 3
        assert len(tx_list) == 3
        # Each protocol maps to exactly one PTU2 and one TxAntDiag file
        for entry in ptu2_list:
            assert len(entry['ptu2FilesList']) == 1
        for entry in tx_list:
            assert len(entry['txAntDiagList']) == 1


# ===========================================================================
# 6. Real fixture files integration smoke test
# ===========================================================================

class TestRealFixtureFilesSmoke:
    """Smoke-test against the real measurement_data/protocol_files/ directory."""

    _PROT_DIR = os.path.join(_root, 'measurement_data', 'protocol_files')

    def test_finds_at_least_two_original_fixtures(self):
        found = ProtocolInfoClass.GetAllProtocolsList(self._PROT_DIR)
        assert len(found) >= 2

    def test_pre_parse_all_fixture_protocols_succeed(self):
        found = ProtocolInfoClass.GetAllProtocolsList(self._PROT_DIR)
        infos, *_ = ProtocolInfoClass.PreParseProtcols(found)
        assert len(infos) == len(found)

    def test_filter_flow_with_default_ui_settings(self):
        """Default: useError=False, useAbort=True, useLimits=True."""
        found = ProtocolInfoClass.GetAllProtocolsList(self._PROT_DIR)
        infos, *_ = ProtocolInfoClass.PreParseProtcols(found)
        accepted, filtered = ProtocolInfoClass.FilterProtocols(
            infos, False, True, True
        )
        # At minimum the two clean original fixtures should be accepted
        assert len(accepted) >= 2

    def test_walk_protocol_files_no_crash(self):
        """walk_protocol_files runs without error on real protocol dir."""
        found = ProtocolInfoClass.GetAllProtocolsList(self._PROT_DIR)
        infos, *_ = ProtocolInfoClass.PreParseProtcols(found)
        accepted, _ = ProtocolInfoClass.FilterProtocols(infos, False, True, True)
        ptu2_list, tx_list, acc, *_ = walk_protocol_files(
            accepted,
            search_ptu2_files=True,
            search_txantdiag_files=True,
            use_error=False,
            use_abort=True,
            use_limits_exceeded=True,
            get_ptu2_files_fn=ProtocolInfoClass.getfiltered_ptu2filelist,
            get_txantdiag_files_fn=ProtocolInfoClass.getfiltered_txantdiagramfilelist,
        )
        # Should produce one entry per accepted protocol (even if no files found)
        assert len(ptu2_list) == len(accepted)
        assert len(tx_list)   == len(accepted)
        assert len(acc)       == len(accepted)

    def test_subfiles_fixture_found_by_pipeline(self):
        """PTU2 and TxAntDiag files inside the real subfiles/ sub-directory
        are discovered because getfiltered_ptu2filelist / getfiltered_txant-
        diagramfilelist both use os.walk(), which recurses into sub-dirs."""
        ptu2_list, tx_list, *_ = walk_protocol_files(
            ProtocolInfoClass.FilterProtocols(
                ProtocolInfoClass.PreParseProtcols(
                    ProtocolInfoClass.GetAllProtocolsList(self._PROT_DIR)
                )[0],
                False, True, True,
            )[0],
            search_ptu2_files=True,
            search_txantdiag_files=True,
            use_error=False,
            use_abort=True,
            use_limits_exceeded=True,
            get_ptu2_files_fn=ProtocolInfoClass.getfiltered_ptu2filelist,
            get_txantdiag_files_fn=ProtocolInfoClass.getfiltered_txantdiagramfilelist,
        )

        all_ptu2 = [
            os.path.normpath(f)
            for entry in ptu2_list for f in entry['ptu2FilesList']
        ]
        all_tx = [
            os.path.normpath(f)
            for entry in tx_list for f in entry['txAntDiagList']
        ]

        subfiles_dir = os.path.join(self._PROT_DIR, 'subfiles')

        # Both Az and El PTU2 scans must be discovered (linked to the cal protocol)
        ptu2_stem = '2024-01-15_12-30-45_Tuner1_rf12345_dsp67890_Seq1_TxAnt1_Diagram1_'
        for ptu2_suffix in ('Az_ptu2.txt', 'El_ptu2.txt'):
            expected = os.path.normpath(os.path.join(subfiles_dir, ptu2_stem + ptu2_suffix))
            assert expected in all_ptu2, (
                f"Subfolder PTU2 file '{ptu2_suffix}' not discovered.\n"
                f"Found PTU2 files: {all_ptu2}"
            )

        # All three TxAntDiag files must be discovered (clean-stem protocol:
        # no TxAnt/Diagram in the protocol name, so file names are unambiguous)
        txant_stem = '2024-01-17_08-00-00_Tuner5_rf50000_dsp60000_Seq5_'
        for tx_suffix in (
            'TxAnt0_Diagram0.txt',
            'TxAnt1_Diagram1.txt',
            'TxAnt2_Diagram2.txt',
        ):
            expected = os.path.normpath(os.path.join(subfiles_dir, txant_stem + tx_suffix))
            assert expected in all_tx, (
                f"Subfolder TxAntDiag file '{tx_suffix}' not discovered.\n"
                f"Found TxAnt files: {all_tx}"
            )


# ===========================================================================
# 7. Subfolder PTU2 / TxAntDiag file discovery (tmp_path)
# ===========================================================================

class TestSubfolderDiscovery:
    """PTU2 and TxAntDiag files in sub-directories of the protocol folder are
    found because getfiltered_ptu2filelist / getfiltered_txantdiagramfilelist
    both use os.walk(), which recurses into sub-directories."""

    _STEM = '2024-03-10_10-00-00_Tuner1_rfSUB_dspSUB_Seq1'

    def test_ptu2_in_subfolder_is_found(self, tmp_path):
        _write_protocol(tmp_path, self._STEM, 'S_sub', 'rfSUB', 'dspSUB')
        subdir = tmp_path / 'associated_files'
        subdir.mkdir()
        ptu2_path = _write_ptu2(subdir, self._STEM)

        ptu2_list, *_ = _run_pipeline(str(tmp_path), search_ptu2=True, search_txantdiag=False)
        found = [os.path.normpath(p) for p in ptu2_list[0]['ptu2FilesList']]
        assert os.path.normpath(ptu2_path) in found

    def test_txantdiag_in_subfolder_is_found(self, tmp_path):
        _write_protocol(tmp_path, self._STEM, 'S_sub', 'rfSUB', 'dspSUB')
        subdir = tmp_path / 'associated_files'
        subdir.mkdir()
        tx_path = _write_tx_diag(subdir, self._STEM)

        _, tx_list, *_ = _run_pipeline(str(tmp_path), search_ptu2=False, search_txantdiag=True)
        found = [os.path.normpath(p) for p in tx_list[0]['txAntDiagList']]
        assert os.path.normpath(tx_path) in found

    def test_both_in_subfolder_found_simultaneously(self, tmp_path):
        _write_protocol(tmp_path, self._STEM, 'S_sub', 'rfSUB', 'dspSUB')
        subdir = tmp_path / 'associated_files'
        subdir.mkdir()
        ptu2_path = _write_ptu2(subdir, self._STEM)
        tx_path = _write_tx_diag(subdir, self._STEM)

        ptu2_list, tx_list, *_ = _run_pipeline(str(tmp_path), search_ptu2=True, search_txantdiag=True)
        found_ptu2 = [os.path.normpath(p) for p in ptu2_list[0]['ptu2FilesList']]
        found_tx = [os.path.normpath(p) for p in tx_list[0]['txAntDiagList']]
        assert os.path.normpath(ptu2_path) in found_ptu2
        assert os.path.normpath(tx_path) in found_tx

    def test_deeply_nested_subfolder_found(self, tmp_path):
        """os.walk recurses through multiple nesting levels."""
        _write_protocol(tmp_path, self._STEM, 'S_sub', 'rfSUB', 'dspSUB')
        deep = tmp_path / 'level1' / 'level2' / 'level3'
        deep.mkdir(parents=True)
        ptu2_path = _write_ptu2(deep, self._STEM)

        ptu2_list, *_ = _run_pipeline(str(tmp_path), search_ptu2=True, search_txantdiag=False)
        found = [os.path.normpath(p) for p in ptu2_list[0]['ptu2FilesList']]
        assert os.path.normpath(ptu2_path) in found

    def test_files_in_sibling_protocol_dir_not_cross_contaminated(self, tmp_path):
        """Files for protocol A in a subfolder are not attributed to protocol B."""
        stem_a = '2024-03-10_10-00-00_Tuner1_rfAAA_dspAAA_Seq1'
        stem_b = '2024-03-10_11-00-00_Tuner1_rfBBB_dspBBB_Seq1'
        _write_protocol(tmp_path, stem_a, 'SA', 'rfAAA', 'dspAAA')
        _write_protocol(tmp_path, stem_b, 'SB', 'rfBBB', 'dspBBB')

        subdir = tmp_path / 'only_for_a'
        subdir.mkdir()
        ptu2_a = _write_ptu2(subdir, stem_a)

        ptu2_list, *_ = _run_pipeline(str(tmp_path), search_ptu2=True, search_txantdiag=False)
        path_map = {
            os.path.normpath(e['protocolPath']): [os.path.normpath(p) for p in e['ptu2FilesList']]
            for e in ptu2_list
        }
        prot_a = os.path.normpath(str(tmp_path / f'{stem_a}_Protocol.txt'))
        prot_b = os.path.normpath(str(tmp_path / f'{stem_b}_Protocol.txt'))
        assert os.path.normpath(ptu2_a) in path_map[prot_a]
        assert os.path.normpath(ptu2_a) not in path_map[prot_b]
