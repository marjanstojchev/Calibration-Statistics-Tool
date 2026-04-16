"""tests/test_protocol_gui_logic.py

Protocol-tab GUI logic — ISTQB-classified White-box Branch/Condition Coverage.

The tests are organised by the GUI granulation:
  ① Choose Protocol Directory / File List
  ② Protocol Type radio buttons: BurnIn / Calibration / Auto Recognition
  ③ Use-protocol checkboxes: Latest / BurnIn-start / EOL Error / Abort / Limits
  ④ Search PTU2 files / Search TxAntDiag files checkboxes
  ⑤ Sensor Muster checkbox

ISTQB Classification tags used in docstrings:
  [SMOKE]       Basic sanity — pipeline runs without errors, main path works.
  [FUNCTIONAL]  Verifies a specific GUI-feature requirement.
  [REGRESSION]  Guards against previously reported and fixed defects.
  [BOUNDARY]    Edge / limiting values of loops, comparisons, or list sizes.
  [INTEGRATION] Two or more components exercised together.

White-box technique: Branch + Condition Coverage (ISTQB MC/DC).

Branches targeted that are NOT exercised by the existing test suite:
  get_protocol_type auto-detect:
    • Gen26 integer value ∉ {0, 3}    → 'Unclear'  (the ``else`` inside val check)
    • Gen26 value is non-integer       → 'Unclear'  (checkInt → False branch)
    • Gen26 line without ';'           → 'Unclear'  (len(parts) <= 1 branch)
    • BurnIn type + no (12a) line      → kept       (filter_prot stays False)
    • Calibration type + (12a) line   → kept        (prot_type ≠ 'BurnIn' short-circuits)
    • Force-mode early return          → no auto-detect, (12a) line irrelevant
  FilterNewProtocols loop:
    • date1 > date2 branch             (reverse-sorted input pair)
    • Three same-sensor in ascending order — exercises "not last element" skip
  FilterProtocols compound flag condition:
    • error ∧ abort both True; use_error=True, use_abort=False → rejected by abort
  walk_protocol_files filename stem:
    • lowercase 'protocol' stripped from filename
    • 'Protocol_Chip' stripped before 'Protocol'
  Combined filter pipeline:
    • Older-error + newer-clean same sensor; use_error=False + use_latest
"""
from __future__ import annotations

import os
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _sub in ['shared']:
    _p = os.path.join(_root, _sub)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from shared.parse_controller import ParseController
from shared.parse_helpers import deduplicate_protocol_list, walk_protocol_files
from shared.protocolsTest import ProtocolInfoClass

# ---------------------------------------------------------------------------
# Fixture file paths (same as test_protocols.py)
# ---------------------------------------------------------------------------

