"""Unit tests for shared.parse_helpers.

Tests cover the pure-logic helpers extracted from main.py:
  - filter_protocol_file_lists
  - merge_into_parsed_dicts
  - deduplicate_protocol_list
  - walk_protocol_files
  - update_filtered_protocol_list
  - collect_unparsed_protocols
"""
import pytest
from types import SimpleNamespace
from shared.parse_helpers import (
    filter_protocol_file_lists,
    merge_into_parsed_dicts,
    deduplicate_protocol_list,
    walk_protocol_files,
    update_filtered_protocol_list,
    collect_unparsed_protocols,
)


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------

def _make_entry(path: str, ptype: str = "Cal") -> dict:
    return {"protocolPath": path, "type": ptype}


def _make_sys_entry(path: str) -> dict:
    return {"protocolPath": path, "ptu2FilesList": [f"{path}_ptu2.txt"]}


def _make_tx_entry(path: str) -> dict:
    return {"protocolPath": path, "txAntDiagList": [f"{path}_tx.txt"]}


def _make_parsed_item(file_name_path: str):
    """Minimal object with .fileTitle.fileNamePath like PTU2ParseData."""
    ft = SimpleNamespace(fileNamePath=file_name_path)
    return SimpleNamespace(fileTitle=ft)


def _empty_prot_to_be_parsed() -> dict:
    return {"protocolPathTypeDictList": []}


def _empty_parsed_prot() -> dict:
    return {"protocolPathTypeDictList": []}


def _empty_file_path_dict() -> dict:
    return {"filePathList": []}


def _empty_parsed_data_dict() -> dict:
    return {"parsedDataList": []}


# ---------------------------------------------------------------------------
# filter_protocol_file_lists
# ---------------------------------------------------------------------------

