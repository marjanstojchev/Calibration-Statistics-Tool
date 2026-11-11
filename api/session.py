"""Per-browser sessions for the cloud API.

Every browser gets its own workspace (uploads, outputs, config copies, logs and
parsed data). The engine in ``shared/`` and the generators keep process-wide
state (module globals, fixed output folders, logger file handlers), so every
operation that touches it runs inside :func:`engine`, which

* holds the session lock  (one operation per session at a time), then
* holds the engine lock   (one engine operation per server process),
* points all engine paths at the session workspace and restores them after.

Locks are blocking: a request that arrives while another one of the same
session is running waits for it to finish instead of seeing half-written state.
"""
from __future__ import annotations

import logging
import os
import re
import shutil
import sys
import threading
import time
import uuid
from collections import deque
from contextlib import contextmanager
from typing import Any, Dict, Iterator, List, Optional

from fastapi import Header, HTTPException, Query

from api import settings

SESSION_ID_RE = re.compile(r"^[A-Za-z0-9-]{16,64}$")

LOG_KINDS = ("system_diagrams", "tx_diagrams", "antenna_patterns", "main_load_data")

# Output kinds served by the downloads router, also the folder names inside a workspace
OUTPUT_KINDS = (
    "system_diagrams", "tx_diagrams", "antenna_patterns", "huellkurven",
    "statistic", "certificates", "merge", "set_curves",
)

# aux attribute holding the output folder of every kind
_AUX_OUTPUT_ATTRS = {
    "system_diagrams": "antSysDiagOutputPath",
    "tx_diagrams": "txAntDiagOutputPath",
    "antenna_patterns": "antPatOutputPath",
    "huellkurven": "huellKurvenOutputPath",
    "statistic": "statisticOutputPath",
    "certificates": "certificatesOutputPath",
    "merge": "mergeOutputPath",
    "set_curves": "setCurvesOutputPath",
}

# aux attribute -> file name inside the session config dir
_AUX_CONFIG_FILES = {
    "statsinputconffilepath": "StatisticsLimitsConfig.json",
    "burnInLimitsFilePath": "BurnInLimits.yaml",
    "calLimitsFilePath": "CalLimits.yaml",
    "burnInLimGroupsFilePath": "BurnInLimGroups.yaml",
    "calLimGroupsFilePath": "CalLimGroups.yaml",
}

# logconfig attribute -> log file name inside the session log dir
_LOGCONFIG_FILES = {
    "antSysDiagLogFilePath": "0_ant_system_diagrams.log",
    "txAntDiagLogFilePath": "0_tx_ant_diagrams.log",
    "antPatLogFilePath": "0_antenna_patterns.log",
    "mainLoadDataLogFilePath": "0_main_loaddata.log",
}

_ENGINE_LOGGER_NAMES = (
    "main_loaddata_logger", "0_ant_system_diagrams_logger",
    "tx_ant_diagrams_logger", "antpat_logger",
)

ENGINE_LOCK = threading.Lock()

# Session whose operation currently owns the engine; log records go to its buffers
_active_session: Optional["Session"] = None


class Session:
    def __init__(self, sid: str) -> None:
        self.id = sid
        self.root = os.path.join(settings.SESSIONS_DIR, sid)
        self.upload_root = os.path.join(self.root, "uploads")
        self.upload_dir: Optional[str] = None  # folder of the current upload, inside upload_root
        self.out_root = os.path.join(self.root, "output")
        self.config_dir = os.path.join(self.root, "config")
        self.log_dir = os.path.join(self.root, "logs")
        self.lock = threading.Lock()
        self.busy: Optional[str] = None
        self.last_used = time.time()
        self.log_buffers: Dict[str, deque] = {k: deque(maxlen=1000) for k in LOG_KINDS}
        self.log_totals: Dict[str, int] = {k: 0 for k in LOG_KINDS}
        self.reset_data()
        for path in [self.upload_root, self.config_dir, self.log_dir] + [self.output_dir(k) for k in OUTPUT_KINDS]:
            os.makedirs(path, exist_ok=True)

    def reset_data(self) -> None:
        """Forget everything that came from an upload."""
        if self.upload_dir:
            shutil.rmtree(self.upload_dir, ignore_errors=True)
            self.upload_dir = None
        self.sys_diag_list: List[Any] = []
        self.tx_diag_list: List[Any] = []
        self.protocol_paths: List[str] = []
        self.state: Dict[str, Any] = {}

    def touch(self) -> None:
        self.last_used = time.time()

    def output_dir(self, kind: str) -> str:
        return os.path.join(self.out_root, kind)

    def log_file(self, attr: str) -> str:
        return os.path.join(self.log_dir, _LOGCONFIG_FILES[attr])

    def config_file(self, attr: str) -> str:
        return os.path.join(self.config_dir, _AUX_CONFIG_FILES[attr])

    def ensure_config(self) -> None:
        """Copy the default config files into the workspace once; user edits stay per session."""
        import user_paths as up
        for fname in os.listdir(up.config_dir):
            dst = os.path.join(self.config_dir, fname)
            if not os.path.exists(dst):
                shutil.copy2(os.path.join(up.config_dir, fname), dst)

    def emit_log(self, kind: str, message: str) -> None:
        self.log_buffers[kind].append(message)
        self.log_totals[kind] += 1

    def summary(self) -> Dict[str, Any]:
        return {
            "session_id": self.id,
            "busy": self.busy,
            "protocols": len(self.protocol_paths),
            "system_diagram_files": len(self.sys_diag_list),
            "tx_diagram_files": len(self.tx_diag_list),
        }


