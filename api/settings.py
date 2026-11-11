"""Deployment settings for the web API, read from environment variables.

This module must be imported before anything from ``shared`` so the
``CST_APP_DIR`` default is in place when ``shared.user_paths`` is first loaded.

Environment variables
---------------------
CST_DATA_DIR            Root for everything the server writes (default: <tmp>/cst-web).
CST_APP_DIR             Config / templates / logs dir of the engine (default: <data>/app).
CST_SESSION_TTL_HOURS   Idle time after which a session workspace is deleted (default 24).
CST_MAX_SESSIONS        Maximum number of live session workspaces (default 200).
CST_LOCK_TIMEOUT_SECONDS  How long a request waits for a busy session/engine (default 900).
CST_MAX_UPLOAD_MB       Maximum size of one upload request (default 500).
CST_CORS_ORIGINS        Comma separated list of extra allowed browser origins.
"""
import os
import tempfile

DATA_DIR = os.path.abspath(os.environ.get("CST_DATA_DIR") or os.path.join(tempfile.gettempdir(), "cst-web"))
os.environ.setdefault("CST_APP_DIR", os.path.join(DATA_DIR, "app"))
# Per-session output folders replace the engine's fixed ones; this only keeps stray writes inside DATA_DIR
os.environ.setdefault("CST_OUTPUT_BASE", os.path.join(DATA_DIR, "shared_output"))

SESSIONS_DIR = os.path.join(DATA_DIR, "sessions")
SESSION_TTL_SECONDS = float(os.environ.get("CST_SESSION_TTL_HOURS", "24")) * 3600
MAX_SESSIONS = int(os.environ.get("CST_MAX_SESSIONS", "200"))
LOCK_TIMEOUT_SECONDS = float(os.environ.get("CST_LOCK_TIMEOUT_SECONDS", "900"))
MAX_UPLOAD_BYTES = int(float(os.environ.get("CST_MAX_UPLOAD_MB", "500")) * 1024 * 1024)

DEV_CORS_ORIGINS = [
    "http://localhost:5173", "http://localhost:5174",
    "http://127.0.0.1:5173", "http://127.0.0.1:5174",
]
CORS_ORIGINS = DEV_CORS_ORIGINS + [
    o.strip() for o in os.environ.get("CST_CORS_ORIGINS", "").split(",") if o.strip()
]