class TestFilterProtocolFileLists:

    def test_single_match_both(self):
        path = "/prot/a.txt"
        prot = {"protocolPathTypeDictList": [_make_entry(path)]}
        sys_d = {"filePathList": [_make_sys_entry(path)]}
        tx_d  = {"filePathList": [_make_tx_entry(path)]}
        parsed = _empty_parsed_prot()

        sys_list, tx_list = filter_protocol_file_lists(prot, sys_d, tx_d, parsed)

        assert len(sys_list) == 1
        assert sys_list[0]["protocolPath"] == path
        assert len(tx_list) == 1
        assert tx_list[0]["protocolPath"] == path

    def test_no_match_returns_empty_stub_entries(self):
        """When no file-list entry matches, an empty stub is appended so the
        output lists stay index-aligned with protToBeParsedDict."""
        prot  = {"protocolPathTypeDictList": [_make_entry("/prot/a.txt")]}
        sys_d = {"filePathList": [_make_sys_entry("/prot/other.txt")]}
        tx_d  = {"filePathList": [_make_tx_entry("/prot/other.txt")]}
        parsed = _empty_parsed_prot()

        sys_list, tx_list = filter_protocol_file_lists(prot, sys_d, tx_d, parsed)

        assert len(sys_list) == 1
        assert sys_list[0] == {"protocolPath": "/prot/a.txt", "ptu2FilesList": []}
        assert len(tx_list) == 1
        assert tx_list[0] == {"protocolPath": "/prot/a.txt", "txAntDiagList": []}

    def test_partial_match_only_sys(self):
        """When only sys matches, tx gets an empty stub (aligned output)."""
        path = "/prot/a.txt"
        prot  = {"protocolPathTypeDictList": [_make_entry(path)]}
        sys_d = {"filePathList": [_make_sys_entry(path)]}
        tx_d  = {"filePathList": []}
        parsed = _empty_parsed_prot()

        sys_list, tx_list = filter_protocol_file_lists(prot, sys_d, tx_d, parsed)

        assert len(sys_list) == 1
        assert sys_list[0]["protocolPath"] == path
        assert len(tx_list) == 1
        assert tx_list[0] == {"protocolPath": path, "txAntDiagList": []}

    def test_partial_match_only_tx(self):
        """When only tx matches, sys gets an empty stub (aligned output)."""
        path = "/prot/b.txt"
        prot  = {"protocolPathTypeDictList": [_make_entry(path)]}
        sys_d = {"filePathList": []}
        tx_d  = {"filePathList": [_make_tx_entry(path)]}
        parsed = _empty_parsed_prot()

        sys_list, tx_list = filter_protocol_file_lists(prot, sys_d, tx_d, parsed)

        assert len(sys_list) == 1
        assert sys_list[0] == {"protocolPath": path, "ptu2FilesList": []}
        assert len(tx_list) == 1
        assert tx_list[0]["protocolPath"] == path

    def test_appends_to_parsed_prot_dict(self):
        paths = ["/prot/a.txt", "/prot/b.txt"]
        entries = [_make_entry(p) for p in paths]
        prot   = {"protocolPathTypeDictList": entries}
        sys_d  = _empty_file_path_dict()
        tx_d   = _empty_file_path_dict()
        parsed = _empty_parsed_prot()

        filter_protocol_file_lists(prot, sys_d, tx_d, parsed)

        assert len(parsed["protocolPathTypeDictList"]) == 2
        assert parsed["protocolPathTypeDictList"][0]["protocolPath"] == paths[0]
        assert parsed["protocolPathTypeDictList"][1]["protocolPath"] == paths[1]

    def test_appends_unconditionally_even_without_file_match(self):
        """Protocol is marked as 'attempted' even when no files are found."""
        prot   = {"protocolPathTypeDictList": [_make_entry("/prot/missing.txt")]}
        sys_d  = _empty_file_path_dict()
        tx_d   = _empty_file_path_dict()
        parsed = _empty_parsed_prot()

        filter_protocol_file_lists(prot, sys_d, tx_d, parsed)

        assert len(parsed["protocolPathTypeDictList"]) == 1

    def test_empty_protocols_returns_empty(self):
        prot   = _empty_prot_to_be_parsed()
        sys_d  = {"filePathList": [_make_sys_entry("/prot/a.txt")]}
        tx_d   = {"filePathList": [_make_tx_entry("/prot/a.txt")]}
        parsed = _empty_parsed_prot()

        sys_list, tx_list = filter_protocol_file_lists(prot, sys_d, tx_d, parsed)

        assert sys_list == []
        assert tx_list == []
        assert parsed["protocolPathTypeDictList"] == []

    def test_multiple_protocols_match_correct_files(self):
        paths = ["/prot/a.txt", "/prot/b.txt", "/prot/c.txt"]
        prot  = {"protocolPathTypeDictList": [_make_entry(p) for p in paths]}
        sys_d = {"filePathList": [_make_sys_entry(p) for p in paths]}
        tx_d  = {"filePathList": [_make_tx_entry(p) for p in paths]}
        parsed = _empty_parsed_prot()

        sys_list, tx_list = filter_protocol_file_lists(prot, sys_d, tx_d, parsed)

        assert len(sys_list) == 3
        assert [e["protocolPath"] for e in sys_list] == paths
        assert len(tx_list) == 3
        assert [e["protocolPath"] for e in tx_list] == paths

    def test_uses_first_match_when_duplicates_in_file_list(self):
        """next() always picks the first matching entry."""
        path = "/prot/a.txt"
        prot  = {"protocolPathTypeDictList": [_make_entry(path)]}
        entry1 = {"protocolPath": path, "ptu2FilesList": ["first.txt"]}
        entry2 = {"protocolPath": path, "ptu2FilesList": ["second.txt"]}
        sys_d = {"filePathList": [entry1, entry2]}
        tx_d  = _empty_file_path_dict()
        parsed = _empty_parsed_prot()

        sys_list, _ = filter_protocol_file_lists(prot, sys_d, tx_d, parsed)

        assert sys_list[0]["ptu2FilesList"] == ["first.txt"]

    def test_does_not_modify_input_dicts_beyond_parsedProtDict(self):
        path = "/prot/a.txt"
        prot  = {"protocolPathTypeDictList": [_make_entry(path)]}
        sys_d = {"filePathList": [_make_sys_entry(path)]}
        tx_d  = {"filePathList": [_make_tx_entry(path)]}
        parsed = _empty_parsed_prot()

        original_sys_len = len(sys_d["filePathList"])
        original_tx_len  = len(tx_d["filePathList"])

        filter_protocol_file_lists(prot, sys_d, tx_d, parsed)

        assert len(sys_d["filePathList"]) == original_sys_len
        assert len(tx_d["filePathList"]) == original_tx_len


