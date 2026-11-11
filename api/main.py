import os
import sys

# The API renders images only; a GUI backend inside worker threads is unreliable.
os.environ.setdefault("MPLBACKEND", "Agg")

# Setup sys.path for shared module imports (same as _cst_stub/main.py)
_root = os.path.dirname(os.path.abspath(__file__))
_parent = os.path.dirname(_root)
_base = _parent if os.path.isdir(os.path.join(_parent, 'shared')) else _root
if _base not in sys.path:
    sys.path.insert(0, _base)
for _subdir in ['shared', 'ui', 'system_diagrams', 'tx_diagrams', 'antenna_patterns']:
    _path = os.path.join(_base, _subdir)
    if os.path.isdir(_path) and _path not in sys.path:
        sys.path.insert(0, _path)

from api import settings  # noqa: E402,F401  (must come before anything from shared/: sets CST_APP_DIR)

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from api.session import store, warm_up
from api.routers import (
    protocols,
    system_diagrams,
    tx_diagrams,
    antenna_patterns,
    huellkurven,
    interactive,
    limits,
    protocol_stats,
    logs,
    downloads,
    session_info,
)


async def _purge_loop():
    while True:
        await asyncio.sleep(600)
        await asyncio.to_thread(store.purge)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    os.makedirs(settings.SESSIONS_DIR, exist_ok=True)
    await asyncio.to_thread(warm_up)
    await asyncio.to_thread(store.purge)
    task = asyncio.create_task(_purge_loop())
    try:
        yield
    finally:
        task.cancel()


app = FastAPI(title="Calibration Statistics Tool API", version="1.0.0", lifespan=lifespan)

# Browsers on another origin (e.g. the Vite dev server) may call the API; add more via CST_CORS_ORIGINS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health():
    return {"status": "ok"}

app.include_router(session_info.router,     prefix="/api/session",               tags=["session"])
app.include_router(protocols.router,        prefix="/api/protocols",             tags=["protocols"])
app.include_router(system_diagrams.router,  prefix="/api/system_diagrams",       tags=["system_diagrams"])
app.include_router(tx_diagrams.router,      prefix="/api/tx_diagrams",           tags=["tx_diagrams"])
app.include_router(antenna_patterns.router, prefix="/api/antenna_patterns",      tags=["antenna_patterns"])
app.include_router(huellkurven.router,      prefix="/api/huellkurven",           tags=["huellkurven"])
app.include_router(interactive.router,      prefix="/api/interactive",           tags=["interactive"])
app.include_router(limits.router,           prefix="/api/limits",                tags=["limits"])
app.include_router(protocol_stats.router,   prefix="/api/stats",                 tags=["stats"])
app.include_router(logs.router,             prefix="/logs",                      tags=["logs"])
app.include_router(downloads.router,        prefix="/api/downloads",             tags=["downloads"])

# Serve React frontend static files (if built)
_react_dist = Path(__file__).parent.parent / "cst-frontend" / "dist"
if _react_dist.exists():
    app.mount("/", StaticFiles(directory=str(_react_dist), html=True), name="frontend")