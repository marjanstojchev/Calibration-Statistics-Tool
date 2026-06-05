import os
import sys

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

from fastapi import FastAPI, UploadFile, File

from api.routers import protocols, system_diagrams, logs

app = FastAPI()

app.include_router(protocols.router, prefix="/api/protocols", tags=["protocols"])
app.include_router(system_diagrams.router, prefix="/api/system_diagrams", tags=["system_diagrams"])
app.include_router(logs.router, prefix="/logs", tags=["logs"])

@app.get("/")
def health():
    return {"status": "ok"}

@app.post("/api/parse")
async def parse_file(file: UploadFile = File(...)):
    contents = await file.read()
    # TODO: call your ParseController here
    return {"filename": file.filename, "size": len(contents)}