"""Unit tests for the Epic 1 limits pipeline (PST-28).

All tests are pure-Python (no Qt required). Mock ParseProtocols objects are
injected directly into the ParseController state dicts — no file I/O.

MANUAL / SMOKE TESTS (verify by running the application):
  1. Parse tab: load a real protocol directory → press "Parse".
     Cal / BurnIn group ComboBoxes must populate with group names.
  2. Statistics tab: press "Write Statistics" → statsTable fills with rows
     (graph, axis, error, protType, limitName, stDev, mean, min, max, …).
  3. Group Forward / Back buttons cycle through groups;
     statsGroupNameLabel must update on every click.
  4. Click graph cell (col 0) → cell turns green, graph panel opens.
  5. Click axis cell (col 1) → cell cycles 0→1→… and updates row.axis.
  6. "Clear" button (statsClearBtn) → statsTable empties, plot resets,
     cell colours cleared.
  7. parseProtWriteStatsPushBtn → fills parseProtStatsParsedTable +
     parseProtStatsFailedTable with accepted / failed protocols.
  8. parseProtClearStatsDataBtn → clears those two protocol tables.
  9. Extend-checkbox ticked → after parse, YAML is re-saved with new entries
     appended, confirmed by reopening the file.

REGRESSION CHECKS (run via pytest):
  - build_limits_rows: de-dup keeps exactly one LimitsRow per
    (limitName, protType) across multiple protocol entries.
  - compute_limits_stats: mean / stDev / Cg / bounds correct for known data.
  - No parsed protocols for a row → row.error set, no exception.
  - Missing YAML file → no crash; protocol routes to failed dict.
  - generateInputFilteredMeasurementLimit: early-return on error/missing key.
  - clear_state: all six limits dicts reset to empty, indices to -1.
"""
import sys
import os
import math
import types

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _sub in ['shared']:
    _p = os.path.join(_root, _sub)
    if _p not in sys.path:
        sys.path.insert(0, _p)

import pytest

from shared.parse_controller import ParseController
from shared.parseProtocols import LimitsRow, LimitsGroup


# ---------------------------------------------------------------------------
# Mock helpers
# ---------------------------------------------------------------------------

def _make_lim(name, value=0.0, value_found=1, min_val=0.0, max_val=0.0):
    """Minimal limit object with the fields read by compute_limits_stats."""
    return types.SimpleNamespace(
        name=name,
        value=value,
        valueFound=value_found,
        min=min_val,
        max=max_val,
    )



def _make_lim_list(*lims):
    return types.SimpleNamespace(limitsList=list(lims))


def _make_pp(lim_list, proto_head=None):
    """Minimal ParseProtocols stand-in."""
    return types.SimpleNamespace(
        inputFilteredMeasurementLimit=lim_list,
        rawParsedProtocolHead=proto_head or {},
    )


def _inject_burn_in(pc, *pps):
    for i, pp in enumerate(pps):
        pc.burnInParsedProtDict['protocolParsingDictList'].append(
            {'protocolPath': f'/fake/bi_{i}.txt', 'type': 'BurnIn',
             'parsing': 'BurnIn', 'parsedData': pp}
        )


def _inject_cal(pc, *pps):
    for i, pp in enumerate(pps):
        pc.calParsedProtDict['protocolParsingDictList'].append(
            {'protocolPath': f'/fake/cal_{i}.txt', 'type': 'Calibration',
             'parsing': 'Calibration', 'parsedData': pp}
        )


def _make_row(limit_name, prot_type):
    r = LimitsRow()
    r.limitName = limit_name
    r.protType  = prot_type
    return r


# ---------------------------------------------------------------------------
# TestLimitsInitialState
# ---------------------------------------------------------------------------