# ---------------------------------------------------------------------------
# merge_into_parsed_dicts
# ---------------------------------------------------------------------------

class TestMergeIntoParsedDicts:

    def test_appends_new_items(self):
        sys_dict = _empty_parsed_data_dict()
        tx_dict  = _empty_parsed_data_dict()
        sys_list = [_make_parsed_item("/path/a.txt")]
        tx_list  = [_make_parsed_item("/path/b.txt")]

        merge_into_parsed_dicts(sys_list, tx_list, sys_dict, tx_dict)

        assert len(sys_dict["parsedDataList"]) == 1
        assert sys_dict["parsedDataList"][0].fileTitle.fileNamePath == "/path/a.txt"
        assert len(tx_dict["parsedDataList"]) == 1
        assert tx_dict["parsedDataList"][0].fileTitle.fileNamePath == "/path/b.txt"

    def test_skips_duplicate_sys_items(self):
        existing = _make_parsed_item("/path/a.txt")
        sys_dict = {"parsedDataList": [existing]}
        tx_dict  = _empty_parsed_data_dict()
        # same path again
        sys_list = [_make_parsed_item("/path/a.txt")]

        merge_into_parsed_dicts(sys_list, [], sys_dict, tx_dict)

        assert len(sys_dict["parsedDataList"]) == 1

    def test_skips_duplicate_tx_items(self):
        sys_dict = _empty_parsed_data_dict()
        existing = _make_parsed_item("/path/b.txt")
        tx_dict  = {"parsedDataList": [existing]}
        tx_list  = [_make_parsed_item("/path/b.txt")]

        merge_into_parsed_dicts([], tx_list, sys_dict, tx_dict)

        assert len(tx_dict["parsedDataList"]) == 1

    def test_new_items_added_duplicates_skipped(self):
        existing = _make_parsed_item("/path/a.txt")
        sys_dict = {"parsedDataList": [existing]}
        tx_dict  = _empty_parsed_data_dict()
        sys_list = [
            _make_parsed_item("/path/a.txt"),   # duplicate
            _make_parsed_item("/path/new.txt"),  # new
        ]

        merge_into_parsed_dicts(sys_list, [], sys_dict, tx_dict)

        assert len(sys_dict["parsedDataList"]) == 2
        paths = [d.fileTitle.fileNamePath for d in sys_dict["parsedDataList"]]
        assert "/path/a.txt" in paths
        assert "/path/new.txt" in paths

    def test_empty_lists_do_not_mutate_dicts(self):
        item = _make_parsed_item("/path/x.txt")
        sys_dict = {"parsedDataList": [item]}
        tx_dict  = {"parsedDataList": [item]}

        merge_into_parsed_dicts([], [], sys_dict, tx_dict)

        assert len(sys_dict["parsedDataList"]) == 1
        assert len(tx_dict["parsedDataList"]) == 1

    def test_multiple_new_items_all_appended(self):
        sys_dict = _empty_parsed_data_dict()
        tx_dict  = _empty_parsed_data_dict()
        sys_list = [_make_parsed_item(f"/path/s{i}.txt") for i in range(5)]
        tx_list  = [_make_parsed_item(f"/path/t{i}.txt") for i in range(3)]

        merge_into_parsed_dicts(sys_list, tx_list, sys_dict, tx_dict)

        assert len(sys_dict["parsedDataList"]) == 5
        assert len(tx_dict["parsedDataList"]) == 3

    def test_duplicate_within_incoming_list_only_added_once(self):
        """Two items with the same path in the incoming list: only one should land."""
        sys_dict = _empty_parsed_data_dict()
        tx_dict  = _empty_parsed_data_dict()
        sys_list = [
            _make_parsed_item("/path/dupe.txt"),
            _make_parsed_item("/path/dupe.txt"),
        ]

        merge_into_parsed_dicts(sys_list, [], sys_dict, tx_dict)

        assert len(sys_dict["parsedDataList"]) == 1

    def test_sys_and_tx_independent(self):
        """A path duplicate in sys does not affect tx dedup."""
        same_path = "/path/shared.txt"
        sys_dict = {"parsedDataList": [_make_parsed_item(same_path)]}
        tx_dict  = _empty_parsed_data_dict()
        tx_list  = [_make_parsed_item(same_path)]  # same path, different dict

        merge_into_parsed_dicts([], tx_list, sys_dict, tx_dict)

        # sys unchanged, tx gets the new item
        assert len(sys_dict["parsedDataList"]) == 1
        assert len(tx_dict["parsedDataList"]) == 1


