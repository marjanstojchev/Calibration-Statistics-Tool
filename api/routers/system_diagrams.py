from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import os

from shared import auxiliary as aux
import logconfig

router = APIRouter()


# ---------------------------------------------------------------------------
# Pydantic models — one per UI configuration panel
# ---------------------------------------------------------------------------

class ChirpConfig(BaseModel):
    chirp0: int = 1
    chirp1: int = 0
    chirp2: int = 0
    chirp3: int = 0


class GraphConfig(BaseModel):
    level: int = 1
    avgLevel: int = 0
    normLevel: int = 1
    avgNormLevel: int = 0
    phaseDiff: int = 1
    avgPhaseDiff: int = 0
    diffPhaseDiff: int = 0
    avgDiffPhaseDiff: int = 0
    corrPhaseDiff: int = 1
    diffPhDiffIdealCurve: int = 1


class PlotSetup(BaseModel):
    targetAngle: int = 1              # 1=target angle, 0=PTU angle
    upsideDown: int = 0               # 0=normal, 1=upside-down
    xScaleSizeAuto: int = 0
    xScaleSizeAz: float = 90.0
    xScaleSizeEl: float = 45.0
    idealPhaseDiff: int = 1
    SeparateRxCh: int = 1
    threeGraphLayout: int = 1
    allOnOneSlide: int = 1
    diffPhaseDiffScalingFactor: float = 1.5
    yLimitsAntTypeSeparately: int = 1
    imageDpi: int = 220
    nofSensorMeasToShow: int = 32
    sortByMeasAngle: int = 0
    useSensorMuster: int = 0
    sensorMusterList: List[str] = Field(default_factory=lambda: ["rf", "dsp", "PT", "MA"])
    graphsPerSlide: int = 1


class DiagramConfig(BaseModel):
    selectDiagrams: int = 0      # 0=all, 1=by range, 2=by list
    oddOrEven: int = 0           # 0=both, 1=odd, 2=even
    lowerNumber: int = 0
    higherNumber: int = 4


class TwoGraphSetup(BaseModel):
    primGraph: str = "level"
    secGraph: str = "normLevel"


class ThreeGraphSetup(BaseModel):
    graphType: str = "corrPhaseDiff"


class FourGraphSetup(BaseModel):
    graphType: str = "level"


class AllOnOneSlideGraph(BaseModel):
    graphType: str = "level"


class SysDiagStartRequest(BaseModel):
    plot_setup: PlotSetup = Field(default_factory=PlotSetup)
    chirp_config: ChirpConfig = Field(default_factory=ChirpConfig)
    graph_config: GraphConfig = Field(default_factory=GraphConfig)
    diagram_config: DiagramConfig = Field(default_factory=DiagramConfig)
    two_graph_setup_list: List[TwoGraphSetup] = Field(default_factory=lambda: [
        TwoGraphSetup(primGraph="level", secGraph="normLevel"),
        TwoGraphSetup(primGraph="corrPhaseDiff", secGraph="diffPhaseDiff"),
    ])
    four_graph_setup_list: List[FourGraphSetup] = Field(default_factory=lambda: [
        FourGraphSetup(graphType="level"),
        FourGraphSetup(graphType="corrPhaseDiff"),
        FourGraphSetup(graphType="diffPhaseDiff"),
    ])
    three_graph_setup_list: List[ThreeGraphSetup] = Field(default_factory=lambda: [
        ThreeGraphSetup(graphType="corrPhaseDiff"),
        ThreeGraphSetup(graphType="diffPhaseDiff"),
        ThreeGraphSetup(graphType="phaseDiff"),
    ])
    all_on_one_slide_graph_list: List[AllOnOneSlideGraph] = Field(default_factory=lambda: [
        AllOnOneSlideGraph(graphType="level"),
        AllOnOneSlideGraph(graphType="corrPhaseDiff"),
        AllOnOneSlideGraph(graphType="diffPhaseDiff"),
    ])
    diagram_config_list: List[Dict[str, Any]] = Field(default_factory=list)
    pptx_title: str = "Antenna_diagrams.pptx"


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/config/defaults")
def get_defaults():
    """Return the default configuration matching the UI startup values."""
    return SysDiagStartRequest().model_dump()


@router.post("/start")
def start(request: Optional[SysDiagStartRequest] = None):
    """Generate system diagrams PPTX from already-parsed PTU2 data.

    All configuration fields are optional and default to the same values
    shown in the desktop UI on startup.  Pass only the fields you want to
    override.

    Requires /api/protocols/parse to have been called first.
    """
    if request is None:
        request = SysDiagStartRequest()

    # Check for parsed data before loading the heavy Qt-dependent module
    import shared.load_protocols as lp
    parseDataList = getattr(lp, 'sysDiagParsedDataList', [])
    if not parseDataList:
        raise HTTPException(status_code=422, detail="No parsed data. Run /api/protocols/parse first.")

    # Lazy-load modules that require Qt initialization
    from system_diagrams import AntennaSystemDiagrams as ant_sys_diags

    ant_sys_diags.start_data_evaluation(
        parseDataList,
        request.plot_setup.model_dump(),
        request.chirp_config.model_dump(),
        request.graph_config.model_dump(),
        request.diagram_config.model_dump(),
        [t.model_dump() for t in request.two_graph_setup_list],
        [t.model_dump() for t in request.four_graph_setup_list],
        [t.model_dump() for t in request.three_graph_setup_list],
        [t.model_dump() for t in request.all_on_one_slide_graph_list],
        request.diagram_config_list,
        logconfig.antSysDiagLogger,
        aux.antSysDiagOutputPath,
        request.pptx_title,
        os.path.join(aux.assetsDir, "template.pptx"),
    )

    return {
        "status": "success",
        "output_path": os.path.join(aux.antSysDiagOutputPath, request.pptx_title),
    }