class TestLimitsInitialState:
    def test_burn_in_parsed_empty(self):
        pc = ParseController()
        assert pc.burnInParsedProtDict['protocolParsingDictList'] == []

    def test_burn_in_failed_empty(self):
        pc = ParseController()
        assert pc.burnInFailedProtDict['protocolParsingDictList'] == []

    def test_cal_parsed_empty(self):
        pc = ParseController()
        assert pc.calParsedProtDict['protocolParsingDictList'] == []

    def test_cal_failed_empty(self):
        pc = ParseController()
        assert pc.calFailedProtDict['protocolParsingDictList'] == []

    def test_limits_row_list_empty(self):
        pc = ParseController()
        assert pc.limitsRowListDict['limitsRowList'] == []

    def test_burn_in_group_dict_defaults(self):
        pc = ParseController()
        assert pc.burnInLimitsGroupDict['limitsGroupList'] == []
        assert pc.burnInLimitsGroupDict['activeGroupIndex'] == -1

    def test_cal_group_dict_defaults(self):
        pc = ParseController()
        assert pc.calLimitsGroupDict['limitsGroupList'] == []
        assert pc.calLimitsGroupDict['activeGroupIndex'] == -1


# ---------------------------------------------------------------------------
# TestBuildLimitsRows
# ---------------------------------------------------------------------------

class TestBuildLimitsRows:
    def test_empty_parsed_dicts_yields_no_rows(self):
        pc = ParseController()
        pc.build_limits_rows()
        assert pc.limitsRowListDict['limitsRowList'] == []

    def test_single_burn_in_limit(self):
        pc = ParseController()
        pp = _make_pp(_make_lim_list(_make_lim('LimitA')))
        _inject_burn_in(pc, pp)
        pc.build_limits_rows()
        rows = pc.limitsRowListDict['limitsRowList']
        assert len(rows) == 1
        assert rows[0].limitName == 'LimitA'
        assert rows[0].protType  == 'BurnIn'

    def test_single_cal_limit(self):
        pc = ParseController()
        pp = _make_pp(_make_lim_list(_make_lim('CalLimit')))
        _inject_cal(pc, pp)
        pc.build_limits_rows()
        rows = pc.limitsRowListDict['limitsRowList']
        assert len(rows) == 1
        assert rows[0].limitName == 'CalLimit'
        assert rows[0].protType  == 'Calibration'

    def test_dedup_same_limit_across_two_protocols(self):
        """Same limit name in two protocols → single row (de-duplication)."""
        pc = ParseController()
        pp1 = _make_pp(_make_lim_list(_make_lim('LimitA')))
        pp2 = _make_pp(_make_lim_list(_make_lim('LimitA')))
        _inject_burn_in(pc, pp1, pp2)
        pc.build_limits_rows()
        assert len(pc.limitsRowListDict['limitsRowList']) == 1

    def test_dedup_same_name_different_prottype_kept(self):
        """Same limit name but different protType → two rows."""
        pc = ParseController()
        bi_pp  = _make_pp(_make_lim_list(_make_lim('LimitA')))
        cal_pp = _make_pp(_make_lim_list(_make_lim('LimitA')))
        _inject_burn_in(pc, bi_pp)
        _inject_cal(pc, cal_pp)
        pc.build_limits_rows()
        rows = pc.limitsRowListDict['limitsRowList']
        assert len(rows) == 2
        types_ = {r.protType for r in rows}
        assert types_ == {'BurnIn', 'Calibration'}

    def test_multiple_limits_in_one_protocol(self):
        pc = ParseController()
        lims = _make_lim_list(
            _make_lim('LimitA'),
            _make_lim('LimitB'),
            _make_lim('LimitC'),
        )
        pp = _make_pp(lims)
        _inject_burn_in(pc, pp)
        pc.build_limits_rows()
        names = [r.limitName for r in pc.limitsRowListDict['limitsRowList']]
        assert sorted(names) == ['LimitA', 'LimitB', 'LimitC']

    def test_limit_from_proto_head(self):
        """Limits sourced from rawParsedProtocolHead dict are also included."""
        pc = ParseController()
        pp = _make_pp(_make_lim_list(), proto_head={'HeadLimit': [1.0, 2.0]})
        _inject_burn_in(pc, pp)
        pc.build_limits_rows()
        names = [r.limitName for r in pc.limitsRowListDict['limitsRowList']]
        assert 'HeadLimit' in names

    def test_rebuild_replaces_previous_rows(self):
        """Calling build_limits_rows a second time replaces the old list."""
        pc = ParseController()
        pp = _make_pp(_make_lim_list(_make_lim('LimitA')))
        _inject_burn_in(pc, pp)
        pc.build_limits_rows()
        assert len(pc.limitsRowListDict['limitsRowList']) == 1

        # Add more data and rebuild
        pp2 = _make_pp(_make_lim_list(_make_lim('LimitB')))
        _inject_burn_in(pc, pp2)
        pc.build_limits_rows()
        names = [r.limitName for r in pc.limitsRowListDict['limitsRowList']]
        assert 'LimitA' in names
        assert 'LimitB' in names


