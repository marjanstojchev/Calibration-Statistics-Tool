"""PST-28: Integration tests — limits pipeline end-to-end.

Covers the chain:
  parse_protocol_limits → build_limits_rows → build_limits_groups
                       → compute_limits_stats

All real YAML files are read from config/ in the project root.
Protocol files are read from measurement_data/protocol_files/.

Tests that exercise file I/O use real project files (read-only) or
tmp_path (for write/extend paths).

REGRESSION SCOPE:
  - Missing YAML → no exception; protocol routed to failed dict.
  - Empty/sentinel path ('No file set.') → graceful skip.
  - Full pipeline with real YAML: no exception; pipeline methods produce
    consistent shapes (row list, group list indices reset to -1).
  - compute_limits_stats after real parse: all row.index values assigned.
  - clear_state after real pipeline run: all limits dicts emptied.
"""
import os
import sys

_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for _sub in ['shared']:
    _p = os.path.join(_root, _sub)
    if _p not in sys.path:
        sys.path.insert(0, _p)

import pytest

from shared.parse_controller import ParseController

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_config_dir       = os.path.join(_root, 'config')
_burn_in_limits   = os.path.join(_config_dir, 'BurnInLimits.yaml')
_cal_limits       = os.path.join(_config_dir, 'CalLimits.yaml')
_burn_in_groups   = os.path.join(_config_dir, 'BurnInLimGroups.yaml')
_cal_groups       = os.path.join(_config_dir, 'CalLimGroups.yaml')
_proto_dir        = os.path.join(_root, 'measurement_data', 'protocol_files')
_burn_in_proto    = os.path.join(
    _proto_dir,
    '2024-01-15_10-15-20_Tuner2_rf12346_dsp67891_Seq2_TxAnt2_Diagram2_BurnIn_Protocol.txt',
)
_cal_proto        = os.path.join(
    _proto_dir,
    '2024-01-15_12-30-45_Tuner1_rf12345_dsp67890_Seq1_TxAnt1_Diagram1_Protocol.txt',
)

