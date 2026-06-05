"""File downloads router — serve generated output files to the web UI.

After generating PPTX, YAML, or DAT files via /start endpoints, the web UI
needs to download them. This router lists and serves files from the output
directories defined in shared.auxiliary.
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from typing import List, Dict
import os
import glob

from shared import auxiliary as aux

router = APIRouter()


# Map user-friendly names to the actual output paths
_OUTPUT_DIRS = {
    "system_diagrams": aux.antSysDiagOutputPath,
    "tx_diagrams": aux.txAntDiagOutputPath,
    "antenna_patterns": aux.antPatOutputPath,
    "huellkurven": aux.huellKurvenOutputPath,
    "statistic": aux.statisticOutputPath,
    "certificates": aux.certificatesOutputPath,
    "merge": aux.mergeOutputPath,
}


@router.get("/list/{output_type}")
def list_output_files(output_type: str) -> Dict[str, List[str]]:
    """List all files in the specified output directory.

    Args:
        output_type: One of system_diagrams, tx_diagrams, antenna_patterns,
                     huellkurven, statistic, certificates, merge.

    Returns:
        {"files": ["Antenna_diagrams.pptx", ...], "directory": "C:\\...\\output"}
    """
    if output_type not in _OUTPUT_DIRS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid output_type. Must be one of: {', '.join(_OUTPUT_DIRS.keys())}",
        )

    output_dir = _OUTPUT_DIRS[output_type]
    if not os.path.isdir(output_dir):
        return {"files": [], "directory": output_dir}

    # List all files (non-recursive for top-level; adjust if needed)
    files = []
    for entry in os.listdir(output_dir):
        path = os.path.join(output_dir, entry)
        if os.path.isfile(path):
            files.append(entry)

    return {"files": sorted(files), "directory": output_dir}


@router.get("/list/{output_type}/recursive")
def list_output_files_recursive(output_type: str) -> Dict[str, List[Dict[str, str]]]:
    """Recursively list all files in the output directory tree.

    Useful for huellkurven output (has AntTypeN subdirectories) and
    antenna_patterns (may have subdirectories per configuration).

    Returns:
        {"files": [{"path": "AntType1/Az_...", "size": 12345, "modified": "..."}], ...}
    """
    if output_type not in _OUTPUT_DIRS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid output_type. Must be one of: {', '.join(_OUTPUT_DIRS.keys())}",
        )

    output_dir = _OUTPUT_DIRS[output_type]
    if not os.path.isdir(output_dir):
        return {"files": [], "directory": output_dir}

    file_list = []
    for root, _, filenames in os.walk(output_dir):
        for filename in filenames:
            full_path = os.path.join(root, filename)
            rel_path = os.path.relpath(full_path, output_dir)
            stat = os.stat(full_path)
            file_list.append({
                "path": rel_path.replace("\\", "/"),  # Normalize for web
                "size": stat.st_size,
                "modified": stat.st_mtime,
            })

    return {"files": sorted(file_list, key=lambda x: x["path"]), "directory": output_dir}


@router.get("/download/{output_type}/{filename:path}")
def download_file(output_type: str, filename: str):
    """Download a specific file from the output directory.

    Args:
        output_type: Output directory type (system_diagrams, tx_diagrams, etc.)
        filename: Relative path to the file (e.g., "Antenna_diagrams.pptx"
                  or "AntType1/Az_TxAnt0_Diagram0_Chirp0.dat")

    Returns:
        File download response with appropriate Content-Type.
    """
    if output_type not in _OUTPUT_DIRS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid output_type. Must be one of: {', '.join(_OUTPUT_DIRS.keys())}",
        )

    output_dir = _OUTPUT_DIRS[output_type]
    file_path = os.path.normpath(os.path.join(output_dir, filename))

    # Security check: prevent directory traversal
    if not file_path.startswith(os.path.normpath(output_dir)):
        raise HTTPException(status_code=400, detail="Invalid file path.")

    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found.")

    # Determine media type based on extension
    ext = os.path.splitext(file_path)[1].lower()
    media_type_map = {
        ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        ".yaml": "application/x-yaml",
        ".yml": "application/x-yaml",
        ".json": "application/json",
        ".dat": "text/plain",
        ".txt": "text/plain",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".csv": "text/csv",
    }
    media_type = media_type_map.get(ext, "application/octet-stream")

    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=os.path.basename(file_path),
    )


@router.delete("/clear/{output_type}")
def clear_output_directory(output_type: str):
    """Delete all files in the specified output directory.

    Equivalent to clicking 'Clear' before generating new output.
    """
    if output_type not in _OUTPUT_DIRS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid output_type. Must be one of: {', '.join(_OUTPUT_DIRS.keys())}",
        )

    output_dir = _OUTPUT_DIRS[output_type]
    if not os.path.isdir(output_dir):
        return {"status": "directory_not_found", "path": output_dir}

    status, msg = aux.clearAll(output_dir)
    if not status:
        raise HTTPException(status_code=500, detail=f"Failed to clear directory: {msg}")

    return {"status": "cleared", "path": output_dir}
