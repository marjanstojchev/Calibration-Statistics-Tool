"""File downloads router — serve the files a session generated to the web UI.

After generating PPTX, YAML, or DAT files via the /start endpoints, the web UI
lists and downloads them from the session's own output folders. A browser never
sees the files of another session, and no server path is exposed.
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from typing import Any, Dict
import os
import shutil

from api.session import OUTPUT_KINDS, Session, exclusive, get_session, safe_join

router = APIRouter()

_MEDIA_TYPES = {
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".yaml": "application/x-yaml",
    ".yml": "application/x-yaml",
    ".json": "application/json",
    ".dat": "text/plain",
    ".txt": "text/plain",
    ".log": "text/plain",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".csv": "text/csv",
}


def _output_dir(session: Session, output_type: str) -> str:
    if output_type not in OUTPUT_KINDS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid output_type. Must be one of: {', '.join(OUTPUT_KINDS)}",
        )
    return session.output_dir(output_type)


@router.get("/list/{output_type}")
def list_output_files(output_type: str, session: Session = Depends(get_session)) -> Dict[str, Any]:
    """List the files in the top level of one of the session's output folders.

    Args:
        output_type: One of system_diagrams, tx_diagrams, antenna_patterns,
                     huellkurven, statistic, certificates, merge, set_curves.

    Returns:
        {"files": ["Antenna_diagrams.pptx", ...], "output_type": "system_diagrams"}
    """
    output_dir = _output_dir(session, output_type)
    files = []
    if os.path.isdir(output_dir):
        files = sorted(e for e in os.listdir(output_dir) if os.path.isfile(os.path.join(output_dir, e)))
    return {"files": files, "output_type": output_type}


@router.get("/list/{output_type}/recursive")
def list_output_files_recursive(output_type: str, session: Session = Depends(get_session)) -> Dict[str, Any]:
    """Recursively list all files in an output folder.

    Useful for huellkurven output (has AntTypeN subdirectories) and
    antenna_patterns (may have subdirectories per configuration).

    Returns:
        {"files": [{"path": "AntType1/Az_...", "size": 12345, "modified": 1.7e9}], ...}
    """
    output_dir = _output_dir(session, output_type)
    file_list = []
    for root, _, filenames in os.walk(output_dir):
        for filename in filenames:
            full_path = os.path.join(root, filename)
            try:
                stat = os.stat(full_path)
            except OSError:
                continue  # removed by a clear while listing
            file_list.append({
                "path": os.path.relpath(full_path, output_dir).replace("\\", "/"),
                "size": stat.st_size,
                "modified": stat.st_mtime,
            })

    return {"files": sorted(file_list, key=lambda x: x["path"]), "output_type": output_type}


@router.get("/download/{output_type}/{filename:path}")
def download_file(output_type: str, filename: str, session: Session = Depends(get_session)):
    """Download a specific file from one of the session's output folders.

    Args:
        output_type: Output folder type (system_diagrams, tx_diagrams, etc.)
        filename: Relative path to the file (e.g., "Antenna_diagrams.pptx"
                  or "AntType1/Az_TxAnt0_Diagram0_Chirp0.dat")
    """
    output_dir = _output_dir(session, output_type)
    file_path = safe_join(output_dir, filename)
    if file_path is None:
        raise HTTPException(status_code=400, detail="Invalid file path.")
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found.")

    ext = os.path.splitext(file_path)[1].lower()
    return FileResponse(
        path=file_path,
        media_type=_MEDIA_TYPES.get(ext, "application/octet-stream"),
        filename=os.path.basename(file_path),
    )


@router.delete("/clear/{output_type}")
def clear_output_directory(output_type: str, session: Session = Depends(get_session)):
    """Delete all files in one of the session's output folders.

    Waits for a running operation of the session, so files are never deleted
    while a generator is still writing them.
    """
    output_dir = _output_dir(session, output_type)
    with exclusive(session, "clear_output"):
        for entry in os.listdir(output_dir):
            path = os.path.join(output_dir, entry)
            if os.path.isdir(path) and not os.path.islink(path):
                shutil.rmtree(path, ignore_errors=True)
            else:
                try:
                    os.remove(path)
                except OSError:
                    pass
    return {"status": "cleared", "output_type": output_type}