# ---------------------------------------------------------------------------
# deduplicate_protocol_list
# ---------------------------------------------------------------------------

class TestDeduplicateProtocolList:

    def test_empty_existing_returns_all(self):
        result = deduplicate_protocol_list(['a.txt', 'b.txt'], [])
        assert result == ['a.txt', 'b.txt']

    def test_all_duplicates_returns_empty(self):
        existing = [{'protocolPath': 'a.txt'}, {'protocolPath': 'b.txt'}]
        result = deduplicate_protocol_list(['a.txt', 'b.txt'], existing)
        assert result == []

    def test_partial_duplicates(self):
        existing = [{'protocolPath': 'a.txt'}]
        result = deduplicate_protocol_list(['a.txt', 'b.txt'], existing)
        assert result == ['b.txt']

    def test_empty_input_returns_empty(self):
        result = deduplicate_protocol_list([], [{'protocolPath': 'a.txt'}])
        assert result == []

    def test_preserves_order(self):
        result = deduplicate_protocol_list(['c.txt', 'a.txt', 'b.txt'], [])
        assert result == ['c.txt', 'a.txt', 'b.txt']

    def test_no_mutation_of_input(self):
        orig = ['a.txt', 'b.txt']
        existing = [{'protocolPath': 'a.txt'}]
        deduplicate_protocol_list(orig, existing)
        assert orig == ['a.txt', 'b.txt']


# ---------------------------------------------------------------------------
# walk_protocol_files
# ---------------------------------------------------------------------------

def _make_pre_parse_info(path, error=False, abort=False, limits=False):
    return SimpleNamespace(
        PathName=path,
        bErrorOccured=error,
        bAbortCriterion=abort,
        bLimitExceeded=limits,
    )


def _mock_ptu2_fn(dir_path, pattern):
    return [f'{dir_path}/ptu2_match.txt']


def _mock_txantdiag_fn(dir_path, stem):
    return [f'{dir_path}/txant_match.txt']


def _noop_fn(dir_path, arg):
    return []


