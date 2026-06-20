from fastapi import FastAPI, UploadFile, File, APIRouter, Depends, HTTPException
from enum import Enum
from pydantic import BaseModel
from typing import TYPE_CHECKING
import os
import tempfile
from pathlib import Path
import yaml

if TYPE_CHECKING:
    from shared.parse_controller import ParseController

router = APIRouter()


class ParseRequest(BaseModel):
    protocol_paths: list[str]
    search_ptu2_files: bool = True
    search_txantdiag_files: bool = False
    use_error: bool = False
    use_abort: bool = True
    use_limits_exceeded: bool = True
    latest_protocol: bool = False


@router.post("/parse")
def parse_protocols(req: ParseRequest):
    """Full parse pipeline: pre-parse → filter → find PTU2 files → load data → store.

    Accepts server-side file paths (protocol .txt files already on disk).
    Only searches for PTU2/TxAnt files if search flags are enabled (no redundant searches).
    Stores loaded data in shared.load_protocols.sysDiagParsedDataList so that
    /api/system_diagrams/start can use it immediately afterwards.
    
    Pipeline:
    1. Validate protocol file paths
    2. Pre-parse protocol metadata
    3. Filter protocols based on error/abort/limits flags
    4. IF search flags enabled → search for PTU2/TxAnt files
    5. Load measurement data
    6. Store in shared module for downstream endpoints
    """
    import protocolsTest as protocolFilter
    import loaddata as ld
    import shared.load_protocols as lp
    from shared.parse_helpers import walk_protocol_files

    # Validate paths
    for p in req.protocol_paths:
        if not os.path.isfile(p):
            raise HTTPException(status_code=400, detail=f"File not found: {p}")

    # Load plotSetup from YAML config (needed by LoadData)
    config_path = Path(__file__).parent.parent.parent / "shared" / "config" / "AntennaSystemDiagramsConf.yaml"
    with open(config_path, "r", encoding="utf8") as f:
        config = yaml.safe_load(f)
    use_sensor_muster = config["plotSetup"]["useSensorMuster"]
    sensor_muster_list = config["plotSetup"]["sensorMusterList"]

    # Step 1: Pre-parse protocol files
    pre_parsed, *_ = protocolFilter.ProtocolInfoClass.PreParseProtcols(req.protocol_paths)

    # Step 2: Filter protocols
    accepted, _ = protocolFilter.ProtocolInfoClass.FilterProtocols(
        pre_parsed, req.use_error, req.use_abort, req.use_limits_exceeded
    )

    if req.latest_protocol:
        accepted = protocolFilter.ProtocolInfoClass.FilterNewProtocols(accepted)

    # Step 3: Find PTU2 and TxAntDiag files ONLY if search flags are enabled
    # Skip filesystem search if both flags are False (no redundant searches)
    sys_diag_parsed_data_list = []
    tx_ant_diag_parsed_data_list = []
    
    if req.search_ptu2_files or req.search_txantdiag_files:
        ptu2_files_list, txantdiag_files_list, *_ = walk_protocol_files(
            accepted,
            req.search_ptu2_files,
            req.search_txantdiag_files,
            req.use_error,
            req.use_abort,
            req.use_limits_exceeded,
            protocolFilter.ProtocolInfoClass.getfiltered_ptu2filelist,
            protocolFilter.ProtocolInfoClass.getfiltered_txantdiagramfilelist,
        )

        # Step 4a: Load PTU2 data (system diagrams + antenna patterns)
        if req.search_ptu2_files:
            for entry in ptu2_files_list:
                ptu2_files = entry.get("ptu2FilesList", [])
                if not ptu2_files:
                    continue
                loaded = ld.LoadData(ptu2_files, use_sensor_muster, sensor_muster_list)
                if loaded.invalidPath != 1:
                    sys_diag_parsed_data_list += loaded.parseDataList

        # Step 4b: Load TxAntDiag data
        if req.search_txantdiag_files:
            import load_TxAntData as ld_tx
            for entry in txantdiag_files_list:
                tx_files = entry.get("txAntDiagList", [])
                if not tx_files:
                    continue
                loaded_tx = ld_tx.LoadData(tx_files, use_sensor_muster, sensor_muster_list)
                if loaded_tx.invalidPath != 1:
                    tx_ant_diag_parsed_data_list += loaded_tx.parseDataList

    # Step 5: Store in shared module for downstream endpoints
    lp.sysDiagParsedDataList = sys_diag_parsed_data_list
    lp.txAntDiagParsedDataList = tx_ant_diag_parsed_data_list

    return {
        "status": "ok",
        "protocols_accepted": len(accepted),
        "ptu2_files_loaded": len(sys_diag_parsed_data_list),
        "tx_ant_diag_loaded": len(tx_ant_diag_parsed_data_list),
    }