_PROT_DIR  = os.path.join(_root, 'measurement_data', 'protocol_files')
_CAL_FILE  = os.path.join(_PROT_DIR, '2024-01-15_12-30-45_Tuner1_rf12345_dsp67890_Seq1_TxAnt1_Diagram1_Protocol.txt')
_BURN_FILE = os.path.join(_PROT_DIR, '2024-01-15_10-15-20_Tuner2_rf12346_dsp67891_Seq2_TxAnt2_Diagram2_BurnIn_Protocol.txt')
_ERROR_FILE = os.path.join(_PROT_DIR, '2024-02-01_08-00-00_Tuner1_rf11111_dsp22222_Seq1_TxAnt0_Diagram0_Error_Protocol.txt')
_ABORT_FILE = os.path.join(_PROT_DIR, '2024-02-01_09-00-00_Tuner1_rf11112_dsp22223_Seq1_TxAnt0_Diagram0_Abort_Protocol.txt')
_LIMITS_FILE = os.path.join(_PROT_DIR, '2024-02-01_10-00-00_Tuner1_rf11113_dsp22224_Seq1_TxAnt0_Diagram0_Limits_Protocol.txt')
_ALL_FLAGS  = os.path.join(_PROT_DIR, '2024-02-01_11-00-00_Tuner1_rf11114_dsp22225_Seq1_TxAnt0_Diagram0_AllFlags_Protocol.txt')
_BI_START   = os.path.join(_PROT_DIR, '2024-02-01_12-00-00_Tuner1_rf12345_dsp67890_Seq1_TxAnt0_Diagram0_BurnIn_Start_Protocol.txt')
_NEWER_FILE = os.path.join(_PROT_DIR, '2024-02-02_08-00-00_Tuner1_rf12345_dsp67890_Seq1_TxAnt0_Diagram0_NewerSameSensor_Protocol.txt')

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _make_info(
    serial: str = 'S1',
    rf: str = 'rf1',
    dsp: str = 'dsp1',
    date_time: str = '2024-01-01-00:00:00',
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


def _make_pc() -> ParseController:
    return ParseController()


def _noop_fn(_dir, _arg):
    return []


def _mock_ptu2_fn(dir_path, _pattern):
    return [f'{dir_path}/found_ptu2.txt']


def _mock_txant_fn(dir_path, _stem):
    return [f'{dir_path}/found_tx.txt']


# ===========================================================================
# [SMOKE] Basic pipeline sanity
# ===========================================================================

class TestSmoke:
    """[SMOKE] Minimal end-to-end sanity: pipeline completes without errors
    and returns a sensible non-empty result with the bundled fixture files."""

    def test_preParse_then_filter_accepts_at_least_one_clean_protocol(self):
        """[SMOKE] Default UI flags (no error, allow abort+limits) → at least one
        protocol is accepted from the fixture directory."""
        infos, *_ = ProtocolInfoClass.PreParseProtcols([_CAL_FILE, _BURN_FILE])
        accepted, _ = ProtocolInfoClass.FilterProtocols(
            infos,
            bUseFilesWithError=False,
            bUseFilesAbbortCriterion=True,
            bUseFilesWIthLimitsExceeded=True,
        )
        assert len(accepted) >= 1

    def test_force_burnin_mode_processes_file_list(self, tmp_path):
        """[SMOKE] Force-BurnIn mode (radio=1) on a list of files: all reported BurnIn."""
        paths = []
        for i in range(3):
            p = tmp_path / f'p{i}_Protocol.txt'
            p.write_text('E=0;\nK=0;\n')
            paths.append(str(p))
        pc = _make_pc()
        result = pc.build_prot_path_type_list(paths, burn_in_cal_mode=1, include_burn_in_start=False)
        assert len(result) == 3
        assert all(r['type'] == 'BurnIn' for r in result)

    def test_build_prot_path_type_list_with_mixed_fixture_files(self):
        """[SMOKE][REGRESSION] PST-T5/PST-T6: Auto-detect with real fixture files.
        PST-T5: Calibration fixture must be detected as 'Calibration'.
        PST-T6: BurnIn fixture must be detected as 'BurnIn'."""
        pc = _make_pc()
        result = pc.build_prot_path_type_list(
            [_CAL_FILE, _BURN_FILE], burn_in_cal_mode=0, include_burn_in_start=True
        )
        types = {os.path.basename(r['protocolPath']): r['type'] for r in result}
        assert len(result) == 2
        assert types[os.path.basename(_CAL_FILE)]  == 'Calibration', 'PST-T5'
        assert types[os.path.basename(_BURN_FILE)] == 'BurnIn',      'PST-T6'


# ===========================================================================
# [FUNCTIONAL] ② Protocol Type: Auto Recognition — branch coverage
# ===========================================================================

class TestProtocolTypeAutoDetectBranches:
    """[FUNCTIONAL] White-box: branch coverage for get_protocol_type auto-detect
    mode. Targets the ``else`` branches and short-circuit conditions NOT covered
    by the existing tests in test_parse_controller.py."""

    def _write(self, tmp_path, name: str, content: str) -> str:
        p = tmp_path / name
        p.write_text(content)
        return str(p)

    # --- Gen26 integer value ∉ {0, 3} → else branch → 'Unclear' ---------------

    def test_gen26_value_one_returns_unclear(self, tmp_path):
        """[FUNCTIONAL] Gen26_UseBurnInMeas[1];1 hits the ``else`` int branch → 'Unclear'."""
        path = self._write(tmp_path, 'p.txt', 'Gen26_UseBurnInMeas[1];1\n')
        assert _make_pc().get_protocol_type(path, 0, False) == 'Unclear'

    def test_gen26_value_two_returns_unclear(self, tmp_path):
        """[FUNCTIONAL] Gen26_UseBurnInMeas[1];2 → 'Unclear' (else branch)."""
        path = self._write(tmp_path, 'p.txt', 'Gen26_UseBurnInMeas[1];2\n')
        assert _make_pc().get_protocol_type(path, 0, False) == 'Unclear'

    def test_gen26_value_five_returns_unclear(self, tmp_path):
        """[FUNCTIONAL] Any integer ∉ {0,3} → else branch → 'Unclear'."""
        path = self._write(tmp_path, 'p.txt', 'Gen26_UseBurnInMeas[1];5\n')
        assert _make_pc().get_protocol_type(path, 0, False) == 'Unclear'

    # --- Gen26 non-integer value → checkInt → False branch -------------------

    def test_gen26_non_integer_value_returns_unclear(self, tmp_path):
        """[FUNCTIONAL] Gen26_UseBurnInMeas[1];abc → checkInt(False) branch → 'Unclear'."""
        path = self._write(tmp_path, 'p.txt', 'Gen26_UseBurnInMeas[1];abc\n')
        assert _make_pc().get_protocol_type(path, 0, False) == 'Unclear'

    def test_gen26_float_value_returns_unclear(self, tmp_path):
        """[FUNCTIONAL] '1.5' is not a valid int → checkInt(False) → 'Unclear'."""
        path = self._write(tmp_path, 'p.txt', 'Gen26_UseBurnInMeas[1];1.5\n')
        # checkInt uses int() which raises on '1.5'
        assert _make_pc().get_protocol_type(path, 0, False) == 'Unclear'

    # --- Gen26 line without semicolon → len(parts) <= 1 branch ---------------

    def test_gen26_no_semicolon_line_returns_unclear(self, tmp_path):
        """[FUNCTIONAL] Gen26 tag with no ';' → len(parts)==1 → type stays 'Unclear'."""
        path = self._write(tmp_path, 'p.txt', 'Gen26_UseBurnInMeas[1]\n')
        assert _make_pc().get_protocol_type(path, 0, False) == 'Unclear'

    # --- BurnIn + NO (12a) line: filter_prot stays False → NOT 'Filtered' ----

    def test_burnin_without_start_line_not_filtered_even_include_false(self, tmp_path):
        """[FUNCTIONAL] BurnIn protocol without (12a) line: filter_prot=False →
        NOT filtered even when include_burn_in_start=False.
        Exercises the ``and filter_prot`` short-circuit = False."""
        path = self._write(tmp_path, 'p.txt', 'Gen26_UseBurnInMeas[1];3\n')
        result = _make_pc().get_protocol_type(path, 0, include_burn_in_start=False)
        assert result == 'BurnIn'

    # --- Calibration + (12a) line → prot_type != 'BurnIn' → NOT 'Filtered' ---

    def test_calibration_with_burnin_start_line_not_filtered(self, tmp_path):
        """[FUNCTIONAL] Calibration protocol that also contains the (12a) start
        line is NOT filtered: prot_type='Calibration' short-circuits ``and prot_type == 'BurnIn'``."""
        content = 'Gen26_UseBurnInMeas[1];0\n(12a) BurnIn Start Check results:;ok\n'
        path = self._write(tmp_path, 'p.txt', content)
        result = _make_pc().get_protocol_type(path, 0, include_burn_in_start=False)
        assert result == 'Calibration'

    def test_unclear_with_burnin_start_line_not_filtered(self, tmp_path):
        """[FUNCTIONAL] 'Unclear' protocol with (12a) line also NOT filtered
        (prot_type ≠ 'BurnIn')."""
        path = self._write(tmp_path, 'p.txt', '(12a) BurnIn Start Check results:\n')
        result = _make_pc().get_protocol_type(path, 0, include_burn_in_start=False)
        assert result == 'Unclear'

    # --- Force mode early-return: (12a) line is irrelevant -------------------

    def test_force_burnin_mode_ignores_start_filter_line(self, tmp_path):
        """[FUNCTIONAL] Force mode=1 returns 'BurnIn' immediately without reading
        the file — the (12a) filter line is never seen, no 'Filtered' possible."""
        content = 'Gen26_UseBurnInMeas[1];3\n(12a) BurnIn Start Check results:;ok\n'
        path = self._write(tmp_path, 'p.txt', content)
        result = _make_pc().get_protocol_type(path, 1, include_burn_in_start=False)
        assert result == 'BurnIn'

    def test_force_cal_mode_ignores_burnin_content_and_start_line(self, tmp_path):
        """[FUNCTIONAL] Force mode=2 returns 'Calibration' without reading the file."""
        content = 'Gen26_UseBurnInMeas[1];3\n(12a) BurnIn Start Check results:;ok\n'
        path = self._write(tmp_path, 'p.txt', content)
        result = _make_pc().get_protocol_type(path, 2, include_burn_in_start=False)
        assert result == 'Calibration'


# ===========================================================================
# [FUNCTIONAL] ② Protocol Type + ③ BurnIn-start — batch scenarios
# ===========================================================================

class TestBurnInStartBatchScenarios:
    """[FUNCTIONAL] Batch-level behavior of build_prot_path_type_list with
    mixed BurnIn-start and normal protocols."""

    def test_batch_burnin_start_excluded_normal_protocols_kept(self, tmp_path):
        """[FUNCTIONAL] Batch of 3: one BurnIn-start (to be excluded), two normal.
        include_burn_in_start=False → only 2 returned."""
        cal = tmp_path / 'cal_Protocol.txt'
        cal.write_text('Gen26_UseBurnInMeas[1];0\n')

        burn = tmp_path / 'burn_Protocol.txt'
        burn.write_text('Gen26_UseBurnInMeas[1];3\n')

        start = tmp_path / 'bistart_Protocol.txt'
        start.write_text('Gen26_UseBurnInMeas[1];3\n(12a) BurnIn Start Check results:;ok\n')

        pc = _make_pc()
        result = pc.build_prot_path_type_list(
            [str(cal), str(burn), str(start)],
            burn_in_cal_mode=0,
            include_burn_in_start=False,
        )
        paths = [r['protocolPath'] for r in result]
        assert len(result) == 2
        assert str(start) not in paths
        assert str(cal)   in paths
        assert str(burn)  in paths

    def test_batch_burnin_start_all_included_when_flag_true(self, tmp_path):
        """[FUNCTIONAL] include_burn_in_start=True → BurnIn-start protocol kept."""
        start = tmp_path / 'bistart_Protocol.txt'
        start.write_text('Gen26_UseBurnInMeas[1];3\n(12a) BurnIn Start Check results:;ok\n')

        pc = _make_pc()
        result = pc.build_prot_path_type_list(
            [str(start)], burn_in_cal_mode=0, include_burn_in_start=True
        )
        assert len(result) == 1
        assert result[0]['type'] == 'BurnIn'

    def test_force_burnin_mode_batch_all_classified_burnin_none_filtered(self, tmp_path):
        """[FUNCTIONAL] Force mode=1 batch: any file content is overridden → no
        file is ever classified as 'Filtered', all returned as 'BurnIn'."""
        start = tmp_path / 'bistart_Protocol.txt'
        start.write_text('Gen26_UseBurnInMeas[1];3\n(12a) BurnIn Start Check results:;ok\n')
        cal = tmp_path / 'cal_Protocol.txt'
        cal.write_text('Gen26_UseBurnInMeas[1];0\n')

        pc = _make_pc()
        result = pc.build_prot_path_type_list(
            [str(start), str(cal)], burn_in_cal_mode=1, include_burn_in_start=False
        )
        assert len(result) == 2
        assert all(r['type'] == 'BurnIn' for r in result)

    def test_real_burnin_start_fixture_excluded_by_default(self):
        """[FUNCTIONAL] Real BurnIn_Start fixture file excluded when
        include_burn_in_start=False (uses actual file on disk)."""
        pc = _make_pc()
        result = pc.build_prot_path_type_list(
            [_BI_START], burn_in_cal_mode=0, include_burn_in_start=False
        )
        assert result == []

    def test_real_burnin_start_fixture_included_when_flag_true(self):
        """[FUNCTIONAL] Same real fixture is included when flag=True."""
        pc = _make_pc()
        result = pc.build_prot_path_type_list(
            [_BI_START], burn_in_cal_mode=0, include_burn_in_start=True
        )
        assert len(result) == 1
        assert result[0]['type'] == 'BurnIn'


# ===========================================================================
# [FUNCTIONAL] ③ EOL flag compound conditions — missing MC/DC paths
# ===========================================================================

class TestEolFlagCompoundConditions:
    """[FUNCTIONAL] Branch/condition coverage for FilterProtocols compound boolean.

    The rejection condition is:
        reject = (not use_error AND error) OR (not use_abort AND abort) OR (not use_limits AND limits)

    Tests below exercise compound paths where multiple flags are set on the
    protocol but only some use-flags are True."""

    def _run(self, infos, use_error=False, use_abort=False, use_limits=False):
        accepted, filtered = ProtocolInfoClass.FilterProtocols(
            infos, use_error, use_abort, use_limits
        )
        return [i.PathName for i in accepted], [i.PathName for i in filtered]

    def test_error_and_abort_both_set_use_error_true_use_abort_false_rejected_by_abort(self):
        """[FUNCTIONAL] Protocol has both error+abort flags. use_error=True (error accepted)
        but use_abort=False → abort clause fires → protocol REJECTED.
        Tests that True OR True short-circuit still rejects."""
        info = _make_info(error=True, abort=True, path='ea.txt')
        accepted, filtered = self._run([info], use_error=True, use_abort=False, use_limits=True)
        assert 'ea.txt' not in accepted
        assert 'ea.txt' in filtered

    def test_abort_and_limits_both_set_use_abort_false_use_limits_true_rejected(self):
        """[FUNCTIONAL] Protocol has abort+limits. use_abort=False → abort clause fires
        even though limits are accepted. Protocol rejected."""
        info = _make_info(abort=True, limits=True, path='al.txt')
        accepted, filtered = self._run([info], use_error=True, use_abort=False, use_limits=True)
        assert 'al.txt' not in accepted
        assert 'al.txt' in filtered

    def test_all_three_flags_set_all_use_true_accepted(self):
        """[FUNCTIONAL] All three flags on protocol, all three use-flags True → accepted.
        Tests that all three `not use_X AND flag` clauses evaluate to False."""
        info = _make_info(error=True, abort=True, limits=True, path='all.txt')
        accepted, _ = self._run([info], use_error=True, use_abort=True, use_limits=True)
        assert 'all.txt' in accepted

    def test_error_only_set_use_error_false_use_abort_use_limits_true_rejected(self):
        """[FUNCTIONAL] Only error flag, use_error=False → rejected; the
        other clauses (abort=False, limits=False) do not trigger."""
        info = _make_info(error=True, path='err.txt')
        accepted, filtered = self._run([info], use_error=False, use_abort=True, use_limits=True)
        assert 'err.txt' not in accepted
        assert 'err.txt' in filtered

    def test_limits_only_set_use_limits_false_use_error_use_abort_true_rejected(self):
        """[FUNCTIONAL] Only limits flag, use_limits=False → rejected."""
        info = _make_info(limits=True, path='lim.txt')
        accepted, filtered = self._run([info], use_error=True, use_abort=True, use_limits=False)
        assert 'lim.txt' not in accepted

    def test_mixed_batch_one_double_flag_rejected_clean_kept(self):
        """[FUNCTIONAL] Mixed batch: clean protocol + error+abort protocol.
        use_error=True, use_abort=False → clean accepted, flagged rejected."""
        clean     = _make_info(path='clean.txt')
        flagged   = _make_info(error=True, abort=True, path='flagged.txt')
        accepted, filtered = self._run([clean, flagged], use_error=True, use_abort=False)
        assert 'clean.txt'   in accepted
        assert 'flagged.txt' in filtered


# ===========================================================================
# [FUNCTIONAL] ③ Latest Protocol + EOL filters — combined sequential pipeline
# ===========================================================================

class TestLatestProtocolWithEolFilters:
    """[FUNCTIONAL/INTEGRATION] Verifies the combined flow:
    FilterProtocols (EOL flags) → FilterNewProtocols (latest-only).
    Tests the sequential application from the GUI's
    ``parseProtnewProtCheckBox`` + EOL checkboxes."""

    def test_older_error_newer_clean_use_error_false_use_latest_only_newer_kept(self):
        """[INTEGRATION] Same sensor: older protocol has error flag, newer is clean.
        use_error=False → older rejected by FilterProtocols.
        FilterNewProtocols then receives only the newer clean protocol → returns it."""
        older = _make_info(
            serial='S1', rf='rf1', dsp='dsp1', date_time='2024-01-01-08:00:00',
            error=True, path='older_error.txt'
        )
        newer = _make_info(
            serial='S1', rf='rf1', dsp='dsp1', date_time='2024-02-01-08:00:00',
            error=False, path='newer_clean.txt'
        )
        accepted, filtered = ProtocolInfoClass.FilterProtocols(
            [older, newer], bUseFilesWithError=False,
            bUseFilesAbbortCriterion=True, bUseFilesWIthLimitsExceeded=True
        )
        latest = ProtocolInfoClass.FilterNewProtocols(accepted)
        latest_paths = [i.PathName for i in latest]

        assert 'older_error.txt' in [i.PathName for i in filtered]
        assert 'newer_clean.txt' in latest_paths
        assert 'older_error.txt' not in latest_paths

    def test_both_clean_same_sensor_use_latest_keeps_only_newer(self):
        """[INTEGRATION] Both protocols clean (no flags), same sensor.
        FilterProtocols accepts both; FilterNewProtocols keeps only the newer."""
        older = _make_info(
            serial='S1', rf='rf1', dsp='dsp1', date_time='2024-01-01-00:00:00',
            path='older.txt'
        )
        newer = _make_info(
            serial='S1', rf='rf1', dsp='dsp1', date_time='2024-03-01-00:00:00',
            path='newer.txt'
        )
        accepted, _ = ProtocolInfoClass.FilterProtocols(
            [older, newer], False, False, False
        )
        latest = ProtocolInfoClass.FilterNewProtocols(accepted)
        paths = [i.PathName for i in latest]

        assert 'newer.txt' in paths
        assert 'older.txt' not in paths

    def test_different_sensors_all_kept_by_filter_new(self):
        """[INTEGRATION] Two different sensors → FilterNewProtocols keeps both
        regardless of date order."""
        p1 = _make_info('S1', 'rf1', 'dsp1', '2024-01-01', path='p1.txt')
        p2 = _make_info('S2', 'rf2', 'dsp2', '2024-01-02', path='p2.txt')
        accepted, _ = ProtocolInfoClass.FilterProtocols([p1, p2], False, False, False)
        latest = ProtocolInfoClass.FilterNewProtocols(accepted)
        paths = [i.PathName for i in latest]

        assert 'p1.txt' in paths
        assert 'p2.txt' in paths

    def test_real_fixture_older_newer_use_latest(self):
        """[INTEGRATION] Real fixture files: _CAL_FILE (Jan) vs _NEWER_FILE (Feb),
        same sensor (rf12345/dsp67890). FilterNewProtocols keeps only newer."""
        infos, *_ = ProtocolInfoClass.PreParseProtcols([_CAL_FILE, _NEWER_FILE])
        accepted, _ = ProtocolInfoClass.FilterProtocols(
            infos, False, False, False
        )
        latest = ProtocolInfoClass.FilterNewProtocols(accepted)
        latest_paths = [i.PathName for i in latest]

        assert _NEWER_FILE in latest_paths
        assert _CAL_FILE   not in latest_paths


# ===========================================================================
# [FUNCTIONAL] ③ FilterNewProtocols — uncovered loop branches
# ===========================================================================

class TestFilterNewProtocolsBranchCoverage:
    """[FUNCTIONAL] White-box branch coverage for the FilterNewProtocols loop.

    The inner comparison ``if date1 > date2`` has two branches:
      True  → append acceptedProtocolsList[idx-1]  (date1 is larger = descending input)
      False → (else) append idx only if last element

    The existing test_protocols.py only tests the False-branch (ascending sorted
    input from FilterProtocols).  The True-branch is exercised below."""

    def _run(self, infos):
        return [i.PathName for i in ProtocolInfoClass.FilterNewProtocols(infos)]

    def test_reverse_sorted_pair_date1_gt_date2_branch_true(self):
        """[FUNCTIONAL] Input is [newer, older] (descending).
        date1 > date2 evaluates True → newer (idx-1) is appended.
        Newer is kept, same effective result as ascending input."""
        newer = _make_info('S1', 'rf1', 'dsp1', '2024-02-01-00:00:00', path='newer.txt')
        older = _make_info('S1', 'rf1', 'dsp1', '2024-01-01-00:00:00', path='older.txt')
        # Deliberately passing reverse-sorted: [newer, older]
        result = self._run([newer, older])
        assert 'newer.txt' in result
        assert 'older.txt' not in result

    def test_three_same_sensor_ascending_only_latest_kept(self):
        """[FUNCTIONAL] Three same-sensor protocols in ascending order.
        Exercises the 'not last element' skip (idx=1: date < next, not last → nothing).
        Only the newest (last) is returned."""
        p1 = _make_info('S1', 'rf1', 'dsp1', '2024-01-01', path='p1.txt')
        p2 = _make_info('S1', 'rf1', 'dsp1', '2024-02-01', path='p2.txt')
        p3 = _make_info('S1', 'rf1', 'dsp1', '2024-03-01', path='p3.txt')
        result = self._run([p1, p2, p3])
        assert 'p3.txt' in result
        assert 'p1.txt' not in result
        assert 'p2.txt' not in result

    def test_two_same_sensor_equal_dates_last_element_appended(self):
        """[FUNCTIONAL/BOUNDARY] Two protocols, same sensor, exactly equal dateAndTime.
        date1 > date2 is False → else branch → idx == len()-1 → appends idx.
        One protocol is returned (the second / idx element)."""
        p1 = _make_info('S1', 'rf1', 'dsp1', '2024-01-01-00:00:00', path='p1.txt')
        p2 = _make_info('S1', 'rf1', 'dsp1', '2024-01-01-00:00:00', path='p2.txt')
        result = self._run([p1, p2])
        # One of them must be returned; the idx (p2) is appended
        assert len(result) == 1
        assert 'p2.txt' in result

    def test_four_same_sensor_only_last_kept(self):
        """[FUNCTIONAL] Four same-sensor protocols ascending: only newest survives."""
        protos = [
            _make_info('S1', 'rf1', 'dsp1', f'2024-0{i+1}-01', path=f'p{i}.txt')
            for i in range(4)
        ]
        result = self._run(protos)
        assert 'p3.txt' in result
        assert len(result) == 1


# ===========================================================================
# [FUNCTIONAL] ④ Search PTU2 / TxAntDiag — stem stripping in walk_protocol_files
# ===========================================================================

class TestWalkProtocolFilesStemStripping:
    """[FUNCTIONAL] Verifies that walk_protocol_files correctly strips
    'Protocol', 'protocol', and 'Protocol_Chip' from the filename stem
    when building the PTU2 search pattern.

    This covers the three ``str.replace`` calls on ``file_name_no_ptu``."""

    def _capture_ptu2_pattern(self) -> tuple:
        """Return (captured_pattern_holder, ptu2_fn) for inspection."""
        holder = {}

        def fn(dir_path, pattern):
            holder['dir']     = dir_path
            holder['pattern'] = pattern
            return []

        return holder, fn

    def _run_walk(self, path: str, ptu2_fn=None) -> dict:
        holder, default_fn = self._capture_ptu2_pattern()
        fn = ptu2_fn if ptu2_fn else default_fn
        info = SimpleNamespace(
            PathName=path, bErrorOccured=False, bAbortCriterion=False, bLimitExceeded=False
        )
        walk_protocol_files([info], True, False, False, False, False, fn, _noop_fn)
        return holder

    def test_uppercase_protocol_stripped_from_middle(self, tmp_path):
        """[FUNCTIONAL] '_Protocol_' stripped: stem used for PTU2 pattern
        does not contain 'Protocol'."""
        path = str(tmp_path / '2024-01-15_Tuner1_rf12345_Protocol.txt')
        holder = self._run_walk(path)
        assert 'Protocol' not in holder.get('pattern', '')

    def test_lowercase_protocol_stripped(self, tmp_path):
        """[FUNCTIONAL] Lowercase 'protocol' replaced: exercises the
        ``.replace('protocol', '')`` branch."""
        path = str(tmp_path / '2024-01-15_Tuner1_rf12345_protocol.txt')
        holder = self._run_walk(path)
        assert 'protocol' not in holder.get('pattern', '')

    def test_protocol_chip_stripped_completely(self, tmp_path):
        """[FUNCTIONAL] 'Protocol_Chip' is replaced before 'Protocol':
        the compound prefix 'Protocol_Chip' disappears."""
        path = str(tmp_path / '2024-01-15_Tuner1_rf12345_Protocol_Chip.txt')
        holder = self._run_walk(path)
        pattern = holder.get('pattern', '')
        assert 'Protocol_Chip' not in pattern
        assert 'Protocol'       not in pattern

    def test_ptu2_pattern_ends_with_dot_txt(self, tmp_path):
        """[FUNCTIONAL] Extension '.txt' is preserved in the PTU2 search pattern."""
        path = str(tmp_path / '2024-01-15_rf99_Protocol.txt')
        holder = self._run_walk(path)
        pattern = holder.get('pattern', '')
        assert pattern.endswith('.txt')

    def test_ptu2_pattern_contains_ptu2_glob(self, tmp_path):
        """[FUNCTIONAL] Pattern always contains '*ptu2*' (case-insensitive search)."""
        path = str(tmp_path / '2024-01-15_rf99_Protocol.txt')
        holder = self._run_walk(path)
        assert 'ptu2' in holder.get('pattern', '').lower()

    def test_search_ptu2_false_no_ptu2_dict_created(self, tmp_path):
        """[FUNCTIONAL] When searchPtu2Files=False, no PTU2 entry is generated."""
        info = SimpleNamespace(
            PathName=str(tmp_path / 'my_Protocol.txt'),
            bErrorOccured=False, bAbortCriterion=False, bLimitExceeded=False,
        )
        ptu2_list, tx_list, *_ = walk_protocol_files(
            [info], False, False, False, False, False, _noop_fn, _noop_fn
        )
        assert ptu2_list == []

    def test_search_txantdiag_false_no_tx_dict_created(self, tmp_path):
        """[FUNCTIONAL] When searchTxAntDiag=False, no TxAntDiag entry is generated."""
        info = SimpleNamespace(
            PathName=str(tmp_path / 'my_Protocol.txt'),
            bErrorOccured=False, bAbortCriterion=False, bLimitExceeded=False,
        )
        ptu2_list, tx_list, *_ = walk_protocol_files(
            [info], False, False, False, False, False, _noop_fn, _noop_fn
        )
        assert tx_list == []

    def test_both_searches_enabled_one_entry_per_protocol(self, tmp_path):
        """[FUNCTIONAL] Both searches enabled for two protocols → two PTU2 dicts
        and two TxAntDiag dicts, each keyed by the correct protocol path."""
        paths = [
            str(tmp_path / 'A_Protocol.txt'),
            str(tmp_path / 'B_Protocol.txt'),
        ]
        infos = [
            SimpleNamespace(
                PathName=p, bErrorOccured=False, bAbortCriterion=False, bLimitExceeded=False,
            )
            for p in paths
        ]
        ptu2_list, tx_list, acc, *_ = walk_protocol_files(
            infos, True, True, False, False, False, _noop_fn, _noop_fn
        )
        assert len(ptu2_list) == 2
        assert len(tx_list)   == 2
        assert [d['protocolPath'] for d in ptu2_list] == paths
        assert [d['protocolPath'] for d in tx_list]   == paths


# ===========================================================================
# [FUNCTIONAL] ① Choose Directory / File List — import deduplication
# ===========================================================================

class TestImportDeduplication:
    """[FUNCTIONAL] Verifies that re-importing already-known protocol files
    is handled correctly by deduplicate_protocol_list and ParseController state.

    Corresponds to the 'Choose Protocol Directory' and 'Choose Protocol List'
    GUI buttons which both feed into fillInProtocolData."""

    def test_first_import_all_paths_returned(self):
        """[FUNCTIONAL] No existing imports → all new paths passed through."""
        paths = ['/a.txt', '/b.txt', '/c.txt']
        result = deduplicate_protocol_list(paths, [])
        assert result == paths

    def test_full_reimport_of_same_dir_returns_empty(self):
        """[FUNCTIONAL] All paths already in state → none returned for re-processing.
        Simulates pressing 'Import Directory' a second time on the same folder."""
        already_imported = [
            {'protocolPath': '/a.txt'},
            {'protocolPath': '/b.txt'},
        ]
        result = deduplicate_protocol_list(['/a.txt', '/b.txt'], already_imported)
        assert result == []

    def test_partial_reimport_only_new_paths_returned(self):
        """[FUNCTIONAL] Some paths already imported, some new → only new returned."""
        already_imported = [{'protocolPath': '/a.txt'}]
        result = deduplicate_protocol_list(['/a.txt', '/b.txt', '/c.txt'], already_imported)
        assert result == ['/b.txt', '/c.txt']

    def test_new_protocols_after_dedup_scheduled_for_parsing(self):
        """[INTEGRATION] New paths from deduplication are appended to
        protToBeParsedDict via collect_unparsed_protocols."""
        from shared.parse_helpers import collect_unparsed_protocols

        new_paths = ['/new_a.txt', '/new_b.txt']
        accepted  = [{'protocolPath': p, 'type': 'Calibration'} for p in new_paths]
        parsed    = {'protocolPathTypeDictList': []}
        to_parse  = {'protocolPathTypeDictList': []}

        collect_unparsed_protocols(accepted, parsed, to_parse)

        assert len(to_parse['protocolPathTypeDictList']) == 2
        parsed_paths = [d['protocolPath'] for d in to_parse['protocolPathTypeDictList']]
        assert '/new_a.txt' in parsed_paths
        assert '/new_b.txt' in parsed_paths

    def test_already_parsed_skipped_in_to_be_parsed(self):
        """[FUNCTIONAL] Protocol already in parsedProtDict → NOT added to
        protToBeParsedDict again (no duplicate parse)."""
        from shared.parse_helpers import collect_unparsed_protocols

        existing = [{'protocolPath': '/already.txt', 'type': 'Calibration'}]
        accepted = [
            {'protocolPath': '/already.txt', 'type': 'Calibration'},
            {'protocolPath': '/fresh.txt',   'type': 'BurnIn'},
        ]
        parsed   = {'protocolPathTypeDictList': [{'protocolPath': '/already.txt'}]}
        to_parse = {'protocolPathTypeDictList': []}

        skipped = collect_unparsed_protocols(accepted, parsed, to_parse)

        paths = [d['protocolPath'] for d in to_parse['protocolPathTypeDictList']]
        assert '/already.txt' not in paths
        assert '/fresh.txt'   in paths
        assert '/already.txt' in skipped


# ===========================================================================
# [FUNCTIONAL] ⑤ Sensor Muster — use_sensor_muster flag propagation
# ===========================================================================

class TestSensorMusterFlagPropagation:
    """[FUNCTIONAL] Verifies that the sensor-muster flag and list are forwarded
    through ParseController.parse_ptu2_files to the underlying parser.

    The Sensor Muster checkbox sets plc.plotSetup['useSensorMuster'] which is
    passed as ``use_sensor_muster`` when parsing PTU2 files."""

    def test_sensor_muster_disabled_zero_forwarded_to_parser(self, tmp_path):
        """[FUNCTIONAL] use_sensor_muster=0 (checkbox unchecked) is passed
        verbatim to parser.parseFile."""
        p = tmp_path / 'data_ptu2.txt'
        p.write_text('dummy')

        pc = _make_pc()
        with patch('shared.parse_controller.ParserFactory') as MockFactory:
            mock_parser = MagicMock()
            mock_parser.bDataValid = True
            MockFactory.create.return_value = mock_parser

            pc.parse_ptu2_files([str(p)], use_sensor_muster=0, sensor_muster_list=[])

            mock_parser.parseFile.assert_called_once_with(str(p), 0, [])

    def test_sensor_muster_enabled_one_forwarded_to_parser(self, tmp_path):
        """[FUNCTIONAL] use_sensor_muster=1 (checkbox checked) is forwarded."""
        p = tmp_path / 'data_ptu2.txt'
        p.write_text('dummy')
        muster_list = ['sensor_A', 'sensor_B']

        pc = _make_pc()
        with patch('shared.parse_controller.ParserFactory') as MockFactory:
            mock_parser = MagicMock()
            mock_parser.bDataValid = True
            MockFactory.create.return_value = mock_parser

            pc.parse_ptu2_files([str(p)], use_sensor_muster=1, sensor_muster_list=muster_list)

            mock_parser.parseFile.assert_called_once_with(str(p), 1, muster_list)

    def test_sensor_muster_forwarded_to_txantdiag_parser(self, tmp_path):
        """[FUNCTIONAL] TxAntDiag parsing also forwards sensor muster correctly."""
        p = tmp_path / 'data_TxAnt0_Diagram0.txt'
        p.write_text('dummy')
        muster_list = ['muster_X']

        pc = _make_pc()
        with patch('shared.parse_controller.ParserFactory') as MockFactory:
            mock_parser = MagicMock()
            mock_parser.bDataValid = False
            MockFactory.create.return_value = mock_parser

            pc.parse_tx_ant_diag_files([str(p)], use_sensor_muster=1, sensor_muster_list=muster_list)

            mock_parser.parseFile.assert_called_once_with(str(p), 1, muster_list)


# ===========================================================================
# [REGRESSION] PST-76 and PST-77 guards
# ===========================================================================

class TestRegressions:
    """[REGRESSION] Explicit regression guards that must always pass.

    PST-76: BurnIn-start line with ';ok' suffix was not matched by '==' comparison
            (fixed: changed to startswith).
    PST-77: Parsed field values retained '\\n' from file lines
            (fixed: added .strip() to all five field assignments in getPreParseInfo).
    """

    # --- PST-76 ---------------------------------------------------------------

    def test_pst76_burnin_start_ok_suffix_still_filtered(self, tmp_path):
        """[REGRESSION] PST-76: '(12a) BurnIn Start Check results:;ok' (with ';ok')
        must still trigger BurnIn-start filtering.  Previously the old '==' check
        failed to match because of the ';ok' suffix."""
        content = 'Gen26_UseBurnInMeas[1];3\n(12a) BurnIn Start Check results:;ok\n'
        p = tmp_path / 'bistart_Protocol.txt'
        p.write_text(content)
        pc = _make_pc()
        result = pc.get_protocol_type(str(p), 0, include_burn_in_start=False)
        assert result == 'Filtered', (
            'PST-76 regression: BurnIn-start with ;ok suffix must be filtered'
        )

    def test_pst76_burnin_start_exact_line_also_filtered(self, tmp_path):
        """[REGRESSION] PST-76: exact line without suffix is also filtered correctly."""
        content = 'Gen26_UseBurnInMeas[1];3\n(12a) BurnIn Start Check results:\n'
        p = tmp_path / 'bistart2_Protocol.txt'
        p.write_text(content)
        pc = _make_pc()
        result = pc.get_protocol_type(str(p), 0, include_burn_in_start=False)
        assert result == 'Filtered'

    # --- PST-77 ---------------------------------------------------------------

    def test_pst77_all_five_fields_stripped_from_newlines(self):
        """[REGRESSION] PST-77: all five parsed fields (date, time→dateTime,
        productSerial, rf, dsp) must have trailing '\\n' stripped.
        Verifies that no field contains a newline character."""
        lines = [
            'Date:;2024-03-15\n',
            'Time:;09:30:00\n',
            'Product-Serial:;UMRR-99999\n',
            'RF-Serial:;55555\n',
            'Dsp-Serial:;66666\n',
        ]
        _, _, _, _, date_time, serial, rf, dsp = ProtocolInfoClass.getPreParseInfo(lines)

        assert '\n' not in date_time, f'PST-77: dateTime contains \\n: {repr(date_time)}'
        assert '\n' not in serial,    f'PST-77: productSerial contains \\n: {repr(serial)}'
        assert '\n' not in rf,        f'PST-77: rf contains \\n: {repr(rf)}'
        assert '\n' not in dsp,       f'PST-77: dsp contains \\n: {repr(dsp)}'

    def test_pst77_date_time_format_correct_with_newlines_in_input(self):
        """[REGRESSION] PST-77: dateTime must be 'YYYY-MM-DD-HH:MM:SS' with NO
        embedded newline between date and time parts."""
        lines = ['Date:;2024-03-15\n', 'Time:;09:30:00\n']
        _, _, _, _, date_time, *_ = ProtocolInfoClass.getPreParseInfo(lines)
        assert date_time == '2024-03-15-09:30:00', (
            f'PST-77 regression: dateTime={repr(date_time)}'
        )

    def test_pst77_serial_stripped_with_newline_in_input(self):
        """[REGRESSION] PST-77: productSerial field stripped correctly."""
        lines = ['Product-Serial:;UMRR-11.00.04-SN12345\n']
        _, _, _, _, _, serial, _, _ = ProtocolInfoClass.getPreParseInfo(lines)
        assert serial == 'UMRR-11.00.04-SN12345'

    def test_pst77_rf_dsp_stripped_with_newlines_in_input(self):
        """[REGRESSION] PST-77: rf and dsp stripped correctly."""
        lines = ['RF-Serial:;RF-0001\n', 'Dsp-Serial:;DSP-0002\n']
        _, _, _, _, _, _, rf, dsp = ProtocolInfoClass.getPreParseInfo(lines)
        assert rf  == 'RF-0001'
        assert dsp == 'DSP-0002'


# ===========================================================================
# [BOUNDARY] Edge values and empty lists
# ===========================================================================

class TestBoundaryValues:
    """[BOUNDARY] Tests at edge limit values:
    empty lists, single-element lists, and extreme ends of comparisons."""

    def test_filter_protocols_empty_input_returns_empty_both(self):
        """[BOUNDARY] FilterProtocols with empty accepted list → both outputs empty."""
        accepted, filtered = ProtocolInfoClass.FilterProtocols([], False, False, False)
        assert accepted  == []
        assert filtered  == []

    def test_filter_new_protocols_two_item_boundary_same_sensor_keeps_newer(self):
        """[BOUNDARY] Minimum meaningful list for FilterNewProtocols (2 same-sensor).
        Exercises the boundary where idx==len()-1 is True on the very first comparison."""
        older = _make_info('S1', 'rf1', 'dsp1', '2024-01-01', path='old.txt')
        newer = _make_info('S1', 'rf1', 'dsp1', '2024-02-01', path='new.txt')
        result = [i.PathName for i in ProtocolInfoClass.FilterNewProtocols([older, newer])]
        assert 'new.txt' in result
        assert 'old.txt' not in result

    def test_build_prot_path_type_list_empty_returns_empty(self):
        """[BOUNDARY] Empty path list → empty result."""
        pc = _make_pc()
        assert pc.build_prot_path_type_list([], 0, False) == []

    def test_walk_protocol_files_empty_accepted_list(self):
        """[BOUNDARY] Empty accepted protocols list → all six outputs empty."""
        ptu2, tx, acc, err, abort, lim = walk_protocol_files(
            [], True, True, True, True, True, _mock_ptu2_fn, _mock_txant_fn
        )
        assert ptu2 == tx == acc == err == abort == lim == []

    def test_filter_protocols_single_clean_protocol(self):
        """[BOUNDARY] List of exactly one clean protocol → accepted, filtered empty."""
        info    = _make_info(path='sole.txt')
        accepted, filtered = ProtocolInfoClass.FilterProtocols([info], False, False, False)
        paths = [i.PathName for i in accepted]
        assert 'sole.txt' in paths
        assert filtered == []

    def test_filter_new_protocols_single_item_returned(self):
        """[BOUNDARY] Single-element list → returned as-is (filtered list is empty,
        falls back to acceptedProtocolsList)."""
        p = _make_info('S1', 'rf1', 'dsp1', '2024-01-01', path='only.txt')
        result = [i.PathName for i in ProtocolInfoClass.FilterNewProtocols([p])]
        assert 'only.txt' in result

    def test_deduplicate_empty_candidates_returns_empty(self):
        """[BOUNDARY] No candidate paths → nothing to return."""
        result = deduplicate_protocol_list([], [{'protocolPath': '/a.txt'}])
        assert result == []

    def test_get_all_protocols_empty_directory(self, tmp_path):
        """[BOUNDARY] Scanning an empty directory → empty protocol list."""
        found = ProtocolInfoClass.GetAllProtocolsList(str(tmp_path))
        assert found == []

    def test_get_all_protocols_nonexistent_directory(self, tmp_path):
        """[BOUNDARY] Non-existent path → os.walk yields nothing → empty list."""
        nonexistent = str(tmp_path / 'does_not_exist')
        found = ProtocolInfoClass.GetAllProtocolsList(nonexistent)
        assert found == []


# ===========================================================================
# [SMOKE] PST-T21 — PTU2 subfiles discovered when Search PTU2 checkbox is checked
# ===========================================================================

class TestSearchPtu2Checkbox:
    """[SMOKE] PST-T21: PTU2 subfiles discovered when Search PTU2 checkbox is checked.

    The 'Search PTU2 Files' checkbox (``parseProtSysDiagCheckBox``) sets
    ``search_ptu2_files`` in the ``walk_protocol_files`` call.  When checked,
    PTU2 files located in sub-directories of the protocol folder must be
    discovered via ``getfiltered_ptu2filelist``'s ``os.walk`` recursion.
    When unchecked, no PTU2 files are collected.

    Uses the real fixture directory ``measurement_data/protocol_files/`` which
    contains PTU2 fixture files inside its ``subfiles/`` subdirectory.
    """

    _PROT_DIR = os.path.join(_root, 'measurement_data', 'protocol_files')
    _SUBDIR   = os.path.join(_PROT_DIR, 'subfiles')
    # Stem of the Cal protocol fixture that has matching PTU2 subfiles
    _CAL_STEM = '2024-01-15_12-30-45_Tuner1_rf12345_dsp67890_Seq1_TxAnt1_Diagram1_'

    def _run(self, search_ptu2: bool) -> list:
        found = ProtocolInfoClass.GetAllProtocolsList(self._PROT_DIR)
        infos, *_ = ProtocolInfoClass.PreParseProtcols(found)
        accepted, _ = ProtocolInfoClass.FilterProtocols(infos, False, True, True)
        ptu2_list, *_ = walk_protocol_files(
            accepted,
            search_ptu2_files=search_ptu2,
            search_txantdiag_files=False,
            use_error=False,
            use_abort=True,
            use_limits_exceeded=True,
            get_ptu2_files_fn=ProtocolInfoClass.getfiltered_ptu2filelist,
            get_txantdiag_files_fn=ProtocolInfoClass.getfiltered_txantdiagramfilelist,
        )
        return ptu2_list

    def test_pst_t21_subfiles_found_when_search_ptu2_checked(self):
        """[SMOKE] PST-T21: search_ptu2=True (checkbox checked) → PTU2 files
        inside subfiles/ sub-directory are discovered for the Cal fixture."""
        ptu2_list = self._run(search_ptu2=True)
        all_ptu2 = [
            os.path.normpath(f)
            for entry in ptu2_list
            for f in entry['ptu2FilesList']
        ]
        expected_az = os.path.normpath(
            os.path.join(self._SUBDIR, self._CAL_STEM + 'Az_ptu2.txt')
        )
        expected_el = os.path.normpath(
            os.path.join(self._SUBDIR, self._CAL_STEM + 'El_ptu2.txt')
        )
        assert expected_az in all_ptu2, (
            f'PST-T21: Az PTU2 subfile not discovered.\nFound: {all_ptu2}'
        )
        assert expected_el in all_ptu2, (
            f'PST-T21: El PTU2 subfile not discovered.\nFound: {all_ptu2}'
        )

    def test_pst_t21_no_ptu2_when_search_unchecked(self):
        """[SMOKE] PST-T21: search_ptu2=False (checkbox unchecked) → no PTU2
        entries produced at all, regardless of what files exist on disk."""
        ptu2_list = self._run(search_ptu2=False)
        assert ptu2_list == [], (
            f'PST-T21: Expected empty PTU2 list when checkbox unchecked. '
            f'Got {len(ptu2_list)} entries.'
        )