class SessionStore:
    def __init__(self) -> None:
        self._sessions: Dict[str, Session] = {}
        self._lock = threading.Lock()

    def get(self, sid: str) -> Session:
        with self._lock:
            session = self._sessions.get(sid)
            if session is None:
                self._purge_locked()
                if len(self._sessions) >= settings.MAX_SESSIONS:
                    raise HTTPException(status_code=503, detail="Server is full, try again later.")
                session = Session(sid)
                self._sessions[sid] = session
            session.touch()
            return session

    def delete(self, sid: str) -> None:
        with self._lock:
            session = self._sessions.get(sid)
            if session is None:
                return
            if not session.lock.acquire(blocking=False):
                raise HTTPException(status_code=409, detail="Session is busy.")
            try:
                del self._sessions[sid]
                shutil.rmtree(session.root, ignore_errors=True)
            finally:
                session.lock.release()

    def purge(self) -> int:
        with self._lock:
            return self._purge_locked()

    def _purge_locked(self) -> int:
        now = time.time()
        removed = 0
        for sid, session in list(self._sessions.items()):
            if now - session.last_used < settings.SESSION_TTL_SECONDS:
                continue
            if not session.lock.acquire(blocking=False):
                continue
            try:
                del self._sessions[sid]
                shutil.rmtree(session.root, ignore_errors=True)
                removed += 1
            finally:
                session.lock.release()
        # Workspaces left behind by a previous server run are removed once they are old enough
        if os.path.isdir(settings.SESSIONS_DIR):
            for name in os.listdir(settings.SESSIONS_DIR):
                path = os.path.join(settings.SESSIONS_DIR, name)
                if name in self._sessions or not os.path.isdir(path):
                    continue
                try:
                    if now - os.path.getmtime(path) > settings.SESSION_TTL_SECONDS:
                        shutil.rmtree(path, ignore_errors=True)
                except OSError:
                    pass
        return removed


store = SessionStore()


def get_session(
    x_session_id: Optional[str] = Header(default=None),
    sid: Optional[str] = Query(default=None),
) -> Session:
    """FastAPI dependency. Plain links and EventSource cannot set headers, so ?sid= is accepted too."""
    value = x_session_id or sid
    if not value or not SESSION_ID_RE.match(value):
        raise HTTPException(status_code=400, detail="Missing or invalid session id (X-Session-Id header).")
    return store.get(value)


def _acquire(lock: threading.Lock, what: str, status: int) -> None:
    if not lock.acquire(timeout=settings.LOCK_TIMEOUT_SECONDS):
        raise HTTPException(status_code=status, detail=f"Timed out waiting for {what}.")


@contextmanager
def exclusive(session: Session, op: str) -> Iterator[Session]:
    """Serialize operations of one session that do not touch the engine (upload staging, clear, ...)."""
    _acquire(session.lock, "the previous operation of this session", 409)
    session.busy = op
    try:
        session.touch()
        yield session
    finally:
        session.busy = None
        session.touch()
        session.lock.release()


@contextmanager
def engine(session: Session, op: str) -> Iterator[Session]:
    """Run engine code for one session: exclusive, with all engine paths pointing into its workspace."""
    global _active_session
    with exclusive(session, op):
        _acquire(ENGINE_LOCK, "the processing engine", 503)
        saved: List[tuple] = []
        try:
            warm_up()
            session.ensure_config()
            _patch_paths(session, saved)
            _reset_file_handlers()
            _active_session = session
            yield session
        finally:
            _active_session = None
            _reset_file_handlers()
            for module, name, value in reversed(saved):
                setattr(module, name, value)
            ENGINE_LOCK.release()


