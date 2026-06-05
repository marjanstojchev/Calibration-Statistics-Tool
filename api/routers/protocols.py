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
    PTU2 files are discovered automatically in the same directory as each protocol.
    Stores loaded data in shared.load_protocols.sysDiagParsedDataList so that
    /api/system_diagrams/start can use it immediately afterwards.
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

    # Step 3: Find PTU2 and TxAntDiag files for each accepted protocol
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
    sys_diag_parsed_data_list = []
    for entry in ptu2_files_list:
        ptu2_files = entry.get("ptu2FilesList", [])
        if not ptu2_files:
            continue
        loaded = ld.LoadData(ptu2_files, use_sensor_muster, sensor_muster_list)
        if loaded.invalidPath != 1:
            sys_diag_parsed_data_list += loaded.parseDataList

    # Step 4b: Load TxAntDiag data
    tx_ant_diag_parsed_data_list = []
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
    controller: "ParseController" = Depends(get_controller)
):
    paths = []
    for f in files:
        # UploadFile.filename can be None, so normalize to a string first.
        filename = f.filename or ""
        suffix = os.path.splitext(filename)[1]
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        tmp.write(await f.read())
        tmp.close()
        paths.append(tmp.name)

    # hand paths to ParseController — same method your desktop app calls
    result = controller.build_prot_path_type_list(
        paths,
        burn_in_cal_mode=0,        # 0 = normal mode, not burn-in/cal
        include_burn_in_start=False
    )
    
    # Store parsed data in shared module for system_diagrams endpoint
    import shared.load_protocols as lp
    lp.sysDiagParsedDataList = result

    return {"protocols": result, "status": "stored"}   # serialize result to JSON → back to Streamlit


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