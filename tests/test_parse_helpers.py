"""Unit tests for shared.parse_helpers.

Tests cover the two pure-logic helpers extracted from main.parseData:
  - filter_protocol_file_lists
  - merge_into_parsed_dicts
"""
import pytest
from types import SimpleNamespace
from shared.parse_helpers import filter_protocol_file_lists, merge_into_parsed_dicts


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

    def test_no_match_returns_empty_lists(self):
        prot  = {"protocolPathTypeDictList": [_make_entry("/prot/a.txt")]}
        sys_d = {"filePathList": [_make_sys_entry("/prot/other.txt")]}
        tx_d  = {"filePathList": [_make_tx_entry("/prot/other.txt")]}
        parsed = _empty_parsed_prot()

        sys_list, tx_list = filter_protocol_file_lists(prot, sys_d, tx_d, parsed)

        assert sys_list == []
        assert tx_list == []

    def test_partial_match_only_sys(self):
        path = "/prot/a.txt"
        prot  = {"protocolPathTypeDictList": [_make_entry(path)]}
        sys_d = {"filePathList": [_make_sys_entry(path)]}
        tx_d  = {"filePathList": []}
        parsed = _empty_parsed_prot()

        sys_list, tx_list = filter_protocol_file_lists(prot, sys_d, tx_d, parsed)

        assert len(sys_list) == 1
        assert tx_list == []

    def test_partial_match_only_tx(self):
        path = "/prot/b.txt"
        prot  = {"protocolPathTypeDictList": [_make_entry(path)]}
        sys_d = {"filePathList": []}
        tx_d  = {"filePathList": [_make_tx_entry(path)]}
        parsed = _empty_parsed_prot()

        sys_list, tx_list = filter_protocol_file_lists(prot, sys_d, tx_d, parsed)

        assert sys_list == []
        assert len(tx_list) == 1

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