class TestWalkProtocolFiles:

    def test_search_ptu2_only(self):
        protos = [_make_pre_parse_info('/data/Protocol.txt')]
        ptu2, tx, acc, err, abort, lim = walk_protocol_files(
            protos, True, False, False, False, False,
            _mock_ptu2_fn, _noop_fn,
        )
        assert len(ptu2) == 1
        assert ptu2[0]['protocolPath'] == '/data/Protocol.txt'
        assert ptu2[0]['ptu2FilesList'] == ['/data/ptu2_match.txt']
        assert tx == []
        assert acc == ['/data/Protocol.txt']

    def test_search_txantdiag_only(self):
        protos = [_make_pre_parse_info('/data/Protocol.txt')]
        ptu2, tx, acc, err, abort, lim = walk_protocol_files(
            protos, False, True, False, False, False,
            _noop_fn, _mock_txantdiag_fn,
        )
        assert ptu2 == []
        assert len(tx) == 1
        assert tx[0]['protocolPath'] == '/data/Protocol.txt'
        assert tx[0]['txAntDiagList'] == ['/data/txant_match.txt']

    def test_search_both(self):
        protos = [_make_pre_parse_info('/data/Protocol.txt')]
        ptu2, tx, acc, err, abort, lim = walk_protocol_files(
            protos, True, True, False, False, False,
            _mock_ptu2_fn, _mock_txantdiag_fn,
        )
        assert len(ptu2) == 1
        assert len(tx) == 1

    def test_error_flag_collected(self):
        protos = [_make_pre_parse_info('/data/Protocol.txt', error=True)]
        _, _, acc, err, abort, lim = walk_protocol_files(
            protos, False, False, True, False, False,
            _noop_fn, _noop_fn,
        )
        assert err == ['/data/Protocol.txt']
        assert abort == []
        assert lim == []

    def test_abort_flag_collected(self):
        protos = [_make_pre_parse_info('/data/Protocol.txt', abort=True)]
        _, _, acc, err, abort, lim = walk_protocol_files(
            protos, False, False, False, True, False,
            _noop_fn, _noop_fn,
        )
        assert abort == ['/data/Protocol.txt']

    def test_limits_flag_collected(self):
        protos = [_make_pre_parse_info('/data/Protocol.txt', limits=True)]
        _, _, acc, err, abort, lim = walk_protocol_files(
            protos, False, False, False, False, True,
            _noop_fn, _noop_fn,
        )
        assert lim == ['/data/Protocol.txt']

    def test_flags_not_collected_when_disabled(self):
        """Error/abort/limits not appended when their use-flag is False."""
        protos = [_make_pre_parse_info('/data/Protocol.txt', error=True, abort=True, limits=True)]
        _, _, acc, err, abort, lim = walk_protocol_files(
            protos, False, False, False, False, False,
            _noop_fn, _noop_fn,
        )
        assert err == [] and abort == [] and lim == []

    def test_acc_prot_always_appended(self):
        protos = [
            _make_pre_parse_info('/data/A_Protocol.txt'),
            _make_pre_parse_info('/data/B_Protocol.txt'),
        ]
        _, _, acc, *_ = walk_protocol_files(
            protos, False, False, False, False, False,
            _noop_fn, _noop_fn,
        )
        assert acc == ['/data/A_Protocol.txt', '/data/B_Protocol.txt']

    def test_empty_input_returns_empty_lists(self):
        ptu2, tx, acc, err, abort, lim = walk_protocol_files(
            [], True, True, True, True, True,
            _mock_ptu2_fn, _mock_txantdiag_fn,
        )
        assert ptu2 == tx == acc == err == abort == lim == []

    def test_filename_strip_protocol_chip(self):
        """'Protocol_Chip' prefix is stripped when building the PTU2 search pattern."""
        called_with = {}

        def capture_ptu2_fn(dir_path, pattern):
            called_with['pattern'] = pattern
            return []

        protos = [_make_pre_parse_info('/data/Protocol_Chip_2024.txt')]
        walk_protocol_files(
            protos, True, False, False, False, False,
            capture_ptu2_fn, _noop_fn,
        )
        # After stripping 'Protocol_Chip', stem should contain '_2024'
        assert 'ptu2' in called_with['pattern'].lower()
        assert 'Protocol_Chip' not in called_with['pattern']


# ---------------------------------------------------------------------------
# update_filtered_protocol_list
# ---------------------------------------------------------------------------