_yaml_files_exist  = pytest.mark.skipif(
    not os.path.isfile(_burn_in_limits),
    reason='config/BurnInLimits.yaml not present',
)
_proto_files_exist = pytest.mark.skipif(
    not os.path.isfile(_burn_in_proto),
    reason='BurnIn protocol file not present in measurement_data/',
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_controller():
    return ParseController()


def _inject_protocol(pc, path, prot_type='BurnIn'):
    pc.protToBeParsedDict['protocolPathTypeDictList'].append(
        {'protocolPath': path, 'type': prot_type}
    )


# ---------------------------------------------------------------------------
# TestParseProtocolLimitsGuards
# ---------------------------------------------------------------------------

class TestParseProtocolLimitsGuards:
    """parse_protocol_limits must skip gracefully for missing/sentinel paths."""

    def test_empty_burn_in_path_no_crash(self, tmp_path):
        proto = tmp_path / 'dummy_Protocol.txt'
        proto.write_text('Gen26_UseBurnInMeas[1];3\n')
        pc = _make_controller()
        _inject_protocol(pc, str(proto), 'BurnIn')
        pc.parse_protocol_limits(
            burn_in_limits_path='',
            cal_limits_path='',
            include_burn_in=True,
            include_cal=False,
            extend_burn_in=False,
            extend_cal=False,
        )
        # Protocol skipped — both dicts still empty
        assert pc.burnInParsedProtDict['protocolParsingDictList'] == []
        assert pc.burnInFailedProtDict['protocolParsingDictList'] == []

    def test_no_file_set_label_no_crash(self, tmp_path):
        proto = tmp_path / 'dummy_Protocol.txt'
        proto.write_text('Gen26_UseBurnInMeas[1];3\n')
        pc = _make_controller()
        _inject_protocol(pc, str(proto), 'BurnIn')
        pc.parse_protocol_limits(
            burn_in_limits_path='No file set.',
            cal_limits_path='No file set.',
            include_burn_in=True,
            include_cal=True,
            extend_burn_in=False,
            extend_cal=False,
        )
        assert pc.burnInParsedProtDict['protocolParsingDictList'] == []
        assert pc.burnInFailedProtDict['protocolParsingDictList'] == []

    def test_include_false_skips_matching_type(self, tmp_path):
        proto = tmp_path / 'dummy_Protocol.txt'
        proto.write_text('Gen26_UseBurnInMeas[1];3\n')
        pc = _make_controller()
        _inject_protocol(pc, str(proto), 'BurnIn')
        pc.parse_protocol_limits(
            burn_in_limits_path=_burn_in_limits,
            cal_limits_path=_cal_limits,
            include_burn_in=False,   # <-- disabled
            include_cal=False,
            extend_burn_in=False,
            extend_cal=False,
        )
        assert pc.burnInParsedProtDict['protocolParsingDictList'] == []
        assert pc.burnInFailedProtDict['protocolParsingDictList'] == []

    def test_nonexistent_yaml_routes_to_failed_not_crash(self, tmp_path):
        proto = tmp_path / 'dummy_Protocol.txt'
        proto.write_text('Gen26_UseBurnInMeas[1];3\n')
        pc = _make_controller()
        _inject_protocol(pc, str(proto), 'BurnIn')
        pc.parse_protocol_limits(
            burn_in_limits_path=str(tmp_path / 'nonexistent.yaml'),
            cal_limits_path='',
            include_burn_in=True,
            include_cal=False,
            extend_burn_in=False,
            extend_cal=False,
        )
        # Must not raise; protocol lands in failed dict
        assert len(pc.burnInFailedProtDict['protocolParsingDictList']) == 1
        assert pc.burnInParsedProtDict['protocolParsingDictList'] == []

    def test_already_parsed_not_duplicated(self, tmp_path):
        proto = tmp_path / 'dummy_Protocol.txt'
        proto.write_text('Gen26_UseBurnInMeas[1];3\n')
        pc = _make_controller()
        _inject_protocol(pc, str(proto), 'BurnIn')
        # Simulate previously parsed
        pc.burnInParsedProtDict['protocolParsingDictList'].append(
            {'protocolPath': str(proto), 'type': 'BurnIn',
             'parsing': 'BurnIn', 'parsedData': None}
        )
        pc.parse_protocol_limits(
            burn_in_limits_path='',
            cal_limits_path='',
            include_burn_in=True,
            include_cal=False,
            extend_burn_in=False,
            extend_cal=False,
        )
        # Still only one entry (de-dup)
        assert len(pc.burnInParsedProtDict['protocolParsingDictList']) == 1


# ---------------------------------------------------------------------------
# TestFullPipelineWithRealYaml
# ---------------------------------------------------------------------------

class TestFullPipelineWithRealYaml:
    """End-to-end: real YAML + real protocol files → no exception anywhere."""

    @_yaml_files_exist
    @_proto_files_exist
    def test_burn_in_parse_no_exception(self):
        pc = _make_controller()
        _inject_protocol(pc, _burn_in_proto, 'BurnIn')
        pc.parse_protocol_limits(
            burn_in_limits_path=_burn_in_limits,
            cal_limits_path='',
            include_burn_in=True,
            include_cal=False,
            extend_burn_in=False,
            extend_cal=False,
        )
        total = (
            len(pc.burnInParsedProtDict['protocolParsingDictList'])
            + len(pc.burnInFailedProtDict['protocolParsingDictList'])
        )
        assert total == 1  # exactly one protocol processed

    @_yaml_files_exist
    @pytest.mark.skipif(
        not os.path.isfile(_cal_proto),
        reason='Cal protocol file not present in measurement_data/',
    )
    def test_cal_parse_no_exception(self):
        pc = _make_controller()
        _inject_protocol(pc, _cal_proto, 'Calibration')
        pc.parse_protocol_limits(
            burn_in_limits_path='',
            cal_limits_path=_cal_limits,
            include_burn_in=False,
            include_cal=True,
            extend_burn_in=False,
            extend_cal=False,
        )
        total = (
            len(pc.calParsedProtDict['protocolParsingDictList'])
            + len(pc.calFailedProtDict['protocolParsingDictList'])
        )
        assert total == 1

    @_yaml_files_exist
    @_proto_files_exist
    def test_build_limits_rows_after_real_parse(self):
        pc = _make_controller()
        _inject_protocol(pc, _burn_in_proto, 'BurnIn')
        pc.parse_protocol_limits(
            burn_in_limits_path=_burn_in_limits,
            cal_limits_path='',
            include_burn_in=True,
            include_cal=False,
            extend_burn_in=False,
            extend_cal=False,
        )
        pc.build_limits_rows()
        rows = pc.limitsRowListDict['limitsRowList']
        # All rows must have non-empty limitName and correct protType
        for row in rows:
            assert row.limitName != ''
            assert row.protType == 'BurnIn'

    @_yaml_files_exist
    @_proto_files_exist
    def test_build_limits_groups_after_real_parse(self):
        pc = _make_controller()
        _inject_protocol(pc, _burn_in_proto, 'BurnIn')
        pc.parse_protocol_limits(
            burn_in_limits_path=_burn_in_limits,
            cal_limits_path='',
            include_burn_in=True,
            include_cal=False,
            extend_burn_in=False,
            extend_cal=False,
        )
        pc.build_limits_rows()
        pc.build_limits_groups(
            burn_in_lim_groups_path=_burn_in_groups,
            cal_lim_groups_path='',
            include_burn_in=True,
            include_cal=False,
            extend_burn_in_groups=False,
            extend_cal_groups=False,
        )
        # Navigation index must reset to -1 regardless of group count
        assert pc.burnInLimitsGroupDict['activeGroupIndex'] == -1

    @_yaml_files_exist
    @_proto_files_exist
    def test_compute_limits_stats_assigns_indices(self):
        pc = _make_controller()
        _inject_protocol(pc, _burn_in_proto, 'BurnIn')
        pc.parse_protocol_limits(
            burn_in_limits_path=_burn_in_limits,
            cal_limits_path='',
            include_burn_in=True,
            include_cal=False,
            extend_burn_in=False,
            extend_cal=False,
        )
        pc.build_limits_rows()
        pc.compute_limits_stats()
        rows = pc.limitsRowListDict['limitsRowList']
        for i, row in enumerate(rows):
            assert row.index == i

    @_yaml_files_exist
    @_proto_files_exist
    def test_full_pipeline_clear_state_resets(self):
        pc = _make_controller()
        _inject_protocol(pc, _burn_in_proto, 'BurnIn')
        pc.parse_protocol_limits(
            burn_in_limits_path=_burn_in_limits,
            cal_limits_path='',
            include_burn_in=True,
            include_cal=False,
            extend_burn_in=False,
            extend_cal=False,
        )
        pc.build_limits_rows()
        pc.build_limits_groups(
            burn_in_lim_groups_path=_burn_in_groups,
            cal_lim_groups_path='',
            include_burn_in=True,
            include_cal=False,
            extend_burn_in_groups=False,
            extend_cal_groups=False,
        )
        pc.compute_limits_stats()

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
