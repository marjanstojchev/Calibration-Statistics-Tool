"""Tests for the session based REST API.

Tests use the FastAPI TestClient, so no running server is needed. Every test works
in its own session (X-Session-Id) inside a temporary data directory.
"""
import glob
import os
import sys
import tempfile
import threading
import uuid

import pytest

# Ensure project root is on sys.path so api/ and shared/ are importable.
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
for _sub in ["shared", "system_diagrams", "tx_diagrams", "antenna_patterns"]:
    _p = os.path.join(_ROOT, _sub)
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)

# Must be set before api.settings is imported
os.environ.setdefault("CST_DATA_DIR", tempfile.mkdtemp(prefix="cst-test-data-"))
os.environ.setdefault("MPLBACKEND", "Agg")

from fastapi.testclient import TestClient

from api import settings
from api.main import app
from api.session import safe_filename, safe_join, store

client = TestClient(app)

_DATA = os.path.join(_ROOT, "measurement_data")
_PROTOCOLS = sorted(glob.glob(os.path.join(_DATA, "protocol_files", "*Protocol.txt")))
_PTU2 = sorted(glob.glob(os.path.join(_DATA, "ptu_files_backup_shapes", "*_ptu2.txt")))
_TX = sorted(
    p for p in glob.glob(os.path.join(_DATA, "tx_antenna_files", "*.txt"))
    if "ptu2" not in p.lower() and "protocol" not in os.path.basename(p).lower()
)
needs_data = pytest.mark.skipif(not (_PROTOCOLS and _PTU2), reason="sample measurement data not available")


@pytest.fixture
def sid():
    value = str(uuid.uuid4())
    yield value
    store.delete(value)


def h(sid_value):
    return {"X-Session-Id": sid_value}


def upload(sid_value, n_prot=3, n_ptu=3, n_tx=2):
    def part(key, paths):
        return [(key, (os.path.basename(p), open(p, "rb"), "text/plain")) for p in paths]

    files = part("files", _PROTOCOLS[:n_prot]) + part("ptu2_files", _PTU2[:n_ptu]) + part("txantdiag_files", _TX[:n_tx])
    try:
        return client.post("/api/protocols/upload", files=files, headers=h(sid_value))
    finally:
        for _, (_, fh, _) in files:
            fh.close()


# ---------------------------------------------------------------------------
# Health and session id handling
# ---------------------------------------------------------------------------

class TestHealth:
    def test_health_returns_ok(self):
        r = client.get("/api/health")
        assert r.status_code == 200
        assert r.json() == {"status": "ok"}


class TestSessionId:
    def test_missing_session_id_is_rejected(self):
        assert client.get("/api/session").status_code == 400

    @pytest.mark.parametrize("bad", ["short", "../../etc/passwd", "a" * 100, "id with spaces and more chars"])
    def test_invalid_session_id_is_rejected(self, bad):
        assert client.get("/api/session", headers={"X-Session-Id": bad}).status_code == 400

    def test_sid_query_parameter_is_accepted(self, sid):
        assert client.get(f"/api/session?sid={sid}").status_code == 200

    def test_summary_of_new_session_is_empty(self, sid):
        data = client.get("/api/session", headers=h(sid)).json()
        assert data["system_diagram_files"] == 0
        assert data["tx_diagram_files"] == 0

    def test_delete_session_removes_workspace(self, sid):
        client.get("/api/session", headers=h(sid))
        root = store.get(sid).root
        assert os.path.isdir(root)
        assert client.delete("/api/session", headers=h(sid)).status_code == 200
        assert not os.path.exists(root)


# ---------------------------------------------------------------------------
# Tabs without data: a clear 422 instead of a 500
# ---------------------------------------------------------------------------

