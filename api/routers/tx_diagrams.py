from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import os

import logconfig
from shared import auxiliary as aux
from api.session import Session, engine, get_session, safe_filename

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
def start(request: Optional[TxStartRequest] = None, session: Session = Depends(get_session)):
    """Generate TX antenna diagrams PPTX from the TxAntDiag data loaded in this session.

    All configuration fields are optional and default to the same values
    shown in the desktop UI on startup.
    """
    if request is None:
        request = TxStartRequest()

    pptx_title = safe_filename(request.pptx_title, "TxAntenna_diagrams.pptx", ".pptx")

    with engine(session, "tx_diagrams"):
        if not session.tx_diag_list:
            raise HTTPException(
                status_code=422,
                detail="No TxAnt diagram data loaded. Upload TxAnt diagram files in the Protocols tab first.",
            )

        # Lazy-load to avoid Qt initialization at module level
        from tx_diagrams import TxAntDiagrams as tx_ant_diags

        # The generator reads this log back for its warning/error summary slide but never creates it
        logconfig.txAntDiagLogger.addFileHandler(session.log_file("txAntDiagLogFilePath"), "w+")

        tx_ant_diags.start_data_evaluation(
            session.tx_diag_list,
            request.plot_setup.model_dump(),
            request.graph_config.model_dump(),
            logconfig.txAntDiagLogger,
            session.output_dir("tx_diagrams"),
            pptx_title,
            os.path.join(aux.assetsDir, "template.pptx"),
        )

    return {
        "status": "success",
        "pptx_file": pptx_title,
        "output_type": "tx_diagrams",
    }