def _modules(*names: str) -> List[Any]:
    # The engine imports 'auxiliary', the API imports 'shared.auxiliary': two module objects
    found = []
    for name in names:
        for candidate in (name, f"shared.{name}"):
            module = sys.modules.get(candidate)
            if module is not None and all(module is not m for m in found):
                found.append(module)
    return found


def _set(saved: List[tuple], modules: List[Any], name: str, value: Any) -> None:
    for module in modules:
        if hasattr(module, name):
            saved.append((module, name, getattr(module, name)))
            setattr(module, name, value)


def _patch_paths(session: Session, saved: List[tuple]) -> None:
    aux = _modules("auxiliary")
    for kind, attr in _AUX_OUTPUT_ATTRS.items():
        _set(saved, aux, attr, session.output_dir(kind))
    _set(saved, aux, "configDir", session.config_dir)
    for attr in _AUX_CONFIG_FILES:
        _set(saved, aux, attr, session.config_file(attr))

    for attr in _LOGCONFIG_FILES:
        _set(saved, _modules("logconfig"), attr, session.log_file(attr))

    # Import-time constants of the plotting modules
    _set(saved, _modules("plotdata"), "outputDir", session.output_dir("system_diagrams"))
    tx_plot = [m for n in ("txantdiag_plotdata", "tx_diagrams.txantdiag_plotdata")
               if (m := sys.modules.get(n)) is not None]
    _set(saved, tx_plot, "outputDir", session.output_dir("tx_diagrams"))


def _reset_file_handlers() -> None:
    """Generators add a new file handler on every run; drop them so runs never write to old sessions' files."""
    for name in _ENGINE_LOGGER_NAMES:
        logger = logging.getLogger(name)
        for handler in list(logger.handlers):
            if isinstance(handler, logging.FileHandler):
                logger.removeHandler(handler)
                handler.close()
    for module in _modules("logconfig"):
        for attr in ("antSysDiagLogger", "txAntDiagLogger", "antPatLogger", "mainLoadDataLogger"):
            wrapper = getattr(module, attr, None)
            if wrapper is not None:
                wrapper.fileHandlerDict.clear()


def fresh_load_log(session: Session) -> None:
    """Start a new main-load-data log file for the session (call inside :func:`engine`)."""
    for module in _modules("logconfig"):
        module.mainLoadDataLogger.addFileHandler(session.log_file("mainLoadDataLogFilePath"), "w+")
        break


def emit_active_log(kind: str, message: str) -> None:
    """Called by the log handlers: route a record to the session owning the engine."""
    session = _active_session
    if session is not None:
        session.emit_log(kind, message)


_warmed = False


def warm_up() -> None:
    """Import every engine module up front so import-time constants are patched consistently."""
    global _warmed
    if _warmed:
        return
    _warmed = True
    import importlib
    for name in (
        "auxiliary", "logconfig", "shared.auxiliary", "plotdata", "txantdiag_plotdata",
        "loaddata", "parse_controller",
        "system_diagrams.AntennaSystemDiagrams", "tx_diagrams.TxAntDiagrams",
        "antenna_patterns.antpat_v5_main_v3",
    ):
        try:
            importlib.import_module(name)
        except Exception:
            logging.getLogger("cst.api").exception("Warm-up import failed: %s", name)


def new_session_id() -> str:
    return str(uuid.uuid4())


NO_DATA_MESSAGE = "No data loaded. Upload files in the Protocols tab first."


def safe_filename(name: Optional[str], default: str, ext: str) -> str:
    """Reduce a user supplied file name to a plain, safe base name with the given extension."""
    base = os.path.basename((name or "").replace("\\", "/")).strip()
    base = re.sub(r"[^A-Za-z0-9._ -]", "_", base).lstrip(".")
    if not base:
        base = default
    if not base.lower().endswith(ext):
        base += ext
    return base


def safe_join(base_dir: str, relative: str) -> Optional[str]:
    """Join a user supplied relative path onto base_dir; None if it would escape base_dir."""
    base = os.path.realpath(base_dir)
    target = os.path.realpath(os.path.join(base, relative))
    try:
        if os.path.commonpath([base, target]) != base:
            return None
    except ValueError:
        return None
    return target
