from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool
from typing import List, Optional, Tuple
import os
import shutil
import uuid
import yaml

from api import settings
from api.session import Session, engine, exclusive, fresh_load_log, get_session

router = APIRouter()

# Same meaning as burn_in_cal_mode of ParseController.build_prot_path_type_list
PROTOCOL_TYPE_MODES = {"auto": 0, "burn_in": 1, "calibration": 2}

async def _save_uploads(uploads, dest_dir: str, budget: List[int]) -> Tuple[List[str], int]:
    """Save uploaded files under their ORIGINAL base names.

    The loaders derive their meaning from the file name (``*_ptu2.txt``,
    ``*_Protocol.txt``, ``_TxAnt<n>_Diagram<n>``), so random temp names would
    make every file look invalid. ``budget`` is the remaining byte allowance of
    the request. Returns the saved paths and how many names were duplicates.
    """
    paths: List[str] = []
    duplicates = 0
    for upload in uploads or []:
        name = os.path.basename((upload.filename or "").replace("\\", "/"))
        if not name:
            continue
        path = os.path.join(dest_dir, name)
        if os.path.exists(path):
            duplicates += 1
        with open(path, "wb") as out:
            while chunk := await upload.read(1024 * 1024):
                budget[0] -= len(chunk)
                if budget[0] < 0:
                    raise HTTPException(status_code=413, detail="Upload is too large.")
                out.write(chunk)
        if path not in paths:
            paths.append(path)
    return paths, duplicates


def _process_upload(
    session: Session,
    stage_dir: str,
    protocol_paths: List[str],
    ptu2_paths: List[str],
    txantdiag_paths: List[str],
    use_error: bool,
    use_abort: bool,
    use_limits_exceeded: bool,
    latest_protocol: bool,
    burn_in_start: bool,
    protocol_type: str,
    duplicates: int,
) -> dict:
    """Parse the staged files and replace the session data. Runs under the session and engine locks."""
    import protocolsTest as protocolFilter
    import loaddata as ld

    with engine(session, "upload"):
        fresh_load_log(session)
        with open(os.path.join(session.config_dir, "AntennaSystemDiagramsConf.yaml"), "r", encoding="utf8") as f:
            plot_setup = yaml.safe_load(f)["plotSetup"]
        use_sensor_muster = plot_setup["useSensorMuster"]
        sensor_muster_list = plot_setup["sensorMusterList"]

        # Pre-parse reads error flags / abort criteria, then the filter options are applied
        pre_parsed, *_ = protocolFilter.ProtocolInfoClass.PreParseProtcols(protocol_paths)
        accepted, _ = protocolFilter.ProtocolInfoClass.FilterProtocols(
            pre_parsed, use_error, use_abort, use_limits_exceeded
        )
        if latest_protocol:
            accepted = protocolFilter.ProtocolInfoClass.FilterNewProtocols(accepted)

        # A single unusable file must not discard the files that parsed fine, so the
        # parsed list is kept regardless of LoadData.invalidPath.
        warnings = []
        if duplicates:
            warnings.append(
                f"{duplicates} uploaded file(s) had the same name as another one and replaced it."
            )
        sys_diag_list = []
        if ptu2_paths:
            loaded = ld.LoadData(ptu2_paths, use_sensor_muster, sensor_muster_list)
            sys_diag_list = loaded.parseDataList
            if len(sys_diag_list) < len(ptu2_paths):
                warnings.append(
                    f"{len(ptu2_paths) - len(sys_diag_list)} of {len(ptu2_paths)} PTU2 files "
                    "could not be loaded. File names must end with '_ptu2.txt' and must not contain "
                    "'Diff' or 'NotOk'; parse errors are in the Load Data log."
                )

        tx_diag_list = []
        if txantdiag_paths:
            import load_TxAntData as ld_tx
            loaded_tx = ld_tx.LoadData(txantdiag_paths, use_sensor_muster, sensor_muster_list)
            tx_diag_list = loaded_tx.parseDataList
            if len(tx_diag_list) < len(txantdiag_paths):
                warnings.append(
                    f"{len(txantdiag_paths) - len(tx_diag_list)} of {len(txantdiag_paths)} "
                    "TxAnt diagram files could not be loaded. File names need the '_TxAnt<n>_Diagram<n>' "
                    "label and the sensor info (rf/dsp numbers); parse errors are in the Load Data log."
                )

        if not (ptu2_paths or txantdiag_paths):
            warnings.append(
                "No PTU2 or TxAnt diagram files were uploaded, so only protocol metadata was read."
            )

        # Everything parsed: replace the previous data in one step
        session.reset_data()
        session.upload_dir = stage_dir
        session.sys_diag_list = sys_diag_list
        session.tx_diag_list = tx_diag_list
        session.protocol_paths = [p.PathName for p in accepted]
        # Used as the defaults of the limits computation
        session.state["protocol_options"] = {
            "burn_in_cal_mode": PROTOCOL_TYPE_MODES[protocol_type],
            "include_burn_in_start": burn_in_start,
        }
    return {
        "status": "ok",
        "protocols_received": len(protocol_paths),
        "protocols_accepted": len(accepted),
        "ptu2_files_received": len(ptu2_paths),
        "ptu2_files_loaded": len(sys_diag_list),
        "tx_ant_diag_received": len(txantdiag_paths),
        "tx_ant_diag_loaded": len(tx_diag_list),
        "warnings": warnings,
        "filters_applied": {
            "use_error": use_error,
            "use_abort": use_abort,
            "use_limits_exceeded": use_limits_exceeded,
            "latest_protocol": latest_protocol,
            "burn_in_start": burn_in_start,
            "protocol_type": protocol_type,
        },
    }


