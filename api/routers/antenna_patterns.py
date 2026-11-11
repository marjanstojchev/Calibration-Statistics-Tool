from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import os

import logconfig
from api.session import NO_DATA_MESSAGE, Session, engine, get_session

router = APIRouter()


# ---------------------------------------------------------------------------
# Pydantic models — match the Antenna Patterns UI panels
# ---------------------------------------------------------------------------

class AntPatTable(BaseModel):
    antenna_pattern_idx: int = 0
    patternType: int = 1          # 1=TX-RX, 2=TX only, 3=RX only
    rotationAxis: int = 1         # 1=z/azimuth, 2=y/elevation
    nofApplicableTxAnt: int = 1
    nofApplicableRxAnt: int = 4
    applTxAntInd: List[int] = Field(default_factory=lambda: [0])
    applRxAntInd: List[int] = Field(default_factory=lambda: [0, 1, 2, 3])
    gainCalcMethod: int = 1       # 1=step-wise, 2=interpolation


class AntPatConf(BaseModel):
    """Single PTU2 input file configuration (matches conf0 in antpat_v5_main_v3)."""
    diagTypeInfo: int = 1         # 1=files contain diagram-type info
    targetAngle: int = 1
    upsideDown: int = 0
    upsideDownInfo: int = 1       # 1=files contain upside-down info
    tables: List[AntPatTable] = Field(default_factory=lambda: [
        AntPatTable(antenna_pattern_idx=0, rotationAxis=1),
        AntPatTable(antenna_pattern_idx=1, rotationAxis=2),
    ])


class AntPatStartRequest(BaseModel):
    # Input / sensor config
    use_sensor_muster: int = 0
    sensor_muster_list: List[str] = Field(default_factory=list)
    # Chirp selection (matches chirpConfig in antpat module)
    chirp_config: Dict[str, int] = Field(default_factory=lambda: {
        "chirp0": 1, "chirp1": 0, "chirp2": 0, "chirp3": 0,
    })
    # PTU2 file configuration
    ptu2_input_conf: AntPatConf = Field(default_factory=AntPatConf)
    # Header metadata (optional — mirrors the UI header panel)
    header_name: str = "Antenna_Pattern_Tables"
    header_type: str = "antennaPattern"
    # Output format: 0=json v1, 1=yaml v1, 2=yaml v2
    output_version: int = 0


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/config/defaults")
def get_defaults():
    """Return default antenna pattern configuration."""
    return AntPatStartRequest().model_dump()


@router.post("/start")
def start(request: Optional[AntPatStartRequest] = None, session: Session = Depends(get_session)):
    """Generate antenna pattern YAML/JSON files from the PTU2 data loaded in this session.

    All configuration fields are optional and default to the same values
    shown in the desktop UI on startup.  The 8-table layout in the UI maps
    to the ``ptu2_input_conf.tables`` list — only enabled tables need to be
    included.
    """
    if request is None:
        request = AntPatStartRequest()

    with engine(session, "antenna_patterns"):
        if not session.sys_diag_list:
            raise HTTPException(status_code=422, detail=NO_DATA_MESSAGE)

        logged_before = session.log_totals["antenna_patterns"]
        from antenna_patterns import antpat_v5_main_v3 as antpat

        # Mirror what ant_pat_handlers.antpat_data_update_and_evaluation() does:
        # set module-level state then call start_data_evaluation.
        antpat.setup["useSensorMuster"] = request.use_sensor_muster
        antpat.setup["sensorMusterList"][:] = list(request.sensor_muster_list)

        antpat.chirpConfig.update(request.chirp_config)

        conf = request.ptu2_input_conf.model_dump()
        antpat.conf0.update({k: v for k, v in conf.items() if k != "tables"})
        antpat.conf0["tables"][:] = [t for t in conf["tables"]]

        antpat.portData["nofDataTables"] = len(antpat.conf0["tables"])
        antpat.portData["version"] = request.output_version

        antpat.ptu2InputConfList[:] = [antpat.conf0]

        antpat.antPatHeader.update({
            "type": request.header_type,
            "name": request.header_name,
        })

        antpat.start_data_evaluation(session.sys_diag_list, logconfig.antPatLogger)

    out_dir = session.output_dir("antenna_patterns")
    produced = [
        name for name in os.listdir(out_dir)
        if os.path.isfile(os.path.join(out_dir, name)) and not name.lower().endswith(".log")
    ]
    if not produced:
        errors = []
        new_lines = session.log_totals["antenna_patterns"] - logged_before
        if new_lines > 0:
            for line in list(session.log_buffers["antenna_patterns"])[-new_lines:]:
                if "[ERROR]" in line:
                    errors.append(line.split("[ERROR]", 1)[-1].strip())
        return {
            "status": "no_output",
            "message": (
                "No antenna pattern files were produced. Check that the Rx/Tx antenna "
                "selection and the rotation axis match your PTU2 data (see the Antenna Patterns log)."
            ),
            "errors": list(dict.fromkeys(errors))[-3:],
            "output_type": "antenna_patterns",
        }
    return {"status": "success", "output_type": "antenna_patterns"}