class TestNoData:
    @pytest.mark.parametrize("path", [
        "/api/system_diagrams/start",
        "/api/tx_diagrams/start",
        "/api/antenna_patterns/start",
        "/api/huellkurven/start",
        "/api/interactive/fill",
    ])
    def test_start_without_data_returns_422(self, sid, path):
        r = client.post(path, headers=h(sid))
        assert r.status_code == 422
        assert "detail" in r.json()

    def test_limits_compute_without_data_returns_422(self, sid):
        assert client.post("/api/limits/compute", json={}, headers=h(sid)).status_code == 422

    def test_limits_rows_before_compute_returns_422(self, sid):
        assert client.get("/api/limits/rows", headers=h(sid)).status_code == 422

    def test_limits_type_is_validated(self, sid):
        assert client.post("/api/limits/compute", json={"limits_type": "nonsense"}, headers=h(sid)).status_code == 400

    def test_stats_returns_counts(self, sid):
        data = client.get("/api/stats/", headers=h(sid)).json()
        assert data["sys_diag_ptu2_loaded"] == 0
        assert data["tx_ant_diag_loaded"] == 0

    def test_interactive_state_starts_empty(self, sid):
        assert client.get("/api/interactive/state", headers=h(sid)).json()["filled"] is False


# ---------------------------------------------------------------------------
# Upload, clear and isolation
# ---------------------------------------------------------------------------

@needs_data
class TestUpload:
    def test_upload_loads_files(self, sid):
        r = upload(sid, n_ptu=4, n_tx=2)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["status"] == "ok"
        assert data["ptu2_files_loaded"] == 4
        assert data["tx_ant_diag_loaded"] == 2
        assert client.get("/api/stats/", headers=h(sid)).json()["sys_diag_ptu2_loaded"] == 4

    def test_sessions_do_not_share_data(self, sid):
        other = str(uuid.uuid4())
        try:
            assert upload(sid, n_ptu=5).status_code == 200
            assert upload(other, n_ptu=2).status_code == 200
            assert client.get("/api/session", headers=h(sid)).json()["system_diagram_files"] == 5
            assert client.get("/api/session", headers=h(other)).json()["system_diagram_files"] == 2
            client.delete("/api/protocols/clear", headers=h(other))
            assert client.get("/api/session", headers=h(sid)).json()["system_diagram_files"] == 5
        finally:
            store.delete(other)

    def test_repeated_clear_and_upload(self, sid):
        for _ in range(3):
            assert upload(sid, n_ptu=3).status_code == 200
            assert client.delete("/api/protocols/clear", headers=h(sid)).status_code == 200
            assert client.get("/api/session", headers=h(sid)).json()["system_diagram_files"] == 0
        assert upload(sid, n_ptu=3).status_code == 200
        assert client.get("/api/session", headers=h(sid)).json()["system_diagram_files"] == 3

    def test_upload_replaces_previous_data(self, sid):
        assert upload(sid, n_ptu=5).status_code == 200
        assert upload(sid, n_ptu=2).status_code == 200
        assert client.get("/api/session", headers=h(sid)).json()["system_diagram_files"] == 2
        uploads = os.listdir(store.get(sid).upload_root)
        assert len(uploads) == 1  # the previous upload folder was removed

    def test_concurrent_uploads_leave_consistent_state(self, sid):
        codes = []
        sizes = [2, 3, 4]

        def run(n):
            codes.append(upload(sid, n_ptu=n).status_code)

        threads = [threading.Thread(target=run, args=(n,)) for n in sizes]
        [t.start() for t in threads]
        [t.join() for t in threads]
        assert codes == [200] * len(sizes)
        loaded = client.get("/api/session", headers=h(sid)).json()["system_diagram_files"]
        assert loaded in sizes  # exactly one upload won, none is half applied
        assert len(os.listdir(store.get(sid).upload_root)) == 1

    def test_upload_without_protocols_keeps_old_data(self, sid):
        assert upload(sid, n_ptu=3).status_code == 200
        r = client.post("/api/protocols/upload", headers=h(sid))
        assert r.status_code == 422
        assert client.get("/api/session", headers=h(sid)).json()["system_diagram_files"] == 3

    def test_protocol_options_are_stored_for_limits(self, sid):
        with open(_PROTOCOLS[0], "rb") as fh:
            r = client.post(
                "/api/protocols/upload?protocol_type=calibration&burn_in_start=true",
                files=[("files", (os.path.basename(_PROTOCOLS[0]), fh, "text/plain"))],
                headers=h(sid),
            )
        assert r.status_code == 200, r.text
        assert r.json()["filters_applied"]["protocol_type"] == "calibration"
        assert store.get(sid).state["protocol_options"] == {"burn_in_cal_mode": 2, "include_burn_in_start": True}

    def test_invalid_protocol_type_is_rejected(self, sid):
        r = client.post(
            "/api/protocols/upload?protocol_type=bogus",
            files=[("files", ("x_Protocol.txt", b"x", "text/plain"))],
            headers=h(sid),
        )
        assert r.status_code == 400
        assert not os.path.isdir(store.get(sid).upload_root) or not os.listdir(store.get(sid).upload_root)

    def test_clear_waits_for_running_operation(self, sid, monkeypatch):
        monkeypatch.setattr(settings, "LOCK_TIMEOUT_SECONDS", 0.2)
        session = store.get(sid)
        with session.lock:
            r = client.delete("/api/protocols/clear", headers=h(sid))
        assert r.status_code == 409
        assert client.delete("/api/protocols/clear", headers=h(sid)).status_code == 200

    def test_interactive_fill_and_state(self, sid):
        assert upload(sid, n_ptu=3).status_code == 200
        filled = client.post("/api/interactive/fill", headers=h(sid)).json()
        assert filled["filled"] is True
        assert client.get("/api/interactive/state", headers=h(sid)).json()["protocol_count"] == filled["protocol_count"]
        assert client.delete("/api/protocols/clear", headers=h(sid)).status_code == 200
        assert client.get("/api/interactive/state", headers=h(sid)).json()["filled"] is False


