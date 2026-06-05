from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import os

import logconfig
from shared import auxiliary as aux

router = APIRouter()


# ---------------------------------------------------------------------------
# Pydantic models — match the Hüllkurven tab UI panels
# ---------------------------------------------------------------------------

class HuellkurvenDataConf(BaseModel):
    AzDiag: int = 1               # Generate azimuth envelope limits
    ElDiag: int = 1               # Generate elevation envelope limits
    minSigma: int = -10           # Min sigma for pattern-sigma method
    maxSigma: int = 10            # Max sigma for pattern-sigma method
    patternLimitsMethod: int = 0  # 0=sigma-based, 1=min/max-based
    minPhaseFactor: int = 5
    maxPhaseFactor: int = 5


class HuellkurvenPlotSetup(BaseModel):
    xScaleSizeAuto: int = 0
    xScaleSizeAz: float = 90.0
    xScaleSizeEl: float = 45.0


class HuellkurvenChirpConfig(BaseModel):
    chirp0: int = 1
    chirp1: int = 0
    chirp2: int = 0
    chirp3: int = 0


class HuellkurvenDiagramConfig(BaseModel):
    selectDiagrams: int = 0      # 0=all, 1=by range, 2=by list
    oddOrEven: int = 0           # 0=both, 1=odd, 2=even
    lowerNumber: int = 0
    higherNumber: int = 4


class HuellkurvenInputConfig(BaseModel):
    """Mirrors the plotSetup fields used by hullkurven_handlers as inputConfig."""
    diagTypeInfo: int = 1
    targetAngle: int = 1
    upsideDown: int = 0
    upsideDownInfo: int = 1
    useSensorMuster: int = 0
    sensorMusterList: List[str] = Field(default_factory=list)


class HuellkurvenStartRequest(BaseModel):
    data_conf: HuellkurvenDataConf = Field(default_factory=HuellkurvenDataConf)
    plot_setup: HuellkurvenPlotSetup = Field(default_factory=HuellkurvenPlotSetup)
    chirp_config: HuellkurvenChirpConfig = Field(default_factory=HuellkurvenChirpConfig)
    diagram_config: HuellkurvenDiagramConfig = Field(default_factory=HuellkurvenDiagramConfig)
    input_config: HuellkurvenInputConfig = Field(default_factory=HuellkurvenInputConfig)
    diagram_config_list: List[Dict[str, Any]] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/config/defaults")
def get_defaults():
    """Return default Hüllkurven configuration matching the UI startup values."""
    return HuellkurvenStartRequest().model_dump()