def get_controller():
    # Lazy-load to avoid Qt initialization at module level
    from shared.parse_controller import ParseController
    return ParseController()

@router.post("/upload")
async def upload_protocols(
    files: list[UploadFile] = File(...),
    ptu2_files: list[UploadFile] = File(None),
    txantdiag_files: list[UploadFile] = File(None),
    search_ptu2_files: bool = True,
    search_txantdiag_files: bool = False,
    use_error: bool = False,
    use_abort: bool = True,
    use_limits_exceeded: bool = True,
    latest_protocol: bool = False,
    controller: "ParseController" = Depends(get_controller)
):
    """Upload protocol files from browser and apply filtering options.
    
    Browser workflow (recommended for web/cloud):
    - Frontend discovers and provides protocol + PTU2/TxAnt files
    - Search flags are IGNORED (no filesystem search)
    - Backend processes only the provided files
    
    Server-side workflow (fallback for backward compatibility):
    - No files provided from browser
    - Search flags enable filesystem search for PTU2/TxAnt
    
    Pipeline:
    1. Save uploaded protocol files to temp directory
    2. Pre-parse protocol metadata (error flags, abort criteria)
    3. Filter protocols based on error/abort/limits flags
    4. IF files provided → use them directly (NO filesystem search)
    5. IF files NOT provided AND search flags enabled → search filesystem
    6. Load measurement data from used files
    7. Store in shared module for downstream endpoints
    
    Returns filter results and file counts.
    """
    import protocolsTest as protocolFilter
    import loaddata as ld
    import shared.load_protocols as lp
    from shared.parse_helpers import walk_protocol_files
    
    # Step 0: Save uploaded protocol files to temp
    protocol_paths = []
    for f in files:
        filename = f.filename or ""
        suffix = os.path.splitext(filename)[1]
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        tmp.write(await f.read())
        tmp.close()
        protocol_paths.append(tmp.name)

    # Load plotSetup from YAML config (needed by LoadData)
    config_path = Path(__file__).parent.parent.parent / "shared" / "config" / "AntennaSystemDiagramsConf.yaml"
    with open(config_path, "r", encoding="utf8") as f:
        config = yaml.safe_load(f)
    use_sensor_muster = config["plotSetup"]["useSensorMuster"]
    sensor_muster_list = config["plotSetup"]["sensorMusterList"]

    # Step 1: Pre-parse protocol files (reads metadata: error flags, abort criteria, etc.)
    pre_parsed, *_ = protocolFilter.ProtocolInfoClass.PreParseProtcols(protocol_paths)

    # Step 2: Filter protocols based on error/abort/limits flags
    # ⚠️ Filtering happens HERE - BEFORE full parsing and PTU2 discovery
    accepted, _ = protocolFilter.ProtocolInfoClass.FilterProtocols(
        pre_parsed, use_error, use_abort, use_limits_exceeded
    )

    if latest_protocol:
        accepted = protocolFilter.ProtocolInfoClass.FilterNewProtocols(accepted)

    # Step 3: Handle PTU2 and TxAntDiag files
    # Option A: Use provided files from frontend (cloud/web/browser workflow) - NO filesystem search
    # Option B: Search filesystem if no files provided (server-side workflow only)
    
    ptu2_paths = []
    txantdiag_paths = []
    
    # Browser workflow: use provided files directly, never search filesystem
    if ptu2_files:
        # Use provided PTU2 files from frontend
        for f in ptu2_files:
            filename = f.filename or ""
            suffix = os.path.splitext(filename)[1]
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            tmp.write(await f.read())
            tmp.close()
            ptu2_paths.append(tmp.name)
    
    if txantdiag_files:
        # Use provided TxAnt files from frontend
        for f in txantdiag_files:
            filename = f.filename or ""
            suffix = os.path.splitext(filename)[1]
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            tmp.write(await f.read())
            tmp.close()
            txantdiag_paths.append(tmp.name)
    
    # Server-side workflow: only search filesystem if NO files provided from browser
    # AND if search flags are enabled
    if not ptu2_files and not txantdiag_files and (search_ptu2_files or search_txantdiag_files):
        # Modular search: can be enabled for server-side deployments
        ptu2_files_list, txantdiag_files_list, *_ = walk_protocol_files(
            accepted,
            search_ptu2_files,
            search_txantdiag_files,
            use_error,
            use_abort,
            use_limits_exceeded,
            protocolFilter.ProtocolInfoClass.getfiltered_ptu2filelist,
            protocolFilter.ProtocolInfoClass.getfiltered_txantdiagramfilelist,
        )
        # Extract paths from search results
        for entry in ptu2_files_list:
            ptu2_paths.extend(entry.get("ptu2FilesList", []))
        for entry in txantdiag_files_list:
            txantdiag_paths.extend(entry.get("txAntDiagList", []))

    # Step 4a: Load PTU2 data (system diagrams + antenna patterns)
    sys_diag_parsed_data_list = []
    if ptu2_paths:
        loaded = ld.LoadData(ptu2_paths, use_sensor_muster, sensor_muster_list)
        if loaded.invalidPath != 1:
            sys_diag_parsed_data_list = loaded.parseDataList

    # Step 4b: Load TxAntDiag data
    tx_ant_diag_parsed_data_list = []
    if txantdiag_paths:
        import load_TxAntData as ld_tx
        loaded_tx = ld_tx.LoadData(txantdiag_paths, use_sensor_muster, sensor_muster_list)
        if loaded_tx.invalidPath != 1:
            tx_ant_diag_parsed_data_list = loaded_tx.parseDataList

    # Step 5: Store in shared module for downstream endpoints
    lp.sysDiagParsedDataList = sys_diag_parsed_data_list
    lp.txAntDiagParsedDataList = tx_ant_diag_parsed_data_list

    return {
        "status": "ok",
        "protocols_accepted": len(accepted),
        "ptu2_files_loaded": len(sys_diag_parsed_data_list),
        "tx_ant_diag_loaded": len(tx_ant_diag_parsed_data_list),
        "filters_applied": {
            "use_error": use_error,
            "use_abort": use_abort,
            "use_limits_exceeded": use_limits_exceeded,
            "latest_protocol": latest_protocol,
            "search_ptu2_files": search_ptu2_files,
            "search_txantdiag_files": search_txantdiag_files
        }
    }


@router.post("/count")         # ← another endpoint on same router
def protocol_count():
    return {"count": 42}


@router.delete("/clear")
def clear_protocols():
    """Clear all parsed protocol data from memory.

    This resets the module-level sysDiagParsedDataList and txAntDiagParsedDataList
    back to empty lists, equivalent to the 'Clear Data' button in the Parse Protocols tab.
    
    Also clears the limits module state since limits depend on parsed data.
    """
    import shared.load_protocols as lp
    from api.routers import limits

    # Clear module-level parsed data lists
    lp.sysDiagParsedDataList = []
    lp.txAntDiagParsedDataList = []

    # Also clear limits state since it depends on parsed data
    limits._last_controller = None
    limits._last_limits_type = "burn_in"

    return {
        "status": "cleared",
        "sys_diag_ptu2_loaded": 0,
        "tx_ant_diag_loaded": 0,
    }