# ---------------------------------------------------------------------------
# Limits
# ---------------------------------------------------------------------------

@needs_data
class TestLimits:
    def test_compute_rows_and_groups(self, sid):
        assert upload(sid, n_prot=len(_PROTOCOLS), n_ptu=1, n_tx=0).status_code == 200
        r = client.post("/api/limits/compute", json={"limits_type": "burn_in"}, headers=h(sid))
        assert r.status_code == 200, r.text
        assert r.json()["row_count"] > 0
        rows = client.get("/api/limits/rows", headers=h(sid)).json()
        assert rows["row_count"] == r.json()["row_count"]
        assert client.get("/api/limits/groups", headers=h(sid)).status_code == 200

    def test_result_belongs_to_one_session(self, sid):
        other = str(uuid.uuid4())
        try:
            assert upload(sid, n_prot=len(_PROTOCOLS), n_ptu=1, n_tx=0).status_code == 200
            assert client.post("/api/limits/compute", json={}, headers=h(sid)).status_code == 200
            assert client.get("/api/limits/rows", headers=h(other)).status_code == 422
        finally:
            store.delete(other)

    def test_invalid_yaml_config_is_rejected(self, sid):
        r = client.post(
            "/api/limits/config/burn_in_limits",
            files={"file": ("x.yaml", b"key: [unclosed", "text/yaml")},
            headers=h(sid),
        )
        assert r.status_code == 400

    def test_unknown_config_name_is_rejected(self, sid):
        r = client.post(
            "/api/limits/config/passwd",
            files={"file": ("x.yaml", b"a: 1", "text/yaml")},
            headers=h(sid),
        )
        assert r.status_code == 404


# ---------------------------------------------------------------------------
# Downloads and safe paths
# ---------------------------------------------------------------------------

