from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import os

import logconfig
from shared import auxiliary as aux

router = APIRouter()


# ---------------------------------------------------------------------------
# Pydantic models — match the TX-Antenna Diagrams UI panels exactly
# ---------------------------------------------------------------------------

class TxPlotSetup(BaseModel):
    useSensorMuster: int = 0
    sensorMusterList: List[str] = Field(default_factory=list)
    targetAngle: int = 0          # 0=PTU angle (TX default), 1=target angle
    upsideDown: int = 0
    AzDiag: int = 1               # Generate azimuth diagrams
    ElDiag: int = 1               # Generate elevation diagrams
    xScaleSizeAuto: int = 0
    xScaleSizeAz: float = 90.0
    xScaleSizeEl: float = 45.0
    imageDpi: int = 220
    nofSensorMeasToShow: int = 32
    plotOrigGraphs: int = 1       # Plot original (un-normalised) graphs
    plotNormGraphs: int = 1       # Plot normalised graphs
    graphsPerSlide: int = 1


class TxGraphConfig(BaseModel):
    level: int = 1                # Corrected TX power via spectrum analyser [dBm]
    levelPowMet: int = 0          # Corrected TX power via power meter [dBm]
    levelMeasSpec: int = 0        # Measured TX power via spectrum analyser [dBm]
    levelMeasPowMet: int = 0      # Measured TX power via power meter [dBm]
    frequency: int = 0            # Frequency [MHz]
    time: int = 0                 # Time [ms]


class TxStartRequest(BaseModel):
    plot_setup: TxPlotSetup = Field(default_factory=TxPlotSetup)
    graph_config: TxGraphConfig = Field(default_factory=TxGraphConfig)
    pptx_title: str = "TxAntenna_diagrams.pptx"


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/config/defaults")
def get_defaults():
    """Return the default TX diagrams configuration matching the UI startup values."""
    return TxStartRequest().model_dump()


@router.post("/start")
def start(request: Optional[TxStartRequest] = None):
    """Generate TX antenna diagrams PPTX from already-parsed TxAntDiag data.

    All configuration fields are optional and default to the same values
    shown in the desktop UI on startup.

    Requires /api/protocols/parse (with search_txantdiag_files=true) to have
    been called first.
    """
    if request is None:
        request = TxStartRequest()

    # Check for parsed data before loading the heavy module
    import shared.load_protocols as lp
    parsed_data = getattr(lp, 'txAntDiagParsedDataList', [])
    if not parsed_data:
        raise HTTPException(
            status_code=422,
            detail="No TxAntDiag parsed data. Run /api/protocols/parse with search_txantdiag_files=true first.",
        )

    # Lazy-load to avoid Qt initialization at module level
    from tx_diagrams import TxAntDiagrams as tx_ant_diags

    tx_ant_diags.start_data_evaluation(
        parsed_data,
        request.plot_setup.model_dump(),
        request.graph_config.model_dump(),
        logconfig.txAntDiagLogger,
        aux.txAntDiagOutputPath,
        request.pptx_title,
        os.path.join(aux.assetsDir, "template.pptx"),
    )

    return {
        "status": "success",
        "output_path": os.path.join(aux.txAntDiagOutputPath, request.pptx_title),
    }