# ---------------------------------------------------------------------------
# TestComputeLimitsStats
# ---------------------------------------------------------------------------

class TestComputeLimitsStats:
    def _make_and_inject(self, prot_type, *value_tuples):
        """
        value_tuples: (value, min_val, max_val) triples for limit 'TestLimit'.
        Returns a configured controller with one row and injected protocols.
        """
        pc = ParseController()
        row = _make_row('TestLimit', prot_type)
        pc.limitsRowListDict['limitsRowList'] = [row]

        for (val, lo, hi) in value_tuples:
            lim = _make_lim('TestLimit', value=val, value_found=1,
                            min_val=lo, max_val=hi)
            pp = _make_pp(_make_lim_list(lim))
            if prot_type == 'BurnIn':
                _inject_burn_in(pc, pp)
            else:
                _inject_cal(pc, pp)
        return pc

    # ---- index assignment --------------------------------------------------

    def test_index_assigned(self):
        pc = self._make_and_inject('BurnIn', (5.0, 0.0, 10.0))
        pc.compute_limits_stats()
        assert pc.limitsRowListDict['limitsRowList'][0].index == 0

    def test_index_sequential_for_multiple_rows(self):
        pc = ParseController()
        rows = [_make_row('LimitA', 'BurnIn'), _make_row('LimitB', 'BurnIn')]
        pc.limitsRowListDict['limitsRowList'] = rows
        pc.compute_limits_stats()
        assert rows[0].index == 0
        assert rows[1].index == 1

    # ---- single value -------------------------------------------------------

    def test_single_value_mean(self):
        pc = self._make_and_inject('BurnIn', (5.0, 1.0, 9.0))
        pc.compute_limits_stats()
        row = pc.limitsRowListDict['limitsRowList'][0]
        assert row.mean == 5.0

    def test_single_value_min_max(self):
        pc = self._make_and_inject('BurnIn', (5.0, 1.0, 9.0))
        pc.compute_limits_stats()
        row = pc.limitsRowListDict['limitsRowList'][0]
        assert row.min == 5.0
        assert row.max == 5.0

    def test_single_value_stdev_zero(self):
        pc = self._make_and_inject('BurnIn', (5.0, 1.0, 9.0))
        pc.compute_limits_stats()
        row = pc.limitsRowListDict['limitsRowList'][0]
        assert row.stDev == 0.0

    def test_single_value_maxdev_zero(self):
        pc = self._make_and_inject('BurnIn', (5.0, 1.0, 9.0))
        pc.compute_limits_stats()
        row = pc.limitsRowListDict['limitsRowList'][0]
        assert row.maxDev == 0.0

    def test_single_value_limits(self):
        pc = self._make_and_inject('BurnIn', (5.0, 1.0, 9.0))
        pc.compute_limits_stats()
        row = pc.limitsRowListDict['limitsRowList'][0]
        assert row.lowerLimit == 1.0
        assert row.upperLimit == 9.0

    def test_single_value_cg_zero_due_to_stdev(self):
        """Cg is 0 when stDev ≤ 1e-12 (single value)."""
        pc = self._make_and_inject('BurnIn', (5.0, 1.0, 9.0))
        pc.compute_limits_stats()
        row = pc.limitsRowListDict['limitsRowList'][0]
        assert row.cg == 0.0

    def test_single_value_insufficient_stdev_error(self):
        pc = self._make_and_inject('BurnIn', (5.0, 1.0, 9.0))
        pc.compute_limits_stats()
        row = pc.limitsRowListDict['limitsRowList'][0]
        assert 13 in row.error

    # ---- two values -------------------------------------------------------

    def test_two_values_mean(self):
        pc = self._make_and_inject('BurnIn', (10.0, 0.0, 30.0), (20.0, 0.0, 30.0))
        pc.compute_limits_stats()
        row = pc.limitsRowListDict['limitsRowList'][0]
        assert row.mean == 15.0

    def test_two_values_min_max(self):
        pc = self._make_and_inject('BurnIn', (10.0, 0.0, 30.0), (20.0, 0.0, 30.0))
        pc.compute_limits_stats()
        row = pc.limitsRowListDict['limitsRowList'][0]
        assert row.min == 10.0
        assert row.max == 20.0

    def test_two_values_stdev(self):
        # stDev = sqrt(((10-15)^2 + (20-15)^2) / 1) = sqrt(50)
        pc = self._make_and_inject('BurnIn', (10.0, 0.0, 30.0), (20.0, 0.0, 30.0))
        pc.compute_limits_stats()
        row = pc.limitsRowListDict['limitsRowList'][0]
        assert abs(row.stDev - round(math.sqrt(50), 6)) < 1e-5

    def test_two_values_maxdev(self):
        pc = self._make_and_inject('BurnIn', (10.0, 0.0, 30.0), (20.0, 0.0, 30.0))
        pc.compute_limits_stats()
        row = pc.limitsRowListDict['limitsRowList'][0]
        assert row.maxDev == 5.0

    def test_two_values_cg(self):
        # tol=30, stDev=sqrt(50); Cg = min(30/20/sqrt(50), 1000)
        pc = self._make_and_inject('BurnIn', (10.0, 0.0, 30.0), (20.0, 0.0, 30.0))
        pc.compute_limits_stats()
        row = pc.limitsRowListDict['limitsRowList'][0]
        expected = round(min(30.0 / 20.0 / math.sqrt(50), 1000.0), 6)
        assert abs(row.cg - expected) < 1e-5

    # ---- three values -------------------------------------------------------

    def test_three_values_stdev(self):
        # values [1, 2, 3]: mean=2, stDev = sqrt((1+0+1)/2) = 1.0
        pc = ParseController()
        row = _make_row('TestLimit', 'BurnIn')
        pc.limitsRowListDict['limitsRowList'] = [row]
        for v in [1.0, 2.0, 3.0]:
            pp = _make_pp(_make_lim_list(_make_lim('TestLimit', value=v,
                                                    min_val=0.0, max_val=5.0)))
            _inject_burn_in(pc, pp)
        pc.compute_limits_stats()
        assert abs(row.stDev - 1.0) < 1e-5

    # ---- error cases --------------------------------------------------------

    def test_no_actual_values_sets_error(self):
        """Limit row with no matching values in parsed data → error set."""
        pc = ParseController()
        row = _make_row('TestLimit', 'BurnIn')
        pc.limitsRowListDict['limitsRowList'] = [row]
        # Protocol with a different limit name
        pp = _make_pp(_make_lim_list(_make_lim('OtherLimit', value=5.0)))
        _inject_burn_in(pc, pp)
        pc.compute_limits_stats()
        assert 2 in row.error

    def test_no_parsed_protocols_sets_error(self):
        """Row whose protType has no parsed protocols → error set, no exception."""
        pc = ParseController()
        row = _make_row('TestLimit', 'BurnIn')
        pc.limitsRowListDict['limitsRowList'] = [row]
        # burnInParsedProtDict is intentionally left empty
        pc.compute_limits_stats()
        assert 2 in row.error

    def test_value_found_zero_excluded(self):
        """Limits with valueFound=0 must not contribute to statistics."""
        pc = ParseController()
        row = _make_row('TestLimit', 'BurnIn')
        pc.limitsRowListDict['limitsRowList'] = [row]
        pp = _make_pp(_make_lim_list(
            _make_lim('TestLimit', value=99.0, value_found=0)  # should be ignored
        ))
        _inject_burn_in(pc, pp)
        pc.compute_limits_stats()
        assert 2 in row.error  # no valid values found

    def test_zero_tolerance_cg_error(self):
        """When upperLimit == lowerLimit, Cg=0 and error key 14 is set."""
        pc = ParseController()
        row = _make_row('TestLimit', 'BurnIn')
        pc.limitsRowListDict['limitsRowList'] = [row]
        for v in [5.0, 6.0]:
            pp = _make_pp(_make_lim_list(
                _make_lim('TestLimit', value=v, min_val=5.0, max_val=5.0)
            ))
            _inject_burn_in(pc, pp)
        pc.compute_limits_stats()
        assert row.cg == 0.0
        assert 14 in row.error

    def test_empty_row_list_no_exception(self):
        """No rows → compute_limits_stats is a no-op, no exception."""
        pc = ParseController()
        pc.compute_limits_stats()  # must not raise


