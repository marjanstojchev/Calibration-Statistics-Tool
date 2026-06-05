from fastapi import APIRouter, HTTPException
from pathlib import Path
import yaml
import os

from shared import auxiliary as aux
import logconfig

router = APIRouter()



@router.post("/start")
def start():
    """Generate system diagrams PPTX from already-parsed PTU2 data."""
    
    # Lazy-load modules that require Qt initialization
    from system_diagrams import AntennaSystemDiagrams as ant_sys_diags
    import shared.load_protocols as lp
    
    # Retrieve parsed data from module storage
    parseDataList = getattr(lp, 'sysDiagParsedDataList', [])
    if not parseDataList:
        return {"error": "No parsed data. Run /parse first."}
    
    # Load configuration
    config_path = Path(__file__).parent.parent.parent / "shared" / "config" / "AntennaSystemDiagramsConf.yaml"
    with open(config_path, 'r', encoding='utf8') as f:
        config = yaml.safe_load(f)
    
    plotSetup = config['plotSetup']
    graphConfig = config['graphConfig']
    chirpConfig = config['chirpConfig']
    diagramConfig = config['diagramConfig']
    twoGraphSetupList = config.get('twoGraphSetupList', {})
    fourGraphSetupList = config.get('fourGraphSetupList', [])
    threeGraphSetupList = config.get('threeGraphSetupList', [])
    allOnOneSlideGraphList = config.get('allOnOneSlideGraphList', [])
    diagramConfigList = config.get('diagramConfigList', [])
    
    # Setup paths and logger
    sysDiagLogger = logconfig.antSysDiagLogger
    output_pathpptx = aux.antSysDiagOutputPath
    pptxTitle = "Antenna_diagrams.pptx"
    starttemp = os.path.join(aux.assetsDir, "template.pptx")
    
    # Generate PPTX
    ant_sys_diags.start_data_evaluation(
        parseDataList,
        plotSetup,
        chirpConfig,
        graphConfig,
        diagramConfig,
        twoGraphSetupList,
        fourGraphSetupList,
        threeGraphSetupList,
        allOnOneSlideGraphList,
        diagramConfigList,
        sysDiagLogger,
        output_pathpptx,
        pptxTitle,
        starttemp
    )
    
    return {
        "status": "success",
        "output_path": os.path.join(output_pathpptx, pptxTitle)
    }