class TestDownloads:
    def _write(self, sid_value, name="result.txt", kind="system_diagrams"):
        folder = store.get(sid_value).output_dir(kind)
        with open(os.path.join(folder, name), "w") as fh:
            fh.write("hello")

    def test_list_and_download_own_file(self, sid):
        self._write(sid)
        listing = client.get("/api/downloads/list/system_diagrams", headers=h(sid)).json()
        assert listing["files"] == ["result.txt"]
        assert "directory" not in listing  # no server path is exposed
        r = client.get("/api/downloads/download/system_diagrams/result.txt", headers=h(sid))
        assert r.status_code == 200 and r.content == b"hello"

    def test_download_with_sid_query(self, sid):
        self._write(sid)
        r = client.get(f"/api/downloads/download/system_diagrams/result.txt?sid={sid}")
        assert r.status_code == 200

    def test_other_session_cannot_download(self, sid):
        other = str(uuid.uuid4())
        try:
            self._write(sid)
            r = client.get("/api/downloads/download/system_diagrams/result.txt", headers=h(other))
            assert r.status_code == 404
            assert client.get("/api/downloads/list/system_diagrams", headers=h(other)).json()["files"] == []
        finally:
            store.delete(other)

    @pytest.mark.parametrize("path", ["../../session.json", "..%2F..%2Fsecret.txt", "%2e%2e/%2e%2e/x"])
    def test_traversal_is_blocked(self, sid, path):
        r = client.get(f"/api/downloads/download/system_diagrams/{path}", headers=h(sid))
        assert r.status_code in (400, 404)

    def test_unknown_output_type_is_rejected(self, sid):
        assert client.get("/api/downloads/list/etc", headers=h(sid)).status_code in (400, 404)

    def test_clear_output_only_affects_own_session(self, sid):
        other = str(uuid.uuid4())
        try:
            self._write(sid)
            self._write(other)
            assert client.delete("/api/downloads/clear/system_diagrams", headers=h(sid)).status_code == 200
            assert client.get("/api/downloads/list/system_diagrams", headers=h(sid)).json()["files"] == []
            assert client.get("/api/downloads/list/system_diagrams", headers=h(other)).json()["files"] == ["result.txt"]
        finally:
            store.delete(other)


class TestSafeHelpers:
    @pytest.mark.parametrize("raw,expected", [
        ("report.pptx", "report.pptx"),
        ("../../evil", "evil.pptx"),
        ("..\\..\\evil.pptx", "evil.pptx"),
        ("", "default.pptx"),
        (None, "default.pptx"),
        ("name with $pecial*chars", "name with _pecial_chars.pptx"),
        (".hidden", "hidden.pptx"),
    ])
    def test_safe_filename(self, raw, expected):
        assert safe_filename(raw, "default.pptx", ".pptx") == expected

    def test_safe_join(self, tmp_path):
        base = str(tmp_path)
        assert safe_join(base, "a/b.txt") == os.path.realpath(os.path.join(base, "a", "b.txt"))
        assert safe_join(base, "../outside.txt") is None
        assert safe_join(base, os.path.join("a", "..", "..", "x")) is None


# ---------------------------------------------------------------------------
# Logs
# ---------------------------------------------------------------------------

class TestLogs:
    def test_logs_all_returns_dict(self, sid):
        data = client.get("/logs/all", headers=h(sid)).json()
        assert set(data) == {"system_diagrams", "tx_diagrams", "antenna_patterns", "main_load_data"}

    def test_logs_module_snapshot(self, sid):
        for module in ("system-diagrams", "tx-diagrams", "antenna-patterns", "main-load-data"):
            r = client.get(f"/logs/{module}", headers=h(sid))
            assert r.status_code == 200
            assert isinstance(r.json(), list)

    def test_logs_require_session(self):
        assert client.get("/logs/all").status_code == 400

    @needs_data
    def test_load_log_is_per_session(self, sid):
        other = str(uuid.uuid4())
        try:
            assert upload(sid, n_ptu=3).status_code == 200
            assert client.get("/logs/main-load-data", headers=h(sid)).json()
            assert client.get("/logs/main-load-data", headers=h(other)).json() == []
        finally:
            store.delete(other)