# ---------------------------------------------------------------------------
# TestBuildGroupObjects
# ---------------------------------------------------------------------------

class TestBuildGroupObjects:
    def _make_rows(self, *names, prot_type='BurnIn'):
        rows = []
        for name in names:
            rows.append(_make_row(name, prot_type))
        return rows

    def test_exact_match_creates_group(self):
        rows = self._make_rows('LimitA0', 'LimitA1', 'LimitB0')
        input_dict = {
            'GroupA': {'Limits': {'ExactMatch': ['LimitA0', 'LimitA1'], 'Contains': []}},
        }
        groups = ParseController._build_group_objects(input_dict, rows, 'BurnIn')
        assert len(groups) == 1
        assert groups[0].name == 'GroupA'
        assert len(groups[0].limitsRowMatchDictList) == 2

    def test_contains_creates_group(self):
        rows = self._make_rows('LimitA0', 'LimitA1', 'OtherLimit0')
        input_dict = {
            'GroupA': {'Limits': {'ExactMatch': [], 'Contains': ['LimitA']}},
        }
        groups = ParseController._build_group_objects(input_dict, rows, 'BurnIn')
        assert len(groups) == 1
        assert len(groups[0].limitsRowMatchDictList) == 2

    def test_no_matching_rows_group_not_added(self):
        rows = self._make_rows('LimitX0')
        input_dict = {
            'EmptyGroup': {'Limits': {'ExactMatch': ['Nonexistent'], 'Contains': []}},
        }
        groups = ParseController._build_group_objects(input_dict, rows, 'BurnIn')
        assert groups == []

    def test_prot_type_filter(self):
        """Rows of wrong protType must not match, even with exact name."""
        rows = self._make_rows('LimitA0', prot_type='Calibration')
        input_dict = {
            'GroupA': {'Limits': {'ExactMatch': ['LimitA0'], 'Contains': []}},
        }
        groups = ParseController._build_group_objects(input_dict, rows, 'BurnIn')
        assert groups == []

    def test_empty_input_dict_returns_empty(self):
        rows = self._make_rows('LimitA0')
        groups = ParseController._build_group_objects({}, rows, 'BurnIn')
        assert groups == []


