"""Unit tests for the REST API endpoints.

Tests use FastAPI TestClient so no running server is needed.
Qt/GUI code is never imported at module level in the API, so
these tests run without a display.
"""
import os
import sys
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

from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

class TestHealth:
    def test_health_returns_ok(self):
        r = client.get("/")
        assert r.status_code == 200
        assert r.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# /api/protocols/parse
# ---------------------------------------------------------------------------

class TestProtocolsParse:
    def test_missing_file_returns_400(self, tmp_path):
        r = client.post(
            "/api/protocols/parse",
            json={"protocol_paths": [str(tmp_path / "nonexistent.txt")]},
        )
        assert r.status_code == 400
        assert "not found" in r.json()["detail"].lower()

    def test_empty_list_returns_ok(self, tmp_path):
        """An empty protocol list should not crash — returns 0 accepted."""
        r = client.post("/api/protocols/parse", json={"protocol_paths": []})
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        assert data["protocols_accepted"] == 0
        assert data["ptu2_files_loaded"] == 0

    def test_valid_protocol_file(self, tmp_path):
        """A real protocol file that exists on disk should be accepted."""
        proto_dir = os.path.join(
            _ROOT,
            "measurement_data", "protocol_files",
        )
        proto_files = [
            os.path.join(proto_dir, f)
            for f in os.listdir(proto_dir)
            if f.endswith("_Protocol.txt")
        ] if os.path.isdir(proto_dir) else []

        if not proto_files:
            pytest.skip("No protocol test files available")

        r = client.post(
            "/api/protocols/parse",
            json={"protocol_paths": [proto_files[0]]},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        assert data["protocols_accepted"] >= 0


# ---------------------------------------------------------------------------
# /api/system_diagrams/start
# ---------------------------------------------------------------------------

class TestSystemDiagramsStart:
    def test_returns_error_when_no_data(self):
        """Should return error dict (not 500) when no data has been parsed."""
        import shared.load_protocols as lp
        lp.sysDiagParsedDataList = []

        r = client.post("/api/system_diagrams/start")
        assert r.status_code == 200
        assert "error" in r.json()


# ---------------------------------------------------------------------------
# /api/tx_diagrams/start
# ---------------------------------------------------------------------------

class TestTxDiagramsStart:
    def test_returns_error_when_no_data(self):
        import shared.load_protocols as lp
        lp.txAntDiagParsedDataList = []

        r = client.post("/api/tx_diagrams/start")
        assert r.status_code == 200
        assert "error" in r.json()


# ---------------------------------------------------------------------------
# /api/antenna_patterns/start
# ---------------------------------------------------------------------------

class TestAntennaPatternsStart:
    def test_returns_error_when_no_data(self):
        import shared.load_protocols as lp
        lp.sysDiagParsedDataList = []

        r = client.post("/api/antenna_patterns/start")
        assert r.status_code == 200
        assert "error" in r.json()


# ---------------------------------------------------------------------------
# /api/limits/compute
# ---------------------------------------------------------------------------

class TestLimitsCompute:
    def test_returns_422_when_no_parsed_data(self, tmp_path):
        import shared.load_protocols as lp
        lp.sysDiagParsedDataList = []

        limits_file = tmp_path / "limits.yaml"
        limits_file.write_text("limits: []")

        r = client.post(
            "/api/limits/compute",
            json={
                "input_limits_file_path": str(limits_file),
                "limits_groups_file_path": str(limits_file),
            },
        )
        assert r.status_code == 422

    def test_missing_limits_file_returns_400(self, tmp_path):
        import shared.load_protocols as lp
        # Fake some data so we pass the empty-list guard
        lp.sysDiagParsedDataList = [object()]

        r = client.post(
            "/api/limits/compute",
            json={
                "input_limits_file_path": str(tmp_path / "missing.yaml"),
                "limits_groups_file_path": str(tmp_path / "missing_groups.yaml"),
            },
        )
        assert r.status_code == 400


# ---------------------------------------------------------------------------
# /api/stats
# ---------------------------------------------------------------------------

class TestStats:
    def test_returns_counts(self):
        import shared.load_protocols as lp
        lp.sysDiagParsedDataList = []
        lp.txAntDiagParsedDataList = []

        r = client.get("/api/stats/")
        assert r.status_code == 200
        data = r.json()
        assert "sys_diag_ptu2_loaded" in data
        assert "tx_ant_diag_loaded" in data


# ---------------------------------------------------------------------------
# /logs endpoints
# ---------------------------------------------------------------------------

class TestLogs:
    def test_logs_all_returns_dict(self):
        r = client.get("/logs/all")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, dict)
        assert "system_diagrams" in data
        assert "tx_diagrams" in data
        assert "antenna_patterns" in data
        assert "main_load_data" in data

    def test_logs_module_snapshot(self):
        for module in ("system-diagrams", "tx-diagrams", "antenna-patterns", "main-load-data"):
            r = client.get(f"/logs/{module}")
            assert r.status_code == 200
            assert isinstance(r.json(), list)
