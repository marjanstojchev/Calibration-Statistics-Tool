from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

import logconfig

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
def start(request: Optional[AntPatStartRequest] = None):
    """Generate antenna pattern YAML/JSON files from already-parsed PTU2 data.

    All configuration fields are optional and default to the same values
    shown in the desktop UI on startup.  The 8-table layout in the UI maps
    to the ``ptu2_input_conf.tables`` list — only enabled tables need to be
    included.

    Requires /api/protocols/parse to have been called first.
    """
    if request is None:
        request = AntPatStartRequest()

    from antenna_patterns import antpat_v5_main_v3 as antpat
    import shared.load_protocols as lp

    parsed_data = getattr(lp, 'sysDiagParsedDataList', [])
    if not parsed_data:
        return {"error": "No parsed data. Run /api/protocols/parse first."}

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

    antpat.start_data_evaluation(parsed_data, logconfig.antPatLogger)

    return {"status": "success"}