# ---------------------------------------------------------------------------
# TestMakeGroupNameDicts
# ---------------------------------------------------------------------------

class TestMakeGroupNameDicts:
    def test_exact_matches_populated(self):
        rows = [
            _make_row('LimitA0', 'BurnIn'),
            _make_row('LimitA1', 'BurnIn'),
            _make_row('LimitA2', 'BurnIn'),
        ]
        result = ParseController._make_group_name_dicts(['LimitA'], rows, 'BurnIn')
        assert len(result) == 1
        d = result[0]
        assert d['groupName'] == 'LimitA'
        assert set(d['Limits']['ExactMatch']) == {'LimitA0', 'LimitA1', 'LimitA2'}
        assert d['Limits']['Contains'] == []

    def test_non_matching_name_returns_empty_exact(self):
        rows = [_make_row('Other0', 'BurnIn')]
        result = ParseController._make_group_name_dicts(['LimitA'], rows, 'BurnIn')
        assert result[0]['Limits']['ExactMatch'] == []

    def test_prot_type_filter(self):
        rows = [_make_row('LimitA0', 'Calibration')]
        result = ParseController._make_group_name_dicts(['LimitA'], rows, 'BurnIn')
        assert result[0]['Limits']['ExactMatch'] == []


# ---------------------------------------------------------------------------
# TestBuildLimitsGroupsNoPath
# ---------------------------------------------------------------------------