@router.post("/upload")
async def upload_protocols(
    files: List[UploadFile] = File(...),
    ptu2_files: Optional[List[UploadFile]] = File(None),
    txantdiag_files: Optional[List[UploadFile]] = File(None),
    use_error: bool = False,
    use_abort: bool = True,
    use_limits_exceeded: bool = True,
    latest_protocol: bool = False,
    burn_in_start: bool = False,
    protocol_type: str = "auto",
    session: Session = Depends(get_session),
):
    """Upload protocol, PTU2 and TxAnt diagram files from the browser and load them.

    The browser sends every file; nothing is read from server folders. The upload
    is all-or-nothing: the files are staged in their own folder first, and the
    session data is only replaced once everything was parsed. A failed upload
    leaves the previous data untouched.
    """
    stage_dir = os.path.join(session.upload_root, uuid.uuid4().hex)
    if protocol_type not in PROTOCOL_TYPE_MODES:
        raise HTTPException(status_code=400, detail="protocol_type must be 'auto', 'burn_in' or 'calibration'.")
    os.makedirs(stage_dir)
    committed = False
    try:
        budget = [settings.MAX_UPLOAD_BYTES]
        protocol_paths, dup1 = await _save_uploads(files, stage_dir, budget)
        ptu2_paths, dup2 = await _save_uploads(ptu2_files, stage_dir, budget)
        txantdiag_paths, dup3 = await _save_uploads(txantdiag_files, stage_dir, budget)
        if not protocol_paths:
            raise HTTPException(status_code=400, detail="No protocol files were uploaded.")

        result = await run_in_threadpool(
            _process_upload, session, stage_dir, protocol_paths, ptu2_paths, txantdiag_paths,
            use_error, use_abort, use_limits_exceeded, latest_protocol, burn_in_start, protocol_type,
            dup1 + dup2 + dup3,
        )
        committed = True
        return result
    finally:
        if not committed:
            shutil.rmtree(stage_dir, ignore_errors=True)


def _clear(session: Session) -> None:
    with exclusive(session, "clear"):
        session.reset_data()


@router.delete("/clear")
def clear_protocols(session: Session = Depends(get_session)):
    """Clear the loaded protocol data and uploaded files of this session ('Clear Data' button).

    Waits for a running operation of the same session to finish first, so a
    clear can never pull data away from a generation in progress.
    """
    _clear(session)
    return {
        "status": "cleared",
        "sys_diag_ptu2_loaded": 0,
        "tx_ant_diag_loaded": 0,
    }