class TestUpdateFilteredProtocolList:

    def _fdict(self, paths=None):
        return {'protocolPathList': list(paths or [])}

    def test_new_paths_added(self):
        fdict = self._fdict()
        update_filtered_protocol_list(['a.txt', 'b.txt'], fdict, set())
        assert fdict['protocolPathList'] == ['a.txt', 'b.txt']

    def test_existing_paths_not_duplicated(self):
        fdict = self._fdict(['a.txt'])
        update_filtered_protocol_list(['a.txt', 'b.txt'], fdict, set())
        assert fdict['protocolPathList'].count('a.txt') == 1
        assert 'b.txt' in fdict['protocolPathList']

    def test_accepted_paths_removed(self):
        fdict = self._fdict(['a.txt', 'b.txt', 'c.txt'])
        update_filtered_protocol_list([], fdict, {'a.txt', 'c.txt'})
        assert fdict['protocolPathList'] == ['b.txt']

    def test_add_then_remove_accepted(self):
        """Paths added in this call that are also in accepted_set are removed."""
        fdict = self._fdict()
        update_filtered_protocol_list(['a.txt', 'b.txt'], fdict, {'a.txt'})
        assert fdict['protocolPathList'] == ['b.txt']

    def test_empty_inputs_no_change(self):
        fdict = self._fdict(['x.txt'])
        update_filtered_protocol_list([], fdict, set())
        assert fdict['protocolPathList'] == ['x.txt']

    def test_all_accepted_leaves_empty_list(self):
        fdict = self._fdict(['a.txt', 'b.txt'])
        update_filtered_protocol_list([], fdict, {'a.txt', 'b.txt'})
        assert fdict['protocolPathList'] == []


# ---------------------------------------------------------------------------
# collect_unparsed_protocols
# ---------------------------------------------------------------------------

class TestCollectUnparsedProtocols:

    def _parsed_dict(self, paths):
        return {'protocolPathTypeDictList': [{'protocolPath': p} for p in paths]}

    def _to_parse_dict(self):
        return {'protocolPathTypeDictList': []}

    def _accepted(self, paths):
        return [{'protocolPath': p, 'type': 'Cal'} for p in paths]

    def test_all_new_appended(self):
        to_parse = self._to_parse_dict()
        skipped = collect_unparsed_protocols(
            self._accepted(['a.txt', 'b.txt']),
            self._parsed_dict([]),
            to_parse,
        )
        assert len(to_parse['protocolPathTypeDictList']) == 2
        assert skipped == []

    def test_already_parsed_skipped(self):
        to_parse = self._to_parse_dict()
        skipped = collect_unparsed_protocols(
            self._accepted(['a.txt', 'b.txt']),
            self._parsed_dict(['a.txt']),
            to_parse,
        )
        paths = [d['protocolPath'] for d in to_parse['protocolPathTypeDictList']]
        assert paths == ['b.txt']
        assert skipped == ['a.txt']

    def test_all_already_parsed(self):
        to_parse = self._to_parse_dict()
        skipped = collect_unparsed_protocols(
            self._accepted(['a.txt', 'b.txt']),
            self._parsed_dict(['a.txt', 'b.txt']),
            to_parse,
        )
        assert to_parse['protocolPathTypeDictList'] == []
        assert set(skipped) == {'a.txt', 'b.txt'}

    def test_empty_accepted_no_change(self):
        to_parse = self._to_parse_dict()
        skipped = collect_unparsed_protocols([], self._parsed_dict(['a.txt']), to_parse)
        assert to_parse['protocolPathTypeDictList'] == []
        assert skipped == []

    def test_no_double_append_on_repeated_call(self):
        """Calling twice with the same accepted list must not duplicate entries."""
        parsed = self._parsed_dict([])
        to_parse = self._to_parse_dict()
        collect_unparsed_protocols(self._accepted(['a.txt']), parsed, to_parse)
        # Simulate second call: 'a.txt' now in parsed
        parsed['protocolPathTypeDictList'].append({'protocolPath': 'a.txt'})
        collect_unparsed_protocols(self._accepted(['a.txt']), parsed, to_parse)
        paths = [d['protocolPath'] for d in to_parse['protocolPathTypeDictList']]
        assert paths.count('a.txt') == 1