class TestBuildLimitsGroupsNoPath:
    def test_empty_path_no_crash(self):
        pc = ParseController()
        row = _make_row('TestGroup0', 'BurnIn')
        pc.limitsRowListDict['limitsRowList'] = [row]
        pc.build_limits_groups('', '', True, True, False, False)
        assert pc.burnInLimitsGroupDict['limitsGroupList'] == []
        assert pc.calLimitsGroupDict['limitsGroupList'] == []

    def test_no_file_set_label_no_crash(self):
        pc = ParseController()
        row = _make_row('TestGroup0', 'BurnIn')
        pc.limitsRowListDict['limitsRowList'] = [row]
        pc.build_limits_groups(
            'No file set.', 'No file set.', True, True, False, False
        )
        assert pc.burnInLimitsGroupDict['limitsGroupList'] == []

    def test_active_group_index_reset_to_minus_one(self):
        pc = ParseController()
        pc.burnInLimitsGroupDict['activeGroupIndex'] = 3
        pc.calLimitsGroupDict['activeGroupIndex']    = 5
        pc.build_limits_groups('', '', False, False, False, False)
        assert pc.burnInLimitsGroupDict['activeGroupIndex'] == -1
        assert pc.calLimitsGroupDict['activeGroupIndex']    == -1


# ---------------------------------------------------------------------------
# TestClearStateLimits
# ---------------------------------------------------------------------------

class TestClearStateLimits:
    def test_limits_dicts_cleared(self):
        pc = ParseController()
        # inject data
        pp = _make_pp(_make_lim_list(_make_lim('LimitA')))
        _inject_burn_in(pc, pp)
        _inject_cal(pc, pp)
        pc.burnInFailedProtDict['protocolParsingDictList'].append({'x': 1})
        pc.calFailedProtDict['protocolParsingDictList'].append({'x': 2})
        pc.limitsRowListDict['limitsRowList'] = [_make_row('LimitA', 'BurnIn')]
        pc.burnInLimitsGroupDict['limitsGroupList'] = [LimitsGroup()]
        pc.calLimitsGroupDict['limitsGroupList']    = [LimitsGroup()]
        pc.burnInLimitsGroupDict['activeGroupIndex'] = 2
        pc.calLimitsGroupDict['activeGroupIndex']    = 4

        pc.clear_state()

        assert pc.burnInParsedProtDict['protocolParsingDictList'] == []
        assert pc.burnInFailedProtDict['protocolParsingDictList'] == []
        assert pc.calParsedProtDict['protocolParsingDictList']    == []
        assert pc.calFailedProtDict['protocolParsingDictList']    == []
        assert pc.limitsRowListDict['limitsRowList']               == []
        assert pc.burnInLimitsGroupDict['limitsGroupList']         == []
        assert pc.calLimitsGroupDict['limitsGroupList']            == []
        assert pc.burnInLimitsGroupDict['activeGroupIndex']        == -1
        assert pc.calLimitsGroupDict['activeGroupIndex']           == -1