@router.post("/start")
def start(request: Optional[HuellkurvenStartRequest] = None):
    """Compute envelope curve (Hüllkurven) limits from already-parsed PTU2 data.

    Generates per-antenna-type, per-angle-setup DAT limit files and PNG plots
    under the configured huellkurven output directory.

    Requires /api/protocols/parse to have been called first.
    """
    if request is None:
        request = HuellkurvenStartRequest()

    from shared import huellkurven_data_processing as hdp
    import shared.load_protocols as lp

    parsed_data = getattr(lp, 'sysDiagParsedDataList', [])
    if not parsed_data:
        raise HTTPException(status_code=422, detail="No parsed data. Run /api/protocols/parse first.")

    data_conf = request.data_conf.model_dump()
    chirp_config = request.chirp_config.model_dump()
    diagram_config = request.diagram_config.model_dump()
    diagram_config_list = request.diagram_config_list
    input_config = request.input_config.model_dump()

    conf_chirp_list = hdp.getConfChirpList(chirp_config)
    if not conf_chirp_list:
        raise HTTPException(status_code=400, detail="No active chirps. Enable at least one chirp in chirp_config.")

    antenna_types = hdp.getAntennaTypesList(parsed_data)
    if not antenna_types:
        raise HTTPException(status_code=422, detail="No antenna types found in parsed data.")

    # Prepare output directory (mirrors hullkurven_handlers._worker)
    create_status, create_msg = aux.createDirectory(aux.huellKurvenOutputPath)
    if not create_status:
        raise HTTPException(status_code=500, detail=f"Failed to create output directory: {create_msg}")
    aux.clearAll(aux.huellKurvenOutputPath)

    VERSION = 1
    comments_dict = {
        "version": (
            " // Pattern calc: Method 0 = Factor*StdDev diff from median + reserve dB;"
            " Method 1 = StdDev diff from max/min."
        ),
    }

    for antenna_type in antenna_types:
        ant_type_output = os.path.join(aux.huellKurvenOutputPath, "AntType" + str(antenna_type))
        aux.createDirectory(ant_type_output)

        ptu2_list = hdp.getPtu2ListPerAntennaType(antenna_type, parsed_data)
        angle_setup_list = hdp.setAngleSetupList(input_config, ptu2_list)
        if not angle_setup_list:
            continue

        for angle_setup in angle_setup_list:
            angle_str = (
                "NofPts=" + str(angle_setup.nofAnglePoints)
                + "_StepSize=" + str(angle_setup.angleStepSize)
                + "_RefPt=" + str(angle_setup.refAnglePoint)
            )
            angle_output = os.path.join(ant_type_output, angle_str)
            aux.createDirectory(angle_output)

            conf_ptu2_list = hdp.getConfiguredPtu2Files(ptu2_list, angle_setup, input_config)
            if not conf_ptu2_list:
                continue

            desired_diagrams = hdp.getDesiredDiagramsList(
                diagram_config, diagram_config_list, antenna_type, conf_ptu2_list
            )
            if not desired_diagrams:
                continue

            cent_freq_dict_list: list = []

            for diag_idx in range(len(desired_diagrams)):
                for chirp in conf_chirp_list:
                    diag_num = desired_diagrams[diag_idx]["diagramNum"]
                    avg_freq = hdp.getAvgFreqPerDiagram(chirp, diag_num, conf_ptu2_list)
                    min_freq = hdp.getMinFreqPerDiagram(chirp, diag_num, conf_ptu2_list)
                    max_freq = hdp.getMaxFreqPerDiagram(chirp, diag_num, conf_ptu2_list)
                    cent_freq_dict_list.append({
                        "avgFreqMHz": format(round(avg_freq / 1e6, 4), ".2f"),
                        "avgFreqGHz": format(round(avg_freq / 1e9, 4), ".2f"),
                        "posFreqDevMHz": format(round((max_freq - avg_freq) / 1e6, 4), ".2f"),
                        "negFreqDevMHz": format(round((avg_freq - min_freq) / 1e6, 4), ".2f"),
                        "diagNum": diag_num,
                        "chirp": chirp,
                    })

                    # Replicate exact Az/El logic from hullkurven_handlers
                    if angle_setup.diagType == "Az":
                        if data_conf["AzDiag"]:
                            limits_data = hdp.createLimitsData(
                                VERSION, comments_dict, desired_diagrams, diag_idx, chirp,
                                antenna_type, conf_ptu2_list, angle_setup, cent_freq_dict_list,
                                "Az", input_config, chirp_config, data_conf, write_output=True,
                            )
                            if limits_data is not None:
                                hdp.savePlotImage(limits_data, aux.huellKurvenOutputPath)
                    elif angle_setup.diagType == "El":
                        if data_conf["ElDiag"]:
                            limits_data = hdp.createLimitsData(
                                VERSION, comments_dict, desired_diagrams, diag_idx, chirp,
                                antenna_type, conf_ptu2_list, angle_setup, cent_freq_dict_list,
                                "El", input_config, chirp_config, data_conf, write_output=True,
                            )
                            if limits_data is not None:
                                hdp.savePlotImage(limits_data, aux.huellKurvenOutputPath)
                    else:
                        # No diagType info — try both axes based on data_conf flags
                        for az_el in ["Az", "El"]:
                            if az_el == "Az" and not data_conf["AzDiag"]:
                                continue
                            if az_el == "El" and not data_conf["ElDiag"]:
                                continue
                            limits_data = hdp.createLimitsData(
                                VERSION, comments_dict, desired_diagrams, diag_idx, chirp,
                                antenna_type, conf_ptu2_list, angle_setup, cent_freq_dict_list,
                                az_el, input_config, chirp_config, data_conf, write_output=True,
                            )
                            if limits_data is not None:
                                hdp.savePlotImage(limits_data, aux.huellKurvenOutputPath)

    return {"status": "success", "output_path": aux.huellKurvenOutputPath}
